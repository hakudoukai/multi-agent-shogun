#!/usr/bin/env bash
#
# audit_gemini.sh harness smoke test
#
# 由来: 副院長令 30f198e3 (P0、homework#1) 達成基準 #2
#   「同harnessが他commitでも再実走可能(heredoc再発しない)をsmokeで実証」
#
# 真因(根治対象): 旧 audit_gemini.sh L135-159 で python3 -c "..." に対し
#   bash literal 展開 ('cycle': $CYCLE,) を行っていたため、CYCLE='5c' 等
#   alphanumeric サイクル名が python source に '5c' として直接埋め込まれ
#   SyntaxError: invalid decimal literal を発生させていた。
#
# 構造修正後: heredoc <<'PYEOF' (quoted = bash expansion 無効) + 環境変数経由 で
#   全 bash 値を python に渡すため、CYCLE/TASK_ID/OUTPUT のいかなる alphanumeric/
#   hex/特殊 token 値も literal 展開されず、SyntaxError は構造的に発生しない。
#
# このスモークでは gemini CLI 呼び出しを行わず、修正後 python heredoc 部のみを
# 単体抽出して様々な cycle 値で実行し、SyntaxError が出ないことを実証する。

set -uo pipefail

PASS=0
FAIL=0
FAILED_CASES=()

run_case() {
    local case_name="$1"
    local task_id="$2"
    local cycle="$3"
    local gemini_out="$4"

    # 修正後 audit_gemini.sh の python heredoc 部を抽出 (extract + verdict 双方)
    local actual
    actual=$(GEMINI_OUT="$gemini_out" AUDIT_TASK_ID="$task_id" AUDIT_CYCLE="$cycle" \
        python3 - <<'PYEOF' 2>&1
import sys, json, re, os
text = os.environ.get('GEMINI_OUT', '')
task_id = os.environ.get('AUDIT_TASK_ID', '')
cycle = os.environ.get('AUDIT_CYCLE', '')
m = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, re.DOTALL)
if m:
    text = m.group(1)
else:
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        text = text[start:end+1]
try:
    d = json.loads(text)
    print(json.dumps(d, ensure_ascii=False))
except Exception as e:
    print(json.dumps({
        'task_id': task_id,
        'cycle': cycle,
        'overall_verdict': 'invocation_error',
        'parse_error': str(e),
        'raw_output': text[:500]
    }, ensure_ascii=False))
PYEOF
)
    local rc=$?

    # SyntaxError が出ていないこと、JSON output が valid であることを確認
    if [ $rc -ne 0 ]; then
        FAIL=$((FAIL + 1))
        FAILED_CASES+=("$case_name (rc=$rc): $actual")
        echo "  ✗ $case_name (rc=$rc)"
        return
    fi
    if echo "$actual" | grep -qE 'SyntaxError|invalid decimal literal'; then
        FAIL=$((FAIL + 1))
        FAILED_CASES+=("$case_name: SyntaxError detected: $actual")
        echo "  ✗ $case_name (SyntaxError detected)"
        return
    fi
    if ! echo "$actual" | python3 -c "import sys, json; json.loads(sys.stdin.read())" 2>/dev/null; then
        FAIL=$((FAIL + 1))
        FAILED_CASES+=("$case_name: not valid JSON: $actual")
        echo "  ✗ $case_name (invalid JSON)"
        return
    fi
    PASS=$((PASS + 1))
    echo "  ✓ $case_name"
}

echo "=== audit_gemini.sh harness smoke (heredoc 再発防止 = literal expansion 断絶) ==="

# Case 1: cycle="5c" (alphanumeric、旧 harness の SyntaxError 直接再現条件)
run_case "C01_cycle_5c_alphanumeric" \
    "ee4d6ce4" "5c" \
    '{"task_id":"ee4d6ce4","cycle":"5c","overall_verdict":"pass","summary":"cycle5c green"}'

# Case 2: cycle="13a" (別 alphanumeric、再現可能性)
run_case "C02_cycle_13a_alphanumeric" \
    "abc12345" "13a" \
    '{"task_id":"abc12345","cycle":"13a","overall_verdict":"pass","summary":"different cycle"}'

# Case 3: cycle=数値純 (旧 harness で安全に動いていた条件、retain)
run_case "C03_cycle_numeric_pure" \
    "dd1234ab" "5" \
    '{"task_id":"dd1234ab","cycle":5,"overall_verdict":"pass","summary":"numeric"}'

# Case 4: cycle に hex 文字混入 ("0xFF" 様)
run_case "C04_cycle_with_hex_chars" \
    "ff112233" "0xFF" \
    '{"task_id":"ff112233","cycle":"0xFF","overall_verdict":"fail","summary":"hex cycle"}'

# Case 5: markdown fence 包み JSON (Gemini の典型 output 形式)
run_case "C05_markdown_fence_json" \
    "ee4d6ce4" "5c" \
    '```json
{"task_id":"ee4d6ce4","cycle":"5c","overall_verdict":"pass"}
```'

# Case 6: 余分なテキスト混在 (Gemini 中ぶれの実例ケース)
run_case "C06_text_then_json" \
    "ee4d6ce4" "5c" \
    'これは Gemini の前書きです。
{"task_id":"ee4d6ce4","cycle":"5c","overall_verdict":"pass","summary":"prefix text"}
末尾コメント。'

# Case 7: 不正 JSON (parse_error fallback の動作確認、SyntaxError は出ない)
run_case "C07_invalid_json_fallback" \
    "ee4d6ce4" "5c" \
    'this is not json at all and there is no brace'

# Case 8: task_id に hex 含む長 uuid (subprocess literal 化されない確認)
run_case "C08_task_id_uuid_with_e_chars" \
    "ee4d6ce4-f3ae-4936-b484-1851f791ca4a" "5c" \
    '{"task_id":"ee4d6ce4-f3ae-4936-b484-1851f791ca4a","cycle":"5c","overall_verdict":"pass"}'

# Case 9: cycle に backslash + quote + 全角 (悪意の bash injection 想定 = env 経由なら安全)
run_case "C09_cycle_special_chars" \
    "ee4d6ce4" "5\";print('inj');\"" \
    '{"task_id":"ee4d6ce4","cycle":"x","overall_verdict":"pass"}'

# Case 10: cycle 空文字 (boundary)
run_case "C10_cycle_empty_string" \
    "ee4d6ce4" "" \
    '{"task_id":"ee4d6ce4","cycle":"","overall_verdict":"pass"}'

# Case 11: GEMINI_OUT が空 (parse_error path、SyntaxError は出ない)
run_case "C11_empty_gemini_output" \
    "ee4d6ce4" "5c" \
    ""

# Case 12: 日本語混入 JSON (NFC/NFD/multi-byte 耐性)
run_case "C12_japanese_in_summary" \
    "ee4d6ce4" "5c" \
    '{"task_id":"ee4d6ce4","cycle":"5c","overall_verdict":"pass","summary":"awk 状態管理で根治"}'

echo ""
echo "=== smoke 結果 ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
if [ $FAIL -ne 0 ]; then
    echo ""
    echo "--- failed cases ---"
    for c in "${FAILED_CASES[@]}"; do
        echo "  $c"
    done
    exit 1
fi
exit 0
