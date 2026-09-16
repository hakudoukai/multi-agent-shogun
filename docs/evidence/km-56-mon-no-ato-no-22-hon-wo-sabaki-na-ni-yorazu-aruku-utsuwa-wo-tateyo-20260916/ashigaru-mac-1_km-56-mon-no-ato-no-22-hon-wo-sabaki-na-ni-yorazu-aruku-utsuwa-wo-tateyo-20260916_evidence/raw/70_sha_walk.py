# -*- coding: utf-8 -*-
"""問二の器 70(第56弾・★名に依らぬ★・据ゑず・束の中)。sha で歩く: 根の下の lstat 通常 file 悉くを讀み sha256 を採り、問はれた sha(16 桁の前置でも 64 桁でも)が ★何処に何本在るか★ を刷る。名は結果の欄であつて、探す鍵ではない。
argv: --root <dir|file> ... [--prefix <束の前置>] ... --sha <hex> ... [--max-bytes N(既定 67108864)]
  --prefix p = dirname(p) の中で basename(p) で始まる entry 悉く(file は讀む・dir は歩く)―― 束の名の前置のみに依り、_manifest/_daichou/_gate 等の後置には依らぬ。
出目: 母數(讀んだ通常 file の本数・byte 和)/ 根ごとの母數 / 跳んだ物(symlink・通常 file でない・讀めぬ・大きすぎ)/ 問はれた sha ごとの当たり(本数と名)/ ★同 sha 複数本★の数(此の器が「一本」と言へぬ場合)/ 歩き中に変つた物(歩き始めより後の mtime)。
偽になる場合(㋕)は末尾に数で刷る。讀むのみ・己の出目は 10_run が書く。"""
import os, sys, hashlib, time
args = sys.argv[1:]; roots = []; shas = []; maxb = 67108864; i = 0
while i < len(args):
    a = args[i]
    if a == '--root': roots.append(args[i + 1]); i += 2
    elif a == '--prefix':
        p = args[i + 1]; d = os.path.dirname(p) or '.'; bn = os.path.basename(p)
        roots += sorted(os.path.join(d, e) for e in os.listdir(d) if e.startswith(bn)); i += 2
    elif a == '--sha': shas.append(args[i + 1].lower()); i += 2
    elif a == '--max-bytes': maxb = int(args[i + 1]); i += 2
    else: print('★引数が解せぬ:', a); sys.exit(2)
t0 = time.time(); idx = {}; per = []; n_link = n_nonreg = n_unread = n_big = n_moved = 0; N = 0; BYTES = 0
def take(p, root):
    global N, BYTES, n_link, n_nonreg, n_unread, n_big, n_moved
    if os.path.islink(p): n_link += 1; return
    if not os.path.isfile(p): n_nonreg += 1; return
    st = os.stat(p)
    if st.st_size > maxb: n_big += 1; return
    try: b = open(p, 'rb').read()
    except OSError: n_unread += 1; return
    if os.stat(p).st_mtime > t0: n_moved += 1
    h = hashlib.sha256(b).hexdigest(); N += 1; BYTES += len(b); idx.setdefault(h, []).append(p)
for r in roots:
    n0 = N
    if os.path.isdir(r):
        for d, ds, fs in os.walk(r):
            for f in fs: take(os.path.join(d, f), r)
    else: take(r, os.path.dirname(r))
    per.append((r, N - n0))
out = [f'# 70 sha で歩く / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 根 {len(roots)} 本 / ★母數 = 讀んだ通常 file {N} 本 / byte 和 {BYTES}★ / 跳んだ: symlink {n_link} / 通常 file でない {n_nonreg} / 讀めぬ {n_unread} / 大きすぎ(>{maxb}) {n_big} / 歩き中に変つた {n_moved} / 所要 {time.time() - t0:.2f} 秒']
for r, k in per: out.append(f'  根 {r} → {k} 本')
out.append(f'## 問はれた sha {len(shas)} 本:')
hit_total = 0
for s in shas:
    hits = [(h, ps) for h, ps in idx.items() if h.startswith(s)]
    n = sum(len(ps) for _, ps in hits); hit_total += 1 if n else 0
    out.append(f'  {s} → {n} 本' + (' ★複数本★' if n > 1 else '') + (' (無し)' if n == 0 else '') + ''.join(f'\n      {p} {os.path.getsize(p)}B' for _, ps in hits for p in ps) + (f'\n      ★{len(hits)} 個の別 sha256 が此の前置に当たる(前置の衝突)★' if len(hits) > 1 else ''))
out.append(f'## 当たり {hit_total}/{len(shas)}(問はれた sha の内 一本以上 在つた数)')
dup = sorted(((len(ps), h, ps) for h, ps in idx.items() if len(ps) > 1), reverse=True)
out.append(f'## ★同 sha 複数本★ = {len(dup)} 個の sha が {sum(k for k, _, _ in dup)} 本の file に跨る(此の器は「一本」と言へぬ)―― 上位 8:')
for k, h, ps in dup[:8]: out.append(f'  {k} 本 sha16 {h[:16]} {os.path.getsize(ps[0])}B 例 {ps[0]}' + (f' 他 {k-1} 本' if k > 1 else ''))
out.append(f'## 空 file(sha256 e3b0c442…)= {len(idx.get("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", []))} 本')
print('\n'.join(out))
