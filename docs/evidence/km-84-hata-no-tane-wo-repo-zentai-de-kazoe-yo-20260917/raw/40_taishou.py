# -*- coding: utf-8 -*-
"""40 ㋓ 両対照(第78弾 km-84)―― ★同じ路(lib_run.run・同じ bash・同じ env の渡し方)★ に 陽性(必ず鳴る種)と 陰性(鳴つてはならぬ種)を各一本ずつ乗せる。
陽性A(器の報せ欄): 今の disk の scripts/inbox_watcher.sh から _th_say / env_state / fix_flag を錨で逐語に抜き(讀むのみ)、番人付きの写し器= fix_flag ASW_PROCESS_TIMEOUT 1 … + L1633 の比較器。値 2 → 報せ 1 行・1側(既定へ倒す)が出ねば器は死んで居る。
陽性B(外の声欄): 30 の乙の写し器(STARTUP_PROMPT_SENT L1469 `-eq 1`)へ abc → interpreter が「integer expression expected」を刷らねば器は死んで居る。
陰性: 同じ二本の写し器に 1 と 0 → 報せ 0・声 0・宣どほりの枝。★陰性が両形(番人付き/裸)で同じ挙動である事★ も併せて示す(黙り= 器の死 と区別する為)。"""
import os, sys, re, time, hashlib
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from lib_run import run, mark; M = '/Users/momizimac/multi-agent-shogun'; H = D + '/raw/40_h'; os.makedirs(H, exist_ok=True)
SRC = M + '/scripts/inbox_watcher.sh'; S = open(SRC, encoding='utf-8').read(); sha16 = hashlib.sha256(S.encode('utf-8')).hexdigest()[:16]
defs = []
for fn in ('_th_say', 'env_state', 'fix_flag'):
    ms = re.findall(r'(?ms)^' + fn + r'\(\)\{.*?^\}$|^' + fn + r'\(\)\{[^\n]*\}$', S); assert len(ms) == 1, (fn, len(ms)); defs.append(ms[0])
cmp_line = [l for l in S.split('\n') if 'if [ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; then' in l]; assert len(cmp_line) == 1
te = re.search(r'\[ .*? \]', cmp_line[0]).group(0)
hA = H + '/A_bannin_ASW_PROCESS_TIMEOUT.sh'; K.kaku(hA, '#!/bin/bash\n# 陽性A の写し器 ―― 番人付き(定義三本は disk の inbox_watcher.sh ' + sha16 + ' から逐語)\n' + '\n'.join(defs) + '\nfix_flag ASW_PROCESS_TIMEOUT 1 ASW_PROCESS_TIMEOUT\nif ' + te + '; then printf \'BRANCH=then\\n\'; else printf \'BRANCH=else\\n\'; fi')
hA0 = [x for x in os.listdir(D + '/raw/30_h') if 'ASW_PROCESS_TIMEOUT' in x]; assert len(hA0) == 1; hA0 = D + '/raw/30_h/' + hA0[0]   # 裸形(30 の写し器)
hB = [x for x in os.listdir(D + '/raw/30_h') if 'STARTUP_PROMPT_SENT' in x]; assert len(hB) == 1; hB = D + '/raw/30_h/' + hB[0]
rows = []
def go(label, h, N, v, expect):
    x = run(h, 'sh', N, v, D); rows.append((label, os.path.relpath(h, D), mark(v), x['rc'], x['branch'], x['utsuwa'], x['soto'], x['head'], expect)); return x
a2 = go('★陽性A(報せ欄・番人付き・値2)★', hA, 'ASW_PROCESS_TIMEOUT', '2', '報せ1・声0・then(既定1へ倒す)')
a1 = go('陰性A1(番人付き・値1)', hA, 'ASW_PROCESS_TIMEOUT', '1', '報せ0・声0・then')
a0 = go('陰性A0(番人付き・値0)', hA, 'ASW_PROCESS_TIMEOUT', '0', '報せ0・声0・else')
n2 = go('裸形(30 の写し器・値2)', hA0, 'ASW_PROCESS_TIMEOUT', '2', '報せ0・声0・else= 黙つて 0側(害の形)')
n1 = go('陰性A1′(裸形・値1)', hA0, 'ASW_PROCESS_TIMEOUT', '1', '報せ0・声0・then')
n0 = go('陰性A0′(裸形・値0)', hA0, 'ASW_PROCESS_TIMEOUT', '0', '報せ0・声0・else')
b = go('★陽性B(声欄・乙 -eq 1・値abc)★', hB, 'STARTUP_PROMPT_SENT', 'abc', '声1・報せ0・else')
b1 = go('陰性B1(乙・値1)', hB, 'STARTUP_PROMPT_SENT', '1', '報せ0・声0・then')
b0 = go('陰性B0(乙・値0)', hB, 'STARTUP_PROMPT_SENT', '0', '報せ0・声0・else')
han = []
han.append(('陽性A 鳴つた(報せ≥1 ∧ then)', a2['utsuwa'] >= 1 and a2['branch'] == 'then'))
han.append(('陽性B 鳴つた(声≥1 ∧ else)', b['soto'] >= 1 and b['branch'] == 'else'))
han.append(('陰性A 番人付きと裸形が同挙動(1→then/0→else・報せ0・声0)', all(x['utsuwa'] == 0 and x['soto'] == 0 for x in (a1, a0, n1, n0)) and a1['branch'] == n1['branch'] == 'then' and a0['branch'] == n0['branch'] == 'else'))
han.append(('陰性B 黙つて宣どほり', b1['branch'] == 'then' and b0['branch'] == 'else' and all(x['utsuwa'] == 0 and x['soto'] == 0 for x in (b1, b0))))
han.append(('裸形の値2 = 黙つて 0側(害)', n2['branch'] == 'else' and n2['utsuwa'] == 0 and n2['soto'] == 0))
ok = sum(1 for _, v in han if v)
K.kaku_tsv(D + '/raw/40_taishou.tsv', rows, header=('label', 'harness', 'value', 'rc', 'branch', 'utsuwa_lines', 'soto_lines', 'stderr_head', 'expect'))
out = [f'# 40 ㋓ 両対照 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 路= raw/lib_run.py run()(30 と同じ)/ 番人の定義三本= disk scripts/inbox_watcher.sh sha16 {sha16}(讀むのみ)/ 走 {len(rows)}',
       '対照\t写し器\t値\trc\t枝\t報せ\t声\t期待\t頭']
out += ['\t'.join(str(x) for x in (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[8], r[7][:70])) for r in rows]
out += [('○ ' if v else '× ') + k for k, v in han]
out.append(f'判= {"通" if ok == len(han) else "★落★"}(○={ok}/{len(han)})')
out.append('対照の証: 同じ路で 陽性A は報せ欄に・陽性B は声欄に鳴る ⇒ 30 の甲 78 走の「報せ0・声0」は ★器の死ではなく器の判断★ である。')
K.kaku(D + '/raw/40_taishou.txt', '\n'.join(out)); print('\n'.join(out))
