#!/usr/bin/env bash
# 50_gaibu.sh — ★INOTIFY_TIMEOUT の後段は [ ] だけではない★
#   L1543 gtimeout "$INOTIFY_TIMEOUT" fswatch …   (mac 路・此の環境で實測可)
#   L1552 [ "$WAITED" -lt "$INOTIFY_TIMEOUT" ]    (test(1))
#   L1567 inotifywait -q -t "$INOTIFY_TIMEOUT" …  (linux 路・★此の環境に不在=測れぬ★)
#   ★害の無い `true` を走らせるのみ。fswatch も watcher も起さぬ。★
set -u
GT="$(command -v gtimeout || true)"
if [ -z "$GT" ]; then echo "★測れぬ★ gtimeout 不在" >&2; exit 3; fi
printf '#colspec\t形札\t逐語\tgtimeout_rc\tgtimeout_stderr\t意味\n'
one(){
  tag="$1"; v="$2"; mean="$3"
  err="$("$GT" "$v" true 2>&1 >/dev/null)"; rc=$?
  printf '%s\t%s\t%s\t%s\t%s\n' "$tag" "[$v]" "$rc" "$(printf '%s' "$err" | tr '\n' ' ' | cut -c1-60)" "$mean"
}
one 07 "-0"  "番人は受けた"
one 08 "0"   "番人は受けた"
one 09 "+50" "番人は受けた"
one 10 " 50 " "番人は受けた"
one 16 "007" "番人は受けた"
one 17 "010" "番人は受けた"
one 18 "9223372036854775807" "番人は受けた"
one 21 "10m" "★番人は拒んだ★"
one 30 "30"  "既定(陰性対照)"
