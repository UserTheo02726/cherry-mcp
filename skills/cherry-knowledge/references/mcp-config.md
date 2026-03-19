# MCP 客户端配置模板

本文档提供各主流 AI 客户端的 MCP 配置方法。

## opencode（推荐）

在项目根目录创建或编辑 `opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "cherry-mcp": {
      "type": "local",
      "command": [
        "npx", "-y", "cherry-mcp@latest",
        "--embed-url", "http://127.0.0.1:1234",
        "--embed-model", "text-embedding-qwen3-embedding-8b",
        "--embed-dim", "4096"
      ],
      "enabled": true
    }
  }
}
```

### 完整参数示例

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

## Claude Desktop

编辑配置文件：

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

### 使用环境变量

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
      ],
      "env": {
        "EMBEDDING_URL": "http://127.0.0.1:1234",
        "EMBEDDING_MODEL": "text-embedding-qwen3-embedding-8b",
        "EMBEDDING_DIMENSION": "4096"
      }
    }
  }
}
```

## Cursor

创建或编辑项目级配置 `.cursor/mcp.json`（全局配置为 `~/.cursor/mcp.json`）：

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

修改后在 Cursor 中重启或重载窗口生效。

## VS Code（原生 MCP 支持）

> VS Code 1.99+ 原生支持 MCP，无需额外扩展。

创建或编辑 `.vscode/mcp.json`（项目级）或用户全局配置：

```json
{
  "servers": {
    "cherry-mcp": {
      "type": "stdio",
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

## 通用 stdio 模式

任何支持 stdio 模式的 MCP 客户端都可以使用：

```bash
npx -y cherry-mcp \
  --embed-url "http://127.0.0.1:1234" \
  --embed-model "text-embedding-qwen3-embedding-8b" \
  --embed-dim 4096
```

## 参数说明

| 参数 | 说明 | 必填 | 默认值 |
|------|------|------|--------|
| `--embed-url` | Embedding API 地址 | 是 | - |
| `--embed-model` | 向量模型 ID | 是 | - |
| `--embed-dim` | 向量维度 | 是 | - |
| `--embed-api-key` | API Token | 否 | - |
| `--top-k` | 返回结果数 | 否 | 20 |
| `--threshold` | 相似度阈值 | 否 | 0.5 |
| `--max-fetch` | 最大读取记录数 | 否 | 1000 |
| `--kb-path` | 知识库路径 | 否 | 自动识别 |
| `--kb-name` | 指定知识库名 | 否 | 全部 |

## Embedding API 示例

### 本地 LM Studio

```
--embed-url http://localhost:1234/v1/embeddings
--embed-model 本地模型ID
```

### SiliconFlow API

```
--embed-url https://api.siliconflow.cn/v1/embeddings
--embed-api-key 你的APIKey
--embed-model Pro/bge-large-zh-v1.5
```

### OpenAI 兼容 API

```
--embed-url https://api.openai.com/v1/embeddings
--embed-api-key 你的APIKey
--embed-model text-embedding-3-small
```
