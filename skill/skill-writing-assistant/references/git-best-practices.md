# Git 最佳实践指南

## 概述
本文件提供使用Git进行版本控制的最佳实践，特别适合在团队中使用。

## 分支策略

### Git Flow模型
```
main
├── develop
│   ├── feature/feature-name
│   ├── release/release-version
│   └── hotfix/hotfix-name
```

### 分支命名规范
- **feature/** - 新功能开发，如 `feature/user-authentication`
- **bugfix/** - 修复bug，如 `bugfix/login-error`
- **hotfix/** - 紧急修复生产问题，如 `hotfix/security-patch`
- **release/** - 发布准备，如 `release/v1.2.0`

## 提交规范

### 提交消息格式
```
<类型>: <简短描述>

<详细描述>

<可选脚注>
```

### 提交类型
- **feat** - 新功能
- **fix** - 修复bug
- **docs** - 文档更新
- **style** - 代码格式调整（不影响功能）
- **refactor** - 代码重构
- **test** - 测试相关
- **chore** - 构建过程或辅助工具的变动

### 示例
```
feat: 添加用户登录功能

- 实现基于JWT的认证系统
- 添加登录表单组件
- 集成后端API

Closes #123
```

## 工作流最佳实践

### 1. 原子提交
- 每个提交只完成一个小的、独立的功能
- 避免多个不相关的更改混在一个提交中

### 2. 频繁提交
- 每完成一个小功能就提交一次
- 保持提交历史清晰

### 3. 描述性提交消息
- 第一行不超过50个字符
- 详细描述问题原因和解决方案
- 使用现在时态

### 4. 代码审查
- 提交前进行自我审查
- 使用Pull Request进行团队代码审查
- 至少需要一位同事批准

## 高级技巧

### 交互式变基
```bash
# 整理最近3个提交
git rebase -i HEAD~3

# 常用命令
# p, pick = 使用提交
# r, reword = 使用提交，但修改提交消息
# e, edit = 使用提交，但暂停修改
# s, squash = 使用提交，但合并到前一个提交
# f, fixup = 类似squash，但丢弃提交消息
# d, drop = 移除提交
```

### 储藏更改
```bash
# 储藏当前更改
git stash

# 列出储藏
git stash list

# 恢复储藏
git stash pop

# 应用特定储藏
git stash apply stash@{0}
```

## 常见问题解决

### 1. 提交到错误分支
```bash
# 在当前分支创建新分支保存更改
git branch temp-branch

# 重置当前分支到之前状态
git reset --hard HEAD~1

# 切换到正确分支
git checkout correct-branch

# 合并临时分支的更改
git merge temp-branch
```

### 2. 撤销已提交的更改
```bash
# 撤销最近一次提交，保留更改
git reset HEAD~1

# 撤销最近一次提交，不保留更改
git reset --hard HEAD~1

# 创建撤销提交
git revert <commit-hash>
```

## 工具推荐

### GUI工具
- **GitHub Desktop** - 初学者友好
- **SourceTree** - 功能丰富
- **GitKraken** - 专业团队

### 命令行工具
- **tig** - 文本界面Git浏览器
- **lazygit** - 终端Git界面
- **diff-so-fancy** - 美化Git差异输出