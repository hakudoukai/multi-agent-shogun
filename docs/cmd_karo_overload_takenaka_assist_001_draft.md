# cmd_karo_overload_takenaka_assist_001 (草案) — 家老輻輳時 竹中自動分担補助

> **Status**: 信長直起案、理事長殿明示直命 2026-05-08 15:45「秀吉業務過剰の場合は、竹中分担補助するようなルールを明確化し、自動実行を組み上げる事」
> **Drafted by**: 信長 (織田信長) 2026-05-08 15:48 JST
> **緊急性**: 中、本朝家老輻輳事故 (= 13:10〜15:30 で大なた + Phase 5 + 文脈アーカイブ + ashigaru2 redo + watcher 緊急 等並列発令、家康/本多起動 12 分以上停滞) の恒久対策

---

## 1. North Star

**家老 (秀吉) が業務過剰となった際、竹中 (計画参謀) が自動的に分担補助する構造的体制** を確立、家老単独 dispatch 容量超過による組織停滞を恒久解消。

## 2. Purpose

本朝の事象:
- 信長並列発令 8 件 (= 13:10〜15:30) で家老輻輳
- 家康 Session Start prompt 送付が 12 分以上遅延
- 本多 0.6 split-window 未実施
- ashigaru2 67 分放置 (= 別要因と連動)

= **家老単独 dispatch では並列度に限界**、構造的補助体制が必要。

## 3. 検知ロジック (= 家老輻輳判定)

以下のいずれかに該当時、輻輳判定:

| 指標 | 閾値 | 計測方法 |
|------|------|---------|
| **karo inbox unread 件数** | **≥ 10 件** | `python3 -c "yaml..."` で count |
| **inbox 受信から処理開始 latency** | **≥ 5 分** | inbox timestamp と report 更新時刻の差 |
| **cmd 受領から ashigaru dispatch latency** | **≥ 5 分** | inbox から ashigaru 宛 inbox_write までの差 |
| **並列 cmd_new 受領数 (1h 内)** | **≥ 5 件** | 1h 内の karo inbox cmd_new count |
| **未着手 sub-phase 数 (= 大なた 等)** | **≥ 3 件** | task YAML status=pending |

複数指標で複合判定、いずれか **≥ 1** で **mild 輻輳**、**≥ 3** で **severe 輻輳**。

## 4. 自動分担トリガー

### 4.1 mild 輻輳 (= 1-2 指標 hit)

竹中に **audit / preparation 補助命令** 自動 inbox_write:
- 担当範囲: 軽量 task (= audit, preparation, 隘路検出, 監視)
- 家老負担: 軽減 (= 重量 task のみに集中)

### 4.2 severe 輻輳 (= 3+ 指標 hit)

竹中に **戦略補助 + 信長 escalation 同時起動**:
- 竹中 = 軽量 task 全引受 + 信長進言
- 信長 = 並列発令 上限自動抑制 + 大なた sub-phase 段階化判断
- ashigaru 並列度自動絞り込み (= 同時 in_progress 数制限)

## 5. 自動分担の境界 (= 厳守)

### 5.1 竹中分担可能 (= 自動振分 OK)

| task 種別 | 詳細 |
|----------|------|
| **audit** | 完遂 task の品質 review、結果分析、信長進言 |
| **preparation** | cmd 草案 8 観点 review、依存 task 整理、preconditions 確認 |
| **隘路検出** | 並列 cmd 整合性 review、競合 risk 抽出 |
| **skill 違反監視** | §19 skill (= pane-identity-verify, codex-cli-required-persona) 運用 audit |
| **dashboard 一部更新** | audit 結果反映、輻輳状態可視化 |
| **信長進言** | 戦略上申、隘路報告、改善提案 |

### 5.2 家老専管 (= 自動分担禁止、家老継続)

| task 種別 | 理由 |
|----------|------|
| **ashigaru dispatch** | F002 順守、家老の専管事項 |
| **三者監査依頼判定** | 家老の判断責務 |
| **強権発動 (罰則)** | §0 常在戦場 mandate 罰則権限は家老 |
| **dashboard 主管更新** | dashboard 主管は家老 (= 信長 mandatory rules §1) |
| **redo protocol 発動** | clear_command 送付権限は家老 |

竹中は 5.2 を一切引受けない、F001 + F002 順守。

## 6. 実装

### 6.1 検知 watcher (= 新規 script)

`scripts/karo_overload_monitor.sh` 新設:
- 1 分間隔で 5 指標 check
- 閾値超過 → cooldown 5 分 + 竹中 inbox_write 自動発火
- 同型 watcher と整合 (= activity_monitor + watchdog 系列)
- §19.3 順守: ブロックなし、advisory 通知のみ

### 6.2 cooldown + 上限 (= §15 SH6 SH2 順守)

- 同一輻輳指標で 1 件竹中 inbox_write、5 分以内重複禁止
- 1h 5 件上限 (= SH6 cap)
- 上限超過時 → 信長 inbox escalation
- exponential backoff (= SH2): 連続失敗時 1s → 2s → 4s

### 6.3 persona 規定追記

#### `instructions/karo.md` (= 家老 hideyoshi/maeda 共通)
- §X. 輻輳時の竹中要請 protocol:
  - 自身で輻輳判定 (= 5 指標 self-check) 周期 5 分
  - 検知時は **自身から竹中に補助要請 inbox_write** (= proactive、watcher 待ちでなく)
  - 補助要請時は task 種別を 5.1 範囲内で明示

#### `instructions/takenaka.md`
- §X. 補助要請受領 protocol:
  - 家老 inbox_write 受領 → 5 分以内応答 + 着手
  - 家老 watcher 自動 trigger からの inbox 同型対応
  - 5.1 範囲外の要請 → 拒否 + 信長 inbox 上申

### 6.4 dashboard 反映

`dashboard.md` に新セクション:
```markdown
## 🏯 家老輻輳状況

| 指標 | 現状 | 閾値 | 状態 |
|------|------|------|------|
| karo inbox unread | N 件 | 10 | OK / mild / severe |
| dispatch latency | N 分 | 5 | OK / mild / severe |
| 並列 cmd_new | N 件 | 5 | OK / mild / severe |
| 竹中補助 task | N 件 | — | 進行中 |
```

家老が 30 分間隔で更新、竹中監視。

## 7. Acceptance Criteria

- ✅ scripts/karo_overload_monitor.sh 新設 + cron / supervisor 登録
- ✅ instructions/karo.md (= hideyoshi/maeda 継承) §X 輻輳要請 protocol 追記
- ✅ instructions/takenaka.md §X 補助受領 protocol 追記
- ✅ dashboard.md 輻輳状況セクション
- ✅ 自動分担動作確認 (= mock 輻輳発生時の竹中自動着手)
- ✅ §15 SH6 / SH2 / SH3 順守確認 (= cooldown / retry / escalation)
- ✅ F001/F002 厳守確認 (= 5.2 自動分担禁止対象)
- ✅ 三者監査 PASS

## 8. PDCA + 期限

- max cycle 5
- cycle1 完遂期限: 本日 17:00
- 即時動作確認: 17:00 以降の家老輻輳事象で実機検証

## 9. 命令文 (= 秀吉発令)

```
秀吉、本 cmd 受領、sub-phase 担当割当:
- 6.1 watcher script: ashigaru2 (= 既存 watcher 系列の経験者)
- 6.2 cooldown logic: ashigaru2 統合
- 6.3 persona 規定追記: 信長兼任 (= 軍師執筆責務、F001 OK)
- 6.4 dashboard 反映: 家老主管
- 三者監査必須 (= 家康 codex 復帰後 + 本多 retrospective + 服部半蔵 招聘後)
PDCA max=5、cycle1 = 本日 17:00 期限。
```

## 10. Risk + Mitigation

| risk | mitigation |
|------|----------|
| 自動 trigger 暴走 (= 連発で竹中 quota 燃焼) | §15 SH6 cap 5/h + cooldown 5 分 |
| 5.2 専管 task の自動分担漏れ | 5 指標 + 5.1/5.2 境界明示、watcher logic で 5.2 除外 |
| 家老/竹中の責務曖昧化 | persona instructions で境界明示、§X 規定追記 |
| §15 SH9 (= state 不整合) | watcher state /tmp/karo_overload_state.json で永続化 + reset |
| 竹中過負荷 (= 補助 task 集中) | 竹中側にも SH6 cap、超過時は信長 escalation |

## 11. 関連資産

- docs/cmd_root_resolution_001_draft.md (= 大なた、本 cmd は別 cmd で並走)
- docs/cmd_phase15_takenaka_proactive_draft.md (= 竹中 招聘、本 cmd で補助 protocol 拡張)
- instructions/karo.md (= 改訂対象)
- instructions/takenaka.md (= 改訂対象)
- instructions/hideyoshi.md / maeda.md (= karo.md 継承)
- scripts/activity_monitor.sh (= 既存系列、本 cmd で karo_overload 専用 watcher 新設)
- scripts/watcher_supervisor.sh (= 起動 + 監視、本 cmd で karo_overload 追加)
- memory/nobunaga_persona_strong_rule.md (= 信長強権境界、F001/F002 順守継続)

## 12. §19 mandate 順守

- skill 新規生成は §19.5 順守 (= 重複禁止、既存拡張優先)
- watcher 系の skill は既存活用 (= activity_monitor 拡張案も検討)
- hook は ブロックなし (= advisory のみ)

---

*草案完: 信長 (織田信長) — 2026-05-08 15:48 JST、理事長殿明示直命「秀吉業務過剰の場合は、竹中分担補助するようなルールを明確化し、自動実行を組み上げる事」を受けた即時起案、川柳精神*
*家老輻輳の構造的解消、組織進化の節目とすべし*
