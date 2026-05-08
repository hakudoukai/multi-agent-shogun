# 本多正信 Phase 16-4 second 起案 — 検証から実装までの全体設計

> 起案: 本多正信 (Codex)  
> 日時: 2026-05-08 18:45 JST  
> 御命令: 理事長殿 18:15「本多進言の検証→実装フローを構築し実施」  
> 統合元: `docs/honda_phase16_3_retrospective_audit_2026-05-08.md`, `docs/honda_initial_proposals_2026-05-08.md`, `docs/honda_audit_lane_status_design_2026-05-08.md`  
> 位置付け: 信長殿が順次 dispatch できる cmd 群の検証・実装・完遂判定 flow 草案。実行命令ではなく、家老殿へ渡すための設計書でござる。

## 0. 結論

Phase 16-4 は cmd を乱発せず、以下の順で通すべし。

1. `cmd_control_plane_reset_admission_001`
2. `cmd_audit_lane_status_field_001`
3. `cmd_registry_transport_integrity_001`
4. `cmd_secondpc_autonomy_pack_001`
5. `cmd_honda_one_shot_ops_001`

順序の理由は明快でござる。まず control-plane を作らねば、指揮権・流入・監査待ち・例外承認が記録できぬ。次に audit lane を固め、未監査成果物を止める。その後、pane/inbox/routing の土台を縛り、SecondPC 自律化と本多 one-shot を載せる。

## 1. 共通 gate

全 cmd は以下の gate を通す。

| gate | 内容 | owner |
|------|------|-------|
| G0 Context | Git 24h、関連 cmd、主要 skill、Supabase lessons seed、既存 docs を読む | 家老 + 担当 |
| G1 Spec | 目的、acceptance criteria、担当、期限、rollback を YAML 化 | 家老 |
| G2 Test Plan | unit / integration / tmux dry run / YAML parse / bats を事前定義 | 家老 + 家康 |
| G3 Implement | 足軽または前田/竹中が担当範囲だけ実装 | 担当 |
| G4 Verify | テスト実行、skip=fail、実値証跡を report へ記録 | 家老 |
| G5 三者監査 | 家康一次、Codex 6軸、Gemini/半蔵8観点。未整備なら fallback 理由を明記 | 家老 |
| G6 Close | acceptance criteria 全件 PASS、dashboard 要対応整理、report YAML 更新 | 家老 |

## 2. 実装一覧

| 優先 | cmd | 主担当 | 補助 | 期限目安 | 完遂判定 |
|---:|-----|--------|------|----------|----------|
| 1 | `cmd_control_plane_reset_admission_001` | ashigaru2 | hideyoshi, takenaka, maeda | 2026-05-08 21:00 | control_plane + checkpoint + admission が dry run PASS |
| 2 | `cmd_audit_lane_status_field_001` | ashigaru2 | ieyasu, honda | 2026-05-08 22:00 | 家康 unavailable 時に blocked_audit_waiting が出る |
| 3 | `cmd_registry_transport_integrity_001` | ashigaru1 + ashigaru6 | honda | 2026-05-09 10:00 | pane/inbox/routing の drift check PASS |
| 4 | `cmd_secondpc_autonomy_pack_001` | ashigaru5 + ashigaru7 + maeda | ashigaru6 | 2026-05-09 14:00 | SecondPC watchdog / monitor / self-audit dry run PASS |
| 5 | `cmd_honda_one_shot_ops_001` | ashigaru2 | honda | 2026-05-09 16:00 | TUI 不調でも docs + report YAML を生成できる |

## 3. cmd_control_plane_reset_admission_001

### 検証 step

| step | 方法 | PASS 条件 |
|------|------|-----------|
| V1 YAML schema | `python3 -c "import yaml; yaml.safe_load(open('queue/control_plane.yaml'))"` | parse error なし |
| V2 checkpoint dry run | `scripts/karo_checkpoint.sh --dry-run` | active cmd / unread / pending / dashboard_pending が出る |
| V3 admission dry run | `scripts/cmd_admission_control.py --dry-run --scenario red` | `queued` or `blocked` を返す |
| V4 lease expiry | expired lease fixture | 期限切れ owner が無効化される |
| V5 dashboard 要対応 | Red scenario | Lord 決裁が必要な item が要対応へ出る |
| V6 三者監査 | 家康 + Codex + Gemini | 全 PASS。SKIP 1 件以上なら未完了 |

### 実装 step

| work | owner | scope |
|------|-------|-------|
| `queue/control_plane.yaml` schema + fixture | ashigaru2 | owner, lease, reset_state, support_owner, emergency_override |
| `scripts/karo_checkpoint.sh` | ashigaru2 | read-only aggregation, no destructive action |
| `scripts/cmd_admission_control.py` | ashigaru2 | accepted/queued/blocked/requires_lord_decision |
| `instructions/karo.md` / `maeda.md` / `takenaka.md` 追記案 | hideyoshi | 代理権限と禁止事項 |
| 竹中補助境界 | takenaka | support_owner only, no dispatch/redo authority |

### 完遂判定 step

```yaml
done_when:
  - "mock Yellow/Orange/Red 3 scenarios が PASS"
  - "queued/blocked item が即時家老投入されない"
  - "control_plane owner と support_owner が明示される"
  - "dashboard 要対応に Lord decision item が出る"
  - "三者監査 PASS、skip=0"
```

## 4. cmd_audit_lane_status_field_001

### 検証 step

| step | 方法 | PASS 条件 |
|------|------|-----------|
| V1 schema parse | `control_plane.audit_lane_status` fixture | required key 全件あり |
| V2 unavailable scenario | `primary_state=unavailable` | `lane_state=blocked_audit_waiting` |
| V3 forbidden transition | blocked -> clear fixture | validator が FAIL |
| V4 exception scenario | authorized_by/expires_at/substitute/scope あり | `exception_active` 許可 |
| V5 no exception | authorized_by 欠落 | 代替監査不可 |
| V6 三者監査 | 家康復旧後 + 本多 retrospective | 代替監査禁止が守られる |

### 実装 step

| work | owner | scope |
|------|-------|-------|
| `audit_lane_status` schema を `queue/control_plane.yaml` に追加 | ashigaru2 | primary_auditor, primary_state, lane_state, blocked_reason, affected_items, exception |
| validator 追加 | ashigaru2 | `scripts/cmd_admission_control.py` または専用 `scripts/checks/audit_lane_status.sh` |
| dashboard 要対応連携 | hideyoshi | blocked item と例外承認選択肢 |
| 本多 report 連携 | honda | docs/report で blocked item summary |

### 完遂判定 step

```yaml
done_when:
  - "家康 unavailable 時に未監査 item が clear にならない"
  - "代替監査は信長承認 + expires_at + scope がない限り不可"
  - "blocked item が downstream dispatch されない"
  - "dashboard 要対応に監査待ちが表示される"
  - "三者監査 PASS、skip=0"
```

## 5. cmd_registry_transport_integrity_001

### 検証 step

| step | 方法 | PASS 条件 |
|------|------|-----------|
| V1 pane 4-way | `bash scripts/checks/pane_identity.sh` | tmux / registry / watcher / docs の drift なし |
| V2 inbox alias | `bash scripts/checks/inbox_alias_integrity.sh` | shogun/karo/gunshi alias が canonical symlink |
| V3 atomic write | `bash scripts/checks/symlink_aware_atomic_write.sh` | critical なし、warn は review 済 |
| V4 routing SSoT | maeda 追加 simulation | receiver が hardcode でなく SSoT 参照 |
| V5 generated docs | §18.1 autogen dry run | 手書き drift が検出される |
| V6 三者監査 | 家康 + Codex + Gemini | 全 PASS、skip=0 |

### 実装 step

| work | owner | scope |
|------|-------|-------|
| §18.1 autogen / pane registry | ashigaru1 | registry SSoT と docs 生成 |
| SecondPC routing SSoT | ashigaru6 | receiver hardcode 廃止 |
| inbox / atomic check hook 案 | ashigaru1 | advisory only, timeout 5s |
| lessons 反映候補 | honda | Supabase organizational_lessons 更新案 |

### 完遂判定 step

```yaml
done_when:
  - "pane identity 4-way check PASS"
  - "inbox alias integrity PASS"
  - "routing hardcode grep で未解決箇所なし"
  - "体制改編 simulation PASS"
  - "三者監査 PASS、skip=0"
```

## 6. cmd_secondpc_autonomy_pack_001

### 検証 step

| step | 方法 | PASS 条件 |
|------|------|-----------|
| V1 watchdog dry run | SecondPC receiver/watcher mock | restart_cap 5/h と manual disable 尊重 |
| V2 activity monitor | idle 5/15/25 fixture | maeda -> nobunaga escalation が段階通り |
| V3 maeda self-audit | `scripts/maeda_self_audit.sh --dry-run` | 配下 idle と自責務を検出 |
| V4 dispatch verify | `scripts/checks/secondpc_dispatch.sh ashigaru5` | task file + inbox_write 両方確認 |
| V5 routing | ashigaru5/6/7/maeda | valid_secondpc 全件 PASS |
| V6 三者監査 | 家康 + Codex + Gemini | 全 PASS、skip=0 |

### 実装 step

| work | owner | scope |
|------|-------|-------|
| SecondPC watchdog | ashigaru7 | receiver + inbox_watcher 監視 |
| SecondPC activity monitor | ashigaru5 | idle detection + escalation |
| routing SSoT 接続 | ashigaru6 | cmd_registry_transport_integrity と整合 |
| maeda self-audit | maeda | 30分間隔案、dashboard 月次 summary |

### 完遂判定 step

```yaml
done_when:
  - "manual disable flag が尊重される"
  - "restart cap 5/h を超えない"
  - "idle escalation が maeda first, nobunaga second で動く"
  - "SecondPC dispatch verify PASS"
  - "三者監査 PASS、skip=0"
```

## 7. cmd_honda_one_shot_ops_001

### 検証 step

| step | 方法 | PASS 条件 |
|------|------|-----------|
| V1 one-shot dry run | `scripts/audit_meta_codex.sh --dry-run` or wrapper | docs と report YAML の出力 path が出る |
| V2 YAML parse | `queue/reports/honda_report.yaml` | parse error なし |
| V3 TUI degraded | honda TUI capture 空白 fixture | one-shot 経路で成果物が出る |
| V4 SH6 cap | 5/h counter fixture | 超過時に自発停止 |
| V5 inbox brief | 信長 inbox message fixture | 1-2 行、詳細 docs 参照 |
| V6 三者監査 | 家康 + Codex + Gemini | 全 PASS、skip=0 |

### 実装 step

| work | owner | scope |
|------|-------|-------|
| `scripts/honda_one_shot.sh` or `audit_meta_codex.sh` 拡張 | ashigaru2 | prompt input, docs output, report YAML update |
| TUI troubleshooting runbook | ashigaru2 | refresh-client / select-window / C-l の使い分け |
| 本多運用 rule 追記 | honda | one-shot primary, TUI secondary |
| codex CLI self audit 維持 | honda | node|codex を許容、claude は重大違反 |

### 完遂判定 step

```yaml
done_when:
  - "TUI 不調時も docs/honda_*.md が生成される"
  - "honda_report.yaml が更新される"
  - "信長 inbox は短文通知のみ"
  - "SH6 cap 5/h を超えない"
  - "三者監査 PASS、skip=0"
```

## 8. Dispatch 用 cmd 草案

信長殿が家老殿へ渡すなら、以下の順に `queue/shogun_to_karo.yaml` へ起票するのがよい。

```yaml
- id: cmd_control_plane_reset_admission_001
  priority: high
  purpose: "家老 reset、指揮権 lease、信長 admission control を control_plane で一体運用できるようにする。"
  acceptance_criteria:
    - "queue/control_plane.yaml が owner, lease_expires_at, scope, reset_state, support_owner, emergency_override を保持する"
    - "scripts/karo_checkpoint.sh が active cmd, unread inbox, pending, dashboard未反映を YAML 出力できる"
    - "scripts/cmd_admission_control.py が accepted/queued/blocked/requires_lord_decision を返す"
    - "Red 判定時の cmd は即時家老投入されず queue/intake_pending.yaml に退避される"
    - "三者監査 PASS、skip=0"

- id: cmd_audit_lane_status_field_001
  priority: high
  purpose: "家康不在時の監査待ちを audit_lane_status で明示し、代替監査の既成事実化を防ぐ。"
  acceptance_criteria:
    - "control_plane.audit_lane_status が required keys を保持する"
    - "primary_state=unavailable 時に lane_state=blocked_audit_waiting となる"
    - "代替監査は信長承認、expires_at、substitute_auditor、scope が揃う場合のみ許可される"
    - "blocked item が downstream dispatch されない"
    - "三者監査 PASS、skip=0"

- id: cmd_registry_transport_integrity_001
  priority: high
  purpose: "pane registry、inbox alias、atomic write、SecondPC routing を SSoT と check で統合する。"
  acceptance_criteria:
    - "pane identity 4-way check PASS"
    - "inbox alias integrity PASS"
    - "symlink-aware atomic write critical なし"
    - "SecondPC receiver が routing SSoT を参照する"
    - "三者監査 PASS、skip=0"

- id: cmd_secondpc_autonomy_pack_001
  priority: high
  purpose: "SecondPC watchdog、activity_monitor、maeda self-audit、dispatch verify を一体で完成させる。"
  acceptance_criteria:
    - "watchdog が manual disable と restart cap 5/h を尊重する"
    - "activity_monitor が 5/15/25 分 idle を検出する"
    - "maeda self-audit dry run PASS"
    - "secondpc_dispatch verify PASS"
    - "三者監査 PASS、skip=0"

- id: cmd_honda_one_shot_ops_001
  priority: medium
  purpose: "本多を TUI 非依存の one-shot 書面起案役として安定運用する。"
  acceptance_criteria:
    - "one-shot wrapper が docs と honda_report.yaml を出力できる"
    - "TUI capture 空白時も成果物が出る"
    - "信長 inbox は短文通知のみ"
    - "SH6 cap 5/h を守る"
    - "三者監査 PASS、skip=0"
```

## 9. 完遂判定の絶対条件

全 cmd 共通で、以下を満たさぬ限り「完了」と呼んではならぬ。

- acceptance criteria 全件 PASS
- テスト SKIP 0
- YAML parse error 0
- dashboard 要対応に未処理の Lord decision が残る場合は「完了」ではなく `requires_lord_decision`
- 家康一次監査または明示 fallback、Codex 6軸、Gemini/半蔵 8観点の証跡あり
- 本多 retrospective は「仕組みが正常に動いたか」を M1-M4 で追記

## 10. 本多最終進言

上様、進言は実装されねばただの紙でござる。しかし、検証なしに実装へ突っ込めば、また紙を増やすだけにござる。

ゆえに本 flow は、まず control-plane、次に audit lane、続いて registry/transport、SecondPC、本多 one-shot の順で、検証を先に置く。足軽を働かせ、家老に統括させ、家康殿・Codex・半蔵殿で検める。これなら、正信の進言は軍令に変わり、軍令は実装に変わり、実装は再発防止として残るでござる。
