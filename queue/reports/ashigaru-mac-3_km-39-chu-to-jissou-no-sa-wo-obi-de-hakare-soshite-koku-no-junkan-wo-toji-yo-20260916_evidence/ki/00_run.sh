#!/bin/bash
# 第38弾 ―― 走らせる器(v2)。
#  (1) 出と誤を別 file に取り、★空なら「空である旨の一行」を書く★(委員長裁 seq310228⑶)。
#  (2) ★LC_ALL=C で★末尾空白を捕へた其の場で削る★ ―― 生の `>` 捕獲は門の條②を素通りする(法
#      「Raw `>` capture bypasses normalization」／「Unified diff blank context line = trailing space」)。
#      削つた行數は 00_rc.txt に殘す ―― ★黙つて直さぬ★。
#  ★之は紙ではなく器である。本弾の問二の材(何が手を変へるか)。★
# 使ひ方: 00_run.sh <tag> <cmd...>   出=kou/<tag>.out 誤=kou/<tag>.err
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"
tag="$1"; shift
o="$B/kou/$tag.out"; e="$B/kou/$tag.err"
"$@" > "$o" 2> "$e"
rc=$?
for f in "$o" "$e"; do
  if [ ! -s "$f" ]; then
    printf '★空であつた★ 器=00_run.sh tag=%s 流=%s 刻=%s 註=不在を成功の顔にせぬ(裁 seq310228⑶)\n' \
      "$tag" "$(basename "$f")" "$(date '+%Y-%m-%dT%H:%M:%S%z')" > "$f"
  fi
done
wso=$(LC_ALL=C grep -cE '[[:blank:]]+$' "$o"); [ $? -ge 2 ] && wso='★測れぬ★'
wse=$(LC_ALL=C grep -cE '[[:blank:]]+$' "$e"); [ $? -ge 2 ] && wse='★測れぬ★'
LC_ALL=C sed -i '' -E 's/[[:blank:]]+$//' "$o" "$e"
printf 'tag=%s rc=%s out_bytes=%s err_bytes=%s ws_kezutta_out(行)=%s ws_kezutta_err(行)=%s koku=%s\n' \
  "$tag" "$rc" "$(wc -c < "$o" | tr -d ' ')" "$(wc -c < "$e" | tr -d ' ')" "$wso" "$wse" \
  "$(date '+%H:%M:%S')" >> "$B/kou/00_rc.txt"
exit $rc
