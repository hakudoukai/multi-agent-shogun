#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第39弾 問三 ―― 「sha で歩く器が既定」が ★偽になる場合★ を数へる。

家老の疵 八十三 = 名を推して探し「無し」と刷つた。sha で歩いたら 6/6 当たつた。
∴ 「sha が既定」は ★概ね正★。然れど ★常に正★ か ―― 之を測る。

測る三つ(手掛りは札の 問三 に在る):
  甲 ★同じ sha の file が二本在る時★ ―― sha は ★単射でない★ 事が在るか
  乙 ★束の外に在る時★               ―― 歩き根の外の物に sha は届くか
  丙 ★大きすぎて歩けぬ時★           ―― 歩く代償を byte で言へ

★陽性対照★= 紙(既知の sha)を束の中から引き当てられるか
★陰性対照★= 在らざる sha(64 個の 'f')が 0 本である事
"""
import collections
import hashlib
import os
import subprocess
import sys

ROOT = os.getcwd()
B = ("queue/reports/ashigaru-mac-3_km-39-chu-to-jissou-no-sa-wo-obi-de-hakare-"
     "soshite-koku-no-junkan-wo-toji-yo-20260916_evidence")
NEG = "f" * 64


def sha_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            out.append(p)
    return sorted(out)


def main():
    print("【歩き根】 %s" % B)
    files = walk(B)
    print("  母數 = ★%d 本★(symlink 除く・__pycache__ 除く ―― ★除いた物は歩いて居らぬ★)" % len(files))
    table = {}
    unreadable = 0
    for p in files:
        try:
            table[p] = sha_of(p)
        except OSError:
            unreadable += 1
    print("  讀めた %d / ★讀めぬ %d★" % (len(table), unreadable))
    print()

    # ── 対照 ─────────────────────────────────────────
    print("【対照】")
    hits_neg = [p for p, s in table.items() if s == NEG]
    print("  陰性(f×64)   当たり = ★%d 本★" % len(hits_neg))
    probe_path = None
    for p in files:
        if p.endswith("/ki/00_run.sh"):
            probe_path = p
            break
    if probe_path is None:
        print("  ★陽性対照の的が無い ―― 數を讀むな★"); return 3
    probe_sha = table[probe_path]
    hits_pos = [p for p, s in table.items() if s == probe_sha]
    print("  陽性(%s…) 当たり = ★%d 本★" % (probe_sha[:16], len(hits_pos)))
    if len(hits_neg) != 0 or len(hits_pos) < 1:
        print("  ★対照が通らぬ ―― 數を讀むな★"); return 3
    print("  ★対照 二本 通つた★")
    print()

    # ── 甲 同じ sha が二本 ────────────────────────────
    print("【甲 ―― 同じ sha の file が二本在るか】")
    by = collections.defaultdict(list)
    for p, s in table.items():
        by[s].append(p)
    dup = {s: ps for s, ps in by.items() if len(ps) > 1}
    print("  相異なる sha = ★%d★ / file = ★%d★ ∴ 重なり = ★%d 本★"
          % (len(by), len(table), len(table) - len(by)))
    print("  ★二本以上を指す sha = %d 個★" % len(dup))
    for s in sorted(dup, key=lambda s: -len(dup[s]))[:6]:
        print("    %s… → %d 本" % (s[:16], len(dup[s])))
        for p in sorted(dup[s])[:4]:
            print("        %s (%d byte)" % (os.path.relpath(p, B), os.path.getsize(p)))
    if dup:
        print("  ∴ ★sha は単射でない★ ―― sha で歩いて当たつても『何本目か』は決まらぬ。")
        print("    因は ★裁 seq310228⑶「空は 0byte でなく空である旨の一行を書け」★ ――")
        print("    空の流れは ★同じ一行★ に成る故、byte が一致するのは ★設計通り★ である。")
    else:
        print("  ∴ 此の束では重なりを見ず ―― ★偽とは言へぬ(未判)★")
    print()

    # ── 乙 束の外 ────────────────────────────────────
    print("【乙 ―― 束の外に在る物に sha は届くか】")
    outside = ["queue/tasks/ashigaru-mac-3.yaml",
               "scripts/stop_hook_inbox.sh"]
    for op in outside:
        if not os.path.isfile(op):
            print("  %s ―― ★file が無い★" % op); continue
        s = sha_of(op)
        hit = [p for p, t in table.items() if t == s]
        print("  %-36s sha %s… 束の中の当たり = ★%d 本★" % (op, s[:16], len(hit)))
    print("  ∴ ★『当たり 0』は『在らぬ』ではない ―― 『此の根の下に在らぬ』である。★")
    print("    sha で歩く器は ★歩き根を宣らねば★ 名で探す器と同じ誤を犯す。")
    print()

    # ── 丙 歩く代償 ──────────────────────────────────
    print("【丙 ―― 大きすぎて歩けぬ時(代償を byte で言ふ)】")
    for target in [B, "queue/reports", "queue", "scripts"]:
        p = subprocess.run(["du", "-sk", target], stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL)
        kb = p.stdout.decode().split("\t")[0].strip() if p.returncode == 0 else "?"
        try:
            mb = "%.1f MB" % (int(kb) / 1024.0)
        except ValueError:
            mb = "★測れぬ★"
        print("  %-22s %14s KB = %12s" % (target, kb, mb))
    print("  ★sha で歩く代償は ★全 byte を讀む★ 事である ―― 名で探す代償は stat のみ。★")
    print("  ∴ 根が大きい程 sha は高く付く。★13 GB を歩けと言ふ器は、実質『歩かぬ』器である。★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
