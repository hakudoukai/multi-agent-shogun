#!/usr/bin/env bash
# km_ryoutaishou_kizu1.sh ―― 裁337507⑶疵① の両対照器（家老mac・2026-09-19）
#
# ★測り方の條★
#  ⑴ rc を★pipe に通さぬ★（`cmd | head` の後の $? は head の物である＝実測で偽値を出した）
#  ⑵ argv は★一語ずつ位置引数で渡す★（zsh は語分割せぬ故 "--lang ja" は一語に成る）
#  ⑶ 出は先頭3行のみ載せ、★総行数を併記★する（畳んだ事を隠さぬ為）
#  ⑷ ★己の出目も刷る★（器が死んで居れば表が空に成る）
# 引数: $1 = 測る本体の path
set -uo pipefail
# ★2026-09-19 器の疵の是正★ ―― ㋟(tmux 不在)で PATH を空 dir に据ゑると
#   `bash` 自身が PATH 越しに引けず rc=127「bash: command not found」＝★的でなく己が死ぬ★。
#   ∴ 本体は★絶対 path の bash★で起す（$BASH = 今走つて居る shell の絶対 path）。
BASH_BIN="${BASH:-/bin/bash}"
TARGET="${1:?usage: km_ryoutaishou_kizu1.sh <path to agent_status.sh>}"
echo "cwd       = $(pwd)"
echo "本体      = ${TARGET}"
echo "本体 sha  = $(shasum -a 256 "$TARGET" | awk '{print $1}')"
echo "bash      = ${BASH_VERSION} (${BASH_BIN})"
echo "tmux      = $(tmux -V 2>&1 || echo '(tmux 無し)')"
echo "刻        = $(date '+%Y-%m-%dT%H:%M:%S%z')"
echo "PATH      = ${PATH}"
echo "-----------------------------------------------------------------"
run() {   # run <名> -- <argv...>
    local name="$1"; shift; shift   # 名 と '--' を落とす
    local out rc n
    out=$("$BASH_BIN" "$TARGET" "$@" 2>&1); rc=$?
    n=$(printf '%s' "$out" | grep -c '' || true)
    echo "■ ${name}"
    echo "   argv = [$*]"
    echo "   rc   = ${rc}"
    echo "   出行数 = ${n}"
    printf '%s\n' "$out" | sed -n '1,3p' | sed 's/^/   出> /'
    echo
}
run "㋐ 引数無(project 路)"          -- 
run "㋑ --help"                      -- --help
run "㋒ -h"                          -- -h
run "㋓ --lang 値無し"               -- --lang
run "㋔ --session 値無し"            -- --session
run "㋕ --panes 値無し"              -- --panes
run "㋖ --lang 空の値"               -- --lang ""
run "㋗ --session 空の値"            -- --session ""
run "㋘ --lang の値が旗"             -- --lang --session
run "㋙ 未知の旗"                    -- --zzz
run "㋚ --lang ja(正)"               -- --lang ja
run "㋛ --session 当たる(陽性対照)"  -- --session multiagent-mac
run "㋜ --session 無い名(陰性対照)"  -- --session zzzznosuch
run "㋝ --session 前方一致の餌"      -- --session multiagent
run "㋞ --panes 該当無"              -- --session multiagent-mac --panes 99
echo "-----------------------------------------------------------------"
echo "■ ㋟ tmux 不在（PATH を空 dir へ据ゑる）"
EMPTY=$(mktemp -d)
out=$(PATH="$EMPTY" "$BASH_BIN" "$TARGET" --session multiagent-mac 2>&1); rc=$?
n=$(printf '%s' "$out" | grep -c '' || true)
echo "   argv = [--session multiagent-mac]  PATH=<空 dir>"
echo "   rc   = ${rc}"
echo "   出行数 = ${n}"
printf '%s\n' "$out" | sed -n '1,3p' | sed 's/^/   出> /'
rmdir "$EMPTY" 2>/dev/null || true
echo
echo "■ ㋠ tmux のみ不在（他の器は symlink で残す＝★㋟ の交絡を除いた形★）"
# ★㋟ の疵★: PATH を空にすると dirname まで消え SCRIPT_DIR が `//` に成る。
#   ∴ 「tmux 不在」を測るには★tmux 以外を残した PATH★が要る。
SHIM=$(mktemp -d)
for c in dirname basename awk sed grep cat date head tail cut wc tr sort uniq \
         python3 timeout gtimeout mktemp shasum env ls rm printf test; do
    w=$(command -v "$c" 2>/dev/null) || continue
    ln -sf "$w" "$SHIM/$c"
done
echo "   shim  = $(ls "$SHIM" | tr '\n' ' ')"
echo "   tmux 在否(shim) = $(PATH="$SHIM" command -v tmux 2>/dev/null || echo '(無し)')"
for arg in "--session multiagent-mac" "" ; do
    if [[ -n "$arg" ]]; then
        out=$(PATH="$SHIM" "$BASH_BIN" "$TARGET" --session multiagent-mac 2>&1); rc=$?
        lab="[--session multiagent-mac]"
    else
        out=$(PATH="$SHIM" "$BASH_BIN" "$TARGET" 2>&1); rc=$?
        lab="[]"
    fi
    n=$(printf '%s' "$out" | grep -c '' || true)
    echo "   argv = ${lab}  PATH=<tmux 以外の shim>"
    echo "   rc   = ${rc}"
    echo "   出行数 = ${n}"
    printf '%s\n' "$out" | sed -n '1,3p' | sed 's/^/   出> /'
done
rm -rf "$SHIM" 2>/dev/null || true
echo
echo "■ 器自身の出目 = 0（此処まで到達した事の證）"
