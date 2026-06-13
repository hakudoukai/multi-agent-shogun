# Incident: second_pc 将軍 bash 落ち + 再点火 env-gap retry 滞留 (2026-06-13)

```yaml
incident:
  timestamp: 2026-06-13T~10:00   # 概算 (second_pc shogun の Claude exit 時刻)
  detected_at: 2026-06-13T10:48  # Commander msg_20260613_104819 で顕在化
  detected_by: Commander / 副院長 (inbox808 堆積 + 再点火後 retry 滞留として観測)
  what_happened: |
    second_pc の将軍 pane で Claude プロセスが exit し、pane が素の bash prompt に
    落ちた (見かけ alive・agent 不在)。以後 inbox watcher の `inboxN` nudge が bash に
    当たり「inboxN: command not found」を連発、未読が 808 件まで堆積した。手動再点火
    でも bare `claude` 起動が env (doppler/ccflare) 欠落で API retry に滞留した。
  root_cause: |
    5 Why:
    1. なぜ agent が応答しない? → pane が bash で Claude が居ない。
    2. なぜ bash に落ちた? → launch wrapper (setup_shogun_standard.sh:68) が
       `... && doppler run … -- claude 2>>log` の `&&` chain で、claude が exit
       (crash/OOM/完了/API 致命/retry 枯渇) すると chain 終了→pane 既定 shell (bash)
       に戻る = 概念上の `claude; exec bash`。
    3. なぜ気付けなかった? → tmux pane は生存 (見かけ alive)。pane_current_command も
       doppler mask 等で生死判定に使えず、capture-pane 内容を見ないと分からない。
    4. なぜ inbox が 808 件堆積? → nudge (`inboxN` send-keys) が bash に当たり command
       not found になるだけで、誰も relaunch しない無人状態が継続した。
    5. なぜ再点火しても直らなかった? → bare `claude` は doppler/ccflare env を継承せず
       (env-gap)、API 認証/ルーティングが欠けて retry に滞留した。
    ∴ 最深層: 「Claude exit→bash fallback」を検知し doppler env 付きで自動再起動する
       ローカル機構が不在だった (cross-PC send-keys 依存のみ)。
  impact: |
    second_pc 将軍が長時間 無人化。inbox 808 件堆積、指揮系統が second_pc で停止。
    実害 = 稼働停止 (データ破壊なし)。
  recovery_action: |
    SSH 手動 3 手で復旧: doppler 経由起動✗ / `claude -c`✗ / `claude` fresh✓ だが
    env-gap で retry 滞留。最終的に env 付き起動で復帰。
  prevention_principle: |
    各PC ローカルに「bash-fallback / stuck-retry を capture-pane 内容で検知し、必ず
    doppler env 付き (--permission-mode auto) で relaunch する」冪等 watchdog を常駐させる。
  prevention_skill: |
    Yes — shogun-relaunch-env-guard skill + scripts/watchdogs/shogun_bash_fallback_watchdog.sh
    + 各PC systemd --user timer (60s)。再起動上限で human_required escalate。
```

## サマリ

second_pc 将軍 pane の Claude が exit→bash に落ち、見かけ alive のまま無人化。nudge が
bash に当たり inbox 808 件堆積。再点火も bare claude の env-gap で滞留。恒久策として
各PC ローカルの bash-fallback / stuck-retry watchdog を実装した。

## 発生・発見

- 発生: 2026-06-13 朝、second_pc 将軍の Claude exit (正確時刻は log 未取得、概算)。
- 発見: Commander msg_20260613_104819、inbox808 堆積・再点火 retry 滞留として顕在化。
- 追命: 副院長追命 670ffbfe(2) → task `subtask_thirdpc_shogun_bash_fallback_watchdog`。

## 事象

1. launch wrapper の `&&` chain 終端で pane が bash prompt に復帰 (Claude 不在)。
2. tmux pane 生存ゆえ「見かけ alive」。`inboxN` nudge → `inboxN: command not found` 連発。
3. 未読 808 件堆積。second_pc 指揮停止。
4. 手動再点火: doppler✗ / `claude -c`✗ / `claude` fresh✓ だが env-gap で API retry 滞留。

## 根本原因 (= 5 Why)

上記 YAML `root_cause` 参照。最深層 = 「Claude exit→bash fallback」を capture 内容で
検知し doppler env 付きで自動再起動するローカル機構の不在。

## 影響範囲

second_pc 将軍の長時間無人化、inbox 808 件堆積、指揮系統停止。データ破壊なし。

## 復旧アクション

SSH 手動 3 手 (doppler✗ / `claude -c`✗ / `claude` fresh✓) で復帰。env 付き起動が要。

## 防止策 (= 本事例から生成)

- **watchdog**: `scripts/watchdogs/shogun_bash_fallback_watchdog.sh` (各PC ローカル, oneshot 60s)
  - 検知 (A) bash-fallback = Claude TUI chrome 不在 + 「command not found」/ shell prompt (+pane_cmd=bash)。
  - 検知 (B) stuck-retry = Claude TUI chrome 在り + 「Retrying… attempt N/M」/ spinner が SBW_STUCK_MIN 分継続 (fingerprint persistence)。
  - 復旧 = @agent_id 取得 → (B) は Esc→C-c→必要なら子 PID SIGTERM で pane 解放 → **doppler env 付き relaunch (--permission-mode auto, bare claude 禁)** → kickoff directive → incident 記録。
  - 安全 = 冪等 flag (TTL) + 連続再起動上限 (cap/window, 超過で human_required escalate) + 手動停止 flag 尊重 + fire/escalate 時のみ DB INSERT (heartbeat flood 回避)。
- **per-PC thin wrapper**: `shogun_bash_fallback_{main,second,third}_watchdog.sh`
- **deploy**: `deploy_shogun_bash_fallback_watchdog.sh` (systemd --user timer 60s, second 優先)
- **DoD テスト**: `test_shogun_bash_fallback_watchdog.sh` (classification 6 + persistence 3 + idempotency 2 + cap 4 + disable 1 + 実 tmux e2e A/B 2 = 19 assertion ALL GREEN)
- **skill**: `skills/shogun-relaunch-env-guard/SKILL.md` + `scripts/checks/shogun_relaunch_env_guard.sh`

## 教訓

1. **再点火は必ず doppler env 付き** (`doppler run … -- claude --permission-mode auto`)。
   bare `claude` は env-gap で API retry に滞留する = やってはいけない。
2. **agent の生死は capture-pane 内容で判定**。`pane_current_command` は doppler mask 等で
   当てにならない (tmux pane 生存 ≠ agent 生存)。
3. **watchdog はローカル化**して cross-PC send-keys 依存を断つ。
4. 自動再起動には**必ず連続上限**を付け、超過は human_required へ escalate (2026-05-05
   SecondPC 暴走事件と同じ「無限再起動」を作らない)。

## 関連 commit

- watchdog 実装 (PDCA cycle chain、Dual Green 監査駆動):
  - `53c92f9` feat: watchdog 初版 (bash-fallback / stuck-retry 検知 + doppler relaunch)
  - `5655570` cycle2: MODE B 子プロセス停止 hardening (証跡+確定検証)
  - `de6329a` cycle3: 孫 claude-stack 再帰検出 + ancestry 確証
  - `5a84954` cycle4: relaunch invariant 検証 / fingerprint 安定化 / tmux preflight SKIP=FAIL
  - `5af5d9d` cycle5: RELAUNCH_CMD strict injection 遮断 / pane-not-freed 無限抑止 cure
  - cycle6 (本 commit): not-freed verdict の caller 配線 / tail_b64 gating / ALLOW_UNSAFE 改行拒否 / history prune / deploy unit 検証
- 関連既存: `enter_restart_common_watchdog.sh` (idle→Enter 系、本件とは別 failure mode・補完関係)
- 過去事故: [docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md](2026-05-05_secondpc_consumption_anomaly.md)
