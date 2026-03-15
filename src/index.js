#!/usr/bin/env node
/**
 * MCP 服务入口 - Cherry Studio 知识库搜索
 *
 * 通过 @modelcontextprotocol/sdk 暴露两个 MCP Tool：
 *   - list_knowledge_bases：列出当前知识库目录下所有有效库
 *   - search_knowledge：向量相似度检索
 *
 * 所有参数均从 config.js 读取（优先级：CLI > ENV > 默认值）。
 * 所有 log 必须写入 stderr，避免污染 stdout 上的 JSON-RPC 通信。
 *
 * Author: Theo
 */
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import config from './config.js';
import { embedText } from './embedding.js';
import { listKnowledgeBases, searchVectors } from './database.js';

// 打印当前生效配置，方便排查参数是否正确注入（输出到 stderr 不污染 MCP 通道）
process.stderr.write(`[cherry-mcp] 启动配置:\n`);
process.stderr.write(`  知识库路径: ${config.kbPath}\n`);
process.stderr.write(`  Embedding API: ${config.embedUrl}\n`);
process.stderr.write(`  模型: ${config.embedModel} (维度: ${config.embedDim})\n`);
process.stderr.write(`  Top-K: ${config.topK}, 阈值: ${config.threshold}, MaxFetch: ${config.maxFetch}\n`);
if (config.kbName) process.stderr.write(`  固定知识库: ${config.kbName}\n`);

const server = new Server(
  { name: 'cherry-mcp', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

// ───────────────────────────────────────── 工具清单 ─────────────────────────
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'list_knowledge_bases',
      description: '列出 Cherry Studio 知识库目录下所有可用知识库及其统计信息（向量数量、维度、文件大小等）。',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    },
    {
      name: 'search_knowledge',
      description: '在 Cherry Studio 知识库中通过自然语言进行向量相似度搜索，返回最相关的文档片段。',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: '搜索关键词或问题，将被转化为向量进行相似度匹配。',
          },
          top_k: {
            type: 'number',
            description: `最多返回结果数（默认 ${config.topK}）。`,
          },
          threshold: {
            type: 'number',
            description: `相似度最低阈值，范围 0–1（默认 ${config.threshold}）。`,
          },
          kb_name: {
            type: 'string',
            description: '限定搜索范围到指定名称的知识库（不填则搜索全部）。',
          },
        },
        required: ['query'],
      },
    },
  ],
}));

// ───────────────────────────────────────── 工具执行 ─────────────────────────
server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params;

  try {
    if (name === 'list_knowledge_bases') {
      const kbs = await listKnowledgeBases();
      if (!kbs.length) {
        return {
          content: [{ type: 'text', text: `未找到知识库。请确认路径：${config.kbPath}` }],
        };
      }
      const lines = kbs.map(kb =>
        `**${kb.name}**\n  路径: ${kb.path}\n  大小: ${kb.sizeMb} MB | 向量数: ${kb.vectorCount} | 维度: ${kb.dimension}`
      );
      return {
        content: [{ type: 'text', text: `发现 ${kbs.length} 个知识库：\n\n${lines.join('\n\n')}` }],
      };
    }

    if (name === 'search_knowledge') {
      const { query, top_k, threshold, kb_name } = args ?? {};

      if (!query || typeof query !== 'string') {
        return { content: [{ type: 'text', text: '参数错误：query 为必填字符串。' }], isError: true };
      }

      process.stderr.write(`[cherry-mcp] 搜索: "${query}"\n`);

      const queryVector = await embedText(query);
      const results = await searchVectors(queryVector, {
        topK: top_k ?? config.topK,
        threshold: threshold ?? config.threshold,
        kbName: kb_name ?? config.kbName,
      });

      if (!results.length) {
        return { content: [{ type: 'text', text: `「${query}」未匹配到任何高相似度内容。` }] };
      }

      const formatted = results.map((r, i) =>
        `--- 结果 ${i + 1}（相似度: ${(r.score * 100).toFixed(1)}%）---\n来源: ${r.source}\n${r.content}`
      ).join('\n\n');

      return {
        content: [{ type: 'text', text: `搜索「${query}」，共 ${results.length} 条结果：\n\n${formatted}` }],
      };
    }

    return { content: [{ type: 'text', text: `未知工具: ${name}` }], isError: true };

  } catch (err) {
    process.stderr.write(`[cherry-mcp] 错误: ${err.message}\n`);
    return { content: [{ type: 'text', text: `执行出错：${err.message}` }], isError: true };
  }
});

// ───────────────────────────────────────── 启动 ──────────────────────────────
const transport = new StdioServerTransport();
await server.connect(transport);
process.stderr.write(`[cherry-mcp] MCP 服务已启动，等待客户端连接...\n`);
