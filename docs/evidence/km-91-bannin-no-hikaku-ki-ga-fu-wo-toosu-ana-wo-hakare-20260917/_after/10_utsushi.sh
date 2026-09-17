#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# stop_hook_inbox.sh — Claude Code Stop Hook for inbox delivery
# ═══════════════════════════════════════════════════════════════
# When a Claude Code agent finishes its turn and is about to go idle,
# this hook:
#   1. Analyzes last_assistant_message to detect task completion/error
#   2. Auto-notifies karo via inbox_write (background, non-blocking)
#   3. Checks the agent's inbox for unread messages
#   4. If unread messages exist, BLOCKs the stop and feeds them back
#
# Usage: Registered as a Stop hook in .claude/settings.json
#   The hook receives JSON on stdin; outputs JSON to stdout.
#
# Environment:
#   TMUX_PANE — used to identify which agent is running
#   __STOP_HOOK_SCRIPT_DIR — override for testing (default: auto-detect)
#   __STOP_HOOK_AGENT_ID  — override for testing (default: from tmux)
#
# ─── fukuincho 段階3 全自動ループ連動 (副院長令 77bd5c6e + 341654e4 反映) ───
# 設計章節正本: docs/08-ops/fukuincho-stage3-auto-loop-design.md
#   commit f1c268d (SHA256=fcf49731df98d812ad83a3d078e01afff306c13e6b867cbc033f3541ab95fb1b)
#   governing audit: subtask_thirdpc_p1_fukuincho_stage3_design_governing_audit_001
#
# 連動責務: 段階3 poke 自動発火後の ack 配送経路温存。
#   - 副院長殿 → Commander の応答 message が inbox に届く → 本 hook が unread 検知 → block
#     して agent に処理させる経路を ★無変更で温存★ する。
#   - poke actuator (scripts/fukuincho_desktop_poke.py) や detect_stale 拡張
#     (scripts/inbox_watcher.sh 末尾) は本 hook を呼出さない (単一責務分離)。
#   - L77/L124/L157 の anchored unread grep (^  read: false$) は副院長令 fc3a5b0b
#     phantom block loop 根治済、本連動でも維持。
#
# ★本 hook = 段階3 連動 referrer のみ、code 改修なし★
# (poke 自動発火後の ack 配送経路は既存 unread→block path を温存することで成立)
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="${__STOP_HOOK_SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# ─── Read stdin (hook input JSON) ───
# ★2026-09-16 裁 seq320321⑴(313209/314012) ―― stdin を時限読みへ(家老mac 自席の器・可逆・事後1便)★
#   旧: `INPUT=$(cat)` は ★EOF が来る迄 永久に待つ★。呼び手が口を閉ぢ損ねれば席は永久に塞がる。
#   本形: bash の `read -t` を使ふ ―― 之は ★内で select(2) を待つ★ ゆゑ裁の文言其の儘。
#         `-d ''` は NUL 迄読む＝JSON に NUL は無い故、常に「EOF か時限」で戻る(rc≠0 が正常)。
#         ★時限切れでも bash は讀めた分を変数へ入れる★(man bash: saves any partial input)。
#   ★註(家老mac 實測 2026-09-16)★: 同じ裁の「全 read に timeout(10s)」は ★`cmd < "$f"` の形では効かぬ★。
#     `<` 再向は shell が open() する故、timeout が exec される前に止まる(FIFO で 120 秒 戻らなんだ)。
#     ∴ 門側は「時限」でなく ★開かぬ(stat)★ で直した。此處は fd が既に開いて居る故 時限が効く。
#   下流は json.load の失敗時に既定へ倒れる形が既に在る ∴ 空・欠けでも新しい落ち枝は要らぬ。
#   可逆: 下の塊を `INPUT=$(cat)` 一行へ戻せば旧挙動(控 = docs/evidence/karo-mac-gate-hook-fix-20260916/raw/00_hook_BEFORE.sh)。
# ★甲(裁 seq322952)★ 閾は ★後で比べる時と同じ演算子★ で検めよ ―― 旧形の glob `*[!0-9]*` は
#   20桁の十進を「數」として通すが、下の `[ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]` は
#   2^63 超で rc=2 を返し ★黙つて else(時限切れを見ぬ側)へ落つる★。
#   加へて `read -t <20桁>` は bash に ★拒まれ(invalid timeout specification)★ ―― 實測(當席 2026-09-17):
#   rc=1・★讀めた字数 0★ ∴ hook 入力 JSON を ★丸ごと落として先へ進む★。而して上の rc=2 ゆゑ ★其の事を報せぬ★。
#   裁 seq324588⑴(最重)。兄弟器 scripts/redundancy/shogun_report_watcher.sh L63-69 と同形。
num_same_op() { [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }
# ★空文字は `:-` が黙つて呑む★ ―― 裁 seq322952 乙「未設定/空文字/空白のみを分け、既定へ倒す時は必ず刷る」
#   に依り、`:-` の前で「在るが空」を分けて刷る(未設定のみ黙る = 裁 seq323687⑵ 乙′・高頻度器の許し)。
if [ -n "${STOP_HOOK_STDIN_TIMEOUT+x}" ] && [ -z "$STOP_HOOK_STDIN_TIMEOUT" ]; then
    echo "[stop_hook] ★STOP_HOOK_STDIN_TIMEOUT が空文字 — 既定 10 へ倒す(fail-closed)★" >&2
fi
STOP_HOOK_STDIN_TIMEOUT="${STOP_HOOK_STDIN_TIMEOUT:-10}"
if ! num_same_op "$STOP_HOOK_STDIN_TIMEOUT"; then
    # ★乙(裁 seq323980⑵)★ 値を己の判定路へ刷る時、改行で ★偽の報せ行★ を生やさせぬ
    case "$STOP_HOOK_STDIN_TIMEOUT" in
        *␊*|*␍*|*␉*)
            echo "[stop_hook] ★STOP_HOOK_STDIN_TIMEOUT が可視印(␊␍␉)を既に含む — 値を刷らず既定 10 へ倒す(fail-closed・裁 seq323980⑵)★" >&2 ;;
        *)
            __th_vp="${STOP_HOOK_STDIN_TIMEOUT//$'\n'/␊}"; __th_vp="${__th_vp//$'\r'/␍}"; __th_vp="${__th_vp//$'\t'/␉}"
            echo "[stop_hook] ★STOP_HOOK_STDIN_TIMEOUT を比較器が扱へぬ(「${__th_vp}」) — 既定 10 へ倒す(fail-closed)★" >&2 ;;
    esac
    STOP_HOOK_STDIN_TIMEOUT=10
fi
INPUT=""
__stdin_t0=$SECONDS
if IFS= read -r -d '' -t "$STOP_HOOK_STDIN_TIMEOUT" INPUT; then
    :
else
    __read_rc=$?
    __stdin_el=$(( SECONDS - __stdin_t0 ))
    # ★実測(家老mac 2026-09-16)★: 此の Mac の /bin/bash は 3.2 ゆゑ
    #   `read -t` は★時限切れでも rc=1★ を返す(EOF と同じ出目)。
    #   rc>128 は bash 4 以降の形であり、shebang は env bash(=brew bash 5)だが
    #   呼び手が `/bin/bash <script>` なら 3.2 で走る ―― ★両方在り得る★。
#   ★訂(當席 2026-09-17 實測)★: 此の Mac に bash 5 は ★無い★(command -v bash=/bin/bash 3.2.57・
#   /opt/homebrew/bin/bash 不在) ∴ `env bash` も 3.2 へ解ける。上の「brew bash 5」は此の機では偽。
    #   ∴ rc だけに頼らず、★経過秒★ でも分ける。
    if [ "$__read_rc" -gt 128 ] || [ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]; then
        echo "[stop_hook] ★stdin 時限切れ(${STOP_HOOK_STDIN_TIMEOUT}秒経過・rc=${__read_rc}) — 讀めた ${#INPUT} 字で続行★" >&2
    fi
fi

# ─── ↑此処まで 生器 scripts/stop_hook_inbox.sh の L1-93 逐語(一字も変へず) ───
# ─── ↓番人の口 = 生器 L117-121 を逐語で継いだ物 + 計測印(當席が足した分は ##KM91 印) ───
# ─── Infinite loop prevention ───
# When stop_hook_active=true, the agent is already continuing from a
# previous Stop hook block. Allow it to stop this time to prevent loops.
STOP_HOOK_ACTIVE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('stop_hook_active', False))" 2>/dev/null || echo "False")
##KM91 計測印: 生器は此の後 [ "$STOP_HOOK_ACTIVE" = "True" ] で番人が効く。効くか否かを刷つて終る。
printf '##KM91 timeout_used=%s read_rc=%s elapsed=%s input_len=%s stop_hook_active=%s bannin=%s\n' \
  "$STOP_HOOK_STDIN_TIMEOUT" "${__read_rc:-0}" "${__stdin_el:-0}" "${#INPUT}" "$STOP_HOOK_ACTIVE" \
  "$( [ "$STOP_HOOK_ACTIVE" = "True" ] && echo '効く' || echo '★効かぬ★' )"
exit 0
