# -*- coding: utf-8 -*-
"""門を最後に走らせる器 60(第68弾)―― ★順が本弾の的★: ① 錠(raw/ と配下を 0555/0444・門の前)→ ② 歩哨(_after/00_hosho.txt・ns の刻)→ ③ 門 三走(selftest / main = 紙+臺帳 / all = 臺帳の項 悉く・出目は悉く _after/)→ ④ 門控(<束>_gate.txt + _after/60_gate_top.r67.txt)→ ⑤ 禁域の前後 sha16。raw/ へは門の後 0 byte(書けもせぬ)。cwd = main 樹の根。rc は returncode 直採。kaki は _after の写しを import(raw を import して __pycache__ を産まぬ・-B も assert)。"""
import os, sys, subprocess, hashlib, re, time, stat
assert sys.flags.dont_write_bytecode, '-B で走らせよ(__pycache__ を産まぬ)'
B = sys.argv[1]; RN = '68'; D = os.path.dirname(B); RAW = D + '/raw'; AFT = D + '/_after'; MAN = B + '_manifest.txt'; PAPER = B + '.md'; M = '/Users/momizimac/multi-agent-shogun'; GATE = M + '/scripts/checks/karo_mac_dasumae_gate.sh'
sys.path.insert(0, AFT); import kaki as K
sys.path.insert(0, M + '/scripts/checks'); import karo_mac_manifest_verify as V
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]; GSHA = sha16(open(GATE, 'rb').read()); os.makedirs(AFT, exist_ok=True)
items = []
for raw in open(MAN, encoding='utf-8'):
    s = raw.strip()
    if not s or s.startswith('#') or not V.SHA.search(s): continue
    items.append(V.paths_of(s)[0])
out = [f'刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {GSHA} / 照合器 sha16 {sha16(open(M + "/scripts/checks/karo_mac_manifest_verify.py", "rb").read())} / 臺帳の項 {len(items)} / 臺帳 sha16 {sha16(open(MAN, "rb").read())} / 紙 sha16 {sha16(open(PAPER, "rb").read())} / cwd {M}']
pyc = [os.path.join(d, f) for d, ds, fs in os.walk(RAW) for f in fs if '__pycache__' in d]; assert not pyc, pyc
nf = nd = 0
for d, ds, fs in os.walk(RAW, topdown=False):
    for f in fs:
        q = os.path.join(d, f)
        if stat.S_ISREG(os.lstat(q).st_mode): os.chmod(q, 0o444); nf += 1
    os.chmod(d, 0o555); nd += 1
out.append(f'① 錠 {time.strftime("%H:%M:%S")} / raw/ 配下 通常 file {nf} → 0444 / dir {nd}(raw 含む)→ 0555 / raw の mode {oct(os.stat(RAW).st_mode & 0o777)} / __pycache__ 0')
K.kaku(AFT + '/00_hosho.txt', f'歩哨 ―― 門の直前の一行 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 錠の後・門の前 / 第{RN}弾'); A = os.stat(AFT + '/00_hosho.txt').st_mtime_ns
out.append(f'② 歩哨 _after/00_hosho.txt / mtime_ns {A} / stat -f %Fm {subprocess.run(["stat", "-f", "%Fm", AFT + "/00_hosho.txt"], capture_output=True, text=True).stdout.strip()}')
p = subprocess.run(['bash', GATE, '--selftest'], capture_output=True, cwd=M)
K.kaku(AFT + '/60_gate_selftest.err', p.stderr.decode('utf-8', 'replace')); K.kaku(AFT + '/60_gate_selftest.out', p.stdout.decode('utf-8', 'replace')); K.kaku(AFT + '/60_gate_selftest.rc', str(p.returncode))
out.append(f"③ selftest | 渡した 0 | rc {p.returncode} | 結語 {[x for x in p.stderr.decode('utf-8', 'replace').split(chr(10)) if x.startswith('★自己検め')]}")
rcs = {}
def run(key, argv):
    K.kaku(f'{AFT}/61_gate_argv_{key}.txt', '\n'.join(argv[1:]))
    p = subprocess.run(['bash', GATE] + argv, capture_output=True, cwd=M); files = argv[1:]; rcs[key] = p.returncode
    K.kaku(f'{AFT}/60_gate_{key}.err', p.stderr.decode('utf-8', 'replace')); K.kaku(f'{AFT}/60_gate_{key}.out', p.stdout.decode('utf-8', 'replace')); K.kaku(f'{AFT}/60_gate_{key}.rc', str(p.returncode))
    so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace'); fuda = [l for l in se.split('\n') if l.startswith('★') and not l.startswith('★出す前')]
    j1 = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', so); tot = re.search(r'byte和 (\d+)', se)
    out.append(f"③ {key} | 渡した {len(files)} | rc {p.returncode} | 札 {len(fuda)} | 條① {j1.groups() if j1 else '−'} | 條⑤ byte和 {tot.group(1) if tot else '−'} | 結語 {[l for l in se.split(chr(10)) if l.startswith('★出す前')]} | stderr sha16 {sha16(p.stderr)}")
    for l in fuda: out.append('    ' + l.replace(D + '/', ''))
run('main', [MAN, PAPER, MAN]); run('all', [MAN] + items)
mb = open(MAN, 'rb').read(); tail = mb[-2:]; body = [l for l in mb.decode('utf-8').split('\n') if l.strip() and not l.startswith('#')]
out.append(f"④ 臺帳自身(別器・門は argv[1] を條②③④⑤に掛けぬ) | bytes {len(mb)} | 実体行 {len(body)} | 括つた行 {sum(1 for l in body if l.startswith('path=' + chr(34)))} | 末尾 2 byte {tail.hex()}(0a 一つ = {tail[-1:] == b'\n' and tail != b'\n\n'}) | CR {mb.count(b'\r')} | 行末空白 {sum(1 for l in mb.split(b'\n') if l.endswith((b' ', b'\t')))} 行 | sha16 {sha16(mb)}")
FORBID = ['scripts/checks/karo_mac_dasumae_gate.sh', 'scripts/checks/karo_mac_manifest_verify.py', 'scripts/checks/karo_mac_manifest_append.py', '.gitignore', '.claude/settings.json']
out.append('⑤ 禁域へ 0 byte | 前(00_start)と今の sha16: ' + ' / '.join(f'{p} {sha16(open(M + "/" + p, "rb").read())}' for p in FORBID))
K.kaku(f'{AFT}/60_gate_rcs.txt', '\n'.join(out)); print('\n'.join(out))
def _n(key):
    se = open(f'{AFT}/60_gate_{key}.err', encoding='utf-8').read(); a = re.search(r'全file\((\d+)本\)', se); b = re.search(r'byte和 (\d+)', se); rc = open(f'{AFT}/60_gate_{key}.rc', encoding='utf-8').read().strip()
    return (a.group(1) if a else '−'), (b.group(1) if b else '−'), rc
na, ba, ra = _n('all'); nm, bm, rm = _n('main')
top = [f'# 第{RN}弾 門控(名 = 60_gate_top.r{RN}・毎回別) # 門控の写し = 走り「all」(渡した {na} 本 = 臺帳の項 悉く / byte和 {ba} / rc {ra})を上に・走り「main」(渡した {nm} 本 = 紙 + 臺帳 / byte和 {bm} / rc {rm})を下に ―― 上端は広い方(argv _after/61_gate_argv_all.txt / _after/61_gate_argv_main.txt・stderr _after/60_gate_all.err / _after/60_gate_main.err)/ 錠 raw/ 0555/0444 は門の前・歩哨 _after/00_hosho.txt mtime_ns {A}',
       f'# 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {GSHA} / 臺帳 sha16 {sha16(open(MAN, "rb").read())} / 紙 sha16 {sha16(open(PAPER, "rb").read())}',
       '## 走り all(stderr 逐語)'] + open(f'{AFT}/60_gate_all.err', encoding='utf-8').read().rstrip('\n').split('\n') + ['## 走り main(stderr 逐語)'] + open(f'{AFT}/60_gate_main.err', encoding='utf-8').read().rstrip('\n').split('\n')
K.kaku(B + '_gate.txt', '\n'.join(top)); K.kaku(AFT + f'/60_gate_top.r{RN}.txt', '\n'.join(top)); print('門控:', B + '_gate.txt', f'+ _after/60_gate_top.r{RN}.txt')
sys.exit(0 if all(v == 0 for v in rcs.values()) else 1)
