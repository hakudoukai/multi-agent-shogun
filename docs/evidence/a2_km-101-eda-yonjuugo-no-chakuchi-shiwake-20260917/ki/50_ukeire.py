# -*- coding: utf-8 -*-
"""㋔ 受入条件を★物で検める★器(checkout せず `git show` の読取のみ)。
検める三つ:
  ㊀ 臺帳が★束内相対★か ―― 自前差分が足した `_manifest.txt`/`MANIFEST.txt` を blob で読み、
     `path=` の値が `docs/` で始まれば ★旧形(repo 相対)★、然らずんば ★束内相対★(裁 seq322699)。
  ㊁ 門控が在り ★rc=0★ か ―― 自前差分が足した `*.rc`(門の控)を読み、中身の数を採る。
  ㊂ 対照(陽性/負)の紙が在るか ―― 自前差分の path に `taishou`/`対照`/`selftest` を含む物を数へる。
★之は「其の枝の中で門が通つた」の控を読んだだけである★ ―― 今の main の上で通る事の證では★無い★。
出: raw/50_ukeire.tsv / raw/50_daichou_gyou.tsv
"""
import os, subprocess, re
ROOT = '/Users/momizimac/multi-agent-shogun'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

def rows(p):
    return [l.split('\t') for l in open(p, encoding='utf-8').read().split(chr(10))[1:] if l.strip()]
war = [(r[0], r[1]) for r in rows('raw/10_bosuu_warimochi.tsv')]
sashi = {r[0]: r for r in rows('raw/20_sashi.tsv')}
mac60 = {r[0]: r[1] for r in rows('raw/10_bosuu_mac60.tsv')}

def show(sha, path):
    r = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (sha, path)], capture_output=True)
    return r.returncode, r.stdout

fu = open('raw/50_ukeire.tsv', 'w', encoding='utf-8')
fu.write('\t'.join(['枝名', '自前file数', '臺帳file数', '束内相対の臺帳', '旧形(docs/起し)の臺帳',
                    '門控rc_file数', 'rc=0の控', 'rc!=0の控', '対照らしき紙数']) + chr(10))
fd = open('raw/50_daichou_gyou.tsv', 'w', encoding='utf-8')
fd.write('枝名\t臺帳path\t行数path=\t先頭のpath=値\t形\n')

for name, sha in war:
    r = sashi[name]
    B = r[6]
    if r[4] == '測れぬ':
        fu.write('%s\t測れぬ\t測れぬ\t測れぬ\t測れぬ\t測れぬ\t測れぬ\t測れぬ\t測れぬ\n' % name)
        continue
    bsha = mac60[B]
    out = subprocess.run(['git', '-C', ROOT, 'diff', '--name-only', '-z', '%s..%s' % (bsha, sha)],
                         capture_output=True).stdout
    ps = [x.decode('utf-8', 'replace') for x in out.split(b'\x00') if x]
    dai = [p for p in ps if os.path.basename(p) in ('_manifest.txt', 'MANIFEST.txt')]
    rcs = [p for p in ps if p.endswith('.rc')]
    tai = [p for p in ps if re.search(r'taishou|selftest|対照', p)]
    sotai = kyuu = 0
    for p in dai:
        rc, b = show(sha, p)
        if rc != 0:
            fd.write('%s\t%s\t測れぬ(show rc=%d)\t-\t測れぬ\n' % (name, p, rc)); continue
        t = b.decode('utf-8', 'replace')
        vs = [l[5:].split(' ', 1)[0] for l in t.split(chr(10)) if l.startswith('path=')]
        kata = '測れぬ(path=0行)'
        if vs:
            kata = '旧形(docs/起し)' if vs[0].startswith('docs/') else '束内相対'
            if kata == '束内相対':
                sotai += 1
            else:
                kyuu += 1
        fd.write('%s\t%s\t%d\t%s\t%s\n' % (name, p, len(vs), vs[0] if vs else '-', kata))
    z = nz = 0
    for p in rcs:
        rc, b = show(sha, p)
        if rc != 0:
            nz += 1; continue
        t = b.decode('utf-8', 'replace').strip()
        if t == '0':
            z += 1
        else:
            nz += 1
    fu.write('\t'.join([name, r[4], str(len(dai)), str(sotai), str(kyuu),
                        str(len(rcs)), str(z), str(nz), str(len(tai))]) + chr(10))
fu.close(); fd.close()
print(open('raw/50_ukeire.tsv', encoding='utf-8').read())
