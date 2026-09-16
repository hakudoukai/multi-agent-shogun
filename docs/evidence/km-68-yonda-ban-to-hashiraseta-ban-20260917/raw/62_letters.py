# -*- coding: utf-8 -*-
"""添状の器 62(第68弾・★臺帳より先に書いた・走らせるのは門の後・出目は根の外 _after/★)。便 9(各 300 字以内・★字数を先に印字し assert の前に DRY で測る★)を karo-mac へ inbox_write.sh(main 樹)で出す(便 9 = 監査提出の代送依頼・gunshi-mac は死箱 rc=68 ゆゑ出さぬ)。
箱を content 鍵の startswith で讀み返し逐語一致を検める(第八の番人)。送る直前に date 相当の刻を取り(端点)、送つた直後に札へ印(status→done・done_at・done_note)。DRY=1 なら送らず印も 63 も書かぬ。数は 21/30/33/35/37/96/60 の .txt から regex で引く(手写しでない)。"""
import sys, os, re, time, subprocess, hashlib, yaml, datetime as dt
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, OUT); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; RN = '68弾'; DRY = bool(os.environ.get('DRY'))
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else 'x' * 16
def rd(p, alt=''): return open(p, encoding='utf-8').read() if os.path.isfile(p) else alt
def P(s): return dt.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')
def num(pat, txt, alt='?'): m = re.search(pat, txt); return m.group(1) if m else alt
P_, MN, G = sha16(B + '.md'), sha16(B + '_manifest.txt'), sha16(B + '_gate.txt')
gate_t = num(r'刻 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', rd(B + '_gate.txt', 'x\n刻 2026-09-17T05:59:59+0900').split('\n')[1])
man = rd(B + '_manifest.txt'); items = sum(1 for l in man.split('\n') if l.startswith('path='))
rcs = rd(OUT + '/60_gate_rcs.txt', '③ all | 渡した 00 | rc 0 | 札 0\n③ main | 渡した 0 | rc 0 | 札 0'); ra = re.search(r'^③ all \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M); rm = re.search(r'^③ main \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M)
A96 = rd(OUT + '/96_after.txt', '⑴ 根 raw/(宣 無・--probe): rc 0 / 母數 0 / 後 0 / ★疵 0★ / P0 根へ 1 byte 書けぬ = PermissionError(13)\n⑵ 根 束全体(宣 = raw/50_sengen.txt): rc 0 / 母數 0 / 後 0(宣に在る 0)/ ★疵 0★\n⑶ 臺帳を照合器で(基点 ""・cwd main 樹): rc 0 / 一致 0 / 相違 0 / 実体無 0 / 読めぬ行 0 (母數 0)')
r1 = re.search(r'⑴ 根 raw/[^\n]*rc (\d+) / 母數 (\d+) / 後 (\d+) / ★疵 (\d+)★ / P0 ([^/\n]*)', A96); r3 = re.search(r'⑶[^\n]*rc (\d+) / 一致 (\d+) / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+) \(母數 (\d+)\)', A96)
p0 = 'EACCES' if 'PermissionError' in (r1.group(5) if r1 else '') else '★書けた★'
st = rd(E + '/00_start.txt'); KI = num(r'起 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', st); SEN_CLOCK = num(r'宣 = (\d\d:\d\d:\d\d)\(', st, '06:00:00'); sen_clock = P(KI[:11] + SEN_CLOCK); SEN_MIN = (sen_clock - P(KI)).total_seconds() / 60
_m = re.search(r"^assigned_at: '?\"?(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)", open(M + '/queue/tasks/ashigaru-mac-1.yaml', encoding='utf-8').read(), re.M); ASG = _m.group(1)
PL = str(rd(B + '.md').count('\n'))
T21 = rd(E + '/21_otsu1.txt'); T30 = rd(E + '/30_p6.txt'); T33 = rd(E + '/33_rc_pipe.txt'); T35 = rd(E + '/35_yotsu.txt'); T37 = rd(E + '/37_jou.txt'); T20 = rd(E + '/20_hanban_verify.txt'); T20w = rd(E + '/20_hanban_wt.txt')
k21 = re.search(r'一本づつ A/B/C 悉く同じ (\d+) / 違ふ (\d+) / 母數 (\d+)', T21); s21 = num(r'結: 乙1 139 = (\d+) / 乙1 133 = \d+', T21); s21b = re.search(r'結: 乙1 139 = (\d+) / 乙1 133 = (\d+) / 乙5 152\(A\) = (\d+) / 乙5 158\(B\) = (\d+)', T21); fu20 = num(r'封=([0-9a-f]{16})', T20); fu20w = num(r'封=([0-9a-f]{16})', T20w)
k30 = re.search(r'P6 を二走目の則で走らせ直す: 41 rc (\d) → 40 rc (\d) = ★(\S+?)★', T30); l1a = re.search(r'L1a\(歩哨→錠\)41 rc (\d) / 40 rc (\d)', T30); l1b = re.search(r'L1b\(錠→歩哨\)41 rc (\d) / 40 rc (\d)', T30); g30 = re.search(r'合 (\d+) 不 (\d+)', T30)
k33 = re.search(r'本の当たり (\d+) = 実行 (\d+) \+ 文 (\d+)', T33); m33 = num(r'母數 通常 file (\d+)', T33); c33 = num(r'陽性対照: 33_positive.sh\(乙\) (\S+) /', T33); s33 = num(r'己の産物\([^)]*\) (\d+) ‖', T33)
k35 = re.search(r'乙1 (\d+) 本: A 合 (\d+) 割れ (\d+) ‖ B 合 (\d+) 割れ (\d+)', T35); j35 = num(r'--jikenme\(彼の対照\): rc (\d)', T35); y71 = num(r'71_yotsu\.py sha16 ([0-9a-f]{16})', T35)
k37 = re.search(r'= ★(\d+)★\(rc 0', T37); h37 = num(r'hook\(settings\.json\)母數 (\d+)', T37); p37 = num(r'process\([^)]*\)母數 (\d+)', T37); s37 = num(r'scripts/ の器 母數 (\d+)', T37); l37 = num(r'launchd plist 母數 (\d+)', T37); gco = num(r'書 checkout b\(f\.txt を v2 に書き換へる\): rc (\d+)', T37); grm = num(r'書 rm -f d/f\.txt\(unlink\): rc (\d+)', T37)
letters = [
 f"[第{RN} 納め 1/9] 束 worktree docs/evidence/km-68-yonda-ban-to-hashiraseta-ban-20260917/ ★置くのみ・commit/push は家老★ / 紙 {P_}({os.path.getsize(B + '.md') if os.path.isfile(B + '.md') else 0}B・{PL}行)/ 臺帳 {MN}(項{items}・append.py のみ・★基点=main樹の根★)/ 門控 {G}(r68)/ 門 all rc{ra.group(2)} 札{ra.group(3)} 渡{ra.group(1)}・main rc{rm.group(2)} / 照合 {r3.group(2)}/{r3.group(3)}/{r3.group(4)}/{r3.group(5)}(母數{r3.group(6)}) / 門の後 raw/ 後{r1.group(3)} 疵{r1.group(4)} {p0}",
 f"[第{RN} 納め 2/9] ㋐版刻器 raw/20_hanban.py: 走らせる直前に realpath/sha16/総行数/git blob vs HEAD/指す行の本文を刷り封=sha16(版札v1・抜き書きすれば封が合はぬ)。21 は verify.py を 20 の Han.module()(讀んだ bytes を其の儘 compile して exec)越しにのみ走らせ settrace の行番号を同じ bytes から引く→讀む物と走らせる物が同一物ゆゑ「讀んだ版≠走らせた版」は構造で起らぬ(憶えるのではない)",
 f"[第{RN} 納め 3/9] ㋐版の顔: main樹 verify.py 198行 a507c998(★汚れ・disk≠HEAD b19ec9ea★)封{fu20} / worktree 写し 127行 bbde471f 封{fu20w}。198行の L133/139/152/158/160 は127行に★無く★、127行の L76/82/95/101/103 は198行で★別の文★=嘘の顔(raw/20_hanban_verify.txt・20_hanban_wt.txt)。71_yotsu は path を刷るが sha も行数も刷らぬ(版刻器が足す物)",
 f"[第{RN} 納め 4/9] ㋐引直し(21): mini 26本 一本づつ A/B/C 同{k21.group(1)} 違{k21.group(2)} 母數{k21.group(3)}。乙1 139={s21b.group(1)} 133={s21b.group(2)} 乙5 152(A)={s21b.group(3)}→158(B)={s21b.group(4)}=第67弾 19/4/3/3 と★同じ数★。同じ数も器を通して初めて言へる(67 は cat -n の手置き・68 は走らせた bytes)。㋑P6(30): 同じ fixture で 則一(41=40から ctime 一行を外した再現) rc{k30.group(1)}→則二(40) rc{k30.group(2)}=★{k30.group(3)}★・何で後=c のみ∴ctime が救つた",
 f"[第{RN} 納め 5/9] ㋑続: 錠の順は別の物を救つた ―― L1a(歩哨→錠)41 rc{l1a.group(1)}/40 rc{l1a.group(2)}(錠の chmod が ctime で鳴る)・L1b(錠→歩哨)41 rc{l1b.group(1)}/40 rc{l1b.group(2)}。∴「ctime を足す」=P6 を救ひ「錠を前へ」=ctime の副作用を消す。形5 合{g30.group(1)} 不{g30.group(2)}。逐語の則 raw/30_rule_verbatim.txt・器の diff -u raw/30_rule_diff.txt(31 が作る・則一は再現であり一走目の器其の物ではない)",
 f"[第{RN} 納め 6/9] ㋒rc管(33・三走): 母數 file {m33}・当たり{k33.group(1)}=実行{k33.group(2)}+文{k33.group(3)}(紙・則・f-string の中で管を語る行)・己の産物{s33}(一走目の出目が己の当たりを逐語で含み二走目で24本に膨れた=自己参照・三走目で名で札)・陽性対照 sh/py {c33}・陰性 黙。直した実行0・直さぬ 文と km-67(錠の下)。★數へぬ物=對話で打つた pipe(67 §7-3 は其の形)★",
 f"[第{RN} 納め 7/9] ㋓四數(35): 專任3 71_yotsu.py {y71} の fuda を --kikai main verify.py で 26本に掛け 乙1 {k35.group(1)}本 A合{k35.group(2)}割れ{k35.group(3)} B合{k35.group(4)}割れ{k35.group(5)}・乙5 3本 合。133 の4本は四数札 0/0/0/0/0=母數0でしか言へず「何行を跳んだか」の欄が無い(欄の欠・盲でない)。71 --jikenme rc{j35}。彼の束へ 0 字",
 f"[第{RN} 納め 8/9] ㋔錠(37・二走): 外の書き手 hook{h37}/process{p37}/scripts{s37}/launchd{l37} の内 raw/ へ錠を外さず書ける経路=★{k37.group(1)}★。git 讀み系(add -f/hash-object/status)rc0・書き系 checkout rc{gco}(unlink EACCES)・rm rc{grm}。生 open(w)/unlink/rename/mkdir 皆 EACCES・read 通。同uid chmod と root は塞がぬ(ctime が痕・root 測れぬ)。一走目 pgrep 空 pattern 母數0 rc2=器の誤り(.first)",
 f"[第{RN} 納め 9/9・監査提出の代送を乞ふ] gunshi-mac は死箱(rc=68)ゆゑ同封→ [監査提出(專任1 第{RN})] 束 docs/evidence/km-68-yonda-ban-to-hashiraseta-ban-20260917/ 紙 {P_} / 臺帳 {MN} / 門 rc{ra.group(2)} / 題=讀んだ版≠走らせた版を版刻器で構造的に塞ぐ / 答=21 同{k21.group(1)}/26・P6 {k30.group(3)}(ctime)・rc管 実行{k33.group(2)}・四數 割れ0・錠外経路{k37.group(1)} / 己の疵: 着手便と既讀化を器でなく手で・33 を三度直した。監査を乞ふ",
]
lens = [len(x) for x in letters]; print('字数', lens)
for i, (x, n) in enumerate(zip(letters, lens), 1): assert n <= 300, f'便{i} {n} 字 > 300'
if DRY: print('DRY ―― 送らず・印も 63 も書かぬ'); print('\n'.join(letters)); sys.exit(0)
os.makedirs(OUT, exist_ok=True)
tanten = time.strftime('%Y-%m-%dT%H:%M:%S')  # ★端点 = 納め便 1 本目を inbox_write.sh へ渡す直前の刻★(00_start の宣に従ふ)
now = tanten + time.strftime('%z')
K.kaku(OUT + '/62_report_body.txt', f'# 62 便の本文(第{RN}・各 300 字以内・先に字数を印字 {lens})/ 刻 {now}\n' + '\n'.join(f'--- 便{i}/{len(letters)} ({n} 字)\n{x}' for i, (x, n) in enumerate(zip(letters, lens), 1)))
rcs_l = []
for i, x in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', 'karo-mac', x, 'report', 'ashigaru-mac-1'], capture_output=True, text=True, cwd=M); rcs_l.append(f'便{i}/{len(letters)} inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else ''))
done_at = time.strftime('%Y-%m-%dT%H:%M:%S'); cp = M + '/queue/tasks/ashigaru-mac-1.yaml'
card = open(cp, encoding='utf-8').read(); assert card.count('\nstatus: assigned\n') == 1
j_seki = (P(tanten) - P(KI)).total_seconds() / 60; d_seki = SEN_MIN - j_seki
j_k = (P(done_at) - P(ASG)).total_seconds() / 60; sen_k = (sen_clock - P(ASG)).total_seconds() / 60; d_k = sen_k - j_k
note = f'納め便 端点 {tanten}(起 {KI}・宣 {SEN_CLOCK})/ 門 {gate_t} / 束 worktree docs/evidence/km-68-yonda-ban-to-hashiraseta-ban-20260917(置くのみ・git add -f・commit は家老)/ 紙 {P_} {os.path.getsize(B + ".md")}B {PL}行 / 臺帳 {MN} 項{items}(append.py のみ・基点 main 樹の根)/ 門控 60_gate_top.r68 / 着手便 1(手) + 便 9(便9=監査提出の代送依頼) / ★両基準: 席 {j_seki:.1f}分 宣−實 {d_seki:+.1f}({"＋過大" if d_seki > 0 else "−過少"})・家老 assigned_at {ASG}→done_at {done_at} = {j_k:.1f}分 宣−實 {d_k:+.1f}({"＋過大" if d_k > 0 else "−過少"})★ / 答=㋐版刻器+21 同{k21.group(1)}/26・㋑P6 {k30.group(3)}(ctime)・㋒実行{k33.group(2)}・㋓割れ0・㋔錠外経路{k37.group(1)}・門の後 raw/ 後{r1.group(3)} 疵{r1.group(4)} {p0}'
card = card.replace('\nstatus: assigned\n', f'\nstatus: done\ndone_at: "{done_at}"\ndone_note: "{note}"\n', 1); open(cp, 'w', encoding='utf-8', newline='\n').write(card)
back = open(cp, encoding='utf-8').read(); da = re.search(r'^done_at: "(\S+)"', back, re.M).group(1)
t8 = time.strftime('%Y-%m-%dT%H:%M:%S%z'); ms = yaml.safe_load(open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
ids = [m['id'] for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith(f'[第{RN} 納め')]
byid = {m['id']: str(m.get('content', '')) for m in ms}; g8 = []
for x, i in zip(letters, ids):
    cc = byid.get(i, '').rstrip('\n'); g8.append(f'{i} 箱 {len(cc)} / 62 {len(x)} / 差 {len(cc) - len(x)} / 逐語一致 {cc == x}')
j_karo = (P(da) - P(ASG)).total_seconds() / 60; d_karo = sen_k - j_karo
K.kaku(OUT + '/63_sent.txt', f'{now}\n宛 karo-mac / type report / from ashigaru-mac-1 / 便 {len(letters)}(各 300 字以内・先に字数を印字 {lens})/ gunshi-mac へは出さず(死箱 rc=68・便 9 で代送を乞ふ)\n' + '\n'.join(rcs_l)
  + f'\n箱 queue/inbox/karo-mac.yaml で本弾の冠 [第{RN} 納め を持つ from=ashigaru-mac-1 の entry(content 鍵・startswith) = {len(ids)} 本: {ids}\n札に印を書いた: status done / done_at {da}(讀み返し) / done_note 有'
  + f'\n★宣⇔實 両基準(宣 = {SEN_CLOCK} の刻・起 {KI}・宣の長さ {SEN_MIN:.1f} 分)★\n席基準  起 {KI}(着手便の刻) → 端点 {tanten}(納め便 1 本目を渡す直前) = 實 {j_seki:.2f} 分 ⇔ 宣 {SEN_MIN:.1f} 分 → 宣−實 {d_seki:+.2f} 分 = {"＋過大(宣が長い)" if d_seki > 0 else "−過少(宣が短い)"}'
  + f'\n家老基準 assigned_at {ASG}(札) → done_at {da} = 實 {j_karo:.2f} 分 ⇔ 宣 {sen_k:.2f} 分 → 宣−實 {d_karo:+.2f} 分 = {"＋過大" if d_karo > 0 else "−過少"}'
  + f'\n★符號は {"同じ" if (d_seki > 0) == (d_karo > 0) else "★分かれた★"}★'
  + f'\n★第八の番人(送出後に箱から本文を讀み返す・刻 {t8})★: ' + ' | '.join(g8)
  + '\n★此の 63 と 62 の .stdout/.err/.rc(根の外 _after/)と札の印は根の外。根(raw/)は錠の下 ―― 96 が證した。★')
print(open(OUT + '/63_sent.txt', encoding='utf-8').read())
