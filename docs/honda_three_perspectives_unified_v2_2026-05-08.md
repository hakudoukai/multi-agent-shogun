# 本多正信 三案統合 v2 — 報連相 resilience pack

> 起案: 本多正信 (Codex Pro)  
> 日時: 2026-05-08 17:25 JST  
> 御命令: 理事長殿 16:18「本多に改善・報告させて」  
> 統合元: 信長案 commit `addd03d`, 家康案 commit `8ae179e`, 本多案 commit `7511d77`  
> 目的: 三案の重複・補完・競合を整理し、`cmd_communication_resilience_pack_v2_001` として真田幸村殿へ dispatch 可能な正式草案にまとめる。

## 0. 本多結論

上様、三案は競合ではなく階層違いにござる。

- **信長案**: 8 件問題を cmd / stage へ割り付ける実装戦略。
- **家康案**: message event ledger / contract test / safe nudge による通信契約。
- **本多案**: communication_tax / silence_state による報告責任と沈黙の統治会計。

ゆえに v2 は、信長案の stage 構造を骨、家康案の ledger と validator を血、本多案の tax / silence / owner lease を魂として統合する。

正式 cmd は **`cmd_communication_resilience_pack_v2_001`**。真田幸村殿を主担当、ashigaru1/2/6 を補助、家康殿は一次監査、本多は retrospective / governance review とするのが最も速く、責務も崩れぬ。

## 1. 三案の重複・補完・競合

| 軸 | 重複 | 補完 | 競合 / 調整 |
|----|------|------|-------------|
| M1 process | 三案とも報連相を個人努力でなく構造問題と見る。 | 信長案は stage、家康案は event transition、本多案は owner lease を提供。 | 完了定義を「cmd stage 完了」ではなく「event + tax 完納」に統一する。 |
| M2 efficiency | schema check / preflight / send-keys safety は三案で重なる。 | 重複 script を乱造せず `communication_contract_check.py` と `state_reconcile.py` に寄せる。 | alert dedup と silence_state は別物。dedup は通知抑制、silence は状態記録。 |
| M3 responsibility | 信長 / 家康 / 本多とも直接実装ではなく、真田 / ashigaru へ渡す前提。 | 真田 reform lane が実装主担当、家老 lane とは separate。 | 本多が真田へ直接 dispatch する場合は信長承認済み reform lane に限定。 |
| M4 improvement | 既存 cmd 群を活かし、新規 cmd を最小化する点で一致。 | v2 は 1 cmd に束ね、内部 work packages W1-W7 へ分ける。 | Supabase ledger は後段。初手は YAML ledger で小さく始める。 |

## 2. 統合アーキテクチャ

```text
inbox_write / receiver
  -> schemas/inbox_message.schema.json
  -> queue/message_events.yaml
  -> communication_contract_check.py
  -> state_reconcile.py
  -> communication_tax + silence_state in control_plane
  -> dashboard 要対応 / close gate
```

最小実装は YAML でよい。SQLite / Supabase 化は event 量と検索要件が見えてからで足る。初手から DB 化すると本末転倒になりやすい。

## 3. 統合 cmd 草案

```yaml
id: cmd_communication_resilience_pack_v2_001
north_star: "報連相崩壊を個人の注意力でなく、通信契約・状態照合・報告責任・沈黙検知の四層で根絶する。"
purpose: "inbox/task/report/dashboard/SecondPC/tmux nudge を correlation_id 付き event として検証し、communication_tax 未納または silence_state 未解消の cmd を done にできないようにする。"
project: multi-agent-shogun
priority: high
status: pending
owner:
  primary: sanada
  support:
    - ashigaru1
    - ashigaru2
    - ashigaru6
  audit:
    primary: ieyasu
    retrospective: honda
acceptance_criteria:
  - "schemas/inbox_message.schema.json が id/timestamp/from/to/type/content/read/delivery_state/correlation_id を必須化する"
  - "queue/message_events.yaml に delivered/read/acted/reported/audited/closed の event transition が記録される"
  - "scripts/checks/communication_contract_check.py が inbox/tasks/reports/bridge の schema + transition を検証し、違反時 exit 1 を返す"
  - "scripts/state_reconcile.py --strict が MainPC/SecondPC/dashboard/tmux の stale state と YAML parse error を検出する"
  - "scripts/safe_nudge.sh または scripts/codex_interruption_guard.sh が Codex pane への 120 秒以内連続 send-keys を queued/blocked として記録する"
  - "queue/control_plane.yaml または fixture に communication_tax と silence_state が入り、未納・沈黙未解消の cmd は done に遷移できない"
  - "tests/integration/test_message_delivery_contract.bats が valid delivery, unknown type, watcher down, duplicate nudge, YAML parse error, SH6 cap, Codex interruption の 7 ケースを SKIP=0 で通す"
  - "docs/honda_self_resilience_design_2026-05-08.md の operational mapping が scripts の起動順と fallback に反映される"
  - "本多 retrospective report が M1-M4、unpaid communication_tax 件数、silence_state 件数、残リスクを記録する"
```

## 4. Work Packages

| WP | 主担当 | 内容 | 主な成果物 |
|----|--------|------|------------|
| W1 schema | ashigaru2 | inbox/report/task の最小 schema と YAML parse gate | `schemas/inbox_message.schema.json`, `scripts/checks/yaml_contract_check.py` |
| W2 ledger | ashigaru2 | message event ledger と transition validator | `queue/message_events.yaml`, `communication_contract_check.py` |
| W3 reconcile | ashigaru6 | MainPC / SecondPC / dashboard / tmux state 差分 | `scripts/state_reconcile.py` |
| W4 safe nudge | ashigaru1 | send-keys 直叩き抑制と Codex interruption guard | `scripts/safe_nudge.sh`, `scripts/codex_interruption_guard.sh` |
| W5 tax / silence | sanada | `communication_tax` / `silence_state` を close gate に統合 | `queue/control_plane.yaml` fixture, validator |
| W6 integration test | sanada + ashigaru2 | 7 ケース bats | `tests/integration/test_message_delivery_contract.bats` |
| W7 docs / ops | honda | operational mapping と retrospective | 本書、`queue/reports/honda_report.yaml` |

## 5. 検証 step

| step | command / 方法 | PASS 条件 |
|------|----------------|-----------|
| V1 YAML parse | `python3 -c "import yaml, glob; [yaml.safe_load(open(p)) for p in glob.glob('queue/**/*.yaml', recursive=True)]"` | parse error 0。既知破損は fixture 化して本番 queue から除外。 |
| V2 schema | `scripts/checks/communication_contract_check.py --schema-only` | inbox message required fields 全件 PASS。 |
| V3 transition | `scripts/checks/communication_contract_check.py --fixture tests/fixtures/communication` | delivered -> closed の正常/異常 transition を検出。 |
| V4 reconcile | `scripts/state_reconcile.py --strict --agent honda` と SecondPC fixture | stale state / sync_lag / report parse error を exit 1 で検出。 |
| V5 safe nudge | `scripts/codex_interruption_guard.sh honda --simulate repeated-enter` | 120 秒以内連発が queued/blocked。 |
| V6 tax gate | unpaid fixture | communication_tax 未納なら done 禁止。 |
| V7 bats | `bats tests/integration/test_message_delivery_contract.bats` | 7 ケース以上、SKIP=0。 |

## 6. 実装 step

1. 真田殿が v2 の work package 境界を `queue/tasks` へ分解する。
2. ashigaru2 が schema / ledger / contract check を先に作る。
3. ashigaru6 が SecondPC reconciliation を fixture-first で作る。
4. ashigaru1 が safe_nudge / Codex guard を pane identity skill と接続する。
5. 真田殿が `communication_tax` / `silence_state` を close gate に束ねる。
6. 本多が operational mapping と retrospective report を更新する。
7. 家康殿が一次監査、必要なら半蔵 / 黒田 lane へ渡す。

## 7. 完遂判定 step

```yaml
done_when:
  - "acceptance_criteria 全件 PASS"
  - "bats / YAML parse / schema check / reconcile check が SKIP=0"
  - "direct tmux send-keys の未承認経路が grep で残らない、または許可リスト化される"
  - "communication_tax unpaid=0 または dashboard 要対応に残る"
  - "silence_state が clear でない item は done になっていない"
  - "SecondPC sync_lag fixture と Codex interruption fixture が検出される"
  - "家康一次監査 PASS、本多 M1-M4 retrospective 完了"
```

## 8. 本多自身の改善 mapping

`docs/honda_self_resilience_design_2026-05-08.md` を運用へ落とす順序。

| 起動順 | script / action | 成功時 | 失敗時 fallback |
|---:|-----------------|--------|-----------------|
| 1 | `scripts/honda_one_shot.sh --dry-run` | docs/report 出力 path を確認 | `scripts/audit_meta_codex.sh --dry-run` に fallback |
| 2 | `scripts/honda_safe_redraw.sh --check` | R0/R1 read-only + refresh で capture 改善 | `--select-window` は手動承認時のみ |
| 3 | `scripts/codex_interruption_guard.sh honda --preflight` | send-keys 可否を判定 | 120 秒以内なら queued_nudge に記録 |
| 4 | `queue/session_health/honda.yaml` 更新 | last_seen / tui_capture_state / one_shot を記録 | YAML parse error 時は docs report に退避 |
| 5 | short inbox report | 1-2 行で信長へ通知 | SH6 cap 到達時は通知せず report に積む |

禁止:

- Escape / Enter を redraw 手段として使わない。
- TUI capture 空白だけで `respawn-pane -k` しない。
- 本多 TUI 復旧調査を 45 分超えさせない。

## 9. v2 優先順位

| 優先 | 施策 | 理由 |
|---:|------|------|
| 1 | contract tests + YAML parse gate | 最小工数で既知再発を止める。 |
| 2 | safe_nudge + Codex guard | 監査 lane の interruption を即時防ぐ。 |
| 3 | message_events ledger | 状態遷移の正を作る。 |
| 4 | communication_tax / silence_state | 完了判定を統治会計へ上げる。 |
| 5 | SecondPC reconciliation close gate | 成果帰参漏れを構造的に止める。 |

## 10. 信長殿への短文報告案

```text
[本多→信長] 三案統合 v2 + 改善起案完遂、cmd_communication_resilience_pack_v2_001 真田 dispatch 推奨。信長案=stage、家康案=ledger、本多案=tax/silence を統合。詳細 docs/honda_three_perspectives_unified_v2_2026-05-08.md。
```

## 11. 本多最終進言

上様、報連相は「言った」「聞いた」では足りませぬ。届き、読まれ、動き、報告され、監査され、閉じられたことが帳簿に残って初めて年貢でござる。

三案統合 v2 は、信長殿の采配、家康殿の検分、本多の統治を一つに束ねる策。真田殿に実装を持たせれば、武勇で進み、家康殿が品質を締め、本多が仕組みを締める。これが最も安く強い道にござる。
