#!/usr/bin/env bash
set -euo pipefail

status=0

pass() { printf 'PASS %s\n' "$1"; }
fail() { printf 'FAIL %s\n' "$1" >&2; status=1; }

require_fixed() {
  local file="$1" expected="$2" label="$3"
  if [[ -f "$file" ]] && grep -Fqx -- "$expected" "$file"; then
    pass "$label"
  else
    fail "$label"
  fi
}

reject_retired() {
  local file="$1" label="$2"
  if [[ ! -f "$file" ]]; then
    fail "$label (missing)"
  elif grep -Eq 'gpt-5\.5|localhost:8082' "$file"; then
    fail "$label (retired value active)"
  else
    pass "$label"
  fi
}

require_fixed "$HOME/.hermes/config.yaml" '  default: gpt-5.6-sol' 'advisor default model'
require_fixed "$HOME/.hermes/.env" 'ANTHROPIC_BASE_URL=http://192.168.11.59:8080' 'advisor centralized ccflare'
require_fixed "$HOME/.hermes/context_length_cache.yaml" '  gpt-5.6-sol@https://chatgpt.com/backend-api/codex: 372000' 'advisor 5.6 context cache'

active=(
  "$HOME/.hermes/config.yaml"
  "$HOME/.hermes/.env"
  "$HOME/.hermes/context_length_cache.yaml"
  "$HOME/hermes-departments/registry.json"
)

for role in reserveimage handoverdocs bianalytics; do
  active+=(
    "$HOME/hermes-departments/$role/config.yaml"
    "$HOME/hermes-departments/$role/context_length_cache.yaml"
  )
done

for file in "${active[@]}"; do
  reject_retired "$file" "retired-value guard: $file"
done

python3 - "$HOME/hermes-departments/registry.json" <<'PY' || status=1
import json
import sys

path = sys.argv[1]
expected = {"reserveimage", "handoverdocs", "bianalytics"}
with open(path, encoding="utf-8") as f:
    data = json.load(f)
roles_raw = data.get("roles", data)
if isinstance(roles_raw, list):
    roles = {row.get("role_id"): row for row in roles_raw}
else:
    roles = roles_raw
bad = []
for name in expected:
    row = roles.get(name, {})
    if row.get("provider") != "openai-codex" or row.get("model") != "gpt-5.6-sol":
        bad.append(name)
if bad:
    print("FAIL department registry: " + ",".join(sorted(bad)), file=sys.stderr)
    raise SystemExit(1)
print("PASS department registry exact model/provider")
PY

if (( status != 0 )); then
  printf 'status=RED gpt56_runtime_canon_mismatch\n' >&2
  exit 1
fi

printf 'status=GREEN standard_model=gpt-5.6-sol endpoint=third_pc:8080\n'
