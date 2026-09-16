# -*- coding: utf-8 -*-
"""10 写し(第72弾)―― 生器二本+照合器を raw/ki/nama/ へ写し、專任3 の diff 7本(枝 a9bb89a から git show で引き、disk の km-50y/an/ と sha を突き合はす)を patch -p1 で当てて kou/otsu/hei/gou を建てる(乙は gate4 の diff が無い → nama の写し)。
加へて 合の写しから gou_x(TIMEOUT の呼び口の床天 1..86400 → 5..60)・gou_y(呼び口の chk を無い名 tmo_okk へ)を str.replace(count を assert)で建てる。專任3 の .nama/ki_*/ の仮器と sha16 を比べる。生器へ 0 字。母數(diff 7本の hunk・定義した関数・変へた関数・呼び口)も此處で数へる。"""
import os, sys, re, subprocess, hashlib, time, shutil, stat
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; TIP = 'a9bb89a'; Y = 'docs/evidence/km-50-yabure-hachikei-no-fusagikata-20260917'
KI = RAW + '/ki'; AN = KI + '/an'; os.makedirs(AN, exist_ok=True)
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]
SRC = {'karo_mac_dasumae_gate.sh': 'scripts/checks/karo_mac_dasumae_gate.sh', 'karo_mac_gate4.sh': 'scripts/checks/karo_mac_gate4.sh', 'karo_mac_manifest_verify.py': 'scripts/checks/karo_mac_manifest_verify.py'}
DIFFS = {'kou': ['kou_dasumae', 'kou_gate4'], 'otsu': ['otsu_dasumae'], 'hei': ['hei_dasumae', 'hei_gate4'], 'gou': ['gou_dasumae', 'gou_gate4']}
out = [f'# 10 写し / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 的 {TIP} / patch {subprocess.run(["patch", "--version"], capture_output=True, text=True).stdout.split(chr(10))[0]}']
def mk(v):
    d = f'{KI}/{v}'; os.makedirs(d, exist_ok=True)
    for f, s in SRC.items(): shutil.copyfile(M + '/' + s, f'{d}/{f}')
    return d
mk('nama'); out.append('nama: ' + ' / '.join(f'{f} {sha16(open(KI + "/nama/" + f, "rb").read())}(生 {sha16(open(M + "/" + s, "rb").read())})' for f, s in SRC.items()))
# 母數: diff 7本
hunks = 0; defs = set(); calls = 0; dl = 0
for v, names in DIFFS.items():
    for n in names:
        b = subprocess.run(['git', 'show', f'{TIP}:{Y}/an/{n}.diff'], capture_output=True, cwd=M).stdout
        disk = open(f'{M}/{Y}/an/{n}.diff', 'rb').read()
        open(f'{AN}/{n}.diff', 'wb').write(b); t = b.decode('utf-8')
        h = t.count('\n@@ '); hunks += h; dl += t.count('\n')
        fn = re.findall(r'^\+([a-z_]+)\(\)\{', t, re.M); defs.update(fn); c = len(re.findall(r'^\+fix_threshold ', t, re.M)); calls += c
        out.append(f'diff {n}: {len(t.splitlines())} 行 / hunk {h} / +定義 {fn} / +呼び口 {c} / sha16 {sha16(b)} disk と {"同" if b == disk else "★違★"}')
out.append(f'★母數★ diff 7 本 / 行 {dl} / hunk {hunks} / 新たに定義した関数 {sorted(defs)}({len(defs)}) / 変へた関数 fix_threshold(2 file) / 変へた呼び口 {calls}(甲 4・乙 1・合 4)/ 的の生器 2 本 + 照合器 1 本(呼ばれるのみ)')
# 当てる
for v, names in DIFFS.items():
    d = mk(v)
    for n in names:
        p = subprocess.run(['patch', '-p1', '-d', d, '-i', f'{AN}/{n}.diff'], capture_output=True, text=True)
        rej = [f for f in os.listdir(d) if f.endswith('.rej') or f.endswith('.orig')]
        out.append(f'{v} ← {n}: rc {p.returncode} / ' + ' | '.join(l for l in p.stdout.splitlines() if l.strip()) + (f' / ★rej/orig {rej}★' if rej else ''))
        for f in rej: os.remove(f'{d}/{f}')
    for f in ('karo_mac_dasumae_gate.sh', 'karo_mac_gate4.sh'):
        mine = sha16(open(f'{d}/{f}', 'rb').read()); theirs = subprocess.run(['git', 'show', f'{TIP}:{Y}/.nama/ki_{v}/{f}'], capture_output=True, cwd=M)
        th = sha16(theirs.stdout) if theirs.returncode == 0 else '(無)'
        out.append(f'  {v}/{f} sha16 {mine} ⇔ 專任3 .nama/ki_{v}/{f} {th} {"★同★" if th == mine else ("(彼の束に無し・乙は gate4 に diff 無し)" if th == "(無)" else "★違★")}')
# 合x / 合y(呼び口だけを替へた合)
g = open(f'{KI}/gou/karo_mac_dasumae_gate.sh', encoding='utf-8').read()
old = 'fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO tmo_ok 1 86400'
for v, new in (('gou_x', 'fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO tmo_ok 5 60'), ('gou_y', 'fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO tmo_okk 1 86400')):
    assert g.count(old) == 1, g.count(old); d = mk(v); shutil.copyfile(f'{KI}/gou/karo_mac_gate4.sh', f'{d}/karo_mac_gate4.sh')
    t = g.replace(old, new); assert t.count(new) == 1 and t != g
    open(f'{d}/karo_mac_dasumae_gate.sh', 'w', encoding='utf-8', newline='\n').write(t)
    out.append(f'{v}: 合 の dasumae の呼び口一行を替へた(count 1 を assert)「{old}」→「{new}」 sha16 {sha16(t.encode())}')
for v in ('nama', 'kou', 'otsu', 'hei', 'gou', 'gou_x', 'gou_y'):
    for f in ('karo_mac_dasumae_gate.sh', 'karo_mac_gate4.sh'):
        p = subprocess.run(['bash', '-n', f'{KI}/{v}/{f}'], capture_output=True, text=True); assert p.returncode == 0, (v, f, p.stderr)
out.append('bash -n: 七形 × 二本 = 14 本 悉く rc 0(文法)'); out.append('★生器 sha16(此の後)★ ' + ' / '.join(f'{f} {sha16(open(M + "/" + s, "rb").read())}' for f, s in SRC.items()))
K.kaku(RAW + '/10_utsushi.txt', '\n'.join(out)); print('\n'.join(out))
