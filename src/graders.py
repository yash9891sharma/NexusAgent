import os
from dotenv import load_dotenv

load_dotenv(override=True)

def get_clean_key(key_name: str) -> str:
    val = os.getenv(key_name)
    if not val:
        try:
            import streamlit as st
            val = st.secrets.get(key_name)
        except Exception:
            pass
    if not val:
        return ""
    return str(val).strip().replace('"', "").replace("'", "")

def grade_doc_relevance(document_text: str, question: str) -> bool:
    """
    Ultra-fast local semantic & keyword relevance grader.
    Eliminates 4x redundant LLM API calls per query to prevent rate-limit hangs.
    """
    if not document_text or not document_text.strip():
        return False
        
    doc_lower = document_text.lower()
    q_lower = question.lower()
    
    # Common document/resume intent words
    doc_intent_words = ["resume", "cv", "pdf", "document", "summary", "skills", "experience", "education", "project", "about"]
    if any(word in q_lower for word in doc_intent_words):
        return True
        
    # Check meaningful keyword overlap
    stop_words = {"what", "is", "the", "of", "in", "to", "a", "an", "for", "on", "with", "this", "me", "show", "tell", "how", "who", "where", "when"}
    keywords = [w.strip("?.,!") for w in q_lower.split() if len(w.strip("?.,!")) > 2 and w.strip("?.,!") not in stop_words]
    
    if not keywords:
        return True
        
    return any(kw in doc_lower for kw in keywords)