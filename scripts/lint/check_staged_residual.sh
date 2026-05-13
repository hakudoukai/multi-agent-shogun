#!/usr/bin/env bash
# pre-commit hook: commit 範囲外 staged 残存 file 検査
# 設計書: docs/scope_contamination_prevention.md §3.2
#
# 目的: ashigaru の commit 時、commit 範囲外 (= 別 task / 別 ashigaru 由来) の
#       staged file が index に残存しているかを検出し、scope_contamination 事故を抑止する。
#
# 引数: pre-commit framework から渡される staged file path 列 (= 本 commit に含まれる file)
# 戻り値:
#   0 = 残存なし or graceful skip 条件成立
#   1 = 残存検出 (= commit 中止推奨)
#
# 検査原理:
#   1. 引数 = 本 commit に取込まれる予定の file 集合 (= "commit_set")
#   2. git diff --cached --name-only --diff-filter=ACMRD = index に staged 状態の file 集合 (= "staged_set")
#   3. residual_set = staged_set - commit_set (= 集合差)
#   4. residual_set が非空なら scope_contamination の risk あり → exit 1
#
# graceful skip:
#   - 引数なし (= 全 staged scan モード) では skip (= 単独実行不能)
#   - git repository 外なら skip
#
# 設計根拠: scripts/lint/check_secrets.sh + check_deliverable_tracked.sh と同 pattern、
#           blast radius 局所、既存 hook 並列追加。

set -euo pipefail

# preflight: git repo 内か
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "[check_staged_residual] not inside git work tree (= graceful skip)"
    exit 0
fi

# 引数 = 本 commit に取込む file (= pre-commit framework から付与)
commit_set=("$@")

if [ ${#commit_set[@]} -eq 0 ]; then
    echo "[check_staged_residual] no commit-target args (= graceful skip、pre-commit framework 経由でない場合)"
    exit 0
fi

# staged_set = index 上の staged file 全件
staged_set=()
while IFS= read -r f; do
    [ -n "$f" ] && staged_set+=("$f")
done < <(git diff --cached --name-only --diff-filter=ACMRD 2>/dev/null || true)

if [ ${#staged_set[@]} -eq 0 ]; then
    # 通常ありえないが念のため
    echo "[check_staged_residual] no staged files (= unexpected but safe)"
    exit 0
fi

# residual_set = staged_set - commit_set
# bash 4+ associative array 使用
declare -A commit_map
for f in "${commit_set[@]}"; do
    commit_map["$f"]=1
done

residual=()
for f in "${staged_set[@]}"; do
    if [ -z "${commit_map[$f]:-}" ]; then
        residual+=("$f")
    fi
done

if [ ${#residual[@]} -eq 0 ]; then
    echo "[check_staged_residual] OK (= commit 範囲外 staged 残存なし、scope_contamination risk なし)"
    exit 0
fi

echo "[check_staged_residual] WARN: 本 commit に含まれない staged file を検出 (= scope_contamination risk)" >&2
echo "[check_staged_residual] 検出 file 一覧:" >&2
for f in "${residual[@]}"; do
    echo "  - $f" >&2
done
echo "[check_staged_residual] 対処: \`git restore --staged <path>\` で commit 範囲外 file を unstage してから commit してください。" >&2
echo "[check_staged_residual] 参照: docs/scope_contamination_prevention.md §3.2" >&2
exit 1
