from langchain_core.prompts import ChatPromptTemplate
from services.llm import get_openai_llm
from langchain_core.output_parsers import StrOutputParser


def rag_generate(state):
    """使用 RAG 生成回答"""
    print("---RAG GENERATE---")
    question = state["question"]
    documents = state["documents"]

    instruction = """
    你是一位負責處理使用者問題的助手，請利用提取出來的資料內容來回應問題。
    若問題的答案無法從資料內取得，請直接回覆你不知道，禁止虛構答案。
    注意：請確保答案的準確性。
    資料:

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

    # 更新狀態並返回
    state["generation"] = generation
    return state


def plain_answer(state):
    """直接使用 LLM 生成回答"""
    print("---GENERATE PLAIN ANSWER---")
    # print(state)
    question = state["question"]

    instruction = """
    你是一位負責處理使用者問題的助手，請利用你的知識來回應問題。
    回應問題時請確保答案的準確性，勿虛構答案。
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

    # 更新狀態並返回
    state["generation"] = generation
    return state
