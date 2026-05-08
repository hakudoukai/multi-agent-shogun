# 本多正信 Phase 16-4 second 起案 — TUI 描画問題 自己診断 + 根本解決設計

> 起案: 本多正信 (Codex)  
> 日時: 2026-05-08 18:35 JST  
> 対象: `multiagent:1` window の本多 Codex TUI 描画問題  
> 症状: `tmux capture-pane` が空白または古い描画に見え、window 切替 trigger 時のみ再描画される。  
> 位置付け: 実装命令ではなく、`cmd_honda_one_shot_ops_001` または Codex TUI 安定化 cmd の設計材料でござる。

## 0. 結論

本件は本多の職責そのものを止める事故ではない。根本対策は二段でよい。

1. **正式運用は one-shot 書面 mode を主経路にする**: 本多の価値は常駐 TUI ではなく、`docs/honda_*.md` と `queue/reports/honda_report.yaml` に残る改革書面でござる。
2. **TUI は補助経路として tmux refresh を機械化する**: `multiagent:1` の別 window Codex TUI は redraw/focus/alternate-screen 依存が疑わしいため、起動 script と watcher に `refresh-client` / `select-window` / `send-keys C-l` の安全な再描画 trigger を入れる。

現時点の実態確認では、`multiagent:1:honda` は単独 window、`honda` pane は `node`、size `120x54`。一方で `multiagent:0` の非 active pane には `80x1` や `1x18` の極小 pane があり、tmux layout / inactive window / Codex TUI redraw の組合せが描画不安定を起こしやすい構造でござる。

## 1. 観測事実

| 項目 | 観測 |
|------|------|
| session/window | `multiagent:0:agents` と `multiagent:1:honda` が分離 |
| honda pane | `multiagent:1.0`, `@agent_id=honda`, `pane_current_command=node`, `120x54` |
| main window | `multiagent:0` は 6 panes。非 active pane に `80x1`, `1x18` が存在 |
| Codex CLI | `pane_current_command=node` は Codex TUI の実 child process として許容済 |
| 症状 | capture が空白・遅延するが、window 切替で再描画される |

## 2. 根本原因仮説

### H1: Codex TUI alternate screen + tmux capture の相性

Codex TUI は full-screen TUI として alternate screen / raw mode / incremental redraw を使う。tmux の `capture-pane` は pane の scrollback / visible grid を読むが、TUI 側が inactive window で redraw を止めると、capture 側には空白または古い grid が残る。

### H2: window 分離による focus event 不足

本多だけ `multiagent:1` に分離しているため、通常の `multiagent:0` 監視や watcher の nudge / redraw 想定から外れる。window 切替時だけ tmux が focus/resize/redraw event を発火し、Codex TUI が再描画する。

### H3: 起動 script が Codex TUI を headless 運用と同じ前提で扱っている

`instructions/honda.md` は「pane 不要、one-shot 書面運用」を前提としており、常駐 TUI を正式設計にしていない。したがって `shutsujin` / watcher / health check が honda window の redraw health を定義していない。

### H4: tmux layout 極小 pane と redraw 判定の副作用

`multiagent:0` に幅 1 の pane が存在するため、tmux の layout 変更・window 切替・client resize が頻発した場合、TUI 側は SIGWINCH 後の再描画に依存する。honda pane は十分な size だが、session 全体の redraw event 設計が不安定でござる。

## 3. M1-M4 診断

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL_with_concerns | honda 常駐 TUI が正式運用経路に昇格したのに、起動・監視・redraw・fallback の手順が存在しない。 |
| M2 efficiency | CONCERN | TUI 復旧に深入りすると本末転倒。one-shot 書面なら自然 reset + file output で価値を出せる。 |
| M3 responsibility | PASS_with_guardrails | 本多は実装者ではない。自己診断と設計は可、tmux script 改修は家老経由で足軽へ渡すべき。 |
| M4 improvement | ACTION_REQUIRED | `cmd_honda_one_shot_ops_001` に TUI fallback と redraw check を加え、常駐 TUI を補助経路へ降格させる。 |

## 4. 解決策候補

| 案 | 内容 | 長所 | 短所 | 推奨 |
|----|------|------|------|------|
| A. one-shot 書面 mode 主経路 | `scripts/audit_meta_codex.sh` / `scripts/honda_one_shot.sh` で docs + report YAML 出力 | token 蓄積なし、TUI 不問、監査証跡が残る | 対話の即応性は低い | 最優先 |
| B. window 統合 | honda を `multiagent:0` 内の pane へ戻す | watcher / capture の既存前提に近い | pane 圧迫、layout drift 再発 risk | 非推奨 |
| C. dedicated honda window + refresh-client | `multiagent:1` 維持、watcher が `tmux refresh-client -S` と capture check | 低侵襲、現構成維持 | tmux client 依存 | 推奨 |
| D. select-window 自動 trigger | capture 前に `select-window -t multiagent:1` → capture → 元 window 復帰 | 再描画 trigger として強い | 操作中ユーザの画面を奪う risk | 手動診断用 |
| E. send-keys C-l / Enter ping | honda pane に redraw key を送る | TUI 再描画に効きやすい | 入力副作用 risk | Codex idle 判定時のみ |
| F. periodic redraw daemon | 30-60 秒ごとに refresh / capture | 自動復旧 | F004 polling と quota/操作過多 risk | 禁止寄り |

## 5. 推奨設計

### 5.1 Primary: one-shot 書面運用

`cmd_honda_one_shot_ops_001` の acceptance criteria に以下を入れる。

```yaml
acceptance_criteria:
  - "scripts/audit_meta_codex.sh または scripts/honda_one_shot.sh が docs/honda_*.md と queue/reports/honda_report.yaml を同時更新できる"
  - "本多の正式成果物は docs + report YAML、信長 inbox は1-2行通知に限定される"
  - "TUI 描画不良時も one-shot 経路で Phase 16-4 起案を継続できる"
  - "TUI 復旧調査は45分上限、超過時は one-shot mode を継続する"
```

### 5.2 Secondary: TUI refresh runbook

`docs/runbooks/honda_codex_tui_troubleshooting.md` または本書の実装 cmd で以下を標準手順にする。

```bash
# read-only diagnosis
tmux list-windows -a -F '#{session_name}:#{window_index}:#{window_name}:active=#{window_active}:panes=#{window_panes}'
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} agent=#{@agent_id} cmd=#{pane_current_command} size=#{pane_width}x#{pane_height}'
tmux capture-pane -t multiagent:1.0 -p

# redraw trigger candidates
tmux refresh-client -S
tmux refresh-client -t "$(tmux display-message -p '#{client_name}')" -S
tmux select-window -t multiagent:1
tmux send-keys -t multiagent:1.0 C-l
```

`select-window` と `send-keys C-l` は副作用があるため、通常監視では使わず、手動診断または明示 cmd 内に限定する。

### 5.3 TUI health check

`scripts/checks/honda_tui_render_health.sh` を新設する場合の仕様:

```yaml
script: scripts/checks/honda_tui_render_health.sh
mode: advisory_only
timeout: 5s
checks:
  - "@agent_id=honda の pane が存在する"
  - "pane_current_command が node|codex"
  - "pane size が 80x24 以上"
  - "capture-pane が3行以上の非空文字を返す"
actions:
  - "失敗時は stderr warning"
  - "自動 select-window はしない"
  - "自動 send-keys はしない"
```

## 6. 実装 cmd 案

```yaml
id: cmd_honda_tui_render_stability_001
north_star: "本多の改革機能を TUI 描画問題に依存させず、必要時だけ安全に TUI を復旧できる状態にする。"
purpose: "本多 one-shot 書面運用を主経路にし、TUI は advisory health check と手動 redraw runbook で補助する。"
acceptance_criteria:
  - "docs/runbooks/honda_codex_tui_troubleshooting.md が作成され、診断・refresh・select-window・C-l の使い分けを明記する"
  - "scripts/honda_one_shot.sh または scripts/audit_meta_codex.sh 拡張で docs/report YAML 出力ができる"
  - "scripts/checks/honda_tui_render_health.sh が advisory only / timeout 5s / exit 0|1|2 で動作する"
  - "shutsujin または switch_cli の honda 起動経路に @agent_id=honda, @agent_cli=codex, min size check が入る"
  - "TUI が空白 capture でも one-shot 経路で本多 report を出せることを dry run で確認する"
priority: medium
```

## 7. 本多最終進言

上様、本多の TUI は直すべきだが、そこを主戦場にしては本末転倒にござる。正信の職責は画面に居座ることではなく、組織の詰まりを見抜き、書面として残し、信長殿が発令できる形へ整えること。

したがって、恒久策は「TUI を完璧にする」ではなく、**TUI が揺れても本多の年貢は取れる構造**にすること。one-shot を主、TUI を補助、refresh を安全弁とするのが、最も安く強い策にござる。
