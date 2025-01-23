from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import AZURE_ENDPOINT, AZURE_DEPLOYMENT, AZURE_API_VERSION
import os


def get_azure_llm():
    """獲取 Azure OpenAI LLM"""
    return AzureChatOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        azure_deployment=AZURE_DEPLOYMENT,
        openai_api_version=AZURE_API_VERSION,
        api_key=os.environ["OPENAI_API_KEY"]
    )


def get_gemini_llm():
    """獲取 Gemini LLM"""
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.7
    )
