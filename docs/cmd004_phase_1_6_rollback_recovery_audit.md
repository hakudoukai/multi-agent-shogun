# cmd_004 Phase 1-6 Rollback Recovery Audit + 再発防止 Mechanism 設計書

- task_id: subtask_cmd004_phase_1_6_rollback_recovery_audit
- parent_cmd: cmd_004
- priority: highest (= 緊急 escalation)
- bloom_level: L4
- author: ashigaru3 (= 滝川一益、F-SEC-1 緊急対応)
- 文書種別: **audit + 再発防止 mechanism 設計書**
- updated: 2026-05-11

---

## 0. 範囲

| 観点 | 含む |
|------|------|
| Phase 1-6 全 deliverable の rollback 検出 inventory | ○ |
| F-SEC-1 root cause 分析 (= git reflog + .gitignore + file mtime) | ○ |
| rollback file 復元 + 整合性 verify (pytest 全件 SKIP=0) | ○ |
| 再発防止 mechanism (= deliverable allowlist + .gitignore whitelist + pre-commit hook + .gitattributes) | ○ |
| 仕組み追加 vs 改修区別 (= 根本治療原則 4 整合) | ○ |

---

## 1. 緊急 finding F-SEC-1 の真因解明

### 1-1. 観測 vs 実態

Phase 6 完遂報告で「Phase 3/5 ファイルが他 agent / linter で rollback されている」と escalation したが、本 task の機械検査で**真因が判明**:

| layer | 観測時の見え方 | 実態 |
|-------|--------------|------|
| tool レイヤ (Read / system-reminder) | requirements.txt から prometheus_client 行が消失、patient-sw.js が v2 状態に rollback | **stale snapshot** (= tool layer の cache 残留)、file system 上は v3 維持 |
| git working tree | (システム reminder と矛盾) | 一貫して Phase 1-6 状態を保持、`wc -l` で v3 (437 lines) / manifest 強化 (72 lines) 等を確認済 |
| git reflog | `reset: moving to HEAD` が 2 件 | uncommitted changes の unstage (= HEAD 不変)、**working tree 改変なし** |
| `.gitignore` | (見落とし) | line 7 の `*` default-ignore + whitelist `!path` 戦略、**Phase 3-6 deliverable 未 whitelist で git 追跡不能** |

### 1-2. 真因 = `.gitignore` whitelist 未更新

- multi-agent repo `.gitignore` は line 7 で `*` 全 ignore、特定 file のみ `!path` で whitelist する **negative pattern** strategy
- Phase 1 で `!docs/cmd004_push_vapid_management.md` は追加されたが、Phase 3-6 の docs / `.pre-commit-config.yaml` / `scripts/lint/*.sh` / `queue/reports/ashigaru3_cmd004_*.yaml` は未追加
- 結果: file は working tree に存在するが `git status` で表示されず、commit 不能 → **「commit に含まれない deliverable」** が生じていた
- これが「rollback」のように見えた原因 = `git log --oneline --name-only` で本 deliverable が登場しないため、別 agent が「rollback したように」見える

### 1-3. working tree rollback は false alarm

- patient-sw.js, patient-manifest.json, PatientAppLayout.tsx の **mtime が 17:20:48 で揃う** → 同時 touch されたが、内容は v3 (Phase 3 完成状態)
- git reset は HEAD 不変、working tree 改変なし
- system-reminder の「modified by user/linter」表記は tool layer の snapshot 比較で発生した false positive

---

## 2. 復元アクション

### 2-1. `.gitignore` whitelist 追加 (AC3)

```diff
+# cmd_004 Phase 3-6 ashigaru3/滝川一益 deliverables
+!docs/cmd004_patient_app_pwa_design.md
+!docs/cmd004_notification_facade_design.md
+!docs/cmd004_observability_design.md
+!docs/cmd004_security_hardening_design.md
+!.pre-commit-config.yaml
+!scripts/lint/
+!scripts/lint/*.sh
+!queue/reports/ashigaru3_cmd004_*.yaml
```

これで `git check-ignore` で全 15 deliverable が **not ignored** に。

### 2-2. 整合性 verify (AC4)

- 全 deliverable file の **物理存在 + key content grep** で確認済
- Phase 1-6 関連 pytest 全件: `python3 -m pytest backend/tests/test_security_hardening.py backend/tests/test_observability.py backend/tests/test_notification_facade.py backend/tests/test_push_notifications_router.py` → **72 passed / 0 failed / 0 skipped / 0 warnings**

---

## 3. 再発防止 Mechanism (AC5、根本治療原則 4 仕組み追加)

### 3-1. deliverable allowlist 検証 script

`scripts/lint/check_deliverable_tracked.sh`:
- Phase 1-6 deliverable 15 件を **inline list** で保持
- `git check-ignore -q` で各 file が ignored でないことを検査
- 1 件でも ignored なら exit 1 + hint 表示

### 3-2. pre-commit hook 統合

`.pre-commit-config.yaml` に `deliverable-tracked` hook を追加:

```yaml
- id: deliverable-tracked
  name: Phase 1-6 deliverable git-tracking verify
  entry: bash scripts/lint/check_deliverable_tracked.sh
  language: system
  pass_filenames: false
  stages: [pre-commit, pre-push]
```

これで commit / push 前に **「設計済 deliverable が .gitignore で誤って ignored になっていないか」** を機械検査。

### 3-3. `.gitattributes` 起案

- 重要 deliverable に **LF eol 固定** + **text 属性明示**
- cross-PC (MC/SC) で CRLF/LF 衝突による merge 失敗を防止
- 全 phase の `*.md`, `*.yaml`, `*.sh`, `*.py`, `*.ts(x)`, `*.json` 等を網羅

### 3-4. tool layer の stale snapshot 対策 (= 観察作法)

機械検査では検出できない tool snapshot inconsistency に対する作法:

| 現象 | 対策 |
|------|------|
| system-reminder で「file was modified」表記 | **必ず Bash で実 file 内容を `head` / `grep` で再確認**、Read tool 単独で結論しない |
| Edit tool 失敗時の "File has not been read yet" | 再 Read してから Edit、cache 状態を信頼しない |
| 観測した「rollback」 | `git status` + `git log` + `wc -l` で実体検査、報告前に 3 経路 cross-check |

### 3-5. 根本治療原則 4 整合 (= 仕組み追加 vs 改修区別)

| 層 | 改修 (= 設計書範囲) | 仕組み追加 (= 別 task) |
|----|-------------------|--------------------|
| `.gitignore` whitelist 追加 | 本 task 内、機械的 | — |
| `check_deliverable_tracked.sh` 新規 | 本 task 内、自前 minimal script | — |
| pre-commit hook 拡張 | 本 task 内、既 config に追加 | — |
| `.gitattributes` 新規 | 本 task 内 | — |
| Git LFS / artifact storage | — | OD-RBA-1 (= 大型 binary 想定時) |
| protected branch / push protection | — | OD-RBA-2 (= GitHub side ops) |

---

## 4. 検証 evidence

### 4-1. deliverable allowlist 検証

```
$ bash scripts/lint/check_deliverable_tracked.sh -v
[OK]   docs/cmd004_push_vapid_management.md
[OK]   queue/reports/ashigaru3_cmd004_push_vapid_infra_report.yaml
[OK]   queue/reports/ashigaru3_cmd004_push_vapid_phase2_report.yaml
[OK]   docs/cmd004_patient_app_pwa_design.md
[OK]   queue/reports/ashigaru3_cmd004_service_worker_offline_sync_report.yaml
[OK]   docs/cmd004_notification_facade_design.md
[OK]   queue/reports/ashigaru3_cmd004_notification_facade_pattern_report.yaml
[OK]   docs/cmd004_observability_design.md
[OK]   queue/reports/ashigaru3_cmd004_observability_infra_report.yaml
[OK]   docs/cmd004_security_hardening_design.md
[OK]   queue/reports/ashigaru3_cmd004_security_hardening_infra_report.yaml
[OK]   .pre-commit-config.yaml
[OK]   scripts/lint/check_secrets.sh
[OK]   scripts/lint/dependency_audit.sh
[OK]   scripts/lint/check_deliverable_tracked.sh
[check_deliverable] summary: ok=15 missing=0 ignored=0 total=15
[check_deliverable] OK: all deliverables tracked.
```

### 4-2. Phase 1-6 pytest

```
============================== 72 passed in 3.44s ==============================
```

(security 16 + observability 20 + facade 24 + push_notifications regression 12 = 72)

---

## 5. Open Items

| OD | 項目 | 申し送り先 |
|----|------|----------|
| OD-RBA-1 | Git LFS / artifact storage 検討 (= 大型 binary deliverable 想定時) | karo (= 後段 ops) |
| OD-RBA-2 | GitHub branch protection / push protection 設定 | karo (= ops) |
| OD-RBA-3 | hakudokai-dev repo にも check_deliverable_tracked.sh 起案 | karo (= 後段 audit task) |
| OD-RBA-4 | tool layer stale snapshot を agent 横断で抑止する SOP 文書化 | karo (= 仕組み追加、規範 update) |

---

## 6. 結論

F-SEC-1 緊急 escalation の真因は **working tree rollback ではなく、`.gitignore` whitelist 未更新による「git 追跡漏れ」** だった。本 task で:

1. `.gitignore` に Phase 3-6 deliverable whitelist を追加 (= 復元)
2. 整合性 verify (= pytest 72/72 SKIP=0)
3. **再発防止 4 層 mechanism** を起案 (= allowlist script + pre-commit hook + .gitattributes + 観察作法)

これで Phase 1-6 一括 push 安全化、家康御差配仰ぎ前段 task 完遂。
