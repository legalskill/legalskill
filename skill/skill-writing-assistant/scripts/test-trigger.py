#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能触发测试脚本

功能：模拟用户查询，测试技能是否在正确时机触发
使用方式：python test-trigger.py --skill /path/to/skill-folder
"""

import os
import sys
import argparse
import yaml
import re

def extract_trigger_phrases(skill_path):
    """从SKILL.md中提取触发短语"""
    skill_file = os.path.join(skill_path, "SKILL.md")
    
    if not os.path.exists(skill_file):
        print(f"错误：未找到SKILL.md文件 {skill_file}")
        return []
    
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取description字段
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        print("错误：未找到有效的YAML frontmatter")
        return []
    
    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        print(f"YAML解析错误: {e}")
        return []
    
    description = frontmatter.get('description', '')
    
    # 从description中提取触发短语
    # 查找引号内的内容
    trigger_patterns = [
        r'当用户提及"(.*?)"时触发',
        r'当用户说"(.*?)"时使用',
        r'当用户询问"(.*?)"时使用',
        r'当用户提到"(.*?)"时使用',
        r'当用户说"(.*?)"时触发',
        r'触发条件.*?"(.*?)"'
    ]
    
    triggers = []
    for pattern in trigger_patterns:
        matches = re.findall(pattern, description)
        triggers.extend(matches)
    
    # 如果没有找到明确的触发短语，尝试从description中提取关键词
    if not triggers:
        # 查找包含"生成"、"制作"、"更新"等动词的短语
        keyword_pattern = r'[生制创更提]"([^"]+)"'
        matches = re.findall(keyword_pattern, description)
        triggers.extend(matches)
    
    return triggers

def generate_test_queries(triggers):
    """基于触发短语生成测试查询"""
    test_queries = []
    
    # 直接使用触发短语
    test_queries.extend(triggers)
    
    # 生成转述查询
    for trigger in triggers:
        # 添加礼貌用语变体
        test_queries.append(f"请{trigger}")
        test_queries.append(f"帮我{trigger}")
        test_queries.append(f"需要{trigger}")
        
        # 添加时间变体
        test_queries.append(f"今天{trigger}")
        test_queries.append(f"现在{trigger}")
        test_queries.append(f"明天{trigger}")
    
    # 去重
    unique_queries = list(set(test_queries))
    
    return unique_queries

def analyze_coverage(triggers, queries):
    """分析查询覆盖率"""
    if not triggers:
        return {"coverage": 0, "analysis": "未找到明确的触发短语"}
    
    coverage_data = {}
    
    for trigger in triggers:
        coverage_data[trigger] = []
        for query in queries:
            # 检查查询是否包含触发短语
            trigger_words = set(trigger.lower().split())
            query_words = set(query.lower().split())
            
            # 计算重叠度
            overlap = len(trigger_words & query_words) / len(trigger_words)
            if overlap > 0.5:  # 超过50%重叠
                coverage_data[trigger].append((query, overlap))
    
    return coverage_data

def print_test_plan(triggers, queries, skill_name):
    """打印测试计划"""
    print("="*60)
    print(f"技能触发测试计划 - {skill_name}")
    print("="*60)
    
    print(f"\n📋 找到 {len(triggers)} 个触发短语：")
    for i, trigger in enumerate(triggers, 1):
        print(f"  {i}. {trigger}")
    
    print(f"\n🔍 生成 {len(queries)} 个测试查询：")
    print("\n  应该触发的查询：")
    for i, query in enumerate(queries[:10], 1):  # 显示前10个
        print(f"  {i}. \"{query}\"")
    
    if len(queries) > 10:
        print(f"  ... 还有 {len(queries)-10} 个查询")
    
    print("\n🚫 不应该触发的查询示例：")
    unrelated_queries = [
        "今天的天气怎么样？",
        "帮我写一个Python函数",
        "创建电子表格",
        "旧金山有什么好玩的？",
        "翻译这段文字",
        "计算数学公式",
        "解释量子物理",
        "推荐一本书",
        "今天的历史事件",
        "健康的饮食建议"
    ]
    
    for i, query in enumerate(unrelated_queries, 1):
        print(f"  {i}. \"{query}\"")
    
    print("\n📊 测试方法：")
    print("  1. 逐一测试「应该触发的查询」，确认技能正常加载")
    print("  2. 测试「不应该触发的查询」，确认技能不触发")
    print("  3. 测试转述和变体查询，确保触发逻辑健壮")
    
    print("\n✅ 成功标准：")
    print("  - 所有「应该触发的查询」正确触发技能（≥90%）")
    print("  - 所有「不应该触发的查询」不触发技能（≥95%）")
    print("  - 常见转述能够正确触发")
    
    print("\n💡 提示：")
    print("  - 记录失败的查询，用于改进description字段")
    print("  - 特别注意模糊查询的边界情况")
    print("  - 考虑不同用户的表达习惯")

def main():
    parser = argparse.ArgumentParser(description="技能触发测试生成器")
    parser.add_argument("--skill", required=True, help="技能文件夹路径")
    parser.add_argument("--output", help="输出测试计划到文件")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.skill):
        print(f"错误：技能路径不存在 {args.skill}")
        sys.exit(1)
    
    # 获取技能名称
    skill_name = os.path.basename(args.skill)
    
    # 提取触发短语
    triggers = extract_trigger_phrases(args.skill)
    
    if not triggers:
        print("⚠️  警告：未找到明确的触发短语")
        print("\n建议检查description字段是否包含：")
        print("  - 用户实际会说的具体短语（用引号括起来）")
        print("  - 如：当用户说\"生成报告\"或\"创建文档\"时使用")
        print("  - 明确的触发条件说明")
        
        # 尝试从文件夹名推测
        folder_triggers = skill_name.replace('-', ' ')
        triggers = [folder_triggers]
        print(f"\n使用文件夹名作为替代触发短语: \"{folder_triggers}\"")
    
    # 生成测试查询
    queries = generate_test_queries(triggers)
    
    # 打印测试计划
    print_test_plan(triggers, queries, skill_name)
    
    # 保存到文件（如果需要）
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            import io
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                print_test_plan(triggers, queries, skill_name)
            
            f.write(output_buffer.getvalue())
        print(f"\n💾 测试计划已保存到 {args.output}")
    
    print("\n" + "="*60)
    print("✨ 测试计划生成完成！")
    print("="*60)

if __name__ == "__main__":
    main()