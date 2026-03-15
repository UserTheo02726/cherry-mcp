---
title: AGENTS.md
description: Agentic coding guidelines for cherry-mcp
---

# AGENTS.md - cherry-mcp 开发指南

本文档为在此仓库中工作的 Agentic Coding 代理提供开发规范与工作流程指引。

## 1. 项目概述

- **项目名称**: cherry-mcp
- **类型**: Node.js ESM 包 (MCP Server)
- **入口文件**: `src/index.js`
- **Node 版本**: >= 18.0.0
- **主要依赖**: `@modelcontextprotocol/sdk`, `sql.js`
- **作者**: Theo

## 2. 构建与测试命令

### 2.1 安装依赖

```bash
npm install
```

### 2.2 运行 MCP 服务（开发调试）

```bash
node src/index.js --top-k 5 --threshold 0.6
```

### 2.3 功能验证脚本（非单元测试）

项目未配置正式测试框架，使用 `test.js` 进行本地功能验证：

```bash
# 方式 1: 直接运行
node test.js

# 方式 2: 通过环境变量传入配置
EMBEDDING_API_KEY=sk-xxx node test.js
```

### 2.4 NPM 发布

```bash
npm login   # 首次需登录
npm publish
```

### 2.5 一键调用（无需本地安装）

```bash
npx cherry-mcp --top-k 10
```

## 3. 代码风格规范

### 3.1 模块系统

- **必须使用 ESM** (`"type": "module"` in package.json)
- 导入使用 `import` / `export`
- Node.js 内置模块使用 `node:` 前缀：
  ```javascript
  import { readFileSync } from 'node:fs';
  import { parseArgs } from 'node:util';
  ```

### 3.2 命名约定

- **变量/函数**: camelCase
- **常量**: UPPER_SNAKE_CASE
- **文件名**: camelCase.js (非 kebab-case)
- **JSDoc @param/@returns**: 使用 TypeScript 类型或 JSDoc 类型

### 3.3 注释规范

- **文件头注释**: 说明模块功能、目的、注意事项
- **函数注释**: JSDoc 格式，包含 `@param` 和 `@returns`
- **业务逻辑注释**: 中文，说明 "为什么" 而非 "做什么"
- **示例**:
  ```javascript
  /**
   * 将文本字符串转换为 Float32Array 特征向量
   * @param {string} text
   * @returns {Promise<Float32Array>}
   */
  export async function embedText(text) { ... }
  ```

### 3.4 错误处理

- 使用 `try/catch` 捕获异步错误
- 错误消息使用中文，格式：`模块名 错误描述`
- MCP 通道的日志**必须写入 stderr**，避免污染 stdout 上的 JSON-RPC 通信：
  ```javascript
  process.stderr.write(`[cherry-mcp] 错误: ${err.message}\n`);
  ```

### 3.5 日志规范

- 所有业务日志输出到 `process.stderr`
- 日志前缀使用 `[cherry-mcp]` 便于过滤
- 避免使用 `console.log`（测试脚本除外）

### 3.6 格式与结构

- 使用 2 空格缩进
- 语句结尾不加分号（除非需要避免歧义）
- 对象/数组多行写法：
  ```javascript
  const config = {
    topK:      parseInt(argv['top-k'] ?? process.env.DEFAULT_TOP_K ?? DEFAULTS.topK, 10),
    threshold: parseFloat(argv['threshold'] ?? process.env.DEFAULT_THRESHOLD ?? DEFAULTS.threshold),
  };
  ```
- 导入分组：外部依赖 → Node.js 内置 → 本地模块（中间空行分隔）

### 3.7 类型注解

- 使用 JSDoc 标注函数参数与返回值类型
- 常用类型: `string`, `number`, `boolean`, `object`, `Array<T>`, `Promise<T>`, `Float32Array`

## 4. MCP 工具开发规范

### 4.1 工具注册

在 `src/index.js` 中使用 `ListToolsRequestSchema` 注册工具：

```javascript
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'tool_name',
      description: '工具描述（中文）',
      inputSchema: {
        type: 'object',
        properties: { ... },
        required: ['param'],
      },
    },
  ],
}));
```

### 4.2 工具执行

使用 `CallToolRequestSchema` 处理工具调用，返回格式：

```javascript
return {
  content: [{ type: 'text', text: '返回内容' }],
  // 或错误：
  isError: true,
  content: [{ type: 'text', text: '错误信息' }],
};
```

### 4.3 参数校验

- 必填参数在 `inputSchema.required` 中声明
- 在工具处理函数中进行类型校验：
  ```javascript
  if (!query || typeof query !== 'string') {
    return { content: [{ type: 'text', text: '参数错误：query 为必填字符串。' }], isError: true };
  }
  ```

## 5. 配置管理

### 5.1 配置模块

所有配置集中在 `src/config.js`，优先级：

```
CLI 参数 > 环境变量 > 内置默认值
```

### 5.2 新增配置项

1. 在 `parseArgs` 的 `options` 中添加 CLI 参数
2. 在 `DEFAULTS` 对象中添加默认值
3. 在 `config` 对象中组合解析逻辑

## 6. 数据库操作

- 使用 `sql.js` 加载 SQLite（无原生依赖）
- CommonJS 模块使用 `createRequire` 加载：
  ```javascript
  const require = createRequire(import.meta.url);
  const initSqlJs = require('sql.js');
  ```
- 使用 `Float32Array` 处理向量数据
- 读取二进制向量时使用 `.slice().buffer` 确保 byteOffset=0

## 7. 向量相似度

- Cherry Studio 使用余弦相似度
- 在 `src/vector_math.js` 中实现
- 公式: `dot(a,b) / (||a|| * ||b||)`

## 8. 注意事项

1. **不要污染 stdout**: MCP 协议通过 stdio 通信，日志必须走 stderr
2. **不要硬编码路径**: 使用 `config.kbPath` 而非写死路径
3. **不要在业务代码中使用 console.log**: 调试除外
4. **WASM 初始化开销**: `sql.js` 初始化较重，需懒加载缓存

## 9. GitHub Actions 自动发布

### 9.1 工作流配置

项目配置了 `.github/workflows/publish.yml`，支持 main/master 分支自动发布：

```yaml
on:
  push:
    branches: [main, master]
```

### 9.2 发布前验证

发布前可本地验证打包内容：

```bash
# 预览会打包的文件（不实际发布）
npm pack --dry-run
```

## 10. 常用命令速查

| 命令 | 说明 |
|:-----|:-----|
| `node src/index.js` | 启动 MCP 服务 |
| `node test.js` | 本地功能验证 |
| `npm pack --dry-run` | 预览发布内容 |
| `npm publish` | 发布到 NPM（本地） |
| `npx cherry-mcp` | 一键调用（远程） |
