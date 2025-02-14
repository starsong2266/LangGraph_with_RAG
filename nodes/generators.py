from langchain_core.prompts import ChatPromptTemplate
from services.llm import get_openai_llm
from langchain_core.output_parsers import StrOutputParser


def rag_generate(state):
    """使用 RAG 生成回答"""
    print("---RAG GENERATE---")
    question = state["question"]
    documents = state["documents"]

    instruction = """
    你是一位專業的問答助手，請依照以下規則回應問題：

    回答規則：
    1. 僅使用提供的文件內容來回答
    2. 若文件中找不到答案，請明確說明「抱歉，提供的資料中沒有相關資訊」
    3. 回答要完整且具體
    4. 禁止添加任何文件未提及的資訊

    文件內容：
    {documents}
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", instruction),
            ("human", "問題: {question}"),
        ]
    )

    # LLM & chain
    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7)
    llm = get_openai_llm()
    rag_chain = prompt | llm | StrOutputParser()

    # RAG generation
    generation = rag_chain.invoke(
        {"documents": documents, "question": question})

    # 更新 state 並回傳
    state["generation"] = generation
    return state


def plain_answer(state):
    """直接使用 LLM 生成回答"""
    print("---GENERATE PLAIN ANSWER---")
    question = state["question"]

    instruction = """
    你是一位專業的問答助手，請依照以下規則回應問題：

    回答規則：
    1. 提供準確且具體的回答
    2. 若不確定答案，請誠實說明「我無法確定答案」
    3. 回答要完整且有條理
    4. 避免提供可能有誤的資訊
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", instruction),
            ("human", "問題: {question}"),
        ]
    )

    # LLM & chain
    llm = get_openai_llm()
    llm_chain = prompt | llm | StrOutputParser()

    generation = llm_chain.invoke({"question": question})

    # 更新 state 並回傳
    state["generation"] = generation
    return state
