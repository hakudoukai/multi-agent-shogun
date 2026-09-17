# -*- coding: utf-8 -*-
"""㋑: 46 枝の ★門控・driver★ から、器の名を逐語で拾ふ。

拾ふ根(母數の宣):
  各枝 X に付き `git diff --name-only <origin/main>...X -- docs/evidence/` の内、
  ★.py / .sh で終るか、path に /_gate/ か /ki/ を含む★物のみ。
  (=其の枝が★自ら加へた★門控と driver。origin/main から受け繼いだ物は根の外。
   ★「根の外」は「無い」の意では無い。★)

拾ふ字(逐語):
  ⑴ scripts/checks/<名>      ⑵ bin/<名>(~/bin・/Users/*/bin を含む)
  ⑶ karo_mac_<名>.py|.sh     ⑷ inbox_mark_read.py / agent_letter.py / deferral_gate.py
  ⑸ <名>gate<名>.sh|.py
  ★拾つた字は「呼んで居る」の證に非ず ―― 註や紙の本文にも現れる。★
  ∴ 出目は「名が現れた」の數であり、「走つた」の數では★ない★。
出目: raw/30_hiroi.tsv (器 x 枝数 x 延べ) / raw/30_hiroi_eda.tsv (枝 x 器)
"""
import subprocess, os, re, collections
os.chdir('/Users/momizimac/multi-agent-shogun')
BD = 'docs/evidence/ashigaru-mac-2_km-104-ki-no-arika-to-unpan-20260917'
OUT = os.path.join(BD, 'raw')
MAIN = '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'
PAT = re.compile(
    r'(?:scripts/checks/[A-Za-z0-9_.+-]+'
    r'|(?:~|/Users/[A-Za-z0-9_.-]+)?/?bin/[A-Za-z0-9_.+-]+'
    r'|karo_mac_[A-Za-z0-9_.+-]+'
    r'|inbox_mark_read\.py|agent_letter\.py|deferral_gate\.py'
    r'|[A-Za-z0-9_.+-]*gate[A-Za-z0-9_.+-]*\.(?:sh|py))')

def norm(tok):
    """器の名に畳む(置き場の別は㋐で測る ―― 此処では★名★のみ)。"""
    t = tok.strip()
    if t.startswith('~'):
        t = t[1:]
    return t.rsplit('/', 1)[-1]

eda = [ln.rstrip('\n').split('\t') for ln in open(os.path.join(OUT, '20_eda45.txt'), encoding='utf-8') if ln.strip()]
print('枝 母數=%d' % len(eda))
ki_eda = collections.defaultdict(set)      # 器名 -> 枝の集合
ki_nobe = collections.Counter()            # 器名 -> 延べ出現
eda_ki = {}
nashi = []
for sha, name in eda:
    p = subprocess.run(['git', 'diff', '--name-only', '%s...%s' % (MAIN, sha), '--', 'docs/evidence/'],
                       capture_output=True, text=True)
    assert p.returncode == 0, (name, p.returncode)
    paths = [x for x in p.stdout.split('\n') if x and
             (x.endswith('.py') or x.endswith('.sh') or '/_gate/' in x or '/ki/' in x)]
    if not paths:
        nashi.append(name); eda_ki[name] = set(); continue
    g = subprocess.run(['git', 'grep', '-I', '-h', '-o', '-E', PAT.pattern.replace('(?:', '('), sha, '--'] + paths,
                       capture_output=True, text=True)
    # git grep rc: 0=当り 1=無し 其れ以外=疵
    assert g.returncode in (0, 1), (name, g.returncode, g.stderr[:200])
    s = set()
    for tok in g.stdout.split('\n'):
        if not tok:
            continue
        n = norm(tok)
        if not n:
            continue
        s.add(n); ki_nobe[n] += 1
    for n in s:
        ki_eda[n].add(name)
    eda_ki[name] = s
print('門控/driver が 0 本の枝=%d %s' % (len(nashi), ' '.join(nashi[:4])))
with open(os.path.join(OUT, '30_hiroi.tsv'), 'w', encoding='utf-8') as f:
    f.write('ki_mei\teda_suu(46中)\tnobe_shutsugen\n')
    for n, es in sorted(ki_eda.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        f.write('%s\t%d\t%d\n' % (n, len(es), ki_nobe[n]))
with open(os.path.join(OUT, '30_hiroi_eda.tsv'), 'w', encoding='utf-8') as f:
    f.write('eda\tki_shurui\tki_mei\n')
    for sha, name in eda:
        s = eda_ki[name]
        f.write('%s\t%d\t%s\n' % (name, len(s), ';'.join(sorted(s)) if s else '-'))
print('拾つた器の名 相異=%d / 延べ=%d' % (len(ki_eda), sum(ki_nobe.values())))
