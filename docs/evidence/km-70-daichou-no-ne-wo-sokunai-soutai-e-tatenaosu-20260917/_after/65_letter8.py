# -*- coding: utf-8 -*-
"""追ひ便 8 の器 65(第70弾・_after/)―― 家老 06:00:41 便(msg_20260917_060041_dcd2cec3「着手便 未着」)への返し。
數は悉く器で測る: 貴箱 karo-mac.yaml の己の便(idx・read・id)/ 箱の尾の刻 / 見張り log の CONTEXT-RESET 行 / staged 数(67 の宣と比べる)。
門は 64 と同じ(宛先・字数・役職名の形・引けぬ數・先送り語)。第八の番人付。測つた生の値は 65_measure.txt へ。"""
import os, sys, re, subprocess, time, yaml, glob
B = sys.argv[1]; D = os.path.dirname(B); AFT = D + '/_after'; sys.path.insert(0, AFT); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}
meas = []
# ① 貴箱の己の便(05:29 以降)
ms = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []
mine = [(i, m) for i, m in enumerate(ms) if m.get('from') == ME and str(m.get('timestamp', '')) >= '2026-09-17T05:29']
n = len(mine); idxs = [i for i, _ in mine]; unread = sum(1 for _, m in mine if m.get('read') is False)
ids4 = '/'.join(m['id'][-4:] for _, m in mine); first_ts = mine[0][1]['timestamp'] if mine else '-'; last_ts = mine[-1][1]['timestamp'] if mine else '-'
meas.append(f'① 貴箱 {TO}.yaml 総 {len(ms)} / 己の便(from={ME}・ts>=05:29) {n} 通 / idx {idxs} / read=false {unread} / 刻 {first_ts}〜{last_ts} / id 尾4 {ids4}')
for i, m in mine: meas.append(f'   idx{i} {m["id"]} {m["timestamp"]} read={m.get("read")} 冠={str(m.get("content",""))[:14]}')
# ② 箱の尾 3 本の刻と read
tail = ms[-3:]; tail_ts = [str(m.get('timestamp', ''))[11:16] for m in tail]; tail_read = [m.get('read') for m in tail]
meas.append(f'② 箱の尾 3 本 idx {list(range(len(ms)-3, len(ms)))} 刻 {tail_ts} read {tail_read} ―― 尾の刻 < 己の便の刻 = {max(str(m.get("timestamp","")) for m in tail) < first_ts}')
# ③ 見張り log の CONTEXT-RESET(06:00 台)
log = M + f'/logs/inbox_watcher_{ME}.log'; hits = []
with open(log, encoding='utf-8', errors='replace') as fh:
    for ln, line in enumerate(fh, 1):
        if 'CONTEXT-RESET' in line and 'Sending /clear before task_assigned' in line: hits.append((ln, line.rstrip()))
last_hit = hits[-1] if hits else (0, '無'); clk = re.search(r'(\d\d:\d\d:\d\d)', last_hit[1]); clk = clk.group(1) if clk else '-'
meas.append(f'③ 見張り log {log} / 「Sending /clear before task_assigned」行 計 {len(hits)} / 最後 L{last_hit[0]} 刻 {clk} / 逐語 {last_hit[1]}')
# ④ staged 数(今)と 67 の宣
st = subprocess.run(['git', 'diff', '--cached', '--name-only', '--', D], capture_output=True, text=True, cwd=M); st_n = len([l for l in st.stdout.splitlines() if l.strip()])
gs = subprocess.run(['git', 'status', '--short', '--', D], capture_output=True, text=True, cwd=M); am = [l for l in gs.stdout.splitlines() if l[:2] == 'AM']
t67 = open(AFT + '/67_git_add.txt', encoding='utf-8').read(); m67 = re.search(r'staged (\d+) 本', t67); decl = m67.group(1) if m67 else '-'
meas.append(f'④ staged 今 {st_n}(git diff --cached --name-only rc {st.returncode}) / 67 宣 {decl} / AM {len(am)} {am}')
body = (f'[第70弾 追ひ 8・06:00便への返し] 着手便({first_ts[11:19]})・納め1〜6・追ひ7({last_ts[11:19]})の{n}通は★悉く貴箱 karo-mac.yaml に在る★(idx{min(idxs)}〜{max(idxs)}・未読{unread}・id尾 {ids4})。'
        f'箱の尾3本は{"/".join(tail_ts)}の既読ゆゑ★回転後の尾は時順に非ず★。/clear は{clk}に見張りの CONTEXT-RESET(task_assigned 型の前に送る・log L{last_hit[0]})で当席へ着いた。束 staged {st_n}(67 宣{decl}・AM{len(am)})。檢分を乞ふ')
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_')); naru = []
if TO not in ROSTER or TO in DEAD or TO == ME: naru.append('宛先')
if not (40 <= len(body) <= 300): naru.append(f'字数 {len(body)}')
if re.fullmatch(r'[a-z0-9_-]+', body): naru.append('役職名の形')
if '?' in body or ' - ' in body: naru.append('引けぬ數')
if n != 8: naru.append(f'己の便 {n}≠8')
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
if q.returncode == 10: naru.append('先送り語')
K.kaku(AFT + '/65_measure.txt', f'# 65 測つた生の値 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}\n' + '\n'.join(meas) + f'\n⑤ 字数 {len(body)} / 門 {naru or "通(0 鳴)"}')
print('字数', len(body), '門', naru or '通(0 鳴)'); print(open(AFT + '/65_measure.txt', encoding='utf-8').read())
if naru: K.kaku(AFT + '/65_letter8.txt', f'★門が鳴つた {naru}★\n' + body); sys.exit(1)
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, 'report', ME], capture_output=True, text=True, cwd=M)
ms2 = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []; hit = [m['id'] for m in ms2 if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == body]
K.kaku(AFT + '/65_letter8.txt', f'# 65 追ひ便 8 / 刻 {koku} / 字数 {len(body)} / inbox_write rc {p.returncode} / 第八の番人 {len(hit)} 本 {hit}\n{body}'); print(open(AFT + '/65_letter8.txt', encoding='utf-8').read()); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 3)
