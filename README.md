---
title: cherry-mcp
description: Cherry Studio 知识库 MCP 服务 - 通过直接读取 Cherry Studio 知识库数据库，实现智能问答
---

# cherry-mcp

Cherry Studio 知识库 MCP 服务，通过直接读取 Cherry Studio 知识库数据库，结合嵌入模型实现智能问答。

## 特性

- 直接读取 Cherry Studio 知识库 SQLite 数据库
- 支持多种嵌入模型服务商 (SiliconFlow、LM Studio、Ollama)
- 向量相似度搜索
- MCP 协议兼容 (stdio 方式连接)

## 架构流程
```
┌──────────────┐     ┌─────────────────┐     ┌────────────────┐     ┌─────────────┐
│   AI IDE     │────▶│  MCP Server     │────▶│  Knowledge Base │────▶│  Embedding  │
│ (Cline/opencode) │◀────│  (Python)       │◀────│   (SQLite)     │◀────│   Service   │
└──────────────┘     └─────────────────┘     └────────────────┘     └─────────────┘
```

## 环境要求

- Python 3.10+

## 快速开始

### 1. 克隆项目

```bash
git clone <repo-url>
cd cherry-mcp
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置

#### .env 文件（IDE 调用时使用）

在项目根目录创建 `.env` 文件：

```
CHERRYSTUDIO_KB_PATH=C:/Users/Theo/AppData/Roaming/CherryStudio/Data/KnowledgeBase
EMBEDDING_URL=https://api.siliconflow.cn
EMBEDDING_API_KEY=sk-your-api-key
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024
```

| 环境变量 | 说明 | 示例 |
|----------|------|------|
| CHERRYSTUDIO_KB_PATH | 知识库路径 | C:/Users/.../KnowledgeBase |
| EMBEDDING_URL | 嵌入模型 API 地址 | https://api.siliconflow.cn |
| EMBEDDING_API_KEY | API 密钥 | sk-xxx |
| EMBEDDING_MODEL | 嵌入模型 ID | BAAI/bge-m3 |
| EMBEDDING_DIMENSION | 向量维度 | 1024 |

> **重要**：嵌入模型配置必须与 Cherry Studio 创建知识库时使用的嵌入模型完全一致。

#### config.json（文档参考，仅供参考）

```json
{
  "cherry-mcp": {
    "search": {
      "default_top_k": 20,
      "default_threshold": 0.5,
      "max_fetch": 1000
    }
  }
}
```

> 注意：此文件仅用于文档参考，不参与代码运行。

### 5. 运行

```bash
python main.py
```

## 错误排查

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 嵌入失败 | API 错误 | 检查 url、api_key 配置 |
| 搜索无结果 | 向量维度不匹配 | 检查 dimension 是否与知识库一致 |
| 知识库未找到 | 路径错误 | 检查 path 配置是否正确 |

## 技术栈

- Python 3.10+
- MCP SDK
- httpx
- numpy
- SQLite

## 参考

- [Cherry Studio](https://cherry-ai.com)
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [SiliconFlow](https://siliconflow.cn)
