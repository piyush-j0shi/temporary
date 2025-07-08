from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    nvidia_api_key: Optional[str] = None
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    model_name: str = "nvidia/llama-3.1-nemotron-70b-instruct"
    max_context_length: int = 3000
    temperature: float = 0.5
    upload_max_size: int = 10 * 1024 * 1024 
    allowed_extensions: list = ["txt", "pdf"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()