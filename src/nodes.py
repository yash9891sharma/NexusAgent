from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def intelligent_router(state: GraphState):
    """
    Sawaal ko analyze karta hai aur decide karta hai ki PDF search karni hai ya direct answer dena hai.
    """
    question = state["question"]
    
    router_prompt = PromptTemplate(
        template="""You are an expert router for an AI agent. 
        Analyze the user question: '{question}'
        
        If the question requires looking into uploaded documents, manuals, or local PDFs, output 'vectorstore'.
        If it is a general knowledge question, coding help, casual chat, or current events, output 'websearch' or 'direct'.
        
        Return ONLY one word: either 'vectorstore' or 'direct'. Do not add any extra text.""",
        input_variables=["question"]
    )
    
    try:
        llm = get_llm()
        chain = router_prompt | llm | StrOutputParser()
        route = chain.invoke({"question": question}).strip().lower()
        
        print(f"--- [ROUTER DECISION]: Route chosen -> {route} ---")
        
        if "vectorstore" in route:
            return {"route": "vectorstore"}
        else:
            return {"route": "direct"}
    except Exception as e:
        print(f"--- [ROUTER ERROR]: {e}, defaulting to vectorstore ---")
        return {"route": "vectorstore"}
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.state import GraphState
from src.graders import grade_doc_relevance, get_clean_key

load_dotenv(override=True)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = None
retriever = None

def get_llm():
    api_key = get_clean_key("GOOGLE_API_KEY")
    if not api_key:
         raise ValueError("GOOGLE_API_KEY is missing! Check .env file.")
         
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0.2,
        api_key=api_key
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
            Document(page_content="Nexus Agent is an advanced autonomous RAG system engineered by Yash Sharma.")
        ]

    vectorstore = Chroma.from_documents(documents=docs_to_index, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return retriever

build_retriever()

def retrieve(state: GraphState):
    question = state["question"]
    current_retriever = retriever if retriever is not None else build_retriever()
    documents = current_retriever.invoke(question)
    return {"documents": documents, "question": question, "retry_count": state.get("retry_count", 0)}

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
    tavily_key = get_clean_key("TAVILY_API_KEY")
    web_doc = []
    if tavily_key and len(tavily_key) > 10:
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
    question = state["question"]
    documents = state.get("documents", [])
    formatted_docs = []
    for doc in documents:
        page_num = doc.metadata.get("page", "Unknown")
        if isinstance(page_num, int):
            page_num += 1
        formatted_docs.append(f"[Source: Page {page_num}]\n{doc.page_content}")
    context_text = "\n\n---\n\n".join(formatted_docs)
    
    prompt = f"""You are Nexus Agent, an intelligent autonomous RAG system designed and engineered by Yash Sharma.
    IMPORTANT RULE: You must always cite the source page number at the very end of your final answer. Use the format "Source: Page X".

Context:
{context_text if context_text else "No external document context found."}
Question: {question}
Instructions:
1. Base your answer factually on the context if provided.
2. If context is empty, answer directly using your foundational intelligence.
3. Keep the answer professional, direct, and concise."""

    try:
        llm = get_llm()
        # StrOutputParser metadata ko hata dega aur clean text dega
        chain = llm | StrOutputParser()
        gen_text = chain.invoke(prompt)
    except Exception as e:
        gen_text = f"An error occurred while generating response: {e}"

    return {
        "generation": gen_text, 
        "documents": documents, 
        "question": question, 
        "retry_count": current_retry
    }