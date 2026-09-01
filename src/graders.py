import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

# Active Groq Model
eval_llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# 1. Document Relevance Grader
class GradeDocuments(BaseModel):
    """Retrieved document relevant hai ya nahi."""
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

structured_doc_grader = eval_llm.with_structured_output(GradeDocuments)

# 2. Hallucination Grader
class GradeHallucinations(BaseModel):
    """Answer context facts par based hai ya nahi."""
    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

structured_hallucination_grader = eval_llm.with_structured_output(GradeHallucinations)

# 3. Answer Utility Grader
class GradeAnswer(BaseModel):
    """Answer question ko resolve karta hai ya nahi."""
    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

structured_answer_grader = eval_llm.with_structured_output(GradeAnswer)