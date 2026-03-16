---
title: cherry-mcp
description: Cherry Studio 知识库 MCP 服务
---

# cherry-mcp

> 将 [Cherry Studio](https://cherry-ai.com/) 的本地知识库通过 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 暴露给 AI 客户端（Cursor、Claude Desktop、opencode 等）。  


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

## IDE配置

### opencode
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "cherry-mcp": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "cherry-mcp@latest",
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

> `--embed-api-key` 使用本地模型时可省略；首次执行 npm 会自动安装依赖。


## 参数配置

所有参数支持 CLI 传入，也可在 `env` 中以环境变量形式注入。  
**优先级**：`CLI 参数 > 环境变量`

> ⚠️ 以下参数为**必填**： `--embed-url`、`--embed-model`、`--embed-dim`

- Windows 默认: C:\Users\<用户名>\AppData\Roaming\CherryStudio\Data\KnowledgeBase

| CLI 参数             | 环境变量                  | 默认值                                   | 说明                               |
|:---------------------|:--------------------------|:-----------------------------------------|:-----------------------------------|
| `--top-k <n>`        | `DEFAULT_TOP_K`           | `20`                                     | 最大返回结果数                     |
| `--threshold <n>`    | `DEFAULT_THRESHOLD`       | `0.5`                                    | 最低相似度阈值（0–1）             |
| `--max-fetch <n>`    | `MAX_FETCH`               | `1000`                                   | 每库最多读取的记录数               |
| `--kb-name <str>`    | `DEFAULT_KB_NAME`         | *(空，搜索全部)*                         | 限定搜索指定名称的知识库           |
| `--kb-path <dir>`    | `CHERRYSTUDIO_KB_PATH`    | *(仅 Windows 自动识别，其他平台需手动指定)* | 知识库根目录路径                   |
| `--embed-url <url>`  | `EMBEDDING_URL`           | *(必填)*                                 | Embedding API 地址                 |
| `--embed-api-key`    | `EMBEDDING_API_KEY`       | *(空)*                                   | API Token（本地模型可留空）        |
| `--embed-model <id>` | `EMBEDDING_MODEL`         | *(必填)*                                 | 向量模型 ID                        |
| `--embed-dim <n>`    | `EMBEDDING_DIMENSION`     | *(必填)*                                 | 向量维度（须与模型实际输出一致）  |

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

> ⚠️ MCP 服务启动后会等待 IDE 客户端连接，不会显示交互界面。

```bash
# 克隆项目
git clone https://github.com/<your-name>/cherry-mcp.git
cd cherry-mcp

# 安装依赖
npm install

# 启动 MCP 服务（等待 IDE 客户端连接）(替换自己的参数)
node src/index.js --embed-url "http://127.0.0.1:1234" --embed-model "text-embedding-qwen3-embedding-8b" --embed-dim 4096

# 或者
EMBEDDING_URL=http://127.0.0.1:1234 EMBEDDING_MODEL=text-embedding-qwen3-embedding-8b EMBEDDING_DIMENSION=4096 node src/index.js

```

## 本地测试工具

> 直接运行脚本测试，无需启动 MCP 服务。

```bash
# 测试 list_knowledge_bases
node -e "
import { listKnowledgeBases } from './src/database.js';
const kbs = await listKnowledgeBases();
console.log(JSON.stringify(kbs, null, 2));
" --embed-url "http://127.0.0.1:1234" --embed-model "text-embedding-qwen3-embedding-8b" --embed-dim 4096

# 测试 search_knowledge（需要 embedding 服务运行中）
node -e "
import { embedText, searchVectors } from './src/embedding.js';
const queryVector = await embedText('你的查询');
const results = await searchVectors(queryVector, { topK: 3, threshold: 0.3 });
for (const r of results) {
  console.log('--- 相似度:', (r.score * 100).toFixed(1) + '% ---');
  console.log('来源:', r.source);
  console.log('内容:', r.content.substring(0, 200) + '...');
  console.log('');
}
" --embed-url "http://127.0.0.1:1234" --embed-model "text-embedding-qwen3-embedding-8b" --embed-dim 4096
```

## 所需前置

- Node.js ≥ 18（用于原生 `fetch` 与 `util.parseArgs`）
- 已运行 Cherry Studio 并建有至少一个知识库
- 可访问的 Embedding API（本地 LM Studio 或远程 SiliconFlow 等）

## 后续优化计划

> 以下是计划中的功能改进和缺陷修复，待逐步实现。

### 高优先级

- [x] **配置 NPM_TOKEN**：在 GitHub 仓库 Secrets 中添加 NPM_TOKEN，并取消 `.github/workflows/publish.yml` 中的发布步骤注释
- [x] **移除硬编码默认值**：修改 `config.js`，移除 `embedModel` 和 `embedDim` 的默认值，要求用户必须显式提供
- [x] **移除不确定路径**：修改 `getDefaultKbPath()`，移除不确定的 Linux/macOS 路径避免误导
- [x] **发布到 npm**：配置完成后，首次发布到 npm 并验证 `npx cherry-mcp` 可正常运行

### 待定

- [ ] 支持 SSE 传输模式（HTTP 远程调用）
- [ ] 添加健康检查工具
