import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.state import GraphState
from src.graders import structured_doc_grader

load_dotenv()

# Active Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Vector Store Manager
vectorstore = None
retriever = None

def build_retriever(pdf_path: str = None):
    global vectorstore, retriever
    docs_to_index = []
    target_path = pdf_path if pdf_path else "data/sample.pdf"
    
    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        try:
            loader = PyPDFLoader(target_path)
            raw_docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
            split_docs = text_splitter.split_documents(raw_docs)
            docs_to_index = [d for d in split_docs if d.page_content.strip()]
            print(f"--- [INFO] Indexed {len(docs_to_index)} chunks from {target_path} ---")
        except Exception as e:
            print(f"--- [WARNING] PDF read failed: {e} ---")

    if not docs_to_index:
        docs_to_index = [
            Document(page_content="Nexus Agent is an autonomous RAG system built by Yash Sharma.")
        ]

    vectorstore = Chroma.from_documents(documents=docs_to_index, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return retriever

# Initial Retriever Build
build_retriever()

# --- Graph Nodes ---

def retrieve(state: GraphState):
    print("--- [NODE: RETRIEVE] Fetching relevant docs ---")
    question = state["question"]
    current_retriever = retriever if retriever is not None else build_retriever()
    documents = current_retriever.invoke(question)
    return {
        "documents": documents,
        "question": question,
        "retry_count": state.get("retry_count", 0)
    }

def grade_documents(state: GraphState):
    print("--- [NODE: GRADE DOCS] Checking document relevance ---")
    question = state["question"]
    documents = state.get("documents", [])
    filtered_docs = []

    if documents:
        for doc in documents:
            try:
                res = structured_doc_grader.invoke({
                    "document": doc.page_content,
                    "question": question
                })
                score = res.content.strip().lower()
                if "yes" in score:
                    filtered_docs.append(doc)
            except Exception as e:
                print(f"--- [WARNING] Grader issue, falling back: {e} ---")
                if any(w in doc.page_content.lower() for w in question.lower().split() if len(w) > 3):
                    filtered_docs.append(doc)

    web_search = "Yes" if len(filtered_docs) == 0 else "No"
    print(f"--- [DECISION] Relevant docs: {len(filtered_docs)} | Trigger Web Search: {web_search} ---")

    return {"documents": filtered_docs, "question": question, "web_search": web_search}

def transform_query(state: GraphState):
    print("--- [NODE: TRANSFORM QUERY] Optimizing query for Web Search ---")
    question = state["question"]
    try:
        better_query = llm.invoke(
            f"Convert this question into a concise 3-4 word Google search query: {question}. Output ONLY the search keywords without quotes."
        ).content.strip().replace('"', '')
    except Exception:
        better_query = question
    return {"question": better_query}

def fallback_search(state: GraphState):
    print("--- [NODE: TAVILY SEARCH] Searching the live web ---")
    query = state["question"]
    tavily_key = os.getenv("TAVILY_API_KEY")
    web_doc = []
    
    if tavily_key:
        try:
            client = TavilyClient(api_key=tavily_key)
            search_results = client.search(query=query, max_results=3)
            web_context = "\n".join([res.get("content", "") for res in search_results.get("results", []) if res.get("content")])
            if web_context.strip():
                web_doc = [Document(page_content=f"Live Web Context:\n{web_context}")]
        except Exception as e:
            print(f"--- [WARNING] Tavily search error: {e} ---")

    docs = state.get("documents", [])
    docs.extend(web_doc)
    return {"documents": docs, "question": query}

def generate(state: GraphState):
    current_retry = state.get("retry_count", 0) + 1
    print(f"--- [NODE: GENERATE] Generating synthesized response ---")
    
    question = state["question"]
    documents = state.get("documents", [])
    context_text = "\n\n".join([d.page_content for d in documents if d.page_content.strip()])
    
    prompt = f"""You are Nexus Agent, an intelligent autonomous AI assistant.

Context:
{context_text if context_text else "No external document context found."}

Question: {question}

Instructions:
1. If relevant document or web context is provided, base your answer factually on it.
2. If context is empty or the question is general knowledge / current affairs, answer directly, accurately, and politely using your foundational intelligence.
3. Keep the answer direct, crisp, and helpful."""

    response = llm.invoke(prompt)
    return {
        "generation": response.content,
        "documents": documents,
        "question": question,
        "retry_count": current_retry
    }