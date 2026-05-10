# Final Solution Synthesis 2026-05-11

## Executive Decision Request

Approve a **completion-gate refactor** for the current 10-agent MainPC formation:

1. Canonicalize audit report schema.
2. Add a verification preflight and report normalizer.
3. Add a completion gate status table.
4. Normalize `partial` into evidence states, not a terminal verdict.
5. Start cross-PC sync event-triggered, and evaluate richer background mechanisms by functional value and side effects.

This addresses:

- `partial` verdict stuck
- cross-PC audit log absence
- Shogun verification gaps
- optimistic completion language
- verify script schema mismatch
- unstarted cycle2 fix loop

## Integrated Root Cause

The root cause remains:

**Completion is not gated by locally verifiable evidence.**

The supporting defects are:

- audit reports have multiple schemas across MC/SC
- `partial` is used as a verdict instead of an evidence state
- Shogun verify is available but not a blocking state transition
- cross-PC report arrival is not a prerequisite for MC verification
- summaries are prose-first instead of gate-table-first

## External Pattern Review

| Source | Useful Pattern | Adopt | Reject / Avoid |
|---|---|---|---|
| wshobson PluginEval | 10 dimensions, quality badges, anti-pattern/rubric thinking | Add `ecosystem_coherence` as optional 10th review lens; use badges only for display | Do not make badge names terminal state |
| ruvnet/ruflo | audit trail both sides, federation trust, PII stripping before outbound data, optional worker/scoring mechanisms | Adopt bidirectional audit trail and PII/redaction gate now; evaluate trust scoring/background workers when they solve a concrete failure mode | Avoid continuous workers only when value, cost bounds, observability, and rollback are unclear |
| catlog22 workflow-test-fix-cycle | generated test sessions, iterative fix loop, pass-rate gate | Adopt bounded test-fix cycle with max iterations and artifacts | Do not run autonomous unbounded fix loops |
| gstack ship/release workflow | sync/test/push/PR/deploy/verify sequence | Adopt non-negotiable ship gate sequence | Do not import a separate release bureaucracy |
| CrewAI hierarchical process | manager delegates and validates outcomes | Karo/Honda should coordinate; validation must be explicit | Do not let manager narrative replace evidence gates |

Sources:

- PluginEval evaluation methodology: https://www.claudepluginhub.com/skills/wshobson-plugin-eval-plugins-plugin-eval/evaluation-methodology
- ruflo federation/audit trail README: https://github.com/ruvnet/ruflo/blob/main/README.md
- catlog22 workflow-test-fix-cycle: https://playbooks.com/skills/catlog22/claude-code-workflow/workflow-test-fix-cycle
- gstack ship workflow overview: https://www.dench.com/blog/gstack-ship-workflow
- CrewAI hierarchical process: https://docs.crewai.com/en/learn/hierarchical-process

## Core Model

Use three separate axes:

```yaml
verdict: pass | pass_with_concerns | fail
evidence_state: complete | blocked_env | missing | schema_unsupported | cross_pc_missing
completion_gate: open | blocked
```

Rules:

- `partial` is not a top-level verdict.
- test unavailable = `evidence_state: blocked_env`, `completion_gate: blocked`
- report absent on MC = `evidence_state: cross_pc_missing`, `completion_gate: blocked`
- unsupported report schema = `evidence_state: schema_unsupported`, `completion_gate: blocked`
- `audited_done` requires `verdict != fail`, `evidence_state: complete`, `shogun_verified: true`

## P0 Changes

### P0-1: Canonical Report Normalizer

Path: `scripts/normalize_audit_reports.py`

Input:

- `queue/reports/kuroda_mainpc_report.yaml`
- `queue/reports/takenaka_mainpc_report.yaml`
- `queue/reports/naomasa_secondpc_report.yaml`
- `queue/reports/acha_secondpc_report.yaml`

Output:

- `queue/reports/audit_report_index.yaml`

Contract:

```yaml
reports:
  - audit_id: naomasa_new_001
    source_file: queue/reports/naomasa_secondpc_report.yaml
    source_section: new_project_audits
    target_id: ...
    verdict: pass | pass_with_concerns | fail
    evidence_state: complete | blocked_env | missing | schema_unsupported | cross_pc_missing
    completion_gate: open | blocked
    shogun_verified: false
```

It must understand:

- canonical `reports: [...]`
- `new_project_audits`
- `phase_b_reaudits`
- legacy named blocks

### P0-2: Verification Preflight

Extend `scripts/shogun_verify_audit.sh`:

```bash
bash scripts/shogun_verify_audit.sh --preflight <audit_id>
```

Return:

- `ready_to_verify`
- `missing_audit_entry`
- `missing_cross_pc_report`
- `unsupported_report_schema`
- `partial_verdict_blocked`
- `missing_log_or_commit`

### P0-3: Completion Gate Table

Path: `queue/reports/completion_gate_status.yaml`

Rows:

```yaml
targets:
  - audit_id: naomasa_new_001
    present_on_mc: true | false
    verdict: pass | pass_with_concerns | fail | unknown
    evidence_state: complete | blocked_env | missing | schema_unsupported | cross_pc_missing
    shogun_verified: true | false
    completion_gate: open | blocked
    next_action: ...
```

Karo/Honda must read this before issuing cycle2 fix or completion summaries.

## P1 Changes

### P1-1: Memory / Rule Sync

Use `docs/memory_sync_design.md`:

- shared memory blocks only
- no raw `MEMORY.md` sync
- secret/PII scan required
- event-triggered push/pull only

### P1-2: Audit Vocabulary Update

Update `MEMORY.md` and generated instructions:

```yaml
verdict: pass | pass_with_concerns | fail
evidence_state: complete | blocked_env | missing | schema_unsupported | cross_pc_missing
completion_gate: open | blocked
```

Do not add `partial` to terminal verdict values.

### P1-3: Bounded Fix Loop

Inspired by test-fix cycle pipelines, define:

- max 7 cycles
- stop on blocked environment
- stop on unsupported schema
- escalation at cycle 7
- every iteration writes test evidence and blocker reason

## P2 Changes

### P2-1: Ecosystem Coherence Lens

PluginEval’s `ecosystem coherence` maps well to this incident.

Add optional 10th lens:

```yaml
10_ecosystem_coherence: pass | concerns | fail
```

Use it for cross-PC/report-schema/memory-sync questions. Keep the existing 9-point audit as the base.

### P2-2: Cross-PC Trust Gate

Borrow from federation patterns, but keep it simple:

- report source must be PC-suffixed
- report hash must match after transfer
- PII/secret scan before outbound sync
- every cross-PC transfer appends an audit record

No mTLS/federation daemon is needed for the current local two-PC formation. If identity drift, report spoofing, or trust decay appears in evidence, evaluate a richer trust mechanism through the worker gate below.

### P2-3: Background Worker Evaluation Gate

Background workers and automated trust scoring are not rejected by slogan. They are acceptable when they answer these checks:

- What concrete failure mode does the mechanism prevent?
- Is the trigger event-based, scheduled, or continuous, and why is that cadence necessary?
- What are the maximum runtime, retry count, and backoff rules?
- Where is the audit trail written?
- How is the worker stopped, rolled back, or disabled?
- What human-visible health signal proves it is working?

If these answers are strong, the mechanism is useful architecture, not wasteful layering.

## Owner Plan

| Priority | Work | Owner | Effort |
|---|---|---|---|
| P0 | normalize audit reports | ashigaru under Karo, reviewed by Gunshi | medium |
| P0 | `--preflight` verify mode | ashigaru under Karo | medium |
| P0 | completion gate table | Karo | small |
| P0 | block completion when evidence unavailable | Shogun + Karo | small |
| P1 | update vocabulary in memory/instructions | Karo + Shogun approval | small |
| P1 | memory sync helper first three commands | ashigaru under Karo, Gunshi design review | medium |
| P2 | ecosystem coherence lens | Gunshi | small |
| P2 | cross-PC transfer hash/PII gate | Karo + SecondPC Karo | medium |
| P2 | background worker / trust scoring evaluation gate | Gunshi + Karo | small |

## Final Proposed Rule

**No canonical report, no verification. No verification, no completion. No full test evidence, no audited_done.**

This is compatible with upstream shogun philosophy because the first fix remains evidence-gated and event-driven while leaving room for useful extensions:

- Karo as coordinator
- Gunshi as advisor/auditor
- event-driven inbox flow for the P0 implementation
- no unbounded polling loops
- no unobservable always-on manager layer
- background workers or trust scoring only after passing the value-and-side-effects gate

## Lord Approval Items

1. Approve P0 implementation.
2. Decide whether `ecosystem_coherence` becomes mandatory or optional.
3. Approve that `partial` is not a terminal verdict.
4. Approve creation of `audit_report_index.yaml` and `completion_gate_status.yaml`.
5. Approve that future background workers/trust scoring may be considered when they pass the value-and-side-effects gate.
