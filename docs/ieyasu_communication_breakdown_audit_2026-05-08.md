# 家康 報連相崩壊 retrospective audit — 2026-05-08

> 起案: 家康 (徳川家康 / ieyasu, Codex Pro)
> 命令: msg_20260508_160113_f326d523, 理事長殿 16:00/16:10 追加命令
> 関連: `docs/communication_resilience_pack_proposal_2026-05-08.md` (信長案, commit `addd03d`)
> 方式: security / bugs / types / tests / duplication / git の 6 軸 retrospective audit

## 0. 結論

今回の報連相崩壊は、単一 bug ではなく **通信 event の契約不在、観測 source の分裂、ACK/既読/報告の状態遷移未検証、そして人間の capture 観察に依存した control-plane** が同時に露呈したものでござる。

信長案は既存 cmd 群と新規 4 cmd への実装マッピングとして妥当である。一方、家康案では異視点として、まず **全通信を「message event ledger」として検証可能にし、agent の作業状態と inbox の既読状態と report YAML を同一 transaction として扱う** ことを提案する。

最優先の構造対策は以下 4 点。

1. `queue/message_events.yaml` または SQLite/Supabase table による通信 ledger 化。
2. `scripts/checks/communication_contract_check.py` による inbox / task / report / bridge の schema + transition 検証。
3. `scripts/state_reconcile.py` による MainPC / SecondPC / dashboard / tmux 実態の差分表示。
4. `scripts/codex_interruption_guard.sh` による send-keys 連発と Codex session interruption の preflight 防止。

## 1. 監査対象と一次資料

確認した一次資料:

| 領域 | 確認内容 |
|------|----------|
| 命令 | `queue/inbox/gunshi.yaml` の未読 `msg_20260508_160113_f326d523` |
| 信長案 | `docs/communication_resilience_pack_proposal_2026-05-08.md`, commit `addd03d` |
| bug 修復 | commit `2f4b960` (`scripts/inbox_write.sh`, `hakudokai_secondpc_receiver_poll.py`) |
| 本多文書 | `docs/honda_recommendations_2026-05-08.md`, `docs/honda_secondpc_inefficiency_retrospective_2026-05-08.md`, `docs/honda_validation_implementation_flow_2026-05-08.md` |
| 家康既存監査 | `queue/reports/gunshi_report.yaml` の 2026-05-08 午後 triage |

## 2. 6 軸 findings

### F1. security — `type` / `message_type` 契約崩壊が routing 誤作動を生んだ

**判定: FAIL**

commit `2f4b960` で修復済みだが、真因は field 名二重 hardcode でござる。`inbox_write.sh` 側と cross-PC receiver 側が同じ message を別 schema として扱い、type field が落ちた。これは単なる通知不備でなく、誤 routing、誤既読化、誤 escalation を誘発する security boundary 破損である。

構造的解決:

- `schemas/inbox_message.schema.json` を新設し、`id/timestamp/from/to/type/content/read/delivery_state/correlation_id` を必須化する。
- `scripts/inbox_write.sh` と receiver は schema validator を通した message だけを保存する。
- `message_type` のような alias field は migration 期間だけ許容し、validator が warning を出す。
- cross-PC bridge は unknown type を maeda fallback せず `dead_letter` に入れ、信長/家老へ短文 alert する。

### F2. bugs — ACK / 既読 / task status / report status が独立更新される

**判定: FAIL**

inbox の `read=true`、task YAML の `status=done|assigned`、report YAML の `status`、dashboard の summary がそれぞれ別工程で更新される。どれか一つが失敗すると「作業済みなのに未読」「未読ゼロなのに task assigned」「report done だが MainPC stale」のような矛盾が残る。

構造的解決:

- `message_events` ledger に `delivered -> read -> acted -> reported -> audited -> closed` の transition を記録する。
- `inbox_write.sh` は message id と correlation id を必ず発行し、task/report 側も同じ id を参照する。
- `scripts/state_reconcile.py --agent <id>` で inbox/task/report/dashboard の矛盾を exit 1 で出す。
- close 前 gate に `state_reconcile.py --strict --cmd <cmd_id>` を必須化する。

### F3. types — YAML が人間文書と機械契約を兼ねて破損しやすい

**判定: FAIL**

本多の SecondPC 調査では `maeda_report.yaml` が colon を含む非 quote 文で parse error になった。同型は ashigaru report YAML parse error として複数回出ている。YAML は人間向け長文を含めるほど壊れやすく、現状は schema も parse gate も弱い。

構造的解決:

- `queue/reports/*.yaml` は machine fields と `body_markdown` を分離する。
- 長文本文は `docs/reports/<task_id>.md` に逃がし、YAML には path と digest だけを置く。
- `scripts/checks/yaml_contract_check.py queue/inbox queue/tasks queue/reports` を新設し、全 agent の parse と required fields を一括確認する。
- `scripts/inbox_write.sh` に multi-line content を YAML literal block として安全保存する unit test を追加する。

### F4. tests — 通信路の contract test が不足し、修復後の運用問題を検出できない

**判定: FAIL**

`2f4b960` は field bug を最小修復したが、MainPC -> SecondPC -> agent wake -> report -> MainPC reconcile までの end-to-end contract test はない。inbox_watcher silent death、SH6 cap、type 欠落、read 状態戻しは単体で修復されても、連結時にまた破綻する。

構造的解決:

- `tests/integration/test_message_delivery_contract.bats` を新設する。
- fixture は MainPC inbox、SecondPC inbox、receiver、watcher、report YAML を tmpdir に作る。
- test case: valid delivery / unknown type dead_letter / watcher down / duplicate nudge dedupe / read ack / report parse error / SH6 cap。
- SKIP は FAIL とし、通信 contract test は `scripts/audit_codex.sh` 前の preflight に入れる。

### F5. duplication — routing / pane / agent alias の正が複数箇所に散っている

**判定: FAIL**

`AGENT_PANES`, `valid_secondpc`, `lib/_section18_roles.sh`, `shim/hakudokai/_section18_roles.py`, `queue/pane_registry.yaml`, CLAUDE/AGENTS の表が別々に存在する。信長案の `cmd_registry_transport_integrity_001` は妥当だが、通信崩壊の観点では pane mapping だけでなく message routing policy も同じ SSoT に含めるべきでござる。

構造的解決:

- `queue/agent_registry.yaml` を新設し、agent_id, persona, pc, inbox_path, task_path, report_path, pane_target, allowed_senders, allowed_message_types を持たせる。
- existing `queue/pane_registry.yaml` は pane 専用 mirror とし、routing は `agent_registry` から生成する。
- receiver / inbox_write / watcher は hardcode list を廃し、registry loader を共有する。
- registry 更新時は `scripts/checks/registry_transport_check.sh` で docs/generated output との差分を検出する。

### F6. git — 通信 infra hotfix が小 commit で入るが、migration と rollback が残らない

**判定: FAIL_with_concerns**

`2f4b960` の 2 行修復は緊急 hotfix として正しい。しかし communication contract は hotfix だけでは再発防止にならぬ。どの message が修復前 schema で書かれたか、どこまで既読・再配送すべきか、rollback 可能かが commit から追えない。

構造的解決:

- 通信 infra commit には `migration_note` を docs または `queue/migrations/` に残す。
- `scripts/repair_inbox_schema.py --dry-run` を用意し、旧 schema message を検出して修復案を出す。
- hotfix commit 後は `communication_contract_check.py --since <commit>` を必須化する。
- rollback は symlink/inbox 実体を壊さぬよう、backup path と realpath を report に記録する。

### F7. bugs/tests — inbox_watcher silent death と SH6 cap が「停止した事実」を伝えない

**判定: FAIL**

watcher が死ぬと、message persistence は残っても wake-up signal が消える。SH6 cap は暴走防止として必要だが、cap 到達後に「誰が止まったか」「どの未読が起こされていないか」を ledger へ出さなければ、沈黙は成功と見分けがつかぬ。

構造的解決:

- watcher は heartbeat を `queue/watchers/<agent>.yaml` に 60 秒間隔で書く。
- SH6 cap 到達は `delivery_state=paused_by_sh6` として message ledger に残す。
- `scripts/checks/watcher_delivery_lag.sh` が `unread_count > 0 and heartbeat stale` を検出する。
- alert は dedupe key `(agent, cause, first_unread_id)` で 15 分 cooldown を持たせる。

### F8. security/bugs — 信長 send-keys 連発が Codex session interruption を誘発する

**判定: FAIL_with_concerns**

send-keys は本来 infrastructure wake-up の最終手段である。短時間に複数回送ると Codex TUI の入力状態や session を壊し、未処理中の文脈が interrupt される。これは F001/F002 だけでなく、監査 lane の独立性と再現性にも影響する。

構造的解決:

- `scripts/codex_interruption_guard.sh <agent>` を新設し、対象 pane の `@agent_id`, `pane_current_command`, `@current_task`, last_nudge_at を確認する。
- 2 分以内の同一 agent への send-keys は禁止ではなく `queued_nudge` として inbox metadata に積む。
- emergency override は `queue/control_plane.yaml` の `emergency_override.expires_at` と `authorized_by` がある時だけ許す。
- 信長や watcher が直接 tmux を叩く経路は `scripts/safe_nudge.sh` に集約する。

## 3. 信長案との違い

| 観点 | 信長案 | 家康案 |
|------|--------|--------|
| 主眼 | 既起案 cmd と新規 cmd への実装 mapping | 通信 event contract と状態遷移の正規化 |
| 最小単位 | cmd / task / agent | message event / correlation id / transition |
| SecondPC | 真田・大なた・autonomy pack へ接続 | MainPC/SecondPC reconciliation を close gate 化 |
| alert | dedup/escalation cmd | watcher heartbeat + delivery_state で沈黙を可視化 |
| send-keys | safety cmd | safe_nudge への集約と emergency lease |

両案は競合せず、信長案の Stage 1-3 に家康案の contract gate を挿し込むのが最も堅い。

## 4. 家康提案 cmd

### cmd_communication_event_ledger_001

Purpose: すべての inbox message を correlation id 付き event として記録し、既読・実行・報告・監査・close の状態遷移を機械検証できるようにする。

Acceptance Criteria:

- `queue/message_events.yaml` または Supabase table が `message_id`, `correlation_id`, `from`, `to`, `type`, `delivery_state`, `task_id`, `report_ref`, `timestamps` を保持する。
- `inbox_write.sh` が event ledger に append する。
- `read=true` 化、task done、report update、audit close が同じ correlation id を参照する。
- `scripts/state_reconcile.py --strict` が矛盾を検出する。

### cmd_communication_contract_tests_001

Purpose: inbox_write / cross-PC receiver / watcher / report YAML の契約を fixture で再現し、通信路の退行を commit 前に止める。

Acceptance Criteria:

- `tests/integration/test_message_delivery_contract.bats` が 7 ケース以上を SKIP=0 で通す。
- unknown type, type field alias, dead_letter, watcher down, duplicate nudge, YAML parse error, SH6 cap を含む。
- `scripts/checks/yaml_contract_check.py` が queue YAML 全件 parse を検証する。

### cmd_safe_nudge_and_codex_guard_001

Purpose: tmux send-keys を安全 wrapper に集約し、Codex session interruption と pane 誤操作を防ぐ。

Acceptance Criteria:

- `scripts/safe_nudge.sh` が pane identity, cli type, cooldown, current_task を確認する。
- direct `tmux send-keys` 使用箇所が grep で列挙され、許可リスト以外は wrapper 化される。
- emergency override は `queue/control_plane.yaml` の lease がなければ発火しない。
- Codex pane への 2 分以内連続 nudge は queued として記録される。

## 5. 優先順位

| 優先 | 対策 | 理由 |
|---:|------|------|
| 1 | `cmd_communication_contract_tests_001` | 既存 bug の再発を最短で止める。小工数で効果が大きい。 |
| 2 | `cmd_safe_nudge_and_codex_guard_001` | Codex interrupt は監査 lane を直接壊すため、即時防御が必要。 |
| 3 | `cmd_communication_event_ledger_001` | 本丸。状態遷移を一元化し、報連相を感覚でなく検証可能にする。 |
| 4 | `cmd_registry_transport_integrity_001` への routing policy 統合 | 既起案を拡張し、hardcode drift を根絶する。 |
| 5 | `cmd_secondpc_state_reconciliation_001` close gate 化 | SecondPC 成果の帰参漏れを恒久的に防ぐ。 |

## 6. 第一報

信長へは以下を報告する。

```text
[家康→信長] 報連相崩壊 audit 完遂。6軸で8件抽出。信長案と異なり、message event ledger + communication contract tests + safe_nudge guard を中核に据える。詳細 docs/ieyasu_communication_breakdown_audit_2026-05-08.md。
```

## 7. 最終進言

報連相は「声を掛ける」だけでは治らぬ。声が届いたか、読まれたか、実行されたか、報告されたか、監査で閉じたかを、ひとつの event として追えねばならぬ。

ゆえに家康の策は、人を責めず、通信を ledger 化し、状態遷移を gate 化し、send-keys を安全 wrapper に閉じることでござる。これにより、信長・家老・前田・SecondPC・家康の誰が見ても同じ戦況図を得られる。
