#!/usr/bin/env bash
# Dependency audit script (cmd_004 Phase 6)
# 設計書: docs/cmd004_security_hardening_design.md §3
#
# Backend (Python): pip-audit / safety (optional)
# Frontend (Node): npm audit
#
# Tool 不在環境では graceful skip + 警告のみ (= 規範4 仕組み追加 vs 改修区別)
set -uo pipefail

EXIT_CODE=0
DRY_RUN=0
BACKEND_REQ="${BACKEND_REQ:-/mnt/c/Projects/hakudokai-dev/backend/requirements.txt}"
FRONTEND_DIR="${FRONTEND_DIR:-/mnt/c/Projects/hakudokai-dev/frontend}"

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=1; shift ;;
        --backend-req) BACKEND_REQ="$2"; shift 2 ;;
        --frontend-dir) FRONTEND_DIR="$2"; shift 2 ;;
        *) shift ;;
    esac
done

log() { echo "[dependency_audit] $*"; }

audit_backend_pip() {
    if ! command -v pip-audit >/dev/null 2>&1; then
        log "pip-audit not installed — skip (recommend: pip install pip-audit)"
        return 0
    fi
    if [ ! -f "$BACKEND_REQ" ]; then
        log "backend requirements.txt not found: $BACKEND_REQ — skip"
        return 0
    fi
    log "running pip-audit -r $BACKEND_REQ ..."
    if [ "$DRY_RUN" -eq 1 ]; then
        log "DRY_RUN — skipping actual scan"
        return 0
    fi
    pip-audit -r "$BACKEND_REQ" --strict
    return $?
}

audit_backend_safety() {
    if ! command -v safety >/dev/null 2>&1; then
        log "safety not installed — skip (recommend: pip install safety)"
        return 0
    fi
    log "running safety check ..."
    if [ "$DRY_RUN" -eq 1 ]; then
        log "DRY_RUN — skipping actual scan"
        return 0
    fi
    safety check -r "$BACKEND_REQ" --output text
    return $?
}

audit_frontend_npm() {
    if [ ! -d "$FRONTEND_DIR" ]; then
        log "frontend dir not found: $FRONTEND_DIR — skip"
        return 0
    fi
    if [ ! -f "$FRONTEND_DIR/package-lock.json" ] && [ ! -f "$FRONTEND_DIR/package.json" ]; then
        log "frontend package.json/package-lock.json not found — skip"
        return 0
    fi
    if ! command -v npm >/dev/null 2>&1; then
        log "npm not installed — skip"
        return 0
    fi
    log "running npm audit (level=high) ..."
    if [ "$DRY_RUN" -eq 1 ]; then
        log "DRY_RUN — skipping actual scan"
        return 0
    fi
    (cd "$FRONTEND_DIR" && npm audit --audit-level=high)
    return $?
}

log "=== backend (pip-audit) ==="
if ! audit_backend_pip; then EXIT_CODE=1; fi

log "=== backend (safety, optional supplement) ==="
audit_backend_safety || true  # safety は補完、結果は EXIT_CODE に影響させない

log "=== frontend (npm audit) ==="
if ! audit_frontend_npm; then EXIT_CODE=1; fi

if [ "$EXIT_CODE" -eq 0 ]; then
    log "OK: no HIGH+ vulnerabilities found (or all tools skipped)"
else
    log "FAIL: vulnerabilities detected — review output above"
fi

exit "$EXIT_CODE"
