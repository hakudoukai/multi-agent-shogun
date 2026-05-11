# Final Solution Synthesis 2026-05-11

## Executive Decision Request

Approve a **completion-gate refactor** for the current 10-agent MainPC formation:

1. Canonicalize audit report schema.
2. Add a verification preflight and report normalizer.
3. Add a completion gate status table.
4. Normalize `partial` into evidence states, not a terminal verdict.
5. Start cross-PC sync event-triggered, and evaluate richer background mechanisms by functional value and side effects.
6. Enforce the top-level rule: **all recurring mistakes must be prevented by mechanism, not by attention or self-assertion.**

This addresses:

- `partial` verdict stuck
- cross-PC audit log absence
- Shogun verification gaps
- optimistic completion language
- verify script schema mismatch
- unstarted cycle2 fix loop
- reliance on human declarations such as `commit_assertion` or "will be careful"

## Integrated Root Cause

The root cause remains:

**Completion is not gated by locally verifiable evidence.**

The supporting defects are:

- audit reports have multiple schemas across MC/SC
- `partial` is used as a verdict instead of an evidence state
- Shogun verify is available but not a blocking state transition
- cross-PC report arrival is not a prerequisite for MC verification
- summaries are prose-first instead of gate-table-first

## V2 Mechanism Hardening

The v2 refinement adopts the Lord's top-level principle:

**Every mistake must be prevented by improving the mechanism.**

Implications:

- `commit_assertion`, self-reflection, and "I will be careful" are not evidence.
- third-party review is useful only as input to mechanical checks.
- completion status must be computed from normalized fields and gate files, not prose.
- violations must become `completion_gate: blocked` automatically.

Naomasa's self-reflection is useful only for the four mechanism inputs below:

1. `partial` detection must force a hard mapping, not silent rounding.
2. generated instructions and task YAML templates must require the three-axis fields.
3. `completion_gate_status.yaml` must become the primary gate before summaries.
4. `10_ecosystem_coherence` must be mandatory for cross-PC, report-schema, and memory-sync audits.

## V2.1 Command Routing Hardening

The v2.1 supplement prevents three Shogun-side judgment failures by making command intent and cross-PC routing machine-checkable:

- interpreting `partial` and issuing immediate directives
- bypassing Ieyasu / SecondPC command authority
- launching MC and SC implementation in parallel without a recorded reason
- issuing ambiguous directives without execution order, dependency, SLA, or start trigger

These are not style problems. They are missing mechanism problems.

### V2.1-1: Command PC Priority Fields

Add required fields to every new `queue/shogun_to_karo.yaml` command:

```yaml
pc_priority: sc_first | mc_first | parallel
pc_priority_reason: "required when pc_priority=parallel"
implementation_pc: mc_only | sc_only | both
implementation_pc_reason: "required when implementation_pc=both"
```

Gate:

- missing `pc_priority` = `cmd_schema_violation`
- missing `implementation_pc` = `cmd_schema_violation`
- `pc_priority: parallel` without `pc_priority_reason` = `cmd_schema_violation`
- `implementation_pc: both` without `implementation_pc_reason` = `cmd_schema_violation`
- any `cmd_schema_violation` blocks dispatch before Karo decomposes work

Implementation path:

- extend `queue/shogun_to_karo.yaml` schema comments and future command template
- add `scripts/validate_cmd_schema.py`
- call the validator from Karo's "new cmd intake" path before task creation
- add a lightweight test fixture set under `scripts/test_validate_cmd_schema.py`

### V2.1-2: MC -> SC Directive Gate

MC must not send operational directives directly to SC Karo / Honda / SC agents.

Allowed cross-PC path:

```text
MC Shogun -> MC Karo -> Ieyasu / SecondPC Shogun channel -> SC Karo -> SC agents
```

Blocked paths:

- MC Shogun -> SC Karo direct directive
- MC Karo -> SC Ashigaru direct task assignment
- MC Gunshi -> SC execution directive
- any cross-PC `inbox_write` that bypasses the SecondPC Shogun authority layer

Implementation path:

- add `scripts/validate_cross_pc_directive.py`
- wrap Supabase / pc_handshake sending helpers with this validator
- require fields: `source_pc`, `source_agent`, `target_pc`, `target_agent`, `directive_type`, `via_agent`
- if `source_pc=main_pc` and `target_pc=second_pc`, require `via_agent=second_pc.shogun`
- write blocked attempts to `queue/reports/directive_gate_log.yaml`

This preserves the existing hierarchy while making bypass physically harder.

### V2.1-3: Simultaneous Implementation Justification Gate

When `implementation_pc: both`, Karo must obtain Gunshi review before dispatch.

Required review row:

```yaml
simultaneous_implementation_review:
  cmd_id: cmd_...
  reviewed_by: gunshi
  verdict: pass | fail
  reason: ...
  duplicate_work_risk: low | medium | high
  ownership_split:
    mc: ...
    sc: ...
```

Gate:

- `implementation_pc: both` without review row = blocked
- review verdict != pass = blocked
- missing ownership split = blocked

Implementation path:

- add `queue/reports/simultaneous_implementation_reviews.yaml`
- extend `scripts/validate_cmd_schema.py` to check for a pass review when `implementation_pc=both`
- Karo must request Gunshi review before assigning MC+SC implementation tasks

### V2.1-4: Shogun Dashboard Read Gate

Shogun must read the primary gate state before issuing completion language or new directives derived from ongoing work.

Required pre-directive inputs:

```yaml
dashboard_read_gate:
  cmd_id: cmd_...
  read_by: shogun
  dashboard_checked_at: ...
  completion_gate_status_checked: true
  unresolved_action_required_count: 0
  blocking_rows: []
```

Gate:

- missing dashboard read record = blocked
- unresolved action-required item = blocked
- `completion_gate_status_checked` not true = blocked
- blocking rows present = blocked unless the directive is explicitly a repair directive for those rows

Implementation path:

- add `queue/reports/shogun_dashboard_read_gate.yaml`
- extend `scripts/validate_cmd_schema.py` or add `scripts/validate_shogun_directive_preflight.py`
- require this gate before Shogun/Karo emits completion summaries or new directives from audit results

This prevents Shogun from relying on memory, confidence, or a stale mental model instead of the live operational state.

### V2.1-5: Shogun Directive Preflight

Before Shogun or Karo issues a directive generated from an audit result, the directive must pass preflight:

```bash
bash scripts/shogun_verify_audit.sh --preflight <audit_id>
python3 scripts/validate_cmd_schema.py queue/shogun_to_karo.yaml --cmd <cmd_id>
python3 scripts/validate_cross_pc_directive.py <directive.yaml>
```

Rules:

- `partial_verdict_blocked` forbids immediate implementation directive
- `missing_audit_entry`, `unsupported_report_schema`, or `missing_log_or_commit` require evidence repair first
- cross-PC target requires Ieyasu / SecondPC Shogun mediation
- `both` implementation requires Gunshi pass review
- dashboard read gate must be open before non-repair directives

### V2.1-6: Execution Strategy / Dependency / SLA Gate

Add required execution fields to every new command and every decomposed task:

```yaml
execution_strategy: parallel | sequential | staged
tasks:
  - task_id: ...
    dependencies: []
    sla:
      first_action_within: ...
      final_deadline: ...
    start_trigger: immediate | dependencies_done | lord_approval | gate_open
```

Command-level gate:

- missing `execution_strategy` = `template_violation`
- `execution_strategy: sequential` without ordered task list = `template_violation`
- `execution_strategy: staged` without stage names and gate criteria = `template_violation`
- `execution_strategy: parallel` with dependencies that imply ordering = `template_violation`

Task-level gate:

- missing `dependencies` array = `template_violation`
- missing `sla.first_action_within` = `template_violation`
- missing `sla.final_deadline` = `template_violation`
- missing `start_trigger` = `template_violation`
- `start_trigger: dependencies_done` with empty dependencies = `template_violation`

Effect:

- any `template_violation` sets `completion_gate: blocked`
- Karo must not infer sequential vs parallel from prose
- Ashigaru must not self-start staged work until `start_trigger` is satisfied
- pending blocked tasks remain in `queue/tasks/pending.yaml`, not pre-assigned to Ashigaru

Implementation path:

- extend `scripts/validate_cmd_schema.py`
- add `scripts/validate_task_template.py`
- add schema comments to `queue/shogun_to_karo.yaml`
- enforce pending blocked task placement in Karo dispatch rules
- add fixture tests for parallel/sequential/staged commands and dependency-trigger mismatch

### Upstream Fit

This is compatible with upstream `yohey-w/multi-agent-shogun` because the change preserves the core model:

- Shogun writes command intent
- Karo decomposes and dispatches
- Ashigaru execute
- Gunshi reviews
- event-driven inbox remains the communication primitive

The additions are local safety gates for a two-PC fork. They do not require a new always-on manager. They encode command metadata and reject unsafe routing before work begins.

### Shogun Output Style Fit

The required fields also discipline Shogun's output style:

- state PC priority explicitly
- state implementation scope explicitly
- state why parallelism is justified
- state execution strategy, dependencies, SLA, and start trigger explicitly
- avoid imperative directives when evidence is not verified
- record mechanism output instead of personal confidence

## External Pattern Review

| Source | Useful Pattern | Adopt | Reject / Avoid |
|---|---|---|---|
| wshobson PluginEval | 10 dimensions, quality badges, anti-pattern/rubric thinking | Add `ecosystem_coherence` as a conditional 10th lens: mandatory for cross-PC/report-schema/memory-sync audits, optional elsewhere; use badges only for display | Do not make badge names terminal state |
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
    source_verdict: ...
    normalization_reason: ...
```

It must understand:

- canonical `reports: [...]`
- `new_project_audits`
- `phase_b_reaudits`
- legacy named blocks

Hard rules:

- if source verdict is `partial`, output `verdict: fail`
- map the cause to `evidence_state` such as `blocked_env`, `missing`, `schema_unsupported`, or `cross_pc_missing`
- set `completion_gate: blocked` until the evidence is complete and Shogun verification is true
- never coerce `partial` into `pass_with_concerns`

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

Hard rule:

- Karo completion summary cannot be issued unless this table exists and the target row has `completion_gate: open`

### P0-4: Generated Instruction / Task Template Gate

Paths:

- `instructions/common/task_flow.md`
- `instructions/generated/codex-karo.md`
- `instructions/generated/codex-gunshi.md`
- `queue/tasks/*.yaml` templates

Required fields for audit-capable tasks:

```yaml
verdict: pass | pass_with_concerns | fail
evidence_state: complete | blocked_env | missing | schema_unsupported | cross_pc_missing
completion_gate: open | blocked
test_evidence:
  command: ...
  passed: ...
  failed: ...
  skipped: ...
shogun_verified: false
```

Preflight rule:

- missing fields = `template_violation`
- `template_violation` = `completion_gate: blocked`
- skipped tests > 0 = `evidence_state: blocked_env` or `fail`, never complete

### P0-5: Primary Gate File

`queue/reports/completion_gate_status.yaml` outranks dashboard summaries.

Dashboard is display data. Completion gate status is operational truth.

Before Karo writes completion language, the mechanism must check:

- target row exists
- normalized report exists
- `verdict != fail`
- `evidence_state: complete`
- `completion_gate: open`
- `shogun_verified: true`

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

Add conditional 10th lens:

```yaml
10_ecosystem_coherence: pass | concerns | fail
```

Use it as mandatory for cross-PC, report-schema, and memory-sync questions. Keep it optional for ordinary single-repo code audits.

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
| P0 | generated instruction / task template gate | Karo + ashigaru under Karo | medium |
| P0 | make completion gate status the primary operational gate | Karo | small |
| P1 | update vocabulary in memory/instructions | Karo + Shogun approval | small |
| P1 | memory sync helper first three commands | ashigaru under Karo, Gunshi design review | medium |
| P2 | ecosystem coherence lens | Gunshi | small |
| P2 | cross-PC transfer hash/PII gate | Karo + SecondPC Karo | medium |
| P2 | background worker / trust scoring evaluation gate | Gunshi + Karo | small |

## Final Proposed Rule

**No canonical report, no verification. No verification, no completion. No full test evidence, no audited_done. No mechanism, no trust.**

This is compatible with upstream shogun philosophy because the first fix remains evidence-gated and event-driven while leaving room for useful extensions:

- Karo as coordinator
- Gunshi as advisor/auditor
- event-driven inbox flow for the P0 implementation
- no unbounded polling loops
- no unobservable always-on manager layer
- background workers or trust scoring only after passing the value-and-side-effects gate

## Lord Approval Items

1. Approve P0 implementation.
2. Approve `ecosystem_coherence` as mandatory for cross-PC/report-schema/memory-sync audits and optional elsewhere.
3. Approve that `partial` is not a terminal verdict.
4. Approve creation of `audit_report_index.yaml` and `completion_gate_status.yaml`.
5. Approve that future background workers/trust scoring may be considered when they pass the value-and-side-effects gate.
6. Approve that `commit_assertion` and self-reflection are non-evidence; only mechanism outputs can open the completion gate.
