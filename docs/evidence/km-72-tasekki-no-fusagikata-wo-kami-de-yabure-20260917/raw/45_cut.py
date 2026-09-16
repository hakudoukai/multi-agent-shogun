# -*- coding: utf-8 -*-
"""45 cut の性質(第72弾)―― 丙 safe_show の `cut -c1-40` が、入力に改行が無い時に出目へ改行を足すか(長さ 3/40/41/60 byte)。同じ入力を tr だけに通した時と比べる。BSD cut(macOS)の實測。"""
import sys, subprocess, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
rows = []
for n in (3, 39, 40, 41, 60):
    s = b'x' * n
    c = subprocess.run(['cut', '-c1-40'], input=s, capture_output=True).stdout; t = subprocess.run(['bash', '-c', "LC_ALL=C tr -c '[:print:]' '?'"], input=s, capture_output=True).stdout
    rows.append([n, len(c), c.endswith(b'\n'), c.count(b'\n'), len(t), t.endswith(b'\n')])
ss = subprocess.run(['bash', '-c', 'safe_show(){ local s="${1:-}" n; n=$(printf "%s" "$s" | wc -c | tr -d " "); printf "%s" "$s" | LC_ALL=C tr -c "[:print:]" "?" | cut -c1-40; printf "(生 %s byte)" "$n"; }; x="$(safe_show "$1")"; printf "%s" "$x" | od -c | head -5; echo; printf "%s" "$x" | wc -l', '_', 'x' * 60], capture_output=True, text=True).stdout
out = [f'# 45 cut / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / cut = {subprocess.run(["which", "cut"], capture_output=True, text=True).stdout.strip()} / uname {subprocess.run(["uname", "-sr"], capture_output=True, text=True).stdout.strip()}', 'n_in\tcut_out_bytes\tcut_ends_LF\tcut_LF_count\ttr_out_bytes\ttr_ends_LF'] + ['\t'.join(map(str, r)) for r in rows] + ['## safe_show("x"×60) を $( ) で受けた物の od -c(先頭)と wc -l', ss.rstrip()]
K.kaku(D + '/raw/45_cut.txt', '\n'.join(out)); print('\n'.join(out))
