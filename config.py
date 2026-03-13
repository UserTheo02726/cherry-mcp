"""
配置管理模块

提供配置加载功能，支持环境变量和配置文件两种方式
"""
import json
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """cherry-mcp 配置类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self._knowledge_base_config: Optional[dict] = None
        
        load_dotenv()
        self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str] = None):
        """从配置文件加载配置"""
        if config_path is None:
            config_path = "config.json"
        
        config_file = Path(config_path)
        
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            self._knowledge_base_config = config_data.get("knowledge_base")
    
    @property
    def knowledge_base_config(self) -> Optional[dict]:
        """知识库配置"""
        return self._knowledge_base_config


_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None, force: bool = False) -> Config:
    """获取全局配置单例"""
    global _config
    if _config is None or force:
        _config = Config(config_path)
    return _config
