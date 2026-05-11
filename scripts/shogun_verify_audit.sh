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

# cmd_013 Stream B: --pc-id <mainpc|secondpc> で writer-owned log path を選択。
# env PC_ID も同等扱い。未指定なら legacy shogun_verification_log.yaml に書込 (= backward compat)。
# 各 PC は自 suffix file のみ書込、他 PC file は read-only。
PC_ID="${PC_ID:-}"
while [ "${1:-}" = "--pc-id" ]; do
    PC_ID="${2:-}"
    shift 2 || true
done

case "$PC_ID" in
    mainpc)   LOG_BASENAME="shogun_verification_mainpc_log.yaml" ;;
    secondpc) LOG_BASENAME="shogun_verification_secondpc_log.yaml" ;;
    "")       LOG_BASENAME="shogun_verification_log.yaml" ;;
    *)
        echo "ERROR: unknown PC_ID='$PC_ID' (= mainpc|secondpc only)" >&2
        exit 1
        ;;
esac
LOG="$REPO_ROOT/queue/reports/$LOG_BASENAME"
mkdir -p "$(dirname "$LOG")"
[ -f "$LOG" ] || echo "verifications: []" > "$LOG"

verify_one() {
    local target="$1"
    python3 - "$REPO_ROOT" "$target" "$LOG" <<'PYEOF'
import sys, os, yaml, subprocess, re, json, hashlib
from datetime import datetime, timezone

repo_root, target, log_path_arg = sys.argv[1], sys.argv[2], sys.argv[3]
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

# Append to verification log (= cmd_013 Stream B: writer-owned log path)
log_path = log_path_arg
try:
    with open(log_path) as f: log = yaml.safe_load(f) or {}
except: log = {}
log.setdefault("verifications", []).append(result)
with open(log_path, "w") as f: yaml.safe_dump(log, f, allow_unicode=True, default_flow_style=False)
PYEOF
}

# --preflight: completion gate 前の事前 check (= cmd_012 P0-2、陛下御裁可 2026-05-11)
# SC preflight fix (cmd_014 統合): audit_report_index.yaml の reports: キーを正しく参照。
# 返却: exit code (0=ready / 1=missing / 2=cross_pc / 3=schema / 4=partial / 5=log_commit)
preflight_one() {
    local audit_id="$1"
    local INDEX="$REPO_ROOT/queue/reports/audit_report_index.yaml"

    python3 - "$REPO_ROOT" "$audit_id" "$INDEX" <<'PYEOF'
import sys, os, yaml

repo_root, audit_id, index_path = sys.argv[1], sys.argv[2], sys.argv[3]

KNOWN_REPORT_FILES = [
    f"{repo_root}/queue/reports/kuroda_mainpc_report.yaml",
    f"{repo_root}/queue/reports/takenaka_mainpc_report.yaml",
    f"{repo_root}/queue/reports/naomasa_secondpc_report.yaml",
    f"{repo_root}/queue/reports/acha_secondpc_report.yaml",
]
KNOWN_SECTIONS = {"reports"}

entry = None

# 1. Check audit_report_index.yaml first.
#    SC fix: support both 'reports:' (canonical) and 'entries:' (legacy) keys.
if os.path.exists(index_path):
    try:
        with open(index_path) as f:
            index = yaml.safe_load(f) or {}
    except Exception:
        index = {}
    index_entries = index.get("reports") or index.get("entries") or []
    for r in (index_entries if isinstance(index_entries, list) else []):
        if isinstance(r, dict) and r.get("audit_id") == audit_id:
            entry = r
            break
    if entry is not None:
        evidence_state = entry.get("evidence_state", "")
        target_pc = entry.get("target_pc", "")
        if evidence_state == "cross_pc_missing" or target_pc == "secondpc":
            print(f"missing_cross_pc_report: evidence_state=cross_pc_missing for {audit_id}")
            sys.exit(2)
        if evidence_state == "schema_unsupported":
            print(f"unsupported_report_schema: evidence_state=schema_unsupported for {audit_id}")
            sys.exit(3)

# 2. MC base: fallback to direct report file scan when not in index.
if entry is None:
    for rf in KNOWN_REPORT_FILES:
        if not os.path.exists(rf):
            continue
        try:
            d = yaml.safe_load(open(rf)) or {}
        except Exception:
            continue
        for section_key, section_data in d.items():
            if not isinstance(section_data, list):
                continue
            for r in section_data:
                if isinstance(r, dict) and r.get("audit_id") == audit_id:
                    if section_key not in KNOWN_SECTIONS:
                        print(f"unsupported_report_schema: entry found in unrecognized section '{section_key}' for {audit_id}")
                        sys.exit(3)
                    entry = r
                    break
            if entry is not None:
                break
        if entry is not None:
            break

# 3. Not found anywhere → missing_audit_entry
if entry is None:
    print(f"missing_audit_entry: {audit_id} not found in any auditor report or index")
    sys.exit(1)

# 4. partial verdict → partial_verdict_blocked
verdict = entry.get("verdict", "")
if verdict == "partial":
    print(f"partial_verdict_blocked: verdict=partial is not a terminal verdict for {audit_id}")
    sys.exit(4)

# 5. log_path or commit_hash missing → missing_log_or_commit
log_path = entry.get("log_path", "")
commit_hash = entry.get("commit_hash", "")
if not log_path or not commit_hash:
    print(f"missing_log_or_commit: log_path={log_path!r} commit_hash={commit_hash!r} for {audit_id}")
    sys.exit(5)

# 6. all preflight checks passed
print(f"ready_to_verify: {audit_id} passes all preflight checks")
sys.exit(0)
PYEOF
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
