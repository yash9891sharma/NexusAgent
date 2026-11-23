from typing import List
from typing_extensions import TypedDict
from langchain_core.documents import Document

class GraphState(TypedDict):
    question: str
    generation: str
    web_search: str
    documents: List[Document]
    retry_count: int
    route: str          # <--- Yeh line add karni hai (Routing ke liye)
    trace: str          # <--- Yeh line add karni hai (Trace text ke liye)