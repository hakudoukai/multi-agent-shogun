# 第67弾 ―― 憶えて居れば防げる疵は、まだ塞がつて居らぬ ―― 門の後に書く病を「出来なく」し、乙1 の 23 と乙5 の 3 を現物へ固める(読取のみ・生器へ 0 字・他席の臺帳へ 0 字)―― 答を先に(★數の出處 = raw/40_mon_no_ato.py(捕へ器)/ raw/42_taishou.{txt,tsv} + .first(對照 二走)/ raw/45_km66*.txt + .first(66 の束へ)/ raw/50_otsu1.txt + raw/otsu1_genbutsu.tsv(乙1/乙5 現物・專任3 へ渡す一枚)/ raw/00_start.txt(起・宣・★則の逐語★)/ _after/96_after.txt(門の後の實走 ―― 紙の後に生れる故 紙は其の数を書けぬ・期待のみ書く)★)

★答★: ㋐ 捕へ器 raw/40_mon_no_ato.py ―― 刻は ★歩哨★(門の直前に一行書く file)の st_mtime_ns。秒でなく ns。歩哨を採つた理由 = 門控は門の★最後★の産物ゆゑ、門控を刻にすると門自身の産物(60_gate_*.err 等)が「前」に隠れ、後の集合が門の産物を隠す。歩哨なら門の産物も悉く「後」に入り、宣に在るか無いかで割れる ∴ ★疵 = 後 ∧ 宣に無い★ が過不足なく出る。後 = mtime | birth | ctime のいづれかが刻より後。rc 2 = 母數 0(歩いて居らぬ・通でも鳴でもない)/ rc 1 = 疵 ≥ 1 / rc 0 = 疵 0。★出来なく★ = 60 が門の★前★に raw/ と配下を 0555/0444 に錠し(書けば EACCES)、門の産物は悉く _after/(根の外)へ置く ―― 66 の「1 本 2 B」は 10_run が門の後に raw/ へ書いた形で、本弾では其の経路が無い。㋑ 66 の束へ(刻 = 門控 _gate.txt の mtime_ns を代用): あの 1 本 2 B(60_gate_run.rc)は ★★捕へた★★(門控 +3.329 ms)。ns が捕へ 秒>秒 が隠した物 ★3 本★(60_gate_top.r66.txt / 60_gate_run.stdout / .err = 門控と同じ秒 02:57:41)。後 4 本は悉く 66 の 50_sengen ㊂ に在る → 疵 0・rc 0。束全体(_after 込)後 32 疵 0。㋒ 對照 ―― 一走目 14 形 合 13 不 1(P6 が黙つた)→ ★則を測つた後に一つ変へ★(ctime を足し・錠を歩哨の前へ)→ 二走目 15 形(陽 7・陰 4・零 1・錠 3)合 15 不 0・陰性で鳴つた 0・陽性で黙つた 0・母數 0 の陽陰 0。㋓ 乙1 23 + 乙5 3 → raw/otsu1_genbutsu.tsv(26 行)。讀手 = main 樹 karo_mac_manifest_verify.py(a507c998c7bd6485・198 行)を settrace で實走: 乙1 19(B2_30 10 / B2_31 9)= ★139 読めぬ行★(裸の名・'/' 無・基点を替へても同じ)/ 乙1 4(karo B0_10・shasum 形)= ★133 sha256= 無 → continue(母數にも入らぬ)★/ 乙5 3 = 基点 "" で 152 実体無・基点 _evidence/ で ★158 一致 3 本★ ∴ ★余欄 durationSec= は生器を破らぬ ―― 破つたのは 66 の己の器(30_sanzan の ledger_parse)であつた = 己の訂正★。

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

## 2. ㋑ 第66弾の束へ(raw/45_km66.txt・刻 = 門控 mtime_ns 1789581461996717875 の代用 ―― 歩哨の無い束ゆゑ・門控より後に生れた物しか「後」に出ぬ = 歩哨より狭い)
- 走り raw(根 = km-66/raw): 母數 74 / 後 4 本 2636 B / 疵 0 / ns が捕へ 秒>秒 が隠す 3 本。★あの 1 本 2 B = 60_gate_run.rc は ★捕へた★(+3.329 ms)★。
  後・宣 60_gate_top.r66.txt 1036B mtime 02:57:41.996778708(+0.061ms) birth 02:57:41.996744625(FB) ctime 02:57:41.996778708 何で後=mbc 宣=raw/60_gate_top.r66.txt
  後・宣 60_gate_run.stdout 1513B mtime 02:57:41.999932334(+3.214ms) birth 02:57:41.999872709(FB) ctime 02:57:41.999932334 何で後=mbc 宣=raw/60_gate_run.stdout
  後・宣 60_gate_run.err 85B mtime 02:57:41.999995626(+3.278ms) birth 02:57:41.999965376(FB) ctime 02:57:41.999995626 何で後=mbc 宣=raw/60_gate_run.err
  後・宣 60_gate_run.rc 2B mtime 02:57:42.000046668(+3.329ms) birth 02:57:42.000020876(FB) ctime 02:57:42.000046668 何で後=mbc 宣=raw/60_gate_run.rc
- 走り all(根 = km-66 束全体): 母數 107 / 後 32 本 47965 B(_after/ の 28 本 込)/ 疵 0。
- ★意味★: 66 の「秒>秒 1 本 2 B」は数が違つて居た(ns なら 4 本 2636 B)。4 本は悉く 66 の 50_sengen ㊂ に在る ∴ 疵ではない。然し「宣に在る名を門の後に根へ書いてよい」のではなく、本弾は其の経路自体を無くした。
- 一走目(ctime 無し・45_km66*.first.txt)も同じ 4 本 / 疵 0 ―― 66 の束では ctime の追加が出目を変へなかつた。

## 3. ㋒ 對照(raw/42_taishou.txt・悉く 40 を subprocess で通した・母數 0 の陽陰は不)
### 3.1 二走目(ctime 込・錠→歩哨の順)―― 形 15 / 合 15 / 不 0 / 陰性で鳴つた 0 / 陽性で黙つた 0
| id | 種 | 形 | 期待 | 實rc | 母數 | 後 | 疵 | 判 | 註 |
| P1 | P | 新 file を歩哨の後に書く | 1 | 1 | 3 | 1 | 1 | 合 |  |
| P2 | P | 既存 a.txt へ追記(birth 前・mtime 後) | 1 | 1 | 2 | 1 | 1 | 合 |  |
| P3 | P | touch(中身同・mtime のみ後) | 1 | 1 | 2 | 1 | 1 | 合 |  |
| P4 | P | ★同秒の後 ns★(66 の穴 = 秒>秒 が隠す形) | 1 | 1 | 2 | 1 | 1 | 合 |  同秒 成(試行1) 歩哨 1789583210153409267 file 1789583210153482891 差 0.074ms |
| P5 | P | 新 dir + file を後に | 1 | 1 | 2 | 1 | 1 | 合 |  |
| P6 | P | utime で mtime を前へ戻した新 file(birth が後) | 1 | 1 | 2 | 1 | 1 | 合 |  e.txt mtime を歩哨-1s へ戻した(birth は後) |
| P7 | P | 宣に在る名(g_mon)と無い名(h)が共に後 → h で鳴る | 1 | 1 | 3 | 2 | 1 | 合 |  |
| N1 | N | 悉く歩哨の前 | 0 | 0 | 3 | 0 | 0 | 合 |  |
| N2 | N | ★同秒の前 ns★(file → 歩哨 が同じ秒) | 0 | 0 | 1 | 0 | 0 | 合 |  同秒 成(試行1) file 1789583210336613713 歩哨 1789583210336711920 差 0.098ms |
| N3 | N | 宣に在る名だけが後(g_mon・mon/) | 0 | 0 | 3 | 2 | 0 | 合 |  |
| N4 | N | 深い dir・悉く前 | 0 | 0 | 4 | 0 | 0 | 合 |  |
| Z1 | Z | 空の根(歩哨のみ) → rc 2 = 歩いて居らぬ | 2 | 2 | 0 | 0 | 0 | 合 |  |
| L1 | L | 錠を歩哨の★前★に掛け --probe で 1 byte 書く → PermissionError・鳴らぬ | PermissionError | 0 | 1 | 0 | 0 | 合 | 根へ 1 byte 書けぬ = PermissionError(13) ★出来なく なつて居る★ 錠 → 歩哨 の順(二走目)/ 根 0555 file 0444 |
| L3 | P | 歩哨の後に錠を外す → ctime で鳴る(外した事自体が捕へられる) | 1 | 1 | 1 | 1 | 1 | 合 |  錠 → 歩哨 → ★錠を外す★(chmod は ctime を動かす) |
| L2 | L | 錠なしで --probe → 書けた(probe が本物である證) | 書けた | 0 | 1 | 0 | 0 | 合 | 根へ 1 byte ★書けた★(錠が掛かつて居らぬ・書いた後に消した ―― 之は書込みである) 錠 無 |
### 3.2 一走目(ctime 無し・錠→歩哨の逆順・raw/42_taishou.first.txt)―― 形 14 / 合 13 / 不 1
| id | 種 | 形 | 期待 | 實rc | 母數 | 後 | 疵 | 判 | 註 |
| P1 | P | 新 file を歩哨の後に書く | 1 | 1 | 3 | 1 | 1 | 合 |  |
| P2 | P | 既存 a.txt へ追記(birth 前・mtime 後) | 1 | 1 | 2 | 1 | 1 | 合 |  |
| P3 | P | touch(中身同・mtime のみ後) | 1 | 1 | 2 | 1 | 1 | 合 |  |
| P4 | P | ★同秒の後 ns★(66 の穴 = 秒>秒 が隠す形) | 1 | 1 | 2 | 1 | 1 | 合 |  同秒 成(試行1) 歩哨 1789582873482718352 file 1789582873482777226 差 0.059ms |
| P5 | P | 新 dir + file を後に | 1 | 1 | 2 | 1 | 1 | 合 |  |
| P6 | P | utime で mtime を前へ戻した新 file(birth が後) | 1 | 0 | 2 | 0 | 0 | ★不★ |  e.txt mtime を歩哨-1s へ戻した(birth は後) |
| P7 | P | 宣に在る名(g_mon)と無い名(h)が共に後 → h で鳴る | 1 | 1 | 3 | 2 | 1 | 合 |  |
| N1 | N | 悉く歩哨の前 | 0 | 0 | 3 | 0 | 0 | 合 |  |
| N2 | N | ★同秒の前 ns★(file → 歩哨 が同じ秒) | 0 | 0 | 1 | 0 | 0 | 合 |  同秒 成(試行1) file 1789582873620942691 歩哨 1789582873621010690 差 0.068ms |
| N3 | N | 宣に在る名だけが後(g_mon・mon/) | 0 | 0 | 3 | 2 | 0 | 合 |  |
| N4 | N | 深い dir・悉く前 | 0 | 0 | 4 | 0 | 0 | 合 |  |
| Z1 | Z | 空の根(歩哨のみ) → rc 2 = 歩いて居らぬ | 2 | 2 | 0 | 0 | 0 | 合 |  |
| L1 | L | 錠の後に --probe で 1 byte 書く → PermissionError | PermissionError | 0 | 1 | 0 | 0 | 合 | 根へ 1 byte 書けぬ = PermissionError(13) ★出来なく なつて居る★ 根 0555 / file 0444 |
| L2 | L | 錠なしで --probe → 書けた(probe が本物である證) | 書けた | 0 | 1 | 0 | 0 | 合 | 根へ 1 byte ★書けた★(錠が掛かつて居らぬ・書いた後に消した ―― 之は書込みである) 錠 無 |
- P6 が黙つた因(實測): macOS(APFS)は utime で mtime を birth より前へ置くと birth も其の刻へ締める ∴ 一走目の則(mtime | birth)では「前」に見えた。ctime は utime で今へ動く ∴ 二走目で捕へた。
- L1 の順: 一走目は 歩哨 → 錠 で、錠(chmod)が ctime を動かす故 二走目の則では鳴る。∴ 錠 → 歩哨 の順に直し、L3(歩哨の後に錠を外す)を陽性として足した。
- ★陰性が一形でも鳴れば騒音★ ―― 二走目 陰性 4 形とも rc 0(鳴 0)。Z1(空の根)は rc 2 で「通」に化けぬ。L2(錠なしの --probe)で「書けた」が出る事が、L1 の PermissionError が本物である證。

## 4. ㋓ 乙1 23 + 乙5 3 の現物(raw/otsu1_genbutsu.tsv・專任3 へ渡す一枚)
- 讀手 = main 樹 scripts/checks/karo_mac_manifest_verify.py(sha16 a507c998c7bd6485・198 行)。臺帳の生の行(bytes)を一行づつ mini 臺帳(raw/otsu1/lines/)へ逐語で写し、main() を sys.settrace で走らせ verify.py の行番号の列を採つた。基点 A = ""(門が渡す形・cwd = main 樹)/ B = <紙>_evidence/ / C = <紙>_evidence/<sub>/。
- 落ちる行(A): 乙1 19 本 → ★139 読めぬ行★ / 乙1 4 本 → ★133 sha256= 無 → continue★ / 乙5 3 本 → 152 実体無。B・C でも乙1 は同じ行で落ち、乙5 のみ B で 158 一致。
### 4.1 一本ごと(欄: 山 / 臺帳 / 行 / 生の行 / 實體 / bytes / 行の sha = 實 sha / 讀手の候補 / A 落ちる行+出目 / B / C ―― 出目 = 一致/相違/実体無/読めぬ)
| 山 | 臺帳 | 行 | 生の行(逐語・短縮) | 實體 | bytes | sha 一致 | paths_of | A | B | C |
|---|---|---|---|---|---|---|---|---|---|---|
| 乙5 | ashigaru-mac-2_B0_axis2_20260908.… | 24 | `desktop/walkthrough.webm sha256=7a278da9bfa8386dff2f7c3b4d4…` | desktop/walkthrough.webm | 87899 | True | desktop/walkthrough.webm | 152 0/0/1/0 | 158 1/0/0/0 | =B 1/0/0/0 |
| 乙5 | ashigaru-mac-2_B0_axis2_20260908.… | 16 | `phone/walkthrough.webm sha256=d694aed6bf9add7dbcb118f357399…` | phone/walkthrough.webm | 90065 | True | phone/walkthrough.webm | 152 0/0/1/0 | 158 1/0/0/0 | =B 1/0/0/0 |
| 乙5 | ashigaru-mac-2_B0_axis2_20260908.… | 20 | `ipad/walkthrough.webm sha256=1b0c14a6488009031d0ec6df18450b…` | ipad/walkthrough.webm | 87081 | True | ipad/walkthrough.webm | 152 0/0/1/0 | 158 1/0/0/0 | =B 1/0/0/0 |
| 乙1 | ashigaru-mac-2_B2_30_20260907.md | 12 | `09_stage2_e2eb83_GREEN_full.txt  sha256=786f553f29228e1bf28…` | raw/09_stage2_e2eb83_GREEN_full.txt | 27266 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_30_20260907.md | 4 | `01_propose_line_splits_idempotency_check.txt  sha256=a34aaf…` | raw/01_propose_line_splits_idempotency_chec… | 32045 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_30_20260907.md | 5 | `02_const_fix_patch_saved_for_reapply.diff  sha256=cd18010fa…` | raw/02_const_fix_patch_saved_for_reapply.di… | 1928 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_30_20260907.md | 3 | `00_worktree_baseline.txt  sha256=d1575792d33466e0e739ffe4c8…` | raw/00_worktree_baseline.txt | 1477 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_30_20260907.md | 7 | `04_stage6_roundtrip_RED.txt  sha256=77542dd23cbf5733bc56d92…` | raw/04_stage6_roundtrip_RED.txt | 619 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_30_20260907.md | 11 | `08_stage6_roundtrip_GREEN.txt  sha256=6caf36ad7516e77a2017b…` | raw/08_stage6_roundtrip_GREEN.txt | 631 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_30_20260907.md | 8 | `05_stage2_e2eb83_RED_scoped_initial.txt  sha256=c0786b55232…` | raw/05_stage2_e2eb83_RED_scoped_initial.txt | 5646 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_30_20260907.md | 9 | `06_stage2_e2eb83_RED_full.txt  sha256=4066f8775015900bbee5b…` | raw/06_stage2_e2eb83_RED_full.txt | 5187 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_30_20260907.md | 6 | `03_stage1_vitest_RED.txt  sha256=3bee5a2006a83073d5ce586e49…` | raw/03_stage1_vitest_RED.txt | 535 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_30_20260907.md | 10 | `07_stage1_vitest_GREEN.txt  sha256=34352b99174d5d55be9de0a4…` | raw/07_stage1_vitest_GREEN.txt | 476 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_31_20260907.md | 7 | `04_vitest_RED_test_names.txt  sha256=2a52150ff7370a66e355c9…` | raw/04_vitest_RED_test_names.txt | 11899 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_31_20260907.md | 8 | `05_e2e_b83_RED_test_names.txt  sha256=d6cb8ac609ee6ba2a3962…` | raw/05_e2e_b83_RED_test_names.txt | 51957 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_31_20260907.md | 11 | `08_dino_check_GREEN_final_15ep.txt  sha256=fe0ba3f612eff1df…` | raw/08_dino_check_GREEN_final_15ep.txt | 1888 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_31_20260907.md | 4 | `01_apply_splits_script_log.txt  sha256=314f13aee086b8b1b820…` | raw/01_apply_splits_script_log.txt | 3985 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_31_20260907.md | 3 | `00_propose_line_splits_full_before_apply.txt  sha256=6f2221…` | raw/00_propose_line_splits_full_before_appl… | 31755 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_31_20260907.md | 6 | `03_dino_check_RED_baseline_15ep.txt  sha256=8cc1d39355e755f…` | raw/03_dino_check_RED_baseline_15ep.txt | 2037 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_31_20260907.md | 9 | `06_dino_check_GREEN_attempt1_15ep.txt  sha256=beca5488adecc…` | raw/06_dino_check_GREEN_attempt1_15ep.txt | 1866 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_31_20260907.md | 5 | `02_propose_line_splits_idempotency_after_apply.txt  sha256=…` | raw/02_propose_line_splits_idempotency_afte… | 35286 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | ashigaru-mac-2_B2_31_20260907.md | 10 | `07_vitest_EXPECTED_diff.txt  sha256=bc2564650e8b33ea89be5f6…` | raw/07_vitest_EXPECTED_diff.txt | 2909 | True | (無) | 139 0/0/0/1 | 139 0/0/0/1 | 139 0/0/0/1 |
| 乙1 | karo_mac_B0_10_kizai_hozen_202609… | 1 | `4481bdf300247bbc557fe6a40a5aae74a26b2a21c40597beeeba0d2ee90…` | kizai/karo_mac_bundle5.sh | 2563 | False | (無) | 133 0/0/0/0 | 133 0/0/0/0 | 133 0/0/0/0 |
| 乙1 | karo_mac_B0_10_kizai_hozen_202609… | 3 | `601ba803e879b9cd4702e5a922a5489ee82aa60b4ae9fa35dd4ffe17398…` | kizai/karo_mac_mark.py | 1015 | False | (無) | 133 0/0/0/0 | 133 0/0/0/0 | 133 0/0/0/0 |
| 乙1 | karo_mac_B0_10_kizai_hozen_202609… | 5 | `8621da48ca42fb5abfc7fb6b2899e5f3245c56123aa32041350cf276b6f…` | kizai/karo_mac_unread.py | 445 | False | (無) | 133 0/0/0/0 | 133 0/0/0/0 | 133 0/0/0/0 |
| 乙1 | karo_mac_B0_10_kizai_hozen_202609… | 4 | `5a4fd680b4e9538e9a67246c61f225fa23d56cca08edac762cf178b6059…` | kizai/karo_mac_read.py | 9521 | False | (無) | 133 0/0/0/0 | 133 0/0/0/0 | 133 0/0/0/0 |
### 4.2 臺帳ごとの全件走り(A = 門と同じ基点 "" / B / C)
  ashigaru-mac-2_B0_axis2_20260908_evidence/manifest.txt: 実体行 21 / sha256= を含む行 11 / A rc 1 1/0/9/1 / B rc 1 9/0/1/1 / C(=B) rc 1 9/0/1/1
  ashigaru-mac-2_B2_30_20260907_evidence/manifest.txt: 実体行 11 / sha256= を含む行 10 / A rc 1 0/0/0/10 / B rc 1 0/0/0/10 / C(raw) rc 1 0/0/0/10
  ashigaru-mac-2_B2_31_20260907_evidence/manifest.txt: 実体行 10 / sha256= を含む行 9 / A rc 1 0/0/0/9 / B rc 1 0/0/0/9 / C(raw) rc 1 0/0/0/9
  karo_mac_B0_10_kizai_hozen_20260908_evidence/manifest.txt: 実体行 5 / sha256= を含む行 0 / A rc 1 0/0/0/0 / B rc 1 0/0/0/0 / C(kizai) rc 1 0/0/0/0
### 4.3 乙5 の 3 行 ―― 生バイト 16 進(臺帳の行そのまま・改行は含まぬ・欄は空白 0x20 一つで区切られ tab は無い)
  ashigaru-mac-2_B0_axis2_20260908.md L24 143 B: 6465736b746f702f77616c6b7468726f7567682e7765626d207368613235363d37613237386461396266613833383664666632663763336234643435336432393538656338643330376463643436646632393634666366346237616637383763206475726174696f6e5365633d32332e35313020746170436f756e743d313420726561647954696d656f7574733d30
  ashigaru-mac-2_B0_axis2_20260908.md L16 141 B: 70686f6e652f77616c6b7468726f7567682e7765626d207368613235363d64363934616564366266396164643764626362313138663335373339396634333539656234363134356161323830666338663239366166663033303536363131206475726174696f6e5365633d32332e33343320746170436f756e743d313420726561647954696d656f7574733d30
  ashigaru-mac-2_B0_axis2_20260908.md L20 140 B: 697061642f77616c6b7468726f7567682e7765626d207368613235363d31623063313461363438383030393033316430656336646631383435306262323531353861656661313031333366336136303064353133326437626666336632206475726174696f6e5365633d32332e36303020746170436f756e743d313420726561647954696d656f7574733d30
### 4.4 專任3 へ ―― 讀手のどの一行で落ちるか(直すのは專任3・此処は現物のみ)
| 落ちる行 | 何 | 本数 | 臺帳側の形 | 讀手側で見る所(行番号は a507c998 の版) |
|---|---|---|---|---|
| 139 | 読めぬ行 = path 候補 0 | 19 | `<裸の名>  sha256=…  bytes=…  lines=…`(B2_30/B2_31・'/' 無) | paths_of の「'/' を含む語のみ」(80 行)―― 裸の名を候補にせぬ。讀手自身の docstring は「./ を冠せ」と言ふ |
| 133 | sha256= 無 → continue | 4(+1 gate7.sh は 66 で甲1) | `<64hex>  <名>`(shasum -a 256 の生の形・karo B0_10) | SHA = `sha256=([0-9a-f]{64})`(45 行)―― 前置の無い 64hex を拾はぬ ∴ 行は母數にも入らぬ |
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
- 起 2026-09-17T03:16:02 / 宣 = 起 + 26 分 = 03:42:02 に門(織り込みは 00_start)。實は 63_sent.txt が両基準で書く。
- 在處: worktree `/Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1/docs/evidence/km-67-mon-no-ato-20260917/`(枝 karo-mac/a1-r56)。項の path は main 樹の根からの相對 ―― worktree の根から引くなら頭の `.claude/worktrees/karo-mac-a1/` を落とす(50_sengen.txt に宣)。

## 9. 出處
raw/00_start.txt(起・宣・則)/ 05_chakushu.txt(着手便)/ 40_mon_no_ato.py(捕へ器)/ 42_taishou.{txt,tsv} + .first.*(對照)+ raw/taishou/(fixture と各形の 40 の出目)/ 45_km66.txt・45_km66_raw.txt・45_km66_all.txt + .first.*(66 へ)/ 50_otsu1.txt + otsu1_genbutsu.tsv + .first.* + raw/otsu1/lines/(mini 臺帳 26)/ 65_kidoku.txt / 50_sengen.txt・50_build_manifest.out / 59_prescan.out / _after/(門の後・根の外): 00_hosho.txt・60_gate_rcs.txt・60_gate_top.r67.txt・96_after.txt・96_raw.txt・96_bundle.txt・62_report_body.txt・63_sent.txt・67_git_add.txt。
