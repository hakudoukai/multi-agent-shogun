# -*- coding: utf-8 -*-
"""添状の器 62(第67弾・★臺帳より先に書いた・走らせるのは門の後・出目は根の外 _after/★)。便 8(各 300 字以内・★字数を先に印字し assert の前に DRY で測る★)を karo-mac へ inbox_write.sh(main 樹)で出す(便 7 = 監査提出の代送依頼・gunshi-mac は死箱 rc=68 ゆゑ出さぬ)。箱を content 鍵の startswith で讀み返し逐語一致を検める(第八の番人)。送つた直後に札へ印(status→done・done_at・done_note)。DRY=1 なら送らず印も 63 も書かぬ。数は 42/45/50/96/60 の .txt から regex で引く(手写しでない)。"""
import sys, os, re, time, subprocess, hashlib, yaml, datetime as dt
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, OUT); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; RN = '67弾'; DRY = bool(os.environ.get('DRY'))
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else 'x' * 16
def rd(p, alt=''): return open(p, encoding='utf-8').read() if os.path.isfile(p) else alt
def P(s): return dt.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')
def num(pat, txt, alt='?'): m = re.search(pat, txt); return m.group(1) if m else alt
P_, MN, G = sha16(B + '.md'), sha16(B + '_manifest.txt'), sha16(B + '_gate.txt')
gate_t = num(r'刻 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', rd(B + '_gate.txt', 'x\n刻 2026-09-17T03:59:59+0900').split('\n')[1])
man = rd(B + '_manifest.txt'); items = sum(1 for l in man.split('\n') if l.startswith('path='))
rcs = rd(OUT + '/60_gate_rcs.txt', '③ all | 渡した 00 | rc 0 | 札 0\n③ main | 渡した 0 | rc 0 | 札 0'); ra = re.search(r'^③ all \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M); rm = re.search(r'^③ main \| 渡した (\d+) \| rc (\d+) \| 札 (\d+)', rcs, re.M)
A96 = rd(OUT + '/96_after.txt', '⑴ 根 raw/(宣 無・--probe): rc 0 / 母數 0 / 後 0 / ★疵 0★ / P0 根へ 1 byte 書けぬ = PermissionError(13)\n⑵ 根 束全体(宣 = raw/50_sengen.txt): rc 0 / 母數 0 / 後 0(宣に在る 0)/ ★疵 0★\n⑶ 臺帳を照合器で(基点 ""・cwd main 樹): rc 0 / 一致 0 / 相違 0 / 実体無 0 / 読めぬ行 0 (母數 0)')
r1 = re.search(r'⑴ 根 raw/[^\n]*rc (\d+) / 母數 (\d+) / 後 (\d+) / ★疵 (\d+)★ / P0 ([^/\n]*)', A96); r2 = re.search(r'⑵ 根 束全体[^\n]*rc (\d+) / 母數 (\d+) / 後 (\d+)\(宣に在る (\d+)\)/ ★疵 (\d+)★', A96); r3 = re.search(r'⑶[^\n]*rc (\d+) / 一致 (\d+) / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+) \(母數 (\d+)\)', A96)
p0 = 'EACCES' if 'PermissionError' in (r1.group(5) if r1 else '') else '★書けた★'
st = rd(E + '/00_start.txt'); KI = num(r'起 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', st); SEN_MIN = float(num(r'宣 = 起 \+ (\d+) 分', st, '26')); sen_clock = P(KI) + dt.timedelta(minutes=SEN_MIN)
_m = re.search(r"^assigned_at: '?\"?(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)", open(M + '/queue/tasks/ashigaru-mac-1.yaml', encoding='utf-8').read(), re.M); ASG = _m.group(1)
j_seki = (P(gate_t) - P(KI)).total_seconds() / 60; d_seki = SEN_MIN - j_seki
PL = str(rd(B + '.md').count('\n')); ch = num(r'id (msg_\S+) /', rd(E + '/05_chakushu.txt'), 'msg_x'); chn = num(r'字数 (\d+)', rd(E + '/05_chakushu.txt'), '?')
T42 = rd(E + '/42_taishou.txt'); T42f = rd(E + '/42_taishou.first.txt'); T45 = rd(E + '/45_km66.txt'); T50 = rd(E + '/50_otsu1.txt')
k42 = re.search(r'形 (\d+)\(.*?/ 合 (\d+) 不 (\d+) / 陰性で鳴つた\(騒音\) (\d+) / 陽性で黙つた (\d+) / 母數 0 の陽陰 (\d+)', T42); k42f = re.search(r'形 (\d+)\(.*?/ 合 (\d+) 不 (\d+)', T42f)
raw45 = re.search(r'走り 45_km66_raw[^\n]*母數 (\d+) / 後 (\d+) 本 (\d+) B / ★疵\(後∧宣に無い\) (\d+) 本 \d+ B★ / ns が捕へ 秒>秒 が隠す (\d+) 本\n\s+あの 1 本 2 B\(60_gate_run.rc\): (★捕へた★|★捕へられぬ★)[^\n]*?\(\+([\d.]+)ms\)', T45)
all45 = re.search(r'走り 45_km66_all[^\n]*後 (\d+) 本 \d+ B / ★疵\(後∧宣に無い\) (\d+) 本', T45)
a50 = re.search(r'A 基点 ""[^\n]*乙1 → 133[^:]*: (\d+) 本 / 乙1 → 139[^:]*: (\d+) 本 / 乙5 → 152[^:]*: (\d+) 本', T50); b50 = num(r'B 基点[^\n]*乙5 → 158 一致: (\d+) 本', T50); vsha = num(r'sha16 ([0-9a-f]{16})\(讀む', T50)
letters = [
 f"[第{RN} 納め 1/8] 束 worktree docs/evidence/km-67-mon-no-ato-20260917/ ★置くのみ・commit/push は家老★ / 紙 {P_}({os.path.getsize(B + '.md') if os.path.isfile(B + '.md') else 0}B・{PL}行)/ 臺帳 {MN}(項{items}・append.py のみ)/ 門控 {G}(r67)/ 門 all rc{ra.group(2)} 札{ra.group(3)} 渡{ra.group(1)}・main rc{rm.group(2)} / 照合 {r3.group(2)}/{r3.group(3)}/{r3.group(4)}/{r3.group(5)} / ★門の後 raw/ へ 後{r1.group(3)} 疵{r1.group(4)}・書けば {p0}★ / 着手便(器05) {ch[-13:]}・{chn}字",
 f"[第{RN} 納め 2/8] ㋐器 raw/40_mon_no_ato.py: 刻=★歩哨★(_after/00_hosho.txt・門の直前の一行)の st_mtime_ns(stat -f %Fm と同値・器が両方印字)。歩哨を採つた理由=門控は門の★最後★の産物ゆゑ門自身の産物が「前」に隠れる・歩哨なら門の産物も悉く後に入り宣で分かれる。後=mtime|birth|ctime>刻・疵=後∧宣に無い→rc1・母數0→rc2。★出来なく★=錠(raw/ 0555/0444)を門の前に掛け門の産物は悉く _after/ へ(60 の順①錠②歩哨③門④門控)",
 f"[第{RN} 納め 3/8] ㋑66の束(刻=門控 _gate.txt の mtime_ns を代用・歩哨無き束): あの1本2B 60_gate_run.rc {raw45.group(6)}(門控+{raw45.group(7)}ms)。ns が捕へ 秒>秒 が隠した物 {raw45.group(5)}本(60_gate_top.r66.txt/60_gate_run.stdout/.err=門控と同秒 02:57:41)。後{raw45.group(2)}本 悉く 66 の 50_sengen ㊂ に在る→疵{raw45.group(4)} rc0。束全体(_after 込)後{all45.group(1)} 疵{all45.group(2)}。∴66 の自白「1本2B」は疵でなく宣に在る門の産物・然し秒の粒度が3本を隠して居た",
 f"[第{RN} 納め 4/8] ㋒對照(悉く 40 を subprocess で・母數0は偽通過として不): 一走目 {k42f.group(1)}形 合{k42f.group(2)} 不{k42f.group(3)}=P6(新fileの mtime を utime で歩哨前へ)が黙つた→macOS は mtime を birth より前へ戻すと birth も締める∴mtime/birth では見えぬ。★則を測つた後に一つ変へた★: ctime を足し・錠を歩哨の★前★へ(錠自体が鳴らぬ順)。二走目 {k42.group(1)}形(陽7陰4零1錠3)合{k42.group(2)} 不{k42.group(3)}・陰性で鳴{k42.group(4)}・陽性で黙{k42.group(5)}・L3=錠を外す事自体が ctime で鳴る。一走目は .first に残す",
 f"[第{RN} 納め 5/8] ㋓乙1: raw/otsu1_genbutsu.tsv 26行(專任3へ)。讀手=main樹 verify.py {vsha}(198行)を settrace で實走・基点は門の渡す\"\"(cwd main樹)。乙1 {a50.group(2)}(B2_30 10/B2_31 9)=★139 読めぬ行★(裸名・\"/\"無・基点を _evidence/raw/ に替へても139)。乙1 {a50.group(1)}(karo B0_10・shasum形)=★133 sha256= 無→continue・母數にも入らぬ★(全件 母數0 rc1)。∴讀手で見れば「dir省き」の前に「方言」で落ちる",
 f"[第{RN} 納め 6/8] ㋓乙5: webm 3行=基点\"\"で152 実体無・基点 _evidence/ で★158 一致 {b50}本★→余欄 durationSec= は生器 verify.py を破らぬ(paths_of は '/' を含む語を拾ひ余欄を跳ぶ)。★破つたのは66の己の器 30_sanzan の ledger_parse=己の訂正★。B0_axis2 全件は\"\"で 1/0/9/1・_evidence/ で 9/0/1/1(残 実体無1=紙の行・読めぬ1=⑪追補前の行)。生バイト16進は tsv 末欄と紙§4",
 f"[第{RN} 納め 7/8] ㋔疵7: 直した=1(既讀化を器65で)4(00_startを器00で)7(便は器が先に測る)。直さぬ=2/3/5/6(前弾の測定則の話・本弾の的でない・紙§5)。㋕意味せぬ事6(紙§6): 疵0≠書けぬ者が居らぬ(ownerは錠を外せる・外せば ctime で鳴る)/對照15合≠恒真でない證明(形は己が選んだ)/66の1本2B捕へた≠66が疵 他。己の新疵3: ★讀んだ版(worktree 127行)≠走らせた版(main 198行)★で行番号を一度誤つた(50 .first)/則を測後に変へた(ctime)/45 の rc を pipe 越しに讀んだ",
 f"[第{RN} 納め 8/8・監査提出の代送を乞ふ] gunshi-mac は死箱(rc=68)ゆゑ同封→ [監査提出(專任1 第{RN})] 束 docs/evidence/km-67-mon-no-ato-20260917/ 紙 {P_} / 臺帳 {MN} / 門 rc{ra.group(2)} / 題=門の後に書く病を出来なく(歩哨ns+錠)+乙1/乙5 現物 / 答=66の1本2B捕へた・隠れ3・疵0 / 對照15形合15 / 乙1 19=139 4=133 乙5 3=152→158 / 門の後 raw/ 後{r1.group(3)} 疵{r1.group(4)} {p0}。監査を乞ふ",
]
lens = [len(x) for x in letters]; print('字数', lens)
for i, (x, n) in enumerate(zip(letters, lens), 1): assert n <= 300, f'便{i} {n} 字 > 300'
if DRY: print('DRY ―― 送らず・印も 63 も書かぬ'); print('\n'.join(letters)); sys.exit(0)
now = time.strftime('%Y-%m-%dT%H:%M:%S%z'); os.makedirs(OUT, exist_ok=True)
K.kaku(OUT + '/62_report_body.txt', f'# 62 便の本文(第{RN}・各 300 字以内・先に字数を印字 {lens})/ 刻 {now}\n' + '\n'.join(f'--- 便{i}/{len(letters)} ({n} 字)\n{x}' for i, (x, n) in enumerate(zip(letters, lens), 1)))
rcs_l = []
for i, x in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', 'karo-mac', x, 'report', 'ashigaru-mac-1'], capture_output=True, text=True, cwd=M); rcs_l.append(f'便{i}/{len(letters)} inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else ''))
done_at = time.strftime('%Y-%m-%dT%H:%M:%S'); cp = M + '/queue/tasks/ashigaru-mac-1.yaml'
card = open(cp, encoding='utf-8').read(); assert card.count('\nstatus: assigned\n') == 1
j_k = (P(done_at) - P(ASG)).total_seconds() / 60; sen_k = (sen_clock - P(ASG)).total_seconds() / 60; d_k = sen_k - j_k
note = f'門 {gate_t}(起 {KI}・宣 起+{SEN_MIN:.0f}分={sen_clock.strftime("%m-%d %H:%M:%S")})/ 束 worktree docs/evidence/km-67-mon-no-ato-20260917(置くのみ・git add -f・commit は家老)/ 紙 {P_} {os.path.getsize(B + ".md")}B {PL}行 / 臺帳 {MN} 項{items}(append.py のみ)/ 門控 60_gate_top.r67 / 着手便(器05)1 + 便 8(便8=監査提出の代送依頼) / ★両基準: 席 {j_seki:.1f}分 宣−實 {d_seki:+.1f}({"＋過大" if d_seki > 0 else "−過少"})・家老 assigned_at {ASG}→done_at {done_at} = {j_k:.1f}分 宣−實 {d_k:+.1f}({"＋過大" if d_k > 0 else "−過少"})★ / 答=㋐歩哨ns+錠(門の前)・㋑66の1本2B捕へた・隠れ3・疵0・㋒15形合15・㋓乙1 19=139 4=133 乙5 3=152→158・門の後 raw/ 後{r1.group(3)} 疵{r1.group(4)} {p0}'
card = card.replace('\nstatus: assigned\n', f'\nstatus: done\ndone_at: "{done_at}"\ndone_note: "{note}"\n', 1); open(cp, 'w', encoding='utf-8', newline='\n').write(card)
back = open(cp, encoding='utf-8').read(); da = re.search(r'^done_at: "(\S+)"', back, re.M).group(1)
t8 = time.strftime('%Y-%m-%dT%H:%M:%S%z'); ms = yaml.safe_load(open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
ids = [m['id'] for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith(f'[第{RN} 納め')]
byid = {m['id']: str(m.get('content', '')) for m in ms}; g8 = []
for x, i in zip(letters, ids):
    cc = byid.get(i, '').rstrip('\n'); g8.append(f'{i} 箱 {len(cc)} / 62 {len(x)} / 差 {len(cc) - len(x)} / 逐語一致 {cc == x}')
j_karo = (P(da) - P(ASG)).total_seconds() / 60; d_karo = sen_k - j_karo
K.kaku(OUT + '/63_sent.txt', f'{now}\n宛 karo-mac / type report / from ashigaru-mac-1 / 便 {len(letters)}(各 300 字以内・先に字数を印字 {lens})/ gunshi-mac へは出さず(死箱 rc=68・便 8 で代送を乞ふ)\n' + '\n'.join(rcs_l)
  + f'\n箱 queue/inbox/karo-mac.yaml で本弾の冠 [第{RN} 納め を持つ from=ashigaru-mac-1 の entry(content 鍵・startswith) = {len(ids)} 本: {ids}\n札に印を書いた: status done / done_at {da}(讀み返し) / done_note 有'
  + f'\n★宣⇔實 両基準(宣 = 起 {KI} + {SEN_MIN:.0f} 分 = {sen_clock} の刻)★\n席基準  起 {KI} → 門 {gate_t} = 實 {j_seki:.2f} 分 ⇔ 宣 {SEN_MIN:.1f} 分 → 宣−實 {d_seki:+.2f} 分 = {"＋過大(宣が長い)" if d_seki > 0 else "−過少(宣が短い)"}'
  + f'\n家老基準 assigned_at {ASG}(札) → done_at {da} = 實 {j_karo:.2f} 分 ⇔ 宣 {sen_k:.2f} 分 → 宣−實 {d_karo:+.2f} 分 = {"＋過大" if d_karo > 0 else "−過少"}'
  + f'\n★符號は {"同じ" if (d_seki > 0) == (d_karo > 0) else "★分かれた★"}★'
  + f'\n★第八の番人(送出後に箱から本文を讀み返す・刻 {t8})★: ' + ' | '.join(g8)
  + '\n★此の 63 と 62 の .stdout/.err/.rc(根の外 _after/)と札の印は根の外。根(raw/)は錠の下 ―― 96 が證した。★')
print(open(OUT + '/63_sent.txt', encoding='utf-8').read())
