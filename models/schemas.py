from typing import List
from pydantic import BaseModel
from datetime import datetime


class ChatMessage(BaseModel):
    role: str  
    content: str
    timestamp: datetime = datetime.now()


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime = datetime.now()


class FileUploadRequest(BaseModel):
    question: str = "What is the main topic?"
    session_id: str


class FileUploadResponse(BaseModel):
    answer: str
    session_id: str
    filename: str
    timestamp: datetime = datetime.now()


class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int


class ChatHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    session_info: SessionInfo