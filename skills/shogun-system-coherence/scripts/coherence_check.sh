#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# coherence_check.sh — settings.yaml ↔ tmux ↔ ps 三者整合性検査
#
# v2 (= 2026-05-10 直政赤鬼の眼 監査指摘の是正):
#   - pkill 全廃 (D006 違反是正、specific PID kill のみ使用)
#   - heredoc + pipeline + stdin 競合 bug 修正 (= 環境変数経由)
#   - pane notation 統一 (= canonical form: multiagent:agents.N)
#
# Usage:
#   bash skills/shogun-system-coherence/scripts/coherence_check.sh
#   bash skills/shogun-system-coherence/scripts/coherence_check.sh --auto-fix
#
# Exit code:
#   0 = 全 ✅
#   1 = 不整合あり (= --auto-fix 無し時)
#   2 = 内部 error
# ════════════════════════════════════════════════════════════════
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

AUTO_FIX="${1:-}"
[ "$AUTO_FIX" = "--auto-fix" ] && AUTO_FIX="yes" || AUTO_FIX="no"

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/coherence_check_$(date +%Y%m%d_%H%M%S).log"

log() { echo "$@" | tee -a "$LOG_FILE"; }

log "═══════════════════════════════════════════════════════════"
log "  System Coherence Check v2 — $(date -Iseconds)"
log "═══════════════════════════════════════════════════════════"

# ════════════════════════════════════════════════════════════════
# Pane notation 正規化 (= R3 是正)
# canonical: multiagent:agents.N (= tmux native list-panes 形式)
# 既出形式: multiagent:0.N、multiagent:agents.N、shogun:main.0、shogun:main
# ════════════════════════════════════════════════════════════════
canonicalize_pane() {
    local p="$1"
    # multiagent:0.N → multiagent:agents.N
    if [[ "$p" =~ ^multiagent:0\.([0-9]+)$ ]]; then
        echo "multiagent:agents.${BASH_REMATCH[1]}"
        return
    fi
    # shogun:main → shogun:main.0
    if [[ "$p" == "shogun:main" ]]; then
        echo "shogun:main.0"
        return
    fi
    echo "$p"
}

# ════════════════════════════════════════════════════════════════
# Stage A: settings.yaml から期待 mapping 抽出
# ════════════════════════════════════════════════════════════════
EXPECTED_FILE="$(mktemp)"
trap 'rm -f "$EXPECTED_FILE"' EXIT

python3 > "$EXPECTED_FILE" <<'PY'
import yaml, json
d = yaml.safe_load(open('config/settings.yaml'))
agents = d.get('cli', {}).get('agents', {})
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
PY

log ""
log "[期待 mapping (settings.yaml)]"
python3 -c "
import json
d = json.load(open('$EXPECTED_FILE'))
for k,v in d.items():
    print(f'  {k:12s} → {v[\"pane\"]:24s} cli={v[\"cli\"]}')
" | tee -a "$LOG_FILE"

# ════════════════════════════════════════════════════════════════
# Stage B + C: tmux pane meta + ps watcher process 三者照合
# 環境変数経由で json を python3 に渡す (= heredoc + stdin 競合 bug 是正)
# ════════════════════════════════════════════════════════════════
NG_FILE="$(mktemp)"
trap 'rm -f "$EXPECTED_FILE" "$NG_FILE"' EXIT

EXPECTED_JSON="$(cat "$EXPECTED_FILE")" python3 > "$NG_FILE" <<'PY'
import json, os, subprocess, re
expected = json.loads(os.environ['EXPECTED_JSON'])

# C: ps から watcher 列挙
ps = subprocess.run(['ps', '-ef'], capture_output=True, text=True).stdout
watchers = {}
for line in ps.splitlines():
    m = re.search(r'inbox_watcher\.sh (\w+) (\S+) (\w+)', line)
    if m:
        agent, pane, cli = m.groups()
        # canonicalize: multiagent:0.N → multiagent:agents.N
        if re.match(r'^multiagent:0\.\d+$', pane):
            pane = pane.replace('multiagent:0.', 'multiagent:agents.')
        elif pane == 'shogun:main':
            pane = 'shogun:main.0'
        watchers[agent] = {'pane': pane, 'cli': cli, 'pid': line.split()[1]}

# B: tmux pane meta
def tmux_get(pane, key):
    r = subprocess.run(['tmux','show-options','-p','-t',pane,'-v',key],
        capture_output=True, text=True)
    return r.stdout.strip()

ng_list = []
for a, exp in expected.items():
    issues = []
    w = watchers.get(a, {})

    if not w:
        issues.append('watcher missing')
    else:
        if w.get('pane') != exp['pane']:
            issues.append(f"watcher pane mismatch: expected={exp['pane']}, actual={w.get('pane')} (PID {w.get('pid')})")
        if w.get('cli') != exp['cli']:
            issues.append(f"watcher cli mismatch: expected={exp['cli']}, actual={w.get('cli')} (PID {w.get('pid')})")

    # tmux pane meta は multiagent 系のみ check (= shogun:main は session 違いゆえ skip)
    if exp['pane'].startswith('multiagent:'):
        aid = tmux_get(exp['pane'], '@agent_id')
        cli = tmux_get(exp['pane'], '@agent_cli')
        if aid and aid != a:
            issues.append(f"tmux @agent_id mismatch: expected={a}, actual={aid}")
        elif not aid:
            issues.append(f"tmux @agent_id empty (= deploy 漏れ可能性)")
        if cli and cli != exp['cli']:
            issues.append(f"tmux @agent_cli mismatch: expected={exp['cli']}, actual={cli}")
        elif not cli:
            issues.append(f"tmux @agent_cli empty")

    if issues:
        ng_list.append({'agent': a, 'expected': exp, 'issues': issues})

print(json.dumps(ng_list, ensure_ascii=False))
PY

ng_count=$(python3 -c "import json; print(len(json.load(open('$NG_FILE'))))")

log ""
if [ "$ng_count" = "0" ]; then
  total=$(python3 -c "import json; print(len(json.load(open('$EXPECTED_FILE'))))")
  log "✅ 全 agent coherence OK ($total 件)"
  exit 0
fi

log "❌ 不整合 $ng_count 件検出:"
python3 -c "
import json
for ng in json.load(open('$NG_FILE')):
    print(f'  [{ng[\"agent\"]}] expected pane={ng[\"expected\"][\"pane\"]} cli={ng[\"expected\"][\"cli\"]}')
    for i in ng['issues']:
        print(f'    - {i}')
" | tee -a "$LOG_FILE"

if [ "$AUTO_FIX" != "yes" ]; then
  log ""
  log "→ --auto-fix で自動修復 (= 信長 D006 例外権限 P002 行使)"
  exit 1
fi

# ════════════════════════════════════════════════════════════════
# Stage D: --auto-fix mode (= 信長 D006-EXC P002 権限行使)
# pkill 全廃、specific PID kill のみ使用
# ════════════════════════════════════════════════════════════════
log ""
log "[--auto-fix mode] 是正着手 (= 信長 P002 権限行使)"

# Step 1: 不整合 watcher を kill (= specific PID のみ、pkill 禁)
KILLED_PIDS=()
while read -r pid; do
    [ -z "$pid" ] && continue
    log "  P002 kill PID=$pid (= ps -fp で対象特定済)"
    ps -fp "$pid" 2>&1 | tee -a "$LOG_FILE" | tail -1
    if kill "$pid" 2>&1; then
        KILLED_PIDS+=("$pid")
    fi
done < <(python3 -c "
import json, re
for ng in json.load(open('$NG_FILE')):
    for issue in ng['issues']:
        m = re.search(r'PID (\d+)', issue)
        if m:
            print(m.group(1))
" | sort -u)
sleep 2

# Step 2: tmux @agent_id / @agent_cli 修正
log ""
log "  tmux pane meta 修正"
python3 <<PY
import json, subprocess
exp = json.load(open('$EXPECTED_FILE'))
for a, e in exp.items():
    if e['pane'].startswith('multiagent:'):
        subprocess.run(['tmux','set-option','-p','-t',e['pane'],'@agent_id',a], capture_output=True)
        subprocess.run(['tmux','set-option','-p','-t',e['pane'],'@agent_cli',e['cli']], capture_output=True)
        print(f"    {e['pane']}: @agent_id={a} @agent_cli={e['cli']}")
PY

# Step 3: watcher_supervisor 再起動 (= specific PID kill のみ、pkill 禁)
log ""
log "  watcher_supervisor 再起動"
SUP_PID=$(ps -ef | grep "scripts/watcher_supervisor.sh" | grep -v grep | awk '{print $2}' | head -1)
if [ -n "$SUP_PID" ]; then
    log "    旧 supervisor PID=$SUP_PID kill (= P002 specific kill)"
    kill "$SUP_PID" 2>&1 | tee -a "$LOG_FILE" || true
    sleep 1
fi
nohup bash scripts/watcher_supervisor.sh >> "$LOG_DIR/watcher_supervisor.log" 2>&1 &
NEW_SUP_PID=$!
log "    新 supervisor PID=$NEW_SUP_PID"
disown
sleep 5

# Step 4: 再 verify (= --auto-fix なしで recursive)
log ""
log "[Stage E: 是正後 再 verify]"
exec bash "$0"
