#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kou_env_parse.py ―― 甲の子器 pane_enter_watcher.py の ★env 讀み三行を逐語で抜いた★物。
逐語の出處: scripts/pane_enter_watcher.py L131 / L134 / L138 (43_chokugo.txt に控)。
子器を丸ごと走らせぬ理由: 本 Mac では pane_exists が ★不在 pane にも True を返す★(41_na.out)
∴ 丸走は捕捉→送出の枝へ入り得る = 危險。故に ★毒の当たる行だけ★ を同じ字で走らせる。
"""
import os
import sys

DEFAULT_STALE_SEC = 300
DEFAULT_POLL_SEC = 10
which = sys.argv[1]
if which == 'STALE_SEC':
    v = int(os.environ.get("STALE_SEC", DEFAULT_STALE_SEC))     # ← L131 逐語
    print("枝: stale_sec=%d" % v)
elif which == 'POLL_SEC':
    v = int(os.environ.get("POLL_SEC", DEFAULT_POLL_SEC))       # ← L134 逐語
    print("枝: poll_sec=%d" % v)
elif which == 'LIVE':
    live = os.environ.get("LIVE", "0") == "1"                   # ← L138 逐語
    print("枝: LIVE=%s → %s" % (live, "実 Enter 送出" if live else "DRY-RUN(縮退)"))
sys.exit(0)
