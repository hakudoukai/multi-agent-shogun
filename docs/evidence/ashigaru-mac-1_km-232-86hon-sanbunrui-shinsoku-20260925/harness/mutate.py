#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 陽性對照の変異体を作る。各置換は★丁度1回★を assert する（0回/2回なら rc=3 で止まる）。
import sys
src, dst = sys.argv[1], sys.argv[2]
t = open(src, encoding="utf-8").read()
REPL = [
    ("# ─── Testing guard ───\n",
     "echo KM232_PROBE_SRC_OUT\necho KM232_PROBE_SRC_ERR >&2\n# ─── Testing guard ───\n"),
    ("process_unread() {\n",
     "process_unread() {\n    echo KM232_PROBE_PU_OUT\n"),
    ("agent_is_busy() {\n",
     "agent_is_busy() {\n    echo KM232_PROBE_AIB_OUT\n    echo KM232_PROBE_AIB_ERR >&2\n"),
]
for old, new in REPL:
    n = t.count(old)
    print(f"count={n} old={old.strip()!r}")
    if n != 1:
        sys.exit(3)
    t = t.replace(old, new)
open(dst, "w", encoding="utf-8").write(t)
