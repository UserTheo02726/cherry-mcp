/**
 * 数据库操作模块 - 扫描与读取 Cherry Studio 知识库
 *
 * Cherry Studio 知识库是 SQLite 数据库，包含一个 vectors 表：
 *   - id: INTEGER
 *   - pageContent: TEXT
 *   - source: TEXT
 *   - vector: BLOB (Float32 小端序二进制)
 *
 * 注意：sql.js 是纯 WASM，需要整库读入内存。对于大型知识库（>50MB）查询较慢，
 * 但可避免任何 C++ 原生编译依赖，保证 npx 无摩擦运行。
 *
 * Author: Theo
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, basename, extname } from 'node:path';
import { createRequire } from 'node:module';
import config from './config.js';

// sql.js 是 CommonJS 包，在 ESM 中需要 createRequire 以正确加载 WASM 二进制
const require = createRequire(import.meta.url);
const initSqlJs = require('sql.js');

let SQL = null;

/** 懒加载并缓存 sql.js 引擎实例（WASM 初始化开销较重） */
async function getSqlEngine() {
  if (!SQL) {
    SQL = await initSqlJs();
  }
  return SQL;
}

/**
 * 递归收集知识库目录下的所有候选数据库文件
 * @returns {string[]} 文件路径列表
 */
function collectDbFiles() {
  const root = config.kbPath;
  const files = [];

  let entries;
  try {
    entries = readdirSync(root);
  } catch {
    return [];
  }

  for (const name of entries) {
    const fullPath = join(root, name);
    const stat = statSync(fullPath);
    if (stat.isFile()) {
      files.push(fullPath);
    } else if (stat.isDirectory()) {
      // Cherry Studio 有时会将库放入子文件夹
      for (const sub of readdirSync(fullPath)) {
        const subPath = join(fullPath, sub);
        if (statSync(subPath).isFile()) {
          files.push(subPath);
        }
      }
    }
  }

  return files;
}

/**
 * 探查单个 SQLite 文件中的向量维度与数量
 * @param {string} filePath
 * @param {object} SQL
 * @returns {{ count: number, dimension: number | null } | null}
 */
function probeDatabase(filePath, SQL) {
  let db;
  try {
    const data = readFileSync(filePath);
    db = new SQL.Database(data);
    const [{ values: [[count]] }] = db.exec('SELECT COUNT(*) FROM vectors');
    const res = db.exec('SELECT vector FROM vectors LIMIT 1');
    let dimension = null;
    if (res.length > 0 && res[0].values[0][0]) {
      const buf = res[0].values[0][0];
      // sql.js 返回 Uint8Array，Float32 每元素 4 字节
      dimension = buf.byteLength / 4;
    }
    return { count: Number(count), dimension };
  } catch {
    return null;
  } finally {
    db?.close();
  }
}

/**
 * 列出所有有效的知识库及其统计信息
 * @returns {Promise<Array>}
 */
export async function listKnowledgeBases() {
  const SQL = await getSqlEngine();
  const files = collectDbFiles();
  const result = [];

  for (const filePath of files) {
    const probe = probeDatabase(filePath, SQL);
    if (probe === null) continue; // 不是合法的 vectors 数据库

    const stat = statSync(filePath);
    const vectorCount = probe.count;
    
    // 根据向量数计算建议参数
    const suggestedTopK = Math.min(50, Math.max(20, Math.floor(vectorCount / 50)));
    const suggestedMaxFetch = Math.min(5000, Math.max(500, vectorCount * 2));
    const suggestedThreshold = 0.5;

    result.push({
      name: basename(filePath, extname(filePath)),
      path: filePath,
      sizeMb: +(stat.size / 1024 / 1024).toFixed(2),
      vectorCount,
      dimension: probe.dimension ?? 'unknown',
      suggestedTopK,
      suggestedMaxFetch,
      suggestedThreshold,
    });
  }

  return result;
}

/**
 * 从指定数据库文件中读取所有记录并与查询向量打分
 * @param {string} filePath
 * @param {Float32Array} queryVector
 * @param {object} SQL
 * @returns {Array<{id, content, source, score}>}
 */
function searchOneDb(filePath, queryVector, SQL) {
  let db;
  try {
    const data = readFileSync(filePath);
    db = new SQL.Database(data);
    const rows = db.exec(
      `SELECT id, pageContent, source, vector FROM vectors LIMIT ${config.maxFetch}`
    );
    if (!rows.length) return [];

    const results = [];
    for (const [id, content, source, vectorBlob] of rows[0].values) {
      if (!vectorBlob || !content) continue;

      // sql.js 返回 Uint8Array，其底层 ArrayBuffer 可能存在 byteOffset 偏移。
      // 使用 .slice() 生成一个 offset=0 的独立 ArrayBuffer 后再构造 Float32Array，
      // 确保向量分量不因偏移而错位（与 Python numpy.frombuffer 的小端字节序保持兼容）。
      const docVector = new Float32Array(vectorBlob.slice().buffer);

      if (docVector.length !== queryVector.length) continue;

      results.push({ id, content, source, _vector: docVector });
    }
    return results;
  } catch {
    return [];
  } finally {
    db?.close();
  }
}

/**
 * 跨库向量搜索
 * @param {Float32Array} queryVector
 * @param {object} opts  - { topK, threshold, kbName }
 * @returns {Promise<Array>}
 */
export async function searchVectors(queryVector, { topK, threshold, kbName } = {}) {
  const { cosineSimilarity } = await import('./vector_math.js');
  const SQL = await getSqlEngine();

  let files = collectDbFiles();

  // 按知识库名称过滤
  if (kbName) {
    files = files.filter(f => basename(f, extname(f)) === kbName);
  }

  const tk = topK ?? config.topK;
  const thr = threshold ?? config.threshold;

  const allResults = [];

  for (const filePath of files) {
    const rows = searchOneDb(filePath, queryVector, SQL);
    for (const row of rows) {
      const score = cosineSimilarity(queryVector, row._vector);
      if (score >= thr) {
        allResults.push({
          id: row.id,
          source: row.source ?? '未知来源',
          content: row.content,
          score,
        });
      }
    }
  }

  allResults.sort((a, b) => b.score - a.score);
  return allResults.slice(0, tk);
}
