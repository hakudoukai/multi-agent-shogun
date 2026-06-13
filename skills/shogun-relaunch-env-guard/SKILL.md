---
name: shogun-relaunch-env-guard
description: shogun/agent 再起動は doppler env 付き起動・生死は capture-pane 判定。bare claude の env-gap 滞留を防止
---

# Shogun Relaunch Env Guard

## いつ使う (= mandatory)

- shogun / agent の Claude が落ちた・詰まった (bash prompt に落ちている、`inboxN:
  command not found` 連発、`Retrying… attempt N/M` 継続) のを検知し **再起動する直前**。
- 手動 SSH で将軍 pane を再点火する時。
- 新しい relaunch / watchdog / 再点火スクリプトを書く時 (レビュー観点)。

## 使わない

- agent が正常稼働中 (capture-pane に Claude TUI chrome = `esc to interrupt` /
  `❯` / `bypass permissions` が見え、進捗している) → 触るな。誤検知 relaunch は
  稼働中 agent を殺す。
- `pane_current_command` だけ見て「bash だから死んでる」と即断する用途 (doppler mask
  で healthy が doppler/node に化ける。生死は **capture-pane 内容** で判定)。
- enter_restart (idle→Enter 確定) の代替 — あちらは別 failure mode。

## 必須チェック手順

1. **生死は capture-pane で判定** (`pane_current_command` を信用しない):
   ```bash
   tmux capture-pane -t shogun-<pc>:0.0 -p -S -40
   ```
   - Claude TUI chrome 在り + 進捗 → 生存。触らない。
   - chrome 不在 + `command not found`/shell prompt → bash-fallback (死)。
   - chrome 在り + `Retrying… attempt N/M`/spinner が数分不変 → stuck (詰まり)。

2. **再起動は必ず doppler env 付き** (bare claude 禁 = env-gap retry 滞留の元):
   ```bash
   # pane (bash) へ送る relaunch コマンド (例: third)
   export PATH="$HOME/.npm-global/bin:$PATH" && cd '<repo>' && \
     doppler run --project openhands --config dev -- claude --permission-mode auto
   ```
   - `claude` 単体 / `claude -c` は env を継承せず NG。
   - doppler が PATH 不在なら relaunch を諦めて人手 escalate (bare claude で誤魔化さない)。

3. **自動化するなら watchdog を使う** (手動 send-keys 連打しない):
   ```bash
   bash scripts/watchdogs/deploy_shogun_bash_fallback_watchdog.sh [main|second|third] install
   ```
   - 冪等 flag + 連続再起動上限 (超過で human_required escalate) + 手動停止 flag 尊重。
   - 停止: `systemctl --user stop shogun_bash_fallback.timer` または
     `touch ~/.local/share/shogun_bash_fallback_shogun_<pc>/DISABLE`。

4. **静的監査** (新規 relaunch script のレビュー時):
   ```bash
   bash scripts/checks/shogun_relaunch_env_guard.sh
   ```
   send-keys で bare claude を起動している箇所 (env-gap リスク) を advisory 検出。

## 過去事例

- 2026-06-13 — second_pc 将軍 bash 落ち + 再点火 env-gap retry 滞留
  詳細: docs/incident_logs/2026-06-13_second_pc_shogun_bash_fallback.md
  教訓: 再点火は必ず doppler env 付き / 生死は capture-pane で判定 / watchdog はローカル化。
- 2026-05-05 — SecondPC 暴走 (無限再起動)
  詳細: docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md
  教訓: 自動再起動には必ず連続上限を付け、超過は escalate。
