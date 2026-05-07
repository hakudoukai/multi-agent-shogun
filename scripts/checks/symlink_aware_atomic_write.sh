#!/usr/bin/env bash
# symlink_aware_atomic_write.sh — atomic replace pattern の symlink 安全性 audit
#
# 2026-05-08 split-brain 事故対策 (docs/incident_logs/2026-05-08_inbox_split_brain.md) の
# pattern audit。tempfile + os.replace / os.rename / mv-tmp の atomic write pattern を
# grep し、直前 5 行内に realpath/readlink 解決が無ければ WARN 列挙。
#
# Usage: bash scripts/checks/symlink_aware_atomic_write.sh
#
# Exit codes:
#   0 = 危険 pattern 検出ゼロ
#   2 = 危険 pattern 検出 (stderr に列挙、manual review 推奨)
#   1 = 予約
#
# IMPORTANT (CLAUDE.md §19.3 mandate):
#   PreToolUse hook で呼ばれる場合、本 script の非 0 exit が親 tool 操作を
#   ブロックしてはならない。呼出側で `|| true` を必ず付ける。

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$SCRIPT_DIR"

# 監査対象 dir (= symlink alias 運用領域 + 周辺)
TARGETS=(scripts shim lib)

issues=0

# ─── Pattern A/B: Python os.replace / os.rename ───
while IFS= read -r line; do
  [ -z "$line" ] && continue
  file="${line%%:*}"
  rest="${line#*:}"
  lineno="${rest%%:*}"
  match="${rest#*:}"

  # 自己除外
  case "$file" in
    scripts/checks/symlink_aware_atomic_write.sh) continue ;;
    *.bak*|*_archive*) continue ;;
  esac

  # 直前 15 行に realpath / readlink があるか (= block 全体スコープ想定)
  start=$((lineno > 15 ? lineno - 15 : 1))
  end=$lineno
  context=$(sed -n "${start},${end}p" "$file" 2>/dev/null)
  if echo "$context" | grep -qE "(realpath|readlink)"; then
    continue  # 安全 pattern (= 直近で canonical 解決済)
  fi

  # match 行内に *_canonical 変数を 2nd 引数として使っていれば safe (= 既に解決済)
  if echo "$match" | grep -qE "os\.(replace|rename)\([^,]+,\s*[a-zA-Z_]*_canonical[\s)]"; then
    continue
  fi

  # comment 行 (= "#" or "//" 直後の match) 除外
  if echo "$match" | grep -qE "^\s*(#|//|--).*os\.(replace|rename)"; then
    continue
  fi

  echo "[symlink_aware_atomic_write] WARN: $file:$lineno potential symlink-unsafe atomic replace" >&2
  echo "[symlink_aware_atomic_write]       match: $(echo "$match" | sed 's/^[ \t]*//' | head -c 100)" >&2
  issues=$((issues + 1))
done < <(grep -rnE "os\.(replace|rename)\(" "${TARGETS[@]}" 2>/dev/null)

# ─── Pattern C: Bash mv with tmp variable ───
while IFS= read -r line; do
  [ -z "$line" ] && continue
  file="${line%%:*}"
  rest="${line#*:}"
  lineno="${rest%%:*}"
  match="${rest#*:}"

  case "$file" in
    scripts/checks/symlink_aware_atomic_write.sh) continue ;;
    *.bak*|*_archive*) continue ;;
  esac

  start=$((lineno > 5 ? lineno - 5 : 1))
  end=$lineno
  context=$(sed -n "${start},${end}p" "$file" 2>/dev/null)
  if echo "$context" | grep -qE "(realpath|readlink)"; then
    continue
  fi

  echo "[symlink_aware_atomic_write] WARN: $file:$lineno potential mv-based atomic replace without symlink resolve" >&2
  echo "[symlink_aware_atomic_write]       match: $(echo "$match" | sed 's/^[ \t]*//' | head -c 100)" >&2
  issues=$((issues + 1))
done < <(grep -rnE "^\s*mv\s+[\"\$].*tmp.*[\"\$]\s+[\"\$].*(yaml|json|md|conf)[\"\$]?" "${TARGETS[@]}" 2>/dev/null)

if [ "$issues" -gt 0 ]; then
  echo "[symlink_aware_atomic_write] $issues potential issue(s) detected." >&2
  echo "[symlink_aware_atomic_write] manual review recommended:" >&2
  echo "[symlink_aware_atomic_write]   - 直前 5 行に realpath/readlink で canonical 解決を追加せよ" >&2
  echo "[symlink_aware_atomic_write]   - 例: scripts/inbox_write.sh L222- (commit dd706ad) を参考" >&2
  echo "[symlink_aware_atomic_write]   - 詳細: docs/incident_logs/2026-05-08_inbox_split_brain.md" >&2
  exit 2
fi

exit 0
