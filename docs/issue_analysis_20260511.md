# Issue Analysis 2026-05-11

## Executive Judgment

The five incidents share one structural root cause:

**completion is being declared before evidence becomes locally verifiable on the reviewing PC.**

The system has strong rules, but several are advisory rather than gate-enforced:

- Shogun verification is not a precondition of completion.
- Cross-PC audit logs are not required to arrive before MC-side verification.
- `partial` verdicts are allowed to coexist with completion language.
- Memory and rule updates do not yet have a durable cross-PC propagation path.

This is not primarily a motivation failure. It is a state machine and evidence pipeline failure.

## Problem Deep Dive

| # | Problem | Immediate Cause | Structural Cause | Required State |
|---|---|---|---|---|
| 1 | Shogun verify duty not executed | `shogun_verification_log.yaml` has no 2026-05-11 entry in this worktree | verify is a script available to run, not a blocking gate | Any `audit_passed` claim must remain incomplete until `shogun_verified=true` exists |
| 2 | SC audit log not pushed | MC cannot see SC `naomasa_new_*` entries | cross-PC report arrival is not part of acceptance criteria | SC report commit/push or equivalent signed transfer must precede MC verify |
| 3 | `partial` verdict remains | pytest environment unavailable | `partial` is used as a tolerated terminal-ish state | `partial` must map to `blocked_verification` or `failed_test_evidence`, never completion |
| 4 | Optimistic reporting | evidence not fetched before summary | reports are narrative-first, evidence-second | summary must cite concrete `audit_id`, commit, log path, test result, and verify result |
| 5 | Cross-PC sync missing | memory sync design exists but not reviewed/implemented | shared operating rules lack a synchronization mechanism | shared memory/rule blocks must be versioned and distributed event-wise |
| 6 | Verify script cannot read SC report structure | `shogun_verify_audit.sh` expects `reports:` list only | MC/SC auditor report schemas diverged (`new_project_audits`, `phase_b_reaudits`, legacy blocks) | verification parser must support the standard schema or normalize inputs before verify |

## 9-Point Analysis

### 1. Functional Correctness

`scripts/shogun_verify_audit.sh` can verify entries present in four report files, but it cannot verify evidence absent from the local repo. Therefore MC-side verification cannot function when SC reports are not committed/pushed or otherwise transferred.

Fix: add a preflight mode:

```bash
bash scripts/shogun_verify_audit.sh --preflight <audit_id>
```

It should return one of:

- `ready_to_verify`
- `missing_audit_entry`
- `unsupported_report_schema`
- `missing_cross_pc_report`
- `partial_verdict_blocked`
- `missing_log_or_commit`

It must also parse or normalize SecondPC report shapes such as:

- top-level `reports: [...]`
- `new_project_audits: [...]`
- `phase_b_reaudits: [...]`
- older named blocks used by Naomasa/Acha reports

### 2. Anti-Duplication

Do not add a new monitor daemon. Existing pieces are enough:

- `scripts/shogun_verify_audit.sh`
- PC-suffixed report files
- inbox/pc_handshake event delivery
- proposed `docs/memory_sync_design.md`

Fix should be a thin gate script plus schema tightening, not another polling watcher.

### 3. Discipline

The active task flow forbids invented statuses in command/task status fields. The correct pattern is:

- keep canonical `status`
- add `audit_status`
- add `cross_pc_sync_status`
- add `shogun_verified`

Do not introduce terminal language for `partial`.

### 4. Logic / State Machine

Current implied flow:

```text
audit report written somewhere -> narrative says done -> maybe verify later
```

Required flow:

```text
audit report written
-> report reachable on reviewing PC
-> tests complete with SKIP=0
-> verdict not partial
-> shogun_verify_audit passes
-> completion may be reported
```

If any step fails, the item is not complete. It is blocked, failed, or pending verification.

### 5. Schema Integrity

Add these fields to audit entries and task summaries:

```yaml
audit_status: passed | passed_with_concerns | failed | blocked_verification
cross_pc_sync_status: local_only | pushed | pulled | verified_present
test_evidence_status: pass | fail | blocked_env | missing
shogun_verified: true | false
shogun_verified_at: null
completion_gate: open | blocked
blocker_reason: null
```

`partial` may remain inside `perspective_verdicts`, but must not be a top-level completion verdict.

Report file schema must also be normalized. Every auditor file should expose a canonical `reports` list, even if legacy sections remain for history. The verify script should read the canonical list first and optionally scan known legacy sections with a warning.

### 6. Test Sufficiency

The rule remains: SKIP or incomplete test execution is not completion.

If pytest cannot run due to environment constraints, the correct state is:

```yaml
test_evidence_status: blocked_env
audit_status: blocked_verification
completion_gate: blocked
```

Do not convert it to `pass_with_concerns` unless an equivalent approved test path is documented.

### 7. Legal / Security

Cross-PC memory sync and report sync must not ship raw private memory, service role keys, or patient data. The memory sync design already states shared block export plus secret/PII validation. The same validator should be reused before any Supabase/source-code-cache transfer.

### 8. Operations / UX

The Shogun needs a small status table, not prose:

| audit_id | present_on_MC | verdict | tests | shogun_verified | completion_gate |
|---|---|---|---|---|---|
| naomasa_new_001 | no | unknown locally | unknown locally | false | blocked |
| naomasa_new_002 | no | unknown locally | unknown locally | false | blocked |
| naomasa_reaudit_001 | no | unknown locally | unknown locally | false | blocked |

This prevents optimistic summaries.

### 9. Documentation

The permanent rules should be added to:

- `instructions/common/task_flow.md`
- `instructions/gunshi_audit_guidelines_v1.md`
- `docs/memory_sync_design.md`
- `scripts/shogun_verify_audit.sh` usage text

## Recommended Action Plan

### P0: Immediate Gate

Owner: Karo + Shogun
Effort: small

Before any completion report, run:

```bash
bash scripts/shogun_verify_audit.sh <audit_id>
```

If the audit entry is absent or `shogun_verified=false`, the report must say blocked, not done.

### P0: Cross-PC Report Arrival Gate

Owner: SecondPC Karo + MainPC Karo
Effort: small

SC must commit/push or otherwise transfer:

- `queue/reports/naomasa_secondpc_report.yaml`
- `queue/reports/acha_secondpc_report.yaml` if relevant
- associated logs or commit hashes

MC must not verify until `git status`/file mtime confirms arrival.

### P1: Verification Preflight Script

Owner: Ashigaru under Karo
Effort: medium

Add `--preflight` to `scripts/shogun_verify_audit.sh` that checks:

- audit entry exists
- report schema is supported or normalized
- report file contains target
- top verdict is not `partial`
- `commit_hash` is valid or explicitly exempt with reason
- `log_path` exists
- related files exist

### P1: Report Schema Normalizer

Owner: Gunshi + Ashigaru under Karo
Effort: medium

Add a normalizer, either inside `scripts/shogun_verify_audit.sh` or as `scripts/normalize_audit_reports.py`, that converts SC/MC variants into:

```yaml
reports:
  - audit_id: ...
    target_id: ...
    verdict: ...
    audited_at: ...
    related_files: [...]
    commit_hash: ...
    log_path: ...
```

This should be run before verification and should emit a warning when it had to read legacy sections.

### P1: Completion Gate Summary

Owner: Karo
Effort: small

Create `queue/reports/completion_gate_status.yaml` with one row per active audit target.

### P1: Partial Verdict Normalization

Owner: Karo + Gunshi
Effort: small

Normalize:

- `partial` due to environment = `blocked_verification`
- `partial` due to failed test = `failed`
- `partial` due to missing evidence = `missing_evidence`

### P2: Memory Sync Implementation

Owner: Karo + Gunshi council
Effort: medium

Implement the helper proposed in `docs/memory_sync_design.md`. Start with `export`, `validate`, and `diff`; delay `apply` until review.

## SLA Proposal

- Audit report written: immediate local inbox to Karo.
- Cross-PC report sync: within 10 minutes of SC audit completion.
- MC verification: within 10 minutes after report arrival.
- If not verifiable within 20 minutes: mark `blocked_verification` and notify Karo.

## Final Recommendation

Adopt a strict phrase rule:

**No local evidence, no completion. No full tests, no audited_done. No cross-PC report arrival, no MC verification. No canonical report schema, no automated verification.**

This aligns with zero polling loops because each gate is triggered by existing inbox/report events, not background scanning.
