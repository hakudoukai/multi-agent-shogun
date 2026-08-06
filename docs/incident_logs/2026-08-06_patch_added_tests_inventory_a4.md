# 足軽4号 → 家老second: Cycle2 patch が触れた test の悉く（base在り／patch追加／判じ得ぬ）

断面: 2026-08-06T12:27:09+09:00 JST（当職 実測。以下は悉く己で打ち直した値、記憶に依らず）
本便は read-only。hakudokai-dev・/tmp/resimg-cycle2-impl-20260806 へ一字も書いておらぬ。test は一切実走しておらぬ（下命の禁に従う）。

## 前提（冒頭・同じ行）

★本列挙が覆うは Cycle2 patch の差分のみ。base 側の既存 test の質は問わず★。
対象 repo = hakudokai-dev（読取のみ）。作業 worktree = `/tmp/resimg-cycle2-impl-20260806`（HEAD=base、dirty=patch そのもの——W203 系 a4 先行監査 `docs/incident_logs/2026-08-06_reserveimage_cycle2_patch_readonly_audit_a4.md` §1 の base HEAD 実測値と一致）。
base commit = `7d463edae84c704edabbd9da5465078dc62e55b1`（本便冒頭で `git -C /tmp/resimg-cycle2-impl-20260806 rev-parse --verify` にて改めて実測・一致）。

## §0 未測・零件の申告

- 「判じ得ぬ」＝**0件**。零の根拠＝下記34 test 悉くが「base file に同名 def が在るか（`git show <base>:<path> | grep -n '^def test_'`）」または「file 自体が base に存在せぬか（`git show <base>:<path>` が rc=128 で fatal）」のいずれかで機械的に判じ切れた。曖昧に倒れた例は無い。
- 本便は「Cycle2 patch が diff で触れた2 test file（`test_phase2_2_booking.py` 改・`test_booking_concurrency_root_migration.py` 新）内の test 関数」を母集団とする。patch が触れなんだ他 test file（例: `test_web_reservation` 配下の他 file）は母集団外＝**未読**。
- `test_phase2_2_booking.py` 内の既存25 test は diff 上 **削除0行**（`git diff --stat` = 121 insertions のみ）ゆえ、本文は base と字面一致するはずだが、当職は diff の unified context 外（変更行から離れた箇所）までは逐一 byte 比較しておらぬ＝「base に在り」は**関数定義行の存在一致**までの実測であり、関数本体の一字一句一致は本便の測定範囲外（未測）。

## §1 用いた命令（逐語）

```
git -C /tmp/resimg-cycle2-impl-20260806 rev-parse --verify 7d463edae84c704edabbd9da5465078dc62e55b1
git -C /tmp/resimg-cycle2-impl-20260806 log -1 --format='%H %s %ci' HEAD
git -C /tmp/resimg-cycle2-impl-20260806 status --porcelain
git -C /tmp/resimg-cycle2-impl-20260806 diff --stat
git -C /tmp/resimg-cycle2-impl-20260806 diff -- backend/tests/web_reservation/test_phase2_2_booking.py
git -C /tmp/resimg-cycle2-impl-20260806 show 7d463edae84c704edabbd9da5465078dc62e55b1:backend/tests/web_reservation/test_phase2_2_booking.py | grep -n "^def test_"
grep -n "^def test_" /tmp/resimg-cycle2-impl-20260806/backend/tests/web_reservation/test_phase2_2_booking.py
git -C /tmp/resimg-cycle2-impl-20260806 show 7d463edae84c704edabbd9da5465078dc62e55b1:backend/tests/test_booking_concurrency_root_migration.py
grep -n "^def test_" /tmp/resimg-cycle2-impl-20260806/backend/tests/test_booking_concurrency_root_migration.py
wc -l /tmp/resimg-cycle2-impl-20260806/backend/tests/test_booking_concurrency_root_migration.py
```

## §2 実測結果

### 2-1 `backend/tests/web_reservation/test_phase2_2_booking.py`（既存file・改）

`git diff --stat` = `121 insertions(+), 0 deletions(-)`（この1fileのみ抽出時）。削除0ゆえ既存25 test は字面上そのまま残置、3 test が新規挿入（330行目と333行目の間）。

| ㈠ test 名 | ㈡ file:line（patch後・working tree） | ㈢ 三値 |
|---|---|---|
| test_get_web_bookable_menus | test_phase2_2_booking.py:150 | base に在り |
| test_available_slots_empty_day | test_phase2_2_booking.py:161 | base に在り |
| test_available_slots_with_existing | test_phase2_2_booking.py:167 | base に在り |
| test_available_slots_cancelled_not_block | test_phase2_2_booking.py:178 | base に在り |
| test_available_slots_with_menu_duration | test_phase2_2_booking.py:189 | base に在り |
| test_create_booking_auto_mode | test_phase2_2_booking.py:196 | base に在り |
| test_create_booking_manual_mode | test_phase2_2_booking.py:205 | base に在り |
| test_booking_source_is_web | test_phase2_2_booking.py:216 | base に在り |
| test_my_appointments | test_phase2_2_booking.py:227 | base に在り |
| test_update_booking_time | test_phase2_2_booking.py:241 | base に在り |
| test_update_booking_other_patient_fails | test_phase2_2_booking.py:250 | base に在り |
| test_update_cancelled_booking_fails | test_phase2_2_booking.py:258 | base に在り |
| test_cancel_booking | test_phase2_2_booking.py:269 | base に在り |
| test_cancel_other_patient_fails | test_phase2_2_booking.py:280 | base に在り |
| test_cancel_already_cancelled | test_phase2_2_booking.py:286 | base に在り |
| test_cancelled_not_in_my_appointments | test_phase2_2_booking.py:293 | base に在り |
| test_create_booking_past_date_rejected | test_phase2_2_booking.py:302 | base に在り |
| test_create_booking_outside_business_hours | test_phase2_2_booking.py:307 | base に在り |
| test_create_booking_conflict_detected | test_phase2_2_booking.py:312 | base に在り |
| test_create_booking_invalid_datetime_format | test_phase2_2_booking.py:318 | base に在り |
| test_update_booking_conflict_detected | test_phase2_2_booking.py:323 | base に在り |
| test_update_booking_past_date_rejected | test_phase2_2_booking.py:330 | base に在り |
| **test_true_two_connection_same_slot_only_one_active_row** | test_phase2_2_booking.py:355 | **patch で追加** |
| **test_exact_request_replay_returns_same_appointment_id** | test_phase2_2_booking.py:408 | **patch で追加**（★ashigaru1 が既に指摘した本命★） |
| **test_durable_idempotency_key_and_slot_claims_after_migration** | test_phase2_2_booking.py:432 | **patch で追加** |
| test_available_slots_invalid_date | test_phase2_2_booking.py:454 | base に在り |
| test_available_slots_hidden_when_all_web_staff_off | test_phase2_2_booking.py:503 | base に在り |
| test_create_booking_rejects_when_all_web_staff_off | test_phase2_2_booking.py:515 | base に在り |

base 側の同名関数定義行番号（参考・行番号は insert 分shiftで異なる。名前は悉く working tree 側と一致・実測済）: 147/158/164/175/186/193/202/213/224/238/247/255/266/277/283/290/299/304/309/315/320/327/333/382/394（25件、新規3件を挟まぬ base file 上の連番）。

### 2-2 `backend/tests/test_booking_concurrency_root_migration.py`（新規file・全体）

`git show 7d463edae84c704edabbd9da5465078dc62e55b1:backend/tests/test_booking_concurrency_root_migration.py` → **rc=128・`fatal: path ... exists on disk, but not in '7d463eda...'`**＝base に file 自体が不在。∴ file 内の test 悉くが patch 追加（file 単位の新規ゆえ判定は一意・「判じ得ぬ」に該当せず）。

| ㈠ test 名 | ㈡ file:line（working tree・全164行） | ㈢ 三値 |
|---|---|---|
| test_gate2_baseline_scan_zero_and_15_minute_grid | test_booking_concurrency_root_migration.py:58 | patch で追加 |
| test_gate2_duplicate_stops_before_any_schema_mutation | test_booking_concurrency_root_migration.py:68 | patch で追加 |
| test_gate3_rehearsal_schema_backfill_and_exact_rollback | test_booking_concurrency_root_migration.py:82 | patch で追加 |
| test_slot_claims_block_offset_overlap_and_partial_index_blocks_status_bypass | test_booking_concurrency_root_migration.py:110 | patch で追加 |
| test_cancel_release_allows_slot_reuse | test_booking_concurrency_root_migration.py:124 | patch で追加 |
| test_idempotency_reconnect_mismatch_and_stale_pending_does_not_block_slot | test_booking_concurrency_root_migration.py:137 | patch で追加 |

## §3 総括（列挙のみ・裁定は書かず）

- 母集団＝34 test（2-1: 28 + 2-2: 6）。
- base に在り＝25件。patch で追加＝9件（2-1の3件 + 2-2の6件）。判じ得ぬ＝0件。
- ★眼目（同じ穴が他にも在るか）への回答★＝★在り申す★。ashigaru1 が指摘したのは `test_exact_request_replay_returns_same_appointment_id` の1件のみだが、**同一 patch 内に更に8件**（同file内2件＋新規file6件）が実装と同時に追加されている。将軍second の条（12:18）「同一 patch で実装と test を同時に追加すれば、その test は実装の振舞いの固定であり独立の証拠にならぬ」に照らせば、**この9件全てが同じ性質を負う候補**である——★但しどれが実際に「独立の証拠として扱われて良いか」の裁定は当職の権限外ゆえ書かぬ★。

## §4 各主張の検め直し方（一行ずつ）

- 「base に在り25件」→ `git -C /tmp/resimg-cycle2-impl-20260806 show 7d463edae84c704edabbd9da5465078dc62e55b1:backend/tests/web_reservation/test_phase2_2_booking.py | grep -n "^def test_"` を再実行し件数・名前を突合せよ。
- 「patch で追加9件」→ 2-1は `git -C /tmp/resimg-cycle2-impl-20260806 diff -- backend/tests/web_reservation/test_phase2_2_booking.py` の `+def test_` 行を数えよ（3件）。2-2は当該file が base に無いこと（rc=128）を再実行して確かめよ。
- 「削除0行」→ `git -C /tmp/resimg-cycle2-impl-20260806 diff --stat -- backend/tests/web_reservation/test_phase2_2_booking.py` の `deletions` 欄を見よ。

## §5 本便が新たに開ける穴

- 「base に在り」は関数定義行の存在一致までの実測であり、**関数本体の一字一句が base と同一である事までは検めておらぬ**（§0 既述）。もし patch が既存 test の**本体**を書き換えつつ diff 上は別の理由で相殺されていた場合（本件では削除0行ゆえ理論上起き得ぬはずだが）、本便はそれを見落とす形になっている。
- 母集団を「patch が diff で触れた2 test file」に限定したため、patch が**間接に**影響する他 test file（例: `booking_service` を import する他所の test）は母集団外＝完全に未読。

## §6 己が本工区で直した誤り

無し（read-onlyゆえ直す手を持たぬ）。

---
生成: ashigaru4 / 2026-08-06T12:27:09+09:00 JST / read-only監査。hakudokai-dev・/tmp/resimg-cycle2-impl-20260806・repo内他fileは一切未変更。
