"""
向量搜索模块

提供向量相似度搜索功能
"""
import logging
from typing import Optional, List, Dict, Any

import numpy as np

from .knowledge_base import KnowledgeBaseManager
from .embedding import EmbeddingClient

logger = logging.getLogger(__name__)

class VectorSearcher:
    """向量搜索器"""
    
    def __init__(
        self,
        knowledge_base: Optional[KnowledgeBaseManager] = None,
        embedding_client: Optional[EmbeddingClient] = None
    ):
        self.knowledge_base = knowledge_base or KnowledgeBaseManager()
        self.embedding_client = embedding_client or EmbeddingClient()
    
    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        kb_name: Optional[str] = None,
        max_fetch: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """搜索知识库
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            threshold: 相似度阈值
            kb_name: 知识库名称（如果不传则搜索所有知识库文件提取合并结果）
            max_fetch: 从数据库最多获取的文档数
            
        Returns:
            搜索结果列表
        """
        config = self.embedding_client.config
        
        # 修复 or 导致的 0 值 bug
        top_k = top_k if top_k is not None else config.search.default_top_k
        threshold = threshold if threshold is not None else config.search.default_threshold
        max_fetch = max_fetch if max_fetch is not None else config.search.max_fetch
        
        try:
            query_vector = await self.embedding_client.embed_text(query)
        except Exception as e:
            logger.error(f"无法获取查询的 Embedding 向量，搜索终止: {e}")
            return []
            
        if query_vector is None:
            return []
        
        results = self.knowledge_base.search(
            query_vector=query_vector,
            top_k=top_k,
            threshold=threshold,
            max_fetch=max_fetch,
            kb_name=kb_name
        )
        
        return results
    
    async def close(self):
        """关闭资源"""
        await self.embedding_client.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
