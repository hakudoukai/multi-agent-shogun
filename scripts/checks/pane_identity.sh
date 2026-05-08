#!/usr/bin/env bash
# pane_identity.sh — tmux pane の @agent_id 整合性検証 (+ 4-way mapping audit)
#
# 用途: tmux 操作前の事前チェック / 定期整合性確認 / 4-way audit (Phase 1)
# 出力: stdout=現状一覧, stderr=違反警告 (advisory)
# exit: 0=整合OK, 1=warning/未来予約, 2=不整合検出 (= advisory、絶対 block しない)
#
# Phase 1 (cmd_phase1_pane_identity_4way_audit_001):
#   既存 self-identification check は保持、4-way mapping audit を追加。
#   4 source: (a) tmux 実態 / (b) queue/pane_registry.yaml /
#             (c) scripts/watcher_supervisor.sh / (d) CLAUDE.md §18.1
#   不整合は stderr 警告 + exit 2 (= advisory only)。
#
# 関連 skill: skills/pane-identity-verify/SKILL.md
# 過去事例: docs/incident_logs/2026-05-07_pane_misidentification.md
#           docs/incident_logs/2026-05-08_pane_mapping_drift.md (Phase 0)
#
# advisory hook 原則 (CLAUDE.md §19.3 mandate):
#   - 絶対 block 禁止 (= mandate)
#   - stderr 警告のみ (= 通知層)
#   - timeout 5 秒上限 (= 内部 timeout + degraded mode)
#   - 手動停止フラグ (~/.openclaw/disable_pane_identity_hook) 尊重

set -uo pipefail

# ─── 定数 ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PANE_REGISTRY="$REPO_ROOT/queue/pane_registry.yaml"
WATCHER_SUPERVISOR="$REPO_ROOT/scripts/watcher_supervisor.sh"
CLAUDE_MD="$REPO_ROOT/CLAUDE.md"
DISABLE_FLAG="$HOME/.openclaw/disable_pane_identity_hook"
LAST_RUN_JSON="/tmp/pane_identity_last_run.json"
TIMEOUT_SECONDS=5

# 手動停止フラグ尊重 (= advisory hook 原則)
if [ -f "$DISABLE_FLAG" ]; then
    echo "▼ pane_identity hook disabled by flag: $DISABLE_FLAG"
    exit 0
fi

# ─── 既存: 設計上の期待配置 (§18 通常 4 panes; ashigaru3 は非常時 +1 で agents.4) ───
# 注意: 本 EXPECTED 定義は既存の self-identification check 用 (§18.1 とは drift あり、
# 4-way audit が drift 検出する)。topology 整合は別 cmd で対応予定。
declare -A EXPECTED
EXPECTED["multiagent:agents.0"]=hideyoshi
EXPECTED["multiagent:agents.1"]=ashigaru1
EXPECTED["multiagent:agents.2"]=ashigaru2
EXPECTED["multiagent:agents.3"]=ieyasu
EXPECTED["shogun:main.0"]=nobunaga

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
echo "▼ 整合性検証 (= 既存 self-identification check)"
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

# ============================================================================
# §X. 4-way mapping audit (Phase 1 — cmd_phase1_pane_identity_4way_audit_001)
# ============================================================================
#
# 4 source の整合性 check (= 全 source で同じ pane↔persona mapping か):
#   A. tmux 実態:                tmux list-panes (= 現実)
#   B. queue/pane_registry.yaml: 静的 SSoT mirror (= 本 cmd で雛形作成)
#   C. watchdog 配置:            scripts/watcher_supervisor.sh start_watcher_if_missing
#   D. CLAUDE.md §18.1:          markdown 配置表 (= SSoT)
#
# 不整合は stderr 警告 + exit 2 (advisory only)。block しない。

run_4way_audit() {
    local audit_corr_id
    audit_corr_id="pane4way-$(date +%s)-$$"
    local mismatch_count=0
    local source_skipped=0
    local audit_err_code="ERR-INFRA-PANE-DRIFT-001"  # 採番台帳未登録、別 cmd で登録予定

    echo ""
    echo "▼ 4-way mapping audit (corr_id=$audit_corr_id, advisory only)"

    # ── A. tmux 実態 ─────────────────────────────────────────────────
    local src_a_raw
    if src_a_raw=$(timeout "$TIMEOUT_SECONDS" tmux list-panes -t multiagent -F '#{pane_index}=#{@agent_id}' 2>/dev/null); then
        :
    else
        echo "  [WARN] source A (tmux) 取得失敗 (degraded mode)" >&2
        src_a_raw=""
        source_skipped=$((source_skipped+1))
    fi

    # ── B. queue/pane_registry.yaml ──────────────────────────────────
    local src_b_raw=""
    if [ -f "$PANE_REGISTRY" ]; then
        if ! src_b_raw=$(timeout "$TIMEOUT_SECONDS" python3 - "$PANE_REGISTRY" <<'PYEOF' 2>/dev/null
import sys, re
path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
except Exception:
    sys.exit(0)
# 単純パーサ: panes: 直下の "- tmux_target: \"multiagent:0.X\"" + agent_id ペアを
# pc=MainPC 限定で抽出する (= yaml モジュール非依存)。
in_panes = False
cur = {}
out = []
for line in text.splitlines():
    if re.match(r"^\s*panes:\s*$", line):
        in_panes = True
        continue
    if not in_panes:
        continue
    if re.match(r"^\w", line):  # 次の top-level key
        if cur:
            out.append(cur)
        in_panes = False
        break
    m = re.match(r"^\s*-\s*tmux_target:\s*\"?([^\"\s]+)\"?\s*$", line)
    if m:
        if cur:
            out.append(cur)
        cur = {"tmux_target": m.group(1)}
        continue
    m = re.match(r"^\s*(agent_id|persona|pc):\s*(\S+)\s*$", line)
    if m and cur:
        cur[m.group(1)] = m.group(2).strip("\"'")
if cur:
    out.append(cur)
# 出力: index=persona (MainPC + multiagent: のみ)
for entry in out:
    tt = entry.get("tmux_target", "")
    pc = entry.get("pc", "")
    persona = entry.get("persona") or entry.get("agent_id") or ""
    if pc != "MainPC":
        continue
    m = re.match(r"^multiagent:0?\.?(\d+)$|^multiagent:[^.]+\.(\d+)$", tt)
    if not m:
        continue
    idx = m.group(1) or m.group(2)
    print(f"{idx}={persona}")
PYEOF
        ); then
            echo "  [WARN] source B (pane_registry.yaml) 解析失敗 (degraded mode)" >&2
            src_b_raw=""
            source_skipped=$((source_skipped+1))
        fi
    else
        echo "  [WARN] source B 不在: $PANE_REGISTRY (degraded mode)" >&2
        source_skipped=$((source_skipped+1))
    fi

    # ── C. watchdog (watcher_supervisor.sh) ──────────────────────────
    local src_c_raw=""
    if [ -f "$WATCHER_SUPERVISOR" ]; then
        if ! src_c_raw=$(timeout "$TIMEOUT_SECONDS" \
            grep -E '^\s*start_watcher_if_missing\s+"[^"]+"\s+"multiagent:agents\.[0-9]+"' \
                "$WATCHER_SUPERVISOR" 2>/dev/null \
            | sed -E 's/^\s*start_watcher_if_missing\s+"([^"]+)"\s+"multiagent:agents\.([0-9]+)".*/\2=\1/'); then
            echo "  [WARN] source C (watcher_supervisor.sh) 解析失敗 (degraded mode)" >&2
            src_c_raw=""
            source_skipped=$((source_skipped+1))
        fi
    else
        echo "  [WARN] source C 不在: $WATCHER_SUPERVISOR (degraded mode)" >&2
        source_skipped=$((source_skipped+1))
    fi

    # ── D. CLAUDE.md §18.1 ───────────────────────────────────────────
    local src_d_raw=""
    if [ -f "$CLAUDE_MD" ]; then
        if ! src_d_raw=$(timeout "$TIMEOUT_SECONDS" python3 - "$CLAUDE_MD" <<'PYEOF' 2>/dev/null
import sys, re
path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
except Exception:
    sys.exit(0)
# §18.1 配置表 (MainPC 部分) のテーブル行を抽出。
# 期待 row: "|  | 家老 (karo) | multiagent:0.0 |" 形式
in_section = False
in_mainpc = False
for line in text.splitlines():
    if re.match(r"^##+\s+§18\.1\b", line):
        in_section = True
        continue
    if in_section and re.match(r"^##\s+§18\.[2-9]\b", line):
        break
    if not in_section:
        continue
    if re.search(r"^###\s+MainPC", line):
        in_mainpc = True
        continue
    if in_mainpc and re.search(r"^###\s+SecondPC", line):
        in_mainpc = False
        continue
    if not in_mainpc:
        continue
    # row pattern: | ... | <agent_label> (<id>) | multiagent:0.X |
    m = re.match(r"^\|.*\(([a-z][a-z0-9]*)\)\s*\|\s*multiagent:0?\.(\d+)\s*\|", line)
    if m:
        agent_id = m.group(1)
        idx = m.group(2)
        print(f"{idx}={agent_id}")
PYEOF
        ); then
            echo "  [WARN] source D (CLAUDE.md §18.1) 解析失敗 (degraded mode)" >&2
            src_d_raw=""
            source_skipped=$((source_skipped+1))
        fi
    else
        echo "  [WARN] source D 不在: $CLAUDE_MD (degraded mode)" >&2
        source_skipped=$((source_skipped+1))
    fi

    # ── persona alias 正規化 (= 旧名 → 新名 に統一して比較) ──
    declare -A ALIAS
    ALIAS[shogun]=nobunaga
    ALIAS[karo]=hideyoshi
    ALIAS[gunshi]=ieyasu
    ALIAS[nobunaga]=nobunaga
    ALIAS[hideyoshi]=hideyoshi
    ALIAS[ieyasu]=ieyasu
    ALIAS[maeda]=maeda
    ALIAS[takenaka]=takenaka

    normalize() {
        local name="$1"
        local resolved="${ALIAS[$name]:-$name}"
        echo "$resolved"
    }

    # raw → 連想配列 (index → normalized persona)
    declare -A SRC_A SRC_B SRC_C SRC_D
    # shellcheck disable=SC2034  # nameref via local -n, shellcheck false positive
    parse_into() {
        local -n target=$1
        local raw=$2
        local line idx val
        while IFS= read -r line; do
            [ -z "$line" ] && continue
            idx="${line%%=*}"
            val="${line#*=}"
            [ -z "$idx" ] && continue
            [ -z "$val" ] && continue
            target["$idx"]=$(normalize "$val")
        done <<< "$raw"
    }
    parse_into SRC_A "$src_a_raw"
    parse_into SRC_B "$src_b_raw"
    parse_into SRC_C "$src_c_raw"
    parse_into SRC_D "$src_d_raw"

    # ── 4-way 比較 ────────────────────────────────────────────────────
    # 全 index (0..5) を走査し、4 source の値を表示 + 不整合検出
    declare -A drift_dump  # index → "A=v1 B=v2 C=v3 D=v4"
    local idx
    echo "  ── per-index comparison (multiagent: のみ、shogun は別 source 確認) ──"
    printf "  %-5s %-12s %-12s %-12s %-12s %s\n" "idx" "A:tmux" "B:registry" "C:watchdog" "D:§18.1" "status"
    for idx in 0 1 2 3 4 5; do
        local va="${SRC_A[$idx]:-}"
        local vb="${SRC_B[$idx]:-}"
        local vc="${SRC_C[$idx]:-}"
        local vd="${SRC_D[$idx]:-}"
        # 全 source 不在 → スキップ
        if [ -z "$va" ] && [ -z "$vb" ] && [ -z "$vc" ] && [ -z "$vd" ]; then
            continue
        fi
        # 既知値の集合を作る (= 空でないものだけ)
        local values=()
        [ -n "$va" ] && values+=("$va")
        [ -n "$vb" ] && values+=("$vb")
        [ -n "$vc" ] && values+=("$vc")
        [ -n "$vd" ] && values+=("$vd")
        # ユニーク数をカウント
        local unique
        unique=$(printf '%s\n' "${values[@]}" | sort -u | wc -l)
        local status_mark
        if [ "$unique" = "1" ]; then
            status_mark="✅ match"
        else
            status_mark="❌ DRIFT"
            drift_dump["$idx"]="A=${va:-_} B=${vb:-_} C=${vc:-_} D=${vd:-_}"
            mismatch_count=$((mismatch_count+1))
        fi
        printf "  %-5s %-12s %-12s %-12s %-12s %s\n" \
            "$idx" "${va:-_}" "${vb:-_}" "${vc:-_}" "${vd:-_}" "$status_mark"
    done

    # ── 結果 ──────────────────────────────────────────────────────────
    local audit_end_ts
    audit_end_ts=$(date -Iseconds 2>/dev/null || date "+%Y-%m-%dT%H:%M:%S%z")
    local last_run_status
    if [ "$mismatch_count" -gt 0 ]; then
        last_run_status="drift"
        echo ""
        echo "  ▼ 4-way audit 結果: ❌ $mismatch_count 件の drift (advisory)" >&2
        # WARN line (= human-readable)
        for idx in "${!drift_dump[@]}"; do
            echo "    [WARN] pane drift detected at index $idx: ${drift_dump[$idx]}" >&2
        done
        # JSON line (= structured)
        echo "    {\"timestamp\":\"$audit_end_ts\",\"level\":\"WARN\",\"source\":\"pane_identity_4way\",\"corr_id\":\"$audit_corr_id\",\"err_code\":\"$audit_err_code\",\"mismatch_count\":$mismatch_count,\"sources_skipped\":$source_skipped,\"advisory\":true}" >&2
        # dump 保存 (= /tmp/pane_identity_drift_<ts>.json)
        local dump_file="/tmp/pane_identity_drift_${audit_corr_id}.json"
        {
            echo "{"
            echo "  \"corr_id\": \"$audit_corr_id\","
            echo "  \"timestamp\": \"$audit_end_ts\","
            echo "  \"err_code\": \"$audit_err_code\","
            echo "  \"sources_skipped\": $source_skipped,"
            echo "  \"mismatches\": {"
            local first=1
            for idx in "${!drift_dump[@]}"; do
                if [ "$first" = "1" ]; then first=0; else echo ","; fi
                printf '    "%s": "%s"' "$idx" "${drift_dump[$idx]}"
            done
            echo ""
            echo "  }"
            echo "}"
        } > "$dump_file" 2>/dev/null || true
        echo "    pane drift detected, advisory only — see $dump_file for details" >&2
    else
        last_run_status="ok"
        echo "  ▼ 4-way audit 結果: ✅ 全 source 整合 (sources_skipped=$source_skipped)"
    fi

    # ── 最終実行情報 (/tmp/pane_identity_last_run.json) ──
    {
        echo "{"
        echo "  \"timestamp\": \"$audit_end_ts\","
        echo "  \"corr_id\": \"$audit_corr_id\","
        echo "  \"status\": \"$last_run_status\","
        echo "  \"mismatch_count\": $mismatch_count,"
        echo "  \"sources_skipped\": $source_skipped,"
        echo "  \"advisory\": true"
        echo "}"
    } > "$LAST_RUN_JSON" 2>/dev/null || true

    # exit code 用に mismatch_count を返す
    return "$mismatch_count"
}

# 4-way audit を実行
audit_mismatches=0
if run_4way_audit; then
    audit_mismatches=0
else
    audit_mismatches=$?
fi

# 結果
echo ""
if [ "$violations" -gt 0 ] || [ "$audit_mismatches" -gt 0 ]; then
    if [ "$violations" -gt 0 ]; then
        echo "▼ 結果: ❌ $violations 件の整合性違反 + $audit_mismatches 件の 4-way drift" >&2
    else
        echo "▼ 結果: ⚠ $audit_mismatches 件の 4-way drift (advisory)" >&2
    fi
    exit 2
elif [ "$warnings" -gt 0 ]; then
    echo "▼ 結果: ⚠ $warnings 件の warning"
    exit 1
else
    echo "▼ 結果: ✅ 整合性 OK + 4-way audit PASS"
    exit 0
fi
