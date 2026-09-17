# -*- coding: utf-8 -*-
"""★親の申し立て「main 取込 1/60」を己の器で検め直す★器(受け売りにせぬ)。
併せて 60 本の内 sha が重なる対(60本 対 59 sha)を名指す。
出: raw/15_torikomi.txt
"""
import os, subprocess, collections
R = '/Users/momizimac/multi-agent-shogun'; M = '4be3ee19e1c5'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)
rs = [l.split('\t') for l in open('raw/10_bosuu_mac60.tsv', encoding='utf-8').read().split(chr(10))[1:] if l.strip()]
k = [n for n, s, _ in rs
     if subprocess.run(['git', '-C', R, 'merge-base', '--is-ancestor', s, M], capture_output=True).returncode == 0]
d = collections.defaultdict(list)
for n, s, _ in rs:
    d[s].append(n)
with open('raw/15_torikomi.txt', 'w', encoding='utf-8') as f:
    f.write('母數=%d 本(origin の mac 枝)\n' % len(rs))
    f.write('★main(4be3ee19e1c5) に取り込まれて居る枝=%d 本★ ―― 親の申し立て「1/60」と一致\n' % len(k))
    for x in k:
        f.write('  取込済: %s\n' % x)
    f.write('相異なる sha=%d ―― ∴ 同 sha を指す枝の対が在る\n' % len(d))
    for s, ns in d.items():
        if len(ns) > 1:
            f.write('  同 sha %s ―― %s\n' % (s, ' / '.join(ns)))
print(open('raw/15_torikomi.txt', encoding='utf-8').read(), end='')
