from services.llm_model import (
    question_grader,
    retrieval_grader,
    hallucination_grader,
    answer_grader,
    question_router
)


def route_question(state):
    """評估問題是否適合回答"""
    print("---QUESTION---")
    question = state["question"]

    score = question_grader.invoke({"question": question})
    grade = score.content
    if grade == "yes":
        return "end"
    else:
        print("---ROUTE QUESTION---")

        source = question_router.invoke({"question": question})

        # Fallback to plain LLM or raise error if no decision
        if "tool_calls" not in source.additional_kwargs:
            print("  -ROUTE TO PLAIN LLM-")
            return "plain_answer"
        if len(source.additional_kwargs["tool_calls"]) == 0:
            raise "Router could not decide source"

        # Choose datasource
        datasource = source.additional_kwargs["tool_calls"][0]["function"]["name"]
        if datasource == "web_search":
            print("  -ROUTE TO WEB SEARCH-")
            return "web_search"
        elif datasource == "vectorstore":
            print("  -ROUTE TO VECTORSTORE-")
            return "vectorstore"


def retrieval_grade(state):
    """評估檢索結果是否相關"""
    print("---GRADE RETRIEVAL---")
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content})
        grade = score.content
        if grade == "yes":
            print("  -GRADE: DOCUMENT RELEVANT-")
            filtered_docs.append(d)
        else:
            print("  -GRADE: DOCUMENT NOT RELEVANT-")
            continue
    return {"documents": filtered_docs, "question": question}


def grade_rag_generation(state):
    """評估生成內容是否合適"""
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    retry_count = state.get("retry_count", 0)

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation})
    grade = score.content

    # 檢查幻覺
    if grade == "no":
        print("  -DECISION: GENERATION IS GROUNDED IN DOCUMENTS-")
        # 檢查問題回答
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke(
            {"question": question, "generation": generation})
        grade = score.content
        if grade == "yes":
            print("  -DECISION: GENERATION ADDRESSES QUESTION-")
            return "useful"
        else:
            print("  -DECISION: GENERATION DOES NOT ADDRESS QUESTION-")
            if retry_count >= 1:
                print("  -MAX RETRIES REACHED, USING PLAIN ANSWER-")
                return "plain_answer"
            state["retry_count"] = retry_count + 1
            return "not useful"
    else:
        print("  -DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY-")
        if retry_count >= 1:
            print("  -MAX RETRIES REACHED, USING PLAIN ANSWER-")
            return "plain_answer"
        state["retry_count"] = retry_count + 1
        return "not supported"


def route_retrieval(state):
    """決定是否生成答案或使用網路搜尋"""
    print("---ROUTE RETRIEVAL---")
    documents = state["documents"]
    retry_count = state.get("retry_count", 0)

    if not documents:
        print("  -NO RELEVANT DOCUMENTS FOUND-")
        if retry_count >= 1:
            print("  -MAX RETRIES REACHED, USING PLAIN ANSWER-")
            return "plain_answer"
        state["retry_count"] = retry_count + 1
        print("  -RETRY WITH WEB SEARCH-")
        return "web_search"

    print("  -RELEVANT DOCUMENTS FOUND, GENERATING ANSWER-")
    return "rag_generate"
