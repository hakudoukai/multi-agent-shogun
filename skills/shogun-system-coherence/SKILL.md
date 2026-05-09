---
name: shogun-system-coherence
description: |
  multi-agent-shogun システムの settings.yaml ↔ tmux pane metadata ↔ inbox_watcher daemon process の
  三者整合性を全数検査・自動修復するスキル。
  「PANE の問題」「ご配達の問題」「相手の誤認」(= 陛下御指摘 2026-05-10) の根絶を目的とする。
  上流 yohey-w/multi-agent-shogun 自体に未装備の根本解 (= H-3 残課題、Issue #110)、本 fork で確立し将来上流貢献候補。
  「coherence」「pane mismatch」「watcher 不整合」「daemon drift」「環境整備」「再起動」「再 deploy」で起動。
  Do NOT use for: 個別 audit 業務 (= gunshi の領分)、新 agent deploy (= shutsujin_departure.sh 領分)。
argument-hint: "[check|auto-fix] (default: check)"
allowed-tools: Bash, Read, Edit
---

# /shogun-system-coherence — 三者整合性 検査・自動修復スキル

## North Star (= 全判断の最上位基準)

このスキルの北極星は **「PANE/配送/誤認の系統的不具合を機構的に根絶」**。
- 設定変更後の daemon 再起動忘れを自動検出
- 三重 drift (= settings.yaml ↔ tmux ↔ ps) を全数照合
- 「読んだはずなのに届かない」を構造的に解消
- 上流 yohey-w/multi-agent-shogun 未対応の H-3 残課題に**本 fork で初めて解を作る**

## 背景 — 上流の構造的欠陥

**上流 yohey-w/multi-agent-shogun の現状 (= 2026-05-10 調査済)**:
- PR #11 で初期 deploy 層のみ pane-base-index 動的取得対応、ランタイム watcher/supervisor は**未対応 (owner 自身 H-3 残課題と認識)**
- Issue #110 (= @agent_id 誤認) は close されたが解決策未実装
- watcher_supervisor.sh は**ハードコード** `while sleep 5` ループ、settings.yaml 参照せず
- coherence verification 概念は code/issue/PR/docs **全て不在**
- 外部事例 (Qiita) でも同症状 — 業界共通課題

**本 fork で確立する解**:
1. 三者整合性 全数照合 (= 本 skill)
2. 不整合 自動修復 (= --auto-fix mode)
3. 設定変更時の検出機構 (= Phase 2 で daemon 再起動 hook)
4. 上流貢献 PR (= Phase 3)

## 機能

### Mode 1: `check` (default、安全確認のみ)
- settings.yaml `cli.agents` から期待 mapping を抽出
- tmux 全 pane の `@agent_id` `@agent_cli` を取得
- ps -ef から `inbox_watcher.sh` 全 process の pane mapping 抽出
- 三者照合、不整合あれば **赤字で詳細出力**
- exit 0 = 全 ✅、exit 1 = 不整合あり

### Mode 2: `--auto-fix` (= 信長 kill 権限要)
- 不整合 watcher を kill (= 信長 kill 権限行使、infra 層のみ)
- tmux pane metadata を settings.yaml と整合させる set
- watcher_supervisor を再起動 (= 正しい pane mapping の watcher 復元)
- 再 verify、再帰的に check mode 実行

## When to Use

- 陛下が「PANE の問題」「届かない」「誤認」と仰せの時
- watcher_supervisor が落ちた疑い (= ps で発見)
- agent CLI 切替後の整合性確認
- session 跨ぎ後の startup ritual (= 朝一)
- 編成変更 (= ashigaru 削除/追加、gunshi 追加 等) 直後
- daily ritual として cron 起動 (= 後述)

## 検査項目 (= 三者照合)

| 観点 | source | 観点 |
|------|--------|------|
| **A. settings.yaml** | `cli.agents.{agent}: {cli}` | source of truth (= 期待値) |
| **B. tmux pane metadata** | `@agent_id` + `@agent_cli` per pane | 実 pane が何の agent か |
| **C. inbox_watcher process** | ps から `inbox_watcher.sh {agent} {pane} {cli}` | daemon が誰宛にどこに nudge 送るか |

3 つが整合していなければ pane mismatch / 配送不達 / 相手誤認の温床。

## 自動修復 procedure

```
1. ps -ef で全 inbox_watcher 列挙
2. 各 watcher の pane / cli が settings.yaml 期待と一致するか check
3. 不一致 → kill (= 信長権限)
4. tmux pane metadata を settings.yaml に揃える set
5. watcher_supervisor.sh を再起動
   - supervisor 自体も停止していた場合は新規起動
   - supervisor が `pgrep` で既存 watcher を spare、欠落 watcher のみ spawn
6. 再 verify (= recursive)
```

## Daily ritual 推奨

```bash
# crontab -e で 1 日 3 回 (朝・昼・晩) check
0 9,13,19 * * * cd /home/user/projects/multi-agent-shogun-newbuild && \
  bash skills/shogun-system-coherence/scripts/coherence_check.sh \
  >> logs/coherence_daily.log 2>&1
```

不整合検出時は ntfy 通知も推奨:
```bash
0 9,13,19 * * * cd /home/user/projects/multi-agent-shogun-newbuild && \
  bash skills/shogun-system-coherence/scripts/coherence_check.sh \
  || bash scripts/ntfy.sh "🚨 system coherence NG"
```

## Configuration

- `config/settings.yaml` cli.agents — source of truth
- pane mapping の慣例 (= shogun:main / multiagent:0.{N})

## 信長 kill 権限との連携

本 skill の `--auto-fix` mode は **信長 kill 権限** (= MEMORY.md 「信長 起動 + kill 権限」section) を行使。
- 対象は `inbox_watcher.sh` の不整合 process のみ (= infra layer)
- agent 本体 (= Claude/Codex/Gemini CLI session) は**対象外** (= 切替は switch_cli.sh 経由)
- kill 前に必ず evidence (= ps -fp) を log に記録

## 上流貢献 (= Phase 3)

本 skill 確立後、yohey-w/multi-agent-shogun に PR 提出予定:
- Issue #110 (= @agent_id 誤認) の解として
- PR #11 (= H-3 残課題) の補完として
- watcher_supervisor.sh の dynamic settings.yaml 読込 refactor (= Phase 2)

## Memory

陛下御教示 (2026-05-10):
- 「PANE の問題やご配達の問題相手の誤認が多発」 → 本 skill で根絶
- 「最初に根本的に完全に解決」 → 三者照合 + 自動修復で達成
- 「上流コミュニティ調査徹底」 → 上流に未装備、本 fork で確立、PR で貢献

## Related

- `skills/shogun-trouble-auto-skill/` — 同種 trouble 自動 skill 化 (= 本 skill も candidate からの正式装備)
- `skills/shogun-ssh-cross-pc/` — SSH 兄弟連絡網 (= 同 cross-PC 整備)
- `scripts/watcher_supervisor.sh` — Phase 2 で動的 settings.yaml 読込に refactor 予定
- `scripts/inbox_watcher.sh` — daemon 本体
- `instructions/shogun_fukuincho_audit_personas.md` 「軍師停止管理責務」 — 同種監視責務
