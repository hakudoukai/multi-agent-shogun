#!/usr/bin/env python3
"""dino_enemy_master_seed.json 再現生成器 (directive 043b1384).

docs/cmd004_dinosaur_100enemies_spec.md の敵 100 行表と
§2-1 difficulty パラメータ / §3-1..3-5 (20 体/段) / min_rank_gate 規約から
決定論的に seed を再生成する。乱数・捏造なし。spec 改訂時はこれを再実行。

usage: python3 assets/dinosaur_kingdom/seed/gen_seed.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SPEC = os.path.join(REPO, "docs/cmd004_dinosaur_100enemies_spec.md")
OUT = os.path.join(HERE, "dino_enemy_master_seed.json")

# spec §2-1 difficulty パラメータ表 + §3-x min_rank_gate。行順 20 体ずつ 5 段。
BUCKETS = [
    ("very_easy", "tamago", 0.00, 0.05, False),
    ("easy", "tamago", 0.05, 0.10, False),
    ("normal", "hiyoko", 0.10, 0.20, False),
    ("hard", "bokensha", 0.15, 0.30, False),
    ("boss", "yusha", 0.20, 0.60, True),
]
ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|"
    r"\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|"
)


def main() -> int:
    rows = []
    for ln in open(SPEC, encoding="utf-8").read().splitlines():
        m = ROW.match(ln)
        if m:
            rows.append({
                "idx": int(m.group(1)),
                "enemy_id": m.group(2).strip(),
                "name": m.group(3).strip(),
                "base_hp": int(m.group(4)),
                "base_xp": int(m.group(5)),
                "age_tier_eligibility": [
                    s.strip() for s in m.group(6).split(",") if s.strip()
                ],
                "drop_tier": int(m.group(7)),
            })
    rows.sort(key=lambda r: r["idx"])
    if len(rows) != 100:
        print(f"NG: spec から 100 体抽出できず ({len(rows)})")
        return 1
    seed = []
    for r in rows:
        diff, rank, crit, drop, sub = BUCKETS[(r["idx"] - 1) // 20]
        seed.append({
            "enemy_id": r["enemy_id"],
            "name": r["name"],
            "difficulty": diff,
            "base_hp": r["base_hp"],
            "base_xp": r["base_xp"],
            "age_tier_eligibility": r["age_tier_eligibility"],
            "min_rank_gate": rank,
            "drop_tier": r["drop_tier"],
            "drop_asset_key": f"dinosaur_kingdom/drops/{r['enemy_id']}",
            "requires_subscription": sub,
            "world_theme_id": 3,
            "crit_rate": crit,
            "drop_rate": drop,
            "is_active": True,
        })
    out = {
        "schema": "passport_dino_enemy_master",
        "source_spec": "docs/cmd004_dinosaur_100enemies_spec.md",
        "directive_id": "043b1384-e414-4932-9551-2821cfaccf13",
        "generated": "2026-05-17",
        "derivation": "敵100行+§3-1..3-5(20体/段)+§2-1 difficultyパラメータ表"
                      "+min_rank_gate規約 から決定論的導出。乱数/捏造なし。",
        "count": len(seed),
        "by_difficulty": {
            d: sum(1 for s in seed if s["difficulty"] == d)
            for d, _, _, _, _ in BUCKETS
        },
        "enemies": seed,
    }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"WROTE {OUT} count={len(seed)} by={out['by_difficulty']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
