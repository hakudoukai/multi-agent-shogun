#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""72_wari.py -- ★門 條④ で鳴つた 0byte を 二つに割る器★(第47弾 ㋑)。

割り方(★此の器が採る條・讀手が己の目で判ぜられる様に逐語で刷る★):
  ⑴ ★器の産物★ = 束の器が ★書いた★ file(走らせた物の出目を捕へた物)。
      ―― 裁 seq310228⑶ が当たる。★空は 0byte でなく「空である旨の一行」★ を書くべきであつた。
  ⑵ ★故意の fixture★ = 門を試す為に ★態と 0byte にした入力★(器が ★讀む★ 側)。
  ⑶ ★辿れぬ★ = 束の器の中に ★書いた行が見当らぬ★ 物。★見立てで ⑴へ寄せぬ。★

辿り方(★名寄せでなく、器の中の dir 定数を解いて ★同じ dir★ に成るかで当てる★):
  ①各器の `NAME = os.path.join(...)` を解き、束の根からの ★実の dir★ を得る
    (B=束 / ROOT=repo 根 / 既に解けた NAME を base に取れる)
  ②`io.open(...,"w")` を含む ★文★(括弧が閉ぢるまで繋ぐ)を拾ひ、其の文が使ふ dir 定数と
    綴り(.err/.out/…)を取る
  ③path の ★親 dir が ①で解けた dir と一致し★、且つ ★綴りが合ふ★ 文だけを根拠とする
  ―― ★行で切れば折り返された write を取り零す★(實測: 初版は 62_seme.py:140-141 を
     44本悉く零し「辿れぬ44」と出した)。∴ 文で讀む。

使ひ方: 72_wari.py <門の log> <測る束の根> <辿る器の在處(ki/)> [<repo 根>]
"""
import io, os, re, sys, subprocess, tempfile

if len(sys.argv) < 4:
    sys.stderr.write(u'★測れぬ: <門の log> <束の根> <ki/> を argv で渡せ★\n'); sys.exit(2)
GATE, BUNDLE, KI = sys.argv[1], sys.argv[2], sys.argv[3]
ROOT = sys.argv[4] if len(sys.argv) > 4 else os.getcwd()
BREL = os.path.relpath(os.path.abspath(BUNDLE), os.path.abspath(ROOT))

RING = re.compile(u'★EOF改行 ―― (.+?) は空file\\(0byte\\)★')
JOIN = re.compile(u'^([A-Z][A-Z0-9_]*)\\s*=\\s*os\\.path\\.join\\(([^)]*)\\)')
SUFF = re.compile(u'\\.(err|out|txt|tsv|md)\\b')

if not os.path.isfile(GATE):
    sys.stderr.write(u'★測れぬ: 門の log が無い %s★\n' % GATE); sys.exit(2)
text = io.open(GATE, encoding='utf-8', errors='replace').read()
paths = sorted(set(RING.findall(text)))
print(u'= 門の log %s' % GATE)
print(u'= ★條④(0byte)で鳴つた★ %d 本' % len(paths))
print(u'= 束 %s (repo 根からの相對 %s)' % (BUNDLE, BREL))

kakigyou = []      # (器, 行番, 逐語, {解けた dir}, [綴り])
kaiketsu_log = []
if not os.path.isdir(KI):
    sys.stderr.write(u'★測れぬ: ki/ が無い %s★\n' % KI); sys.exit(2)

for na in sorted(os.listdir(KI)):
    if not na.endswith('.py'):
        continue
    src = io.open(os.path.join(KI, na), encoding='utf-8', errors='replace').read().split(u'\n')
    kai = {u'B': BREL, u'ROOT': u''}          # ★解けた dir 定数★
    for l in src:
        m = JOIN.match(l.strip())
        if not m:
            continue
        nm, arg = m.group(1), m.group(2)
        toks = [t.strip() for t in arg.split(',')]
        base = toks[0]
        if base not in kai:
            continue
        rest = []
        ok = True
        for t in toks[1:]:
            mm = re.match(u'^[ur]?["\'](.*)["\']$', t)
            if not mm:
                ok = False
                break
            rest.append(mm.group(1))
        if not ok:
            continue
        kai[nm] = os.path.normpath(os.path.join(kai[base], *rest)) if rest else kai[base]
    kaiketsu_log.append((na, dict(kai)))
    i = 0
    while i < len(src):
        l = src[i]
        if 'io.open(' in l:
            bun, j = l, i
            while (bun.count('(') > bun.count(')')) and j + 1 < len(src) and j - i < 6:
                j += 1
                bun = bun + u' ' + src[j].strip()
            if '"w"' in bun or "'w'" in bun:
                dirs = {}
                for nm, d in kai.items():
                    if re.search(u'\\b%s\\b' % nm, bun):
                        dirs[nm] = d
                sufs = sorted(set(SUFF.findall(bun)))
                kakigyou.append((na, i + 1, bun.strip(), dirs, sufs))
            i = j + 1
            continue
        i += 1

print(u'= 束の器の ★書く文★ %d 本' % len(kakigyou))
print()
print(u'-- ★解けた dir 定数★(器ごと) --')
for na, kai in kaiketsu_log:
    ds = u' '.join([u'%s=%s' % (k, v or u'(repo根)') for k, v in sorted(kai.items())])
    print(u'  %-18s %s' % (na, ds))


def ate(path):
    oya = os.path.dirname(path)
    m = SUFF.search(path)
    suf = m.group(1) if m else u''
    hit = []
    for (na, i, l, dirs, sufs) in kakigyou:
        if suf not in sufs:
            continue
        if not any(os.path.normpath(d) == os.path.normpath(oya) for d in dirs.values() if d):
            continue
        hit.append((na, i, l))
    return hit


kubun = {u'⑴器の産物': [], u'⑵故意の fixture': [], u'⑶辿れぬ': []}
gyou = []
for p in paths:
    ap = os.path.join(ROOT, p)
    by = os.path.getsize(ap) if os.path.isfile(ap) else -1
    if '/fixture/' in p:
        k, ev = u'⑵故意の fixture', u'fixture/ の下 ―― 器が ★讀む★ 側'
    else:
        h = ate(p)
        if h:
            k = u'⑴器の産物'
            ev = u' ／ '.join([u'%s:%d' % (x[0], x[1]) for x in h]) + u'  ' + h[0][2][:150]
        else:
            k, ev = u'⑶辿れぬ', u'★束の器の中に書いた文が見当らぬ★'
    kubun[k].append(p)
    gyou.append((k, p, by, ev))

print()
for k in [u'⑴器の産物', u'⑵故意の fixture', u'⑶辿れぬ']:
    print(u'★%s★ %d 本' % (k, len(kubun[k])))
print(u'★和★ %d (= 鳴つた %d)' % (sum(len(v) for v in kubun.values()), len(paths)))

print()
print(u'kubun\tbytes\tpath\t根拠(器:行 逐語)')
for k, p, by, ev in gyou:
    print(u'%s\t%d\t%s\t%s' % (k, by, p, ev))

print()
print(u'== ★機の陽性対照★ ―― 「生で書く」形が 0byte を産む事を、器自身に實演させる ==')
tmp = tempfile.mkdtemp(prefix='km47_wari_')
try:
    r = subprocess.run([sys.executable, '-B', '-c', 'import sys; sys.stdout.write("")'],
                       capture_output=True, text=True)
    nama = os.path.join(tmp, 'nama.err')
    io.open(nama, 'w', encoding='utf-8', newline='').write(r.stderr)
    print(u'  ★生書き★ bytes=%d ―― 62_seme.py:140 / 63_damatte.py:33 と同じ形'
          % os.path.getsize(nama))
    kaki = os.path.join(os.path.dirname(os.path.abspath(__file__)), '70_kaki.py')
    tou = os.path.join(tmp, 'tootta.err')
    subprocess.run([sys.executable, '-B', kaki, tou, '--nushi', '72_wari.py-taishou'],
                   input=r.stderr, capture_output=True, text=True)
    print(u'  ★70_kaki を通す★ bytes=%d ―― 裁 seq310228⑶ の「空である旨の一行」'
          % os.path.getsize(tou))
    print(u'  ∴ ★0byte は「空であつた」の証ではなく、★書き手が生で書いた事★ の証である。★')
finally:
    for f in os.listdir(tmp):
        os.unlink(os.path.join(tmp, f))
    os.rmdir(tmp)
