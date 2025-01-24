from dotenv import load_dotenv
import os

# 載入 .env 檔案
load_dotenv()

# 取得環境變數
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
