#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ★甲の子の stub★ 生の scripts/pane_enter_watcher.py は呼ばぬ・触らぬ。
# 親 L52 の env 渡しで何が届いたかを repr で刷り、親の環を止める為 rc=0 で退く。
import os, sys, signal
for k in ("LIVE", "STALE_SEC", "POLL_SEC"):
    print("子が受けた %s=%r" % (k, os.environ.get(k, "<未設定>")), flush=True)
print("argv=%r" % (sys.argv[1:],), flush=True)
os.kill(os.getppid(), signal.SIGTERM)   # 親(写し)の無限環を此処で断つ
sys.exit(0)
