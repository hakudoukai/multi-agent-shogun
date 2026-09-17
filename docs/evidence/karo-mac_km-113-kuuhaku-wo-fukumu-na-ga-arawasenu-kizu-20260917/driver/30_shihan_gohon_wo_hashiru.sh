#!/bin/bash
# ★四版 × 五見本 を走らせる★
#   引数 $1 = 見本を建てる先(束の外)  $2 = raw の置き先  $3 = repo 根
#   出目は ★stdout★ に出る(此の照合器は stderr へ出さぬ ―― 門の .sh とは違ふ)。
set -u
FX="$1"; RAW="$2"; ROOT="$3"
PY=/opt/homebrew/bin/python3
B="$(cd "$(dirname "$0")/.." && pwd)"
TABA="$ROOT/docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917"

"$PY" -B "$B/driver/10_mihon_wo_tateru.py" "$FX" || exit 2

printf '%-14s %-10s %-6s %s\n' 版 見本 rc 出目
printf '%s\n' '-------------- ---------- ------ --------------------------------------'
for v in v1_127gyou v2_originmain v3_worktree v4_naoshita; do
  for s in s_A s_B s_C s_D; do
    log="$RAW/31_${v}_${s}.out"
    "$PY" -B "$B/_ver/${v}.py" "$FX/$s/manifest.txt" "$FX/$s" > "$log" 2>&1
    rc=$?
    msg=$(grep -E '一致 |実体無 ' "$log" | head -1 | sed 's/^ *//' | cut -c1-40)
    printf '%-14s %-10s %-6s %s\n' "$v" "$s" "$rc" "$msg"
  done
  log="$RAW/31_${v}_km105taba.out"
  "$PY" -B "$B/_ver/${v}.py" "$TABA/MANIFEST.txt" "$TABA" > "$log" 2>&1
  rc=$?
  msg=$(grep -E '一致 |実体無 ' "$log" | head -1 | sed 's/^ *//' | cut -c1-40)
  printf '%-14s %-10s %-6s %s\n' "$v" "km105実束" "$rc" "$msg"
done
