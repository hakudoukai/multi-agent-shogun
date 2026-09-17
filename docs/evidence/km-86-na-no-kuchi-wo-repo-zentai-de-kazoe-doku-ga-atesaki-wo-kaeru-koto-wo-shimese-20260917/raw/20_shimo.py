# -*- coding: utf-8 -*-
"""20 ㋑ 名の口が下流で何に成るか(第79弾 km-86・★二走★)―― 10 が 名 と分けた口(10_na.tsv)の (file, 名) ごとに、同 file の ★註でない行★ で名を参照する行を悉く拾ひ、
lib_yomite(10 と同じ則)で ⑴ tmux target / ⑵ session 名 / ⑶ path・dir・file / ⑷ topic・宛先 role / ⑸ 比較の左右 / 數 / 伝(讀まぬ) / 口 / 他 に分ける。
★二走で足した二つ(初走 .first の疵)・三走= lib_yomite の則を締めた(代入を比較と誤る/子器へ渡す env を path と誤る/他file でも別名を追ふ)・四走= 他言語の同名は讀手でなく別口★: (a) shell の一段の派生= `x="…$N…"` / `local x=$(… $N …)` の x を別名とし、x を参照する行も讀手に数へる(欄 all_matches に「派」を付す)。
  (b) 同 file に害の讀手が無い (file,名) は ★根A の他 file★ を直名で探し、其処の讀手を「他file:path」で挙げる(初走は同 file のみ= ER_PANE_TARGET 等 source 先で讀まれる名を「讀まれぬ」と誤つた)。
一行に二類以上が当たれば ⑴>⑵>⑷>⑶>⑸>數>伝>口>他 の順で一類に落とし、落とした數(重なり)を刷る。★讀まれぬ口★= 同 file にも他 file にも口の行の外に参照が無い(file,名)。
各類に file:行 の実例を ≥1 本挙げる(器が挙げる・手で選ばぬ)。scope_out の三 file も ★歩く★(毒当てを除くのは 30)。"""
import os, sys, re, time, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from lib_yomite import classes_sh, classes_py; M = '/Users/momizimac/multi-agent-shogun'
na = [l.split('\t') for l in open(D + '/raw/10_na.tsv', encoding='utf-8').read().split('\n')[1:] if l]
rootA = [l for l in open(D + '/raw/00_rootA.txt', encoding='utf-8').read().split('\n') if l]
SRC = {f: open(M + '/' + f, encoding='utf-8', errors='replace').read().split('\n') for f in rootA}
keys = sorted({(r[0], r[2]) for r in na}); port_lines = collections.defaultdict(set)
for r in na: port_lines[(r[0], r[2])].add(int(r[1]))
PRI = ['⑴', '⑵', '⑷', '⑶', '⑸', '數', '伝', '口', '他']; HARM = ('⑴', '⑵', '⑶', '⑷', '⑸')
def aliases_sh(L, N):
    a = set()
    for l in L:
        if l.lstrip().startswith('#'): continue
        m = re.match(r'^\s*(?:local\s+|export\s+|declare\s+[-a-zA-Z]+\s+|readonly\s+)?([A-Za-z_][A-Za-z0-9_]*)=', l)
        if m and m.group(1) != N and re.search(r'\$\{?' + re.escape(N) + r'(?![A-Za-z0-9_])', l): a.add(m.group(1))
    return a
def aliases_py(L, N):
    a = set()
    for l in L:
        m = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*.*os\.(?:environ\.get|getenv|environ\[)\(?\s*[\'"]' + re.escape(N) + r'[\'"]', l)
        if m: a.add(m.group(1))
    return a
def scan(f, N, L, kind, with_alias):
    """file f の行を N(と派生)で分類。返り= [(f, line, N, one, all_matches, verbatim)]、集計 Counter。"""
    al = (aliases_sh(L, N) if kind == 'sh' else aliases_py(L, N)) if with_alias else set(); out = []; cs = collections.Counter(); kas = 0
    for i, l in enumerate(L, 1):
        c, s = classes_sh(N, l) if kind == 'sh' else classes_py(N, al, l); tag = ''
        if not c and kind == 'sh' and al:
            for x in al:
                c2, s2 = classes_sh(x, l)
                if c2 & set(HARM) | (c2 & {'數'}): c |= c2; s = s2; tag = '派' + x; break
        if not c: continue
        one = next(p for p in PRI if p in c); harm = {x for x in c if x in HARM}
        if len(harm) > 1: kas += 1
        if i in port_lines.get((f, N), set()) and one in ('伝', '他'): one = '口'
        out.append((f, i, N, one, '+'.join(sorted(c, key=PRI.index)) + (' ' + tag if tag else ''), s.strip())); cs[one] += 1
    return out, cs, kas, al
rows = []; kasanari = 0; per = {}; cross = {}; nalias = 0; douimei = collections.defaultdict(list)
for f, N in keys:
    kind = 'py' if f.endswith('.py') else 'sh'; o, cs, kas, al = scan(f, N, SRC[f], kind, True); rows += o; kasanari += kas; per[(f, N)] = cs; nalias += len(al)
    if not any(cs[x] for x in HARM + ('數',)):
        hits = []
        for g in rootA:
            if g == f: continue
            gk = 'py' if g.endswith('.py') else 'sh'
            if not any(re.search(r'(?<![A-Za-z0-9_])' + re.escape(N) + r'(?![A-Za-z0-9_])', l) for l in SRC[g]): continue
            if gk != kind: douimei[(f, N)].append(g); continue   # ★四走: 言語が違ふ file の同名は「己の口で受ける別の口」= 此の口の讀手ではない(初〜三走は讀手に混ぜた・510 行)
            o2, cs2, _, _ = scan(g, N, SRC[g], gk, True)   # ★三走: 他file でも一段の別名を追ふ(PANE_TARGET="$ER_PANE_TARGET" → tmux -t "$PANE_TARGET")
            h2 = [r for r in o2 if r[3] in HARM + ('數',)]
            if h2: hits.append((g, h2))
        if hits: cross[(f, N)] = hits
K.kaku_tsv(D + '/raw/20_shimo.tsv', rows, header=('file', 'line', 'name', 'class', 'all_matches', 'verbatim'))
xrows = [(f, N, g, r[1], r[3], r[4], r[5]) for (f, N), hits in cross.items() for g, h2 in hits for r in h2]
K.kaku_tsv(D + '/raw/20_cross.tsv', xrows, header=('port_file', 'name', 'reader_file', 'line', 'class', 'all_matches', 'verbatim'))
tot = collections.Counter(r[3] for r in rows); harm_rows = [r for r in rows if r[3] in HARM]; hasei = sum(1 for r in rows if '派' in r[4])
yomarenu = []; den_nomi = []; kind_of_key = collections.Counter()
for k, cs in per.items():
    rd = {x for x in cs if x in HARM + ('數',)}
    if rd: kind_of_key['+'.join(sorted(rd, key=PRI.index))] += 1
    elif k in cross: kind_of_key['他file で讀む'] += 1
    elif k in douimei: kind_of_key['同名の別口(他言語)のみ'] += 1
    elif cs['伝'] or cs['他']: den_nomi.append(k); kind_of_key['伝/他のみ'] += 1
    else: yomarenu.append(k); kind_of_key['★讀まれぬ(口のみ・他file にも無)★'] += 1
xt = collections.Counter(r[4] for r in xrows)
SO = {'scripts/pane_enter_watcher_supervisor.sh', 'scripts/lib/detect_stale.sh', 'scripts/watchdogs/enter_restart_commander_watchdog.sh'}
so_rows = [r for r in harm_rows if r[0] in SO]; so_x = [r for r in xrows if r[0] in SO or r[2] in SO]
ex = {}
for c in HARM:
    rr = [r for r in rows if r[3] == c and '派' not in r[4]] or [r for r in rows if r[3] == c]; ex[c] = rr[0] if rr else None
    if not ex[c]:
        xr = [r for r in xrows if r[4] == c]; ex[c] = (xr[0][2], xr[0][3], xr[0][1], c, xr[0][5], xr[0][6]) if xr else None
out = [f'# 20 ㋑ 名の口の下流(二走) / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 名の口 {len(na)} 口 → (file,名) {len(keys)} 組 / 参照行 {len(rows)}(註を除く・派生の行 {hasei}・別名 {nalias})/ 他file の讀手 行 {len(xrows)}(組 {len(cross)})',
       '則: lib_yomite.py(10 と同じ・逐語は其の file)。一行一類= ⑴>⑵>⑷>⑶>⑸>數>伝>口>他 の優先。派= 一段の別名(x="…$N…")経由。他file= 同 file に害の讀手が無い組を根A の他 file で直名で探した。',
       f'★害の類(同 file・行): ⑴ tmux target {tot["⑴"]} / ⑵ session 名 {tot["⑵"]} / ⑶ path・dir・file {tot["⑶"]} / ⑷ topic・宛先 role {tot["⑷"]} / ⑸ 比較 {tot["⑸"]} ＝ 害の行 {len(harm_rows)}★ ／ 數 {tot["數"]} / 伝 {tot["伝"]} / 口 {tot["口"]} / 他 {tot["他"]} ／ 和 {sum(tot.values())} = 参照行 {len(rows)}',
       f'★害の類(他file・行): ⑴ {xt["⑴"]} / ⑵ {xt["⑵"]} / ⑶ {xt["⑶"]} / ⑷ {xt["⑷"]} / ⑸ {xt["⑸"]} / 數 {xt["數"]} ＝ {len(xrows)}★',
       f'排他性: 一行に害の類が二つ以上当たつた行 = {kasanari}(優先順で一類へ落とした)',
       f'同名の別口(他言語・讀手に数へぬ・四走): 組 {len(douimei)} / file 延べ {sum(len(v) for v in douimei.values())}(例: ' + ' / '.join(f'{k[0].split("/")[-1]}:{k[1]}→{len(v)}file' for k, v in list(douimei.items())[:6]) + ')',
       '★(file,名) ごとの讀手の組合せ: ' + ' / '.join(f'{k} {v}' for k, v in sorted(kind_of_key.items(), key=lambda x: -x[1])) + '★',
       f'★讀まれぬ口(宣のみ・同 file にも他 file にも参照 0)= {len(yomarenu)} 組★: ' + (' / '.join(f'{f.split("/")[-1]}:{N}' for f, N in yomarenu) or '0'),
       f'伝/他のみ(讀まぬが表示・export・子器へ渡す・他file にも害の讀手無し)= {len(den_nomi)} 組: ' + (' / '.join(f'{f.split("/")[-1]}:{N}' for f, N in den_nomi[:60]) + (' …' if len(den_nomi) > 60 else '')),
       f'scope_out 三 file の害の行(歩いた・30 で毒当てを除く)= 同file {len(so_rows)} 行(' + ' / '.join(f'{f.split("/")[-1]} {sum(1 for r in so_rows if r[0] == f)}' for f in sorted(SO)) + f')・他file 経由 {len(so_x)} 行',
       '## 各類の実例(器が最初に挙げた一本・file:行 名 | 逐語)']
out += [f'  {c} {ex[c][0]}:{ex[c][1]}\t{ex[c][2]}\t{ex[c][4]}\t| {ex[c][5][:140]}' if ex[c] else f'  {c} ★実例無し(0 行)★' for c in HARM]
out.append('## 他file の讀手(口の file→讀手の file:行 名 類 | 逐語)'); out += [f'  {r[0].split("/")[-1]} → {r[2]}:{r[3]}\t{r[1]}\t{r[4]}\t{r[5]}\t| {r[6][:130]}' for r in xrows] or ['  0']
out.append('## 害の行 全行(同 file・file:行 名 類 当たつた類 | 逐語)'); out += [f'  {r[0]}:{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}\t| {r[5][:150]}' for r in harm_rows]
out.append('## (file,名) ごと(讀手の類と行)')
for (f, N), cs in sorted(per.items()):
    rl = [r for r in rows if r[0] == f and r[2] == N and r[3] in HARM + ('數',)]
    out.append(f'  {f}\t{N}\t害 {len(rl)}\t' + ' '.join(f'{r[3]}L{r[1]}' for r in rl[:12]) + (' …' if len(rl) > 12 else '') + f'\t伝 {cs["伝"]} 口 {cs["口"]} 他 {cs["他"]}' + (f'\t他file {sum(len(h) for g, h in cross[(f, N)])}' if (f, N) in cross else ''))
K.kaku(D + '/raw/20_shimo.txt', '\n'.join(out)); print('\n'.join(out[:16])); print('...'); print('\n'.join(out[16:16 + min(40, len(xrows))]))
