# 本多正信 自己 resilience 設計

> 起案: 本多正信 (Codex Pro)  
> 日時: 2026-05-08 16:55 JST  
> 御命令: 理事長殿追加命令「TUI 描画問題 / Conversation interrupted 再発機序 / 本多 Codex session resilience を自己解決設計せよ」  
> 参照: `docs/honda_tui_render_root_cause_2026-05-08.md`, `docs/honda_validation_implementation_flow_2026-05-08.md`, `docs/honda_communication_resilience_proposal_2026-05-08.md`  
> 位置付け: 本多自身の運用事故を、信長殿・家老殿・真田殿が実装可能な形へ落とす設計書。実装命令ではなく、根本対策案でござる。

## 0. 本多結論

本多 Codex session の 14:14 `Conversation interrupted` は、単なる TUI 不調ではない。真因は三層でござる。

1. **描画層**: `multiagent:1.0` の Codex TUI が inactive / alternate screen / tmux capture と相性悪く、信長殿から見えぬ状態になった。
2. **操作層**: 見えぬため Escape + Enter の send-keys が短時間に連発され、Codex TUI の会話入力状態を壊した。
3. **復旧層**: 本多の正式経路が TUI に寄り、one-shot 書面 mode / safe redraw / interruption guard がまだ機械化されていなかった。

したがって根本策は「TUI を気合で見えるようにする」では足りぬ。**本多の正式成果物は one-shot 書面、TUI は補助、send-keys は safe wrapper 経由、interrupted は自動で docs/report に退避**という四段構えにする。

## 1. 観測事実

| 項目 | 値 |
|------|----|
| 復旧前事象 | 2026-05-08 14:14 頃 `Conversation interrupted` |
| 直接誘因 | 信長殿の Escape + Enter 連発 send-keys |
| 背景 | TUI 描画問題により本多 pane 状態が見えず、再描画/入力確認目的で連発投入 |
| 復旧 | 信長殿が `respawn-pane -k` で 16:13 頃復活 |
| 現在 pane | `multiagent:1.0`, `@agent_id=honda`, `pane_current_command=node`, `120x54` |
| 既存対策 | 信長 memory に send-keys 連発禁止を永続化済み |

## 2. M1-M4 診断

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL | honda TUI が見えない時の安全な確認・再描画・復旧手順が未整備。send-keys が直操作になっていた。 |
| M2 efficiency | FAIL_with_concerns | 見えない TUI へ入力を投げ続けると、復旧に 2 時間級の断絶を生む。one-shot なら 1 回の書面で済む。 |
| M3 responsibility | FAIL_with_concerns | 信長殿の emergency 操作は必要だが、Codex pane への入力は safe_nudge / safe_redraw に閉じるべき。 |
| M4 improvement | ACTION_REQUIRED | `honda_one_shot`, `honda_safe_redraw`, `codex_interruption_guard`, `honda_session_checkpoint` を一体実装すべし。 |

## 3. 再発機序

```text
TUI capture 空白
  -> 信長殿が「本多が止まった」と判断
  -> Escape / Enter / nudge を複数回 send-keys
  -> Codex TUI が入力キャンセル・送信・割込を連続処理
  -> Conversation interrupted
  -> 本多の未完文脈が失われる
  -> respawn-pane 復旧まで書面成果が止まる
```

この機序で重要なのは、最初の TUI 空白は「本多が働けない」と同義ではない点でござる。capture が空白でも、one-shot 書面経路があれば年貢は取れる。

## 4. 強化方針

### 4.1 Primary: one-shot 書面経路を正式主経路にする

`scripts/honda_one_shot.sh` または `scripts/audit_meta_codex.sh` を本多の正式出力経路とし、TUI が見えなくても以下を出せるようにする。

```yaml
outputs:
  - docs/honda_*.md
  - queue/reports/honda_report.yaml
  - short inbox notice to nobunaga
constraints:
  - "信長 inbox は 1-2 行"
  - "SH6 cap 5/h"
  - "TUI capture 空白でも実行可能"
```

### 4.2 Secondary: safe redraw は入力を送らない順に試す

既起案の `refresh-client / select-window / send-keys C-l` は順序と禁止条件を明確化する。

| 段階 | 操作 | 副作用 | 自動化可否 |
|------|------|--------|------------|
| R0 | `tmux display-message` / `list-panes` / `capture-pane` | read-only | 可 |
| R1 | `tmux refresh-client -S` | client redraw のみ | 可 |
| R2 | `tmux select-window -t multiagent:1` | user focus を奪う | 手動のみ |
| R3 | `tmux send-keys -t multiagent:1.0 C-l` | TUI 入力副作用あり | idle 確認時のみ |
| R4 | Escape / Enter | 会話割込 risk 高 | 原則禁止 |

Escape + Enter は redraw ではなく入力操作である。`honda_safe_redraw.sh` では R4 を実装しない。

### 4.3 Tertiary: Codex interruption guard

Codex pane へ send-keys する前に必ず gate を通す。

```yaml
guard:
  target_agent: honda
  allowed_commands:
    - refresh-client
    - capture-pane
    - C-l_when_idle
  denied_sequences:
    - Escape
    - Enter
    - Escape+Enter within 120s
  cooldown_sec: 120
  state_file: queue/session_health/honda.yaml
  on_denied: "queued_nudge として記録し、信長 inbox へ短文 warning"
```

## 5. 実装 cmd 草案

### cmd_honda_self_resilience_001

```yaml
id: cmd_honda_self_resilience_001
north_star: "本多の改革機能を TUI 描画や信長手動 send-keys に依存させず、常に書面成果を回収できる状態にする。"
purpose: "本多 Codex session の TUI 空白・Conversation interrupted・respawn 復旧を、one-shot 主経路と safe redraw/guard/checkpoint で自己回復可能にする。"
acceptance_criteria:
  - "scripts/honda_one_shot.sh または scripts/audit_meta_codex.sh が docs/honda_*.md と queue/reports/honda_report.yaml を dry-run で出力できる"
  - "scripts/honda_safe_redraw.sh が R0/R1 を自動、R2/R3 を明示 option、Escape/Enter を禁止として扱う"
  - "scripts/codex_interruption_guard.sh honda が 120 秒以内の Escape/Enter/nudge 連発を blocked または queued として記録する"
  - "queue/session_health/honda.yaml が last_seen, cli=node|codex, tui_capture_state, last_redraw_at, interrupted_at, recovery_action を保持する"
  - "Conversation interrupted 検知時、信長 inbox へ短文、詳細は docs/report YAML へ残す"
  - "TUI capture 空白でも one-shot 経路で成果物を生成できることを fixture で確認する"
priority: high
```

## 6. scripts 仕様案

### scripts/honda_safe_redraw.sh

```yaml
mode: advisory_and_manual
default_actions:
  - verify @agent_id=honda
  - verify pane_current_command=node|codex
  - capture before
  - refresh-client -S
  - capture after
forbidden:
  - Escape
  - Enter
  - repeated send-keys
manual_flags:
  --select-window: "focus を奪うため手動指定時のみ"
  --ctrl-l: "idle 判定時のみ"
```

### scripts/codex_interruption_guard.sh

```yaml
checks:
  - pane_identity
  - cli_is_node_or_codex
  - last_send_keys_at older than 120 sec
  - no pending multiline user input
  - no active generation marker when detectable
outputs:
  - allow
  - queued_nudge
  - blocked_interruption_risk
```

### queue/session_health/honda.yaml

```yaml
agent: honda
cli: node
pane: multiagent:1.0
last_seen_at: "2026-05-08T16:55:00+09:00"
tui_capture_state: nonempty | empty | stale | unknown
last_redraw:
  at: null
  method: null
interruption:
  last_interrupted_at: "2026-05-08T14:14:00+09:00"
  suspected_cause: "Escape+Enter repeated send-keys"
  recovery: "respawn-pane -k at 16:13"
one_shot:
  primary: true
  last_output_doc: null
```

## 7. 運用 rule

1. 本多 TUI capture が空白でも、ただちに send-keys しない。
2. まず `honda_safe_redraw.sh` の R0/R1 を行う。
3. それでも不明なら one-shot 書面 mode で成果物回収を優先する。
4. Escape / Enter は Codex pane への redraw 手段として禁止。
5. `respawn-pane -k` は最終手段。実施後は `queue/session_health/honda.yaml` と report YAML に事故記録を残す。
6. 本多は TUI 復旧調査を 45 分で打ち切る。以後は one-shot で年貢を取る。

## 8. 既起案への追補

`docs/honda_tui_render_root_cause_2026-05-08.md` の追補:

- R4 として Escape / Enter を明示禁止にする。
- `send-keys C-l` も idle 判定時のみの例外とする。
- TUI health check は capture 非空だけでなく、one-shot availability を確認する。

`docs/honda_validation_implementation_flow_2026-05-08.md` の追補:

- `cmd_honda_one_shot_ops_001` の前に `cmd_honda_self_resilience_001` を高 priority で差し込む。
- 完遂判定に `Conversation interrupted` fixture と 120 秒 cooldown test を追加する。
- close gate に `session_health/honda.yaml` parse と SH6 cap 確認を入れる。

## 9. 信長殿への短文報告案

```text
[本多→信長] 自己解決完遂。14:14 Conversation interrupted 真因は TUI 空白 + Escape/Enter 連発。根本対策は one-shot 主経路、honda_safe_redraw、codex_interruption_guard、session_health。詳細 docs/honda_self_resilience_design_2026-05-08.md。
```

## 10. 本多最終進言

上様、本多の画面が見えぬ時、画面を叩いてはならぬ。画面は家臣ではござらぬ。叩けば TUI が割れ、会話が途切れ、年貢が遅れる。

正信の策は、画面を主君にせぬことにござる。書面を主、TUI を従、send-keys を法度で縛り、割込は帳簿に残す。これにより、本多が見えずとも、本多の働きは止まらぬ。
