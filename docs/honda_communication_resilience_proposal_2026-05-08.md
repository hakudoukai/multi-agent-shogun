# 本多正信 報連相 resilience 異視点提案

> 起案: 本多正信 (Codex Pro)  
> 日時: 2026-05-08 16:35 JST  
> 御命令: 理事長殿 16:10「原因と解決方法システム提案」  
> 参照: `docs/communication_resilience_pack_proposal_2026-05-08.md` commit `addd03d`, `docs/ieyasu_communication_breakdown_audit_2026-05-08.md`, 本多既起案 5 件, Supabase `organizational_lessons` seed 9 件  
> 位置付け: 信長案の実装 mapping、家康案の通信 contract に対する、本多の retrospective / governance / 組織経済視点でござる。

## 0. 本多結論

上様、報連相崩壊は「通知が届かぬ」だけではござらぬ。真因は、組織が **報告を年貢として徴収する仕組み** を持たず、各 agent の善意・capture 観察・inbox 既読・report YAML を別々に信用していることにござる。

信長案は既存 cmd への割付として妥当。家康案は message event ledger と contract test が堅い。だが本多の見立てでは、さらに上位に **報連相の納税台帳** が要る。

改革の核は四つ。

1. **通信を成果物の一部にする**: task 完了とは code / doc 完成ではなく、`delivered -> read -> acted -> reported -> audited -> closed` が揃った状態と定義する。
2. **沈黙を状態として扱う**: watcher silent death、SH6 cap、Codex interruption、未読放置は失敗でも成功でもなく `silence_state` として ledger に載せる。
3. **報告責任を owner lease に紐付ける**: 家老、前田、真田、本多、家康の誰が「閉じる責任」を持つかを `queue/control_plane.yaml` に残す。
4. **報連相税を軽く、未納罰を重くする**: 5 秒 preflight と自動 schema check は安く入れ、未報告・未同期・YAML parse error は close gate で止める。

よって信長案 `cmd_communication_resilience_pack_001` は、家康案の `communication_event_ledger` と統合しつつ、本多案として **`cmd_communication_tax_and_silence_accounting_001`** を追加すべし。

## 1. 確認した文脈

| 領域 | 値で確認した内容 | 本提案への反映 |
|------|------------------|----------------|
| Codex plan | `plan_type=prolite`, `account_id=5258dfba-619d-4003-9880-9d6ad4e2957b`, workspace `Personal` | 本多 Codex Pro 前提で起案継続可 |
| Git | 直近 24h に `addd03d`, `2f4b960`, `c5ae3c4`, `0535879`, `5877465`, `d7f14dd` 等 | 既存 hotfix / 本多起案 / 信長案と重複しない |
| Skill | pane identity, codex persona, inbox alias, symlink atomic, secondpc dispatch, lessons-to-skill | 新規 skill 乱造でなく、既存 skill を communication close gate に接続 |
| Supabase | `organizational_lessons` は read 全開、write は `honda/hideyoshi/shogun`、seed 9 件 | 報連相事故を lesson として INSERT/UPDATE 候補化 |
| 進行中 cmd | 大なた root resolution、control_plane、registry/transport、SecondPC reconciliation、communication resilience | cmd 群を束ねる上位 accounting を提案 |

注: `scripts/codex_supabase_query.sh` は現時点で未存在。Supabase 実接続は本提案では行わず、migration と seed を一次資料として扱った。

## 2. M1-M4 Retrospective

| 軸 | 判定 | 所見 |
|----|------|------|
| M1 process | FAIL | inbox、task、report、dashboard、SecondPC state、tmux wake-up が別々に更新され、完了の定義が一貫していない。 |
| M2 efficiency | FAIL | 「届いたか確認」「起きているか確認」「報告が読めるか確認」が毎回人手に戻り、同じ確認で quota を燃やしている。 |
| M3 responsibility | FAIL_with_concerns | 誰が報告を閉じる owner か不明。真田 direct lane、家老 lane、SecondPC lane、本多 retrospective lane が並び、close 責任が散る。 |
| M4 improvement | ACTION_REQUIRED | message ledger だけでなく、owner lease、silence accounting、close tax gate を一体化すべきでござる。 |

## 3. 信長案・家康案との違い

| 観点 | 信長案 | 家康案 | 本多案 |
|------|--------|--------|--------|
| 主眼 | 8 問題を既存 + 新規 cmd へ割付 | message event ledger と contract test | 報告責任と沈黙を会計化し、close gate へ載せる |
| 最小単位 | cmd / stage | message event / correlation id | task 年貢 = 成果 + 報告 + 監査 + owner close |
| 防ぐもの | 実装漏れ | schema / transition 破綻 | 未報告・未同期・沈黙の成功誤認 |
| owner | 実装担当 cmd | event producer / consumer | control_plane lease owner |
| 最終 gate | Stage 1-3 | contract check | communication tax paid / silence cleared |

三案は競合しない。信長案を総大将、家康案を通信契約、本多案を統治会計として重ねるのがよい。

## 4. 新規 cmd 草案

### cmd_communication_tax_and_silence_accounting_001

```yaml
id: cmd_communication_tax_and_silence_accounting_001
north_star: "報連相を善意でなく組織の徴税工程にし、未報告・沈黙・状態分裂を close 前に必ず検出する。"
purpose: "task/cmd の完了条件に communication_tax と silence_state を導入し、owner lease と message ledger に基づいて close 可否を判定できるようにする。"
acceptance_criteria:
  - "queue/control_plane.yaml に communication_tax.required, owner, due_events, unpaid_items, silence_state が記録される"
  - "task close 前に delivered/read/acted/reported/audited/closed の必須 event が揃うことを validator が確認する"
  - "watcher down, SH6 cap, Codex interruption, SecondPC sync lag は silence_state として記録され、成功扱いされない"
  - "unpaid communication_tax がある cmd は dashboard.md 要対応または pending に残り、done へ遷移できない"
  - "SecondPC state reconciliation は communication_tax close gate の一部として走り、MainPC stale state を検出する"
  - "本多 retrospective report に M1-M4 と unpaid/silence 件数が残る"
priority: high
```

## 5. Schema 案

`queue/control_plane.yaml` へ追加する。

```yaml
communication_tax:
  required: true
  owner: hideyoshi | maeda | sanada | honda | ieyasu | nobunaga
  scope: cmd | subtask | audit | reform_lane | secondpc_lane
  due_events:
    - delivered
    - read
    - acted
    - reported
    - audited
    - closed
  paid_events:
    delivered:
      at: "2026-05-08T16:35:00+09:00"
      by: inbox_write
      ref: msg_id
    read: null
    acted: null
    reported: null
    audited: null
    closed: null
  unpaid_items:
    - event: reported
      reason: report_yaml_parse_error | secondpc_sync_lag | watcher_down | owner_unknown
      blocking: true
  silence_state:
    state: clear | watcher_silent | sh6_paused | codex_interrupted | sync_lag | unknown
    first_seen_at: null
    last_checked_at: null
    evidence: null
  close_policy: block_on_unpaid
```

## 6. 実装への組込み順

| 優先 | 既存/新規 | 組込み |
|---:|-----------|--------|
| 1 | `cmd_communication_contract_tests_001` | YAML schema と transition test を先に入れる。 |
| 2 | `cmd_safe_nudge_and_codex_guard_001` | Codex interruption を `silence_state=codex_interrupted` として記録。 |
| 3 | `cmd_communication_event_ledger_001` | event ledger に communication_tax の paid/unpaid を接続。 |
| 4 | `cmd_control_plane_reset_admission_001` | owner lease と communication_tax owner を同じ control_plane へ置く。 |
| 5 | `cmd_communication_tax_and_silence_accounting_001` | close gate と dashboard 要対応へ統合。 |

## 7. 8 問題への対応

| 問題 | 本多案の効き所 |
|------|----------------|
| field `type` 落ち | contract test + unpaid `delivered` で close 不能 |
| SecondPC state 不整合 | `sync_lag` silence_state として記録、reconciliation が未完なら done 禁止 |
| watcher silent death | `watcher_silent` は成功でも idle でもなく要対応 |
| maeda_report YAML 破損 | `reported` event 未納、parse error が blocking |
| ACK / 既読 / report 分裂 | paid_events を correlation id で束ねる |
| send-keys 連発 | `codex_interrupted` と queued_nudge を ledger に残す |
| alert dedup 不足 | silence_state に dedupe key と first_seen_at を置く |
| 家老/真田/本多 lane 並走 | owner lease により「誰が閉じるか」を明示 |

## 8. Supabase lessons 反映候補

```yaml
category: other
root_cause: "報連相を成果物の一部として定義せず、inbox既読・task状態・report YAML・dashboard・SecondPC state が独立更新され、未報告や沈黙が成功と見分けられなかった。"
resolution: "communication_tax と silence_state を control_plane / message ledger に追加し、close 前に delivered/read/acted/reported/audited/closed の納付を validator で確認する。"
skill_impact: "inbox-alias-integrity, secondpc-dispatch-verify, symlink-aware-atomic-write, codex-cli-required-persona を communication close gate へ接続する。"
lessons: "報告は任意の礼儀ではなく task 完了条件である。沈黙は成功ではなく状態として記録し、owner lease に基づき解消する。"
tags:
  - phase16
  - communication
  - resilience
  - honda
  - control_plane
  - silence_accounting
```

## 9. 信長殿への短文報告案

```text
[本多→信長] 報連相 resilience 異視点起案完了。信長案=cmd mapping、家康案=event ledger に加え、本多案は communication_tax + silence_state を提案。報告を task 完了条件として徴税し、沈黙を成功扱いさせぬ。詳細 docs/honda_communication_resilience_proposal_2026-05-08.md。
```

## 10. 本多最終進言

上様、報連相は気合では治らぬ。声を出せ、返事をせよ、と叱るだけでは、次も watcher が死に、YAML が壊れ、SecondPC の成果が帰参せぬ。

正信の策は、報告を年貢として帳簿に載せることにござる。届いた、読んだ、動いた、報告した、監査した、閉じた。この六つが揃うまで完了ではない。沈黙は沈黙として記録し、誰の責任で解くかを lease に刻む。

これにより、無理させず、楽させず、されど年貢は必ず取る組織となるでござる。
