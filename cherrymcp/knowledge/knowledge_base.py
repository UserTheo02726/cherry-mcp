"""
知识库管理模块

提供对 Cherry Studio 知识库数据库的访问能力
"""
import sqlite3
from pathlib import Path
from typing import Optional
import numpy as np

from .config import get_kb_config, KnowledgeBaseConfig


class KnowledgeBaseManager:
    """Cherry Studio 知识库管理器"""
    
    def __init__(self, config: Optional[KnowledgeBaseConfig] = None):
        self.config = config or get_kb_config()
        self._db_path: Optional[str] = None
        self._find_knowledge_base()
    
    def _find_knowledge_base(self):
        """查找知识库数据库"""
        kb_dir = Path(self.config.kb_path)
        
        if not kb_dir.exists():
            return
        
        for item in kb_dir.iterdir():
            if item.is_file() and item.suffix in [".db", ".sqlite", ""]:
                self._db_path = str(item)
                return
            
            if item.is_dir():
                for db_file in item.iterdir():
                    if db_file.is_file():
                        self._db_path = str(db_file)
                        return
    
    @property
    def db_path(self) -> Optional[str]:
        """获取数据库路径"""
        return self._db_path
    
    def list_knowledge_bases(self) -> list[dict]:
        """列出所有知识库"""
        kb_dir = Path(self.config.kb_path)
        
        if not kb_dir.exists():
            return []
        
        results = []
        for item in kb_dir.iterdir():
            if item.is_file():
                results.append({
                    "name": item.stem,
                    "path": str(item),
                    "size": item.stat().st_size
                })
            elif item.is_dir():
                for db_file in item.iterdir():
                    if db_file.is_file():
                        results.append({
                            "name": db_file.stem,
                            "path": str(db_file),
                            "size": db_file.stat().st_size
                        })
        
        return results
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.0,
        max_fetch: int = 1000
    ) -> list[dict]:
        """搜索知识库
        
        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            threshold: 相似度阈值
            max_fetch: 从数据库最多获取的文档数
            
        Returns:
            搜索结果列表
        """
        if not self._db_path:
            return []
        
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, pageContent, source, vector FROM vectors LIMIT ?",
                (max_fetch,)
            )
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                doc_id, content, source, vector_bytes = row
                
                if not vector_bytes or not content:
                    continue
                
                doc_vector = np.frombuffer(vector_bytes, dtype=np.float32)
                
                if len(doc_vector) != len(query_vector):
                    continue
                
                similarity = self._cosine_similarity(query_vector, doc_vector)
                
                if similarity >= threshold:
                    results.append({
                        "id": doc_id,
                        "content": content,
                        "source": source,
                        "score": float(similarity)
                    })
            
            conn.close()
            
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            print(f"知识库搜索错误: {e}")
            return []
    
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
        """获取向量维度"""
        if not self._db_path:
            return None
        
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT vector FROM vectors LIMIT 1")
            row = cursor.fetchone()
            
            conn.close()
            
            if row and row[0]:
                return len(np.frombuffer(row[0], dtype=np.float32))
            
            return None
        
        except Exception:
            return None
