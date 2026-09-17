# ebb0e8ad SecondPC receiver routing repair — acceptance record

- Measured/final verification: `2026-09-09T04:10:03+09:00` (SecondPC shell clock)
- Isolated worktree: `/tmp/hakudokai-worktrees/ebb0e8ad-origin-main-receiver-map`
- Base: `origin/main` = `d5630faff995b0f4693283beb3a3f0fc9f69105b`
- Scope: `shim/hakudokai/hakudokai_secondpc_receiver_poll.py`, receiver tests only. No receiver service restart, no production DB write, no read/ACK mutation, no Windows operation.

## Direct live observation (read-only)

At 04:03 JST the active tmux user options were:

- `karo-second:0.0|karo-second`
- `multiagent-second:0.0|ashigaru-second-1`
- `multiagent-second:0.1|ashigaru-second-3`
- `multiagent-second:0.2|ashigaru-second-2`
- `hermes-gunshi-second:0.0|gunshi-second`

This confirms the old hard-coded `karo-second -> multiagent-second:0.0` points at the wrong live identity, and legacy `gunshi-second -> multiagent-second:0.8` has no active pane.

## Repair and acceptance

1. Worker mapping uses current tmux `@agent_id` identity, never a fixed pane index. Current aliases map only to existing active worker identities.
2. Dedicated downlink targets `gunshi-second`, `honbucho`, and `dr-s` are excluded from generic receiver delivery. Their source row is not written, retried, or ACK-mutated; a local `delivery_failed` record is retained and a once-per-row sender notice is attempted.
3. Retry-cap failure preserves the original handshake ACK and records local `delivery_failed`; it returns a sender failure notice rather than `acknowledged_by=dead_letter`.
4. Invalid target remains a local dead-letter with the established one-time escalation, but original handshake ACK fields are not PATCHed.
5. Negative controls cover downlink-owned target, invalid target, existing retry-cap behavior, and legacy unroutable one-time notice behavior.

## Evidence

```text
python3 -m pytest -q tests/test_ebb0e8ad_receiver_routing.py tests/test_watcher_hotfix.py tests/test_ff5c9068_unroutable_notice_dedupe.py
15 passed in 0.45s
python3 -m py_compile shim/hakudokai/hakudokai_secondpc_receiver_poll.py
RC=0
git diff --check origin/main...HEAD
RC=0
```

- Fixed commit: `65ed90074e93ef734669929e92d590b856d4fa42`
- Fixed tree: `67855ec0cfbef6895d4821100a4f9b5c337bc493`
- Worktree porcelain after commit: empty


- New acceptance test: `tests/test_ebb0e8ad_receiver_routing.py` (5 cases).
- Existing receiver regression tests updated only where the former false-ACK retry-cap expectation contradicted this task's approved acceptance condition.
- Rollback before deployment: discard the isolated branch/worktree. No running unit has been changed.
