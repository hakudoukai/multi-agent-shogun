#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hakudokai/projects/multi-agent-shogun
if [ -f "$ROOT/shim/hakudokai/lib/sb_auth.sh" ]; then source "$ROOT/shim/hakudokai/lib/sb_auth.sh"; fi
if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  if command -v doppler >/dev/null 2>&1 && [ "${SENMU_DOPPLER_CHILD:-0}" != 1 ]; then
    export SENMU_DOPPLER_CHILD=1
    exec doppler run --project openhands --config dev --preserve-env="SENMU_DOPPLER_CHILD" -- "$0" "$@"
  fi
  echo 'senmu desktop route: supabase environment missing' >&2; exit 1
fi
exec /usr/bin/python3 "$ROOT/shim/hakudokai/senmu_desktop_route_watcher.py" "$@"
