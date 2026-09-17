# -*- coding: utf-8 -*-
"""31 既存 test の出目(第81弾 km-92)―― repo の test 二本(scripts/tests/test_detect_stale.sh 単体・test_fukuincho_detect_stale_cli.sh 統合)を写しの樹(raw/utsushi/… 又は指定の樹)へ置き、姿 B(/bin/date)と G(gdate+flock stub)で走らせ PASS/FAIL と rc を刷る。test は mktemp(/tmp)へ書く・repo へ 0 字。"""
import os, sys, re, time, subprocess, hashlib
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
TREE = sys.argv[2] if len(sys.argv) > 2 else D + '/raw/utsushi'; TAG = sys.argv[3] if len(sys.argv) > 3 else '31'
out = [f'# {TAG} 既存 test / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 樹 {os.path.relpath(TREE, D)} / lib sha16 {hashlib.sha256(open(TREE + "/scripts/lib/detect_stale.sh", "rb").read()).hexdigest()[:16]}']
for t in ('test_detect_stale.sh', 'test_fukuincho_detect_stale_cli.sh'):
    src = f'/Users/momizimac/multi-agent-shogun/scripts/tests/{t}'; dst = f'{TREE}/scripts/tests/{t}'
    out.append(f'{t}: repo sha16 {hashlib.sha256(open(src, "rb").read()).hexdigest()[:16]} / 写し sha16 {hashlib.sha256(open(dst, "rb").read()).hexdigest()[:16]}')
    for shape in ('B', 'G'):
        e = dict(os.environ); e['LC_ALL'] = 'C'; e.pop('DETECT_STALE_STALE_SEC', None)
        if shape == 'G': e['PATH'] = D + '/raw/stub_gnu:' + e['PATH']
        p = subprocess.run(['/bin/bash', dst], capture_output=True, text=True, env=e, timeout=300); o = p.stdout + p.stderr
        K.kaku(D + f'/raw/{TAG}_{t[:-3]}_{shape}.out', o)
        summ = re.findall(r'(?:PASS|FAIL)[^\n]*\d+[^\n]*', o); fails = [l for l in o.split('\n') if '[FAIL]' in l or re.match(r'\s*FAIL', l)]
        out.append(f'  姿{shape}: rc {p.returncode} / 集計行 {summ[-1][:100] if summ else "(無し)"} / FAIL 行 {len(fails)}' + ''.join('\n      ' + f[:150] for f in fails[:8]))
K.kaku(D + f'/raw/{TAG}_tests.txt', '\n'.join(out)); print('\n'.join(out))
