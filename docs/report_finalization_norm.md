# report 最終化規範 (= bounded push 後 SHA 即埋め + completion-claim scoped grep)

`task_id`: subtask_cmd020_scope_contamination_prevention_v2
`parent_cmd`: cmd_020
`reporter`: ashigaru2
`created_at`: 2026-05-13T18:50:00+09:00
`repo_scope`: multi-agent-shogun-newbuild only

## 1. 背景 — 本日 4 件再発の教訓

本日 (= 2026-05-13) の完遂報告 yaml で **commit SHA TBD / push status pending / AC 系 pending** が完遂主張時点に残存した事案が 4 件 (= ashigaru1 / ashigaru3 / ashigaru4 / ashigaru5 / ashigaru7) 連続発生し、いずれも直政 post-audit で `fail_requires_report_correction` 判定を受けた。

ashigaru2 第 1 弾 (= e062f63/9676222/651efcf) も同じ瑕疵 (= commit_3 SHA TBD + push_plan pending) を内包し直政 post-audit で fail 判定。本書は **bounded push 後 SHA 即埋め** + **completion-claim sections のみ scoped grep + allowlist** の 2 段構えで本 root cause を構造的に解消する。

## 2. 用語定義

| 用語 | 定義 |
|------|------|
| 完遂主張部 (= completion-claim sections) | 完遂報告 yaml 内で「本 task は完遂」と主張する根拠を述べる top-level section 群。具体的には `commit_history`, `push_plan`, `acceptance_criteria`, `next_actions` の 4 section。 |
| 履歴部 / 引用部 (= historical / quoted sections) | `revise_history`, `fail_evidence`, `source_quotes`, `prior_state`, `cycle{N}_state` 等の **過去の状態を記録する** section 群。これら section 内の `pending` 等は過去の状態 evidence として正当。 |
| 未確定 token (= forbidden token) | 完遂主張部に出現すると「未確定」扱いとなる文字列。具体的には `TBD`, `TBD_SHA`, `pending`, `予定`, `planned`, `in_progress`, および `予定` (日本語)。 |
| status taxonomy enum | 状態 enum 値で内部に "pending" 等を含み得る。例: `completion_gate: open_with_concerns`, `verdict: pass_with_conditions`. allowlist で exempt する。 |

## 3. 規範 — bounded push 後 SHA 即埋め

bounded F007 push 完遂直後、ashigaru は **同 commit chain 内** で完遂報告 yaml の commit_history と push_plan section に actual SHA を埋め戻すこと。具体的手順は以下である。

1. 5 commit を inline batch で作成。最終 commit (= report yaml 自身) 内の `commit_history` / `push_plan` section に `TBD_SHA_1..TBD_SHA_5` placeholder を一旦置く。
2. worktree + cherry-pick で bounded F007 push を準備。pre-push verify で expected SHA 列と actual SHA 列の equality assert (= printf + diff exit 0) を実施。
3. push 完了直後、actual SHA 列を report yaml の `commit_history` / `push_plan` section に埋め戻す。
4. 同 SHA backfill を 6 番目の revise commit として inline で追加し、再度 bounded F007 push (= 1 commit only)。
5. 最終 report yaml に `check_report_finalization.sh` を適用し、completion-claim sections に未確定 token が残存しないことを machine verify。

revise commit の頻度を最小化するため、可能であれば最初の bounded push で `report yaml` を含めず、push 後に SHA を埋めた report yaml を 1 つの revise commit で push する 2 段構えも許容される (= task YAML の `push_plan.commits` 数に応じて選択)。

## 4. 規範 — completion-claim scoped grep

`check_report_finalization.sh` は以下の規範下動作する。

- **scope**: top-level key が `commit_history`, `push_plan`, `acceptance_criteria`, `next_actions` の 4 section 内の行のみを走査。それ以外の section (= 履歴部 / 引用部 / fail_evidence / meta header) は走査対象外。
- **forbidden tokens**: `TBD`, `TBD_SHA`, `pending`, `予定`, `planned`, `in_progress` を completion-claim sections 内に検出したら exit 1。
- **allowlist**: `scripts/lint/report_finalization_allowlist.txt` に列挙された substring pattern に line が match した場合は exempt (= status taxonomy enum / lifecycle meta field / 履歴引用)。
- **comment 行**: `# ` で始まる comment 行は走査前に除去。
- **invocation**: `bash scripts/lint/check_report_finalization.sh <report.yaml>` で単一 file 走査、複数 file も可。

## 5. 規範 — allowlist 設計

allowlist は以下 3 系統で構成する (= `scripts/lint/report_finalization_allowlist.txt` § comment 区分)。

1. **status taxonomy enum**: `completion_gate: open_with_concerns`, `verdict: pass_with_conditions` 等の enum 値。内部に `pending` を含み得るが state name として正当。
2. **task lifecycle meta fields**: `audit_gate_status:`, `pre_audit_verdict:`, `pre_audit_msg:`, `pre_audit_cycle:`, `pre_audit_pass:` 等の lifecycle marker。完遂主張部内に過去の audit cycle 経歴として引用される場合は exempt。
3. **履歴 / 引用 cross-reference**: `historical_status:`, `prior_state:`, `cycle{N}_state:` 等の prefix で始まる field は履歴部の引用として exempt。

allowlist 拡張は別 task で karo 経由起案する。task ごとの個別 exempt 必要時は task YAML の `report_finalization_allowlist_extension` field を将来追加する (= 本書未実装、別 cycle)。

## 6. 規範 — 自身実証

本規範の有効性は **本 task の完遂報告 yaml 自身** で実証する。

- `queue/reports/ashigaru2_subtask_cmd020_scope_contamination_v2_report.yaml` の completion-claim sections に未確定 token が残存しないこと。
- `scripts/test/test_report_finalization_grep_evidence.py` で本 report に対し `check_report_finalization.sh` を実行し pass evidence を pytest として記録 (= AC5)。
- 本 task のための test fixture (= 故意に `TBD` を含む報告 yaml) で fail evidence も pytest として記録。

本 self-verify chain により、規範の運用可能性を deliverable 自身の commit 内で機械保証する。

## 7. 適用範囲 + 例外

- 本規範は `multi-agent-shogun-newbuild` repo 内の `queue/reports/*.yaml` 完遂報告 yaml に適用。
- `hakudokai-dev` repo は範囲外。
- preview-only 報告 (= `*_inventory.yaml`, `*_pytest.log`) は対象外 (= 完遂主張部を持たない)。
- 直政 audit 報告 (`queue/reports/naomasa_*`) は対象外 (= 評価 side の報告で完遂主張部の意味論が異なる)。

## 7-bis. 規範 — semantic stale guard (= 2026-05-13 post-audit 拡張)

直政 post-audit (= queue/reports/naomasa_ashigaru2_scope_contamination_v2_post_audit_20260513.yaml) で **token regex 単独では捕捉できない semantic stale state** が指摘された (= findings[0] severity=high)。具体例: `push_plan.status: ready_for_bounded_push` が `commit_history` に確定 SHA 存在後も残存し、完遂主張と矛盾するが、`ready_for_bounded_push` という string は forbidden token regex (`TBD` / `pending` / `予定` / `planned` / `in_progress`) と接尾辞接頭辞いずれの形でも合致しない。

本 §7-bis では `check_report_finalization.sh` に **semantic stale guard** を追加し、以下の 2 条件の同時成立を検出する。

| 条件 | 検出 path |
|------|----------|
| (a) `commit_history` 内に **resolved SHA** (= `sha: <7-40 桁 hex>`) が 1 件以上 | `RESOLVED_SHA_REGEX='\bsha:[[:space:]]*[0-9a-f]{7,40}\b'` |
| (b) `push_plan` 内に `status:` が **semantic stale state** value を保持 | `SEMANTIC_STALE_STATES_REGEX='\b(ready_for_bounded_push\|awaiting_bounded_push\|awaiting_push\|requires_sha_backfill\|requires_backfill\|ready_for_push)\b'` |

両条件成立時、`check_report_finalization.sh` は `[push_plan semantic_stale_guard]` 診断付きで `exit 1` を返す。

**設計指針** — `pending_bounded_push` / `pending_backfill` 等は既存 `pending[a-z_]*` 正規表現で既に捕捉される。本 §7-bis は **既 token regex で捕捉漏れする stale state value** のみを補足する。

**legitimate な pre-push 状態** (= 5 commit 作成前に report yaml を起案、push 後 SHA backfill 予定) は SHA 不在故 (a) 不成立で本 guard 不発動。これにより誤検出を回避する。

pytest case:
- `test_semantic_stale_state_with_resolved_shas_fails`: (a) ∧ (b) → fail
- `test_pre_push_stale_state_without_resolved_shas_passes`: (b) のみ → pass (= pre-push legitimate state)
- `test_completed_status_with_resolved_shas_passes`: completed + resolved SHA → pass (= positive post-push case)

allowlist 経由で個別免除可能 (= 履歴 cross-reference 内に stale state を引用する場合は historical line として allowlist match で skip)。

## 8. 起案完了基準

本書は以下を満たすことを基準とする。

- §1 背景 + §2 用語定義 + §3 SHA 即埋め規範 + §4 scoped grep 規範 + §5 allowlist 設計 + §6 自身実証 + §7 適用範囲 + §8 起案完了基準 の全 section を含む。
- §3 + §4 + §5 が `scripts/lint/check_report_finalization.sh` + `scripts/lint/report_finalization_allowlist.txt` の実装と整合する。
- §6 が `scripts/test/test_report_finalization_grep_evidence.py` の test 内容と整合する。
- 本書は inline batch commit 規範下、commit_3 (= AC2 install + AC5 finalization 規範) で release する。
