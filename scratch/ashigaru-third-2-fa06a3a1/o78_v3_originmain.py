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
import re

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
    # ★目は此の 31 本 (一意) が正である (2026-09-08・総監督 裁 288068)★:
    #   CI (.github/workflows/sync-source-cache.yml) の目は 28 本で、下の
    #   `.cache/audit_redo/**/*.md` `.cache/audit_redo/**/*.txt` `docs/audits/**/*.log` の
    #   3 本を欠く —— 453ca4a4 命令より前の形の儘ゆゑ。CI ⊂ v3 (逆向きの差は 0 本)。
    "docs/audits/**/*.md",
    "docs/audits/**/*.txt",
    "docs/audits/**/*.log",
    "supabase/migrations/*.sql",
    "supabase/functions/**/*.ts",
    ".cache/audit_redo/**/*.md",
    ".cache/audit_redo/**/*.txt",
]

# ===== 除外パターン =====
# ★CI の目との差 (2026-09-08・総監督 裁 288068 で v3 を正とした)★:
#  ・v3 は `**/*.test.*` `**/*.spec.*` `**/test_*` を ★除かぬ★ —— cache は「動く物」ではなく
#    「読める写し」ゆゑ、試験 code も監査で読む対象として残す (CI は此の 3 本を除いて居た)。
#  ・v3 は `**/.git/**` を ★除く★ —— 入口が追跡簿 (collect_files) ゆゑ本来入らぬが、
#    glob 経路へ戻つた時の帯として残す (二重の止め)。CI には無い。
EXCLUDE_PATTERNS = [
    "**/__pycache__/**",
    "**/node_modules/**",
    "**/dist/**",
    "**/.git/**",
    "frontend/src/vite-env.d.ts",
]

# ===== 除外ディレクトリ名（高速フィルタ） =====
# ★帯 (二重の止めの外側)★: 追跡簿基準 (collect_files) が主の止めだが、
# 万一 venv 等を git add した場合にも入らぬやう名前でも止める。
# .venv/.venv-linux = python の仮想環境 (2026-07-19 の 1 走行で 15,288 行が
# `backend/**/*.py` × 作業樹 glob で表へ入つた)。.codex_audit = 監査の作業置場。
EXCLUDE_DIRS = {
    "node_modules", "__pycache__", "dist", ".git",
    ".venv", ".venv-linux", "venv", ".codex_audit",
}

# ===== UPSERT バッチサイズ =====
BATCH_SIZE = 50

# ===== 前回 sync commit の state =====
# stale 検査を全表走査 (LIMIT/OFFSET の頁繰り) から git 差分へ移すために要る。
# 一次= DB の commit_hash 列 (updated_at DESC LIMIT 1 の 1 行・idx_source_code_cache_updated
#   が効く)。runner を跨いで共有され、fresh clone でも読める。
# 二次= 追跡外の state file (下記)。DB へ触れぬ経路 (dry-run 等) と DB 不通時の控へ。
LAST_SYNC_COMMIT_FILE = "sync_last_commit.txt"

# ===== upsert の衝突 key =====
# 表定義 supabase/migrations/20260403020939_create_source_code_cache.sql:
#   file_path TEXT PRIMARY KEY —— 同 path は 1 行しか持てぬ。
# ∴ 同 file を別 commit で同期しても行は増えず content/commit_hash が上書きされる。
# on_conflict を落とすと PostgREST 側の既定解決に委ねる形になるゆゑ明示で固定する。
UPSERT_CONFLICT_KEY = "file_path"


def should_exclude(file_path: str) -> bool:
    """除外パターンに一致するか判定"""
    for pattern in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False


def list_tracked_files(repo_root: Path) -> list[str]:
    """git の追跡簿 (index) を列挙する。

    ★git を通せぬ時は例外で止まる★ —— 作業樹 glob への無言の退避を作らぬ
    (床 no-silent-failure)。退避を置くと「git が無い環境では従前どほり
    追跡外も入る」形になり、直した筈の道が黙つて戻る。
    -z ゆゑ path は生 (非 ASCII の quote 無し)・区切は NUL。
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:                     # git 実行体が無い
        raise RuntimeError(f"git を実行できぬ: {repo_root}") from exc
    except subprocess.CalledProcessError as exc:         # repo でない/壊れて居る等
        raise RuntimeError(
            f"git ls-files が失敗した (rc={exc.returncode}): "
            f"{(exc.stderr or '').strip()}"
        ) from exc
    return [rel for rel in proc.stdout.split("\0") if rel]


def collect_files(repo_root: Path) -> list[str]:
    """同期対象を収集する。★入口は git の追跡簿★ (作業樹 glob ではない)。

    v2 まで: repo_root.glob(INCLUDE_PATTERNS) —— git を一切見ぬゆゑ、追跡外の
    `backend/.venv/**/*.py` 等が `backend/**/*.py` に当たつて表へ入つた。
    v3: 追跡済 path のみを母集合とし、INCLUDE/EXCLUDE の意味は従前どほり掛ける。
    matcher は stale 側と同じ matches_include_patterns を使ひ、入口と出口で
    glob の意味を 1 本に揃へる。
    """
    files = set()
    for rel in list_tracked_files(repo_root):
        path = repo_root / rel
        if not path.is_file():                           # 追跡簿に在るが作業樹に無い
            continue
        # ★repo 内の path 部分のみ見る★: 従前は絶対 path の parts を見て居たゆゑ、
        # repo_root 自身の親 dir 名が "dist" 等だと全 file が落ちる形だつた。
        if any(part in EXCLUDE_DIRS for part in Path(rel).parts):
            continue
        if not matches_include_patterns(rel):
            continue
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
        params={"on_conflict": UPSERT_CONFLICT_KEY},
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


def _state_file(repo_root: Path) -> Path:
    return repo_root / "tmp" / LAST_SYNC_COMMIT_FILE


def read_last_sync_commit_from_state(repo_root: Path) -> str | None:
    """追跡外 state file から前回 sync commit を讀む。無ければ None。"""
    p = _state_file(repo_root)
    try:
        v = p.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    except OSError as e:
        print(f"-- STATE_READ_FAILED: {p}: {e}", file=sys.stderr)
        return None
    return v or None


def write_last_sync_commit(repo_root: Path, commit_hash: str) -> None:
    """同期後に前回 sync commit を追跡外 state file へ書く (追跡 file は書かぬ)。"""
    p = _state_file(repo_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(commit_hash + "\n", encoding="utf-8")


def get_last_sync_commit_from_db() -> str | None:
    """cache の最新行 1 件だけ讀んで前回 sync commit を得る。

    全表の LIMIT/OFFSET 頁繰り (get_cached_paths) との差: 1 request・1 row・索引
    idx_source_code_cache_updated(updated_at DESC) 上の走査で済む。
    """
    url = f"{SUPABASE_URL}/rest/v1/source_code_cache"
    resp = httpx.get(
        url, headers=_headers(),
        params={"select": "commit_hash", "order": "updated_at.desc", "limit": "1"},
        timeout=30.0,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return None
    return data[0].get("commit_hash") or None


def commit_exists(repo_root: Path, rev: str) -> bool:
    """rev が此の樹で解決できるか (shallow clone・別枝では解決できぬ)。"""
    if not rev:
        return False
    r = subprocess.run(
        ["git", "cat-file", "-e", f"{rev}^{{commit}}"],
        cwd=repo_root, capture_output=True, text=True,
    )
    return r.returncode == 0


def deleted_paths_since(repo_root: Path, prev_commit: str, head: str = "HEAD") -> set[str]:
    """prev_commit..head で消えた (D) / 改名元 (R) の path を返す純粋な git 讀取。

    D = 削除、R = 改名 (旧 path は cache から除く対象・新 path は upsert 側が入れる)。
    M/A は削除対象にしない。
    """
    r = subprocess.run(
        ["git", "diff", "--name-status", "--diff-filter=DR", f"{prev_commit}..{head}"],
        cwd=repo_root, capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git diff failed ({r.returncode}): {r.stderr.strip()[:200]}")
    out: set[str] = set()
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        code = parts[0]
        if code.startswith("D") and len(parts) >= 2:
            out.add(parts[1].replace("\\", "/"))
        elif code.startswith("R") and len(parts) >= 3:
            out.add(parts[1].replace("\\", "/"))  # 改名元
    return out


def _glob_pattern_to_regex(pattern: str) -> "re.Pattern[str]":
    """INCLUDE_PATTERNS を pathlib.Path.glob と同じ意味の正規表現へ写す。

    ★fnmatch と glob は `**` の意味が違ふ★: fnmatch.fnmatch("scripts/a.py",
    "scripts/**/*.py") は False だが Path.glob("scripts/**/*.py") は同 file を拾ふ
    (`**` は 0 個以上の階層)。collect_files は glob、compute_stale_paths は fnmatch を
    使つて居るゆゑ、直下 file (scripts/a.py 等) は cache に入るのに stale 判定では
    拾はれぬ非対称が在る。git 差分経路では glob 側の意味に揃へる。
    """
    out = ["^"]
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:[^/]+/)*")
            i += 3
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    out.append("$")
    return re.compile("".join(out))


_INCLUDE_REGEXES = None


def matches_include_patterns(rel_path: str) -> bool:
    """collect_files (Path.glob) と同じ意味で INCLUDE 対象か判定する。"""
    global _INCLUDE_REGEXES
    if _INCLUDE_REGEXES is None:
        _INCLUDE_REGEXES = [_glob_pattern_to_regex(p) for p in INCLUDE_PATTERNS]
    return any(r.match(rel_path) for r in _INCLUDE_REGEXES)


def stale_paths_from_git(repo_root: Path, prev_commit: str, all_local_paths: set[str]) -> set[str]:
    """git 差分の D/R から、cache から除くべき INCLUDE 対象 path を算出する純関数寄りの層。

    ★全表走査をせぬ★。ローカルに現存する path (再追加・別 pattern で拾へる物) は除く。
    """
    candidates = deleted_paths_since(repo_root, prev_commit)
    stale: set[str] = set()
    for cp in candidates:
        if cp in all_local_paths:
            continue
        if should_exclude(cp):
            continue
        if matches_include_patterns(cp):
            stale.add(cp)
    return stale


def get_cache_row_count() -> int | None:
    """行数だけを 1 request で得る (Prefer: count=exact・row は 0 件返す)。

    従来の「全 file_path を頁繰りして len() を取る」最終カウントの置換。
    """
    url = f"{SUPABASE_URL}/rest/v1/source_code_cache"
    headers = {**_headers(), "Prefer": "count=exact", "Range-Unit": "items", "Range": "0-0"}
    resp = httpx.get(url, headers=headers, params={"select": "file_path"}, timeout=30.0)
    resp.raise_for_status()
    cr = resp.headers.get("content-range", "")
    if "/" in cr:
        tail = cr.rsplit("/", 1)[1]
        if tail.isdigit():
            return int(tail)
    return None


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


def _rev_parse(repo_root: Path, ref: str) -> str:
    """ref を commit へ解く。解けねば空文字 (例外にせぬ ―― 呼手が「解けぬ」で分岐する)。"""
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "-q", f"{ref}^{{commit}}"],
        capture_output=True, text=True, cwd=repo_root
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _names(stdout: str) -> set[str]:
    return set(stdout.strip().split("\n")) if stdout.strip() else set()


def changed_paths_from_git(repo_root: Path) -> set[str]:
    """--changed-only の窓を出す。★既定は origin/main...HEAD (三点) の儘★。

    三点記法は「合流点から HEAD まで」を見るゆゑ、★HEAD が origin/main 其の物★
    (= main へ押した後に CI が走る形) では ★己と己の差 = 0 本★ になり、merge で
    入つた変更が 1 本も出ぬ (2026-09-08 PR#140 の Upserted 0 の因・総監督 裁 288198)。
    ★三点が 0 本 且つ origin/main と HEAD が同じ commit の時のみ★ 第一親 (HEAD^1) との
    差へ落とす。其れ以外 ―― 枝の上・三点が 1 本でも出た時・origin/main を解けぬ時 ――
    の振舞ひは ★従前どほり★ (既定不変)。
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True, text=True, cwd=repo_root
    )
    # origin/mainが取得できない場合のフォールバック (従前どほり)
    if result.returncode != 0:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, cwd=repo_root
        )
        return _names(result.stdout)
    if result.stdout.strip():
        return _names(result.stdout)
    head = _rev_parse(repo_root, "HEAD")
    base = _rev_parse(repo_root, "origin/main")
    if head and base and head == base:
        first_parent = subprocess.run(
            ["git", "diff", "--name-only", "HEAD^1", "HEAD"],
            capture_output=True, text=True, cwd=repo_root
        )
        if first_parent.returncode == 0:
            names = _names(first_parent.stdout)
            print(f"-- CHANGED_ONLY_FIRST_PARENT: three_dot=0 origin/main==HEAD "
                  f"({head[:9]}) first_parent_files={len(names)}", file=sys.stderr)
            return names
    return set()


def main():
    repo_root = Path(__file__).parent.parent  # scripts/ の親 = リポジトリルート
    commit_hash = get_commit_hash()

    dry_run = "--dry-run" in sys.argv
    changed_only = "--changed-only" in sys.argv
    full_stale_scan = "--full-stale-scan" in sys.argv  # 溜まつた古い path の一掃 (明示指定時のみ)
    # ★帯 (2026-09-08・総監督 裁 288068)★: shallow clone (CI の actions/checkout fetch-depth 2) から
    # 呼ぶと prev_commit が解けず stale が全表走査へ落ち、★他の枝にしか無い path を悉く消す★形になる。
    # 旗を渡した時のみ stale を止める。★既定は従前どほり (hook・手打ちの振舞ひは動かぬ)★。
    no_stale = "--no-stale" in sys.argv

    # Supabase接続チェック（dry-run以外）
    if not dry_run and (not SUPABASE_URL or not SUPABASE_KEY):
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_KEY が未設定", file=sys.stderr)
        print("  backend/.env を確認してください", file=sys.stderr)
        sys.exit(1)

    # 同期対象ファイル収集
    if changed_only:
        changed_files = changed_paths_from_git(repo_root)
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
    stale_source = "none"
    try:
        if no_stale:
            print("-- STALE_SKIPPED: reason=--no-stale", file=sys.stderr)
            stale_source = "skipped"
        else:
            all_local_paths = set(collect_files(repo_root))
            prev_commit = None
            prev_source = "none"
            if not full_stale_scan:
                try:
                    prev_commit = get_last_sync_commit_from_db()
                    prev_source = "db" if prev_commit else "none"
                except Exception as e:
                    print(f"-- STATE_DB_READ_FAILED: {e}", file=sys.stderr)
                if not prev_commit:
                    prev_commit = read_last_sync_commit_from_state(repo_root)
                    prev_source = "state_file" if prev_commit else prev_source
                if prev_commit and not commit_exists(repo_root, prev_commit):
                    print(f"-- STALE_FALLBACK_FULL_SCAN: reason=prev_commit_unresolvable "
                          f"prev={prev_commit} source={prev_source}", file=sys.stderr)
                    prev_commit = None
            if full_stale_scan or not prev_commit:
                if not full_stale_scan:
                    print(f"-- STALE_FALLBACK_FULL_SCAN: reason=no_prev_commit source={prev_source}",
                          file=sys.stderr)
                cached_paths = get_cached_paths()
                stale = compute_stale_paths(cached_paths, all_local_paths)
                stale_source = "full_scan"
            else:
                stale = stale_paths_from_git(repo_root, prev_commit, all_local_paths)
                stale_source = f"git_diff:{prev_source}:{prev_commit}"
            stale_attempted = len(stale)
            if stale:
                stale_deleted = delete_stale(stale)
                print(f"-- Deleted stale cache entries: {stale_deleted} (source={stale_source}) "
                      f"({', '.join(sorted(stale)[:5])}{'...' if len(stale) > 5 else ''})", file=sys.stderr)
            else:
                print(f"-- No stale cache entries found (source={stale_source})", file=sys.stderr)
    except Exception as e:
        # 握り潰さず非0で上位(pre-push hook 等)へ伝へる。attempted は算出前に落ちた場合 0 のまま。
        stale_cleanup_failed = 1
        exit_code = 1
        print(f"-- STALE_CLEANUP_FAILED: attempted={stale_attempted} deleted={stale_deleted} "
              f"not_deleted={stale_attempted - stale_deleted} source={stale_source} error={e}",
              file=sys.stderr)

    # 同期対象リストを追跡外 state file へ更新（参照用・追跡 file は書かぬ）
    list_path = repo_root / "tmp" / "sync_file_list.txt"
    list_path.parent.mkdir(parents=True, exist_ok=True)
    all_files = collect_files(repo_root)
    list_path.write_text("\n".join(all_files) + "\n", encoding="utf-8")
    print(f"-- Updated {list_path}: {len(all_files)} files", file=sys.stderr)

    # 最終カウント表示 (従来は全 file_path を頁繰りして len() を取つて居た = 2 度目の全表走査)
    try:
        total = get_cache_row_count()
        print(f"-- Cache total: {total if total is not None else 'unknown'} rows", file=sys.stderr)
    except Exception as e:
        print(f"-- COUNT_CHECK_FAILED: {e}", file=sys.stderr)

    # 次回の git 差分の起点を残す (同期が全件通つた時のみ更新)
    if exit_code == 0:
        try:
            write_last_sync_commit(repo_root, commit_hash)
            print(f"-- Recorded last sync commit: {commit_hash}", file=sys.stderr)
        except OSError as e:
            print(f"-- STATE_WRITE_FAILED: {e}", file=sys.stderr)

    if exit_code:
        print(f"-- FAILED: {errors} file(s) not synced, stale_cleanup_failed={stale_cleanup_failed} (exit {exit_code})", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
