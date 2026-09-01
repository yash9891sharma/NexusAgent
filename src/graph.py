from langgraph.graph import StateGraph, END
from src.state import GraphState
from src.nodes import retrieve, grade_documents, generate, transform_query, fallback_search
from src.graders import structured_hallucination_grader, structured_answer_grader

def decide_to_generate(state: GraphState):
    if state.get("web_search") == "Yes":
        return "transform_query"
    return "generate"

def grade_generation(state: GraphState):
    print("--- [EVALUATION] Checking hallucination & answer quality ---")
    retry_count = state.get("retry_count", 0)

    # Loop guardrail (max 2 retries)
    if retry_count >= 2:
        print("--- [GUARD] Max retries reached. Returning output ---")
        return "useful"

    documents = state.get("documents", [])
    generation = state.get("generation", "")
    question = state.get("question", "")

    context_text = "\n\n".join([d.page_content for d in documents])
    
    try:
        # Hallucination check
        h_score = structured_hallucination_grader.invoke(
            f"Facts:\n{context_text}\n\nAnswer:\n{generation}"
        )
        if h_score.binary_score.lower() != "yes":
            print("--- [RE-TRY] Generation not grounded. Regenerating... ---")
            return "not_grounded"
        
        # Utility check
        a_score = structured_answer_grader.invoke(
            f"Question:\n{question}\n\nAnswer:\n{generation}"
        )
        if a_score.binary_score.lower() == "yes":
            print("--- [SUCCESS] Answer is accurate & useful! ---")
            return "useful"
        else:
            return "not_useful"
    except Exception:
        # Fallback if structured parsing hits a schema edge case
        return "useful"

# Graph Construction
workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_node("transform_query", transform_query)
workflow.add_node("fallback_search", fallback_search)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")

workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)

workflow.add_edge("transform_query", "fallback_search")
workflow.add_edge("fallback_search", "generate")

workflow.add_conditional_edges(
    "generate",
    grade_generation,
    {
        "not_grounded": "generate",
        "not_useful": "transform_query",
        "useful": END,
    },
)

nexus_app = workflow.compile()