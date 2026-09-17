# -*- coding: utf-8 -*-
"""㋔ 衝突の測りを★一段深くする★器。
★40 の「M の交はり 78/78 対」は其の儘では衝突の数に非ず★ ――
  同じ path を二枝が改変して居ても、其の ★blob が同一★ なら(＝共通祖先から受け継いだ儘)
  併せて merge しても衝突せぬ。★衝突と数へてよいのは blob が異なる対のみ★。
形: 各枝 X の ⑴M path 毎に `git rev-parse X:<path>` で blob を取り、対毎に blob 相異を数へる。
出: raw/45_blob.tsv / raw/45_shoutotsu_shin.tsv
"""
import os, subprocess, itertools
ROOT = '/Users/momizimac/multi-agent-shogun'; MAIN = '4be3ee19e1c5'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

def rows(p):
    return [l.split('\t') for l in open(p, encoding='utf-8').read().split(chr(10))[1:] if l.strip()]
war = [(r[0], r[1]) for r in rows('raw/10_bosuu_warimochi.tsv')]

def blob(sha, path):
    r = subprocess.run(['git', '-C', ROOT, 'rev-parse', '%s:%s' % (sha, path)],
                       capture_output=True, text=True)
    return (r.returncode, r.stdout.strip() if r.returncode == 0 else '測れぬ(rc=%d)' % r.returncode)

Mpaths = {}
for n, s in war:
    o = subprocess.run(['git', '-C', ROOT, 'diff', '--name-status', '-z', '%s...%s' % (MAIN, s)],
                       capture_output=True).stdout.split(b'\x00')
    Mpaths[n] = [o[i+1].decode('utf-8', 'replace') for i in range(0, len(o)-1, 2) if o[i] == b'M']

B = {}
with open('raw/45_blob.tsv', 'w', encoding='utf-8') as f:
    f.write('枝名\tpath\tblob40\trev_parse_rc\tmain側blob40\t main と同じか\n')
    for n, s in war:
        for p in Mpaths[n]:
            rc, b = blob(s, p)
            rcm, bm = blob(MAIN, p)
            B[(n, p)] = b
            f.write('%s\t%s\t%s\t%d\t%s\t%s\n' % (n, p, b, rc, bm, '同' if b == bm else '異'))

with open('raw/45_shoutotsu_shin.tsv', 'w', encoding='utf-8') as f:
    f.write('枝X\t枝Y\t共有M_file数\t内blob同一\t内★blob相異=真の衝突★\t相異path\n')
    tot = 0; real = 0
    for (nx, _), (ny, _) in itertools.combinations(war, 2):
        sh = set(Mpaths[nx]) & set(Mpaths[ny])
        same = [p for p in sorted(sh) if B[(nx, p)] == B[(ny, p)]]
        diff = [p for p in sorted(sh) if B[(nx, p)] != B[(ny, p)]]
        tot += 1
        if diff:
            real += 1
        f.write('%s\t%s\t%d\t%d\t%d\t%s\n' % (nx, ny, len(sh), len(same), len(diff),
                                              ';'.join(diff) if diff else '-'))
print('対=%d / ★blob 相異が在る対(真の衝突)=%d★' % (tot, real))
import collections
c = collections.Counter()
for (nx, _), (ny, _) in itertools.combinations(war, 2):
    for p in sorted(set(Mpaths[nx]) & set(Mpaths[ny])):
        if B[(nx, p)] != B[(ny, p)]:
            c[p] += 1
for p, k in c.most_common():
    print('  相異 path %s ―― %d 対' % (p, k))
