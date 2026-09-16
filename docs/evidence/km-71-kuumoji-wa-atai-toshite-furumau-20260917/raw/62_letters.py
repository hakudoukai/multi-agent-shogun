# -*- coding: utf-8 -*-
"""添状の器 62(第71弾・★臺帳より先に書いた・走らせるのは門の後・出目は根の外 _after/★)。便 5(各 300 字以内・字数を先に印字)を karo-mac へ inbox_write.sh で出す(便 5 = 宣⇔實 + 監査提出の代送依頼・gunshi-mac は死箱 rc=68)。
数は raw/20_bosu.txt・raw/30_mon_santai.txt・raw/40_katachi.txt・_after/60_gate_rcs.txt から regex で引く(手写しでない)。門(05 と同じ)が一つでも鳴れば一通も送らぬ。DRY=1 なら送らず印も 63 も書かぬ。第八の番人付。二走目(一走目 DRY は便1 が 309 字で鳴つた → _after/62_dry.first.stdout)。
端点 = 納め最終便(5/5)を inbox_write.sh へ渡す直前の date 刻(着手便 05 の宣の定義と同じ)。"""
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
T20, T30, T40 = rd(E + '/20_bosu.txt'), rd(E + '/30_mon_santai.txt'), rd(E + '/40_katachi.txt')
N = num(r'★N\(器・現物\)= (\d+) 本★', T20); Ms = num(r'★M\(長さ0の文字列が判定に効き得る箇所・現物\)= (\d+) 箇所★', T20); forms = num(r'形別 M\(現物\): (.+?) / 内', T20); high = num(r'危=high\(形A の左が slice・形F\) (\d+)', T20)
posn = num(r'陽性対照 fixture/pos.py★ 形別 拾つた数 (\{[^}]+\}) →', T20); negok = '一つも拾はず' in T20; posok = '悉く拾つた' in T20; nonpy = num(r'非 \.py (\d+)', T20); hinon = num(r'非通常 (\d+)', T20)
tally = num(r'条①|條① 通/落 の数\(態別・24 走中 各 8\)★: (.+)', T30); dep = num(r'cwd で條①が反転した \(臺帳, 態\) = (\d+) 組', T30)
def sub(sk, kind, ck): return num(sk + r' × ' + re.escape(kind) + r' × cwd=' + ck + r': 通 (\d+) / 落 \d+', T30) + '/' + num(sk + r' × ' + re.escape(kind) + r' × cwd=' + ck + r': 通 \d+ / 落 (\d+)', T30)
KI = rd(E + '/05_chakushu_koku.txt').strip(); SEN = 25; sen_clock = P(KI) + dt.timedelta(minutes=SEN) if KI else None
letters = [
 f"[第71弾 納め 1/5] 束 main樹 docs/evidence/{KM}/(置くのみ・commit は家老)紙 {P_}({PB}B・{PL}行)/ 臺帳 {MN}(項{items}・append.py・基点=束の根)/ 門控 {G}(r71)/ 門(基点=束の根): main rc{g['main'].group(2)} all rc{g['all'].group(2)} 渡{g['all'].group(1)}・基点無し rc{g['nobase'].group(2)}(落ちて正)/ 共有器と四束へ0byte(印 前後同)。自主束は動かさず紙§0で親子を宣した",
 f"[第71弾 納め 2/5・㋐母數] 歩き根=km-70 束+自主束+km-71 束(己)・深さ無限・S_ISREG かつ .py・非通常{hinon}/非.py {nonpy} は母數外・fixture 2 本と己 1 本は別札。★N={N} 本 / M={Ms} 箇所★(形別 {forms}・内 危=high {high})。M は「効き得る箇所」の上界であつて疵の数ではない(D/E は欠を扱ふ設計が多く、空が来るかは器で判ぜぬ)",
 f"[第71弾 納め 3/5・㋑門三態] 四臺帳(km-47/50=舊形 repo根相対・km-70/自主束=束内相対)×態3(unset/\"\"/\".\")×cwd2=24走・argv=[臺帳,臺帳]・据ゑず。條① {tally}。★cwd で反転 {dep} 組=\"\" と \".\" の全8組・unset は0組★ ∴ \"\" は \".\" と同じ挙動(cwd 相対)で、札だけが「引数 明示」。舊形×\"\"×cwd=束の根 通/落 {sub('kuu', '舊形(repo根相対)', 'taba')}・束内相対×\"\"×repo {sub('kuu', '束内相対', 'repo')}",
 f"[第71弾 納め 4/5・㋒㋓形と対照] 形6(A 包含 in / B == '' / C x or 定数 / D 裸の真偽 / E 三項 else 定数 / F startswith(''))を 40 で★評価して★示した(''→ A True・B True・C 既定・D False・E 定数・F True)。対照は檢出子 20 自身の路(fixture/pos.py・neg.py を同じ os.walk で歩き現物と分ける): 陽性 {posn} {'悉く拾つた' if posok else '★落★'}・陰性 {'0 で通' if negok else '★誤拾★'}・rc {0 if posok and negok else 1}・刻 20 の頭",
 "[第71弾 納め 5/5・㋔と代送依頼] 塞ぎ方は紙§5のみ(据ゑず): ①門 L197 に env_state を当て empty/blank を拒む(戻し=if の一行) ②verify L97 `if any(argv[2:])`+札に渡した値(戻し=一行) ③己の `l[:1] in 'AM'`→`l and l[0] in 'AM'`(km-70 66 で既述)。塞がぬ物: \".\" の明示(正当)・値の来歴・他席の器。宣⇔實は追ひ便で。gunshi-mac は死箱ゆゑ監査提出の代送を乞ふ",
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
