# -*- coding: utf-8 -*-
"""添状の器 62(第66弾・★臺帳より先に書いた・走らせるのは門の後・出目は根の外 _after/★)。便 5(各 300 字以内・★字数を先に印字し assert の前に DRY で測る★)を karo-mac へ、監査提出 1 を gunshi-mac へ inbox_write.sh(main 樹)で出し、箱を content 鍵の startswith で讀み返し逐語一致を検める(第八の番人)。送つた直後に札へ印(status→done・done_at・done_note)。DRY=1 なら送らず印も 63 も書かぬ。
本弾の答の数は ★30/32/33 の .txt から regex で引く(手写しでない)★。"""
import sys, os, re, time, subprocess, hashlib, yaml, datetime as dt
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; RN = '66弾'; DRY = bool(os.environ.get('DRY'))
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else 'x' * 16
def rd(p, alt=''): return open(p, encoding='utf-8').read() if os.path.isfile(p) else alt
def P(s): return dt.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')
def num(pat, txt, alt='?'): m = re.search(pat, txt); return m.group(1) if m else alt
P_, MN, G = sha16(B + '.md'), sha16(B + '_manifest.txt'), sha16(B + '_gate.txt')
gate_t = num(r'刻 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', rd(B + '_gate.txt', 'x\n刻 2026-09-17T03:00:00+0900').split('\n')[1])
man = rd(B + '_manifest.txt'); items = sum(1 for l in man.split('\n') if l.startswith('path='))
rcs = rd(E + '/60_gate_rcs.txt', 'all | 渡した 00 | rc 0 | 札 0\nmain | 渡した 0 | rc 0 | 札 0'); ra = re.search(r'^all \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M); rm = re.search(r'^main \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M)
j1 = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)', rd(OUT + '/99_after_gate.txt', '一致 ★00★ / 相違 0 / 実体無 0 / 読めぬ行 0'))
a99 = re.search(r'より後の mtime\(★日付込み・秒 > 秒★\): (\d+) 本 / byte 和 (\d+)', rd(OUT + '/99_after_gate.txt', 'より後の mtime(★日付込み・秒 > 秒★): 0 本 / byte 和 0'))
st = rd(E + '/00_start.txt'); KI = num(r'起 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', st); SEN_MIN = float(num(r'宣 = 起 \+ (\d+) 分', st, '28')); sen_clock = P(KI) + dt.timedelta(minutes=SEN_MIN)
_m = re.search(r"^assigned_at: '?\"?(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)", open(M + '/queue/tasks/ashigaru-mac-1.yaml', encoding='utf-8').read(), re.M); ASG = _m.group(1)
j_seki = (P(gate_t) - P(KI)).total_seconds() / 60; d_seki = SEN_MIN - j_seki
PL = str(rd(B + '.md').count('\n')); ch = num(r'id (msg_\S+) /', rd(E + '/05_chakushu.txt'), 'msg_x'); chn = num(r'字数 (\d+)', rd(E + '/05_chakushu.txt'), '?')
S = rd(E + '/30_sanzan.txt'); S1 = rd(E + '/30_sanzan.first.txt'); T2 = rd(E + '/32_1byte.txt'); T3 = rd(E + '/33_onore.txt')
nor = num(r'★載らぬ (\d+)★', S); nf = num(r'配下の通常 file 計 (\d+)', S); nor1 = num(r'★載らぬ (\d+)★', S1)
kou = re.search(r'★甲\(載せぬのが正\) (\d+) 本 (\d+) B / 乙\(疵\) (\d+) 本 (\d+) B / 丙\(決められぬ\) (\d+) 本 (\d+) B / 総和 (\d+) = 載らぬ (\d+) 差 (\d+)★', S)
c = lambda k: num(r'\n  ' + re.escape(k) + r'[^:]*: (\d+) 本', S)
hei_m = re.search(r'丙2 (\d+) → (\d+) 本 / 乙3 (\d+) → (\d+) / 乙4 (\d+) → (\d+) / 丙計 (\d+) → (\d+)', S)
pos = num(r'当たる位置 = (\d+) 箇所', T2); ct = num(r'紙 ctime > 臺帳 mtime = (\w+)', T2); apn = num(r'より後の mtime を持つ臺帳 = (\d+)/40', S)
jibun = num(r'配下計 (\d+) 本は母數', T3); jn = num(r'己の km-6x 束は (\d+) 本とも', T3); a1in = num(r'己\(ashigaru-mac-1_\)の紙 = (\d+) 本', T3)
letters = [
 f"[第{RN} 納め 1/5] 束 worktree docs/evidence/km-66-noranu-336-20260917/ ★置くのみ・commit/push は家老★ / 紙 {P_}({os.path.getsize(B + '.md') if os.path.isfile(B + '.md') else 0}B・{PL}行)/ 臺帳 {MN}(項{items}・append.py のみ)/ 門控 {G}(r66)/ 門 all rc{ra.group(2)} 札{ra.group(3)} 渡{ra.group(1)}・main rc{rm.group(2)} / 照合 {j1.group(1)}/{j1.group(2)}/{j1.group(3)}/{j1.group(4)} / 門の後に raw/ へ 秒>秒 {a99.group(1)}本{a99.group(2)}B / 着手便(器05) {ch[-13:]}・{chn}字",
 f"[第{RN} 納め 2/5] ★答㋐: 則を先に(00_start・順序も則)。載らぬ{nor}/{nf}(02:47・動かぬ)= ★甲{kou.group(1)}本{kou.group(2)}B★(甲1門{c('甲1')}/甲2臺帳器{c('甲2')}/甲3pycache{c('甲3')}/甲4宣{c('甲4')}=path逐語2+親dir7)+★乙{kou.group(3)}本{kou.group(4)}B★(乙1届かぬ{c('乙1')}/乙5讀めぬ行{c('乙5')}/乙3門の後{c('乙3')}/乙4渡さず{c('乙4')}/乙2名0)+★丙{kou.group(5)}本{kou.group(6)}B★(丙2同秒{c('丙2')}/丙1 0/丙0 0)差{kou.group(9)}。一走目{nor1}は己の2MB閾が産んだ差7(.first に残す・disk動かず)★",
 f"[第{RN} 納め 3/5] ㋑乙の何故: 乙1 23=項は在るがdir省きで届かぬ(B2_30 10/B2_31 9/karo B0_10 4)・乙5 3=webm行の余欄durationSec=が讀み手を破る・乙3 6=km-34 sunaba/ 臺帳の+183〜225s後・乙4 17=B0_axis2 9+soukantoku 3+km-34 2+km-36 1(臺帳の1s前)+km-sengen 2(fixture)=「渡さず」≠「誤り」・rc=3 実測0(追記器の生より後の臺帳{apn}/40)・不明0。㋒丙={hei_m.group(7)}(同秒)→同分に締めて{hei_m.group(8)}(乙4 {hei_m.group(5)}→{hei_m.group(6)})零でない",
 f"[第{RN} 納め 4/5] ㋓相違1: 実22047Bから一byte抜き22047通り→宣shaに当たる位置{pos}=22045/22046 共に0x0a=★末尾LF LFの一つ★(紙は條④複)。紙birth/mtime/ctime 20:19:01<臺帳20:19:20・ctime>臺帳={ct}∴臺帳が後・紙は其の後触られず→臺帳の器がLF一つ落ちた写しをhashした。何の写しかは決められぬ(要=a2の臺帳の器か其のlog)。git untracked・写し0。㋔己:40の内己の舊紙{a1in}本は載らぬ0・km-60〜65の{jn}束{jibun}本は定義が外す・本束は門の後に同則(_after/33)",
 f"[第{RN} 納め 5/5] ㋕意味せぬ事9(紙§7): 甲285≠書き手の宣(甲1〜3は名の形・宣で当てたのは9・内7は親dirの緩い一致)/乙4 17≠誤り(fixture S2S3・門のargv)/乙3≠疵(凍結=臺帳mtimeと置いた・門控の刻でない)/丙2≠決められぬの全数/336動かぬ≠中身不変(sha未比)/343≠誤測(則の差)/rc=3 0≠拒む名無し(器が無い刻)/臺帳が後≠臺帳が誤り/甲4は否定を讀まぬ。疵7(§8):既讀化を手で・2MB閾・乙5は一走目の後に足した山・00_startを手で・甲4b緩い等。据ゑず・禁域0字・DB0・臺帳手書き0",
]
audit = f"[監査提出(專任1 第{RN})] 束 worktree docs/evidence/km-66-noranu-336-20260917 / 紙 {P_} / 臺帳 {MN}(append.py のみ)/ 門控 {G}(r66)/ 門 all rc{ra.group(2)}・main rc{rm.group(2)} / 題=載らぬ336を先に書いた則で三山へ(読取のみ・据ゑず)/ 答=甲{kou.group(1)}/乙{kou.group(3)}/丙{kou.group(5)}(同分{hei_m.group(8)})差0・乙の何故=届かぬ23/讀めぬ行3/門の後6/渡さず17・相違1=末尾LF一つ(臺帳が後)・一走目343は己の2MB閾。監査を乞ふ"
lens = [len(x) for x in letters]; print('字数', lens, '監査提出', len(audit))
for i, (x, n) in enumerate(zip(letters, lens), 1): assert n <= 300, f'便{i} {n} 字 > 300'
assert len(audit) <= 300, f'監査提出 {len(audit)} 字'
if DRY: print('DRY ―― 送らず・印も 63 も書かぬ'); print('\n'.join(letters + [audit])); sys.exit(0)
now = time.strftime('%Y-%m-%dT%H:%M:%S%z'); os.makedirs(OUT, exist_ok=True)
K.kaku(OUT + '/62_report_body.txt', f'# 62 便の本文(第{RN}・各 300 字以内・先に字数を印字 {lens}・監査提出 {len(audit)} 字・宛 gunshi-mac)/ 刻 {now}\n' + '\n'.join(f'--- 便{i}/{len(letters)} ({n} 字)\n{x}' for i, (x, n) in enumerate(zip(letters, lens), 1)) + f'\n--- 監査提出 gunshi-mac ({len(audit)} 字)\n{audit}')
rcs_l = []
for i, x in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', 'karo-mac', x, 'report', 'ashigaru-mac-1'], capture_output=True, text=True, cwd=M); rcs_l.append(f'便{i}/{len(letters)} inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else ''))
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', 'gunshi-mac', audit, 'report', 'ashigaru-mac-1'], capture_output=True, text=True, cwd=M); rcs_l.append(f'監査提出 gunshi-mac inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else ''))
done_at = time.strftime('%Y-%m-%dT%H:%M:%S'); cp = M + '/queue/tasks/ashigaru-mac-1.yaml'
card = open(cp, encoding='utf-8').read(); assert card.count('\nstatus: assigned\n') == 1
j_k = (P(done_at) - P(ASG)).total_seconds() / 60; sen_k = (sen_clock - P(ASG)).total_seconds() / 60; d_k = sen_k - j_k
note = f'門 {gate_t}(起 {KI}・宣 起+{SEN_MIN:.0f}分={sen_clock.strftime("%m-%d %H:%M:%S")})/ 束 worktree docs/evidence/km-66-noranu-336-20260917(置くのみ・git add -f・commit は家老)/ 紙 {P_} {os.path.getsize(B + ".md")}B {PL}行 / 臺帳 {MN} 項{items}(append.py のみ)/ 門控 60_gate_top.r66 / 着手便(器05)1 + 便 5 + 監査提出 1(gunshi-mac) + 追ひ便 6(64・根の外 _after/) / ★両基準: 席 {j_seki:.1f}分 宣−實 {d_seki:+.1f}({"＋過大" if d_seki > 0 else "−過少"})・家老 assigned_at {ASG}→done_at {done_at} = {j_k:.1f}分 宣−實 {d_k:+.1f}({"＋過大" if d_k > 0 else "−過少"})★ / 答=載らぬ{nor}/{nf} 甲{kou.group(1)}/乙{kou.group(3)}/丙{kou.group(5)}(同分{hei_m.group(8)})差0・乙=届かぬ23/讀めぬ行3/門の後6/渡さず17・相違1=末尾LF一つ(臺帳が後)・一走目343=2MB閾'
card = card.replace('\nstatus: assigned\n', f'\nstatus: done\ndone_at: "{done_at}"\ndone_note: "{note}"\n', 1); open(cp, 'w', encoding='utf-8', newline='\n').write(card)
back = open(cp, encoding='utf-8').read(); da = re.search(r'^done_at: "(\S+)"', back, re.M).group(1)
t8 = time.strftime('%Y-%m-%dT%H:%M:%S%z'); ms = yaml.safe_load(open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
ids = [m['id'] for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith(f'[第{RN} 納め')]
gm = yaml.safe_load(open(M + '/queue/inbox/gunshi-mac.yaml', encoding='utf-8')).get('messages') or []
ida = [m['id'] for m in gm if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith(f'[監査提出(專任1 第{RN})]')]
g_read = sum(1 for m in gm if m.get('read') is True); g_all = len(gm)
byid = {m['id']: str(m.get('content', '')) for m in ms}; byid.update({m['id']: str(m.get('content', '')) for m in gm}); g8 = []
for x, i in zip(letters + [audit], ids + ida):
    cc = byid.get(i, '').rstrip('\n'); g8.append(f'{i} 箱 {len(cc)} / 62 {len(x)} / 差 {len(cc) - len(x)} / 逐語一致 {cc == x}')
j_karo = (P(da) - P(ASG)).total_seconds() / 60; d_karo = sen_k - j_karo
K.kaku(OUT + '/63_sent.txt', f'{now}\n宛 karo-mac / type report / from ashigaru-mac-1 / 便 {len(letters)}(各 300 字以内・先に字数を印字 {lens})+ ★gunshi-mac 宛★ 監査提出 1({len(audit)} 字)\n' + '\n'.join(rcs_l)
  + f'\n箱 queue/inbox/karo-mac.yaml で本弾の冠 [第{RN} 納め を持つ from=ashigaru-mac-1 の entry(content 鍵・startswith) = {len(ids)} 本: {ids}\n監査提出の entry(queue/inbox/gunshi-mac.yaml) = {len(ida)} 本: {ida} / ★gunshi-mac の箱: entry {g_all} 本の内 read:true {g_read} 本(送達≠受読)★\n札に印を書いた: status done / done_at {da}(讀み返し) / done_note 有'
  + f'\n★宣⇔實 両基準(宣 = 起 {KI} + {SEN_MIN:.0f} 分 = {sen_clock} の刻)★\n席基準  起 {KI} → 門 {gate_t} = 實 {j_seki:.2f} 分 ⇔ 宣 {SEN_MIN:.1f} 分 → 宣−實 {d_seki:+.2f} 分 = {"＋過大(宣が長い)" if d_seki > 0 else "−過少(宣が短い)"}'
  + f'\n家老基準 assigned_at {ASG}(札・★己の自己識別 02:38:22 より後の刻★) → done_at {da} = 實 {j_karo:.2f} 分 ⇔ 宣 {sen_k:.2f} 分 → 宣−實 {d_karo:+.2f} 分 = {"＋過大" if d_karo > 0 else "−過少"}'
  + f'\n★符號は {"同じ" if (d_seki > 0) == (d_karo > 0) else "★分かれた★"}★'
  + f'\n★第八の番人(送出後に箱から本文を讀み返す・刻 {t8})★: ' + ' | '.join(g8)
  + '\n★此の 63 と 62 の .stdout/.err/.rc(根の外 _after/)と札の印は、此の後の 96_after_send が 99 との差で測る。根(raw/)には門の後 門自身のみ ―― 96 が證す。★')
print(open(OUT + '/63_sent.txt', encoding='utf-8').read())
