#!/usr/bin/env python3
# encoding: utf-8
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2023-2026 律锥·legalskill
"""School-level recommendation engine (light mode, single-year)."""
import math
from loader import (get_schools, get_school_stats, lookup_school,
                    score_to_rank_local, get_pool_size,
                    get_volunteer_config, describe_volunteer_mode)


# Expert-mode slot ratios: (chong_pct, bao_pct, wen_pct=1-chong-bao)
# Keyed by actual province volunteer slot count (not doubled)
SLOT_RATIOS = {
    112: (0.28, 0.30),
    96:  (0.30, 0.30),
    80:  (0.25, 0.30),
    48:  (0.20, 0.30),
    45:  (0.20, 0.30),
    40:  (0.20, 0.30),
    24:  (0.15, 0.35),
    10:  (0.10, 0.40),
    9:   (0.10, 0.40),
}


def _slot_ratios(slots):
    """Return (chong_pct, bao_pct) for given province slot count."""
    if slots in SLOT_RATIOS:
        return SLOT_RATIOS[slots]
    return (0.20, 0.30)  # default


def _tier_range(candidates):
    """Return display string for tier probability range."""
    if not candidates:
        return "0%"
    probs = [c['prob'] for c in candidates]
    lo = min(probs)
    hi = max(probs)
    if abs(lo - hi) < 0.05:
        return f"{lo:.0f}%"
    return f"{lo:.0f}-{hi:.0f}%"


def _strided_sample(items, n):
    """Take n evenly-spaced samples from a sorted list.
    Ensures smooth coverage across the full range, not just extremes."""
    if len(items) <= n:
        return items
    step = len(items) / n
    sampled = []
    for i in range(n):
        idx = int(i * step)
        sampled.append(items[idx])
    return sampled


def _apply_scenario(chong_raw, wen_raw, bao_raw, score, batch_lines, n_chong, n_wen, n_bao):
    """四场景过滤：基于分数与本科线的关系决定本科/专科的混合策略。

    场景1 — 纯本科：分数远高于本科线，全部推荐本科
    场景2 — 本科为主专科为辅：本科放冲/稳，专科只放保
    场景3 — 专科为主本科为辅：专科放稳/保，本科只放冲
    场景4 — 纯专科：分数远低于本科线，全部推荐专科

    batch_lines: province_lines() 返回的批次线列表 [{batch, score, ...}, ...]
    """
    if not batch_lines or not isinstance(batch_lines, (list, tuple)):
        return chong_raw, wen_raw, bao_raw, None, 68.0

    # 从批次线中提取本科批分数线
    benke_xian = None
    for bl in batch_lines:
        if isinstance(bl, dict):
            bname = bl.get('batch', '')
            if bname in ('本科批', '普通类一段'):
                try:
                    benke_xian = int(float(bl['score']))
                except (ValueError, TypeError, KeyError):
                    pass
                break

    if not benke_xian:
        return chong_raw, wen_raw, bao_raw, None, 68.0

    # 按本科/专科分离
    def is_ben(c):
        return c.get('level') == '本科'

    c_ben = [c for c in chong_raw if is_ben(c)]
    c_zhu = [c for c in chong_raw if not is_ben(c)]
    w_ben = [c for c in wen_raw if is_ben(c)]
    w_zhu = [c for c in wen_raw if not is_ben(c)]
    b_ben = [c for c in bao_raw if is_ben(c)]
    b_zhu = [c for c in bao_raw if not is_ben(c)]

    diff = score - benke_xian

    if diff >= 20:
        # 场景1: 纯本科方案
        new_chong, new_wen, new_bao = c_ben, w_ben, b_ben
        scenario = '纯本科方案'
        bao_threshold = 68.0
    elif diff >= 0:
        # 场景2: 本科为主，专科为辅 — 专科只参加保
        new_chong = c_ben
        new_wen = w_ben
        new_bao = b_ben + b_zhu
        scenario = '本科为主，专科为辅'
        bao_threshold = 68.0
    elif diff >= -30:
        # 场景3: 专科为主，本科为辅 — 本科只参加冲
        new_chong = c_ben + c_zhu
        new_wen = w_zhu
        new_bao = b_zhu
        scenario = '专科为主，本科为辅'
        bao_threshold = 50.0  # 专科概率区间被数据上限压缩，用 50% 替代 68%
    else:
        # 场景4: 纯专科方案
        new_chong, new_wen, new_bao = c_zhu, w_zhu, b_zhu
        scenario = '纯专科方案'
        bao_threshold = 50.0  # 同理，概率区间压缩，50% 即为高概率

    return new_chong, new_wen, new_bao, scenario, bao_threshold


def recommend(user_score, category="物理类", year="2025",
              province_id="13", target_slots=None, exclude_schools=None,
              api_rank=None, api_pool=None, batch_lines=None):
    """
    Generate school-level 冲/稳/保 recommendations.

    - Tier assignment: logistic boundary at 32% / 68%
    - Probability: real logistic sigmoid model (K=2.5), no linear interpolation
    - Sampling: strided across full probability range within each tier
    - Ratio: expert-style per province slot count
    - Sort: ascending prob for uniform stride coverage
    """
    exclude_schools = exclude_schools or set()
    pid = int(province_id) if province_id else 13

    vcfg = get_volunteer_config(pid)
    province_slots = vcfg[0]
    if target_slots is None:
        target_slots = province_slots * 2

    # 1. Score to rank — API 优先（线上数据更新及时），本地兜底
    rank_info = None
    if api_rank is not None:
        rank_info = {'rank': int(api_rank), 'year': year, 'category': category}
    if not rank_info:
        rank_info = score_to_rank_local(user_score, year, category, province_id)
    if not rank_info:
        return {"error": f"No segment data for {province_id} {year} {category}"}
    user_rank = rank_info['rank']

    # 2. Pool size
    pool = get_pool_size(province_id, year, category)
    if not pool:
        pool = 300000
    rank_pct = user_rank / pool * 100

    # 3. Filter school_stats by province + category
    stats = get_school_stats()
    cat_key = category[0] if category else '物'
    matching = [st for st in stats
                if cat_key in st['c']
                and str(st['p']) == str(province_id)]
    if not matching:
        matching = [st for st in stats
                    if '综' in st['c']
                    and str(st['p']) == str(province_id)]
    if not matching:
        # Old-style labels: 文科 / 理科 (新疆 etc.)
        if cat_key == '历':
            matching = [st for st in stats
                        if '文' in st['c']
                        and str(st['p']) == str(province_id)]
        elif cat_key == '物':
            matching = [st for st in stats
                        if '理' in st['c']
                        and str(st['p']) == str(province_id)]
    if not matching:
        return {"error": f"No admission data for province {province_id} category {category}"}

    # 4. Classify by logistic tier boundary
    K = 2.5
    LEVEL_MAP = {'2001': '本科', '2002': '专科', '2003': '本科'}
    candidates = []

    for st in matching:
        school_id = st['i']
        if school_id in exclude_schools:
            continue
        school = lookup_school(school_id)
        if not school:
            continue

        admit_rank = int(st['r']) if st['r'] else 0
        if admit_rank <= 0:
            continue
        ratio = user_rank / admit_rank
        clipped = max(0.01, min(ratio, 40.0))
        logistic_prob = 100.0 / (1.0 + math.exp(K * (clipped - 1.0)))

        level_text = LEVEL_MAP.get(str(school['l']),
            school['l'] if school['l'] and len(str(school['l'])) <= 4 else '本科')

        if logistic_prob >= 68:
            tier = 'bao'
        elif logistic_prob >= 32:
            tier = 'wen'
        else:
            tier = 'chong'

        candidates.append({
            'sid': school_id,
            'name': school['n'],
            'province': school['p'],
            'level': level_text,
            'f985': school['9'],
            'f211': school['2'],
            'dual': school['d'],
            'website': school.get('w', ''),
            'admissions_site': school.get('z', ''),
            'admit_rank': admit_rank,
            'batch': st['b'],
            'category': st['c'],
            'ratio': round(ratio, 2),
            'tier': tier,
            'prob': round(logistic_prob, 1),
        })

    # Sort within tier: ascending prob (for strided sampling across full range)
    sort_key = lambda c: c['prob']
    chong_raw = sorted([c for c in candidates if c['tier'] == 'chong'], key=sort_key)
    wen_raw   = sorted([c for c in candidates if c['tier'] == 'wen'],   key=sort_key)
    bao_raw   = sorted([c for c in candidates if c['tier'] == 'bao'],   key=sort_key)

    # Expert ratios per province slot count
    chong_pct, bao_pct = _slot_ratios(province_slots)
    n_chong = int(target_slots * chong_pct)
    n_bao   = int(target_slots * bao_pct)
    n_wen   = target_slots - n_chong - n_bao

    # 四场景过滤：根据分数与本科线的关系决定本科/专科混合策略
    chong_raw, wen_raw, bao_raw, scenario, bao_threshold = _apply_scenario(
        chong_raw, wen_raw, bao_raw, user_score, batch_lines, n_chong, n_wen, n_bao)

    # 场景动态阈值调整：某些场景下概率区间被压缩，需要调整保底/稳妥的划分
    if bao_threshold < 68.0:
        # 重新按调整后的阈值划分档位（不改概率，只改档位归属）
        all_after_scenario = chong_raw + wen_raw + bao_raw
        for item in all_after_scenario:
            p = item['prob']
            if p >= bao_threshold:
                item['tier'] = 'bao'
            elif p >= 32.0:
                item['tier'] = 'wen'
            else:
                item['tier'] = 'chong'
        # 重新按档位分离
        sort_key = lambda c: c['prob']
        chong_raw = sorted([c for c in all_after_scenario if c['tier'] == 'chong'], key=sort_key)
        wen_raw   = sorted([c for c in all_after_scenario if c['tier'] == 'wen'],   key=sort_key)
        bao_raw   = sorted([c for c in all_after_scenario if c['tier'] == 'bao'],   key=sort_key)

    # Strided sampling: evenly cover full probability range in each tier
    # Filter out schools with < 5% probability (very slim chance, not worth recommending)
    chong_raw = [c for c in chong_raw if c['prob'] >= 5.0]
    chong_cands = _strided_sample(chong_raw, n_chong)
    wen_cands   = _strided_sample(wen_raw, n_wen)
    bao_cands   = _strided_sample(bao_raw, n_bao)

    # Probabilities are real logistic-model values (computed above, stored in 'prob')

    vdesc = describe_volunteer_mode(vcfg)

    return {
        'score': user_score,
        'rank': user_rank,
        'pool_size': pool,
        'rank_pct': round(rank_pct, 2),
        'category': category,
        'year': year,
        'province_id': province_id,
        'volunteer_mode': vcfg[1],
        'volunteer_slots': vcfg[0],
        'volunteer_desc': vdesc,
        'scenario': scenario,
        'tiers': {
            '冲': {'label': f'冲刺 (录取概率{_tier_range(chong_cands)})', 'count': len(chong_cands), 'schools': chong_cands},
            '稳': {'label': f'稳妥 (录取概率{_tier_range(wen_cands)})',   'count': len(wen_cands),   'schools': wen_cands},
            '保': {'label': f'保底 (录取概率{_tier_range(bao_cands)})',   'count': len(bao_cands),   'schools': bao_cands},
        },
        'total_schools': len(chong_cands) + len(wen_cands) + len(bao_cands),
    }
