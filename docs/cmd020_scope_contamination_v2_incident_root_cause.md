# cmd_020 scope_contamination v2 — incident root cause evidence

`task_id`: subtask_cmd020_scope_contamination_prevention_v2
`parent_cmd`: cmd_020
`reporter`: ashigaru2
`created_at`: 2026-05-13T18:35:00+09:00
`repo_scope`: multi-agent-shogun-newbuild only

## 1. 目的

本日 (= 2026-05-13) 発生した scope_contamination incident 3 件 (= ashigaru3 / ashigaru7 / ashigaru6 関連 commit) の root cause を機械 evidence として記録し、scope_contamination v2 (= ashigaru2 redo task) の hook 再設計 + auto-install 仕組みが当該 incident を構造的に解消することの logical proof を提示する。

本書は **規範 source-of-truth** (= `docs/scope_contamination_prevention.md`) を補完する evidence 文書であり、規範本体ではない。改訂は別 task で karo 経由起案するものとする。

## 2. 本日 incident 3 件 evidence

### 2.1 incident_1: ashigaru3 commit `65c917e` (= ashigaru7 file 混入)

| 項目 | 値 |
|------|-----|
| commit SHA | `65c917e0dd5924ad04797138cf2d181fe7d77174` |
| commit 時刻 | 2026-05-13T14:03:05+09:00 |
| git author | `hakudokai (SC karo) <hakudoukai@gmail.com>` |
| actual session agent | ashigaru3 (= commit message `docs(cmd_020/sc_specialty_inventory)` 整合) |
| 含有 file 1 | `docs/cmd_020_implementation_required_14_cmd_proposal.md` (= **ashigaru7 deliverable**) |
| 含有 file 2 | `queue/reports/ashigaru3_subtask_cmd020_sc_specialty_inventory_report.yaml` (= ashigaru3 own) |
| atomic integrity | **broken** (= ashigaru7 file 混入) |

**incident detail**: ashigaru3 が `sc_specialty_inventory_report` の addendum commit を切る際、index に ashigaru7 task (`implementation_required_14_cmd_proposal.md`) の staged 残存があり、`git commit` が無指示で取り込んだ。 commit message + commit 内 ashigaru3 own file 構成からは ashigaru3 session 帰属が読み取れるが、git author は SC karo session が後刻 git config を overwrite した結果と推察される (= last-write-wins race)。

### 2.2 incident_2: ashigaru7 commit `240dd7a` (= ashigaru3/4 file 混入)

| 項目 | 値 |
|------|-----|
| commit SHA | `240dd7a6df76edd2bf9f62deecbc151e2b8d9bf8` |
| commit 時刻 | 2026-05-13T14:02:15+09:00 |
| git author | `hakudokai (SC karo) <hakudoukai@gmail.com>` |
| actual session agent | ashigaru7 (= commit message `docs(cmd_020 classification_logic)` 整合) |
| 含有 file 1 | `docs/dashboard_layer_c_function.md` (= **ashigaru3 Layer C deliverable**、cross-layer anchor 1 行 edit) |
| 含有 file 2 | `docs/dashboard_layer_d_zunou.md` (= **ashigaru4 Layer D deliverable**、cross-layer anchor 1 行 edit) |
| 含有 file 3 | `docs/dashboard_status_classification_logic.md` (= ashigaru7 own) |
| atomic integrity | **broken** (= ashigaru3 + ashigaru4 file 混入、cross-layer anchor edit は正当だが authorize 経路欠落) |

**incident detail**: ashigaru7 が classification_logic task の commit を切る際、cross-layer reference anchor (= Layer C + D の §6) に 1 行追加し、他 ashigaru の deliverable を同一 commit に含めた。 anchor edit 自体は task 設計上必要だが、ashigaru7 が他 ashigaru 担当 file を編集する権限が **task manifest allowlist** に明示されておらず、機械検証手段が無かった。

### 2.3 incident_3: ashigaru6 commit `a25a1b7` (= ashigaru7 file 全件混入、author drift)

| 項目 | 値 |
|------|-----|
| commit SHA | `a25a1b7cb3ddeeeffd8a42a8a9947c08609872ab` |
| commit 時刻 | 2026-05-13T14:24:35+09:00 |
| git author | `hakudokai (SC karo) <hakudoukai@gmail.com>` |
| actual session agent | **ashigaru6 / ashigaru7 / karo の 3 candidate** (= 機械決定不能) |
| 含有 file (4 件) | `queue/reports/ashigaru7_subtask_cmd020_implementation_required_14_cmd_proposal_inventory.yaml` / `..._pytest.log` / `..._report.yaml` / `scripts/test/test_subtask_cmd020_implementation_required_14_cmd_proposal_static_contract.py` |
| atomic integrity | **open_with_concerns** (= author 名義 + actual session 不一致、3 candidate 並列) |

**incident detail**: commit message は `docs(cmd_020 14cmd revision_v2)` で ashigaru7 task の revise を示すが、本 task assignee field によれば ashigaru6 が当該 14_cmd_proposal revise 担当だった可能性もあり、author 名義は SC karo session の git config overwrite を経た結果である。 tmux pane @agent_id verify 経路無しでは 3 agent のいずれの session で commit が切られたか機械決定不能。

## 3. 真因 — 4 階層分析

3 件 incident に共通する真因は **以下 4 階層の構造的欠陥** であり、ashigaru 個人の作業手順問題ではない。

| 階層 | 真因 | 影響 |
|------|------|------|
| L1 即因 | `.git/hooks/pre-commit` 自体が install されていない | commit 直前検査が一切走らない |
| L2 装備因 | `pre-commit install` (= framework 経由 installer) が SC WSL 環境で実行されていない | hook 装備済 (`.pre-commit-config.yaml`) でも無実体 |
| L3 設計因 (旧 hook) | `check_staged_residual.sh` の commit_set = staged_set 同一 logic、residual_set 常空 | 仮に hook install されていても元事故 (= 他 agent staged 巻取り) を検出不能 |
| L4 識別因 | git config user.{name,email} が共有資源、last-write-wins race で他 agent に overwrite される | author 名義 drift、actual session agent と git author 解離、機械追跡不能 |

L3 + L4 は scope_contamination 第 1 弾 (= ashigaru2 commit `e062f63/9676222/651efcf`) で内包したまま残存し、本日 incident 3 件で顕在化した。

## 4. v2 解消 — logical proof

scope_contamination v2 (= 本 task) は L1-L4 全 4 階層を **構造的に** 解消する。各階層と解消手段の対応は以下である。

| 階層 | 解消手段 (= v2 deliverable) | logical proof |
|------|------|----------------|
| L1 | `scripts/install_pre_commit_hook.sh` (= chmod +x + idempotent overwrite + SessionStart trigger proposal) | `.git/hooks/pre-commit` 実体を保証し、commit 直前検査を必ず走らせる。SessionStart hook 経由 install 提案で session 起動毎に自動 active 化。 |
| L2 | install script は `pre-commit` framework 依存を排除した直接 shim 方式 (= bash entrypoint 直叩き) | framework install 状態に依存せず、bash + git のみで動作。SC + MC 両環境で実行可能。 |
| L3 | `scripts/lint/check_file_path_owner.sh` (= file path owner 識別 + tmux @agent_id 比較 + task manifest allowlist) | commit_set / staged_set 同一前提を廃棄し、各 staged file の owner を file path pattern から決定、現 agent ≠ owner なら reject。 |
| L4 | hook 内で **tmux pane @agent_id を primary identity source**、`git config user.name` は fallback only + 非 ashigaru id 警告 | git config last-write-wins race に依存しない一次 source を確立、actual session agent と一致。 |

加えて **AC3 元事故 re-introduce test 6 件** で本日 incident 3 件を simulation して PASS evidence を取り、設計欠陥が再発しないことを behavioral test で機械保証する (= 旧 5 件 static test では検出不能だった設計欠陥を test 自身が見抜く)。

## 5. 規範 cross-reference

本書は以下と cross-reference する。

| 文書 | 役割 |
|------|------|
| `docs/scope_contamination_prevention.md` | 規範 source-of-truth、§3 再発防止策 4 件 (i)-(iv) は本 v2 で再設計 (= 別 cycle で本書補追) |
| `scripts/lint/check_file_path_owner.sh` | AC1 hook 実装、L3 + L4 解消 |
| `scripts/install_pre_commit_hook.sh` | AC2 install、L1 + L2 解消 |
| `scripts/test/test_scope_contamination_re_introduce.py` | AC3 behavioral test、本書 incident 3 件 simulate |
| `scripts/lint/check_report_finalization.sh` | AC5 report final 化 scoped grep + allowlist |
| `docs/report_finalization_norm.md` | AC5 規範本体 |
| `queue/reports/ashigaru2_subtask_cmd020_scope_contamination_v2_inventory.yaml` | AC0 inventory、本書 evidence 抽出 source |

## 6. 起案完了基準

本書は以下を満たすことを基準とする。

- §1 目的 + §2 本日 incident 3 件 evidence + §3 真因 4 階層分析 + §4 v2 解消 logical proof + §5 規範 cross-reference + §6 起案完了基準 の全 section を含む。
- §2 の 3 incident 全件で commit SHA + 含有 file + atomic_integrity + impact_assessment + git author + actual session agent を明示する。
- §3 + §4 で L1-L4 各階層と v2 deliverable の 1:1 対応を提示し、構造的解消の logical proof を機械検証可能な形 (= deliverable 引照) で記述する。
- 本書は inline batch commit 規範下、commit_1 (= AC0 inventory + AC7 incident root cause doc) で release する。
