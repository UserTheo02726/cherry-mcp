---
title: cherry-mcp
description: Cherry Studio 知识库 MCP 服务
---

# cherry-mcp

> 将 [Cherry Studio](https://cherry-ai.com/) 的本地知识库通过 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 暴露给 AI 客户端（Cursor、Claude Desktop、opencode 等）。  
> 纯 Node.js 实现，**无需 Python、无需安装、开箱即用**。

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

> `--embed-api-key` 使用本地模型时可省略；首次执行 npm 会自动安装依赖。


## 参数配置

所有参数支持 CLI 传入，也可在 `env` 中以环境变量形式注入。  
**优先级**：`CLI 参数 > 环境变量 > 内置默认值`

- Windows 默认: C:\Users\<用户名>\AppData\Roaming\CherryStudio\Data\KnowledgeBase
- macOS  默认: ~/Library/Application Support/CherryStudio/Data/KnowledgeBase
- Linux  默认: ~/.config/CherryStudio/Data/KnowledgeBase

| CLI 参数             | 环境变量                  | 默认值                                   | 说明                               |
|:---------------------|:--------------------------|:-----------------------------------------|:-----------------------------------|
| `--top-k <n>`        | `DEFAULT_TOP_K`           | `20`                                     | 最大返回结果数                     |
| `--threshold <n>`    | `DEFAULT_THRESHOLD`       | `0.5`                                    | 最低相似度阈值（0–1）             |
| `--max-fetch <n>`    | `MAX_FETCH`               | `1000`                                   | 每库最多读取的记录数               |
| `--kb-name <str>`    | `DEFAULT_KB_NAME`         | *(空，搜索全部)*                         | 限定搜索指定名称的知识库           |
| `--kb-path <dir>`    | `CHERRYSTUDIO_KB_PATH`    | 跨平台自动识别 Cherry Studio 数据目录   | 知识库根目录路径                   |
| `--embed-url <url>`  | `EMBEDDING_URL`           | `http://127.0.0.1:1234/v1/embeddings`   | Embedding API 地址                 |
| `--embed-api-key`    | `EMBEDDING_API_KEY`       | *(空)*                                   | API Token（本地模型可留空）        |
| `--embed-model <id>` | `EMBEDDING_MODEL`         | `text-embedding-qwen3-embedding-8b`     | 向量模型 ID                        |
| `--embed-dim <n>`    | `EMBEDDING_DIMENSION`     | `4096`                                   | 向量维度（须与模型实际输出一致）  |

### 传入 CLI 参数示例

```json
{
  "command": "npx",
  "args": [
    "-y", "cherry-mcp",
    "--top-k", "10",
    "--threshold", "0.6",
    "--embed-url", "https://api.siliconflow.cn",
    "--embed-api-key", "sk-xxxx",
    "--embed-model", "BAAI/bge-m3",
    "--embed-dim", "1024"
  ]
}
```

## 可用工具 (MCP Tools)

| 工具名                   | 说明                                             |
|:-------------------------|:-------------------------------------------------|
| `list_knowledge_bases`   | 列出所有知识库（名称、路径、向量数量、维度等）  |
| `search_knowledge`       | 向量相似度检索，返回最相关的文档片段            |

## 本地开发

```bash
git clone https://github.com/<your-name>/cherry-mcp.git
cd cherry-mcp
npm install
node src/index.js --top-k 5
```

## 发布到 NPM

若要让任何电脑都能直接 `npx cherry-mcp`：

```bash
# 1. 注册并登录 npm 账号（仅首次）
npm login

# 2. 发布
npm publish
```

> 发布后，全球任何安装了 Node.js 的用户只需一句 `npx cherry-mcp` 即可使用。

## 所需前置

- Node.js ≥ 18（用于原生 `fetch` 与 `util.parseArgs`）
- 已运行 Cherry Studio 并建有至少一个知识库
- 可访问的 Embedding API（本地 LM Studio 或远程 SiliconFlow 等）
