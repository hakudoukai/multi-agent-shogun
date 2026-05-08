#!/usr/bin/env bash
# tests/migrations/test_organizational_lessons_rls.sh
# cmd_organizational_lessons_supabase_001 cycle2 — RLS + trigger 実 apply test
#
# 動作:
#   1. ephemeral PostgreSQL (pgserver, bundled binary, sudo 不要) を起動
#   2. backend/migrations/007_organizational_lessons.sql を apply
#   3. authenticated 相当 role + SET LOCAL app.current_agent='<role>' で
#      INSERT / SELECT / DELETE を実行し RLS + SECURITY DEFINER trigger 挙動を検証
#   4. 全テスト PASS で exit 0、いずれか FAIL で exit 1
#
# 検証項目 (task subtask_organizational_lessons_supabase_001_cycle2 仕様):
#   - INSERT 成功 + audit row 生成 (writer = honda / hideyoshi / shogun)
#   - ashigaru INSERT 失敗
#   - rijicho DELETE 成功 / 他 role DELETE 失敗 (RLS USING で row 不可視 → rowcount=0)
#   - SELECT 全 agent 可
#   - audit_log() が SECURITY DEFINER + search_path 固定であること
#
# 前提: python3 + pip + venv が利用可能 (= sudo 不要)
# 既存資産: tests/checks 系 fixture pattern を踏襲、独自 framework は作らず

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv-pg-test"
PYTHON_HARNESS="${REPO_ROOT}/tests/migrations/test_organizational_lessons_rls.py"

# ----------------------------------------------------------------
# venv bootstrap (idempotent, 初回のみ pip install)
# ----------------------------------------------------------------
if [[ ! -x "${VENV_DIR}/bin/python3" ]]; then
    echo "[setup] creating venv at ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
fi

if ! "${VENV_DIR}/bin/python3" -c "import pgserver, psycopg" 2>/dev/null; then
    echo "[setup] installing pgserver + psycopg[binary] (initial run only)"
    "${VENV_DIR}/bin/pip" install --quiet --upgrade pip
    "${VENV_DIR}/bin/pip" install --quiet pgserver "psycopg[binary]"
fi

# ----------------------------------------------------------------
# Run python harness
# ----------------------------------------------------------------
exec "${VENV_DIR}/bin/python3" "${PYTHON_HARNESS}" "$@"
