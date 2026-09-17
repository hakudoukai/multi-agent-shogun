#!/bin/bash
# 乙の★名の口★の毒: rc では映らぬ。「解けた path」と「書き込みが着くか」を測る。
# ★稼働 log (/tmp/fukuincho_detect_stale.log) へは一字も書かぬ★ ―― 絶対 path は「書かず」と刷る。
SUNA="$1"; shift          # 砂場 (相対名が落ちる先)
cd "$SUNA" || exit 9
UTS="$2"
# source せず、乙 L31 の逐語と同じ解決だけを行ふ (関数は呼ばぬ = 書き込み無)
RESOLVED="${DETECT_STALE_LOG:-/tmp/fukuincho_detect_stale.log}"
printf '解けたpath=[%s]\n' "$RESOLVED"
case "$RESOLVED" in
  /*) printf '着弾=書かず(絶対path・稼働 log の疑ひ故)\n'; exit 0 ;;
esac
if printf 'km83\n' >> "$RESOLVED" 2>/dev/null; then
  printf '着弾=成(砂場に file 生成)\n'
else
  printf '着弾=否(rc非0・然し乙は 2>/dev/null||true で呑む)\n'
fi
