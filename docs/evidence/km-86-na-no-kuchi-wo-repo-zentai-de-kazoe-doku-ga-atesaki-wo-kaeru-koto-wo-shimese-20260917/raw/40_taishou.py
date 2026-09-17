# -*- coding: utf-8 -*-
"""40 ㋔ 両対照(第79弾 km-86)―― ★同じ路(raw/lib_run.py run()・同じ bash・同じ env の渡し方・同じ stub PATH)★ に 陽性(必ず鳴る/変はる種)と 陰性(鳴つてはならぬ・変はつてはならぬ種)を乗せる。
陽性A(向先が変はる・⑶ path): `D="${D:-queue}"; printf TARGET "$D/x.yaml"` へ `../km86`→ 上へ / `/tmp/km86_abs`→ 根が変はる。乙形 `${D-queue}` へ 空文字 → `/x.yaml`(根そのもの)。
陽性B(tmux の誤配・⑴): `P="${P:-shogun-main:0.0}"; tmux send-keys -t "$P" Enter` へ 在らぬ名 → stub の argv に其の儘(実 tmux 0 打= 写し器が `command -v tmux` を刷り stub の path である事も併せ示す)。
陽性C(「実行された」の検出子): `eval "x=$P"` へ `$(printf INJ86)` → 向先 INJ86(★之は写し器の中の eval であり repo の器ではない・検出子が鳴り得る証★)。
陽性D(外の声の欄): `[ "$P" -eq 1 ]` へ abc → interpreter の声 1(km-84 と同じ)。
陰性: 同じ写し器に宣どほりの名 → 向先= 期待どほり・報せ 0・声 0・rc 0(「無」= 器の死ではなく器の判断の証)。各走に rc と刻を併記。"""
import os, sys, re, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from lib_run import run, mark, TMUX_FN; H = D + '/raw/40_h'; os.makedirs(H, exist_ok=True)
HEX = "| od -An -v -tx1 | tr -d ' \\n'; printf '\\n'"
def W(name, body): p = H + '/' + name; K.kaku(p, '#!/bin/bash\n# 対照の写し器(第79弾 km-86)\n' + TMUX_FN + '\n' + body); return p
hA = W('A_kou_path.sh', f'D="${{D:-queue}}"\nprintf \'TARGET=\'; printf \'%s\' "$D/x.yaml" {HEX}')
hA2 = W('A2_otsu_path.sh', f'D="${{D-queue}}"\nprintf \'TARGET=\'; printf \'%s\' "$D/x.yaml" {HEX}')
hB = W('B_tmux.sh', 'P="${P:-shogun-main:0.0}"\nprintf \'WHICH=%s\\n\' "$(command -v tmux)"\ntmux send-keys -t "$P" Enter')   # ★二走: WHICH は stdout へ(初走は stderr へ刷り己の報せ 1 を数へた= 疵)
hC = W('C_eval.sh', f'P="${{P:-kaname86}}"\neval "x=$P"\nprintf \'TARGET=\'; printf \'%s\' "$x" {HEX}')
hD = W('D_koe.sh', 'P="${P:-1}"\nif [ "$P" -eq 1 ]; then printf \'BRANCH=then\\n\'; else printf \'BRANCH=else\\n\'; fi')
rows = []
def go(label, h, N, v, expect):
    x = run(h, 'sh', N, v, D); t = time.strftime('%H:%M:%S'); tv = (x['tmux'][x['tmux'].index('-t') + 1] if '-t' in x['tmux'] else (x['targets'][0] if x['targets'] else '無'))
    rows.append((label, os.path.relpath(h, D), mark(v), x['rc'], x['branch'], x['utsuwa'], x['soto'], mark(tv), expect, t, x['head'])); return x, tv
a_neg, a_t = go('陰性A(甲 path・宣どほり)', hA, 'D', 'queue', 'queue/x.yaml・報せ0・声0')
a_up, a_ut = go('★陽性A1(甲 path・..入り)★', hA, 'D', '../km86', '../km86/x.yaml= 上へ')
a_abs, a_at = go('★陽性A2(甲 path・絶対)★', hA, 'D', '/tmp/km86_abs', '/tmp/km86_abs/x.yaml= 根が変はる')
a_emp, a_et = go('陰性A′(甲 path・空文字→既定へ)', hA, 'D', '', 'queue/x.yaml(既定へ落ちる)')
o_emp, o_et = go('★陽性A3(乙 path・空文字→素通し)★', hA2, 'D', '', '/x.yaml= 根そのもの')
o_neg, o_t = go('陰性A″(乙 path・宣どほり)', hA2, 'D', 'queue', 'queue/x.yaml')
b_neg, b_t = go('陰性B(tmux・宣どほり)', hB, 'P', 'shogun-main:0.0', '-t shogun-main:0.0・stub')
b_pos, b_pt = go('★陽性B(tmux・在らぬ名)★', hB, 'P', 'zz_no_such_km86', '-t zz_no_such_km86(stub が其の儘受ける)')
c_neg, c_t = go('陰性C(eval・宣どほり)', hC, 'P', 'kaname86', 'kaname86')
c_pos, c_pt = go('★陽性C(eval・$(…)入り)★', hC, 'P', '$(printf INJ86)', 'INJ86= ★実行された★(写し器の eval)')
d_neg, d_t = go('陰性D(-eq・値1)', hD, 'P', '1', 'then・声0')
d_pos, d_pt = go('★陽性D(-eq・abc)★', hD, 'P', 'abc', '声1(integer expression expected)')
# WHICH(stub の証)
import subprocess
env = dict(os.environ); env['PATH'] = D + '/raw/stub:' + env['PATH']; wh = subprocess.run(['/bin/bash', '-c', 'command -v tmux'], capture_output=True, text=True, env=env).stdout.strip()
han = [('陽性A1 上へ(向先に .. )', '..' in a_ut and a_ut != a_t), ('陽性A2 根が変はる(向先が / で始まる)', a_at.startswith('/') and not a_t.startswith('/')), ('陽性A3 乙の空文字= /x.yaml(根そのもの)', o_et == '/x.yaml'), ('陰性A′ 甲の空文字= 既定へ(queue/x.yaml)', a_et == 'queue/x.yaml'),
       ('陽性B 在らぬ名が stub の -t に其の儘', b_pt == 'zz_no_such_km86'), ('陽性C 検出子が鳴る(INJ86 が向先に)', c_pt == 'INJ86'), ('陽性D 声 ≥1', d_pos['soto'] >= 1),
       ('陰性 6 走 悉く 報せ0・声0・rc0・向先=宣どほり', all(x['utsuwa'] == 0 and x['soto'] == 0 and x['rc'] == 0 for x in (a_neg, o_neg, b_neg, c_neg, d_neg)) and a_t == 'queue/x.yaml' and o_t == 'queue/x.yaml' and b_t == 'shogun-main:0.0' and c_t == 'kaname86' and d_neg['branch'] == 'then'),
       ('stub の証: command -v tmux = raw/stub/tmux', wh == D + '/raw/stub/tmux')]
ok = sum(1 for _, v in han if v)
K.kaku_tsv(D + '/raw/40_taishou.tsv', rows, header=('label', 'harness', 'value', 'rc', 'branch', 'utsuwa_lines', 'soto_lines', 'target', 'expect', 'koku', 'stderr_head'))
out = [f'# 40 ㋔ 両対照 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 路= raw/lib_run.py run()(30 と同じ・stub PATH 同じ)/ 走 {len(rows)} / command -v tmux(stub PATH)= {wh}',
       '対照\t写し器\t値\trc\t枝\t報せ\t声\t向先\t期待\t刻\t頭']
out += ['\t'.join(str(x) for x in r) for r in rows]
out += [('○ ' if v else '× ') + k for k, v in han]
out.append(f'判= {"通" if ok == len(han) else "★落★"}(○={ok}/{len(han)})')
out.append('対照の証: 同じ路で 陽性A は向先が変はり・陽性B は stub が毒を其の儘 -t に受け・陽性C は検出子が鳴り・陽性D は声欄に鳴る ⇒ 30 の 5440 走の「報せ 0・声 0」は ★器の死ではなく器の判断★、且つ 30 の「★実行された★ 0」は検出子の死ではない。')
K.kaku(D + '/raw/40_taishou.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if ok == len(han) else 1)
