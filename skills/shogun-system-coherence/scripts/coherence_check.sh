#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# coherence_check.sh — settings.yaml ↔ tmux ↔ ps 三者整合性検査
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
log "  System Coherence Check — $(date -Iseconds)"
log "═══════════════════════════════════════════════════════════"

# settings.yaml から期待 mapping 抽出
expected_json=$(python3 <<'PY'
import yaml, json
d = yaml.safe_load(open('config/settings.yaml'))
agents = d.get('cli', {}).get('agents', {})
# pane mapping 推定 (= settings.yaml にコメントのみゆえ慣例で再現)
pane_map = {
    'shogun': 'shogun:main',
    'karo': 'multiagent:0.0',
}
ashi_count = sum(1 for k in agents if k.startswith('ashigaru'))
for i in range(1, ashi_count+1):
    pane_map[f'ashigaru{i}'] = f'multiagent:0.{i}'
if 'gunshi' in agents:
    pane_map['gunshi'] = f'multiagent:0.{ashi_count+1}'
if 'gunshi2' in agents:
    pane_map['gunshi2'] = f'multiagent:0.{ashi_count+2}'
out = {a: {'pane': pane_map.get(a, '?'), 'cli': cli} for a, cli in agents.items()}
print(json.dumps(out))
PY
)

log ""
log "[期待 mapping (settings.yaml)]"
echo "$expected_json" | python3 -c "import json,sys; [print(f'  {k:12s} → {v[\"pane\"]:18s} cli={v[\"cli\"]}') for k,v in json.loads(sys.stdin.read()).items()]" | tee -a "$LOG_FILE"

# 三者照合
result=$(python3 <<PY
import json, subprocess, re
expected = json.loads('''$expected_json''')

ps = subprocess.run(['ps', '-ef'], capture_output=True, text=True).stdout
watchers = {}
for line in ps.splitlines():
    m = re.search(r'inbox_watcher\.sh (\w+) (\S+) (\w+)', line)
    if m:
        agent, pane, cli = m.groups()
        watchers[agent] = {'pane': pane.replace('agents.','0.'), 'cli': cli, 'pid': line.split()[1]}

ng_list = []
for a, exp in expected.items():
    w = watchers.get(a, {})
    pane_meta = {}
    if exp['pane'].startswith('multiagent:'):
        p_idx = exp['pane'].split('.')[-1]
        pane_meta['aid'] = subprocess.run(['tmux','show-options','-p','-t',exp['pane'],'-v','@agent_id'],
            capture_output=True, text=True).stdout.strip()
        pane_meta['cli'] = subprocess.run(['tmux','show-options','-p','-t',exp['pane'],'-v','@agent_cli'],
            capture_output=True, text=True).stdout.strip()
    issues = []
    if not w:
        issues.append('watcher missing')
    else:
        if w.get('pane') != exp['pane']:
            issues.append(f"watcher pane: expected {exp['pane']}, got {w.get('pane')} (PID {w.get('pid')})")
        if w.get('cli') != exp['cli']:
            issues.append(f"watcher cli: expected {exp['cli']}, got {w.get('cli')}")
    if pane_meta:
        if pane_meta.get('aid') and pane_meta.get('aid') != a:
            issues.append(f"tmux @agent_id: expected {a}, got {pane_meta.get('aid')}")
        if pane_meta.get('cli') and pane_meta.get('cli') != exp['cli']:
            issues.append(f"tmux @agent_cli: expected {exp['cli']}, got {pane_meta.get('cli')}")
    if issues:
        ng_list.append({'agent': a, 'issues': issues})
print(json.dumps(ng_list, ensure_ascii=False))
PY
)

ng_count=$(echo "$result" | python3 -c "import json,sys; print(len(json.loads(sys.stdin.read())))")

log ""
if [ "$ng_count" = "0" ]; then
  log "✅ 全 agent coherence OK ($(echo "$expected_json" | python3 -c "import json,sys; print(len(json.loads(sys.stdin.read())))") 件)"
  exit 0
fi

log "❌ 不整合 $ng_count 件検出:"
echo "$result" | python3 -c "
import json, sys
for ng in json.loads(sys.stdin.read()):
    print(f\"  [{ng['agent']}]\")
    for i in ng['issues']:
        print(f'    - {i}')
" | tee -a "$LOG_FILE"

if [ "$AUTO_FIX" != "yes" ]; then
  log ""
  log "→ --auto-fix で自動修復 (= D006 緩和済 信長権限要)"
  exit 1
fi

log ""
log "[--auto-fix mode] 修復着手"
log "  1. 不整合 watcher の kill"
log "  2. tmux @agent_id / @agent_cli set"
log "  3. watcher_supervisor 再起動"
echo "$result" | python3 <<'PY'
import json, subprocess, sys
data = json.loads(sys.stdin.read())
for ng in data:
    for issue in ng['issues']:
        if 'PID' in issue:
            import re
            m = re.search(r'PID (\d+)', issue)
            if m:
                pid = m.group(1)
                print(f'  kill {pid} (= 不整合 watcher)')
                subprocess.run(['kill', pid], capture_output=True)
PY

# tmux @agent_id 修正
echo "$expected_json" | python3 <<'PY'
import json, sys, subprocess
expected = json.loads(sys.stdin.read())
for a, exp in expected.items():
    if exp['pane'].startswith('multiagent:'):
        subprocess.run(['tmux','set-option','-p','-t',exp['pane'],'@agent_id',a], capture_output=True)
        subprocess.run(['tmux','set-option','-p','-t',exp['pane'],'@agent_cli',exp['cli']], capture_output=True)
        print(f'  tmux meta set: {exp["pane"]} @agent_id={a} @agent_cli={exp["cli"]}')
PY

log "  watcher_supervisor 再起動"
pkill -f watcher_supervisor.sh 2>/dev/null || true
sleep 1
nohup bash scripts/watcher_supervisor.sh >> logs/watcher_supervisor.log 2>&1 &
disown
sleep 5

log ""
log "[再 verify]"
exec bash "$0"  # recursive verify (= --auto-fix 引数渡さず再 check)
