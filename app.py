import streamlit as st
import time
import tempfile
import os

# --- BACKEND IMPORTS ---
from src.graph import nexus_app
from src.nodes import build_retriever 

# --- STREAMING FUNCTION ---
def stream_text(text):
    """Creates a typewriter effect for the final text output."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Nexus Autonomous AI", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR & ARCHITECTURE ---
    # --- SIDEBAR & ARCHITECTURE ---
with st.sidebar:
    st.markdown("### 📁 Upload Documents")
    st.markdown("<span style='font-size: 12px;'>Upload PDF to index into knowledge base</span>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["pdf"])
    if uploaded_file is not None:
        if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            with st.spinner("Processing & indexing document..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                build_retriever(tmp_path)
                st.session_state.last_uploaded = uploaded_file.name
                st.success(f"Ready: {uploaded_file.name}")

    st.markdown("---")
    st.markdown("### ⚙️ System Architecture")
    st.markdown("• **LLM Model:** Google Gemini 3.6 Flash")
    st.markdown("• **Embeddings:** MiniLM-L6-v2")
    st.markdown("• **Vector DB:** ChromaDB Vector Store")
    st.markdown("• **Web Search:** Tavily Fallback Engine")
    
    st.markdown("---")
    # Developer Signature Card
    st.markdown("""
        <div style="padding: 12px; background: rgba(15, 23, 42, 0.7); border-radius: 8px; text-align: center; border: 1px solid #1e293b;">
            <div style="font-size: 11px; color: #64748b; letter-spacing: 1px; text-transform: uppercase;">Lead Engineer</div>
            <div style="font-family: 'Orbitron', sans-serif; font-size: 16px; font-weight: bold; color: #ffffff; margin: 4px 0;">Yash Sharma</div>
            <div style="font-size: 11px; color: #00f2fe;">Autonomous AI & RAG Specialist</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
   # 1. Clear Chat Button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []

    # 2. Save Session Feature (Safe check ke sath)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💾 Save Session")
    
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        chat_export = "Nexus Autonomous AI - Session History\n"
        chat_export += "="*40 + "\n\n"
        
        for msg in st.session_state.messages:
            role = "🧑‍💻 USER" if msg["role"] == "user" else "🤖 NEXUS"
            chat_export += f"{role}:\n{msg['content']}\n\n"
            chat_export += "-"*40 + "\n"
            
        st.download_button(
            label="📥 Download Chat Log",
            data=chat_export,
            file_name="nexus_session.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("Start chatting to enable download.")

import base64

# --- MAIN CHAT HEADER ---
# Logo file ko securely HTML mein dikhane ke liye function
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    img_b64 = get_base64_image("logo.svg")
    img_html = f'<img src="data:image/svg+xml;base64,{img_b64}" width="220" style="margin-bottom: 15px;">'
except FileNotFoundError:
    img_html = "" # Agar logo nahi mila toh crash nahi hoga

# Logo aur Title dono ko ek hi Center-Aligned block mein lock kar diya
st.markdown(
    f"""
    <div style="text-align: center;">
        {img_html}
        <h1 style="margin-bottom: 10px; margin-top: 0px;">Nexus Autonomous AI</h1>
        <p style="font-size: 15px; color: #a1a1aa;">
            Engineered & Built by <b style="color: white;">Yash Sharma</b> <code style="font-size: 12px;">CREATOR</code><br>
            Ask questions about your uploaded documents or any real-time topic.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()
# --- CHAT HISTORY INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DISPLAY CLEAN CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "trace" in message and message["trace"]:
            with st.expander("🛠️ View AI Execution Trace"):
                st.markdown(message["trace"])

# --- CHAT INPUT & LIVE GENERATION ---
if prompt := st.chat_input("Type your question here (PDF or general knowledge)..."):
    
    # 1. User Message Display & Save
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

# 2. Assistant Message Generation with True Token Streaming
with st.chat_message("assistant"):
    inputs = {"question": prompt}
    trace_text = "Execution trace unavailable."
    
    # Ek temporary placeholder live node updates ke liye
    status_placeholder = st.empty()
    
    try:
        # Generator function jo LangGraph se direct live tokens stream karega safely
        def token_generator():
            final_gen = ""
            for msg, metadata in nexus_app.stream(inputs, stream_mode="messages"):
                node_info = metadata.get("langgraph_node", "processing")
                status_placeholder.text(f"⚡ Running node: {node_info}...")
                
                if msg.content:
                    # Handle both string and list content safely
                    chunk_str = ""
                    if isinstance(msg.content, list):
                        for part in msg.content:
                            if isinstance(part, dict) and "text" in part:
                                chunk_str += part["text"]
                            else:
                                chunk_str += str(part)
                    else:
                        chunk_str = str(msg.content)
                    
                    final_gen += chunk_str
                    yield chunk_str
            
            # Streaming khatam hote hi status placeholder hata dein
            status_placeholder.empty()
            st.session_state.temp_final_response = final_gen

        # Streamlit ka built-in st.write_stream live generator ke sath
        st.write_stream(token_generator())
        
        # Fallback response variable from session state
        final_response = getattr(st.session_state, "temp_final_response", "Response generated.")
        
        # Hide the execution trace in an expander
        with st.expander("🛠️ View AI Execution Trace"):
            st.markdown("Node execution completed successfully via stream pipeline.")
            
        # 3. Save Assistant Message to History
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_response,
            "trace": "Execution trace captured."
        })
        
    except Exception as e:
        status_placeholder.empty()
        error_msg = str(e)
        
        # 1. Rate Limit (429) Error check
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.warning("⚠️ **API Rate Limit Reached:** Google Gemini ki free tier limit exceed ho gayi hai. Kripya thodi der baad try karein ya billing check karein.")
        
        # 2. Authentication / API Key Error check
        elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
            st.error("🔑 **Authentication Error:** Aapki API key invalid ya expire ho chuki hai. Kripya apni valid API key update karein.")
        
        # 3. Any other unexpected error
        else:
            st.error(f"❌ **Execution Failed:** {error_msg}")