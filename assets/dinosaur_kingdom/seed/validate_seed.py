#!/usr/bin/env python3
"""dino_enemy_master_seed.json を spec DDL CHECK 制約で検証 (directive 043b1384).

passport_dino_enemy_master の DDL 制約を seed に適用し、DDL apply 前に
不整合を機械検出する。exit 0 = 全件 spec 整合、1 = 違反あり。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, "dino_enemy_master_seed.json")
DIFF = {"very_easy", "easy", "normal", "hard", "boss"}
RANKS = {"tamago", "hiyoko", "bokensha", "yusha", "okoku_senshi"}
AGE = {"egg", "chick", "adventurer", "hero", "kingdom_warrior"}


def main() -> int:
    d = json.load(open(SEED, encoding="utf-8"))
    e = d["enemies"]
    err = []
    ids = set()
    for i, r in enumerate(e):
        t = f"[{i} {r.get('enemy_id')}]"
        if r["enemy_id"] in ids:
            err.append(f"{t} duplicate enemy_id (PRIMARY KEY)")
        ids.add(r["enemy_id"])
        if r["difficulty"] not in DIFF:
            err.append(f"{t} difficulty CHECK fail: {r['difficulty']}")
        if not r["base_hp"] > 0:
            err.append(f"{t} base_hp>0 CHECK fail: {r['base_hp']}")
        if not r["base_xp"] >= 0:
            err.append(f"{t} base_xp>=0 CHECK fail: {r['base_xp']}")
        if not 1 <= r["drop_tier"] <= 8:
            err.append(f"{t} drop_tier 1..8 CHECK fail: {r['drop_tier']}")
        if r["min_rank_gate"] not in RANKS:
            err.append(f"{t} min_rank_gate unknown: {r['min_rank_gate']}")
        if not r["age_tier_eligibility"] or any(
            a not in AGE for a in r["age_tier_eligibility"]
        ):
            err.append(f"{t} age_tier_eligibility invalid: {r['age_tier_eligibility']}")

    print(f"count={len(e)} unique_ids={len(ids)} declared={d.get('count')}")
    print(f"by_difficulty={d.get('by_difficulty')}")
    if len(e) != 100 or d.get("count") != 100:
        err.append("count != 100 (spec は 100 体)")
    if err:
        print("NG: spec/DDL 整合違反")
        for x in err[:20]:
            print("  -", x)
        return 1
    print("OK: 100 体全件 passport_dino_enemy_master DDL CHECK 整合")
    return 0


if __name__ == "__main__":
    sys.exit(main())
