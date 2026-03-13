"""
cherry-mcp 入口文件

通过 stdio 方式连接 AI IDE，直接读取知识库实现检索
"""
import asyncio

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from config import get_config
from cherrymcp.tools.knowledge_tools import KnowledgeTools


async def main():
    """主入口函数"""
    config = get_config()
    knowledge_tools = KnowledgeTools()
    
    server = Server("cherry-mcp")
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """列出所有可用工具"""
        return [
            Tool(
                name="list_knowledge_bases",
                description="列出所有可用的知识库",
                description_for_model="当用户想要查看有哪些知识库可供搜索时调用此工具",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="search_knowledge",
                description="在知识库中搜索相关内容",
                description_for_model="当用户想要从知识库中获取特定信息时调用此工具。使用向量相似度搜索，返回最相关的结果。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词或问题"
                        },
                        "kb_name": {
                            "type": "string",
                            "description": "知识库名称（可选，不填则搜索所有）"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "返回结果数量",
                            "default": 20
                        },
                        "threshold": {
                            "type": "number",
                            "description": "相似度阈值（0-1）",
                            "default": 0.5
                        }
                    },
                    "required": ["query"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict | None) -> list[TextContent]:
        """调用工具"""
        try:
            if name == "list_knowledge_bases":
                result = await knowledge_tools.list_knowledge_bases()
                return [TextContent(type="text", text=result)]
            
            elif name == "search_knowledge":
                query = arguments.get("query")
                kb_name = arguments.get("kb_name")
                top_k = arguments.get("top_k")
                threshold = arguments.get("threshold")
                
                result = await knowledge_tools.search_knowledge(
                    query=query,
                    kb_name=kb_name,
                    top_k=top_k,
                    threshold=threshold
                )
                return [TextContent(type="text", text=result)]
            
            else:
                return [TextContent(type="text", text=f"未知工具: {name}")]
        
        except Exception as e:
            return [TextContent(type="text", text=f"错误: {str(e)}")]
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
