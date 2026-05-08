#!/usr/bin/env bash
# fake_tmux.sh — bats fixture, pane_identity.sh の TMUX_CMD 差替先
#
# 環境変数で挙動制御:
#   FAKE_TMUX_PANES  — "target=value" の改行区切り文字列
#                      例: "multiagent:agents.0=hideyoshi\nmultiagent:agents.1=ashigaru1\n..."
#   FAKE_TMUX_DELAY  — list-panes -t multiagent 呼出 1 件目に sleep 秒数 (timeout テスト用)
#   FAKE_TMUX_LIST_FAIL — set with any value to make list-panes -t multiagent exit 1
#
# 対応サブコマンド:
#   has-session -t <s>          — 常に exit 0
#   list-panes -t <s> -a -F ... — FAKE_TMUX_PANES から該当 session の row を出力
#   list-panes -t <s> -F ...    — 同上 (multiagent FAKE_TMUX_DELAY/FAIL 適用)
#   list-panes -a -F ...        — 全 row 出力
#   display-message -t <tgt> -p <fmt> — FAKE_TMUX_PANES から target の値を返す

set -uo pipefail

cmd="${1:-}"
shift || true

# 引数 parser
session=""
list_all=0
target=""
fmt=""
while [ $# -gt 0 ]; do
    case "$1" in
        -t) session="${2:-}"; target="${2:-}"; shift 2 ;;
        -a) list_all=1; shift ;;
        -F) fmt="${2:-}"; shift 2 ;;
        -p) shift ;;
        *)  shift ;;
    esac
done

# panes 配列読込 (改行 or タブ区切り対応)
panes_raw="${FAKE_TMUX_PANES:-}"
# \n 文字列を実改行に変換 (env で渡しやすくするため)
panes_raw="$(printf '%b' "$panes_raw")"

case "$cmd" in
    has-session)
        # session 名をチェック (FAKE_TMUX_PANES に該当 session が含まれているか)
        if [ -z "$panes_raw" ]; then
            exit 1
        fi
        if printf '%s\n' "$panes_raw" | grep -q "^${session}:"; then
            exit 0
        fi
        exit 1
        ;;
    list-panes)
        # multiagent 限定取得時の特殊挙動 (timeout/fail テスト用)
        if [ "$list_all" = "0" ] && [ "$session" = "multiagent" ]; then
            if [ -n "${FAKE_TMUX_LIST_FAIL:-}" ]; then
                exit 1
            fi
            if [ -n "${FAKE_TMUX_DELAY:-}" ]; then
                sleep "$FAKE_TMUX_DELAY"
            fi
            # 4-way audit の format "#{pane_index}=#{@agent_id}" を想定
            printf '%s\n' "$panes_raw" \
                | grep "^multiagent:agents\." \
                | sed -E 's/^multiagent:agents\.([0-9]+)=(.*)$/\1=\2/'
            exit 0
        fi
        # 全件 or session 全 pane 表示用
        if [ "$list_all" = "1" ]; then
            # -F が "#{@agent_id}" 形式 (重複検知) なら value のみ
            if [ "$fmt" = "#{@agent_id}" ]; then
                printf '%s\n' "$panes_raw" | sed -E 's/^[^=]*=//' | grep -v '^$' || true
                exit 0
            fi
            # その他 (Pane Identity Map dump)
            printf '%s\n' "$panes_raw" | while IFS= read -r row; do
                [ -z "$row" ] && continue
                t="${row%%=*}"
                v="${row#*=}"
                echo "  $t  @agent_id=$v  pid=99999  cmd=fake"
            done
            exit 0
        fi
        # session 指定 list-panes
        printf '%s\n' "$panes_raw" | while IFS= read -r row; do
            [ -z "$row" ] && continue
            t="${row%%=*}"
            v="${row#*=}"
            if [[ "$t" == "$session:"* ]]; then
                echo "  $t  @agent_id=$v  pid=99999  cmd=fake"
            fi
        done
        exit 0
        ;;
    display-message)
        # target=multiagent:agents.X 等を lookup
        printf '%s\n' "$panes_raw" | while IFS= read -r row; do
            [ -z "$row" ] && continue
            t="${row%%=*}"
            v="${row#*=}"
            if [ "$t" = "$target" ]; then
                echo "$v"
                exit 0
            fi
        done
        # not found → empty (= pane 不在 or @agent_id 未設定 動作)
        echo ""
        exit 0
        ;;
    *)
        echo ""
        exit 0
        ;;
esac
