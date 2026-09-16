# -*- coding: utf-8 -*-
"""00 起(第72弾)―― 生器四本の sha16 と、讀むだけの束(專任3 km-50 二束・親 km-71/71b)の印を先に取る(60 が前⇔後を比べ、0 字 を示す)。"""
import os, sys, time, hashlib, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
def snap(d):
    rows = []
    for r, ds, fs in os.walk(d):
        for f in fs:
            q = os.path.join(r, f)
            if os.path.isfile(q) and not os.path.islink(q): rows.append(os.path.relpath(q, d) + ' ' + hashlib.sha256(open(q, 'rb').read()).hexdigest())
    rows.sort(); return hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16] + f'({len(rows)})'
KI = {'門': 'scripts/checks/karo_mac_dasumae_gate.sh', 'gate4': 'scripts/checks/karo_mac_gate4.sh', '照合器': 'scripts/checks/karo_mac_manifest_verify.py', 'append': 'scripts/checks/karo_mac_manifest_append.py'}
TABA = {'km-50y': 'docs/evidence/km-50-yabure-hachikei-no-fusagikata-20260917', 'km-50k': 'docs/evidence/km-50-kara-wa-todokazu-20260917', 'km-71': 'docs/evidence/km-71-kuumoji-wa-atai-toshite-furumau-20260917', 'km-71b': 'docs/evidence/km-71b-fusagikata-ni-an-20260917'}
tip = subprocess.run(['git', 'rev-parse', '--short', 'ashigaru-mac-3/km-50-yabure-hachikei-no-fusagikata-20260917'], capture_output=True, text=True, cwd=M).stdout.strip()
tree = subprocess.run(['git', 'rev-parse', 'ashigaru-mac-3/km-50-yabure-hachikei-no-fusagikata-20260917^{tree}'], capture_output=True, text=True, cwd=M).stdout.strip()[:12]
out = [f'# 00 起 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / ' + ' / '.join(f'{k} sha16 {sha16(M + "/" + p)}' for k, p in KI.items()), f'的の枝 tip {tip} tree {tree}(讀むのみ)'] + [f'{k} {snap(M + "/" + d)}→(00_start の前)' for k, d in TABA.items()]
K.kaku(D + '/raw/00_start.txt', '\n'.join(out)); print('\n'.join(out))
