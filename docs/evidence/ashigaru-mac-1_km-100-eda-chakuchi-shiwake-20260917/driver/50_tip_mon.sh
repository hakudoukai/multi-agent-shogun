#!/bin/bash
# 50_tip_mon.sh ―― ㋔ 受入条件「門 rc=0 か／臺帳が束内相対か」を ★tip の束そのもの★ で測る。
# tip の evidence dir を `git archive`(読取)で repo 外の scratch へ展開し(checkout せず・工作樹不触)、
# 條① 照合器(karo_mac_manifest_verify.py <臺帳> .)と 出す前の門(KM_GATE_MANIFEST_BASE=. 付き・argv=臺帳に載る path)を当てる。
# 用法: bash driver/50_tip_mon.sh <REPO> raw/40_hakari.tsv <SCRATCH> raw/75_tip_mon.tsv raw/75_logs
set -u
REPO=$1; HAKARI=$2; SCR=$3; OUT=$4; LOGD=$5
VER=$REPO/scripts/checks/karo_mac_manifest_verify.py; GATE=$REPO/scripts/checks/karo_mac_dasumae_gate.sh
mkdir -p "$SCR" "$LOGD"
printf 'branch\tsha12\tevidence_dir\tarchive_rc\tfile_n\tdaichou\tjou1_rc\tjou1_line\tgate_argv_n\tgate_rc\tgate_last_line\n' > "$OUT"
tail -n +2 "$HAKARI" | while IFS=$'\t' read -r branch sha _rest; do
  dirs=$(printf '%s\n' "$_rest" | awk -F'\t' '{print $16}')   # d2_evidence_dirs は 18 欄目(branch,sha を除いて 16 欄目)
  for d in $(printf '%s' "$dirs" | tr ',' ' '); do
    safe=$(printf '%s' "$branch" | tr '/' '__'); dst="$SCR/$safe"; mkdir -p "$dst"
    git -c core.quotePath=false -C "$REPO" archive "$sha" -- "docs/evidence/$d" | tar -x -C "$dst"; arc=$?
    b="$dst/docs/evidence/$d"; n=$(find "$b" -type f | grep -c '')
    man=$(cd "$b" && ls -1 2>/dev/null | grep -iE 'manifest' | grep -vE '\.(first|second|third|fourth|fifth)\.|hashiri' | head -1)
    if [ -z "$man" ]; then printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$branch" "${sha:0:12}" "$d" "$arc" "$n" "臺帳無" "-" "-" "-" "-" "-" >> "$OUT"; continue; fi
    lg="$LOGD/${safe}__${d}"
    ( cd "$b" && python3 -B "$VER" "$man" . ) > "$lg.jou1.out" 2> "$lg.jou1.err"; j1=$?
    j1l=$(grep -E '一致|相違|実体無' "$lg.jou1.out" "$lg.jou1.err" | head -1 | sed 's/^[^:]*://')
    argv=$(cd "$b" && grep -E '^path=' "$man" | sed -E 's/^path=([^ ]+).*/\1/')
    an=$(printf '%s\n' "$argv" | grep -c '')
    ( cd "$b" && KM_GATE_MANIFEST_BASE=. bash "$GATE" "$man" $argv ) > "$lg.gate.out" 2> "$lg.gate.err"; grc=$?
    gl=$(grep -E '出してよい|出すな|落ちた|止' "$lg.gate.err" | tail -1)
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$branch" "${sha:0:12}" "$d" "$arc" "$n" "$man" "$j1" "$j1l" "$an" "$grc" "$gl" >> "$OUT"
  done
done
echo "scratch=$SCR"
