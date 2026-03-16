---
title: AGENTS.md
description: Agentic coding guidelines for cherry-mcp
---

# AGENTS.md - cherry-mcp 开发指南

本文档为在此仓库中工作的 Agentic Coding 代理提供开发规范与工作流程指引。

## 1. 项目概述

| 项目 | 说明 |
|:-----|:-----|
| 名称 | cherry-mcp |
| 类型 | Node.js ESM 包 (MCP Server) |
| 入口 | `src/index.js` |
| Node | >= 20.0.0 |
| 依赖 | `@modelcontextprotocol/sdk`, `sql.js` |

## 2. 构建与测试命令

```bash
# 安装依赖
npm install

# 运行 MCP 服务（需提供必填参数）
node src/index.js --embed-model "text-embedding-qwen3-embedding-8b" --embed-dim 4096

# 功能验证
node test.js

# 预览发布内容
npm pack --dry-run

# 本地发布（需先 npm login）
npm publish
```

## 3. 代码风格规范

### 3.1 模块系统
- **必须使用 ESM** (`"type": "module"`)
- Node.js 内置模块使用 `node:` 前缀

### 3.2 命名约定
- 变量/函数: camelCase
- 常量: UPPER_SNAKE_CASE
- 文件名: camelCase.js

### 3.3 注释规范
- 文件头注释: 说明模块功能、目的
- 函数注释: JSDoc 格式，包含 `@param` 和 `@returns`
- 业务逻辑注释: 中文，说明"为什么"

### 3.4 错误处理
- 使用 `try/catch` 捕获异步错误
- 错误消息使用中文
- **MCP 日志必须写入 stderr**，避免污染 stdout

### 3.5 格式
- 2 空格缩进
- 语句结尾不加分号
- 导入分组: 外部依赖 → Node.js 内置 → 本地模块

## 4. MCP 工具开发

### 4.1 工具注册
在 `src/index.js` 中使用 `ListToolsRequestSchema`：

```javascript
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'tool_name',
    description: '工具描述（中文）',
    inputSchema: {
      type: 'object',
      properties: { ... },
      required: ['param'],
    },
  }],
}));
```

### 4.2 工具执行
```javascript
return {
  content: [{ type: 'text', text: '返回内容' }],
  // 或错误：
  isError: true,
  content: [{ type: 'text', text: '错误信息' }],
};
```

## 5. 配置管理

### 5.1 必填参数
以下参数为**必填**，必须通过 CLI 或环境变量提供：
- `--embed-model`: 向量模型 ID
- `--embed-dim`: 向量维度

### 5.2 优先级
```
CLI 参数 > 环境变量
```

## 6. 数据库操作

- 使用 `sql.js` 加载 SQLite（无原生依赖）
- CommonJS 模块使用 `createRequire` 加载
- 向量数据使用 `Float32Array`

## 7. 向量相似度

- Cherry Studio 使用余弦相似度
- 公式: `dot(a,b) / (||a|| * ||b||)`

## 8. 注意事项

1. **不要污染 stdout**: MCP 协议通过 stdio 通信
2. **不要硬编码路径**: 使用 `config.kbPath`
3. **不要使用 console.log**: 使用 `process.stderr.write()`

## 9. GitHub Actions 自动发布

### 9.1 工作流
`.github/workflows/publish.yml` 会自动比对版本发布：
- 读取 `package.json` 当前版本
- 调用 `npm view . version` 获取已发布版本
- 仅当版本不一致时执行发布

### 9.2 发布流程
```bash
# 1. 修改版本号
npm version patch  # 或手动修改 package.json

# 2. 同步更新 package-lock.json（重要！）
npm install

# 3. 一起提交并推送
git add package.json package-lock.json
git commit -m "release: v1.x.x"
git push
```

> ⚠️ **必须同时提交 package-lock.json**，否则用户通过 `npx cherry-mcp@latest` 安装时可能获取到旧版本的依赖锁定文件。

## 10. 常用命令速查

| 命令 | 说明 |
|:-----|:-----|
| `node src/index.js` | 启动 MCP 服务 |
| `node test.js` | 本地功能验证 |
| `npm pack --dry-run` | 预览发布内容 |
| `npx cherry-mcp@latest` | 一键调用 |
