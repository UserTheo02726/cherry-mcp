/**
 * Embedding 客户端 - 调用 OpenAI 兼容格式的向量 API
 *
 * 使用 Node 18+ 原生 fetch，无额外依赖。
 * 向量以 Float32Array 格式返回，保证与 Cherry Studio 落盘数据的二进制兼容。
 *
 * Author: Theo
 */
import config from './config.js';

/**
 * 将文本字符串转换为 Float32Array 特征向量
 * @param {string} text
 * @returns {Promise<Float32Array>}
 */
export async function embedText(text) {
  const headers = { 'Content-Type': 'application/json' };
  if (config.embedApiKey) {
    headers['Authorization'] = `Bearer ${config.embedApiKey}`;
  }

  const response = await fetch(config.embedUrl, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model: config.embedModel,
      input: text,
    }),
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Embedding API 错误 (${response.status}): ${errText}`);
  }

  const data = await response.json();
  const embedding = data?.data?.[0]?.embedding;

  if (!Array.isArray(embedding)) {
    throw new Error(`API 响应格式异常，未找到 data[0].embedding 字段: ${JSON.stringify(data)}`);
  }

  return new Float32Array(embedding);
}
