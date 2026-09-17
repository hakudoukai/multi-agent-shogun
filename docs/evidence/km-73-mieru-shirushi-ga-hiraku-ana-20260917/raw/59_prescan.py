# -*- coding: utf-8 -*-
"""門の前の検め 59(第73弾・km-72 の写し)―― 紙と raw/ 配下の通常 file に 條②(行末空白)③(CR)④(EOF 改行 丁度 1)を己で当て、鳴つた物を名指す(門を先に読み、門の前に直す為)。0byte も名指す(空は「空である旨の一行」の條)。"""
import os, sys, stat, time
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; sys.path.insert(0, E); import kaki as K
files = [B + '.md'] + sorted(os.path.join(d, f) for d, ds, fs in os.walk(E) for f in fs if '__pycache__' not in d)
bad = []; n = 0; hi = 0
for q in files:
    if not stat.S_ISREG(os.lstat(q).st_mode): hi += 1; continue
    n += 1; b = open(q, 'rb').read(); r = os.path.relpath(q, D)
    if len(b) == 0: bad.append(f'{r}: 0byte'); continue
    if b'\r' in b: bad.append(f'{r}: CR {b.count(b"\r")}')
    if any(l.endswith((b' ', b'\t')) for l in b.split(b'\n')): bad.append(f'{r}: 行末空白')
    if not b.endswith(b'\n') or b.endswith(b'\n\n'): bad.append(f'{r}: EOF 改行が丁度 1 でない')
# ★第72弾: 行末空白を持つ fixture(專任3 の diff 7 本の写し raw/ki/an/*.diff・patch の .rej・汚れ fixture raw/fx/kegare.txt)は 條② で鳴るのが正 ―― 宣して分け、宣に無い鳴りのみで止める★
# ★第73弾: 宣する fixture は無い(raw/ の出目は悉く esc で書き、台 raw/dai/*.sh は生器の切り身+置換行)―― 鳴れば宣に無い故 止まる。初走は此の註釈を行中に置き `; nondecl = …` を呑んで NameError(己の memory「行中の註釈 patch は行の残りを殺す」を又踏んだ)★
decl = []; nondecl = [b_ for b_ in bad if b_ not in decl]; nondecl = [b_ for b_ in bad if b_ not in decl]
K.kaku(E + '/59_prescan.txt', f'# 59 門の前の検め / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 歩いた {n} 本(非通常 {hi})/ 鳴 {len(bad)}(内 宣した fixture {len(decl)} / 宣に無い {len(nondecl)})\n' + '\n'.join(bad))
print(open(E + '/59_prescan.txt', encoding='utf-8').read()); sys.exit(1 if nondecl else 0)
