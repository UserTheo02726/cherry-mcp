"""
嵌入模型客户端

提供对嵌入 API 的访问能力
"""
from typing import Optional
import logging

import httpx
import numpy as np

from .config import get_kb_config, KnowledgeBaseConfig

logger = logging.getLogger(__name__)

class EmbeddingError(Exception):
    """嵌入模型调用异常"""
    pass

class EmbeddingClient:
    """嵌入模型客户端"""
    
    def __init__(self, config: Optional[KnowledgeBaseConfig] = None):
        self.config = config or get_kb_config()
        self._client = httpx.AsyncClient(timeout=30)
    
    async def embed_text(self, text: str) -> np.ndarray:
        """将文本转为嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
            
        Raises:
            EmbeddingError: 嵌入模型调用失败时抛出异常
        """
        try:
            response = await self._client.post(
                self.config.embedding.url,
                json={
                    "model": self.config.embedding.model,
                    "input": text
                },
                headers=self.config.embedding.headers
            )
            response.raise_for_status()
            
            data = response.json()
            embedding = data["data"][0]["embedding"]
            
            return np.array(embedding, dtype=np.float32)
        
        except Exception as e:
            logger.error(f"嵌入文本失败: {e}")
            raise EmbeddingError(f"嵌入文本失败: {e}") from e
    
    async def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """批量将文本转为嵌入向量
        
        Args:
            texts: 输入文本列表
            
        Returns:
            嵌入向量列表
            
        Raises:
            EmbeddingError: 嵌入模型调用失败时抛出异常
        """
        try:
            response = await self._client.post(
                self.config.embedding.url,
                json={
                    "model": self.config.embedding.model,
                    "input": texts
                },
                headers=self.config.embedding.headers
            )
            response.raise_for_status()
            
            data = response.json()
            embeddings = []
            
            for item in data["data"]:
                embeddings.append(np.array(item["embedding"], dtype=np.float32))
            
            return embeddings
        
        except Exception as e:
            logger.error(f"批量嵌入失败: {e}")
            raise EmbeddingError(f"批量嵌入失败: {e}") from e
    
    async def close(self):
        """关闭客户端"""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
