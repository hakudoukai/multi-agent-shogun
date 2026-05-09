#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# skill_candidate_scan.sh — 4 系統トラブル検知 + 集約 + 閾値判定
#
# Usage:
#   bash skills/shogun-trouble-auto-skill/scripts/skill_candidate_scan.sh [scan|aggregate|status]
#
# 起動方式:
#   - 手動: 上記 usage
#   - 自動: session_start_hook から 1 日 1 回 (= rate-limited)
#
# 出力:
#   - queue/skill_candidates.yaml に append (= 新規 candidate)
#   - 既存 candidate の hit_count 集約
#   - 閾値超え → stdout に「草案化推奨」 + dashboard 🚨 追加
# ════════════════════════════════════════════════════════════════
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

CANDIDATES_YAML="queue/skill_candidates.yaml"
PUNISHMENT_LOG="queue/reports/shogun_punishment_log.yaml"
DASHBOARD="dashboard.md"

mode="${1:-scan}"
NOW=$(date -Iseconds)

print_section() { echo ""; echo "═══ $1 ═══"; }

[ -f "$CANDIDATES_YAML" ] || { echo "ERR: $CANDIDATES_YAML 不在"; exit 2; }

# ════════════════════════════════════════════════════════════════
# Mode: status — 現状一覧
# ════════════════════════════════════════════════════════════════
if [ "$mode" = "status" ]; then
  print_section "skill_candidates 現状"
  python3 <<'PY'
import yaml
data = yaml.safe_load(open('queue/skill_candidates.yaml'))
cands = data.get('candidates', [])
stats = data.get('stats', {})
print(f"総候補数: {len(cands)}")
print(f"承認済: {stats.get('approved', 0)}")
print(f"草案中: {stats.get('drafted', 0)}")
print(f"閾値超 (承認待ち): {stats.get('threshold_reached_pending_approval', 0)}")
print(f"却下: {stats.get('rejected', 0)}")
print()
print("─── 直近 5 件 ───")
for c in sorted(cands, key=lambda x: x.get('detected_at', ''), reverse=True)[:5]:
    print(f"[{c['id']}] {c['signature']:30s} hit={c.get('hit_count',1):2d} status={c['status']}")
PY
  exit 0
fi

# ════════════════════════════════════════════════════════════════
# Mode: aggregate — 既存 candidate の hit_count 再集計
# ════════════════════════════════════════════════════════════════
if [ "$mode" = "aggregate" ] || [ "$mode" = "scan" ]; then
  print_section "Stage 2 集約 — punishment_log 同根原因再発検知"
  python3 <<'PY'
import yaml
from collections import Counter
import os
if not os.path.exists('queue/reports/shogun_punishment_log.yaml'):
    print("punishment_log 不在、skip")
else:
    log = yaml.safe_load(open('queue/reports/shogun_punishment_log.yaml')) or {}
    entries = log.get('entries', []) if isinstance(log, dict) else []
    if not entries:
        print("punishment entry 0 件")
    else:
        roots = Counter(e.get('root_cause', 'unknown') for e in entries)
        print(f"punishment entries: {len(entries)} 件")
        for root, cnt in roots.most_common(5):
            mark = "🚨 ≥2 件" if cnt >= 2 else "  "
            print(f"  {mark} [{cnt}回] {root[:60]}")
PY
fi

# ════════════════════════════════════════════════════════════════
# Mode: scan — Stage 1 検知 (= phrase/dashboard/cmd)
# ════════════════════════════════════════════════════════════════
if [ "$mode" = "scan" ]; then
  print_section "Stage 1 検知 — dashboard 🚨要対応 残留 (>24h)"
  if [ -f "$DASHBOARD" ]; then
    awk '/🚨/{flag=1} flag && /---/{flag=0} flag' "$DASHBOARD" 2>/dev/null | head -20
  else
    echo "dashboard.md 不在"
  fi

  print_section "Stage 1 検知 — Lord 発話 phrase (= conversation transcript からは要外部入力)"
  echo "本 mode は本 conversation 内の Lord 発話を直接 scan できぬ"
  echo "→ shogun (Claude Code) が直接 detect_lord_phrase() 呼出 (= skill 本体の責務)"

  print_section "Stage 3 閾値判定 (= severity 別 N、7 日窓)"
  python3 <<'PY'
import yaml
from datetime import datetime, timedelta, timezone
data = yaml.safe_load(open('queue/skill_candidates.yaml'))
cands = data.get('candidates', [])
cfg = data.get('config', {})
thresholds = cfg.get('thresholds', {'blocking': 2, 'normal': 3, 'cosmetic': 5})
window_days = cfg.get('time_window_days', 7)

# 同 signature 7 日窓内の hit_count 集計
from collections import defaultdict
sig_recent = defaultdict(list)
now = datetime.now(timezone.utc)
for c in cands:
    try:
        det = c.get('detected_at')
        if isinstance(det, str):
            dt = datetime.fromisoformat(det.replace('Z','+00:00'))
        else:
            dt = datetime.combine(det, datetime.min.time(), tzinfo=timezone.utc)
        if (now - dt).days <= window_days:
            sig_recent[c['signature']].append(c)
    except Exception:
        pass

threshold_pending = []
for sig, group in sig_recent.items():
    sev = group[0].get('severity', 'normal')
    n = thresholds.get(sev, 3)
    total = sum(c.get('hit_count', 1) for c in group)
    if total >= n and any(c.get('status') in ('detected', 'aggregated') for c in group):
        threshold_pending.append((sig, sev, n, total))

explicit = [c for c in cands if c.get('explicit_skill_request') and c.get('status') in ('detected','aggregated')]
print(f"閾値超 (承認待ち): {len(threshold_pending)}")
for sig, sev, n, total in threshold_pending:
    print(f"  → 草案化推奨: {sig} (severity={sev} N={n} 7日内hit={total})")
print(f"明示 skill 化要請 (= severity/N 無視): {len(explicit)}")
for c in explicit:
    print(f"  → 草案化推奨: {c['signature']} (Lord 明示)")
PY

  print_section "✅ scan 完遂、last_scan_at 更新"
  python3 -c "
import yaml
d = yaml.safe_load(open('queue/skill_candidates.yaml'))
d.setdefault('stats', {})['last_scan_at'] = '$NOW'
with open('queue/skill_candidates.yaml','w') as f:
    yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False)
print('last_scan_at = $NOW')
"
fi
