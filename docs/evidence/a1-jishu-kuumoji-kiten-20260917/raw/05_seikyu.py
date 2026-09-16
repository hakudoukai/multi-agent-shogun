# -*- coding: utf-8 -*-
"""05 弾を請ふ便(二走目・一走目は 301 字で己の門に鳴つた→ .first)(自主束・おめざめくん便 06:32 への応へ)。數は器で測る: 契約 file の有無 / 板の自分owner未完行 / 己の DB 送信器の有無(agent_letter.py ROLE_PC)。門は 65 と同じ。第八の番人付。"""
import os, sys, re, subprocess, time, yaml, glob
B = sys.argv[1]; RAW = B + '/raw'; sys.path.insert(0, RAW); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}
meas = []
gf = sorted(glob.glob(M + '/queue/goals/*')); mine = [p for p in gf if os.path.basename(p).startswith(ME) and not os.path.isdir(p)]
meas.append(f'① 契約 file queue/goals/{ME}*.yaml(活きた物・done/ を除く) {len(mine)} 本 {[os.path.basename(p) for p in mine]} / dir 直下 総 {len(gf)}')
bd = subprocess.run([os.path.expanduser('~/bin/sb'), 'read', 'board', '60'], capture_output=True, text=True); blocks = [b for b in bd.stdout.split('  ' + '-' * 60) if 'id:' in b]
own = [b for b in blocks if re.search(r'owner_role: ' + re.escape(ME) + r'\s*$', b, re.M) and not re.search(r'status: (done|completed|cancelled)', b)]
meas.append(f'② 板 sb read board 60 rc {bd.returncode} / 頭 {bd.stdout.splitlines()[0] if bd.stdout else "-"} / blocks {len(blocks)} / owner_role={ME} 未完 {len(own)}')
src = open(os.path.expanduser('~/bin/agent_letter.py'), encoding='utf-8').read(); has = bool(re.search(r'"' + re.escape(ME) + r'"\s*:', src))
meas.append(f'③ ~/bin/agent_letter.py の ROLE_PC に "{ME}" {"在" if has else "無"}(DB 便の器 {"有" if has else "無"})')
body = (f'[專任1→家老mac・弾を請ふ] おめざめくん便(06:32)に応へ測つた: 契約 file {len(mine)}本・板 owner=專任1 未完 {len(own)}行・DB便の器は當席に無(agent_letter ROLE_PC に無∴本便は箱で代へる)。第70弾は納め済(追ひ8 迄)・檢分待ち。'
        f'★残弾0ゆゑ第71弾を請ふ★。候補: ⑴門の基点の口が空文字("")の時の挙動(便5で未測)を讀取のみで測る ⑵`s[:1] in "AM"` 型(空文字で True・66)を己の束の器で悉皆。着手迄 ⑴を自主束 docs/evidence/a1-jishu-kuumoji-kiten-20260917/ で讀取のみ進める')
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_')); naru = []
if TO not in ROSTER or TO in DEAD or TO == ME: naru.append('宛先')
if not (40 <= len(body) <= 300): naru.append(f'字数 {len(body)}')
if '?' in body: naru.append('引けぬ數')
q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=body.encode('utf-8'), capture_output=True)
if q.returncode == 10: naru.append('先送り語')
K.kaku(RAW + '/05_measure.txt', f'# 05 測つた生の値 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}\n' + '\n'.join(meas) + f'\n④ 字数 {len(body)} / 門 {naru or "通(0 鳴)"}')
print(open(RAW + '/05_measure.txt', encoding='utf-8').read())
if naru: K.kaku(RAW + '/05_seikyu.txt', f'★門が鳴つた {naru}★\n' + body); sys.exit(1)
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, body, 'report', ME], capture_output=True, text=True, cwd=M)
ms2 = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []; hit = [m['id'] for m in ms2 if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == body]
K.kaku(RAW + '/05_seikyu.txt', f'# 05 弾を請ふ便 / 刻 {koku} / 字数 {len(body)} / inbox_write rc {p.returncode} / 第八の番人 {len(hit)} 本 {hit}\n{body}'); print(open(RAW + '/05_seikyu.txt', encoding='utf-8').read()); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 3)
