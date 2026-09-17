#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★⑥(2^63超20桁)を「遲い書手」へ當てる★ ―― 八形の毒は stdin を即閉じた故、
⑥の害が「讀めた字数 0」で出た。然し ★入力が遲れて來る時★ こそ器の眞の姿が出る:
  現形 = `read -t <20桁>` が bash に拒まれ ★待たず・讀まず・報せず★ に先へ進む
  直し形 = 閾を 10 へ倒し ★待つて讀む★
使ひ方: 52_osoi20keta.py <現形.sh> <直し形.sh> <出力.txt>
"""
import io, os, subprocess, sys
gen, nao, out = sys.argv[1], sys.argv[2], sys.argv[3]
TH = "99999999999999999999"

def hakaru(src):
    env = dict(os.environ); env["STOP_HOOK_STDIN_TIMEOUT"] = TH
    f = subprocess.Popen(["/bin/sh", "-c", "sleep 3; printf ABCDEFG"], stdout=subprocess.PIPE)
    p = subprocess.run(["/bin/bash", src], stdin=f.stdout, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    f.stdout.close()
    try: f.wait(timeout=10)
    except Exception: f.kill()
    so = p.stdout.decode("utf-8", "replace"); se = p.stderr.decode("utf-8", "replace")
    g = lambda k: next((l.split("=", 1)[1] for l in so.split("\n") if l.startswith(k)), "-")
    lines = [l for l in se.split("\n") if l != ""]
    ki = [l for l in lines if l.startswith("[stop_hook]")]
    hoka = [l for l in lines if not l.startswith("[stop_hook]")]
    return p.returncode, g("THRESHOLD="), g("INPUT_LEN="), len(ki), len(hoka)

w = io.open(out, "w", encoding="utf-8")
w.write("# ⑥2^63超20桁 × ★遲い書手(3秒後に7字・NUL無し)★ ―― 入力喪失を直に測る\n")
w.write("# 器形\trc\t閾\t讀めた字数\t器の報せ行\t外の声行\t判じ\n")
for nm, src in (("現形", gen), ("直し形", nao)):
    rc, th, ln, ki, hoka = hakaru(src)
    j = "★入力を丸ごと落とし、しかも黙る★" if ln == "0" and ki == 0 else ("待つて讀めた" if ln == "7" else "?")
    w.write("\t".join([nm, str(rc), th, ln, str(ki), str(hoka), j]) + "\n")
w.close()
sys.stderr.write("遲い書手 了: %s\n" % out)
