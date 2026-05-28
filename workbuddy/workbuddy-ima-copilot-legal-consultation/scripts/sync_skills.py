#!/usr/bin/env python3
"""
技能副本同步检查脚本

基于 `D:\\github\\skills-mapping.json` 定义的映射关系，
对比源技能目录与 WorkBuddy 内嵌副本的一致性。

用法：
    python sync_skills.py              # 仅检查，打印差异报告
    python sync_skills.py --sync       # 检查并自动同步（源 → 副本）
    python sync_skills.py --json       # JSON 格式输出（供脚本消费）
"""

import sys
import json
import hashlib
import os
import shutil
from pathlib import Path
from typing import Optional

# Windows 控制台 GBK 编码兼容：强制 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# WorkBuddy 副本保留的元数据文件（不在源目录中，sync 不删除）
PRESERVED_FILES = {"_meta.json", "_skillhub_meta.json"}

# 映射表路径
MAPPING_FILE = Path("D:/github/skills-mapping.json")


def hash_file(path: Path) -> str:
    """计算文件 MD5 hash。"""
    h = hashlib.md5()
    h.update(path.read_bytes())
    return h.hexdigest()


def scan_files(root: Path, exclude: set = None) -> dict:
    """扫描目录下所有文件，返回 {相对路径: md5}。"""
    exclude = exclude or set()
    result = {}
    if not root.exists():
        return result
    for f in root.rglob("*"):
        if f.is_file() and f.name not in exclude:
            rel = f.relative_to(root).as_posix()
            result[rel] = hash_file(f)
    return result


def compare(source: Path, target: Path) -> dict:
    """
    对比源目录与副本目录。
    返回: {status, missing, extra, changed, ok, details}
    """
    src_files = scan_files(source)
    tgt_files_full = scan_files(target)  # 不含 PRESERVED_FILES
    tgt_all = {f.relative_to(target).as_posix() for f in target.rglob("*")
               if f.is_file()}

    # 判断专属保留文件
    preserved_in_target = {f for f in tgt_all if f.split("/")[-1] in PRESERVED_FILES}

    missing = []
    extra = []
    changed = []
    ok = []

    for rel_path, src_hash in src_files.items():
        if rel_path in tgt_files_full:
            if tgt_files_full[rel_path] == src_hash:
                ok.append(rel_path)
            else:
                changed.append(rel_path)
        else:
            missing.append(rel_path)

    for rel_path in tgt_files_full:
        if rel_path not in src_files:
            # 如果后缀是 PRESERVED_FILES 中的文件名，跳过
            if rel_path.split("/")[-1] in PRESERVED_FILES:
                continue
            extra.append(rel_path)

    status = "一致"
    if missing or extra or changed:
        status = "不一致"

    return {
        "status": status,
        "source": str(source),
        "target": str(target),
        "missing": missing,
        "extra": extra,
        "changed": changed,
        "ok": ok,
        "preserved": list(preserved_in_target),
        "total_source": len(src_files),
        "total_target": len(tgt_files_full),
    }


def sync(source: Path, target: Path, dry_run: bool = False) -> list:
    """同步源目录到副本目录。返回操作列表。"""
    actions = []
    if not source.exists():
        return [{"action": "error", "msg": f"源目录不存在: {source}"}]
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)
        actions.append({"action": "mkdir", "path": str(target)})

    src_files = scan_files(source)
    tgt_files_full = scan_files(target)
    tgt_all = {f.relative_to(target).as_posix() for f in target.rglob("*")
               if f.is_file()}

    # 复制新增/变更文件
    for rel_path, src_hash in src_files.items():
        src_file = source / rel_path
        tgt_file = target / rel_path
        if rel_path not in tgt_files_full or tgt_files_full[rel_path] != src_hash:
            if not dry_run:
                tgt_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, tgt_file)
            actions.append({"action": "copy" if not dry_run else "would_copy",
                            "file": rel_path})

    # 删除副本多余文件（保留 PRESERVED_FILES）
    for rel_path in tgt_files_full:
        if rel_path not in src_files:
            if rel_path.split("/")[-1] in PRESERVED_FILES:
                continue
            tgt_file = target / rel_path
            if not dry_run:
                tgt_file.unlink()
            actions.append({"action": "delete" if not dry_run else "would_delete",
                            "file": rel_path})

    # 清理空目录
    if not dry_run:
        for root, dirs, files in os.walk(str(target), topdown=False):
            for d in dirs:
                dpath = Path(root) / d
                try:
                    dpath.rmdir()
                except OSError:
                    pass

    return actions


def main():
    dry_run = True
    json_out = False

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--sync":
            dry_run = False
        elif sys.argv[i] == "--json":
            json_out = True
        i += 1

    # 读取映射表
    mapping_path = Path(os.environ.get("SKILLS_MAPPING_FILE", MAPPING_FILE))
    if not mapping_path.exists():
        print(f"❌ 映射表不存在: {mapping_path}", file=sys.stderr)
        return 1

    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    workspace = mapping_path.parent
    results = {}

    for agent_name, agent_info in mapping.get("agents", {}).items():
        display = agent_info.get("displayName", agent_name)
        results[agent_name] = {"displayName": display, "skills": []}

        for skill in agent_info.get("skills", []):
            source_path = workspace / skill["source"]
            target_path = workspace / skill["target"]

            if dry_run:
                result = compare(source_path, target_path)
            else:
                result = {
                    "status": "sync",
                    "source": str(source_path),
                    "target": str(target_path),
                    "actions": sync(source_path, target_path, dry_run=False),
                }

            results[agent_name]["skills"].append({
                "name": skill["name"],
                "version": skill["version"],
                "result": result,
            })

    if json_out:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        has_issues = False
        for agent_name, data in results.items():
            print(f"\n{'=' * 60}")
            print(f"📦 Agent: {data['displayName']} ({agent_name})")
            print(f"{'=' * 60}")

            for s in data["skills"]:
                r = s["result"]
                print(f"\n  技能: {s['name']} v{s['version']}")

                if dry_run:
                    print(f"  状态: {r['status']}")
                    print(f"  源: {r['source']}")
                    print(f"  副本: {r['target']}")

                    if r["missing"]:
                        has_issues = True
                        print(f"  ❌ 副本缺少 ({len(r['missing'])}):")
                        for f_path in r["missing"]:
                            print(f"     - {f_path}")

                    if r["changed"]:
                        has_issues = True
                        print(f"  ⚠️  内容不一致 ({len(r['changed'])}):")
                        for f_path in r["changed"]:
                            print(f"     - {f_path}")

                    if r["extra"]:
                        has_issues = True
                        print(f"  ➕ 副本多余 ({len(r['extra'])}):")
                        for f_path in r["extra"]:
                            print(f"     - {f_path}")

                    if r["preserved"]:
                        print(f"  🔒 保留文件 ({len(r['preserved'])}):")
                        for f_path in r["preserved"]:
                            print(f"     - {f_path}")

                    if r["ok"]:
                        print(f"  ✅ 一致: {r['total_source'] - len(r['changed'])}/{r['total_source']} 个文件")
                else:
                    actions = r.get("actions", [])
                    if actions:
                        print(f"  操作: {len(actions)} 项")
                        for a in actions:
                            icon = "📝" if a["action"] == "copy" else "🗑️ " if a["action"] == "delete" else "📁"
                            print(f"     {icon} {a['action']}: {a.get('file', a.get('path', ''))}")
                    else:
                        print(f"  ✅ 已是最新，无需同步")

        if dry_run and has_issues:
            print(f"\n💡 运行 python sync_skills.py --sync 可自动同步")

    return 0 if (dry_run or not json_out) else 0


if __name__ == "__main__":
    sys.exit(main())
