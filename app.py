import os
import time
import tempfile
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="NEXUS // AUTONOMOUS AI HUD",
    page_icon="💠",
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

# --- High-Tech Cyberpunk & Neon HUD Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=JetBrains+Mono:wght@300;400;600&display=swap');

    /* Global Background & Fonts */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0d1322 0%, #05070d 100%) !important;
        color: #e0f2fe !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Grid Overlay Pattern */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(rgba(0, 242, 254, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 242, 254, 0.03) 1px, transparent 1px);
        background-size: 35px 35px;
        pointer-events: none;
        z-index: 0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(7, 11, 20, 0.95) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.2) !important;
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.8) !important;
    }

    /* Cyber Title & Badges */
    .cyber-logo {
        font-family: 'Orbitron', sans-serif;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #00f2fe, #4facfe, #00c6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
    }

    .hud-badge {
        display: inline-block;
        padding: 3px 10px;
        font-size: 11px;
        border-radius: 4px;
        border: 1px solid #00f2fe;
        color: #00f2fe;
        background: rgba(0, 242, 254, 0.1);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-right: 5px;
    }

    /* Modern Glass Chat Bubbles */
    .stChatMessage {
        background: rgba(13, 20, 36, 0.75) !important;
        border: 1px solid rgba(0, 242, 254, 0.15) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 14px !important;
    }

    /* User Message Highlight */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        border-left: 3px solid #4facfe !important;
    }

    /* Assistant Message Highlight */
    div[data-testid="stChatMessage"]:nth-child(even) {
        border-left: 3px solid #00f2fe !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.08) !important;
    }

    /* Input Field Styling */
    div[data-testid="stChatInput"] input {
        background: rgba(10, 16, 30, 0.9) !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        border-radius: 8px !important;
        color: #00f2fe !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    div[data-testid="stChatInput"] input:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.3) !important;
    }

    /* Expander / Trace Telemetry */
    .streamlit-expanderHeader {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(0, 242, 254, 0.2) !important;
        border-radius: 6px !important;
        color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Deck ---
with st.sidebar:
    st.markdown('<div class="cyber-logo">NEXUS // SYS</div>', unsafe_allow_html=True)
    st.markdown("""
        <div>
            <span class="hud-badge">V2.4 ONLINE</span>
            <span class="hud-badge">LLAMA-3.1</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 🛰 DATA INGESTION DECK")
    uploaded_file = st.file_uploader("Mount Reference Vector (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            with st.spinner("Extracting tokens & mapping vector space..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                build_retriever(tmp_path)
                st.session_state.last_uploaded = uploaded_file.name
                st.success(f"DATA MATRIX MOUNTED: {uploaded_file.name}")

    st.markdown("---")
    st.markdown("### ⚙️ SYSTEM TELEMETRY")
    st.markdown("• Node Routing: `Autonomous Dynamic`")
    st.markdown("• Vector Engine: `ChromaDB ChromaEngine`")
    st.markdown("• Fallback Mode: `Tavily Live Web Search`")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("RESET MEMORY BUFFER", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main HUD Dashboard ---
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown('<h1 class="cyber-logo" style="font-size: 38px;">NEXUS AGENT HUD</h1>', unsafe_allow_html=True)
    st.markdown("`AUTONOMOUS RAG ENGINE // SELF-CORRECTING LOGIC // LIVE WEB INTEGRATION`")
with col2:
    st.markdown("""
        <div style="text-align: right; padding-top: 15px;">
            <span style="color: #22c55e; font-size: 13px;">● SYSTEM STATUS: NOMINAL</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Render Chat Thread ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Command Loop ---
if prompt := st.chat_input("Input system command or query database..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        with status_placeholder.status("⚡ [PIPELINE ENGAGED] Routing Execution Graph...", expanded=True) as status:
            inputs = {"question": prompt, "retry_count": 0}
            state_history = []
            final_output = None

            start_time = time.time()
            for output in nexus_app.stream(inputs):
                for key, value in output.items():
                    state_history.append(f"`[TRACE]` Node completed: **`{key.upper()}`**")
                    if key == "grade_documents":
                        status.write(f"⚖️ Document Grading: Route Search = `{value.get('web_search', 'No')}`")
                    elif key == "transform_query":
                        status.write("🔄 Query Query Vector Re-optimized")
                    elif key == "web_search":
                        status.write("🌐 Live Web Fallback Extracted")
                    elif key == "generate":
                        final_output = value.get("generation")
                        status.write("✨ Synthesizing Neural Output...")

            elapsed = round(time.time() - start_time, 2)
            status.update(label=f"✔ [EXECUTION COMPLETE] Synthesized in {elapsed}s", state="complete", expanded=False)

        if final_output:
            st.markdown(final_output)
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
            with st.expander("📡 AGENT TELEMETRY & EXECUTION TRACE"):
                for step in state_history:
                    st.markdown(step)