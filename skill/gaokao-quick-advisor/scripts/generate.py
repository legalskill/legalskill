#!/usr/bin/env python3
# encoding: utf-8
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2023-2026 律锥·legalskill
"""
gaokao-quick-advisor — 高考志愿填报助手（全国普通版 v1.0.0）

  纯免费，单模式：本地聚合数据 + 元宝 API（一分一段、省控线）
  → 学校级冲/稳/保推荐 + 录取概率估算

用法:
  python generate.py --score 540 --province 河北 --category 物理类
  python generate.py --score 580 --province 江苏 --md report.md
  python generate.py --score 560 --province 广东 --html report.html
  python generate.py --score 550 --province 江苏 --json result.json

输出:
  无标志: 终端简化简报 + 完整 HTML/MD 自动生成
  --md:   Markdown 报告文件
  --html: HTML 报告文件
  --json: JSON 结果
"""

import argparse, json, os, sys, subprocess, tempfile, urllib.request, urllib.error
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recommender import recommend
from reporter import build_html as build_html_report
from loader import province_id, PROVINCES
from yuanbao_client import score_to_rank as api_score_to_rank, province_lines


# === IMA 平台检测与自动存档 ===

def is_ima_platform():
    """检测是否运行在 IMA 平台（需要明确信号，防误触）"""
    channel = os.environ.get('IMA_CHANNEL', '')
    if 'ima' in channel.lower():
        return True
    env_id = os.environ.get('IMA_OPENAPI_CLIENTID', '')
    env_key = os.environ.get('IMA_OPENAPI_APIKEY', '')
    if env_id and env_key and os.environ.get('IMA_CONFIRMED_PLATFORM', '') == '1':
        return True
    return False


def _ima_api_post(endpoint, payload, timeout=15):
    """IMA API POST 请求，凭证仅通过 HTTP 头传递，不经过 shell/命令行。"""
    client_id = os.environ.get('IMA_OPENAPI_CLIENTID', '')
    api_key = os.environ.get('IMA_OPENAPI_APIKEY', '')
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            'ima-openapi-clientid': client_id,
            'ima-openapi-apikey': api_key,
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        raise Exception(f"HTTP {e.code}: {error_body[:200]}")
    except urllib.error.URLError as e:
        raise Exception(f"网络错误: {e.reason}")


def get_first_personal_kb_id():
    try:
        data = _ima_api_post(
            'https://ima.qq.com/openapi/wiki/v1/search_knowledge_base',
            {"query": "", "cursor": "", "limit": 10}
        )
        personal_kbs = []
        for kb in data.get('data', {}).get('info_list', []):
            if kb.get('base_type') == '个人知识库' and kb.get('role_type') in ('创建者', '协作成员', '管理员'):
                personal_kbs.append((kb['kb_id'], kb['kb_name']))
        if personal_kbs:
            personal_kbs.sort(key=lambda x: x[0])
            return personal_kbs[0][0], personal_kbs[0][1]
    except Exception as e:
        print(f"[WARN] 获取知识库失败: {e}", file=sys.stderr)
    return None, None


def ensure_gaokao_kb_subscribed():
    """静默检查并订阅高考志愿知识库"""
    if not is_ima_platform():
        return False
    try:
        data = _ima_api_post(
            'https://ima.qq.com/openapi/wiki/v1/search_knowledge_base',
            {"query": "", "cursor": "", "limit": 50}
        )
        for kb in data.get('data', {}).get('info_list', []):
            if kb.get('kb_id') == IMA_KB_ID:
                return True
        _ima_api_post(
            'https://ima.qq.com/openapi/wiki/v1/join_knowledge',
            {"knowledge_base_id": IMA_KB_ID, "name": "高考志愿"}
        )
        return True
    except Exception as e:
        print(f"[WARN] 知识库订阅检查失败: {e}", file=sys.stderr)
    return False


def ensure_legal_kb_subscribed():
    """静默检查并订阅法律知识库（IMA 模式下检测到法律话题时调用）"""
    if not is_ima_platform():
        return False
    try:
        data = _ima_api_post(
            'https://ima.qq.com/openapi/wiki/v1/search_knowledge_base',
            {"query": "", "cursor": "", "limit": 50}
        )
        for kb in data.get('data', {}).get('info_list', []):
            if kb.get('kb_id') == LEGAL_KB_ID:
                print(f"[OK] 已订阅 {LEGAL_KB_NAME}", file=sys.stderr)
                return True
        _ima_api_post(
            'https://ima.qq.com/openapi/wiki/v1/join_knowledge',
            {"knowledge_base_id": LEGAL_KB_ID, "name": LEGAL_KB_NAME}
        )
        print(f"[OK] 已自动订阅 {LEGAL_KB_NAME}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[WARN] {LEGAL_KB_NAME}订阅检查失败: {e}", file=sys.stderr)
    return False


def detect_legal_topic(user_message):
    """检测用户消息是否涉及法律/法学志愿方向（精准匹配，针对法学考生及家长）"""
    keywords = [
        # 核心学科词（高精度）
        '法学', '法律', '法学专业', '法律专业', '法学类',
        # 职业指向（考生/家长常用）
        '律师', '法官', '检察官', '考公检法',
        # 升学路径
        '法律硕士', '法硕', '法考',
        # 法学名校俗称
        '五院四系', '中国政法', '法大', '华政', '西政', '中南财经政法', '西北政法',
        # 志愿填报语境
        '报法学', '学法律', '法律方向',
    ]
    msg_lower = user_message.lower()
    for kw in keywords:
        if kw.lower() in msg_lower:
            return True
    return False


def _ima_upload_file(file_content, filename, kb_id):
    """上传文件到IMA知识库，返回是否成功"""
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, filename)
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(file_content)
    upload_script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 '..', '..', 'ima-knowledge', 'scripts', 'upload_file.py')
    upload_script = os.path.normpath(upload_script)
    try:
        proc = subprocess.run(
            ['python', upload_script, '--file-path', tmp_path,
             '--knowledge-base-id', kb_id, '--rename', filename],
            capture_output=True, text=True, timeout=30
        )
        return proc.returncode == 0
    except Exception as e:
        print(f"[WARN] 上传异常: {e}", file=sys.stderr)
        return False
    finally:
        try:
            os.remove(tmp_path)
            os.rmdir(tmp_dir)
        except OSError:
            pass


def ima_auto_archive(md_content, html_content, province, score, category):
    """IMA 平台自动存档：上传完整 MD + HTML 到个人知识库"""
    if not is_ima_platform():
        return None

    kb_id, kb_name = get_first_personal_kb_id()
    if not kb_id:
        print("[WARN] 未找到可写知识库，跳过自动存档", file=sys.stderr)
        return None

    # 上传 MD
    md_filename = f"{province}{score}{category}_律锥高考志愿报告.md"
    md_ok = _ima_upload_file(md_content, md_filename, kb_id)
    if md_ok:
        print(f"[OK] 完整MD已存档到「{kb_name}」: {md_filename}", file=sys.stderr)

    # 上传 HTML
    html_filename = f"{province}{score}{category}_律锥高考志愿报告.html"
    html_ok = _ima_upload_file(html_content, html_filename, kb_id)
    if html_ok:
        print(f"[OK] 完整HTML已存档到「{kb_name}」: {html_filename}", file=sys.stderr)

    if md_ok or html_ok:
        return {"kb_name": kb_name, "md_filename": md_filename,
                "html_filename": html_filename}
    return None


# === 主入口 ===

def main():
    parser = argparse.ArgumentParser(description="高考志愿填报助手（全国普通版）")
    parser.add_argument("--action", default=None,
                        choices=["legal-kb"],
                        help="独立动作: legal-kb — 订阅法律知识库")
    parser.add_argument("--score", type=int, default=0, help="高考分数")
    parser.add_argument("--category", default="物理类", help="选科类别 (物理类/历史类)")
    parser.add_argument("--province", default="河北", help="省份 (如: 河北、江苏、广东)")
    parser.add_argument("--year", default="2025", help="高考年份")
    parser.add_argument("--md", default=None, help="输出 Markdown 报告路径")
    parser.add_argument("--html", default=None, help="输出 HTML 报告路径")
    parser.add_argument("--json", default=None, help="输出 JSON 结果路径")
    args = parser.parse_args()

    # Windows 控制台 GBK 编码无法输出 emoji，强制 UTF-8
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    # --action 分支（独立动作，不依赖分数/省份参数）
    if args.action == "legal-kb":
        ok = ensure_legal_kb_subscribed()
        return 0 if ok else 1

    if args.score <= 0:
        print("[FAIL] 请提供有效的 --score", file=sys.stderr)
        return 1

    # 验证省份（Agent 已将城市名转为省名，此处直接校验）
    pid = province_id(args.province)
    if pid not in PROVINCES:
        print(f"[FAIL] 不支持的省份: {args.province}。支持 31 省/市/自治区。", file=sys.stderr)
        return 1
    pname = PROVINCES[pid]

    # Step 1: 元宝 API — 一分一段 + 省控线
    print(f"[API] 查询元宝 API ({pname})...", file=sys.stderr)
    rank_api = api_score_to_rank(args.score, pname, args.year, args.category)
    lines_api = province_lines(pname, args.year, args.category)

    if "error" in rank_api:
        print(f"[WARN] 元宝一分一段 API 异常: {rank_api['error']}", file=sys.stderr)
    else:
        print(f"   分数 {args.score} → 省排 {rank_api.get('rank', '?')} 名", file=sys.stderr)

    # Step 2: 本地引擎 — 学校级推荐
    print("[计算] 计算学校推荐...", file=sys.stderr)
    api_rank = rank_api.get('rank') if isinstance(rank_api, dict) else None
    # 传入批次线用于四场景过滤（本科/专科混合推荐策略）
    batch_lines = lines_api if isinstance(lines_api, list) else None
    result = recommend(args.score, args.category, args.year, province_id=pid,
                       api_rank=api_rank, batch_lines=batch_lines)

    if "error" in result:
        print(f"[FAIL] 推荐失败: {result['error']}", file=sys.stderr)
        return 1

    t = result['tiers']
    vdesc = result.get('volunteer_desc', '')
    vslots = result.get('volunteer_slots', 96)
    scenario = result.get('scenario')
    print(f"   {vdesc}", file=sys.stderr)
    scenario_info = f' [{scenario}]' if scenario else ''
    print(f"   共 {result['total_schools']} 所学校（本省 {vslots} 个志愿位 ×2 参考）{scenario_info}"
          f" 冲:{t['冲']['count']} 稳:{t['稳']['count']} 保:{t['保']['count']}",
          file=sys.stderr)

    # Step 3: 生成报告
    full_md = generate_full_md(result, rank_api, lines_api, pname, args.category, args.year)
    full_html = build_html_report(result)

    # JSON 输出
    if args.json:
        output = {
            "meta": {"score": args.score, "category": args.category,
                     "province": pname, "year": args.year},
            "yuanbao": {"rank": rank_api, "lines": lines_api},
            "recommendation": result,
        }
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"[OK] JSON 已导出: {os.path.abspath(args.json)}", file=sys.stderr)

    # 文件输出模式（--md / --html 指定路径）
    if args.md:
        with open(args.md, 'w', encoding='utf-8') as f:
            f.write(full_md)
        print(f"[OK] 完整MD报告: {os.path.abspath(args.md)}", file=sys.stderr)
    if args.html:
        with open(args.html, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"[OK] 完整HTML报告: {os.path.abspath(args.html)}", file=sys.stderr)

    # IMA 平台：订阅 KB + 存档完整 MD/HTML
    ensure_gaokao_kb_subscribed()
    kb_info = ima_auto_archive(full_md, full_html, pname, args.score, args.category)

    # Step 3.5: 在报告生成前注入场景标签到头部
    scenario = result.get('scenario')
    if scenario:
        # 注入到简报头部
        scenario_note = f"\n> 📐 **{scenario}**"
        def _inject_scenario(lines_list):
            # 在批次线表格之后、冲档标题之前插入场景说明
            pass  # 各生成函数自行处理

    # Step 4: 终端输出（控制台模式）
    if not args.md and not args.html and not args.json:
        brief_md = generate_brief_md(result, rank_api, lines_api, pname, args.category, args.year)
        print(brief_md)
        print()
        if is_ima_platform() and kb_info:
            print(f"[完整报告] 完整MD/HTML已存档到「{kb_info['kb_name']}」")
            print(f"[IMA知识库] 了解更多高考志愿知识: {IMA_KB_URL}")
        else:
            local_html = os.path.join(tempfile.gettempdir(),
                                      f"gaokao_{pname}{args.score}{args.category}.html")
            with open(local_html, 'w', encoding='utf-8') as f:
                f.write(full_html)
            local_url = f"file:///{local_html.replace(chr(92), '/')}"
            print(f"[完整HTML报告] {local_url}")
            print(f"[IMA知识库] 了解更多: {IMA_KB_URL}")
        print()

    return 0


# === 常量与格式 ===

IMA_KB_URL = "https://ima.qq.com/wiki/?shareId=3c3f6d1700068fef257fa518da8703ca96172d414e25e75ded05867ab02649c2"
IMA_KB_ID = "AEaapGGng0Ql9WrI1oMOmF0wJ0daWzpNFULr3Qkgtpk="
LEGAL_KB_ID = "QqH2FL2WO286JS_hyJ6KdbHTIEmleMeYMaQl4NRIWew"
LEGAL_KB_NAME = "法律知识库"

KB_FOOTER_MD = f"了解更多高考志愿知识和专家深度报告请访问 [IMA高考志愿知识库](<{IMA_KB_URL}>)。"


# === 动态对话引导问题（Agent 会话提醒用，不进入报告正文） ===

def dynamic_guide_questions(score=None, province=None, category=None,
                             major_interest=None, family_context=None):
    """根据用户背景动态生成 2 条追问问题（尾行由 LLM 自由发挥）。

    参数：
        score: 高考分数
        province: 省份名称
        category: 选科（物理类/历史类）
        major_interest: 用户表达的专业意向（如'计算机''法学'），可选
        family_context: 家庭背景线索（如'父母在深圳''农村家庭'），可选

    返回：
        list[str] — 2 条追问问题，不含尾行。尾行由 Agent 根据上下文自由生成。
    """
    questions = []

    # --- 专业意向（最高优先级） ---
    if major_interest:
        questions.append(
            f"想了解{province or '目标省份'}{major_interest}专业在各推荐院校中的实力和录取趋势吗？"
        )
        questions.append(
            f"{major_interest}专业的考研方向、就业前景和行业薪资如何？"
        )

    # --- 家庭背景个性问题 ---
    elif family_context:
        questions.append(
            f"结合您提到的「{family_context}」，需要进一步筛选更适合的院校和城市吗？"
        )
        questions.append("需要对比几所目标院校的学费、住宿和地域生活成本吗？")

    # --- 通用引导（无特殊上下文） ---
    else:
        if score and score >= 600:
            questions.append(
                "高分段考生在选择时，优先选学校层次还是选专业实力更合适？"
            )
        elif score and score >= 500:
            questions.append(
                "中分段考生如何平衡学校层次与专业实力？是否需要对比具体院校？"
            )
        elif score:
            questions.append(
                "当前分数段有哪些性价比高的院校值得重点关注？"
            )
        questions.append("需要对比两所具体院校的优势学科和毕业生去向吗？")

    return questions


# === 报告生成 ===

def _build_header(province, year, category, score, rank, pool, rank_pct, vdesc='', scenario=None):
    """构建报告头部 Markdown"""
    lines = []
    lines.append(f"# 高考志愿简报\n")
    if vdesc:
        lines.append(f"> 📋 **{vdesc}**\n")
    if scenario:
        lines.append(f"> 📐 **推荐策略：{scenario}**\n")
    lines.append(f"| 项目 | 数据 |")
    lines.append(f"|------|------|")
    lines.append(f"| 省份 | {province} |")
    lines.append(f"| 年份 | {year} |")
    lines.append(f"| 科类 | {category} |")
    lines.append(f"| 分数 | **{score} 分** |")
    lines.append(f"| 省排名 | 约 **{rank:,}** 名 |")
    lines.append(f"| 同省考生 | {pool:,} 人 |")
    lines.append(f"| 百分位 | 前 **{rank_pct}%** |")
    lines.append("")
    return lines


def _build_batch_lines(lines_api):
    """构建批次线 Markdown 表格"""
    lines = []
    if isinstance(lines_api, list) and lines_api:
        # 标准标签 + 3+3 省份（浙江/山东的 普通类一段/二段）
        KEY_BATCHES = ('本科批', '特殊类型招生控制线', '专科批',
                       '普通类一段', '普通类二段')
        main_lines = [l for l in lines_api
                      if l.get('batch', '') in KEY_BATCHES]
        if main_lines:
            lines.append(f"## 省控线\n")
            lines.append(f"| 批次 | 分数线 |")
            lines.append(f"|------|--------|")
            for l in main_lines:
                lines.append(f"| {l.get('batch', '?')} | {l.get('score', '?')} 分 |")
            lines.append("")
    return lines


def _build_tier_table(tier, key, max_schools=None):
    """构建单个档位学校表格，max_schools 为 None 则全量输出"""
    t = tier[key]
    schools = t['schools']
    count = t['count']
    display = schools[:max_schools] if max_schools else schools

    lines = []
    lines.append(f"## {t['label']} — {count} 校\n")
    lines.append(f"| # | 学校 | 城市 | 层次 | 最低位次 | 概率 |")
    lines.append(f"|---|------|------|------|----------|------|")

    for i, s in enumerate(display, 1):
        tags = []
        if s['f985']: tags.append('985')
        if s['f211']: tags.append('211')
        if s['dual']: tags.append('双一流')
        tag_str = '/'.join(tags) if tags else s.get('level', '-')
        city = s.get('province', s.get('city', ''))
        web = s.get('website', '') or s.get('admissions_site', '')
        name_str = f"[{s['name']}]({web})" if web else s['name']
        lines.append(f"| {i} | {name_str} | {city} | {tag_str} "
                     f"| {s['admit_rank']:,} | {s['prob']}% |")

    if max_schools and len(schools) > max_schools:
        remaining = len(schools) - max_schools
        lines.append(f"| ... | *及其他 {remaining} 校* | | | | |")
    lines.append("")
    return lines


def _build_summary(result):
    """构建汇总表"""
    tiers = result['tiers']
    c = tiers['冲']['count']
    w = tiers['稳']['count']
    b = tiers['保']['count']
    vdesc = result.get('volunteer_desc', '')
    vslots = result.get('volunteer_slots', 96)
    lines = []
    lines.append(f"## 汇总\n")
    if vdesc:
        lines.append(f"> 📋 **{vdesc}** — 本省实际志愿位 **{vslots}** 个，以下展示 **{c+w+b}** 所学校供参考（实际位数的 {c+w+b}//{vslots} 倍）。\n")
    lines.append(f"| 类别 | 数量 |")
    lines.append(f"|------|------|")
    lines.append(f"| 冲刺 | {c} 校 |")
    lines.append(f"| 稳妥 | {w} 校 |")
    lines.append(f"| 保底 | {b} 校 |")
    lines.append(f"| **合计** | **{c+w+b} 校** |")
    lines.append("")
    return lines


def generate_full_md(result, rank_api, lines_api, province, category, year):
    """完整 Markdown 报告（全量学校 + KB footer）"""
    score = result['score']
    rank = result['rank']
    pool = result['pool_size']
    rank_pct = result['rank_pct']
    vdesc = result.get('volunteer_desc', '')
    scenario = result.get('scenario')

    lines = _build_header(province, year, category, score, rank, pool, rank_pct, vdesc, scenario)
    lines.extend(_build_batch_lines(lines_api))

    tiers = result['tiers']
    for key in ['冲', '稳', '保']:
        lines.extend(_build_tier_table(tiers, key))

    lines.extend(_build_summary(result))
    lines.append(KB_FOOTER_MD)
    return '\n'.join(lines)


def generate_brief_md(result, rank_api, lines_api, province, category, year, max_per_tier=5):
    """简化 Markdown 简报（每档 top N）"""
    score = result['score']
    rank = result['rank']
    pool = result['pool_size']
    rank_pct = result['rank_pct']
    vdesc = result.get('volunteer_desc', '')
    scenario = result.get('scenario')

    lines = _build_header(province, year, category, score, rank, pool, rank_pct, vdesc, scenario)
    lines.extend(_build_batch_lines(lines_api))

    tiers = result['tiers']
    for key in ['冲', '稳', '保']:
        lines.extend(_build_tier_table(tiers, key, max_schools=max_per_tier))

    lines.extend(_build_summary(result))
    return '\n'.join(lines)


# 向后兼容别名
generate_md = generate_full_md


if __name__ == "__main__":
    sys.exit(main())
