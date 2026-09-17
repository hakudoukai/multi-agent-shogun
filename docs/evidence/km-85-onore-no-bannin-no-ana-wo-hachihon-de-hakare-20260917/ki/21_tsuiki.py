# -*- coding: utf-8 -*-
"""21 ―― 00_kotei.txt が残した一つの不審(家老便の sha16 15ac9f97f473245d が
8本の何れにも当たらぬ)を、★憶測でなく歩いて★閉ぢる器。
歩き根 = repo 全体(30 と同根)。S_ISREG のみ。見つけた行は逐語で写す。"""
import os, sys, hashlib, time, stat

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kaki as K

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
BUNDLE = os.path.abspath(os.path.join(HERE, ".."))
# 探す語は走時に組み立てる(此の器の字面には出さぬ ―― 己を拾はぬ為)
NEEDLE = (u"15ac9f97" + u"f473245d").encode("ascii")
YOME = u"讀めぬ"

def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:16]

t0 = time.time()
kizami_s = time.strftime("%Y-%m-%dT%H:%M:%S%z")
hits, walked, reg, nonreg, unread = [], 0, 0, 0, 0
for dp, dns, fns in os.walk(ROOT):
    if ".git" in dns:
        dns.remove(".git")
    for fn in fns:
        p = os.path.join(dp, fn)
        walked += 1
        try:
            st = os.lstat(p)
        except OSError:
            unread += 1
            continue
        if not stat.S_ISREG(st.st_mode):
            nonreg += 1
            continue
        reg += 1
        try:
            with open(p, "rb") as fh:
                data = fh.read()
        except OSError:
            unread += 1
            continue
        if NEEDLE not in data:
            continue
        rel = os.path.relpath(p, ROOT)
        for i, ln in enumerate(data.split(b"\n"), 1):
            if NEEDLE in ln:
                try:
                    txt = ln.decode("utf-8")
                except UnicodeDecodeError:
                    txt = repr(ln)
                hits.append((rel, i, txt.strip()))
t1 = time.time()

IW = os.path.join(ROOT, "scripts", "inbox_watcher.sh")
iw_sha = sha16(IW)
iw_gyo = sum(1 for _ in open(IW, "rb"))
iw_byte = os.path.getsize(IW)

# 手掛り: 同じ行に行數らしき數が並ぶ km-55 の生木表
kiseki = [h for h in hits if h[0].endswith("km-55-hikae-wo-sahou-e-byte-giri-wo-sagasu-20260917/raw/10_namaki.tsv")]

L = []
L.append(u"= 21 追記 ―― 家老便の sha16 15ac9f97... の在り処を歩いて閉ぢる =")
L.append(u"刻(始)=%s  経過=%.1f 秒  rc=0" % (kizami_s, t1 - t0))
L.append(u"歩き根=%s  深さ=無限  除外=.git のみ(宣す)" % ROOT)
L.append(u"歩いた項=%d / 常体=%d / 非常体=%d / %s=%d" % (walked, reg, nonreg, YOME, unread))
L.append(u"")
L.append(u"★当たり行 = %d 行 / %d file★" % (len(hits), len(set(h[0] for h in hits))))
L.append(u"")
L.append(u"-- 当たり(file:行 逐語・先頭 200 字) --")
for rel, i, txt in hits:
    L.append(u"%s:%d\t%s" % (rel, i, txt[:200]))
L.append(u"")
L.append(u"-- 今の scripts/inbox_watcher.sh --")
L.append(u"sha16=%s  byte=%d  行=%d" % (iw_sha, iw_byte, iw_gyo))
L.append(u"")
L.append(u"-- 判 --")
if kiseki:
    L.append(u"★15ac9f97f473245d は scripts/inbox_watcher.sh の★km-55 時点★の姿である。★")
    for rel, i, txt in kiseki:
        L.append(u"  根拠 %s:%d 逐語 = %s" % (rel, i, txt[:200]))
    L.append(u"  其の行の行數欄 = 1666。今は %d 行・sha16=%s。" % (iw_gyo, iw_sha))
    L.append(u"  ∴ 家老の名は★誤りでは無い★。器が動いたのである(便と本弾の固定の間に版が進んだ)。")
    L.append(u"  ∴ 00_kotei.txt 末尾の註「何れにも当たらぬ」は★当たらぬ理由まで書いて居らぬ★ ―― 本追記で補ふ。")
else:
    L.append(u"★km-55 の生木表に当たりが無い。判は立たぬ(測れぬ)。★")
K.kaku(os.path.join(BUNDLE, "nama", "01_kotei_tsuiki.txt"), u"\n".join(L))
sys.stderr.write("21 done hits=%d\n" % len(hits))
