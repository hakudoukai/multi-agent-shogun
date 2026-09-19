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
# cycle2 fix (subtask_pane_identity_4way_audit_001_cycle2):
#   M1 — return code modulo 256 wrap 解消: 0/1 のみ return、count は MISMATCH_COUNT_GLOBAL
#         グローバル変数で伝達 (mismatch=256 件以上で 0 と誤判定する Codex B1 対応)。
#   M2 — global timeout budget: SECONDS タイマで 5 秒上限を全 source 集計で強制、
#         各 subprocess は 2 秒以下個別 timeout、budget 超過時は残 source skip。
#   S1 — CLAUDE.md §18.1 parser を `awk -F'|'` で column 指定に変更 (列 3=エージェント、列 4=pane)。
#   S2 — drift dump file を `mktemp` + `umask 077` で安全生成 (symlink/clobber 攻撃対策)。
#   S3 — persona alias を lib/_section18_roles.sh の SECTION18_ROLE_ALIASES から動的 load、
#         本スクリプト内 hardcode は fallback (degraded) のみ。
#
# 関連 skill: skills/pane-identity-verify/SKILL.md
# 過去事例: docs/incident_logs/2026-05-07_pane_misidentification.md
#           docs/incident_logs/2026-05-08_pane_mapping_drift.md (Phase 0)
#
# advisory hook 原則 (CLAUDE.md §19.3 mandate):
#   - 絶対 block 禁止 (= mandate)
#   - stderr 警告のみ (= 通知層)
#   - timeout 5 秒上限 (= 内部 global budget + degraded mode)
#   - 手動停止フラグ (~/.openclaw/disable_pane_identity_hook) 尊重

set -uo pipefail

# /tmp dump file の symlink/clobber 攻撃対策 (cycle2 S2)
umask 077

# ─── 定数 ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
# bats test 用 env var override (= ":=" は env で set 済の値を尊重)
: "${PANE_REGISTRY:=$REPO_ROOT/queue/pane_registry.yaml}"
: "${WATCHER_SUPERVISOR:=$REPO_ROOT/scripts/watcher_supervisor.sh}"
: "${CLAUDE_MD:=$REPO_ROOT/CLAUDE.md}"
: "${SECTION18_ROLES_LIB:=$REPO_ROOT/lib/_section18_roles.sh}"
: "${DISABLE_FLAG:=$HOME/.openclaw/disable_pane_identity_hook}"
: "${LAST_RUN_JSON:=/tmp/pane_identity_last_run.json}"
: "${TMUX_CMD:=tmux}"

# cycle2 M2: timeout 戦略
#   - TIMEOUT_GLOBAL_SECONDS: 全 4-way audit の合計上限 (SECONDS タイマで強制)
#   - TIMEOUT_PER_SOURCE_SECONDS: 個別 subprocess の上限 (こちらは現実的に小さく)
TIMEOUT_GLOBAL_SECONDS=5
TIMEOUT_PER_SOURCE_SECONDS=2

# cycle2 M1: count 伝達はグローバル変数経由 (return modulo 256 wrap 解消)
# shellcheck disable=SC2034  # bats test + 外部 caller (e.g. dashboard) が参照
MISMATCH_COUNT_GLOBAL=0
# shellcheck disable=SC2034
SOURCES_SKIPPED_GLOBAL=0
# shellcheck disable=SC2034
LAST_AUDIT_STATUS_GLOBAL="unknown"

# 手動停止フラグ尊重 (= advisory hook 原則)
if [ -f "$DISABLE_FLAG" ]; then
    echo "▼ pane_identity hook disabled by flag: $DISABLE_FLAG"
    exit 0
fi

# ─── cycle2 S3: persona alias 単一 source 化 ──────────────────────────
# lib/_section18_roles.sh から SECTION18_ROLE_ALIASES を load (= 二重管理解消)。
# load 失敗時は最小 fallback (= degraded、機能継続)。
ALIAS_NORMALIZE_OK=0
if [ -f "$SECTION18_ROLES_LIB" ]; then
    # shellcheck disable=SC1090
    if source "$SECTION18_ROLES_LIB" 2>/dev/null; then
        if declare -F section18_resolve_alias >/dev/null 2>&1; then
            ALIAS_NORMALIZE_OK=1
        fi
    fi
fi

# normalize_persona — 旧名 → 新名 (= 4 source 比較時の正規化)
# 単一 source: lib/_section18_roles.sh の section18_resolve_alias 関数を利用 (S3)
# fallback: load 失敗時は最小 alias map (= degraded)
normalize_persona() {
    local name="$1"
    [ -z "$name" ] && { echo ""; return 0; }
    if [ "$ALIAS_NORMALIZE_OK" = "1" ]; then
        section18_resolve_alias "$name"
    else
        case "$name" in
            shogun) echo nobunaga ;;
            karo)   echo hideyoshi ;;
            gunshi) echo ieyasu ;;
            *)      echo "$name" ;;
        esac
    fi
}

# ─── 既存: 設計上の期待配置 (§18 通常 5 + 非常時 +1) ───────────────────
# 注意: 本 EXPECTED 定義は既存の self-identification check 用 (§18.1 と同等)。
# ★bash 3.2 対応 (2026-09-19 家老mac・裁 seq337297)★
# declare -A は 3.2 で invalid option であり、続く添字代入が算術評価され
# set -u で shell が落ちる。∴ ★改行区切りの表 + 関数引き★ へ改める。
# ★km-214 (2026-09-19 專任1・裁 seq337388㋑)★ 期待表は手書きせず ★queue/pane_registry.yaml から引く★
#   (理「手で表へ足せば腐る」)。鍵 = tmux_target 逐語・値 = persona(無ければ agent_id)。
#   対象 = pc: MainPC かつ status: 通常運用。registry 無し / parse 不能 / 席 0 / python 無し の四形は
#   ★各々別の出目で fail-closed★(黙つて空表へ倒れず violations に数へる)。
#   引く手は .venv/bin/python3(env PYTHON で上書き可・無ければ PATH の python3・其れも無ければ fail-closed)。
: "${PYTHON:=$REPO_ROOT/.venv/bin/python3}"
if [ ! -x "$PYTHON" ]; then
    if command -v python3 >/dev/null 2>&1; then PYTHON="$(command -v python3)"; else PYTHON=""; fi
fi
EXPECTED_TABLE=""
EXPECTED_TABLE_STATE=""   # ok / no_python / no_registry / parse_error / empty
if [ -z "$PYTHON" ]; then
    EXPECTED_TABLE_STATE="no_python"
elif [ ! -f "$PANE_REGISTRY" ]; then
    EXPECTED_TABLE_STATE="no_registry"
else
    if EXPECTED_TABLE=$("$PYTHON" - "$PANE_REGISTRY" <<'PYEOF' 2>/dev/null
import sys
try:
    import yaml
    d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
    panes = (d or {}).get("pane_registry", {}).get("panes") or []
except Exception as e:
    sys.exit(3)
rows = []
for p in panes:
    if not isinstance(p, dict):
        continue
    if p.get("pc") != "MainPC" or p.get("status") != "通常運用":
        continue
    tt = str(p.get("tmux_target") or "").strip()
    who = str(p.get("persona") or p.get("agent_id") or "").strip()
    if tt and who and " " not in tt:
        rows.append(f"{tt}={who}")
if not rows:
    sys.exit(4)
print("\n".join(rows))
PYEOF
    ); then
        EXPECTED_TABLE_STATE="ok"
    else
        _rc=$?
        if [ "$_rc" -eq 4 ]; then EXPECTED_TABLE_STATE="empty"; else EXPECTED_TABLE_STATE="parse_error"; fi
        EXPECTED_TABLE=""
    fi
fi

# 表から値を引く (見つからぬなら空・常に rc=0)
table_get() {
    local tbl="$1" want="$2" line
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        if [ "${line%%=*}" = "$want" ]; then
            echo "${line#*=}"
            return 0
        fi
    done <<< "$tbl"
    echo ""
    return 0
}

# 表の鍵を列べる (鍵に空白を含まぬことが前提)
table_keys() {
    local line
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        echo "${line%%=*}"
    done <<< "$1"
}

violations=0
warnings=0

# ★km-214★ 期待表の四形を先に刷る(fail-closed・黙らぬ)
case "$EXPECTED_TABLE_STATE" in
    ok)          echo "  ▷ 期待表 = $PANE_REGISTRY から $(table_keys "$EXPECTED_TABLE" | grep -c .) 席 (MainPC・通常運用) を引いた" ;;
    no_python)   echo "  ❌ 期待表を引けぬ: python3 が無い (.venv/bin/python3 も PATH も) ―― fail-closed" >&2; violations=$((violations+1)) ;;
    no_registry) echo "  ❌ 期待表を引けぬ: registry 不在 $PANE_REGISTRY ―― fail-closed" >&2; violations=$((violations+1)) ;;
    parse_error) echo "  ❌ 期待表を引けぬ: registry を parse できぬ $PANE_REGISTRY ―― fail-closed" >&2; violations=$((violations+1)) ;;
    empty)       echo "  ❌ 期待表を引けぬ: registry に MainPC・通常運用 の席が 0 ―― fail-closed" >&2; violations=$((violations+1)) ;;
    *)           echo "  ❌ 期待表の状態が不明 [$EXPECTED_TABLE_STATE] ―― fail-closed" >&2; violations=$((violations+1)) ;;
esac

echo "▼ Pane Identity Map"
# ★km-214 (裁 seq337507⑶疵②)★ -t は ★=名★(完全一致)。前方一致は生きた別 session(例 multiagent-mac)を掴む。
for s in shogun multiagent; do
    if "$TMUX_CMD" has-session -t "=$s" 2>/dev/null; then
        "$TMUX_CMD" list-panes -t "=$s" -a -F '  #{session_name}:#{window_name}.#{pane_index}  @agent_id=#{@agent_id}  pid=#{pane_pid}  cmd=#{pane_current_command}' 2>&1
    else
        echo "  ⚠ session $s が存在しない" >&2
        warnings=$((warnings+1))
    fi
done

echo ""
echo "▼ 整合性検証 (= 既存 self-identification check)"
for pane_target in $(table_keys "$EXPECTED_TABLE"); do
    expected=$(table_get "$EXPECTED_TABLE" "$pane_target")
    # ★km-214★ display-message/list-panes は目標が無い時 TMUX の中では今の client へ黙つて落ちる(実測 raw/21)。
    #   ∴ 先づ session を完全一致で確かめ、無ければ比較せず「session 不在」と刷る(fail-closed: 掴み違ひを防ぐ)。
    _sess="${pane_target%%:*}"
    if ! "$TMUX_CMD" has-session -t "=$_sess" 2>/dev/null; then
        echo "  ⚠ $pane_target: session $_sess が無い(完全一致) ―― 比較せず (期待=$expected)" >&2
        warnings=$((warnings+1))
        continue
    fi
    actual=$("$TMUX_CMD" display-message -t "=$pane_target" -p '#{@agent_id}' 2>/dev/null)
    if [ -z "$actual" ]; then
        case "$pane_target" in shogun:*) _is_shogun=1 ;; *) _is_shogun=0 ;; esac
        if [ "$_is_shogun" -eq 1 ]; then
            echo "  ⚪ $pane_target @agent_id=空 (= shogun pane、許容範囲)"
        else
            echo "  ❌ $pane_target: pane 不在 or @agent_id 未設定 (期待=$expected)" >&2
            violations=$((violations+1))
        fi
    elif [ "$(normalize_persona "$actual")" != "$(normalize_persona "$expected")" ]; then
        echo "  ❌ $pane_target: 期待=$expected 実態=$actual" >&2
        violations=$((violations+1))
    else
        echo "  ✅ $pane_target = $expected"
    fi
done

# 重複 @agent_id 検知 (= 同じ agent が複数 pane に存在)
echo ""
echo "▼ 重複 @agent_id 検知"
dup=$("$TMUX_CMD" list-panes -a -F '#{@agent_id}' 2>/dev/null | grep -v '^$' | sort | uniq -d)
if [ -n "$dup" ]; then
    echo "  ❌ 重複検出:" >&2
    echo "$dup" | sed 's/^/     /' >&2
    violations=$((violations+1))
else
    echo "  ✅ 重複なし"
fi

# ============================================================================
# §X. 4-way mapping audit (Phase 1 — cycle2 fix 適用版)
# ============================================================================
#
# 4 source の整合性 check:
#   A. tmux 実態 / B. queue/pane_registry.yaml /
#   C. scripts/watcher_supervisor.sh / D. CLAUDE.md §18.1
#
# 不整合は stderr 警告 + exit 2 (advisory only)。block しない。
#
# cycle2 fix:
#   M1 — count は MISMATCH_COUNT_GLOBAL 経由、return は 0/1 のみ
#   M2 — 全 source 取得を SECONDS タイマで 5 秒以内に強制、超過時残 source skip
#   S1 — CLAUDE.md parser を awk -F'|' に変更
#   S2 — drift dump を mktemp + umask 077 で生成

# 内部用 deadline チェッカ (M2)
_check_deadline() {
    [ "$SECONDS" -lt "$TIMEOUT_GLOBAL_SECONDS" ]
}

run_4way_audit() {
    local audit_corr_id
    audit_corr_id="pane4way-$(date +%s)-$$"
    local mismatch_count=0
    local source_skipped=0
    local audit_err_code="ERR-INFRA-PANE-DRIFT-001"  # 採番台帳未登録、別 cmd で登録予定

    # M2: SECONDS タイマで global budget 強制 (= ここから計測開始)
    SECONDS=0

    echo ""
    echo "▼ 4-way mapping audit (corr_id=$audit_corr_id, advisory only, budget=${TIMEOUT_GLOBAL_SECONDS}s)"

    # ── A. tmux 実態 ─────────────────────────────────────────────────
    local src_a_raw=""
    if _check_deadline; then
        # ★km-214★ =multiagent(完全一致)・session が無ければ list-panes は今の client へ落ちるゆゑ has-session を先に
        if "$TMUX_CMD" has-session -t "=multiagent" 2>/dev/null && src_a_raw=$(timeout "$TIMEOUT_PER_SOURCE_SECONDS" "$TMUX_CMD" list-panes -t "=multiagent" -F '#{pane_index}=#{@agent_id}' 2>/dev/null); then
            :
        else
            echo "  [WARN] source A (tmux) 取得失敗 (degraded mode)" >&2
            src_a_raw=""
            source_skipped=$((source_skipped+1))
        fi
    else
        echo "  [WARN] global budget 超過 (elapsed=${SECONDS}s)、source A skip" >&2
        source_skipped=$((source_skipped+1))
    fi

    # ── B. queue/pane_registry.yaml ──────────────────────────────────
    local src_b_raw=""
    if _check_deadline; then
        if [ -f "$PANE_REGISTRY" ]; then
            if ! src_b_raw=$(timeout "$TIMEOUT_PER_SOURCE_SECONDS" python3 - "$PANE_REGISTRY" <<'PYEOF' 2>/dev/null
import sys, re
path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
except Exception:
    sys.exit(0)
in_panes = False
cur = {}
out = []
for line in text.splitlines():
    if re.match(r"^\s*panes:\s*$", line):
        in_panes = True
        continue
    if not in_panes:
        continue
    if re.match(r"^\w", line):
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
    else
        echo "  [WARN] global budget 超過 (elapsed=${SECONDS}s)、source B skip" >&2
        source_skipped=$((source_skipped+1))
    fi

    # ── C. watchdog (watcher_supervisor.sh) ──────────────────────────
    local src_c_raw=""
    if _check_deadline; then
        if [ -f "$WATCHER_SUPERVISOR" ]; then
            if ! src_c_raw=$(timeout "$TIMEOUT_PER_SOURCE_SECONDS" \
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
    else
        echo "  [WARN] global budget 超過 (elapsed=${SECONDS}s)、source C skip" >&2
        source_skipped=$((source_skipped+1))
    fi

    # ── D. CLAUDE.md §18.1 (cycle2 S1: awk -F'|' parser) ────────────
    # 列 3 = エージェント (例: "家老 (karo)"), 列 4 = tmux pane (例: "multiagent:0.0")
    local src_d_raw=""
    if _check_deadline; then
        if [ -f "$CLAUDE_MD" ]; then
            # shellcheck disable=SC2016  # awk script intentionally uses single quotes (no shell expansion)
            if ! src_d_raw=$(timeout "$TIMEOUT_PER_SOURCE_SECONDS" awk -F'|' '
                BEGIN { in_section=0; in_mainpc=0 }
                /^##+ §18\.1[^0-9]/ { in_section=1; next }
                in_section && /^## §18\.[2-9][^0-9]/ { exit }
                !in_section { next }
                /^### MainPC/ { in_mainpc=1; next }
                /^### SecondPC/ { in_mainpc=0; next }
                !in_mainpc { next }
                NF < 4 { next }
                {
                    agent_col = $3
                    pane_col = $4
                    if (match(agent_col, /\([a-z][a-z0-9]*\)/) == 0) next
                    agent = substr(agent_col, RSTART+1, RLENGTH-2)
                    if (match(pane_col, /multiagent:0?\.[0-9]+/) == 0) next
                    tgt = substr(pane_col, RSTART, RLENGTH)
                    n = index(tgt, ".")
                    idx = substr(tgt, n+1)
                    print idx "=" agent
                }
            ' "$CLAUDE_MD" 2>/dev/null); then
                echo "  [WARN] source D (CLAUDE.md §18.1) 解析失敗 (degraded mode)" >&2
                src_d_raw=""
                source_skipped=$((source_skipped+1))
            fi
        else
            echo "  [WARN] source D 不在: $CLAUDE_MD (degraded mode)" >&2
            source_skipped=$((source_skipped+1))
        fi
    else
        echo "  [WARN] global budget 超過 (elapsed=${SECONDS}s)、source D skip" >&2
        source_skipped=$((source_skipped+1))
    fi

    # ── parse raw → 連想配列 (index → normalized persona) ───────────
    # ★bash 3.2 対応★: 連想配列も local -n (nameref, bash 4.3+) も 3.2 に無い。
    # ∴ 各 source を「idx=正規化persona」の★改行区切りの表★へ畳み、table_get で引く。
    local SRC_A SRC_B SRC_C SRC_D
    normalize_block() {
        local raw="$1"
        local line idx val
        while IFS= read -r line; do
            [ -z "$line" ] && continue
            idx="${line%%=*}"
            val="${line#*=}"
            [ -z "$idx" ] && continue
            [ -z "$val" ] && continue
            echo "${idx}=$(normalize_persona "$val")"
        done <<< "$raw"
    }
    SRC_A=$(normalize_block "$src_a_raw")
    SRC_B=$(normalize_block "$src_b_raw")
    SRC_C=$(normalize_block "$src_c_raw")
    SRC_D=$(normalize_block "$src_d_raw")

    # ── 4-way 比較 ────────────────────────────────────────────────────
    # ★bash 3.2 対応★: drift の積み上げも表(1行1件・`idx=記述`)とする。
    local drift_dump=""
    local drift_line=""
    local idx
    echo "  ── per-index comparison (multiagent: のみ、shogun は別 source 確認) ──"
    printf "  %-5s %-12s %-12s %-12s %-12s %s\n" "idx" "A:tmux" "B:registry" "C:watchdog" "D:§18.1" "status"
    for idx in 0 1 2 3 4 5; do
        local va vb vc vd
        va=$(table_get "$SRC_A" "$idx")
        vb=$(table_get "$SRC_B" "$idx")
        vc=$(table_get "$SRC_C" "$idx")
        vd=$(table_get "$SRC_D" "$idx")
        if [ -z "$va" ] && [ -z "$vb" ] && [ -z "$vc" ] && [ -z "$vd" ]; then
            continue
        fi
        local values=()
        [ -n "$va" ] && values+=("$va")
        [ -n "$vb" ] && values+=("$vb")
        [ -n "$vc" ] && values+=("$vc")
        [ -n "$vd" ] && values+=("$vd")
        local unique
        # ★BSD の wc -l は空白を詰める(`       1`)★。
        # 旧形はその値を [ "$unique" = "1" ] と比べて居た故、
        # ★一致して居ても決して真にならぬ(=全件 DRIFT に見える)★。
        # ∴ awk で詰め物の無い数を出す。
        unique=$(printf '%s\n' "${values[@]}" | sort -u | awk 'END{print NR}')
        local status_mark
        if [ "$unique" = "1" ]; then
            status_mark="✅ match"
        else
            status_mark="❌ DRIFT"
            drift_dump="${drift_dump}${idx}=A=${va:-_} B=${vb:-_} C=${vc:-_} D=${vd:-_}
"
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
        while IFS= read -r drift_line; do
            [ -z "$drift_line" ] && continue
            echo "    [WARN] pane drift detected at index ${drift_line%%=*}: ${drift_line#*=}" >&2
        done <<< "$drift_dump"
        echo "    {\"timestamp\":\"$audit_end_ts\",\"level\":\"WARN\",\"source\":\"pane_identity_4way\",\"corr_id\":\"$audit_corr_id\",\"err_code\":\"$audit_err_code\",\"mismatch_count\":$mismatch_count,\"sources_skipped\":$source_skipped,\"advisory\":true}" >&2

        # cycle2 S2: mktemp + umask 077 で安全な dump file 生成 (symlink/clobber 攻撃対策)
        local dump_file
        if dump_file=$(mktemp --suffix=.json -p "${TMPDIR:-/tmp}" "pane_identity_drift.XXXXXX" 2>/dev/null); then
            :
        elif dump_file=$(mktemp -p "${TMPDIR:-/tmp}" "pane_identity_drift.XXXXXX" 2>/dev/null); then
            # mktemp --suffix 非対応版 (BSD): 後付け改名
            if mv -- "$dump_file" "${dump_file}.json" 2>/dev/null; then
                dump_file="${dump_file}.json"
            fi
        else
            dump_file="/tmp/pane_identity_drift_${audit_corr_id}.json"
        fi
        chmod 600 -- "$dump_file" 2>/dev/null || true
        {
            echo "{"
            echo "  \"corr_id\": \"$audit_corr_id\","
            echo "  \"timestamp\": \"$audit_end_ts\","
            echo "  \"err_code\": \"$audit_err_code\","
            echo "  \"sources_skipped\": $source_skipped,"
            echo "  \"mismatches\": {"
            local first=1
            while IFS= read -r drift_line; do
                [ -z "$drift_line" ] && continue
                if [ "$first" = "1" ]; then first=0; else echo ","; fi
                printf '    "%s": "%s"' "${drift_line%%=*}" "${drift_line#*=}"
            done <<< "$drift_dump"
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

    # cycle2 M1: count は global 経由、return は 0/1 のみ (= modulo 256 wrap 解消)
    # shellcheck disable=SC2034  # 外部 caller / bats test が参照
    MISMATCH_COUNT_GLOBAL=$mismatch_count
    # shellcheck disable=SC2034
    SOURCES_SKIPPED_GLOBAL=$source_skipped
    # shellcheck disable=SC2034
    LAST_AUDIT_STATUS_GLOBAL="$last_run_status"
    if [ "$mismatch_count" -gt 0 ]; then
        return 1
    fi
    return 0
}

# 4-way audit を実行 (M1: 戻り値は 0/1 のみ、count は MISMATCH_COUNT_GLOBAL から取得)
run_4way_audit || true
audit_mismatches=$MISMATCH_COUNT_GLOBAL

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
