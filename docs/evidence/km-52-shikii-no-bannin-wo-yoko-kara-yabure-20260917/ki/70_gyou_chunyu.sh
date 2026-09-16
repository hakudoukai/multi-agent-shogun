#!/usr/bin/env bash
# 70 — ★行注入は四器悉くで起きるか。偽の一行は「作れる」か★(㋓)
#   番人が値を拒む時、逐語で "${_ft_v}" を鳴らし口へ挿す。値に改行が在れば一行が二行に割れる。
#   ★${VAR} で括る ―― 「」等の多byte字が直後に来ると裸の $VAR は名に食はれる(既知の罠)★
set -u
say_watcher(){ printf '%s\n' "[watcher] $*" >&2; }
say_health(){  printf '%s\n' "[health_check] $*" >&2; }
say_context(){ echo "[context_warn] $*" >&2; }
LOG="$(mktemp)"; say_enter(){ printf '[%s] %s\n' "FIXED_TS" "$*" | tee -a "${LOG}" >/dev/null; }
# 器ごとに鳴らし口が違ふ: watcher/health/context は stderr、enter は LOG file(tee -a)。
#   ∴ 数へる流れも器ごとに変へる。★同じ物差しを別の器に当てぬ★
count_stderr(){ "$1" "$2" 2>&1 1>/dev/null | wc -l | tr -d ' '; }
count_log(){ : > "${LOG}"; say_enter "$1" >/dev/null 2>&1; wc -l < "${LOG}" | tr -d ' '; }
msg(){ printf '★閾 INOTIFY_TIMEOUT を比較器が扱へぬ(「%s」) ―― 既定 30 へ倒す(fail-closed)★' "$1"; }

echo "=== 陰性対照: 改行無しの拒否 → 一行 ==="
printf 'watcher\t行=%s\n' "$(count_stderr say_watcher "$(msg abc)")"
printf 'health \t行=%s\n' "$(count_stderr say_health  "$(msg abc)")"
printf 'context\t行=%s\n' "$(count_stderr say_context "$(msg abc)")"
printf 'enter  \t行=%s (LOG)\n' "$(count_log "$(msg abc)")"

echo "=== 形12: 値=50<改行>9999 → 二行(注入成立) ==="
V="$(printf '50\n9999')"
printf 'watcher\t行=%s\n' "$(count_stderr say_watcher "$(msg "${V}")")"
printf 'health \t行=%s\n' "$(count_stderr say_health  "$(msg "${V}")")"
printf 'context\t行=%s\n' "$(count_stderr say_context "$(msg "${V}")")"
printf 'enter  \t行=%s (LOG)\n' "$(count_log "$(msg "${V}")")"

echo "=== ★偽記録を仕立てる★: 値に完結した第二行を仕込む ==="
FORGE="$(printf '30 へ倒す(fail-closed)★\n[watcher] ★閾 INOTIFY_TIMEOUT 正常 ―― 値9999 受理★')"
echo "--- watcher stderr 逐字 ---"
say_watcher "$(msg "${FORGE}")" 2>&1 1>/dev/null | cat -n
