from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

from rag.retrieval import retrieve_context


def stream_openrouter_rag(question: str , chat_id: str):

    context = retrieve_context(question , chat_id)

    prompt = f"""
Before giving any response say that this response is from uploaded document using OpenRouter.

You are a helpful AI assistant.



If the answer cannot be found in the context:

Then generate answer on your own and say

"I couldn't find that information in the uploaded documents.."

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=True,
    )

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content