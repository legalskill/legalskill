#!/usr/bin/env python3
# encoding: utf-8
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2023-2026 律锥·legalskill
"""Light data loader - loads pre-computed JSON data files."""
import json, os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

_cache = {}

def _load(name):
    if name not in _cache:
        fp = os.path.join(DATA_DIR, name)
        with open(fp, 'r', encoding='utf-8') as f:
            _cache[name] = json.load(f)
    return _cache[name]


def get_schools():
    """Return list of {i, n, c, p, t, l, 9, 2, d, w, z}
    i=id, n=name, c=city, p=province, t=district_code(行政区划),
    l=level, 9=is_985, 2=is_211, d=is_双一流,
    w=官网URL, z=招生网URL"""
    return _load('schools.json')


def lookup_school(school_id):
    """Look up a single school by id."""
    schools = get_schools()
    # Build index on first call
    if not hasattr(lookup_school, '_index'):
        lookup_school._index = {s['i']: s for s in schools}
    return lookup_school._index.get(school_id)


def get_school_stats():
    """Return list of {i, p, c, b, r} — single-year (2024) admission rank."""
    return _load('school_stats.json')


def get_segments():
    """Return list of {p, y, c, s, r} — score->rank lookup (all provinces)."""
    return _load('segments.json')


def get_pool_totals():
    """Return list of {p, y, c, t} — total test-takers by province/year/category."""
    return _load('pools.json')


# ── Province mapping ──
PROVINCES = {
    '11': '北京', '12': '天津', '13': '河北', '14': '山西', '15': '内蒙古',
    '21': '辽宁', '22': '吉林', '23': '黑龙江',
    '31': '上海', '32': '江苏', '33': '浙江', '34': '安徽', '35': '福建', '36': '江西', '37': '山东',
    '41': '河南', '42': '湖北', '43': '湖南', '44': '广东', '45': '广西', '46': '海南',
    '50': '重庆', '51': '四川', '52': '贵州', '53': '云南', '54': '西藏',
    '61': '陕西', '62': '甘肃', '63': '青海', '64': '宁夏', '65': '新疆',
}

# ── Province volunteer config ──
# (province_id, slots, mode, majors_per_slot, has_adjustment, note)
PROVINCE_VOLUNTEER_CONFIG = {
    # 专业+院校 — 每个志愿即一个专业，无调剂
    13: (96, '专业+院校', 1, False, '河北'),
    50: (96, '专业+院校', 1, False, '重庆'),
    52: (96, '专业+院校', 1, False, '贵州'),
    21: (112, '专业+院校', 1, False, '辽宁'),
    37: (96, '专业+院校', 1, False, '山东'),
    33: (80, '专业+院校', 1, False, '浙江'),
    # 院校专业组 — 每个志愿为一个专业组（含多个专业），有组内调剂
    41: (48, '院校专业组', 6, True, '河南'),
    44: (45, '院校专业组', 6, True, '广东'),
    43: (45, '院校专业组', 6, True, '湖南'),
    42: (45, '院校专业组', 6, True, '湖北'),
    51: (45, '院校专业组', 6, True, '四川'),
    61: (45, '院校专业组', 6, True, '陕西'),
    14: (45, '院校专业组', 6, True, '山西'),
    62: (45, '院校专业组', 6, True, '甘肃'),
    36: (45, '院校专业组', 6, True, '江西'),
    15: (45, '院校专业组', 12, True, '内蒙古'),
    34: (45, '院校专业组', 6, True, '安徽'),
    32: (40, '院校专业组', 6, True, '江苏'),
    35: (40, '院校专业组', 6, True, '福建'),
    45: (40, '院校专业组', 6, True, '广西'),
    53: (40, '院校专业组', 10, True, '云南'),
    31: (24, '院校专业组', 4, True, '上海'),
    # 老高考 — 院校志愿
    65: (9, '院校', 1, False, '新疆一批'),
    54: (10, '院校', 1, False, '西藏'),
}


def get_volunteer_config(province_id):
    """Get volunteer config for province, return (slots, mode, mps, adj, note)."""
    pid = int(province_id) if province_id else 13
    if pid in PROVINCE_VOLUNTEER_CONFIG:
        return PROVINCE_VOLUNTEER_CONFIG[pid]
    if pid in (11, 12, 46):  # 北京/天津/海南 3+3 → 院校专业组
        return (30, '院校专业组', 4, True, '')
    if pid in (22, 23, 63, 64):  # 吉林/黑龙江/青海/宁夏 3+1+2
        return (45, '院校专业组', 6, True, '')
    return (30, '院校专业组', 6, True, '')


def describe_volunteer_mode(config):
    """Human-readable volunteer mode description."""
    slots, mode, mps, adj, note = config
    if mode == '专业+院校':
        return f"{mode} · {slots}个志愿位 · 每志愿1个专业 · 无调剂风险"
    elif mode == '院校专业组':
        adj_txt = '有组内调剂' if adj else ''
        return f"{mode} · {slots}个志愿位 · 每组{mps}个专业 · {adj_txt}"
    else:
        return f"{mode} · {slots}个志愿位"


# 城市→省份映射（LLM 负责语义理解，本表仅留示例格式供参考）
CITY_TO_PROVINCE = {
    # 示例：'苏州': '32',  # → 江苏
    # Agent 调用前将城市名转换为省名（如"苏州"→"江苏"），再传入 --province 参数
}

def province_id(name):
    """Convert province or city name to province id."""
    if not name:
        return '13'
    name = name.replace('省','').replace('市','').replace('自治区','').replace('回族','').replace('壮族','').replace('维吾尔','')
    for pid, pname in PROVINCES.items():
        if pname == name or pname in name:
            return pid
    # 城市→省份后备
    pid = CITY_TO_PROVINCE.get(name)
    if pid:
        return pid
    return '13'  # default Hebei


def score_to_rank_local(score, year="2025", category="物理类", province_id="13"):
    """Local score-to-rank conversion using segments data.
    More reliable than API when offline or API down."""
    segs = get_segments()
    # Filter by province, year and category
    matching = [s for s in segs
                if str(s['p']) == str(province_id)
                and str(s['y']) == str(year)
                and s['c'] == category]
    if not matching:
        # Try with broader category match
        if '物理' in category:
            matching = [s for s in segs
                        if str(s['p']) == str(province_id)
                        and str(s['y']) == str(year)
                        and '物理' in s['c']]
        elif '历史' in category:
            matching = [s for s in segs
                        if str(s['p']) == str(province_id)
                        and str(s['y']) == str(year)
                        and '历史' in s['c']]
    if not matching:
        # 3+3省份（北京/天津/上海/浙江/山东/海南）使用"综合"分类
        matching = [s for s in segs
                    if str(s['p']) == str(province_id)
                    and str(s['y']) == str(year)
                    and '综合' in s['c']]
    if not matching:
        # 老标签制省份（新疆等）使用"文科"/"理科"
        if '历史' in category or '文' in category:
            matching = [s for s in segs
                        if str(s['p']) == str(province_id)
                        and str(s['y']) == str(year)
                        and '文' in s['c']]
        elif '物理' in category or '理' in category:
            matching = [s for s in segs
                        if str(s['p']) == str(province_id)
                        and str(s['y']) == str(year)
                        and '理' in s['c']]
    if not matching:
        return None
    # Sort by score ascending for bisect (bisect assumes ascending order)
    matching.sort(key=lambda x: x['s'])
    scores = [s['s'] for s in matching]
    import bisect
    # Find rightmost position where score <= target
    idx = bisect.bisect_right(scores, score) - 1
    if idx < 0:
        idx = 0
    s = matching[idx]
    return {'score': s['s'], 'rank': s['r'], 'year': s['y'], 'category': s['c']}


def get_pool_size(province_id="13", year="2025", category="物理类"):
    """Get total test-takers count for normalization."""
    pools = get_pool_totals()
    for p in pools:
        if str(p['p']) == str(province_id) and str(p['y']) == year:
            pc = p['c']
            # Direct match: same category, substring, or comprehensive
            if (pc == category or category in pc or pc in category
                    or '综合' in pc
                    or ('历史' in category and '文' in pc)
                    or ('物理' in category and '理' in pc)
                    or ('文' in category and '文' in pc)
                    or ('理' in category and '理' in pc)):
                return p['t']
    return None
