# -*- coding: utf-8 -*-
"""臺帳の器 50(第71弾 補・km-71 の写し)―― ★cd 束の根★ で karo_mac_manifest_append.py を呼び、束内相対の臺帳を建てる(裁 322699・手書き 0)。対象 = 紙 + raw/ 配下の通常 file(S_ISREG・__pycache__ 無)。_after/ と門控は員外(門の後に生れる)。"""
import os, sys, subprocess, stat, time, hashlib
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; AP = M + '/scripts/checks/karo_mac_manifest_append.py'; MAN = B + '_manifest.txt'
assert not os.path.exists(MAN), '臺帳が既に在る ―― 二度建てぬ'
files = [os.path.relpath(B + '.md', D)]; hi = 0
for d, ds, fs in os.walk(E):
    ds[:] = [x for x in ds if x != '__pycache__']
    for f in sorted(fs):
        q = os.path.join(d, f)
        if not stat.S_ISREG(os.lstat(q).st_mode): hi += 1; continue
        files.append(os.path.relpath(q, D))
files = [files[0]] + sorted(files[1:])
p = subprocess.run(['python3', '-B', AP, MAN] + files, capture_output=True, cwd=D)
so = p.stdout.decode('utf-8', 'replace'); K.kaku(E + '/50_build_manifest.out', so); K.kaku(E + '/50_build_manifest.err', p.stderr.decode('utf-8', 'replace'))
mb = open(MAN, 'rb').read(); rows = [l for l in mb.decode('utf-8').split('\n') if l.startswith('path=')]
K.kaku(E + '/50_sengen.txt', f'# 50 臺帳の宣 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / append.py sha16 {hashlib.sha256(open(AP, "rb").read()).hexdigest()[:16]} / cwd = 束の根 {D}\n渡した {len(files)} 本(紙 1 + raw/ {len(files) - 1}・非通常 {hi})/ rc {p.returncode} / 項 {len(rows)} / 括つた {sum(1 for l in rows if l.startswith(chr(112) + "ath=" + chr(34)))} / 一行目 {rows[0][:60] if rows else "-"}\n★基点 = 束の根(束内相対)。照合は KM_GATE_MANIFEST_BASE={D} を門へ、或は verify.py 第二引数へ。★\n★此の宣は臺帳の後に書かれる故 臺帳に載らぬ(員外)。臺帳自身も員外。★')
print(so.strip()); print(open(E + '/50_sengen.txt', encoding='utf-8').read()); sys.exit(p.returncode)
