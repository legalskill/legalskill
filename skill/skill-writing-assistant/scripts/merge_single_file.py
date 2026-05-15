#!/usr/bin/env python3
"""
合并技能的所有文件为单个Markdown文件。
运行: python merge_single_file.py > skill-writing-assistant-complete.md
"""

import os
import sys

def set_stdout_encoding():
    """确保标准输出使用UTF-8编码"""
    try:
        # Python 3.7+
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # 旧版本Python，尝试使用io.TextIOWrapper
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass  # 忽略错误，继续执行

def read_file(path):
    """读取文件内容，返回字符串"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"无法读取文件 {path}: {e}", file=sys.stderr)
        return ""

def main():
    set_stdout_encoding()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 要合并的文件顺序
    files = [
        os.path.join(base_dir, "SKILL.md"),
        os.path.join(base_dir, "references", "creating-skills.md"),
        os.path.join(base_dir, "references", "modifying-skills.md"),
        os.path.join(base_dir, "references", "output-spec.md"),
        os.path.join(base_dir, "references", "examples.md"),
        os.path.join(base_dir, "references", "troubleshooting.md"),
        os.path.join(base_dir, "references", "resources.md"),
        os.path.join(base_dir, "references", "checklist.md"),
        os.path.join(base_dir, "references", "license.md"),
    ]
    
    output_lines = []
    
    for file_path in files:
        if os.path.exists(file_path):
            content = read_file(file_path)
            if content:
                # 添加文件分隔注释
                output_lines.append(f"\n\n<!-- 文件: {os.path.basename(file_path)} -->\n\n")
                output_lines.append(content)
    
    # 输出到标准输出
    sys.stdout.write(''.join(output_lines))

if __name__ == "__main__":
    main()