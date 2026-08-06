# 足軽4号 → 家老second: reserveimage-cycle2-gate2-4-handoff patch 実読監査（read-only）

断面: 2026-08-06T08:5x JST（当職 実測・以下は悉く 己で取った値）
本便は read-only。apply/worktree新設/commit/DB書込/test実走は 一切 行っておらぬ。

## §0 未測（冒頭に置く）

- 本便では **①〜⑬の13項matrixを実走してはおらぬ**（下命(3)②「走らせるな」に従う・紙上設計のみ）。
- appointment_service.py の staff 経路が booking_concurrency_root.py の idempotency 機構（acquire/complete_idempotency）を **一切 呼んでおらぬ**事は import 文の実測で確認したが、staff 側の他の呼出し元（appointments.py 等 patch 対象外）は **未読**。
- update_booking の `conn.execute(f"UPDATE appointments SET ...")` 以降（commit 有無等）は diff の可視範囲外ゆえ **未測**。

## §1 patch/rollback/base の実測（claim vs 監査済、同じ行）

| 項目 | 家老second 申告値 (staged) | 当職 実測値 (audited) | 一致 |
|---|---|---|---|
| patch 行数 | 932行 | 932行 | 一致 |
| patch bytes | 39313 bytes | 39313 bytes | 一致 |
| patch sha256 | 2542891ace...5280835 | `2542891ace734a458637fc634cf9712283faa1b25639c8d92de95ba7d5280835`（64桁） | 一致 |
| rollback 行数 | 36行 | 36行 | 一致 |
| rollback sha256 | b710adf34...12171 | `b710adf340636644d5a3ff5d3920d4db6ded43268f9646c44e8de5e669312171`（64桁） | 一致 |
| base repo HEAD | 7d463edae84c704edabbd9da5465078dc62e55b1 | `7d463edae84c704edabbd9da5465078dc62e55b1`（40桁） | 一致 |
| `find /tmp /home/hakudokai -xdev -type f -size 39313c` | 一件（同patch） | 一件（同patch、再実行し確認） | 一致 |

sha256/行数/HEAD/find は悉く **監査済**（当職が己で sha256sum・wc・git rev-parse・find を打ち直した値）。staged 値との差異 **0件**。

## §2 (2)①〜④ 再測（一致/不一致 同じ行）

① `diff --git` 件数=6（申告一致） → 再測 `grep -c '^diff --git'`=**6、一致**。対象6path も申告と完全一致。

② `/tmp/resimg-cycle2-impl-20260806` dirty=patch そのもの、`git apply --check --reverse` rc=0 →
再測: `git status --porcelain` dirty件数=**6件**（M×4・??×2、申告の6件と一致）。
`git -C /tmp/resimg-cycle2-impl-20260806 apply --check --reverse` → **rc=0、出力0byte、一致**。

③ 清きbase 7d463ed には当たる、`git apply --check -p1` rc=0 →
再測: base の該当4file（booking.py/appointment_service.py/booking_service.py/test_phase2_2_booking.py）を `git show 7d463ed:<path>` で scratchpad へ read-only 取出し、db/migrations・tests 配下の新規2fileの親dirも作成のうえ
`git apply --check -p1` → **rc=0、出力0byte、一致**。

④ `/tmp/resimg-cycle2-base-audit` rc=1、因は同worktree自身のdirty1件（M test_phase2_2_booking.py）で patch の瑕ではない →
再測: `git status --porcelain`=**1件のみ（M test_phase2_2_booking.py）、申告と一致**。
`git apply --check -p1` → **rc=1、一致**。エラー文=`patch failed: backend/tests/web_reservation/test_phase2_2_booking.py:6` / `patch does not apply`（同一fileに局所化）。
**追加検算（当職独自）**: 残り5path を `--include=<path>` で個別 `--check` したところ **悉く rc=0**（申告④の主張「他5pathは無傷」を裏付ける独立証跡）。
なお当該dirty diff実物を読んだところ、対象file冒頭に `import threading`/`import time` を追加しテスト関数群を追加する内容で、**patch 自身が加えようとする変更とほぼ同型の先行変更**が既にworktreeへ入っており、これが context 不一致を生んでいる（推測でなく diff 実読による）。

**罠の再現（申告(1)注記の検算）**: `git apply --check | head` 相当を試しはせなんだが、申告の`rc=141`機序（SIGPIPE）は本監査でも `[ $rc -ne 0 ] && cat ...` の `&&` 短絡でBashツールが「Exit code 1」を誤表示する事象として **別形で実際に踏んだ**（個別5file全rc=0だったにも関わらず最終行の `[ ]` テストがfalseとなり `&&` 全体がrc=1を返した）。rc の取り方は罠が多いという申告の指摘は **独立に裏付けられた**。

**①〜④ 総括**: 4項目とも申告と実測が **悉く一致**。不一致 0件。

## §3 patch 全6path 実読・誤り/危うき箇所（当てて終いにせず）

### 3-1 booking.py（api層）
- `request.headers.get("Idempotency-Key")` を6番目の位置引数として渡す。`booking_service.create_booking` のsignature順（conn, clinic_id, patient_no, menu_id, start_time, treatment_content=None, idempotency_key=None）と実測突合し **順一致**。誤り無し。

### 3-2 appointment_service.py（staff経路）
- `sqlite3` import は base file に既存（実測済、L10）。`except sqlite3.IntegrityError` は成立する。
- 旧: INSERT直後に即commit → 履歴INSERT→再commit（2 commit）。
  新: INSERT後、`claim_appointment_slots` と履歴INSERTを **同一transaction・単一commit** にまとめ、IntegrityErrorで丸ごとrollback。
  **これは意図的な改善**（コメント「履歴も予約・slot claimsと同一transactionで記録する」と整合）。ただし **挙動変化**である点は明記すべき: 旧コードは予約行のcommitを履歴insertの成否から独立させていたが、新コードは予約行自体もslot claim失敗時に道連れでrollbackされる。これが許容される設計判断か（呼出元がappointment_idの存在を前提にしていないか）は **appointment_service.py の呼出元（patch対象外）を読まねば断じられぬ**。
- **★staff経路には idempotency機構（acquire/complete_idempotency）が一切配線されておらぬ★**（importにも無し、実測済）。slot claim（二重予約防止）のみ staff側にも効くが、**同一要求再送の重複防止はstaff経路には及ばぬ**。これは(3)節本文の「patch自体に瑕は無い」主張とは別軸の**設計上の非対称**であり、「誤り」ではなく「未実装範囲」として報告する（咎めるなの条・零ならば零と書け、に従い★staff側idempotencyは0件★と明記）。

### 3-3 booking_service.py（web経路・本体）
- `BEGIN IMMEDIATE` を関数冒頭で取得し、writer を直列化する設計。SQLite側で後続要求が先行commit後の行を見てから判定できるため、TOCTOU窓を閉じる設計として妥当（preflight文書§9-Aの推奨と整合）。
- 例外分岐は `BookingConflictError` → `(IdempotencyConflict, IdempotencyInProgress)` → `sqlite3.IntegrityError` → `sqlite3.OperationalError`(locked/busy時のみdomain化) → `Exception`（rollbackして再raise）の順で、型の重複衝突は無い。実読で確認。
- **★危うき箇所★**: `existing`（同一要求の簡易replay一致）判定は `if existing and not (root_enabled and idempotency_key):` で、**idempotency_keyが無い場合は常にこの簡易replayへ流れ**、`_check_conflict` を経ずに早期returnする。これはmigration適用前後を問わず有効な経路であり、**idempotency_keyを使わない全クライアントが対象**になる（api層はheaderが無ければNoneを渡すのみで必須化していない）。挙動としては「完全一致する予約が既にあれば同じ内容を返す」なので害は無さそうだが、**この早期return分岐が`_check_conflict`を一度も通さない**ことは、conflictの定義（offset重複等）によっては見落としが無いか要検討点として記録する（今回のscope=読取のみゆえ裁定はせぬ）。
- `update_booking`: `release_appointment_slots`→`claim_appointment_slots`の順で新slotを確保してから、実際の`UPDATE appointments SET ...`が走る（diffの可視範囲ではその後）。claim失敗時はrollback+raiseで実UPDATE到達前に止まるため安全に見えるが、**このUPDATE以降にconn.commit()が置かれているかはdiff外（未測）**。
- `cancel_booking`: `UPDATE`実行→`release_appointment_slots`の順。releaseがUPDATEの後という順序自体に問題は無いが、両者を包む例外処理・commit位置がdiff外で **未測**。

### 3-4 test_phase2_2_booking.py
- 新規3testを実読。`monkeypatch.setattr(booking_service, "_check_conflict", ...)` はモジュール属性差替えであり、`create_booking`内の裸名参照が都度モジュール辞書を引く仕様と整合するため機能する。誤り無し。
- `test_true_two_connection_same_slot_only_one_active_row`: barrier同期は `_check_conflict` 呼出前後で行われるが、実際の直列化点は `BEGIN IMMEDIATE`（`_check_conflict`より前）であるため、**barrier機構自体は本root-cure下ではほぼ役割を失っている**（BEGIN IMMEDIATEの時点で片方は既にblockされる）。テストの結論（active row=1, error=1）自体は成立するが、"barrier"が検証している同期点と実際の排他点が **設計上ズレている**点は指摘に値する（誤りではないが、テストの説明コメントが古い設計を前提にしている可能性）。

### 3-5 booking_concurrency_root.py（新規migration本体）
- `_appointments_ddl_without_broken_unique()`: base DDL文字列の厳密一致置換（12-space indent含め実測で一致確認済）。needle不一致時は `RuntimeError` で即fail-fast。fragile だが安全側。
- **★最重要の危うき箇所★**: `apply_booking_concurrency_root()` は `conn.commit()` を `try` ブロック内（スキーマ再構築の直後）で実行し、その **後に** `PRAGMA foreign_key_check` を走らせて `fk_errors` があれば `RuntimeError` を投げる。**このraiseの時点で既にcommit済み**であり、`except`節のrollbackは対象外（`try`は既に正常終了しcommitまで済んでいるため）。
  ∴ **fk_check failが起きた場合、schema変更は committed のまま raise される**。関数内部にはこのケースの自動ロールバック手段が無い。
  rollback手順書（reserveimage-cycle2-ddl-rehearsal-rollback-20260806.md）が「migration後の検査...が1件でもFAILした場合」に**外部ファイルbackup復元**を唯一のexact rollbackと明記しているのは、この設計（関数内部が自己ロールバックしない）と整合しており、**運用側は認識済**と見える。ただし「patch自体に瑕は無い」（申告(2)③の趣旨）を「migration適用は無条件に安全」と読み違えぬよう、**fk_check fail時は外部backup復元が必須**という前提を本監査でも明記しておく。
- `appointment_history.appointment_id REFERENCES appointments(appointment_id)` を実測確認（base file L123）。table rename→再作成の期間はFK名前解決の対象になり得るため、この事後fk_checkは実質的に意味のある安全網である。ただし上記の通り「fail時は非commit」ではない点に注意。

### 3-6 test_booking_concurrency_root_migration.py
- `test_gate3_rehearsal_schema_backfill_and_exact_rollback`: migration実行後、**関数内部のrollbackではなく、事前に取ったfile-levelバックアップのbyte-for-byte復元**でrollbackを模擬している。これは§3-5の設計（内部非自己ロールバック）と整合しており、rollback手順書が要求する手順を実際に演習している点は妥当。
- 他5testは実読の範囲で誤り検出せず（fixture・assertion・claim整合は一貫）。

### 3-7 誤り摘出まとめ（零件は零と書く）
- **構文/import/signature順の誤り**: 0件（実測範囲内）。
- **論理的な誤り（明確なバグ）**: 0件（明確に「動かぬ」箇所は見つからず）。
- **設計上の危うさ/非対称（誤りではないが要注意）**: 3件
  1. staff経路（appointment_service.py）にidempotency機構が未配線（slot claimのみ）。
  2. `apply_booking_concurrency_root`のfk_check失敗時、内部commit済みで自己rollback無し（外部backup復元が前提の設計）。
  3. `existing`簡易replay早期returnがidempotency_key未使用時は常時有効で`_check_conflict`を経由しない。

## §4 13項matrix の走らせ方設計（紙上のみ・★走らせておらぬ★）

出所: `reserveimage-cycle2-concurrency-idempotency-evidence-and-root-design-20260806.md` §6「migration適用前の必須RED/GREEN」①〜⑬（rollback文書「13項＋⑬」の⑬は同§6の項番13そのもの）。

| # | 項目 | 本patchでの既存カバー | 走らせ方（紙上設計） |
|---|---|---|---|
| 1 | baseline duplicate scan | `test_gate2_baseline_scan_zero_and_15_minute_grid` | 隔離rehearsal DBへ`scan_active_overlaps`/`scan_slot_granularity`を先に走らせ、overlap=0・invalid_grid=0を確認してからのみ§2へ進む（fail時は§4rollbackへ即分岐、migration自体を試みない） |
| 2 | same key/same payload → 同じID | `test_durable_idempotency_key_and_slot_claims_after_migration`前半 | 同一idempotency_keyで2回`create_booking`を呼び、`retry == first`かつ`appointments`行数不変を確認（既存test既に実施） |
| 3 | same key/different payload → 409 | 同test後半 | 同一key・別payloadで`BookingConflictError(match="different payload")`を確認（既存test既に実施） |
| 4 | restart/reconnect後のretry | `test_idempotency_reconnect_mismatch_and_stale_pending_does_not_block_slot`が近似 | 同testはconn close/reopenを模擬しTTL失効後の再claimを検証済。★「processそのものの再起動」は未検証★－file-backed DBへの新規connectで代替する設計は既存testで足りるかを要判定（新規実行はせぬ） |
| 5 | 真の2接続same slot | `test_true_two_connection_same_slot_only_one_active_row` | 既存test。ただしbarrierの同期点(§3-4指摘)がBEGIN IMMEDIATEの実排他点とズレている旨を実行前提として記録した上で走らせる設計とする |
| 6 | offset overlap | `test_slot_claims_block_offset_overlap_and_partial_index_blocks_status_bypass`前半 | 既存test。15分slotを跨ぐoffset(09:30開始・9:00枠と重複)でIntegrityErrorを確認済 |
| 7 | T/space cross-channel | **無し（gap）** | 設計: staff側（appointment_service.py, T区切り想定）とWeb側（space区切り）で同一論理時刻へ2threadから同時create、`claim_appointment_slots`のPK衝突で片方のみ成功することを検証する新規testを要設計（本監査では設計のみ・作成せず） |
| 8 | confirmed/tentative status差 | `test_slot_claims_block_offset_overlap_and_partial_index_blocks_status_bypass`後半 | 既存test。status違い("tentative")でも`_add`単体INSERTがpartial unique indexでIntegrityErrorになることを確認済 |
| 9 | cancel後のslot再利用 | `test_cancel_release_allows_slot_reuse` | 既存test。cancel→release→同slotへ新規claimが成功することを確認済 |
| 10 | reschedule競合: 旧claimを失わずatomic rollback | **無し（gap）** | 設計: `update_booking`で新時刻へのclaimが失敗するケースを作り、①旧claimが削除されたままになっていないか（release→claim失敗時に旧claimも失った状態で終わっていないか）②例外がBookingConflictErrorとして安定して伝播するか、をrollback後の`appointment_slot_claims`行数で検証する新規testを要設計（§3-3で指摘した「releaseが先・claimが後」の順序ゆえ、claim失敗時に**旧claimは既に消えている**——これは本監査での★新規finding★であり、item10のgapを埋める過程で見つかった） |
| 11 | staff/Web双方が同じclaims/idempotency contract | 部分（slot claimsのみ） | 設計: staff経路(`appointment_service.create_appointment`)がidempotency_keyを受け取れない現状を前提に、①slot claims契約は共通（実測済）②idempotency契約は非対称（§3-2既述）という2軸に分けて評価する。「同じcontractを使用」は**slot claimsのみ真、idempotencyは偽**と裁定材料を分けて渡す設計とする |
| 12 | migration rollback/forward-fix手順 | `test_gate3_rehearsal_schema_backfill_and_exact_rollback` + rollback runbook | 既存test+runbookで演習済（§3-5参照）。runbookの手順1-6を実際のrehearsal DBに対し順に実行する設計（本監査では実行せず） |
| 13 | migration後も既知欠陥snapshotへ陽性対照を当てればRED維持 | **無し（gap）** | 設計: migration適用**前**のservice snapshot（root_tables_present=False相当のコード、または`_check_conflict`のみの旧経路）に対して、item5/6/7と同じ陽性対照testを当て、`active_count==2`等の意図的RED（欠陥再現）を確認する。migration適用**後**は同じ陽性対照がGREEN(active_count==1)に転じることをペアで示す設計とする（検出器の生死を確かめる回、§3の本日規律「0件の三問」③検出器は生きているか、に相当） |

**総括**: 13項中、★9項は本patchの既存9testで直接/近似カバー済★、★3項(⑦T/space cross-channel・⑩reschedule atomic rollback・⑬既知欠陥への陽性対照維持)は本patchにテストが無くgap★、★1項(④restart/reconnect)は近似カバーだが「真のprocess再起動」は未検証★。
gap中、**item10の設計検討そのものから新規finding**（reschedule時のrelease→claim順序ゆえclaim失敗でも旧claimは戻らない）を得た——これは §3 の誤り摘出に本来含めるべき事項であり、ここに追記する。

## §5 己が本工区で直した誤り

無し（read-onlyゆえ直す手を持たぬ。見つけた事項は悉く上記へ記録するに留めた）。

---
生成: ashigaru4 / 2026-08-06 / read-only監査、repo内file・patch対象file 一切未変更。
