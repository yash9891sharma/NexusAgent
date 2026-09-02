import os
import time
import base64
import tempfile
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Nexus AI | Autonomous Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Auto-Clean API Keys ---
for key in ["GROQ_API_KEY", "TAVILY_API_KEY"]:
    if key in st.secrets:
        raw_val = str(st.secrets[key])
        os.environ[key] = "".join(raw_val.split()).strip('"\'')

from src.graph import nexus_app
from src.nodes import build_retriever

# --- High-Tech Modern Cyberpunk Theme Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Dark Canvas */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0d1322 0%, #05070d 100%) !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Ambient Cyber Grid Overlay */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(rgba(0, 242, 254, 0.02) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 242, 254, 0.02) 1px, transparent 1px);
        background-size: 30px 30px;
        pointer-events: none;
        z-index: 0;
    }

    /* Remove Streamlit default top blank padding from sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(9, 14, 26, 0.95) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.2) !important;
    }
    
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0.8rem !important;
    }

    [data-testid="stSidebarContent"] {
        padding-top: 0.8rem !important;
    }

    /* Pure Centered Logo Wrapper */
    .sidebar-logo-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-top: 0px;
        margin-bottom: 12px;
        text-align: center;
    }

    .sidebar-logo-box img {
        width: 165px !important;
        height: auto !important;
        display: block;
        margin: 0 auto !important;
    }

    /* Centered Badges */
    .badge-container {
        display: flex;
        justify-content: center;
        gap: 6px;
        margin-top: 6px;
        margin-bottom: 18px;
    }

    .badge-pill {
        display: inline-block;
        padding: 3px 9px;
        font-size: 11px;
        font-weight: 600;
        border-radius: 4px;
        border: 1px solid #00f2fe;
        color: #00f2fe;
        background: rgba(0, 242, 254, 0.1);
    }

    /* Glassmorphism Chat Bubble Containers */
    .stChatMessage {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(0, 242, 254, 0.15) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(8px) !important;
        margin-bottom: 12px !important;
    }

    div[data-testid="stChatMessage"]:nth-child(odd) {
        border-left: 3px solid #4facfe !important;
    }

    div[data-testid="stChatMessage"]:nth-child(even) {
        border-left: 3px solid #00f2fe !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.08) !important;
    }

    /* Terminal Input Bar */
    div[data-testid="stChatInput"] input {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        border-radius: 8px !important;
        color: #00f2fe !important;
    }

    div[data-testid="stChatInput"] input:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.25) !important;
    }
</style>
""", unsafe_allow_html=True)

# Function to encode local SVG/PNG to Base64 (guarantees centered display)
def get_logo_html():
    file_path = "logo.svg" if os.path.exists("logo.svg") else ("logo.png" if os.path.exists("logo.png") else None)
    if not file_path:
        return ""
    mime = "image/svg+xml" if file_path.endswith(".svg") else "image/png"
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f'''
        <div class="sidebar-logo-box">
            <img src="data:{mime};base64,{data}" alt="Nexus Logo">
        </div>
    '''

# --- Sidebar Deck ---
with st.sidebar:
    st.markdown(get_logo_html(), unsafe_allow_html=True)

    st.markdown("""
        <div class="badge-container">
            <span class="badge-pill">Autonomous RAG</span>
            <span class="badge-pill">Llama-3.1</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📁 Upload Documents")
    uploaded_file = st.file_uploader("Upload PDF to index into knowledge base", type=["pdf"])
    
    if uploaded_file is not None:
        if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            with st.spinner("Processing & indexing document..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                build_retriever(tmp_path)
                st.session_state.last_uploaded = uploaded_file.name
                st.success(f"✓ Ready: {uploaded_file.name}")

    st.markdown("---")
    st.markdown("### ⚙️ System Features")
    st.markdown("• **LLM Model:** Groq Llama-3.1-8B")
    st.markdown("• **Embeddings:** MiniLM-L6-v2")
    st.markdown("• **Vector DB:** ChromaDB Vector Store")
    st.markdown("• **Web Search:** Tavily Fallback Engine")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Dashboard Header ---
col1, col2 = st.columns([0.78, 0.22])
with col1:
    st.markdown("""
        <h1 style="font-family: 'Orbitron', sans-serif; font-size: 32px; font-weight: 800; 
                   background: linear-gradient(90deg, #00f2fe, #4facfe); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px;">
            Nexus Autonomous AI
        </h1>
    """, unsafe_allow_html=True)
    st.caption("Ask questions about your uploaded documents or any real-time topic.")
with col2:
    st.markdown("""
        <div style="text-align: right; padding-top: 15px;">
            <span style="color: #22c55e; font-size: 13px; font-weight: 600;">● System Ready</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Query Execution Pipeline
if prompt := st.chat_input("Type your question here (PDF or general knowledge)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        with status_placeholder.status("⚙️ Thinking & checking documents...", expanded=True) as status:
            inputs = {"question": prompt, "retry_count": 0}
            state_history = []
            final_output = None

            start_time = time.time()
            for output in nexus_app.stream(inputs):
                for key, value in output.items():
                    if key == "retrieve":
                        status.write("📄 Searching relevant context in documents...")
                        state_history.append("• Step 1: Checked document vector store")
                    elif key == "grade_documents":
                        is_web = value.get('web_search', 'No')
                        status.write(f"⚖️ Evaluating document relevance (Need Web Search: `{is_web}`)")
                        state_history.append(f"• Step 2: Graded document relevance (Web Search = {is_web})")
                    elif key == "transform_query":
                        status.write("🔄 Re-phrasing query for online search...")
                        state_history.append("• Step 3: Optimized search keywords for web fallback")
                    elif key == "web_search":
                        status.write("🌐 Fetching real-time information from web...")
                        state_history.append("• Step 4: Searched live internet via Tavily API")
                    elif key == "generate":
                        final_output = value.get("generation")
                        status.write("✨ Synthesizing final answer...")
                        state_history.append("• Step 5: Generated final response with Groq LLM")

            elapsed = round(time.time() - start_time, 2)
            status.update(label=f"✓ Done in {elapsed}s", state="complete", expanded=False)

        if final_output:
            st.markdown(final_output)
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
            with st.expander("🔍 See Step-by-Step AI Execution Trace"):
                for step in state_history:
                    st.markdown(step)