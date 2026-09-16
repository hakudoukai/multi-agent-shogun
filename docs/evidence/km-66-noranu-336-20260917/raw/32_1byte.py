# -*- coding: utf-8 -*-
"""相違 1 の器 32(第66弾・㋓)―― …soukantoku291437_1r_20260908.md: 臺帳 manifest_v2origin.txt の宣 sha 5229… bytes 22046 / 実 24e7… 22047。
①実の 22047 B から一 byte を抜いた 22047 通りの sha256 を悉く計り、宣 sha に当たる位置と其の byte(字か改行か空白か)を出す。②当たらねば「一 byte の挿入ではない」。③stat の mtime/ctime/birthtime を臺帳の mtime と並べる。④git(queue/reports は untracked)。読取のみ。"""
import os, sys, time, hashlib, subprocess, stat, re
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; D = M + '/queue/reports'
P = D + '/ashigaru-mac-2_soukantoku291437_1r_20260908.md'; MAN = D + '/ashigaru-mac-2_soukantoku291437_1_20260908_evidence/manifest_v2origin.txt'
t0 = time.strftime('%Y-%m-%dT%H:%M:%S%z'); b = open(P, 'rb').read(); real = hashlib.sha256(b).hexdigest()
ln = [l for l in open(MAN, encoding='utf-8', errors='replace').read().split('\n') if os.path.basename(P) in l]
m = re.search(r'sha256=([0-9a-f]{64})', ln[0]) if ln else None; want = m.group(1) if m else None; wb = re.search(r'bytes=(\d+)', ln[0]) if ln else None
out = [f'# 相違 1 の決着 32 / 刻 {t0} / 紙 {P} / 臺帳 {MAN}', f'臺帳の行(逐語): {ln[0] if ln else "★無し★"}', f'宣 sha256 {want} bytes {wb.group(1) if wb else "?"} / 実 sha256 {real} bytes {len(b)} / 差 {len(b) - int(wb.group(1)) if wb else "?"} B']
hits = []
if want and len(b) - int(wb.group(1)) == 1:
    for i in range(len(b)):
        if hashlib.sha256(b[:i] + b[i + 1:]).hexdigest() == want: hits.append(i)
    out.append(f'★① 一 byte を抜いて宣 sha に当たる位置 = {len(hits)} 箇所★(試した {len(b)} 通り)')
    for i in hits:
        c = b[i]; line_no = b[:i].count(b'\n') + 1; ls = b.rfind(b'\n', 0, i) + 1; le = b.find(b'\n', i); le = len(b) if le < 0 else le
        out.append(f'  位置 {i}(0 起点)/ byte 0x{c:02x} = {"改行 LF" if c == 0x0a else "復帰 CR" if c == 0x0d else "空白" if c == 0x20 else "tab" if c == 0x09 else repr(chr(c)) if c < 128 else "多 byte 字の一部"} / 行 {line_no}(その行の {i - ls} 字目・行長 {le - ls} B)/ 末尾からの距離 {len(b) - 1 - i} / 其の行(逐語・先頭 120B): {b[ls:le][:120]!r}')
    if hits and all(b[i] == b[hits[0]] for i in hits) and (max(hits) - min(hits) + 1 == len(hits)): out.append(f'  ★同じ byte の連(0x{b[hits[0]]:02x}×{len(hits)})の何れを抜いても同じ ―― 「連の何処か」までしか決まらぬが、byte の正体は決まる★')
    if not hits: out.append('★② 一 byte 挿入では宣 sha に届かぬ ―― 差は 1 byte の挿入ではない(置換+挿入 等)。決めるには宣 sha の中身(22046 B の原本)が要る★')
else: out.append('★差が 1 byte でない / 臺帳の行が無い ―― ① は走らせぬ★')
st = os.stat(P); sm = os.stat(MAN)
f = lambda t: time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t)) + f'.{int((t % 1) * 1e6):06d}'
out.append(f'③ 紙: birth {f(st.st_birthtime)} / mtime {f(st.st_mtime)} / ctime {f(st.st_ctime)} ; 臺帳: birth {f(sm.st_birthtime)} / mtime {f(sm.st_mtime)} / ctime {f(sm.st_ctime)}')
out.append(f'   紙 mtime < 臺帳 mtime = {st.st_mtime < sm.st_mtime} / ★紙 ctime > 臺帳 mtime = {st.st_ctime > sm.st_mtime}★(真なら紙は臺帳の後に inode が触られた ―― cp -p は mtime を保ち ctime は保たぬ)/ 紙 birth {"<" if st.st_birthtime < sm.st_mtime else ">"} 臺帳 mtime')
g = subprocess.run(['git', '-C', M, 'ls-files', '--error-unmatch', '--', os.path.relpath(P, M)], capture_output=True, text=True)
out.append(f'④ git ls-files rc={g.returncode}({"tracked" if g.returncode == 0 else "untracked ―― 履歴無し・原本は git に無い"})')
blob = hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest(); ce = subprocess.run(['git', '-C', M, 'cat-file', '-e', blob], capture_output=True, text=True)
out.append(f'   実の中身の blob sha1 {blob} → git cat-file -e rc={ce.returncode}({"在る" if ce.returncode == 0 else "無い"})')
# 同じ sha(宣)の写しが別の場所に在るか ―― 40 本の _evidence と docs/evidence を basename で当たり sha を比べる
same = []
for root in (D, M + '/docs/evidence'):
    for d, ds, fs in os.walk(root):
        for x in fs:
            if x == os.path.basename(P) and os.path.realpath(os.path.join(d, x)) != os.path.realpath(P):
                q = os.path.join(d, x); s_ = hashlib.sha256(open(q, 'rb').read()).hexdigest(); same.append(f'{os.path.relpath(q, M)} {os.path.getsize(q)}B sha {s_[:16]} {"★宣と同じ★" if s_ == want else "実と同じ" if s_ == real else "別物"}')
out.append(f'⑤ 同名の写し(queue/reports・docs/evidence を歩いた・己を除く)= {len(same)} 本' + (': ' + ' ; '.join(same) if same else ''))
K.kaku(E + '/32_1byte.txt', '\n'.join(out)); print('\n'.join(out))
