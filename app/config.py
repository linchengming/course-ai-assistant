"""
Configuration management for the Course AI Assistant.
Loads settings from environment variables.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-ada-002"
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    
    # Vector Database Configuration
    vectordb_path: str = "./vectordb"
    collection_name: str = "course_documents"
    
    # RAG Configuration
    retrieval_top_k: int = 20
    rerank_top_k: int = 3
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Prompts templates
REFUND_POLICY_PROMPT = """你是一位专业的课程顾问。请基于以下课程资料，回答用户关于退费政策的问题。

注意事项：
1. 准确引用退费政策条款
2. 说明退费流程和时间
3. 如有特殊情况，需要说明
4. 语气友好、专业

课程资料：
{context}

用户问题：{question}

请给出详细、准确的回答：
"""

GENERAL_PROMPT = """你是一位专业的课程顾问助手。请基于以下资料回答用户问题。

要求：
1. 回答要准确、完整
2. 如果资料中没有相关信息，请诚实告知
3. 语气友好、专业
4. 可以适当举例说明

参考资料：
{context}

用户问题：{question}

回答：
"""
