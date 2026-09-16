# -*- coding: utf-8 -*-
"""㋑ 第66弾の束へ捕へ器 40 を掛ける 45(第67弾)。歩哨が無い束ゆゑ 刻 = 門控 _gate.txt の mtime_ns を代用(門控は門の最後の産物 ∴ 門自身の産物は「前」に落ち、門控の後に書かれた物だけが「後」に出る ―― 歩哨より狭い集合になる事を紙に書く)。二走: 根 = km-66/raw と 根 = km-66 束全体(_after/ 込み)。出目は己の束 raw/45_*(己の門の前ゆゑ根の中でよい)。66 の raw/ には 0 byte。"""
import os, sys, subprocess, re, time
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
W = '/Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1'; B66 = W + '/docs/evidence/km-66-noranu-336-20260917'; P66 = B66 + '/ashigaru-mac-1_km-66-noranu-336-20260917'
GATE66 = P66 + '_gate.txt'; SEN66 = B66 + '/raw/50_sengen.txt'
g = open(GATE66, encoding='utf-8').read().split('\n'); koku = re.search(r'刻 (\S+)', g[1]).group(1)
res = []
for nm, root in (('45_km66_raw', B66 + '/raw'), ('45_km66_all', B66)):
    p = subprocess.run(['python3', '-B', E + '/40_mon_no_ato.py', root, GATE66, SEN66, E, nm], capture_output=True, text=True)
    txt = p.stdout; ato = [l for l in txt.split('\n') if l.startswith('  後')]
    hit = [l for l in ato if '60_gate_run.rc' in l]; mu = re.search(r'母數 通常 file (\d+)', txt); kz = re.search(r'後∧宣に無い\(疵\) (\d+) 本 (\d+) B', txt); at = re.search(r'## 後 (\d+) 本 (\d+) B', txt); hid = re.search(r'隠す物 (\d+) 本 (\d+) B', txt)
    res.append(f'## 走り {nm} / 根 {os.path.relpath(root, W)} / rc {p.returncode} / 母數 {mu.group(1) if mu else "?"} / 後 {at.group(1) if at else "?"} 本 {at.group(2) if at else "?"} B / ★疵(後∧宣に無い) {kz.group(1) if kz else "?"} 本 {kz.group(2) if kz else "?"} B★ / ns が捕へ 秒>秒 が隠す {hid.group(1) if hid else "?"} 本')
    res.append(f'   あの 1 本 2 B(60_gate_run.rc): {"★捕へた★ " + hit[0].strip() if hit else "★捕へられぬ★(後の列に無い)"}')
    for l in ato: res.append('  ' + l.strip())
    if p.stderr.strip(): res.append('   stderr: ' + p.stderr.strip()[:300])
out = [f'# 45 ㋑ 第66弾へ / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 刻の代用 = 門控 {os.path.basename(GATE66)} の mtime_ns {os.stat(GATE66).st_mtime_ns}(門控に書かれた刻 {koku} は秒止まり)/ 宣 = 66 raw/50_sengen.txt の ㊂ 行 / 66 が 99/96 で出した「秒>秒 1 本 2 B = 60_gate_run.rc」を ns で裁く'] + res
K.kaku(E + '/45_km66.txt', '\n'.join(out)); print('\n'.join(out))
