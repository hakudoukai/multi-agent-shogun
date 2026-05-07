#!/usr/bin/env bash
# agent_periodic_push.sh — 15分毎に家老を起こして全体前進催促
#
# 用途: agent 完成 → idle のまま放置を防止。systemd user timer で 15分毎実行。
# 理事長殿御指示 (2026-05-07):
#   - shogun (= 理事長殿との対話) 活動中は一旦停止 (= skip)
#   - idle 中のみ家老 inbox に push
#
# 動作:
#   1. shogun 活動検知 → 活動中なら即 skip (会話/作業を妨げない)
#   2. idle agent 集計
#   3. shogun_to_karo.yaml の pending cmd 集計
#   4. 家老に「全体前進催促」inbox_write
#   5. log: /tmp/agent_periodic_push.log

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="/tmp/agent_periodic_push.log"

now_ts="$(date '+%Y-%m-%dT%H:%M:%S')"

# ─── shogun 活動検知 (= 理事長殿との対話/作業中なら skip) ───

# 検知1: shogun pane の bottom 行にスピナー or 思考キーワード
SHOGUN_BOTTOM=$(tmux capture-pane -t "shogun:main.0" -p -e -J -S -10 2>/dev/null \
    | sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g; s/\x1b[()][AB012]//g; s/\x1b[78]//g' \
    | tail -10)
if echo "$SHOGUN_BOTTOM" | grep -qE '(thinking|Crunched|Cogitated|Brewed|Churned|Cooked|Bash\(|tokens|✻|✶|✽|✢)'; then
    echo "[$now_ts] SKIPPED: shogun pane active (spinner/working detected)" >> "$LOG"
    exit 0
fi

# 検知2: shogun 対話 jsonl の最終変更時刻 (= 5分以内に変更 = 対話中)
JSONL_DIR="$HOME/.claude/projects/-mnt-c-Users-User-projects-multi-agent-shogun"
if [ -d "$JSONL_DIR" ]; then
    LATEST_JSONL=$(ls -t "$JSONL_DIR"/*.jsonl 2>/dev/null | head -1)
    if [ -n "$LATEST_JSONL" ]; then
        jsonl_age=$(( $(date +%s) - $(stat -c '%Y' "$LATEST_JSONL" 2>/dev/null || echo 0) ))
        if [ "$jsonl_age" -lt 300 ]; then
            echo "[$now_ts] SKIPPED: shogun jsonl modified ${jsonl_age}s ago (conversation active)" >> "$LOG"
            exit 0
        fi
    fi
fi

# ─── idle agent 集計 (= 15分以上 report.yaml が更新されてない) ───
IDLE_AGENTS=()
for a in karo gunshi ashigaru1 ashigaru2 hideyoshi ieyasu; do
    report="$SCRIPT_DIR/queue/reports/${a}_report.yaml"
    if [ -f "$report" ]; then
        mtime=$(stat -c '%Y' "$report" 2>/dev/null || echo 0)
        age=$(( $(date +%s) - mtime ))
        if [ "$age" -gt 900 ]; then
            IDLE_AGENTS+=("${a}: ${age}s idle (report 最終更新からの経過)")
        fi
    fi
done

# SecondPC agent 状況 (best-effort、SSH失敗時は無視)
if ssh -o ConnectTimeout=5 -o BatchMode=yes hakudokai@192.168.11.47 'true' 2>/dev/null; then
    for a in maeda ashigaru5 ashigaru6 ashigaru7; do
        sp_age=$(ssh -o ConnectTimeout=5 -o BatchMode=yes hakudokai@192.168.11.47 \
            "stat -c '%Y' ~/projects/multi-agent-shogun/queue/reports/${a}_report.yaml 2>/dev/null || echo 0" 2>/dev/null)
        sp_age=${sp_age:-0}
        if [ "$sp_age" -gt 0 ]; then
            age=$(( $(date +%s) - sp_age ))
            if [ "$age" -gt 900 ]; then
                IDLE_AGENTS+=("${a} (SecondPC): ${age}s idle")
            fi
        fi
    done
fi

# ─── shogun_to_karo.yaml の pending cmd ───
PENDING=$(grep -c "status: pending" "$SCRIPT_DIR/queue/shogun_to_karo.yaml" 2>/dev/null || echo 0)
PENDING=${PENDING%%[^0-9]*}
IN_PROGRESS=$(grep -c "status: in_progress" "$SCRIPT_DIR/queue/shogun_to_karo.yaml" 2>/dev/null || echo 0)
IN_PROGRESS=${IN_PROGRESS%%[^0-9]*}

# ─── 家老に push (= 全体前進催促) ───
IDLE_LIST=""
if [ "${#IDLE_AGENTS[@]}" -gt 0 ]; then
    for entry in "${IDLE_AGENTS[@]}"; do
        IDLE_LIST="${IDLE_LIST}
  - ${entry}"
    done
fi

MSG="【15分定期 push — 全体前進催促 (将軍 idle 中)】

shogun (= 理事長殿との対話) idle 中につき、systemd timer による機械的催促。

【現状】
- idle agent: ${#IDLE_AGENTS[@]} 体${IDLE_LIST}
- shogun_to_karo.yaml: pending=${PENDING:-0} / in_progress=${IN_PROGRESS:-0}

【家老への依頼】
1. idle agent への次タスク発令を判断 (= 待ち時間ゼロ作戦 / 小児アプリ / Phase 6-9 / DD-154/155 Phase B/C 等から選択)
2. 残タスクから新規 cmd を shogun_to_karo.yaml に追加し PDCA を回す
3. dashboard.md 更新
4. agent が完成したら即時次タスク発令する自走判断を強化

【注記】
- 本 push は agent_periodic_push.sh (systemd timer 15min) によるもの、shogun の意図ではない
- 緊急以外は将軍経由不要、家老の自律判断で OK
- shogun の対話復帰時は本 push は自動 skip される設計"

if [ -x "$SCRIPT_DIR/scripts/inbox_write.sh" ]; then
    bash "$SCRIPT_DIR/scripts/inbox_write.sh" karo "$MSG" status_update shogun >>"$LOG" 2>&1 || true
fi

echo "[$now_ts] SENT push to karo (idle=${#IDLE_AGENTS[@]}, pending=${PENDING:-0}, in_progress=${IN_PROGRESS:-0})" >> "$LOG"
exit 0
