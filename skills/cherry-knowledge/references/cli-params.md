# CLI 参数详解

本文档详细说明 cherry-mcp 的所有 CLI 参数。

## 参数优先级

```
CLI 参数 > 环境变量 > 内置默认值
```

## 必填参数

### --embed-url

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 环境变量 | `EMBEDDING_URL` |
| 说明 | Embedding API 地址，OpenAI 兼容格式 |
| 示例 | `http://127.0.0.1:1234` 或 `https://api.siliconflow.cn/v1/embeddings` |
| 自动补全 | 如果未以 `/v1/embeddings` 结尾，会自动追加 |

### --embed-model

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 环境变量 | `EMBEDDING_MODEL` |
| 说明 | 向量模型 ID，必须与实际使用的模型匹配 |
| 示例 | `text-embedding-qwen3-embedding-8b`、`bge-large-zh-v1.5`、`text-embedding-3-small` |

### --embed-dim

| 属性 | 值 |
|------|-----|
| 类型 | positive integer |
| 环境变量 | `EMBEDDING_DIMENSION` |
| 说明 | 向量维度，必须与模型实际输出维度一致 |
| 示例 | `4096`、`1024`、`1536` |

> **重要**：如果维度不匹配，搜索结果将不准确或完全无结果。

---

## 可选参数

### --top-k

| 属性 | 值 |
|------|-----|
| 类型 | positive integer |
| 环境变量 | `DEFAULT_TOP_K` |
| 默认值 | `20` |
| 说明 | 最多返回结果数 |
| 建议 | 根据知识库向量总数调整，向量多时可适当增大 |

### --threshold

| 属性 | 值 |
|------|-----|
| 类型 | float (0-1) |
| 环境变量 | `DEFAULT_THRESHOLD` |
| 默认值 | `0.5` |
| 说明 | 相似度最低阈值，低于此值的结果将被过滤 |
| 示例 | `0.6` 表示只返回相似度 >= 60% 的结果 |

### --max-fetch

| 属性 | 值 |
|------|-----|
| 类型 | positive integer |
| 环境变量 | `MAX_FETCH` |
| 默认值 | `1000` |
| 说明 | 每个知识库最多读取的向量记录数 |
| 建议 | 大型知识库可适当增大，但会增加内存占用和查询时间 |

### --kb-name

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 环境变量 | `DEFAULT_KB_NAME` |
| 默认值 | `null`（搜索全部） |
| 说明 | 限定搜索范围到指定名称的知识库 |
| 示例 | `--kb-name "技术文档"` |

### --kb-path

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 环境变量 | `CHERRYSTUDIO_KB_PATH` |
| 默认值 | 自动识别（见下方） |
| 说明 | 知识库根目录路径 |

**自动识别默认值**：

| 操作系统 | 默认路径 |
|----------|----------|
| Windows | `C:\Users\{用户名}\AppData\Roaming\CherryStudio\Data\KnowledgeBase` |
| macOS | `~/Library/Application Support/CherryStudio/Data/KnowledgeBase` |
| Linux | `~/.config/CherryStudio/Data/KnowledgeBase` |

### --embed-api-key

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 环境变量 | `EMBEDDING_API_KEY` |
| 默认值 | 空 |
| 说明 | API 认证 Token，本地模型可省略 |
| 示例 | `sk-xxxxx` |

---

## 使用示例

### 完整参数

```bash
node src/index.js \
  --embed-url "http://127.0.0.1:1234" \
  --embed-model "text-embedding-qwen3-embedding-8b" \
  --embed-dim 4096 \
  --top-k 10 \
  --threshold 0.6 \
  --max-fetch 500 \
  --kb-path "C:\Users\Theo\AppData\Roaming\CherryStudio\Data\KnowledgeBase"
```

### 使用环境变量

```bash
export EMBEDDING_URL="http://127.0.0.1:1234"
export EMBEDDING_MODEL="text-embedding-qwen3-embedding-8b"
export EMBEDDING_DIMENSION=4096

node src/index.js
```

### 指定知识库

```bash
node src/index.js \
  --embed-url "http://127.0.0.1:1234" \
  --embed-model "text-embedding-qwen3-embedding-8b" \
  --embed-dim 4096 \
  --kb-name "技术文档"
```

---

## 常见参数组合

| 场景 | 推荐参数 |
|------|----------|
| 小型知识库（<1000向量） | `--top-k 20 --threshold 0.5` |
| 大型知识库（>10000向量） | `--top-k 50 --threshold 0.7 --max-fetch 2000` |
| 精确搜索 | `--top-k 5 --threshold 0.8` |
| 广泛探索 | `--top-k 50 --threshold 0.3` |

---

## 错误处理

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `embed-url 为必填参数` | 未提供 --embed-url | 添加 --embed-url 参数 |
| `embed-model 为必填参数` | 未提供 --embed-model | 添加 --embed-model 参数 |
| `embed-dim 必须为正整数` | 维度值无效 | 检查 --embed-dim 值是否为正整数 |
| `API 错误 (401)` | API Key 错误或过期 | 检查 --embed-api-key |
| `API 错误 (404)` | 模型不存在 | 检查 --embed-model 是否正确 |
