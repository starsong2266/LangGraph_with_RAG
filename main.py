import asyncio
from app import run_query_with_timeout


async def test_query():
    question = "大型重型機車的定義?"
    try:
        answer = await run_query_with_timeout(question)
        print(answer)
    except Exception as e:
        print(f"錯誤：{str(e)}")

if __name__ == "__main__":
    asyncio.run(test_query())
