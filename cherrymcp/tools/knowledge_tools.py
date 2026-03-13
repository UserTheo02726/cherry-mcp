"""
知识库 MCP 工具模块
"""
from typing import Optional

from config import get_config
from cherrymcp.knowledge import (
    KnowledgeBaseManager,
    EmbeddingClient,
    VectorSearcher,
    get_kb_config
)


class KnowledgeTools:
    """知识库工具类"""
    
    def __init__(self, config_path: Optional[str] = None):
        config = get_config(config_path)
        kb_config = get_kb_config(config.knowledge_base_config)
        
        self.kb_manager = KnowledgeBaseManager(kb_config)
        self.embedding_client = EmbeddingClient(kb_config)
        self.searcher = VectorSearcher(
            knowledge_base=self.kb_manager,
            embedding_client=self.embedding_client
        )
    
    async def list_knowledge_bases(self) -> str:
        """列出所有知识库"""
        kbs = self.kb_manager.list_knowledge_bases()
        
        if not kbs:
            return "未找到知识库，请确保 Cherry Studio 已创建知识库。"
        
        result = "可用知识库列表:\n\n"
        for kb in kbs:
            size_mb = kb["size"] / (1024 * 1024)
            result += f"- {kb['name']}\n"
            result += f"  大小: {size_mb:.2f} MB\n\n"
        
        return result
    
    async def search_knowledge(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        kb_name: Optional[str] = None,
        max_fetch: Optional[int] = None
    ) -> str:
        """搜索知识库"""
        results = await self.searcher.search(
            query=query,
            top_k=top_k,
            threshold=threshold,
            kb_name=kb_name,
            max_fetch=max_fetch
        )
        
        if not results:
            return f"未找到与「{query}」相关的内容。"
        
        output = f"搜索「{query}」找到 {len(results)} 条结果:\n\n"
        
        for i, r in enumerate(results, 1):
            score = r["score"]
            source = r["source"]
            content = r["content"][:500]
            
            output += f"--- 结果 {i} (相似度: {score:.2%}) ---\n"
            output += f"来源: {source}\n"
            output += f"内容: {content}\n\n"
        
        return output
    
    async def close(self):
        """关闭资源"""
        await self.searcher.close()
