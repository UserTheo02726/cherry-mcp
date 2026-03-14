"""
Cherry Studio 知识库检索工具

本地 CLI 工具，用于从 Cherry Studio 知识库中搜索内容。

用法:
    python main.py search "关键词"          # 搜索所有知识库
    python main.py list                      # 列出所有知识库
    python main.py search "关键词" --kb-name "my-kb"  # 搜索指定知识库
    python main.py search "关键词" --top-k 5  # 指定返回数量
    python main.py search "关键词" --threshold 0.6  # 指定相似度阈值
"""
import argparse
import asyncio
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# 配置基础日志格式
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(levelname)s: %(message)s"
)

from cherrymcp.knowledge import KnowledgeBaseManager, VectorSearcher


def list_knowledge_bases() -> str:
    """列出所有知识库"""
    try:
        kb_manager = KnowledgeBaseManager()
        kbs = kb_manager.list_knowledge_bases()
        
        if not kbs:
            return "未找到知识库，请确保 Cherry Studio 已在配置目录下创建知识库。"
        
        result = "可用知识库列表:\n\n"
        for kb in kbs:
            size_mb = kb["size"] / (1024 * 1024)
            result += f"- {kb['name']}\n"
            result += f"  路径: {kb['path']}\n"
            result += f"  大小: {size_mb:.2f} MB\n"
            if kb['dimension'] > 0:
                result += f"  向量维度: {kb['dimension']}d\n"
            else:
                result += "  向量维度: 未知\n"
            result += f"  向量数量: {kb['vector_count']} 条\n\n"
        
        return result
    except Exception as e:
        logging.error(f"获取知识库列表失败: {e}")
        sys.exit(1)


async def search_knowledge(
    query: str,
    top_k: int | None = None,
    threshold: float | None = None,
    kb_name: str | None = None,
    max_fetch: int | None = None
) -> str:
    """搜索知识库"""
    async with VectorSearcher() as searcher:
        try:
            results = await searcher.search(
                query=query,
                top_k=top_k,
                threshold=threshold,
                kb_name=kb_name,
                max_fetch=max_fetch
            )
            
            if not results:
                target = f"知识库「{kb_name}」" if kb_name else "所有知识库"
                return f"在{target}中未找到与「{query}」相关的高相似度内容。"
            
            output = f"搜索「{query}」找到 {len(results)} 条结果:\n\n"
            
            for i, r in enumerate(results, 1):
                score = r["score"]
                source = r.get("source", "未知来源")
                content = r.get("content", "")
                
                output += f"--- 结果 {i} (相似度: {score:.2%}) ---\n"
                output += f"来源: {source}\n"
                output += f"内容: {content}\n\n"
            
            return output
            
        except Exception as e:
            logging.error(f"搜索过程出现异常: {e}")
            sys.exit(1)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="Cherry Studio 知识库检索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py list
  python main.py search "什么是 AI"
  python main.py search "如何安装" --top-k 5
  python main.py search "配置" --threshold 0.7
  python main.py search "常见问题" --kb-name "my-knowledge-base"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有知识库")
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索知识库")
    search_parser.add_argument("query", type=str, help="搜索关键词")
    search_parser.add_argument("--top-k", type=int, help="返回结果数量")
    search_parser.add_argument("--threshold", type=float, help="相似度阈值 (0-1)")
    search_parser.add_argument("--kb-name", type=str, help="指定知识库名称（不指定则检索全部）")
    search_parser.add_argument("--max-fetch", type=int, help="从数据库最多获取的文档数")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list":
        result = list_knowledge_bases()
        print(result)
    
    elif args.command == "search":
        result = asyncio.run(search_knowledge(
            query=args.query,
            top_k=args.top_k,
            threshold=args.threshold,
            kb_name=args.kb_name,
            max_fetch=args.max_fetch
        ))
        print(result)


if __name__ == "__main__":
    # 配置 httpx 的日志等级，避免 debug 信息干扰
    logging.getLogger("httpx").setLevel(logging.WARNING)
    main()
