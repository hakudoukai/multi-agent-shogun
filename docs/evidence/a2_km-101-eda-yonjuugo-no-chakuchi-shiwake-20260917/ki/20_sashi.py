# -*- coding: utf-8 -*-
"""㋑㋒ 二つの差分を★測り分ける★器。
 ⑴ 対 origin/main: `git diff --name-only 4be3ee19e1c5...<sha>` の行数。
    ★之は「此の枝が変へた file 数」では無い★ ―― 共通祖先から見て
    ★origin/main と此の枝の間に開いて居る file 数★(＝main が何 file 遅れて居るか)である。
 ⑵ 自前: 60本の mac tip の内 ★X の真の祖先★(is-ancestor 真 かつ sha≠X)を悉く挙げ、
    `git rev-list --count B..X` が最小の B を選び `git diff --name-only B..X` の行数。
    ★祖先 tip が一本も無ければ ⑵=測れぬ★(0 とは書かぬ)。
 ㋒ commit 数 = `git rev-list --count 4be3ee19e1c5..<sha>` / 触る top-level 領域。
★同点の断り★: rev-list --count が最小の B が複数在る時は ★sha の辞書順で最小★ を採り、
              同点の本数を tsv の欄に残す(恣意で選ばぬ)。
★名の断り★: file 数は `-z`(NUL 区切り)で数へる。改行を含む名でも壊れぬ。
              併せて素の行数も測り、食ひ違へば tsv に出る。
出: raw/20_sashi.tsv / raw/20_sosen.tsv
"""
import os, subprocess, re
ROOT = '/Users/momizimac/multi-agent-shogun'
MAIN = '4be3ee19e1c5'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

def g(*a):
    r = subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True)
    return r.returncode, r.stdout, r.stderr

def names_z(spec):
    rc, out, err = g('diff', '--name-only', '-z', spec)
    xs = [x for x in out.split(b'\x00') if x]
    return rc, xs, err.decode('utf-8', 'replace')

def names_line(spec):
    rc, out, err = g('diff', '--name-only', spec)
    t = out.decode('utf-8', 'replace')
    n = 0 if t == '' else len(t.rstrip(chr(10)).split(chr(10)))
    return rc, n

def count(spec):
    rc, out, _ = g('rev-list', '--count', spec)
    return rc, out.decode().strip()

def ryouiki(xs):
    ts = []
    for x in xs:
        s = x.decode('utf-8', 'replace')
        ts.append(s.split('/')[0] if '/' in s else s)
    return sorted(set(ts))

war = []
for line in open('raw/10_bosuu_warimochi.tsv', encoding='utf-8').read().split(chr(10))[1:]:
    if line.strip():
        p = line.split('\t')
        war.append((p[0], p[1]))
mac60 = []
for line in open('raw/10_bosuu_mac60.tsv', encoding='utf-8').read().split(chr(10))[1:]:
    if line.strip():
        p = line.split('\t')
        mac60.append((p[0], p[1]))

fs = open('raw/20_sashi.tsv', 'w', encoding='utf-8')
fs.write('\t'.join(['枝名', 'sha40', '⑴file数_対main_NUL', '⑴行数_対main_行',
                    '⑵file数_自前_NUL', '⑵行数_自前_行', '⑵基準枝B', '⑵基準B迄のcommit数',
                    '祖先tip本数', '同点B本数', 'commit数_main起点', '領域⑴', '領域⑵']) + chr(10))
fo = open('raw/20_sosen.tsv', 'w', encoding='utf-8')
fo.write('\t'.join(['枝名X', 'sha40X', '祖先tip枝名B', 'sha40B', 'rev_list_count_B..X']) + chr(10))

for name, sha in war:
    rc1, xs1, e1 = names_z('%s...%s' % (MAIN, sha))
    assert rc1 == 0, '★⑴ diff rc=%d %s %s★' % (rc1, name, e1)
    rcl1, n1l = names_line('%s...%s' % (MAIN, sha))
    rcc, ncom = count('%s..%s' % (MAIN, sha))
    assert rcc == 0
    # 祖先 tip を悉く挙げる
    sosen = []
    for bn, bs in mac60:
        if bs == sha:
            continue
        r = subprocess.run(['git', '-C', ROOT, 'merge-base', '--is-ancestor', bs, sha],
                           capture_output=True)
        if r.returncode == 0:
            rc2, c = count('%s..%s' % (bs, sha))
            assert rc2 == 0
            sosen.append((bn, bs, int(c)))
    sosen.sort(key=lambda t: (t[2], t[1]))
    for t in sosen:
        fo.write('%s\t%s\t%s\t%s\t%d\n' % (name, sha, t[0], t[1], t[2]))
    if sosen:
        mn = sosen[0][2]
        tie = [t for t in sosen if t[2] == mn]
        B = tie[0]          # 同点は sha 辞書順で最小(sort 済)
        rc2, xs2, e2 = names_z('%s..%s' % (B[1], sha))
        assert rc2 == 0, '★⑵ diff rc=%d %s %s★' % (rc2, name, e2)
        rcl2, n2l = names_line('%s..%s' % (B[1], sha))
        c2 = '%d' % len(xs2)
        c2l = '%d' % n2l
        bname = B[0]
        bcnt = '%d' % B[2]
        ntie = '%d' % len(tie)
        ry2 = ','.join(ryouiki(xs2)) or '(差分なし)'
    else:
        c2 = c2l = '測れぬ'
        bname = '測れぬ(祖先tip 0本)'
        bcnt = '測れぬ'
        ntie = '0'
        ry2 = '測れぬ'
    fs.write('\t'.join([name, sha, str(len(xs1)), str(n1l), c2, c2l, bname, bcnt,
                        str(len(sosen)), ntie, ncom,
                        ','.join(ryouiki(xs1)) or '(差分なし)', ry2]) + chr(10))
    print('%-62s ⑴=%3d ⑵=%-6s 祖先tip=%2d commit=%s' % (name[:62], len(xs1), c2, len(sosen), ncom))
fs.close(); fo.close()
