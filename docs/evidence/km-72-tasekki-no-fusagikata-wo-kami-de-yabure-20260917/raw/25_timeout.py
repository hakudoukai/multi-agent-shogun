# -*- coding: utf-8 -*-
"""25 timeout(1) の語法を 0.1 秒粒で実測(第72弾)―― 乙/合 が「受けた」値が後段で何を意味するか。`timeout V true` の rc(番人が見る物)と `timeout V sleep 2` の rc と経過(後段が実際にする物)。專任3 の粒は 1 秒(㋕⑸)。"""
import sys, subprocess, time, shutil
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
TB = shutil.which('timeout'); V = ['1', '0', '0m', '0.0', '0.5', '10m', '1e9', '99999d', '86401', '--help', '--version', '-v', ' 5 ', '5\n', '-0', '+5', '010']
rows = []
for v in V:
    p = subprocess.run([TB, v, 'true'], capture_output=True); t0 = time.time(); q = subprocess.run([TB, v, 'sleep', '2'], capture_output=True); el = time.time() - t0
    rows.append([repr(v), p.returncode, len(p.stdout), q.returncode, f'{el:.1f}', ('番人 受' if p.returncode != 125 else '番人 拒') + ' / 後段 ' + ('時限が効いた' if q.returncode == 124 else ('時限は 2 秒より長いか無し(此の器では分てぬ・一走目は「無し」と書いた疵 → .first)' if q.returncode == 0 and el >= 1.9 else f'rc {q.returncode} で即時(命は走らず)' if el < 0.5 else f'rc {q.returncode}'))])
K.kaku_tsv(D + '/raw/25_timeout.tsv', rows, ['value_repr', 'true_rc', 'true_stdout_bytes', 'sleep2_rc', 'elapsed_s', '判']); K.kaku(D + '/raw/25_timeout.txt', f'# 25 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / timeout = {TB} / {subprocess.run([TB, "--version"], capture_output=True, text=True).stdout.splitlines()[0]}\n' + '\n'.join('\t'.join(map(str, r)) for r in rows)); print(open(D + '/raw/25_timeout.txt', encoding='utf-8').read())
