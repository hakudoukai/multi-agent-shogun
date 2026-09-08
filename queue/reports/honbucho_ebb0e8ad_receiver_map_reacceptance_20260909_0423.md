# ebb0e8ad receiver routing — reacceptance after independent-audit REVISE

- Time: `2026-09-09T04:22:34+09:00` (SecondPC shell clock)
- Prior fixed revision: `f3415522295cbe682f24ab66f2017b20b6c4c4d5`
- Audit finding: the retry-cap regression fixture incorrectly allowed an inherited delivery-notice marker to suppress the sender-facing failure notice. It contradicted the target-specific contract: original ACK is never mutated, but one sender-facing `receiver_delivery_failed` notice is emitted.

## Narrow correction

`tests/test_watcher_hotfix.py::TestSecondpcReceiverRetry::test_retry_cap_dead_letters` now isolates both delivery-state fixture paths and asserts:

1. the original source row is not recorded as delivered;
2. the source request has no `acknowledged_by` mutation;
3. exactly the non-mutating `receiver_delivery_failed` sender notice is posted.

No receiver runtime, live DB, original ACK/read state, systemd unit, or Windows process was changed.

## Re-run evidence

```text
python3 -m pytest -q tests/test_ebb0e8ad_receiver_routing.py tests/test_watcher_hotfix.py tests/test_ff5c9068_unroutable_notice_dedupe.py
15 passed
python3 -m py_compile shim/hakudokai/hakudokai_secondpc_receiver_poll.py
RC=0
git diff --check origin/main...HEAD
RC=0
```

The implementation scope remains: identity-based worker pane resolution, dedicated-downlink exclusion, retry-cap ACK nonmutation with separate local failure state, and invalid-target negative control. This correction is sent for a single re-audit, as required by `seq293829`.
