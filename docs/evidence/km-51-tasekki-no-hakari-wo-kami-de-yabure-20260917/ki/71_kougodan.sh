#!/bin/bash
# 71_kougodan.sh ―― ★18閾の「後段の讀手」を、生器から己の手で引く★
# 使ひ方: 71_kougodan.sh <watcher> <health> <context> <enter>
# ★專任2 の「後段の逐語」欄は 18 の内 6 が散文(「冷却比較」「段の番号」「打鍵中の見送り上限」)で
#   行番も演算子も無い。∴ 彼の欄からは割れぬ。生器から引き直す。★
# 出し方: 閾名<TAB>器<TAB>行<TAB>讀手<TAB>逐語
set -u
W="$1"; H="$2"; C="$3"; E="$4"
printf '閾名\t器\t行\t讀手\t使用箇所の逐語\n'
hiku(){ # $1=閾名 $2=器path $3=器札
  local na="$1" f="$2" ki="$3" n
  # ★番人列と番人の定義そのものは除く★
  grep -n "\\b${na}\\b" "$f" | grep -v 'fix_threshold' | grep -v "^[0-9]*:for _t in\|^[0-9]*: *${na}:" \
  | grep -v '^[0-9]*: *#' | while IFS= read -r ln; do
      n="${ln%%:*}"; local body="${ln#*:}"
      local yo='―'
      case "$body" in
        *'$(('*"${na}"*|*"${na}"*'))'*) yo='算術$(( ))' ;;
      esac
      case "$body" in
        *gtimeout*|*inotifywait*) yo='外器' ;;
        *'[ '*-lt*|*'[ '*-ge*|*'[ '*-gt*|*'[ '*-le*) [ "$yo" = '―' ] && yo='test[ ]' ;;
      esac
      case "$body" in
        *"\${${na}:-"*) yo="${yo}+残存既定" ;;
      esac
      printf '%s\t%s\t%s\t%s\t%s\n' "$na" "$ki" "$n" "$yo" "$(printf '%s' "$body" | sed 's/^[[:space:]]*//')"
    done
}
for na in ESCALATE_PHASE1 ESCALATE_PHASE2 ESCALATE_COOLDOWN NUDGE_COOLDOWN_SEC NUDGE_COOLDOWN_SEC_CODEX \
          NUDGE_COOLDOWN_SEC_CLAUDE ASW_PHASE APPROVAL_ALERT_COOLDOWN MAX_TYPING_SKIP INOTIFY_TIMEOUT; do
  hiku "$na" "$W" watcher
done
for na in HEALTH_CHECK_COOLDOWN_SEC HEALTH_CHECK_TOKEN_WARN HEALTH_CHECK_TOKEN_CRIT; do hiku "$na" "$H" health; done
for na in CONTEXT_WARN_BYTES CONTEXT_DANGER_BYTES; do hiku "$na" "$C" context; done
for na in ER_THRESHOLD_MIN ER_FIRE_CAP_COUNT ER_FIRE_CAP_WINDOW_MIN; do hiku "$na" "$E" enter; done
