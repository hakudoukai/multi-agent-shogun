# -*- coding: utf-8 -*-
"""㋕ 重なりを測る器。
 甲: 割当 13 本の内 ★tip が他の tip の真の祖先★ に成つて居る対を悉く名指す(鎖)。
 乙: 割当の外(60本)まで広げ、★割当の枝が他席の枝に呑まれて居るか★も測る。
 ★真の祖先★の定義: `git merge-base --is-ancestor A B` rc=0 かつ sha(A)≠sha(B)。
   (is-ancestor は A=B でも rc=0 を返す ∴ sha 同値は除く ―― 之を書かねば自分が自分の祖先に成る)
出: raw/30_uchi_pairs.tsv / raw/30_soto_nomikomi.tsv / raw/30_kusari.txt
"""
import os, subprocess
ROOT = '/Users/momizimac/multi-agent-shogun'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

def rows(p):
    return [l.split('\t') for l in open(p, encoding='utf-8').read().split(chr(10))[1:] if l.strip()]

war = [(r[0], r[1]) for r in rows('raw/10_bosuu_warimochi.tsv')]
mac60 = [(r[0], r[1]) for r in rows('raw/10_bosuu_mac60.tsv')]

def anc(a, b):
    if a == b:
        return False
    return subprocess.run(['git', '-C', ROOT, 'merge-base', '--is-ancestor', a, b],
                          capture_output=True).returncode == 0

def cnt(a, b):
    r = subprocess.run(['git', '-C', ROOT, 'rev-list', '--count', '%s..%s' % (a, b)],
                       capture_output=True, text=True)
    assert r.returncode == 0
    return int(r.stdout.strip())

with open('raw/30_uchi_pairs.tsv', 'w', encoding='utf-8') as f:
    f.write('祖先側枝A\tsha40A\t子孫側枝B\tsha40B\tcommit数A..B\n')
    uchi = []
    for na, sa in war:
        for nb, sb in war:
            if anc(sa, sb):
                uchi.append((na, sa, nb, sb, cnt(sa, sb)))
                f.write('%s\t%s\t%s\t%s\t%d\n' % uchi[-1])
    if not uchi:
        f.write('(割当13本の中に祖先=子孫の対は一つも無し)\t-\t-\t-\t-\n')

with open('raw/30_soto_nomikomi.tsv', 'w', encoding='utf-8') as f:
    f.write('割当枝X\tsha40X\tXを呑む他tip本数\t呑む枝名(;区切)\n')
    nomi = {}
    for nx, sx in war:
        ds = [n for n, s in mac60 if s != sx and anc(sx, s)]
        nomi[nx] = ds
        f.write('%s\t%s\t%d\t%s\n' % (nx, sx, len(ds), ';'.join(sorted(set(ds))) if ds else '-'))

# 鎖を描く(割当内)
with open('raw/30_kusari.txt', 'w', encoding='utf-8') as f:
    f.write('★割当13本の内での鎖(A が B の真の祖先なら A → B)★\n')
    if not uchi:
        f.write('鎖 = 0 本(13本は互ひに独立 ―― 一本も他の一本を含まぬ)\n')
    for t in uchi:
        f.write('%s → %s (commit差 %d)\n' % (t[0], t[2], t[4]))
    f.write('\n★割当の外(60本)まで見た「呑まれ」★\n')
    for nx, ds in nomi.items():
        f.write('%s : 呑む tip %d 本%s\n' % (nx, len(ds), (' ―― ' + ';'.join(sorted(set(ds)))) if ds else ''))
print(open('raw/30_kusari.txt', encoding='utf-8').read())
