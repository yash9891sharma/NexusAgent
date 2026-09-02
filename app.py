import os
import time
import base64
import tempfile
from PIL import Image
import streamlit as st

# --- Auto-Clean API Keys ---
for key in ["GROQ_API_KEY", "TAVILY_API_KEY"]:
    if key in st.secrets:
        raw_val = str(st.secrets[key])
        os.environ[key] = "".join(raw_val.split()).strip('"\'')

# --- Robust Favicon Loader ---
fav_icon = "⚡"
if os.path.exists("logo.png"):
    try:
        fav_icon = Image.open("logo.png")
    except Exception:
        fav_icon = "⚡"

# --- Page Configuration ---
st.set_page_config(
    page_title="Nexus AI | Engineered by Yash Sharma",
    page_icon=fav_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)
from src.graph import nexus_app
from src.nodes import build_retriever

# --- Futuristic Cyberpunk Styling ---
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

    /* Sidebar Alignment & Shift Upwards */
    section[data-testid="stSidebar"] {
        background-color: rgba(9, 14, 26, 0.95) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.2) !important;
    }

    section[data-testid="stSidebar"] .block-container,
    [data-testid="stSidebarContent"] {
        padding-top: 0.8rem !important;
    }

    /* Centered Logo Box */
    .sidebar-logo-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-top: 0px;
        margin-bottom: 10px;
        text-align: center;
    }

    .sidebar-logo-box img {
        width: 155px !important;
        height: auto !important;
        display: block;
        margin: 0 auto !important;
    }

    /* Centered Badges */
    .badge-container {
        display: flex;
        justify-content: center;
        gap: 6px;
        margin-top: 4px;
        margin-bottom: 16px;
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

    /* Chat Bubbles */
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

    /* Terminal Chat Input */
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

# Function to encode logo for zero-margin centered rendering
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
    st.markdown("### ⚙️ System Architecture")
    st.markdown("• **LLM Model:** Groq Llama-3.1-8B")
    st.markdown("• **Embeddings:** MiniLM-L6-v2")
    st.markdown("• **Vector DB:** ChromaDB Vector Store")
    st.markdown("• **Web Search:** Tavily Fallback Engine")

    # Developer Signature Card
    st.markdown("---")
    st.markdown("""
        <div style="padding: 12px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 10px; text-align: center;">
            <div style="font-size: 11px; color: #64748b; letter-spacing: 1px; text-transform: uppercase;">Lead Engineer</div>
            <div style="font-family: 'Orbitron', sans-serif; font-size: 15px; font-weight: 700; color: #ffffff; margin: 4px 0;">Yash Sharma</div>
            <div style="font-size: 11px; color: #00f2fe;">Autonomous AI & RAG Specialist</div>
        </div>
    """, unsafe_allow_html=True)

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
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 2px;">
            Nexus Autonomous AI
        </h1>
        <div style="font-size: 13px; color: #94a3b8; margin-bottom: 8px;">
            Engineered & Built by <span style="color: #00f2fe; font-weight: 600;">Yash Sharma</span> 
            <span style="background: rgba(0,242,254,0.12); color: #00f2fe; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 6px; border: 1px solid rgba(0,242,254,0.3);">CREATOR</span>
        </div>
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