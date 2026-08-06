# 足軽4号「危うき三件」独立 read-only 三値判定 (足軽1号)

- 断面秒: 2026-08-06T09:13:42+0900
- 対象: /home/hakudokai/hermes-departments/honbucho/reports/reserveimage-cycle2-gate2-4-handoff-20260806.patch
  実測 sha256=2542891ace734a458637fc634cf9712283faa1b25639c8d92de95ba7d5280835、932行 (下命書記載値と一致確認)
- base側参照: `git -C /tmp/resimg-stage1-runtime-20260806 show 7d463edae84c704edabbd9da5465078dc62e55b1:<path>` (read-only、実在確認済 2026-08-06T02:05:00+0900コミット)
- 禁則順守: apply/worktree新設/DB/走行/hakudokai-dev書込み 一切なし。全て `git show` によるテキスト読取と patch本文読解のみ。

## 母集団宣言 (読了範囲)

1. patch本文: 932行全行 (100%)
2. base `backend/services/appointment_service.py`: `git show` で全740行取得・全行 grep+目視
3. 新規ファイル `backend/db/migrations/booking_concurrency_root.py`: patch差分から全301行(新規ファイル全量="@@ -0,0 +1,301@@"と一致)を復元し全行読了
4. `backend/services/web_reservation/booking_service.py`: patchの全4hunk("@@ -192,55 +202,140@@" "@@ -315,9 +410,12@@" "@@ -341,6 +439,19@@" "@@ -401,6 +512,7@@")を新ファイル行番号へ写像し全hunk範囲を読了 (hunk外の不変部分は未読=対象外)
5. `backend/api/appointments.py`: 全190行中 目視は1-40行のみ。ただし `grep -n "idempot\|Idempotency"` は全190行に対し実行(hit=0)。目視は部分・grep一致検索は全数。
6. patch全体に対する `grep -n "dempot"` 全932行 (100%) — Idempotency関連の全出現箇所を洗い出し、①の裏取りに使用。

## 判定

### ①「staff経路(appointment_service.py)にidempotency機構が未配線(slot claimsのみ)」→ ★㈠在る★

根拠:
- patch: `backend/services/appointment_service.py` hunk (元行218〜、diff内 read行25-59) は
  `from backend.db.migrations.booking_concurrency_root import claim_appointment_slots` を import し (diff内 read行21)、
  `create_appointment` 関数内で `claim_appointment_slots(...)` のみ呼ぶ (slot claims機構)。
  `acquire_idempotency` / `complete_idempotency` / `idempotency_key` は一切import・呼出なし。
- patch全体 grep "dempot" (932行) で `appointment_service.py` 側hunk内に1件もヒットなし。
- base側 `appointment_service.py` (全740行) にも idempotency 関連記述なし (`grep -i idempot` hit=0)。
  `create_appointment` シグネチャ (base行122-126) に `idempotency_key` 引数なし。patchでも追加されず。
- 呼出元 `backend/api/appointments.py` (全190行、grep全数実行 hit=0) は `create_appointment` をimportし
  `POST /api/appointments` (staff向けCRUD、`CreateAppointmentRequest.source: str = "staff"`) を提供。
  対照として web予約側 `backend/api/web_reservation/booking.py` は
  `request.headers.get("Idempotency-Key")` (diff行9) をservice層へ渡している — staff側に同等の配線なし。
- ∴ staff経路はslot claims(排他)のみでidempotency machinery(重複要求の同一視・completed replay)は未配線。実測で再現。

### ②「apply_booking_concurrency_rootはforeign_key_check失敗時に已にcommit済・自己rollback無し」→ ★㈠在る★

根拠 (復元後の `booking_concurrency_root.py` 実ファイル行番号):
- 284行目 `conn.commit()` — スキーマ移行(テーブルrename/再作成/index作成/booking_idempotency+appointment_slot_claims新設/backfill)を確定commit。
- 285-291行目 `except Exception: ... finally:` — この try節が保護するのは279-284行目 (backfillループ〜commit)までの例外のみ。
  commit(284行目)が例外なく完了すれば、except節はrollbackせずに素通りする。
- 293行目 `fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()` — **try/except/finally節の外**、
  つまり284行目のcommit確定・291行目のfinally完了の**後**に実行される。
- 294-295行目 `if fk_errors: raise RuntimeError(...)` — この分岐に到達した時点でDBは既にcommit済 (284行目)。
  このRuntimeError発生経路には rollback呼出が存在しない (285-291行目のtry/exceptは既に終了済のスコープ)。
- ∴ foreign_key_check失敗時、スキーマ移行は既にディスクへcommit済であり、関数内に自己rollbackの経路は無い。実測で再現。
  (テスト `test_gate3_rehearsal_schema_backfill_and_exact_rollback` はファイルコピーによる外部backup/restoreパターンを採っており、
  DB内部トランザクションでの自己rollbackに依存していない設計であることも傍証)

### ③「idempotency_key未使用時の早期return経路」→ ★㈠在る★

根拠 (復元後の `booking_service.py` 実ファイル行番号、hunk `@@ -192,55 +202,140 @@` 起点で写像):
- 249行目 `if root_enabled and idempotency_key:` — idempotency_key未使用(None/空文字)時はFalseで素通り。
- 260-269行目 `existing = conn.execute(SELECT ... WHERE clinic_id=? AND patient_id=? AND unit_id=1 AND source='web' AND status NOT IN(...) AND start=?/end=?/content=? ORDER BY appointment_id DESC LIMIT 1)`
  — idempotency_key抜きでも「同一患者・同時刻・同内容」ヒューリスティックで既存active予約を検索。
- 270行目 `if existing and not (root_enabled and idempotency_key):` — idempotency_key未使用(falsy)なら
  `not (... and idempotency_key)` は常にTrueとなるため、existing真値のみで条件成立。
- 271-278行目 `conn.commit(); return {...}` — この時点で早期return。
- 280行目 `_check_conflict(conn, clinic_id, start_dt, end_dt)` — 早期return経路はこの競合検証・
  282行目以降のINSERT・claim_appointment_slots呼出のいずれも通らない。
- ∴ idempotency_key未使用時、`existing`ヒューリスティック一致のみでconflict検証を経ずに早期returnする経路が実在する。実測で再現。

## 三値まとめ

| # | 主張 | 判定 | 根拠file:line |
|---|---|---|---|
| ① | staff経路にidempotency機構が未配線(slot claimsのみ) | ㈠在る | appointment_service.py(patch内, 元行218〜/新規21,39-56)・api/appointments.py全190行grep hit=0 |
| ② | apply_booking_concurrency_rootはFK check失敗時に已にcommit済・自己rollback無し | ㈠在る | booking_concurrency_root.py:284(commit)/285-291(try/except/finally境界)/293-295(commit後のFK check・rollback経路無し) |
| ③ | idempotency_key未使用時の早期return経路 | ㈠在る | booking_service.py:249,260-269,270-278(早期return)/280(_check_conflict未通過) |

★㈢未測は0件★ — 全三件とも静的読解(patch本文+base比較)のみで再現可能、DB稼働・走行を要さず実測完了。
★㈡(無い/誤り)も0件★ — 仮説に合わせて探した結果ではなく、静的コード読解の直接帰結として三件とも実在を確認。

## 境界・自己申告

- appointments.py は目視40行に留まる (grep全数は実施済のため①判定への影響なし、念のため明記)。
- 本報告は read-only 独立監査であり、危うさの重大度・修正要否の裁定は行っていない (下命通り inventory徹底、裁定は権限外)。
- 本工区が新たに開ける穴: なし (書込み・apply・commit 一切未実施、既存記録の追加のみ)。
