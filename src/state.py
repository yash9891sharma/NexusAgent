from typing import List, TypedDict

class GraphState(TypedDict):
    """
    Nexus Agent state schema
    """
    question: str
    generation: str
    web_search: str
    documents: List[str]
    retry_count: int