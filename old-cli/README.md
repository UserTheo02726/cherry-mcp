# Cherry Studio 知识库检索工具

本地 CLI 工具，用于从 Cherry Studio 知识库中搜索内容。

## 功能

- 列举并统计所有可用的知识库详情（大小、向量维度、数量等）
- 支持同时跨**多个知识库**进行全局联合向量相似度搜索并聚合评分
- 支持通过参数精确定位搜索**特定知识库**
- 支持自定义搜索参数（top_k、threshold、max_fetch）
- 自动适配跨平台默认配置目录（Windows / Mac / Linux）

## 依赖

- Python 3.10+
- `pydantic` (强类型配置管理)
- `httpx` (异步并发网络请求)
- `numpy` (向量运算)
- `python-dotenv` (环境变量加载)

## 安装

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate.bat
# 激活虚拟环境 (macOS/Linux)
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制配置
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# 编辑 .env 文件，填入你的配置
```

## 配置 (.env)

**重要**：嵌入模型配置必须与 Cherry Studio 中创建知识库时的设置完全一致，否则搜索将无法返回正确结果。

### 嵌入模型配置说明

| 参数 | 说明 | 注意事项 |
|------|------|----------|
| `EMBEDDING_URL` | 嵌入模型 API 地址 | 必须与 Cherry Studio 知识库设置中的 API 地址一致 |
| `EMBEDDING_API_KEY` | 嵌入模型 API 密钥 | 必须与 Cherry Studio 中使用的密钥一致 |
| `EMBEDDING_MODEL` | 嵌入模型名称 | **必须与知识库创建时使用的模型一致** |
| `EMBEDDING_DIMENSION` | 向量维度 | **必须与知识库的向量维度一致，否则会提示维度不匹配或找不到结果** |

### 配置示例

```env
# 可选：手动指定 Cherry Studio 知识库路径（如不指定则根据系统自动找寻默认路径）
# CHERRYSTUDIO_KB_PATH=C:/Users/YourUser/AppData/Roaming/CherryStudio/Data/KnowledgeBase

# 嵌入模型配置（必须与 Cherry Studio 知识库设置一致）
EMBEDDING_URL=https://api.siliconflow.cn/v1/embeddings
EMBEDDING_API_KEY=sk-your-api-key
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024

# 搜索参数（可选）
DEFAULT_TOP_K=20
DEFAULT_THRESHOLD=0.5
MAX_FETCH=1000
```

### 向量维度问题排查

如果搜索返回 0 条结果，很可能是向量维度不匹配，请通过 `python main.py list` 命令查看当前各个知识库储存的**实际维度**。

**常见向量维度参考**：
- `text-embedding-qwen3-embedding-8b`: 4096
- `BAAI/bge-m3`: 1024
- `BAAI/bge-large-zh-v1.5`: 1024

## 使用方法

在使用之前，请确保已经激活虚拟环境。

```bash
# 查看帮助
python main.py --help

# 列出所有知识库及其详情（路径、维度、向量数量）
python main.py list

# 全局搜索所有知识库（合并结果），使用默认配置参数
python main.py search "跨平台支持"

# 仅在特定的知识库内进行搜索（由 list 命令显示的知识库文件夹名）
python main.py search "安装步骤" --kb-name "mW3rzDuJfCoDSKMi0nE5J"

# 自定义返回数量及最低相似度阈值
python main.py search "内存错误" --top-k 5 --threshold 0.65
```

## 命令行参数 (Search)

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | (必填) 搜索的关键词字符串 | 无 |
| `--top-k` | 期望返回的最高相似度结果数量 | 读取自 `.env` (`DEFAULT_TOP_K`) |
| `--threshold` | 相似度过滤的最低阈值 (0-1) | 读取自 `.env` (`DEFAULT_THRESHOLD`) |
| `--max-fetch` | 从单个数据库预获取的最多文档数 | 读取自 `.env` (`MAX_FETCH`) |
| `--kb-name` | 指定具体的知识库进行检索 | (全部可用库合并搜索) |

## 项目结构

```
cherry-mcp/
├── main.py                 # CLI 入口
├── .env                    # 环境变量配置文件
├── requirements.txt        # Python 依赖
├── venv/                   # Python 虚拟环境 (被忽略)
│
└── cherrymcp/
    └── knowledge/
         ├── config.py          # 基于 Pydantic 的配置映射与加载
         ├── embedding.py       # Async 文本嵌入 API 请求客户端
         ├── knowledge_base.py  # SQLite 多知识库迭代与综合控制层
         └── vector_search.py   # 搜索核心、并库策略及降级调度
```

## TODO 计划

- [ ] 封装为 MCP 工具标准服务，可由支持外接 MCP Server 的各类工具（如 Claude Desktop, Cursor 等）远程调用
- [ ] 支持 SSE 模式运行，提供 HTTP API 接口
- [ ] 丰富边界单元测试及 CI 构建支持