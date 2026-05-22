# OpenClaw 配置字段完整参考

> 本文档提供 OpenClaw 核心配置字段的完整参考，继承自官方文档 `~/.openclaw/openclaw.json` JSON5 配置体系。
> 所有字段均为可选——OpenClaw 在省略时使用安全默认值。

## 配置格式

JSON5（支持注释 `//` 和 `/* */`、尾随逗号）。

## 顶层结构

```json5
{
  agents: {},        // 智能体默认值和多智能体列表
  channels: {},      // 频道配置
  gateway: {},       // 网关服务器配置
  tools: {},         // 工具策略
  skills: {},        // Skills 管理
  plugins: {},       // 插件管理
  mcp: {},           // MCP 服务器定义
  session: {},       // 会话生命周期
  messages: {},      // 消息投递
  hooks: {},         // Webhook 端点
  cron: {},          // 定时任务
  browser: {},       // 浏览器自动化
  models: {},        // 模型目录
  talk: {},          // Talk 模式
  env: {},           // 环境变量
  secrets: {},       // 密钥管理
  auth: {},          // 认证存储
  logging: {},       // 日志
  diagnostics: {},   // 诊断和 OpenTelemetry
  ui: {},            // UI 定制
  bindings: [],      // 多智能体路由绑定
  update: {},        // 自动更新
  acp: {},           // ACP 协议
  discovery: {},     // 服务发现
  cli: {},           // CLI 定制
  bundles: {},       // 旧版插件沙箱
}
```

## agents.defaults

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",     // 工作区路径（默认 cwd）
      repoRoot: "~/Projects/openclaw",         // 可选：仓库根目录
      skills: ["github", "weather"],           // 技能白名单（省略=无限制）
      skipBootstrap: false,                    // 禁止自动创建引导文件
      skipOptionalBootstrapFiles: ["SOUL.md"], // 跳过可选引导文件
      contextInjection: "always",              // always | continuation-skip | never
      bootstrapMaxChars: 12000,                // 单文件截断上限
      bootstrapTotalMaxChars: 60000,           // 总计截断上限
      imageMaxDimensionPx: 1200,               // 图片最大像素
      userTimezone: "Asia/Shanghai",           // 时区
      timeFormat: "auto",                      // auto | 12 | 24
      model: {                                 // 模型配置
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["openai/gpt-5.4"],
      },
      models: {                                // 模型目录（同时也是 /model 白名单）
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "openrouter/*": {},                    // 动态发现某个Provider所有模型
      },
      thinkingDefault: "low",                  // off | minimal | low | medium | high | xhigh | adaptive | max
      verboseDefault: "off",                   // off | on | full
      elevatedDefault: "on",                   // off | on | ask | full
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      maxConcurrent: 4,
      params: { cacheRetention: "long" },      // 全局 Provider 参数
      heartbeat: {
        every: "30m",
        target: "last",
        prompt: "Read HEARTBEAT.md if it exists...",
        isolatedSession: false,
        timeoutSeconds: 45,
      },
      compaction: {
        mode: "safeguard",                     // default | safeguard
        memoryFlush: { enabled: true },
      },
      sandbox: {
        mode: "off",                           // off | non-main | all
        backend: "docker",                     // docker | ssh | openshell
        scope: "agent",                        // session | agent | shared
        workspaceAccess: "none",               // none | ro | rw
      },
      contextPruning: { mode: "off" },         // off | cache-ttl
      blockStreamingDefault: "off",
      typingMode: "instant",                   // never | instant | thinking | message
    },
    list: [],                                  // 每个智能体的覆盖配置
  },
}
```

## agents.list（多智能体）

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        model: "anthropic/claude-opus-4-6",
        thinkingDefault: "high",
        skills: ["docs-search"],
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
        },
      },
    ],
  },
}
```

## gateway

```json5
{
  gateway: {
    mode: "local",               // local | remote
    port: 18789,
    bind: "loopback",            // auto | loopback | lan | tailnet | custom
    auth: {
      mode: "token",             // none | token | password | trusted-proxy
      token: "your-token",       // 或 OPENCLAW_GATEWAY_TOKEN
      allowTailscale: true,
    },
    tailscale: {
      mode: "off",               // off | serve | funnel
    },
    controlUi: {
      enabled: true,
      basePath: "/openclaw",
    },
    tls: {
      enabled: false,
      autoGenerate: false,
    },
    reload: {
      mode: "hybrid",            // off | restart | hot | hybrid
      debounceMs: 500,
    },
  },
}
```

## tools

```json5
{
  tools: {
    profile: "coding",           // minimal | coding | messaging | full
    allow: ["group:fs"],
    deny: ["browser", "canvas"],
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
    toolsBySender: {
      "*": { deny: ["exec", "process"] },
    },
    exec: {                                 // exec 工具安全
      applyPatch: true,                     // 是否启用 apply_patch
    },
  },
}
```

## skills

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm",                  // npm | pnpm | yarn | bun
    },
    entries: {
      "image-lab": {
        apiKey: "GEMINI_KEY_HERE",
        env: { GEMINI_API_KEY: "KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
    limits: {
      maxSkillsPromptChars: 18000,
    },
  },
}
```

## mcp

```json5
{
  mcp: {
    sessionIdleTtlMs: 600000,    // 空闲回收（0=禁用）
    servers: {
      docs: {
        command: "npx",
        args: ["-y", "@modelcontextprotocol/server-fetch"],
      },
      remote: {
        url: "https://example.com/mcp",
        transport: "streamable-http",  // streamable-http | sse
        headers: { Authorization: "Bearer ${MCP_REMOTE_TOKEN}" },
      },
    },
  },
}
```

## 环境变量

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

支持 `${VAR_NAME}` 语法在任意配置字符串中引用环境变量。

## 密钥管理 (SecretRef)

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

## 配置包含 ($include)

```json5
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },         // 单文件替换
  broadcast: { $include: ["./a.json5", "./b.json5"] },  // 数组深度合并
}
```

最大嵌套 10 层。路径相对于包含文件所在目录。

## 更多细节

完整官方参考：[Configuration Reference](https://docs.openclaw.ai/gateway/configuration-reference)
