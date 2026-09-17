#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★両対照★(裁 seq324588「負テスト両対照」)。毒八形だけでは「報せ 0 行」が
★器が黙つた★のか ★判定路が死んで居る★のか 分かれぬ ―― 故に二本 立てる。
  陰性対照 = 正しき十進 3・stdin 即閉 → ★報せ 0 行が正★(倒す事由が無い)
  陽性対照 = 閾 1・stdin を 3 秒 開けた儘 → ★時限切れの報せ 1 行が正★(比較路が生きて居る証)
使ひ方: 50_taishou.py <寫し.sh> <出力.txt>
"""
import io, os, subprocess, sys
src, out = sys.argv[1], sys.argv[2]

def hakaru(th, osoi):
    env = dict(os.environ); env.pop("STOP_HOOK_STDIN_TIMEOUT", None)
    if th is not None:
        env["STOP_HOOK_STDIN_TIMEOUT"] = th
    if osoi:
        # ★遲い書手★ 3秒後に初めて字を出す(NUL は出さぬ) ∴ read -t 1 は時限で切れる
        f = subprocess.Popen(["/bin/sh", "-c", "sleep 3; printf ABCDEFG"],
                             stdout=subprocess.PIPE)
        p = subprocess.run(["/bin/bash", src], stdin=f.stdout, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        f.stdout.close()
        try: f.wait(timeout=10)
        except Exception: f.kill()
    else:
        p = subprocess.run(["/bin/bash", src], input=b"ABCDEFG", env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    so = p.stdout.decode("utf-8", "replace"); se = p.stderr.decode("utf-8", "replace")
    g = lambda k: next((l.split("=", 1)[1] for l in so.split("\n") if l.startswith(k)), "-")
    lines = [l for l in se.split("\n") if l != ""]
    ki = [l for l in lines if l.startswith("[stop_hook]")]
    hoka = [l for l in lines if not l.startswith("[stop_hook]")]
    jigen = sum(1 for l in ki if "時限切れ" in l)
    return p.returncode, g("THRESHOLD="), g("INPUT_LEN="), len(ki), len(hoka), jigen

rows = []
rc, th, ln, ki, hoka, jg = hakaru("3", False)
rows.append(("陰性対照(閾3・即閉)", rc, th, ln, ki, hoka, jg, 0, 0, "報せ0・時限0 が正"))
rc2, th2, ln2, ki2, hoka2, jg2 = hakaru("1", True)
rows.append(("陽性対照(閾1・3秒遲れ)", rc2, th2, ln2, ki2, hoka2, jg2, 1, 1, "報せ1・時限1 が正"))
w = io.open(out, "w", encoding="utf-8")
w.write("# %s ―― 両対照(陰性=倒す事由無し / 陽性=時限切れを實際に踏ませる)\n" % src)
w.write("# 対照\trc\t閾\t讀めた字数\t器の報せ行\t外の声行\t時限切れ行\t期待報せ\t期待時限\t判じ\n")
for r in rows:
    ok = "○" if (r[4] == r[7] and r[6] == r[8]) else "×"
    w.write("\t".join(str(x) for x in r) + "\t" + ok + "\n")
w.close()
sys.stderr.write("対照了: %s\n" % out)
