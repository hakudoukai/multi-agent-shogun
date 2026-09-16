# -*- coding: utf-8 -*-
"""添状の器 62(自主束・★臺帳より先に書いた・走らせるのは門の後・出目は根の外 _after/★)。便 3(各 300 字以内・字数を先に印字)を karo-mac へ inbox_write.sh で出す(便 3 = 監査提出の代送依頼・gunshi-mac は死箱 rc=68)。
数は raw/10_kuumoji.txt と _after/60_gate_rcs.txt から regex で引く(手写しでない)。門(05 と同じ)が一つでも鳴れば一通も送らぬ。DRY=1 なら送らず印も 63 も書かぬ。第八の番人付。
二走目: 一走目(DRY・_after/62_dry.first.stdout)は表の列取りが一つずれ(相違の列を実体無と読み「実体無0」と刷つた)→ 添字を [4](実体無)/[2](一致)へ直した。"""
import sys, os, re, time, subprocess, hashlib, yaml, glob
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; OUT = D + '/_after'; os.makedirs(OUT, exist_ok=True); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; DRY = bool(os.environ.get('DRY')); ME = 'ashigaru-mac-1'; TO = 'karo-mac'; DEAD = {'gunshi-mac'}; KM = os.path.basename(D)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else 'x' * 16
def rd(p, alt=''): return open(p, encoding='utf-8').read() if os.path.isfile(p) else alt
def num(pat, txt, alt='?'): m = re.search(pat, txt); return m.group(1) if m else alt
P_, MN, G = sha16(B + '.md'), sha16(B + '_manifest.txt'), sha16(B + '_gate.txt'); PL = str(rd(B + '.md').count('\n')); PB = os.path.getsize(B + '.md') if os.path.isfile(B + '.md') else 0
items = sum(1 for l in rd(B + '_manifest.txt').split('\n') if l.startswith('path='))
rcs = rd(OUT + '/60_gate_rcs.txt', '③ main | 渡した 0 | rc 9 | 札 0\n③ all | 渡した 0 | rc 9 | 札 0\n③ nobase | 渡した 0 | rc 9 | 札 0')
g = {k: re.search(r'^③ ' + k + r' \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M) for k in ('main', 'all', 'nobase')}
T = rd(E + '/10_kuumoji.txt'); hazure = num(r'外れ (\d+) 行 / 母數 (\d+) 走', T); bosu = num(r'外れ \d+ 行 / 母數 (\d+) 走', T)
def row(tool, bk, ck):
    m = re.search(r'^\| ' + tool + r' \| ' + bk + r' \| ' + ck + r' \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| ([^|]+?) \| ([^|]+?) \|', T, re.M)
    return m.groups() if m else ('?',) * 8
kr, kt = row('gate', 'kuu', 'repo'), row('gate', 'kuu', 'taba'); vr, vt = row('verify', 'kuu', 'repo'), row('verify', 'kuu', 'taba'); hr, ht = row('gate', 'kuuhaku', 'repo'), row('gate', 'kuuhaku', 'taba')
GS = num(r'門 sha16 ([0-9a-f]{16})', T); VS = num(r'照合器 sha16 ([0-9a-f]{16})', T); KOKU05 = num(r'刻 (\S+) /', rd(E + '/05_seikyu.txt'))
letters = [
 f"[專任1 自主束 納め 1/3・空文字基点] 束 main樹 docs/evidence/{KM}/(置くのみ・commit は家老)紙 {P_}({PB}B・{PL}行)/ 臺帳 {MN}(項{items}・append.py・基点=束の根)/ 門控 {G} / 門(基点=束の根): main rc{g['main'].group(2)} all rc{g['all'].group(2)} 渡{g['all'].group(1)}・基点無し rc{g['nobase'].group(2)}(落ちて正)/ 共有器へ0byte・km-70 束へ0byte(印 前後同)。起=05便 {KOKU05[11:19]}・宣は出さなんだ(疵)",
 f"[自主束 納め 2/3・答] km-70 便5の未測「基点の口が空文字」を 二器×基点四態×cwd二所={bosu}走で測つた(臺帳=km-70 項139・門 {GS}・照合器 {VS})。外れ{hazure}。★空文字 \"\" は札「引数 明示」を刷りながら cwd で反転★: 門 kuu repo根 rc{kr[0]} 実体無{kr[4]}「出すな」/ 束の根 rc{kt[0]} 一致{kt[2]}「出してよい」(verify 直も同じ rc{vr[0]}/rc{vt[0]})。unset・明示・空白\" \"は cwd 不依存(空白は両所 rc{hr[0]} 実体無{hr[4]})",
 f"[自主束 納め 3/3・提案と代送依頼] 讀んだ逐語: 門 L197 は ${{x+set}} で空を通し L194 註が「空文字も cwd 相対の明示」と自認・乙 env_state(L40)は閾にのみ当たり基点には当たらぬ。∴9/12 止血(L185)が閉ぢた「立つ場所で出目が変はる」形が、呼ぶ側の \"\" で再び開く。提案(器の改めではない): 基点にも env_state を当て empty/blank は拒むか既定へ倒して刷る。gunshi-mac は死箱ゆゑ監査提出の代送を乞ふ(紙 {P_})",
]
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_')); naru = []
if TO not in ROSTER or TO in DEAD or TO == ME: naru.append('宛先')
for i, b in enumerate(letters, 1):
    if not (40 <= len(b) <= 300): naru.append(f'便{i} 字数 {len(b)}')
    if '?' in b.replace('?', '', 0) and re.search(r'\?', b): naru.append(f'便{i} 引けぬ數')
    q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=b.encode('utf-8'), capture_output=True)
    if q.returncode == 10: naru.append(f'便{i} 先送り語')
print('字数', [len(b) for b in letters], '門', naru or '通(0 鳴)')
if DRY or naru:
    K.kaku(OUT + '/62_dry.stdout', f'# DRY={DRY} 門 {naru or "通"} 字数 {[len(b) for b in letters]}\n' + '\n--- \n'.join(letters)); print(open(OUT + '/62_dry.stdout', encoding='utf-8').read()); sys.exit(1 if naru else 0)
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); rec = [koku, f'宛 {TO} / type report / from {ME} / 便 {len(letters)}(各 300 字以内・字数 {[len(b) for b in letters]})']
for i, b in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report', ME], capture_output=True, text=True, cwd=M); rec.append(f'便{i}/{len(letters)} inbox_write rc={p.returncode}')
ms = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []
hits = [[m['id'] for m in ms if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == b] for b in letters]
rec.append(f'★第八の番人(刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")})★: ' + ' | '.join(f'便{i} 箱 {len(h)} 本 {h} 逐語一致 {len(h) == 1}' for i, h in enumerate(hits, 1)))
K.kaku(OUT + '/62_report_body.txt', '\n'.join(f'--- 便{i}/{len(letters)} ({len(b)} 字)\n{b}' for i, b in enumerate(letters, 1))); K.kaku(OUT + '/63_sent.txt', '\n'.join(rec)); print('\n'.join(rec))
sys.exit(0 if all(len(h) == 1 for h in hits) else 3)
