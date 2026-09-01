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

# Active Groq LLM & Tavily Client
llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Local HuggingFace Embeddings
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
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            split_docs = text_splitter.split_documents(raw_docs)
            docs_to_index = [d for d in split_docs if d.page_content.strip()]
            print(f"--- [INFO] Indexed {len(docs_to_index)} chunks from {target_path} ---")
        except Exception as e:
            print(f"--- [WARNING] PDF read failed: {e} ---")

    if not docs_to_index:
        docs_to_index = [
            Document(page_content="Yash Sharma is pursuing a Bachelor of Computer Application (BCA). He has skills in HTML, CSS, Advanced Excel, Web Development, and AI.")
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
            prompt = (
                f"Question: {question}\n"
                f"Context: {doc.page_content}\n\n"
                f"Does the context contain any relevant keywords, candidate details, skills, or education? Answer yes or no."
            )
            try:
                score = structured_doc_grader.invoke(prompt)
                if score.binary_score.lower() == "yes":
                    filtered_docs.append(doc)
            except Exception:
                filtered_docs.append(doc)

    if not filtered_docs and documents:
        resume_keywords = ["my", "i", "resume", "skills", "education", "degree", "experience", "projects", "yash"]
        if any(w in question.lower() for w in resume_keywords):
            filtered_docs = documents

    web_search = "Yes" if len(filtered_docs) == 0 else "No"
    print(f"--- [DECISION] Relevant docs: {len(filtered_docs)} | Web search needed: {web_search} ---")

    return {"documents": filtered_docs, "question": question, "web_search": web_search}

def generate(state: GraphState):
    current_retry = state.get("retry_count", 0) + 1
    print(f"--- [NODE: GENERATE] Generating response (Attempt {current_retry}) ---")
    
    question = state["question"]
    documents = state.get("documents", [])
    
    context_text = "\n\n".join([d.page_content for d in documents])
    prompt = (
        f"You are an intelligent AI assistant.\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n\n"
        f"Provide a direct, concise, and complete answer based strictly on the context provided:"
    )
    
    response = llm.invoke(prompt)
    return {
        "generation": response.content,
        "documents": documents,
        "question": question,
        "retry_count": current_retry
    }

def transform_query(state: GraphState):
    print("--- [NODE: TRANSFORM QUERY] Optimizing query for Web Search ---")
    question = state["question"]
    better_query = llm.invoke(f"Rephrase this question into a clean 3-4 word keyword search query for Google/Web Search. Output ONLY the query without quotes: {question}").content.strip()
    return {"question": better_query}

def fallback_search(state: GraphState):
    print("--- [NODE: TAVILY SEARCH] Searching the live web ---")
    query = state["question"]
    try:
        search_results = tavily_client.search(query=query, max_results=3)
        web_context = "\n".join([res["content"] for res in search_results.get("results", [])])
        web_doc = [Document(page_content=f"Web Search Results:\n{web_context}")]
    except Exception as e:
        web_doc = [Document(page_content=f"Live search failed: {e}")]

    docs = state.get("documents", [])
    docs.extend(web_doc)
    return {"documents": docs, "question": query}