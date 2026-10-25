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
if "uploaded_files_list" not in st.session_state:
    st.session_state.uploaded_files_list = []

if "messages" not in st.session_state:
    st.session_state.messages = []

    # Follow-up click tracker
if "followup_clicked" not in st.session_state:
    st.session_state.followup_clicked = None
import uuid

# Graph ki memory ke liye thread ID
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Yeh config hum apne graph ko pass karenge
config = {"configurable": {"thread_id": st.session_state.thread_id}}
# --- SIDEBAR & ARCHITECTURE ---
with st.sidebar:
    st.markdown("### 📂 Upload Documents")
    st.markdown("<span style='font-size: 12px;'>Upload PDF to index into knowledge base</span>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["pdf"])
    if uploaded_file is not None:
        # Check karein ki file pehle se list mein hai ya nahi taaki duplicate entry na ho
        if uploaded_file.name not in st.session_state.uploaded_files_list:
            with st.spinner("Processing & indexing document..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                build_retriever(tmp_path)
                st.session_state.uploaded_files_list.append(uploaded_file.name)
                st.success(f"Ready: {uploaded_file.name}")

    # --- INDEXED DOCUMENTS STATUS TRACKER ---
    st.markdown("---")
    st.markdown("### 📚 Indexed Knowledge Base")
    
    if st.session_state.uploaded_files_list:
        for file_name in st.session_state.uploaded_files_list:
            st.markdown(f"✅ <span style='font-size: 13px; color: #e2e8f0;'>{file_name}</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span style='font-size: 12px; color: #94a3b8;'>No documents indexed yet.</span>", unsafe_allow_html=True)
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
    # Seedha inline condition likhi hai, koi variable nahi banaya
    with st.chat_message(message["role"], avatar="logo.svg" if message["role"] == "assistant" else None):
        st.markdown(message["content"])
        if "trace" in message and message["trace"]:
            with st.expander("🛠️ View AI Execution Trace"):
                st.markdown(message["trace"])
# --- CHAT INPUT & LIVE GENERATION ---
user_input = st.chat_input("Type your question here (PDF or general knowledge)...")

# Override input agar kisi follow-up button par click hua hai
if st.session_state.get("followup_clicked"):
    prompt = st.session_state.followup_clicked
    st.session_state.followup_clicked = None
else:
    prompt = user_input
# --- AUTOMATIC CHAT EXECUTION ---
if prompt:
    # 1. User ka question turant screen par dikhayein
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Assistant ka response generate karein (Bina kisi Yes/No button ke)
    with st.chat_message("assistant", avatar="logo.svg"):
        status_placeholder = st.empty()
        
        try:
            status_placeholder.text("⚡ Nexus Agent is thinking...")
            
            inputs = {"question": prompt}
            final_state = nexus_app.invoke(inputs)
            status_placeholder.empty()
            
            final_response = final_state.get("generation", "Error: Could not generate answer.")
            trace_text = final_state.get("trace", "Autonomous execution completed.")

            st.markdown(final_response)
            
            with st.expander("🛠️ View AI Execution Trace"):
                st.markdown(trace_text)
                
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_response,
                "trace": trace_text
            })
            
        except Exception as e:
            status_placeholder.empty()
            st.error(f"❌ System Error: {str(e)}")