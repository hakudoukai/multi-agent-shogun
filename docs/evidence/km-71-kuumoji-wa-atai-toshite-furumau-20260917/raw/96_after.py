# -*- coding: utf-8 -*-
"""96 門の後(第71弾): shell 直取り三本(60_run.*)を kaki へ・臺帳に無い raw/ の通常 file を名指す(50 の自產物の筈)・staged を再取り。"""
import os, sys, time, subprocess, stat
B = sys.argv[1]; D = os.path.dirname(B); RAW = D + '/raw'; AFT = D + '/_after'; sys.path.insert(0, RAW); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
out = [f'# 96 門の後 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}']
for n in ('60_run.stdout', '60_run.err', '60_run.rc'):
    p = f'{AFT}/{n}'; b0 = os.path.getsize(p); K.kaku(p, open(p, encoding='utf-8').read()); out.append(f'kaki 通し {n}: {b0} → {os.path.getsize(p)} bytes' + (' (0byte → 空である旨の一行)' if b0 == 0 else ''))
man = [l.split(' sha256=')[0][5:] for l in open(B + '_manifest.txt', encoding='utf-8') if l.startswith('path=')]
disk = sorted(os.path.relpath(os.path.join(r, f), D) for r, ds, fs in os.walk(RAW) for f in fs if stat.S_ISREG(os.lstat(os.path.join(r, f)).st_mode))
ingai = [p for p in disk if p not in set(man)]; out.append(f'臺帳の項 {len(man)}(紙 1 + raw/ {len(man)-1}) / raw/ disk 通常 {len(disk)} / 員外 {len(ingai)} {ingai} ―― 50 の自產物(臺帳の後に書かれる)なら疵 0')
out.append('判: ' + ('★員外は悉く 50 の自產物 ―― 疵 0★' if ingai and all(p.startswith('raw/50_') for p in ingai) else ('員外 0(50 の自產物も無い ―― 測れて居るか疑へ)' if not ingai else '★50 以外の員外あり★')))
g = lambda *a: subprocess.run(['git'] + list(a), capture_output=True, text=True, cwd=M); rel = os.path.relpath(D, M)
p = g('add', '-f', '--', rel); st = [l for l in g('status', '--porcelain', '--', rel).stdout.split('\n') if l]
out.append(f'git add -f(96 の後・rc {p.returncode}) / porcelain A {sum(1 for l in st if l[:2]=="A ")} AM {sum(1 for l in st if l[:2]=="AM")} 他 {sum(1 for l in st if l[:2] not in ("A ","AM"))} / 本 96 の出目は此の後に書かれる故 未 staged に残る')
K.kaku(AFT + '/96_after.txt', '\n'.join(out)); print('\n'.join(out))
