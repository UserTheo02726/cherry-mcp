"""
知识库管理模块

提供对 Cherry Studio 知识库数据库的访问能力
"""
import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import numpy as np

from .config import get_kb_config, KnowledgeBaseConfig

logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    """Cherry Studio 知识库管理器"""
    
    def __init__(self, config: Optional[KnowledgeBaseConfig] = None):
        self.config = config or get_kb_config()
    
    def _get_databases(self) -> List[Path]:
        """获取所有潜在的知识库数据库文件"""
        kb_dir = Path(self.config.kb_path)
        if not kb_dir.exists():
            return []
        
        databases = []
        for item in kb_dir.iterdir():
            if item.is_file():
                # 我们已知该目录下都是合法数据库，或者至少尝试连接
                databases.append(item)
            elif item.is_dir():
                for db_file in item.iterdir():
                    if db_file.is_file():
                        databases.append(db_file)
        return databases
    
    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """列出所有知识库文件及统计信息"""
        databases = self._get_databases()
        results = []
        
        for db_path in databases:
            try:
                with sqlite3.connect(str(db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM vectors")
                    count = cursor.fetchone()[0]
                    
                    # 探测维度
                    cursor.execute("SELECT vector FROM vectors LIMIT 1")
                    row = cursor.fetchone()
                    dim = None
                    if row and row[0]:
                        dim = len(np.frombuffer(row[0], dtype=np.float32))
                        
                    results.append({
                        "name": db_path.stem,
                        "path": str(db_path),
                        "size": db_path.stat().st_size,
                        "vector_count": count,
                        "dimension": dim
                    })
            except Exception as e:
                logger.debug(f"跳过无效数据库文件 {db_path}: {e}")
                
        return results
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.0,
        max_fetch: int = 1000,
        kb_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索知识库 (跨所有文件汇总)
        
        Args:
            query_vector: 查询向量
            top_k: 最终返回的全局结果数量
            threshold: 相似度阈值
            max_fetch: 每个数据库最多获取的文档数
            kb_name: 若提供，则仅搜索文件名匹配的这个数据库
            
        Returns:
            排好序的搜索结果列表
        """
        databases = self._get_databases()
        
        if kb_name:
            databases = [db for db in databases if db.stem == kb_name]
            if not databases:
                logger.warning(f"未找到名为 {kb_name} 的知识库")
                return []

        all_results = []
        
        for db_path in databases:
            try:
                with sqlite3.connect(str(db_path)) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute(
                        "SELECT id, pageContent, source, vector FROM vectors LIMIT ?",
                        (max_fetch,)
                    )
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        doc_id, content, source, vector_bytes = row
                        
                        if not vector_bytes or not content:
                            continue
                        
                        doc_vector = np.frombuffer(vector_bytes, dtype=np.float32)
                        
                        if len(doc_vector) != len(query_vector):
                            logger.warning(f"维度不匹配 (知识库 {db_path.name}): 查询={len(query_vector)}, 本地={len(doc_vector)}")
                            continue
                        
                        similarity = self._cosine_similarity(query_vector, doc_vector)
                        
                        if similarity >= threshold:
                            all_results.append({
                                "id": doc_id,
                                "database": db_path.name,
                                "content": content,
                                "source": source,
                                "score": float(similarity)
                            })
            except Exception as e:
                logger.error(f"知识库查询错误 ({db_path.name}): {e}")
                
        # 全局排序并截取 Top K
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """计算余弦相似度"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def get_vector_dimensions(self) -> Optional[int]:
        """获取整个知识库环境的参考向量维度（取随机一个有效库）"""
        for kb in self.list_knowledge_bases():
            if kb.get("dimension") is not None:
                return kb["dimension"]
        return None
