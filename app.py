from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from nodes.generators import rag_generate, plain_answer
from nodes.retrievers import web_search, retrieve
from nodes.graders import route_question, retrieval_grade, route_retrieval, grade_rag_generation, update_web_search, update_rag_generate
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
    workflow.add_node("update_web_search", update_web_search)
    workflow.add_node("update_rag_generate", update_rag_generate)

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

    workflow.add_edge("update_web_search", "web_search")
    workflow.add_edge("update_rag_generate", "rag_generate")

    workflow.add_conditional_edges(
        "retrieval_grade",
        route_retrieval,
        {
            "web_search": "update_web_search",
            "rag_generate": "rag_generate",
            "plain_answer": "plain_answer",
        },
    )

    workflow.add_conditional_edges(
        "rag_generate",
        grade_rag_generation,
        {
            "not supported": "update_rag_generate",
            "not useful": "update_web_search",
            "useful": END,
            "plain_answer": "plain_answer",
        },
    )

    workflow.add_edge("plain_answer", END)

    return workflow.compile()


def run_query(question: str):
    """執行查詢"""
    app = create_workflow()
    inputs = {
        "question": question,
        "retry_count": 0
    }

    output = None  # 初始化 output 變數
    for output in app.stream(inputs):
        print("\n")

    if output is None:  # 檢查是否有輸出
        return "抱歉，無法處理您的問題"

    if "rag_generate" in output:
        return output["rag_generate"]["generation"]
    elif "plain_answer" in output:
        return output["plain_answer"]["generation"]


app = FastAPI(title="機車交通法規問答系統")

# 允許跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定義請求和回應的資料模型


class Question(BaseModel):
    text: str


class Answer(BaseModel):
    response: str


@app.post("/query", response_model=Answer)
async def get_answer(question: Question):
    """處理問答請求"""
    try:
        answer = run_query(question.text)
        return Answer(response=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 修改啟動方式
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
