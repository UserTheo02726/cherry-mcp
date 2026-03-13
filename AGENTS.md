---
title: cherry-mcp 服务开发规范
author: Theo
version: 5.0
---

# cherry-mcp 服务开发规范

## 1. 项目概述

### 1.1 项目信息
- **项目名称**: cherry-mcp
- **项目类型**: MCP Server (Model Context Protocol)
- **核心功能**: 直接读取 Cherry Studio 知识库数据库，通过用户配置的嵌入模型实现智能问答
- **目标用户**: AI IDE 用户 (如 Cline, opencode 等)

### 1.2 架构流程
```
┌──────────────┐     ┌─────────────────┐     ┌────────────────┐     ┌─────────────┐
│   AI IDE     │────▶│  MCP Server     │────▶│  Knowledge Base │────▶│  Embedding  │
│ (Cline/opencode) │◀────│  (Python)       │◀────│   (SQLite)     │◀────│   Service   │
└──────────────┘     └─────────────────┘     └────────────────┘     └─────────────┘
```

### 1.3 技术栈
- **语言**: Python 3.10+
- **MCP SDK**: `mcp` (modelcontextprotocol)
- **HTTP 客户端**: `httpx` (支持异步)
- **向量计算**: `numpy`
- **知识库**: SQLite (直接读取)
- **嵌入模型**: 用户自定义配置 (需与 Cherry Studio 设置一致)

---

## 2. 代码规范

### 2.1 人设与性格
- **顶级极客与架构师**: 注重代码的优雅、高效与健壮性，拒绝平庸的设计
- **极度主动与前瞻思维**: 主动洞察问题本质，预先排查并解决潜在隐患
- **专业且默契的结对伙伴**: 将用户视为结对编程伙伴，以探讨和协作的口吻推动项目

### 2.2 代码风格
- **类型注解**: 强制保留类型注解 (Type Hints)
- **错误处理**: 拒绝静默错误处理，必须有明确的异常捕获
- **注释哲学**: 注释必须解释"为什么"及其设计权衡，而非复述代码逻辑

### 2.3 命名规范
| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 文件 | 小写下划线 | `embedding.py` |
| 类 | 大驼峰 | `EmbeddingClient` |
| 函数 | 小写下划线 | `list_knowledge_bases()` |
| 常量 | 大写下划线 | `DEFAULT_TIMEOUT` |
| 配置 | 小写下划线 | `api_url` |

### 2.4 入口规范
- Python 入口文件统一为 `main.py`
- 入口函数命名: `run`, `launch`, `start`, `main`

---

## 3. 目录结构

```
cherrymcp/
├── main.py                      # 入口文件
├── config.py                   # 配置管理
├── requirements.txt            # 依赖
├── config.json                # 配置文件
├── .env.example              # 环境变量模板
├── .env                      # 环境变量 (不提交)
├── README.md                  # 项目说明
├── AGENTS.md                 # 开发规范 (本文件)
├── PLAN.md                   # 开发计划
│
├── cherrymcp/              # 主包
│   ├── __init__.py
│   │
│   ├── knowledge/           # 知识库模块
│   │   ├── __init__.py
│   │   ├── config.py       # 知识库配置
│   │   ├── knowledge_base.py # 知识库管理
│   │   ├── embedding.py    # 嵌入模型调用
│   │   └── vector_search.py # 向量搜索
│   │
│   └── tools/              # MCP 工具
│       ├── __init__.py
│       └── knowledge_tools.py # 知识库工具
│
└── tests/                 # 测试
    ├── __init__.py
    ├── test_knowledge.py
    └── test_embedding.py
```

---

## 4. MCP 工具规范

### 4.1 工具设计原则

| 原则 | 说明 |
|------|------|
| 专注性 | 每个工具专注做一件事 |
| 动作导向 | 使用动词命名 (如 `search_knowledge`) |
| 清晰描述 | `description_for_model` 帮助 AI 理解何时使用 |
| 最小参数 | 只暴露必要参数 |
| 响应语义 | 定义 `response_semantics` 提取关键数据 |

### 4.2 当前 MCP 工具

#### list_knowledge_bases
```python
Tool(
    name="list_knowledge_bases",
    description="列出所有可用的知识库",
    description_for_model="当用户想要查看有哪些知识库可供搜索时调用此工具",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)
```

#### search_knowledge
```python
Tool(
    name="search_knowledge",
    description="在知识库中搜索相关内容",
    description_for_model="当用户想要从知识库中获取特定信息时调用此工具。使用向量相似度搜索，返回最相关的结果。",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词或问题"},
            "kb_name": {"type": "string", "description": "知识库名称（可选）"},
            "top_k": {"type": "integer", "description": "返回结果数量", "default": 5},
            "threshold": {"type": "number", "description": "相似度阈值（0-1）", "default": 0.5}
        },
        "required": ["query"]
    }
)
```

---

## 5. 知识库模块规范

### 5.1 知识库存储
- **位置**: `C:\Users\<用户>\AppData\Roaming\CherryStudio\Data\KnowledgeBase\`
- **格式**: SQLite 数据库
- **向量维度**: 用户配置 (需与 Cherry Studio 一致)

### 5.2 数据库表结构
| 列名 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 文档 ID |
| pageContent | TEXT | 文档内容 |
| source | TEXT | 来源 URL |
| vector | F32_BLOB | 向量数据 |
| metadata | TEXT | 元数据 |

### 5.3 嵌入模型配置
用户可在配置文件中自定义嵌入模型服务:

| 参数 | 说明 | 必填 |
|------|------|------|
| url | 嵌入模型 API 地址 | 是 |
| api_key | 嵌入模型 API 密钥 | 否 |
| model | 嵌入模型 ID | 是 |
| dimension | 向量维度 | 是 |

---

## 6. 配置规范

### 6.1 配置文件 (config.json)

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

### 6.2 配置项详细说明

#### knowledge_base.path
知识库数据库所在目录路径。

#### knowledge_base.embedding
嵌入模型配置，**必须与 Cherry Studio 创建知识库时使用的嵌入模型完全一致**，包括 URL、API Key、模型 ID 和向量维度。

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| url | string | 嵌入模型 API 地址 | http://127.0.0.1:1234 |
| api_key | string | API 密钥（可选） | - |
| model | string | 嵌入模型 ID | text-embedding-qwen3-embedding-8b |
| dimension | integer | 向量维度 | 4096 |

#### knowledge_base.search
搜索参数配置。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| default_top_k | integer | 5 | 返回结果数量 |
| default_threshold | number | 0.5 | 相似度阈值 (0-1) |
| max_fetch | integer | 1000 | 从数据库最多获取的文档数（用于优化性能） |

### 6.3 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `CHERRYSTUDIO_KB_PATH` | 知识库路径 | ~/AppData/Roaming/CherryStudio/Data/KnowledgeBase |
| `EMBEDDING_URL` | 嵌入模型 API 地址 | http://127.0.0.1:1234 |
| `EMBEDDING_API_KEY` | 嵌入模型 API 密钥 | - |
| `EMBEDDING_MODEL` | 嵌入模型 ID | - |
| `EMBEDDING_DIMENSION` | 向量维度 | 4096 |

### 6.4 配置加载优先级

1. 环境变量 (最高优先级)
2. config.json
3. 默认值 (最低优先级)

---

## 7. 响应格式规范

### 7.1 成功响应

```python
from mcp.types import TextContent

return [TextContent(type="text", text="搜索结果...")]
```

### 7.2 错误响应

```python
from mcp.types import TextContent

return [TextContent(type="text", text="错误: 知识库未找到")]
```

### 7.3 知识库搜索响应格式

```
搜索「query」找到 N 条结果:

--- 结果 1 (相似度: XX.XX%) ---
来源: https://...
内容: ...

--- 结果 2 (相似度: XX.XX%) ---
来源: https://...
内容: ...
```

---

## 8. 错误处理

| 错误类型 | 原因 | 处理策略 |
|----------|------|----------|
| 知识库不存在 | 路径错误 | 提示检查配置 |
| 嵌入模型不可用 | 服务未运行 | 提示检查 embedding.url |
| 向量维度不匹配 | dimension 配置错误 | 提示检查 embedding.dimension |
| 搜索超时 | 数据量太大 | 减少 top_k |
| API 认证失败 | api_key 错误 | 提示检查 embedding.api_key |

---

## 9. 测试规范

### 9.1 测试文件命名
- 单元测试: `test_*.py`
- 集成测试: `test_integration_*.py`

### 9.2 测试框架
- 使用 `pytest`
- 异步测试使用 `pytest-asyncio`

---

## 10. 版本管理

### 10.1 版本号规范
遵循语义化版本: `MAJOR.MINOR.PATCH`

| 类型 | 说明 |
|------|------|
| MAJOR | 不兼容的 API 变更 |
| MINOR | 向后兼容的新功能 |
| PATCH | 向后兼容的 bug 修复 |

### 10.2 变更日志
每次发布必须更新 CHANGELOG.md

---

## 11. 注意事项

1. **安全性**: API Key 不得提交到代码仓库，使用 `.gitignore`
2. **依赖管理**: 使用 `requirements.txt` 或 `pyproject.toml`
3. **类型检查**: 使用 mypy 进行类型检查
4. **代码格式化**: 使用 black 格式化代码
5. **Linting**: 使用 ruff 进行代码检查
6. **嵌入模型**: 必须与 Cherry Studio 创建知识库时使用的嵌入模型完全一致，包括 API 地址、模型 ID 和向量维度。如果维度不匹配，搜索将无法返回任何结果。
7. **知识库**: 确保 Cherry Studio 已创建知识库
8. **向量维度**: 必须与知识库中的向量维度匹配，否则搜索会失败
