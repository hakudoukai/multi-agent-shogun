#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# switch_cli.sh — エージェントのCLIセッションを安全に切り替える
#
# Usage:
#   bash scripts/switch_cli.sh <agent_id> [--type <cli_type>] [--model <model_name>]
#
# Examples:
#   # settings.yaml の現在値で再起動（CLI種別/モデル変更なし）
#   bash scripts/switch_cli.sh ashigaru3
#
#   # Codex Spark → Claude Sonnet に切替
#   bash scripts/switch_cli.sh ashigaru3 --type claude --model claude-sonnet-4-6
#
#   # 同一CLI内でモデルだけ変更（Sonnet → Opus）
#   bash scripts/switch_cli.sh ashigaru3 --model claude-opus-4-6
#
#   # 全足軽を一括切替 (§18 配置: 1-3 + 5-8、4 は欠番)
#   for i in 1 2 3 5 6 7 8; do bash scripts/switch_cli.sh ashigaru$i --type claude --model claude-sonnet-4-6; done
#
# Flow:
#   1. (Optional) settings.yaml を更新
#   2. 現在のCLIに /exit を送信
#   3. シェルプロンプトの復帰を待機
#   4. build_cli_command() で新CLIコマンドを構築
#   5. tmux send-keys で新CLIを起動
#   6. tmux pane metadata を更新（@agent_cli, @model_name）
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SETTINGS_FILE="${PROJECT_ROOT}/config/settings.yaml"
LOG_FILE="${PROJECT_ROOT}/logs/switch_cli.log"

# cli_adapter.sh + §18 役名定義をロード
source "${PROJECT_ROOT}/lib/cli_adapter.sh"
source "${PROJECT_ROOT}/lib/_section18_roles.sh"

# ─── ログ ───
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [switch_cli] $*"
    echo "$msg" >&2
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

# ─── Usage ───
usage() {
    echo "Usage: $0 <agent_id> [--type <cli_type>] [--model <model_name>]"
    echo ""
    echo "  agent_id   karo, ashigaru1-3, ashigaru5-8, gunshi (§18: 4 = 欠番)"
    echo "  --type     claude | codex | copilot | kimi"
    echo "  --model    claude-sonnet-4-6 | claude-opus-4-6 | gpt-5.3-codex | etc."
    echo ""
    echo "If --type/--model omitted, uses current settings.yaml values."
    exit 1
}

# ─── Agent ID → tmux pane 解決 ───
# @agent_id メタデータから動的にペインを検索する（ペイン番号のズレに対応）
# フォールバック: メタデータが見つからない場合は従来の固定マッピングを使用
resolve_pane() {
    local agent_id="$1"

    # Phase 1: @agent_id メタデータから動的検索
    local pane_count
    pane_count=$(tmux list-panes -t "multiagent:agents" 2>/dev/null | wc -l)
    if [[ "$pane_count" -gt 0 ]]; then
        for i in $(seq 0 $((pane_count - 1))); do
            local aid
            aid=$(tmux display-message -t "multiagent:agents.$i" -p '#{@agent_id}' 2>/dev/null)
            if [[ "$aid" == "$agent_id" ]]; then
                echo "multiagent:agents.$i"
                return 0
            fi
        done
        log "WARN: @agent_id=$agent_id not found in any pane. Falling back to fixed mapping."
    fi

    # Phase 2: フォールバック（§18 配置に基づく MainPC pane 固定マッピング）
    #
    # cycle1 三者監査 B2/R2 fix: 旧実装は SecondPC ashigaru5-8 にも multiagent:agents.5-8
    # を返していたが、これは MainPC 上では存在しない pane (= 別 agent の pane を踏みかねない)。
    # 動的検索失敗時に send-keys で送信先を誤ると、model_switch / clear_command が
    # 別 agent に届く事故になるため、SecondPC agent には明示エラー終了を返す。
    #
    # SecondPC で switch_cli を実行する場合は、SecondPC 側 tmux で本スクリプトを
    # 実行する想定 (Phase 1 の @agent_id 動的検索が SecondPC tmux 内で成立する)。
    # MainPC から SecondPC を跨ぐ switch_cli は本スクリプト範囲外。
    local pane_base
    pane_base=$(tmux show-options -t multiagent -v @pane_base 2>/dev/null || echo "0")

    # SecondPC agent: 動的検索失敗時はエラー終了 (B2/R2 fix)
    if section18_is_secondpc_agent "$agent_id"; then
        log "ERROR: SecondPC agent ($agent_id) の pane が動的検索で見つかりませんでした。"
        log "       SecondPC tmux 上で本スクリプトを実行するか、@agent_id metadata を確認してください。"
        log "       (CLAUDE.md §18.1: SecondPC は別 tmux session、MainPC からの fallback 不可)"
        return 1
    fi

    # MainPC agent: SECTION18_MAINPC_PANE_ORDER 順で pane index を解決
    local mainpc_idx
    if mainpc_idx=$(section18_mainpc_pane_index "$agent_id" 2>/dev/null); then
        echo "multiagent:agents.$((pane_base + mainpc_idx))"
        return 0
    fi

    log "ERROR: Unknown agent_id: $agent_id (§18: ashigaru4 は欠番)"
    return 1
}

# ─── settings.yaml 更新 (Python使用) ───
update_settings_yaml() {
    local agent_id="$1"
    local new_type="${2:-}"
    local new_model="${3:-}"

    if [[ -z "$new_type" && -z "$new_model" ]]; then
        return 0
    fi

    log "Updating settings.yaml: ${agent_id} → type=${new_type:-<unchanged>}, model=${new_model:-<unchanged>}"

    "${PROJECT_ROOT}/.venv/bin/python3" << PYEOF
import yaml, sys, os, datetime

settings_path = "${SETTINGS_FILE}"
agent_id = "${agent_id}"
new_type = "${new_type}" or None
new_model = "${new_model}" or None

with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

with open(settings_path, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f) or {}

cli = data.setdefault('cli', {})
agents = cli.setdefault('agents', {})
agent_cfg = agents.get(agent_id)
if not isinstance(agent_cfg, dict):
    agent_cfg = {}
    agents[agent_id] = agent_cfg

timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
comment = f"# {timestamp}: switch_cli.sh による切替"

if new_type:
    agent_cfg['type'] = new_type
if new_model:
    agent_cfg['model'] = new_model

data['cli']['agents'][agent_id] = agent_cfg

# コメント保持のため、対象エージェント行だけsedで置換する方が安全だが
# 完全性のためyaml.dumpを使用。コメントは失われる。
# → 代わりにsed的なアプローチ: 対象ブロックだけ書き換える

# Simple approach: read lines, find agent block, replace
lines = content.split('\n')
new_lines = []
in_agent_block = False
agent_indent = None
skip_until_next = False

i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.lstrip()

    # Detect our agent's block start
    if stripped.startswith(f'{agent_id}:'):
        in_agent_block = True
        agent_indent = len(line) - len(stripped)
        new_lines.append(line)
        # Write the updated fields
        inner_indent = ' ' * (agent_indent + 2)
        if new_type:
            new_lines.append(f'{inner_indent}type: {new_type}')
        if new_model:
            new_lines.append(f'{inner_indent}model: {new_model}  {comment}')
        # Skip old sub-fields
        i += 1
        while i < len(lines):
            next_line = lines[i]
            next_stripped = next_line.lstrip()
            if next_stripped == '' or next_stripped.startswith('#'):
                # Keep blank lines and comments between blocks
                if next_stripped.startswith('#') and len(next_line) - len(next_stripped) > agent_indent:
                    i += 1
                    continue
                break
            next_indent = len(next_line) - len(next_stripped)
            if next_indent <= agent_indent:
                break  # Next agent or section
            i += 1
        in_agent_block = False
        continue
    else:
        new_lines.append(line)
    i += 1

with open(settings_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))
    if not content.endswith('\n'):
        pass
    else:
        f.write('\n') if not '\n'.join(new_lines).endswith('\n') else None

print("OK")
PYEOF
}

# ─── 現在のCLI種別を取得（tmux metadata） ───
get_current_pane_cli() {
    local pane="$1"
    tmux show-options -p -t "$pane" -v @agent_cli 2>/dev/null | tr -d '[:space:]' || echo "claude"
}

# ─── /exit送信 ───
send_exit() {
    local pane="$1"
    local current_cli="$2"

    log "Sending exit command to ${pane} (current CLI: ${current_cli})"

    case "$current_cli" in
        codex)
            # Codex: suggestion UI dismissal → Ctrl-C → /exit
            tmux send-keys -t "$pane" Escape 2>/dev/null || true
            sleep 0.3
            tmux send-keys -t "$pane" C-c 2>/dev/null || true
            sleep 0.5
            tmux send-keys -t "$pane" "/exit" 2>/dev/null || true
            sleep 0.3
            tmux send-keys -t "$pane" Enter 2>/dev/null || true
            ;;
        claude)
            tmux send-keys -t "$pane" "/exit" 2>/dev/null || true
            sleep 0.3
            tmux send-keys -t "$pane" Enter 2>/dev/null || true
            ;;
        copilot|kimi)
            tmux send-keys -t "$pane" C-c 2>/dev/null || true
            sleep 0.5
            tmux send-keys -t "$pane" "/exit" 2>/dev/null || true
            sleep 0.3
            tmux send-keys -t "$pane" Enter 2>/dev/null || true
            ;;
        *)
            tmux send-keys -t "$pane" "/exit" 2>/dev/null || true
            sleep 0.3
            tmux send-keys -t "$pane" Enter 2>/dev/null || true
            ;;
    esac
}

# ─── シェルプロンプト待ち（最大15秒） ───
wait_for_shell_prompt() {
    local pane="$1"
    local max_wait=15
    local waited=0

    log "Waiting for shell prompt on ${pane}..."

    while [ "$waited" -lt "$max_wait" ]; do
        sleep 1
        waited=$((waited + 1))

        local last_lines
        last_lines=$(tmux capture-pane -t "$pane" -p 2>/dev/null | grep -v '^$' | tail -3)

        # シェルプロンプトの検出パターン
        # PS1にはカスタムプロンプト（shutsujin由来）や標準的な$/%が含まれる
        if echo "$last_lines" | grep -qE '[\$%#❯►] *$'; then
            log "Shell prompt detected after ${waited}s"
            return 0
        fi

        # "exit" / "Bye" 等のCLI終了メッセージを検出
        if echo "$last_lines" | grep -qiE '(bye|goodbye|exiting|exit)'; then
            sleep 1  # 終了メッセージの後、プロンプトが出るまで少し待つ
            log "CLI exit message detected after ${waited}s"
            return 0
        fi
    done

    log "WARN: Shell prompt not detected after ${max_wait}s. Proceeding anyway."
    return 0  # タイムアウトしても続行（最悪でもコマンドが送られるだけ）
}

# ─── モデル表示名の正規化（cli_adapter.sh の get_model_display_name を使用） ───
# get_model_display_name は cli_adapter.sh から source 済み

# ─── tmux pane metadata 更新 ───
update_pane_metadata() {
    local pane="$1"
    local new_cli_type="$2"
    local display_name="$3"

    log "Updating pane metadata: @agent_cli=${new_cli_type}, @model_name=${display_name}"

    tmux set-option -p -t "$pane" @agent_cli "$new_cli_type" 2>/dev/null || true
    tmux set-option -p -t "$pane" @model_name "$display_name" 2>/dev/null || true
    tmux select-pane -t "$pane" -T "$display_name" 2>/dev/null || true
}

# ═══════════════════════════════════════════════════════════════
# メイン処理
# ═══════════════════════════════════════════════════════════════

# 引数パース
if [ $# -lt 1 ]; then
    usage
fi

# --help が第1引数の場合
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    usage
fi

AGENT_ID="$1"
shift

NEW_TYPE=""
NEW_MODEL=""

while [ $# -gt 0 ]; do
    case "$1" in
        --type)
            NEW_TYPE="$2"
            shift 2
            ;;
        --model)
            NEW_MODEL="$2"
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            ;;
    esac
done

# バリデーション
if [[ -n "$NEW_TYPE" ]] && ! _cli_adapter_is_valid_cli "$NEW_TYPE"; then
    log "ERROR: Invalid CLI type: ${NEW_TYPE}. Allowed: ${CLI_ADAPTER_ALLOWED_CLIS}"
    exit 1
fi

# Step 0: pane解決
PANE_TARGET=$(resolve_pane "$AGENT_ID")
if [ -z "$PANE_TARGET" ]; then
    exit 1
fi
log "=== Starting CLI switch for ${AGENT_ID} (pane: ${PANE_TARGET}) ==="

# Step 0.5: --model指定時に--type未指定なら、モデル名からCLI種別を自動推定
if [[ -n "$NEW_MODEL" && -z "$NEW_TYPE" ]]; then
    case "$NEW_MODEL" in
        gpt-5.3-codex*|gpt-5-codex*)
            NEW_TYPE="codex"
            log "Auto-inferred type=codex from model=${NEW_MODEL}"
            ;;
        claude-*)
            NEW_TYPE="claude"
            log "Auto-inferred type=claude from model=${NEW_MODEL}"
            ;;
    esac
fi

# Step 1: settings.yaml 更新（--type/--model 指定時のみ）
if [[ -n "$NEW_TYPE" || -n "$NEW_MODEL" ]]; then
    update_settings_yaml "$AGENT_ID" "$NEW_TYPE" "$NEW_MODEL"
fi

# Step 2: 切替後のCLI情報を取得（settings.yaml反映後）
TARGET_CLI_TYPE=$(get_cli_type "$AGENT_ID")
TARGET_MODEL=$(get_agent_model "$AGENT_ID")
TARGET_CMD=$(build_cli_command "$AGENT_ID")

log "Target: cli=${TARGET_CLI_TYPE}, model=${TARGET_MODEL}, cmd=${TARGET_CMD}"

# Step 3: 現在のCLIを /exit で終了
CURRENT_CLI=$(get_current_pane_cli "$PANE_TARGET")
log "Current CLI: ${CURRENT_CLI}"
send_exit "$PANE_TARGET" "$CURRENT_CLI"

# Step 4: シェルプロンプトを待つ
wait_for_shell_prompt "$PANE_TARGET"

# Step 5: 新しいCLIコマンドを送信
log "Launching new CLI: ${TARGET_CMD}"
tmux send-keys -t "$PANE_TARGET" "$TARGET_CMD" 2>/dev/null || true
sleep 0.3
tmux send-keys -t "$PANE_TARGET" Enter 2>/dev/null || true

# Step 6: tmux pane metadata 更新
DISPLAY_NAME=$(get_model_display_name "$AGENT_ID")
update_pane_metadata "$PANE_TARGET" "$TARGET_CLI_TYPE" "$DISPLAY_NAME"

log "=== CLI switch complete: ${AGENT_ID} → ${TARGET_CLI_TYPE}/${TARGET_MODEL} (${DISPLAY_NAME}) ==="
echo "OK: ${AGENT_ID} → ${TARGET_CLI_TYPE}/${TARGET_MODEL}"
