#!/usr/bin/env python3
"""dino asset 検知・統合チェック (directive 0ad2abf5).

asset_manifest.json の各 slot について、final.expected_path に
placeholder でない実画像が存在するか検知し、貼り込み可否を判定する。

実画像が現れたら 1 コマンドで「検知 → 採用判定」が回るようにするための
検証器。実貼り込み (placeholder 削除 + current.kind=final 更新) は
本スクリプトの判定が real=OK になった slot に対し swap_procedure を適用する。

exit code: 0 = 検証成功 (実画像 0 でも整合していれば 0), 1 = 整合崩れ
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "asset_manifest.json")
IMG_EXT = (".webp", ".png", ".jpg", ".jpeg")


def main() -> int:
    m = json.load(open(MANIFEST, encoding="utf-8"))
    real, placeholder, broken = [], [], []
    for a in m.get("assets", []):
        key = a["asset_key"]
        ph = a["current"]["path"]
        final = a.get("final", {})
        exp = final.get("expected_path") or final.get("expected_path_pattern", "")
        repo_root = os.path.dirname(os.path.dirname(HERE))
        ph_abs = os.path.join(repo_root, ph)
        exp_abs = os.path.join(repo_root, exp) if exp and "{" not in exp else None
        has_real = bool(exp_abs and os.path.isfile(exp_abs)
                        and exp_abs.lower().endswith(IMG_EXT))
        if has_real:
            real.append(key)
        elif os.path.isfile(ph_abs):
            placeholder.append(key)
        else:
            broken.append(key)

    print(f"real_image_integrated : {len(real)} {real}")
    print(f"placeholder_pending   : {len(placeholder)} {placeholder}")
    print(f"broken_slot           : {len(broken)} {broken}")
    print(f"total_slots           : {len(m.get('assets', []))}")
    if broken:
        print("NG: placeholder も実画像も無い slot あり (整合崩れ)")
        return 1
    print("OK: 全 slot が placeholder か実画像で解決 (整合維持)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
