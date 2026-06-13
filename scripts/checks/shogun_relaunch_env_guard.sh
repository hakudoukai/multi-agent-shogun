#!/usr/bin/env bash
#
# Check — shogun-relaunch-env-guard (advisory)
#
# 由来: §19 lessons-to-skill / incident 2026-06-13 (second_pc bash 落ち + env-gap)。
# 目的: send-keys で ★bare claude★ を起動している箇所 (= doppler env 欠落で
#       API retry 滞留する env-gap リスク) を静的に advisory 検出する。
#
# 判定: 同一行に `send-keys` と literal `claude` があり、かつ `doppler` を含まない行。
#       (正規経路は `doppler run … -- claude …`。$command 変数経由の launch は literal
#        "claude" を含まないので誤検知しない。)
# 終了コード: 0 = OK (該当なし) / 1 = warning (該当あり)。★critical (2) は出さない=ブロック禁★。
# stdout = 人間向けサマリ、stderr = 判定根拠 (該当行)。

set -uo pipefail

cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../.." 2>/dev/null || exit 0

# 探索対象 (.bak/.git/node_modules/archive/checks/tests/skills/test_ は除外 = 本 check
# 自身・テスト fixture・skill 文書の自己誤検知を避ける)。claude は ★コマンド位置★
# (行頭 / ; / && / 空白 直後で、後続が 空白・フラグ・引用・行末) のものだけを対象とし、
# banner 文字列中の "claude" (例 `将軍 / claude'`) は拾わない。
HITS=$(grep -rnE 'send-keys' scripts shim 2>/dev/null \
  | grep -vE '\.bak|/archive/|node_modules|/checks/|/tests/|test_|/skills/' \
  | grep -vE '^[^:]*:[0-9]+:[[:space:]]*#' \
  | grep -E '(^|[;&|"[:space:]])claude([[:space:]]|--|"|$)' \
  | grep -v 'doppler' \
  || true)

if [ -z "$HITS" ]; then
  echo "shogun-relaunch-env-guard: OK (bare-claude send-keys relaunch なし)"
  exit 0
fi

echo "shogun-relaunch-env-guard: WARNING — bare claude を send-keys 起動している可能性 (env-gap リスク)。"
echo "  → doppler run --project openhands --config dev -- claude --permission-mode auto を使うこと。"
echo "  詳細: skills/shogun-relaunch-env-guard/SKILL.md"
{
  echo "--- 該当行 ---"
  printf '%s\n' "$HITS"
} >&2
exit 1
