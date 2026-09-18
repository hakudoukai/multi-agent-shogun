#!/bin/bash
# 30_yomite.sh ―― ★四讀手の讀みを己の手で測る★(專任2 の 53_yomite.tsv を検める)
# 使ひ方: 30_yomite.sh <被験shell>    例: 30_yomite.sh /bin/bash
# 刷る: 形\t-ge0_rc\t[ ]が8と讀むか\t[ ]が10と讀むか\t$(( ))\tpython\tgtimeout
# ★單位★: rc=終了符 / 值=讀手が得た整数 / 拒=器が起動を拒んだ
set -u
SH_UNDER="${1:-/bin/bash}"
printf '#被験shell\t%s\t%s\n' "$SH_UNDER" "$("$SH_UNDER" -c 'echo ${BASH_VERSION:-非bash}')"
printf '#形\tge0_rc\ttest==8\ttest==10\tarith\tpython\tgtimeout\n'
for v in '010' '007' '0x32' '0o62' '+50' ' 50 ' '-0' '0' '50' '2' '9223372036854775807'; do
  r=$("$SH_UNDER" -c '
    v="$1"
    [ "$v" -ge 0 ] 2>/dev/null; g=$?
    if [ "$v" -eq 8 ] 2>/dev/null; then e8=y; else e8=n; fi
    if [ "$v" -eq 10 ] 2>/dev/null; then e10=y; else e10=n; fi
    a=$( (echo "$((v))") 2>/dev/null ) || a=拒
    printf "%s\t%s\t%s\t%s" "$g" "$e8" "$e10" "${a:-拒}"
  ' _ "$v")
  p=$(python3 -c 'import sys
try: print(int(sys.argv[1]))
except Exception as e: print("拒")' "$v")
  if command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$v" true >/dev/null 2>&1; t="rc=$?"
  else
    t=不在
  fi
  printf '%s\t%s\t%s\t%s\n' "$(printf '%s' "$v" | sed 's/ /␠/g')" "$r" "$p" "$t"
done
