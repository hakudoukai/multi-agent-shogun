# -*- coding: utf-8 -*-
"""紙を書く器 70(第67弾)―― 本文は此処に固定し kaki で <束>.md へ置く(行末空白 0・CR 0・EOF 改行 1)。★表(對照 二走・乙1/乙5 現物・66 の後の列)は 42/45/50 の出目から器が引く(手写しでない)★。数は各 .txt から regex で引き、引けねば落ちる。argv[1] = 束の prefix。"""
import sys, os, re
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; sys.path.insert(0, E); import kaki as K
def rd(p): return open(p, encoding='utf-8').read()
def num(pat, txt): m = re.search(pat, txt); assert m, pat; return m.group(1)
T42 = rd(E + '/42_taishou.txt'); T42f = rd(E + '/42_taishou.first.txt'); T45 = rd(E + '/45_km66.txt'); T50 = rd(E + '/50_otsu1.txt'); ST = rd(E + '/00_start.txt'); T45f = rd(E + '/45_km66.first.txt')
tsv = [l.rstrip('\n').split('\t') for l in open(E + '/otsu1_genbutsu.tsv', encoding='utf-8')][1:]; assert len(tsv) == 26
def short(s, n): s = s.replace('|', '｜'); return s if len(s) <= n else s[:n - 1] + '…'
tab42 = '\n'.join(l for l in T42.split('\n') if l.startswith('|')); tab42f = '\n'.join(l for l in T42f.split('\n') if l.startswith('|'))
k42 = re.search(r'形 (\d+)\(.*?/ 合 (\d+) 不 (\d+) / 陰性で鳴つた\(騒音\) (\d+) / 陽性で黙つた (\d+) / 母數 0 の陽陰 (\d+)', T42); k42f = re.search(r'形 (\d+)\(.*?/ 合 (\d+) 不 (\d+) / 陰性で鳴つた\(騒音\) (\d+) / 陽性で黙つた (\d+)', T42f)
raw45 = re.search(r'走り 45_km66_raw[^\n]*母數 (\d+) / 後 (\d+) 本 (\d+) B / ★疵\(後∧宣に無い\) (\d+) 本 \d+ B★ / ns が捕へ 秒>秒 が隠す (\d+) 本\n\s+あの 1 本 2 B\(60_gate_run.rc\): (★捕へた★|★捕へられぬ★)[^\n]*?\(\+([\d.]+)ms\)', T45); assert raw45
all45 = re.search(r'走り 45_km66_all[^\n]*母數 (\d+) / 後 (\d+) 本 (\d+) B / ★疵\(後∧宣に無い\) (\d+) 本', T45); assert all45
ato45 = '\n'.join('  ' + l.strip() for l in T45.split('\n')[2:8] if l.strip().startswith('後'))
gate66ns = num(r'mtime_ns (\d+)', T45)
a50 = re.search(r'A 基点 ""[^\n]*乙1 → 133[^:]*: (\d+) 本 / 乙1 → 139[^:]*: (\d+) 本 / 乙5 → 152[^:]*: (\d+) 本', T50); assert a50; b50 = num(r'B 基点[^\n]*乙5 → 158 一致: (\d+) 本', T50); vsha = num(r'sha16 ([0-9a-f]{16})\(讀む', T50)
led50 = '\n'.join('  ' + l.strip() for l in T50.split('\n') if l.strip().startswith(('ashigaru-mac-2_', 'karo_mac_')) and 'manifest.txt:' in l)
hex50 = '\n'.join('  ' + l.strip() for l in T50.split('\n') if re.match(r'\s+ashigaru-mac-2_B0_axis2_20260908\.md L\d+ \d+ B: [0-9a-f]+$', l))
KI = num(r'起 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', ST); SEN = num(r'宣 = 起 \+ (\d+) 分', ST); SENC = num(r'宣 = 起 \+ \d+ 分 = (\d\d:\d\d:\d\d) に門', ST)
rows = '\n'.join(f'| {r[0]} | {short(r[1], 34)} | {r[2]} | `{short(r[3], 60)}` | {short(r[4], 44)} | {r[5]} | {r[7]} | {short(r[8], 26)} | {r[9]} {r[10]} | {r[11]} {r[12]} | {r[13]} {r[14]} |' for r in tsv)
n133 = sum(1 for r in tsv if r[9] == '133'); n139 = sum(1 for r in tsv if r[9] == '139'); n152 = sum(1 for r in tsv if r[9] == '152'); assert (n133, n139, n152) == (4, 19, 3), (n133, n139, n152)
T = f'''# 第67弾 ―― 憶えて居れば防げる疵は、まだ塞がつて居らぬ ―― 門の後に書く病を「出来なく」し、乙1 の 23 と乙5 の 3 を現物へ固める(読取のみ・生器へ 0 字・他席の臺帳へ 0 字)―― 答を先に(★數の出處 = raw/40_mon_no_ato.py(捕へ器)/ raw/42_taishou.{{txt,tsv}} + .first(對照 二走)/ raw/45_km66*.txt + .first(66 の束へ)/ raw/50_otsu1.txt + raw/otsu1_genbutsu.tsv(乙1/乙5 現物・專任3 へ渡す一枚)/ raw/00_start.txt(起・宣・★則の逐語★)/ _after/96_after.txt(門の後の實走 ―― 紙の後に生れる故 紙は其の数を書けぬ・期待のみ書く)★)

★答★: ㋐ 捕へ器 raw/40_mon_no_ato.py ―― 刻は ★歩哨★(門の直前に一行書く file)の st_mtime_ns。秒でなく ns。歩哨を採つた理由 = 門控は門の★最後★の産物ゆゑ、門控を刻にすると門自身の産物(60_gate_*.err 等)が「前」に隠れ、後の集合が門の産物を隠す。歩哨なら門の産物も悉く「後」に入り、宣に在るか無いかで割れる ∴ ★疵 = 後 ∧ 宣に無い★ が過不足なく出る。後 = mtime | birth | ctime のいづれかが刻より後。rc 2 = 母數 0(歩いて居らぬ・通でも鳴でもない)/ rc 1 = 疵 ≥ 1 / rc 0 = 疵 0。★出来なく★ = 60 が門の★前★に raw/ と配下を 0555/0444 に錠し(書けば EACCES)、門の産物は悉く _after/(根の外)へ置く ―― 66 の「1 本 2 B」は 10_run が門の後に raw/ へ書いた形で、本弾では其の経路が無い。㋑ 66 の束へ(刻 = 門控 _gate.txt の mtime_ns を代用): あの 1 本 2 B(60_gate_run.rc)は ★{raw45.group(6)}★(門控 +{raw45.group(7)} ms)。ns が捕へ 秒>秒 が隠した物 ★{raw45.group(5)} 本★(60_gate_top.r66.txt / 60_gate_run.stdout / .err = 門控と同じ秒 02:57:41)。後 {raw45.group(2)} 本は悉く 66 の 50_sengen ㊂ に在る → 疵 {raw45.group(4)}・rc 0。束全体(_after 込)後 {all45.group(2)} 疵 {all45.group(4)}。㋒ 對照 ―― 一走目 {k42f.group(1)} 形 合 {k42f.group(2)} 不 {k42f.group(3)}(P6 が黙つた)→ ★則を測つた後に一つ変へ★(ctime を足し・錠を歩哨の前へ)→ 二走目 {k42.group(1)} 形(陽 7・陰 4・零 1・錠 3)合 {k42.group(2)} 不 {k42.group(3)}・陰性で鳴つた {k42.group(4)}・陽性で黙つた {k42.group(5)}・母數 0 の陽陰 {k42.group(6)}。㋓ 乙1 23 + 乙5 3 → raw/otsu1_genbutsu.tsv(26 行)。讀手 = main 樹 karo_mac_manifest_verify.py({vsha}・198 行)を settrace で實走: 乙1 {a50.group(2)}(B2_30 10 / B2_31 9)= ★139 読めぬ行★(裸の名・'/' 無・基点を替へても同じ)/ 乙1 {a50.group(1)}(karo B0_10・shasum 形)= ★133 sha256= 無 → continue(母數にも入らぬ)★/ 乙5 3 = 基点 "" で 152 実体無・基点 _evidence/ で ★158 一致 {b50} 本★ ∴ ★余欄 durationSec= は生器を破らぬ ―― 破つたのは 66 の己の器(30_sanzan の ledger_parse)であつた = 己の訂正★。

## 0. 断(先に)
1. **★門の後に書く病は「憶える」では塞がらぬ ―― 塞いだのは順序である。★** 錠(0555/0444)を門の前に掛け、門の産物の置き場を根の外(_after/)へ移した。60 の順 = ①錠 ②歩哨 ③門 ④門控。書こうとすれば EACCES で落ちる(42 L1・_after/96 の P0)。
2. **★秒の粒度は門の産物を隠す。★** 66 の 99/96 は「秒>秒 1 本 2 B」と出したが、ns で測れば同じ秒に 3 本(60_gate_top.r66.txt・60_gate_run.stdout・.err)が門控の後に生れて居た。4 本とも 66 の宣に在る ∴ 疵 0 ―― ★然し 66 の紙は「1 本」と書いた。数が違つて居た。★
3. **★陽性 7 の内 1 は一走目で黙つた。★** P6(新 file を utime で歩哨より前へ戻す)―― macOS は mtime を birth より前へ戻すと birth も其処へ締める ∴ mtime/birth では見えぬ。ctime(utime が今へ動かす)を足して捕へた。★則を測つた後に変へた ―― 変へた事と一走目の出目(.first)を残す。★ 錠(chmod)も ctime を動かす故、錠は歩哨の★前★に掛ける順に揃へた(錠が後なら錠自体が鳴る = 一走目 L1 の形)。
4. **★乙1 の 23 は「dir 省き」より先に「方言」で落ちる。★** verify.py で見れば B2_30/B2_31 の 19 本は裸の名('/' 無)ゆゑ path 候補が取れず 139 読めぬ行 ―― 基点を何処へ替へても届かぬ。karo B0_10 の 4 本は shasum 形(`<sha>  <名>`)で `sha256=` が無く 133 で continue ―― ★数へられも咎められもせぬ(臺帳全件で 一致 0 / 母數 0 → rc 1 は「ok > 0」の條で出る)★。
5. **★乙5 の「余欄が讀み手を破る」は誤りであつた。★** 生器 verify.py の paths_of は '/' を含む語を拾ひ余欄を跳ぶ ∴ 基点さへ届けば 158 一致。破つたのは 66 の己の器 30_sanzan の ledger_parse(項の形を厳しく取る regex)。★己の前弾の紙 §3 乙5 の理由「余欄で讀み手が破れる」を、此処で訂正する。★
6. **★讀んだ版と走らせた版が別であつた(己の疵)。★** 50 の一走目は worktree HEAD の verify.py(127 行・bbde471f)を cat -n で讀み 76/82/95 の行番号を置いたが、走らせたのは main 樹の版(198 行・a507c998)。出目が 0/82 と喰ひ違つて器が暴いた。二走目で main 樹の行(133/139/152/158/160)へ直し .first を残す。

## 1. ㋐ 捕へ器 40(則は 00_start に先に書いた・要約)
| 項 | 則 |
|---|---|
| 刻 | 歩哨 file(_after/00_hosho.txt・60 が門の直前に書く一行)の st_mtime_ns。stat -f %Fm と同じ kernel の値 ―― 器が両方を印字し一致を示す |
| 何故 歩哨か | 門控は門の最後の産物 ∴ 門控を刻にすると門自身の産物が「前」に隠れる。歩哨を門の前に置けば門の産物は悉く「後」に入り、宣で割れる ∴ 疵 = 後 ∧ 宣に無い |
| 後 | mtime_ns > 刻 ★又は★ birth_ns(stat -f %FB)> 刻 ★又は★ ctime_ns > 刻(★二走目で足した★)。同 = mtime_ns == 刻(数へる)。前 = 其の他 |
| 宣 | 宣 file の ㊂ 行から fnmatch 型を取る(brace 展開・(…) は落とす・<束> は *・末尾 / は配下悉く) |
| rc | 2 = 母數 0(★歩いて居らぬ = 通でも鳴でもない★)/ 1 = 疵 ≥ 1 / 0 = 疵 0 |
| 錠 | 60 が門の前に raw/ 配下 file 0444・dir 0555。--probe で根へ 1 byte 書き PermissionError を記録(P0)。owner は錠を外せるが、外せば chmod が ctime を動かし 40 が鳴る(42 L3) |
| 比較 | 同じ刻を 秒>秒 でも数へ「ns が捕へて 秒>秒 が隠す物」を印字する |

## 2. ㋑ 第66弾の束へ(raw/45_km66.txt・刻 = 門控 mtime_ns {gate66ns} の代用 ―― 歩哨の無い束ゆゑ・門控より後に生れた物しか「後」に出ぬ = 歩哨より狭い)
- 走り raw(根 = km-66/raw): 母數 {raw45.group(1)} / 後 {raw45.group(2)} 本 {raw45.group(3)} B / 疵 {raw45.group(4)} / ns が捕へ 秒>秒 が隠す {raw45.group(5)} 本。★あの 1 本 2 B = 60_gate_run.rc は {raw45.group(6)}(+{raw45.group(7)} ms)★。
{ato45}
- 走り all(根 = km-66 束全体): 母數 {all45.group(1)} / 後 {all45.group(2)} 本 {all45.group(3)} B(_after/ の 28 本 込)/ 疵 {all45.group(4)}。
- ★意味★: 66 の「秒>秒 1 本 2 B」は数が違つて居た(ns なら 4 本 2636 B)。4 本は悉く 66 の 50_sengen ㊂ に在る ∴ 疵ではない。然し「宣に在る名を門の後に根へ書いてよい」のではなく、本弾は其の経路自体を無くした。
- 一走目(ctime 無し・45_km66*.first.txt)も同じ 4 本 / 疵 0 ―― 66 の束では ctime の追加が出目を変へなかつた。

## 3. ㋒ 對照(raw/42_taishou.txt・悉く 40 を subprocess で通した・母數 0 の陽陰は不)
### 3.1 二走目(ctime 込・錠→歩哨の順)―― 形 {k42.group(1)} / 合 {k42.group(2)} / 不 {k42.group(3)} / 陰性で鳴つた {k42.group(4)} / 陽性で黙つた {k42.group(5)}
{tab42}
### 3.2 一走目(ctime 無し・錠→歩哨の逆順・raw/42_taishou.first.txt)―― 形 {k42f.group(1)} / 合 {k42f.group(2)} / 不 {k42f.group(3)}
{tab42f}
- P6 が黙つた因(實測): macOS(APFS)は utime で mtime を birth より前へ置くと birth も其の刻へ締める ∴ 一走目の則(mtime | birth)では「前」に見えた。ctime は utime で今へ動く ∴ 二走目で捕へた。
- L1 の順: 一走目は 歩哨 → 錠 で、錠(chmod)が ctime を動かす故 二走目の則では鳴る。∴ 錠 → 歩哨 の順に直し、L3(歩哨の後に錠を外す)を陽性として足した。
- ★陰性が一形でも鳴れば騒音★ ―― 二走目 陰性 4 形とも rc 0(鳴 0)。Z1(空の根)は rc 2 で「通」に化けぬ。L2(錠なしの --probe)で「書けた」が出る事が、L1 の PermissionError が本物である證。

## 4. ㋓ 乙1 23 + 乙5 3 の現物(raw/otsu1_genbutsu.tsv・專任3 へ渡す一枚)
- 讀手 = main 樹 scripts/checks/karo_mac_manifest_verify.py(sha16 {vsha}・198 行)。臺帳の生の行(bytes)を一行づつ mini 臺帳(raw/otsu1/lines/)へ逐語で写し、main() を sys.settrace で走らせ verify.py の行番号の列を採つた。基点 A = ""(門が渡す形・cwd = main 樹)/ B = <紙>_evidence/ / C = <紙>_evidence/<sub>/。
- 落ちる行(A): 乙1 {n139} 本 → ★139 読めぬ行★ / 乙1 {n133} 本 → ★133 sha256= 無 → continue★ / 乙5 {n152} 本 → 152 実体無。B・C でも乙1 は同じ行で落ち、乙5 のみ B で 158 一致。
### 4.1 一本ごと(欄: 山 / 臺帳 / 行 / 生の行 / 實體 / bytes / 行の sha = 實 sha / 讀手の候補 / A 落ちる行+出目 / B / C ―― 出目 = 一致/相違/実体無/読めぬ)
| 山 | 臺帳 | 行 | 生の行(逐語・短縮) | 實體 | bytes | sha 一致 | paths_of | A | B | C |
|---|---|---|---|---|---|---|---|---|---|---|
{rows}
### 4.2 臺帳ごとの全件走り(A = 門と同じ基点 "" / B / C)
{led50}
### 4.3 乙5 の 3 行 ―― 生バイト 16 進(臺帳の行そのまま・改行は含まぬ・欄は空白 0x20 一つで区切られ tab は無い)
{hex50}
### 4.4 專任3 へ ―― 讀手のどの一行で落ちるか(直すのは專任3・此処は現物のみ)
| 落ちる行 | 何 | 本数 | 臺帳側の形 | 讀手側で見る所(行番号は a507c998 の版) |
|---|---|---|---|---|
| 139 | 読めぬ行 = path 候補 0 | 19 | `<裸の名>  sha256=…  bytes=…  lines=…`(B2_30/B2_31・'/' 無) | paths_of の「'/' を含む語のみ」(80 行)―― 裸の名を候補にせぬ。讀手自身の docstring は「./ を冠せ」と言ふ |
| 133 | sha256= 無 → continue | 4(+1 gate7.sh は 66 で甲1) | `<64hex>  <名>`(shasum -a 256 の生の形・karo B0_10) | SHA = `sha256=([0-9a-f]{{64}})`(45 行)―― 前置の無い 64hex を拾はぬ ∴ 行は母數にも入らぬ |
| 152 | 実体無 = 候補は在るが基点で届かぬ | 3(+ B0_axis2 の jsonl/json 6) | `phone/walkthrough.webm sha256=… durationSec=…`(基点 = _evidence/ を宣する行が無い) | bases(97〜105 行)―― 門は "" を渡す ∴ cwd 相対のみ。臺帳の在處(dirname(man))を基点に足せば届く |
- ★余欄 durationSec= tapCount= readyTimeouts= は讀手を破らぬ★(B で 158 一致 3/3)。66 §3 乙5 の理由は己の器 30_sanzan の ledger_parse の話であつた ―― 訂正する。

## 5. ㋔ 66 §8 の疵 7 ―― 直した物と直さぬ物
| # | 66 の疵 | 本弾 | 理由 |
|---|---|---|---|
| 1 | 己の箱の既讀化を手(python 一行)で | ★直した★ | 器 65_kidoku.py が札の便 id を引き read: false → true を一つだけ替へ、前後と bytes を raw/65_kidoku.txt に残す |
| 2 | 一走目に 2MB 閾を置き 26 と揃へず 343 | 直さぬ | 前弾の測定則(載らぬの三山)の話・本弾は其の則を走らせぬ |
| 3 | 乙5 を一走目の後に足した | 直さぬ(★然し 訂正★) | 山を足した事は前弾の則の話。乙5 の「理由」は本弾 §4 で訂正した(余欄は生器を破らぬ) |
| 4 | 00_start を手で書いた | ★直した★ | 器 00_start.py が刻・札 sha16・禁域 sha16 を計り kaki で書く |
| 5 | 甲4b(親 dir)が緩い | 直さぬ | 前弾の則の話・本弾に甲4 は無い |
| 6 | cwd が二度動いた | 直さぬ(別の形で残る) | 本弾の器は悉く絶対 path ―― 然し 50 の一走目で「讀んだ版 ≠ 走らせた版」が出た。cwd の疵でなく版の疵。§6-6 |
| 7 | 便を先に 300 超で書いた | ★直した★ | 05/62 は字数を先に印字し DRY で測る。62 の DRY は 5/6/7/8 便を 344/301/331 → 335/304/326 → 300/263/306 と三度咎め、四度目で 296/263/294/288 に収めた(割つた: 5 便を二つに) |

## 6. ㋕ 意味せぬ事(本弾の数が言はぬ事・6)
1. **疵 0(_after/96 で期待)≠ 門の後に raw/ へ書ける者が居らぬ。** owner は錠を外せる。外せば chmod が ctime を動かし 40 が鳴る(L3)―― 鳴るのは「外した」事であつて「書いた」事ではない。
2. **對照 15 形 合 15 ≠ 40 が恒真でない事の證明。** 形は己が選んだ。選ばなかつた形(rename・hard link・root による書込・別 mount)は測つて居らぬ。
3. **66 の 1 本 2 B を捕へた ≠ 66 が疵であつた。** 4 本とも宣に在る。違つて居たのは「1 本」と書いた数(秒の粒度)。
4. **乙1 19 = 139 ≠ 「dir 省き」が無い。** dir は省かれて居る(66 の乙1 は sha で当てた)。讀手は其処へ届く前に '/' 無で落ちる ∴ 139 を直しても次は 152(基点)で落ちる筈 ―― 測つて居らぬ(mini 臺帳に ./ を冠す実験はせず・直す側の仕事)。
5. **乙5 3 = 158 一致(基点 B)≠ B0_axis2 の臺帳が讀める。** 全件は B で 9/0/1/1 ―― 実体無 1(紙の行 queue/reports/… は main 樹の根が基点)・読めぬ 1(⑪追補前の行)が残る。
6. **P0 PermissionError ≠ 「書けぬ」の全數。** probe は一形(open 'wb')のみ。unlink・rename・mkdir は試して居らぬ(dir 0555 ゆゑ落ちる筈・測つて居らぬ)。

## 7. 己の疵(本弾・4)
1. ★讀んだ版 ≠ 走らせた版★(§0-6・50 一走目・.first)。
2. ★則を測つた後に一つ変へた★(ctime・錠の順・§3・.first)。変へねば P6 が黙つた儘であつた ―― 変へた事を書く。
3. 45 の rc を `| head` の後の `$?` で讀んだ(pipe 越し)―― 45_km66.rc(10_run 直採)が正。
4. 62 の便を初めに 300 超で書いた(三度)―― 器が門の前で捕へた。

## 8. 据ゑず・触れず・門の後の期待
- 据ゑず(scripts/ ~/bin settings.json hook instructions/ 0 字・門・照合器・追記器は讀む/走らせるのみ・60 が前後の sha16 で示す)/ 他席の臺帳・紙・箱に 0 字(mini 臺帳は己の束へ写した)/ 66 の束に 0 字(45 は讀むのみ・出目は己の raw/)/ DB 0(sb 0 回)/ git は rev-parse のみ(commit/push 0・add -f は納めの後に己の束のみ)/ tmux send-keys 0 / 臺帳は append.py のみが書き 手書き 0 / raw への本文は kaki(mini 臺帳の生 bytes のみ逐語ゆゑ例外)。
- ★門の後の期待(_after/96_after.txt が證す・紙は其の数を書けぬ)★: ⑴ 根 raw/(宣 無・--probe): 後 0・疵 0・P0 PermissionError・rc 0 ⑵ 根 束全体(宣 = raw/50_sengen.txt): 後 = _after/ と門控 悉く宣に在る・疵 0・rc 0 ⑶ 臺帳 照合 rc 0 ⑷ 錠 悉く 0444/0555。★一つでも違へば追ひ便で告げる。★
- 起 {KI} / 宣 = 起 + {SEN} 分 = {SENC} に門(織り込みは 00_start)。實は 63_sent.txt が両基準で書く。
- 在處: worktree `/Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1/docs/evidence/km-67-mon-no-ato-20260917/`(枝 karo-mac/a1-r56)。項の path は main 樹の根からの相對 ―― worktree の根から引くなら頭の `.claude/worktrees/karo-mac-a1/` を落とす(50_sengen.txt に宣)。

## 9. 出處
raw/00_start.txt(起・宣・則)/ 05_chakushu.txt(着手便)/ 40_mon_no_ato.py(捕へ器)/ 42_taishou.{{txt,tsv}} + .first.*(對照)+ raw/taishou/(fixture と各形の 40 の出目)/ 45_km66.txt・45_km66_raw.txt・45_km66_all.txt + .first.*(66 へ)/ 50_otsu1.txt + otsu1_genbutsu.tsv + .first.* + raw/otsu1/lines/(mini 臺帳 26)/ 65_kidoku.txt / 50_sengen.txt・50_build_manifest.out / 59_prescan.out / _after/(門の後・根の外): 00_hosho.txt・60_gate_rcs.txt・60_gate_top.r67.txt・96_after.txt・96_raw.txt・96_bundle.txt・62_report_body.txt・63_sent.txt・67_git_add.txt。
'''
K.kaku(B + '.md', T); b = open(B + '.md', 'rb').read(); print('紙', B + '.md', len(b), 'B', b.count(b'\n'), '行')
