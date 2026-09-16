# -*- coding: utf-8 -*-
"""着手便の器 05(第56弾・第55弾を写した ―― ★弾番は束の名から・起と宣は 00_start から讀む(手で打たぬ)★・字数を書く前に測り、超えれば送らずに .first へ残して落ちる)。work_started + ETA を karo-mac へ inbox_write.sh で出し、
箱を content 鍵の startswith で讀み返して id と字数と逐語一致を 05_chakushu.txt に残す(第八の番人)。門の前ゆゑ臺帳の項。家老の箱へは inbox_write 以外 0 byte(read の反転 0)。"""
import sys, os, re, time, subprocess, yaml
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
RN = re.search(r'_km-(\d+)-', E).group(1)
st = open(E + '/00_start.txt', encoding='utf-8').read()
ki = re.search(r'起 \d{4}-\d\d-\d\dT(\d\d:\d\d:\d\d)', st).group(1); sen = re.search(r'起 \+ (\d+) 分 = (\d\d:\d\d:\d\d) に門', st); tsha = re.search(r'task sha16 ([0-9a-f]{16})', st).group(1)
body = (f'[第{RN}弾 着手便] ashigaru-mac-1 work_started 起 {ki} / 札 {tsha} 5521B 68行 受 / ★宣 ETA 起+{sen.group(1)}分={sen.group(2)} に門★(r54 宣25 實13 / r55 宣20 實4084=停止 ∴ 三問ゆゑ 40)/ 手順: 問一 22本を裁 310228⑵ で ㋐門自身/㋑其れ以外 に分け和 36096 を閉ぢ・30 の HH:MM:SS と日付込み 31 を並べる→問二 sha で歩く器を束の中に建て三束で走らせ 家老の 6/6・母數 234 と突き合はす→問三「知つて居て直さなかつた」を器で数へる→門→便。門の後の出目は根の外 _after/ へ')
n = len(body); print('字数', n)
if n > 300:
    K.kaku(E + '/05_chakushu.first.txt', f'字数 {n} > 300 ∴ 送らず\n{body}'); print('★超過 ―― 送らず★'); sys.exit(1)
p = subprocess.run(['bash', 'scripts/inbox_write.sh', 'karo-mac', body, 'report', 'ashigaru-mac-1'], capture_output=True, text=True)
now = time.strftime('%Y-%m-%dT%H:%M:%S%z')
ms = yaml.safe_load(open('queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
ids = [m['id'] for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith(f'[第{RN}弾 着手便]')]
byid = {m['id']: str(m.get('content', '')) for m in ms}; c = byid.get(ids[0], '').rstrip('\n') if ids else ''
K.kaku(E + '/05_chakushu.txt', f'{now}\n宛 karo-mac / type report / from ashigaru-mac-1 / 着手便({n} 字) inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:160]}' if p.stderr.strip() else '') + f'\n箱の entry(content 鍵・startswith) = {len(ids)} 本: {ids}\n第八の番人: 箱 {len(c)} / 05 {n} / 差 {len(c) - n} / 逐語一致 {c == body}\n本文: {body}')
print(open(E + '/05_chakushu.txt', encoding='utf-8').read())
