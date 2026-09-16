# -*- coding: utf-8 -*-
"""㊂ 鎖の一段 31(第56弾・30_kusari を写して ★mtime を日付込みの秒で比べる★・出力 dir を argv で取る)。argv = <名> <出力dir> <歩き根> <前段の出目 or -> <臺帳 or -> <門控 or ->。讀むのみ(己の .txt を <出力dir> に書く以外 0 byte)。
30 との差は三つ: ⑴ mtime を '%Y-%m-%dT%H:%M:%S' で持ち門控の刻と日付込みで比べる(30 は HH:MM:SS の文字列比較 ∴ 日付を跨ぐと偽の「後」が出る = 第55弾 97 の實測 32 本)⑵ 出力 dir を argv[2] で取る(歩き根の外へ置ける ∴ 門の後の歩きが根へ書かぬ)⑶ 前段の表の刻の欄も日付込み。
★己の出目(此の .txt と、駆動器 10_run が己の終了後に書く .stdout/.err/.rc)は此の表に無い ―― 出力 dir が歩き根の外なら根にも無い。★"""
import os, sys, re, time, hashlib, subprocess
name, outd, root, prev, man, gate = sys.argv[1:7]; E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
now = time.strftime('%Y-%m-%dT%H:%M:%S%z'); sh = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
reg = {}
for d, ds, fs in os.walk(root):
    for f in fs:
        p = os.path.join(d, f)
        if os.path.islink(p) or not os.path.isfile(p): continue
        st = os.stat(p); reg[os.path.relpath(p, root)] = (sh(p), st.st_size, time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(st.st_mtime)))
out = [f'# {name} 鎖の一段(日付込み・31)/ 刻 {now} / 歩き根 {root} / 出力 dir {outd} / lstat 通常 file {len(reg)} / byte 和 {sum(v[1] for v in reg.values())} / ★此の器の己の出目 4 本({name}.txt・{name}.stdout/.err/.rc)は此の表に無い(出力 dir が根の外なら根にも無い)★']
if prev != '-' and os.path.isfile(prev):
    pv = {}
    for l in open(prev, encoding='utf-8'):
        m = re.match(r'  ([0-9a-f]{16})\t(\d+)\t(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\t(.+)$', l.rstrip('\n'))
        if m: pv[m.group(4)] = (m.group(1), int(m.group(2)), m.group(3))
    new = sorted(set(reg) - set(pv)); gone = sorted(set(pv) - set(reg)); chg = sorted(k for k in set(reg) & set(pv) if reg[k][0] != pv[k][0])
    out.append(f'## 前段 {os.path.basename(prev)}(見えた {len(pv)})との差: 新 {len(new)} / 変 {len(chg)} / 消 {len(gone)} → 此の段が見えた {len(reg)} = 前段 {len(pv)} + 新 {len(new)} − 消 {len(gone)} → {"閉ぢる" if len(reg) == len(pv) + len(new) - len(gone) else "★閉ぢぬ★"}')
    for k in new: out.append(f'  新 {k} {reg[k][1]}B {reg[k][2]}')
    for k in chg: out.append(f'  変 {k} {pv[k][0]}→{reg[k][0]} {pv[k][1]}→{reg[k][1]}B')
    for k in gone: out.append(f'  消 {k}')
else: out.append('## 前段 無(鎖の一段目)')
if man != '-' and os.path.isfile(man):
    p = subprocess.run(['python3', '-B', 'scripts/checks/karo_mac_manifest_verify.py', man], capture_output=True, text=True)
    out.append(f'## 臺帳 {os.path.basename(man)} を照合器で: rc {p.returncode} / ' + next((l.strip() for l in p.stdout.split('\n') if '一致' in l), '−') + ((' / ' + ' ; '.join(l.strip() for l in p.stdout.split('\n') if l.strip().startswith('★'))) if p.returncode else ''))
else: out.append('## 臺帳 無(未だ建てて居らぬ・或は渡さず)')
if gate != '-' and os.path.isfile(gate):
    gl = open(gate, encoding='utf-8').read().split('\n'); gt = re.search(r'刻 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', gl[1]).group(1)
    after = sorted(k for k, v in reg.items() if v[2] > gt)
    out.append(f'## 門控 {os.path.basename(gate)} の刻 {gt} より後の mtime(★日付込み★): {len(after)} 本 / byte 和 {sum(reg[k][1] for k in after)} ―― ★門の後に此の根へ書いた byte(此の段が見えた分・己の 4 本は外)★')
    for k in after: out.append(f'  後 {k} {reg[k][1]}B {reg[k][2]}')
    if not after: out.append('  (空 ―― 門の後に此の根へ書いた物は一本も無い・裁 310228⑶ の一行)')
else: out.append('## 門控 無(門の前・或は渡さず)')
out.append(f'## 表(sha16\\tbytes\\tmtime 日付込み\\t名) {len(reg)} 本')
for k in sorted(reg): out.append(f'  {reg[k][0]}\t{reg[k][1]}\t{reg[k][2]}\t{k}')
os.makedirs(outd, exist_ok=True); K.kaku(f'{outd}/{name}.txt', '\n'.join(out)); print('\n'.join(out[:len(out) - len(reg) - 1]))
