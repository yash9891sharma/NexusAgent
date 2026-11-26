import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv(override=True)

def get_clean_key(key_name: str) -> str:
    val = os.getenv(key_name)
    
    # 2. Agar nahi mila, toh Streamlit Secrets se try karein
    if not val:
        try:
            import streamlit as st
            val = st.secrets.get(key_name)
        except Exception:
            pass
            
    # 3. Safe string replace (Agar key None hai toh crash nahi hoga)
    if not val:
        return ""
        
    return str(val).strip().replace('"', "").replace("'", "")

def grade_doc_relevance(document_text: str, question: str) -> bool:
    try:
        api_key = get_clean_key("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API Key is missing!")
            
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.8-flash",
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
        
        # Safe parsing for gemini-3.8-flash (list or string)
        raw_content = res.content
        ans = (raw_content[0].get("text", "") if isinstance(raw_content, list) else str(raw_content)).strip().lower()
        return "yes" in ans
        
    except Exception as e:
        print(f"--- [WARNING] Grader fallback: {e} ---")
        return any(w in document_text.lower() for w in question.lower().split() if len(w) > 3)