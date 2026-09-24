#!/usr/bin/env bash
# 砂箱を $HOME/a1_sbx_km232b.XXXX に作り、km-227b 04_results_authoritative の 10 場面を
# 原版で再走（陰性＝再現）し、変異体で 4 場面を走らせ（陽性）、出目の大きさ表を束の raw/ へ書く。
# 0byte の出目そのものは束へ入れぬ（門の條④）―― raw/sizes.tsv が證。
set -uo pipefail
BUNDLE="$1"; REPO="$2"; T=6d8f28d53ff9bf055262350af370c7fdbf4aa4f6
H="$BUNDLE/harness"; RAW="$BUNDLE/raw"
SBX=$(mktemp -d "$HOME/a1_sbx_km232b.XXXX")
echo "sbx=$SBX" > "$RAW/sbx_path.txt"
mkdir -p "$SBX/bin_absent" "$SBX/bin_negctrl"
cp "$H/tmux_absent" "$SBX/bin_absent/tmux"; cp "$H/tmux_negctrl" "$SBX/bin_negctrl/tmux"; chmod +x "$SBX"/bin_*/tmux
for v in main karo main_mut karo_mut; do
  V="$SBX/ver_$v"; mkdir -p "$V/scripts" "$V/lib" "$V/queue/inbox" "$V/.venv/bin"
  git -C "$REPO" show "$T:scripts/inbox_watcher.sh" > "$V/scripts/inbox_watcher.sh"
  git -C "$REPO" show "$T:lib/agent_status.sh" > "$V/lib/agent_status.sh"
  git -C "$REPO" show "$T:lib/cli_adapter.sh" > "$V/lib/cli_adapter.sh"
  ln -s "$(command -v python3)" "$V/.venv/bin/python3"
done
for v in karo karo_mut; do
  patch "$SBX/ver_$v/scripts/inbox_watcher.sh" < "$H/karo_carve.diff" >> "$RAW/patch_karo.out" 2>> "$RAW/patch_karo.err"
  echo "$v rc=$?" >> "$RAW/patch_karo.rc"
done
for v in main karo; do
  python3 "$H/mutate.py" "$SBX/ver_$v/scripts/inbox_watcher.sh" "$SBX/ver_${v}_mut/scripts/inbox_watcher.sh" >> "$RAW/mutate.out" 2>> "$RAW/mutate.err"
  echo "$v rc=$?" >> "$RAW/mutate.rc"
done
shasum -a 256 "$SBX"/ver_*/scripts/inbox_watcher.sh "$SBX"/ver_*/lib/*.sh | sed "s|$SBX/||" > "$RAW/sbx_inputs.sha256"
run() { # name ver cli mock age
  cp "$H/seed_inbox.yaml" "$SBX/ver_$2/queue/inbox/testagent.yaml"
  O="$SBX/out/$1"; mkdir -p "$O"
  printf '%s\n' "cwd=<sbx> argv=bash harness/run_case.sh <sbx>/ver_$2 $3 $4 <sbx>/out/$1 <sbx>/bin_$4 ${5:-}" >> "$RAW/argv_all.txt"
  ( cd "$SBX" && bash "$H/run_case.sh" "$SBX/ver_$2" "$3" "$4" "$O" "$SBX/bin_$4" ${5:-} ) > "$SBX/out/$1.driver.stdout" 2> "$SBX/out/$1.driver.stderr"
  echo "$1 rc=$?" >> "$RAW/driver_rc_all.txt"
}
run neg_main_claude_absent   main claude absent
run neg_main_claude_negctrl  main claude negctrl
run neg_main_codex_absent    main codex  absent
run neg_main_codex_negctrl   main codex  negctrl
run neg_main_codex_phase2    main codex  absent 150
run neg_main_codex_phase3    main codex  absent 250
run neg_karo_claude_absent   karo claude absent
run neg_karo_codex_absent    karo codex  absent
run neg_karo_codex_phase2    karo codex  absent 150
run neg_karo_codex_phase3    karo codex  absent 250
run pos_main_claude_absent   main_mut claude absent
run pos_main_codex_absent    main_mut codex  absent
run pos_karo_claude_absent   karo_mut claude absent
run pos_karo_codex_absent    karo_mut codex  absent
( cd "$SBX/out" && find . -type f | sed 's|^\./||' | LC_ALL=C sort | while IFS= read -r f; do
    printf '%s\t%s\t%s\n' "$(wc -c < "$f" | tr -d ' ')" "$(shasum -a 256 "$f" | cut -c1-64)" "$f"
  done ) > "$RAW/sizes.tsv"
( cd "$SBX/out" && find . -type f -size +0 | sed 's|^\./||' | LC_ALL=C sort ) > "$RAW/copied_nonempty.txt"
while IFS= read -r f; do mkdir -p "$RAW/out/$(dirname "$f")"; cp "$SBX/out/$f" "$RAW/out/$f"; done < "$RAW/copied_nonempty.txt"
( cd "$SBX/out" && find . -type f -size 0 | sed 's|^\./||' | LC_ALL=C sort ) > "$RAW/not_copied_empty.txt"
rm -rf "$SBX"; echo "sbx_removed_rc=$? exists_after=$(test -e "$SBX" && echo 1 || echo 0)" >> "$RAW/sbx_path.txt"
