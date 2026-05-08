# 本多正信 初回組織改革提言

> 起案: 本多正信 (Codex)  
> 日付: 2026-05-08 JST  
> 対象: 本朝事故 9 件 retrospective M1-M4 監査  
> 参照: `docs/honda_recommendations_2026-05-08.md`, `AGENTS.md` commit `2141588`, `docs/cmd_root_resolution_001_draft.md`, `backend/migrations/007_organizational_lessons.sql`, `backend/migrations/008_organizational_lessons_seed.sql`  
> 位置付け: Phase 16-3 first 任務成果、Phase 16-4 組織改革 cmd 起案権限の発動準備

## 0. 本多結論

上様、本朝の 9 事故は別々の火事に見えるが、根は三つに収束する。

1. **状態の正が散っている**: pane、inbox alias、SecondPC routing、体制改編、CLI 稼働状態が、人手 markdown と hardcode と runtime に分散した。
2. **control-plane が 1 pane に過密**: 家老が dispatch、dashboard、redo、監査依頼、緊急対応、記録を抱え、reset も代行も入場制限もなかった。
3. **事故後学習はあるが、発動条件が弱い**: skill は増えたが advisory に留まり、Supabase organizational_lessons は器ができた段階で、信長/家老/本多の起案ループへまだ完全接続されていない。

ゆえに、Phase 16-4 の初手は「新 cmd を多産する」ことではない。既存 6 cmd 候補を束ね、次の順で通すべし。

| 優先 | cmd 候補 | 目的 |
|---:|----------|------|
| 1 | `cmd_control_plane_reset_admission_001` | 既存 `cmd_karo_token_reset_baton_001` + `cmd_shogun_admission_control_001` を統合。家老 reset、baton lease、信長発令制限を一体化する。 |
| 2 | `cmd_registry_transport_integrity_001` | pane registry、inbox alias、atomic write、SecondPC routing を SSoT と advisory check で縛る。 |
| 3 | `cmd_secondpc_autonomy_lane_001` | SecondPC watchdog、activity_monitor、maeda self-audit、routing SSoT を同時に完成させる。 |
| 4 | `cmd_honda_one_shot_ops_001` | 本多を TUI 非依存の書面起案役として正式運用し、改革提言を docs/report/Supabase へ残す。 |
| 5 | `cmd_karo_overload_takenaka_assist_001` | 既起案を維持。ただし竹中は補助者であり、指揮継承者ではないことを lease で縛る。 |
| 6 | `cmd_bulk_dispatch_template_001` | 最後に導入。F002 境界が難しいため、家老承認 template と emergency flag が整ってからにする。 |

## 1. Codex 能力拡張確認

`AGENTS.md` commit `2141588` で、家康と本多は「何も知らない Codex」ではなく、Git、進行中 cmd、Skill MD、Supabase organizational_lessons、事故記録を踏まえて監査する義務を負った。

本起案で確認した文脈は以下。

| 領域 | 確認内容 | 本起案への反映 |
|------|----------|----------------|
| Git | 直近 commit は `2141588`、`4dbac5b`、`c05aab0`、`7230e4e`、`7c0ece0`、`eb46e06`、`7f3e8da` 等。 | 既存起案と実装進行を壊さず、重複 cmd を避ける。 |
| Supabase | `organizational_lessons` は read 全開、write は honda/hideyoshi/shogun、DELETE は rijicho。008 seed は本朝事故 9 件の初期登録。 | Phase 16-4 では本多が docs だけでなく lessons 更新候補を出せる。 |
| Skill | `pane-identity-verify`, `codex-cli-required-persona`, `inbox-alias-integrity`, `symlink-aware-atomic-write`, `secondpc-dispatch-verify`, `lessons-to-skill` を確認。 | 新 skill 乱造でなく、既存 skill 拡張と hook 配線を優先。 |
| 本多既起案 | `docs/honda_recommendations_2026-05-08.md` の Q1-Q5 と 6 cmd 候補を再読。 | 家老 SPOF、admission、one-shot 運用を本提言の中核に据える。 |
| 制約 | SH6 5/h、本末転倒厳禁、F001/F002、§19.5 重複禁止。 | 信長 inbox は着手と完遂の短文に限定し、cmd 候補を統合する。 |

注: `~/.codex/auth.json` は存在し、account_id を確認済み。`jq` は環境に無いため、Python でローカル確認した。Supabase への外部接続は本任務では実行せず、migration と seed を一次資料として扱った。

## 2. 本朝事故 9 件 M1-M4 監査

### 2.1 split-brain

対象: `queue/inbox` の `karo.yaml` と `hideyoshi.yaml`、`gunshi.yaml` と `ieyasu.yaml` の分裂。

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL | Phase 3 rename/symlink 導入時に、`scripts/inbox_write.sh` の atomic replace が symlink を壊す契約違反を検証していなかった。 |
| M2 efficiency | FAIL | 約 37 分の通信分裂、救出 merge、alias 復旧、再検証が発生。5 秒の alias integrity check が無かった代償が大きい。 |
| M3 responsibility | FAIL_with_concerns | transport 層変更の owner が曖昧。信長が復旧したが、本来は家老/infra script の preflight で防ぐべき領域。 |
| M4 improvement | ACTION | `inbox-alias-integrity` と `symlink-aware-atomic-write` を PreToolUse/weekly check へ配線。queue/inbox alias は registry 化し、atomic write は canonical path 必須とする。 |

### 2.2 SecondPC misroute

対象: `hakudokai_secondpc_receiver_poll.py` の valid_secondpc / AGENT_PANES hardcode が maeda 追加に追従せず、commit `7777a9b` で対症修正された件。

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL | routing の正が `lib/_section18_roles.sh` / `shim/hakudokai/_section18_roles.py` / receiver hardcode に分散。体制改編が routing に自動波及しなかった。 |
| M2 efficiency | FAIL | misroute 1 件の修正が対症療法となり、同型 hardcode が残る限り次の persona 追加で再発する。 |
| M3 responsibility | FAIL_with_concerns | SecondPC lane の owner は前田だが、MainPC 家老が cross-PC routing の成否まで握る構造で境界が曖昧。 |
| M4 improvement | ACTION | `cmd_registry_transport_integrity_001` に routing SSoT 化を統合。体制改編 simulation で SSoT 1 箇所更新から receiver 反映まで検証する。 |

### 2.3 SecondPC 自律機構欠落

対象: SecondPC watchdog、activity_monitor、maeda self-audit 不足。

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL | SecondPC は MainPC subset として後付けされ、watchdog、activity_monitor、self-audit が同時導入されなかった。 |
| M2 efficiency | FAIL | idle 検知不在、watcher silent death、dispatch 漏れが別々に表面化し、同じ自律機構不足を複数の rework に分散させた。 |
| M3 responsibility | FAIL | 前田は SecondPC 家老だが、自己監査 script と lane authority が無い。責務だけ増え、観測と復旧権限が不足した。 |
| M4 improvement | ACTION | `cmd_secondpc_autonomy_lane_001` を起案候補とし、SecondPC watchdog、activity_monitor、maeda self-audit、dispatch verify を一体実装する。 |

### 2.4 pane drift

対象: 2026-05-07 pane misidentification と 2026-05-08 pane mapping drift。

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL | `CLAUDE.md`、shutsujin、watchdog、tmux runtime の mapping が乖離。runtime `@agent_id` が存在したのに判断手順が使わなかった。 |
| M2 efficiency | FAIL | 夜討ち約 6.5h の家康 nudge 不発、三者監査停滞、4 件未着手。pane 確認 1 行を省いた損失が大きい。 |
| M3 responsibility | FAIL_with_concerns | 信長自身が pane 番号推測で操作した。緊急時でも pane identity skill を bypass しない仕組みが必要。 |
| M4 improvement | ACTION | `pane-identity-verify` は単 pane check から 4-way audit へ拡張済み。Phase 16-4 では §18.1 autogen と registry lock を完遂対象にする。 |

### 2.5 F001 越権

対象: 信長または監査役が緊急対応で直接実装・直接操作に寄る構造。特に pane 復旧、alias 救出、家康代替 audit 起動など。

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL_with_concerns | emergency で信長直筆復旧が発生する設計は必要だが、復旧後に家老経由へ戻す exit criteria が明文化不足。 |
| M2 efficiency | CONCERN | 直筆復旧は速いが、属人化する。短期速度と長期再現性の tradeoff が未管理。 |
| M3 responsibility | FAIL | F001/F002 は明文化済みでも、緊急例外の「誰が、どこまで、いつ戻すか」が YAML で残らない。 |
| M4 improvement | ACTION | `queue/control_plane.yaml` に `emergency_override`, `authorized_by`, `expires_at`, `return_to_owner` を持たせる。越権を精神論でなく lease 化する。 |

### 2.6 家康代替永久禁止

対象: AGENTS.md の Codex 能力拡張で言及された「家康代替 audit 永久禁止」文脈。家康不在時に家老や信長が代替 audit を積むと、独立監査が崩れる問題。

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL_with_concerns | 家康が token 限界で止まった時、代替 audit の誘惑が発生した。これは監査独立性の破壊であり、復旧 priority を下げてはならない。 |
| M2 efficiency | CONCERN | 代替 audit は短期の詰まりを解くが、後で再監査や判断取消が必要になりやすい。長期 throughput を下げる。 |
| M3 responsibility | FAIL | 家康は一次監査、服部は二次、黒田は議長、本多は retrospective。代替で混ぜると責務境界が崩れる。 |
| M4 improvement | ACTION | `control_plane` に `audit_lane_status` を追加し、家康不在時は「監査待ち」と明示。代替は信長明示承認かつ一時例外として audit log に残す。 |

### 2.7 家康 token 限界

対象: 家康が Claude opus で約 12 時間稼働し、243.6k token で input lost に至った件。

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL | Phase 5 Codex 移行が未完で、監査 persona が Claude の長時間 context に依存した。80/95% 閾値検知も無かった。 |
| M2 efficiency | FAIL | 事前 reset なら短時間で済むが、限界後は audit 停止、再起動、文脈復元が必要になった。 |
| M3 responsibility | FAIL_with_concerns | 家康自身の self-audit と agent_health_check の二重防御が遅れた。家老や信長が補完しようとすると監査独立性を損なう。 |
| M4 improvement | ACTION | `codex-cli-required-persona` と `agent_health_check` の `node|codex` 対応を前提に、家康/本多は Claude 起動を重大違反として検知。token auto-clear escalation は家老にも横展開する。 |

### 2.8 家老 SPOF

対象: 秀吉 1 pane に control-plane、dispatch-plane、dashboard、redo、監査依頼、報告が集中した件。

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL | 家老 reset protocol、baton lease、前田代行、竹中補助、信長 admission が単一 flow として接続されていない。 |
| M2 efficiency | FAIL | 13:10-15:30 の多重発令で家康/本多起動遅延、ashigaru 放置、dispatch latency が発生。並列化が throughput でなく滞留を増やした。 |
| M3 responsibility | FAIL_with_concerns | 竹中補助は有効だが、竹中は dispatch 権を持たない。前田代行は lease が必要。信長は流入を抑える責任を持つ。 |
| M4 improvement | ACTION | `cmd_control_plane_reset_admission_001` を最優先。既存の reset baton と admission control を分けずに同一 cmd で実装する。 |

### 2.9 本多 TUI 描画

対象: 本多常駐 TUI の描画/起動問題と、one-shot 書面運用の必要性。

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | CONCERN | 本多は監査・改革役であり、常駐 TUI がなくても価値を出せる。TUI 復旧が任務の前提になると本末転倒。 |
| M2 efficiency | PASS_with_conditions | one-shot は自然 reset され、docs/report に残るため token 蓄積に強い。長時間 TUI 調査は 45 分で打ち切るべき。 |
| M3 responsibility | PASS_with_conditions | 本多は直接実装者でない。書面起案 mode は F001/F002 を守りやすい。 |
| M4 improvement | ACTION | `cmd_honda_one_shot_ops_001` を通し、`scripts/audit_meta_codex.sh` の出力先、report YAML、信長短文通知を正式化する。 |

## 3. 横断真因

| 真因 | 該当事故 | 改革方向 |
|------|----------|----------|
| SSoT 分散 | split-brain, misroute, pane drift, SecondPC 自律欠落 | registry/transport integrity pack |
| control-plane 過密 | 家老 SPOF, F001 越権, 家康代替禁止 | reset baton, lease, admission |
| 監査 lane 不安定 | 家康 token, 家康代替禁止, 本多 TUI | Codex persona guard, one-shot ops |
| advisory の弱さ | pane drift, F001 越権, split-brain | skill violation logging, staged enforcement |
| 改編 checklist 不在 | misroute, SecondPC 自律欠落, pane drift | regime change checklist, post-change audit |

## 4. 既存 6 cmd 候補の整理

`docs/honda_recommendations_2026-05-08.md` の 6 cmd 候補は良い。ただし Phase 16-4 では重複実装を避け、以下の形に整理する。

| 既存候補 | 扱い | 理由 |
|----------|------|------|
| `cmd_karo_token_reset_baton_001` | `cmd_control_plane_reset_admission_001` に統合 | reset だけでは流入過多を止められない。admission と同時に入れる。 |
| `cmd_shogun_admission_control_001` | 同上 | queued/blocked を control_plane owner と紐付ける必要がある。 |
| `cmd_dual_karo_lane_001` | `cmd_control_plane_reset_admission_001` の Phase 2 | lease が先、dual lane はその上に載せる。 |
| `cmd_honda_one_shot_ops_001` | 単独で維持 | 本多運用の安定化は小工数で価値が高い。 |
| `cmd_bulk_dispatch_template_001` | 後回し | F002 境界が難しく、admission と lease の前に入れると危険。 |
| `cmd_karo_overload_takenaka_assist_001` | 既起案を補強 | 竹中は補助者であり、代行 owner ではない。control_plane 参照を追加すべき。 |

## 5. Phase 16-4 発動準備

### 5.1 本多の起案権限境界

本多は改革 cmd 草案を起案できる。ただし実行命令ではない。

| できる | できない |
|--------|----------|
| 事故横断分析、M1-M4 retrospective、cmd 草案、acceptance criteria、優先順位、信長 inbox への短文進言 | ashigaru 直接命令、家老 bypass dispatch、直接実装、dashboard 主管更新、三者監査最終判定 |

### 5.2 起案前 preflight

Phase 16-4 で本多が cmd 草案を出す前に、以下を必ず見る。

1. 直近 Git: `git log --oneline --since="24 hours ago" | head -40`
2. 関連 cmd: `docs/cmd_*_draft.md`
3. 事故記録: `docs/incident_logs/`
4. Skill: 主要 6 skill の SKILL.md
5. Supabase: `organizational_lessons` schema と seed。接続可能なら後続で read query。
6. SH6: 本多から信長 inbox への通知数が 5/h 未満であること。

### 5.3 最初に起案すべき cmd

```yaml
id: cmd_control_plane_reset_admission_001
north_star: "家老 SPOF と信長発令過多を同時に抑え、土曜決戦の throughput を滞留で潰さぬ。"
purpose: "家老 reset、指揮権 lease、信長 admission control、竹中補助境界を YAML と script で一体運用できるようにする。"
acceptance_criteria:
  - "queue/control_plane.yaml が owner, lease_expires_at, scope, reset_state, audit_lane_status, emergency_override を保持する"
  - "scripts/karo_checkpoint.sh が active cmd, unread inbox, pending, dashboard未反映を YAML 出力できる"
  - "scripts/cmd_admission_control.py が accepted/queued/blocked/requires_lord_decision を返す"
  - "Red 判定時の cmd は即時家老投入されず queue/intake_pending.yaml に退避される"
  - "竹中補助は dispatch/redo/dashboard主管を持たず、control_plane の support_owner としてのみ記録される"
  - "Lord 決裁が必要な item は dashboard.md の要対応欄へ必ず出る"
priority: high
```

この cmd が通れば、家老 token、SPOF、F001 越権、家康代替禁止、竹中補助、信長流入制御が同じ control-plane に乗る。改革の最初の石はこれでよい。

### 5.4 第二に起案すべき cmd

```yaml
id: cmd_registry_transport_integrity_001
north_star: "pane/inbox/routing の分裂を止め、agent が同じ現実を見て動く組織にする。"
purpose: "pane registry、inbox alias、atomic write、SecondPC routing を SSoT と advisory check で統合する。"
acceptance_criteria:
  - "queue/pane_registry.yaml と tmux @agent_id の drift を検出できる"
  - "CLAUDE.md §18.1 は registry 由来の autogen 区間を持つ"
  - "scripts/checks/inbox_alias_integrity.sh が shogun/karo/gunshi alias を検証する"
  - "scripts/checks/symlink_aware_atomic_write.sh が os.replace/os.rename/mv tmp pattern を検出する"
  - "SecondPC receiver は hardcode でなく lib/_section18_roles.sh / shim/hakudokai/_section18_roles.py を参照する"
  - "体制改編 simulation で SSoT 1 箇所更新が watcher/receiver/doc へ波及する"
priority: high
```

## 6. 本多最終進言

上様、改革は多ければ良いのではござらぬ。今朝の 9 件は、すべて「人が頑張れば治る」顔をしておるが、実際は **状態、指揮権、通信路、監査 lane** の欠落でござる。

まず `control_plane` を作り、次に registry/transport を縛る。SecondPC と本多 one-shot はその上に載せる。bulk dispatch は最後でよい。これが「無理させず、楽させず、年貢だけは取る」組織改革にござる。

以上、謀臣 正信、Phase 16-4 発動準備として慎んで起案いたす。
