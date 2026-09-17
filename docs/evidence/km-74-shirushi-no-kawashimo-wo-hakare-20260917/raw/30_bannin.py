# -*- coding: utf-8 -*-
"""30 閾の番人(㋒)―― 凍結版 scripts/ で「閾」を刷る file と其の番人の行(倒す・値を刷る・乙門)を数へ、20箇所6file と照らし、己の ㋓/㋔ が当たる箇所を名指す。40 = _th_say が $( ) で捕られぬ事。"""
import sys, re, subprocess, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; C = '6dbe09e6'
def show(p): return subprocess.run(['git', 'show', f'{C}:{p}'], capture_output=True, text=True, cwd=M).stdout.split('\n')
files = [x.replace(C + ':', '') for x in subprocess.run(['git', 'grep', '-l', '閾', C, '--', 'scripts'], capture_output=True, text=True, cwd=M).stdout.split() if x]
rows = []; out = [f'# 30 閾の番人 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 凍結点 {C} / 母數= git grep -l 閾 {C} -- scripts = {len(files)} file']
out.append('file | 閾の行 | 倒す行(既定へ) | 値を刷る行(「…」) | 乙門(*␊*) | 乙置換(_ft_vp) | 番人か')
tot4 = 0; tot6 = 0
for p in sorted(files):
    src = show(p); n_ik = sum(1 for l in src if '閾' in l); taosu = [i for i, l in enumerate(src, 1) if re.search(r'既定.*倒す|倒す.*既定|既定 .* を用ゐる', l)]
    suru = [i for i, l in enumerate(src, 1) if re.search(r'閾.*「\$\{', l)]; otsu = [i for i, l in enumerate(src, 1) if '*␊*' in l]; vp = [i for i, l in enumerate(src, 1) if '_ft_vp=' in l]
    ban = len(taosu) > 0; tot6 += len(taosu); tot4 += len(taosu) if p in ('scripts/inbox_watcher.sh', 'scripts/watchdogs/enter_restart_common_watchdog.sh', 'scripts/agent_health_check.sh', 'scripts/checks/context_usage_warn.sh') else 0
    out.append(f'{p} | {n_ik} | {len(taosu)} {taosu} | {len(suru)} {suru} | {len(otsu)} {otsu} | {len(vp)} {vp} | {"番人" if ban else "註/表示のみ"}'); rows.append((p, n_ik, len(taosu), len(suru), len(otsu), len(vp), '番人' if ban else '否'))
out.append(f'=== 20箇所6file との照らし === 番人を持つ file= {sum(1 for r in rows if r[6] == "番人")} / 倒す行の和= 四器 {tot4}・番人 6 file {tot6}。★裁 323062⑷ の「20箇所」は四器の倒す行の和 20 と一致し、「6file」は dasumae_gate・gate4 を足した数と一致する ―― 然れど 6 file の倒す行の和は {tot6} であり 20 ではない。裁の 20 と 6 の ★定義は己の器では一つに閉ぢぬ★(家老 km-74 紙 95 行目も「閉じて居らぬ」)。二つの数を並べて置く。')
out.append('=== ㋔(印の曖昧性)が当たる箇所 === 値を刷る行の内 ★乙置換を経て刷る 4 箇所★(watcher:164 / watchdog:115 / health:125 / ctxwarn:71)―― 其の直前の乙門(161/112/122/68)が「入力に既に ␊␍␉ が在れば値を刷らず倒す」で曖昧を消して居る(裁 323980⑵・己の ㋔ 12/20 が産んだ一条)。∴ 四器では ㋔ は ★閉ぢた★。')
out.append('  ★乙が未だ当たらぬ 2 箇所★= dasumae_gate:59 `「${raw}」`・gate4:92 `「${raw}」` ―― 乙置換 0・乙門 0 ゆゑ ★行注入(\\n を含む閾)がそのまま stderr へ出る★。家老が枝で当てる順は ★此の 2 箇所を先★(番人の残り)。')
out.append('=== ㋓(byte 切り)が当たる箇所 === 値を刷る 6 箇所 悉く(上 4 + dasumae:59 + gate4:92)―― 但し 20 の戸籍で下流の byte 切りは 0 ゆゑ ★潜在★。四器の中の切り 4 本(20 の戸籍: watcher:439/744・watchdog:223・health:361)は閾の値ではない。')
# 40: _th_say が $( ) で捕られぬ(f-string に backslash を置けぬゆゑ先に数へる)
CAP = re.compile(r'\$\([^)]*_th_say'); parts = []
for p in ('scripts/inbox_watcher.sh', 'scripts/watchdogs/enter_restart_common_watchdog.sh', 'scripts/agent_health_check.sh', 'scripts/checks/context_usage_warn.sh'):
    src = show(p); c = sum(1 for l in src if CAP.search(l)); t = sum(1 for l in src if '$(' in l); parts.append(f'{p.split("/")[-1]} 捕り {c}(陽性対照 $( 総 {t})')
out.append('=== 40 印が器の中で値に戻る路 === _th_say を $( ) で捕る行(四器)= ' + ' / '.join(parts) + ' ―― 0 本。印は stderr へ出た後、同じ process の中で値に戻らぬ。watchdog の log() は tee で stdout にも出す(service の StandardOutput= append)が讀む器は 10 で 0。')
K.kaku(D + '/raw/30_bannin.txt', '\n'.join(out)); K.kaku_tsv(D + '/raw/30_bannin.tsv', rows, ['file', '閾行', '倒す', '値刷', '乙門', '乙置換', '番人']); print('\n'.join(out))
