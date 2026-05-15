## 快速检查清单

在分发技能前使用此检查清单：

### 开发前
- [ ] 确定了2-3个具体用例
- [ ] 确定了工具（内置或MCP）
- [ ] 审查了本指南和示例技能
- [ ] 规划了文件夹结构

### 开发期间
- [ ] 文件夹命名为kebab-case
- [ ] SKILL.md文件存在（精确拼写）
- [ ] skill.yaml 存在（与 SKILL.md 同级）
- [ ] skill.yaml name/version 与 SKILL.md frontmatter 一致
- [ ] skill.yaml triggers 列表已填写
- [ ] skill.yaml not_for 至少 1 项
- [ ] skill.yaml references 完整列出 references/ 下所有 .md
- [ ] YAML frontmatter有`---`分隔符
- [ ] name字段：kebab-case，无空格，无大写
- [ ] **name: 冒号后必须带空格**（如 `name: my-skill`，不要写成 `name:my-skill`）
- [ ] **compatibility 只放在 skill.yaml，不放 SKILL.md frontmatter**
- [ ] description包含功能和何时使用
- [ ] license字段：CC BY-SA 4.0（文档许可）
- [ ] metadata.author：律锥·legalskill
- [ ] metadata.version：语义化版本号
- [ ] metadata.category：技能分类
- [ ] 若含代码，scripts/src/ 文件头部有 SPDX 标识
- [ ] **检查并删除技能文件夹中的空目录**
- [ ] 任何地方都没有XML标签（`< >`）
- [ ] 指令清晰且可操作
- [ ] 包含错误处理
- [ ] 提供了示例
- [ ] 清晰链接了参考资料

### 上传前
- [ ] SKILL.md 末尾包含免责声明（法律类/通用类）
- [ ] **README.md 中的目录结构、版本号、references 列表与实际文件结构一致**
- [ ] 在明显任务上测试了触发
- [ ] 在转述请求上测试了触发
- [ ] 验证了在不相关主题上不触发
- [ ] 功能测试通过
- [ ] 工具集成有效（如果适用）
- [ ] 压缩为.zip文件

### 上传后
- [ ] 在实际对话中测试
- [ ] 监控触发不足/过度触发
- [ ] 收集用户反馈
- [ ] 迭代描述和指令
- [ ] 更新metadata中的版本

---

**最后提示**：技能是活文档。随着您获得更多用户反馈和使用数据，定期更新和改进您的技能。从简单开始，迭代改进，并始终以用户结果为中心。

如需进一步帮助，请使用skill-creator技能或参考官方文档。

---