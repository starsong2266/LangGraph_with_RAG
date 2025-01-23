from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document
from data.data import retrieve_documents


def web_search(state):
    """執行網路搜尋"""
    print("---WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents", [])

    search_tool = TavilySearchResults()
    results = search_tool.invoke({"query": question})
    web_results = [Document(page_content=d["content"]) for d in results]

    documents.extend(web_results)
    return {"documents": documents, "question": question}


def retrieve(state):
    """從向量資料庫檢索文件"""
    print("---RETRIEVE---")
    question = state["question"]

    retriever = retrieve_documents()
    documents = retriever.invoke(question)

    return {"documents": documents, "question": question}
