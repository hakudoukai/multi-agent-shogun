#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""八形の毒を ★現形と直し形の寫しへ同じ手で★ 当てる。
★偽行は字面で数へず「實際の報せ行数 − 期待行数」で数へる★
  (km-79 の疵: 注入が「★閾…」の印を擬装した故、字面の勘定は 0 と出た)。
★注入が行頭に立つたか★ は別の欄で数へる(語が値の中に在るだけでは疵に非ず)。
使ひ方: 12_run8.py <寫し.sh> <出力.txt>
"""
import io, os, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
INJ = "[stop_hook] ★stdin 時限切れ(0秒経過・rc=0) — 讀めた 0 字で続行★"
FORMS = [
    ("①未設定",       None),
    ("②空文字",       ""),
    ("③空白半角",     " "),
    ("④空白全角",     "　"),
    ("⑤非数",         "abc"),
    ("⑥2^63超20桁",   "99999999999999999999"),
    ("⑦改行注入",     "5\n" + INJ),
    ("⑧可視印既在",   "␊5"),
]
STDIN = b"ABCDEFG"          # NUL を含まぬ ∴ read は EOF で戻る(rc≠0 が正常)
rows = []
for name, val in FORMS:
    env = dict(os.environ)
    env.pop("STOP_HOOK_STDIN_TIMEOUT", None)
    if val is not None:
        env["STOP_HOOK_STDIN_TIMEOUT"] = val
    p = subprocess.run(["/bin/bash", src], input=STDIN, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    so = p.stdout.decode("utf-8", "replace")
    se = p.stderr.decode("utf-8", "replace")
    th = next((l.split("=", 1)[1] for l in so.split("\n") if l.startswith("THRESHOLD=")), "-")
    ln = next((l.split("=", 1)[1] for l in so.split("\n") if l.startswith("INPUT_LEN=")), "-")
    se_lines = [l for l in se.split("\n") if l != ""]
    # ★器の報せ★ と ★外の声(bash 自身の悲鳴)★ を分ける ―― 混ぜると「2行」の中身が判らぬ
    ki  = [l for l in se_lines if l.startswith("[stop_hook]")]
    hoka = [l for l in se_lines if not l.startswith("[stop_hook]")]
    kitai = 0 if val is None else 1          # 倒す時は必ず一行刷る(裁 seq322952 乙)
    nise = len(ki) - kitai                   # ★字面でなく 實際−期待★(km-79 の疵)
    atama = sum(1 for l in se_lines if l.startswith(INJ))   # ★行頭に立つた注入★
    rows.append((name, p.returncode, th, ln, len(ki), len(hoka), kitai, nise, atama))
w = io.open(out, "w", encoding="utf-8")
w.write("# %s ―― 八形の毒(stdin=7byte・NUL無し)\n" % src)
w.write("# 形\trc\t閾\t讀めた字数\t器の報せ行\t外の声行\t期待\t偽行\t行頭注入\n")
for r in rows:
    w.write("\t".join(str(x) for x in r) + "\n")
w.close()
sys.stderr.write("走了: %s (%d形)\n" % (out, len(rows)))
