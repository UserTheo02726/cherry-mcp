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
  } else if (os === 'darwin') {
    return join(homedir(), 'Library', 'Application Support', 'CherryStudio', 'Data', 'KnowledgeBase');
  } else {
    // Linux / WSL
    return join(homedir(), '.config', 'CherryStudio', 'Data', 'KnowledgeBase');
  }
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
  embedUrl:   'http://127.0.0.1:1234/v1/embeddings',
  embedModel: 'text-embedding-qwen3-embedding-8b',
  embedDim:   4096,
  topK:       20,
  threshold:  0.5,
  maxFetch:   1000,
};

/** 解析 embed-url，自动补全 /v1/embeddings 路径，默认值来自 DEFAULTS */
function resolveEmbedUrl(raw) {
  if (!raw) return DEFAULTS.embedUrl;
  const trimmed = raw.replace(/\/$/, '');
  return trimmed.endsWith('/v1/embeddings') ? trimmed : `${trimmed}/v1/embeddings`;
}

/** 统一的配置对象，所有模块均从这里读取 */
const config = {
  topK:        parseInt(argv['top-k']      ?? process.env.DEFAULT_TOP_K      ?? DEFAULTS.topK,       10),
  threshold:   parseFloat(argv['threshold'] ?? process.env.DEFAULT_THRESHOLD  ?? DEFAULTS.threshold),
  maxFetch:    parseInt(argv['max-fetch']  ?? process.env.MAX_FETCH           ?? DEFAULTS.maxFetch,   10),
  kbName:      argv['kb-name']      ?? process.env.DEFAULT_KB_NAME    ?? null,
  kbPath:      argv['kb-path']      ?? process.env.CHERRYSTUDIO_KB_PATH ?? getDefaultKbPath(),
  embedUrl:    resolveEmbedUrl(argv['embed-url']     ?? process.env.EMBEDDING_URL),
  embedApiKey: argv['embed-api-key'] ?? process.env.EMBEDDING_API_KEY ?? '',
  embedModel:  argv['embed-model']   ?? process.env.EMBEDDING_MODEL   ?? DEFAULTS.embedModel,
  embedDim:    parseInt(argv['embed-dim']   ?? process.env.EMBEDDING_DIMENSION ?? DEFAULTS.embedDim, 10),
};

export default config;
