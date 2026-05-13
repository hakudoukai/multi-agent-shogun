# unmatched_verified_targets 8→0 transition — 2026-05-14 機械証拠 trace

## 概要

`compute_shogun_reflection_stats` が報告する `unmatched_verified_targets_count` に関し、
2026-05-12 snapshot (`queue/reports/unverified_inventory_20260512.yaml` helper_evidence) は
`8` を記録、信長殿 direct dispatch (msg_20260513_sc_direct_dispatch_6b77a957) は
`11 件 dashboard mapping 改修` を表記、2026-05-14 SC truth-gate 機械測定は `0` を測定。
本書は 3 値の出典 + transition の機械証拠 chain + 現実態 SoT 化 (= dashboard mutation 禁、
regression invariant 装着 path) を記録する。

- 対象 task: `subtask_cmd020_unmatched_verified_targets_dashboard_mapping` revision 2
- 担当: ashigaru4 (大久保彦左衛門) on SC
- 機械測定 git HEAD: `9ebb3e2`
- 関連 helper: `scripts/regenerate_dashboard.py` L1009-L1071 (`UNMATCHED_VERIFY_RETAIN_REGISTRY` +
  `annotate_unmatched_with_retain`)、L1437-L1586 (`compute_shogun_reflection_stats`)

## 1. 三値の出典

| 値 | 出典 | 生成時刻 | helper |
|----|------|----------|--------|
| 8 件 (snapshot) | `queue/reports/unverified_inventory_20260512.yaml` `helper_evidence.unmatched_verified_targets_count` | 2026-05-12T20:28:12+09:00 | `scripts/extract_unverified_inventory.py` 経由 `compute_shogun_reflection_stats` |
| 11 件 (directive) | `msg_20260513_sc_direct_dispatch_6b77a957` 信長殿 → ashigaru4 | 2026-05-13T15:25:13+09:00 | 別 channel (= karo task assignment 経由) |
| 0 件 (current) | SC 機械測定 (= 本 task AC0 truth gate) | 2026-05-14T00:21:00+09:00 | `compute_shogun_reflection_stats` 直接呼出 + `python3 scripts/regenerate_dashboard.py --dry-run` |

snapshot `8` と directive `11` の 3 件差分は本 task scope では archival 整合性事項として retain (= 信長殿 directive の表記は別 channel、scope 内追跡不要)。

## 2. 関連 commit chain (snapshot → current)

snapshot 生成時点 (= commit `41c659b`) と現在 (= commit `9ebb3e2`) の間に着地した
helper / 関連 file の改修 commit:

| commit | 時刻 | 著者 | 主旨 |
|--------|------|------|------|
| `41c659b` | 2026-05-12T20:30:20+09:00 | ashigaru1 | `feat(cmd_004/cycle12)` 信長殿 20:18 audit pipeline 復活 + `scripts/extract_unverified_inventory.py` 装着 + snapshot 起案 (= helper_evidence.active_entries_total=41 / unmatched=8 / matched=17) |
| `c63e94f` | 2026-05-12T21:09:30+09:00 | ashigaru1 | `feat(cmd_020/cycle13)` W9 spider_thread mapping normalization |
| `0825bdc` | 2026-05-12T22:06:36+09:00 | ashigaru1 | `feat(cmd_020/cycle14)` **generator context SoT 化 + UNMATCHED_VERIFY_RETAIN_REGISTRY 4 entry 装着** + `annotate_unmatched_with_retain` 新規 + `compute_shogun_reflection_stats(precomputed_states=, retain_registry=)` 拡張 |
| `79f96e7` | 2026-05-12T23:51:56+09:00 | ashigaru4 | `feat(cmd_020/cycle15)` dashboard alert section に shogun_verified=true 昇格 tier 装着 |
| `e2189be` | 2026-05-13T14:13:45+09:00 | SC karo (本多忠勝) | `feat(cmd_020 w9_shogun_verification_log_pytest_fix)` w9_batch/w9_stage blocked field |
| `a08cf37` | 2026-05-13T16:14:14+09:00 | ashigaru1 | `merge SC audit chain into MC chain` (信長殿 (A) pattern GO) |

`queue/reports/shogun_verification_mainpc_log.yaml` 自体は 2026-05-11T14:08:36 (= commit `80cc68e`
`auto(main_pc): 6files`) を最後に touch なし。snapshot 直前 (= `41c659b`) と現在 (= `9ebb3e2`)
の double-check 結果、当 file content 完全同一 (= verifications 105 件 / `shogun_verified=True`
12 件 / `migration_note != legacy_migrated` 条件下 active 0 件)。

## 3. UNMATCHED_VERIFY_RETAIN_REGISTRY (cycle14 装着 4 entry)

| candidate_id | match_substring | reason | source_log |
|---|---|---|---|
| retain_phase_1_6_rollback_kuroda_meta_audit | kuroda_audit_cmd004_phase_1_6_rollback | kuroda audit chain 個別 formal audit (= cmd_004 phase 1-6 rollback)、children に phase rollback 用 placeholder 不在ゆえ正当 retain | queue/reports/kuroda_mainpc_report.yaml#kuroda_cmd004_phase_1_6_rollback_individual_formal_audit_20260512 |
| retain_cmd012_preflight_verify | cmd012_p02_preflight_verify | cmd_012 phase02 preflight verify (= 別 chain、cmd_020 dashboard 6 Layer 外)、Layer C-12/13 系は cmd_012 implementation を carry するが preflight verify entry 自体は構造 children 未紐付 | queue/reports/shogun_verification_mainpc_log.yaml#target=cmd012_p02_preflight_verify |
| retain_w9_supabase_completed_evidence_71 | subtask_cmd004_w9_supabase_completed_evidence_audit_71 | W9 Supabase completed evidence audit (= 71 件外部証跡 audit)、Stage B batch1-6 (C-15-B1-B6) とは別 chain の supabase metadata audit ゆえ children mapping 対象外 | queue/reports/shogun_verification_mainpc_log.yaml#target=subtask_cmd004_w9_supabase_completed_evidence_audit_71 |
| retain_delta_ashigaru2_ceremony_trigger_cycle2 | subtask_delta_ashigaru2_ceremony_trigger_cycle2_001 | delta ashigaru2 ceremony_trigger cycle2 (= 別 delta chain、cycle 13 後追加された verify entry)、dashboard 6 Layer 構造に delta ceremony chain 用 placeholder 不在 (= 後続 cycle で Layer E 候補) | queue/reports/shogun_verification_mainpc_log.yaml#target=subtask_delta_ashigaru2_ceremony_trigger_cycle2_001 |

registry 装着 commit: `0825bdc` (= cycle14)

## 4. 真因究明 — 8→0 はなぜ起きたか

### 4.1 task yaml 仮説 (= 「retain_registry 吸収」) と機械測定の乖離

task yaml `description.背景` 節:
> 既装着 helper: UNMATCHED_VERIFY_RETAIN_REGISTRY (= scripts/regenerate_dashboard.py L1037
> annotate_unmatched_with_retain + L1437 compute_shogun_reflection_stats)
> ...
> retain_registry に追加された entry list (= 8→0 を吸収した実 entries)

しかし `annotate_unmatched_with_retain` は **母集団そのものを 0 化する logic ではなく**、
unmatched 各 entry に `retain_status=registered/unregistered` + `candidate_id` + `reason` +
`source_log` を annotate するだけの helper である (= `scripts/regenerate_dashboard.py`
L1037-L1071)。stats dict の最終 `unmatched_verified_targets` リスト長は annotate
前の `unmatched_raw` リスト長と等しい (= `out.append(annotated)` で 1:1 map)。

したがって「registry の 4 entry が 8→0 transition を吸収」は機械的にあり得ない。

### 4.2 機械測定上の真因

`compute_shogun_reflection_stats` (L1484):

```python
active_entries = [v for v in shogun_entries if _is_active_shogun_entry(v)]
```

unmatched 母集団は `active_entries` のうち child pattern に match しなかった entry。
よって `unmatched_count = 0` の必要条件は **`active_entries == 0` または全 active が
mapped child の pattern に match**。

機械測定 (= AC0 (b) stats_dict.json):
- `active_entries_total: 0`
- `matched_count: 0` (= 0 active のうち 0 が pattern match、trivially zero)
- `unmatched_verified_targets_count: 0` (= 0 active のうち 0 が unmatched、trivially zero)

`shogun_verification_mainpc_log.yaml` の `_is_active_shogun_entry` filter 通過数 = 0
(= verifications 105 件のうち `shogun_verified=True` は 12 件、全件 `migration_note=
legacy_migrated` 付き ゆえ active 判定で除外)。

snapshot 時点の `active_entries_total=41` と現在の `active_entries_total=0` の乖離は、
**snapshot 生成時の MC 側 mainpc_log と git に commit されている mainpc_log の間に
未追跡変更 (= uncommitted entries) があった可能性が高い** (= snapshot helper_evidence と
git 履歴の二重整合性を取った double-check 結果、commit `41c659b` 時点の git tracked
mainpc_log には active=0)。

### 4.3 結論 — 「8→0」は表面、本質は「active=41→0」(= cross-PC 履歴整合性事項)

本 task scope では **現実態 (= active=0 / unmatched=0) を SoT** とし、cross-PC
履歴整合性の遡及調査は別 cycle (= karo 経由提起候補) に委ねる。retain_registry 4 entry
は metadata annotation 用 装着 として retain (= 当該 4 entry が将来 active 復帰した際の
正当 retain reason 機械証跡 source)、dashboard.md mutation 禁、regression invariant 装着
で固定化する。

## 5. dashboard.md mutation 禁の根拠

現実態 (= current unmatched=0) では:
- `compute_shogun_reflection_stats` の `unmatched_verified_targets` field は空 list、
  template の `{% if shogun_reflection_stats.unmatched_verified_targets %}` 節は描画されない
- registry annotation table も table body 空となる
- 結果として dashboard.md にも対応 section は不在 (= 現状 markdown と diff null)

よって AC3 の dashboard.md 不変 verify (= regenerate 出力 = 既存 dashboard equivalent)
は機械的に成立する。

## 6. regression invariant の意義 (= AC2 装着内容)

将来発生し得る regression risk:
1. `shogun_verification_mainpc_log.yaml` への active entry 追加で `_is_active_shogun_entry`
   通過 entry が復帰 (= unmatched 母集団復活)
2. retain_registry 4 entry が誤って削除 (= registered count 喪失)
3. `compute_shogun_reflection_stats` の SoT path 改修で count 値が integer / list 不整合化
4. dashboard render path で stats dict の値が render 後に差分発生 (= 直政 cycle2
   `dashboard_regression_assertion_underspecified` finding 整合)
5. transition documentation file (= 本書) が削除 / リネーム (= audit trail 喪失)

`scripts/test/test_unmatched_verified_targets_regression.py` に 5 件 pytest 装着:

1. `test_unmatched_verified_targets_count_zero_invariant`
   — `len(stats["unmatched_verified_targets"]) == 0` 固定化
2. `test_retain_registry_full_completeness`
   — registry 4 entry 全件の `candidate_id` + `reason` + `source_log` 非空 verify
3. `test_dashboard_render_metric_invariance_after_stats`
   — render 前後で `matched_count` + `green_count` 等 5 stat 不変 verify
4. `test_baseline_metric_snapshot`
   — `children_total` + `eligible_count` + `mapped_count` + `matched_count` +
     `green_count` + `unmatched_unregistered_count` 機械測定 baseline 固定化
5. `test_transition_documentation_file_exists`
   — 本書 (`docs/unmatched_verified_targets_8_to_0_transition_20260514.md`) の存在 verify
     + 本 task `audit_id` ref 整合

## 7. retain_registry 拡張 / 縮約の運用規範

新規 unmatched active entry が将来発生した場合の SoP:
1. retain reason が機械証跡で証明可能 → registry に 1 entry 追加 (= candidate_id / reason
   / source_log 3 field 必須、根拠 yaml への file#anchor URI で source_log)
2. retain reason が未確立 → unregistered のまま放置せず、別 layer の child placeholder
   起案 or 個別 audit chain で吸収
3. registry entry の縮約は別 cycle (= 信長殿 御差配下、karo 提起) でのみ可

本書は registry 4 entry 装着当時の `0825bdc` 起案責務 retain (= cycle14 著者 ashigaru1) を
継承 trace、本 task では新規 entry 追加 / 縮約は行わない (= 既装着 helper 不変、
constraint `existing_helper_reuse` 整合)。

## 8. audit_id

`audit_id`: `transition_doc_unmatched_verified_targets_8_to_0_20260514_ashigaru4`

本書は AC1 evidence_required の `docs/unmatched_verified_targets_8_to_0_transition_20260514.md`
として retain、AC2 pytest `test_transition_documentation_file_exists` が本 audit_id を含む
ref を機械 verify する。

## 9. 関連 evidence

- inventory yaml: `queue/reports/ashigaru4_subtask_cmd020_unmatched_verified_targets_dashboard_mapping_inventory.yaml`
- pytest log: `queue/reports/ashigaru4_subtask_cmd020_unmatched_verified_targets_dashboard_mapping_pytest.log`
- final report: `queue/reports/ashigaru4_subtask_cmd020_unmatched_verified_targets_dashboard_mapping_report.yaml`
- snapshot: `queue/reports/unverified_inventory_20260512.yaml`
- 直政 pre_audit cycle2 verdict: `queue/reports/naomasa_unmatched_verified_targets_dashboard_mapping_preaudit_cycle2_20260514.yaml`
