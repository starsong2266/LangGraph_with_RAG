from typing import List, Optional, TypedDict
from langchain.schema import Document


class GraphState(TypedDict):
    """圖狀態類別"""
    question: str
    generation: Optional[str]
    documents: Optional[List[Document]]
    retry_count: Optional[int]
