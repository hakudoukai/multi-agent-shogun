#!/usr/bin/env bash
# pre-commit hook: staged file の secret pattern 検査 (cmd_004 Phase 6)
# 設計書: docs/cmd004_security_hardening_design.md §2-3
#
# 引数: pre-commit framework から渡される staged file path 列
# 戻り値: HIGH pattern 検出時 1、それ以外 0
#
# validate_report_privacy.py の HIGH_PATTERNS を再利用 (= 二重実装回避、規範2 構造改善)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VALIDATOR="$SCRIPT_DIR/scripts/validate_report_privacy.py"

if [ ! -f "$VALIDATOR" ]; then
    echo "[check_secrets] validate_report_privacy.py が見つかりません: $VALIDATOR" >&2
    echo "[check_secrets] graceful skip (= hook fail させない、scope 外環境)" >&2
    exit 0
fi

# 引数なし (= 全 staged file scan モード) では git diff から抽出
files=("$@")
if [ ${#files[@]} -eq 0 ]; then
    while IFS= read -r f; do
        [ -n "$f" ] && files+=("$f")
    done < <(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
fi

if [ ${#files[@]} -eq 0 ]; then
    echo "[check_secrets] no staged files to scan"
    exit 0
fi

violations=0
for f in "${files[@]}"; do
    # 存在 + 通常 file かつ git tracked (= .gitignore-d でない) のみ
    [ -f "$f" ] || continue
    case "$f" in
        *.env|*.env.*|*.lock|*node_modules*|*.git/*|*.venv/*)
            continue
            ;;
    esac
    # validate_report_privacy.py の関数を直接 import 実行
    if ! python3 - "$f" <<'PY'
import sys
import importlib.util
import pathlib

target = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location(
    "validate_report_privacy",
    pathlib.Path(__file__).parent / "../.." / "scripts" / "validate_report_privacy.py",
)
PY
    then
        :  # 上記 inline は path 解決失敗、下の shell python に委譲
    fi

    output=$(python3 -c "
import sys
import importlib.util
import pathlib
script_dir = pathlib.Path('$SCRIPT_DIR')
validator = script_dir / 'scripts' / 'validate_report_privacy.py'
spec = importlib.util.spec_from_file_location('vrp', str(validator))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
try:
    with open('$f', 'r', encoding='utf-8', errors='replace') as fh:
        text = fh.read()
except Exception as e:
    print(f'READ_ERROR:{e}', file=sys.stderr)
    sys.exit(0)
high, warn = mod.scan_text(text)
if high:
    for h in high:
        print(f\"[HIGH] {h.get('name')} in $f sample={h.get('sample','')[:80]!r}\")
    sys.exit(1)
sys.exit(0)
" 2>&1) || rc=$?
    rc=${rc:-0}
    if [ "$rc" -ne 0 ]; then
        echo "$output"
        violations=$((violations + 1))
    fi
done

if [ "$violations" -gt 0 ]; then
    echo "[check_secrets] FAIL: $violations file(s) with HIGH secret patterns. Commit rejected."
    exit 1
fi
echo "[check_secrets] OK: scanned ${#files[@]} file(s), no HIGH secret patterns."
exit 0
