from langchain_core.prompts import ChatPromptTemplate
from services.llm import get_openai_llm
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
    llm = get_openai_llm()
    instruction = """
    你是一個專業的問題分類專家，負責將使用者問題導向最適合的搜尋工具。請根據以下規則選擇工具：

    1. 向量資料庫 (vectorstore)：
       - 適用於查詢大型重型機車相關的法規與規定
       - 包含主題：駕照規定、考照要求、路權規範、標線標誌規定、道路安全法規
       - 若問題涉及上述任一主題，請使用此工具

    2. 網路搜尋 (web_search)：
       - 若問題不屬於向量資料庫的範疇，請使用此工具

    請仔細分析問題內容，選擇最合適的工具進行查詢。
    """

    route_prompt = ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("human", "{question}"),
    ])

    structured_llm_router = llm.bind_tools(tools=[web_search, vectorstore])
    return route_prompt | structured_llm_router


def create_question_grader():
    """創建評估問題的 LLM"""
    llm = get_openai_llm()
    instruction = """
    你是內容審核專家，負責識別並過濾不當內容。請依照以下標準評估使用者問題：

    評估重點：
    1. 暴力內容：暴力行為、威脅、攻擊性語言
    2. 色情內容：露骨的性暗示、不當性話題
    3. 毒品內容：毒品相關、違禁藥物

    回答規則：
    - 若問題包含上述任一類型的內容，請回答 'yes'
    - 若問題不包含任何不當內容，請回答 'no'
    - 請嚴格執行審核標準，確保內容安全
    """

    return ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("human", "{question}"),
    ]) | llm


def create_retrieval_grader():
    """創建評估檢索結果的 LLM"""
    llm = get_openai_llm()
    instruction = """
    你是搜尋結果評估專家，負責判斷檢索文件與使用者問題的相關性。評估標準如下：

    相關性判斷標準：
    1. 關鍵字匹配：文件是否包含問題中的重要關鍵字
    2. 語意相關：文件內容是否在語意層面回答了問題
    3. 資訊完整性：文件是否包含回答問題所需的核心資訊

    回答規則：
    - 符合上述標準，請回答 'yes'
    - 不符合標準，請回答 'no'
    """

    return ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("human", "文件: \n\n {document} \n\n 使用者問題: {question}"),
    ]) | llm


def create_hallucination_grader():
    """創建評估幻覺的 LLM"""
    llm = get_openai_llm()
    instruction = """
    你是答案準確性審查專家，負責檢查生成的回答是否存在幻覺（虛構資訊）。評估標準如下：

    幻覺判斷標準：
    1. 資訊來源：回答中的所有資訊必須能在提供的文件中找到對應依據
    2. 推論合理：若有推論，必須基於文件提供的資訊
    3. 細節正確：數字、日期、名稱等具體細節必須與文件相符

    回答規則：
    - 發現幻覺（包含文件未提及的資訊），回答 'yes'
    - 回答完全基於文件內容，回答 'no'
    """

    return ChatPromptTemplate.from_messages([
        ("system", instruction),
        ("human", "文件: {documents}\n生成回答: {generation}"),
    ]) | llm


def create_answer_grader():
    """創建評估回答品質的 LLM"""
    llm = get_openai_llm()
    instruction = """
    你是回答品質評估專家，負責評估生成回答的完整性與品質。評估標準如下：

    品質評估標準：
    1. 完整性：是否完整回答了使用者的問題要點
    2. 準確性：回答內容是否準確無誤
    3. 邏輯性：論述是否合理且連貫
    4. 清晰度：表達是否清楚易懂

    回答規則：
    - 符合所有評估標準，回答 'yes'
    - 未達到任一標準，回答 'no'
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
