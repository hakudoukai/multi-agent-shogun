# -*- coding: utf-8 -*-
"""着手便の器 05(第67弾・66 の形)―― 字数を先に印字し 300 字を超えれば送らず落ちる。inbox_write.sh(main 樹)で karo-mac へ出し、箱を content 鍵の startswith で讀み返し id・字数・逐語一致を raw/05_chakushu.txt に置く(第八の番人)。"""
import sys, os, time, subprocess, re, yaml
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'
st = open(E + '/00_start.txt', encoding='utf-8').read()
KI = re.search(r'起 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', st).group(1); SEN = re.search(r'宣 = 起 \+ (\d+) 分 = (\d\d:\d\d:\d\d) に門', st)
body = (f"[第67弾 着手便] 札 e638748eb93c5f8a 受領 03:09(自己識別 date)。的=㋐門の後に書く病を出来なくする器(歩哨ns+錠)を束に建て㋑66の束で1本2Bを裁き㋒陽7陰4零1を器越しに通し㋓乙1 23+乙5 3を讀手の落ちる行番号で現物へ。"
        f"端点: 席=起{KI[11:]}(00_start)〜門控の刻/家老=札assigned_at 03:06:00〜done_at。宣=起+{SEN.group(1)}分={SEN.group(2)}に門(66實14.7×器6/4+對照4)。束=worktree docs/evidence/km-67-mon-no-ato-20260917")
n = len(body); print('字数', n)
if n > 300: print(f'★{n} 字 > 300 ―― 送らず落ちる★'); sys.exit(5)
now = time.strftime('%Y-%m-%dT%H:%M:%S%z')
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', 'karo-mac', body, 'work_started', 'ashigaru-mac-1'], capture_output=True, text=True, cwd=M)
ms = yaml.safe_load(open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
hit = [m for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith('[第67弾 着手便]')]
lines = [now, f'宛 karo-mac / type work_started / from ashigaru-mac-1 / 字数 {n}(器が先に測つた・300 以下) / inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:160]}' if p.stderr.strip() else ''),
         f'箱 queue/inbox/karo-mac.yaml の entry(content 鍵・startswith) = {len(hit)} 本']
for m in hit:
    c = str(m.get('content', '')).rstrip('\n'); lines.append(f'  id {m.get("id")} / timestamp {m.get("timestamp")} / type {m.get("type")} / 箱 {len(c)} 字 / 差 {len(c) - n} / 逐語一致 {c == body} / read {m.get("read")}')
lines.append(f'本文: {body}')
K.kaku(E + '/05_chakushu.txt', '\n'.join(lines)); print(open(E + '/05_chakushu.txt', encoding='utf-8').read())
sys.exit(0 if (p.returncode == 0 and len(hit) == 1 and hit[0].get('content', '').rstrip('\n') == body) else 6)
