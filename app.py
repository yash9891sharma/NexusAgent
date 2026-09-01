import os
import time
import streamlit as st
from src.graph import nexus_app

# --- Page Configuration ---
st.set_page_config(
    page_title="Nexus Agent | Autonomous RAG",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Gemini-Inspired Custom Styling ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Header Gradient */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 25px;
    }
    
    /* Chat Message Bubbles */
    .stChatMessage {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 12px;
    }
    
    /* Status & Chips */
    .badge-chip {
        display: inline-block;
        padding: 4px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 20px;
        background-color: #21262d;
        color: #58a6ff;
        border: 1px solid #30363d;
        margin-right: 6px;
    }
    
    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #090d13;
        border-right: 1px solid #21262d;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Setup ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar Controls ---
with st.sidebar:
    # Top Logo + Sharp Title
    st.markdown("""
        <div style="text-align: center; margin-bottom: 15px;">
            <img src="https://raw.githubusercontent.com/yash9891sharma/NexusAgent/main/logo.png" 
                 style="width: 90px; height: 90px; object-fit: cover; border-radius: 16px; box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);">
            <h2 style="color: #f8fafc; font-size: 1.3rem; margin-top: 10px; margin-bottom: 2px; font-weight: 700;">NEXUS AGENT</h2>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Autonomous RAG Pipeline</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="display:flex; justify-content:center; gap:6px; margin-bottom:15px;"><span class="badge-chip">Groq: Qwen-2.5-32B</span><span class="badge-chip">LangGraph</span></div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("#### 📄 Knowledge Base")
    uploaded_file = st.file_uploader("Upload reference documents (PDF)", type=["pdf"])
    if uploaded_file:
        st.success(f"Loaded: `{uploaded_file.name}`")
        
    st.divider()
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Interface ---
st.markdown('<div class="hero-title">Nexus Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Autonomous Self-Correcting RAG System with Real-Time Web Fallback</div>', unsafe_allow_html=True)

# Render Chat History
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "✨"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "trace" in message and message["trace"]:
            with st.expander("🔍 Agent Execution & Verification Trace", expanded=False):
                st.caption(message["trace"])

# User Input Handling
if prompt := st.chat_input("Ask a question about your documents or any real-time topic..."):
    # Display user query
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Assistant Response Generation
    with st.chat_message("assistant", avatar="✨"):
        with st.status("🧠 Agent thinking...", expanded=True) as status:
            start_time = time.time()
            
            st.write("🔍 Querying Vector Database...")
            inputs = {"question": prompt}
            
            # Execute LangGraph Workflow
            state_history = []
            final_output = None
            for output in nexus_app.stream(inputs):
                for key, value in output.items():
                    state_history.append(f"• Node **`{key}`** executed.")
                    if key == "grade_documents":
                        st.write("⚖️ Grading document relevance & hallucination check...")
                    elif key == "transform_query":
                        st.write("🔄 Reformulating query for internet search...")
                    elif key == "web_search":
                        st.write("🌐 Fetching external context via Tavily...")
                    elif key == "generate":
                        st.write("✨ Generating synthesized grounded answer...")
                        final_output = value.get("generation")
            
            elapsed = time.time() - start_time
            status.update(label=f"Answer synthesized in {elapsed:.2f}s", state="complete", expanded=False)

        # Fallback if no generation node captured
        answer_text = final_output if final_output else "Unable to generate a valid response."
        st.markdown(answer_text)
        
        # Save to session history
        trace_summary = "\n".join(state_history)
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer_text,
            "trace": trace_summary
        })