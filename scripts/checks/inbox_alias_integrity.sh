#!/usr/bin/env bash
# inbox_alias_integrity.sh — queue/inbox/ alias↔canonical symlink integrity audit
#
# 2026-05-08 split-brain 事故 (docs/incident_logs/2026-05-08_inbox_split_brain.md) の
# 再発防止。alias が regular file 化、md5 不一致、broken symlink 等を検出する。
#
# Usage: bash scripts/checks/inbox_alias_integrity.sh
#
# Exit codes:
#   0 = 全 alias が canonical へ正しく解決、md5 一致
#   2 = 不整合検出 (stderr に警告出力)
#   1 = 予約 (使用せず)
#
# IMPORTANT (CLAUDE.md §19.3 mandate):
#   PreToolUse hook で呼ばれる場合、本 script の非 0 exit が親 tool 操作を
#   ブロックしてはならない。呼出側で `|| true` を必ず付ける。
#
# Timeout: 5秒上限を想定 (= queue/inbox/ は小さい想定)。

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$SCRIPT_DIR"

# alias:canonical pair (= Phase 3 design pattern)
PAIRS=(
  "queue/inbox/shogun.yaml:queue/inbox/nobunaga.yaml"
  "queue/inbox/karo.yaml:queue/inbox/hideyoshi.yaml"
  "queue/inbox/gunshi.yaml:queue/inbox/ieyasu.yaml"
)

issues=0

for pair in "${PAIRS[@]}"; do
  alias_path="${pair%%:*}"
  canonical_path="${pair##*:}"

  # 1. alias 存在確認
  if [ ! -e "$alias_path" ] && [ ! -L "$alias_path" ]; then
    echo "[inbox_alias_integrity] WARN: alias missing: $alias_path" >&2
    issues=$((issues + 1))
    continue
  fi

  # 2. alias が symlink であること
  if [ ! -L "$alias_path" ]; then
    echo "[inbox_alias_integrity] WARN: alias is regular file (= split-brain risk): $alias_path" >&2
    echo "[inbox_alias_integrity]       expected: symlink to $(basename "$canonical_path")" >&2
    issues=$((issues + 1))
    continue
  fi

  # 3. canonical 存在確認
  if [ ! -e "$canonical_path" ]; then
    echo "[inbox_alias_integrity] WARN: canonical missing for $alias_path: $canonical_path" >&2
    issues=$((issues + 1))
    continue
  fi

  # 4. symlink target が期待 canonical を指しているか
  resolved="$(readlink -f "$alias_path" 2>/dev/null)"
  expected="$(readlink -f "$canonical_path" 2>/dev/null)"
  if [ -z "$resolved" ] || [ "$resolved" != "$expected" ]; then
    echo "[inbox_alias_integrity] WARN: $alias_path resolves to $resolved" >&2
    echo "[inbox_alias_integrity]       expected: $expected" >&2
    issues=$((issues + 1))
    continue
  fi

  # 5. md5 一致確認 (= alias dereferenced 内容 ≡ canonical 内容)
  alias_md5=$(md5sum "$alias_path" 2>/dev/null | awk '{print $1}')
  canonical_md5=$(md5sum "$canonical_path" 2>/dev/null | awk '{print $1}')
  if [ "$alias_md5" != "$canonical_md5" ]; then
    echo "[inbox_alias_integrity] WARN: md5 mismatch $alias_path vs $canonical_path" >&2
    echo "[inbox_alias_integrity]       alias_md5=$alias_md5 canonical_md5=$canonical_md5" >&2
    issues=$((issues + 1))
    continue
  fi
done

if [ "$issues" -gt 0 ]; then
  echo "[inbox_alias_integrity] $issues issue(s) detected." >&2
  echo "[inbox_alias_integrity] Recovery procedure: docs/incident_logs/2026-05-08_inbox_split_brain.md" >&2
  exit 2
fi

# 健全
exit 0
