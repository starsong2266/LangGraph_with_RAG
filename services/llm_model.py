from langchain_core.prompts import ChatPromptTemplate
from services.llm import get_azure_llm
from pydantic import BaseModel, Field


# 定義工具類別
class web_search(BaseModel):
    """
    網路搜尋工具。若問題與大型重型機車的資訊"無關"，請使用web_search工具搜尋解答。
    """
    query: str = Field(description="使用網路搜尋時輸入的問題")


class vectorstore(BaseModel):
    """
    紀錄關大型重型機車相關資訊的向量資料庫工具。若問題與之有關，請使用此工具搜尋解答。
    """
    query: str = Field(description="搜尋向量資料庫時輸入的問題")


def create_question_router():
    """創建問題路由 LLM"""
    llm = get_azure_llm()
    instruction = """
    你是將使用者問題導向向量資料庫或網路搜尋的專家。
    向量資料庫包含有關大型重型機車的道路交通管理法規資訊。對於大型重型機車、駕照、標線標誌規定、道路法規這些主題的問題，請使用向量資料庫工具。其他情況則使用網路搜尋工具。
    """

    route_prompt = ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("human", "{question}"),
    ])

    structured_llm_router = llm.bind_tools(tools=[web_search, vectorstore])
    return route_prompt | structured_llm_router


def create_question_grader():
    """創建評估問題的 LLM"""
    llm = get_azure_llm()
    instruction = """
    你是一個評分的人員，專門評定該問題是否與與暴力、色情、毒品相關。
    如果使用者問題有與暴力、色情、毒品相關的關鍵字或語意，回答 'yes'，否則回答 'no'。
    """

    return ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("human", "{question}"),
    ]) | llm


def create_retrieval_grader():
    """創建評估檢索結果的 LLM"""
    llm = get_azure_llm()
    instruction = """
    你是一個評分的人員，負責評估文件與使用者問題的關聯性。
    如果文件包含與使用者問題相關的關鍵字或語意，則將其評為相關。
    輸出 'yes' or 'no' 代表文件與問題的相關與否。
    """

    return ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("human", "文件: \n\n {document} \n\n 使用者問題: {question}"),
    ]) | llm


def create_hallucination_grader():
    """創建評估幻覺的 LLM"""
    llm = get_azure_llm()
    instruction = """
    你是一個評分的人員，專門評定生成的回答是否與提供的文件相符。
    如果回答包含文件中未提及的資訊，回答 'yes'，否則回答 'no'。
    """

    return ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("human", "文件: {documents}\n生成回答: {generation}"),
    ]) | llm


def create_answer_grader():
    """創建評估回答品質的 LLM"""
    llm = get_azure_llm()
    instruction = """
    你是一個評分的人員，專門評定生成的回答是否完整回答了問題。
    如果回答完整且合理，回答 'yes'，否則回答 'no'。
    """

    return ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("human", "問題: {question}\n生成回答: {generation}"),
    ]) | llm


# 創建所有 LLM 實例
question_grader = create_question_grader()
retrieval_grader = create_retrieval_grader()
hallucination_grader = create_hallucination_grader()
answer_grader = create_answer_grader()
question_router = create_question_router()
