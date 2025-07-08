import logging
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from models.schemas import (
    ChatRequest, ChatResponse, FileUploadResponse,
    ChatMessage, SessionInfo, ChatHistory
)
from functions.file_functions import FileService
from functions.llm_functions import LLMService
from functions.memory_functions import MemoryService

logger = logging.getLogger(__name__)

router = APIRouter()

file_service = FileService()
llm_service = LLMService()
memory_service = MemoryService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat message."""
    try:
        if not memory_service.session_exists(request.session_id):
            memory_service.create_session(request.session_id)
        
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now()
        )
        memory_service.save_message(request.session_id, user_message)
        context = memory_service.get_conversation_context(request.session_id)
        response_content = llm_service.generate_response(context)
        
        assistant_message = ChatMessage(
            role="assistant",
            content=response_content,
            timestamp=datetime.now()
        )
        memory_service.save_message(request.session_id, assistant_message)
        
        return ChatResponse(
            response=response_content,
            session_id=request.session_id,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    question: str = "What is the main topic?",
    session_id: str = None
):
    """Handle file upload and question."""
    try:
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if not memory_service.session_exists(session_id):
            memory_service.create_session(session_id)
        
        text = file_service.extract_text(file)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the file.")
        
        truncated_context = file_service.truncate_context(text)
        
        user_message = ChatMessage(
            role="user",
            content=f"[Uploaded file: {file.filename}] {question}",
            timestamp=datetime.now()
        )
        memory_service.save_message(session_id, user_message)
        response_content = llm_service.generate_context_response(truncated_context, question)
        
        assistant_message = ChatMessage(
            role="assistant",
            content=response_content,
            timestamp=datetime.now()
        )
        memory_service.save_message(session_id, assistant_message)
        
        return FileUploadResponse(
            answer=response_content,
            session_id=session_id,
            filename=file.filename,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in upload endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/history", response_model=ChatHistory)
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    try:
        if not memory_service.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = memory_service.get_chat_history(session_id)
        session_info = memory_service.get_session_info(session_id)
        
        if session_info is None:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return ChatHistory(
            session_id=session_id,
            messages=messages,
            session_info=session_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting chat history")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/clear")
async def clear_session(session_id: str):
    """Clear a session."""
    try:
        if not memory_service.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        memory_service.clear_session(session_id)
        
        return JSONResponse(content={"message": "Session cleared successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error clearing session")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/new")
async def create_new_session():
    """Create a new session."""
    try:
        session_id = str(uuid.uuid4())
        memory_service.create_session(session_id)
        
        return JSONResponse(content={"session_id": session_id})
        
    except Exception as e:
        logger.exception("Error creating new session")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/info", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get session information."""
    try:
        session_info = memory_service.get_session_info(session_id)
        
        if session_info is None:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting session info")
        raise HTTPException(status_code=500, detail=str(e))