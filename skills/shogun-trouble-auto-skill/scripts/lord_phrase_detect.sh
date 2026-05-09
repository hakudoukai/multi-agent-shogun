#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# lord_phrase_detect.sh — Lord 発話 trouble phrase 検知 + 集約
#
# 拡張 #2 — 拙者 (Claude Code shogun) が Lord の各発言後に呼出する想定。
# 「毎日トラブル」「また同じ」「何度も」等の phrase を検知 → candidates.yaml 更新。
#
# Usage:
#   bash skills/shogun-trouble-auto-skill/scripts/lord_phrase_detect.sh "<lord_message>"
#
# 出力 (stdout):
#   検知無し → "no_match"
#   検知あり → "match: signature=<sig> severity=<sev> hit_count=<n> threshold_reached=<bool>"
# ════════════════════════════════════════════════════════════════
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

LORD_MSG="${1:-}"
[ -z "$LORD_MSG" ] && { echo "Usage: $0 '<lord_message>'"; exit 2; }

CANDIDATES="queue/skill_candidates.yaml"
[ -f "$CANDIDATES" ] || { echo "ERR: $CANDIDATES 不在"; exit 2; }

# Python で集約処理 (= bash で yaml は重い)
LORD_MSG="$LORD_MSG" python3 <<'PY'
import os, sys, yaml, re, hashlib
from datetime import datetime, timedelta, timezone

msg = os.environ['LORD_MSG']

# trouble phrase 群 (= SKILL.md Rule 1 と同期)
TROUBLE_PATTERNS = [
    r'毎日.*?トラブル', r'また.*?同じ', r'何度も', r'繰り返し',
    r'もう一度.*?(?:同じ|トラブル|エラー)', r'またか', r'また.*?起き',
    r'毎回', r'同じ問題', r'前にも', r'前回も',
]
SKILL_REQUEST = [r'スキル化', r'skill\s*化', r'自動化して']

# severity 自動判定
SEVERITY_BLOCKING = [
    '停止', '不能', 'failed', 'エラー', 'blocker', '接続不能',
    '使えな', '動かな', '繋がらな', '繋がな', 'つながらな',
    '反応しな', '応答しな', '落ちて', 'crash', 'down', 'block'
]
SEVERITY_COSMETIC = ['UI', 'format', 'warning', 'alignment', 'typo', 'cosmetic']

trouble_hit = any(re.search(p, msg) for p in TROUBLE_PATTERNS)
explicit = any(re.search(p, msg) for p in SKILL_REQUEST)

if not (trouble_hit or explicit):
    print("no_match")
    sys.exit(0)

# signature 抽出 — keyword 化 (= 直近 50 文字の word を抽出)
words = re.findall(r'[ぁ-んァ-ヶー一-龯a-zA-Z]{2,}', msg)
STOPWORDS = {'陛下','拙者','兄上','弟御','御差配','仕る','信長','家康',
             'です','ます','して','する','された','という','こと','もの',
             'これ','それ','あれ','この','その','あの','よう','ため',
             '今日','今','もう','また','まだ','とても','ちょっと'}
significant = [w for w in words if w not in STOPWORDS and len(w) >= 2]
sig_keywords = significant[:5]
# signature: 上位 3 keyword を _ で連結、ASCII 化 (= ROMAJI 不可ゆえ md5 短縮で代替)
if sig_keywords:
    raw = '_'.join(sig_keywords[:3])
    if re.match(r'^[a-zA-Z0-9_]+$', raw):
        signature = raw.lower()
    else:
        signature = sig_keywords[0][:20] + '_' + hashlib.md5(raw.encode()).hexdigest()[:8]
else:
    signature = 'unknown_' + hashlib.md5(msg.encode()).hexdigest()[:8]

severity = 'normal'
if any(k in msg for k in SEVERITY_BLOCKING):
    severity = 'blocking'
elif any(k in msg for k in SEVERITY_COSMETIC):
    severity = 'cosmetic'

# candidates 更新
with open('queue/skill_candidates.yaml') as f:
    data = yaml.safe_load(f)
data.setdefault('candidates', [])
data.setdefault('signature_index', {})
data.setdefault('config', {'thresholds': {'blocking': 2, 'normal': 3, 'cosmetic': 5}, 'time_window_days': 7})

now = datetime.now(timezone.utc)
existing_id = data['signature_index'].get(signature)

if existing_id:
    # hit_count++
    for c in data['candidates']:
        if c['id'] == existing_id:
            c['hit_count'] = c.get('hit_count', 1) + 1
            c['last_detected_at'] = now.isoformat()
            target = c
            break
else:
    new_id = f"cand_{now.strftime('%Y%m%d_%H%M%S')}"
    target = {
        'id': new_id,
        'detected_at': now.isoformat(),
        'source': 'lord_speech_auto',
        'signature': signature,
        'severity': severity,
        'keywords': sig_keywords,
        'context': f'Lord 発話自動検知: "{msg[:200]}"',
        'hit_count': 1,
        'threshold_reached': False,
        'explicit_skill_request': explicit,
        'status': 'detected',
    }
    data['candidates'].append(target)
    data['signature_index'][signature] = new_id

# 閾値判定 (= 7 日窓内集計)
window = data['config'].get('time_window_days', 7)
n = data['config']['thresholds'].get(target['severity'], 3)
recent_hits = 0
for c in data['candidates']:
    if c['signature'] != signature:
        continue
    try:
        dt = datetime.fromisoformat(str(c.get('detected_at')).replace('Z','+00:00'))
        if (now - dt).days <= window:
            recent_hits += c.get('hit_count', 1)
    except Exception:
        recent_hits += c.get('hit_count', 1)

if recent_hits >= n or explicit:
    target['threshold_reached'] = True
    if target.get('status') == 'detected':
        target['status'] = 'aggregated' if not explicit else 'threshold_reached'

# stats 更新
data.setdefault('stats', {})
data['stats']['total_candidates'] = len(data['candidates'])
data['stats']['last_scan_at'] = now.isoformat()

with open('queue/skill_candidates.yaml', 'w') as f:
    yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

print(f"match: signature={signature} severity={target['severity']} hit_count={recent_hits} threshold_reached={target['threshold_reached']} explicit={explicit}")
PY
