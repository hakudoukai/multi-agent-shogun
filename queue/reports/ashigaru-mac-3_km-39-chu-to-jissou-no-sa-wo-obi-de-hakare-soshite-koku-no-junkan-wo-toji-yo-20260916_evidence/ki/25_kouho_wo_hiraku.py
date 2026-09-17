#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第39弾 問一 ㋔ の続 ―― 候補 42 の内 ★生きた本の 18★ を開いて、裁く材を束に残す。

★裁くのは人である。★ 此の器は ★字を運ぶのみ★ ―― 註の行と、其の後 12 行を刷る。
控(名に bak を含む)24 本は生きた本の写しゆゑ此処では開かぬ ―― ★除いたと書く★。
"""
import os
import sys

# 20_ の出目から ★生きた本のみ★ を書き取つた(控 24 本は除く)
TARGETS = [
    ("scripts/checks/ephemeral_worktree_hygiene.sh", 12),
    ("scripts/checks/karo_mac_dasumae_gate.sh", 42),
    ("scripts/checks/karo_mac_gate4.sh", 61),
    ("scripts/commander_send_shogun_second.sh", 69),
    ("scripts/fukuincho_desktop_poke.py", 331),
    ("scripts/inbox_watcher.sh", 57),
    ("scripts/inbox_watcher.sh", 561),
    ("scripts/inbox_watcher.sh", 568),
    ("scripts/inbox_watcher.sh", 712),
    ("scripts/inbox_watcher.sh", 841),
    ("scripts/inbox_watcher.sh", 1028),
    ("scripts/inbox_watcher.sh", 1111),
    ("scripts/inbox_watcher.sh", 1323),
    ("scripts/inbox_watcher.sh", 1543),
    ("scripts/karo_overload_monitor.sh", 487),
    ("scripts/ratelimit_check.sh", 335),
    ("scripts/stop_hook_inbox.sh", 71),
    ("scripts/stop_hook_inbox.sh", 72),
]
AFTER = 12


def main():
    print("【裁く材】 生きた本の候補 = ★%d 本★(控 24 本は写しゆゑ除いた ―― ★歩いては居る★)" % len(TARGETS))
    print("  刷るは 註の行 + 其の後 %d 行。★裁は此処に書かぬ。紙に書く。★" % AFTER)
    missing = 0
    for path, ln in TARGETS:
        if not os.path.isfile(path):
            print("\n══ %s:%d ―― ★file が無い★" % (path, ln))
            missing += 1
            continue
        lines = open(path, encoding="utf-8").read().split("\n")
        print("\n══ %s:%d ══" % (path, ln))
        for j in range(ln, min(ln + AFTER, len(lines)) + 1):
            mark = "註→" if j == ln else "   "
            print("  %s L%-5d| %s" % (mark, j, lines[j - 1][:150]))
    print("\n★無かつた file = %d★" % missing)
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
