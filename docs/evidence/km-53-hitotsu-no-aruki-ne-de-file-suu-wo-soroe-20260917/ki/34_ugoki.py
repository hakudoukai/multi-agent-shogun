#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 34_ugoki.py ―― ★「disk の數は刻の函数である」を一枚で見せる器★(第53弾 ㋑の根)
#
# 本弾で實際に起きた事: 10:24:18 の disk は 定義丁 23口、10:27:13 の disk は 22口 であつた。
#   間に触られたのは一本のみ。∴ ★三席の file 數が合はぬのは、誰かが誤つたのではなく
#   「disk」が各席の測つた刻で違ふ物を指して居た可能性が在る★ ―― 之を名指しで示す。
#
# 使ひ方: 34_ugoki.py --rev <rev> --mato <file> [--mato <file> ...]
import sys, os, re, time, hashlib, subprocess

rev = None; mato = []
av = sys.argv[1:]; i = 0
while i < len(av):
    if av[i] == '--rev' and i+1 < len(av): rev = av[i+1]; i += 2; continue
    if av[i] == '--mato' and i+1 < len(av): mato.append(av[i+1]); i += 2; continue
    sys.stderr.write(u'★測れぬ: 知らぬ引数 %s★\n' % av[i]); sys.exit(2)
if not rev or not mato:
    sys.stderr.write(u'★測れぬ: --rev と --mato を argv で渡せ★\n'); sys.exit(2)

KOU = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*):-([0-9]+)\}')
SHIKII_NA = re.compile(r'^[A-Z][A-Z0-9_]*$')

def kuchi(s):
    out = []
    for no, ln in enumerate(s.split(u'\n'), 1):
        if ln.lstrip().startswith(u'#'): continue
        for m in KOU.finditer(ln):
            if SHIKII_NA.match(m.group(1)) and int(m.group(2)) >= 1:
                out.append(u'%s:-%s@%d' % (m.group(1), m.group(2), no))
    return out

w = sys.stdout.write
w(u'# 34_ugoki ―― disk と版の口を並べ、動いた所を名指す / 刻= %s\n' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
w(u'# 條= 定義丁 條(全)∧條(閾)(名 ^[A-Z][A-Z0-9_]*$ ∧ 既定>=1 ∧ 註行に非ず) / 單位= 出現(occ)\n')
w(u'# 比べる版= %s\n' % rev)
rc = 0
for m in mato:
    w(u'\n=== %s ===\n' % m)
    if not os.path.isfile(m):
        w(u'★測れぬ: disk に file が無い★\n'); rc = 3; continue
    b = open(m, 'rb').read()
    st = os.stat(m)
    w(u'[disk] mtime= %s / sha256/16= %s / bytes= %d\n'
      % (time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(st.st_mtime)),
         hashlib.sha256(b).hexdigest()[:16], len(b)))
    p = subprocess.Popen(['git', 'show', '%s:%s' % (rev, m)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o, e = p.communicate()
    if p.returncode != 0:
        w(u'★測れぬ: git show rc=%d(%s に此の path 無し)★\n' % (p.returncode, rev)); rc = 3; continue
    w(u'[%s] sha256/16= %s / bytes= %d\n' % (rev, hashlib.sha256(o).hexdigest()[:16], len(o)))
    kd = kuchi(b.decode('utf-8', 'replace')); kr = kuchi(o.decode('utf-8', 'replace'))
    w(u'口: disk= %d / %s= %d / 差= %+d\n' % (len(kd), rev, len(kr), len(kd) - len(kr)))
    nd = [x.split(u'@')[0] for x in kd]; nr = [x.split(u'@')[0] for x in kr]
    import collections
    cd = collections.Counter(nd); cr = collections.Counter(nr)
    for na in sorted(set(cd) | set(cr)):
        if cd[na] != cr[na]:
            w(u'  ★動いた名★ %s : disk %d ⇔ %s %d (%+d)\n' % (na, cd[na], rev, cr[na], cd[na] - cr[na]))
    w(u'  disk の口(行附)= %s\n' % u' '.join(kd))
    w(u'  %s の口(行附)= %s\n' % (rev, u' '.join(kr)))
sys.exit(rc)
