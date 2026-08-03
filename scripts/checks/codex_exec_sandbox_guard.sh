#!/usr/bin/env bash
# codex_exec_sandbox_guard.sh — Codex exec (agentic CLI) 起動前 sandbox 検証 guard
#
# ★DRAFT★ §19 lessons capture (incident 2026-07-21 Codex audit live-repo write near-miss)。
# commit は理事長殿明示承認後のみ。
#
# 目的: audit_codex.sh / npx @openai/codex exec を「監査/read-only」目的で起動する前に呼び、
#       live repo cwd + sandbox 未確立なら停止 (fail-closed)。信長 SAFETY 裁定 (2026-07-21) =
#       検証済 sandbox 確立まで当PC の Codex exec 全面停止。
#
# 使い方: bash scripts/checks/codex_exec_sandbox_guard.sh [intended_cwd]
# exit: 0=安全 (sandbox確認済で起動可) / 1=停止 (halt or live-repo-cwd or sandbox未確立) / 2=判定不能
# stderr に警告を出す。timeout 5 秒相当 (重い処理はしない)。

set -uo pipefail

INTENDED_CWD="${1:-$PWD}"

# --- (0) halt フラグ: 信長 SAFETY 裁定による全面停止 ---
# 検証済 sandbox 機構が確立し halt 解除されるまで、既定で停止する (fail-closed)。
#
# ★重要 (§19検分finding是正・信長 msg_20260721_223309)★:
# halt 解除は ★env 変数単独で成立させない★。env 1行での解除は、lane A v7 で撤去した
# CODEX_BYPASS_APPROVALS_SANDBOX opt-in と同型の「自己供給 bypass (改竄痕跡なし)」であり、
# F-LA-1 非拡大 fail-closed 原則に反する。∴解除は ★改竄痕跡の残る理事長GO記録file★ の
# 実在+内容検証で成立させる。
# ★GO記録file は理事長GO発令後に上位のみが配置する。agent 自己配置/自己設定 = D-lane違反★
# (推奨=root所有・agent書込不可の固定path。lane A の人間鍵配備要件と同思想)。
GO_RECORD="/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record"   # 固定path (env override 禁=自己供給回避)
GO_MARKER="CODEX_EXEC_SANDBOX_GO: APPROVED"   # 理事長GO発令文書が持つ期待marker
if [ ! -f "$GO_RECORD" ]; then
  echo "[codex_exec_sandbox_guard] BLOCK: halt解除の理事長GO記録file不在 ($GO_RECORD)。検証済sandbox未確立 (信長SAFETY裁定2026-07-21・seq132707)。Codex exec を起動するな=Codex leg documented扱いへ。" >&2
  exit 1
fi
if ! grep -q "$GO_MARKER" "$GO_RECORD" 2>/dev/null; then
  echo "[codex_exec_sandbox_guard] BLOCK: 理事長GO記録fileに期待marker不在=無効。halt解除不成立。" >&2
  exit 1
fi
# ★注意: 本checkはfile実在+内容のみ検証。真の改竄防止は GO_RECORD が root所有・agent書込不可path
#   に上位配置されること (agent自己配置=D-lane違反) で成立する。DRAFT段階=要件明記に留める。

# --- (1) live repo cwd 検出 ---
# 絶対path書込は cwd 隔離だけでは防げないが、live repo cwd は明確な危険サインとして停止する。
case "$INTENDED_CWD" in
  */projects/multi-agent-shogun|*/projects/multi-agent-shogun/*|*/projects/multi-agent-shogun-newbuild*)
    echo "[codex_exec_sandbox_guard] BLOCK: intended_cwd=$INTENDED_CWD は live repo。Codex exec を live repo cwd で起動するな。" >&2
    exit 1
    ;;
esac

# --- (2) sandbox 実体の最小検証 (network/fs 制約が効いているか) ---
# ここは環境の sandbox 実装に依存する placeholder。未実装なら判定不能で保守的に停止側 (exit 2→呼出側は停止扱い)。
if [ -z "${CODEX_SANDBOX_KIND:-}" ]; then
  echo "[codex_exec_sandbox_guard] WARN: CODEX_SANDBOX_KIND 未設定=sandbox種別不明。保守的に判定不能(2)を返す。" >&2
  exit 2
fi

echo "[codex_exec_sandbox_guard] OK: sandbox=$CODEX_SANDBOX_KIND 検証済・非live cwd=$INTENDED_CWD。Codex exec 起動可。"
exit 0
