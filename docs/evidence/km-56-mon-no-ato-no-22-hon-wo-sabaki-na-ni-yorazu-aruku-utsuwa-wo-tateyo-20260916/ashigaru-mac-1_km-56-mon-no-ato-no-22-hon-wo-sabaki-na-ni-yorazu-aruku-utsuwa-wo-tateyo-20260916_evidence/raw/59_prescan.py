# -*- coding: utf-8 -*-
"""前置器 59(第55弾・第54弾を写した・byte 同一でない = 此の一行のみ・臺帳より先・門より先・員外 ㊂)。50 と同じ selection() で載る筈の證 + 紙を取り、
⑴ 己の byte 述語(條② 末尾空白 / 條③ CR / 條④ 0byte・末尾≠LF・LF LF)を python で当て ⑵ 門を -- で一走(入口側・讀むのみ)。
鳴れば己の産物を直して(臺帳の前ゆゑ直してよい・旧出目は .first)再走。rc = 1 if 鳴 else 0。"""
import os, sys, subprocess, hashlib, importlib.util, re, time
B = sys.argv[1]; E = B + '_evidence/raw'; GATE = 'scripts/checks/karo_mac_dasumae_gate.sh'; PAPER = B + '.md'
sys.path.insert(0, E); import kaki as K
spec = importlib.util.spec_from_file_location('b50', E + '/50_build_manifest.py'); b50 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b50)
keep, ex_nl, ex_post, nonreg, ex_first, ex_self, ex_part, ex_copy = b50.selection(B + '_evidence')
files = [p for p in (PAPER,) if os.path.isfile(p)] + keep
out = [f'# 前置器 59 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 渡した {len(files)}(紙 {len(files)-len(keep)} + 證 {len(keep)})/ 員外 ㊀{len(ex_nl)} ㊂{len(ex_post)} ㊃{len(nonreg)} ㊄{len(ex_first)} ㊅{len(ex_self)} ㊆{len(ex_part)} ㊇{len(ex_copy)}']
ring = []
for p in files:
    b = open(p, 'rb').read(); r = []
    if len(b) == 0: r.append('條④空')
    else:
        if not b.endswith(b'\n'): r.append('條④無')
        elif b.endswith(b'\n\n'): r.append('條④複')
    n2 = len(re.findall(rb'[ \t]+\r?\n', b)) + (1 if re.search(rb'[ \t]+\Z', b) else 0)
    if n2: r.append(f'條②({n2}行)')
    if b'\r' in b: r.append('條③')
    if r: ring.append((p, r))
out.append(f'## ⑴ 己の byte 述語: 鳴つた file {len(ring)} / 母數 {len(files)}')
for p, r in ring: out.append(f'  ★{r} {os.path.relpath(p, B + "_evidence")}')
p = subprocess.run(['bash', GATE, '--'] + files, capture_output=True)
K.kaku(E + '/59_gate_pre.err', p.stderr.decode('utf-8', 'replace')); K.kaku(E + '/59_gate_pre.out', p.stdout.decode('utf-8', 'replace')); K.kaku(E + '/59_gate_pre.rc', str(p.returncode))
se = p.stderr.decode('utf-8', 'replace'); st = [l for l in se.split('\n') if l.startswith('★') and not l.startswith('★出す前')]
tot = re.search(r'byte和 (\d+)', se)
out.append(f'## ⑵ 門 -- 一走(入口側): rc {p.returncode} / 札 {len(st)} / byte和 {tot.group(1) if tot else "−"} / stderr sha16 {hashlib.sha256(p.stderr).hexdigest()[:16]}')
for l in st: out.append('  ' + l.replace(B + '_evidence/', ''))
rc = 1 if (ring or p.returncode != 0) else 0
out.append(f'# 前置器 59 計: 己の述語 鳴 {len(ring)} / 門 rc {p.returncode} → {"★鳴つた ―― 己の産物を直して再走せよ(臺帳の前)★" if rc else "清い ―― 臺帳を組んでよい"}')
K.kaku(E + '/59_prescan.out', '\n'.join(out)); K.kaku(E + '/59_prescan.rc', str(rc)); print('\n'.join(out)); sys.exit(rc)
