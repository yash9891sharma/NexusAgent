import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Universal free-tier model on Groq
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

grader_prompt = PromptTemplate(
    template="""You are an expert document evaluator.

Document excerpt:
{document}

Question:
{question}

Does this document excerpt contain relevant information to answer the question?
Reply ONLY with 'yes' or 'no'.""",
    input_variables=["document", "question"]
)

structured_doc_grader = grader_prompt | llm