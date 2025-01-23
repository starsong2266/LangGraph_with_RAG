from langchain_community.document_loaders import PyPDFLoader
import requests
from services.embeddings import EmbeddingService


def load_documents():
    """載入 PDF 文件"""
    url = "https://www.freeway.gov.tw/Upload/Html/2017824171/inf/motorcycle%20safety_02.pdf"
    pdf_path = "motorcycle_safety_02.pdf"

    response = requests.get(url)
    with open(pdf_path, "wb") as file:
        file.write(response.content)

    loader = PyPDFLoader(pdf_path)
    return loader.load()


def retrieve_documents():
    """建立向量資料庫"""
    embedding_service = EmbeddingService()

    # 載入文件並建立向量資料庫
    documents = load_documents()
    vectorstore = embedding_service.create_vectorstore(documents)
    retriever = vectorstore.as_retriever()
    return retriever
