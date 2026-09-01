import os
import time
import tempfile
import streamlit as st

st.set_page_config(
    page_title="Nexus Agent | Autonomous Self-Correcting RAG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-Sanitize Secrets
for key in ["GROQ_API_KEY", "TAVILY_API_KEY"]:
    if key in st.secrets:
        raw_val = str(st.secrets[key])
        os.environ[key] = "".join(raw_val.split()).strip('"\'')

from src.graph import nexus_app
from src.nodes import build_retriever

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .stChatMessage { border-radius: 12px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚡ Nexus Agent")
    st.caption("Autonomous RAG Pipeline")
    
    st.markdown("---")
    st.subheader("📁 Document Knowledge Base")
    uploaded_file = st.file_uploader("Upload reference documents (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            with st.spinner("Processing & indexing PDF..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                build_retriever(tmp_path)
                st.session_state.last_uploaded = uploaded_file.name
                st.success(f"✓ {uploaded_file.name} successfully indexed!")
    
    st.markdown("---")
    if st.button("🗑 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main Header
st.title("Nexus Agent")
st.caption("Autonomous Self-Correcting RAG System with Real-Time Web Fallback")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask a question about your documents or any general topic..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        with status_placeholder.status("⚙️ Executing Autonomous Pipeline...", expanded=True) as status:
            inputs = {"question": prompt, "retry_count": 0}
            state_history = []
            final_output = None

            start_time = time.time()
            for output in nexus_app.stream(inputs):
                for key, value in output.items():
                    state_history.append(f"• Node **`{key}`** completed")
                    if key == "grade_documents":
                        status.write(f"⚖️ Grading relevance (Trigger Web Search: `{value.get('web_search', 'No')}`)")
                    elif key == "transform_query":
                        status.write("🔄 Query transformed for Web Search")
                    elif key == "web_search":
                        status.write("🌐 Live Web Search executed")
                    elif key == "generate":
                        final_output = value.get("generation")
                        status.write("✨ Synthesizing final response...")

            elapsed = round(time.time() - start_time, 2)
            status.update(label=f"✓ Answer synthesized in {elapsed}s", state="complete", expanded=False)

        if final_output:
            st.markdown(final_output)
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
            with st.expander("🔍 Agent Execution & Verification Trace"):
                for step in state_history:
                    st.markdown(step)