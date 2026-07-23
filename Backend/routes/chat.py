
from llms.opencreaterag import stream_openrouter_rag
from llms.opencreate import stream_openrouter
from llms.groqvision import stream_image_response

import google.genai.types as types
from llms.llm import stream_response1

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from bson import ObjectId
from datetime import datetime
# pyrefly: ignore [missing-import]
from llms.rag_llm import stream_response2
from models import NewChat, ChatRequest

from database import messages_collection, chats_collection
from llms.gapi import get_response_stream
import routes.upload as upload
from routes.download import download_file

# pyrefly: ignore [missing-import]
from auth.dependencies import get_current_user
router = APIRouter()

@router.post("/new-chat")
def create_chat(chat: NewChat, user_id: str = Depends(get_current_user)):

    result = chats_collection.insert_one({
        "title": chat.title,
        "user_id": user_id,
        "image_path": None,
        "pdf_path": None,
        "created_at": datetime.utcnow()
    })

    return {
        "chat_id": str(result.inserted_id)
    }

@router.get("/messages/{chat_id}")
def get_messages(chat_id: str, user_id: str = Depends(get_current_user)):

    docs = messages_collection.find(
        {"chat_id": chat_id, "user_id": user_id}
    ).sort("created_at", 1)

    return [
        {
            "role": doc["role"],
            "text": doc["text"]
        }
        for doc in docs
    ]

@router.get("/chats")
def get_chats(user_id: str = Depends(get_current_user)):

        chats = chats_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1)

        history1 = []

        for chat in chats:
            history1.append({
                "chat_id": str(chat["_id"]),
                "title": chat["title"]
            })

        return history1


        history2 = []

        for chat in chats:
            history2.append({
                "chat_id": str(chat["_id"]),
                "title": chat["title"]
            })

        return history2

@router.post("/chat/stream")
def chat_stream(req: ChatRequest, user_id: str = Depends(get_current_user)):

    chats_collection.update_one(
        {
            "_id": ObjectId(req.chat_id),
            "title": "New Chat"
        },
        {
            "$set": {
                "title": req.message
            }
        }
    )
    

    chat = chats_collection.find_one(
    {
        "_id": ObjectId(req.chat_id),
        "user_id": user_id
    }
   )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.get("pdf_url") and not chat.get("rag_ready"):
        return StreamingResponse(
        iter(["Please wait a few seconds while I finish processing your PDF..."]),
        media_type="text/plain"
    )

    pdf_url = chat.get("pdf_url")
    image_url = chat.get("image_url")
    
    messages_collection.insert_one({
        "chat_id": req.chat_id,
        "user_id": user_id, 
        "role": "user",
        "text": req.message,
        "created_at": datetime.utcnow()
    })



    chat = chats_collection.find_one(
    {
        "_id": ObjectId(req.chat_id),
        "user_id": user_id
    }
)

    pdf_url = chat.get("pdf_url")
    image_url = chat.get("image_url")

    pdf_path = download_file(pdf_url, "temp.pdf") if pdf_url else None
    image_path = download_file(image_url, "temp.jpg") if image_url else None

    print("STREAM chat_id:", req.chat_id)
     # Fetch the entire chat history
    history = list(
        messages_collection.find(
            {"chat_id": req.chat_id,
            "user_id": user_id}
        ).sort("created_at", 1)
    )

   



     
     # This is for GROQ


    messages1 = [
        {
            "role": "system",
            "content": """
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

"""
        }
    ]




     #This is Gemini

    messages2 = [
    types.Content(
        role="user",
        parts=[
            types.Part(
                text="""
You are a helpful AI assistant.

Before every response say This response is from ChatBot Gemini.

Format every answer using Markdown.

Rules:
- Use headings
- Use bullet points
- Use emojis
- Don't give same type of stucture to every response give different structures to differet responses
- Create some emojis while converstation accoding to the user message
"""
            )
        ]
    )
]

     # Add conversation history
    for msg in history:

        role = "assistant" if msg["role"] == "bot" else "user"
        #GROQ API

        messages1.append({
            "role": role,
            "content": msg["text"]
        })

    for msg in history:
        #Gemini APi
        role = "model" if msg["role"] == "bot" else "user"
        messages2.append(
            types.Content(
                role=role,
                parts=[types.Part(text=msg["text"])]
            )
        )


    def generate():
        full_response = ""
        print("pdf_url:", pdf_url)
        print("image_url:", image_url)
        print("pdf_path:", pdf_path)
        print("image_path:", image_path)
        print("Model:", req.model)
        try:

            if pdf_path and image_path:
                
                print(">>> USING GEMINI WITH PDF + IMAGE <<<")
                for chunk in get_response_stream(
                    messages2,
                    pdf_path=pdf_path,
                    image_path=image_path
                ):
                    full_response += chunk
                    yield chunk

                

            

            elif pdf_path:
                print(">>> USING PDF <<<")

                if req.model == "openrouter":
                    print("OpenCreate pdf<<<<")
                    for chunk in stream_openrouter_rag(req.message , req.chat_id):
                        full_response += chunk
                        yield chunk

                elif req.model == "groq":
                    print("GROQ pdf<<<<")
                    for chunk in stream_response2(req.message , req.chat_id):
                        full_response += chunk
                        yield chunk

                

            elif image_path:
                print(">>> USING IMAGE <<<")

                if req.model == "gemini":
                    print("gemini image<<<<")
                    for chunk in get_response_stream(messages2, image_path=image_path):

                        full_response += chunk
                        yield chunk

                elif req.model == "groq":
                    print("GROQ image<<<<")
                    for chunk in stream_image_response(req.message , image_path=image_path):
                        full_response += chunk
                        yield chunk

            else:
                print(">>> NORMAL CHAT <<<")

               
                if req.model == "gemini":
                    print("Gemini<<<<")
                    for chunk in get_response_stream(messages2):
                        full_response += chunk
                        yield chunk

                elif req.model == "openrouter":
                    print("OpenCreate<<<<")
                    for chunk in stream_openrouter(messages1):
                        full_response += chunk
                        yield chunk

                elif req.model == "groq":
                    print("GROQ<<<<")
                    for chunk in stream_response1(messages1):
                        full_response += chunk
                        yield chunk


        except Exception as e:
            import traceback
            traceback.print_exc()   # <-- Look at your terminal
            yield f"\n\nError: {e}"

        finally:
            messages_collection.insert_one({
            "chat_id": req.chat_id,
            "user_id": user_id,
            "role": "bot",
            "text": full_response,
            "created_at": datetime.utcnow()


        })

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )

@router.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str, user_id: str = Depends(get_current_user)):
    chat = chats_collection.find_one({
    "_id": ObjectId(chat_id),
    "user_id": user_id
})
    print("chat found:",chat)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    import os

# Delete files first
    if chat.get("image_path") and os.path.exists(chat["image_path"]):
        os.remove(chat["image_path"])

    if chat.get("pdf_path") and os.path.exists(chat["pdf_path"]):
        os.remove(chat["pdf_path"])

    messages_collection.delete_many({
        "chat_id": chat_id
    })

    chats_collection.delete_one({
        "_id": ObjectId(chat_id)
    })

    return {"message": "Chat deleted successfully"}
    