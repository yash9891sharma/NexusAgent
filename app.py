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
    
    # 1. Clear Chat Button (Ab sirf ek baar hai)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []

    # 2. Save Session Feature
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💾 Save Session")
    
    if len(st.session_state.messages) > 0:
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

    # 2. Assistant Message Generation with Live Streaming
    with st.chat_message("assistant"):
        inputs = {"question": prompt}
        final_state = None
        
        # Status container to show live LangGraph node execution
        with st.status("Initializing Nexus Agent...", expanded=True) as status:
            try:
                # Stream outputs from the LangGraph nodes
                for output in nexus_app.stream(inputs):
                    for node_name, node_state in output.items():
                        status.update(label=f"Executing node: **{node_name}**...", state="running")
                        final_state = node_state
                
                status.update(label="Graph execution complete!", state="complete")
                
                # Extract final values
                if final_state:
                    final_response = final_state.get("generation", "Error: No response generated.")
                    trace_text = final_state.get("trace", "Execution trace unavailable.")
                else:
                    final_response = "Error: System returned an empty state."
                    trace_text = ""

                # Write final response using typewriter effect
                st.write_stream(stream_text(final_response))
                
                # Hide the execution trace in an expander
                with st.expander("🛠️ View AI Execution Trace"):
                    st.markdown(trace_text)
                    
                # 3. Save Assistant Message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_response,
                    "trace": trace_text
                })

            except Exception as e:
                status.update(label="Execution Failed", state="error")
                st.error(f"An error occurred: {str(e)}")