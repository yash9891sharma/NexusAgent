from langgraph.graph import END, StateGraph
from src.state import GraphState
from src.nodes import (
    retrieve,
    grade_documents,
    generate,
    transform_query,
    fallback_search
)

def decide_to_generate(state: GraphState):
    web_search = state.get("web_search")
    if web_search == "Yes":
        return "transform_query"
    return "generate"

workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("transform_query", transform_query)
workflow.add_node("web_search", fallback_search)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate"
    }
)
workflow.add_edge("transform_query", "web_search")
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

nexus_app = workflow.compile()