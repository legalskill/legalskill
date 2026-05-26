<p align="center">
  <h1 align="center">⚖️ 律锥·legalskill</h1>
  <p align="center"><strong>法律技能开源社区</strong> — 法律人的 AI 实战赋能与合规护航开源技能社区</p>
  <p align="center">
    <a href="#-使命锥处囊中脱颖而出">使命</a> ·
    <a href="#-行业背景">背景</a> ·
    <a href="#-法律技能">技能</a> ·
    <a href="#-技能目录">目录</a> ·
    <a href="#-许可">许可</a> ·
    <a href="#-参与">参与</a>
  </p>
</p>

---

## 🔷 使命：锥处囊中，脱颖而出

**律锥·legalskill** 是由兼具计算机与法学双背景的执业律师孙律师发起的**法律技能开源社区**。

我们致力于帮助法律人化解一个核心矛盾：**"想用不敢用，会用用不好。"** 通过开放、合规、实战导向的开源法律技能（Legal Skill），让每一位律师都能安全、高效地驾驭 AI 工具，在智能时代实现职业价值的脱颖而出。

---

## 🔶 行业背景

2025 年 2 月，**DeepSeek 开源**引爆法律科技新一轮浪潮；同期，腾讯 AI 工作台 **ima.copilot** 持续进化，以 RAG 为核心打造基于个人知识库的"可溯源"智能工作台，为法律场景的合规检索提供了坚实底座。随后，知识库广场、知识号、订阅知识库等功能相继上线。2026 年 3 月，**OpenClaw 开源**引发法律智能体热潮；4 月，**ima 正式上线 copilot**。

**律锥·legalskill** 在此背景下正式启动 GitHub 开源项目库：不盲目追逐技术奇观，也不回避 AI 浪潮，而是专注于 **AI 工具在法律实务中的落地应用与风险防范**，以开源技能为媒介，陪伴法律人从工具使用者成长为生态共建者。

---

## 🔷 核心理念

| 理念 | 内涵 |
|:-----|:-----|
| **AI 是放大器，而非替代者** | 放大律师的专业价值，而非让其廉价化。 |
| **人的幻觉比 AI 幻觉危害更大** | 警惕"自以为在进步"的认知负债，坚持实战验证。 |
| **生态选择大于工具选择** | 回归微信客户主阵地，构建可持续服务闭环。 |
| **开源共享，合规先行** | 无加密、无后门，合规红线植入每一个法律技能的基因。 |

---

## 🛠️ 法律技能

律锥·legalskill 以 **法律技能（Legal Skill）** 为核心产出，每一个技能都是可独立运行、可组合调用的智能单元。它们深度适配 ima.copilot 知识库 RAG 能力，同时兼容通用环境，实现"一次编写，双端可用"。

### 官方维护技能

| 技能 | 简介 | 适用场景 |
|:-----|:-----|:---------|
| [tencent-ima-copilot-legal-consultation](./skill/tencent-ima-copilot-legal-consultation) | 资深律师式法律咨询，深度适配 ima.copilot 知识库 RAG，五阶段分步诊断，法条与案例均可溯源验证。ima.copilot 环境自动走 RAG 检索，非 ima.copilot 环境自动走联网检索。 | ima.copilot / Claude / API |
| [claw-agent-workspace](./skill/claw-agent-workspace) | Claw 智能体工作区引导管理，自动扫描技能目录生成动态路由注入 AGENTS.md、SOUL.md 等引导文件 | Claude Code / API |

### 社区精选技能

> 查看更多社区贡献的技能，请访问 [技能目录](./SKILL_CATALOG.md)。

---

## 📁 项目结构

```text
legalskill/
├── .github/
│   └── workflows/jekyll-gh-pages.yml
├── skill/
│   ├── tencent-ima-copilot-legal-consultation/   # 法律咨询技能
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   ├── skill.yaml
│   │   ├── references/
│   │   └── scripts/
│   └── claw-agent-workspace/                     # Claw 智能体工作区引导
│       ├── SKILL.md
│       ├── README.md
│       ├── skill.yaml
│       ├── references/
│       └── assets/
├── _config.yml                                   # GitHub Pages 配置
├── CNAME                                         # 自定义域名
├── CONTRIBUTING.md                               # 贡献指南
├── index.md                                      # GitHub Pages 首页
├── LICENSE-CODE                                  # Apache 2.0
├── LICENSE-CONTENT                               # CC BY-SA 4.0
├── README.md
├── SKILL_CATALOG.md                              # 社区技能目录
└── SKILL_TEMPLATE.md                             # 技能模板
```

---

## ⚖️ 许可

律锥·legalskill 的法律技能采用 **代码与内容双许可**，按文件类型明确区隔：

| 资产类型 | 涵盖文件 | 适用许可 |
|:---------|:---------|:---------|
| **代码** | `.py` `.js` `.ts` `.json` `.yaml` 及适配器、路由逻辑等可执行文件 | Apache License 2.0 |
| **内容** | `SKILL.md`、`references/` 下全部文件、输出模板文本、方法论说明 | CC BY-SA 4.0 |

**许可效果**：

- Apache 2.0 覆盖的代码可自由使用、修改、商用，须保留原版权声明。
- CC BY-SA 4.0 覆盖的内容可自由使用、修改、商用，但须署名"律锥·legalskill"，且修改后须以相同许可公开。该义务仅在分发修改后的内容作品时触发，SaaS 模式下作为服务调用不受影响。

仓库内提供两份许可全文：`LICENSE-CODE` 与 `LICENSE-CONTENT`。每个 `SKILL.md` 文件头部 `license` 字段亦标注 CC BY-SA 4.0。

---

## 🛡️ 合规红线

本社区所有法律技能产出均为 **初步法律研究参考，不构成正式法律意见**。

- AI 生成内容须经人工复核后方可采用。
- 严禁将涉案涉密信息输入公域大模型。
- 检索结果中涉及的法规与案例，使用者须自行核实现行有效性。
- 案件实质推进前，请务必咨询具备相应执业资格的律师。

---

## 🤝 参与

**律锥·legalskill** 欢迎所有法律人与开发者共建法律技能开源社区：

- **贡献技能**：参考 `CONTRIBUTING.md` 和 [tencent-ima-copilot-legal-consultation](./skill/tencent-ima-copilot-legal-consultation) 的目录结构提交 PR。新技能须包含 `SKILL.md`（含 CC BY-SA 4.0 声明与完整免责声明）、代码文件及标准元数据 `skill.yaml`。
- **推荐技能**：在 [GitHub Discussions](https://github.com/legalskill/legalskill/discussions/categories/ideas) 推荐优秀的外部技能，经审核后可收录至社区技能目录。
- **反馈建议**：在 Issues 提出使用问题或新技能想法。
- **成为维护者**：持续贡献高质量法律技能后，可申请核心维护资格。

---

## 📬 联系

| 渠道 | 用途 |
|:-----|:-----|
| 微信公众号「律锥」（微信号：`legalskill`） | 社区动态、技能更新推送、深度文章 |
| 微信 / QQ（`89930280`，备注 `github`） | 使用问题、Bug 反馈、联系作者 |
| 邮箱 `89930280@qq.com` | 日常联系、材料发送 |
| [QQ频道](https://pd.qq.com/s/970hmmfux?b=9)（频道号：`pd89930280`） | 法律人日常交流、问题互助 |
| [QQ群](https://qm.qq.com/q/8947858)（群号：`8947858`） | 社区即时讨论、使用交流 |
| [ima.copilot 法律技能知识库](https://ima.qq.com/wiki/?shareId=8138fdfd3f6c571966e2433946f437f8f8814548b738a2cd8ca9a80b7aed177c) | 即开即用的法律技能知识库 |
| 孙律师个人公众号「孙律师」（微信号：`AGILVSHI`） | 执业思考、技术拆解、行业观察 |

<p align="center"><strong>律锥·legalskill</strong> 不仅开源法律技能，更开源一种安全、务实、可持续的 AI 工作方式。</p>

<p align="center">锥处囊中，脱颖而出 · 陪伴法律人走稳 AI 时代的执业之路</p>
