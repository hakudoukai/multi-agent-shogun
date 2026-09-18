#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""63_damatte.py -- ★「黙つて別の物を讀む」を 現物で起す器★。

㋑ の「最も悪いのは何れか」に答へる為の対照。
形だけでは 黙るか鳴るかは決まらぬ ―― ★切り落した先に物が在るか否か★ で決まる。
∴ ★囮(をとり)★ を置いて 起す。

  甲 囮の胴が 狙ひと ★同じ★  → BEFORE は ★一致・rc0=通れ★ と刷る(★黙つた★)
  乙 其の後 狙ひの胴を ★書き換へる★ → BEFORE は 尚 ★一致・rc0★(★臺帳が守つて居らぬ★)
  丙 囮の胴が 狙ひと ★違ふ★  → BEFORE は ★相違★(鳴るが ★診立ては「版が違ふ」で 人を git へ遣る★)
"""
import io, os, subprocess, sys, hashlib

ROOT = os.path.abspath(sys.argv[1])
B = os.path.abspath(sys.argv[2])
D = os.path.join(B, "fixture", "damatte")
AN = os.path.join(B, "an", "damatte")
for d in (D, AN):
    os.makedirs(d, exist_ok=True)
APPEND = os.path.join(ROOT, "scripts", "checks", "karo_mac_manifest_append.py")
VB = os.path.join(B, "patch", "verify_BEFORE.py")
VA = os.path.join(B, "patch", "verify_AFTER.py")
ZEN = u"　"          # 全角空白 ―― 書き手は括らぬ / 讀手の \s は当たる

def hashi(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def hashiru(v, man, na):
    r = subprocess.run([sys.executable, "-B", v, man, ROOT + os.sep],
                       cwd=ROOT, capture_output=True, text=True)
    io.open(os.path.join(AN, na + ".out"), "w", encoding="utf-8", newline="").write(r.stdout)
    io.open(os.path.join(AN, na + ".err"), "w", encoding="utf-8", newline="").write(r.stderr)
    at = u"?"
    for l in r.stdout.split(u"\n"):
        if l.strip().startswith(u"一致"):
            at = l.strip().replace(u"★", u"")
            break
    return r.returncode, at

kiroku = []
for fuda, onaji in ((u"KOU_onaji_dou", True), (u"HEI_chigau_dou", False)):
    d = os.path.join(D, fuda)
    os.makedirs(d, exist_ok=True)
    mato = os.path.join(d, u"a" + ZEN + u"b.txt")        # ★狙ひ★(全角空白を含む名)
    otori = os.path.join(d, u"a")                        # ★囮★(① が切り落した先)
    io.open(mato, "w", encoding="utf-8", newline="").write(u"MATO\n")
    io.open(otori, "w", encoding="utf-8", newline="").write(u"MATO\n" if onaji else u"OTORI-CHIGAU\n")

    man = os.path.join(AN, fuda + u".man.txt")
    if os.path.exists(man):
        os.remove(man)
    r = subprocess.run([sys.executable, "-B", APPEND, man, mato],
                       cwd=ROOT, capture_output=True, text=True)
    gyou = [l for l in io.open(man, encoding="utf-8").read().split(u"\n")
            if l and not l.startswith(u"#")][-1]
    kukutta = gyou.split(u"path=", 1)[1][:1] in u"\"'"

    b1 = hashiru(VB, man, fuda + u".BEFORE")
    a1 = hashiru(VA, man, fuda + u".AFTER")

    # 乙 ―― 狙ひの胴だけ書き換へる(臺帳は触らぬ)
    io.open(mato, "w", encoding="utf-8", newline="").write(u"MATO-KAKIKAETA\n")
    b2 = hashiru(VB, man, fuda + u".BEFORE.kaki")
    a2 = hashiru(VA, man, fuda + u".AFTER.kaki")

    kiroku.append(dict(fuda=fuda, onaji=onaji, kukutta=kukutta,
                       mato=os.path.relpath(mato, ROOT), otori=os.path.relpath(otori, ROOT),
                       sha_mato_ima=hashi(mato), sha_otori=hashi(otori), gyou=gyou,
                       b1=b1, a1=a1, b2=b2, a2=a2))

o = []
for k in kiroku:
    o.append(u"= %s (囮の胴が狙ひと %s / 書き手は括つたか=%s)"
             % (k["fuda"], u"★同じ★" if k["onaji"] else u"★違ふ★", k["kukutta"]))
    o.append(u"  狙ひ %s" % k["mato"])
    o.append(u"  囮   %s" % k["otori"])
    o.append(u"  臺帳 %s" % k["gyou"][:150])
    o.append(u"  ⑴臺帳の直後   BEFORE rc=%d %s   |   AFTER rc=%d %s" % (k["b1"][0], k["b1"][1], k["a1"][0], k["a1"][1]))
    o.append(u"  ⑵狙ひを書換後 BEFORE rc=%d %s   |   AFTER rc=%d %s" % (k["b2"][0], k["b2"][1], k["a2"][0], k["a2"][1]))
    o.append(u"")
t = u"\n".join(o)
io.open(os.path.join(AN, u"damatte.txt"), "w", encoding="utf-8", newline="").write(t + u"\n")
sys.stdout.write(t + u"\n")
