#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 32_sa.py ―― ★二つの數の差を「何の file が入り 何が落ちたか」で名指す器★(第53弾 ㋑)
#
# 「誰が正しい」ではなく「何の定義でどれが立つ」を出す。
# 使ひ方: 32_sa.py --hidari "<gen>,<tan>,<kitei>,<chu>" --migi "<gen>,<tan>,<kitei>,<chu>"
#                  [--kazu <30_kazu.py の路>]
import sys, os, subprocess, time, re

d = {'--hidari': None, '--migi': None,
     '--kazu': os.path.join(os.path.dirname(os.path.abspath(__file__)), '30_kazu.py')}
av = sys.argv[1:]; i = 0
while i < len(av):
    if av[i] in d and i+1 < len(av): d[av[i]] = av[i+1]; i += 2; continue
    sys.stderr.write(u'★測れぬ: 知らぬ引数 %s★\n' % av[i]); sys.exit(2)
if not d['--hidari'] or not d['--migi']:
    sys.stderr.write(u'★測れぬ: --hidari と --migi を argv で渡せ★\n'); sys.exit(2)

def hiku(spec):
    gen, tan, kitei, chu = spec.split(',')
    p = subprocess.Popen([sys.executable, '-B', d['--kazu'], '--gen', gen,
                          '--tan', tan, '--kitei', kitei, '--chu', chu],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o, e = p.communicate()
    if p.returncode != 0:
        sys.stderr.write(u'★測れぬ: 30_kazu が rc=%d(%s)★\n' % (p.returncode, spec)); sys.exit(3)
    txt = o.decode('utf-8')
    tbl = {}
    inb = False
    for ln in txt.split(u'\n'):
        if ln.startswith(u'--- file毎内訳'): inb = True; continue
        if inb:
            if ln.startswith(u'---') or ln == u'': inb = False; continue
            f = ln.split(u'\t')
            if len(f) >= 3:
                na = [x.split(u'@')[0] for x in f[2].split()]
                tbl[f[0]] = (int(f[1]), na)
    m = re.search(r'\[丁閾\] 口= (\d+)  file= (\d+)', txt)
    return spec, (int(m.group(1)), int(m.group(2))), tbl

sl, sn, st = hiku(d['--hidari'])
ml, mn, mt = hiku(d['--migi'])
w = sys.stdout.write
w(u'# 32_sa ―― 二つの數の差を名指す / 刻= %s\n' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
w(u'# 左= %s ⇒ 口 %d / file %d\n' % (sl, sn[0], sn[1]))
w(u'# 右= %s ⇒ 口 %d / file %d\n' % (ml, mn[0], mn[1]))
w(u'# 綴 = gen,tan(occ=出現單位/line=行單位),kitei(既定の下限),chu(nuku=註行除く/komu=註行込)\n')
w(u'\n--- 左のみに在る file(右で落ちた) ---\n')
only_l = sorted(set(st) - set(mt))
if not only_l: w(u'(無し)\n')
for f in only_l: w(u'%s\t口 %d\t%s\n' % (f, st[f][0], u' '.join(st[f][1])))
w(u'\n--- 右のみに在る file(左で落ちた) ---\n')
only_r = sorted(set(mt) - set(st))
if not only_r: w(u'(無し)\n')
for f in only_r: w(u'%s\t口 %d\t%s\n' % (f, mt[f][0], u' '.join(mt[f][1])))
w(u'\n--- 両方に在るが口數が違ふ file ---\n')
sa = 0
both = sorted(set(st) & set(mt))
chigau = [f for f in both if st[f][0] != mt[f][0]]
if not chigau: w(u'(無し)\n')
for f in chigau:
    a, b = set(st[f][1]), set(mt[f][1])
    w(u'%s\t左 %d ⇔ 右 %d\t左のみ名[%s] 右のみ名[%s]\n'
      % (f, st[f][0], mt[f][0], u' '.join(sorted(a-b)), u' '.join(sorted(b-a))))
w(u'\n--- 勘定 ---\n')
w(u'file: 左 %d ― 左のみ %d + 右のみ %d = 右 %d\n' % (sn[1], len(only_l), len(only_r), mn[1]))
kl = sum(st[f][0] for f in only_l); kr = sum(mt[f][0] for f in only_r)
kd = sum(mt[f][0] - st[f][0] for f in chigau)
w(u'口  : 左 %d ― 左のみ %d + 右のみ %d + 共通の増減 %+d = %d (右の實測 %d ―― 一致=%s)\n'
  % (sn[0], kl, kr, kd, sn[0] - kl + kr + kd, mn[0],
     u'真' if sn[0] - kl + kr + kd == mn[0] else u'★偽★'))
sys.exit(0)
