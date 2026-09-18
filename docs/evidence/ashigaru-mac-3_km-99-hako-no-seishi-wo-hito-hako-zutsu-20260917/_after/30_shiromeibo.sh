#!/bin/bash
# ㋓ ―― inbox_write.sh L43-48 の _iw_name_list を ★逐語で写し取つて★ 走らせる器。
# 生器は読取のみ。SCRIPT_DIR は inbox_write.sh と同じ値(repo 根)を argv[1] で受ける。
SCRIPT_DIR="${1:?repo 根を渡せ}"
_iw_name_list() {
    _TMUX_BIN="$(command -v tmux 2>/dev/null || true)"
    {
        { [ -n "$_TMUX_BIN" ] && "$_TMUX_BIN" list-panes -a -F '#{@agent_id}' 2>/dev/null; } || true
        ls -1 "$SCRIPT_DIR/queue/inbox" 2>/dev/null | sed -n 's/\.yaml$//p'
    } | grep -v '^$' | grep -v '[,[:space:]]' | sort -u
}
_iw_name_list
