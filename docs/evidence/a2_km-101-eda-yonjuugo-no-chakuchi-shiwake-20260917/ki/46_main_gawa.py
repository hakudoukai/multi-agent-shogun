# -*- coding: utf-8 -*-
"""㋔ ★main 側の動き★ と重なるかを測る器(PR を出した時に現に当たる相手)。
各枝 X に就き:
  merge-base(main, X) を採り、★main 側が merge-base から変へた file★ と
  ★X 側が merge-base から変へた file(=⑴)★ の交はりを数へ、
  其の path の blob が main と X で異なるかを書く(異なれば ★手で解く要り★)。
★之が「PR が当たる相手」である ―― 13本同士の交はり(45)とは別物ゆゑ混ぜぬ。★
出: raw/46_main_gawa.tsv
"""
import os, subprocess
ROOT = '/Users/momizimac/multi-agent-shogun'; MAIN = '4be3ee19e1c5'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

def rows(p):
    return [l.split('\t') for l in open(p, encoding='utf-8').read().split(chr(10))[1:] if l.strip()]
war = [(r[0], r[1]) for r in rows('raw/10_bosuu_warimochi.tsv')]

def nz(spec):
    o = subprocess.run(['git', '-C', ROOT, 'diff', '--name-only', '-z', spec],
                       capture_output=True).stdout
    return set(x.decode('utf-8', 'replace') for x in o.split(b'\x00') if x)

def blob(sha, p):
    r = subprocess.run(['git', '-C', ROOT, 'rev-parse', '%s:%s' % (sha, p)],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else '無し(rc=%d)' % r.returncode

with open('raw/46_main_gawa.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(['枝名', 'merge_base_sha40', 'main側変更file数', 'X側変更file数(⑴)',
                       '交はりfile数', '内blob相異(手で解く要り)', '交はるpath']) + chr(10))
    for name, sha in war:
        mb = subprocess.run(['git', '-C', ROOT, 'merge-base', MAIN, sha],
                            capture_output=True, text=True).stdout.strip()
        m = nz('%s..%s' % (mb, MAIN))
        x = nz('%s..%s' % (mb, sha))
        inter = sorted(m & x)
        diff = [p for p in inter if blob(MAIN, p) != blob(sha, p)]
        f.write('\t'.join([name, mb, str(len(m)), str(len(x)), str(len(inter)),
                           str(len(diff)), ';'.join(inter) if inter else '-']) + chr(10))
print(open('raw/46_main_gawa.tsv', encoding='utf-8').read())
