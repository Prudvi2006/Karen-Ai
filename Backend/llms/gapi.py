from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def get_response_stream(messages, pdf_path=None, image_path=None):
    contents = list(messages)

    if pdf_path:
        pdf_file = client.files.upload(file=pdf_path)
        contents.append(pdf_file)

    if image_path:
        image_file = client.files.upload(file=image_path)
        contents.append(image_file)

    stream = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=contents
    )

    for chunk in stream:
        if chunk.text:
            yield chunk.text