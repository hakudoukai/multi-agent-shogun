---
name: codex-exec-sandbox-guard
description: agentic CLI (codex exec 等) を監査/read-only目的で起動する前に sandbox 隔離を検証し、未検証なら停止する (live repo 書込 near-miss 再発防止)
---

# Codex exec sandbox guard

> ★DRAFT★ — §19 lessons capture (incident: 2026-07-21 Codex audit live-repo write near-miss)。commit は理事長殿明示承認後のみ。

## いつ使う (= mandatory)

- `scripts/audit_codex.sh` / `npx @openai/codex exec` など **agentic CLI を「監査/read-only」目的で起動する直前**。
- 三者監査 gate で Codex leg を回す前。
- 他の agentic coding CLI (write 権限を持つもの) を隔離前提で起動する時。

## 使わない

- 純粋な read-only コマンド (grep/git diff 単体等) の実行前。
- agentic CLI を「意図的に repo を編集させる」正規タスク (このskillは監査/read-only用途限定)。

## 手順

1. **halt フラグ確認**: 信長 SAFETY 裁定 (2026-07-21) により、★検証済 sandbox が確立するまで当PC の Codex exec 実行は全面停止★。`scripts/checks/codex_exec_sandbox_guard.sh` が halt を検知したら **起動しない** (Codex leg = documented 扱いへ)。
   - ★halt 解除は env 変数単独で行わない (§19検分finding是正)★: env 1行での解除は lane A v7 で撤去した CODEX_BYPASS_APPROVALS_SANDBOX opt-in と同型の自己供給 bypass (改竄痕跡なし) で F-LA-1 原則に反する。解除は ★改竄痕跡の残る理事長GO記録file (固定path・実在+内容検証)★ で成立させる。
   - ★本記録file の設定/配置は理事長GO発令後に上位のみが行う。agent の自己設定/自己配置 = D-lane違反★ (推奨=root所有・agent書込不可path=lane A 人間鍵配備要件と同思想)。
2. **cwd 検証**: codex exec を live repo (`~/projects/multi-agent-shogun` 等) の cwd で起動しない。cwd が live repo なら停止。
3. **絶対path書込封じ確認**: cwd 隔離だけでは絶対path書込を防げない (incident の教訓)。filesystem write を封じた検証済 sandbox (network/fs 制約) 内でのみ起動。sandbox 未確立なら起動しない (fail-closed)。
4. **無効出力時の判定**: Codex verdict が無効出力 (非JSON/空) の時は persona 汚染と即断せず、まず `/tmp/codex_audit_*_log` の `apply_patch` エラーを確認。live-repo 書込試行なら raw 保全 + SAFETY 上申 + Codex leg documented 扱い。
5. **有効JSON産出時も**: 書込試行の観測がなくても機構 risk は同一ゆえ、close報/監査記録に機構 risk を併記開示。

## 再発防止の infra 側 (理事長GO/横断発令対象・本skill範囲外)

- `audit_codex.sh` の codex exec を検証済 sandbox 内 + 非live cwd 強制へ是正 (艦隊共有 infra・独断改修禁)。

## 関連

- incident: `docs/incident_logs/2026-07-21_codex-audit-live-repo-write.md`
- check: `scripts/checks/codex_exec_sandbox_guard.sh`
- memory: `codex-audit-live-repo-write-risk`
- 全艦隊 SAFETY 上申: seq132707/id=035e283b
