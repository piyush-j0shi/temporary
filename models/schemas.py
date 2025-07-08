"""Pydantic models for the chat application.

This module defines the Pydantic models used for data validation and
serialization in the chat application.
"""

from typing import List
from pydantic import BaseModel
from datetime import datetime


class ChatMessage(BaseModel):
    """A single chat message.

    Attributes:
        role: The role of the message sender (e.g., 'user', 'assistant').
        content: The content of the message.
        timestamp: The timestamp of the message.
    """
    role: str  
    content: str
    timestamp: datetime = datetime.now()


class ChatRequest(BaseModel):
    """A chat request.

    Attributes:
        message: The user'''s message.
        session_id: The session ID.
    """
    message: str
    session_id: str


class ChatResponse(BaseModel):
    """A chat response.

    Attributes:
        response: The assistant'''s response.
        session_id: The session ID.
        timestamp: The timestamp of the response.
    """
    response: str
    session_id: str
    timestamp: datetime = datetime.now()


class FileUploadRequest(BaseModel):
    """A file upload request.

    Attributes:
        question: The question about the file.
        session_id: The session ID.
    """
    question: str = "What is the main topic?"
    session_id: str


class FileUploadResponse(BaseModel):
    """A file upload response.

    Attributes:
        answer: The answer to the question.
        session_id: The session ID.
        filename: The name of the uploaded file.
        timestamp: The timestamp of the response.
    """
    answer: str
    session_id: str
    filename: str
    timestamp: datetime = datetime.now()


class SessionInfo(BaseModel):
    """Information about a session.

    Attributes:
        session_id: The session ID.
        created_at: The timestamp when the session was created.
        last_activity: The timestamp of the last activity in the session.
        message_count: The number of messages in the session.
    """
    session_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int


class ChatHistory(BaseModel):
    """The chat history for a session.

    Attributes:
        session_id: The session ID.
        messages: The list of chat messages.
        session_info: The session information.
    """
    session_id: str
    messages: List[ChatMessage]
    session_info: SessionInfo