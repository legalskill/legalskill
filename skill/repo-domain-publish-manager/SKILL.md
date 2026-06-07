---
name: repo-domain-publish-manager
description: 管理 GitHub/Gitee 代码仓库同步、Cloudflare 域名 DNS 与页面规则配置、本地文件组织与发布的综合运维技能。当用户需要操作 GitHub 仓库（同步、Pages 部署、README 维护）、Gitee 镜像/私仓管理、Cloudflare DNS 记录与重定向规则、或跨仓库本地文件整理发布时使用。触发词包括："管理仓库"、"同步 GitHub"、"配置域名"、"DNS 设置"、"Pages 部署"、"Gitee 镜像"、"发布技能"、"域名重定向"。
license: CC BY-SA 4.0
metadata:
  author: 律锥·legalskill https://www.legalskill.cn
  version: "1.2.0"
  category: operations
  tags: "github, gitee, cloudflare, dns, domain, repository, deployment, file-management"
  updated_at: "2026-05-27T04:30:00Z"
---

# 仓库、域名与发布管理助手

本技能覆盖从代码仓库管理到域名 DNS 配置、再到本地文件组织发布的完整运维链路。基于 2026-05-15 实战验证的标准流程。

## 概述

当用户需要管理 **GitHub 仓库**（组织仓/个人仓同步与 Pages 部署）、**Gitee 仓库**（镜像/私仓）、**Cloudflare 域名 DNS 与页面规则**、或**本地文件跨仓库整理发布**时，按本技能的标准流程操作。

核心原则：
- 操作前先扫描现状，再决定行动
- 不可逆操作（删除、推送覆盖）须先确认
- Cloudflare API 操作优先使用已保存的 Token

## 决策树

```
用户任务属于哪类？
├── GitHub 仓库管理 → 按「GitHub 仓库同步流程」执行
├── GitHub Pages 部署 → 按「Pages 部署与排障」执行
├── Gitee 镜像/私仓 → 按「Gitee 仓库管理」执行
├── Cloudflare DNS/域名 → 按「域名管理流程」执行
├── 本地文件整理发布 → 按「本地文件管理流程」执行
├── WorkBuddy Agent 技能发布 → 按「WorkBuddy 技能同步」执行
└── 综合运维（跨模块）→ 依次执行各模块，最后做一致性检查
```

## 一、配置发现（前置步骤）

执行任何操作前，先读取现有配置：

1. Cloudflare Token：如果 `token/cloudflare.txt` 存在则读取
2. GitHub 远程配置：`git remote -v` 获取远程仓库地址
3. 当前目录结构：列出目标目录

## 二、GitHub 仓库同步流程

### 2.1 组织仓库同步
当同步组织仓库（如 `github.com/legalskill/<repo>`）时：
- 如果 `D:\github\<repo>` 本地目录存在：
  - 阅读 `references/github-ops.md` 获取详细流程
  - 对比本地与远程提交差异（`git log --oneline -5` vs 远程）
  - 以本地为准时，先 `git pull --rebase` 再 `git push`
  - 以远程为准时，先 `git fetch` 再 `git reset --hard origin/main`
- 如果本地目录不存在：先 `git clone`，再按需调整

### 2.2 README 维护
- 遍历 README.md 中所有链接，确认指向正确仓库
- 目录结构与实际文件树保持一致

### 2.3 分支管理
- 默认分支：`main` 或 `v4`（取决于仓库）
- 禁止直接 force push 到 main

## 三、GitHub Pages 部署与排障

当遇到 Pages 部署问题时：
- 阅读 `references/github-ops.md` 中的 Pages 排障章节
- 常见问题：
  - **404 Not Found**：检查仓库 Settings → Pages → Source 是否为 GitHub Actions
  - **Workflow success 但页面不可访问**：确认 deploy-pages job 实际执行
  - **Jekyll 部署覆盖自定义 Workflow**：确保 Source 选 GitHub Actions 而非 Deploy from branch

## 四、Gitee 仓库管理

### 4.1 组织仓库镜像
- Gitee 组织（如 `gitee.com/legalskill`）作为 GitHub 的国内镜像
- 同步方式：从 GitHub clone 后 push 到 Gitee 对应仓库

### 4.2 个人私有仓库
- 私仓（如 `gitee.com/legalskill/sunlegal`）用于个人技能/工具
- 与组织仓独立管理，不自动同步

### 4.3 授权配置
- 使用 Git 凭据管理器（Windows）自动记住账号密码
- 首次推送时输入凭据，后续自动使用

## 五、Cloudflare 域名管理流程

### 5.1 Token 管理
- Token 默认位置：`token/cloudflare.txt`
- 创建 Token 要求权限：DNS 编辑 + 页面规则编辑
- 如果 Token 不存在，引导用户到 Cloudflare 控制台创建

### 5.2 DNS 记录管理
当需要管理 DNS 记录时，阅读 `references/cloudflare-ops.md`：
- Zone ID：`9caa3942688c15b6655f55982d2980a9`（legalskill.cn）
- 常用操作：列出记录、添加 A/CNAME 记录、修改代理状态

### 5.3 页面规则（重定向）
- `www.legalskill.cn/*` → 301 重定向到 Gitee Pages
- `git.legalskill.cn` → 指向代码仓库主页
- 规则优先级：数字越小越优先

### 5.4 故障排查
- **522 Connection Timed Out**：目标服务器不可达，检查 DNS 指向的 IP 是否正确
- **DNS 记录不生效**：检查代理状态（proxied: true/false）

## 六、本地文件管理流程

### 6.1 跨仓库文件迁移
当将文件从一个本地目录迁移到另一个时：
- 阅读 `references/local-file-ops.md`
- 步骤：
  1. 确认源目录和目标目录结构
  2. 对比差异，列出需迁移的文件
  3. 逐目录迁移，保持子目录结构
  4. 验证完整性

### 6.2 目录结构标准
```
D:\legalskill\              # 主工作区
├── repo-domain-publish-manager/  # 本技能
├── skill-writing-assistant/      # 技能编写助手
├── token/                        # 凭据存储
│   └── cloudflare.txt
└── ...（其他技能/项目）

D:\github\                   # GitHub 本地镜像区
├── legalskill/              # 组织仓库镜像
└── sunlegal/                # 个人仓库镜像
```

## 七、端到端工作流：技能发布

当用户要求"发布一个技能到 GitHub + Gitee"时：

```
D:\legalskill\<skill>\          D:\github\legalskill\skill\<skill>\       GitHub + Gitee
   (开发工作区)          →        (本地发布目录，有 git)           →        (线上)
   修改、验证                     同步 + git add/commit/push             双平台推送
```

1. **工作区修改**：在 `D:\legalskill\<skill>\` 下完成所有编辑
2. **同步到发布目录**：将技能目录同步到 `D:\github\legalskill\skill\<skill>\`。使用 `robocopy` 排除临时目录、分发素材和备份文件：
   ```powershell
   robocopy D:\legalskill\<skill>\ D:\github\legalskill\skill\<skill>\ /E /XD scratch single-file /XF *.bak *.old *.backup
   ```
   同步前确保 `scratch/` 外无残留备份（参见 `references/local-file-ops.md` §6.3 自查命令）。**`single-file/` 目录不纳入 Git**（自动生成的分发素材，随技能一起 robocopy 到发布目录但 just for reference）。
3. **生成 single-file/ 分发素材**：在发布前，若技能包含 `scripts/merge_single_file.py`，运行它生成/更新 `single-file/` 目录：
   ```bash
   python scripts/merge_single_file.py
   ```
   生成 3 个文件：合并版 `SKILL.md` + 版本化 `.md` + 版本化 `.zip`（排除 scratch/ 和 single-file/）。此步骤可选，仅对需要多平台分发素材的技能执行。
4. **打包完整 zip**：将整个发布目录打成 zip 存档到 `D:\github\zip\`（`*` 通配打包全部文件）。**命名规范**：`<技能名>_<版本>_<YYYYMMDD>.zip`（如 `skill-writing-assistant_1.2.0_20260527.zip`），历史版本通过日期后缀自然保留：
   ```powershell
   mkdir D:\github\zip 2>nul
   powershell -Command "Compress-Archive -Path D:\github\legalskill\skill\<skill>\* -DestinationPath D:\github\zip\<skill>_<version>_<date>.zip -Force"
   ```
   打包后验证 zip 内文件数与源目录一致（参见 `references/local-file-ops.md` §3 步骤 1.6）。
5. **发布复查**（`git push` 前）：对照 `references/local-file-ops.md` §3 检查清单逐项确认；检查 scratch/ 外无残留备份。
6. **提交推送**：
   ```bash
   cd D:\github\legalskill
   git add -A
   git commit -m "<msg>"
   git push origin main      # GitHub
   git push gitee main       # Gitee
   ```
7. **更新 Pages**：如果技能有文档站点，触发 Pages 重新部署
8. **DNS 检查**：确认域名重定向规则正确

> 工作区 (`D:\legalskill`) 不是 git 仓库，可自由存放 token、临时文件等；发布目录 (`D:\github\legalskill`) 是 git 追踪的干净发布包。两边分离，保持线上整洁。

## 八、WorkBuddy 技能同步（Agent 技能专用）

> 适用范围：已绑定 WorkBuddy Agent 的技能（如 `tencent-ima-copilot-legal-consultation`），需要将技能源同步到 WorkBuddy 插件目录的内嵌副本。详细流程见 `references/workbuddy-sync.md`。

### 8.1 映射关系

技能与 WorkBuddy Agent 的映射记录在 `D:\github\skills-mapping.json`。`sync_skills.py` 读取此文件，按 `source → target` 逐对同步。

### 8.2 同步步骤

修改技能源文件后：

```bash
# 1. 如果版本号变更 → 同步两处
#    - 编辑 skill/skill.yaml 的 version 字段
#    - 编辑 D:\github\skills-mapping.json 对应 skill 的 version 字段

# 2. 运行同步（在 publish-manager 目录下）
cd D:\legalskill\repo-domain-publish-manager
python scripts/sync_skills.py              # 先检查差异
python scripts/sync_skills.py --sync       # 确认后自动同步

# 3. 提交 Git（源 + WorkBuddy 副本都在同一个 legalskill 仓库）
cd D:\github\legalskill
git add -A
git commit -m "skill: vX.X.X - 更新说明"
git push origin main
```

### 8.3 保留文件

WorkBuddy 副本中有两个元数据文件由 SkillHub/IDE 自动生成，同步时不会被删除：
- `_meta.json`：SkillHub 发布元数据
- `_skillhub_meta.json`：本地安装元数据

### 8.4 关键约束

- `sync_skills.py` 是发布工具，存放在 `repo-domain-publish-manager/scripts/`，**不随 WorkBuddy 产品分发**
- WorkBuddy 目录是产品，不应包含开发工具脚本
- `skills-mapping.json` 是 sync_skills.py 的唯一数据源，版本号变更时必须同步更新

## 关键约束 (Gotchas)

- Cloudflare API Token 存储在 `token/cloudflare.txt`，不要提交到 Git 仓库
- GitHub Pages 必须在 Settings → Pages 中将 Source 设为 GitHub Actions，否则 deploy-pages 不生效
- Gitee 与 GitHub 分开管理，一个的修改不会自动同步到另一个
- DNS 修改有 TTL 缓存延迟，修改后最多等待 5 分钟生效
- 不可逆操作（`git push --force`、删除 DNS 记录、删除仓库文件）必须先获得用户确认
- `git.legalskill.cn` 是国内 Gitee 镜像入口，`www.legalskill.cn` 重定向到 Gitee Pages
- **技能平台 URL 规律**（发布后可主动推算公共链接，无需用户提供）：
  - SkillHub：`https://skillhub.cn/skills/{skill-name}`（`skill-name` = 技能目录名，小写连字符）
  - IMA Skill：`https://ima.qq.com/skill?shareId={share_id}&from=share`
  - GitHub：`https://github.com/legalskill/legalskill/tree/main/skill/{skill-name}`

## 获取详细指南

- 当需要管理 Cloudflare DNS 记录、Token 创建或页面规则时，阅读 `references/cloudflare-ops.md`。
- 当需要 GitHub 仓库同步、Pages 部署或 README 维护时，阅读 `references/github-ops.md`。
- 当需要 Gitee 镜像同步、私仓管理或授权配置时，阅读 `references/gitee-ops.md`。
- 当需要跨仓库文件迁移、目录结构调整时，阅读 `references/local-file-ops.md`。

> **免责声明**：以上内容由 AI 辅助生成，仅供参考，具体操作前请结合实际情况进行专业判断。Cloudflare API Token 等凭据请妥善保管，严禁将涉密信息输入公域大模型。

*技能版本：1.2.0 | 作者：[律锥·legalskill](https://www.legalskill.cn) | 文档许可：CC BY-SA 4.0*
