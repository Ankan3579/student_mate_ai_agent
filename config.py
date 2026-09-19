from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv
import os 
load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_api_key:
    raise ValueError("MISTRAL_API_KEY environment variable is not set.")

LLM = ChatOpenRouter(api_key=openrouter_api_key, model="mistral-medium-3-5", temperature=0 , max_tokens=300)

