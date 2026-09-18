#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 33_sou.py ―― ★「當席の 22口/8file は何の定義で立つか」を枡目で掃く器★(第53弾 ㋑)
# 源 × 單位 × 既定閾 × 註 の全枡を 30_kazu.py で数へ、頭に 根・刻・rc を書く。
# 使ひ方: 33_sou.py --gens "disk index <rev>..." [--kazu <路>]
import sys, os, subprocess, time

d = {'--gens': None, '--kazu': os.path.join(os.path.dirname(os.path.abspath(__file__)), '30_kazu.py'),
     '--ne': u'scripts .claude'}
av = sys.argv[1:]; i = 0
while i < len(av):
    if av[i] in d and i+1 < len(av): d[av[i]] = av[i+1]; i += 2; continue
    sys.stderr.write(u'★測れぬ: 知らぬ引数 %s★\n' % av[i]); sys.exit(2)
if not d['--gens']:
    sys.stderr.write(u'★測れぬ: --gens を argv で渡せ★\n'); sys.exit(2)
gens = d['--gens'].split()

rc_top = subprocess.Popen(['git','rev-parse','--show-toplevel'], stdout=subprocess.PIPE)
top = rc_top.communicate()[0].decode('utf-8').strip()
w = sys.stdout.write
w(u'# 33_sou ―― 枡目の掃き / 刻= %s\n' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
w(u'# ★根(歩き根 一本)= %s★ / 頂= %s / 深さ= 全深(git 追跡の全 path)\n' % (d['--ne'], top))
w(u'# 器= 30_kazu.py(定義丁の條を持つ唯一の器) / 源の数= %d / 枡= 源 × 單位2 × 既定閾2 × 註2\n' % len(gens))
w(u'# 綴: 源 <TAB> 單位(occ=出現/line=行) <TAB> 既定閾(1=既定>=1 / 0=下限無し) <TAB> 註(nuku=除く/komu=込む) <TAB> 口 <TAB> file <TAB> rc\n')
w(u'# ★定義丁(專任1 km-77 逐語)の枡 = 單位 occ ∧ 既定閾 1 ∧ 註 nuku★ ―― 他の枡は「別の母數」である\n')
w(u'#\n')
n = 0; warui = 0
for g in gens:
    for tan in ('occ', 'line'):
        for kitei in ('1', '0'):
            for chu in ('nuku', 'komu'):
                p = subprocess.Popen([sys.executable, '-B', d['--kazu'], '--gen', g,
                                      '--ne', d['--ne'], '--tan', tan, '--kitei', kitei, '--chu', chu],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                o, e = p.communicate(); n += 1
                kuchi = fil = u'―'
                for ln in o.decode('utf-8').split(u'\n'):
                    if ln.startswith(u'★[丁閾] 口='):
                        t = ln.replace(u'★', u'').split()
                        kuchi = t[1].split(u'=')[-1] or t[2]
                        fil = t[-1]
                        break
                if p.returncode != 0: warui += 1
                w(u'%s\t%s\t%s\t%s\t口= %s\tfile= %s\trc= %d\n'
                  % (g, tan, kitei, chu, kuchi, fil, p.returncode))
w(u'#\n# 枡の数= %d / rc≠0 の枡= %d\n' % (n, warui))
sys.exit(0 if warui == 0 else 4)
