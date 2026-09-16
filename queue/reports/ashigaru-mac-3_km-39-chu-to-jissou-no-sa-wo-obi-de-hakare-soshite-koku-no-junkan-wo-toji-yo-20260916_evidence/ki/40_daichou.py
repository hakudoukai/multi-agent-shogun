# -*- coding: utf-8 -*-
u"""臺帳(甲型 `path= sha256= bytes=`)を作る。歩き根・外に足す物・除く形 悉く argv から取る。
  用: 10_daichou.py <出す臺帳> <歩き根[,歩き根...]> [--soto <file>]... [--nozoku <部分一致>]...
  刷る: 歩いた本數(母數) / 載せた項 / 除いた本(名つき) / 宣 byte和 / 臺帳自身の寸法
  ★除いたと宣る物も母數に数へる(法「A declared exclusion still counts in 母數」)★
  ★歩き根は argv から取る(第37弾 疵六 ―― literal を抱へぬ)★"""
import sys, os, stat, hashlib

argv = sys.argv[1:]
if len(argv) < 2:
    sys.stderr.write(u"用: 10_daichou.py <臺帳> <歩き根> [--soto f] [--nozoku pat]\n")
    sys.exit(2)

out_man = argv[0]
roots = []
soto = []
nozoku = []
i = 1
while i < len(argv):
    a = argv[i]
    if a == u'--soto':
        soto.append(argv[i+1]); i += 2
    elif a == u'--nozoku':
        nozoku.append(argv[i+1]); i += 2
    else:
        roots.append(a); i += 1

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

walked = []
for r in roots:
    for dirpath, dirnames, filenames in os.walk(r, followlinks=False):
        dirnames[:] = [d for d in dirnames if d != '__pycache__']
        for fn in sorted(filenames):
            p = os.path.join(dirpath, fn)
            st = os.lstat(p)
            if stat.S_ISREG(st.st_mode):
                walked.append(p)
for s in soto:
    if os.path.isfile(s):
        walked.append(s)

walked = sorted(set(walked))
bogen = len(walked)

# 臺帳自身は載せぬ(和 甲)。之も「除いた」に数へて名で宣る。
nozoita = []
noseru = []
for p in walked:
    why = None
    if os.path.abspath(p) == os.path.abspath(out_man):
        why = u'臺帳自身(和 甲)'
    else:
        for pat in nozoku:
            if pat in p:
                why = u'--nozoku "%s"' % pat
                break
    if why:
        nozoita.append((p, why))
    else:
        noseru.append(p)

rows = []
total = 0
for p in noseru:
    b = os.path.getsize(p)
    total += b
    rows.append(u"path=%s sha256=%s bytes=%d" % (p, sha256(p), b))

with open(out_man, 'w') as f:
    f.write(u"\n".join(rows) + u"\n")

w = sys.stdout.write
w(u"★臺帳=%s★\n" % out_man)
w(u"歩き根(本)=%d\n" % len(roots))
for r in roots:
    w(u"  根| %s\n" % r)
for s in soto:
    w(u"  外| %s\n" % s)
for pat in nozoku:
    w(u"  除形| %s\n" % pat)
w(u"★歩いた本數(母數・本)=%d★\n" % bogen)
w(u"★載せた項(本)=%d★\n" % len(rows))
w(u"★除いた(本)=%d★\n" % len(nozoita))
for p, why in nozoita:
    w(u"  除| %s ―― %s\n" % (p, why))
w(u"★宣 byte和(bytes)=%d★ ―― 臺帳自身は入れぬ(和 甲)\n" % total)
w(u"臺帳自身(bytes)=%d\n" % os.path.getsize(out_man))
w(u"和 乙(臺帳を一度入れた和・bytes)=%d\n" % (total + os.path.getsize(out_man)))
