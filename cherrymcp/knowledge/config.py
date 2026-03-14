"""
知识库配置模块
"""
import os
import platform
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

def _get_default_kb_path() -> str:
    """获取跨平台的默认知识库路径"""
    system = platform.system()
    if system == "Windows":
        return os.path.expanduser("~\\AppData\\Roaming\\CherryStudio\\Data\\KnowledgeBase")
    elif system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/CherryStudio/Data/KnowledgeBase")
    else:  # Linux (including WSL)
        return os.path.expanduser("~/.config/CherryStudio/Data/KnowledgeBase")

DEFAULT_KB_PATH = _get_default_kb_path()
DEFAULT_LM_STUDIO_URL = "http://127.0.0.1:1234"
DEFAULT_EMBEDDING_MODEL = "text-embedding-qwen3-embedding-8b"
DEFAULT_EMBEDDING_DIMENSION = 4096
DEFAULT_TOP_K = 20
DEFAULT_THRESHOLD = 0.5
DEFAULT_MAX_FETCH = 1000


class EmbeddingConfig(BaseModel):
    """嵌入模型配置"""
    url: str = Field(default_factory=lambda: os.environ.get("EMBEDDING_URL", DEFAULT_LM_STUDIO_URL))
    api_key: str = Field(default_factory=lambda: os.environ.get("EMBEDDING_API_KEY", ""))
    model: str = Field(default_factory=lambda: os.environ.get("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL))
    dimension: int = Field(default_factory=lambda: int(os.environ.get("EMBEDDING_DIMENSION", DEFAULT_EMBEDDING_DIMENSION)))

    def __init__(self, **data):
        super().__init__(**data)
        # 确保 URL 正确追加 /v1/embeddings
        if not self.url.endswith("/v1/embeddings"):
            self.url = f"{self.url.rstrip('/')}/v1/embeddings"

    @property
    def headers(self) -> dict:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


class SearchConfig(BaseModel):
    """搜索配置"""
    default_top_k: int = Field(default_factory=lambda: int(os.environ.get("DEFAULT_TOP_K", DEFAULT_TOP_K)))
    default_threshold: float = Field(default_factory=lambda: float(os.environ.get("DEFAULT_THRESHOLD", DEFAULT_THRESHOLD)))
    max_fetch: int = Field(default_factory=lambda: int(os.environ.get("MAX_FETCH", DEFAULT_MAX_FETCH)))


class KnowledgeBaseConfig(BaseModel):
    """知识库配置类"""
    path: str = Field(default_factory=lambda: os.environ.get("CHERRYSTUDIO_KB_PATH", DEFAULT_KB_PATH))
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

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
        if config_dict:
            embedding_data = config_dict.pop("embedding", {})
            search_data = config_dict.pop("search", {})
            
            embedding_config = EmbeddingConfig(**embedding_data)
            search_config = SearchConfig(**search_data)
            
            _config = KnowledgeBaseConfig(
                **config_dict,
                embedding=embedding_config,
                search=search_config
            )
        else:
            _config = KnowledgeBaseConfig()
    return _config


def reset_kb_config():
    """重置配置单例"""
    global _config
    _config = None
