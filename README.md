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

复制配置模板并编辑：

```bash
copy config.example.json config.json
```

编辑 `config.json`，填入你的嵌入模型配置。

| 配置项 | 说明 | 示例 |
|--------|------|------|
| url | 嵌入模型 API 地址 | https://api.siliconflow.cn |
| api_key | API 密钥 | sk-xxx |
| model | 嵌入模型 ID | BAAI/bge-m3 |
| dimension | 向量维度 | 1024 |

> **重要**：嵌入模型配置必须与 Cherry Studio 创建知识库时使用的嵌入模型完全一致，包括 URL、API Key、模型 ID 和向量维度。

### 5. 运行

```bash
python main.py
```

## 配置说明

### knowledge_base.embedding

```json
{
  "url": "https://api.siliconflow.cn",
  "api_key": "sk-your-api-key-here",
  "model": "BAAI/bge-m3",
  "dimension": 1024
}
```

| 参数 | 说明 |
|------|------|
| url | 嵌入模型 API 地址 |
| api_key | API 密钥 (可选) |
| model | 嵌入模型 ID |
| dimension | 向量维度 (必须与知识库一致) |

### knowledge_base.search

| 参数 | 默认值 | 说明 |
|------|--------|------|
| default_top_k | 20 | 返回结果数量 |
| default_threshold | 0.5 | 相似度阈值 (0-1) |
| max_fetch | 1000 | 从数据库最多获取的文档数 |

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
