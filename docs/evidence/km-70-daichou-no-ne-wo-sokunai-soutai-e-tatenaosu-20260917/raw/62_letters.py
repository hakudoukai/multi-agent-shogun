# -*- coding: utf-8 -*-
"""添状の器 62(第70弾・★臺帳より先に書いた・走らせるのは門の後・出目は根の外 _after/★)。便 6(各 300 字以内・字数を先に印字)を karo-mac へ inbox_write.sh で出す(便 6 = 監査提出の代送依頼・gunshi-mac は死箱)。
数は 20/30/60 の .txt から regex で引く(手写しでない)。門(05 と同じ・胴と封筒の中身)が一つでも鳴れば一通も送らぬ。DRY=1 なら送らず印も 63 も書かぬ。
札: km-70 の札が在れば status→done を打つ。無ければ「札無し」と 63 に書き、打たぬ(km-69 done の札へは触れぬ)。"""
import sys, os, re, time, subprocess, hashlib, yaml, datetime as dt, glob
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, OUT); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; RN = '70弾'; DRY = bool(os.environ.get('DRY')); ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}; KM = os.path.basename(D)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else 'x' * 16
def rd(p, alt=''): return open(p, encoding='utf-8').read() if os.path.isfile(p) else alt
def P(s): return dt.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')
def num(pat, txt, alt='?'): m = re.search(pat, txt); return m.group(1) if m else alt
P_, MN, G = sha16(B + '.md'), sha16(B + '_manifest.txt'), sha16(B + '_gate.txt')
man = rd(B + '_manifest.txt'); items = sum(1 for l in man.split('\n') if l.startswith('path=')); PL = str(rd(B + '.md').count('\n'))
rcs = rd(OUT + '/60_gate_rcs.txt', '③ main | 渡した 0 | rc 0 | 札 0\n③ all | 渡した 0 | rc 0 | 札 0\n③ nobase | 渡した 0 | rc 1 | 札 0')
g = {k: re.search(r'^③ ' + k + r' \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M) for k in ('main', 'all', 'nobase')}
T20 = rd(E + '/20_tatenaoshi.txt'); T30 = rd(E + '/30_taishou.txt')
def s20(k5):
    sec = T20[T20.index('## ' + k5):]; sec = sec[:sec.index('判 ')]
    return dict(kou=num(r'項\(sha256= 有・path 讀めた\) (\d+)', sec), rc=num(r'append\.py\(cwd = [^)]*\) rc (\d+)', sec), fuu=num(r'sha16 ([0-9a-f]{16}) bytes \d+ 行 \d+ / 項', sec), kuk=num(r'括つた\(空白名\) (\d+)', sec), tai=num(r'対一致\(同じ相対名・同じ sha256\) (\d+)', sec), ingai=num(r'員外\(束の disk に在つて臺帳に無い通常 file\) (\d+) 本', sec), atama=num(r'でない行 (\d+)★', sec), nai=num(r'★束に無い名 (\d+)★', sec))
def s30(k5, lab, ki):
    sec = T30[T30.index('## ' + k5):]; nxt = sec.find('\n## ', 3); sec = sec if nxt < 0 else sec[:nxt]
    m = re.search(re.escape(lab) + r'[^\n]*' + re.escape(ki) + r'[^\n]*?: rc (\d+) / (?:母數 (\d+) 一致 (\d+) 相違 (\d+) 実体無 (\d+)|條① (?:★落★|通)\[(\d+)/(\d+)/(\d+)/(\d+)/\d+\])', sec)
    if not m: return '?'
    if m.group(2): return f'rc{m.group(1)} {m.group(3)}/{m.group(4)}/{m.group(5)}(母數{m.group(2)})'
    return f'rc{m.group(1)} {m.group(7)}/{m.group(8)}/{m.group(9)}(母數{m.group(6)})'
a, b = s20('km-47'), s20('km-50'); ketsu = '通' if '★三本とも期待通り' in T30 else '★外れ★'
st = rd(E + '/00_start.txt'); KI = rd(E + '/05_chakushu_koku.txt').strip(); SEN_MIN = float(num(r'宣 = 起 \+ (\d+) 分', st, '42')); sen_clock = P(KI) + dt.timedelta(minutes=SEN_MIN); HATCHU = '2026-09-17T05:29:46'
A96 = rd(OUT + '/96_after.txt', '照合 rc 0 / 一致 0 相違 0 実体無 0 讀めぬ 0(母數 0) / 後 0 / 印 前後 ?')
letters = [
 f"[第{RN} 納め 1/6] 束 ★main樹★ docs/evidence/{KM}/ 置くのみ・commit/push は家老 / 紙 {P_}({os.path.getsize(B + '.md') if os.path.isfile(B + '.md') else 0}B・{PL}行)/ 臺帳 {MN}(項{items}・append.py のみ・★基点=束の根(束内相対・裁322699)★)/ 門控 {G}(r70)/ 門 KM_GATE_MANIFEST_BASE=束: main rc{g['main'].group(2)} all rc{g['all'].group(2)} 渡{g['all'].group(1)}・★基点無し rc{g['nobase'].group(2)}(落ちて正)★ / 門の後 {num(r'後 (\d+)', A96)} 疵 印前後{num(r'印 前後 (\S+)', A96)}",
 f"[第{RN} 納め 2/6] ㋐建て直し(20・cd 束→append.py・新束 raw/saiken/ へ・既成束へ0字): km-47 旧項{a['kou']}→新項{a['tai']} 対一致{a['tai']} 頭違ひ{a['atama']} 無{a['nai']} 括{a['kuk']}(空白名1) rc{a['rc']} 封{a['fuu']} 員外{a['ingai']} / km-50 旧項{b['kou']}→対一致{b['tai']} 括{b['kuk']} rc{b['rc']} 封{b['fuu']} 員外{b['ingai']}。新旧の (相対名, sha256) 対は悉く同じ ―― 変つたのは path の頭だけ",
 f"[第{RN} 納め 3/6] ㋑對照 km-47(項22・verify直/門min/門all・cwd main樹): ㋐明示基点=束の根 verify {s30('km-47', '㋐', 'verify')} 門min {s30('km-47', '㋐', '門 min')} 門all {s30('km-47', '㋐', '門 all')} / ㋑基点無し(unset・既定=repo根) verify {s30('km-47', '㋑', 'verify')} 門min {s30('km-47', '㋑', '門 min')} / ㋒出鱈目 verify {s30('km-47', '㋒', 'verify')} 門min {s30('km-47', '㋒', '門 min')}(一致/相違/実体無)",
 f"[第{RN} 納め 4/6] ㋑對照 km-50(項39): ㋐ verify {s30('km-50', '㋐', 'verify')} 門min {s30('km-50', '㋐', '門 min')} 門all {s30('km-50', '㋐', '門 all')} / ㋑ verify {s30('km-50', '㋑', 'verify')} 門min {s30('km-50', '㋑', '門 min')} / ㋒ verify {s30('km-50', '㋒', 'verify')} 門min {s30('km-50', '㋒', '門 min')}。讀めぬ行 0・門の條②③④ 鳴0(全走)。結 {ketsu}。参考㋓ 基点\"\" cwd=束 → 一致(cwd に依る故 使はぬ)",
 f"[第{RN} 納め 5/6] 意味せぬ事(紙§4に8): 既成の臺帳は改めて居らぬ(舊形の儘固定・新臺帳は km-70 内)/ 一致N は旧 sha と同じの意で旧の正しさは言はぬ / km-47 の旧形1 は空白名の括り(形②・讀める唯一の形)を讀み手が「旧形」と札する事で禁破りでない / 門 all rc0 は員外8本の條②③④を測つて居らぬ。★km-70 の札が無い(km-69 done の儘)故 札へ印を打たず★・基点の口が空文字の時は未測",
 f"[第{RN} 納め 6/6・監査提出の代送を乞ふ] gunshi-mac は死箱(rc=68)ゆゑ同封→ [監査提出(專任1 第{RN})] 束 main樹 docs/evidence/{KM}/ 紙 {P_} / 臺帳 {MN}(束内相対) / 門 main rc{g['main'].group(2)} / 題=km-47・km-50 の臺帳を束内相対で建て直し(裁322699)、明示基点→一致N/実体無0/rc0・既定→実体無N/rc1・出鱈目→rc1 を verify と門の双方で示す / 答は便2〜5。監査を乞ふ",
]
lens = [len(x) for x in letters]; print('字数', lens)
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_'))
naru = []
if TO not in ROSTER or TO in DEAD or TO == ME: naru.append(f'宛先 {TO} が名簿に無い/死箱/己')
for i, (x, n) in enumerate(zip(letters, lens), 1):
    if not (40 <= n <= 300): naru.append(f'便{i} {n} 字 が 40..300 の外')
    if re.fullmatch(r'[a-z0-9_-]+', x): naru.append(f'便{i} 胴が役職名の形')
    if '?' in x.replace('？', ''): naru.append(f'便{i} 引けなんだ數(?)が在る')
    q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=x.encode('utf-8'), capture_output=True)
    if q.returncode == 10: naru.append(f'便{i} 先送り語: ' + q.stdout.decode('utf-8', 'replace').strip()[:100])
print('門', naru or '通(0 鳴)')
if DRY: print('\n'.join(letters)); print('DRY ―― 送らず・印も 63 も書かぬ'); sys.exit(1 if naru else 0)
assert not naru, naru
tanten = time.strftime('%Y-%m-%dT%H:%M:%S'); now = tanten + time.strftime('%z')
K.kaku(OUT + '/62_report_body.txt', f'# 62 便の本文(第{RN}・各 300 字以内・先に字数を印字 {lens})/ 刻 {now}\n' + '\n'.join(f'--- 便{i}/{len(letters)} ({n} 字)\n{x}' for i, (x, n) in enumerate(zip(letters, lens), 1)))
rcs_l = []
for i, x in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, x, 'report', ME], capture_output=True, text=True, cwd=M); rcs_l.append(f'便{i}/{len(letters)} inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else ''))
done_at = time.strftime('%Y-%m-%dT%H:%M:%S'); cp = M + '/queue/tasks/ashigaru-mac-1.yaml'; card = open(cp, encoding='utf-8').read()
tid = num(r'^task_id: (\S+)', card); fuda = '札無し(札の task_id は ' + tid + '・status ' + num(r'^status: (\S+)', card) + ' ―― km-70 の札は書かれて居らぬ故 印を打たず)'
if tid.startswith('km-70') and card.count('\nstatus: assigned\n') == 1:
    card = card.replace('\nstatus: assigned\n', f'\nstatus: done\ndone_at: "{done_at}"\ndone_note: "納め便 端点 {tanten}(起 {KI}・宣 {sen_clock.strftime("%H:%M:%S")}) / 束 main樹 docs/evidence/{KM} / 紙 {P_} / 臺帳 {MN} 項{items}(束内相対) / 門控 60_gate_top.r70 / 對照 {ketsu}"\n', 1); open(cp, 'w', encoding='utf-8', newline='\n').write(card); fuda = f'札に印を書いた: status done / done_at {done_at}'
j_seki = (P(tanten) - P(KI)).total_seconds() / 60; d_seki = SEN_MIN - j_seki
j_k = (P(done_at) - P(HATCHU)).total_seconds() / 60; sen_k = (sen_clock - P(HATCHU)).total_seconds() / 60; d_k = sen_k - j_k
t8 = time.strftime('%Y-%m-%dT%H:%M:%S%z'); ms = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []
ids = [m['id'] for m in ms if m.get('from') == ME and str(m.get('content', '')).startswith(f'[第{RN} 納め')]; byid = {m['id']: str(m.get('content', '')) for m in ms}
g8 = [f'{i} 箱 {len(byid.get(i, "").rstrip(chr(10)))} / 62 {len(x)} / 逐語一致 {byid.get(i, "").rstrip(chr(10)) == x}' for x, i in zip(letters, ids)]
K.kaku(OUT + '/63_sent.txt', f'{now}\n宛 {TO} / type report / from {ME} / 便 {len(letters)}(各 300 字以内・先に字数を印字 {lens})/ gunshi-mac へは出さず(死箱 rc=68・便 6 で代送を乞ふ)\n' + '\n'.join(rcs_l)
  + f'\n箱 queue/inbox/{TO}.yaml で本弾の冠 [第{RN} 納め を持つ from={ME} の entry = {len(ids)} 本: {ids}\n{fuda}'
  + f'\n★宣⇔實 両基準(宣 = {sen_clock.strftime("%H:%M:%S")} の刻・起 {KI}・宣の長さ {SEN_MIN:.1f} 分・建て方 10 器 × 2.78 分/器 × 1.5)★\n席基準  起 {KI}(着手便の刻・器 05) → 端点 {tanten}(納め便 1 本目を渡す直前) = 實 {j_seki:.2f} 分 ⇔ 宣 {SEN_MIN:.1f} 分 → 宣−實 {d_seki:+.2f} 分 = {"＋過大(宣が長い)" if d_seki > 0 else "−過少(宣が短い)"} / 實 ÷ 器 10 = {j_seki / 10:.2f} 分/器(次弾の數の材料)'
  + f'\n家老基準 発注便 {HATCHU}(札が無い故 assigned_at の代り) → 端点 {done_at} = 實 {j_k:.2f} 分 ⇔ 宣 {sen_k:.2f} 分 → 宣−實 {d_k:+.2f} 分 = {"＋過大" if d_k > 0 else "−過少"}\n★符號は {"同じ" if (d_seki > 0) == (d_k > 0) else "★分かれた★"}★'
  + f'\n★第八の番人(送出後に箱から本文を讀み返す・刻 {t8})★: ' + ' | '.join(g8))
print(open(OUT + '/63_sent.txt', encoding='utf-8').read()); sys.exit(0 if all('rc=0' in r for r in rcs_l) and len(ids) == len(letters) and all('True' in x for x in g8) else 3)
