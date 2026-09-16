#!/bin/bash
# 41_ukezara.sh ―― ★「一様18」を受け皿の差で破る★
#   watcher 10本: fix_threshold "$n" "$d" "$n"      (★env名へ書き戻す★)
#   他 8本      : fix_threshold NAME  d  BETSUMEI  (★別名へ書く=env名は生の儘★)
#   ∴ 子プロセスが継ぐ値が違ふ。番人段の出目は ★形のみの函数ではない★。
# 使ひ方: 41_ukezara.sh <番人片path> <毒値>
set -u
KATA="$1"; DOKU="$2"
. "$KATA"                                   # 番人(_th_say/env_state/num_same_op/fix_threshold)を読む
printf '#形式\t親の受け皿\t親のenv名\t★子が継ぐ値★\t判\n'

export T_A="$DOKU"
fix_threshold T_A 120 T_A            2>/dev/null          # 甲=watcher 式
ko_a=$(bash -c 'printf "%s" "${T_A-★未設定★}"')
# ★判の述語(宣): 「親が実際に使ふ値(受け皿)」と「子が継ぐ値」が割れた時のみ★毒が子へ★。
#   ∴ 清き値では両者が一致し、陰性対照は必ず「清」に出る(出なければ器が壊れて居る)。
printf '甲(watcher式)\t%s\t%s\t%s\t%s\n' "$T_A" "$T_A" "$ko_a" "$([ "$ko_a" = "$T_A" ] && echo 清 || echo ★毒が子へ★)"

export T_B="$DOKU"
fix_threshold T_B 120 BETSU          2>/dev/null          # 乙=enter/health/context 式
ko_b=$(bash -c 'printf "%s" "${T_B-★未設定★}"')
printf '乙(他三器式)\t%s\t%s\t%s\t%s\n' "$BETSU" "$T_B" "$ko_b" "$([ "$ko_b" = "$BETSU" ] && echo 清 || echo ★毒が子へ★)"

# 陰性対照: 清い値は両式とも子へ其の儘
export T_C=120
fix_threshold T_C 120 T_C 2>/dev/null; ko_c=$(bash -c 'printf "%s" "${T_C-★未設定★}"')
export T_D=120
fix_threshold T_D 120 BETSU2 2>/dev/null; ko_d=$(bash -c 'printf "%s" "${T_D-★未設定★}"')
printf '陰性:甲清値\t%s\t%s\t%s\t%s\n' "$T_C" "$T_C" "$ko_c" "$([ "$ko_c" = "$T_C" ] && echo 清 || echo ★毒が子へ★)"
printf '陰性:乙清値\t%s\t%s\t%s\t%s\n' "$BETSU2" "$T_D" "$ko_d" "$([ "$ko_d" = "$BETSU2" ] && echo 清 || echo ★毒が子へ★)"
