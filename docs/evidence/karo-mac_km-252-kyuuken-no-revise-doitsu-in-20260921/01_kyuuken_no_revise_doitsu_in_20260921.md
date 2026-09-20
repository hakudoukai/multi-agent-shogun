# km-252 ―― 九件の REVISE は同一因である（一束）

## ① 件名・刻・母數

- 件名: 軍師 gunshi-main が家老mac へ返した REVISE 九件の因を一束へ畳む
- 刻: 2026-09-21T02:3x JST（各測の刻は 80_raw/8*_measure_*.txt の冠に逐語）
- 母數: REVISE 九件 ＋ 其の親九件 = **18 件**。悉く `~/bin/sb read seq <N>` で個別に引いた
  （要約・記憶・他 agent の報に依らぬ。生の出目は 80_raw/rev_*.txt / par_*.txt 計 18 枚）
- 検分 repo: `/Users/momizimac/multi-agent-shogun`（Mac・mac_pc）
- 本束の固定 commit / tree: 本紙の後に彫るゆゑ**本紙では宣せぬ**（雛形 v1.3 L138 に依り納便で宣す）

## ② 九件の表（生の出目より機械的に起した）

| REVISE seq | 刻 | 親 seq | 判の発 | 判の宛 | 親の発 | 親の宛 |
|---|---|---|---|---|---|---|
| 344826 | 2026-09-20T18:10:35 | 337810 | gunshi-main | karo-mac | dr-m | gunshi-mac |
| 344827 | 2026-09-20T18:10:35 | 342968 | gunshi-main | karo-mac | karo-mac | gunshi-mac |
| 344835 | 2026-09-20T18:11:42 | 330866 | gunshi-main | karo-mac | karo-mac | gunshi-mac |
| 344845 | 2026-09-20T18:13:15 | 330886 | gunshi-main | karo-mac | karo-mac | gunshi-mac |
| 344855 | 2026-09-20T18:14:57 | 331860 | gunshi-main | karo-mac | ashigaru-mac-1 | gunshi-mac |
| 344856 | 2026-09-20T18:14:57 | 331864 | gunshi-main | karo-mac | ashigaru-mac-1 | gunshi-mac |
| 344978 | 2026-09-20T18:33:25 | 343175 | gunshi-main | karo-mac | karo-mac | gunshi-mac |
| 344979 | 2026-09-20T18:33:25 | 343176 | gunshi-main | karo-mac | karo-mac | gunshi-mac |
| 344980 | 2026-09-20T18:33:25 | 343177 | gunshi-main | karo-mac | karo-mac | gunshi-mac |

**放置の長さ**（家老mac が一件も讀まなかつた時間・現刻 2026-09-21T02:3x 基準）:
六件（344826〜344856）= **約 8時間20分**／三件（344978〜344980）= **約 8時間00分**。
**★之は家老mac の落度である（⑤に自申）★**

## ③ 因は九件悉く同一である

軍師が名指した欠けを九件の content から抜いた（逐語は 80_raw/rev_*.txt）:

| 欠けの名 | 逐語（代表） | 何件 |
|---|---|---|
| ㋐ 検分 repo path が受け手に無い | 344978「repo欠。…申告repo未在、commit/tree/baseを既知repoで検証不能」 | 九件悉く |
| ㋑ 紙が受け手の検分根に無い | 344979「paper欠。紙pathは当席検分根に無く、full SHA/bytes/489行を独立照合不能」 | 九件悉く |
| ㋒ raw argv/rc を独立検分できぬ | 344980「raw欠。manifestは申告のみで…独立検分不能。PASS/close不可」 | 九件悉く |

**∴ 三本の柱は互ひに別の欠けではなく、★一つの事の三つの顔★である**
＝ **受け手（main_pc の gunshi-main）が Mac の repo・束・紙へ到達できぬ**。
家老mac が出した値（40桁 commit/tree・full SHA256・bytes/lines）は**悉く正しく載つて居た**が、
受け手は其れを**己の器で再現できぬ**ゆゑ PASS を出せぬ。
∴ **値を足しても九件は閉ぢぬ。到達の路を作らねば閉ぢぬ。**

## ④ 路の棚卸し ―― 家老mac が seq347130 で挙げた三択は二つが潰れた

| 路 | 中身 | 測り | 判 |
|---|---|---|---|
| ㋐ | 總監督代行が Mac の枝を main へ push | 未測（外部依存） | **残る** |
| ㋑ | 束を共有樹 `/mnt/c/DentalBI` へ置き双方が讀む | `/bin/test -d /mnt/c` → **rc=1 不在**（陽性對照=己の repo は rc=0） | **★潰れた★** |
| ㋒ | 判を同 PC の `gunshi-mac` へ移す | 親九件の宛 = **gunshi-mac 9/9**／判の発 = **gunshi-main 9/9・gunshi-mac 0/9** | **★潰れた（既に實行済で成らず）★** |
| ㋓ | 確定路 main_pc へ束を渡す（新たに見えた） | `~/.ssh/config` に `Host mainpc`(192.168.11.11:2222 user・IdentityFile 在)／known_hosts に **3 行の痕** | **未走・裁を請ふ** |
| ㋔ | Mac から GitHub へ直に push | memory 条 `project_mac_key_cannot_push_this_repo` が不可と言ふ（remote は https ゆゑ鍵経路でない） | **要再測** |

**★㋒ が潰れた事の意味★** ―― 家老mac は「判を gunshi-mac へ移せば閉ぢる」と二便（seq347130・seq347252）で宣したが、
**親九件は初めから `target_agent: gunshi-mac` であつた**。宛先は既に同 PC の軍師であり、
**main_pc の gunshi-main が代りに判を取つた**。∴ 宛先を替へる策では閉ぢぬ。
（何故 gunshi-mac が取らず gunshi-main が取るのか＝**未測**。gunshi-mac の箱 `queue/inbox/gunshi-mac.yaml` が死箱 rc=68 である事が因の候補だが、DB の `--to gunshi-mac` は rc=0 で通るゆゑ断ぜぬ。）

## ⑤ 家老mac の落度（先に述べる）

- ㊿+8 **九件を 8時間 讀まなかつた** ―― 判は宛先（gunshi-mac）と違ふ席（gunshi-main）から返るゆゑ、
  宛先で返りを探す癖が機序であつた。**療法 = 返りは親（parent_seq）で探せ・DB 箱を毎巡歩け**。
- ㊿+9 **母數を「三件」と狭く語つて居た** ―― 實は九件（seq347251 で自申済）。
- ㊿+10 **㋒ を己の見立てとして二便で上へ宣したが、數が之を反証した** ―― 上記④。
  **測る前に見立てを宣した**のが機序。療法 = 策を宣す前に其の策が既に實行済でないかを親の `target_agent` で測れ。
- ㊿+11 **器の空振りを席の状態と讀みかけた** ―― `sb read inbox 200` の出目に `sender_agent` を grep し 0 を得て
  「gunshi-mac は DB へ書かぬ」と讀みかけた。**陽性對照（己=karo-mac）も 0 を返した**ゆゑ器の欄が無いと判つた。
  （80_raw/84_measure_inbox_fields.txt に生の出目）
- ㊿+12 **brace group 内に逆引用符を書き command substitution を起した**（parse error）。
  更に「parse error なら何も走らぬ」と仮定したが、**再走の冒頭で 4 枚が既に在つた**
  ∴ **parse error は前半の実行を止めなかつた**。仮定を測らずに書いた落度。

## ⑥ 求むる裁（Mac事業部長へ）

1. **路 ㋓ の可否** ―― 確定路 main_pc(192.168.11.11:2222 user) へ、家老mac が束（または `git bundle` 一本）を
   置く事を許すか。**他 PC へ file を置く手ゆゑ変更統制に当たると判じ、實走せず裁を請ふ**。
   許されぬ場合は ㋐（總監督代行の push）へ倒す。
2. **㋒ の後始末** ―― `gunshi-mac` 宛の提出が `gunshi-main` へ渡る機序を測る事は、Mac lane の判の路そのものである。
   之を家老mac が測つて良いか（讀取のみで測る見込み）。
3. **九件の扱ひ** ―― 路が立つまで九件は `PASS 不可` の儘である。**取り下げて再提出するか・路が立つまで置くか**。

## ⑦ 未測（測つて居らぬ物を明記する）

- 路㋓ の**実走**（ssh 到達・書込可否）―― **未走**。裁を待つ。
- 路㋔ の**再測**（GitHub push 可否）―― **未測**。memory 条に依る伝聞のみ。
- `gunshi-mac` が判を取らぬ**因** ―― **未測**（死箱 rc=68 は候補に過ぎぬ）。
- 九件の親が指す束が**今も disk に在るか** ―― **未測**（本束では親の便の逐語のみを扱ふ）。
