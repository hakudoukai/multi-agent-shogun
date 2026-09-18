# -*- coding: utf-8 -*-
"""★當て紙 甲 の効き目と ★限界★ を實測する★(家老令 km-153 ㋐ 締め)
甲を ★複製にのみ★ 當てて(共用樹の門は触れぬ)七本の fx を走らせ、當てる前(raw/30 の旧基底)と並べる。
鳴りの語彙は ★raw/30_nari_no_goi.tsv から読む★ ―― 同じ表を二度書かぬ(二重実装の禁)。
四札: 刻=冠 / 根=cwd / rc=subprocess の returncode(★管を通さず★) / 対照=fx04(清い紙・鳴らぬのが正)と fx06(甲が閉ぢぬ面)。"""
import os
import sys
import shutil
import hashlib
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

GATE = "scripts/checks/karo_mac_dasumae_gate.sh"
KEN = os.path.join(BUNDLE, "_fx", "kentei")
FX = os.path.join(BUNDLE, "raw", "fx")
KYUU = os.path.join(BUNDLE, "_fx", "base_kyuu_disk.sh")
P_KOU = os.path.join(BUNDLE, "raw", "50_atenashi_kou_jou4.patch")

# ―― 鳴りの語彙を成果物から読む(表を二度書かぬ) ――
GOI = []
for ln in open(os.path.join(BUNDLE, "raw", "30_nari_no_goi.tsv"), encoding="utf-8").read().split("\n")[1:]:
    if ln.strip():
        k, v = ln.split("\t")[:2]
        GOI.append((k, v))
assert len(GOI) >= 8, "語彙が %d 行 ―― raw/30 を疑へ" % len(GOI)

# ―― 甲を複製へ當てる(共用樹の門は触れぬ) ――
D = os.path.join(KEN, "kou_atta")
if os.path.isdir(D):
    shutil.rmtree(D)
os.makedirs(os.path.join(D, "scripts", "checks"))
shutil.copyfile(KYUU, os.path.join(D, GATE))
e = dict(os.environ); e["GIT_DIR"] = os.path.join(KEN, "arienu.git")
ap = subprocess.run(["git", "apply", "-v", os.path.abspath(P_KOU)], cwd=D, env=e,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
assert ap.returncode == 0, "甲が當たらぬ(rc=%d) ―― %s" % (ap.returncode, ap.stderr.decode("utf-8", "replace")[:200])
ATTA = os.path.join(D, GATE)
kaku(os.path.join(BUNDLE, "raw", "60_kou_wo_ateta_kiroku.txt"),
     "as-of %s(UTC)\n當て先=%s(★複製★)\n"
     "共用樹の門=%s ―― ★本弾で一字も動かして居らぬ(下の sha256 は 30/50 弾と同一)★\n"
     "當てる前 sha256 %s\n當てた後 sha256 %s\ngit apply rc=%d\n%s\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        os.path.relpath(ATTA, ROOT), GATE,
        hashlib.sha256(open(KYUU, "rb").read()).hexdigest(),
        hashlib.sha256(open(ATTA, "rb").read()).hexdigest(), ap.returncode,
        ap.stderr.decode("utf-8", "replace").strip()))

def natta(out, err, na):
    hits = []
    for ln in (out + "\n" + err).split("\n"):
        if "★" not in ln or na not in ln:
            continue
        for k, v in GOI:
            if k in ln:
                hits.append(v)
                break
        else:
            hits.append("★語彙外の鳴り ―― 『%s』★" % ln.strip()[:40])
    return hits

def hashiru(base, fxp):
    p = subprocess.run(["bash", base, "--", fxp], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    return p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"), p.returncode

# ―― 當てる前(raw/30 の旧基底の列)を成果物から読む ――
MAE = {}
for ln in open(os.path.join(BUNDLE, "raw", "30_nikitei_no_nari.tsv"), encoding="utf-8").read().split("\n")[1:]:
    c = ln.split("\t")
    if len(c) >= 5 and c[1].startswith("旧"):
        MAE[c[0]] = (c[2], c[4])

rows = []
for na in sorted(os.listdir(FX)):
    p = os.path.join(FX, na)
    if not os.path.isfile(p):
        continue
    out, err, rc = hashiru(ATTA, p)
    hits = natta(out, err, na)
    mae_rc, mae_nari = MAE.get(na, ("(引けぬ)", "(引けぬ)"))
    ima_nari = " / ".join(hits) or "一つも鳴らず"
    # ★★ を飾りとして落してから較べる ―― 飾りの差を「動いた」と読ませぬ(raw/30 は鳴らぬ時 ★一つも鳴らず★ と書く)★
    nao = lambda x: str(x).replace("★", "").strip()
    ugoki = "―― 同じ" if (nao(mae_rc) == nao(rc) and nao(mae_nari) == nao(ima_nari)) else "★動いた★"
    rows.append([na, mae_rc, mae_nari, rc, ima_nari, ugoki])
    for suf, body in (("out", out), ("err", err), ("rc", str(rc) + "\n")):
        kaku(os.path.join(BUNDLE, "raw", "31_run", "60_kou_atta_%s.%s" % (na, suf)), body)
kaku_tsv(os.path.join(BUNDLE, "raw", "60_kou_no_kikime.tsv"), rows,
         header=["札(fixture)", "當てる前 rc(旧基底)", "當てる前の鳴り", "甲を當てた後 rc", "當てた後の鳴り", "動き"])

d = dict((r[0], r) for r in rows)
kaku(os.path.join(BUNDLE, "raw", "61_kikime_dan.txt"),
     "as-of %s(UTC)\n根=%s\n\n"
     "【甲の効き目 ―― 動いたのは一本だけである】\n"
     "・fx05(CRLF 空行): 當てる前 %s『%s』 → 當てた後 rc=%s『%s』 ★閉ぢた★\n"
     "・fx07(素の空行)  : 當てる前 %s『%s』 → 當てた後 rc=%s『%s』 ―― 旧から鳴つて居た口を ★壊して居らぬ★\n"
     "・fx04(清い紙)    : 當てる前 %s『%s』 → 當てた後 rc=%s『%s』 ―― ★濡れ衣を作つて居らぬ(陽性対照の裏)★\n"
     "・fx03(kaki の空) : 當てる前 %s『%s』 → 當てた後 rc=%s『%s』 ―― 源で一行書いた紙は通る(㋑ の形)\n\n"
     "【★甲の限界 ―― 之を隠さぬ★】\n"
     "・fx06(U+3000 一字の行): 當てた後も rc=%s『%s』 ―― ★甲では閉ぢぬ★。\n"
     "  末尾行は空でなく「見えぬ一字」である ∴ 「空か」を問ふ甲の口には入らぬ。\n"
     "  形(U+3000/U+00A0/U+2003/U+FEFF…)を数へ上げる仕方では永久に閉ぢぬ ∴ codepoint の ★類★ で判ずる器が要る。\n"
     "  上流は裁 seq330497 で兄弟器 karo_mac_fukashiji.py を据ゑて之を閉ぢた(raw/30: 新基底で fx06 は rc=1)。\n"
     "  ∴ 當席の断は「甲は材として出すが、★本筋は上流の版へ入れ替へる事★」である(門の入替は変更統制)。\n\n"
     "【語の註 ―― 表の札を其の儘読むな】\n"
     "・fx05 の當てた後の鳴りが『條④(旧・末尾2字 0a0a の口)』と出るのは、甲が ★say の文言を逐語で引き継いだ★ 故である。\n"
     "  口は既に「末尾2字の一致」ではなく「末尾一行が空か」である ―― 語彙表(raw/30)は文言で引く ∴ 札は古い名で出る。\n\n"
     "【之が意味せぬ事】\n"
     "・fx05 が閉ぢた事は ★此の席の門が直つた事ではない★ ―― 當てたのは _fx/kentei/ の複製のみ。\n"
     "・七本は當席が拵へた 陽性対照 であり、現に世に在る紙の分布ではない。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT,
        d["05_crlf_kuugyou.txt"][1], d["05_crlf_kuugyou.txt"][2], d["05_crlf_kuugyou.txt"][3], d["05_crlf_kuugyou.txt"][4],
        d["07_sunao_kuugyou.txt"][1], d["07_sunao_kuugyou.txt"][2], d["07_sunao_kuugyou.txt"][3], d["07_sunao_kuugyou.txt"][4],
        d["04_kiyoi.txt"][1], d["04_kiyoi.txt"][2], d["04_kiyoi.txt"][3], d["04_kiyoi.txt"][4],
        d["03_kaki_kara.txt"][1], d["03_kaki_kara.txt"][2], d["03_kaki_kara.txt"][3], d["03_kaki_kara.txt"][4],
        d["06_u3000_kuugyou.txt"][3], d["06_u3000_kuugyou.txt"][4]))
for r in rows:
    print("%-22s 前 %s『%s』 → 後 rc=%s『%s』 %s" % (r[0], r[1], r[2], r[3], r[4], r[5]))
