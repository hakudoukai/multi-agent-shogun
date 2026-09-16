#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""64_shizukari.py -- ★形ごとに「黙り得るか」を 現物で決める器★。

63 は 一形(全角空白)で 黙りを起した。之は ★全形に対して同じ手を掛ける★。
手順(形ごと):
  ① BEFORE が第一に挙げた候補 cands[0] を取る
  ② 其の path に ★狙ひと同じ胴★ の囮を建てる(親 dir も掘る)
  ③ BEFORE を再び走らす
     rc=0 一致 かつ 讀んだ物が囮 → ★黙り得る(最悪)★
     鳴る                        → ★鳴るに留まる★
  ④ 囮を ★必ず★ 取り除く(次の形を汚さぬ為)
★判ずるな、建てて測れ。★
"""
import io, os, re, sys, json, shutil, subprocess, hashlib, importlib.util

ROOT = os.path.abspath(sys.argv[1])
B = os.path.abspath(sys.argv[2])
AN = os.path.join(B, "an")
OUT = os.path.join(AN, "shizukari")
os.makedirs(OUT, exist_ok=True)
VB = os.path.join(B, "patch", "verify_BEFORE.py")

def yomu(path, na):          # ★器をそのまま載せる——写し直さぬ★
    sp = importlib.util.spec_from_file_location(na, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m
mae = yomu(VB, "km46_mae64")

tsv = io.open(os.path.join(AN, "kata.tsv"), encoding="utf-8").read().split(u"\n")
atama = tsv[0].split(u"\t")
gyou = [dict(zip(atama, l.split(u"\t"))) for l in tsv[1:] if l.strip()]

NAWA = os.path.join(B, "fixture", "nawa")   # ★縄張り——囮は束の外へ出さぬ★

def hashiru(man, na, base=None):
    r = subprocess.run([sys.executable, "-B", VB, man, (base or ROOT) + os.sep],
                       cwd=ROOT, capture_output=True, text=True)
    io.open(os.path.join(OUT, na + u".out"), "w", encoding="utf-8", newline="").write(r.stdout)
    at = u"?"
    for l in r.stdout.split(u"\n"):
        if l.strip().startswith(u"一致"):
            at = l.strip().replace(u"★", u"")
    return r.returncode, at

o = []
kazu = {u"黙り得る": 0, u"鳴るに留まる": 0, u"囮を建てられぬ": 0, u"元より正": 0}
for g in gyou:
    fuda = g.get(u"札", u"")
    man = os.path.join(AN, u"man", fuda + u".one.txt")
    if not os.path.isfile(man):
        o.append(u"%-12s ★測れぬ(臺帳の一行が無い ―― 行に建てぬ形)★" % fuda)
        continue
    # ★TSV の顕表記を戻すな——臺帳の行から BEFORE に直に問へ★
    gyoumoji = [l for l in io.open(man, encoding="utf-8").read().split(u"\n")
                if l.strip() and not l.startswith(u"#")][-1]
    cb = mae.paths_of(gyoumoji)
    moto = hashiru(man, fuda + u".moto")
    if moto[0] == 0 and u"一致 1" in moto[1]:
        kazu[u"元より正"] += 1
        o.append(u"%-12s 元より rc=0 ―― 囮を試さぬ" % fuda)
        continue
    if not cb:
        o.append(u"%-12s ★候補零 ―― 囮の置き所が無い★" % fuda)
        kazu[u"囮を建てられぬ"] += 1
        continue
    kouho = cb[0]
    # ★囮の胴は「臺帳が録した sha を持つ物」の写しでなければならぬ★
    #   (適当な胴を置けば 相違 と鳴り、★黙りを起せぬ——之が最初の走りの疵★)
    sen = re.search(r"sha256=([0-9a-f]{64})", gyoumoji)
    mato_dou = None
    mato_na = None
    for dpath, _dn, fns in os.walk(os.path.join(B, "fixture")):
        for fn in fns:
            c = os.path.join(dpath, fn)
            try:
                d = open(c, "rb").read()
            except OSError:
                continue
            if sen and hashlib.sha256(d).hexdigest() == sen.group(1):
                mato_dou, mato_na = d, c
                break
        if mato_dou is not None:
            break
    if mato_dou is None:
        o.append(u"%-12s ★測れぬ(録された sha を持つ物が束に無い)★" % fuda)
        continue
    # ★候補は根からの相対ゆゑ、素直に join すると 根の直下に `"docs` の如き dir を掘る。
    #   (一走り目に 実際に掘つた——己の器が根を汚した。以後 縄張りへ逃がす)★
    otori = os.path.join(NAWA, kouho.lstrip(u"/"))
    if os.path.relpath(otori, NAWA).startswith(u".."):
        o.append(u"%-14s ★建てられぬ(縄張りの外へ出る候補)★" % fuda)
        kazu[u"囮を建てられぬ"] += 1
        continue
    tateta = False
    try:
        d = os.path.dirname(otori)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        if not os.path.exists(otori):
            open(otori, "wb").write(mato_dou)
            tateta = True
    except Exception as e:
        o.append(u"%-12s ★囮を建てられぬ(%s)★ 候補=%s" % (fuda, type(e).__name__, kouho[:60]))
        kazu[u"囮を建てられぬ"] += 1
        continue
    if not tateta:
        o.append(u"%-12s ★既に在つた ―― 建てずに測る★ 候補=%s" % (fuda, kouho[:60]))
    ato = hashiru(man, fuda + u".otori", base=NAWA)
    if ato[0] == 0 and u"一致 1" in ato[1]:
        kazu[u"黙り得る"] += 1
        han = u"★黙り得る(最悪)★"
    else:
        kazu[u"鳴るに留まる"] += 1
        han = u"鳴るに留まる"
    o.append(u"%-14s %s" % (fuda, han))
    o.append(u"    囮前 rc=%d %s" % (moto[0], moto[1]))
    o.append(u"    囮後 rc=%d %s" % (ato[0], ato[1]))
    o.append(u"    囮 %s  ←胴は %s の写し"
             % (kouho, os.path.relpath(mato_na, ROOT) if mato_na else u"?"))
    o.append(u"    ★囮は縄張り %s の下に建て、測り了へて除いた★"
             % os.path.relpath(NAWA, ROOT))
    if tateta:
        os.remove(otori)

o.append(u"")
o.append(u"= 締 " + u" / ".join(u"%s %d" % (k, v) for k, v in kazu.items()))
t = u"\n".join(o)
io.open(os.path.join(AN, u"shizukari.txt"), "w", encoding="utf-8", newline="").write(t + u"\n")
sys.stdout.write(t + u"\n")
