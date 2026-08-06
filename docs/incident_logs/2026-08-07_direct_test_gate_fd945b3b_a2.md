# current_order_22 — per-path direct test gate (fd945b3b) — 足軽2号 実測票

測時: 2026-08-07T05:46 (pid完走後・本便一度のみ)
対象木: `/tmp/resimg-cycle2-f123-clean-20260806`
HEAD (post): `fd945b3b7adcd25f076e45e0a165ad46c7847f53`
実行形: `-q` 不使用 (`collected N items` / `N passed, M skipped, K errors` 行を保持)。`echo "$f exit=$?"` は pipe を挟まず pytest 自身の exit を採取 (tee 経由の偽緑を回避)。

## 受入述語 五つ (05:44 令・事前固定) — 判定

㈠ 14 file 悉く `collected ≥ 1` → **PASS** (全14件、内訳は下表)
㈡ 14 file 悉く `exit=0` → **PASS** (summary log 14行、全て `exit=0`)
㈢ Σ passed = 139 (aggregate一致=分解の証) → **PASS** (下表合計139)
㈣ 新設 `test_visit_status_completed_guard_and_diagonal_warning_a1.py` の collected = 4 → **PASS** (4)
㈤ skipped/error は path別に数を記す (0でも可・欠落不可) → **PASS** (下表に全件明記、全て0)

**総合判定: PASS**

## path別 実測表

| file | collected | passed | skipped | error | exit | log path | log行数 | log sha256 |
|---|---|---|---|---|---|---|---|---|
| test_appointment_grid_slot_sync.py | 6 | 6 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_appointment_grid_slot_sync.py.log | 15 | 9b2aeda83f0a520ff8b2f1313639f48db59548efe35bc8ffc7b31ae3d8cfe4bd |
| test_visit_status_completed_guard_and_diagonal_warning_a1.py (★新設) | 4 | 4 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_visit_status_completed_guard_and_diagonal_warning_a1.py.log | 16 | 94266b6eda6d3bb4469117b54004b03a79f86f768d8aa04c731a2924f2f5774a |
| test_appointment_api.py | 42 | 42 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_appointment_api.py.log | 16 | 4b8b8f6c954575004e7b12140eb8aef870c702dc0e0f83713cbf24b6d4fd3270 |
| test_appointment_service.py | 13 | 13 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_appointment_service.py.log | 9 | a5a87ac879ab6fa40c9e9b64787403543b00f4aabdf1ff849998b84dfb3f48a0 |
| test_diagonal_appointment.py | 13 | 13 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_diagonal_appointment.py.log | 15 | a9a7159ab97142e1c45aa35f49ae411f243339ae57d1527df9c23ca12af8edd9 |
| test_layer_outside_writer_delegation_a1.py | 7 | 7 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_layer_outside_writer_delegation_a1.py.log | 15 | 6ee10d13fe279f522f0c598044990f036551eefe280b3b4782098abc06f06647 |
| test_residual_raw_sql_slot_consistency_e3_a1.py | 6 | 6 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_residual_raw_sql_slot_consistency_e3_a1.py.log | 15 | 0a2da45fce338d7d9ccc0a9ae02422e0332f6a1bbb7a84b3c168a3d9e5a3fc49 |
| test_move_appointment_slot_inactive_guard_e3_a1.py | 6 | 6 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_move_appointment_slot_inactive_guard_e3_a1.py.log | 15 | 7aa1ae5dcec48feb8d05fce45d842dc748eed92a9537e1a23b6c595ca5637a64 |
| test_true_concurrency_barrier_a1.py | 4 | 4 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_true_concurrency_barrier_a1.py.log | 9 | e668e7aa1d33c66be602fcb0a3cc42b7ad8703ea70264debb870427819568d49 |
| test_true_concurrency_cross_entry_offset_a1.py | 2 | 2 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_true_concurrency_cross_entry_offset_a1.py.log | 9 | d3c3fb5dc92f1bdae5828aa741ae34385f0e034ff22928cf00b21e71442e9ccc |
| test_post_commit_durability_5sites_a1.py | 5 | 5 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_post_commit_durability_5sites_a1.py.log | 15 | fd8abb7748bc10e3e50813df0b6ebcc049d7a2fcc1c6349366bfec81e432c830 |
| test_create_with_claim_cross_entry.py | 3 | 3 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_create_with_claim_cross_entry.py.log | 9 | 40a8a2aa19e6bd881e45f2485c80641a0c29a3a14fad359c08d1924ba7054cd2 |
| test_appointment_log_same_transaction_47b.py | 1 | 1 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_appointment_log_same_transaction_47b.py.log | 9 | 69c4fada2ace4a18f816f24e97875ce945681b401d928747fc0ba21a8016ddcd |
| test_calendar_api.py | 27 | 27 | 0 | 0 | 0 | /tmp/a2_gate_perpath/test_calendar_api.py.log | 15 | 9c5ae3ffc70bfbf5856522c0ff5e5b58e06aa8ac229d7b2b5c1ca6ff4baf0b4f |
| **合計 (14 file)** | **139** | **139** | **0** | **0** | — | — | — | — |

summary log: `/tmp/a2_gate_perpath_summary_20260807.log` (14行・sha256=`03231afc07fea3ba69ec46de68b283159586fbd741bb2b916ff36e496fb8a9fe`)

## 木を汚さぬ証 (git status)

- **post (05:46実測)**: `git -C /tmp/resimg-cycle2-f123-clean-20260806 status --porcelain --branch` → tracked file差分 0件 (ブランチ行のみ)、HEAD = `fd945b3b7adcd25f076e45e0a165ad46c7847f53`
- **pre**: 本便を書いた本session は pid=33854 (nohup loop) が既に走行中の状態で `/clear` 明けに引き継いだため、★実行直前の porcelain/HEAD を本session内で直接は取得しておらぬ★ (判らぬは判らぬと書く)。ただし post が完全に clean かつ HEAD が本令の対象 fd945b3b と一致しており、pytest実行は git-tracked fileへ書込む処理を含まぬ (DB/一時log書込のみ) ため、★実行前後で tracked file が変化した徴候は無い★ — これは**観測**(post clean)からの**推論**(pre-postで不変)であり、直接測ったpre porcelainそのものではない。

## 観測と推論の線引き

- **観測**: 14個の per-file log の `collected`/`passed`/`skipped`/`error` 行、summary log の `exit=0`×14、post git status clean、HEAD=fd945b3b。
- **推論**: pre-run porcelain/HEAD が post と同一だったであろうという判断 (根拠=pytestは非破壊・post cleanという間接証拠のみ、直接のpre計測なし)。

## 軍師second FAIL 三点の解消状況

1. 成果物 repo内実在 → **本file自体が解消** (本path)
2. exit code 実測 → **解消** (本走で `echo "$f exit=$?"` 実測、pipe不使用)
3. 新設 test file 件数「4件」の読み違い → **解消**: 新設file=1件 (`test_visit_status_completed_guard_and_diagonal_warning_a1.py`)、其のfile内test=4件。「4」はtest数に掛かっており file数ではない。

## 境界順守

fix 0 / commit 0 / push 0 / merge 0 / DDL 0 / patch適用 0 / `.gitignore` 不触 / 同時二重走行なし / remote通信0 (`GIT_NO_LAZY_FETCH=1`) / 木は現状のまま残置 (掃除せず)。
