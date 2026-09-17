#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stop_hook_inbox.sh から ★stdin 時限読みの塊★ だけを切り出し、單独で走る寫しを作る。
★行番号を焼き込まぬ★(memory: Never hardcode a line number; locate by verbatim)。
  始= `STOP_HOOK_STDIN_TIMEOUT="${STOP_HOOK_STDIN_TIMEOUT:-10}"`(直し形は其の上の num_same_op() から)
  終= `if IFS= read` 以後 最初の 行頭 `fi`
出目は stdout へ「閾と讀めた字数」・判定は原器の儘 stderr へ出る(二つの路を混ぜぬ)。
使ひ方: 10_slice.py <src.sh> <out.sh>
"""
import io, sys
src, out = sys.argv[1], sys.argv[2]
L = io.open(src, encoding="utf-8").read().split("\n")
TH = 'STOP_HOOK_STDIN_TIMEOUT="${STOP_HOOK_STDIN_TIMEOUT:-10}"'
i = next(n for n, l in enumerate(L) if l.strip() == TH)
# 直し形: 直上に num_same_op() が在れば其処から取る
j = i
for n in range(i - 1, max(-1, i - 25), -1):
    if L[n].startswith("num_same_op()"):
        j = n
        break
k = next(n for n, l in enumerate(L) if l.startswith("if IFS= read"))
e = next(n for n in range(k, len(L)) if L[n] == "fi")
body = L[j:e + 1]
head = ["#!/usr/bin/env bash",
        "# ★寫し★ 10_slice.py が %s から切り出した(手で書いて居らぬ)" % src,
        "set -euo pipefail"]
tail = ['printf "THRESHOLD=%s\\n" "$STOP_HOOK_STDIN_TIMEOUT"',
        'printf "INPUT_LEN=%s\\n" "${#INPUT}"']
io.open(out, "w", encoding="utf-8").write("\n".join(head + body + tail) + "\n")
sys.stderr.write("切つた: %s → %s (%d行・始=%d 終=%d)\n" % (src, out, len(head) + len(body) + len(tail), j + 1, e + 1))
