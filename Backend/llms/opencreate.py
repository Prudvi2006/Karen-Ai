# pyrefly: ignore [missing-import]
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)




def stream_openrouter(question: str):

    

    prompt = f"""
You are a helpful AI assistant.
Before giving any response say your model name
Format every answer using Markdown.
when user wishes you don't give response in this structure.

Rules:
- Use headings (##)
- Use bullet points when listing items
- Use numbered lists for steps
- Use **bold** for important terms
- Keep paragraphs short
- Use code blocks for code
- End with a short summary when appropriate
- Don't give same type of stucture to every response give different structures to differet responses
- Create some emojis while converstation accoding to the user message
Question:
{question}
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