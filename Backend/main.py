
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_router
from routes.auth import router as auth_router
from routes.upload import router as upload_router

app = FastAPI()

# Allow CORS for localhost and optional production frontend URL
origins = [
    "http://localhost:5173",
    "https://karen-ai-multimodal-rag-chatbot.vercel.app",
    
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    print("🚀 FastAPI server started")
    
@app.get("/")
def root():
    return {"message": "Karen AI API is running!"}

app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(auth_router)

