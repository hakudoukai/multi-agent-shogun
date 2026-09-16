# -*- coding: utf-8 -*-
"""追ひ便の器 64(第56弾・第55弾 65 を写した ―― 96(31 日付込み・根の外)の出目を便 7 として karo-mac へ出し <束>_after/63b_sent.txt に記録する)。DRY=1 なら送らず。未宣の産物は無い筈(悉く臺帳の註に名で宣した)―― 有れば 96 の「新」に見える。"""
import sys, os, re, time, subprocess, yaml
B = sys.argv[1]; E = B + '_evidence/raw'; OUT = B + '_after'; sys.path.insert(0, E); import kaki as K
RN = re.search(r'_km-(\d+)-', B).group(1); DRY = bool(os.environ.get('DRY'))
def rd(p, alt): return open(p, encoding='utf-8').read() if os.path.isfile(p) else alt
t96 = rd(OUT + '/96_after_send.txt', '一致 ★0★ / 相違 0 / 実体無 0 / 読めぬ行 0  (母數 0)\nとの差: 新 0 / 変 0 / 消 0\n秒 > 秒★): 0 本 / byte 和 0\n(第55弾 97 の定義): 0 本 / byte 和 0 ―― 差 = 門控と同じ秒に生れた 0 本 / 0 B')
j1 = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', t96); dif = re.search(r'との差: 新 (\d+) / 変 (\d+) / 消 (\d+)', t96)
a = re.search(r'秒 > 秒★\): (\d+) 本 / byte 和 (\d+)', t96); n = re.search(r'\(第55弾 97 の定義\): (\d+) 本 / byte 和 (\d+) ―― 差 = 門控と同じ秒に生れた (\d+) 本 / (\d+) B', t96)
body = f"[第{RN}弾 追ひ便 7] ★門の後に根(_evidence)へ書いた byte(96・日付込み)= 秒>秒 {a.group(1)}本/{a.group(2)}B・ns>秒.000 {n.group(1)}本/{n.group(2)}B(=門控と同じ秒の門自身 {n.group(3)}本/{n.group(4)}B)★ 99→96 新{dif.group(1)}/変{dif.group(2)}/消{dif.group(3)}(変 0 = 項へ 0 byte)・臺帳の項 照合 {j1.group(1)}/{j1.group(2)}/{j1.group(3)}/{j1.group(4)}。門の後の出目(99/62/63/96/64/63b)は悉く根の外 <束>_after/(臺帳の註に名で宣した)。此の 63b と 64 の出目 3 本と便 7 と札の印は家老が測る"
print('字数', len(body)); assert len(body) <= 300, f'便7 {len(body)} 字'
if DRY: print('DRY'); print(body); sys.exit(0)
now = time.strftime('%Y-%m-%dT%H:%M:%S%z')
p = subprocess.run(['bash', 'scripts/inbox_write.sh', 'karo-mac', body, 'report', 'ashigaru-mac-1'], capture_output=True, text=True)
ms = yaml.safe_load(open('queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
ids = [m['id'] for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith(f'[第{RN}弾 追ひ便 7]')]
byid = {m['id']: str(m.get('content', '')) for m in ms}; c = byid.get(ids[0], '').rstrip('\n') if ids else ''
K.kaku(OUT + '/63b_sent.txt', f'{now}\n宛 karo-mac / type report / from ashigaru-mac-1 / 便 7({len(body)} 字) inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else '') + f'\n箱の entry(content 鍵・startswith) = {len(ids)} 本: {ids}\n第八の番人: 箱 {len(c)} / 64 {len(body)} / 差 {len(c) - len(body)} / 逐語一致 {c == body}\n本文: {body}\n★此の 63b・64 の出目 3 本(根の外 _after/)・便 7・札の印 = 本弾の器の誰も測らぬ。家老が測る。根(_evidence)は 96 が最後に見た。★')
print(open(OUT + '/63b_sent.txt', encoding='utf-8').read())
