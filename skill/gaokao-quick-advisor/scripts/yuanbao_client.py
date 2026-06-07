#!/usr/bin/env python3
# encoding: utf-8
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2023-2026 律锥·legalskill
"""
Yuanbao API client - score-to-rank and province-score-line queries.
Adapted from legacy yuanbao fetch_data.py scripts.
"""
import json, sys, urllib.request, urllib.parse
import bisect

BASE_URL = "https://gaokao.search.qq.com/skills_data"

# 3+3 provinces: unified scoring, no separate 物理/历史 segments
# API expects classify=综合 for these, not 物理/历史
PROVINCES_33 = {'北京', '天津', '上海', '浙江', '山东', '海南'}


def _classify_for_api(place, category):
    """Map user-facing category to API classify parameter.
    3+3 provinces use '综合', others use 物理/历史."""
    if place in PROVINCES_33:
        return '综合'
    return category.rstrip('类') if category else category

def _api(api_type, params, retry=2):
    """Generic API caller for gaokao.search.qq.com"""
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, quote_via=urllib.parse.quote)
    url = f"{BASE_URL}?type={api_type}&from=open_tB0fU5wP&{qs}"
    for _ in range(retry):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                r = json.loads(resp.read().decode("utf-8"))
                if r.get("status") != 0:
                    return {"error": r.get("message", "API error"), "status": r.get("status")}
                return r.get("data", {})
        except urllib.error.URLError as e:
            last_err = f"Network error: {e}"
        except json.JSONDecodeError as e:
            last_err = f"JSON parse error: {e}"
    return {"error": last_err}


def score_to_rank(score, place="河北", year="2025", category="物理类"):
    """Convert score to provincial rank. Returns dict with rank, same_score_count."""
    classify = _classify_for_api(place, category)
    q = {
        "year": year,
        "place": place,
        "classify": classify,
        "title": "高考;一分一段表",
    }
    data = _api("score_range", q)
    if "error" in data:
        return data

    records = data.get("score_range_res", [])
    for record in records:
        detail = record.get("查询数据", [])
        if not detail:
            continue
        # detail is high-score to low-score; reverse to low→high for bisect
        detail_rev = list(reversed(detail))
        scores = []
        for item in detail_rev:
            try:
                sc = item.get("返回的查询分数", "")
                if "-" in sc:
                    scores.append(int(sc.split("-")[0]))
                else:
                    scores.append(int(sc))
            except (ValueError, TypeError):
                scores.append(0)

        idx = bisect.bisect_right(scores, score) - 1
        if idx < 0:
            idx = 0
        item = detail_rev[idx]
        return {
            "year": record.get("查询分数线年份", year),
            "place": record.get("适用地区", place),
            "category": record.get("选科类别", category),
            "score": item.get("返回的查询分数", str(score)),
            "same_score_count": item.get("同分人数", "?"),
            "rank": item.get("排名位次", "?"),
            "user_score": score,
        }
    return {"error": "No score data found"}


def province_lines(place="河北", year="2025", category="物理类"):
    """Get province batch cutoff lines. Returns list of {batch, score} dicts."""
    student = _classify_for_api(place, category)
    q = {
        "year": year,
        "place": place,
        "student": student,
    }
    data = _api("province_score_line", q)
    if "error" in data:
        return data

    records = data.get("地区分数线") or data.get("查询分数线") or data.get("province_score_line_res") or []
    lines = []
    for r in records:
        lines.append({
            "batch": r.get("录取批次", "?"),
            "score": r.get("分数", "?"),
            "year": r.get("分数查询年份", year),
            "place": r.get("分数线所属地区", place),
        })
    return lines


if __name__ == "__main__":
    # Quick test
    r = score_to_rank(540, "河北", "2025", "物理类")
    print(json.dumps(r, ensure_ascii=False, indent=2))
    l = province_lines("河北", "2025", "物理类")
    print(json.dumps(l, ensure_ascii=False, indent=2))
