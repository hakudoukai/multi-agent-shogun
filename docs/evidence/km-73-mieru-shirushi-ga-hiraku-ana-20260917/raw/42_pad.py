# -*- coding: utf-8 -*-
"""㋓ 桁揃へ 42 ―― 短い値(1\\n2 → 乙 札に ␊ 一つ)の札を printf '%-Ns|'(bash 組込・/usr/bin/printf)・awk printf %-Ns・column 風の桁で揃へ、
C と UTF-8 で「詰め物の後の | の位置(byte と 字)」が ␊ の分だけずれるかを、対照(1x2・同じ字数で ASCII)と並べて刷る。"""
import os, sys, time, subprocess
D = sys.argv[1]; E = D + '/raw'; sys.path.insert(0, E); import kaki as K, dai73 as T
loc = subprocess.run(['locale', '-a'], capture_output=True, text=True).stdout.split(); U8 = next((l for l in ('en_US.UTF-8', 'ja_JP.UTF-8') if l in loc), 'C')
p = T.dai_path(E + '/dai', 'watcher', '乙'); rows = []
def fuda(v): return T.hashi(p, v)[2].rstrip(b'\n').split(b'\xe3\x80\x8c', 1)[1].split(b'\xe3\x80\x8d', 1)[0]  # 「…」の中だけ
for nm, v in (('乙 1\\n2 → 1␊2', '1\n2'), ('対照 1x2(ASCII 同字数)', '1x2'), ('乙 三印 1\\n\\r\\t2', '1\n\r\t2'), ('対照 1xyz2', '1xyz2')):
    f = fuda(v)
    for lc in ('C', U8):
        env = {'LC_ALL': lc}; fs = f.decode('utf-8')
        for on, argv, inp in (('bash printf %-12s|', ['/bin/bash', '-c', 'printf "%-12s|" "$1"', '_', fs], None), ('/usr/bin/printf %-12s|', ['/usr/bin/printf', '%-12s|', fs], None), ('awk printf %-12s|', ['awk', '{printf "%-12s|", $0}'], f), ('wc -m', ['wc', '-m'], f), ('bash ${#v}', ['/bin/bash', '-c', 'printf "%s" "${#1}"', '_', fs], None)):
            r = subprocess.run(argv, input=inp, capture_output=True, env=env); o = r.stdout
            bar = o.find(b'|'); rows.append((nm, lc, on, T.esc(f), len(f), len(fs), T.esc(o).strip(), len(o), bar if bar >= 0 else '-', (len(o[:bar].decode('utf-8', 'replace')) if bar >= 0 else '-')))
K.kaku_tsv(E + '/42_pad.tsv', rows, ['値', 'locale', '器', '札の値(esc)', '値 bytes', '値 字', '出目(esc)', '出目 bytes', '| の byte 位置', '| の字位置'])
out = [f'# 42 桁揃へ / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / UTF-8 locale = {U8}']
for lc in ('C', U8):
    for on in ('bash printf %-12s|', '/usr/bin/printf %-12s|', 'awk printf %-12s|'):
        a = next(r for r in rows if r[0].startswith('乙 1') and r[1] == lc and r[2] == on); b = next(r for r in rows if r[0].startswith('対照 1x2') and r[1] == lc and r[2] == on)
        out.append(f'{lc} {on}: 乙「{a[3]}」| の字位置 {a[9]}(byte {a[8]}) ⇔ 対照「{b[3]}」| の字位置 {b[9]}(byte {b[8]}) → {"★揃はぬ(差 %s 字)★" % (a[9]-b[9]) if isinstance(a[9], int) and isinstance(b[9], int) and a[9] != b[9] else "揃ふ"}')
K.kaku(E + '/42_pad.txt', '\n'.join(out)); print('\n'.join(out))
