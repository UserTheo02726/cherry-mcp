# Cherry Studio 知识库检索工具

本地 CLI 工具，用于从 Cherry Studio 知识库中搜索内容。

## 功能

- 列出所有知识库
- 向量相似度搜索
- 支持自定义搜索参数（top_k、threshold）

## 当前限制

- 搜索当前只支持**单个知识库**（自动选择第一个数据库文件）
- `--kb-name` 参数暂未实现多知识库选择

## 安装

```bash
# 创建虚拟环境
python -m venv venv

# 安装依赖
venv\Scripts\pip.exe install -r requirements.txt

# 复制配置
copy .env.example .env

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
| `EMBEDDING_DIMENSION` | 向量维度 | **必须与知识库的向量维度一致，否则搜索无结果** |

### 如何获取配置

1. 打开 Cherry Studio
2. 进入「知识库」设置
3. 查看嵌入模型配置
4. 将对应参数填入 `.env`

```env
# Cherry Studio 知识库路径
CHERRYSTUDIO_KB_PATH=C:/Users/Theo/AppData/Roaming/CherryStudio/Data/KnowledgeBase

# 嵌入模型配置（必须与 Cherry Studio 知识库设置一致）
EMBEDDING_URL=https://api.siliconflow.cn
EMBEDDING_API_KEY=sk-your-api-key
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024

# 搜索参数（可选）
DEFAULT_TOP_K=20
DEFAULT_THRESHOLD=0.5
MAX_FETCH=1000
```

### 向量维度不匹配问题

如果搜索返回 0 条结果，很可能是向量维度不匹配：

- 知识库向量维度：查看 Cherry Studio 知识库数据库中的向量维度
- 配置中的维度：必须与上述维度完全一致

**常见向量维度**：
- `text-embedding-qwen3-embedding-8b`: 4096
- `BAAI/bge-m3`: 1024
- `BAAI/bge-large-zh-v1.5`: 1024

## 使用方法

```bash
# 激活虚拟环境
venv\Scripts\activate.bat

# 列出知识库
python main.py list

# 搜索知识库（使用默认参数）
python main.py search "关键词"

# 搜索知识库（自定义参数）
python main.py search "关键词" --top-k 5 --threshold 0.6

# Windows 中文输出
set PYTHONIOENCODING=utf-8
python main.py search "关键词"
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--top-k` | 返回结果数量 | 20 |
| `--threshold` | 相似度阈值 (0-1) | 0.5 |
| `--kb-name` | 指定知识库名称 | 全部 |

## 项目结构

```
cherry-mcp/
├── main.py                 # CLI 入口
├── .env                   # 配置文件
├── requirements.txt        # 依赖
├── venv/                  # 虚拟环境
│
└── cherrymcp/
    └── knowledge/
        ├── config.py       # 配置读取
        ├── embedding.py    # 文本向量化
        ├── knowledge_base.py  # 知识库管理
        └── vector_search.py   # 向量搜索
```

## 依赖

- Python 3.10+
- httpx
- numpy
- python-dotenv

## TODO 计划

- [ ] 支持多知识库搜索（通过 `--kb-name` 选择知识库）
- [ ] 封装为 MCP 工具，可被 AI IDE（如 Cursor、OpenCode）调用
- [ ] 支持 SSE 模式运行，提供 HTTP API 接口
- [ ] 编写单元测试