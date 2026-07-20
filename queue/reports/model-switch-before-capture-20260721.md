# model切替 切替前capture成果(環境部長引継ぎ用)

- 作成: karo-main, 2026-07-21 01:46 (委員長裁定seq131804 / 将軍指示 msg_20260721_014456)
- 経緯: model切替執行命令(msg_20260721_012648)の実行中、tmux send-keys が Claude Code auto-mode classifier に拒否され停止(blocker上申 msg_20260721_012829、キー送信0件=全pane未変更)。以後の切替実行は環境部長担当。

## role×pane 一覧(POST_REBOOT_RESUME 20260712 正本マッピング準拠)

| role | pane target | 切替先(命令上) | 本capture |
|---|---|---|---|
| 将軍main | shogun-main:0.0 | claude-opus-4-8 | 済 01:27:33 |
| 家老main(当職) | multiagent-main:0.0 | 対象外(fable-5維持・変更禁) | — |
| 足軽1 | multiagent-main:0.1 | ★対象外: human-verification hold中・AI接触禁止(capture含め未接触)★ | 未実施(hold) |
| 足軽2 | multiagent-main:0.2 | claude-sonnet-5 | 済 01:45:27 |
| 足軽3 | multiagent-main:0.3 | claude-sonnet-5 | 済 01:45:27 |
| 足軽4 | multiagent-main:0.4 | claude-sonnet-5 | 済 01:45:27 |
| 足軽5 | multiagent-main:0.5 | claude-sonnet-5 | 済 01:45:27 |
| 足軽6 | multiagent-main:0.6 | claude-sonnet-5 | 済 01:45:27 |
| 足軽7 | multiagent-main:0.7 | claude-sonnet-5 | 済 01:45:27 |
| 軍師(codex) | multiagent-main:0.8 | 対象外・接触禁 | 未実施(対象外) |

## 切替前capture

### shogun-main:0.0(2026-07-21 01:27:33 実測、idle=❯プロンプト・spinner無)

```
❯
────────────────────────────────────────────
  ⏵⏵ auto mode on · 1 monitor · esc to interrupt · ctrl+t to hide tasks · ← for agents · ↓ to manage    97% context used
```

(原文capture: queue/recovery/model_switch_evidence_20260721/shogun_before_0127.txt)

### multiagent-main:0.2〜0.7(2026-07-21 01:45:27 実測、各tail4行)

```
=== multiagent-main:0.2 (2026-07-21 01:45:27) ===
──────────────────────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle) · esc to interrupt · ← f…
                                           0% until auto-compact

=== multiagent-main:0.3 (2026-07-21 01:45:27) ===
──────────────────────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle) · ← for agents
                                           9% until auto-compact

=== multiagent-main:0.4 (2026-07-21 01:45:27) ===
❯
──────────────────────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle) · ← for agents

=== multiagent-main:0.5 (2026-07-21 01:45:27) ===
❯
──────────────────────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle) · ← for agents

=== multiagent-main:0.6 (2026-07-21 01:45:27) ===
❯
──────────────────────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle) · ← for agents

=== multiagent-main:0.7 (2026-07-21 01:45:27) ===
❯
──────────────────────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle) · ← for agents
```

## 所見(正直申告)

- statusline tail4行には model名表示が含まれない(model実測は各paneで/statusまたは/model照会が必要)。
- 0.2/0.3 は capture時点で ❯ プロンプト行が tail4 に写っていない(0.2=esc to interrupt表示あり=busyの可能性、0.3=auto-compact 9%)。環境部長は切替直前に各pane idle再確認を要す。
- 0.4〜0.7 は ❯ 表示=idle。
- 当職によるキー送信は本件を通じ0件。全pane model未変更のまま引継ぐ。
