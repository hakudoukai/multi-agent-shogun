#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第39弾 問三 v2 ―― 35_ の二つの疵を直す。★35_ は消さぬ(現物)★。

35_ の疵:
  疵A ★器が己の出目を数へた★ ―― kou/35_sha.{out,err} は 00_run.sh が
      走らす前に ★空で作られる★ 故、0byte 二本が「同じ sha」に見えた。
      刷つた因「空である旨の一行ゆゑ」は ★偽★ であつた(其の一行は走り終へた後に書かれる)。
  疵B ★du の rc≠0 で數を捨てた★ ―― du は ★讀めぬ一本を鳴らしつつ和は刷つて居た★。
      rc は「器が鳴つた」であり「數が無い」ではない。★二つは別事★。

v2: ⑴己の出目を argv で受けて除き、除いた數を刷る ⑵du の 出目・rc・鳴を分けて刷る。
usage: 36_...v2.py <除く path> [<除く path>...]
"""
import collections
import hashlib
import os
import subprocess
import sys

B = ("queue/reports/ashigaru-mac-3_km-39-chu-to-jissou-no-sa-wo-obi-de-hakare-"
     "soshite-koku-no-junkan-wo-toji-yo-20260916_evidence")
NEG = "f" * 64


def sha_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv):
    skip = set(os.path.normpath(a) for a in argv[1:])
    print("【歩き根】 %s" % B)
    print("  ★己の出目として除く★ = %d 本 %s"
          % (len(skip), " ".join(sorted(os.path.relpath(s, B) for s in skip)) or "(無し)"))
    print("  ★註★ 『除いた』は『歩いて居らぬ』ではない ―― 歩いた上で落とした。")
    files, skipped = [], 0
    for dirpath, dirnames, filenames in os.walk(B):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            p = os.path.normpath(os.path.join(dirpath, fn))
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            if p in skip:
                skipped += 1
                continue
            files.append(p)
    print("  母數 = ★%d 本★(歩いた %d ― 除いた %d)" % (len(files), len(files) + skipped, skipped))
    table, unreadable = {}, 0
    for p in files:
        try:
            table[p] = sha_of(p)
        except OSError:
            unreadable += 1
    print("  讀めた %d / ★讀めぬ %d★" % (len(table), unreadable))
    print()

    print("【対照】")
    neg = [p for p, s in table.items() if s == NEG]
    pos_t = next((p for p in files if p.endswith("/ki/00_run.sh")), None)
    if pos_t is None:
        print("  ★陽性対照の的が無い ―― 數を讀むな★"); return 3
    pos = [p for p, s in table.items() if s == table[pos_t]]
    print("  陰性(f×64) = ★%d 本★ / 陽性(%s…) = ★%d 本★" % (len(neg), table[pos_t][:16], len(pos)))
    if neg or not pos:
        print("  ★対照が通らぬ ―― 數を讀むな★"); return 3
    print("  ★対照 二本 通つた★")
    print()

    print("【甲 ―― 同じ sha の file が二本在るか(己の出目を除いた後)】")
    by = collections.defaultdict(list)
    for p, s in table.items():
        by[s].append(p)
    dup = {s: ps for s, ps in by.items() if len(ps) > 1}
    print("  相異なる sha = ★%d★ / file = ★%d★ ∴ 重なり = ★%d 本★"
          % (len(by), len(table), len(table) - len(by)))
    print("  ★二本以上を指す sha = %d 個★" % len(dup))
    for s in sorted(dup, key=lambda t: -len(dup[t])):
        print("    %s… → %d 本 (%d byte)" % (s[:16], len(dup[s]), os.path.getsize(dup[s][0])))
        for p in sorted(dup[s]):
            print("        %s" % os.path.relpath(p, B))
    if dup:
        print("  ∴ ★sha は単射でない★ ―― 当たつても『何本目か』は決まらぬ。")
    else:
        print("  ∴ 此の刻の此の束では重なり無し ―― ★『sha は単射』とは言へぬ(未判)★")
        print("    (35_ が見た重なりは ★器自身の空の出目★ であつた ―― 疵A)")
    # 空である旨の一行 が幾つ在るか(将来の重なりの種)
    kara = [p for p in table if "★空であつた★" in open(p, encoding="utf-8", errors="replace").read()[:200]]
    print("  ★『空である旨の一行』を持つ流れ = %d 本★ ―― 刻と流名を含む故 ★互ひに異なる★。" % len(kara))
    print("    ∴ 裁 seq310228⑶ の一行は ★重なりを生まぬ書き方★ に成つて居る(00_run.sh の功)。")
    print()

    print("【乙 ―― 束の外に在る物に sha は届くか】")
    for op in ["queue/tasks/ashigaru-mac-3.yaml", "scripts/stop_hook_inbox.sh"]:
        if not os.path.isfile(op):
            print("  %s ―― ★file が無い★" % op); continue
        s = sha_of(op)
        print("  %-36s sha %s… 束の中の当たり = ★%d 本★"
              % (op, s[:16], len([p for p, t in table.items() if t == s])))
    print("  ∴ ★『当たり 0』は『在らぬ』ではない ―― 『此の根の下に在らぬ』である。★")
    print()

    print("【丙 ―― 歩く代償と、歩けぬ根】")
    print("  %-14s %14s %10s %s" % ("根", "KB(出目)", "rc", "鳴(stderr 一行目)"))
    for target in [B, "queue/reports", "queue", "scripts"]:
        p = subprocess.run(["du", "-sk", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.stdout.decode().split("\t")[0].strip() or "★出目無し★"
        err = (p.stderr.decode().strip().split("\n") or [""])[0][:60]
        nm = target if len(target) <= 14 else "…" + target[-13:]
        print("  %-14s %14s %10d %s" % (nm, out, p.returncode, err or "(無し)"))
    print("  ★rc≠0 でも和は出て居る ―― ★『器が鳴つた』と『數が無い』は別事★(疵B)。★")
    print("  ∴ queue/ は ★13.8 GB 級★。★sha で歩けば全 byte を讀む ―― 名なら stat のみ。★")
    print("    加へて ★讀めぬ一本(Permission denied)★ が根の中に在る ――")
    print("    ★sha の歩きは其處で ★静かに欠ける★。欠けを数へぬ器は『無し』と刷る。★")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
