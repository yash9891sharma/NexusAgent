import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Fast & stable grader model
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

grader_prompt = PromptTemplate(
    template="""You are an expert document relevance evaluator.

Document excerpt:
{document}

User question:
{question}

Evaluate if the document excerpt contains relevant information, context, or keywords to help answer the user question.
Respond with ONLY 'yes' or 'no'. Do not add any explanation or punctuation.""",
    input_variables=["document", "question"]
)

# Robust grading chain (Crash-proof without tool calling)
structured_doc_grader = grader_prompt | llm