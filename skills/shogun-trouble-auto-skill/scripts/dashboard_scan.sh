#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# dashboard_scan.sh — dashboard.md 🚨要対応 残留 entry 検知
#
# 拡張 #3 — 24h 以上残留する 🚨 entry を signature 化、candidates.yaml に集約。
#
# Usage:
#   bash skills/shogun-trouble-auto-skill/scripts/dashboard_scan.sh
# ════════════════════════════════════════════════════════════════
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

DASHBOARD="dashboard.md"
[ -f "$DASHBOARD" ] || { echo "ERR: $DASHBOARD 不在"; exit 2; }

# flock で同時書込破損防止 (= R4 是正、直政赤鬼指摘 2026-05-10)
LOCK_FILE="queue/skill_candidates.yaml.lock"
exec 200>"$LOCK_FILE"
flock -w 10 200 || { echo "ERR: flock timeout"; exit 3; }

python3 <<'PY'
import yaml, re, subprocess, hashlib
from datetime import datetime, timedelta, timezone

# dashboard.md 内の 🚨 section 抽出
content = open('dashboard.md').read()
# 🚨【要対応N】 から次の 🚨 or --- まで
entries = re.findall(r'🚨【要対応\d+】[^\n]*(?:\n(?!🚨|---|##)[^\n]*)*', content)

# 各 entry の git blame で初出 commit を取得
def first_seen(line):
    try:
        out = subprocess.run(
            ['git', 'log', '--all', '--reverse', '--format=%H %ct', '-S', line[:50], '--', 'dashboard.md'],
            capture_output=True, text=True, timeout=10
        )
        first_line = out.stdout.strip().split('\n')[0]
        if first_line:
            commit, ts = first_line.split(maxsplit=1)
            return datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except Exception:
        pass
    return None

now = datetime.now(timezone.utc)
threshold = timedelta(hours=24)

# yaml 読込
with open('queue/skill_candidates.yaml') as f:
    data = yaml.safe_load(f)
data.setdefault('candidates', [])
data.setdefault('signature_index', {})

stale_count = 0
for entry in entries:
    title_match = re.match(r'(🚨【要対応\d+】[^\n🔴]+)', entry)
    title = title_match.group(1).strip() if title_match else entry[:50]
    title = re.sub(r'\s+', ' ', title)[:80]

    seen_at = first_seen(title)
    if not seen_at:
        continue
    age = now - seen_at
    if age < threshold:
        continue

    # 24h 以上残留 → signature 化
    sig_base = re.sub(r'[^a-zA-Z0-9一-龯ぁ-んァ-ヶ]', '_', title.lower())
    signature = re.sub(r'_+', '_', sig_base)[:40].strip('_')
    if not signature:
        signature = f'dashboard_stale_{hashlib.md5(title.encode()).hexdigest()[:8]}'

    # severity 判定 (= 🔴🔴 の数 or keywords)
    if '🔴🔴' in entry or '完全停止' in entry:
        severity = 'blocking'
    elif '🔴' in entry:
        severity = 'normal'
    else:
        severity = 'normal'

    # 既存 signature あれば skip (= dashboard 同 entry 重複避け)
    if signature in data['signature_index']:
        continue

    new_id = f"cand_dash_{now.strftime('%Y%m%d_%H%M%S')}_{stale_count:02d}"
    data['candidates'].append({
        'id': new_id,
        'detected_at': now.isoformat(),
        'source': 'dashboard_stale_24h',
        'signature': signature,
        'severity': severity,
        'keywords': re.findall(r'[一-龯ぁ-んァ-ヶ]{2,}', title)[:5],
        'context': f'dashboard 🚨 entry が {age.days}日{age.seconds//3600}時間 残留\nentry: {title}',
        'hit_count': 1,
        'threshold_reached': severity == 'blocking',  # blocking 1 hit でも残留 = 危険
        'explicit_skill_request': False,
        'status': 'detected',
        'stale_since': seen_at.isoformat(),
    })
    data['signature_index'][signature] = new_id
    stale_count += 1
    print(f"  [新規] {signature[:40]:40s} severity={severity} age={age.days}d{age.seconds//3600}h")

if stale_count == 0:
    print("dashboard 残留 24h 以上の 🚨 entry 検知無し")
else:
    data.setdefault('stats', {})
    data['stats']['total_candidates'] = len(data['candidates'])
    data['stats']['last_dashboard_scan_at'] = now.isoformat()
    with open('queue/skill_candidates.yaml', 'w') as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"\n計 {stale_count} 件の 🚨 残留 candidate 追加")
PY
