#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# agent_pane_mapping.sh — Agent ↔ Pane mapping の SSoT helper
#
# 目的 (= 竹中 f1 是正、2026-05-10):
#   shutsujin_departure.sh / watcher_supervisor.sh / coherence_check.sh で
#   独立に実装されていた agent → pane 計算ロジックを単一 source に集約。
#   DRY 違反解消、将来の編成変更時の drift 根絶。
#
# 慣例 (= settings.yaml `cli.agents` の出現順):
#   shogun → shogun:main.0
#   karo, ashigaru1..N, gunshi, gunshi2 → multiagent:agents.{0,1,..}
#
# 提供関数:
#   apm_list_agents                  — 全 agent name を出現順で list (改行区切り)
#   apm_get_pane <agent_id>          — agent → pane (= multiagent:agents.N or shogun:main.0)
#   apm_get_pane_index <agent_id>    — pane index 数値のみ (shogun は 0)
#   apm_get_cli <agent_id>           — agent → cli (= settings.yaml の cli.agents.<agent>)
#   apm_get_all_mappings_json        — 全 agent の {pane, cli} を JSON で出力
#
# 依存: python3 (yaml module)、awk
# 使用方法:
#   source "$PROJECT_ROOT/lib/agent_pane_mapping.sh"
#   pane=$(apm_get_pane gunshi)  # → multiagent:agents.7
# ════════════════════════════════════════════════════════════════

# プロジェクトルート解決 (= source 元の cli_adapter.sh と同 pattern)
APM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APM_PROJECT_ROOT="$(cd "${APM_DIR}/.." && pwd)"
APM_SETTINGS="${APM_SETTINGS:-${APM_PROJECT_ROOT}/config/settings.yaml}"

# ─────────────────────────────────────────────────────────────
# apm_list_agents — settings.yaml の cli.agents 出現順を改行区切りで出力
# ─────────────────────────────────────────────────────────────
apm_list_agents() {
    awk '/^  agents:/{f=1;next} f&&/^  [^ ]/{exit} f&&/^[ ]{4}[A-Za-z0-9_]+:/{
        sub(/^[ ]*/,""); sub(/:.*/,""); print
    }' "$APM_SETTINGS"
}

# ─────────────────────────────────────────────────────────────
# apm_get_pane <agent_id> — agent → pane (canonical form)
#   shogun → shogun:main.0
#   それ以外 → multiagent:agents.{index} (= 出現順 0-based、shogun を除く)
# ─────────────────────────────────────────────────────────────
apm_get_pane() {
    local target="$1"
    [ -z "$target" ] && { echo ""; return 1; }

    if [ "$target" = "shogun" ]; then
        echo "shogun:main.0"
        return 0
    fi

    local idx=0
    local agent
    while read -r agent; do
        [ -z "$agent" ] && continue
        [ "$agent" = "shogun" ] && continue
        if [ "$agent" = "$target" ]; then
            echo "multiagent:agents.${idx}"
            return 0
        fi
        idx=$((idx+1))
    done < <(apm_list_agents)
    echo ""
    return 1
}

# ─────────────────────────────────────────────────────────────
# apm_get_pane_index <agent_id> — pane index 数値のみ
# ─────────────────────────────────────────────────────────────
apm_get_pane_index() {
    local target="$1"
    [ "$target" = "shogun" ] && { echo 0; return 0; }
    local pane
    pane=$(apm_get_pane "$target")
    if [[ "$pane" =~ \.([0-9]+)$ ]]; then
        echo "${BASH_REMATCH[1]}"
        return 0
    fi
    echo ""
    return 1
}

# ─────────────────────────────────────────────────────────────
# apm_get_cli <agent_id> — settings.yaml の cli.agents.<agent>
# ─────────────────────────────────────────────────────────────
apm_get_cli() {
    local target="$1"
    [ -z "$target" ] && { echo ""; return 1; }
    python3 -c "
import yaml, sys
try:
    with open('$APM_SETTINGS') as f:
        cfg = yaml.safe_load(f) or {}
    val = cfg.get('cli', {}).get('agents', {}).get('$target', '')
    print(val if val else '')
except Exception:
    print('')
" 2>/dev/null
}

# ─────────────────────────────────────────────────────────────
# apm_get_all_mappings_json — 全 agent {pane, cli} を JSON で出力
#   ─ python3 による settings.yaml 一括読込 (= 効率優先)
# ─────────────────────────────────────────────────────────────
apm_get_all_mappings_json() {
    python3 <<PY
import yaml, json
try:
    with open('$APM_SETTINGS') as f:
        cfg = yaml.safe_load(f) or {}
    agents = cfg.get('cli', {}).get('agents', {})
    out = {}
    idx = 0
    for a, cli in agents.items():
        if a == 'shogun':
            pane = 'shogun:main.0'
        else:
            pane = f'multiagent:agents.{idx}'
            idx += 1
        out[a] = {'pane': pane, 'cli': cli}
    print(json.dumps(out))
except Exception as e:
    print('{}')
PY
}

# Self-test (= source 時に何もせず、direct execution 時のみ動作確認)
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo "=== apm self-test ==="
    echo "[apm_list_agents]"
    apm_list_agents
    echo ""
    echo "[apm_get_pane gunshi]"
    apm_get_pane gunshi
    echo ""
    echo "[apm_get_pane gunshi2]"
    apm_get_pane gunshi2
    echo ""
    echo "[apm_get_cli gunshi]"
    apm_get_cli gunshi
    echo ""
    echo "[apm_get_all_mappings_json]"
    apm_get_all_mappings_json | python3 -m json.tool
fi
