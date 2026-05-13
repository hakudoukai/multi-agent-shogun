# scope_contamination 根本治療 規範文書

`task_id`: subtask_cmd020_scope_contamination_prevention_inline_batch_commit_hook
`parent_cmd`: cmd_020
`reporter`: ashigaru2
`created_at`: 2026-05-13T14:10:00+09:00
`repo_scope`: multi-agent-shogun-newbuild only

## 1. 背景 (= ashigaru3 Layer C 11:18 通達 root cause)

cmd_020 dashboard Layer chain 進行下、2026-05-12 11:17 (msg_20260512_111743_d21693f4) で
**ashigaru3 Layer C 完遂 commit f3651ae に貴殿 ashigaru2 staged 状態の Layer B file が自動取込された scope_contamination 事故** が発生した。具体的に混入したのは以下 2 件である。

- `queue/reports/ashigaru2_dashboard_layer_b_inventory.yaml` (= ashigaru2 deliverable)
- `.gitignore` Layer B whitelist 行 (= ashigaru2 起案)

ashigaru3 自身が `git add` した file は Layer C 関連のみで、上記 2 件は ashigaru3 の commit 範囲外であった。にもかかわらず混入したのは、commit 直前に index にあった ashigaru2 staged 残存 file を、`git commit` が無指示で取り込んだためである。

本事故は **scope_contamination** (= ある ashigaru の commit に別 ashigaru の staged 残存 file が混入する事故) であり、再発すれば commit 帰属が崩壊し、F007 例外 bounded push の equality assert も保証できなくなる。

## 2. root cause 分析 (= ashigaru2 pre-commit 未実施 + staged 残存)

ashigaru3 commit 時点で、ashigaru2 は AC0 inventory yaml + .gitignore Layer B whitelist 行を `git add` した後に **commit せず staged 状態のまま停滞させていた**。これが直接の混入経路である。

原因階層は以下 4 段で整理できる。

| 階層 | 原因 | 影響 |
|------|------|------|
| L1 即因 | ashigaru2 staged 残存 file が index にあった | 別 commit に混入 |
| L2 行動因 | ashigaru2 inline batch commit を実施していなかった (= AC0 commit を後回し) | 直接因 L1 を生む |
| L3 設計因 | inline batch commit 規範が明文化されておらず ashigaru1 Layer A 実証のみだった | 行動因 L2 が起こりやすい |
| L4 構造因 | pre-commit hook で staged 残存検査が無く、機械的抑止が無かった | 行動因 L2 が起きても検出できない |

L1 + L2 は ashigaru2 本人の作業手順、L3 + L4 は規範 + tooling の構造的欠陥である。根本治療原則 (= 5-10 年運用整合、短期 hack 禁) に従い、本規範文書は L1-L4 全てに対応する。

## 3. 再発防止策 4 件

### 3.1 (i) inline batch commit 規範 broadcast

各 ashigaru は task 進行中、deliverable 完成毎に **即 commit** すること。staged 状態のまま次 phase に進むことを禁ずる。

**規範定義**:

1. `git add` 直後に `git commit` (= staged-to-commit 即時)。
2. 1 task 内では 3 commit atomic 構成 (= inventory + impl + test/report) を default 規範とする。
3. 各 commit 直後に `git status --porcelain` で自 file の staged 残存ゼロを verify。
4. 他 ashigaru 進行中 file は触れず、自身分のみ explicit path で `git add` する (= `git add .` / `git add -A` 禁)。

**規範の根拠**: ashigaru1 Layer A 実証 (= 2026-05-11 22:30 完遂、3 commit atomic) で実証済の手順を全 ashigaru の default 規範に昇格させる。

**例外**: F007 例外 bounded push 前の cherry-pick worktree 内 commit はこの規範の対象外 (= 別 worktree 内動作で main 流入と独立)。

### 3.2 (ii) pre-commit hook 装備 (= `.pre-commit-config.yaml` 更新)

`scripts/lint/check_staged_residual.sh` を pre-commit hook chain に追加し、commit 完了直後に staged 残存 file が無いことを機械検証する。

**hook 動作**:

1. `pre-commit-msg` stage で実行 (= commit message 編集後 / commit 確定直前)。
2. `git diff --cached --name-only` で本 commit に含まれる file 列挙。
3. `git status --porcelain` のうち `^[MARCD] ` (= staged 変更) が `本 commit 取込分` を除き残存していれば警告を出す。
4. 残存 staged が **異なる作者 / 異なる task 由来** の可能性が高い場合 (= 検出した path の prefix が現 commit と無関係) は exit 1 で commit 中止。
5. 残存が無い場合 exit 0 で通過。

**graceful skip**: hook script 不在環境 (= 古い checkout / pre-commit 未 install) では何もしない (= exit 0)。

**設計根拠**: 既存 hook (= `secret-detect-staged` + `deliverable-tracked`) と同じ pattern (= scripts/lint/ 配下 bash entrypoint、`pass_filenames: true`) で並列追加し、blast radius を局所化する。新 hook 単独の不具合で既存 hook を巻き込まない。

### 3.3 (iii) 直政 audit gate 「staged 残存 check」追加

直政 Codex 事前監査 (= 規範 2 指示書事前監査) + ashigaru 報告 post-audit の双方で、以下 check 項目を追加する。

**事前監査 check 項目 (追加 1 件)**:

- 「task YAML に `inline batch commit 規範遵守` constraint が constraints field に記載されているか」を verify。記載なし → pass_with_concerns (= karo に補追指示)。

**事後監査 check 項目 (追加 1 件)**:

- 「commit 完了後、`git status --porcelain` 等の staged 残存ゼロ evidence が完遂報告 yaml に記載されているか」を verify。記載なし → 報告差し戻し。

**実装責任分界**:

- 本文書は規範 + check 項目の明文化のみ。直政事前監査 / 事後監査の実装 (= naomasa hook 改修) は別 task として karo が起案する (= 本 task 範囲外)。
- 本文書は「規範の source-of-truth」として直政 / karo / ashigaru の共通参照点となる。

### 3.4 (iv) ashigaru 完遂報告 「pre-commit verify 完遂」明示 field 義務化

各 ashigaru の完遂報告 yaml (= `queue/reports/ashigaru{N}_*_report.yaml`) に以下 field を必須追記する。

```yaml
pre_commit_verify:
  staged_residual_zero_after_commit: true       # 各 commit 直後 `git status --porcelain` で自 file 残存ゼロを確認したか
  commits_atomic_count: 3                        # 本 task の自身 commit 数 (= inline batch 規範下 default 3)
  cross_agent_contamination_risk_check: pass    # 他 ashigaru 進行中 file への混入 risk 無し
  verify_command: |
    git log --format=%H -3
    git status --porcelain
  verify_evidence: |
    (= commit 直後の status 結果を coloquial に retain、commit SHA + status 抜粋を必須記載)
```

**field 義務化の効力**:

- 本 field 不在の完遂報告は **未完成扱い** とする (= 直政 post-audit で差し戻し)。
- 本 field の値が `false` ないし `evidence` が空である場合は **要再実施** として扱う。
- 本 field は ashigaru 自身による「機械 verify を自ら実施した」evidence であり、自己責任の明示である。

**先行実装 reference**: 本 task の完遂報告 yaml (= `ashigaru2_subtask_cmd020_scope_contamination_prevention_inline_batch_commit_hook_report.yaml`) に上記 field を実装し、規範 + 実装の双方を本 task 内で同時 release する。

## 4. 適用範囲 (= multi-agent-shogun-newbuild repo only)

本規範は `multi-agent-shogun-newbuild` repo 内の全 ashigaru / gunshi / karo の commit に対して適用する。`hakudokai-dev` repo は本規範の **適用範囲外** とする (= 別 commit gate 設計、cross-repo 整合は別 task で karo が起案)。

`shogun` (= 信長殿) の MC 統合 commit は本規範の対象外とする (= shogun は agent でなく orchestrator、別 protocol)。

## 5. cross-reference (= cmd_004 Phase 6 既存 hook 整合)

`.pre-commit-config.yaml` の既存 hook は本規範下 retain する。

| hook id | source task | 役割 | 本規範下扱い |
|---------|------------|------|--------------|
| `secret-detect-staged` | cmd_004 Phase 6 (security hardening) | secret/PII 検出 | retain (= 不変) |
| `deliverable-tracked` | cmd_004 Phase 1-6 rollback recovery audit | deliverable git-tracking verify | retain (= 不変) |
| `staged-residual-check` | **本 task 新規** | staged 残存検査 | **append** (= 並列追加) |

既存 2 hook の `stages: [pre-commit, pre-push]` 配置と整合させる。

## 6. 起案完了基準 (= 本 task AC alignment)

本規範文書の起案完遂は以下を満たすことを基準とする。

- §1 背景 + §2 root cause 4 階層分析 + §3 再発防止策 4 件 + §4 適用範囲 + §5 cross-reference + §6 起案完了基準 の全 section を含む (= AC2 alignment)。
- §3.1-§3.4 が task YAML の AC2 (i)-(iv) と 1:1 対応する。
- static source-contract test (= `scripts/test/test_subtask_cmd020_scope_contamination_prevention_inline_batch_commit_hook_static_contract.py`) で 4 件再発防止策 anchor + pre-commit hook 装備 anchor + audit gate section + pre_commit_verify field section 全件 PASS (= AC3 alignment、SKIP=0 / FAIL=0)。
- `.pre-commit-config.yaml` に `id: staged-residual-check` hook が append され、entrypoint `scripts/lint/check_staged_residual.sh` が存在する (= AC2 (ii) alignment)。
- 本規範文書は完遂報告 yaml + inline batch 3 commit + bounded F007 push で release される (= AC4 + AC5 alignment、push は陛下御差配仰ぎ後)。

本文書は規範の source-of-truth であり、改訂は別 task で karo 経由起案するものとする。
