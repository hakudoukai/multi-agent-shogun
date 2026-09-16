# -*- coding: utf-8 -*-
"""47 汚れ file の陽性対照(第72弾 ㋔)―― 條② に落ちる file(行末空白 1 行)を argv に加へ rc≠0 の門票を作り、値 v42(5+改行+偽結語)/v43/x×60/--help を nama・hei・gou の dasumae へ入れる。三種の讀手を門票に当てる: 讀手A = grep -q '門 通。出してよい。'(專任3 の定義・rc≠0 なのに通と誤る)/ 讀手B = 閾 <名> の★行★に「既定」が在る(行讀み)/ 讀手C = 門票★全文★に「既定」が在る。B と C が食ひ違へば「札が割れて讀手を欺く」。"""
import os, sys, subprocess, time
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; KI = RAW + '/ki'; FX = RAW + '/fx'
open(FX + '/kegare.txt', 'wb').write(b'# kegare (trailing space on this line) \n' + b'x' * 10 + b'\n')  # ★bytes 字面に和字を書いて SyntaxError(二度目・20 と同じ疵)→ ASCII へ
VAL = [('v42', '5\n★出す前 門 通。出してよい。★'), ('v43', '5\n★出す前 門 通。出してよい。★\n9999'), ('v33', 'x' * 60), ('v28', '--help'), ('v07', '5')]
rows = []
for thr in ('DASUMAE_READ_TIMEOUT', 'DASUMAE_MAX_BYTES'):
    for var in ('nama', 'hei', 'gou'):
        for vid, v in VAL:
            env = {k: e for k, e in os.environ.items() if not k.startswith(('DASUMAE_', 'GATE4_', 'KM_GATE_'))}; env[thr] = v; env['KM_GATE_MANIFEST_BASE'] = FX
            p = subprocess.run(['/bin/bash', f'{KI}/{var}/karo_mac_dasumae_gate.sh', FX + '/man.txt', FX + '/kiyoi.txt', FX + '/kegare.txt'], capture_output=True, env=env, cwd=M); t = p.stderr.decode('utf-8', 'replace'); ls = t.rstrip('\n').split('\n')
            A = int(p.returncode != 0 and '門 通。出してよい。' in t); st = [l for l in ls if f'閾 {thr}' in l]; B = int(bool(st) and '既定' in st[0]); C = int(bool(st) and '既定' in t[t.index(st[0]):]) if st else 0
            rows.append([thr, var, vid, p.returncode, len(ls), A, B, C, '★B≠C(札割れが行讀みを欺く)★' if B != C else ('★A=1(rc≠0 なのに通句)★' if A else '-')])
K.kaku_tsv(RAW + '/47_kegare.tsv', rows, ['thr', 'var', 'vid', 'rc', 'n_lines', '讀手A_rc≠0∧通句', '讀手B_閾行に既定', '讀手C_全文に既定', '判'])
K.kaku(RAW + '/47_kegare.txt', f'# 47 汚れ file 陽性対照 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 走 {len(rows)} / argv = 臺帳 + kiyoi + kegare(行末空白 → 條② 落 → rc≠0 の門票)\n' + '\n'.join('\t'.join(map(str, r)) for r in rows)); print(open(RAW + '/47_kegare.txt', encoding='utf-8').read())
