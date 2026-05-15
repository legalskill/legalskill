#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能数据验证脚本

功能：验证Claude Skill的文件结构和内容格式
使用方式：python validate.py --path /path/to/skill-folder
"""

import os
import sys
import argparse
import re
import yaml
import json
from pathlib import Path

def check_folder_name(folder_path):
    """检查文件夹名是否符合kebab-case"""
    folder_name = os.path.basename(folder_path)
    
    # kebab-case检查：只允许小写字母、数字和连字符
    pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
    if not re.match(pattern, folder_name):
        return False, f"文件夹名不符合kebab-case: {folder_name}"
    
    return True, f"文件夹名符合kebab-case: {folder_name}"

def check_skill_file(folder_path):
    """检查SKILL.md文件是否存在且格式正确"""
    skill_path = os.path.join(folder_path, "SKILL.md")
    
    if not os.path.exists(skill_path):
        return False, "未找到SKILL.md文件"
    
    # 检查文件大小
    file_size = os.path.getsize(skill_path)
    if file_size > 500000:  # 约500KB
        return False, f"SKILL.md文件过大: {file_size}字节"
    
    # 读取文件内容
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return False, "SKILL.md文件编码不正确，应为UTF-8"
    
    # 检查YAML frontmatter
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        return False, "未找到有效的YAML frontmatter"
    
    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        return False, f"YAML frontmatter解析错误: {e}"
    
    # 检查必需字段
    required_fields = ['name', 'description']
    missing_fields = []
    for field in required_fields:
        if field not in frontmatter:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必需字段: {', '.join(missing_fields)}"
    
    # 检查name字段格式
    name = frontmatter.get('name', '')
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        return False, f"name字段不符合kebab-case: {name}"
    
    # 检查description长度
    description = frontmatter.get('description', '')
    if len(description) > 1024:
        return False, f"description字段过长: {len(description)}字符（最大1024）"
    
    # 检查XML标签
    if '<' in description or '>' in description:
        return False, "description字段包含XML标签（< 或 >），这是不允许的"
    
    return True, "SKILL.md文件格式正确"

def check_references_directory(folder_path):
    """检查references目录结构"""
    ref_path = os.path.join(folder_path, "references")
    
    if os.path.exists(ref_path):
        # 检查是否包含不必要的README.md
        readme_path = os.path.join(ref_path, "README.md")
        if os.path.exists(readme_path):
            return False, "references目录中包含README.md，应将其内容移至SKILL.md"
    
    return True, "references目录检查通过"

def check_assets_directory(folder_path):
    """检查assets目录"""
    assets_path = os.path.join(folder_path, "assets")
    
    if os.path.exists(assets_path):
        # 检查常见文件类型
        allowed_extensions = {'.md', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.ttf', '.woff', '.woff2'}
        for root, dirs, files in os.walk(assets_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in allowed_extensions:
                    return False, f"assets目录包含不支持的文件类型: {file}"
    
    return True, "assets目录检查通过"

def main():
    parser = argparse.ArgumentParser(description="验证Claude Skill结构")
    parser.add_argument("--path", required=True, help="技能文件夹路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"错误：路径不存在 {args.path}")
        sys.exit(1)
    
    if not os.path.isdir(args.path):
        print(f"错误：{args.path} 不是目录")
        sys.exit(1)
    
    checks = [
        ("文件夹名称", check_folder_name),
        ("SKILL.md文件", check_skill_file),
        ("references目录", check_references_directory),
        ("assets目录", check_assets_directory)
    ]
    
    all_passed = True
    results = []
    
    for check_name, check_func in checks:
        passed, message = check_func(args.path)
        results.append((check_name, passed, message))
        
        if not passed:
            all_passed = False
        
        if args.verbose or not passed:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}: {message}")
    
    print("\n" + "="*50)
    
    if all_passed:
        print("✅ 所有检查通过！技能结构完整且符合规范。")
        print("\n建议下一步：")
        print("1. 运行触发测试：测试技能在相关查询时是否正常加载")
        print("2. 运行功能测试：验证技能产生正确的输出")
        print("3. 打包为ZIP文件：压缩整个技能文件夹")
        print("4. 上传到Claude: 设置 > 能力 > 技能 > 上传技能")
    else:
        print("❌ 发现以下问题需要修复：")
        for check_name, passed, message in results:
            if not passed:
                print(f"  - {check_name}: {message}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())