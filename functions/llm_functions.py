import logging
from typing import List, Dict
from openai import OpenAI, OpenAIError
from fastapi import HTTPException
from config.settings import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        if not settings.nvidia_api_key:
            raise ValueError("NVIDIA_API_KEY environment variable is required")
        
        self.client = OpenAI(
            api_key=settings.nvidia_api_key,
            base_url=settings.nvidia_base_url,
        )

    def generate_response(self, messages: List[Dict[str, str]], context: str = None) -> str:
        """Generate response using NVIDIA's Nemotron model."""
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
        """Generate response based on context and question."""
        messages = [
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
        return self.generate_response(messages)