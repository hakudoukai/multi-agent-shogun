# -*- coding: utf-8 -*-
"""添状の器 62(第71弾 補・★臺帳より先に書いた・走らせるのは門の後・出目は根の外 _after/★)。便 3(各 300 字以内・字数を先に印字)を karo-mac へ inbox_write.sh で出す(便 3 = 疵と代送依頼)。
数は _after/60_gate_rcs.txt と紙から regex で引く(手写しでない)。門(05 と同じ)が一つでも鳴れば一通も送らぬ。DRY=1 なら送らず印も 63 も書かぬ。第八の番人付。端点 = 納め最終便(3/3)を inbox_write.sh へ渡す直前の date 刻(着手便 05 の宣の定義と同じ)。"""
import sys, os, re, time, subprocess, hashlib, yaml, glob, datetime as dt
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; OUT = D + '/_after'; os.makedirs(OUT, exist_ok=True); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; DRY = bool(os.environ.get('DRY')); ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}; KM = os.path.basename(D)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else 'x' * 16
def rd(p, alt=''): return open(p, encoding='utf-8').read() if os.path.isfile(p) else alt
def num(pat, txt, alt='?'): m = re.search(pat, txt); return m.group(1) if m else alt
def P(s): return dt.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')
P_, MN, G = sha16(B + '.md'), sha16(B + '_manifest.txt'), sha16(B + '_gate.txt'); PL = str(rd(B + '.md').count('\n')); PB = os.path.getsize(B + '.md') if os.path.isfile(B + '.md') else 0
items = sum(1 for l in rd(B + '_manifest.txt').split('\n') if l.startswith('path='))
rcs = rd(OUT + '/60_gate_rcs.txt', '③ main | 渡した 0 | rc 9 | 札 0\n③ all | 渡した 0 | rc 9 | 札 0\n③ nobase | 渡した 0 | rc 9 | 札 0')
g = {k: re.search(r'^③ ' + k + r' \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M) for k in ('main', 'all', 'nobase')}
KI = rd(E + '/05_chakushu_koku.txt').strip(); SEN = 4; sen_clock = P(KI) + dt.timedelta(minutes=SEN) if KI else None
letters = [
 f"[第71弾 補 納め 1/3] 束 main樹 docs/evidence/{KM}/(置くのみ・commit は家老)紙 {P_}({PB}B・{PL}行)/ 臺帳 {MN}(項{items}・append.py・基点=束の根)/ 門控 {G}(r71b)/ 門(基点=束の根): main rc{g['main'].group(2)} all rc{g['all'].group(2)} 渡{g['all'].group(1)}・基点無し rc{g['nobase'].group(2)}(落ちて正)/ 共有器と三束(親 km-71・自主束・km-70)へ0byte(印 前後同)。親=km-71(改め㋑㋒は其處で納め済)",
 f"[第71弾 補 納め 2/3・改め㋐] 案イ(拒む・rc1・札「空/空白―許さぬ」)/ 案ロ(既定へ倒し★必ず刷る★)を門 L196〜205 への unified diff・戻し方一行(cp -p 控)・塞がぬ物(\".\" の明示・verify 直呼び・全角空白・案ロは舊形で rc0 が通る)で並べた(紙§2§3・表§4)。★推し=イ★(書き忘れを既定で通すのは rc だけ見る呼び手に見えぬ)。据ゑず・門 sha16 {num(r'門 sha16 ([0-9a-f]{16})', rd(B + '.md'))}",
 f"[第71弾 補 納め 3/3・疵と代送依頼] 疵①改め便 06:44:06 を納め 06:49:30 の後 06:50 に読んだ(箱を弾の途中で読まなんだ・二度目)→「重ねて測るな」の後に ㋑24走を重ねた(害=重ねた事のみ・共有器0byte)。直し=次弾から着手便の後に箱を読む段 07 を鎖へ。疵②便1・着手便・追ひ6 の一走目が 300 字超で己の門に鳴つた(.first)。gunshi-mac は死箱ゆゑ監査提出の代送を乞ふ(紙 {P_})",
]
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_')); naru = []
if TO not in ROSTER or TO in DEAD or TO == ME: naru.append('宛先')
for i, b in enumerate(letters, 1):
    if not (40 <= len(b) <= 300): naru.append(f'便{i} 字数 {len(b)}')
    if '?' in b: naru.append(f'便{i} 引けぬ數')
    q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=b.encode('utf-8'), capture_output=True)
    if q.returncode == 10: naru.append(f'便{i} 先送り語')
print('字数', [len(b) for b in letters], '門', naru or '通(0 鳴)')
if DRY or naru:
    K.kaku(OUT + '/62_dry.stdout', f'# DRY={DRY} 門 {naru or "通"} 字数 {[len(b) for b in letters]}\n' + '\n--- \n'.join(letters)); print(open(OUT + '/62_dry.stdout', encoding='utf-8').read()); sys.exit(1 if naru else 0)
rec = []
for i, b in enumerate(letters, 1):
    koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    if i == len(letters): rec.append(f'★端点(納め最終便 {i}/{len(letters)} を inbox_write.sh へ渡す直前の date 刻)= {koku}★')
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report', ME], capture_output=True, text=True, cwd=M); rec.append(f'便{i}/{len(letters)} 刻 {koku} inbox_write rc={p.returncode}')
ms = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []
hits = [[m['id'] for m in ms if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == b] for b in letters]
rec.append(f'★第八の番人(刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")})★: ' + ' | '.join(f'便{i} 箱 {len(h)} 本 {h} 逐語一致 {len(h) == 1}' for i, h in enumerate(hits, 1)))
end = P(re.search(r'端点[^=]*= (\S+)★', '\n'.join(rec)).group(1)); jitsu = (end - P(KI)).total_seconds() / 60 if KI else 0
rec.append(f'★宣⇔實(席基準)★ 起 {KI}(着手便 05 の刻)→ 端点 {end.strftime("%Y-%m-%dT%H:%M:%S")} = 實 {jitsu:.2f} 分 ⇔ 宣 {SEN} 分(宣の刻 {sen_clock.strftime("%H:%M:%S") if sen_clock else "?"}) → 宣−實 {SEN - jitsu:+.2f} 分 = {"＋過大(宣が長い)" if SEN - jitsu > 0 else "−過小(宣が短い)"} / 器 11 本 → 實 ÷ 器 = {jitsu / 11:.2f} 分/器(次弾の材料)')
K.kaku(OUT + '/62_report_body.txt', '\n'.join(f'--- 便{i}/{len(letters)} ({len(b)} 字)\n{b}' for i, b in enumerate(letters, 1))); K.kaku(OUT + '/63_sent.txt', '\n'.join(rec)); print('\n'.join(rec))
sys.exit(0 if all(len(h) == 1 for h in hits) else 3)
