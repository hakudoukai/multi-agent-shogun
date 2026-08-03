# 発注テンプレ — 委譲契約8項目 (管理者共通綱領 v1.0 第1条)

> **正本**: `project_documents id=690355b9` / version v1.0 / is_current=true / SHA256 fc880ea4…（照合済）
> **採用**: 理事長制定「管理者共通綱領（指示を出す側の統一原則）v1.0」を **SecondPC 発注規則** として採用（信長 msg_20260718_090750 経由周知、2026-07-18）。
> **拘束範囲**: karo-second が SecondPC 系で **指示 / 発注 / 委譲** を出す全場面。**足軽への task YAML 発行にも本8項目を必須組込み**。
> **独断改訂禁**: 正本改訂は 委員長起案 → 相談役監査 → 理事長承認。本テンプレは正本の運用写しであり、正本と乖離させない。

## 第1条 — 委譲契約8項目（発注時 必須・欠落は様式差し戻し可、hold 責任は発注側）

| # | 項目 | 記載規約 |
|---|------|---------|
| 1 | **要件** | 目的・背景。★理事長発言は原文引用★（口頭要約に置換しない）。 |
| 2 | **作業場所** | 絶対 path / worktree / branch / 基点 commit を明示。 |
| 3 | **環境** | 対象 PC / 実行環境 / credential 所在（★値は書かない★）。 |
| 4 | **前工程成果物** | path + SHA（★口頭要約のみの引継ぎ禁★）。 |
| 5 | **受入条件** | 実測可能な green 条件（★曖昧語禁★・DD-072 §M 準拠）。 |
| 6 | **成果物規約** | 出力先 path / 命名 / ファイル必須（★chat 報告のみ禁★）。 |
| 7 | **差し戻し時の直し方** | 再提出単位 + 再監査条件。 |
| 8 | **Completion Definition** | done_when / not_done_when / evidence / scope / stop_boundaries / if_blocked / report_to。 |

## 付帯規則

- **SHA-256 添付**: 全成果物に SHA-256 を添付。★SHA 無しは差し戻し可★。
- **軍師（家康）依頼経路**: 第3条-4。軍師への依頼は必ず **家老の正式 task YAML 経由**。直送 hold は 5 日滞留の実害既発ゆえ厳守。
- **欠落発注**: 8項目いずれか欠落は様式差し戻し可。hold 責任は発注側（＝発注者が hold の責を負う）。

## task YAML への組込み雛形

```yaml
task:
  task_id: subtask_xxx
  parent_cmd: cmd_xxx
  bloom_level: Lx
  # --- 委譲契約8項目 (綱領 v1.0 第1条) ---
  requirement: |            # (1) 目的・背景（理事長発言は原文引用）
  work_location:            # (2) 絶対path / worktree / branch / base_commit
    path:
    branch:
    base_commit:
  environment:              # (3) 対象PC / 実行環境 / credential所在(値は書かない)
  upstream_artifacts:       # (4) path + SHA（口頭要約禁）
  acceptance:               # (5) 実測可能green条件（曖昧語禁・DD-072 §M）
  deliverable_spec:         # (6) 出力先path / 命名 / ファイル必須
  redo_protocol:            # (7) 再提出単位 + 再監査条件
  completion_definition:    # (8)
    done_when:
    not_done_when:
    evidence:
    scope:
    stop_boundaries:
    if_blocked:
    report_to:
  status: assigned
  timestamp: "ISO8601"
```
