from langchain_groq import ChatGroq
from .config import GROQ_API_KEY

llm = ChatGroq(model="openai/gpt-oss-20b", groq_api_key=GROQ_API_KEY)