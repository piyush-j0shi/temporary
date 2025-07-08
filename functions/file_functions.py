import logging
from typing import BinaryIO
from PyPDF2 import PdfReader
from fastapi import UploadFile, HTTPException
from config.settings import settings

logger = logging.getLogger(__name__)


class FileService:
    @staticmethod
    def extract_text_from_pdf(file: BinaryIO) -> str:
        """Extract text from PDF file."""
        try:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise HTTPException(status_code=400, detail="Failed to extract text from PDF")

    @staticmethod
    def extract_text_from_txt(file: BinaryIO) -> str:
        """Extract text from TXT file."""
        try:
            content = file.read()
            return content.decode("utf-8")
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            raise HTTPException(status_code=400, detail="Failed to extract text from TXT file")

    @classmethod
    def extract_text(cls, file: UploadFile) -> str:
        """Extract text from uploaded file based on extension."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided.")
        
        file.file.seek(0, 2)  
        file_size = file.file.tell()
        file.file.seek(0)  
        
        if file_size > settings.upload_max_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {settings.upload_max_size} bytes"
            )
        
        extension = file.filename.lower().split('.')[-1]
        
        if extension not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Only {', '.join(settings.allowed_extensions)} are allowed."
            )
        
        if extension == "txt":
            return cls.extract_text_from_txt(file.file)
        elif extension == "pdf":
            return cls.extract_text_from_pdf(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

    @staticmethod
    def truncate_context(text: str, max_length: int = None) -> str:
        """Truncate text to maximum context length."""
        if max_length is None:
            max_length = settings.max_context_length
        return text[:max_length]