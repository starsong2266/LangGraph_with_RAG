from services.llm import get_openai_llm
from nodes.generators import rag_generate, plain_answer
from nodes.retrievers import web_search, retrieve
from nodes.graders import route_question, retrieval_grade, route_retrieval, grade_rag_generation
from models.state import GraphState
from langgraph.graph import StateGraph, END


def create_workflow():
    """創建工作流程圖"""
    workflow = StateGraph(GraphState)

    # 添加節點
    workflow.add_node("web_search", web_search)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("retrieval_grade", retrieval_grade)
    workflow.add_node("rag_generate", rag_generate)
    workflow.add_node("plain_answer", plain_answer)

    # 設置條件入口
    workflow.set_conditional_entry_point(
        route_question,
        {
            "web_search": "web_search",
            "vectorstore": "retrieve",
            "plain_answer": "plain_answer",
            "end": END,
        },
    )

    workflow.add_edge("retrieve", "retrieval_grade")
    workflow.add_edge("web_search", "retrieval_grade")

    workflow.add_conditional_edges(
        "retrieval_grade",
        route_retrieval,
        {
            "web_search": "web_search",
            "rag_generate": "rag_generate",
        },
    )

    workflow.add_conditional_edges(
        "rag_generate",
        grade_rag_generation,
        {
            "not supported": "rag_generate",
            "not useful": "web_search",
            "useful": END,
        },
    )

    workflow.add_edge("plain_answer", END)

    return workflow.compile()


def run_query(question: str):
    """執行查詢"""
    app = create_workflow()
    inputs = {"question": question}

    for output in app.stream(inputs):
        print("\n")

    if "rag_generate" in output:
        return output["rag_generate"]["generation"]
    elif "plain_answer" in output:
        return output["plain_answer"]["generation"]
    else:
        return "不回答該問題"


if __name__ == "__main__":
    # 執行查詢
    question = "駕照更換規定?"
    answer = run_query(question)
    print(answer)
