# -*- coding: utf-8 -*-
"""臺帳の器 50(第78弾 km-84・km-81b の写し・紙= README.md・臺帳= MANIFEST.txt)―― ★cd 束の根★ で karo_mac_manifest_append.py を呼び、束内相対の臺帳を建てる(裁 322699・手書き 0)。対象= README.md + raw/ 配下(通常 file・__pycache__ 除く・50 の出目・_gate/・_after/ は員外)。"""
import os, sys, subprocess, stat, time, hashlib
D = sys.argv[1]; E = D + '/raw'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; AP = M + '/scripts/checks/karo_mac_manifest_append.py'; MAN = D + '/MANIFEST.txt'
assert not os.path.exists(MAN), '臺帳が既に在る ―― 二度建てぬ'
files = ['README.md']; hi = 0
for d, ds, fs in os.walk(E):
    ds[:] = [x for x in ds if x != '__pycache__']
    for f in sorted(fs):
        q = os.path.join(d, f)
        if not stat.S_ISREG(os.lstat(q).st_mode): hi += 1; continue
        if f.startswith('50_build_manifest.') or f == '50_sengen.txt': continue
        files.append(os.path.relpath(q, D))
files = [files[0]] + sorted(files[1:])
p = subprocess.run(['python3', '-B', AP, MAN] + files, capture_output=True, cwd=D)
so = p.stdout.decode('utf-8', 'replace'); K.kaku(E + '/50_build_manifest.out', so); K.kaku(E + '/50_build_manifest.err', p.stderr.decode('utf-8', 'replace'))
rows = [l for l in open(MAN, encoding='utf-8').read().split('\n') if l.startswith('path=')] if os.path.exists(MAN) else []
K.kaku(E + '/50_sengen.txt', f'# 50 臺帳の宣 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / append.py sha16 {hashlib.sha256(open(AP, "rb").read()).hexdigest()[:16]} / cwd= 束の根 {D} / 基点= 束内相対(裁 322699) / 渡した {len(files)} / 臺帳の項 {len(rows)} / 非通常 file {hi} / rc {p.returncode}\n員外(臺帳に載せぬ・宣): MANIFEST.txt 其の物 / _gate/*(門控) / raw/50_build_manifest.out .err / raw/50_sengen.txt / _after/*(門の出目・便・臺帳の後)\n渡した path:\n' + '\n'.join('  ' + f for f in files))
print(so.strip()); print(open(E + '/50_sengen.txt', encoding='utf-8').read()[:1500]); sys.exit(p.returncode)
