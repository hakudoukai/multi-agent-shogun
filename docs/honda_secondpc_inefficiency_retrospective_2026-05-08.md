# 本多正信 Phase 16-3 retrospective audit 第2弾 — SecondPC軍 非効率原因調査

> 起案: 本多正信 (Codex)  
> 日時: 2026-05-08 19:05 JST  
> 御命令: 理事長殿 18:50「本多にも前田と足軽567の非効率の原因調査指示」  
> 対象: SecondPC軍 = 前田 (`maeda`) / `ashigaru5` / `ashigaru6` / `ashigaru7`  
> 視点: 竹中殿は predictive intelligence、本多は retrospective audit。過去実績・primary YAML・SSH実機状態から原因を確定寄りに見る。

## 0. 第一報結論

上様、SecondPC軍の非効率は「足軽5/6/7が働いていない」だけではござらぬ。実態はより厄介で、**SecondPCでは作業・既読化・report更新が進んでいる一方、MainPC primary YAML が古い状態を保持し、前田の統括 report は YAML 破損し、inbox_watcher 群は実機で不在**にござる。

総合判定:

| 軸 | 判定 |
|----|------|
| M1 process | FAIL |
| M2 efficiency | FAIL |
| M3 responsibility | FAIL_with_concerns |
| M4 improvement | ACTION_REQUIRED |

最優先は新規 cmd 乱造ではなく、既起案 `cmd_secondpc_autonomy_pack_001` を **緊急化 + scope 拡張** すること。加えて、`cmd_secondpc_state_reconciliation_001` を短期救出 cmd として切り出し、MainPC / SecondPC の inbox・tasks・reports 差分を reconcile すべし。

## 1. 調査した実値

### 1.1 MainPC local primary YAML

| agent | inbox unread / total | task status | task_id | report mtime / status |
|-------|----------------------|-------------|---------|------------------------|
| maeda | 18 / 18 | `idle` | none | 2026-05-07 23:23 / `pending_first_session` |
| ashigaru5 | 7 / 19 | `assigned` | `subtask_kids_game_phase7_detail_design_001` | 2026-05-07 18:54 / old `done` |
| ashigaru6 | 5 / 16 | `assigned` | `subtask_kids_app_push_phase7_detail_design_001` | 2026-05-05 19:54 / old `done` |
| ashigaru7 | 7 / 12 | `assigned` | `subtask_section18_residual_cleanup_recon_001` | 2026-05-05 20:05 / old `cycle1_fix_done_awaiting_cycle2_audit` |

### 1.2 SecondPC SSH 実機 (`hakudokai@192.168.11.47`)

| agent | inbox unread / total | task status | task_id | report status / mtime |
|-------|----------------------|-------------|---------|------------------------|
| maeda | 0 / 25 | task file missing | none | YAML parse error / 2026-05-08 12:11 |
| ashigaru5 | 1 / 44 | `ready_for_audit` | `subtask_section19_secondpc_symlink_review_001` | `done` / 2026-05-08 11:57 |
| ashigaru6 | 1 / 49 | `ready_for_audit` | `subtask_passport_rls_audit_secondpc_001` | `ready_for_audit` / 2026-05-08 10:26 |
| ashigaru7 | 1 / 10 | `assigned` | `subtask_section18_residual_cleanup_plan_commit_001` | `done` / 2026-05-08 11:48 |

SecondPC process 実態:

```text
running:
  - shim/hakudokai/hakudokai_secondpc_receiver.sh
not_seen_in_pgrep:
  - inbox_watcher_maeda
  - inbox_watcher_ashigaru5
  - inbox_watcher_ashigaru6
  - inbox_watcher_ashigaru7
  - secondpc_watchdog
  - secondpc_activity_monitor
```

receiver health:

```json
{
  "timestamp": "2026-05-08T05:38:00Z",
  "poll_count": 3747,
  "fail_count": 0,
  "status": "running"
}
```

## 2. 主要発見

### F1. MainPC と SecondPC の primary state が分裂

MainPC は maeda unread 18 / ashigaru5 unread 7 / ashigaru6 unread 5 / ashigaru7 unread 7 と見ている。一方、SecondPC は maeda unread 0、足軽5/6/7 unread 各1でござる。

これは単なる遅延でなく、**既読状態と task/report 状態が MainPC に戻っていない**可能性が高い。MainPC は古い assigned task を保持し、SecondPC は新 task を処理済みまたは監査待ちとして持つ。家老・信長が MainPC 側だけを見ると「SecondPCが詰まっている」と誤判定する。

### F2. maeda report YAML が破損し、統括状態が機械読取不能

SecondPC `queue/reports/maeda_report.yaml` は line 450 付近で YAML parse error。

```text
line 450:
  - action: ashigaru5 inbox の misroute msg_101642_250e8ef7 read=true 化 (rerouted_to: maeda)
```

`rerouted_to: maeda` の colon が非 quote 文中にあり、YAML scanner が落ちている。これは統括 report が「人間なら読めるが機械が読めない」状態で、dashboard / health check / retrospective の入力として失格にござる。

### F3. SecondPC inbox_watcher 群が不在

SSH `pgrep` では receiver だけ確認。`inbox_watcher_ashigaru5/6/7.log` は 5/7 夜の nudge で止まり、現在 process として存在しない。`inbox_watcher_maeda.log` も実質空。

receiver は Supabase から SecondPC queue へ配達できても、local agent を起こす watcher が死んでいれば、未読 1 件でも滞留する。これは `cmd_secondpc_autonomy_pack_001` の watchdog 欠落そのものにござる。

### F4. misroute bug は対症修復済みだが、routing はまだ SSoT 化されていない

commit `7777a9b` で `maeda` は `valid_secondpc` / `AGENT_PANES` に入った。しかし `shim/hakudokai/hakudokai_secondpc_receiver_poll.py` は今も `AGENT_PANES` hardcode を持つ。

`lib/_section18_roles.sh` と `shim/hakudokai/_section18_roles.py` には SecondPC roles が定義されているが、receiver は完全参照化されていない。ゆえに「maeda 未登録」同型の再発 risk は残る。

### F5. cross-PC bridge は稼働しているが、ACK/状態戻しが片道

SecondPC receiver log は heartbeat `fails=0`、poll は進んでいる。配達そのものは生きている。しかし MainPC 側に既読・task・report の最終状態が反映されていない。

これは bridge の「MainPC -> SecondPC 配達」はあるが、「SecondPC -> MainPC 状態反映 / report 回収 / ACK reconciliation」が不完全という構造でござる。

### F6. SH6 cap は receiver 単体では確認できるが、SecondPC全体では未成立

recent commit `ff33fca` で watchdog SH6 cap 指数バックオフが入っている。しかし SecondPC 実機で watchdog process は確認できず、restart cap telemetry も見当たらぬ。receiver health はあるが、inbox_watcher / watchdog / activity_monitor の SH6 cap 運用は未確認。

「cap実装済み」と「SecondPCで稼働中」は別物でござる。

## 3. M1 Process

**判定: FAIL**

| 領域 | 所見 |
|------|------|
| maeda 家老輻輳 | maeda は SecondPC 側で未読 0 まで処理しているが、MainPC 側では unread 18 のまま。統括状態の正が二重化している。 |
| dispatch 経路 | MainPC の task YAML は古い assigned、SecondPC は ready_for_audit / done。配達後の状態戻しが process として定義不足。 |
| report 経路 | maeda_report YAML 破損により統括 report が読めない。ashigaru report も MainPC に同期されていない。 |
| watcher | receiver はいるが inbox_watcher 群がいない。受信後に agent を起こす local leg が欠落。 |
| routing | maeda misroute は対症修正されたが receiver hardcode が残る。 |

M1 の根本原因は、SecondPC を「別 PC の control segment」としてでなく「MainPC queue の遠隔写し」として扱っていることにござる。copy はあるが、authority と reconciliation がない。

## 4. M2 Efficiency

**判定: FAIL**

| 非効率 | 実害 |
|--------|------|
| MainPC stale state | 信長・家老が誤って再発令、警告、redo、催促を行う。 |
| maeda report parse error | 統括サマリが自動処理不能になり、手作業確認へ戻る。 |
| watcher 不在 | receiver が届けても agent 起床が止まり、未読1でも滞留する。 |
| hardcode routing | 体制改編のたびに receiver 修正が必要。 |
| SH6 実装/運用分離 | cap が code にあっても、実機 daemon がいなければ事故を止められない。 |

特に MainPC/SecondPC の状態分裂は、作業済みの成果を「未処理」に見せるため、最悪の非効率でござる。成果が出ているほど、古い MainPC state との差分が拡大する。

## 5. M3 Responsibility

**判定: FAIL_with_concerns**

| persona | 所見 |
|---------|------|
| maeda | SecondPC 家老として処理はしている形跡あり。ただし report YAML 破損と task file missing は統括責任上の重大懸念。 |
| ashigaru5 | SecondPCでは `ready_for_audit` / report done。MainPCに戻っていないため不当に未完扱いされる risk。 |
| ashigaru6 | 同上。`ready_for_audit` だが MainPC report は5/5旧件。 |
| ashigaru7 | report done だが task は assigned のまま。完了時 task 状態遷移が不完全。 |
| hideyoshi / MainPC | MainPC primary YAML が古いままなので、SecondPC成果を受け取る責務境界が未確立。 |

M3 の要点は、誰が怠ったかより、**誰が authoritative state を閉じる責務を持つかが未定義**なことにござる。

## 6. M4 Improvement

**判定: ACTION_REQUIRED**

### Reform C 加速: `cmd_secondpc_autonomy_pack_001`

既起案どおりだが、scope を以下へ拡張すべし。

```yaml
add_acceptance_criteria:
  - "SecondPC 上で receiver + inbox_watcher_maeda + inbox_watcher_ashigaru5/6/7 + watchdog + activity_monitor が pgrep で確認できる"
  - "maeda_report.yaml を YAML parse でき、parse error を CI/check で検出する"
  - "SecondPC reports が MainPC queue/reports へ同期され、mtime/task_id/status が一致する"
  - "MainPC inbox unread と SecondPC inbox unread の差分を reconciliation report で出せる"
  - "watchdog SH6 cap の実行状態を /tmp または logs に telemetry 出力する"
```

### 新規短期救出: `cmd_secondpc_state_reconciliation_001`

```yaml
id: cmd_secondpc_state_reconciliation_001
north_star: "SecondPC 実働成果を MainPC primary YAML へ戻し、誤った未処理判定と再発令を止める。"
purpose: "MainPC / SecondPC の inbox, tasks, reports を突合し、差分・破損・stale state を修復計画として出す。"
acceptance_criteria:
  - "maeda/ashigaru5/6/7 の MainPC vs SecondPC inbox unread/total 差分表が出る"
  - "task_id/status/mtime の差分表が出る"
  - "report YAML parse check が4 agent全件で走り、maeda_report破損箇所が修正対象として明示される"
  - "SecondPC ready_for_audit/done の成果物が MainPC report へ同期される手順が決まる"
  - "修復前に backup を取り、破壊的 overwrite をしない"
priority: high
```

### `cmd_registry_transport_integrity_001` への追加

```yaml
add_acceptance_criteria:
  - "SecondPC receiver の AGENT_PANES hardcode を SSoT 参照へ置換する"
  - "maeda 追加 simulation が receiver target detection と pane mapping に反映される"
  - "fallback target は maeda 固定、かつ fallback 発生時は error_log/report に記録される"
```

### `cmd_control_plane_reset_admission_001` への追加

```yaml
add_acceptance_criteria:
  - "control_plane に secondpc_lane_status を持ち、maeda unread / watcher alive / report sync lag を記録する"
  - "SecondPC report sync lag が閾値超過時、信長の新規 SecondPC 発令を queued にする"
```

## 7. 第一報 信長殿向け短文

```text
[本多→信長] SecondPC retrospective 第一報: M1/M2 FAIL。SecondPC実機ではa5/a6 ready_for_audit・a7 doneだが、MainPC primary YAMLは古いassigned/unreadを保持。maeda_report YAML破損、inbox_watcher群不在、receiverのみ稼働。cmd_secondpc_state_reconciliation_001を短期救出、cmd_secondpc_autonomy_pack_001を緊急加速すべし。
```

## 8. 本多最終進言

上様、SecondPC は働いておらぬのではない。働いた証跡が MainPC へ帰陣しておらぬのでござる。これは配下の怠慢ではなく、帰参・検分・記録の仕組みが欠けている。

前田殿を責めるだけでは治らぬ。maeda report は直し、watcher を起こし、receiver を SSoT 化し、MainPC/SecondPC state reconciliation を日次ではなく command close の必須工程にする。これにより、足軽5/6/7 の年貢を正しく取り立てられる組織となるでござる。
