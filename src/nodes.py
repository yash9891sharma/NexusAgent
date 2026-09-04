# src/nodes.py
import os
from tavily import TavilyClient
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.state import GraphState
from src.graders import grade_doc_relevance

GROQ_API_KEY = "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"
TAVILY_API_KEY = "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"

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = None
retriever = None

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        api_key=GROQ_API_KEY
    )

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
        except Exception as e:
            print(f"--- [WARNING] PDF read failed: {e} ---")

    if not docs_to_index:
        docs_to_index = [
            Document(page_content="Nexus Agent is an advanced autonomous self-correcting RAG system designed, engineered, and developed by Yash Sharma. It uses LangGraph, Groq, ChromaDB, and Tavily Search.")
        ]

    vectorstore = Chroma.from_documents(documents=docs_to_index, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return retriever

build_retriever()

def retrieve(state: GraphState):
    question = state["question"]
    current_retriever = retriever if retriever is not None else build_retriever()
    documents = current_retriever.invoke(question)
    return {
        "documents": documents,
        "question": question,
        "retry_count": state.get("retry_count", 0)
    }

def grade_documents(state: GraphState):
    question = state["question"]
    documents = state.get("documents", [])
    filtered_docs = []

    for doc in documents:
        if grade_doc_relevance(doc.page_content, question):
            filtered_docs.append(doc)

    web_search = "Yes" if len(filtered_docs) == 0 else "No"
    return {"documents": filtered_docs, "question": question, "web_search": web_search}

def transform_query(state: GraphState):
    question = state["question"]
    try:
        llm = get_llm()
        better_query = llm.invoke(
            f"Convert this question into a concise 3-4 word keyword search query for Google: {question}. Output ONLY keywords without quotes."
        ).content.strip().replace('"', '')
    except Exception:
        better_query = question
    return {"question": better_query}

def fallback_search(state: GraphState):
    query = state["question"]
    web_doc = []
    
    if TAVILY_API_KEY:
        try:
            client = TavilyClient(api_key=TAVILY_API_KEY)
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
    question = state["question"]
    documents = state.get("documents", [])
    context_text = "\n\n".join([d.page_content for d in documents if d.page_content.strip()])
    
    prompt = f"""You are Nexus Agent, an intelligent autonomous RAG system designed and engineered by Yash Sharma.

Context:
{context_text if context_text else "No external document context found."}

Question: {question}

Instructions:
1. If asked about your creator, developer, or origin, state clearly that you were designed and built by Yash Sharma.
2. If document or web context is provided, base your answer factually on it.
3. If context is empty or the question is general knowledge, answer directly, accurately, and crisply using your foundational intelligence.
4. Keep the answer professional, direct, and concise."""

    try:
        llm = get_llm()
        response = llm.invoke(prompt)
        gen_text = response.content
    except Exception as e:
        gen_text = f"An error occurred while generating response: {e}"

    return {
        "generation": gen_text,
        "documents": documents,
        "question": question,
        "retry_count": current_retry
    }