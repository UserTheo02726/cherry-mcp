/**
 * 向量数学工具 - 余弦相似度计算
 *
 * Cherry Studio 使用余弦相似度为向量匹配打分，这里纯用 JS 复现。
 * 两个 Float32Array 的点积除以各自模长的乘积。
 *
 * Author: Theo
 */

/**
 * 计算两个 Float32Array 向量间的余弦相似度
 * @param {Float32Array} a
 * @param {Float32Array} b
 * @returns {number} 相似度分数，范围 [0, 1]；若模为零则返回 0
 */
export function cosineSimilarity(a, b) {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot   += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  return denom === 0 ? 0 : dot / denom;
}
