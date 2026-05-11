# Background Worker Evaluation Gate

## Purpose

Background workers and automated trust scoring are not accepted or rejected by slogan.
They are approved only when they prevent a concrete failure mode and can be bounded,
observed, audited, and disabled.

This gate applies before adding any new daemon, watcher, scheduler, retry loop, or
automated trust scorer to the multi-agent system. It is especially relevant for:

- cross-PC report transfer and verification
- inbox delivery and escalation
- ntfy phone input
- audit report normalization and completion gates
- memory sync and instruction propagation

The current system already has acceptable worker patterns. `scripts/inbox_watcher.sh`
uses file-change events rather than a polling loop, writes metrics, and throttles
nudge delivery. `scripts/ntfy_listener.sh` uses the ntfy streaming endpoint, writes
incoming messages atomically, and reconnects after a dropped stream. These are useful
workers because their purpose, trigger, audit trail, and recovery behavior are explicit.

## Evaluation Gate

Every proposed background worker or automated trust scorer must answer all six
questions below. A worker may be implemented only when all required answers are
specific enough to test.

| # | Question | Pass condition | Fail condition |
|---|---|---|---|
| 1 | What concrete failure mode does it prevent? | Names a real observed failure, such as missed inbox wake-up, cross-PC report absence, stale completion gate, or trust spoofing. | Says only "improve reliability", "make it automatic", or "monitor everything". |
| 2 | Is the trigger event-based, scheduled, or continuous, and why is that cadence necessary? | Uses the narrowest cadence that solves the failure mode. Event-based is preferred when file, inbox, or webhook events exist. | Adds a continuous loop when an event, hook, or one-shot preflight would work. |
| 3 | What are maximum runtime, retry count, and backoff rules? | Defines max runtime, retry limit, backoff, and terminal failure behavior. | Retries forever without a cooldown, cap, or escalation path. |
| 4 | Where is the audit trail written? | Writes structured evidence to `queue/`, `logs/`, or a named report file with timestamps and result codes. | Only prints to stdout or relies on prose summary in chat. |
| 5 | How is the worker stopped, rolled back, or disabled? | Has a documented stop command, feature flag, config switch, or supervisor control. | Requires killing unknown processes or editing code live. |
| 6 | What human-visible health signal proves it is working? | Provides a dashboard row, metric file, log heartbeat, unread latency, or verification entry. | Has no observable signal until a user reports failure. |

Decision rule:

- `approve`: all six questions pass and the worker has a bounded implementation plan.
- `approve_with_concerns`: the failure mode is real, but one non-critical answer needs
  a follow-up before audited_done.
- `reject`: any answer is missing, unbounded, unobservable, or incompatible with the
  event-driven inbox model.

## Anti-Patterns

Reject these patterns unless a stronger design review explicitly overrides them.

- **Polling loop where an event exists**: repeatedly scanning `queue/inbox/*.yaml`
  instead of using `inotifywait`, a hook, or an explicit command.
- **Always-on manager without ownership**: a daemon that can modify task state but has
  no named owner, log file, or stop procedure.
- **Unbounded retry**: reconnecting or retrying forever without max runtime, backoff,
  or escalation records.
- **Narrative-only trust score**: saying a PC or agent is trusted without hashes,
  source suffixes, verification logs, or reproducible checks.
- **Silent repair**: rewriting YAML, reports, or memory without preserving the broken
  input and recording what was changed.
- **Completion by side effect**: marking a task complete because a worker ran, without
  canonical report evidence and preflight verification.

Concrete current-system risks:

- `scripts/watcher_supervisor.sh` runs a 5-second supervisor loop. This is acceptable
  only because its scope is narrow: ensure known watcher processes exist for known
  panes, then sleep. A broader "scan and fix every state" daemon would fail this gate.
- `scripts/ntfy_listener.sh` reconnects every 5 seconds after a dropped stream. This is
  acceptable for a streaming input connection, but any similar reconnect loop must
  document its auth, corrupt-file handling, audit trail, and stop procedure.
- `scripts/inbox_watcher.sh` has timeout and escalation fallback. This is acceptable
  because the primary trigger is event-driven and the fallback exists for WSL2 or CLI
  delivery edge cases, not as the primary delivery mechanism.

## Approved Patterns

Use these as reference designs.

| Pattern | Current example | Why it passes |
|---|---|---|
| Event-triggered file watcher | `scripts/inbox_watcher.sh` with `inotifywait` | Prevents missed inbox wake-ups, blocks while idle, records metrics, throttles nudges. |
| Atomic mailbox writer | `scripts/inbox_write.sh` | Uses lock + temp file + rename, caps mailbox growth, keeps message body in YAML rather than tmux input. |
| Streaming external input | `scripts/ntfy_listener.sh` | Uses ntfy streaming, writes `queue/ntfy_inbox.yaml`, backs up corrupt inbox data, reconnects after disconnect. |
| Narrow supervisor | `scripts/watcher_supervisor.sh` | Restarts only known watcher processes for known agents and logs per-agent output. |
| One-shot preflight | `scripts/shogun_verify_audit.sh --preflight <audit_id>` | Returns a bounded status code and does not become a resident worker. |

Preferred implementation order:

1. One-shot command or preflight.
2. Event-triggered hook or file watcher.
3. Scheduled worker with bounded cadence.
4. Continuous worker only when streaming or supervision is the actual requirement.

## Checklist

Use this checklist before any new worker or trust scorer is assigned.

- [ ] Failure mode is named and linked to an incident, report, or acceptance criterion.
- [ ] Existing event source was checked before proposing a loop.
- [ ] Trigger type is declared: event-based, scheduled, continuous, or one-shot.
- [ ] Cadence is justified and narrower alternatives were rejected with reasons.
- [ ] Maximum runtime is defined.
- [ ] Retry count is defined.
- [ ] Backoff and cooldown are defined.
- [ ] Terminal failure writes a structured record.
- [ ] Audit trail path is named.
- [ ] Health signal is visible to Karo or Shogun without reading raw process output.
- [ ] Stop, rollback, or disable procedure is documented.
- [ ] Secrets and PII are not written to logs or cross-PC payloads.
- [ ] The worker cannot mark completion without canonical report evidence.
- [ ] The design preserves event-driven inbox flow and does not create a polling-first path.

## Decision Record Template

```yaml
worker_eval:
  id: <worker_or_scorer_id>
  proposed_by: <agent>
  failure_mode: <specific failure prevented>
  trigger_type: event_based | scheduled | continuous | one_shot
  cadence_reason: <why this cadence is necessary>
  max_runtime_sec: <int>
  retry_count: <int>
  backoff: <policy>
  audit_trail_path: <queue/... or logs/...>
  health_signal: <dashboard row, metric, log heartbeat, verification entry>
  stop_or_disable: <command/config/feature flag>
  pii_secret_policy: <how sensitive data is excluded>
  completion_gate_interaction: <how it avoids false audited_done>
  decision: approve | approve_with_concerns | reject
  decision_reason: <short evidence-based reason>
```

## Example Decisions

```yaml
worker_eval:
  id: inbox_watcher
  failure_mode: "Unread agent inbox messages may not wake the target pane."
  trigger_type: event_based
  cadence_reason: "inotifywait wakes only on inbox file changes; timeout is fallback."
  max_runtime_sec: "resident, supervised; individual wait blocks until event or timeout"
  retry_count: "nudge throttled; escalation phases bounded by cooldown"
  backoff: "NUDGE_COOLDOWN_SEC / NUDGE_COOLDOWN_SEC_CODEX"
  audit_trail_path: "logs/inbox_watcher_<agent>.log and queue/metrics/<agent>_selfwatch.yaml"
  health_signal: "unread_latency_sec, read_count, estimated_tokens"
  stop_or_disable: "stop watcher process or disable escalation flags"
  decision: approve
  decision_reason: "Event-driven, bounded fallback, structured metrics."
```

```yaml
worker_eval:
  id: generic_completion_poller
  failure_mode: "Unknown"
  trigger_type: continuous
  cadence_reason: "Always check everything"
  max_runtime_sec: "unbounded"
  retry_count: "unbounded"
  audit_trail_path: "none"
  health_signal: "none"
  stop_or_disable: "kill process"
  decision: reject
  decision_reason: "No concrete failure mode, no audit trail, polling-first design."
```
