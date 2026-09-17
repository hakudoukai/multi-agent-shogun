# -*- coding: utf-8 -*-
"""添状の器 62(第73弾・km-72 の写し・便 4・★臺帳より先に書いた・走らせるのは門の後・出目は _after/★)。数は _after/60_gate_rcs.txt と raw/ の出目から regex で引く(手写しでない)。門(05 と同じ)が一つでも鳴れば一通も送らぬ。DRY=1 なら送らず印も 63 も書かぬ。第八の番人付。端点 = 納め最終便(4/4)を inbox_write.sh へ渡す直前の date 刻。送る前に己の箱を読む(作法⑿③・未読が在れば送らず止まる)。"""
import sys, os, re, time, subprocess, hashlib, yaml, glob, datetime as dt
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
T10, T20, T25, T30, T40, T45, T47 = (rd(E + '/' + n) for n in ('10_saigen.txt', '20_seigyo.txt', '25_terminal.txt', '30_shell.txt', '40_keta.txt', '45_aimai.txt', '47_hei.txt'))
KI = rd(E + '/05_chakushu_koku.txt').strip(); SEN = 24; sen_clock = P(KI) + dt.timedelta(minutes=SEN) if KI else None; NKI = len(glob.glob(E + '/*.py'))
letters = [
 f"[第73弾 納め 1/4] 束 main樹 docs/evidence/{KM}/紙 {P_}({PB}B・{PL}行)/ 臺帳 {MN}(項{items}・append.py・基点=束の根)/ 門控 {G}(員外)/ 門: main rc{g['main'].group(2)}・all rc{g['all'].group(2)} 渡{g['all'].group(1)}・基点無し rc{g['nobase'].group(2)}/ 生器4本・彼の二束へ0byte(印同)/ 器 {NKI} 本(宣16)/ 08:10便 讀了・/clear後 context空・八問測了ゆゑ中間便に代へ本納め",
 f"[第73弾 納め 2/4・㋐㋑㋒] ㋐彼の48走は己の台で {num(r'一致 (\d+)', T10)}/{num(r'母數 (\d+)', T10)} 一致=同じ石を二人で踏んだ(台・LF讀手・C・bash3.2・逐語の五つ共有・raw/10)。㋑乙は3字を封じ Cc {num(r'Cc は (\d+)', T20)} の内 {num(r'残る Cc = (\d+)', T20)}+Zl/Zp2 が残る。二行に割る字は讀手で違ふ: byte讀手0・Python splitlines {num(r'讀手 py.splitlines: (\d+)', T20)}・tmux画面 {num(r'成つた形 (\d+)/', T25)}(VT/FF)。㋒四本とも env bash=3.2、sh起動の呼び手 {num(r'「sh <器>」の形 = (\d+)', T30)}/{num(r'呼び手の行 (\d+)', T30)}、dash では Bad substitution で台が死に閾が立たぬ",
 f"[第73弾 納め 3/4・㋓㋔] ★㋓ ␊は3byte1字。byte切り(cut -b・C の cut -c/${{v:0:N}}・bash printf %.Ns はUTF-8でも)が印の中で切り乙の札にUTF-8不正0xE2を産む {num(r'不正を産んだ走 = (\d+/\d+)', T40)}=乙が甲を退けた理由が下流で戻る★。cut は札にLFを足す {num(r'LF を足した走 = (\d+)', T40)}(甲・現行も同)=第72弾3-1と同族。printf %-Ns は byte詰めで印毎に2字ずれ(raw/42)。★㋔ 値に元から␊が在ると乙の札は注入と区別できぬ {num(r'乙: 区別できぬ対 (\d+/\d+)', T45)}(A/B C/D E/F sha同)=新しい偽り。escape の escape(乙′)なら {num(r'乙′: 区別できぬ対 (\d+/\d+)', T45)}(据ゑず)",
 f"[第73弾 納め 4/4・㋕㋖㋗・疵] ㋕表は紙§6(甲/乙/乙′/丙1 %q/丙2 b64/丙3 数/丙4 刷らぬ×7欄)。推さぬ。丙1は可逆・全封・ASCIIだが札2.5倍・全角０も変り・dashで値が空(rc0)。㋖意味せぬ事七(乙を破つたは偽=乙は宣した事を悉く果たす・破れたのは宣の外)。㋗宣24分(16器×1.48)⇔實は63_sent。疵8=05が308字・25の陽性対照0行(-s無)・47のdash欄誤導・inline python の __pycache__・丙3の制御字誤算 等(紙§9)。監査提出の代送を乞ふ(紙 {P_})",
]
un = [m for m in (yaml.safe_load(open(M + f'/queue/inbox/{ME}.yaml', encoding='utf-8')).get('messages') or []) if not m.get('read')]
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_')); naru = []
if TO not in ROSTER or TO in DEAD or TO == ME: naru.append('宛先')
if un: naru.append(f'己の箱に未読 {len(un)}: {[m["id"] for m in un]}')
for i, b in enumerate(letters, 1):
    if not (40 <= len(b) <= 300): naru.append(f'便{i} 字数 {len(b)}')
    if '?' in b: naru.append(f'便{i} 引けぬ數')
    q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=b.encode('utf-8'), capture_output=True)
    if q.returncode == 10: naru.append(f'便{i} 先送り語')
print('字数', [len(b) for b in letters], '門', naru or '通(0 鳴)')
if DRY or naru:
    K.kaku(OUT + '/62_dry.stdout', f'# DRY={DRY} 門 {naru or "通"} 字数 {[len(b) for b in letters]}\n' + '\n--- \n'.join(letters)); print(open(OUT + '/62_dry.stdout', encoding='utf-8').read()); sys.exit(1 if naru else 0)
rec = [f'箱(送る前・作法⑿③)未読 {len(un)}']
for i, b in enumerate(letters, 1):
    koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    if i == len(letters): rec.append(f'★端点(納め最終便 {i}/{len(letters)} を inbox_write.sh へ渡す直前の date 刻)= {koku}★')
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report', ME], capture_output=True, text=True, cwd=M); rec.append(f'便{i}/{len(letters)} 刻 {koku} inbox_write rc={p.returncode}')
ms = yaml.safe_load(open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8')).get('messages') or []
hits = [[m['id'] for m in ms if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == b] for b in letters]
rec.append(f'★第八の番人(刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")})★: ' + ' | '.join(f'便{i} 箱 {len(h)} 本 {h} 逐語一致 {len(h) == 1}' for i, h in enumerate(hits, 1)))
end = P(re.search(r'端点[^=]*= (\S+)★', '\n'.join(rec)).group(1)); jitsu = (end - P(KI)).total_seconds() / 60 if KI else 0
rec.append(f'★宣⇔實(席基準)★ 起 {KI}(着手便 05 の刻)→ 端点 {end.strftime("%Y-%m-%dT%H:%M:%S")} = 實 {jitsu:.2f} 分 ⇔ 宣 {SEN} 分(宣の刻 {sen_clock.strftime("%H:%M:%S") if sen_clock else "?"}) → 宣−實 {SEN - jitsu:+.2f} 分 = {"＋過大(宣が長い)" if SEN - jitsu > 0 else "−過小(宣が短い)"} / 器 {NKI} 本(宣 16)→ 實 ÷ 器 = {jitsu / NKI:.2f} 分/器(次弾の材料・讀みの刻を含む)')
K.kaku(OUT + '/62_report_body.txt', '\n'.join(f'--- 便{i}/{len(letters)} ({len(b)} 字)\n{b}' for i, b in enumerate(letters, 1))); K.kaku(OUT + '/63_sent.txt', '\n'.join(rec)); print('\n'.join(rec))
sys.exit(0 if all(len(h) == 1 for h in hits) else 3)
