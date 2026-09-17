# -*- coding: utf-8 -*-
"""20 byte 切りの戸籍(㋐)―― 凍結版 四器の中と、10 で挙げた讀み手(0 本)と、起動器の中の byte 切りの形を数へる。零には四札。"""
import os, sys, re, subprocess, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; C = '6dbe09e6'; H = os.path.expanduser('~')
PAT = re.compile(r"cut -b|cut -c|printf ['\"]?%[-]?\.[0-9]|substr\(|\$\{[A-Za-z_]+:[0-9]+:[0-9]+\}|\$\{[A-Za-z_]+:0:|head -c|LC_ALL=C|LANG=C|\[:[0-9]+\]")
MATO = {'watcher': 'scripts/inbox_watcher.sh', 'watchdog': 'scripts/watchdogs/enter_restart_common_watchdog.sh', 'health': 'scripts/agent_health_check.sh', 'ctxwarn': 'scripts/checks/context_usage_warn.sh'}
rows = []; out = [f'# 20 byte 切りの戸籍 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 凍結点 {C} / 形= cut -b・cut -c・printf %.N・substr(・${{v:0:N}}・head -c・LC_ALL=C・[:N](python 切片)']
out.append('=== ⑴ 四器の中(凍結版・行番号は git show) ===')
for k, p in MATO.items():
    src = subprocess.run(['git', 'show', f'{C}:{p}'], capture_output=True, text=True, cwd=M).stdout.split('\n'); hits = [(i, l) for i, l in enumerate(src, 1) if PAT.search(l)]
    th = [i for i, l in enumerate(src, 1) if '_th_say' in l]
    out.append(f'  {k:9s} {p}: byte 切り {len(hits)} 本 / 母數 {len(src)} 行 / _th_say の行 {len(th)}: {th}')
    for i, l in hits: out.append(f'    :{i}: {l.strip()[:130]}  ← _th_say の行か= {"是" if "_th_say" in l else "否(別の値)"}'); rows.append((k, p, i, 'th_say' if '_th_say' in l else 'other', l.strip()[:80]))
out.append('=== ⑵ 讀み手(10 の戸籍で 0 本)の中の byte 切り= ★讀み手が 0 ゆゑ 0(母數 0)★ ―― 「無い」ではなく「讀む器が無い」')
bt = H + '/hermes-departments-mac/bin/boot-mac-fleet.sh'; t = open(bt, encoding='utf-8', errors='replace').read().split('\n'); n = sum(1 for l in t if PAT.search(l))
out.append(f'=== ⑶ Mac 起動器(書き手・讀むのみ): byte 切り {n} 本 / 母數 {len(t)} 行 ===')
o = subprocess.run(f"git grep -c -E 'cut -c|substr\\(' {C} -- scripts", shell=True, capture_output=True, text=True, cwd=M).stdout.strip().split('\n')
out.append(f'=== ⑷ ★陽性対照★ 同じ形を凍結版 scripts/ 全体へ(git grep -c)= {len([x for x in o if x])} file: ' + ' / '.join(x.replace(C + ":", "") for x in o if x) + ' ―― 器は在る物を見得る')
out.append('=== ⑸ 己の第73弾 raw/40 の切り(cut -c1-N・${V:0:N}・printf %.N)は ★己の探り針★ であつて四器の下流の器ではない ―― 18/66 の割れは「切れば割れる」の實證であり「現に切る器が在る」の證ではない')
out.append(f'=== ∴ ㋐ の答 === 四器が刷る _th_say の行の下流に byte 切りは ★現に 0 本★(讀み手 0・起動器 0)。四器の中の切りは ★{len(rows)} 本★(器が数へた・上 ⑴ の行)で、悉く _th_say の行ではなく別の値(uuid 切片・startup_prompt・topic・session id)。★己の初版の結びは頭で 2 と書いた ―― 器の数 {len(rows)} に直した(書く前に問へ)。★∴ ㋓ は「讀み手が現れた時に開く穴」(潜在)であり、凍結版では ★閉ぢて居る★ ―― 但し人の端末と Claude(hook の stderr)は器の外ゆゑ数へて居らぬ。')
K.kaku(D + '/raw/20_bytegiri.txt', '\n'.join(out)); K.kaku_tsv(D + '/raw/20_bytegiri.tsv', rows, ['器', 'path', '行', '種', '逐語']); print('\n'.join(out))
