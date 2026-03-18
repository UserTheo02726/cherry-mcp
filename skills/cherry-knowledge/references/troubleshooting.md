# 常见问题排查

本文档列出使用 cherry-mcp 时可能遇到的常见问题及解决方法。

---

## 问题 1：知识库找不到

### 症状

调用 `list_knowledge_bases` 返回"未找到知识库"。

### 可能原因

1. **路径错误** - 知识库目录路径不正确
2. **Cherry Studio 未创建知识库** - 还没有在 Cherry Studio 中添加任何知识库
3. **数据库文件损坏** - SQLite 文件损坏

### 解决方法

1. **检查路径**：
   ```bash
   # 确认知识库目录存在
   ls "C:\Users\你的用户名\AppData\Roaming\CherryStudio\Data\KnowledgeBase"
   ```

2. **手动指定路径**：
   ```bash
   --kb-path "你的知识库实际路径"
   ```

3. **在 Cherry Studio 中创建知识库**：
   - 打开 Cherry Studio
   - 点击"知识库"→"添加知识库"
   - 添加文档或文件夹

---

## 问题 2：搜索无结果

### 症状

`search_knowledge` 返回"未匹配到任何高相似度内容"。

### 可能原因

1. **向量维度不匹配** - `--embed-dim` 与实际模型输出不一致
2. **阈值过高** - `--threshold` 设置太高
3. **查询内容不在知识库中** - 知识库确实没有相关内容
4. **Embedding 服务未运行** - LM Studio 或其他 embedding 服务未启动

### 解决方法

1. **确认向量维度**：
   - 查看 `list_knowledge_bases` 返回的维度信息
   - 确认 `--embed-dim` 参数与之一致

2. **降低阈值测试**：
   ```bash
   --threshold 0.3
   ```

3. **检查 Embedding 服务**：
   ```bash
   # 确认 LM Studio 已启动并加载了 embedding 模型
   # 或确认远程 API 可访问
   curl http://127.0.0.1:1234/v1/embeddings \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"model": "你的模型", "input": "test"}'
   ```

4. **先列出知识库确认有数据**：
   ```
   调用 list_knowledge_bases 确认知识库有向量数据
   ```

---

## 问题 3：API 连接失败

### 症状

报错 "Embedding API 错误" 或 "connect ECONNREFUSED"。

### 可能原因

1. **Embedding 服务未启动** - LM Studio 或 API 服务未运行
2. **端口错误** - 端口号不正确
3. **防火墙拦截** - 防火墙阻止了连接

### 解决方法

1. **确认 LM Studio 启动**：
   - 打开 LM Studio
   - 确认已加载 embedding 模型
   - 确认 Server 按钮已点击（变为 "Stop Server"）

2. **检查端口**：
   ```bash
   # 确认 LM Studio 显示的端口
   # 通常是 http://localhost:1234
   ```

3. **测试 API 连接**：
   ```bash
   curl http://127.0.0.1:1234/v1/models
   ```

4. **使用正确的 URL**：
   ```bash
   # 正确
   --embed-url http://127.0.0.1:1234
   
   # 错误（缺少 http://）
   --embed-url localhost:1234
   ```

---

## 问题 4：参数错误

### 症状

报错 "xxx 为必填参数" 或 "参数解析错误"。

### 可能原因

1. **必填参数缺失** - 未提供 embed-url、embed-model 或 embed-dim
2. **参数格式错误** - 数值类型使用了非数字
3. **客户端配置格式错误** - JSON 格式错误

### 解决方法

1. **提供所有必填参数**：
   ```bash
   --embed-url "http://127.0.0.1:1234" \
   --embed-model "text-embedding-qwen3-embedding-8b" \
   --embed-dim 4096
   ```

2. **验证 JSON 配置**：
   - 使用 JSON 验证器检查配置文件格式
   - 注意逗号、引号等语法

3. **参数值类型正确**：
   ```bash
   # 正确
   --embed-dim 4096
   
   # 错误
   --embed-dim "4096"  # 字符串
   ```

---

## 问题 5：搜索结果不准确

### 症状

返回的结果与查询不相关，或者相关的结果排在后面。

### 可能原因

1. **向量维度不匹配** - 维度不一致导致向量计算错误
2. **阈值过低** - 返回了太多不相关结果
3. **模型不匹配** - 索引和查询使用了不同的 embedding 模型

### 解决方法

1. **确认维度匹配**：
   - 知识库创建时使用的维度
   - 查询时指定的维度
   - 两者必须完全一致

2. **使用相同的模型**：
   - 知识库用什么模型创建的
   - 查询就必须用什么模型

3. **调整阈值**：
   ```bash
   --threshold 0.7  # 提高相关性要求
   ```

---

## 问题 6：MCP 服务启动后无响应

### 症状

服务启动成功但客户端无法连接。

### 可能原因

1. **客户端配置错误** - MCP 客户端配置不正确
2. **版本不兼容** - cherry-mcp 版本与客户端不兼容

### 解决方法

1. **检查客户端配置**：
   - 参考 `mcp-config.md` 确认配置正确
   - 注意 JSON 格式

2. **重新安装**：
   ```bash
   npx -y cherry-mcp@latest ...
   ```

3. **查看日志**：
   - MCP 服务会输出日志到 stderr
   - 检查错误信息

---

## 问题 7：大型知识库查询慢

### 症状

查询响应时间过长。

### 可能原因

1. **数据量大** - 知识库有大量向量
2. **max-fetch 过大** - 读取了太多记录
3. **内存不足** - sql.js 需要将整个数据库加载到内存

### 解决方法

1. **减少 max-fetch**：
   ```bash
   --max-fetch 500
   ```

2. **限制搜索范围**：
   ```bash
   --kb-name "指定知识库名"
   ```

3. **使用 SSD** - 将知识库放在 SSD 上提升 IO 性能

---

## 获取帮助

如果以上方法都无法解决问题：

1. 检查 GitHub Issues
2. 确认 Node.js 版本 >= 20
3. 确认 @modelcontextprotocol/sdk 版本
4. 查看 MCP 服务日志获取详细错误信息
