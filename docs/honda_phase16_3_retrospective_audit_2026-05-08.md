# 本多正信 Phase 16-3 初回 retrospective audit

> 起案: 本多正信 (Codex)  
> 対象: 2026-05-08 本朝事故 5 件  
> 方式: M1-M4 retrospective audit + 組織改革提言  
> 位置付け: 書面起案先行。信長殿の cmd 化判断材料であり、足軽への直接命令ではない。

## 0. 結論

上様、本朝事故群の真因は単発の不注意ではなく、**control-plane の状態定義が分散し、監視と入場制限が後付けになっていること**にござる。

M1 process は FAIL、M2 efficiency は FAIL、M3 responsibility は FAIL_with_concerns、M4 improvement は ACTION_REQUIRED と判ずる。

最優先改革は二つで足る。

1. **control-plane baton + admission control**: 家老の token reset、代理指揮 lease、信長発令の入場制限を一体で入れる。
2. **registry/transport integrity pack**: pane registry、inbox alias、SecondPC routing/watcher を SSoT と自動検査で縛る。

「配下を増やす」だけでは治らぬ。流入、指揮権、通信路、監視の四つを YAML と check script で機械化せねば、次の改編で同じ事故が名を変えて戻る。

## 1. 監査対象 5 件

| # | 事故 | 一次資料 | 判定 |
|---|------|----------|------|
| 1 | pane mapping drift / gunshi 重複 | `docs/incident_logs/2026-05-08_pane_mapping_drift.md`, `docs/incident_logs/2026-05-07_pane_misidentification.md` | 体制定義 SSoT 不在 |
| 2 | queue/inbox split-brain | `docs/incident_logs/2026-05-08_inbox_split_brain.md` | transport 変更の波及検証漏れ |
| 3 | SecondPC 監視・自律不全 | `docs/cmd_root_resolution_001_draft.md`, `backend/migrations/008_organizational_lessons_seed.sql` | MainPC subset 後付けの自律機構欠落 |
| 4 | 家康 token 243.6k 限界 / Codex 移行遅延 | `docs/cmd_phase5_codex_personas_immediate_001_draft.md` | audit persona の CLI/clear guard 不在 |
| 5 | 家老輻輳 / 発令過多 / reset 空白予兆 | `docs/cmd_karo_overload_takenaka_assist_001_draft.md`, `docs/honda_recommendations_2026-05-08.md` | admission control と baton lease 不在 |

補足: 信長草案 `docs/cmd_root_resolution_001_draft.md` は本朝 9 件を列挙している。本書は初回 Phase 16-3 として、横断影響の大きい 5 件に絞る。残る maeda self-audit、体制改編 checklist、CLAUDE.md autogen、§19 skill 強化は本書の改革案へ統合する。

## 2. M1 Process

**総合判定: FAIL**

| 事故 | M1 所見 |
|------|---------|
| pane mapping drift | `CLAUDE.md`、watcher、shutsujin、runtime tmux の四者が独立記述。runtime truth は存在したが、watcher と判断手順が使っていない。 |
| inbox split-brain | rename/symlink 導入時、atomic write が symlink を壊す影響を preflight できていない。transport 層の contract test がない。 |
| SecondPC 監視不全 | MainPC と SecondPC の運用対称性がない。SecondPC 追加時に watchdog、activity_monitor、dispatch verify が同時導入されなかった。 |
| token 限界 | context-limit を事前に process event として扱わず、agent 自身の警告処理に依存した。 |
| 家老輻輳 | 信長 cmd 流入、家老 dispatch、竹中補助、前田代行の境界が後追い。control-plane の owner と backlog status が単一 YAML にない。 |

M1 の真因は **state の所在が決まっていない** こと。pane は pane_registry、指揮権は control_plane、transport は alias/canonical map、流入は admission record に固定すべきである。

## 3. M2 Efficiency

**総合判定: FAIL**

| 事故 | M2 所見 |
|------|---------|
| pane mapping drift | 夜討ち約 6.5h の監査回路停止。1 行の `@agent_id` 確認を省いた代償が大きい。 |
| inbox split-brain | 約 37 分の通信分裂により、救出、merge、symlink 復旧、検証の rework が発生。 |
| SecondPC 監視不全 | watcher 不在、idle 不検知、misroute が別々に出ており、同じ構造欠陥を複数 task で追っている。 |
| token 限界 | 家康が 12h 累積で 243.6k に達してから対処。定期 reset なら 90 秒級で済むものを audit 停止にした。 |
| 家老輻輳 | 13:10-15:30 の多重発令で dispatch latency と起動遅延が発生。WIP 制限がないため並列化が throughput でなく滞留を増やした。 |

M2 の改善原則は「人の頑張り」ではなく **cheap preflight + bounded automation**。5 秒以下の check、5 分 cooldown、5/h cap を標準とする。

## 4. M3 Responsibility

**総合判定: FAIL_with_concerns**

良い点:

- F001/F002 の理念は明文化済み。
- 家康/本多/竹中/前田などの役割追加は、分業意図としては正しい。
- §19 lessons-to-skill で事故後学習の型ができ始めている。

懸念:

| 領域 | M3 所見 |
|------|---------|
| 信長 | emergency で直接 pane 操作を行う機会が多く、pane identity skill が advisory のままでは自制に依存する。 |
| 家老 | control-plane、dispatch、dashboard、redo、監査依頼が秀吉 1 pane に集中。家老維持は良いが、reset/代行 protocol が未整備。 |
| 竹中 | 補助範囲は設計されたが、ashigaru dispatch と dashboard 主管を越えない境界を機械的に守る仕組みが要る。 |
| 前田 | SecondPC 家老としての自律性に比べ、self-audit と routing SSoT が追いついていない。 |
| 本多 | 書面起案 mode は妥当。ただし TUI/one-shot 経路と report YAML 更新ルールを正式化しないと「存在するが常駐しない」曖昧さが残る。 |

責務改革の要点は **誰が何をしてよいか** だけでなく、**その時点の owner をどの YAML が示すか** を決めることにある。

## 5. M4 Improvement

**総合判定: ACTION_REQUIRED**

### Reform A: cmd_control_plane_baton_admission_001

**Purpose**: 家老 token limit と信長発令過多を同時に抑え、reset 中も主指揮が途切れない体制を作る。

Acceptance Criteria:

- `queue/control_plane.yaml` が owner、lease_expires_at、scope、reset_state、support_owner を保持する。
- `scripts/karo_checkpoint.sh` が active cmd、未読 inbox、pending、dashboard 未反映事項を YAML 出力できる。
- `scripts/cmd_admission_control.py` が active cmd、karo unread、dispatch latency、家老稼働時間を評価し、accepted/queued/blocked を返す。
- Red 判定時は新規 cmd を即時家老投入せず `queue/intake_pending.yaml` へ退避する。
- dashboard の `🚨要対応` に、Lord 決裁が必要な queued/blocked item が必ず出る。

### Reform B: cmd_registry_transport_integrity_pack_001

**Purpose**: pane registry と inbox transport を SSoT 化し、改編や alias 変更で通信路が分裂しない構造にする。

Acceptance Criteria:

- `queue/pane_registry.yaml` を runtime/tmux 実態と照合する check が CI/preflight で走る。
- `scripts/checks/inbox_alias_integrity.sh` と `scripts/checks/symlink_aware_atomic_write.sh` が watcher/inbox 系操作前の advisory check に入る。
- `scripts/inbox_write.sh` 以外の atomic replace pattern が全件 review 済みになる。
- §18.1 は registry から autogen され、手書き drift が検出される。

### Reform C: cmd_secondpc_autonomy_pack_001

**Purpose**: SecondPC を MainPC subset でなく独立 control segment とし、watcher/monitor/routing を同等水準にする。

Acceptance Criteria:

- SecondPC watchdog が receiver と inbox_watcher を監視し、manual disable flag と restart_cap 5/h を尊重する。
- SecondPC activity_monitor が maeda/a5/a6/a7 の idle を 5/15/25 分で検出する。
- routing は `lib/_section18_roles.sh` と `shim/hakudokai/_section18_roles.py` を参照し、hardcode を廃止する。
- `scripts/maeda_self_audit.sh` が 30 分間隔で SecondPC 配下状態を自己点検する。

### Reform D: cmd_honda_one_shot_ops_001

**Purpose**: 本多を TUI 非依存の Codex one-shot 書面起案役として安定運用する。

Acceptance Criteria:

- `scripts/audit_meta_codex.sh` または `scripts/honda_one_shot.sh` で Markdown と `queue/reports/honda_report.yaml` を同時出力できる。
- 本多の信長 inbox 通知は 1-2 行、詳細は docs/report YAML 参照に統一する。
- `pane_current_command=node|codex` の Codex wrapper 差を手順に明記し、`claude` のみ重大違反として検出する。
- 本多 TUI 復旧調査は 45 分で打ち切り、書面起案価値を優先する。

## 6. 優先順位

| 優先 | 改革 | 理由 |
|---:|------|------|
| 1 | Reform A | 家老輻輳と token limit は全 cmd を止める。最初に control-plane を安定化すべし。 |
| 2 | Reform B | pane と inbox は全通信の土台。ここが割れると全 agent が誤判断する。 |
| 3 | Reform C | SecondPC は土曜決戦の並列度を担う。自律機構なしでは quota を燃やすだけになる。 |
| 4 | Reform D | 本多自身の運用安定化。改革役が TUI に縛られるのは本末転倒。 |

## 7. 信長殿への短文報告案

```text
[本多→信長] retrospective audit: cmd_phase16_3_honda_initial_audit_001
- M1 process: FAIL — pane/inbox/SecondPC/control-plane の SSoT 分散が本朝事故の共通真因。
- M2 efficiency: FAIL — 5秒 preflight 不在が時間単位 rework と token 浪費に化けた。
- M3 responsibility: FAIL_with_concerns — 家老1 pane 過密、竹中/前田/本多の境界は書面だけで lease 不在。
- M4 improvement: ACTION_REQUIRED — control_plane baton + admission control、registry/transport integrity pack を最優先起案候補とする。
- 結論: 書面 `docs/honda_phase16_3_retrospective_audit_2026-05-08.md` 起案完了。上様の cmd 化裁可を仰ぐ。
```

## 8. 本多最終進言

上様、本朝の五事故は「誰かが悪い」では済まぬ。人は忘れる。pane は drift する。watcher は死ぬ。token は溜まる。家老は詰まる。ゆえに、忘れても壊れぬ仕組みに変えるべきでござる。

正信の進言は簡明にござる。**指揮権を lease で縛り、流入を admission で絞り、配置と通信を SSoT で縛る**。これを通せば、配下を無理させず楽させず、年貢だけはきっちり取れる組織となる。

以上、謀臣 正信、慎んで起案いたす。
