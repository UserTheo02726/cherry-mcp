"""
知识库配置模块
"""
import os
from pathlib import Path
from typing import Optional

DEFAULT_KB_PATH = os.path.expanduser(
    "~\\AppData\\Roaming\\CherryStudio\\Data\\KnowledgeBase"
)
DEFAULT_LM_STUDIO_URL = "http://127.0.0.1:1234"
DEFAULT_EMBEDDING_MODEL = "text-embedding-qwen3-embedding-8b"
DEFAULT_EMBEDDING_DIMENSION = 4096
DEFAULT_TOP_K = 20
DEFAULT_THRESHOLD = 0.5
DEFAULT_MAX_FETCH = 1000


class EmbeddingConfig:
    """嵌入模型配置"""
    
    def __init__(self, config: Optional[dict] = None):
        config = config or {}
        
        base_url = config.get("url") or os.environ.get(
            "EMBEDDING_URL",
            DEFAULT_LM_STUDIO_URL
        )
        self.url = f"{base_url.rstrip('/')}/v1/embeddings"
        self.api_key = config.get("api_key") or os.environ.get("EMBEDDING_API_KEY", "")
        self.model = config.get("model") or os.environ.get(
            "EMBEDDING_MODEL",
            DEFAULT_EMBEDDING_MODEL
        )
        self.dimension = config.get("dimension") or int(os.environ.get(
            "EMBEDDING_DIMENSION",
            DEFAULT_EMBEDDING_DIMENSION
        ))
    
    @property
    def headers(self) -> dict:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


class SearchConfig:
    """搜索配置"""
    
    def __init__(self, config: Optional[dict] = None):
        config = config or {}
        
        self.default_top_k = int(config.get("default_top_k") or os.environ.get("DEFAULT_TOP_K", DEFAULT_TOP_K))
        self.default_threshold = float(config.get("default_threshold") or os.environ.get("DEFAULT_THRESHOLD", DEFAULT_THRESHOLD))
        self.max_fetch = int(config.get("max_fetch") or os.environ.get("MAX_FETCH", DEFAULT_MAX_FETCH))


class KnowledgeBaseConfig:
    """知识库配置类"""
    
    def __init__(self, config_dict: Optional[dict] = None):
        kb_config = config_dict or {}
        
        self.path = kb_config.get("path") or os.environ.get(
            "CHERRYSTUDIO_KB_PATH",
            DEFAULT_KB_PATH
        )
        
        embedding_config = kb_config.get("embedding", {})
        self.embedding = EmbeddingConfig(embedding_config)
        
        search_config = kb_config.get("search", {})
        self.search = SearchConfig(search_config)
    
    @property
    def kb_path(self) -> str:
        """知识库路径"""
        return self.path
    
    @property
    def exists(self) -> bool:
        """知识库目录是否存在"""
        return Path(self.path).exists()


_config: Optional[KnowledgeBaseConfig] = None


def get_kb_config(config_dict: Optional[dict] = None, force: bool = False) -> KnowledgeBaseConfig:
    """获取知识库配置单例
    
    Args:
        config_dict: 配置字典
        force: 强制重新创建配置
    """
    global _config
    if _config is None or force:
        _config = KnowledgeBaseConfig(config_dict)
    return _config


def reset_kb_config():
    """重置配置单例"""
    global _config
    _config = None
