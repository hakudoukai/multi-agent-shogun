# -*- coding: utf-8 -*-
"""㋐: ★器の母數を宣し、在り処を四つの目で測る★。

母數の宣(先に宣してから使ふ):
  母數 = (A) ∪ (B)
  (A) disk 上の実体 ―― scripts/checks/ と /Users/momizimac/bin の直下の★常の file★。
      除く: dir・__pycache__・`.bak`/`.orig`/`.pre`/`.new` を名に含む控・sweep_manifest.json 等の非実行物は
      ★除かず載せる★(判ずるのは後)。★「除いた」は「無い」の意では無い。★
  (B) ㋑(ki/30_hiroi.py)が 46 枝の門控・driver から逐語で拾つた名の内、★甲=艦隊の器★と判じた物。
  判じの則(機械が決める・字面で決めぬ):
    甲 = 其の名の file が (A) の歩き根の下に実在する(控 .bak 等も可)
    丙 = (A) に無く、束の中(docs/evidence/**)に同名の file が在る ―― ★束内の私器★
    乙 = (A) にも束にも無く、`command -v` が /bin /usr/bin /usr/sbin /opt/homebrew に解ける ―― ★系の器★
    丁 = 何れにも当たらぬ ―― ★不明★
  ★甲のみを㋐の表に載せる。乙丙丁は数だけ書き、名は raw に残す。★

四つの目(一本づつ):
  ⑴ disk 有無        = os.path.exists(実在の path)
  ⑵ origin/main 有無 = `git ls-tree -r --name-only 4be3ee19e1c5 -- <repo 相対 path>` が非空
  ⑶ local main 有無  = 同上を main(363d5fb0…) で
  ⑷ 抱へる ref 本数  = ★二つの母數で測る★
       甲: 手許の ref 悉く(`git for-each-ref` = 90本・内訳を紙に書く)
       乙: origin の heads 悉く(ls-remote 240本・手許に物が無い sha は「測れぬ」へ)
  ★~/bin は repo の外ゆゑ、⑵⑶⑷は構造上 悉く「無」である。★
   之は「器が無い」の意では無く、★「git が知り得ぬ置き場に在る」★の意である。
出目: raw/40_arika.tsv / raw/40_bunrui.tsv / raw/40_ref_bosuu.txt
"""
import os, re, subprocess, collections, shutil
os.chdir('/Users/momizimac/multi-agent-shogun')
BD = 'docs/evidence/ashigaru-mac-2_km-104-ki-no-arika-to-unpan-20260917'
OUT = os.path.join(BD, 'raw')
MAIN_O = '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'
MAIN_L = '363d5fb060845171338c067ef42bfcbef8ad9188'
CHK = 'scripts/checks'
HBIN = '/Users/momizimac/bin'

# ---- (A) disk 実体 ----
disk = {}          # 名 -> (置き場, 実 path, repo 相対 path か None)
for n in sorted(os.listdir(CHK)):
    p = os.path.join(CHK, n)
    if os.path.isfile(p):
        disk[n] = ('scripts/checks', p, p)
for n in sorted(os.listdir(HBIN)):
    p = os.path.join(HBIN, n)
    if os.path.isfile(p) and n not in disk:
        disk[n] = ('~/bin', p, None)
print('(A) disk 実体=%d (scripts/checks=%d, ~/bin=%d)' % (
    len(disk), sum(1 for v in disk.values() if v[0] == 'scripts/checks'),
    sum(1 for v in disk.values() if v[0] == '~/bin')))

# ---- (B) ㋑の拾ひ ----
hiroi = {}
for i, ln in enumerate(open(os.path.join(OUT, '30_hiroi.tsv'), encoding='utf-8')):
    if i == 0:
        continue
    a = ln.rstrip('\n').split('\t')
    hiroi[a[0]] = (int(a[1]), int(a[2]))
print('(B) ㋑の拾ひ 相異=%d' % len(hiroi))

# 束内の私器か(丙)
p = subprocess.run(['git', 'ls-files', '--', 'docs/evidence/'], capture_output=True, text=True)
assert p.returncode == 0
taba_base = set(x.rsplit('/', 1)[-1] for x in p.stdout.split('\n') if x)
print('束内(追跡下)の basename 相異=%d' % len(taba_base))

bunrui = {}
for n in hiroi:
    if n in disk:
        bunrui[n] = '甲'
    elif any(b == n or b.startswith(n) for b in taba_base) and n not in disk:
        bunrui[n] = '丙'
    elif shutil.which(n) and shutil.which(n).rsplit('/', 1)[0] in ('/bin', '/usr/bin', '/usr/sbin', '/opt/homebrew/bin'):
        bunrui[n] = '乙'
    else:
        bunrui[n] = '丁'
c = collections.Counter(bunrui.values())
print('(B) 判じ: 甲=%d 乙=%d 丙=%d 丁=%d' % (c['甲'], c['乙'], c['丙'], c['丁']))
with open(os.path.join(OUT, '40_bunrui.tsv'), 'w', encoding='utf-8') as f:
    f.write('ki_mei\thanji\teda_suu\tnobe\n')
    for n in sorted(hiroi, key=lambda x: (bunrui[x], -hiroi[x][0], x)):
        f.write('%s\t%s\t%d\t%d\n' % (n, bunrui[n], hiroi[n][0], hiroi[n][1]))

# ---- ref の母數 ----
local_refs = []
p = subprocess.run(['git', 'for-each-ref', '--format=%(refname) %(objecttype) %(objectname)'],
                   capture_output=True, text=True)
assert p.returncode == 0
for ln in p.stdout.split('\n'):
    if not ln:
        continue
    rn, ot, on = ln.split(' ')
    local_refs.append((rn, ot, on))
remote_heads = []
for ln in open(os.path.join(OUT, '00_lsremote.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if ln:
        sha, ref = ln.split('\t', 1)
        remote_heads.append((ref, sha))

def inv(sha):
    """其の commit が抱へる scripts/checks/ の path 集合。手許に物が無ければ None(測れぬ)。"""
    r = subprocess.run(['git', 'ls-tree', '-r', '--name-only', sha + '^{commit}', '--', CHK + '/'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return set(x for x in r.stdout.split('\n') if x)

cacheL, measL, unmeasL = {}, 0, 0
for rn, ot, on in local_refs:
    s = inv(on)
    if s is None:
        unmeasL += 1
    else:
        measL += 1
    cacheL[rn] = s
cacheR, measR, unmeasR = {}, 0, 0
for ref, sha in remote_heads:
    s = inv(sha)
    if s is None:
        unmeasR += 1
    else:
        measR += 1
    cacheR[ref] = s
with open(os.path.join(OUT, '40_ref_bosuu.txt'), 'w', encoding='utf-8') as f:
    f.write('手許 ref 母數=%d (測れた=%d 測れぬ=%d)\n' % (len(local_refs), measL, unmeasL))
    k = collections.Counter(r[0].split('/')[1] for r in local_refs)
    f.write('  内訳: ' + ' '.join('%s=%d' % (a, b) for a, b in sorted(k.items())) + '\n')
    f.write('origin heads 母數=%d (測れた=%d 測れぬ=%d)\n' % (len(remote_heads), measR, unmeasR))
    f.write('★~/bin は repo の外ゆゑ ref 数は構造上 0。之は「器が無い」の意では無い。★\n')
print('手許 ref=%d(測れた %d) / origin heads=%d(測れた %d)' % (len(local_refs), measL, len(remote_heads), measR))

# ---- ㋐の表 ----
target = dict(disk)
for n, h in bunrui.items():
    if h == '甲' and n not in target:
        target[n] = ('?', n, None)
rows = []
for n in sorted(target):
    where, real, rel = target[n]
    d = 1 if os.path.exists(real) else 0
    if rel:
        o = subprocess.run(['git', 'ls-tree', '-r', '--name-only', MAIN_O, '--', rel], capture_output=True, text=True)
        l = subprocess.run(['git', 'ls-tree', '-r', '--name-only', MAIN_L, '--', rel], capture_output=True, text=True)
        om = 1 if o.stdout.strip() else 0
        lm = 1 if l.stdout.strip() else 0
        rl = sum(1 for v in cacheL.values() if v and rel in v)
        rr = sum(1 for v in cacheR.values() if v and rel in v)
    else:
        om = lm = rl = rr = 0
    he = hiroi.get(n, (0, 0))
    rows.append((n, where, str(d), str(om), str(lm), str(rl), str(rr), str(he[0]), str(he[1])))
with open(os.path.join(OUT, '40_arika.tsv'), 'w', encoding='utf-8') as f:
    f.write('ki_mei\tokiba\t(1)disk\t(2)origin_main\t(3)local_main\t(4)temoto_ref(90中)\t(4)origin_heads(240中)\t(B)eda_suu(46中)\t(B)nobe\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
print('㋐の表 行=%d' % len(rows))
