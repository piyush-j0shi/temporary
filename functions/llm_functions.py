"""
llm_functions.py

This module provides the LLMService class for interacting with NVIDIA's Nemotron model via the OpenAI-compatible API. It handles message formatting, context injection, and error handling for generating responses from the LLM.

Classes:
    LLMService: Service for generating responses from NVIDIA's Nemotron model.
"""
import logging
from typing import List, Dict
from openai import OpenAI, OpenAIError
from fastapi import HTTPException
from config.settings import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for generating responses from NVIDIA's Nemotron model via OpenAI-compatible API.

    Methods:
        __init__():
            Initializes the LLMService with API credentials and client.
        generate_response(messages, context=None):
            Generates a response from the LLM based on provided messages and optional context.
        generate_context_response(context, question):
            Generates a response from the LLM using a context string and a user question.
    """
    def __init__(self):
        """
        Initializes the LLMService.

        Raises:
            ValueError: If the NVIDIA API key is not set in the environment.
        """
        if not settings.nvidia_api_key:
            raise ValueError("NVIDIA_API_KEY environment variable is required")
        
        self.client = OpenAI(
            api_key=settings.nvidia_api_key,
            base_url=settings.nvidia_base_url,
        )

    def generate_response(self, messages: List[Dict[str, str]], context: str = None) -> str:
        """
        Generate a response using NVIDIA's Nemotron model.

        Args:
            messages (List[Dict[str, str]]):
                A list of message dictionaries, each with 'role' and 'content' keys, representing the conversation history.
            context (str, optional):
                Additional context information to provide to the model. Defaults to None.

        Returns:
            str: The generated response from the model in markdown format.

        Raises:
            HTTPException: If the API returns an error or an empty response, or if an unexpected error occurs.
        """
        try:
            formatted_messages = [
                {"role": "system", "content": "You are an expert assistant. Always provide answers in markdown format."}
            ]
            
            if context:
                formatted_messages.append({
                    "role": "system", 
                    "content": f"Context information:\n{context}"
                })
            
            formatted_messages.extend(messages)
            
            response = self.client.chat.completions.create(
                model=settings.model_name,
                messages=formatted_messages,
                temperature=settings.temperature
            )
            
            content = response.choices[0].message.content
            
            if content is None:
                raise HTTPException(status_code=500, detail="Empty response from API")
            
            return content
            
        except OpenAIError as e:
            logger.exception("NVIDIA API error")
            raise HTTPException(status_code=500, detail=f"NVIDIA API error: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error in LLM service")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    def generate_context_response(self, context: str, question: str) -> str:
        """
        Generate a response based on provided context and question.

        Args:
            context (str):
                The context information to provide to the model.
            question (str):
                The user's question.

        Returns:
            str: The generated response from the model in markdown format.
        """
        messages = [
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
        return self.generate_response(messages)