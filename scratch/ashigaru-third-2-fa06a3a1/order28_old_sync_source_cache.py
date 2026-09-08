#!/usr/bin/env python3
"""
source_code_cache自動同期スクリプト v3.0

v2からの変更点:
- SQL生成のみ → Supabase REST API経由で直接UPSERT
- git rm済みファイルのcache自動削除
- --dry-run でSQL出力のみ（後方互換）
"""
import io
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import fnmatch

import httpx
from dotenv import load_dotenv

# Windows cp932対策 (ガード付き)
# 無条件のTextIOWrapper差し替えはpytest等のcaptureストリームを破壊する
# (旧wrapperのGCで下層fileがcloseされ "I/O operation on closed file")。
# 実コンソールがUTF-8でない場合のみ包み直す。
def _force_utf8(stream):
    try:
        enc = (getattr(stream, "encoding", "") or "").lower()
        if hasattr(stream, "buffer") and enc not in ("utf-8", "utf8"):
            return io.TextIOWrapper(stream.buffer, encoding="utf-8")
    except Exception:
        pass
    return stream

sys.stdout = _force_utf8(sys.stdout)
sys.stderr = _force_utf8(sys.stderr)

# backend/.env を読み込む
_env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(_env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# ===== 同期対象のglobパターン =====
INCLUDE_PATTERNS = [
    "frontend/src/**/*.tsx",
    "frontend/src/**/*.ts",
    "backend/**/*.py",
    "tests/**/*.py",
    "tools/**/*.py",
    "scripts/**/*.py",
    "scripts/**/*.ps1",
    "scripts/**/*.sh",
    "scripts/git-hooks/*",
    "infra/**/*.tf",
    "infra/**/*.ps1",
    "infra/**/*.md",
    "supabase/migrations/*.sql",
    "supabase/functions/**/*.ts",
    "supabase/seed/*.sql",
    "supabase/policies/*.sql",
    "docs/audits/**/*.md",
    "docs/audits/**/*.txt",
    "docs/audits/**/*.patch",
    "docs/codex_audits/**/*.md",
    "docs/codex_audits/**/*.txt",
    "docs/gemini_audits/**/*.md",
    "docs/gemini_audits/**/*.txt",
    "CLAUDE.md",
    ".claude/rules/*.md",
    ".claude/agents/*.md",
    ".claude/commands/*.md",
    ".claude/skills/**/*.md",
    # 副医院長 453ca4a4 命令 (理事長直接命令): 監査永続化対象を拡張
    "docs/audits/**/*.md",
    "docs/audits/**/*.txt",
    "docs/audits/**/*.log",
    "supabase/migrations/*.sql",
    "supabase/functions/**/*.ts",
    ".cache/audit_redo/**/*.md",
    ".cache/audit_redo/**/*.txt",
]

# ===== 除外パターン =====
EXCLUDE_PATTERNS = [
    "**/__pycache__/**",
    "**/node_modules/**",
    "**/dist/**",
    "**/.git/**",
    "frontend/src/vite-env.d.ts",
]

# ===== 除外ディレクトリ名（高速フィルタ） =====
EXCLUDE_DIRS = {"node_modules", "__pycache__", "dist", ".git"}

# ===== UPSERT バッチサイズ =====
BATCH_SIZE = 50


def should_exclude(file_path: str) -> bool:
    """除外パターンに一致するか判定"""
    for pattern in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False


def collect_files(repo_root: Path) -> list[str]:
    """globパターンで同期対象ファイルを収集"""
    files = set()
    for pattern in INCLUDE_PATTERNS:
        for path in repo_root.glob(pattern):
            if not path.is_file():
                continue
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            rel = str(path.relative_to(repo_root)).replace("\\", "/")
            if not should_exclude(rel):
                files.add(rel)
    return sorted(files)


def get_commit_hash() -> str:
    """現在のgit commitハッシュを取得"""
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _headers() -> dict[str, str]:
    """Supabase REST API 共通ヘッダー"""
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def upsert_batch(rows: list[dict]) -> int:
    """source_code_cacheにバッチUPSERT。成功件数を返す。"""
    url = f"{SUPABASE_URL}/rest/v1/source_code_cache"
    headers = {
        **_headers(),
        "Prefer": "return=minimal,resolution=merge-duplicates",
    }
    resp = httpx.post(
        url, headers=headers,
        params={"on_conflict": "file_path"},
        content=json.dumps(rows, ensure_ascii=False),
        timeout=60.0,
    )
    resp.raise_for_status()
    return len(rows)


# 一過性(サーバ側)障害の分類 (相談役seq129641 blocker2):
# 共有インフラの503/521等を「ファイル毒」と誤分類しない。
TRANSIENT_HTTP_STATUS = {429, 500, 502, 503, 504, 520, 521, 522, 523, 524, 525}
MAX_UPSERT_TRIES = 3  # 初回+リトライ2回 (backoff 1s→2s)


def is_transient_error(exc: Exception) -> bool:
    """サーバ側/経路起因で再試行に意味がある失敗か (=ファイル内容の毒ではない)。"""
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in TRANSIENT_HTTP_STATUS
    return False


def upsert_batch_with_retry(rows: list[dict]) -> int:
    """transient障害はbounded backoff付きで再試行。非transientは即raise。"""
    delay = 1.0
    for attempt in range(1, MAX_UPSERT_TRIES + 1):
        try:
            return upsert_batch(rows)
        except Exception as e:
            if is_transient_error(e) and attempt < MAX_UPSERT_TRIES:
                print(f"-- TRANSIENT ({type(e).__name__}): retry {attempt}/{MAX_UPSERT_TRIES - 1} in {delay:.0f}s", file=sys.stderr)
                time.sleep(delay)
                delay *= 2
                continue
            raise


def compute_stale_paths(cached_paths: set[str], all_local_paths: set[str]) -> set[str]:
    """cacheにあるがローカルに実在しないINCLUDE対象パスを算出する純関数。

    ★母集合は必ず「repo全体のcollect_files結果」を渡すこと。--changed-onlyの
    縮小集合を渡すと、未変更だが実在する全ファイルがstale誤認され大量DELETEされる
    (相談役seq129633監査で発見された潜在欠陥。現cacheでは2113件が誤削除候補だった)。
    """
    stale: set[str] = set()
    for cp in cached_paths:
        if cp in all_local_paths:
            continue
        for pattern in INCLUDE_PATTERNS:
            if fnmatch.fnmatch(cp, pattern):
                stale.add(cp)
                break
    return stale


def upsert_with_isolation(batch: list[dict]) -> tuple[int, int]:
    """batch UPSERTし、失敗時は1件ずつ隔離リトライして毒ファイルを特定する。

    従来はbatch内1件の不良で50件全部がエラー計上され、どのファイルが原因か
    分からないまま6日間の同期停止を招いた(task f46d46a9)。戻り値は(成功数, 失敗数)。
    """
    try:
        upsert_batch_with_retry(batch)
        return len(batch), 0
    except Exception as e:
        if is_transient_error(e):
            # サーバ側障害が retry 後も継続 → 個別隔離するとHTTP呼出が最大50倍に
            # 増幅するだけ(相談役seq129650実測153回)。fan-outせず即停止する。
            print(f"-- TRANSIENT_BATCH_FAILURE ({len(batch)} files): server-side outage persists, "
                  f"no per-row fan-out: {e}", file=sys.stderr)
            return 0, len(batch)
        print(f"-- BATCH FAILED ({len(batch)} files) -> 1件ずつ隔離リトライ: {e}", file=sys.stderr)
    ok = 0
    ng = 0
    for row in batch:
        try:
            upsert_batch_with_retry([row])
            ok += 1
        except Exception as e:
            ng += 1
            if is_transient_error(e):
                # サーバ側障害: ファイルの毒ではない (誤分類禁止・相談役seq129641)
                print(f"-- TRANSIENT FAILURE (server-side, not file poison): {row['file_path']}: {e}", file=sys.stderr)
            else:
                print(f"-- POISON FILE isolated: {row['file_path']}: {e}", file=sys.stderr)
    return ok, ng


def get_cached_paths() -> set[str]:
    """source_code_cacheに存在する全file_pathを取得"""
    url = f"{SUPABASE_URL}/rest/v1/source_code_cache"
    headers = {**_headers()}
    all_paths: set[str] = set()
    offset = 0
    limit = 1000
    while True:
        resp = httpx.get(
            url, headers=headers,
            params={"select": "file_path", "offset": str(offset), "limit": str(limit)},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        for row in data:
            all_paths.add(row["file_path"])
        if len(data) < limit:
            break
        offset += limit
    return all_paths


def delete_stale(stale_paths: set[str]) -> int:
    """cacheから削除されたファイルを除去。削除件数を返す。"""
    if not stale_paths:
        return 0
    url = f"{SUPABASE_URL}/rest/v1/source_code_cache"
    headers = {
        **_headers(),
        "Prefer": "return=minimal",
    }
    # PostgRESTのin演算子: file_path=in.(path1,path2,...)
    # パスにカンマが含まれることはないので安全
    paths_csv = ",".join(f'"{p}"' for p in sorted(stale_paths))
    resp = httpx.request(
        "DELETE", url, headers=headers,
        params={"file_path": f"in.({paths_csv})"},
        timeout=30.0,
    )
    resp.raise_for_status()
    return len(stale_paths)


def escape_sql(text: str) -> str:
    """SQLインジェクション防止のエスケープ（dry-run用）"""
    return text.replace("'", "''")


def generate_upsert_sql(file_path: str, content: str, commit_hash: str) -> str:
    """1ファイル分のUPSERT SQLを生成（dry-run用）"""
    escaped_content = escape_sql(content)
    escaped_path = escape_sql(file_path)
    line_count = content.count('\n') + 1
    file_size = len(content.encode('utf-8'))
    return f"""INSERT INTO source_code_cache (file_path, content, line_count, file_size, commit_hash, updated_at)
VALUES ('{escaped_path}', '{escaped_content}', {line_count}, {file_size}, '{commit_hash}', now())
ON CONFLICT (file_path) DO UPDATE SET
  content = EXCLUDED.content,
  line_count = EXCLUDED.line_count,
  file_size = EXCLUDED.file_size,
  commit_hash = EXCLUDED.commit_hash,
  updated_at = now();"""


def main():
    repo_root = Path(__file__).parent.parent  # scripts/ の親 = リポジトリルート
    commit_hash = get_commit_hash()

    dry_run = "--dry-run" in sys.argv
    changed_only = "--changed-only" in sys.argv

    # Supabase接続チェック（dry-run以外）
    if not dry_run and (not SUPABASE_URL or not SUPABASE_KEY):
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_KEY が未設定", file=sys.stderr)
        print("  backend/.env を確認してください", file=sys.stderr)
        sys.exit(1)

    # 同期対象ファイル収集
    if changed_only:
        # origin/mainとの差分を使い、マージコミットでも全変更を検出
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            capture_output=True, text=True, cwd=repo_root
        )
        # origin/mainが取得できない場合のフォールバック
        if result.returncode != 0:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                capture_output=True, text=True, cwd=repo_root
            )
        changed_files = set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
        all_sync_files = collect_files(repo_root)
        sync_files = [f for f in all_sync_files if f in changed_files]
        print(f"-- Changed-only mode: {len(sync_files)} of {len(all_sync_files)} files changed", file=sys.stderr)
    else:
        sync_files = collect_files(repo_root)
        print(f"-- Full sync mode: {len(sync_files)} files detected", file=sys.stderr)

    # ===== dry-run: SQL出力のみ =====
    if dry_run:
        for file_path in sync_files:
            full_path = repo_root / file_path
            if not full_path.exists():
                continue
            try:
                content = full_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            if not content.strip():
                continue
            print(generate_upsert_sql(file_path, content, commit_hash))
            print()
        print(f"-- Dry-run complete: {len(sync_files)} files", file=sys.stderr)
        return

    # ===== 実行モード: Supabase REST API経由でUPSERT =====
    now_iso = datetime.now(timezone.utc).isoformat()
    synced = 0
    skipped = 0
    errors = 0
    batch: list[dict] = []

    for file_path in sync_files:
        full_path = repo_root / file_path
        if not full_path.exists():
            print(f"-- SKIP (not found): {file_path}", file=sys.stderr)
            skipped += 1
            continue

        try:
            content = full_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # 旧監査ログ等にUTF-8非準拠バイトが混在(2026-04月分3件)。cacheの目的は
            # 検索可能な写しなので、不正バイトはU+FFFDに置換して同期し事実をログに残す。
            print(f"-- SANITIZE (undecodable bytes replaced): {file_path}", file=sys.stderr)
            content = full_path.read_text(encoding='utf-8', errors='replace')

        if not content.strip():
            print(f"-- SKIP (empty): {file_path}", file=sys.stderr)
            skipped += 1
            continue

        # NUL文字はPostgreSQLのtext型が受け付けず(22P05)、混入1件でbatch全滅の
        # 巻き添え事故を起こしていた(task f46d46a9)。除去して同期し、事実をログに残す。
        if "\x00" in content:
            print(f"-- SANITIZE (NUL bytes removed): {file_path}", file=sys.stderr)
            content = content.replace("\x00", "")

        batch.append({
            "file_path": file_path,
            "content": content,
            "line_count": content.count('\n') + 1,
            "file_size": len(content.encode('utf-8')),
            "commit_hash": commit_hash,
            "updated_at": now_iso,
        })

        if len(batch) >= BATCH_SIZE:
            ok, ng = upsert_with_isolation(batch)
            synced += ok
            errors += ng
            print(f"-- Upserted batch: {synced} files", file=sys.stderr)
            batch = []

    # 残りバッチ
    if batch:
        ok, ng = upsert_with_isolation(batch)
        synced += ok
        errors += ng

    print(f"-- Upserted: {synced}, Skipped: {skipped}, Errors: {errors}, Commit: {commit_hash}", file=sys.stderr)

    # errors>0 は非zero終了で上位(pre-push hook等)へ正直に伝える
    # (相談役seq129641 blocker1: 全滅時でもexit 0だと隠蔽が残る)
    exit_code = 1 if errors else 0

    # ===== git rm済みファイルのcache自動削除 =====
    # stale母集合は同期モードに関わらずrepo全体(collect_files)を使う。
    # sync_files(--changed-onlyでは縮小集合)を使うと未変更ファイルを大量誤削除する
    # (相談役seq129633指摘の根治)。
    stale_attempted = 0
    stale_deleted = 0
    stale_cleanup_failed = 0
    try:
        cached_paths = get_cached_paths()
        all_local_paths = set(collect_files(repo_root))
        stale = compute_stale_paths(cached_paths, all_local_paths)
        stale_attempted = len(stale)
        if stale:
            stale_deleted = delete_stale(stale)
            print(f"-- Deleted stale cache entries: {stale_deleted} ({', '.join(sorted(stale)[:5])}{'...' if len(stale) > 5 else ''})", file=sys.stderr)
        else:
            print("-- No stale cache entries found", file=sys.stderr)
    except Exception as e:
        # 握り潰さず非0で上位(pre-push hook 等)へ伝へる。attempted は算出前に落ちた場合 0 のまま。
        stale_cleanup_failed = 1
        exit_code = 1
        print(f"-- STALE_CLEANUP_FAILED: attempted={stale_attempted} deleted={stale_deleted} "
              f"not_deleted={stale_attempted - stale_deleted} error={e}", file=sys.stderr)

    # 同期対象リストを追跡外 state file へ更新（参照用・追跡 file は書かぬ）
    list_path = repo_root / "tmp" / "sync_file_list.txt"
    list_path.parent.mkdir(parents=True, exist_ok=True)
    all_files = collect_files(repo_root)
    list_path.write_text("\n".join(all_files) + "\n", encoding="utf-8")
    print(f"-- Updated {list_path}: {len(all_files)} files", file=sys.stderr)

    # 最終カウント表示
    try:
        cached_final = get_cached_paths()
        print(f"-- Cache total: {len(cached_final)} files", file=sys.stderr)
    except Exception as e:
        print(f"-- WARNING: count check failed: {e}", file=sys.stderr)

    if exit_code:
        print(f"-- FAILED: {errors} file(s) not synced, stale_cleanup_failed={stale_cleanup_failed} (exit {exit_code})", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
