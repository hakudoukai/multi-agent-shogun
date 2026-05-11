# Cross-PC Repo Accessibility Preflight Protocol

起案: 井伊直政 (SecondPC Codex)
根拠: 家康下命 msg_20260511_160641_c2095705 / subtask_cross_pc_repo_protocol_design
目的: PC 専属 repo を誤った PC の足軽へ配分する事故を、task YAML 起案時点の機械 preflight で防ぐ。

---

## 1. Position In The Rules

本規範は F007 / auto_git_sync 系列の前段 gate である。F007 が「git 同期後の状態」を扱うのに対し、本規範は「そもそもその PC から対象 path を読めるか」を判定する。

最上位原則:

- 仕組みで防ぐ: 足軽の勘や着手後の blocked_env 報告に依存しない。
- 機械証跡のみ: `ls`, `stat`, `git -C ... status`, `realpath` の結果で判定する。
- fail closed: target path が不可視なら SC 足軽へ配分しない。
- F001-F007 整合: 家老は preflight と配分判断まで行い、実装代行はしない。

---

## 2. Repo Classification

| Class | Definition | Assignment Rule |
|-------|------------|-----------------|
| SC-only | SecondPC にのみ実体がある repo/path | SC ashigaru/gunshi only |
| MC-only | MainPC にのみ実体がある repo/path | MC ashigaru only; SC assignment forbidden |
| Shared | 両 PC が同一 repo を持ち、git sync/pull で収束できる repo | Either PC allowed after local preflight |

Known path audit on SecondPC (2026-05-11):

| Path Prefix | Observed On SC | Classification | Evidence |
|-------------|----------------|----------------|----------|
| `/mnt/c/Projects/hakudokai-dev/` | exists | Shared | `ls -ld` succeeded; `git -C ... status` usable |
| `/home/hakudokai/projects/multi-agent-shogun-newbuild/` | exists | Shared | current repo; `git status --branch` clean at preflight time |
| `/home/hakudokai/projects/multi-agent-shogun/` | exists | SC/local legacy | present on SC with unrelated dirty shim files; do not assume MC parity |
| `/mnt/c/Users/User/Documents/DentalBI/` | missing | MC-only | `ls: cannot access ... No such file or directory` on SC |

Any new path prefix not listed here is `unknown` until `ls -ld`, `stat`, and `git -C <repo> rev-parse --show-toplevel` succeed on the assigning PC.

---

## 3. Prefix Mapping

| target_path Prefix | Responsible PC | Karo Action |
|--------------------|----------------|-------------|
| `/mnt/c/Users/User/Documents/DentalBI/` | MainPC | Do not assign to SC. Reassign to MC ashigaru via brother chain. |
| `/mnt/c/Projects/hakudokai-dev/` | Shared | SC assignment allowed only after `stat` and `git status` pass. |
| `/home/hakudokai/projects/multi-agent-shogun-newbuild/` | Shared | SC assignment allowed; push/pull path must be recorded if MC must consume. |
| `/home/hakudokai/projects/multi-agent-shogun/` | SC/local legacy | Treat as SC-local unless MC existence is separately verified. |
| Other `/mnt/c/Users/...` | unknown, likely PC-specific | Block until source PC is identified. |

If a task has multiple `target_path` values, the strictest class wins. One MC-only path makes the whole task MC-only unless the task is explicitly split.

---

## 4. Dual Preflight Gate

### Gate A: Karo Before Task YAML

Karo must run these checks before assigning any task with `target_path`, `deliverable`, or prose path references:

```bash
TARGET="/path/from/task"
test -e "$TARGET" || { echo "blocked_env:path_missing:$TARGET"; exit 20; }
stat "$TARGET" >/dev/null || { echo "blocked_env:stat_failed:$TARGET"; exit 21; }
REPO="$(git -C "$TARGET" rev-parse --show-toplevel 2>/dev/null || true)"
test -n "$REPO" || { echo "blocked_env:not_git_repo:$TARGET"; exit 22; }
git -C "$REPO" status --short --branch | sed -n '1,20p'
```

For file paths that do not exist yet, Karo must preflight the nearest existing parent directory and record `target_path_expected_new: true`.

Task YAML additions:

```yaml
repo_access_preflight:
  pc: secondpc
  checked_at: "YYYY-MM-DDTHH:MM:SS+09:00"
  target_paths:
    - path: "/mnt/c/Projects/hakudokai-dev/backend/api/kanban.py"
      class: shared
      exists: true
      repo_root: "/mnt/c/Projects/hakudokai-dev"
      git_status_checked: true
  assignment_allowed: true
```

### Gate B: Ashigaru Before Work

Ashigaru must repeat a lightweight check before editing:

```bash
test -e "$TARGET" && stat "$TARGET" >/dev/null
```

If this fails, the ashigaru must stop and report:

```bash
bash scripts/inbox_write.sh karo "blocked_env: target_path inaccessible on this PC: $TARGET" report_received ashigaruN
```

They must not improvise alternate local paths.

---

## 5. blocked_env Escalation

When SC detects an MC-only path:

1. Mark task `blocked_env` or do not assign it.
2. Report to Karo inbox with path, PC, and command evidence.
3. Karo asks MainPC brother chain to reassign.
4. If the task also contains shared repo work, split shared and MC-only parts into separate tasks.
5. Completion gate remains `blocked` until the correct PC produces machine evidence.

Report fields:

```yaml
evidence_state: blocked_env
completion_gate: blocked
blocked_reason: "target_path is MC-only; inaccessible from SecondPC"
repo_access_preflight:
  failing_path: "/mnt/c/Users/User/Documents/DentalBI/..."
  observed_error: "No such file or directory"
```

---

## 6. Karo.md Patch Proposal

Insert this gate between current Karo workflow step 5 (`decompose_tasks`) and step 6 (`write_yaml`):

```diff
 workflow:
   - step: 5
     action: decompose_tasks
+  - step: 5.5
+    action: repo_access_preflight
+    mandatory: true
+    note: |
+      For every task containing target_path/deliverable/prose file paths:
+      1. Classify each path as SC-only / MC-only / Shared / unknown.
+      2. Run ls/stat/git status on the assigning PC before writing task YAML.
+      3. If any path is MC-only (e.g. /mnt/c/Users/User/Documents/DentalBI/),
+         do not assign to SC ashigaru; reassign through MC brother chain.
+      4. If path is Shared (e.g. /mnt/c/Projects/hakudokai-dev/),
+         assignment is allowed only when local stat + git status evidence is recorded.
+      5. Write repo_access_preflight into task YAML.
   - step: 6
     action: write_yaml
```

This is a proposal rather than direct Karo instruction mutation because Karo workflow changes should be reviewed by Karo/Shogun before becoming active law.

---

## 7. Audit Lens Decision

Add an explicit `11_cross_pc_repo_check` lens. Existing `10_ecosystem_coherence` covers cross-PC report/schema/memory flow, but it does not specifically fail a task whose source path is physically inaccessible from the assigned PC. Keeping this separate preserves the 10th lens and makes repo accessibility a pre-work gate rather than a broad ecosystem concern.

Verdict guidance:

- `pass`: All target paths are classified, locally accessible on the assigned PC, and git status evidence is recorded.
- `concerns`: Shared repo path is accessible, but MC consumption/push-pull verification is not yet attached.
- `fail`: Any assigned target path is PC-specific and inaccessible from the assigned PC, or the task lacks path classification for a path-bearing assignment.

---

## 8. Enforcement Roadmap

Phase 1, now:

- Document this protocol.
- Add `11_cross_pc_repo_check` to audit guidelines.
- Add Karo step 5.5 proposal.

Phase 2, follow-up task:

- Implement `scripts/preflight_repo_access.sh`.
- Add a task YAML validator rule requiring `repo_access_preflight` when `target_path` exists.
- Add completion gate integration so `blocked_env` prevents audited_done.

This separation avoids overbuilding in the design task while preserving a direct enforcement path.
