#!/usr/bin/env python3
# encoding: utf-8
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2023-2026 律锥·legalskill
"""Light HTML report generator for school-level recommendations."""


IMA_KB_URL = "https://ima.qq.com/wiki/?shareId=3c3f6d1700068fef257fa518da8703ca96172d414e25e75ded05867ab02649c2"

# 配色体系 — 高考绿白渐变头部 + 分档色
HEADER_BG   = "#1B5E20"   # 深绿头部起点
HEADER_GRAD = "#E8F5E9"   # 头部渐变终点（绿→白）
ACCENT      = "#2E7D32"   # 中绿强调色
LIGHT_BG    = "#C8E6C9"   # 浅绿（表头底/hover）
BUTTON_BG   = "rgba(255,255,255,0.9)"   # 半透白按钮
BUTTON_TEXT = "#1B5E20"   # 按钮文字深绿
BODY_BG     = "#F1F8E9"   # 极浅绿页面底

# 三档配色 — 冲:橙 / 稳:绿 / 保:浅蓝
TIER_COLORS = {
    '冲': '#E65100',
    '稳': '#2E7D32',
    '保': '#1565C0',
}
TIER_CSS = {'冲': 'tier-chong', '稳': 'tier-wen', '保': 'tier-bao'}


def build_html(result):
    """
    Build a single-page HTML report from recommendation results.
    """
    score = result['score']
    rank = result['rank']
    pool = result['pool_size']
    rank_pct = result['rank_pct']
    category = result['category']
    year = result['year']
    tiers = result['tiers']
    vdesc = result.get('volunteer_desc', '')
    vmode = result.get('volunteer_mode', '')
    vcfg_slots = result.get('volunteer_slots', 96)

    # Mode tip
    if vmode == '专业+院校':
        vtip = f'本省为「专业+院校」模式，{vcfg_slots}个志愿位，每志愿=1个专业，无调剂。以下展示{vcfg_slots * 2}所学校供参考。'
    elif vmode == '院校专业组':
        vtip = f'本省为「院校专业组」模式，{vcfg_slots}个志愿位，每组含多个专业，有组内调剂风险。以下展示{vcfg_slots * 2}所学校供参考。'
    else:
        vtip = f'本省为「{vmode}」志愿模式。'

    chong_n = tiers['冲']['count']
    wen_n = tiers['稳']['count']
    bao_n = tiers['保']['count']
    show_count = chong_n + wen_n + bao_n

    # Tier tables
    tier_html = ""

    for key in ['冲', '稳', '保']:
        t = tiers[key]
        schools = t['schools']
        tc = TIER_COLORS[key]
        tcss = TIER_CSS[key]
        if not schools:
            tier_html += f"<div class='section {tcss}'><h2>{t['label']}</h2><p class='empty'>暂无匹配学校</p></div>"
            continue

        tier_html += f"<div class='section {tcss}' style='border-top:3px solid {tc};'>"
        tier_html += f"<h2>{t['label']}</h2>"
        tier_html += "<table><thead><tr>"
        tier_html += "<th>#</th><th>学校</th><th>省份</th><th>层次</th><th>标签</th><th>2024录取位次</th><th>录取概率</th><th>官网</th>"
        tier_html += "</tr></thead><tbody>"

        for i, s in enumerate(schools, 1):
            tags = []
            if s['f985']: tags.append('985')
            if s['f211']: tags.append('211')
            if s['dual']: tags.append('双一流')
            if not tags:
                tags.append(s['level'] or '-')

            tier_html += f"<tr>"
            tier_html += f"<td>{i}</td>"
            tier_html += f"<td class='school-name'>{s['name']}</td>"
            tier_html += f"<td>{s.get('province', s.get('city', ''))}</td>"
            tier_html += f"<td>{s['level']}</td>"
            tier_html += f"<td>{'/'.join(tags)}</td>"
            tier_html += f"<td>{s['admit_rank']:,}</td>"
            tier_html += f"<td class='prob'>{s['prob']}%</td>"
            url = s.get('admissions_site') or s.get('website', '')
            if url:
                sn = s['name']
                tier_html += f"<td><a href='{url}' target='_blank' rel='noopener' class='sch-link' title='{sn}官网'>🔗</a></td>"
            else:
                tier_html += f"<td></td>"
            tier_html += "</tr>"

        tier_html += "</tbody></table></div>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>高考志愿简报 - {score}分 {category}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; background: {BODY_BG}; color: #333; line-height: 1.6; }}
.container {{ max-width: 960px; margin: 0 auto; padding: 20px; }}
.header {{ background: linear-gradient(135deg, {HEADER_BG} 0%, {HEADER_GRAD} 100%); color: #fff; padding: 32px 30px; border-radius: 12px; margin-bottom: 20px; }}
.header h1 {{ font-size: 24px; margin-bottom: 12px; text-shadow: 0 1px 3px rgba(0,0,0,0.3); }}
.header .meta {{ display: flex; gap: 10px; flex-wrap: wrap; font-size: 14px; }}
.header .meta span {{ background: {BUTTON_BG}; color: {BUTTON_TEXT}; padding: 4px 12px; border-radius: 20px; font-weight: 500; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.section {{ background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
.section h2 {{ font-size: 18px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid {LIGHT_BG}; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th {{ background: {LIGHT_BG}; padding: 8px 6px; text-align: left; border-bottom: 2px solid {ACCENT}; font-weight: 600; white-space: nowrap; color: {HEADER_BG}; }}
td {{ padding: 6px; border-bottom: 1px solid #f0f0f0; }}
tr:hover {{ background: {LIGHT_BG}; }}
.school-name {{ font-weight: 600; }}
.sch-link {{ color: {ACCENT}; text-decoration: none; font-size: 14px; }}
.sch-link:hover {{ color: #1B5E20; text-decoration: underline; }}
.prob {{ font-weight: bold; }}
.empty {{ color: #999; font-style: italic; }}
/* 三档配色 */
.tier-chong h2 {{ color: #E65100; }}
.tier-chong .sch-link {{ color: #E65100; }}
.tier-chong .prob {{ color: #E65100; }}
.tier-wen h2 {{ color: #2E7D32; }}
.tier-wen .sch-link {{ color: #2E7D32; }}
.tier-wen .prob {{ color: #2E7D32; }}
.tier-bao h2 {{ color: #1565C0; }}
.tier-bao .sch-link {{ color: #1565C0; }}
.tier-bao .prob {{ color: #1565C0; }}
.data-source {{ background: {BUTTON_BG}; border-left: 4px solid {ACCENT}; }}
.data-source p {{ font-size: 14px; color: #555; line-height: 1.8; }}
.brand {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding: 20px; }}
.brand a {{ color: {ACCENT}; font-weight: 600; text-decoration: none; }}
.brand a:hover {{ text-decoration: underline; }}
.header .meta-tip {{ margin-top: 10px; font-size: 13px; opacity: 0.85; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
    <h1>🎓 高考志愿简报</h1>
    <div class="meta">
        <span>📊 {score} 分</span>
        <span>🏅 省排名 {rank:,}</span>
        <span>👥 全省 {pool:,} 人 (前 {rank_pct}%)</span>
        <span>📚 {category} | {year}年</span>
        <span>📋 {vdesc}</span>
    </div>
    <div class="meta-tip">{vtip}</div>
    <div class="meta-tip" style="margin-top:6px; font-size:12px; opacity:0.75;">💡 点击每行末尾 🔗 直通学校官网</div>
</div>
{tier_html}
<div class='section'>
    <h2>💡 说明</h2>
    <ol style="padding-left: 20px; line-height: 2.2; font-size: 14px;">
        <li>此报告展示{show_count}所学校参考（冲/稳/保 = {chong_n}/{wen_n}/{bao_n}），按{vmode}模式列出，概率从低到高排列。</li>
    </ol>
</div>
<div class='section data-source'>
    <h2>📚 IMA 高考志愿知识库</h2>
    <p>更多高考知识、专家高考志愿报告请访问 <a href='{IMA_KB_URL}' target='_blank' rel='noopener' style='color:{ACCENT}; font-weight:600;'>【IMA知识库】高考志愿</a></p>
    <p><a href='{IMA_KB_URL}' target='_blank' rel='noopener' style='color:{ACCENT}; word-break:break-all;'>{IMA_KB_URL}</a></p>
    <p style='color:#888;'>本报告录取位次数据来源于<strong>元宝 API</strong>（一分一段表 + 省控线查询），结合本地聚合录取统计综合分析。录取概率为历史数据近似值，仅供参考，不代表实际录取结果。</p>
</div>
<div class="brand">Powered by <a href="http://www.legalskill.cn" target="_blank" rel="noopener">律锥·高考志愿技能</a></div>
</div>
</body>
</html>"""

    return html
