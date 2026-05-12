#!/usr/bin/env bash
# SessionStart hook — 起動/resume//clear/compact 全経路で Session Start 手順を確定的に注入
#
# 公式仕様 (hooks-guide.md):
#   - matcher: startup / resume / clear / compact (全 matcher で発火させる)
#   - stdout の plain text は additionalContext として Claude の context に注入される
#   - exit 0 で正常終了。失敗しても black hole にならぬよう set -e は使わず graceful degrade
#
# 本 hook の目的:
#   shutsujin_departure.sh の STEP 6.7 (起動時 inbox broadcast) 廃止 (commit 485ab9f, 2026-02-08)
#   以降、起動時に Session Start が発火せず、persona 未確立で「自己紹介して」に対し
#   全エージェントが「我は将軍」と誤認する事故が発生 (2026-04-19)。
#   SessionStart hook で確定的に Session Start 手順を注入し、/clear・compaction も同時カバーする。
#
# Note: ashigaru5(Codex CLI), ashigaru6(Codex CLI) は Claude Code hook 対象外。
# この hook は Claude Code セッションのみで発火する。
# Codex CLI 環境では TMUX_PANE が設定されても @agent_id が未設定のため
# silent exit となり、ログも残らない（正常動作）。

set -uo pipefail

AGENT_ID=""
if [ -n "${TMUX_PANE:-}" ]; then
    AGENT_ID=$(tmux display-message -t "$TMUX_PANE" -p '#{@agent_id}' 2>/dev/null || true)
fi

# @agent_id 未設定 (= multi-agent 環境外の個人 Claude Code) → silent exit で干渉せぬ
if [ -z "$AGENT_ID" ]; then
    exit 0
fi

LOG_DIR="$(dirname "$0")/../logs"
mkdir -p "$LOG_DIR" || true
echo "[$(date -Iseconds)] $AGENT_ID session_start_hook fired" \
    >> "$LOG_DIR/session_start_hook.log" || true

# ─── inbox 整合 verify (cmd_inbox_reform AC#1) ───
# agent_id ↔ inbox_file ↔ inbox_watcher.sh args (第1引数 agent_id + 第2引数 pane_target)
# を個別照合し、各 mismatch を別個 warning として明示する。
# pgrep 単独禁 — ps -eo args= で第1引数/第2引数を厳密 parse。
# 訂正 path: warning + karo 報告 path で停止 (= ashigaru は watcher 再起動 / tmux 操作 / persona
# 切替実行禁、F002 違反 risk 防止)。
inbox_integrity_verify() {
    local agent_id="$1"
    local script_root
    # robust resolution: BASH_SOURCE for function-defining script, fallback to $0
    if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
        script_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    else
        script_root="$(cd "$(dirname "$0")/.." && pwd)"
    fi
    local current_tmux_pane="${TMUX_PANE:-}"
    local inbox_file="$script_root/queue/inbox/${agent_id}.yaml"
    local warning_count=0
    local recovery_paths=""

    # Check 1: agent_id ↔ inbox_file 個別照合
    if [ ! -f "$inbox_file" ]; then
        cat <<WARN
⚠️ WARNING #1 — agent_id ↔ inbox_file MISMATCH:
   agent_id=$agent_id
   expected inbox_file=$inbox_file
   status: FILE NOT FOUND
   可能性: persona alias (例: karo=hideyoshi、ashigaru4=maeda)
WARN
        recovery_paths+="  - inbox 不在: karo に inbox_write で 「agent_id=$agent_id 用 inbox file 不在」報告 (= 自分で alias 切替 / symlink 操作禁)"$'\n'
        warning_count=$((warning_count + 1))
    fi

    # Check 2 & 3: inbox_watcher.sh args 厳密 parse (= ps -eo args=、pgrep 単独禁)
    local watcher_found=0
    local watcher_pane_target_arg=""
    while IFS= read -r line; do
        local cmd_tail first_arg second_arg
        cmd_tail=$(echo "$line" | sed -E 's|^.*inbox_watcher\.sh[[:space:]]+||')
        first_arg=$(echo "$cmd_tail" | awk '{print $1}')
        second_arg=$(echo "$cmd_tail" | awk '{print $2}')
        if [ "$first_arg" = "$agent_id" ]; then
            watcher_found=1
            watcher_pane_target_arg="$second_arg"
            break
        fi
    done < <(ps -eo args= 2>/dev/null | grep -F 'inbox_watcher.sh' | grep -v ' grep ' || true)

    if [ "$watcher_found" -eq 0 ]; then
        cat <<WARN
⚠️ WARNING #2 — inbox_watcher.sh 第1引数 ↔ agent_id MISMATCH:
   agent_id=$agent_id
   status: 該当する inbox_watcher.sh process が見当たりません
   evidence: ps -eo args= で inbox_watcher.sh 第1引数 == $agent_id 不一致
   可能性: SC pivot directive 誤投函先 risk (= 2026-05-12 真因)
WARN
        recovery_paths+="  - watcher 不在: karo に inbox_write で 「agent_id=$agent_id 用 inbox_watcher.sh process 未起動」報告 (= 自分で watcher 再起動禁、足軽範囲外)"$'\n'
        warning_count=$((warning_count + 1))
    elif [ -n "$current_tmux_pane" ] && [ -n "$watcher_pane_target_arg" ]; then
        # Check 3: 第2引数 pane_target ↔ current pane 個別照合
        local current_index_path current_name_path
        current_index_path=$(tmux display-message -t "$current_tmux_pane" -p '#{session_name}:#{window_index}.#{pane_index}' 2>/dev/null || true)
        current_name_path=$(tmux display-message -t "$current_tmux_pane" -p '#{session_name}:#{window_name}.#{pane_index}' 2>/dev/null || true)
        if [ "$watcher_pane_target_arg" != "$current_index_path" ] && [ "$watcher_pane_target_arg" != "$current_name_path" ]; then
            cat <<WARN
⚠️ WARNING #3 — inbox_watcher.sh 第2引数 ↔ current pane MISMATCH:
   watcher pane_target arg: $watcher_pane_target_arg
   current pane (index form): $current_index_path
   current pane (name form):  $current_name_path
   可能性: watcher 起動時 pane drift、tmux session 構造変化
WARN
            recovery_paths+="  - pane drift: karo に inbox_write で 「agent_id=$agent_id watcher pane_target drift ($watcher_pane_target_arg vs 現在 $current_index_path)」報告 (= 自分で watcher 再起動禁)"$'\n'
            warning_count=$((warning_count + 1))
        fi
    fi

    if [ "$warning_count" -gt 0 ]; then
        cat <<TAIL
----
📋 訂正 path (= warning + karo 報告まで、watcher 再起動 / tmux 操作 / persona 切替実行は ashigaru 範囲外、F002 違反 risk 防止):
$recovery_paths
TAIL
    fi
    return 0
}

INBOX_VERIFY_OUTPUT=""
INBOX_VERIFY_OUTPUT=$(inbox_integrity_verify "$AGENT_ID" 2>&1 || true)
if [ -n "$INBOX_VERIFY_OUTPUT" ]; then
    echo "[$(date -Iseconds)] $AGENT_ID inbox_integrity_verify warning(s):" \
        >> "$LOG_DIR/session_start_hook.log" || true
    printf '%s\n' "$INBOX_VERIFY_OUTPUT" >> "$LOG_DIR/session_start_hook.log" || true
fi

case "$AGENT_ID" in
    shogun|karo|gunshi)
        # command-layer agents: full Session Start (Step 1-6)
        cat <<EOF
**CRITICAL: Session Start 手順を最優先で実行せよ**

貴殿は **${AGENT_ID}** である。tmux pane から確定的に読み出した事実であり、推測不要。

以下を順番に実行せよ (省略禁止、ユーザ応答/inbox 処理はこの後):

1. \`tmux display-message -t "\$TMUX_PANE" -p '#{@agent_id}'\` で自己識別を再確認
2. \`mcp__memory__read_graph\` でルール・嗜好・教訓を復元
3. (shogun のみ) \`memory/MEMORY.md\` を Read
4. \`instructions/${AGENT_ID}.md\` を最後まで必読 — persona・戦国口調・forbidden_actions 再確立 **(絶対省略禁止)**
5. \`queue/\` 配下 (tasks/, inbox/, reports/) から state 再構築
6. **inbox 整合 verify** (自動 hook 実行済) — 下記 warning があれば内容 ack の上、訂正 path に従って karo 報告 (= watcher 再起動 / tmux 操作 / persona 切替実行は禁、warning + karo 報告まで)

**Step 1-4 完了まで inbox 処理・ユーザ応答は禁止**。inbox{N} nudge が先に届いても無視し、persona 確立を優先せよ。

Rationale: 2026-04-18 に家老が「我は将軍」と役職誤認する persona 崩壊事例あり。
command-layer agent は persona + 戦国口調 + forbidden_actions の再確立が必須。

なお、本メッセージは SessionStart hook (scripts/session_start_hook.sh) が
tmux pane の @agent_id を読み出して生成したものであり、推測や混同の余地はない。
EOF
        if [ -n "$INBOX_VERIFY_OUTPUT" ]; then
            echo ""
            echo "=== inbox 整合 verify 出力 (= cmd_inbox_reform AC#1 装着 hook) ==="
            printf '%s\n' "$INBOX_VERIFY_OUTPUT"
            echo "=== end inbox 整合 verify ==="
        fi
        ;;
    ashigaru*)
        # worker agents: /clear Recovery (ashigaru only) 準拠の軽量手順
        cat <<EOF
**CRITICAL: Session Start 手順を最優先で実行せよ**

貴殿は **${AGENT_ID}** である。tmux pane から確定的に読み出した事実。

足軽用軽量手順 (CLAUDE.md「/clear Recovery (ashigaru only)」準拠):

1. \`queue/tasks/${AGENT_ID}.yaml\` を Read
   - status=assigned かつ work → タスク実行
   - idle → 待機
   - done → 待機 (再報告禁止)
2. タスクに \`project:\` があれば \`context/{project}.md\` を Read
3. タスクに \`target_path:\` があれば対象ファイルを Read
4. Step 1-3 完了後にタスク着手
5. **inbox 整合 verify** (自動 hook 実行済) — 下記 warning があれば内容 ack の上、karo へ inbox_write で報告 (= watcher 再起動 / tmux 操作 / persona 切替実行は ashigaru 範囲外、F002 違反 risk 防止)

**Step 1-2 完了まで inbox 処理・ユーザ応答は禁止**。
初回起動時は CLAUDE.md 自動ロード済み、instructions/ashigaru.md の再読は不要 (コスト節約)。

本メッセージは SessionStart hook (scripts/session_start_hook.sh) が
tmux pane の @agent_id を読み出して生成したものであり、推測や混同の余地はない。
EOF
        if [ -n "$INBOX_VERIFY_OUTPUT" ]; then
            echo ""
            echo "=== inbox 整合 verify 出力 (= cmd_inbox_reform AC#1 装着 hook) ==="
            printf '%s\n' "$INBOX_VERIFY_OUTPUT"
            echo "=== end inbox 整合 verify ==="
        fi
        ;;
    *)
        cat <<EOF
**Session Start**: agent_id=${AGENT_ID}。CLAUDE.md の Session Start 手順に従い自己の instructions/*.md を読み込め。
EOF
        if [ -n "$INBOX_VERIFY_OUTPUT" ]; then
            echo ""
            echo "=== inbox 整合 verify 出力 ==="
            printf '%s\n' "$INBOX_VERIFY_OUTPUT"
            echo "=== end inbox 整合 verify ==="
        fi
        ;;
esac

exit 0
