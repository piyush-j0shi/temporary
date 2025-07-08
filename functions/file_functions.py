"""Service for handling file-related operations.

This module provides functionalities for extracting text from various file types
and truncating text content.
"""

import logging
from typing import BinaryIO
from PyPDF2 import PdfReader
from fastapi import UploadFile, HTTPException
from config.settings import settings

logger = logging.getLogger(__name__)


class FileService:
    """Handles file processing, including text extraction and content truncation.
    """

    @staticmethod
    def extract_text_from_pdf(file: BinaryIO) -> str:
        """Extracts text content from a PDF file.

        Args:
            file: A binary file-like object representing the PDF.

        Returns:
            The extracted text content from the PDF.

        Raises:
            HTTPException: If an error occurs during text extraction.
        """
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
        """Extracts text content from a TXT file.

        Args:
            file: A binary file-like object representing the TXT file.

        Returns:
            The extracted text content from the TXT file.

        Raises:
            HTTPException: If an error occurs during text extraction.
        """
        try:
            content = file.read()
            return content.decode("utf-8")
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            raise HTTPException(status_code=400, detail="Failed to extract text from TXT file")

    @classmethod
    def extract_text(cls, file: UploadFile) -> str:
        """Extracts text from an uploaded file based on its extension.

        Args:
            file: The uploaded file object.

        Returns:
            The extracted text content from the file.

        Raises:
            HTTPException:
                - If no filename is provided.
                - If the file size exceeds the maximum allowed size.
                - If the file type is not supported.
                - If an error occurs during text extraction.
        """
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
        """Truncates the given text to a specified maximum length.

        Args:
            text: The input text string.
            max_length: The maximum length for the truncated text. If None,
                        `settings.max_context_length` is used.

        Returns:
            The truncated text string.
        """
        if max_length is None:
            max_length = settings.max_context_length
        return text[:max_length]