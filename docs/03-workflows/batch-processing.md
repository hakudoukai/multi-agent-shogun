# Batch Processing Protocol (all agents)

出典: CLAUDE.md (元「Batch Processing Protocol」節) からの移設実体 (副院長令 7de922ec 裁定、2026-06-04 Commander)。改訂責務は理事長殿の専権事項。

When processing large datasets (30+ items requiring individual web search, API calls, or LLM generation), follow this protocol. Skipping steps wastes tokens on bad approaches that get repeated across all batches.

## Default Workflow (mandatory for large-scale tasks)

```
① Strategy → 家康 review → incorporate feedback
② Execute batch1 ONLY → 信長 QC
③ QC NG → Stop all agents → Root cause analysis → 家康 review
   → Fix instructions → Restore clean state → Go to ②
④ QC OK → Execute batch2+ (no per-batch QC needed)
⑤ All batches complete → Final QC
⑥ QC OK → Next phase (go to ①) or Done
```

## Rules

1. **Never skip batch1 QC gate.** A flawed approach repeated 15 batches = 15× wasted tokens.
2. **Batch size limit**: 30 items/session (20 if file is >60K tokens). Reset session (/new or /clear) between batches.
3. **Detection pattern**: Each batch task MUST include a pattern to identify unprocessed items, so restart after /new can auto-skip completed items.
4. **Quality template**: Every task YAML MUST include quality rules (web search mandatory, no fabrication, fallback for unknown items). Never omit — this caused 100% garbage output in past incidents.
5. **State management on NG**: Before retry, verify data state (git log, entry counts, file integrity). Revert corrupted data if needed.
6. **家康 review scope**: Strategy review (step ①) covers feasibility, token math, failure scenarios. Post-failure review (step ③) covers root cause and fix verification.
