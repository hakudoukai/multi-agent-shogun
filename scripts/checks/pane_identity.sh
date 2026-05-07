#!/usr/bin/env bash
# pane_identity.sh — tmux pane の @agent_id 整合性検証
#
# 用途: tmux 操作前の事前チェック / 定期整合性確認
# 出力: stdout=現状一覧, stderr=違反警告
# exit: 0=整合OK, 1=warning, 2=critical (= 期待と異なる)
#
# 関連 skill: skills/pane-identity-verify/SKILL.md
# 過去事例: docs/incident_logs/2026-05-07_pane_misidentification.md

set -uo pipefail

# 設計上の期待配置 (§18 通常 4 panes; ashigaru3 は非常時 +1 で agents.4)
declare -A EXPECTED
EXPECTED["multiagent:agents.0"]=karo
EXPECTED["multiagent:agents.1"]=ashigaru1
EXPECTED["multiagent:agents.2"]=ashigaru2
EXPECTED["multiagent:agents.3"]=gunshi
EXPECTED["shogun:main.0"]=shogun

violations=0
warnings=0

echo "▼ Pane Identity Map"
for s in shogun multiagent; do
    if tmux has-session -t "$s" 2>/dev/null; then
        tmux list-panes -t "$s" -a -F '  #{session_name}:#{window_name}.#{pane_index}  @agent_id=#{@agent_id}  pid=#{pane_pid}  cmd=#{pane_current_command}' 2>&1
    else
        echo "  ⚠ session $s が存在しない" >&2
        warnings=$((warnings+1))
    fi
done

echo ""
echo "▼ 整合性検証"
for pane_target in "${!EXPECTED[@]}"; do
    expected="${EXPECTED[$pane_target]}"
    actual=$(tmux display-message -t "$pane_target" -p '#{@agent_id}' 2>/dev/null)
    if [ -z "$actual" ]; then
        if [ "$pane_target" = "shogun:main.0" ]; then
            # shogun pane は @agent_id 未設定でも OK (= claude 起動時に設定される設計)
            echo "  ⚪ $pane_target @agent_id=空 (= shogun pane、許容範囲)"
        else
            echo "  ❌ $pane_target: pane 不在 or @agent_id 未設定 (期待=$expected)" >&2
            violations=$((violations+1))
        fi
    elif [ "$actual" != "$expected" ]; then
        echo "  ❌ $pane_target: 期待=$expected 実態=$actual" >&2
        violations=$((violations+1))
    else
        echo "  ✅ $pane_target = $expected"
    fi
done

# 重複 @agent_id 検知 (= 同じ agent が複数 pane に存在)
echo ""
echo "▼ 重複 @agent_id 検知"
dup=$(tmux list-panes -a -F '#{@agent_id}' 2>/dev/null | grep -v '^$' | sort | uniq -d)
if [ -n "$dup" ]; then
    echo "  ❌ 重複検出:" >&2
    echo "$dup" | sed 's/^/     /' >&2
    violations=$((violations+1))
else
    echo "  ✅ 重複なし"
fi

# 結果
echo ""
if [ "$violations" -gt 0 ]; then
    echo "▼ 結果: ❌ $violations 件の整合性違反" >&2
    exit 2
elif [ "$warnings" -gt 0 ]; then
    echo "▼ 結果: ⚠ $warnings 件の warning"
    exit 1
else
    echo "▼ 結果: ✅ 整合性 OK"
    exit 0
fi
