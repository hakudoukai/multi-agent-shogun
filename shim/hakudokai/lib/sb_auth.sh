#!/usr/bin/env bash
# sb_curl — Supabase auth through a private temporary curl config.
# The credential value is never placed in argv. A subshell-local EXIT trap
# removes the config on success, curl failure, HUP, INT, TERM, and shell exit.
sb_curl() (
  set +x
  local _cfg
  umask 077
  _cfg="$(mktemp "${TMPDIR:-/tmp}/sb-curl.XXXXXX")" || exit 1
  _sb_curl_cleanup() { rm -f -- "$_cfg"; }
  trap _sb_curl_cleanup EXIT
  trap 'exit 129' HUP
  trap 'exit 130' INT
  trap 'exit 143' TERM
  chmod 600 "$_cfg" || exit 1
  printf '%s
'     "header = \"Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY:?SUPABASE_SERVICE_ROLE_KEY unset}\""     "header = \"apikey: ${SUPABASE_SERVICE_ROLE_KEY}\"" >"$_cfg" || exit 1
  curl --config "$_cfg" "$@"
)
