import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    api_key=groq_api_key,
    model="llama-3.3-70b-versatile"
)
def stream_response1(message: str):
    for chunk in llm.stream(message):
        if chunk.content:
            yield chunk.content
