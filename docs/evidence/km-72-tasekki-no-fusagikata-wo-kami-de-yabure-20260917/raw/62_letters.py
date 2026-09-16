# -*- coding: utf-8 -*-
"""添状の器 62(第72弾・km-71b の写し・便 4・★臺帳より先に書いた・走らせるのは門の後・出目は _after/★)。数は _after/60_gate_rcs.txt と raw/ の出目から regex で引く(手写しでない)。門(05 と同じ)が一つでも鳴れば一通も送らぬ。DRY=1 なら送らず印も 63 も書かぬ。第八の番人付。端点 = 納め最終便(4/4)を inbox_write.sh へ渡す直前の date 刻。"""
import sys, os, re, time, subprocess, hashlib, yaml, glob, csv, datetime as dt
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; OUT = D + '/_after'; os.makedirs(OUT, exist_ok=True); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; DRY = bool(os.environ.get('DRY')); ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}; KM = os.path.basename(D)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else 'x' * 16
def rd(p, alt=''): return open(p, encoding='utf-8').read() if os.path.isfile(p) else alt
def num(pat, txt, alt='?'): m = re.search(pat, txt); return m.group(1) if m else alt
def P(s): return dt.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')
P_, MN, G = sha16(B + '.md'), sha16(B + '_manifest.txt'), sha16(B + '_gate.txt'); PL = str(rd(B + '.md').count('\n')); PB = os.path.getsize(B + '.md') if os.path.isfile(B + '.md') else 0
items = sum(1 for l in rd(B + '_manifest.txt').split('\n') if l.startswith('path='))
rcs = rd(OUT + '/60_gate_rcs.txt', '③ main | 渡した 0 | rc 9 | 札 0\n③ all | 渡した 0 | rc 9 | 札 0\n③ all_kiyoi | 渡した 0 | rc 9 | 札 0\n③ nobase | 渡した 0 | rc 9 | 札 0')
g = {k: re.search(r'^③ ' + k + r' \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M) for k in ('main', 'all', 'all_kiyoi', 'nobase')}
decl = num(r"宣した行末空白 fixture (\d+) 本", rcs); T40 = rd(E + '/40_matome.txt'); T10 = rd(E + '/10_utsushi.txt'); T20 = rd(E + '/20_matrix.txt'); r47 = list(csv.DictReader(open(E + '/47_kegare.tsv', encoding='utf-8'), delimiter='\t')); r48 = list(csv.DictReader(open(E + '/48_lead_nl.tsv', encoding='utf-8'), delimiter='\t'))
bc_hei = sum(1 for r in r47 if r['var'] == 'hei' and 'B≠C' in r['判']); den = sum(1 for r in r47 if r['var'] == 'hei'); n48 = sum(1 for r in r48 if r['門票を門に掛けた rc'] == '1')
KI = rd(E + '/05_chakushu_koku.txt').strip(); SEN = 4; sen_clock = P(KI) + dt.timedelta(minutes=SEN) if KI else None
letters = [
 f"[第72弾 納め 1/4] 束 main樹 docs/evidence/{KM}/(commit は家老)紙 {P_}({PB}B・{PL}行)/ 臺帳 {MN}(項{items}・append.py・基点=束の根)/ 門控 {G}(r72)/ 門: main rc{g['main'].group(2)}・all rc{g['all'].group(2)}(宣したfixture {decl}本が條②で鳴るのが正)・all_kiyoi rc{g['all_kiyoi'].group(2)} 渡{g['all_kiyoi'].group(1)}・基点無し rc{g['nobase'].group(2)}/ 生器4本・讀んだ四束へ0byte(印同)",
 f"[第72弾 納め 2/4・母數と最重の穴] 母數=diff 7本/{num(r'行 (\d+) /', T10)}行/hunk {num(r'hunk (\d+)', T10)}/新関数3/呼び口{num(r'変へた呼び口 (\d+)', T10)}・路K={num(r'K = (\d+) 路', rd(B + '.md'))}本(実走)。★丙 safe_show の cut -c1-40 が 40byte以上で出目に改行を足し、札を二行に割る★(raw/45)。彼が塞いだ「札の行割れ」を x×60 で丙自身が起こす(生器では起きぬ)。行讀みの讀手は既定へ倒した事を見失ふ(raw/47 hei B≠C {bc_hei}/{den})",
 f"[第72弾 納め 3/4・乙と甲] 乙 tmo_ok は timeout に値を第一引数で渡す故 --help/--version を受け(rc0)、後段が help 2783byte を門票へ吐き 條⑤「測れぬ」で file を咎める。床1天86400 は整数綴りのみ: 0m/0.0/99999d/1e9 が素通り・★86401 は拒み 2^63 は受ける★。甲の札「扱へぬ か 範囲外」は讀めぬ{num(r'kou ge0=2: (\d+)', T40)}と範囲外{int(num(r'kou ge0=0: (\d+)', T40, '0')) + int(num(r'kou ge0=1: (\d+)', T40, '0'))}を分けぬ(裁322952乙に反す)",
 f"[第72弾 納め 4/4・合と受ける路・疵] 合は patch を6順+2順に重ねても建たぬ(二本目から rej・同sha 0/8)=手織り。TIMEOUT では乙が甲を上書きし札だけ甲の語。合x(床天替)=札「許5..60」で1と86400が受かる/合y(chk誤字)=全値既定・札は値を咎め・bash error一行・rc0。★「\\n5」は生甲丙合 悉く受け 條⑤の行が切れ 門票が己の條②に落ちる({n48}/40・gate4はrc0の儘)★。疵=bytes字面に和字 二度・40の裁讀み三度直し。監査提出の代送を乞ふ(紙 {P_})",
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
end = P(re.search(r'端点[^=]*= (\S+)★', '\n'.join(rec)).group(1)); jitsu = (end - P(KI)).total_seconds() / 60 if KI else 0; NKI = 20
rec.append(f'★宣⇔實(席基準)★ 起 {KI}(着手便 05 の刻)→ 端点 {end.strftime("%Y-%m-%dT%H:%M:%S")} = 實 {jitsu:.2f} 分 ⇔ 宣 {SEN} 分(宣の刻 {sen_clock.strftime("%H:%M:%S") if sen_clock else "?"}) → 宣−實 {SEN - jitsu:+.2f} 分 = {"＋過大(宣が長い)" if SEN - jitsu > 0 else "−過小(宣が短い)"} / 器 {NKI} 本(新規 11 + 写し 9)→ 實 ÷ 器 = {jitsu / NKI:.2f} 分/器(次弾の材料・讀みの刻を含む)')
K.kaku(OUT + '/62_report_body.txt', '\n'.join(f'--- 便{i}/{len(letters)} ({len(b)} 字)\n{b}' for i, b in enumerate(letters, 1))); K.kaku(OUT + '/63_sent.txt', '\n'.join(rec)); print('\n'.join(rec))
sys.exit(0 if all(len(h) == 1 for h in hits) else 3)
