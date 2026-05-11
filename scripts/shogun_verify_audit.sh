#!/usr/bin/env bash
# scripts/shogun_verify_audit.sh — 信長による実監査データ確認 (= 架空監査検出)
#
# 陛下御差配 2026-05-10:
#   「信長は随時監査の実データ記録を確認し、架空の監査報告に騙されない用に心掛ける事。
#    監査合格と実監査データ確認のフラグをプログラム毎に付ける仕組みを作ること」
#
# Usage:
#   bash scripts/shogun_verify_audit.sh <audit_id_or_target>
#   bash scripts/shogun_verify_audit.sh --random-20pct  (= 20% ランダム検査)
#   bash scripts/shogun_verify_audit.sh --all-yellow    (= 全 🟡 PASS_WITH_CONCERNS 検査)
#
# Output: queue/reports/shogun_verification_log.yaml に検査 entry 追加

set -euo pipefail

# REPO_ROOT は env override 可 (= --preflight test 用)。production では default を使う。
REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
LOG="$REPO_ROOT/queue/reports/shogun_verification_log.yaml"
mkdir -p "$(dirname "$LOG")"
[ -f "$LOG" ] || echo "verifications: []" > "$LOG"

verify_one() {
    local target="$1"
    python3 - "$REPO_ROOT" "$target" <<'PYEOF'
import sys, os, yaml, subprocess, re, json, hashlib
from datetime import datetime, timezone

repo_root, target = sys.argv[1], sys.argv[2]
checks = {
    "codex_log_exists": False,
    "gemini_log_exists": False,
    "commit_hash_valid": False,
    "findings_specific": False,
    "timestamp_consistent": False,
    "related_files_exist": False,
}
flags = []

# 軍師 reports から target_id matching entry を探索
# 2026-05-10 sync 修復: PC suffix 命名規則採用 (= 家康 Option 1)
report_files = [
    f"{repo_root}/queue/reports/kuroda_mainpc_report.yaml",
    f"{repo_root}/queue/reports/takenaka_mainpc_report.yaml",
    f"{repo_root}/queue/reports/naomasa_secondpc_report.yaml",
    f"{repo_root}/queue/reports/acha_secondpc_report.yaml",
]

audit_entry = None
auditor_who = None
for rf in report_files:
    if not os.path.exists(rf): continue
    try:
        d = yaml.safe_load(open(rf)) or {}
        for r in d.get("reports", []) or []:
            if isinstance(r, dict) and (r.get("audit_id") == target or r.get("target_id") == target):
                audit_entry = r
                auditor_who = os.path.basename(rf).replace("_report.yaml","")
                break
    except: pass
    if audit_entry: break

if not audit_entry:
    print(json.dumps({"target": target, "status": "NOT_FOUND", "checks": checks, "flags": ["target audit entry not found in any auditor report"]}, ensure_ascii=False))
    sys.exit(0)

# Check 1: codex/gemini log
log_pattern = audit_entry.get("log_path", "")
if log_pattern and os.path.exists(log_pattern):
    if "codex" in log_pattern.lower():
        checks["codex_log_exists"] = True
    if "gemini" in log_pattern.lower():
        checks["gemini_log_exists"] = True
else:
    flags.append(f"log file not found: {log_pattern or '(no log_path field)'}")

# Check 2: commit_hash valid (= git log で出るか)
ch = audit_entry.get("commit_hash", "")
if ch:
    r = subprocess.run(["git","-C",repo_root,"cat-file","-e",ch], capture_output=True)
    checks["commit_hash_valid"] = (r.returncode == 0)
    if r.returncode != 0:
        flags.append(f"invalid commit_hash: {ch}")

# Check 3: findings 具体性 (= 行番号 / 関数名 / 具体的な観点)
findings = audit_entry.get("findings", []) or []
findings_text = " ".join(str(f) for f in findings) if findings else ""
generic_phrases = ["all good","looks fine","problem none","適切","問題ありません","良好です","特記なし","実装適切"]
generic_count = sum(1 for p in generic_phrases if p in findings_text.lower() or p in findings_text)
specific_count = len(re.findall(r"L\d+|line \d+|\.[a-zA-Z]+:\d+|def \w+|class \w+|function \w+", findings_text))
if findings and specific_count > 0 and generic_count <= 1:
    checks["findings_specific"] = True
elif not findings:
    flags.append("no findings (但し true zero-issue case may be valid)")
else:
    flags.append(f"findings too generic (specific={specific_count}, generic={generic_count})")

# Check 4: timestamp consistency (= audited_at と log mtime の乖離)
audited_at = audit_entry.get("audited_at", "")
if audited_at and log_pattern and os.path.exists(log_pattern):
    log_mtime = os.path.getmtime(log_pattern)
    try:
        a = audited_at.replace("Z","+00:00")
        ts = datetime.fromisoformat(a).timestamp()
        drift = abs(log_mtime - ts)
        checks["timestamp_consistent"] = drift < 60
        if drift >= 60:
            flags.append(f"timestamp drift {int(drift)}s > 60s threshold")
    except: pass

# Check 5: related_files exist
rf = audit_entry.get("related_files", []) or []
if rf:
    all_exist = all(os.path.exists(os.path.join(repo_root, p)) or os.path.exists(p) for p in rf)
    checks["related_files_exist"] = all_exist
    if not all_exist:
        flags.append(f"some related_files do not exist: {[p for p in rf if not (os.path.exists(os.path.join(repo_root,p)) or os.path.exists(p))]}")
else:
    flags.append("no related_files field")

passed = sum(1 for v in checks.values() if v)
total = len(checks)
shogun_verified = (passed >= 4 and "log file not found" not in str(flags) and "invalid commit_hash" not in str(flags))

result = {
    "target": target,
    "auditor_who": auditor_who,
    "shogun_verified": shogun_verified,
    "checks_passed": f"{passed}/{total}",
    "checks": checks,
    "flags": flags,
    "audit_entry_excerpt": {k: audit_entry.get(k) for k in ["audit_id","target_id","verdict","audited_at","commit_hash"] if k in audit_entry},
    "verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
}
print(json.dumps(result, ensure_ascii=False, indent=2))

# Append to verification log
log_path = f"{repo_root}/queue/reports/shogun_verification_log.yaml"
try:
    with open(log_path) as f: log = yaml.safe_load(f) or {}
except: log = {}
log.setdefault("verifications", []).append(result)
with open(log_path, "w") as f: yaml.safe_dump(log, f, allow_unicode=True, default_flow_style=False)
PYEOF
}

# --preflight: completion gate 前の事前 check (= cmd_012 P0-2、陛下御裁可 2026-05-11)
# 返却: stdout に status string + exit code (0..5)。verify log は触らない。
preflight_one() {
    local target="$1"
    local result
    result="$(python3 - "$REPO_ROOT" "$target" <<'PYEOF'
import sys, os, yaml

repo_root, target = sys.argv[1], sys.argv[2]

INDEX_PATH = os.path.join(repo_root, "queue/reports/audit_report_index.yaml")
COMPLETION_GATE_PATH = os.path.join(repo_root, "queue/reports/completion_gate_status.yaml")
REPORT_FILES = [
    os.path.join(repo_root, "queue/reports/kuroda_mainpc_report.yaml"),
    os.path.join(repo_root, "queue/reports/takenaka_mainpc_report.yaml"),
    os.path.join(repo_root, "queue/reports/naomasa_secondpc_report.yaml"),
    os.path.join(repo_root, "queue/reports/acha_secondpc_report.yaml"),
]
SC_REPORTS = [
    os.path.join(repo_root, "queue/reports/naomasa_secondpc_report.yaml"),
    os.path.join(repo_root, "queue/reports/acha_secondpc_report.yaml"),
]
KNOWN_SECTIONS = ("reports", "new_project_audits", "phase_b_reaudits", "additional_cmd_audits")

audit_entry = None
auditor_who = None
source_section = None
unsupported_seen = False

# Step 1: index file (= normalize_audit_reports.py 出力) 優先
if os.path.exists(INDEX_PATH):
    try:
        idx = yaml.safe_load(open(INDEX_PATH)) or {}
        for e in (idx.get("entries") or []):
            if isinstance(e, dict) and e.get("audit_id") == target:
                audit_entry = e
                auditor_who = e.get("auditor_who")
                source_section = e.get("section") or "reports"
                break
    except Exception:
        unsupported_seen = True

# Fallback: PC suffix 命名規則の report files を直接 scan
if audit_entry is None:
    for rf in REPORT_FILES:
        if not os.path.exists(rf):
            continue
        try:
            d = yaml.safe_load(open(rf)) or {}
        except Exception:
            unsupported_seen = True
            continue
        if not isinstance(d, dict):
            unsupported_seen = True
            continue
        for sec in KNOWN_SECTIONS:
            entries = d.get(sec)
            if not isinstance(entries, list):
                continue
            for r in entries:
                if isinstance(r, dict) and (r.get("audit_id") == target or r.get("target_id") == target):
                    audit_entry = r
                    auditor_who = os.path.basename(rf).replace("_report.yaml", "")
                    source_section = sec
                    break
            if audit_entry is not None:
                break
        if audit_entry is not None:
            break
        # 未知 section に audit_id がある場合は schema 非対応として記録
        for key, val in d.items():
            if key in KNOWN_SECTIONS or not isinstance(val, list):
                continue
            for r in val:
                if isinstance(r, dict) and (r.get("audit_id") == target or r.get("target_id") == target):
                    unsupported_seen = True
                    break
            if unsupported_seen:
                break
        if unsupported_seen:
            break

if audit_entry is None:
    if unsupported_seen:
        print("unsupported_report_schema")
        sys.exit(0)
    print("missing_audit_entry")
    sys.exit(0)

# Step 2: target_pc 判定 → secondpc なら SC report file の到達確認
target_pc = audit_entry.get("target_pc")
if not target_pc and os.path.exists(COMPLETION_GATE_PATH):
    try:
        cg = yaml.safe_load(open(COMPLETION_GATE_PATH)) or {}
        for e in (cg.get("entries") or []):
            if isinstance(e, dict) and e.get("audit_id") == target:
                target_pc = e.get("target_pc")
                break
    except Exception:
        pass
if not target_pc and auditor_who:
    if "secondpc" in auditor_who:
        target_pc = "secondpc"
    elif "mainpc" in auditor_who:
        target_pc = "mainpc"

if target_pc == "secondpc":
    if not any(os.path.exists(p) for p in SC_REPORTS):
        print("missing_cross_pc_report")
        sys.exit(0)

# Step 3: source_section が KNOWN_SECTIONS のいずれかであることを確認 (= schema 認識可)
if source_section not in KNOWN_SECTIONS:
    print("unsupported_report_schema")
    sys.exit(0)

# Step 4: partial verdict 検出 (= top-level または perspective_verdicts)
verdict = audit_entry.get("verdict", "")
if isinstance(verdict, str) and "partial" in verdict.lower():
    print("partial_verdict_blocked")
    sys.exit(0)
pv = audit_entry.get("perspective_verdicts")
if isinstance(pv, dict):
    for v in pv.values():
        if isinstance(v, str) and "partial" in v.lower():
            print("partial_verdict_blocked")
            sys.exit(0)

# Step 5: commit_hash 非空 + log_path 実在
ch = audit_entry.get("commit_hash") or ""
lp = audit_entry.get("log_path") or ""
ch_ok = isinstance(ch, str) and ch.strip() != ""
if isinstance(lp, str) and lp.strip():
    lp_full = lp if os.path.isabs(lp) else os.path.join(repo_root, lp)
    lp_ok = os.path.exists(lp_full)
else:
    lp_ok = False
if not (ch_ok and lp_ok):
    print("missing_log_or_commit")
    sys.exit(0)

print("ready_to_verify")
sys.exit(0)
PYEOF
)"
    echo "$result"
    case "$result" in
        ready_to_verify)           return 0 ;;
        missing_audit_entry)       return 1 ;;
        missing_cross_pc_report)   return 2 ;;
        unsupported_report_schema) return 3 ;;
        partial_verdict_blocked)   return 4 ;;
        missing_log_or_commit)     return 5 ;;
        *)
            echo "ERROR: unknown preflight result: $result" >&2
            return 99
            ;;
    esac
}

case "${1:-}" in
    --all)
        # 陛下御差配 2026-05-10 00:10: ランダム sampling 厳禁、全数全件
        # 全軍師 report yaml の全 audit entry を全件 verify
        for rf in queue/reports/{kuroda_mainpc,takenaka_mainpc,naomasa_secondpc,acha_secondpc}_report.yaml; do
            [ -f "$rf" ] || continue
            python3 -c "
import yaml, sys
try:
    d = yaml.safe_load(open('$rf')) or {}
    for r in (d.get('reports') or []):
        if isinstance(r, dict) and r.get('audit_id'):
            print(r['audit_id'])
except: pass" | while IFS= read -r aid; do
                [ -n "$aid" ] && verify_one "$aid"
            done
        done
        ;;
    --random*|--all-yellow)
        echo "ERROR: ランダム sampling は陛下御差配で禁止。--all で全件全数 verify せよ" >&2
        exit 1
        ;;
    --preflight)
        # cmd_012 P0-2: completion gate 前の事前 check (= 6 種 return code)
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 --preflight <audit_id>" >&2
            exit 1
        fi
        set +e
        preflight_one "$2"
        ec=$?
        set -e
        exit "$ec"
        ;;
    "")
        echo "Usage: $0 <audit_id_or_target_id> | --all (= 全数全件 verify、必ず全件)" >&2
        echo "       $0 --preflight <audit_id>  (= completion gate 前の事前 check)" >&2
        echo "陛下御差配: ランダム sampling 厳禁、時間より正確さ優先、全数主義" >&2
        exit 1
        ;;
    *)
        verify_one "$1"
        ;;
esac
