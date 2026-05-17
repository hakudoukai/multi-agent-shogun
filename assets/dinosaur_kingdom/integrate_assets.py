#!/usr/bin/env python3
"""dino 実画像 自動取込 executor (directive c5d565bb).

asset_manifest.json の各 slot を走査し、final.expected_path に
placeholder でない実画像 (.webp/.png/.jpg/.jpeg) が出現したら:
  1. 対応する *.placeholder.svg を削除
  2. manifest の current を {kind:final, path:expected_path} に更新
  3. final.status を 'integrated' に更新
を実施する。これにより 3rd-PC が実画像を expected_path へ置いた瞬間、
1 コマンドで「貼り込み」が完了する (asset_key 不変ゆえ app 側コード変更不要)。

既定は dry-run (--apply 指定時のみ実書込)。実画像 0 件なら swap 0 件で
安全に no-op。--self-test で swap ロジックを一時 fixture で検証。

exit: 0 = 正常 (swap 0 でも OK), 1 = 整合崩れ/エラー
"""
import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MANIFEST = os.path.join(HERE, "asset_manifest.json")
IMG_EXT = (".webp", ".png", ".jpg", ".jpeg")


def _scan(manifest, repo_root):
    """returns (to_swap, pending, broken) lists of asset_key."""
    to_swap, pending, broken = [], [], []
    for a in manifest.get("assets", []):
        final = a.get("final", {})
        exp = final.get("expected_path")
        cur_path = a.get("current", {}).get("path", "")
        cur_kind = a.get("current", {}).get("kind")
        real = bool(
            exp and "{" not in exp
            and os.path.isfile(os.path.join(repo_root, exp))
            and exp.lower().endswith(IMG_EXT)
        )
        if real and cur_kind != "final":
            to_swap.append(a["asset_key"])
        elif cur_kind == "final":
            continue
        elif cur_path and os.path.isfile(os.path.join(repo_root, cur_path)):
            pending.append(a["asset_key"])
        else:
            broken.append(a["asset_key"])
    return to_swap, pending, broken


def _do_swap(manifest, repo_root, apply):
    swapped = []
    for a in manifest.get("assets", []):
        final = a.get("final", {})
        exp = final.get("expected_path")
        if not exp or "{" in exp:
            continue
        if not (os.path.isfile(os.path.join(repo_root, exp))
                and exp.lower().endswith(IMG_EXT)):
            continue
        if a.get("current", {}).get("kind") == "final":
            continue
        ph = a.get("current", {}).get("path", "")
        ph_abs = os.path.join(repo_root, ph)
        if apply:
            if ph.endswith(".placeholder.svg") and os.path.isfile(ph_abs):
                os.remove(ph_abs)
            a["current"] = {"kind": "final", "path": exp, "renderable": True}
            final["status"] = "integrated"
        swapped.append({"asset_key": a["asset_key"], "from": ph, "to": exp})
    return swapped


def self_test():
    """合成 fixture で swap ロジックを検証 (本番 manifest 不変)。"""
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "x"))
        ph = "x/foo.placeholder.svg"
        real = "x/foo.webp"
        open(os.path.join(d, ph), "w").write("<svg/>")
        open(os.path.join(d, real), "wb").write(b"\x00")
        m = {"assets": [{
            "asset_key": "t/foo",
            "current": {"kind": "placeholder", "path": ph},
            "final": {"expected_path": real, "status": "awaiting"},
        }]}
        sw = _do_swap(m, d, apply=True)
        ok = (
            len(sw) == 1
            and not os.path.isfile(os.path.join(d, ph))
            and m["assets"][0]["current"]["kind"] == "final"
            and m["assets"][0]["final"]["status"] == "integrated"
        )
        print("self_test:", "OK" if ok else "NG", sw)
        return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true", help="実書込 (既定 dry-run)")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        return self_test()

    m = json.load(open(MANIFEST, encoding="utf-8"))
    to_swap, pending, broken = _scan(m, REPO)
    print(f"detected_real(to_swap)={len(to_swap)} {to_swap}")
    print(f"placeholder_pending={len(pending)} {pending}")
    print(f"broken={len(broken)} {broken}")
    if broken:
        print("NG: placeholder も実画像も無い slot あり")
        return 1
    sw = _do_swap(m, REPO, apply=args.apply)
    if args.apply and sw:
        json.dump(m, open(MANIFEST, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(f"APPLIED {len(sw)} swap(s):")
    else:
        print(f"DRY-RUN {len(sw)} swap candidate(s) "
              f"(--apply で実行):" if sw else "no real images yet -> 0 swap")
    for s in sw:
        print("  ", s["asset_key"], s["from"], "->", s["to"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
