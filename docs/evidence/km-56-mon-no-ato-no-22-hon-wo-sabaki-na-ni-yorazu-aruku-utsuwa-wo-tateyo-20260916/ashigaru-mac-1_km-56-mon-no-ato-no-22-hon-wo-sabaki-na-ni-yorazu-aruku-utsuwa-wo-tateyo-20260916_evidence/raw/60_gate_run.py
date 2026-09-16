# -*- coding: utf-8 -*-
"""門を最後に走らせる器(第55弾・第54弾 raw/60 を写した ―― ★弾番と門控の名を束の名から導く(第54弾は「第53弾 門控」と手で打つた弾番が外れた = 疵 八十二 の席の同形)★ ―― 五形(A/B/D/E/C)の判別と空白のみの行の別数へを持つ)。★合致した形の種数★を印字する。
臺帳自身の末尾・不可視文字を別器で検める(門は argv[1] を條②③④⑤に掛けぬ故・gate.sh:97)。三走: selftest / main = 紙 1 + 臺帳(臺帳付)/ all = 臺帳の項 悉く(臺帳付)。
rc = subprocess.returncode 直採。argv の列は 61_ に残す。出目は kaki の作法(空は一行)。門・照合器は讀むのみ。"""
import os, sys, subprocess, hashlib, re, time
B = sys.argv[1]; RN = re.search(r'_km-(\d+)-', B).group(1); E = B + '_evidence/raw'; MAN = B + '_manifest.txt'; PAPER = B + '.md'; GATE = 'scripts/checks/karo_mac_dasumae_gate.sh'
sys.path.insert(0, E); import kaki as K
sys.path.insert(0, 'scripts/checks'); import karo_mac_manifest_verify as V
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]
GSHA = sha16(open(GATE, 'rb').read())
items = []
for raw in open(MAN, encoding='utf-8'):
    s = raw.strip()
    if not s or s.startswith('#') or not V.SHA.search(s): continue
    items.append(V.paths_of(s)[0])
out = [f'刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {GSHA} / 照合器 sha16 {sha16(open("scripts/checks/karo_mac_manifest_verify.py","rb").read())} / 臺帳の項 {len(items)} / 臺帳 sha16 {sha16(open(MAN,"rb").read())} / 紙 sha16 {sha16(open(PAPER,"rb").read())} / 渡した = argv[1](臺帳)を除く本数']
p = subprocess.run(['bash', GATE, '--selftest'], capture_output=True)
K.kaku(E + '/60_gate_selftest.err', p.stderr.decode('utf-8', 'replace')); K.kaku(E + '/60_gate_selftest.out', p.stdout.decode('utf-8', 'replace')); K.kaku(E + '/60_gate_selftest.rc', str(p.returncode))
out.append(f"selftest | 渡した 0 | rc {p.returncode} | 結語 {[x for x in p.stderr.decode('utf-8','replace').split(chr(10)) if x.startswith('★自己検め')]}")
def run(key, argv):
    K.kaku(f'{E}/61_gate_argv_{key}.txt', '\n'.join(argv[1:]))
    p = subprocess.run(['bash', GATE] + argv, capture_output=True); files = argv[1:]
    K.kaku(f'{E}/60_gate_{key}.err', p.stderr.decode('utf-8', 'replace')); K.kaku(f'{E}/60_gate_{key}.out', p.stdout.decode('utf-8', 'replace')); K.kaku(f'{E}/60_gate_{key}.rc', str(p.returncode))
    so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace')
    fuda = [l for l in se.split('\n') if l.startswith('★') and not l.startswith('★出す前')]
    j1 = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', so); tot = re.search(r'byte和 (\d+)', se)
    line = f"{key} | 渡した {len(files)} | rc {p.returncode} | 札 {len(fuda)} | 條① {j1.groups() if j1 else '−'} | 條⑤ byte和 {tot.group(1) if tot else '−'} | 結語 {[l for l in se.split(chr(10)) if l.startswith('★出す前')]} | stderr sha16 {sha16(p.stderr)}"
    out.append(line)
    for l in fuda: out.append('    ' + l.replace(B + '_evidence/', ''))
run('main', [MAN, PAPER, MAN]); run('all', [MAN] + items)
FORMS = [("A 引用符付 ^path=\"…\"", re.compile(r'^path="([^"]+)" sha256=([0-9a-f]{64}) bytes=(\d+) lines=(\d+)\s*$')), ("B 素形 ^path=<裸>", re.compile(r'^path=(?!")([^\s"]\S*) sha256=([0-9a-f]{64}) bytes=(\d+) lines=(\d+)\s*$')), ("D 三欄 引用符付", re.compile(r'^path="([^"]+)" sha256=([0-9a-f]{64}) bytes=(\d+)\s*$')), ("E 三欄 素形", re.compile(r'^path=(?!")([^\s"]\S*) sha256=([0-9a-f]{64}) bytes=(\d+)\s*$')), ("C 鍵無し ^<path> …", re.compile(r'^(?!path=)(\S+) sha256=([0-9a-f]{64}) bytes=(\d+) lines=(\d+)\s*$'))]
body = [l for l in open(MAN, encoding='utf-8').read().split('\n') if l.strip() and not l.startswith('#')]
ws_only = sum(1 for l in open(MAN, encoding='utf-8').read().split('\n') if l and not l.strip())
cnt = {nm: sum(1 for l in body if rx.match(l)) for nm, rx in FORMS}; nz = [nm for nm, c in cnt.items() if c]
out.append(f"臺帳の方言(五形) | 実体行 {len(body)} | 空白のみの行(第39弾 §3⑵ の境・本弾 ㊂ で己の器 32 も同じ数を印字する) {ws_only} | " + ' / '.join(f'{nm} 合致 {c}' for nm, c in cnt.items()) + f" | ★排他性: 合致した形の種数 = {len(nz)} {nz}★ | 五形の外の実体行 {sum(1 for l in body if not any(rx.match(l) for _, rx in FORMS))} | 緩い錨 'path=' の語 = {sum(1 for l in open(MAN, encoding='utf-8') if 'path=' in l)}(註を含む・語で数へた數)⇔ 行頭錨 {cnt['B 素形 ^path=<裸>']}")
mb = open(MAN, 'rb').read(); tail = mb[-2:]; inv = sorted(set(hex(b) for b in mb if b < 0x20 and b not in (0x0a,)) | set(c for c in ('　', ' ', '​', ' ', '﻿') if c in mb.decode('utf-8', 'replace')))
ws = sum(1 for l in mb.split(b'\n') if l.rstrip(b'\n').endswith((b' ', b'\t')))
out.append(f"臺帳自身(別器・門は argv[1] を條②③④⑤に掛けぬ) | bytes {len(mb)} | 末尾 2 byte {tail.hex()}(0a 一つ = {tail[-1:] == b'\n' and tail != b'\n\n'}) | CR {mb.count(b'\r')} | 行末空白 {ws} 行 | 制御・不可視 {inv or '無'} | sha16 {sha16(mb)}")
FORBID = ['scripts/checks/karo_mac_dasumae_gate.sh', 'scripts/checks/karo_mac_manifest_verify.py', '.gitignore', '.claude/settings.json']
st = subprocess.run(['git', 'status', '--porcelain', '--', 'scripts/', '.gitignore', 'instructions/', '.claude/settings.json'], capture_output=True, text=True).stdout.split('\n')
out.append('禁域(門 scripts/checks/ を含む)へ 0 byte | 前(00_start)と今の sha16: ' + ' / '.join(f'{p} {sha16(open(p, "rb").read())}' for p in FORBID) + f" | git status(scripts/ .gitignore instructions/ .claude/settings.json)の行 {len([l for l in st if l])}(本弾の前から在る worktree 差・本弾は触れて居らぬ: 00_start の sha16 と一致で示す) | .git/index mtime {time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(os.stat('.git/index').st_mtime))}")
K.kaku(f'{E}/60_gate_rcs.txt', '\n'.join(out)); print('\n'.join(out))

# ★上端の門控(<束>_gate.txt)を組む ―― 第45弾 ㊄ の形(案を己の産物で試す・器へは据ゑぬ): 一行目に「何れの走りを写したか」を宣し、広い走り(all = 臺帳の項 悉く)を先に、狭い走り(main = 紙 + 臺帳)を後に、逐語で写す。
def _n(key):
    se = open(f'{E}/60_gate_{key}.err', encoding='utf-8').read(); import re as _r
    a = _r.search(r'全file\((\d+)本\)', se); b = _r.search(r'byte和 (\d+)', se); rc = open(f'{E}/60_gate_{key}.rc', encoding='utf-8').read().strip()
    return (a.group(1) if a else '−'), (b.group(1) if b else '−'), rc
na, ba, ra = _n('all'); nm, bm, rm = _n('main')
top = [f'# 門控の写し = 走り「all」(渡した {na} 本 = 臺帳の項 悉く / byte和 {ba} / rc {ra})を上に・走り「main」(渡した {nm} 本 = 紙 + 臺帳 / byte和 {bm} / rc {rm})を下に ―― ★上端に置いたのは広い方である★(argv の列 raw/61_gate_argv_all.txt / raw/61_gate_argv_main.txt・stderr の写し raw/60_gate_all.err / raw/60_gate_main.err)',
       f'# 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {GSHA} / 臺帳 sha16 {sha16(open(MAN, "rb").read())} / 紙 sha16 {sha16(open(PAPER, "rb").read())}',
       '## 走り all(stderr 逐語)'] + open(f'{E}/60_gate_all.err', encoding='utf-8').read().rstrip('\n').split('\n') + ['## 走り main(stderr 逐語)'] + open(f'{E}/60_gate_main.err', encoding='utf-8').read().rstrip('\n').split('\n')
top[0] = f'# 第{RN}弾 門控(名 = 60_gate_top.r{RN}・毎回別) ' + top[0]
K.kaku(B + '_gate.txt', '\n'.join(top)); K.kaku(E + f'/60_gate_top.r{RN}.txt', '\n'.join(top)); print('上端の門控を組んだ:', B + '_gate.txt', f'+ raw/60_gate_top.r{RN}.txt')
