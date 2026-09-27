#!/usr/bin/env bash
# b2e654902: 二版(main/fix) × 九場面 を一つづつ別 bash で走らせる。rc は管を通さず file へ。
set -u
W="$1"; E="$2"
H="$E/harness"
for ver in main fix; do
  for c in "claude absent" "claude negctrl" "claude idle" "codex absent" "codex negctrl" "codex idle" "codex idle 150" "codex absent 150" "codex absent 250"; do
    set -- $c
    name="${ver}_$1_$2${3:+_age$3}"
    OUT="$E/raw/run3_cases/$name"
    mkdir -p "$OUT"
    (cd "$W" && /bin/bash "$H/run_case.sh" "$W/.sbx/ver_$ver" "$1" "$2" "$OUT" ${3:-}) > "$OUT/driver.stdout" 2> "$OUT/driver.stderr"
    echo $? > "$OUT/driver.rc"
    printf '%s\tdriver_rc=%s\tsource_rc=%s\tprocess_unread_rc=%s\tagent_is_busy_rc=%s\tsendkeys=%s\n' "$name" "$(cat "$OUT/driver.rc")" "$(cat "$OUT/source.rc" 2>/dev/null || echo NA)" "$(cat "$OUT/process_unread.rc" 2>/dev/null || echo NA)" "$(cat "$OUT/agent_is_busy_direct.rc" 2>/dev/null || echo NA)" "$(head -1 "$OUT/sendkeys_count.txt" 2>/dev/null || echo NA)"
  done
done
