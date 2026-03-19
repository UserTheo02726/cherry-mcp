---
name: cherry-knowledge
description: |
  Cherry Studio 本地知识库搜索助手。
  当用户想要搜索本地文档、查询 Cherry Studio 知识库、在知识库中找资料时使用此 skill。
  也适用于用户询问如何配置、使用 Cherry Studio MCP 服务的场景。
  确保在用户提到"知识库"、"Cherry Studio"、"搜索文档"、"找资料"时主动触发此 skill。
---

# Cherry Studio 知识库搜索 Skill

本 skill 为 Cherry Studio 本地知识库提供搜索能力。通过 MCP 协议，用户可以在 AI 客户端中直接搜索本地知识库文档。

## 前置条件

使用此 skill 前，用户需要满足以下条件：

1. **Node.js >= 20** - 运行 MCP 服务需要
2. **Cherry Studio 已运行** - 且创建过至少一个知识库
3. **Embedding API** - 本地 LM Studio 或远程 SiliconFlow 等

## 快速开始

### 1. 配置 MCP

根据用户使用的 AI 客户端，参考 `references/mcp-config.md` 进行配置：

- **opencode** - 推荐配置方式
- **Claude Desktop**
- **Cursor**
- **其他 MCP 客户端**

### 2. 必填参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--embed-url` | Embedding API 地址 | `http://127.0.0.1:1234` |
| `--embed-model` | 向量模型 ID | `text-embedding-qwen3-embedding-8b` |
| `--embed-dim` | 向量维度 | `4096` |

详细参数说明见 `references/cli-params.md`

### 3. 可用工具

MCP 服务暴露两个工具：

| 工具名 | 说明 |
|--------|------|
| `list_knowledge_bases` | 列出所有知识库（名称、路径、向量数量、维度等） |
| `search_knowledge` | 向量相似度检索，返回最相关的文档片段 |

## 使用示例

### 示例 1：列出知识库

```
用户：列出我的知识库
AI：调用 list_knowledge_bases 工具
```

返回示例：
```
发现 2 个知识库：

**mW3rzDuJfCoDSKMi0nE5J**
  路径: C:\Users\Theo\AppData\Roaming\CherryStudio\Data\KnowledgeBase\mW3rzDuJfCoDSKMi0nE5J.db
  大小: 2.82 MB | 向量数: 378 | 维度: 1024

**wgDxA02hPN2Bm0DAXHkFc**
  路径: C:\Users\Theo\AppData\Roaming\CherryStudio\Data\KnowledgeBase\wgDxA02hPN2Bm0DAXHkFc.db
  大小: 1.05 MB | 向量数: 124 | 维度: 1024
```

> **注意**：知识库名称是 Cherry Studio 自动生成的 Base62 随机 ID（如 `mW3rzDuJfCoDSKMi0nE5J`），**并非** Cherry Studio UI 中显示的知识库别名。
> 使用 `kb_name` 参数时须填写此 ID，而不是 UI 里起的名字。
> 知识库文件名与 Cherry Studio UI 中显示的知识库别名无关。文件名才是 MCP 真正使用的知识库名称。

### 示例 2：搜索文档

```
用户：搜索关于 React 组件优化的内容
AI：调用 search_knowledge 工具，query="React 组件优化"
```

返回示例：
```
搜索「React 组件优化」，共 3 条结果：

--- 结果 1（相似度: 92.3%）---
来源: docs/react/performance.md
使用 React.memo() 包裹纯展示组件可以避免不必要的重新渲染...

--- 结果 2（相似度: 87.1%）---
来源: docs/react/hooks.md
useCallback 和 useMemo 用于缓存函数和计算结果...

--- 结果 3（相似度: 82.5%）---
来源: notes/优化技巧.txt
避免在 useEffect 中直接修改 DOM，应该通过状态管理...
```

## 参数配置

所有参数支持 CLI 传入或环境变量注入。**优先级**：`CLI 参数 > 环境变量`

### 必填参数

- `--embed-url` / `EMBEDDING_URL` - Embedding API 地址
- `--embed-model` / `EMBEDDING_MODEL` - 向量模型 ID
- `--embed-dim` / `EMBEDDING_DIMENSION` - 向量维度

### 可选参数

- `--top-k` - 最大返回结果数（默认 20）
- `--threshold` - 最低相似度阈值 0-1（默认 0.5）
- `--max-fetch` - 每库最多读取记录数（默认 1000）
- `--kb-name` - 限定搜索指定名称的知识库
- `--kb-path` - 知识库根目录路径

详细说明见 `references/cli-params.md`

## 问题排查

遇到问题时先查阅 `references/troubleshooting.md`，常见问题包括：

1. **知识库找不到** - 检查路径是否正确
2. **搜索无结果** - 调整 threshold 或检查向量维度
3. **API 连接失败** - 确认 Embedding 服务是否运行
4. **参数错误** - 检查必填参数是否完整

## 项目信息

- **npm 包**: `cherry-mcp`
- **文档**: MCP 服务基于 `@modelcontextprotocol/sdk` 实现
- **配置参考**: `references/mcp-config.md`
