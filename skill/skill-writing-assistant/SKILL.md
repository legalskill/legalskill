---
name: skill-writing-assistant
description: 指导用户编写新的标准技能或修改现有技能。提供从规划、设计、编写到测试、迭代和分发的完整指南，遵循 agentskills.io 标准技能规范。包含最佳实践、示例、模板和故障排除。当用户询问"如何创建skill"、"如何修改skill"、"skill编写指南"、"skill最佳实践"或需要技能开发帮助时使用。当用户要求输出标准格式的技能Markdown文件时，按 agentskills.io 规范格式输出。当用户要求"单文件模式"时，生成合并的单个Markdown文件。
license: CC BY-SA 4.0
metadata:
  author: 律锥·legalskill
  version: "1.1.0"
  category: development
  tags: [skill-creation, documentation, best-practices]
  documentation: https://agentskills.io/
---

# 技能编写与修改助手

本技能提供创建和修改标准技能的完整指南。遵循渐进式披露原则：本文件包含核心指令，详细文档请参考`references/`目录中的文件。

## 概述

技能（Skill）是包含指令的文件夹，用于指导AI处理特定任务或工作流。本技能将指导您：
1. 创建全新的技能
2. 修改和优化现有技能
3. 遵循最佳实践和规范
4. 输出符合规范的标准技能Markdown文件

## 快速开始

当您需要创建或修改技能时，请告知我您的具体需求。我将根据以下指南提供帮助：

- **创建新技能**：请参考 `references/creating-skills.md` 获取详细步骤。
- **修改现有技能**：请参考 `references/modifying-skills.md` 获取诊断和改进方法。
- **输出标准文件**：当您要求"输出技能文件"或"生成标准格式"时，我会按照 `references/output-spec.md` 中的规范生成完整的技能Markdown文件。
- **单文件模式**：如果您需要单个合并的Markdown文件（包含所有内容），请说明"单文件模式"或"输出单个文件"。我将生成一个包含全部内容的单一Markdown文件，便于您查看或分发。

## 核心工作流

### 1. 确定需求
- 明确技能的目标用户和用例
- 选择适当的技能类别（文档创建、工作流自动化、MCP增强）

### 2. 设计结构
- 使用kebab-case命名技能文件夹
- 创建标准的目录结构（SKILL.md、skill.yaml、references/、scripts/、assets/）
- 编写有效的YAML frontmatter（名称和描述）
- 编写 skill.yaml 机器可读元数据（与 frontmatter 保持一致）

### 3. 编写内容
- 在SKILL.md中提供清晰、可操作的指令
- 将详细文档放在references/目录中
- 嵌入错误处理和示例

### 4. 测试与迭代
- 测试技能触发和功能
- 收集反馈并优化描述和指令

## 使用详细指南

本技能遵循渐进式披露原则。默认情况下，我只加载核心指令。当您需要详细了解某个主题时，我会引导您查阅相应的参考资料：

- **创建技能详细步骤**：`references/creating-skills.md`
- **修改技能详细步骤**：`references/modifying-skills.md`
- **输出规范**：`references/output-spec.md`
- **完整示例**：`references/examples.md`
- **故障排除**：`references/troubleshooting.md`
- **资源链接**：`references/resources.md`
- **快速检查清单**：`references/checklist.md`

## 单文件模式

如果您希望获得包含所有内容的单个Markdown文件（例如用于离线阅读或分发），请明确要求"单文件模式"。在该模式下，我将生成一个合并的Markdown文件，包含所有参考资料的内容，并保持原有结构。

### 文件大小约束

单文件模式生成的合并文件应遵守以下约束，超出时需精简内容或拆分：

| 指标 | 建议上限 | 说明 |
|:-----|:--------|:------|
| 总字符数 | ≤ 50,000 字符 | 超出后影响加载性能 |
| 总行数 | ≤ 1,000 行 | 超出后影响阅读体验 |

生成完成后应动态检测文件大小，超限时提示用户考虑精简或拆分。

您也可以使用 `scripts/merge_single_file.py` 脚本生成单文件版本。运行以下命令：
## 重要提示

- 技能文件夹必须命名为kebab-case（例如 `my-skill-name`）。
- SKILL.md 必须精确使用此文件名（区分大小写）。
- 描述字段必须包含技能功能和触发条件。
- 避免在frontmatter中使用XML尖括号（< >）。
- 保持SKILL.md简洁，将详细内容移至references/目录。
- **name: 冒号后必须带空格**（`name: my-skill` 而非 `name:my-skill`），YAML 严格解析器不接受压缩格式。
- **compatibility 字段只放在 skill.yaml**，不要放在 SKILL.md 的 YAML frontmatter 中——平台校验时 frontmatter 不认识该字段。
- **删除技能文件夹中的空目录**（如空的 adapters/），校验时会识别为多余内容产生警告。
- **README.md 必须同步**：发布前检查 README 中的版本号、目录结构、references 列表与实际文件一致。

## 获取帮助

如果您在使用本技能时遇到问题，请参考 `references/troubleshooting.md` 或询问我具体问题。

---

> **免责声明**：本技能仅提供技能编写指导与模板参考，生成内容的法律合规性由使用者自行判断。严禁将涉密信息输入公域大模型。

---

*技能版本：1.1.0 | 作者：律锥·legalskill | 文档许可：CC BY-SA 4.0*