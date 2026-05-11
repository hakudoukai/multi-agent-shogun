# Supabase verification_events Fallback Design

## Purpose

Option A prime keeps cross-PC Shogun verification evidence in PC-suffixed git-tracked logs plus a generated canonical index. This fallback makes a stronger conflict-resistant path ready if git-based evidence sharing proves unstable.

Use Supabase `verification_events` only when there is clear failure evidence. It is heavier than git, but it provides native cross-PC writes, server-side uniqueness, centralized audit history, and deterministic snapshot generation.

## Activation Triggers

Activate this fallback only when at least one of these conditions is true:

- Three or more merge conflicts occur in verification log or generated index files within 24 hours.
- Privacy validator fails to reliably block absolute paths, secrets, patient identifiers, clinic identifiers, or raw exception bodies.
- Canonical git index disagrees between MainPC and SecondPC twice for the same `target_id`.
- Writer ownership is violated twice, meaning a PC writes to the other PC's suffix log.
- Completion gate blocks because one PC cannot pull the counterpart verification log within the SLA.
- Shogun or Karo explicitly declares `verification_events_fallback_required: true` after incident review.

Do not activate because of a single transient git failure. The fallback changes the authoritative storage layer and should be treated as `cmd_014`, not an ad hoc hotfix.

## Table Schema

Preferred table: `public.verification_events`.

```sql
create table if not exists public.verification_events (
  event_id text primary key,
  source_pc text not null check (source_pc in ('main_pc', 'second_pc')),
  target_id text not null,
  verified_at timestamptz not null,
  shogun_verified boolean not null,
  checks_passed text not null,
  payload_hash text not null check (payload_hash ~ '^[a-f0-9]{64}$'),
  redacted_payload jsonb not null,
  created_at timestamptz not null default now(),
  unique (source_pc, target_id, verified_at, payload_hash)
);

create index if not exists verification_events_target_idx
  on public.verification_events (target_id, verified_at desc);

create index if not exists verification_events_source_idx
  on public.verification_events (source_pc, created_at desc);
```

`event_id` should be deterministic:

```text
ve_<source_pc>_<target_id_slug>_<verified_at_utc_compact>_<payload_hash_12>
```

The `redacted_payload` may include only:

- `audit_id`
- `target_id`
- `source_pc`
- `auditor_who`
- `verified_at`
- `shogun_verified`
- `checks_passed`
- `checks`
- `flags_redacted`
- `commit_hash`
- `payload_hash`

It must not include raw `log_path`, absolute local paths, secrets, `.env` fragments, patient identifiers, clinic identifiers, or raw exception bodies.

## RLS Policy

Enable RLS and split read/write responsibilities by source PC.

```sql
alter table public.verification_events enable row level security;

create policy verification_events_read_all_pcs
on public.verification_events
for select
using (
  current_setting('request.jwt.claims', true)::jsonb ->> 'role' in ('service_role', 'authenticated')
);

create policy verification_events_insert_main_pc
on public.verification_events
for insert
with check (
  source_pc = 'main_pc'
  and current_setting('request.jwt.claims', true)::jsonb ->> 'role' = 'service_role'
);

create policy verification_events_insert_second_pc
on public.verification_events
for insert
with check (
  source_pc = 'second_pc'
  and current_setting('request.jwt.claims', true)::jsonb ->> 'role' = 'service_role'
);
```

If both PCs share one service role key, RLS cannot distinguish device identity by itself. In that case the helper script must enforce `source_pc` from `config/settings.yaml` or `HAKUDOKAI_PC_ID`, and the table should still keep RLS enabled for read/write boundary documentation. A stronger future version should use per-PC service accounts or Edge Function wrappers.

## Insert API Path

Reuse the existing Supabase REST pattern from `scripts/sync_to_supabase.sh`:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `POST /rest/v1/verification_events?on_conflict=event_id`
- `Prefer: resolution=merge-duplicates,return=minimal`

Proposed one-shot helper:

```text
shim/hakudokai/hakudokai_verification_events.py
```

Commands:

- `validate-log --in queue/reports/shogun_verification_mainpc_log.yaml`
- `import-log --source-pc main_pc --in queue/reports/shogun_verification_mainpc_log.yaml --dry-run`
- `push-event --source-pc main_pc --event-json /tmp/verification_event.json`
- `pull-index --out queue/reports/verification_events_index.yaml`
- `diff-index --local queue/reports/verification_events_index.yaml`

The helper must be one-shot. No daemon and no polling loop are introduced. Delivery continues through inbox, `pc_handshake`, SSH direct notice, or explicit Karo task.

## Generated Snapshot Pattern

Repo-side generated snapshot:

```text
queue/reports/verification_events_index.yaml
```

This file should be git tracked and generated from Supabase by:

```text
scripts/sync_verification_events.py
```

Snapshot shape:

```yaml
generated_at: "2026-05-11T10:21:38+09:00"
source: supabase.verification_events
events:
  - event_id: ve_main_pc_cmd012_20260511T012138Z_abcdef123456
    source_pc: main_pc
    target_id: cmd012_p01_normalize_audit_reports_cycle2
    verified_at: "2026-05-11T01:21:38Z"
    shogun_verified: true
    checks_passed: "5/6"
    payload_hash: "..."
completion_view:
  cmd012_p01_normalize_audit_reports_cycle2:
    main_pc_verified: true
    second_pc_verified: false
    latest_verified_at: "2026-05-11T01:21:38Z"
    completion_gate: blocked_waiting_second_pc
```

The snapshot is a generated view, not the write source. Merge conflicts in the snapshot are resolved by regenerating from Supabase.

## Migration Path

1. Freeze Option A prime writers during migration.
2. Run privacy validator against:
   - `queue/reports/shogun_verification_mainpc_log.yaml`
   - `queue/reports/shogun_verification_secondpc_log.yaml`
3. Convert each log entry into a `verification_events` row.
4. Reject or redact entries containing absolute paths, secrets, patient/clinic identifiers, or raw exception text.
5. Import with deterministic `event_id`; duplicate imports must be idempotent.
6. Pull `queue/reports/verification_events_index.yaml` from Supabase.
7. Compare event counts and payload hashes against source logs.
8. Update `completion_gate_status.yaml` to read `verification_events_index.yaml`.
9. Mark PC-suffixed git logs as archived/read-only or keep them as local raw evidence excluded from completion gate.

## cmd_014 Acceptance Criteria Draft

All conditions must be true before `cmd_014` can be marked done:

- SQL migration for `verification_events` exists and is reviewed.
- RLS is enabled; read policy and insert boundary are documented.
- `hakudokai_verification_events.py` or equivalent helper supports validate, import dry-run, push, pull-index, and diff-index.
- `scripts/sync_verification_events.py` generates `queue/reports/verification_events_index.yaml`.
- Generated snapshot is git tracked and contains no raw absolute paths, secrets, patient identifiers, clinic identifiers, or raw exception bodies.
- Import from existing PC-suffixed logs is idempotent and duplicate-safe.
- Tests cover duplicate `event_id`, invalid `source_pc`, redaction failure, network failure, Supabase conflict, and snapshot regeneration.
- `completion_gate_status.yaml` can consume `verification_events_index.yaml`.
- No background polling loop is added.
- SKIP count is zero in the test report.

## Owner Plan

- Shogun: approve fallback activation only after trigger evidence is present.
- Karo: open `cmd_014`, assign implementation, and enforce no-polling discipline.
- Ashigaru implementation owner: SQL migration, helper script, sync script, and tests.
- Gunshi: audit schema, redaction rules, migration results, and completion gate semantics.
- SecondPC Karo/Ieyasu: verify source_pc enforcement and read access from SecondPC.

Estimated effort:

- SQL + RLS migration: small.
- Helper + REST insert/pull: medium.
- Redaction validator integration: medium.
- Snapshot generation and completion gate integration: medium.
- Cross-PC migration verification: medium to large.

## Recommendation

Keep Option A prime as the first implementation. Prepare this fallback as `cmd_014` but do not activate it without trigger evidence. Supabase is justified only when git-based verification sharing repeatedly fails or privacy/index correctness cannot be guaranteed with PC-suffixed logs.
