# cmd_020 W11 completion trigger watcher — Background Worker Evaluation Gate Check

**Target worker**: `scripts/watch_w11_trigger.sh` + `systemd/dashboard-w11-trigger.{service,timer}`
**Proposed by**: ashigaru5 (= subtask_cmd020_w11_completion_trigger_watcher)
**Audited cycles**: naomasa cycle1〜cycle5 (= cycle5 verdict `pass_with_conditions`, `queue/reports/naomasa_cmd020_w11_trigger_preaudit_cycle5_20260513.yaml`)
**Gate doc source-of-truth**: [docs/background_worker_eval_gate.md](./background_worker_eval_gate.md)
**Decision**: `approve_with_concerns`

## 0. Purpose

W11 in_progress 2 件 (= `C-V29-W11DDA` + `C-V30-W11DDB`) の external Supabase
completion 状態遷移を SC family chain に届け、direct/post-audit chain 起動遅延を
防ぐ。`docs/background_worker_eval_gate.md` の Evaluation Gate 6 質問 + Decision
Record 13 fields + Anti-Patterns 全件自検 + Checklist 全件確認の evidence を
本ドキュメントに記録する。

## 1. Evaluation Gate — 6 質問 1-to-1 mapping

正本 (= `docs/background_worker_eval_gate.md` §Evaluation Gate) の文言を遵守し、
6 質問それぞれに pass-condition で答える。

### Q1 — What concrete failure mode does it prevent?

W11 in_progress 2 件 (= `C-V29-W11DDA` + `C-V30-W11DDB`) の external Supabase
completion event が SC family chain に届かず stale 化し、direct/post-audit chain
起動遅延が発生する failure mode を防ぐ。

- 観測 evidence: `queue/reports/naomasa_sc_audit_phase2_status_green_path_20260512.yaml`
  `w11_in_progress_2.completion_gate: monitor` + `recommended_assignment.monitor_only`
  に 2 候補が monitor 待ち状態と明示済。
- "improve reliability" / "make it automatic" / "monitor everything" の slogan には
  該当せず、観測済 monitor backlog の closure を目的とする。
- pass condition 適合: 既に Karo へ報告された "real observed failure" (= W11
  in_progress 候補 2 件の monitor 待ち) に直結。

### Q2 — Is the trigger event-based, scheduled, or continuous, and why is that cadence necessary?

- **trigger_type**: `scheduled`
- **cadence**: 10〜15 分間隔 (= `OnUnitActiveSec=600s`〜`900s`、初期は `600s`)
- **cadence_reason** (= "narrowest cadence that solves the failure mode" 適合):
    - SC 側 (= ashigaru5 pane / multi-agent repo) には **Supabase 起点の file /
      inbox / webhook event source が存在しない**。具体検証:
        - `queue/inbox/*.yaml` は agent ↔ agent のみで、Supabase external state を
          反映しない。
        - `scripts/inbox_watcher.sh` の `inotifywait` は local file change のみ検出。
        - Supabase MCP は **outbound query 専用**で、push/webhook を SC に届ける
          channel 不在 (= `queue/reports/naomasa_sc_audit_phase2_status_green_path_20260512.yaml`
          `execution_constraints.supabase_mcp_live_query` evidence)。
    - 故に "event-based is preferred when file, inbox, or webhook events exist" の
      pass condition において **event source 不在**であり、scheduled が
      narrowest cadence になる。
    - 10〜15 分間隔は audit ETA (= 10〜15 min/item) と同 order で、stale 検知遅延
      の上限を audit timeline に整合させる。1 分未満の cadence は監査開始 ETA に対し
      過密で polling-adjacent 性能悪化、1 時間以上の cadence は audit chain
      遅延を悪化させるため不採用。
    - Anti-Pattern §"Polling loop where an event exists" は **event source 不在**
      故に該当しない (= 本書 §3 Anti-Pattern 自検でも明示 reject 不該当を記録)。
- pass condition 適合: cadence justified + 狭い代替 (= event-based) を理由付きで reject。

### Q3 — What are maximum runtime, retry count, and backoff rules?

- **max_runtime_sec**: `60` (= systemd `TimeoutStartSec=60s` + script 内 `timeout 60`
  guard 想定)
- **retry_count**: `1` (= Supabase MCP query 失敗時の即時単発再試行のみ。連続再試行禁)
- **backoff**: `next timer tick` (= 単発再試行失敗後は cooldown を待たず次 timer
  起動に委譲、`OnUnitActiveSec` で natural backoff)
- **terminal failure behavior**:
    - structured record を `queue/reports/ashigaru5_subtask_cmd020_w11_completion_trigger_watcher_run_log.yaml`
      に append (= `result_code=fail` + reason 記録)。
    - `scripts/inbox_write.sh karo "watch_w11_trigger terminal failure" report_received ashigaru5`
      で karo へ通知。
    - resident process 化禁、stuck 検出時は systemd `TimeoutStartSec=60s` で強制終了。
- pass condition 適合: runtime / retry / backoff / terminal failure 4 要素を bounded
  に定義、unbounded retry 該当なし。

### Q4 — Where is the audit trail written?

- **audit_trail_path**:
    - `logs/watch_w11_trigger.log` (= stderr/stdout 構造 log、timestamp + level 付)。
    - `queue/reports/ashigaru5_subtask_cmd020_w11_completion_trigger_watcher_run_log.yaml`
      (= structured append-only YAML、`timestamp` + `result_code` + `items_detected`
      + `query_duration_ms` + `supabase_mcp_available` field)。
- prose summary only / stdout only への該当: なし。
- pass condition 適合: `queue/` + `logs/` に timestamps + result codes を持つ
  構造化 evidence を書き込む。

### Q5 — How is the worker stopped, rolled back, or disabled?

- **stop**: `systemctl --user stop dashboard-w11-trigger.timer`
- **disable**: `systemctl --user disable dashboard-w11-trigger.timer`
- **rollback (config switch)**: `systemd/dashboard-w11-trigger.timer` の
  `OnUnitActiveSec=` を `Unit=/dev/null` に置換、または unit file 削除 +
  `systemctl --user daemon-reload`。
- **feature flag**: 環境変数 `WATCH_W11_TRIGGER_DRY_RUN=1` で query 起動せず log
  のみ書き出す mode (= 安全運用用、本実装で対応)。
- pass condition 適合: documented stop / disable / config switch / feature flag
  全件 documented、`kill unknown processes` 不要。

### Q6 — What human-visible health signal proves it is working?

- **dashboard row**: `dashboard.md` の Layer F 監視層 section に `W11 trigger
  watcher` row を Karo が追加 (= 本 task 外、handoff 申し送り)。本 watcher 自身は
  Karo の集計対象として heartbeat YAML を提示する。
- **metric file**: `queue/metrics/w11_trigger_heartbeat.yaml`
    - `last_run_ts`: ISO8601 timestamp
    - `last_result`: `ok` / `no_change` / `detected` / `fail`
    - `items_detected`: integer (= W11 候補 2 件中、completed 化を検知した数)
    - `next_run_eta`: ISO8601 timestamp (= `last_run_ts + OnUnitActiveSec`)
- **log heartbeat**: `logs/watch_w11_trigger.log` の最新行 timestamp。
- **verification entry**: 検知時の `scripts/inbox_write.sh karo "..." report_received
  ashigaru5` 発信 evidence。
- pass condition 適合: dashboard row + metric file + log heartbeat + 検知時通知の
  4 観点で human-visible signal を提供。

## 2. Decision Record (13 fields full)

`docs/background_worker_eval_gate.md` §Decision Record Template の 13 fields を
すべて埋める (= 文言遵守、`approve_with_concerns` 以上必須)。

```yaml
worker_eval:
  id: watch_w11_trigger
  proposed_by: ashigaru5
  failure_mode: "W11 in_progress 2 件 (C-V29-W11DDA + C-V30-W11DDB) の external Supabase completion event が SC family chain に届かず stale 化、direct/post-audit chain 起動遅延"
  trigger_type: scheduled
  cadence_reason: "SC 側 Supabase 起点 event source (file/inbox/webhook) 不在故 event_based 不能、one-shot polled query が narrowest cadence。Anti-Pattern 'Polling loop where an event exists' は event 不在故不該当。10-15min cadence は audit ETA と同 order で stale 上限を audit timeline に整合。"
  max_runtime_sec: 60
  retry_count: 1
  backoff: "next timer tick (= OnUnitActiveSec で natural backoff、resident retry 禁)"
  audit_trail_path: "logs/watch_w11_trigger.log + queue/reports/ashigaru5_subtask_cmd020_w11_completion_trigger_watcher_run_log.yaml"
  health_signal: "dashboard.md Layer F row (= Karo handoff) + queue/metrics/w11_trigger_heartbeat.yaml (last_run_ts + last_result + items_detected + next_run_eta) + logs/watch_w11_trigger.log 最新行"
  stop_or_disable: "systemctl --user stop dashboard-w11-trigger.timer && systemctl --user disable dashboard-w11-trigger.timer (rollback = unit file 削除 + daemon-reload, feature flag = WATCH_W11_TRIGGER_DRY_RUN=1)"
  pii_secret_policy: "Supabase service-role key 等 secret は環境変数 (= ~/.config/systemd/user/dashboard-w11-trigger.service.d/secret.conf, 0600) で注入し log/yaml/inbox payload に書き出さず、log は id (= C-V29-W11DDA / C-V30-W11DDB) + status + commit_hash の prefix 8 桁のみ記録、PII (患者 id / 個人名) は本 watcher payload に含まれない (= development_progress テーブルは patient PII を持たない)。"
  completion_gate_interaction: "検出時は scripts/inbox_write.sh karo に通知し、direct で audited_done mark しない (= 検知 → karo → naomasa post-audit chain 起動経路を維持)。canonical report evidence + shogun_verify_audit.sh --preflight は naomasa 側で実施、本 watcher は detect-and-notify only (= 'Completion by side effect' anti-pattern 抵触禁)。"
  decision: approve_with_concerns
  decision_reason: "Failure mode は real observed (= naomasa SC audit phase2 で monitor 候補 2 件明示)、scheduled cadence は event source 不在を evidence-based に根拠付け、13 fields 全件 bounded。残 concern: Supabase MCP availability は preflight (= scripts/inbox_write 経由ではなく run_log.yaml 内 supabase_mcp_available field で機械記録)、unavailable 時は terminal failure 経路で karo 通知 (= monitor readiness は主張せず)。"
```

### 13 fields 埋め状況 self-check table

| # | field | 値 | bounded? |
|---|---|---|---|
| 1 | id | `watch_w11_trigger` | ✅ |
| 2 | proposed_by | `ashigaru5` | ✅ |
| 3 | failure_mode | W11 2 件 stale 化 (= naomasa report ref) | ✅ |
| 4 | trigger_type | `scheduled` | ✅ |
| 5 | cadence_reason | event source 不在 + audit ETA 整合 | ✅ |
| 6 | max_runtime_sec | `60` | ✅ bounded |
| 7 | retry_count | `1` | ✅ bounded |
| 8 | backoff | next timer tick | ✅ bounded |
| 9 | audit_trail_path | `logs/` + `queue/reports/` 2 路 | ✅ structured |
| 10 | health_signal | dashboard row + metric YAML + log heartbeat + 通知 | ✅ observable |
| 11 | stop_or_disable | `systemctl --user` + flag + rollback procedure | ✅ documented |
| 12 | pii_secret_policy | secret は env、PII 不在 (development_progress) | ✅ documented |
| 13 | completion_gate_interaction | detect-and-notify only、direct audited_done 禁 | ✅ documented |

## 3. Anti-Patterns 自検 (= 正本 §Anti-Patterns 全件 1-to-1)

| anti-pattern | 該当判定 | evidence |
|---|---|---|
| Polling loop where an event exists | **不該当** | SC 側に Supabase 起点 file/inbox/webhook event source なし (= §1 Q2 cadence_reason で根拠記述)。`inotifywait` / hook / one-shot preflight は external Supabase 状態を捕捉できない故、scheduled cadence が narrowest。 |
| Always-on manager without ownership | **不該当** | 各 timer tick 毎 single query + 即終了 (= resident process 禁、`max_runtime_sec=60`)。owner = ashigaru5 / Karo handoff、log file (= `logs/watch_w11_trigger.log`)、stop 手順 (= §1 Q5) 全件記録。 |
| Unbounded retry | **不該当** | `retry_count=1` + `backoff=next timer tick` + `max_runtime_sec=60` で 3 軸 bounded、terminal failure 時は structured record + inbox 通知。 |
| Narrative-only trust score | **不該当** | trust scorer 機能なし。`items_detected` は Supabase row の `status` + `commit_hash` 状態を直接 reflect、narrative trust score 不在。 |
| Silent repair | **不該当** | YAML / report / memory への repair 書込なし、`detect-and-notify only` で source row を変更せず Karo へ inbox 通知のみ。 |
| Completion by side effect | **不該当** | direct `audited_done` mark 禁を明示 (= §1 Q5 feature flag + §2 completion_gate_interaction)、canonical post-audit chain (= naomasa → karo → shogun_verify_audit.sh) を維持。 |

`scripts/watcher_supervisor.sh` 等 acceptable 例との比較:
- supervisor は **既知 watcher process 起動確認 only** (= scope narrow、5s loop)。
- 本 W11 trigger は **scheduled one-shot + bounded ExecStart** (= timer 経由)。
- 両者 acceptable 範囲だが完全別 layer、重複なし。

## 4. Checklist (= 正本 §Checklist 全件)

- [x] Failure mode is named and linked to an incident, report, or acceptance criterion.
      → `queue/reports/naomasa_sc_audit_phase2_status_green_path_20260512.yaml`
- [x] Existing event source was checked before proposing a loop.
      → inbox / inotify / webhook 全件 unavailable 確認済 (= §1 Q2)。
- [x] Trigger type is declared: event-based, scheduled, continuous, or one-shot.
      → `scheduled` (= 各 tick で one-shot query)
- [x] Cadence is justified and narrower alternatives were rejected with reasons.
      → §1 Q2、event-based reject reason 明示。
- [x] Maximum runtime is defined.
      → `60s`
- [x] Retry count is defined.
      → `1`
- [x] Backoff and cooldown are defined.
      → next timer tick (= OnUnitActiveSec 600〜900s)
- [x] Terminal failure writes a structured record.
      → run_log.yaml + karo inbox notify
- [x] Audit trail path is named.
      → `logs/watch_w11_trigger.log` + `queue/reports/.../run_log.yaml`
- [x] Health signal is visible to Karo or Shogun without reading raw process output.
      → metric YAML + dashboard handoff
- [x] Stop, rollback, or disable procedure is documented.
      → `systemctl --user stop/disable` + dry-run flag
- [x] Secrets and PII are not written to logs or cross-PC payloads.
      → secret は env、PII 不在 (development_progress は患者 PII を持たない)
- [x] The worker cannot mark completion without canonical report evidence.
      → detect-and-notify only、direct audited_done 禁
- [x] The design preserves event-driven inbox flow and does not create a polling-first path.
      → inbox / inotify は本 watcher と独立に維持、本 watcher は external Supabase 状態の補助 stream

## 5. completion_gate_interaction — 詳細記述

正本 §"Completion by side effect" anti-pattern を回避するため、本 watcher は
**detect-and-notify only** に責務を限定する。具体:

1. `scripts/watch_w11_trigger.sh` は Supabase MCP query で W11 2 候補の `status` +
   `commit_hash` を取得する。
2. 検出条件 (= `status='completed'` AND `commit_hash != ''`) を満たした row が
   あった場合、以下を実施:
    - `queue/reports/ashigaru5_subtask_cmd020_w11_completion_trigger_watcher_run_log.yaml`
      に `detected` イベントを append (= timestamp + 候補 id + commit_hash 8 桁
      prefix + items_detected count)。
    - `queue/metrics/w11_trigger_heartbeat.yaml` を上書き更新 (= last_run_ts +
      last_result=detected + items_detected)。
    - `scripts/inbox_write.sh karo "W11 completion candidate detected: <id list>"
      report_received ashigaru5` で Karo に通知。
3. **以下の操作は禁止** (= machine guard + 静的 test で常時検証):
    - `audited_done` / `shogun_verified` の status 直接書込。
    - `queue/reports/shogun_verification_log.yaml` の rewrite。
    - `dashboard.md` の row 直接編集 (= Karo が dashboard 書込 owner)。
4. Karo は通知受領後、naomasa に post-audit task を assign し、naomasa が
   canonical evidence (= report YAML + shogun_verify_audit.sh --preflight) で
   audited_done 判定を行う chain を維持する。

## 6. Concerns (= `approve_with_concerns` の根拠)

cycle5 naomasa pre-audit でも明示された 3 件の medium-severity concern を retain:

1. **scheduled は polling-adjacent**: event source 不在ゆえ scheduled は最善だが、
   将来 Supabase webhook / pg_notify SC bridge が装備された場合は event-based
   に置換する申し送り (= future TODO、本 doc §7 参照)。
2. **static test 名指し**: §1 Q1〜Q6 evidence を機械 verify する
   `scripts/test/test_subtask_cmd020_w11_completion_trigger_watcher_static_contract.py`
   を本 task で同時配備し、test 名指し concern を解消する。
3. **Supabase MCP 可用性**: 本 watcher 起動時に MCP 接続 preflight を実施し、
   unavailable 時は run_log.yaml に `supabase_mcp_available: false` を記録、
   `last_result=fail` + karo inbox notify、`detected` event は発火しない (=
   "monitor readiness" を主張しない)。

## 7. Future TODO (= 申し送り、本 task scope 外)

- T-W11-1: Supabase webhook / `pg_notify` を SC bridge 経由で受信する event-based
  代替が装備された場合、本 watcher は event_based watcher に置換する。
- T-W11-2: `dashboard.md` Layer F 監視層に `watch_w11_trigger heartbeat` row を
  追加する (= Karo owner)。
- T-W11-3: W11 完遂後、本 watcher は 2 候補が `audited_done` に遷移した時点で
  `systemctl --user disable dashboard-w11-trigger.timer` する自然停止申し送り。

## 8. References

- Source-of-truth: `docs/background_worker_eval_gate.md`
- Failure mode evidence: `queue/reports/naomasa_sc_audit_phase2_status_green_path_20260512.yaml`
- Pre-audit cycle5: `queue/reports/naomasa_cmd020_w11_trigger_preaudit_cycle5_20260513.yaml`
- Task YAML: `queue/tasks/subtask_cmd020_w11_completion_trigger_watcher.yaml`
- Inventory: `queue/reports/ashigaru5_subtask_cmd020_w11_completion_trigger_watcher_inventory.yaml`
- Implementation: `scripts/watch_w11_trigger.sh`
- systemd unit: `systemd/dashboard-w11-trigger.service` + `systemd/dashboard-w11-trigger.timer`
- Static contract test: `scripts/test/test_subtask_cmd020_w11_completion_trigger_watcher_static_contract.py`
