# cherry-mcp

将 [Cherry Studio](https://cherry-ai.com/) 的本地知识库通过 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 暴露给 AI 客户端（Cursor、Claude Desktop、opencode 等）。

[![npm version](https://img.shields.io/npm/v/cherry-mcp?style=flat-square)](https://www.npmjs.com/package/cherry-mcp)
[![Node.js](https://img.shields.io/badge/Node.js->=20-3c873a?style=flat-square)](https://nodejs.org)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

[快速开始](#快速开始) · [参数配置](#参数配置) · [可用工具](#可用工具) · [本地开发](#本地开发)

## 快速开始

在任何支持 MCP 的 AI 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "cherry-mcp": {
      "command": "npx",
      "args": [
        "-y", "cherry-mcp",
        "--embed-url", "http://127.0.0.1:1234",
        "--embed-model", "text-embedding-qwen3-embedding-8b",
        "--embed-dim", "4096"
      ]
    }
  }
}
```

> [!TIP]
> `--embed-api-key` 使用本地模型时可省略；首次执行 npm 会自动安装依赖。

### opencode 配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "cherry-mcp": {
      "type": "local",
      "command": [
        "npx", "-y", "cherry-mcp@latest",
        "--top-k", "10",
        "--threshold", "0.6",
        "--max-fetch", "1000",
        "--kb-path", "C:\\Users\\你的用户名\\AppData\\Roaming\\CherryStudio\\Data\\KnowledgeBase",
        "--embed-url", "http://127.0.0.1:1234",
        "--embed-model", "text-embedding-qwen3-embedding-8b",
        "--embed-dim", "4096"
      ],
      "enabled": true
    }
  }
}
```

## 参数配置

所有参数支持 CLI 传入，也可通过环境变量注入。**优先级**：`CLI 参数 > 环境变量`

> [!IMPORTANT]
> 以下参数为**必填**：`--embed-url`、`--embed-model`、`--embed-dim`

| CLI 参数 | 环境变量 | 默认值 | 说明 |
|:---------|:---------|:-------|:-----|
| `--top-k <n>` | `DEFAULT_TOP_K` | `20` | 最大返回结果数 |
| `--threshold <n>` | `DEFAULT_THRESHOLD` | `0.5` | 最低相似度阈值（0-1） |
| `--max-fetch <n>` | `MAX_FETCH` | `1000` | 每库最多读取的记录数 |
| `--kb-name <str>` | `DEFAULT_KB_NAME` | - | 限定搜索指定名称的知识库 |
| `--kb-path <dir>` | `CHERRYSTUDIO_KB_PATH` | Windows 自动识别 | 知识库根目录路径 |
| `--embed-url <url>` | `EMBEDDING_URL` | *(必填)* | Embedding API 地址 |
| `--embed-api-key` | `EMBEDDING_API_KEY` | - | API Token（本地模型可留空） |
| `--embed-model <id>` | `EMBEDDING_MODEL` | *(必填)* | 向量模型 ID |
| `--embed-dim <n>` | `EMBEDDING_DIMENSION` | *(必填)* | 向量维度（须与模型实际输出一致） |

## 可用工具

| 工具名 | 说明 |
|:-------|:-----|
| `list_knowledge_bases` | 列出所有知识库（名称、路径、向量数量、维度等） |
| `search_knowledge` | 向量相似度检索，返回最相关的文档片段 |

## 本地开发

```bash
# 克隆项目
git clone https://github.com/你的用户名/cherry-mcp.git
cd cherry-mcp

# 安装依赖
npm install

# 启动 MCP 服务（替换为自己的参数）
node src/index.js --embed-url "http://127.0.0.1:1234" --embed-model "text-embedding-qwen3-embedding-8b" --embed-dim 4096

# 或使用环境变量
EMBEDDING_URL=http://127.0.0.1:1234 EMBEDDING_MODEL=text-embedding-qwen3-embedding-8b EMBEDDING_DIMENSION=4096 node src/index.js
```

> [!NOTE]
> MCP 服务启动后会等待 IDE 客户端连接，不会显示交互界面。

## 前置要求

- Node.js >= 20
- 已运行 Cherry Studio 并创建至少一个知识库
- 可访问的 Embedding API（本地 LM Studio 或远程 SiliconFlow 等）
