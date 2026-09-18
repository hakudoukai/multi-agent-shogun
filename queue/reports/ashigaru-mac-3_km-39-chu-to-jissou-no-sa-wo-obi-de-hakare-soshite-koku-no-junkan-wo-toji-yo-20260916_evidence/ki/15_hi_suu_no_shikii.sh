#!/bin/bash
# 第39弾 問一 ㋓ の裏 ―― 「閾に ★數でない字★ が入つた時どうなるか」を測る。
# ★的(stop_hook_inbox.sh)は走らせて居らぬ。★ 測るのは ★shell の素の振舞ひ★ であり、
#   的から写したのは ★L37 の set -euo pipefail★ と ★L147 の比較の形★ の二つのみ。
#   ∴ 之は「的の實行の觀測」ではない ―― ★同じ形を別の場所で演じた★ 物である。
set -u
say(){ printf '%s\n' "$*"; }

say "★的から写した形★"
say "  L37 : set -euo pipefail"
say "  L147: if [ \"\${UNREAD_COUNT:-0}\" -gt \"\$MASS_UNREAD_THRESHOLD\" ]; then"
say ""

for thr in 5 '' abc 0 -1; do
  out=$(bash -c 'set -euo pipefail; UNREAD_COUNT=3; MASS_UNREAD_THRESHOLD=${MASS_UNREAD_THRESHOLD:-5};
    if [ "${UNREAD_COUNT:-0}" -gt "$MASS_UNREAD_THRESHOLD" ]; then echo "枝=exit0(mass guard)"; else echo "枝=落ちて block へ"; fi
    echo "到達=比較の後"' MASS_UNREAD_THRESHOLD="$thr" 2>&1)
  rc=$?
  printf '閾=%-6s rc=%-3s 出目=%s\n' "'${thr}'" "$rc" "$(printf '%s' "$out" | tr '\n' '|')"
done
say ""
say "★讀み方★"
say "  ・空文字は \${VAR:-5} が呑む ∴ 5 と同じ ―― ★既定へ倒れる(安全側)★"
say "  ・★數でない字は [ が rc=2 を返し、set -e が其處で殺す★ ―― 比較の後の行へ ★到達せぬ★"
say "  ・0 や負は通る ―― ★閾 0 なら未讀 1 で既に『大量』と看做され、帯 1〜5 が ★消える★★"
say ""
say "★hook としての意味(案・据ゑて居らぬ)★"
say "  Claude Code の Stop hook は rc=2 を ★block★ と讀む。∴ 閾に非數が入ると"
say "  『未讀を數へる前に』hook が rc=2 で死に、其の stderr が block の理由として席へ返る ―― "
say "  ★即ち 帯に依らず 常に塞がる★。之は L71 の宣とも L147 の意図とも違ふ第三の出目である。"
say "  ★但し 之は ★字と shell の振舞ひから導いた案★ であり、的を走らせて確かめて居らぬ。★"
