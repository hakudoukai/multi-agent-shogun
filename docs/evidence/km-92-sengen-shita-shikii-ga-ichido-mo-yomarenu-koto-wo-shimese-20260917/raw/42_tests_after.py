# -*- coding: utf-8 -*-
"""42 既存 test・直し後(第81弾 km-92・二走= 40 二走の写しで・初走は .first)―― 31 と同じ二本(単体・CLI 統合)を raw/40_utsushi(直した写し)で、姿 B(/bin/date・flock 無し)/ BF(B + flock stub)/ G(gdate + flock stub)で走らせる。31(直し前)との差が直しの効き。test は mktemp(/tmp)へ書く・repo へ 0 字。"""
import os, sys, re, time, subprocess, hashlib
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; TREE = D + '/raw/40_utsushi'; TAG = '42'
out = [f'# {TAG} 既存 test・直し後 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 樹 {os.path.relpath(TREE, D)} / lib sha16 {hashlib.sha256(open(TREE + "/scripts/lib/detect_stale.sh", "rb").read()).hexdigest()[:16]}']
for t in ('test_detect_stale.sh', 'test_fukuincho_detect_stale_cli.sh'):
    dst = f'{TREE}/scripts/tests/{t}'; out.append(f'{t}: 写し sha16 {hashlib.sha256(open(dst, "rb").read()).hexdigest()[:16]}(repo と同じ・31 参照)')
    for shape in ('B', 'BF', 'G'):
        e = dict(os.environ); e['LC_ALL'] = 'C'; e.pop('DETECT_STALE_STALE_SEC', None)
        if shape == 'G': e['PATH'] = D + '/raw/stub_gnu:' + e['PATH']
        if shape == 'BF': e['PATH'] = D + '/raw/stub_flock:' + e['PATH']
        p = subprocess.run(['/bin/bash', dst], capture_output=True, text=True, env=e, timeout=300); o = p.stdout + p.stderr
        K.kaku(D + f'/raw/{TAG}_{t[:-3]}_{shape}.out', o)
        summ = re.findall(r'(?:PASS|FAIL)[^\n]*\d+[^\n]*', o); fails = [l for l in o.split('\n') if '[FAIL]' in l or re.match(r'\s*FAIL', l)]
        out.append(f'  姿{shape:2s}: rc {p.returncode} / 集計行 {summ[-1][:100] if summ else "(無し)"} / FAIL 行 {len(fails)}' + ''.join('\n      ' + f[:150] for f in fails[:8]))
K.kaku(D + f'/raw/{TAG}_tests.txt', '\n'.join(out)); print('\n'.join(out))
