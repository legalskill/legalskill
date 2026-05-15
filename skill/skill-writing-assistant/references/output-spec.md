---
name: skill-output-spec
description: 生成符合 agentskills.io 标准技能规范的 Markdown 文件。当用户要求"输出技能文件"、"生成技能Markdown"、"保存为规范格式"或类似请求时使用。遵循CommonMark标准和渐进式披露原则，确保生成的文件格式正确、结构完整。
license: CC BY-SA 4.0
allowed-tools: "Bash(python:*) Bash(npm:*)"
metadata:
  author: 律锥·legalskill
  version: "1.1.0"
  category: documentation
  tags: [skill-creation, markdown, formatting]
  documentation: https://agentskills.io/
---

# 技能输出规范生成器

## 概述

本技能指导生成符合 agentskills.io 标准技能规范的 Markdown 格式技能文件。严格遵循CommonMark标准和GitHub Flavored Markdown (GFM)扩展，确保生成的技能文件具有最佳兼容性和可移植性。

## 先决条件

使用本技能前，请确保：
- 已经规划好技能的目标、受众和用例
- 确定了技能的结构和内容组织
- 了解技能需要调用的工具（MCP或内置工具）

## 工作流程

### 步骤1：确认技能需求
当用户请求输出技能文件时，首先确认：
- 技能名称（必须使用kebab-case格式）
- 技能功能描述
- 触发条件和使用场景
- 是否需要特定工具或MCP集成

### 步骤2：生成YAML Frontmatter
按照以下格式生成YAML frontmatter：
- 使用 `---` 分隔符包裹（开头和结尾各一行 `---`）
- `---` 必须顶格无缩进
- 包含必需字段：`name`、`description`、`license`、`metadata`
- 可选字段：`allowed-tools`
- ⚠️ `compatibility` 不放在 SKILL.md frontmatter，只放在 `skill.yaml` 中

### 步骤3：生成 skill.yaml
在 SKILL.md 同级创建 `skill.yaml` 机器可读元数据文件。详见下方"skill.yaml 规范"。

### 步骤4：编写技能正文
YAML frontmatter之后紧跟Markdown正文，中间以空行分隔。正文应包括：
- 技能概述
- 核心功能说明
- 使用示例
- 故障排除指南

### 步骤5：末尾免责声明
所有技能的 SKILL.md 末尾**必须包含**免责声明引用块。法律类技能使用标准免责声明，非法律类技能使用通用免责声明。

**法律类技能免责声明**（必含）：

```markdown
> **免责声明**：以上分析仅为基于您提供信息、结合公开法律资料生成的初步法律研究参考，不构成正式法律意见。案件实质推进前，请咨询执业律师。AI 生成内容须经人工复核。严禁将涉密信息输入公域大模型。
```

**非法律类技能免责声明**（必含）：

```markdown
> **免责声明**：以上内容由 AI 辅助生成，仅供参考，具体实施前请结合实际情况进行专业判断。严禁将涉密信息输入公域大模型。
```

### 步骤6：许可证体系
律锥·legalskill 技能采用双层许可，详见 `references/license.md`：

| 层级 | 覆盖范围 | 许可证 |
|:-----|:---------|:-------|
| 文档层 | `SKILL.md` 及 `references/` 下 `.md` 文件 | CC BY-SA 4.0 |
| 代码层 | `scripts/`、`src/` 下代码文件 | Apache-2.0 |

`license` 字段指 SKILL.md 及 references/ 的文档许可，代码部分见仓库根目录 `LICENSE-CODE`。

若技能包含代码，在 `src/` 或代码文件头部标注：
```text
# SPDX-License-Identifier: Apache-2.0
```

## 格式规范

### 整体结构要求
1. **外层包装**：生成的技能文件应以一个Markdown代码块（` ```markdown `）包裹整个输出
2. **代码块闭合**：最外层的 ` ```markdown ` 代码块开始和结束的反引号必须顶格无缩进

### YAML Frontmatter规范
```yaml
name: skill-name-in-kebab-case      # name: 冒号后必须带空格
description: 清晰描述技能功能和触发条件，包含用户可能使用的具体短语
license: CC BY-SA 4.0
allowed-tools: "Bash(python:*) Bash(npm:*)"  # 可选
metadata:
  author: 律锥·legalskill
  version: "1.0.0"
  category: 类别
  tags: [标签1, 标签2]  # 可选
  documentation: 文档链接  # 可选
```

**必填字段说明**：
- `license`：必填，指 SKILL.md 及 references/ 的文档许可（CC BY-SA 4.0）。代码部分见仓库根目录 LICENSE-CODE。
- `metadata.author`：必填，统一使用"律锥·legalskill"。
- `metadata.version`：必填，语义化版本号。
- `metadata.category`：必填，技能分类（如 legal、development 等）。

> ⚠️ **注意**：`compatibility` 字段只放在 `skill.yaml` 中，不在 SKILL.md frontmatter 中出现。

### skill.yaml 规范（机器可读元数据）

每个技能**必须**包含一个 `skill.yaml` 文件，与 SKILL.md 同级。用于工具链（包管理、搜索、校验、批量部署）自动读取。

```yaml
name: skill-name-in-kebab-case       # 必填，与 SKILL.md name 一致
version: "1.0.0"                     # 必填，与 SKILL.md metadata.version 一致
author: 律锥·legalskill              # 必填
license: CC BY-SA 4.0                # 必填，文档许可
category: legal                      # 必填，技能分类
tags: [tag1, tag2]                   # 必填，搜索标签

triggers:                            # 必填，触发关键词列表
  - "用户可能说的短语"
  - "关键词"

not_for:                             # 必填，排除场景（防止误触发）
  - "不适用于的场景描述"

references:                          # 必填，references/ 下文件清单
  - file: kb-profiles.md
    desc: 文件用途简述

knowledge_bases:                     # 可选，依赖的 IMA 知识库
  - name: "知识库全名"
    required: false                  # true=必须订阅 / false=可选增强
    role: "该库在本技能中的角色"

compatibility:                       # 必填，兼容平台列表
  - IMA
  - Claude.ai
  - Claude Code
  - API
```

**字段规则**：
- `name`、`version` 必须与 SKILL.md frontmatter 保持一致。
- `triggers` 列表提供搜索和自动分类能力，不替代 description 中的触发描述。
- `not_for` 用于避免技能误触发，至少列出 1 项。
- `references` 必须完整列出 references/ 下所有 .md 文件，添加简短用途说明。
- `knowledge_bases` 仅在技能依赖 IMA 知识库时填写。

### 正文格式要求
- **标题**：使用1-6个`#`符号，后接空格和标题文本
- **段落与换行**：段落间用空行分隔
- **强调**：`*斜体*`、`**粗体**`、`***粗斜体***`
- **列表**：无序列表使用`-`，有序列表使用数字加`.`
- **代码**：行内代码使用单个反引号，代码块使用三个反引号加语言标识符
- **表格**（GFM扩展）：使用管道符创建表格
- **引用块**：使用`>`符号
- **水平线**：使用`---`、`***`或`___`

### 示例输出要求
如果技能包含示例输出，应根据内容类型使用正确的代码块包裹：
- **文本输出**：使用 ` ```text ` 代码块
- **代码输出**：使用 ` ```bash `、` ```python ` 等
- **数据输出**：使用 ` ```json `、` ```xml `、` ```yaml ` 等
- **错误信息**：使用 ` ```text ` 或 ` ```bash ` 代码块

**关键原则**：所有代码块的开始和结束反引号必须顶格无缩进。

## 技能示例

以下是一个完整技能文件的标准输出格式：

````markdown
```yaml
name: example-skill            # 冒号后必须带空格
description: 这是一个示例技能，用于演示标准技能文件格式。当用户要求"生成示例技能"或"展示技能格式"时使用。
license: CC BY-SA 4.0
metadata:
  author: 律锥·legalskill
  version: "1.0.0"
  category: example
  tags: [demo, example, formatting]
```

# 示例技能

## 概述

这是一个用于演示标准技能文件格式的示例技能。

## 核心功能

### 1. 功能一
- 展示技能结构
- 演示格式规范

### 2. 功能二
- 提供代码示例
- 展示最佳实践

## 代码示例

```bash
# 示例命令
echo "Hello, Skill!"
```

```python
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2023-2026 律锥·legalskill

def example_function():
    """示例函数"""
    return "示例输出"
```

---

> **免责声明**：以上内容由 AI 辅助生成，仅供参考，具体实施前请结合实际情况进行专业判断。严禁将涉密信息输入公域大模型。

---

*技能版本：1.0.0 | 作者：律锥·legalskill | 文档许可：CC BY-SA 4.0*
````

## 故障排除

### 问题1：技能不上传
**症状**：收到错误"Could not find SKILL.md in uploaded folder"
**原因**：生成的Markdown文件没有正确的外层代码块包装
**解决方案**：
- 确保整个输出被 ` ```markdown ` 代码块包裹
- 检查开始和结束反引号是否顶格无缩进

### 问题2：YAML解析错误
**症状**：上传时提示"Invalid frontmatter"
**原因**：YAML格式不正确
**解决方案**：
- 检查YAML缩进（使用空格，不要用制表符）
- 确保键值对格式正确
- 避免在description字段中使用XML尖括号（< >）

### 问题3：技能不触发
**症状**：生成的技能文件不上传或不触发
**原因**：description字段缺少触发条件
**解决方案**：
- 在description中包含用户可能说的具体短语
- 明确技能的使用场景和触发条件
- 遵循渐进式披露原则，保持frontmatter简洁

## 许可声明

本规范文件（output-spec.md）采用 **CC BY-SA 4.0** 许可。详见 `references/license.md` 了解律锥·legalskill 的双层许可体系。

---

*技能版本：1.1.0 | 作者：律锥·legalskill | 文档许可：CC BY-SA 4.0*