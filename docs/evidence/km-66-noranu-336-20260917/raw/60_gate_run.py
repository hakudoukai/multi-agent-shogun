# -*- coding: utf-8 -*-
"""門を最後に走らせる器 60(第66弾・前弾の形・path を本弾の在處(worktree docs/evidence)に合はせた)。三走: selftest / main = 紙 + 臺帳(臺帳付)/ all = 臺帳の項 悉く(臺帳付)。cwd = main 樹の根(項の path が其処からの相對ゆゑ)。rc は returncode 直採。argv の列は 61_ に残す。門控 = <束>_gate.txt + raw/60_gate_top.r66.txt。禁域の前後の sha16 を印字。"""
import os, sys, subprocess, hashlib, re, time
B = sys.argv[1]; RN = '66'; D = os.path.dirname(B); E = D + '/raw'; MAN = B + '_manifest.txt'; PAPER = B + '.md'; M = '/Users/momizimac/multi-agent-shogun'; GATE = M + '/scripts/checks/karo_mac_dasumae_gate.sh'
sys.path.insert(0, E); import kaki as K
sys.path.insert(0, M + '/scripts/checks'); import karo_mac_manifest_verify as V
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]; GSHA = sha16(open(GATE, 'rb').read())
items = []
for raw in open(MAN, encoding='utf-8'):
    s = raw.strip()
    if not s or s.startswith('#') or not V.SHA.search(s): continue
    items.append(V.paths_of(s)[0])
out = [f'刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {GSHA} / 照合器 sha16 {sha16(open(M + "/scripts/checks/karo_mac_manifest_verify.py", "rb").read())} / 臺帳の項 {len(items)} / 臺帳 sha16 {sha16(open(MAN, "rb").read())} / 紙 sha16 {sha16(open(PAPER, "rb").read())} / cwd {M}']
p = subprocess.run(['bash', GATE, '--selftest'], capture_output=True, cwd=M)
K.kaku(E + '/60_gate_selftest.err', p.stderr.decode('utf-8', 'replace')); K.kaku(E + '/60_gate_selftest.out', p.stdout.decode('utf-8', 'replace')); K.kaku(E + '/60_gate_selftest.rc', str(p.returncode))
out.append(f"selftest | 渡した 0 | rc {p.returncode} | 結語 {[x for x in p.stderr.decode('utf-8', 'replace').split(chr(10)) if x.startswith('★自己検め')]}")
def run(key, argv):
    K.kaku(f'{E}/61_gate_argv_{key}.txt', '\n'.join(argv[1:]))
    p = subprocess.run(['bash', GATE] + argv, capture_output=True, cwd=M); files = argv[1:]
    K.kaku(f'{E}/60_gate_{key}.err', p.stderr.decode('utf-8', 'replace')); K.kaku(f'{E}/60_gate_{key}.out', p.stdout.decode('utf-8', 'replace')); K.kaku(f'{E}/60_gate_{key}.rc', str(p.returncode))
    so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace'); fuda = [l for l in se.split('\n') if l.startswith('★') and not l.startswith('★出す前')]
    j1 = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', so); tot = re.search(r'byte和 (\d+)', se)
    out.append(f"{key} | 渡した {len(files)} | rc {p.returncode} | 札 {len(fuda)} | 條① {j1.groups() if j1 else '−'} | 條⑤ byte和 {tot.group(1) if tot else '−'} | 結語 {[l for l in se.split(chr(10)) if l.startswith('★出す前')]} | stderr sha16 {sha16(p.stderr)}")
    for l in fuda: out.append('    ' + l.replace(D + '/', ''))
run('main', [MAN, PAPER, MAN]); run('all', [MAN] + items)
mb = open(MAN, 'rb').read(); tail = mb[-2:]; body = [l for l in mb.decode('utf-8').split('\n') if l.strip() and not l.startswith('#')]
out.append(f"臺帳自身(別器・門は argv[1] を條②③④⑤に掛けぬ) | bytes {len(mb)} | 実体行 {len(body)} | 括つた行 {sum(1 for l in body if l.startswith('path=' + chr(34)))} | 末尾 2 byte {tail.hex()}(0a 一つ = {tail[-1:] == b'\n' and tail != b'\n\n'}) | CR {mb.count(b'\r')} | 行末空白 {sum(1 for l in mb.split(b'\n') if l.endswith((b' ', b'\t')))} 行 | sha16 {sha16(mb)}")
FORBID = ['scripts/checks/karo_mac_dasumae_gate.sh', 'scripts/checks/karo_mac_manifest_verify.py', 'scripts/checks/karo_mac_manifest_append.py', '.gitignore', '.claude/settings.json']
out.append('禁域へ 0 byte | 前(00_start)と今の sha16: ' + ' / '.join(f'{p} {sha16(open(M + "/" + p, "rb").read())}' for p in FORBID) + f" | main .git/index mtime {time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(os.stat(M + '/.git/index').st_mtime))} / worktree index mtime {time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(os.stat(M + '/.git/worktrees/karo-mac-a1/index').st_mtime))}")
K.kaku(f'{E}/60_gate_rcs.txt', '\n'.join(out)); print('\n'.join(out))
def _n(key):
    se = open(f'{E}/60_gate_{key}.err', encoding='utf-8').read(); a = re.search(r'全file\((\d+)本\)', se); b = re.search(r'byte和 (\d+)', se); rc = open(f'{E}/60_gate_{key}.rc', encoding='utf-8').read().strip()
    return (a.group(1) if a else '−'), (b.group(1) if b else '−'), rc
na, ba, ra = _n('all'); nm, bm, rm = _n('main')
top = [f'# 第{RN}弾 門控(名 = 60_gate_top.r{RN}・毎回別) # 門控の写し = 走り「all」(渡した {na} 本 = 臺帳の項 悉く / byte和 {ba} / rc {ra})を上に・走り「main」(渡した {nm} 本 = 紙 + 臺帳 / byte和 {bm} / rc {rm})を下に ―― 上端は広い方(argv raw/61_gate_argv_all.txt / raw/61_gate_argv_main.txt・stderr raw/60_gate_all.err / raw/60_gate_main.err)',
       f'# 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {GSHA} / 臺帳 sha16 {sha16(open(MAN, "rb").read())} / 紙 sha16 {sha16(open(PAPER, "rb").read())}',
       '## 走り all(stderr 逐語)'] + open(f'{E}/60_gate_all.err', encoding='utf-8').read().rstrip('\n').split('\n') + ['## 走り main(stderr 逐語)'] + open(f'{E}/60_gate_main.err', encoding='utf-8').read().rstrip('\n').split('\n')
K.kaku(B + '_gate.txt', '\n'.join(top)); K.kaku(E + f'/60_gate_top.r{RN}.txt', '\n'.join(top)); print('門控:', B + '_gate.txt', f'+ raw/60_gate_top.r{RN}.txt')
