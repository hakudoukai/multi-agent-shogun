# km-200 再測 ―― 胴が空でも通す器の census（板 8c96d308・專任1 ashigaru-mac-1・2026-09-26）

下命: 家老mac 便 msg_20260926_115624_02fd6c88 と goal file `queue/goals/ashigaru-mac-1.yaml`（11:55）。
「空胴の4種（0byte・空白のみ・改行のみ・引数無し）を census し、通す・撥ねる・測れぬに分けて器を特定する。読み取りと紙だけで行い、器は変へず、空便は出さない」。
親 commit は origin/main b9573b2d376e9a0a372234b696a733677feb7919。

## 旧納めとの関係

- 9/19 に一度納めている（commit 2b3405a8578b8ee0f72dc7bbadb5f215e9386a42・枝 `ashigaru-mac-1/km-200-karano-dou-wo-toosu-utsuwa-no-census-20260918`）。
  - 監査便 334907/334908/334909/334911 を gunshi-mac 宛に出した。seqs 334912〜335511 を歩いたが、判定は見つからなかった（判定未着）。
  - 板は 9/24 の付替で「未着手」に戻った。
- その後に器が変はった。このため、今の版で新しい束を作った。
  - agent_letter.py は 271行から 341行になった。
  - inbox_write.sh は稼働木の版と origin/main の版に分かれた。
  - 送る器が3本（km_send.sh・l1send・mac_send.py）増えた。
  - 詳細は `raw/10_bosuu.txt`。

## 母數と対象（REVISE⑤ で揃へた）

- 根 `~/bin` の深さ1にある、実行できる file のうち、名に sb|letter|inbox|board|send を含み、.bak と .pre を除いた物：**17本**（`raw/10_bosuu.txt`・11:57:54）。
- **除外4本**（送る器ではない＝胴を受けて外へ出す路を持たぬ）：
  - cc_goal_from_board.py（板を読んで goal file を作る）
  - inbox_mark_read.py（己の箱に既読を付ける）
  - km_inbox_read_mark.sh（同上の包み）
  - orphan_inbox_trap.py（迷ひ箱を捕へる検め）
- **対象13本**＋repo 側 `scripts/inbox_write.sh` の2版（稼働木 409行・563271ea…／origin/main 366行・96a1e235…）＝**15の器**。下の判定表は17行（agent_letter と稼働木 inbox_write は路で2行に分けた・他は1行1器）。
- sb-* 8本の形の差は `raw/22_sb_diff.txt`（sb-ashigaru-mac-1 を基準にした diff の逐語）。役の名だけ違う物が5本、sb-karo-mac は後ろに `--requires-response` を足す、sb-gakushu-bucho は `set -eu` と `$1 != write` で rc2、sb は `read` の口を持ち役が karo-mac。
- .bak と .pre の族53本は census の外（呼ばれる器ではない）。

## 測り方（板・箱・DB へ出さぬ形のみ）

- 種は `raw/seed/` の4本（sha と hex は `raw/12_seed_sha.txt`）。e0=0byte、e1=半角空白・TAB・全角空白、e2=改行のみ、c=対照。
- 1本目の器 `raw/20_jissoku.sh`（11:59:45）：agent_letter 直（argv と --content-file・--dry-run）、sb-ashigaru-mac-1、inbox_write 稼働木を `IW_NAME_TEST_ONLY=1`（名の門の直後で exit 0）、board_write の引数無し。
- 2本目の器 `raw/21_jissoku_tsuika.sh`（12:37:49・REVISE⑤ で足した）：
  - 他の sb-* 7本の ⒜⒝⒞（--dry-run）と ⒟（usage に落ちる形だけ）。
  - inbox_write 稼働木の後段を、止まり木 `IW_DEFERRAL_TEST_ONLY=1`（DEFERRAL gate の直後）と `IW_DEAD_TEST_ONLY=1`（dead-inbox gate の直後）で。宛先は死箱 karo-mac と生箱 ashigaru-mac-2 の両方。
  - mac_send.py を、標 `x` と空の cwd で（L83 の標の門より先へ進まぬ）。対照は標 `km-200` で L85 まで進め、cwd に scripts/ が無いゆゑ rc4 で止まることを見た。走った後も cwd は空（器の末行）。
- 走らせぬ路の字面は `raw/30_jimen.txt` に逐語で置いた。

## 判定表（甲=撥ねる・乙=rc0 で通す・丙=測れぬ）

各欄に **［実走］／［字面］／［未測］** を付けた。［字面］と［未測］の欄は断定ではない。

| 器・路 | ⒜0byte | ⒝空白のみ | ⒞改行のみ | ⒟引数無し | 拠 |
|---|---|---|---|---|---|
| agent_letter.py argv | 甲 rc2［実走］ | 甲 rc2［実走］ | 甲 rc2［実走］ | **乙 rc0**［実走］（usage を刷って0） | 20 |
| agent_letter.py --content-file | 甲 rc2［実走］ | 甲 rc2［実走］ | 甲 rc2［実走］ | 甲 rc2［実走］（旗のみ） | 20 |
| sb-ashigaru-mac-1 | 甲 rc2［実走］ | 甲 rc2［実走］ | 甲 rc2［実走］ | **乙 rc0**［実走］（`write letter`／`write`）・甲 rc2［実走］（何も無い） | 20 |
| sb-ashigaru-mac-2 | 甲 rc2［実走］ | 甲 rc2［実走］ | 甲 rc2［実走］ | **乙 rc0**［実走］（`write letter`／`write`）・甲 rc2［実走］（何も無い） | 21 |
| sb-ashigaru-mac-3 | 同上［実走］ | 同上［実走］ | 同上［実走］ | 同上［実走］ | 21 |
| sb-gunshi-mac | 同上［実走］ | 同上［実走］ | 同上［実走］ | 同上［実走］ | 21 |
| sb-shogun-mac | 同上［実走］ | 同上［実走］ | 同上［実走］ | 同上［実走］ | 21 |
| sb-gakushu-bucho | 甲 rc2［実走］ | 甲 rc2［実走］ | 甲 rc2［実走］ | **乙 rc0**［実走］（`write letter`／`write`）・甲 rc2［実走］（何も無い） | 21 |
| sb-karo-mac | 甲 rc2［実走］ | 甲 rc2［実走］ | 甲 rc2［実走］ | **乙 rc0**［実走］（`write`）・甲 rc2［実走］（何も無い）・`write letter` は甲 rc2 の見込み［字面・未走］（後ろの `--requires-response` が本文の位置に来て L186 で die） | 21・22 |
| sb | ［未測］ | ［未測］ | ［未測］ | ［未測］ | 22 の字面のみ（役 karo-mac で agent_letter へ渡す形は sb-karo-mac と同じだが `--requires-response` は無い）。creds が `.sb_env` ゆゑ走らせていない |
| inbox_write.sh 稼働木 argv | 甲 rc1［実走］ | **乙 rc0**［実走・DEFERRAL の後まで・生箱は DEAD の後まで］ | **乙 rc0**［実走・同］ | 甲 rc1［実走］ | 20・21 |
| inbox_write.sh 稼働木 stdin | 甲 rc1［実走］ | **乙 rc0**［実走・DEFERRAL の後まで］ | 甲 rc1［実走］ | ― | 20・21 |
| inbox_write.sh origin/main | 甲［字面］ | 乙［字面］ | 乙［字面］ | 甲［字面］ | 止まり木が無く、走らせれば箱へ書く∴［未測］ |
| board_write.py | ― | 空 value `k=` は乙［字面・未走］ | 同左 | 甲 rc2［実走］ | 走らせれば板へ PATCH |
| km_send.sh | 甲 rc2 L17［字面］ | 甲（agent_letter に任せる）［字面］ | 同左［字面］ | 甲 rc2 L13［字面］ | 禁ゆゑ［未走］ |
| l1send | 甲（agent_letter に任せ rc4）［字面］ | 同左［字面］ | 同左［字面］ | 甲 rc2［字面］ | 本物の便を出し得るゆゑ［未走］ |
| mac_send.py | rc3［実走］ | rc3［実走］ | rc3［実走］ | 甲 rc2［実走］（引数無し／`send` のみ） | 21。★rc3 は標の門で、対照 c も同じ rc3★ ∴ 空を撥ねる門ではない（下の 4.） |

## 撥ねない器（名指し・［実走］で見た物だけを断定する）

1. **agent_letter.py**：⒟で rc0［実走］。usage を刷って `return 0` する（L166）。呼ぶ側の `|| die` が効かない。9/19 と同じ。
2. **sb-* 7本**（sb-ashigaru-mac-1/2/3・sb-gunshi-mac・sb-shogun-mac・sb-gakushu-bucho・sb-karo-mac）：`write` だけで rc0［実走・7本とも］。sb-karo-mac 以外の6本は `write letter` だけでも rc0［実走］。wrapper が `write` の後ろを agent_letter へ渡し、1. に当たる。sb だけは［未測］。
3. **inbox_write.sh（稼働木の版）**：⒝空白のみ（argv・stdin）と ⒞改行のみ（argv）を、名の門・DEFERRAL gate まで通す［実走］。生箱（ashigaru-mac-2）宛なら dead-inbox gate も通す［実走］。
   - 死箱（karo-mac 等4箱）宛は dead-inbox gate が胴に関わりなく rc68 で止める［実走・対照も rc68］。∴ karo-mac 宛に限れば、空の胴は箱へ届かない。ただし空を撥ねたのではない。
   - dead-inbox gate より後（増幅 guard・cross-PC bridge・flock 書込）は［未測］。ここで空を撥ねるかは断定しない（字面では増幅 guard は `[a→b][t]` の数だけを見ており、空の検めは見当たらない）。
4. **mac_send.py**：空の胴を撥ねる門を持たない［字面 L83］。四形が止まるのは「標が本文に無い」ためで、対照も同じ rc3［実走］。標が本文に在れば（例：空白を標にする）空白の胴も L85 へ進み得る［字面・未走］。
5. **board_write.py**：`key=`（空 value）をそのまま PATCH の body に入れる［字面・未走］。

## 受入の範囲（限定の明記）

- 本 census が断定するのは［実走］の欄だけである。
- ［字面］の欄（origin/main 版 inbox_write・board_write の空 value・km_send.sh・l1send・sb-karo-mac の `write letter`・mac_send.py の標を空白にした形）は見込みであり、受入の断定から外す。
- ［未測］の欄（sb・inbox_write 稼働木の dead-inbox gate より後・origin/main 版 inbox_write の実走）は、測っていないことだけを述べる。
- 走らせなかった理由は一つである：これらは止まり木を持たず、走らせれば板・箱・DB へ本当に書くか、本物の便を出し得る。下命の「器は変へず、空便は出さない」に従った。

## 9/19 から良くなった点・訂正

- 良くなった：agent_letter の `--content-file` 路は、空の3形と旗だけの形を撥ねる。
- 新しい3本（km_send.sh・l1send・mac_send.py）：km_send.sh と l1send は自らの門か任せた先で四形を撥ねる見込み［字面］。mac_send.py は［実走］で止まるが標の門であり、空の門ではない（REVISE⑤ で訂正・前版は「甲」と書いていた）。
- 己の器の黄を捕へて直した：1度目の実測（`raw/_first/`）では、inbox_write の argv ⒞ が rc1 と出た。
  - 種を読む関数が `$()` で包まれていたため、末尾の改行が落ちて E2 が0字になっていた。
  - 変数へ直に入れる形に直した。種の字数の assert（E0=0・E1=3・E2=1・C=29）を足して走らせ直した結果、rc0（乙）と出た。
  - 1度目の結果を正と取ってはならない。
- REVISE⑤ で訂正：前版（commit 3bca58ea）は「他の sb-* は sha が 9/19 と同じ」ことを根拠に代表1本で済ませ、inbox_write の後段を丙で置いた。今版は sb-* 7本と inbox_write の後段2門を［実走］で測り、全行に［実走／字面／未測］を付けた。

## 案（据ゑない・器は変へていない）

- agent_letter：⒟で usage を刷る時は rc2 を返す。
- inbox_write：L29 の検めを strip 後の空に広げる。
- board_write：空 value を撥ねる。空へ戻す時は明示の `null` を使ふ。
- どれも変更統制の対象である（委員長の許可が要る）。専任は彫らない。

## 測れていない物

- sb（`.sb_env` を読む wrapper）の四形。
- inbox_write 稼働木の dead-inbox gate より後（増幅 guard・bridge・flock 書込）。
- origin/main 版 inbox_write の実走（止まり木が無い）。
- board_write の空 value の実走。
- km_send.sh・l1send の実走。
- sb-karo-mac の `write letter` のみ。
- mac_send.py の、標が本文に在る時の空白の胴。
