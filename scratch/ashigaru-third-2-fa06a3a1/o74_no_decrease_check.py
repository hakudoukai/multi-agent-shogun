#!/usr/bin/env python3
"""PR#140 merge 後の検算: source_code_cache から ★減つた file_path が 0 本か★ を測る規。

★DB へ触れぬ★。上官が打つた SELECT の出力 (csv 2 本) を突き合はせるだけ。
  pre  = merge 前の写し (総監督 2026-09-08・4,249 行・sha256 先頭 a98d3b07f289c7de)
  post = 初回 CI 走行後に同じ SELECT を打つた出力

★「減」の定義★: pre に在つた file_path のうち post に無い本数。1 = file_path 1 本。
★行数の差ではない★ ―― CI は書き足すゆゑ、増が減を隠す (四条③: 意味の違ふ数を足し引きせぬ)。

使ひ方: python3 o74_no_decrease_check.py <pre.csv> <post.csv> [--expect-pre 4249]
戻り値: 減 0 なら 0、減 1 本以上なら 1、csv が読めねば 2。
"""
import csv
import hashlib
import sys


def load_paths(path: str) -> list[str]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows or "file_path" not in rows[0]:
        raise SystemExit(f"-- ERR: file_path 列が無い: {path}")
    return [r["file_path"] for r in rows]


def sha256_16(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    pre_p, post_p = sys.argv[1], sys.argv[2]
    expect_pre = None
    if "--expect-pre" in sys.argv:
        expect_pre = int(sys.argv[sys.argv.index("--expect-pre") + 1])
    pre_list, post_list = load_paths(pre_p), load_paths(post_p)
    pre, post = set(pre_list), set(post_list)
    print(f"-- pre : {pre_p} sha256_16={sha256_16(pre_p)} 行={len(pre_list)} 一意={len(pre)}")
    print(f"-- post: {post_p} sha256_16={sha256_16(post_p)} 行={len(post_list)} 一意={len(post)}")
    if len(pre_list) != len(pre):
        print(f"-- 註: pre に file_path の重複 {len(pre_list) - len(pre)} 本 (鍵は file_path 1 列ゆゑ本来 0)")
    if len(post_list) != len(post):
        print(f"-- 註: post に file_path の重複 {len(post_list) - len(post)} 本")
    if expect_pre is not None and len(pre_list) != expect_pre:
        print(f"-- 註: pre の行数 {len(pre_list)} は申告 {expect_pre} と違ふ (写しが別物の疑ひ)")
    gone = sorted(pre - post)
    added = sorted(post - pre)
    print(f"-- 減(pre に在り post に無い file_path) = {len(gone)} 本")
    print(f"-- 増(post にのみ在る file_path)       = {len(added)} 本")
    for x in gone[:20]:
        print(f"--   減: {x}")
    if len(gone) > 20:
        print(f"--   … 他 {len(gone) - 20} 本")
    return 1 if gone else 0


if __name__ == "__main__":
    sys.exit(main())
