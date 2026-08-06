# target `4a0e9036` の断面における述語①の成否（母集団列挙・足軽5号）

## 下命

karo-second msg_20260807_021704_b918f5eb (2026-08-07T02:17:04)。

契約名 = 「target `4a0e9036` の断面における述語①の成否」
述語①(本部長殿逐語) = 「全occupancy-changing入口が共通domain commandを通る」
必須陽性対照三つ = appointment_service E-3／diagonal_service 317・375／appointment_grid 534
境界 = 測るのみ・実装fix 0／commit 0／push 0／merge 0／DDL 0／migration 0・a1木は読取のみ・②③④⑤には手を出さぬ

★測時=2026-08-07T02:24:04+0900、盤を測ってから本便を書く（karo-second令⑤の条を当職も順守）★

## 使用worktree

`/tmp/resimg-verify5-gate4b-4a0e9036-20260807`（前工区で作成済・target `4a0e9036ed94022d79baa4a1e2cf88d5827eec12`
へdetached HEAD・`git status --porcelain`測時点で無変更確認済・独立scratch dir要件を既に充足の為
再作成せず流用）。a1のworktree(`/tmp/resimg-cycle2-f123-clean-20260806`)は本工区でも読取のみ
（a1が本commit以降の作業を継続中でdirty＝当然・裁定せず記録のみ）。

## 母集団の定義（★先に書く★）

**「occupancy-changing入口」= `appointments` table への write（`conn.execute` による raw SQL、
または `appointment_lifecycle.py` の4共通command経由）のうち、以下いずれかの列を変更するもの**:
`status`（active↔`cancelled`/`no_show`のboundary跨ぎに限る）・`unit_id`・`start_time`・
`end_time`・`duration_minutes`。★これらはappointment_slot_claimsのPK(clinic_id,unit_id,slot_start)
または「どのslotを占有するか」を直接左右する列であり、占有の変更そのものを表す★。

**共通domain command = `backend/services/appointment_lifecycle.py` の公開関数4つ**
（委譲先4つ、当module docstringに明記）:
`create_appointment_with_claim`（create-with-claim）／`move_appointment_slot`
（reschedule-sync）／`deactivate_appointment`（deactivate-release）／
`reactivate_appointment`（reactivate-claim）。

**除外する物（★「全件」の隣に書く★）**:
1. **非occupancy列のみのUPDATE**（version/updated_at/updated_by/modification_count/
   cancel_type・cancel_reason・cancelled_at・cancelled_by/linked_appointment_id・
   link_type・link_order/prediction_score・prediction_label）——占有先(slot)を左右しない
   帳簿列に限定される書込み。
2. **statusをactive集合内でのみ遷移させる書込み**（例: confirmed→confirmed系,
   visit_statusのみarrived/in_tx/billing/done等）——ACTIVE_SQL(`booking_concurrency_root.py`)
   の述語 `status NOT IN ('cancelled','no_show')` に照らし、active↔inactiveの境界を跨がぬ限り
   占有に影響しない。
3. **`appointment_lifecycle.py`自身の内部UPDATE**（4関数の実装本体）——呼び手ではなく
   共通command自体ゆえ「委譲したか」を問う対象外。
4. **DBマイグレーション/schema定義スクリプト**（`booking_concurrency_root.py`の
   `CREATE TABLE`/one-time backfill、`appointment_tables.py`のtable rebuild）——
   実行時のuser操作起点ではなく一度限りのschema進化ゆえ「入口」の母集団に含めない。
5. **到達不能と既に確定済のcase**（`email_parser.py:109`・INSERT列にunit_id欠落＝
   NOT NULL制約で必ず例外→`except Exception: return None`で握り潰し・前工区(a4/a6)で
   確定済・別票でlocked test化・★本工区外として母集団から除くが存在自体は明記★）。

## 母集団（列挙・一件ずつ判定）

### A. 共通commandへ委譲済（PASS）— 17件

| # | 呼び手 | 経路 | 委譲先 |
|---|---|---|---|
| A1 | appointment_service.py:333 (create_appointment) | insert_sql委譲 | create_appointment_with_claim |
| A2 | appointment_service.py:481+488 (update_appointment) | raw UPDATE直後にmove委譲 | move_appointment_slot ★=positive control「appointment_service E-3」★ |
| A3 | appointment_service.py:598 | 直接呼出 | deactivate_appointment |
| A4 | appointment_service.py:698 | 直接呼出 | deactivate_appointment |
| A5 | web_reservation/booking_service.py:288 | insert_sql委譲 | create_appointment_with_claim |
| A6 | web_reservation/booking_service.py:409+416 | raw UPDATE直後にmove委譲 | move_appointment_slot |
| A7 | web_reservation/booking_service.py:474 | 直接呼出 | deactivate_appointment |
| A8 | diagonal_service.py:127 | insert_sql委譲 | create_appointment_with_claim |
| A9 | diagonal_service.py:163 | insert_sql委譲 | create_appointment_with_claim |
| A10 | diagonal_service.py:277+284 (update_linked_appointment・diagonal_first枝) | raw UPDATE直後にmove委譲 | move_appointment_slot |
| A11 | diagonal_service.py:301+305 (update_linked_appointment・diagonal_second枝) | raw UPDATE直後にmove委譲 | move_appointment_slot |
| A12 | diagonal_service.py:355 (cancel_linked_appointment) | 直接呼出 | deactivate_appointment |
| A13 | booking_manage.py:279+291 (change_booking) | raw UPDATE直後にmove委譲 | move_appointment_slot |
| A14 | appointment_detail.py:117+128 (api_update_detail) | raw UPDATE直後にmove委譲 | move_appointment_slot |
| A15 | appointment_grid.py:769+792 (move drag) | raw UPDATE直後にmove委譲 | move_appointment_slot |
| A16 | appointment_grid.py:519 (status endpoint cancel枝) | 直接呼出 | deactivate_appointment |
| A17 | appointment_grid.py:543 (status endpoint reactivate枝) | 直接呼出 | reactivate_appointment |

★下書き時点で見出しを14件と書きA1-A17まで列挙した後に数え違いへ気付き17件へ訂正した
（karo-second令⑤に従い明記——増えたのではなく当職の見出し表記の誤り。列挙内容自体は
不変）。

### B. ★委譲されていない・述語①不成立（構造上NOT-DELEGATED）★ — 2件（+境界事例1件）

| # | 箇所 | 内容 | 判定理由 |
|---|---|---|---|
| B1 | `diagonal_service.py` `propagate_status` (status書込 line 411、release呼出 line ~427) | linked予約が`no_show`へ連動する際、`UPDATE appointments SET status=?,visit_status=?...`を直書きし、`deactivate_appointment`を通らず、代わりに`concurrency_root.release_appointment_slots`を★直接★呼ぶ | active(no_show化)→inactive境界を跨ぐ占有変更だが、共通command 4つのいずれも経由せず、一段下のprimitiveを直接叩いている。★コード自身のコメント（2026-08-06家老second指摘）が「共通command層への未委譲の到達可能case」と明記済み★——当職の発見ではなく既知の自己申告事項の確認 |
| B2 | `routers/next_appointment.py:71` (INSERT) + `:84` (claim呼出) | 予約作成をraw INSERTで行い、`create_appointment_with_claim`を経由せず、`concurrency_root.claim_appointment_slots`を★直接★呼ぶ | create系だが4共通commandの外。★コード自身のコメント（2026-08-06）が「層外writer」だった経緯とclaim追加による部分是正を明記済み★——idempotency_key機構等、`create_appointment_with_claim`が持つ他の保護は本経路に無い |
| B3(境界) | `appointment_grid.py:534`（status endpoint「booked」枝）＝★陽性対照「appointment_grid 534」の実測★ | `req.status=="booked"`時、`elif new_status:`枝で`UPDATE appointments SET status=?,visit_status=NULL...`を直書き。この枝は`apt["status"]`の現在値を条件に含まぬ為、**もし呼出時点で`apt["status"]=="cancelled"`であっても本枝が実行され、`reactivate_appointment`（slot再claim）を経由しない** | ★正直な留保★: backendコード単体では、cancelled状態から「booked」を選ぶ経路を阻む guard が本file内に見当たらぬ。フロントエンドがcancelled予約に対し「booked」選択肢自体を出さない設計であれば実質到達不能だが、それは本工区(backend測定)の射程外につき★未検証★。よって「構造上NOT-DELEGATED」と「到達可能性は未確認」を分けて記録する |

## 陽性対照 三つの実測結果（令名指し・逐語照合）

1. **appointment_service E-3** → A2 (`appointment_service.py:481+488`)。★委譲済・PASS★。
   前工区(Gate4b ⒜)で`test_move_appointment_slot_inactive_guard_e3_a1.py`により
   E-3 guard自体も4/4 PASS確認済（本便では委譲経路の存在のみ再確認）。
2. **diagonal_service 317・375** → ★行番号不一致を正直に記録★。当職の対象commit断面で
   317行目・375行目そのものは `cancel_linked_appointment` のparameter定義行／
   raw UPDATE末尾の閉じ括弧行であり、occupancy書込みの実体を指していない
   （`awk 'NR==317{print} NR==375{print}'`で実測・逐語=317行目`    conn: sqlite3.Connection,`
   ／375行目`            )`）。★これが令の誤記か当職の断面と令作成者の断面が
   数行ずれておるかは当職には判じ得ぬ★。意味的に最も近い候補群（診断:
   diagonal_serviceのmove/cancel委譲群）は A10・A11・A12（いずれもPASS・委譲済）
   および B1（`propagate_status`・未委譲）であり、当職はこの4件を代替候補として
   実測し記録した。★数字の一致は取れておらぬ事を明記する（誤りを「一致した」で覆わぬ）★。
3. **appointment_grid 534** → B3。★委譲されておらぬ事を実測で確認★。当職の推測では
   これは「委譲済の既知good example」ではなく「raw SQLだが到達可能性未確定のcase」
   であった。令の意図（陽性対照＝既知の答え合わせ）と当職の実測結果が食い違う可能性が
   ある為、★裁定を仰がず、実測した通りをそのまま報告する★（言い換えて期待値へ寄せない）。

## dead code の発見（境界事例・欠陥数へは混ぜない）

`appointment_grid.py:525-531`（`elif new_status and new_visit_status:`枝）は、
`_FRONT_TO_BACK_STATUS`（line 470-478）の全7エントリを実読した結果、
`new_status`と`new_visit_status`が同時に真になる組は存在せず、★到達不能★
（email_parser.py:109と同型のパターン）。母集団には数えるが、実行され得ぬゆえ
述語①の成否判定自体が意味を成さぬ枝として区別する。

## 結果（述語・断面明記）

**「target `4a0e9036` の断面における述語①」＝ ★不成立（全件ではない）★**。

- 委譲済(PASS) = 17件（A1-A17）
- 未委譲(述語①不成立) = 2件確定（B1: diagonal_service propagate_status no_show／
  B2: next_appointment.py create）+ 1件到達可能性未検証(B3: appointment_grid「booked」枝)
- 到達不能ゆえ判定対象外 = 2件（email_parser.py:109・母集団定義⑤で除外／
  appointment_grid.py:525-531 dead branch・母集団には含めたが実行され得ず）

B1・B2はいずれも★コード自身のコメントが「未委譲の既知case」と自己申告済み★——
当職が新たに発見したものではなく、既存の自己申告を独立に実測・確認したものである。
B3は当職が今回新たに気づいた候補であり、到達可能性は backend 単体では確定できない。

## 本測りが覆っていない層

- フロントエンドの入力制約（「booked」選択肢がcancelled予約に対し実際に提示されるか）は
  backend測定の射程外——B3の到達可能性はここに依存し★未確定のまま残す★。
- B1・B2が「機能的に危険か」（=実際に二重予約やstale claimを引き起こすか）は本工区の
  射程外。本工区は「共通domain commandを通るか否か」という構造的述語のみを測っており、
  B1は`release_appointment_slots`を直接呼ぶ事で機能的には保護されている可能性がある
  （測っていない）。
- gate3 detector（a4作）自体を当職は再実装/再走していない。本列挙は当職が独立に
  grep+直読で行った物であり、a4/a6のdetectorとの突合せ(件数一致確認)は行っていない。

## 境界遵守声明

測るのみ・実装fix 0（当職のworktree `git status --porcelain` 測時点で無変更）・commit 0・
push 0・merge 0・DDL 0・migration 0・a1木は読取のみ（write 0）・②③④⑤へは手を出していない
（B1/B2/B3はいずれも「読んで記録した」のみで一切のcode変更なし）。

## 令⑤の条二つ・当職の適用

- 「盤は測ってから書け」: 本便は全実測（grep・sed直読・git show blob照合）を先に終えた
  02:24以降にのみ書いた。
- 「数が変わった時、誤りか増えたか進んだかを書け」: 上記A節で「14件」→「17件」の
  見出し表記誤りを訂正の際に明記した（増えたのではなく数え違い）。
