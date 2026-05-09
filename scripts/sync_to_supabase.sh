#!/usr/bin/env bash
# scripts/sync_to_supabase.sh — source_code_cache へ重要 file UPSERT
#
# 陛下御差配 2026-05-09: 「適時 Supabase のプログラム保存場所への保存も忘れずに」
# 既存機構: source_code_cache table (REST API 経由 UPSERT)
# 関連: rpc/list_source_files / rpc/get_source_code / rpc/search_source_code
#
# Usage:
#   bash scripts/sync_to_supabase.sh [file1] [file2] ...
#   引数なし = key file 既定 list を全 UPSERT
#
# Env (= ~/.bashrc 永続化推奨):
#   SUPABASE_URL              (= https://pxvnhkiqyxkejzivspde.supabase.co)
#   SUPABASE_SERVICE_ROLE_KEY (= service_role JWT)

set -euo pipefail

SUPABASE_URL="${SUPABASE_URL:-https://pxvnhkiqyxkejzivspde.supabase.co}"
SK="${SUPABASE_SERVICE_ROLE_KEY:-}"

if [ -z "$SK" ]; then
  echo "ERROR: SUPABASE_SERVICE_ROLE_KEY not set" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMIT="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo "unknown")"

# 既定 key file list (= 引数なし時)
DEFAULT_FILES=(
  "queue/shogun_to_karo.yaml"
  "memory/MEMORY.md"
  "dashboard.md"
  ".mcp.json"
  ".claude/settings.json"
  "instructions/shogun.md"
  "instructions/karo.md"
)

FILES=("$@")
if [ "${#FILES[@]}" -eq 0 ]; then
  FILES=("${DEFAULT_FILES[@]}")
fi

upsert_one() {
  local path="$1"
  local full="$REPO_ROOT/$path"
  if [ ! -f "$full" ]; then
    echo "  ✗ skip: $path (not found at $full)"
    return
  fi
  python3 - "$full" "$path" "$COMMIT" "$SUPABASE_URL" "$SK" <<'PYEOF'
import sys, json, urllib.request, os
fp, label, commit, url, sk = sys.argv[1:6]
content = open(fp, 'r', encoding='utf-8', errors='replace').read()
size = os.path.getsize(fp)
lines = content.count('\n') + 1
payload = [{
    "file_path": label,
    "content": content,
    "file_size": size,
    "line_count": lines,
    "commit_hash": commit,
}]
req = urllib.request.Request(
    f"{url}/rest/v1/source_code_cache?on_conflict=file_path",
    data=json.dumps(payload).encode('utf-8'),
    headers={
        "apikey": sk, "Authorization": f"Bearer {sk}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    },
    method="POST",
)
try:
    r = urllib.request.urlopen(req, timeout=30)
    print(f"  ✓ {label}: {size}B / {lines} lines / {commit} → {r.status}")
except urllib.error.HTTPError as e:
    print(f"  ✗ {label}: HTTP {e.code} — {e.read().decode()[:200]}")
except Exception as e:
    print(f"  ✗ {label}: {e}")
PYEOF
}

echo "=== sync_to_supabase: ${#FILES[@]} files (commit=$COMMIT) ==="
for f in "${FILES[@]}"; do
  upsert_one "$f"
done
echo "=== done ==="
