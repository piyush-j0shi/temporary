"""Configuration settings for the application.

This module defines the configuration settings for the application, including
API keys, model parameters, and file upload limits.
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Pydantic BaseSettings class for application configuration.

    Attributes:
        nvidia_api_key: The NVIDIA API key.
        nvidia_base_url: The base URL for the NVIDIA API.
        model_name: The name of the model to use.
        max_context_length: The maximum context length for the model.
        temperature: The temperature for the model.
        upload_max_size: The maximum file size for uploads.
        allowed_extensions: The allowed file extensions for uploads.
    """
    nvidia_api_key: Optional[str] = None
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    model_name: str = "nvidia/llama-3.1-nemotron-70b-instruct"
    max_context_length: int = 3000
    temperature: float = 0.5
    upload_max_size: int = 10 * 1024 * 1024 
    allowed_extensions: list = ["txt", "pdf"]
    
    class Config:
        """Pydantic configuration class.

        Attributes:
            env_file: The name of the environment file.
            env_file_encoding: The encoding of the environment file.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()