# 本多正信 Phase 16-4 first 起案 — audit_lane_status schema 草案

> 起案: 本多正信 (Codex)  
> 日時: 2026-05-08 18:05 JST  
> 御命令: 理事長殿 17:55「家康不在時監査待ち明示は本多の責務」  
> 位置付け: `queue/control_plane.yaml` 新設時に入れる §2.6 `audit_lane_status` field の schema 草案。実装命令ではなく、信長殿・家老殿が cmd 化するための設計書でござる。

## 0. 結論

上様、家康殿が不在または token / CLI / pane 事故で監査不能となった時、組織が最も犯しやすい誤りは「誰かが代わりに監査したことにする」ことでござる。これは短期には詰まりを解くが、監査独立性を崩し、後で差戻し・再監査・責任境界崩壊を招く。

ゆえに `queue/control_plane.yaml` には、指揮権 lease や admission control と並べて、**監査 lane の状態を明示する `audit_lane_status` を必須 field として置くべし**。家康不在時は `blocked_audit_waiting` と明記し、代替監査は信長殿の明示承認がある一時例外だけに限定する。

## 1. 背景

本朝事故 9 件のうち、特に次の三件が本 schema の直接根拠でござる。

| 事故 | 教訓 |
|------|------|
| 家康 token 243.6k 限界 | 一次監査 lane が止まると、家老・信長・本多が代替したくなる。だが代替は独立性を損なう。 |
| 家康代替 audit 永久禁止 | 家康は一次監査、半蔵は二次、黒田は議長、本多は retrospective。役割混同は監査結果の信用を落とす。 |
| 家老 SPOF / 発令過多 | control-plane に監査待ち状態が無いと、未監査成果物が次工程へ流れ、後戻りが増える。 |

本多の責務は、家康不在時に代替監査を行うことではない。**「今は監査待ちであり、進めてはならぬ」と control-plane に可視化すること**でござる。

## 2. Schema 草案

`queue/control_plane.yaml` に以下を追加する。

```yaml
audit_lane_status:
  required: true
  primary_auditor: ieyasu
  primary_state: available | degraded | unavailable | recovering
  lane_state: clear | audit_waiting | blocked_audit_waiting | exception_active
  blocked_reason: null | token_limit | cli_mismatch | pane_unavailable | inbox_unread | reset_in_progress | unknown
  affected_items:
    - id: "cmd_or_subtask_id"
      type: cmd | subtask | report | redo
      waiting_since: "2026-05-08T17:55:00+09:00"
      required_audit: primary | secondary | chair | retrospective
      current_holder: hideyoshi | maeda | takenaka | honda | none
      next_allowed_action: wait | restore_ieyasu | request_lord_exception | reroute_after_approval
  exception:
    active: false
    authorized_by: null
    authorized_at: null
    expires_at: null
    substitute_auditor: null
    scope: null
    reason: null
  last_checked_at: "2026-05-08T17:55:00+09:00"
  last_checked_by: honda
  notes: "家康不在時は blocked_audit_waiting を明示し、代替監査を既成事実化しない。"
```

## 3. Field semantics

| field | 意味 | 必須 |
|-------|------|------|
| `primary_auditor` | 一次監査の正担当。現行は `ieyasu` 固定。 | yes |
| `primary_state` | 家康殿の稼働状態。CLI mismatch や token limit は `unavailable` または `recovering`。 | yes |
| `lane_state` | 監査 lane として次工程へ流せるか。`blocked_audit_waiting` は次工程停止。 | yes |
| `blocked_reason` | 止める根拠。後続が「なぜ待ちか」を読めるようにする。 | yes when blocked |
| `affected_items` | 監査待ちで止めている cmd / subtask / report。 | yes when waiting |
| `exception` | 代替監査を許す一時例外。通常は `active: false`。 | yes |
| `last_checked_*` | 本多または家老が最後に状態確認した時刻と主体。 | yes |

## 4. 状態遷移

```text
clear
  -> audit_waiting
     条件: 成果物が監査待ちに入ったが、家康殿が available

audit_waiting
  -> blocked_audit_waiting
     条件: 家康殿が unavailable/degraded/recovering で、一次監査が完了できない

blocked_audit_waiting
  -> audit_waiting
     条件: 家康殿が復旧し、同じ affected_items を監査できる

blocked_audit_waiting
  -> exception_active
     条件: 信長殿が例外を明示承認し、期限・scope・代替者を記録

exception_active
  -> audit_waiting
     条件: 例外期限切れ、または家康殿復旧後に正式再監査へ戻す

audit_waiting
  -> clear
     条件: 必須監査が完了し、家老/黒田の次工程判定へ進める
```

禁止遷移:

| from | to | 理由 |
|------|----|------|
| `blocked_audit_waiting` | `clear` | 監査不能を「完了」に変換してはならぬ。 |
| `blocked_audit_waiting` | `exception_active` without `authorized_by` | 代替監査は信長殿の明示承認なき限り不可。 |
| `exception_active` | `clear` without audit log | 例外監査は後で追跡できねばならぬ。 |

## 5. M1-M4 判定

### M1 process

`audit_lane_status` により、監査待ちが dashboard や口頭報告の曖昧な文言でなく、control-plane の primary data として残る。家康殿不在時に「監査済み扱い」が混入する事故を止められる。

### M2 efficiency

短期の代替監査より、明示的な wait の方が rework を減らす。未監査成果物を先へ流すと、後で黒田殿・家老殿・信長殿の判断を巻き戻すため、総工数が増える。

### M3 responsibility

家康殿は一次監査、本多は retrospective / 組織改革、半蔵殿は二次整合性、黒田殿は議長。`audit_lane_status` はこの境界を YAML で守る。例外は信長殿承認つきの lease とし、恒久代替を禁止する。

### M4 improvement

`cmd_control_plane_reset_admission_001` の acceptance criteria に `audit_lane_status` を入れ、`scripts/cmd_admission_control.py` は `blocked_audit_waiting` の時に新規 downstream dispatch を止めるべきでござる。

## 6. Acceptance Criteria 案

`cmd_control_plane_reset_admission_001` へ追加すべき条件:

```yaml
acceptance_criteria:
  - "queue/control_plane.yaml が audit_lane_status.primary_auditor, primary_state, lane_state, blocked_reason, affected_items, exception を保持する"
  - "家康 unavailable 時は未監査成果物が blocked_audit_waiting として記録され、clear に直接遷移できない"
  - "代替監査は exception.active=true, authorized_by, expires_at, substitute_auditor, scope が揃う場合のみ許可される"
  - "scripts/cmd_admission_control.py は lane_state=blocked_audit_waiting の対象 cmd を downstream dispatch しない"
  - "dashboard.md の要対応欄に監査待ち item と復旧/例外承認の選択肢が表示される"
  - "本多 report YAML に audit_lane_status の最終確認時刻と blocked item 数が記録される"
```

## 7. 運用 rule

1. 家康殿が `unavailable` の時、本多は代替監査をしない。
2. 本多は `audit_lane_status` の待ち状態を短文で信長 inbox へ報告し、詳細は docs/report YAML に残す。
3. 家老殿は `blocked_audit_waiting` の item を pending に置き、足軽へ redo / next task として流さない。
4. 信長殿が例外承認する時は、期限・scope・代替者を必ず書く。無期限例外は禁止。
5. 家康殿復旧後は、例外監査済み item も必要に応じて正式再監査へ戻す。

## 8. Supabase lessons 反映候補

`organizational_lessons` へ将来 UPDATE / INSERT するなら、以下の lesson として蓄積する。

```yaml
category: token_limit
root_cause: "一次監査 persona 不在時の状態 field が control-plane に無く、代替監査や未監査通過の誘惑が生じた。"
resolution: "queue/control_plane.yaml に audit_lane_status を追加し、blocked_audit_waiting と exception lease を明示する。"
skill_impact: "codex-cli-required-persona と honda one-shot ops に、代替監査禁止と監査待ち明示を追記候補とする。"
lessons: "監査 lane は availability と completion を分けて記録する。監査不能は完了ではなく blocked として扱う。"
tags:
  - phase16
  - audit_lane
  - ieyasu
  - honda
  - control_plane
```

## 9. 本多最終進言

上様、監査は「誰かが見た」では足りませぬ。誰が、どの権限で、どの期限内に、何を見たかが残らねば、後で軍議の根が腐る。

家康殿不在時の正解は代役探しではなく、まず **監査待ちを監査待ちとして明示すること**。これを `control_plane` に刻めば、家老殿も竹中殿も前田殿も迷わぬ。無理させず、楽させず、されど年貢は取り切るための、小さく強い field にござる。
