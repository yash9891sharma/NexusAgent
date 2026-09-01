import os
import streamlit as st
from src.graph import nexus_app

# 1. UI Page Setup
st.set_page_config(
    page_title="Nexus Agent - Self-Correcting RAG",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Nexus Agent: Self-Correcting RAG")
st.caption("Powered by LangGraph, Groq, ChromaDB & Tavily Live Search")

# 2. Sidebar for PDF Upload
with st.sidebar:
    st.header("📄 Knowledge Base")
    uploaded_file = st.file_uploader("Upload PDF Resume / Document", type=["pdf"])
    
    if uploaded_file is not None:
        os.makedirs("data", exist_ok=True)
        pdf_target_path = os.path.join("data", "sample.pdf")
        with open(pdf_target_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Loaded `{uploaded_file.name}` into system!")

    st.markdown("---")
    st.markdown("**Workflow Execution:**")
    st.markdown("* Step 1: ChromaDB Local Vector Search")
    st.markdown("* Step 2: Relevance Grading")
    st.markdown("* Step 3: Tavily Live Web Search Fallback")
    st.markdown("* Step 4: Anti-Hallucination Evaluation")

# 3. Chat Session Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. User Input & Graph Invocation
if user_prompt := st.chat_input("Apna sawaal yahan puchiye..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        status_box = st.status("🔍 Nexus Agent processing query...", expanded=True)
        
        try:
            status_box.write("⚙️ Running LangGraph nodes...")
            initial_inputs = {"question": user_prompt, "retry_count": 0}
            
            result = nexus_app.invoke(initial_inputs)
            
            # Decision check: Local context vs Web search
            if result.get("web_search") == "Yes":
                status_box.write("🌐 Context missing locally -> Triggered Tavily Live Web Search.")
            else:
                status_box.write("📑 Found relevant context inside uploaded Document.")
                
            status_box.write("✅ Passed Hallucination & Answer Quality Check.")
            status_box.update(label="Response Complete!", state="complete", expanded=False)

            # Display Output
            final_response = result.get("generation", "No response generated.")
            st.markdown(final_response)
            st.session_state.messages.append({"role": "assistant", "content": final_response})

        except Exception as e:
            status_box.update(label="Execution Error", state="error", expanded=True)
            st.error(f"Error during graph execution: {e}")