# -*- coding: utf-8 -*-
"""00 起(第71弾 補)―― 禁域の sha16 と 親束(km-71)・自主束・km-70 の印を先に取る(60 が前⇔後を比べる)。"""
import os, sys, time, hashlib
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
def snap(d):
    rows = []
    for r, ds, fs in os.walk(d):
        for f in fs:
            q = os.path.join(r, f)
            if os.path.isfile(q) and not os.path.islink(q): rows.append(os.path.relpath(q, d) + ' ' + hashlib.sha256(open(q, 'rb').read()).hexdigest())
    rows.sort(); return hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16] + f'({len(rows)})'
TABA = {'km-70': 'docs/evidence/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917', 'a1-jishu': 'docs/evidence/a1-jishu-kuumoji-kiten-20260917', 'km-71': 'docs/evidence/km-71-kuumoji-wa-atai-toshite-furumau-20260917'}
out = [f'# 00 起 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {sha16(M + "/scripts/checks/karo_mac_dasumae_gate.sh")} / 照合器 sha16 {sha16(M + "/scripts/checks/karo_mac_manifest_verify.py")}'] + [f'{k} {snap(M + "/" + d)}→(00_start の前)' for k, d in TABA.items()]
K.kaku(D + '/raw/00_start.txt', '\n'.join(out)); print('\n'.join(out))
