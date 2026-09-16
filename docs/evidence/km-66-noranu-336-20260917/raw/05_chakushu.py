# -*- coding: utf-8 -*-
"""着手便の器 05(第66弾)―― ★本弾は器で送る(前弾は手で送り疵とした)★。字数を先に印字し 300 字を超えれば送らず落ちる(字数の器は鎖の前)。inbox_write.sh(main 樹)で karo-mac へ出し、箱を content 鍵の startswith で讀み返し id・字数・逐語一致を raw/05_chakushu.txt に置く(第八の番人)。"""
import sys, os, time, subprocess, re, yaml
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'
st = open(E + '/00_start.txt', encoding='utf-8').read()
KI = re.search(r'起 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', st).group(1); SEN = re.search(r'宣 = 起 \+ (\d+) 分 = (\d\d:\d\d:\d\d) に門', st)
body = (f"[第66弾 着手便] 札 3194389eb1cfad17 受領 02:38(自己識別 date)。的=載らぬ336を★先に書いた則★で甲(員外)/乙(疵・一本ごと何故)/丙(決められぬ)へ分け、相違1の1byteをbyteで決め、己の出目が何の山かも測る。"
        f"端点: 席=起{KI[11:]}(00_start)〜門控の刻/家老=札assigned_at〜done_at。宣=起+{SEN.group(1)}分={SEN.group(2)}に門(織り込み=器4本16+紙6+凍結門便6)。束=worktree docs/evidence/km-66-noranu-336-20260917")
n = len(body); print('字数', n)
if n > 300: print(f'★{n} 字 > 300 ―― 送らず落ちる★'); sys.exit(5)
now = time.strftime('%Y-%m-%dT%H:%M:%S%z')
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', 'karo-mac', body, 'work_started', 'ashigaru-mac-1'], capture_output=True, text=True, cwd=M)
ms = yaml.safe_load(open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
hit = [m for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith('[第66弾 着手便]')]
lines = [now, f'宛 karo-mac / type work_started / from ashigaru-mac-1 / 字数 {n}(器が先に測つた・300 以下) / inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:160]}' if p.stderr.strip() else ''),
         f'箱 queue/inbox/karo-mac.yaml の entry(content 鍵・startswith) = {len(hit)} 本']
for m in hit:
    c = str(m.get('content', '')).rstrip('\n'); lines.append(f'  id {m.get("id")} / timestamp {m.get("timestamp")} / type {m.get("type")} / 箱 {len(c)} 字 / 差 {len(c) - n} / 逐語一致 {c == body} / read {m.get("read")}')
lines.append(f'本文: {body}')
K.kaku(E + '/05_chakushu.txt', '\n'.join(lines)); print(open(E + '/05_chakushu.txt', encoding='utf-8').read())
sys.exit(0 if (p.returncode == 0 and len(hit) == 1 and hit[0].get('content', '').rstrip('\n') == body) else 6)
