# -*- coding: utf-8 -*-
"""門を最後に走らせる器 60(第71弾 補・前の sha と印は raw/00_start.txt)―― ① 錠(raw/ 0555/0444)→ ② 歩哨 → ③ 門 四走(selftest / main=紙+臺帳 / all=臺帳の項 悉く ―― main・all は KM_GATE_MANIFEST_BASE=束の根 / nobase=main と同じ argv で unset → 落ちる事を見せる)→ ④ 門控 → ⑤ 禁域の前後(前は raw/10_kuumoji.txt の頭の sha16)+ km-70 束の印 前後。出目は悉く _after/。cwd = main 樹。"""
import os, sys, subprocess, hashlib, re, time, stat
assert sys.flags.dont_write_bytecode, '-B で走らせよ'
B = sys.argv[1]; RN = '71b'; D = os.path.dirname(B); RAW = D + '/raw'; AFT = D + '/_after'; MAN = B + '_manifest.txt'; PAPER = B + '.md'; M = '/Users/momizimac/multi-agent-shogun'; GATE = M + '/scripts/checks/karo_mac_dasumae_gate.sh'
sys.path.insert(0, RAW); import kaki as K
sys.path.insert(0, M + '/scripts/checks'); import karo_mac_manifest_verify as V
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]; GSHA = sha16(open(GATE, 'rb').read()); os.makedirs(AFT, exist_ok=True)
items = []
for raw in open(MAN, encoding='utf-8'):
    s = raw.strip()
    if not s or s.startswith('#') or not V.SHA.search(s): continue
    items.append(os.path.join(D, V.paths_of(s)[0]))
out = [f'刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {GSHA} / 照合器 sha16 {sha16(open(M + "/scripts/checks/karo_mac_manifest_verify.py", "rb").read())} / 臺帳の項 {len(items)} / 臺帳 sha16 {sha16(open(MAN, "rb").read())} / 紙 sha16 {sha16(open(PAPER, "rb").read())} / cwd {M} / 基点 KM_GATE_MANIFEST_BASE={D}']
pyc = [os.path.join(d, f) for d, ds, fs in os.walk(RAW) for f in fs if '__pycache__' in d]; assert not pyc, pyc
nf = nd = 0
for d, ds, fs in os.walk(RAW, topdown=False):
    for f in fs:
        q = os.path.join(d, f)
        if stat.S_ISREG(os.lstat(q).st_mode): os.chmod(q, 0o444); nf += 1
    os.chmod(d, 0o555); nd += 1
out.append(f'① 錠 {time.strftime("%H:%M:%S")} / raw/ 配下 通常 file {nf} → 0444 / dir {nd}(raw 含む)→ 0555 / raw の mode {oct(os.stat(RAW).st_mode & 0o777)} / __pycache__ 0')
K.kaku(AFT + '/00_hosho.txt', f'歩哨 ―― 門の直前の一行 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 錠の後・門の前 / 第71弾 補'); A = os.stat(AFT + '/00_hosho.txt').st_mtime_ns
out.append(f'② 歩哨 _after/00_hosho.txt / mtime_ns {A}')
p = subprocess.run(['bash', GATE, '--selftest'], capture_output=True, cwd=M)
K.kaku(AFT + '/60_gate_selftest.err', p.stderr.decode('utf-8', 'replace')); K.kaku(AFT + '/60_gate_selftest.out', p.stdout.decode('utf-8', 'replace')); K.kaku(AFT + '/60_gate_selftest.rc', str(p.returncode))
out.append(f"③ selftest | 渡した 0 | rc {p.returncode} | 札 0 | 結語 {[x for x in p.stderr.decode('utf-8', 'replace').split(chr(10)) if x.startswith('★自己検め')]}")
rcs = {}
def run(key, argv, base):
    K.kaku(f'{AFT}/61_gate_argv_{key}.txt', f'# KM_GATE_MANIFEST_BASE={base if base is not None else "(unset)"}\n' + '\n'.join(argv))
    env = dict(os.environ); env.pop('KM_GATE_MANIFEST_BASE', None)
    if base is not None: env['KM_GATE_MANIFEST_BASE'] = base
    p = subprocess.run(['bash', GATE] + argv, capture_output=True, cwd=M, env=env); files = argv[1:]; rcs[key] = p.returncode
    K.kaku(f'{AFT}/60_gate_{key}.err', p.stderr.decode('utf-8', 'replace')); K.kaku(f'{AFT}/60_gate_{key}.out', p.stdout.decode('utf-8', 'replace')); K.kaku(f'{AFT}/60_gate_{key}.rc', str(p.returncode))
    so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace'); fuda = [l for l in se.split('\n') if l.startswith('★') and not l.startswith('★出す前')]
    j1 = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', so); tot = re.search(r'byte和 (\d+)', se); kt = [l for l in se.split('\n') if l.startswith('條① 基点')]
    out.append(f"③ {key} | 渡した {len(files)} | rc {p.returncode} | 札 {len(fuda)} | 條① {j1.groups() if j1 else '−'} | 基点 {kt[0][:40] if kt else '−'} | 條⑤ byte和 {tot.group(1) if tot else '−'} | 結語 {[l for l in se.split(chr(10)) if l.startswith('★出す前')]} | stderr sha16 {sha16(p.stderr)}")
    for l in fuda: out.append('    ' + l.replace(D + '/', ''))
run('main', [MAN, PAPER, MAN], D); run('all', [MAN] + items, D); run('nobase', [MAN, PAPER, MAN], None)
mb = open(MAN, 'rb').read(); tail = mb[-2:]; body = [l for l in mb.decode('utf-8').split('\n') if l.strip() and not l.startswith('#')]
out.append(f"④ 臺帳自身(別器・門は argv[1] を條②③④⑤に掛けぬ) | bytes {len(mb)} | 実体行 {len(body)} | 括つた行 {sum(1 for l in body if l.startswith('path=' + chr(34)))} | 末尾 2 byte {tail.hex()}(0a 一つ = {tail[-1:] == b'\n' and tail != b'\n\n'}) | CR {mb.count(b'\r')} | 行末空白 {sum(1 for l in mb.split(b'\n') if l.endswith((b' ', b'\t')))} 行 | sha16 {sha16(mb)}")
T10 = open(RAW + '/00_start.txt', encoding='utf-8').read(); mae = {'scripts/checks/karo_mac_dasumae_gate.sh': re.search(r'門 sha16 ([0-9a-f]{16})', T10).group(1), 'scripts/checks/karo_mac_manifest_verify.py': re.search(r'照合器 sha16 ([0-9a-f]{16})', T10).group(1)}
FORBID = list(mae) + ['scripts/checks/karo_mac_manifest_append.py', '.gitignore', '.claude/settings.json', 'scripts/inbox_write.sh']
ima = {p_: sha16(open(M + '/' + p_, 'rb').read()) for p_ in FORBID}
out.append('⑤ 禁域へ 0 byte | 前(00_start・無い物は 今 のみ)⇔今: ' + ' / '.join(f'{p_} {mae.get(p_, "−")}→{ima[p_]} {"同" if mae.get(p_) == ima[p_] else ("(前 無)" if p_ not in mae else "★違★")}' for p_ in FORBID))
def taba_in(d):
    rows = []
    for r, ds, fs in os.walk(M + '/' + d):
        for f in fs:
            q = os.path.join(r, f)
            if os.path.isfile(q) and not os.path.islink(q): rows.append(os.path.relpath(q, M + '/' + d) + ' ' + hashlib.sha256(open(q, 'rb').read()).hexdigest())
    rows.sort(); return hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16], len(rows)
TABA = {'km-70': 'docs/evidence/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917', 'a1-jishu': 'docs/evidence/a1-jishu-kuumoji-kiten-20260917', 'km-71': 'docs/evidence/km-71-kuumoji-wa-atai-toshite-furumau-20260917'}
mae_in = dict(re.findall(r'(km-70|a1-jishu|km-71) ([0-9a-f]{16}\(\d+\))→', T10)); ima_in = {k: (lambda t: f'{t[0]}({t[1]})')(taba_in(d)) for k, d in TABA.items()}
out.append('⑥ 三束(親 km-71・自主束・km-70)へ 0 字 | 印 前(00_start)⇔今: ' + ' / '.join(f'{k} {mae_in.get(k, "?")}→{ima_in[k]} {"同" if mae_in.get(k) == ima_in[k] else "★違★"}' for k in TABA))
K.kaku(f'{AFT}/60_gate_rcs.txt', '\n'.join(out)); print('\n'.join(out))
def _n(key):
    se = open(f'{AFT}/60_gate_{key}.err', encoding='utf-8').read(); a = re.search(r'全file\((\d+)本\)', se); b = re.search(r'byte和 (\d+)', se); rc = open(f'{AFT}/60_gate_{key}.rc', encoding='utf-8').read().strip()
    return (a.group(1) if a else '−'), (b.group(1) if b else '−'), rc
na, ba, ra = _n('all'); nm, bm, rm = _n('main'); nn, bn, rn = _n('nobase')
top = [f'# 第{RN}弾 門控(名 = 60_gate_top.r{RN}・毎回別) # 三走 ―― 「all」(渡した {na} 本 = 臺帳の項 悉く / byte和 {ba} / rc {ra})・「main」(渡した {nm} 本 = 紙 + 臺帳 / byte和 {bm} / rc {rm})は ★KM_GATE_MANIFEST_BASE=束の根★ / 「nobase」(main と同じ argv・環境変数 unset / rc {rn})は ★既定基点(repo 根)では束内相対の臺帳が悉く実体無で落ちる事の證★ ―― argv _after/61_gate_argv_*.txt・stderr _after/60_gate_*.err / 錠 raw/ 0555/0444 は門の前・歩哨 _after/00_hosho.txt mtime_ns {A}',
       f'# 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {GSHA} / 臺帳 sha16 {sha16(open(MAN, "rb").read())} / 紙 sha16 {sha16(open(PAPER, "rb").read())} / 基点 {D}',
       '## 走り all(stderr 逐語・基点明示)'] + open(f'{AFT}/60_gate_all.err', encoding='utf-8').read().rstrip('\n').split('\n') + ['## 走り main(stderr 逐語・基点明示)'] + open(f'{AFT}/60_gate_main.err', encoding='utf-8').read().rstrip('\n').split('\n') + ['## 走り nobase(stderr 逐語・基点無し ―― 落ちて正)'] + open(f'{AFT}/60_gate_nobase.err', encoding='utf-8').read().rstrip('\n').split('\n')
K.kaku(B + '_gate.txt', '\n'.join(top)); K.kaku(AFT + f'/60_gate_top.r{RN}.txt', '\n'.join(top)); print('門控:', B + '_gate.txt', f'+ _after/60_gate_top.r{RN}.txt')
sys.exit(0 if rcs['main'] == 0 and rcs['all'] == 0 and rcs['nobase'] == 1 else 1)
