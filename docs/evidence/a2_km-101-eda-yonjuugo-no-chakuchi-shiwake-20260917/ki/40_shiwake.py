# -*- coding: utf-8 -*-
"""㋓㋔ 仕分けと衝突の器。★拠り所は下の KIJUN に先に宣し、其の儘機械で当てる(恣意を挟まぬ)。★

KIJUN(逐語):
  丙(測れぬ) = ①手許に物が無い(cat-file rc≠0) または ②祖先 tip 0 本で ⑵ が測れぬ。
  乙(捨てる=PR を起こさず理事長裁を待つ) = ①⑵=0 file(自前の中身が無い) または
                                           ②tip が他の mac tip の★真の祖先★(他枝が悉く含む)。
  甲(着地させる=PR) = 丙でも乙でも無い物。
  ★乙は「消す」に非ず★ ―― 裁 325884 により不可逆削除は理事長専管。乙 = ★PR を起こさず裁を待つ★。

衝突の測り(㋔の一項):
  ⑴(対 main)の内 ★M(既存 file の改変)★ の path を枝毎に採り、割当13本の総当りで交はりを数へる。
  ★A(追加)のみの重なりは衝突に非ず★(別 path を足すだけ)ゆゑ M に絞る。
  併せて ⑵(自前)の path の交はりも数へ、両方を紙に残す。
出: raw/40_status.tsv / raw/40_shoutotsu_M.tsv / raw/40_shiwake.tsv
"""
import os, subprocess, itertools
ROOT = '/Users/momizimac/multi-agent-shogun'
MAIN = '4be3ee19e1c5'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

def rows(p):
    return [l.split('\t') for l in open(p, encoding='utf-8').read().split(chr(10))[1:] if l.strip()]

def name_status(spec):
    r = subprocess.run(['git', '-C', ROOT, 'diff', '--name-status', '-z', spec], capture_output=True)
    assert r.returncode == 0, spec
    toks = [t for t in r.stdout.split(b'\x00')]
    out = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if not t:
            i += 1; continue
        st = t.decode()
        if st[0] in 'RC':
            old = toks[i+1].decode('utf-8', 'replace'); new = toks[i+2].decode('utf-8', 'replace')
            out.append((st[0], new, old)); i += 3
        else:
            out.append((st[0], toks[i+1].decode('utf-8', 'replace'), '-')); i += 2
    return out

war = [(r[0], r[1]) for r in rows('raw/10_bosuu_warimochi.tsv')]
sashi = {r[0]: r for r in rows('raw/20_sashi.tsv')}
nomi = {r[0]: int(r[2]) for r in rows('raw/30_soto_nomikomi.tsv')}
catrc = {r[0]: int(r[2]) for r in rows('raw/10_bosuu_warimochi.tsv')}

Mset = {}
own = {}
fs = open('raw/40_status.tsv', 'w', encoding='utf-8')
fs.write('\t'.join(['枝名', '⑴A_追加', '⑴M_改変', '⑴D_削除', '⑴R_改名',
                    '⑵A_追加', '⑵M_改変', '⑵D_削除', '⑵R_改名', '自前は追加のみか']) + chr(10))
for name, sha in war:
    ns1 = name_status('%s...%s' % (MAIN, sha))
    Mset[name] = set(p for st, p, _ in ns1 if st == 'M')
    r = sashi[name]
    B = r[6]
    if r[4] == '測れぬ':
        ns2 = []
        own[name] = set()
        add_only = '測れぬ'
    else:
        bsha = [s for n, s in
                [(x[0], x[1]) for x in rows('raw/10_bosuu_mac60.tsv')] if n == B][0]
        ns2 = name_status('%s..%s' % (bsha, sha))
        own[name] = set(p for st, p, _ in ns2)
        add_only = '追加のみ' if all(st == 'A' for st, _, _ in ns2) and ns2 else ('空' if not ns2 else '改変を含む')
    def c(ns, k):
        return sum(1 for st, _, _ in ns if st == k)
    fs.write('\t'.join([name] + ['%d' % c(ns1, k) for k in 'AMDR'] +
                       (['%d' % c(ns2, k) for k in 'AMDR'] if r[4] != '測れぬ' else ['測れぬ']*4) +
                       [add_only]) + chr(10))
fs.close()

with open('raw/40_shoutotsu_M.tsv', 'w', encoding='utf-8') as f:
    f.write('枝X\t枝Y\t⑴Mの交はり_file数\t⑵自前pathの交はり_file数\t交はるMのpath(先頭5)\n')
    for (nx, _), (ny, _) in itertools.combinations(war, 2):
        im = Mset[nx] & Mset[ny]
        io = own[nx] & own[ny]
        f.write('%s\t%s\t%d\t%d\t%s\n' % (nx, ny, len(im), len(io),
                ';'.join(sorted(im)[:5]) if im else '-'))

with open('raw/40_shiwake.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(['枝名', 'sha40', '⑴file数', '⑵file数', 'commit数', '領域⑵',
                       '甲乙丙', '理由(一行)']) + chr(10))
    tally = {}
    for name, sha in war:
        r = sashi[name]
        if catrc[name] != 0:
            k, riyuu = '丙', '手許に物が無い(cat-file rc≠0) ―― 測れぬ'
        elif r[4] == '測れぬ':
            k, riyuu = '丙', '祖先 tip が一本も無く ⑵ が測れぬ'
        elif int(r[4]) == 0:
            k, riyuu = '乙', '⑵=0 file ―― 直近祖先 tip と中身が同じで、単独で足す物が無い'
        elif nomi[name] > 0:
            k, riyuu = '乙', 'tip が他の mac tip %d 本の真の祖先 ―― 其の末端が含む' % nomi[name]
        else:
            k = '甲'
            riyuu = '鎖の末端(呑む tip 0本)で自前 %s file を持つ ―― 着地させねば此の分は何処にも残らぬ' % r[4]
        tally[k] = tally.get(k, 0) + 1
        f.write('\t'.join([name, sha, r[2], r[4], r[10], r[12], k, riyuu]) + chr(10))
print('仕分け:', tally)
print(open('raw/40_status.tsv', encoding='utf-8').read())
