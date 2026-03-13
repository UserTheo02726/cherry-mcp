"""
Cherry Studio 知识库检索工具

本地 CLI 工具，用于从 Cherry Studio 知识库中搜索内容。

用法:
    python main.py search "关键词"          # 搜索知识库
    python main.py list                      # 列出所有知识库
    python main.py search "关键词" --top-k 5  # 指定返回数量
    python main.py search "关键词" --threshold 0.6  # 指定相似度阈值
"""
import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from cherrymcp.knowledge import get_kb_config, KnowledgeBaseManager, EmbeddingClient, VectorSearcher


def list_knowledge_bases() -> str:
    """列出所有知识库"""
    from cherrymcp.knowledge import KnowledgeBaseManager
    config = get_kb_config()
    kb_manager = KnowledgeBaseManager(config)
    kbs = kb_manager.list_knowledge_bases()
    
    if not kbs:
        return "未找到知识库，请确保 Cherry Studio 已创建知识库。"
    
    result = "可用知识库列表:\n\n"
    for kb in kbs:
        size_mb = kb["size"] / (1024 * 1024)
        result += f"- {kb['name']}\n"
        result += f"  大小: {size_mb:.2f} MB\n\n"
    
    return result


async def search_knowledge(
    query: str,
    top_k: int | None = None,
    threshold: float | None = None,
    kb_name: str | None = None
) -> str:
    """搜索知识库"""
    config = get_kb_config()
    
    # 使用传入的参数或从配置读取默认值
    actual_top_k = top_k if top_k is not None else config.search.default_top_k
    actual_threshold = threshold if threshold is not None else config.search.default_threshold
    
    kb_manager = KnowledgeBaseManager(config)
    embedding_client = EmbeddingClient(config)
    searcher = VectorSearcher(kb_manager, embedding_client)
    
    try:
        results = await searcher.search(
            query=query,
            top_k=actual_top_k,
            threshold=actual_threshold,
            kb_name=kb_name
        )
        
        if not results:
            return f"未找到与「{query}」相关的内容。"
        
        output = f"搜索「{query}」找到 {len(results)} 条结果 (top_k={actual_top_k}, threshold={actual_threshold}):\n\n"
        
        for i, r in enumerate(results, 1):
            score = r["score"]
            source = r["source"]
            content = r["content"]
            
            output += f"--- 结果 {i} (相似度: {score:.2%}) ---\n"
            output += f"来源: {source}\n"
            output += f"内容: {content}\n\n"
        
        return output
    finally:
        await searcher.close()


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
    search_parser.add_argument("--kb-name", type=str, help="指定知识库名称")
    
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
            kb_name=args.kb_name
        ))
        print(result)


if __name__ == "__main__":
    main()
