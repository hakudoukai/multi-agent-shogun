# -*- coding: utf-8 -*-
"""48 前の改行(第72弾)―― 46 で `[` が「前の改行は許し 後の改行は拒む」と出た。∴ 「\\n5」「\\n\\n\\n5」は 甲(num_in_range)も生(num_same_op)も★受け★、受けた路(條⑤ の行)で生の儘 刷られる ―― 丙(safe_show)は拒む路しか守らぬ。
門票を file に落として ★門自身の 條②(行末空白)③④★ に掛け、門票が門に落ちるかを測る(nama の dasumae を検め器に使ふ・argv に門票のみ)。dasumae = MAX_BYTES / gate4 = MAX_FILE_MB。"""
import os, sys, subprocess, tempfile, shutil, time
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; KI = RAW + '/ki'; FX = RAW + '/fx'
esc = lambda s: s.replace('\n', '\\n').replace('\t', '\\t')
G = tempfile.mkdtemp(prefix='km72_48.'); g = lambda *a: subprocess.run(['git'] + list(a), capture_output=True, text=True, cwd=G, check=True)
g('init', '-q', '-b', 'main'); g('config', 'user.email', 'km72@example'); g('config', 'user.name', 'km72'); shutil.copyfile(FX + '/kiyoi.txt', G + '/kiyoi.txt'); g('add', 'kiyoi.txt'); g('commit', '-q', '-m', 'fx'); g('remote', 'add', 'origin', G); g('fetch', '-q', 'origin'); open(G + '/kiyoi.txt', 'ab').write(b'y\n'); g('add', 'kiyoi.txt')
VAL = [('n1', '\n5'), ('n3', '\n\n\n5'), ('sn', ' \n5'), ('n1000', '\n1000'), ('t1', '\t1000')]
rows = []; TK = tempfile.mkdtemp(prefix='km72_48tk.')
for gate, thr in (('dasumae', 'DASUMAE_MAX_BYTES'), ('gate4', 'GATE4_MAX_FILE_MB')):
    for var in (['nama', 'kou', 'hei', 'gou']):
        for vid, v in VAL:
            env = {k: e for k, e in os.environ.items() if not k.startswith(('DASUMAE_', 'GATE4_', 'KM_GATE_'))}; env[thr] = v
            if gate == 'dasumae': env['KM_GATE_MANIFEST_BASE'] = FX; argv = ['/bin/bash', f'{KI}/{var}/karo_mac_dasumae_gate.sh', FX + '/man.txt', FX + '/kiyoi.txt']
            else: argv = ['/bin/bash', f'{KI}/{var}/karo_mac_gate4.sh', G, 'kiyoi.txt']
            p = subprocess.run(argv, capture_output=True, env=env, cwd=M); t = p.stderr.decode('utf-8', 'replace'); ls = t.rstrip('\n').split('\n')
            fuda = [l for l in ls if f'閾 {thr}' in l]; sai = '倒' if fuda else '受'; j5 = [l for l in ls if '條⑤' in l]; tw = sum(1 for l in ls if l.endswith((' ', '\t'))); blank = sum(1 for l in ls if l == '')
            tk = f'{TK}/{gate}_{var}_{vid}.txt'; open(tk, 'wb').write(p.stderr)
            e2 = {k: e for k, e in os.environ.items() if not k.startswith(('DASUMAE_', 'GATE4_', 'KM_GATE_'))}; e2['KM_GATE_MANIFEST_BASE'] = FX
            q = subprocess.run(['/bin/bash', f'{KI}/nama/karo_mac_dasumae_gate.sh', FX + '/man.txt', tk], capture_output=True, env=e2, cwd=M); q2 = [l for l in q.stderr.decode('utf-8', 'replace').split('\n') if l.startswith('★條②') or l.startswith('★條③') or l.startswith('★條④')]
            rows.append([gate, var, vid, esc(v), p.returncode, sai, len(ls), esc(j5[0]) if j5 else '(條⑤ 無)', tw, blank, q.returncode, esc(' | '.join(q2))[:120]])
shutil.rmtree(G); shutil.rmtree(TK)
K.kaku_tsv(RAW + '/48_lead_nl.tsv', rows, ['gate', 'var', 'vid', 'val', 'rc', 'sai', 'n_lines', '條⑤の行(esc)', '行末空白の行', '空行', '門票を門に掛けた rc', '鳴つた條'])
K.kaku(RAW + '/48_lead_nl.txt', f'# 48 前の改行 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 走 {len(rows)}(門票の検め 各 1 走 = 更に {len(rows)})\n' + '\n'.join('\t'.join(map(str, r)) for r in rows)); print(open(RAW + '/48_lead_nl.txt', encoding='utf-8').read())
