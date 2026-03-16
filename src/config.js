/**
 * 配置模块 - 统一解析 CLI 参数、环境变量与系统默认值
 *
 * 优先级：CLI 参数 > 环境变量 > 内置默认值
 * 注意：不加载 .env 文件，环境变量由 MCP 客户端或系统注入。
 *
 * Author: Theo
 */
import { parseArgs } from 'node:util';
import { homedir, platform } from 'node:os';
import { join } from 'node:path';

/** 根据操作系统返回 Cherry Studio 知识库的默认路径 */
function getDefaultKbPath() {
  const os = platform();
  if (os === 'win32') {
    return join(homedir(), 'AppData', 'Roaming', 'CherryStudio', 'Data', 'KnowledgeBase');
  }
  return null;
}

/** 解析命令行参数 */
const { values: argv } = parseArgs({
  args: process.argv.slice(2),
  strict: false,
  options: {
    'top-k':         { type: 'string' },
    'threshold':     { type: 'string' },
    'max-fetch':     { type: 'string' },
    'kb-name':       { type: 'string' },
    'kb-path':       { type: 'string' },
    'embed-url':     { type: 'string' },
    'embed-api-key': { type: 'string' },
    'embed-model':   { type: 'string' },
    'embed-dim':     { type: 'string' },
  }
});

/** 所有参数的内置默认值（集中管理，避免散落在各处）*/
const DEFAULTS = {
  topK:       20,
  threshold:  0.5,
  maxFetch:   1000,
};

/** 解析必填参数，如果未提供则抛出错误 */
function resolveRequired(key, cliKey, envKey) {
  const value = argv[cliKey] ?? process.env[envKey] ?? null;
  if (!value) {
    throw new Error(`${key} 为必填参数，请通过 CLI 参数 --${cliKey} 或环境变量 ${envKey} 提供`);
  }
  return value;
}

/** 解析必填数值参数，如果未提供或无效则抛出错误 */
function resolveRequiredInt(key, cliKey, envKey) {
  const raw = argv[cliKey] ?? process.env[envKey] ?? null;
  if (!raw) {
    throw new Error(`${key} 为必填参数，请通过 CLI 参数 --${cliKey} 或环境变量 ${envKey} 提供`);
  }
  const value = parseInt(raw, 10);
  if (isNaN(value) || value <= 0) {
    throw new Error(`${key} 必须为正整数，当前值: ${raw}`);
  }
  return value;
}

/** 统一的配置对象，所有模块均从这里读取 */
const config = {
  topK:        parseInt(argv['top-k']      ?? process.env.DEFAULT_TOP_K      ?? DEFAULTS.topK,       10),
  threshold:   parseFloat(argv['threshold'] ?? process.env.DEFAULT_THRESHOLD  ?? DEFAULTS.threshold),
  maxFetch:    parseInt(argv['max-fetch']  ?? process.env.MAX_FETCH           ?? DEFAULTS.maxFetch,   10),
  kbName:      argv['kb-name']      ?? process.env.DEFAULT_KB_NAME    ?? null,
  kbPath:      argv['kb-path']      ?? process.env.CHERRYSTUDIO_KB_PATH ?? getDefaultKbPath(),
  embedUrl:    resolveRequired('embed-url', 'embed-url', 'EMBEDDING_URL'),
  embedApiKey: argv['embed-api-key'] ?? process.env.EMBEDDING_API_KEY ?? '',
  embedModel:  resolveRequired('embed-model', 'embed-model', 'EMBEDDING_MODEL'),
  embedDim:    resolveRequiredInt('embed-dim', 'embed-dim', 'EMBEDDING_DIMENSION'),
};

export default config;
