# 2026-06-04 branch race (並行 agent + 単一 working tree 共有) — worktree 分離恒久対策案

**Incident ID**: 2026-06-04_branch_race_worktree_separation
**起票**: Commander (third_pc)
**起票契機**: 副院長裁定 bf477155 (worktree 分離を恒久対策として課題登録、着手は現 push 後)
**深刻度**: Medium (影響軽微・データ消失なし、但し ★再発済★ ゆえ根治要)
**関連 row**: ca82d378 (X1-X3 初回上申) / d18700de (X1-X3 再発上申) / bf477155 (副院長裁定)

## 事象サマリ

third_pc (= momizi-dx) 上で Commander が `/home/hakudoukai/multi-agent-shogun/` という ★単一 git working tree★ で作業中、同 working tree を共有する別 agent (karo-third 系) が並行で別 branch (`stop_hook_grep_anchor_hotfix` / `agent_health_check_grep_anchor_hotfix`) へ checkout したため、Commander の current branch が想定外に切り替わり、commit が想定外 branch へ着地した。

### 観測ケース

| 時刻 | commit | 想定 branch | 実際 branch | 結果 |
|------|--------|------------|-------------|------|
| 2026-06-04 15:25 | 8665167 (Box CCG + visual 2) | ashigaru-third-1 | **karo-third/stop_hook_grep_anchor_hotfix** | 想定外着地 (ca82d378 で上申) |
| 2026-06-04 17:00 | 517575b (CLAUDE.md DentalBI 行) | ashigaru-third-1 | **karo-third/agent_health_check_grep_anchor_hotfix** | 想定外着地 (d18700de で上申) |
| 2026-06-04 17:14 | e516617 (smoke fixture HTML) | ashigaru-third-1 | **ashigaru-third-1** ★正規 lands★ | branch ガード hold 成功 (本 commit) |

## 5 Why

1. **Why 想定外 branch に commit?** → Commander の current branch が作業中に切り替わった
2. **Why current branch が切り替わった?** → 別 agent (karo-third) が同じ working tree (`/home/hakudoukai/multi-agent-shogun/`) で `git checkout` を実行
3. **Why 単一 working tree を共有?** → 全 agent (Commander, karo-third 等) が same WSL ホスト上の same dir を直接編集する設計
4. **Why same dir を直接編集する設計?** → 当初 single-agent 想定で設計、複数 agent 並行運用は後から発生
5. **Why 後追い設計に対応していない?** → ★per-agent worktree 分離の設計が未着手★ — incident 発生まで顕在化せず

## 即時ガード (副院長裁定 bf477155 verbatim、全 PC 全 agent 適用)

★commit 前に必ず `git branch --show-current` で意図 branch 確認 → 違えば checkout してから add/commit★

```bash
# 推奨 wrapper (commit 前に必ず実行)
EXPECTED_BRANCH="ashigaru-third-1/subtask_ee4d6ce4_enter_restart"
CURRENT=$(git branch --show-current)
if [ "$CURRENT" != "$EXPECTED_BRANCH" ]; then
  echo "WARN: current=$CURRENT != expected=$EXPECTED_BRANCH" >&2
  echo "  → git checkout $EXPECTED_BRANCH を先に実行せよ" >&2
  exit 1
fi
git add ... && git commit ...
```

## 恒久対策 (★worktree 分離設計★)

### 案 A: per-agent worktree (推奨)

各 agent (Commander/karo-third/main_pc shogun 等) に専用 worktree を割り当て:

```bash
# Commander 専用 worktree
git worktree add ~/multi-agent-shogun-commander ashigaru-third-1/subtask_ee4d6ce4_enter_restart
# karo-third 専用 worktree
git worktree add ~/multi-agent-shogun-karo karo-third/agent_health_check_grep_anchor_hotfix
# 各 agent は CWD として自身の worktree を使用
```

メリット:
- 完全な branch 分離 (互いの checkout が干渉しない)
- 同 git repository を共有 (objects/refs は単一、push/pull 完全互換)
- agent 識別と worktree path の 1:1 対応で透明

デメリット:
- worktree path の管理 (agent 起動時に CWD 切替を強制する必要)
- disk 使用量増加 (各 worktree が full checkout、但し objects は shared)

### 案 B: dispatcher 経由 commit (代替)

agent は直接 commit せず、Commander/dispatcher 経由で git 操作を一元化:
- 利点: branch race 完全防止
- 欠点: 全 commit が Commander 経由となり、自走性低下

### 案 C: branch lock file (軽量)

`.git/branch.lock` を agent 起動時に作成 → commit 中の checkout block:
- 利点: 最小変更
- 欠点: race condition 完全防止不可

★推奨 = 案 A (worktree 分離)★

## 着手タイミング (副院長裁定 verbatim)

「今は V5/3PC env 最優先ゆえ、worktree 分離は ★incident_log/dev_plan に課題登録のみ (着手は現 push 後)★」

→ ★本 incident_log land で課題登録完了★、実装着手は V5 PASS + 3PC env 統一実証完了後。

## 散在 branch 整理 (副院長裁定 verbatim)

```
V5      = origin/feat/ekarte-v3-handover-ab-hamakatsu-thirdpc@2c01f681 (main_pc 将軍 checkout 中)
env+box = ashigaru-third-1/subtask_ee4d6ce4_enter_restart@0e3d9d4→e516617 (Commander)
docs    = karo-third/agent_health_check_grep_anchor_hotfix@517575b (CLAUDE.md DentalBI 行のみ)
karo-3rd 旧 = karo-third/stop_hook_grep_anchor_hotfix@8665167 (Box CCG 系、既 deprecated)
```

統合: ★D レーン=理事長承認の整合 merge 時にまとめて consolidate★。今は各 branch で自走継続。

## 関連 canon / rule

- FKI-DEV-ROOT-CURE (再発ゆえ構造対処、副院長裁定 bf477155 明示)
- FKI-CANON-GUARDIAN-01 (正本守護、本 incident_log を canon-guardian 配下で land)
- DD-178 row 唯一鍵 (両軍師同一 commit 揃え)

## 月次自己点検

- 次月 (2026-07) 月初に worktree 分離案 A の実装着手判定
- 実装後の monitoring: agent 起動時 worktree 自動割当 + branch 切替監視

## 改訂責務

本 incident_log の改訂は **理事長殿の専権事項**。副院長・Commander は提案のみ可。
