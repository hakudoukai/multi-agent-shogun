# -*- coding: utf-8 -*-
"""㋑ 乙が封ぜぬ物を数へる 20 ―― 名指しの十形(+封じた三形を陽性対照に)を四器×(現行/乙)で走らせ、四つの讀手で行を数へる。
加へて watcher 一本で ★Cc 全 65 字 + Zl/Zp★ を乙に通し、讀手毎に「二行に割る物」を数へる。NUL は env に載らぬ(execve)故 別に測る。"""
import os, sys, subprocess, time, unicodedata
D = sys.argv[1]; E = D + '/raw'; sys.path.insert(0, E); import kaki as K, dai73 as T
NAMED = [('LF \\n', '\n'), ('CR \\r', '\r'), ('TAB \\t', '\t'), ('VT \\v', '\x0b'), ('FF \\f', '\x0c'), ('BS \\b', '\x08'), ('NUL', '\x00'), ('ESC', '\x1b'),
         ('U+2028 LS', '\u2028'), ('U+2029 PS', '\u2029'), ('U+0085 NEL', '\x85'), ('U+00A0 NBSP', '\xa0'), ('U+3000 全角空白', '\u3000')]
rows = []; hdr = ['生器', '案', '形', '値(esc)', 'LF', 'py.splitlines', 'wc-l', 'awk-NR', 'OUT', 'UTF-8', 'rc', '札(esc・120字迄)']
def run(key, an, nm, ch):
    p = T.dai_path(E + '/dai', key, an); v = '1' + ch + T.FAKE
    try: rc, so, se = T.hashi(p, v)
    except ValueError as x: return (dict(T.TGT)[key], an, nm, T.esc(v), '-', '-', '-', '-', '-', '-', f'env に載らぬ: {x}', '-')
    y = T.yomite(se); return (dict(T.TGT)[key], an, nm, T.esc(v), y['LF'], y['py.splitlines'], y['wc-l'], y['awk-NR'], T.out_of(so), T.u8(se), rc, T.esc(se)[:120])
for key, rel in T.TGT:
    for an in ('現行', '乙'):
        for nm, ch in NAMED: rows.append(run(key, an, nm, ch))
        rc, so, se = T.hashi(T.dai_path(E + '/dai', key, an), '777'); y = T.yomite(se)
        rows.append((rel, an, '陰性 777', '777', y['LF'], y['py.splitlines'], y['wc-l'], y['awk-NR'], T.out_of(so), T.u8(se), rc, T.esc(se)[:120]))
K.kaku_tsv(E + '/20_seigyo.tsv', rows, hdr)
# 全 Cc + Zl + Zp を watcher 乙 で(NUL 除く)
p = T.dai_path(E + '/dai', 'watcher', '乙'); allrows = []; split_by = {k: [] for k in ('LF', 'py.splitlines', 'wc-l', 'awk-NR')}
cc = [chr(c) for c in range(0x110000) if unicodedata.category(chr(c)) in ('Cc', 'Zl', 'Zp')]
for ch in cc:
    if ch == '\x00': allrows.append(('U+0000', 'Cc', '-', '-', '-', '-', 'env に載らぬ(execve は NUL 終端)')); continue
    rc, so, se = T.hashi(p, '1' + ch + T.FAKE); y = T.yomite(se)
    for k in split_by:
        if y[k] >= 2: split_by[k].append('U+%04X' % ord(ch))
    allrows.append(('U+%04X' % ord(ch), unicodedata.category(ch), y['LF'], y['py.splitlines'], y['wc-l'], y['awk-NR'], T.u8(se)))
K.kaku_tsv(E + '/20_zenbu.tsv', allrows, ['字', '種', 'LF', 'py.splitlines', 'wc-l', 'awk-NR', 'UTF-8'])
# NUL ―― bash が $( ) で落とすか
r = subprocess.run(['/bin/bash', '-c', 'v=$(printf "1\\000x"); printf "%s" "$v" | xxd -p; printf "%s" "${#v}"'], capture_output=True, text=True)
# 陽性対照: 現行 + LF で四讀手が悉く >=2 か
p0 = T.dai_path(E + '/dai', 'watcher', '現行'); y0 = T.yomite(T.hashi(p0, '1\n' + T.FAKE)[2]); yneg = T.yomite(T.hashi(p0, '777')[2])
n_cc = sum(1 for ch in cc if unicodedata.category(ch) == 'Cc'); n_z = len(cc) - n_cc
hd = [f'# 20 乙が封ぜぬ物 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 名指し {len(NAMED)} 形 × 四器 × (現行/乙) + 陰性 = {len(rows)} 走 / 全 Cc {n_cc} + Zl/Zp {n_z} = {len(cc)} 字を watcher 乙 で {len(cc) - 1} 走(NUL 除く)',
      f'★陽性対照(現行 + \\n)★ 四讀手 = {y0} ―― 悉く ≥2 で讀手は生きて居る / 陰性対照(777)= {yneg}',
      f'★乙が置くのは 3 字(\\n \\r \\t)。Cc は {n_cc} 字 ∴ 残る Cc = {n_cc - 3} 字、Zl/Zp {n_z} 字も残る(計 {len(cc) - 3})★',
      '★其の内「札を二行に割る物」は讀手で違ふ★:'] + [f'  讀手 {k}: {len(v)} 字 {v}' for k, v in split_by.items()] + [
      f'NUL: bash の $( ) は NUL を落とす ―― v=$(printf "1\\000x") → hex {r.stdout.strip().split(chr(10))[0] if r.stdout else "-"} / 長さ {r.stdout.strip().split(chr(10))[-1] if r.stdout else "-"}(stderr: {r.stderr.strip()[:80] or "無"})/ env 経由は execve が拒む(20_seigyo.tsv の NUL 行)',
      '読み: LF/wc-l/awk-NR(byte の \\n だけを行の切れ目と見る讀手)には、乙の後 二行に割る字は ★0★。py.splitlines(Python の行の定義)には VT/FF/FS/GS/RS/NEL/LS/PS が残る ―― ★「封ぜぬ物の本数」は讀手を名指さねば一つの數に成らぬ★']
K.kaku(E + '/20_seigyo.txt', '\n'.join(hd)); print('\n'.join(hd))
