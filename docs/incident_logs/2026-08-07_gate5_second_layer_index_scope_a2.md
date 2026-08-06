# Gate5 second-layer (DB index) scope census — ashigaru2 (a2)

- 測時: 2026-08-07T00:17:29+09:00 (date -Iseconds 実値)
- 令: current_order_13_20260807_001200_GATE5_SECOND_LAYER_SCOPE (queue/inbox/ashigaru2.yaml msg_20260807_001301_69a6ca97・家老second発)
- mode: read-only (実装fix 0 / 新test 0 / commit 0 / push 0 / merge 0 / DDL 0)
- 器: worktree = /tmp/resimg-verify2-cycle2-barrier-20260806 (branch=ashigaru2-verify-cycle2-barrier-20260806, base=e88e7582fa2c8d83e4617cec962a5724df8ad695・前工区 current_order_12 から不変・本工区で新規 commit 0 件・HEAD=e88e758のまま)
- 範囲: backend/db/migrations/booking_concurrency_root.py（第二層index定義）+ backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py（RED test 3種の実ソース）

## ㈠ 実 index 定義（逐語・backend/db/migrations/booking_concurrency_root.py:253-255）

```
CREATE UNIQUE INDEX uq_appointments_active_exact_start
ON appointments(clinic_id,unit_id,start_time)
WHERE status NOT IN ('cancelled','no_show')
```

- 列: `clinic_id, unit_id, start_time`（複合3列）
- WHERE句（partial条件）: `status NOT IN ('cancelled','no_show')` = active行（cancelled/no_show以外）のみに適用

## ㈡ 射程（述語・定義文からのみ、推さず）

UNIQUE indexは複合key `(clinic_id,unit_id,start_time)` の **完全一致（exact tuple equality）** のみを禁ずる機構である。SQLiteのUNIQUE制約は range/interval 比較を持たず、`start_time` の値そのものの等号判定のみを行う。

∴ 射程 = **exact start_time 一致のみ**。

区間重複（offset overlap = start_timeが異なる二つの予約がdurationで重なる場合）は、二行のindex key中 `start_time` が異なる限り、この索引には一切掛からない。定義文中に区間/duration/rangeを扱う語彙（BETWEEN・OVERLAPS等）は存在しない — 定義文そのものから断定できる（推測ではない）。

## ㈢ 三つの扉、各々「二層目を通した後になお通る場合」（述語）

前提: 三つの扉 = ⒜Web-vs-Web（同一start_time）／⒝Web-vs-Staff（同一start_time・cross-entry）／⒞offset overlap（start_timeが15分ずれた部分重複）— いずれも `backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py` の3 test群 (`test_web_vs_web_barrier_*` L162, `test_web_vs_staff_barrier_*` L350, `test_offset_overlap_barrier_*` L311/400) の実装から確認（読取のみ）。

- ⒜ **Web-vs-Web（同一start_time）**: 二層目のindex keyが両者で完全一致するため、二層目自身が（app層のclaim呼出とは独立に）appointments INSERT時にUNIQUE違反で拒む。∴ **なお通る場合 = 0**（二層目単独で閉じる。claim機構の呼出有無に関わらず）。
- ⒝ **Web-vs-Staff（同一start_time・cross-entry）**: 同様に、appointments tableへのINSERTである限りentry（Web/Staff）を問わずindex keyが一致すれば二層目が拒む。∴ **なお通る場合 = 0**。
- ⒞ **offset overlap（start_timeが異なる部分重複）**: 二行のindex key中 `start_time` が異なるため、二層目のUNIQUE制約は不成立（発火せず）。二層目はこの場合に関し構造上無力（㈡の帰結そのもの）。∴ 二層目通過後になお通るか否かは **一層目（claim機構＝appointment_slot_claims UNIQUE INSERT）の射程のみに懸かる**。一層目のapp層呼出=0（Gate5 barrier task・current_order_12 karo_second_verify実測で既測・本工区では再測せず引用のみ）。∴ **なお通る場合 = 非0（丸裸）**。

## ㈣ RED test（offset overlap）が正しく「裸の場合」に当たるかの検め

`backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py`:
- `test_offset_overlap_barrier_RED_on_pre_root_schema` (L311) と `test_offset_overlap_barrier_true_concurrent_partial_conflict` (L400) は、いずれも `_run_offset_overlap_barrier` (L277) を共用し、start_timeを15分ずらした二予約をthreading.Barrierで真並行同期する設計。pre-root schema（二層目index未適用の断面）でRED（success=2・両者成功）を示す。
- 当該fileのdocstring（L406-407）に「`uq_appointments_active_exact_start`はoffset overlapに構造上無力（定義から・test不要）」と明記されており、本票㈡の定義文解析と**独立に一致**（写さず自ら定義文から導出した後に確認）。

∴ 貴殿（当職＝ashigaru2の前工区current_order_12）のRED testは **正しく「二層目が構造上及ばぬ裸の場合」に当たっている** — 一致。

## ㈤ 結論（述語で・数でなく）

> **二層通過後の reachable case = 0 ではない。**

述語で書けば:
「⒜⒝（exact-time扉）は二層目が独立に閉じるため reachable = 0。⒞（offset overlap扉）は二層目の射程外（定義上）かつ一層目（claim機構）の呼出=0（既測）であるため、二層通過後も reachable = 非0」。

∴ 全体としての述語「未委譲 reachable case = 0」は **不成立** — 不成立の所在は **⒞offset overlap扉に限定される**（⒜⒝は二層目のみで既に閉じておりcase=0）。

これは家老second便（msg_20260807_001301_69a6ca97）の記載と一致する。本票は当該記載を**写さず**、定義文（㈠㈡）とtestソース（㈢㈣）から独立に導出した。

## 第四値（判らぬ）

無し。全項、定義文（backend/db/migrations/booking_concurrency_root.py:253-255）およびtestソース（backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py）から直接確認済み。

## 禁の遵守

実装fix 0 / 新test 0 / commit 0 / push 0 / merge 0 / DDL 0 — 本工区中、worktree HEADは base (e88e758) のまま不変（`git log --oneline -1` 実測で確認）。既存fileの読取のみ。
