#!/usr/bin/env bash
# 92 — 直し前/後 を同じ入力で走らせ、★判定不変・注入のみ消える★を示す
set -u
run_guard(){  # $1=guardファイル $2=環境値
  ( _th_say(){ printf '[watcher] %s\n' "$*" >&2; }
    unset T OUT; T="$2"
    # guard の頭〜fix_threshold 定義のみ source(末尾の実行部は写しに無い→定義だけ)
    . "$1"
    _ef="$(mktemp)"; fix_threshold T 30 OUT 2>"$_ef" 1>/dev/null
    printf 'OUT=%s\t鳴り行数=%s\n' "${OUT:-?}" "$(wc -l <"$_ef" | tr -d ' ')"
    rm -f "$_ef" )
}
BEF="$(dirname "$0")/guard_inbox_watcher.sh"
AFT="$(dirname "$0")/91_guard_patched.sh"
INJ="$(printf '50\n9999')"
echo "=== 陽性: 改行注入(㋐12) ==="
printf '前 '; run_guard "$BEF" "$INJ"
printf '後 '; run_guard "$AFT" "$INJ"
echo "=== 陰性: 清数30 ==="
printf '前 '; run_guard "$BEF" "30"
printf '後 '; run_guard "$AFT" "30"
echo "=== ⑷ 意味不変: 直しは表示のみ。倒す先(OUT)と fail-closed 判定は上の通り前後一致 ==="
echo "--- 後の鳴り逐字(注入が一行に均された證) ---"
( _th_say(){ printf '[watcher] %s\n' "$*" >&2; }; unset T OUT; T="$INJ"; . "$AFT"
  fix_threshold T 30 OUT 2>&1 1>/dev/null | cat -n )
