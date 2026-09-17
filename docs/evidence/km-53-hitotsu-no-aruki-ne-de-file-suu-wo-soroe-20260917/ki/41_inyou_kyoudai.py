#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 41_inyou_kyoudai.py ―― ★同じ file に残つた「兄弟の口」の陰陽対照★(第53弾 ㋒補)
#
# 40_inyou.py は stdin 時限(STOP_HOOK_STDIN_TIMEOUT)を測る。然し ★同じ hook の中に
# 旧形の glob 番人が残つて居る口が在る★。本器は其の口を ★名を argv から取つて★ 測る。
# ★對象は讀むのみ・寫しで測る・行番号は字面で探す★。
#
# 使ひ方:
#   41_inyou_kyoudai.py --mato <對象sh> --na <閾名> --sahen <左項名> --sahenatai <左項の値>
#                       --atai <閾の値> --dest <寫し>
import sys, os, io, re, subprocess, time, hashlib

d = {'--mato': None, '--na': None, '--sahen': None, '--sahenatai': None,
     '--atai': None, '--dest': None}
av = sys.argv[1:]; i = 0
while i < len(av):
    if av[i] in d and i+1 < len(av): d[av[i]] = av[i+1]; i += 2; continue
    sys.stderr.write(u'★測れぬ: 知らぬ引数 %s★\n' % av[i]); sys.exit(2)
for k in d:
    if d[k] is None:
        sys.stderr.write(u'★測れぬ: %s を argv で渡せ★\n' % k); sys.exit(2)
mato, na, sahen, sahenatai, atai, dest = (d['--mato'], d['--na'], d['--sahen'],
                                          d['--sahenatai'], d['--atai'], d['--dest'])
if not os.path.exists(mato):
    sys.stderr.write(u'★測れぬ: 對象が無い %s★\n' % mato); sys.exit(2)
raw = open(mato, 'rb').read()
sha16 = hashlib.sha256(raw).hexdigest()[:16]
lines = raw.decode('utf-8').split(u'\n')

def find_re(pat, frm=0):
    r = re.compile(pat)
    for n in range(frm, len(lines)):
        if r.search(lines[n]): return n
    return -1

i_def = find_re(re.escape(na) + r'=\$\{' + re.escape(na) + r':-')
# ★疵(本弾で 40_inyou が踏んだ物と同根)★ 字面だけで探すと ★註行★ を拾ひ、
#   寫しの `if` の座に註を置いて `else` を宙に浮かせる。∴ ⑴註行に非ず ⑵if/elif…then を條に加へる。
_pat = re.compile(r'-(?:gt|ge|lt|le|eq|ne)\s+"\$' + re.escape(na) + r'"')
hantei_ate = []
for _k, _ln in enumerate(lines):
    if not _pat.search(_ln): continue
    _t = _ln.strip()
    hantei_ate.append((_k, _t.startswith(u'#'),
                       (_t.startswith(u'if ') or _t.startswith(u'elif ')) and _t.rstrip().endswith(u'then'), _t))
i_cmp = -1
for _k, _chu, _kata, _t in hantei_ate:
    if (not _chu) and _kata:
        i_cmp = _k; break
w = sys.stdout.write
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
w(u'# 41_inyou_kyoudai ―― 兄弟の口の陰陽対照 / 刻= %s\n' % koku)
w(u'# 對象= %s / sha16= %s / 行= %d / 閾名= %s / 左項= %s\n'
  % (mato, sha16, raw.count(b'\n'), na, sahen))
if i_def < 0 or i_cmp < 0 or i_cmp <= i_def:
    w(u'★測れぬ: 字面が見付からぬ(定義=%d 判定=%d ―― 1起点・-1 は不在)★\n' % (i_def+1, i_cmp+1))
    sys.exit(3)
bannin = lines[i_def:i_cmp]
hantei = lines[i_cmp]
kata = u'旧形(case の glob *[!0-9]*)' if any(u'[!0-9]' in l for l in bannin) \
       else u'新形(比べる時と同じ演算子で検む)'
w(u'# 番人域(逐語)= %d〜%d 行(%d 行) / 判定行= %d 行\n'
  % (i_def+1, i_cmp, len(bannin), i_cmp+1))
w(u'# 判定行の候補(字面が当たつた行 悉く)= %d 本 ★註行・if 以外は採らぬ★\n' % len(hantei_ate))
for _k, _chu, _kata, _t in hantei_ate:
    w(u'#   %d 行: 註行=%s / if…then=%s / 採=%s : %s\n'
      % (_k+1, u'真' if _chu else u'偽', u'真' if _kata else u'偽',
         u'★之★' if _k == i_cmp else u'―', _t))
w(u'# 判定行(逐語): %s\n' % hantei.strip())
w(u'# 番人の形= %s\n' % kata)

h = [u'#!/bin/bash',
     u'# ★寫し★ 對象= %s sha16= %s / 刻= %s' % (mato, sha16, koku),
     u'# 番人域・判定行は對象から ★逐語で写した★。枝のみ本器が付す(宣)。',
     u'%s=%s' % (na, "'" + atai.replace("'", "'\\''") + "'"),
     u'%s=%s' % (sahen, "'" + sahenatai.replace("'", "'\\''") + "'"),
     u'# ---- 番人域(逐語 %d〜%d) ----' % (i_def+1, i_cmp)]
h.extend(bannin)
h.append(u'# ---- 番人域 了 ----')
h.append(u'echo "番人の後: %s=[${%s}] %s=[${%s}]"' % (na, na, sahen, sahen))
m = re.search(r'\[[^\]]*-(?:gt|ge|lt|le|eq|ne)\s+"\$' + re.escape(na) + r'"\s*\]', hantei)
if m:
    h.append(m.group(0))
    h.append(u'echo "閾比較の素 rc=$?"')
h.append(u'# ---- 判定行(逐語 %d) ----' % (i_cmp+1))
h.append(hantei.rstrip())
h.append(u'    echo "★閾を越えたと見る(then へ入つた)★"')
h.append(u'else')
h.append(u'    echo "★閾を越えたと見ぬ(else へ落ちた)★"')
h.append(u'fi')
h.append(u'exit 0')
txt = u'\n'.join(h) + u'\n'
with io.open(dest, 'w', encoding='utf-8', newline='') as fh: fh.write(txt)
os.chmod(dest, 0o755)
w(u'# 寫し= %s sha16= %s\n' % (dest, hashlib.sha256(txt.encode('utf-8')).hexdigest()[:16]))
pn = subprocess.Popen(['/bin/bash', '-n', dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
on, en = pn.communicate()
w(u'# 寫しの形検め(bash -n) rc= %d\n' % pn.returncode)
if pn.returncode != 0:
    for _l in en.decode('utf-8', 'replace').split(u'\n'):
        if _l: w(u'#   [bash -n err] %s\n' % _l)
    w(u'★測れぬ: 寫しの形が壊れて居る(bash -n rc=%d) ―― 判定を刷らぬ★\n' % pn.returncode)
    sys.exit(4)
p = subprocess.Popen(['/bin/bash', dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
o, e = p.communicate()
w(u'\n--- 寫しの出目(%s= %s / %s= %s) rc= %d ---\n' % (na, atai, sahen, sahenatai, p.returncode))
for ln in o.decode('utf-8','replace').split(u'\n'):
    if ln: w(u'[out] %s\n' % ln)
for ln in e.decode('utf-8','replace').split(u'\n'):
    if ln: w(u'[err] %s\n' % ln)
sys.exit(0)
