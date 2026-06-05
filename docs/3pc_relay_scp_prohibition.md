# 3PC Relay scp 廃止運用ルール (cmd_016 Stage 1 Step 5)

## 制定

- 制定日: 2026-06-05 (cmd_016 Stage 1 完遂時)
- 制定根拠: 副院長令 c04130e4-36ea-4d45-bed7-7892f023ddf9 (P0 全PC並行稼働令)
- Commander dispatch: 822e0392-3a1a-472e-abd8-798beb0080ed
- 規範 layer: CANON-SHOGUN-COMMS-RESTORE-01 + FKI-DEV-ROOT-CURE-FIRST + FKI-SELF-FAULT 整合
- 既完遂 ref: commit `ad4f1dd` (Shogun Main, 2026-06-04T10:38:07+09:00) — `scripts/watchdogs/enter_restart_common_watchdog.sh` git 追跡化
- 機械 evidence: SHA256 `576cb6fddcb78a647bdf730fc0bc45b0789f4e8a288b7563393160f61dbaa73a` (= MC commit ↔ SC pull 完全一致 retain)

## 真因 (root cause)

5/30 観測の同型 drift 真因:

1. 3PC relay 修正を SC pane へ `scp` 直上書きで配布
2. 配布先 path (例: `scripts/watchdogs/enter_restart_common_watchdog.sh`) が **`.gitignore` の `scripts/watchdogs/` 包括除外配下** に位置
3. SC 側で untracked のまま稼働 → 後続の `git pull` 等で実体差し戻し / 上書きされ revert
4. MC ↔ SC 間で wrapper 内容が静かに divergent、3PC relay 信頼性 drift

要するに: **scp 直上書きは git 視界外 → 規範下の sync 機構 (= git pull) に勝てぬため必ず巻き戻る** 構造欠陥。

## 規範 (radical solution)

### 禁則

- `scripts/watchdogs/` 配下 (= 3PC relay 用 wrapper / supervisor 群) への **`scp` / `rsync` 直上書きを禁ずる**。
- 同様に、`.gitignore` で包括除外されている path に対する SC pane 直 patch も禁ずる (drift 再生産源)。

### 適用範囲 (現時点)

- `scripts/watchdogs/enter_restart_common_watchdog.sh` (= 本 cycle whitelist 例外明示済、`.gitignore:168`)
- `scripts/watchdogs/` 配下 3PC relay 関連の wrapper / supervisor 一式
- 関連 `*.service` / `*.timer` (= systemd unit、git-native 配布のみ)

新規 3PC relay 用 script を `scripts/watchdogs/` に追加する場合:

1. **`.gitignore` に whitelist 例外を明示** (= `!scripts/watchdogs/<basename>` 1 行追加)
2. `git add` → `git commit` → `git push` で MC origin/main 上に配置
3. SC は `git pull` で取得 (auto-git-sync.timer も fast-forward only ゆえ整合)

### 配布経路 (git-native のみ retain)

| layer | trigger | 動作 |
|---|---|---|
| MC 改修 | agent workflow | git add + commit + **手動 push (陛下御差配仰ぎつつ)** |
| SC 取得 | `auto-git-sync.timer` (= 5min systemd interval) | `git fetch` + fast-forward `git pull` のみ |
| 緊急 | shogun 直介入 | `git pull` 手動実行 (= ssh 経由でも git layer に限定) |

★scp / rsync の直上書きは禁則。例外を立てる場合は副院長令 + 陛下御差配の二重承認を要する。★

## 検証 (smoke 実証)

cmd_016 Stage 1 Step 4 (AC1) で実証済 — 詳細 log: [`queue/reports/cmd_016_stage1_smoke.yaml`](../queue/reports/cmd_016_stage1_smoke.yaml)

要旨:

- SC 側 `mktemp` 配下に `git clone` → `git pull` 後の SHA256 が MC commit (`ad4f1dd`) と完全一致 (`576cb6f...`)
- `git diff` / `git status` いずれも clean (= untracked / modification 無)
- → scp 廃止 + git-native 配布で **drift 構造的に排除** retain

## 規範整合

- CANON-SHOGUN-COMMS-RESTORE-01: 3PC relay 信頼性復元
- FKI-DEV-ROOT-CURE-FIRST: 対症療法禁、真因 (scp 直上書き構造) 根治
- FKI-SELF-FAULT: 「対症療法に逃げず根治したか」自問
- F007 (commit + push は agent workflow 規範下手動): 本書 commit も同規範下 (= 副院長令 trust gate 整合)
- 信頼三原則: 機械 evidence (SHA256 + git log) 主義

## 改訂責務

本書の改訂は副院長令ないし陛下御差配を要する。現場 AI は提案のみ可、独立改訂禁。
