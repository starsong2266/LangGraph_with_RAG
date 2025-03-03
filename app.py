from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from nodes.generators import rag_generate, plain_answer
from nodes.retrievers import web_search, retrieve
from nodes.graders import route_question, retrieval_grade, route_retrieval, grade_rag_generation, update_web_search, update_rag_generate
from models.state import GraphState
from langgraph.graph import StateGraph, END
from psycopg_pool import ConnectionPool
from config.config import DB_URI
from contextlib import asynccontextmanager
from typing import List
from datetime import datetime
from langgraph.checkpoint.postgres import PostgresSaver
import json

# 添加全局連接池
_pool = None


def get_connection_pool():
    """獲取全局連接池"""
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=DB_URI,
            max_size=20,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
            },
        )
    return _pool


def create_postgres_saver():
    try:
        pool = get_connection_pool()
        postgres_saver = PostgresSaver(pool)
        postgres_saver.setup()
        return postgres_saver
    except Exception as e:
        print(f"創建 PostgresSaver 時發生錯誤: {str(e)}")
        raise


def setup_database():
    """設置資料庫表格"""
    try:
        pool = get_connection_pool()
        with pool.connection() as conn:
            with conn.cursor() as cur:
                # 創建對話歷史表格
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        conversation_id TEXT PRIMARY KEY,
                        state JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
    except Exception as e:
        print(f"設置資料庫時發生錯誤: {str(e)}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    global _pool
    setup_database()  # 在應用啟動時創建表格
    yield
    if _pool is not None:
        _pool.close()
        _pool = None

app = FastAPI(title="機車交通法規問答系統", lifespan=lifespan)

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


class ConversationHistory(BaseModel):
    conversation_id: str
    question: str
    answer: str
    created_at: datetime


@app.post("/query", response_model=Answer)
async def get_answer(question: Question):
    """處理問答請求"""
    try:
        answer = run_query(question.text)
        return Answer(response=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history", response_model=List[ConversationHistory])
async def get_history():
    """獲取對話歷史"""
    try:
        pool = get_connection_pool()
        with pool.connection() as conn:
            with conn.cursor() as cur:
                # 添加日誌
                print("正在查詢對話歷史...")
                cur.execute("""
                    SELECT conversation_id, 
                           state->>'question' as question,
                           state->>'generation' as answer,
                           created_at
                    FROM conversation_history
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
                rows = cur.fetchall()
                print(f"查詢結果: {rows}")  # 添加日誌

                return [
                    ConversationHistory(
                        conversation_id=row[0],
                        question=row[1],
                        answer=row[2],
                        created_at=row[3]
                    )
                    for row in rows
                ]
    except Exception as e:
        print(f"獲取歷史記錄時發生錯誤: {str(e)}")  # 添加錯誤日誌
        raise HTTPException(status_code=500, detail=str(e))


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

    postgres_saver = create_postgres_saver()

    return workflow.compile(checkpointer=postgres_saver)


def run_query(question: str):
    """執行查詢"""
    app = create_workflow()
    conversation_id = str(datetime.now().timestamp())

    inputs = {
        "question": question,
        "web_search_retry_count": 0,
        "rag_generate_retry_count": 0
    }
    config = {
        "configurable": {
            "thread_id": "default",
            "checkpoint_ns": "conversation",
            "checkpoint_id": conversation_id
        }
    }

    output = None
    for output in app.stream(inputs, config=config):
        print("\n")

    if output is None:
        return "抱歉，無法處理您的問題"

    # 保存對話歷史
    try:
        answer = ""
        if "rag_generate" in output:
            answer = output["rag_generate"]["generation"]
        elif "plain_answer" in output:
            answer = output["plain_answer"]["generation"]

        print(f"準備保存對話歷史: ID={conversation_id}, Q={question}, A={answer}")

        pool = get_connection_pool()
        with pool.connection() as conn:
            with conn.cursor() as cur:
                # 先刪除多餘的舊記錄，只保留最新的兩條（加上即將插入的新記錄，共三條）
                cur.execute("""
                    DELETE FROM conversation_history 
                    WHERE conversation_id NOT IN (
                        SELECT conversation_id 
                        FROM conversation_history 
                        ORDER BY created_at DESC 
                        LIMIT 2
                    )
                """)

                # 插入新記錄
                state = json.dumps({
                    "question": question,
                    "generation": answer
                })
                cur.execute("""
                    INSERT INTO conversation_history (conversation_id, state, created_at)
                    VALUES (%s, %s::jsonb, %s)
                """, (conversation_id, state, datetime.now()))

                conn.commit()
                print("對話歷史保存成功")
    except Exception as e:
        print(f"保存對話歷史時發生錯誤: {str(e)}")
        print(f"錯誤詳情: question={question}, answer={answer}")

    return answer


# 修改啟動方式
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
