---
title: cherry-mcp 开发计划
author: Theo
date: 2026-03-13
version: 7.0
---

# cherry-mcp 开发计划

## 1. 项目概述

### 1.1 目标
创建一个 MCP 服务，通过直接读取 Cherry Studio 知识库数据库 + 用户配置的嵌入模型，实现智能问答功能。

### 1.2 架构流程
```
┌──────────────┐     ┌─────────────────┐     ┌────────────────┐     ┌─────────────┐
│   AI IDE     │────▶│  MCP Server     │────▶│  Knowledge Base │────▶│  Embedding  │
│ (Cline/opencode) │◀────│  (Python)       │◀────│   (SQLite)     │◀────│   Service   │
└──────────────┘     └─────────────────┘     └────────────────┘     └─────────────┘
```

### 1.3 技术方案
- **语言**: Python 3.10+
- **MCP SDK**: `mcp` (modelcontextprotocol)
- **HTTP 客户端**: `httpx` (支持异步)
- **向量计算**: `numpy`
- **知识库**: SQLite (直接读取)
- **嵌入模型**: 用户自定义配置 (需与 Cherry Studio 设置一致)

---

## 2. 需求分析

### 2.1 知识库存储
- **位置**: `C:\Users\<用户>\AppData\Roaming\CherryStudio\Data\KnowledgeBase\`
- **格式**: SQLite 数据库
- **向量维度**: 用户配置 (需与 Cherry Studio 一致)

### 2.2 知识库表结构
| 列名 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 文档 ID |
| pageContent | TEXT | 文档内容 |
| uniqueLoaderId | TEXT | 加载器 ID |
| source | TEXT | 来源 URL |
| vector | F32_BLOB | 向量数据 |
| metadata | TEXT | 元数据 |

### 2.3 嵌入模型配置
用户可配置的嵌入模型参数:

| 参数 | 说明 | 必填 |
|------|------|------|
| url | 嵌入模型 API 地址 | 是 |
| api_key | 嵌入模型 API 密钥 | 否 |
| model | 嵌入模型 ID | 是 |
| dimension | 向量维度 | 是 |

---

## 3. 技术方案

### 3.1 技术栈
- **语言**: Python 3.10+
- **MCP SDK**: `mcp` (modelcontextprotocol)
- **HTTP 客户端**: `httpx`
- **向量计算**: `numpy`
- **连接方式**: stdio

### 3.2 配置文件 (config.json)
```json
{
  "knowledge_base": {
    "path": "C:/Users/Theo/AppData/Roaming/CherryStudio/Data/KnowledgeBase",
    "embedding": {
      "url": "http://127.0.0.1:1234",
      "api_key": "",
      "model": "text-embedding-qwen3-embedding-8b",
      "dimension": 4096
    },
    "search": {
      "default_top_k": 5,
      "default_threshold": 0.5,
      "max_fetch": 1000
    }
  }
}
```

### 3.3 环境变量
| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| CHERRYSTUDIO_KB_PATH | 知识库路径 | ~/AppData/Roaming/CherryStudio/Data/KnowledgeBase |
| EMBEDDING_URL | 嵌入模型 API 地址 | http://127.0.0.1:1234 |
| EMBEDDING_API_KEY | 嵌入模型 API 密钥 | - |
| EMBEDDING_MODEL | 嵌入模型 ID | - |
| EMBEDDING_DIMENSION | 向量维度 | 4096 |

### 3.4 MCP 工具设计原则

| 原则 | 说明 |
|------|------|
| 专注性 | 每个工具专注做一件事 |
| 动作导向 | 使用动词命名 (如 search_knowledge) |
| 清晰描述 | description_for_model 帮助 AI 理解何时使用 |
| 最小参数 | 只暴露必要参数 |
| 响应语义 | 定义 response_semantics 提取关键数据 |

### 3.5 MCP 工具设计

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `list_knowledge_bases` | 列出所有知识库 | 无 |
| `search_knowledge` | 搜索知识库内容 | query, kb_name, top_k, threshold |

### 3.6 目录结构

```
cherrymcp/
├── main.py                      # 入口文件
├── config.py                   # 配置管理
├── requirements.txt             # 依赖
├── config.json                 # 配置文件
├── .env.example              # 环境变量模板
│
├── cherrymcp/              # 主包
│   ├── __init__.py
│   │
│   ├── knowledge/             # 知识库模块 (已实现)
│   │   ├── __init__.py
│   │   ├── config.py         # 知识库配置
│   │   ├── knowledge_base.py # 知识库管理
│   │   ├── embedding.py      # 嵌入模型调用
│   │   └── vector_search.py  # 向量搜索
│   │
│   └── tools/                 # MCP 工具
│       ├── __init__.py
│       └── knowledge_tools.py # 知识库工具
│
└── tests/                    # 测试
    ├── __init__.py
    ├── test_knowledge.py
    └── test_embedding.py
```

---

## 4. 实施计划

### Phase 1: 知识库模块 (已完成)
- [x] 创建 `knowledge/` 目录结构
- [x] 实现 `knowledge_base.py`
- [x] 实现 `embedding.py`
- [x] 实现 `vector_search.py`

### Phase 2: MCP 工具 (已完成)
- [x] 实现 `knowledge_tools.py`
- [x] 实现 `list_knowledge_bases` 工具
- [x] 实现 `search_knowledge` 工具
- [x] 更新 `main.py` - 集成知识库工具

### Phase 3: 清理与优化 (已完成)
- [x] 删除 Cherry Studio API 客户端 (不再需要)
- [x] 简化配置结构
- [x] 更新文档

### Phase 4: 性能优化 (已完成)
- [x] 添加 max_fetch 配置项，限制从数据库获取的文档数量
- [ ] 单元测试
- [ ] 集成测试
- [ ] 错误处理优化
- [ ] 性能优化

### Phase 5: 文档与部署
- [ ] README 文档
- [ ] 使用示例
- [ ] 配置说明

---

## 5. 配置项详细说明

### 5.1 knowledge_base.embedding

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| url | string | 嵌入模型 API 地址 | http://127.0.0.1:1234 |
| api_key | string | API 密钥（可选） | - |
| model | string | 嵌入模型 ID | text-embedding-qwen3-embedding-8b |
| dimension | integer | 向量维度 | 4096 |

### 5.2 knowledge_base.search

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| default_top_k | integer | 5 | 返回结果数量 |
| default_threshold | number | 0.5 | 相似度阈值 (0-1) |
| max_fetch | integer | 1000 | 从数据库最多获取的文档数 |

---

## 6. 错误处理

| 错误类型 | 原因 | 处理策略 |
|----------|------|----------|
| 知识库不存在 | 路径错误 | 提示检查配置 |
| 嵌入模型不可用 | 服务未运行 | 提示检查 embedding.url |
| 向量维度不匹配 | dimension 配置错误 | 提示检查 embedding.dimension |
| 搜索超时 | 数据量太大 | 减少 top_k |
| API 认证失败 | api_key 错误 | 提示检查 embedding.api_key |

---

## 7. 待确认问题

- [x] 嵌入模型支持多种服务商 (SiliconFlow、LM Studio、Ollama 等)
- [x] 支持多个知识库切换
- [x] 向量搜索参数可配置
- [x] 用户自定义嵌入模型参数 (url, api_key, model, dimension)

---

## 8. 参考资源

- MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- Cherry Studio 知识库: `~/AppData/Roaming/CherryStudio/Data/KnowledgeBase/`
