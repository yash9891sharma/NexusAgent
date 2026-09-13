import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

def get_clean_key(name: str) -> str:
    val = ""
    try:
        import streamlit as st
        if name in st.secrets:
            val = str(st.secrets[name])
    except Exception:
        pass
    if not val:
        val = os.getenv(name, "")
    return "".join(val.split()).strip('"\'')

def grade_doc_relevance(document_text: str, question: str) -> bool:
    try:
        api_key = get_clean_key("GOOGLE_API_KEY")
        if not api_key:
             raise ValueError("API Key is missing!")
             
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            temperature=0,
            api_key=api_key
        )
        prompt = PromptTemplate(
            template="""You are a document relevance evaluator.
Document:
{document}

Question:
{question}

Does this document contain information directly relevant to the question? Reply ONLY 'yes' or 'no'.""",
            input_variables=["document", "question"]
        )
        chain = prompt | llm
        res = chain.invoke({"document": document_text, "question": question})
        return "yes" in res.content.strip().lower()
    except Exception as e:
        print(f"--- [WARNING] Grader fallback: {e} ---")
        return any(w in document_text.lower() for w in question.lower().split() if len(w) > 3)