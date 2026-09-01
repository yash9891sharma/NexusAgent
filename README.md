# ⚡ Nexus Agent: Self-Correcting Agentic RAG System
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://yash-nexus-agent.streamlit.app)

An intelligent, self-correcting Retrieval-Augmented Generation (RAG) agent built with **LangGraph**, **Groq (Qwen)**, **ChromaDB**, and **Tavily Web Search**.

## 🚀 Key Features
- **Local Document Retrieval**: Fast semantic search over custom PDF resumes using ChromaDB.
- **Document Grading Node**: LLM evaluator grades context relevance before generating answers.
- **Dynamic Fallback & Web Search**: Automatically searches live internet via Tavily when context is missing locally.
- **Anti-Hallucination Checks**: Self-evaluates output to eliminate AI hallucinations.
- **Interactive Streamlit UI**: Real-time chat interface with dynamic document re-indexing.

## 🛠️ How to Run Locally

1. Clone repo & install requirements:
   ```bash
   pip install -r requirements.txt