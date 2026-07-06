from pydantic import BaseModel, EmailStr

class ChatRequest(BaseModel):
    chat_id: str
    message: str
    model: str

class NewChat(BaseModel):
    title: str = "New Chat"


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str