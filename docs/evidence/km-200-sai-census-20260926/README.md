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

## 母數

- 根 `~/bin` の深さ1にある、実行できる file のうち、名に sb|letter|inbox|board|send を含み、.bak と .pre を除いた物：17本（`raw/10_bosuu.txt`・11:57:54）。
- このうち送る器ではない4本を除いた：
  - cc_goal_from_board.py
  - inbox_mark_read.py
  - km_inbox_read_mark.sh
  - orphan_inbox_trap.py
- sb-* は同じ形の wrapper ゆゑ、自席の sb-ashigaru-mac-1 を1本走らせて代表にした。他の sb-* は sha が 9/19 と同じ。
- repo 側 `scripts/inbox_write.sh` は稼働木の版（409行・563271ea…）と origin/main の版（366行・96a1e235…）の2版を別に数へた。
- .bak と .pre の族は53本あるが、census の外に置いた（呼ばれる器ではない）。

## 測り方（板にも箱にも出さない）

- 種は `raw/seed/` の4本。sha と hex は `raw/12_seed_sha.txt`。
  - e0 は 0byte。
  - e1 は半角空白・TAB・全角空白。
  - e2 は改行のみ。
  - c は対照。
- 器は `raw/20_jissoku.sh` を使った。
  - agent_letter は `--dry-run` で走らせた。胴の門 L223 は dry-run より前にある。
  - inbox_write は `IW_NAME_TEST_ONLY=1` で走らせた。L75 で exit 0 になり、胴の門 L29 はこれより前にある。
  - board_write は引数無しだけ走らせた。
- 字面の判定は `raw/30_jimen.txt` に逐語で置いた。km_send.sh は禁ゆゑ走らせていない。

## 判定表（甲=撥ねる・乙=rc0 で通す・丙=測れぬ）

| 器・路 | ⒜0byte | ⒝空白のみ | ⒞改行のみ | ⒟引数無し | 拠 |
|---|---|---|---|---|---|
| agent_letter.py argv | 甲 rc2 | 甲 rc2 | 甲 rc2 | **乙 rc0**（usage を刷って0） | 実測 |
| agent_letter.py --content-file | 甲 rc2 | 甲 rc2 | 甲 rc2 | 甲 rc2（旗のみ） | 実測 |
| sb-ashigaru-mac-1（sb-* 代表） | 甲 rc2 | 甲 rc2 | 甲 rc2 | **乙 rc0**（`write letter` だけ、または `write` だけ）／甲 rc2（何も無い） | 実測 |
| inbox_write.sh 稼働木 argv | 甲 rc1 | **乙 rc0** | **乙 rc0** | 甲 rc1 | 実測（L75 まで） |
| inbox_write.sh 稼働木 stdin | 甲 rc1 | **乙 rc0** | 甲 rc1 | ― | 実測（L75 まで） |
| inbox_write.sh origin/main | 甲（字面） | 乙（字面） | 乙（字面） | 甲（字面） | 丙（止まり木が無い・走らせれば箱へ書く） |
| board_write.py | ― | 空 value `k=` は乙（字面） | 同左 | 甲 rc2 | ⒟は実測・他は丙（走らせれば板へ PATCH） |
| km_send.sh | 甲 rc2 L17 | 甲（agent_letter L223 に任せる） | 甲（同） | 甲 rc2 L13 | 字面・丙（禁ゆゑ走らせない） |
| l1send | 甲（agent_letter に任せる→ seq が無く rc4） | 甲（同） | 甲（同） | 甲 rc2 | 字面・丙 |
| mac_send.py | 甲 rc3 L83（標が本文に無い） | 甲 rc3 | 甲 rc3 | 甲 rc2 L70 | 字面・丙 |

## 撥ねない器（名指し）

1. **agent_letter.py**：⒟引数無しで rc0。本文が無くても rc0 のため、呼ぶ側の `|| die` が効かない。
   - usage を刷って `return 0` する。
   - 9/19 と同じ。版が変はっても残っている。
2. **sb-* wrapper**：`write letter` だけ、または `write` だけで rc0。
   - wrapper は `write` の後ろを丸ごと agent_letter に渡す。そこで 1. に当たる。
3. **inbox_write.sh（稼働木の版）**：⒝空白のみを argv と stdin の両方で、⒞改行のみを argv で、胴の門 L29 を通す。
   - L29 は `-z "$CONTENT"` だけを見て、strip していない。
   - L75 より後の門は測っていない。L75 より後で撥ねるかどうかは丙。
   - origin/main の版も L29 の字面は同じ。
4. **board_write.py**：`key=`（空 value）を字面の上でそのまま PATCH の body に入れる（L37〜44）。
   - 走らせれば板を書くことになるため、丙のまま置く。

## 9/19 から良くなった点・訂正

- 良くなった：agent_letter の `--content-file` 路は、空の3形と旗だけの形を撥ねる。
- 良くなった：新しい3本（km_send.sh・l1send・mac_send.py）は、自らの門か任せた先で四形を撥ねる（字面）。
- 己の器の黄を捕へて直した：1度目の実測（`raw/_first/`）では、inbox_write の argv ⒞ が rc1 と出た。
  - 種を読む関数が `$()` で包まれていたため、末尾の改行が落ちて E2 が0字になっていた。
  - 変数へ直に入れる形に直した。種の字数の assert（E0=0・E1=3・E2=1・C=29）を足して走らせ直した結果、rc0（乙）と出た。
  - 1度目の結果を正と取ってはならない。

## 案（据ゑない・器は変へていない）

- agent_letter：⒟で usage を刷る時は rc2 を返す。
- inbox_write：L29 の検めを strip 後の空に広げる。
- board_write：空 value を撥ねる。空へ戻す時は明示の `null` を使ふ。
- どれも変更統制の対象である（委員長の許可が要る）。専任は彫らない。

## 測れていない物

- inbox_write の L75 より後（DEFERRAL-GATE 以下）。
- origin/main 版 inbox_write の実走。
- board_write の空 value の実走。
- km_send.sh・l1send・mac_send.py の実走。
- 他の sb-*（sha が同じことを根拠に、代表で済ませた）。
