from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import OPENAI_API_KEY  # 從 config 引入


def get_openai_llm():
    """獲取 OpenAI LLM"""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=OPENAI_API_KEY
    )


def get_gemini_llm():
    """獲取 Gemini LLM"""
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.7
    )
