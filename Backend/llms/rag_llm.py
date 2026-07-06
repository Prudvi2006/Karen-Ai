from dotenv import load_dotenv
import os

from langchain_groq import ChatGroq

from rag.retrieval import retrieve_context

load_dotenv()

groq_api_key2 = os.getenv("GROQ_API_KEY2")

llm = ChatGroq(
    api_key=groq_api_key2,
    model="llama-3.3-70b-versatile"
)








def stream_response2(question: str , chat_id: str):

    context = retrieve_context(question , chat_id)

    

    prompt = f"""
Before giving any response say that this response is from uploaded document

You are a helpful AI assistant.

Answer ONLY using the provided context.

If the answer cannot be found in the context, reply:

"I couldn't find that information in the uploaded documents. And say this response is given by my own"

- Think on your own and give response on you own

- Create some emojis while converstation accoding to the user message

Context:
{context}

Question:
{question}

Answer:
"""
    
    for chunk in llm.stream(prompt):
        if chunk.content:
            yield chunk.content
      
