# -*- coding: utf-8 -*-
# 歩行器: argv の根を歩き ⑴tmux の -t 的 ⑵ashigaru-mac-4/5/6 の字面 を數へる
# 母數・除いた物・rc を悉く刷る。行単位。
import os, sys, re, io

SKIPDIR = {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache"}
MAXB = int(os.environ.get("MAXB", "1048576"))   # 1MB 超は除く(宣する)

# -t の的: tmux が同行に在る物のみ甲
RE_T = re.compile(r'''-t[= ]+(['"]?)([^\s'"();|&]+)''')
RE_456 = re.compile(r'ashigaru-mac-([456])\b')

def classify(tgt):
    if tgt.startswith('%'):      return 'pane_id'
    if tgt.startswith('='):      return '完全一致'
    if tgt.startswith('$'):      return '変数'
    if tgt.startswith('"$') or tgt.startswith("'$"): return '変数'
    return '★前方一致risk★'

roots = sys.argv[1:]
n_file = n_read = n_skip_big = n_skip_bin = 0
n_skip_self = 0
SELF = os.environ.get("KM_SELF_BUNDLE","")
# ★除く根を argv でなく env で名指す★(母數を三通り取る爲)
SKIPPFX = [os.path.normpath(x) for x in os.environ.get("KM_SKIP_PREFIXES","").split(",") if x.strip()]
n_skip_pfx = 0
big = []
hits_t = []      # (path, lineno, tgt, kind, line)
hits_456 = []    # (path, lineno, which, line)
rc_walk = 0
stumbles = []   # ★躓いた path を名指す★(rc=1 だけでは何處で止まつたか判らぬ)
for root in roots:
    if not os.path.exists(root):
        print("★根が無い★ %s" % root); rc_walk = 1; continue
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIPDIR]
        # ★己の束を除く★（此の器の出目を收める束を數へれば自己言及に成る）
        _ndp = os.path.normpath(dp)
        _hit = [x for x in SKIPPFX if _ndp == x or _ndp.startswith(x + os.sep)]
        if _hit:
            for _r, _d, _f in os.walk(dp):
                n_skip_pfx += len(_f)
            dns[:] = []; continue
        if SELF and _ndp.startswith(os.path.normpath(SELF)):
            for _r, _d, _f in os.walk(dp):
                n_skip_self += len(_f)        # ★枝を刈る前に下まで數へる★(直下のみでは 0 と出て偽の通に成る)
            dns[:] = []; continue
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                st = os.lstat(p)
            except OSError as e:
                rc_walk = 1; stumbles.append(("stat", p, repr(e))); continue
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            n_file += 1
            if st.st_size > MAXB:
                n_skip_big += 1; big.append((st.st_size, p)); continue
            try:
                b = io.open(p, 'rb').read()
            except OSError as e:
                rc_walk = 1; stumbles.append(("open", p, repr(e))); continue
            if b'\0' in b:
                n_skip_bin += 1; continue
            try:
                s = b.decode('utf-8')
            except UnicodeDecodeError:
                s = b.decode('utf-8', 'replace')
            n_read += 1
            for i, ln in enumerate(s.split('\n'), 1):
                if 'tmux' in ln:
                    for m in RE_T.finditer(ln):
                        tgt = m.group(2)
                        hits_t.append((p, i, tgt, classify(tgt), ln.strip()[:160]))
                for m in RE_456.finditer(ln):
                    hits_456.append((p, i, m.group(1), ln.strip()[:160]))

print("=== 母數 ===")
print("根            = %s" % " ".join(roots))
print("rc(歩行)      = %d" % rc_walk)
print("★躓いた file = %d 本★" % len(stumbles))
for kind, p, err in stumbles[:30]:
    print("  躓 %-5s %s  %s" % (kind, p, err))
print("全file        = %d" % n_file)
print("読めた        = %d" % n_read)
print("除いた(>%dB) = %d" % (MAXB, n_skip_big))
print("除いた(binary)= %d" % n_skip_bin)
print("★除いた(己の束 %s)= %d★" % (SELF or "(未指定)", n_skip_self))
print("★除いた(名指の根 %s)= %d★" % (",".join(SKIPPFX) or "(無)", n_skip_pfx))
for sz, p in sorted(big, reverse=True)[:25]:
    print("  除大 %12d %s" % (sz, p))

print()
print("=== ⑴ tmux -t の的 (同行に tmux が在る物のみ) ===")
from collections import Counter
c = Counter(k for _, _, _, k, _ in hits_t)
print("的の総数 = %d" % len(hits_t))
for k in ['★前方一致risk★', 'pane_id', '完全一致', '変数']:
    print("  %-14s = %d" % (k, c.get(k, 0)))
risk_files = {}
for p, i, tgt, k, ln in hits_t:
    if k == '★前方一致risk★':
        risk_files.setdefault(p, []).append((i, tgt, ln))
print("★risk を持つ file = %d 本★" % len(risk_files))
for p in sorted(risk_files):
    print("  --- %s (%d件)" % (p, len(risk_files[p])))
    for i, tgt, ln in risk_files[p]:
        print("      L%-5d 的=%-34s | %s" % (i, tgt, ln))

print()
print("=== ⑵ ashigaru-mac-4/5/6 の字面 ===")
c2 = Counter(w for _, _, w, _ in hits_456)
print("総数 = %d  (-4=%d / -5=%d / -6=%d)" % (len(hits_456), c2.get('4',0), c2.get('5',0), c2.get('6',0)))
f456 = {}
for p, i, w, ln in hits_456:
    f456.setdefault(p, []).append((i, w, ln))
print("持つ file = %d 本" % len(f456))
for p in sorted(f456):
    print("  --- %s (%d件)" % (p, len(f456[p])))
    for i, w, ln in f456[p][:40]:
        print("      L%-5d -%s | %s" % (i, w, ln))
    if len(f456[p]) > 40:
        print("      ...他 %d 件" % (len(f456[p]) - 40))
