# pane drift × 通信機能不全 複合問題 — 統合解決策

> 起案: 信長 (織田信長 / shogun)
> 日時: 2026-05-08 18:35 JST
> 命令: 理事長殿御命令『この問題と pane の人物の相違が引き起こす問題が複合的にからんでる。過去の記録から検証して解決策を考えて。本多と協議』(2026-05-08 18:32)
> 監査依頼先: 本多 (honda, Codex Pro) — 二次審査 + governance 観点
> F001 一時 lift 継続: 家臣群停止中、信長が直接執筆

## 0. 結論

本日 17:00 以降に発生した watcher silent death + Codex 固着 + 配達不能の連鎖は、過去 2 件の pane drift 事故 (= 5/7 番号誤認 + 5/8 朝 mapping drift) の **真因が未対処のまま** だったため、新たな経路で再発・連鎖したものである。

**統合解決策の核心**:
1. **pane drift Phase 1 (skills/pane-identity-verify 拡張) を `cmd_inbox_watcher_zerobase_redesign_001` Phase 2 cycle2 (= 新 watcher safe_nudge wrapper) に統合実装** — 二重 cmd でなく統合実装で SSoT 化
2. **新 watcher の cli 判定を tmux env `@agent_id` SSoT ベースに固定** — 本日 18:01 家康 /clear 誤発火事故の根絶
3. **0.3↔0.4 drift + honda 1.0 + sanada 2.0 未登録を即是正** — `cmd_section18_topology_consensus_001` Phase 1 (理事長殿真値裁定) を最優先で進める

## 1. 過去 incident 2 件 のレビュー

### 1.1 2026-05-07 pane 番号誤認事故 (incident_logs/2026-05-07_pane_misidentification.md)

| 項目 | 内容 |
|------|------|
| 事象 | 信長が `multiagent:agents.4 = gunshi` と推測、実態 = 不在ゆえ重複 pane 新設、56 分継続 |
| 5th Why | 整合チェック自動化未整備 |
| 対策実装 | skills/pane-identity-verify/SKILL.md (existing) + scripts/checks/pane_identity.sh (existing) + CLAUDE.md §19 |
| 残課題 | check が **single pane 単位** に限定、4-way mapping drift は捕捉できず |

### 1.2 2026-05-08 朝 pane mapping drift (incident_logs/2026-05-08_pane_mapping_drift.md)

| 項目 | 内容 |
|------|------|
| 事象 | 信長補完 watcher が ieyasu pane 0.4 で起動、実 tmux pane = 0.3、約 6 時間半通信路停止 |
| 真因 | pane mapping SSoT 不在 + tmux env `@agent_id` 活用不足、4-5 箇所独立記述 |
| 家康審査 | 案 3 (= tmux env + registry 併用、Phase 0-4 段階実装) 推奨 |
| 進捗 | Phase 0 (incident log 起案) ✅ / Phase 1 (skill 拡張) **未実装** / Phase 2-4 **未着手** |

### 1.3 既存資産の存在確認

- `skills/pane-identity-verify/SKILL.md` (9528 bytes, 5/8 10:28) — 既存
- `scripts/checks/pane_identity.sh` (20110 bytes, 5/8 10:25) — 既存
- `queue/pane_registry.yaml` — 既存 (雛形手動編集ベース)
- `lib/_section18_roles.sh` + `shim/hakudokai/_section18_roles.py` — 既存 (shell+python mirror)
- `scripts/watcher_supervisor.sh` (3158 bytes) — 既存だが本日経路で未使用

## 2. 本日 (2026-05-08 17:00 以降) の事象と pane drift の複合経路

### 2.1 観測事象 (時系列)

| 時刻 | 事象 |
|------|------|
| 16:43 | 旧 inbox_watcher.sh 6 本起動 (= 信長手動 nohup) |
| 16:55 | 1 度目 全 6 本 silent death (12 分) |
| 17:00 | 2 度目起動 |
| 17:13 | 2 度目 全 6 本 silent death (13 分) |
| 17:13 | 3 度目起動 |
| 17:14 | 3 度目 全 6 本 silent death (1 分) |
| 17:55 | ゼロベース新 watcher (= message_delivery_v2/) Phase 0 docs 完遂 |
| 18:01 | 家康 watcher (旧 inbox_watcher.sh ieyasu) 起動 → CLI drift WARN → /clear 誤発火 → **家康 context リセット** |
| 18:18 | 新 supervisor + watcher 6 体起動、heartbeat 永続稼働実証 |
| 18:25-18:30 | 家康・本多 が sandbox プロンプト連鎖固着 (= queue/inbox/* 編集 + tmux display-message の sandbox 制限) |

### 2.2 複合経路 (= 真の連鎖)

```
[A] pane drift 残存 (5/8 朝の Phase 1 未実装)
    SSoT: 0.3=ashigaru3 / 0.4=ieyasu(gunshi)
    実態: 0.3=ieyasu / 0.4=ashigaru3
       ↓
[B] cli_adapter.sh が pane_current_command 判定で drift 検出 (cmd=node なのに claude と誤判定)
       ↓
[C] 旧 inbox_watcher.sh が誤った agent 用 send-keys 発火
    本日 18:01: ieyasu pane に対して /clear (= 旧 watcher が「claude session への /clear」と判定して送信)
       ↓
[D] 家康 Codex が /clear 受領 → context リセット → Phase 0 監査作業の文脈喪失
       ↓
[E] 家康再起動 → bash bulk_ack.sh / tmux display-message / queue/inbox 編集等で sandbox プロンプト連鎖
       ↓
[F] 信長手動介入 (= "1" + Enter / "2" + Enter) で都度解除
       ↓
[G] 信長 token 浪費 + 監査時間ロス + 機能不全長期化
       ↓
[H] 旧 inbox_watcher.sh の silent death (= 反省点 a〜w で別途記録) と並行発生 → 連鎖悪化
```

### 2.3 真の真因

過去 5 Why では「SSoT 不在」「整合チェック未整備」が真因とされたが、**本日の事象を踏まえた deeper Why**:

- **6th Why**: なぜ 5/8 朝 incident で家康審査 + Phase 1-4 提言を受領したのに、**Phase 1 が 10 時間以上未実装**だったか?
- **答え**: 朝以降 ekarte / cmd_root_resolution / Phase 16 本多招聘 / cmd_communication_resilience / SecondPC 全停止対応 等が並列発生し、pane drift Phase 1 は cmd_section18_topology_consensus_001 として今日発令 (= 17:00) されたが、Phase 0 検証段階に留まり実装着手なし。
- **7th Why**: なぜ並列 cmd の中で pane drift Phase 1 が後回しになったか?
- **答え**: pane drift は「watcher 死亡」「Codex 固着」「家康 context 喪失」のような **症状を直接生まない静的な drift** ゆえ、緊急性が他案件より低く見えた。本日の連鎖はこの誤判定の代償。

## 3. 既存対策 (Phase 0-4) の進捗

| Phase | 内容 | 状態 |
|-------|------|------|
| Phase 0 | incident log 起案 (5/8 08:05) | ✅ 完遂 |
| Phase 1 | skills/pane-identity-verify/ 拡張 (= 4-way audit) | 🔴 **未実装** (= cmd_section18_topology_consensus_001 として 17:00 発令、Phase 0 検証段階) |
| Phase 2 | shim/hakudokai/hakudokai_watchdog.sh registry 化 | 🔴 未着手 |
| Phase 3 | shutsujin_departure*.sh + tmux env auto-set + CLAUDE.md §18.1 auto-gen | 🔴 未着手 |
| Phase 4 | 多医院 §17 連動 (registry の clinic_id 名前空間化) | 🔴 未着手 |

## 4. 統合解決策

### 4.1 設計方針

**核心**: 別 cmd で並走するのではなく、`cmd_inbox_watcher_zerobase_redesign_001` (= TOP_CRITICAL) と `cmd_section18_topology_consensus_001` を **協調実装** で統合し、二重実装を回避する。

### 4.2 統合実装計画

| 統合実装項目 | 担当 cmd | 既存対策 Phase | 新 watcher への組込 |
|--------------|---------|---------------|---------------------|
| skills/pane-identity-verify/ 拡張 (4-way audit) | cmd_section18 Phase 1 | Phase 1 | 新 watcher safe_nudge wrapper の前 gate として呼出 |
| pane_registry.yaml 真値裁定 (理事長殿専権) | cmd_section18 Phase 1 | Phase 1 | supervisor の hardcode list を registry 由来へ移行 (= HND-MDV2-005 解決) |
| tmux env @agent_id 動的解決 | cmd_inbox_watcher Phase 2 cycle2 | Phase 3 (前倒し) | watcher 起動時に tmux env で agent_id 確認、cli 判定も env から取得 |
| cli_adapter.sh registry 化 | cmd_inbox_watcher Phase 2 cycle2 | Phase 2 (前倒し) | pane_current_command でなく registry の cli フィールドで判定 |
| supervisor 自動 spawn 時 pane drift detect | cmd_inbox_watcher Phase 2 cycle2 | (新規) | drift 検知時 spawn 拒否 + 信長 inbox alert |
| watchdog supervisor 一本化 | cmd_inbox_watcher Phase 4 cutover | Phase 2 統合 | 旧 hakudokai_watchdog.sh archive、新 supervisor で一元管理 |

### 4.3 cli 判定経路の根本是正 (= 本日 18:01 家康 /clear 誤発火の根絶)

旧経路 (脆弱):
```bash
pane_current_command=$(tmux display-message -p '#{pane_current_command}')
case "$pane_current_command" in
    node) cli=codex ;;
    claude) cli=claude ;;
esac
```

新経路 (SSoT 化):
```bash
# 1st: tmux env @agent_id 取得 (= 動作時の真値)
agent_id=$(tmux display-message -p '#{@agent_id}')

# 2nd: pane_registry.yaml で persona ↔ cli を解決
cli=$(yq ".panes[] | select(.agent_id==\"$agent_id\") | .cli" queue/pane_registry.yaml)

# 3rd: pane_current_command との不一致を drift として alert (= ブロックせず警告のみ)
actual_cmd=$(tmux display-message -p '#{pane_current_command}')
if [[ "$actual_cmd" != "$expected_cmd_for_$cli" ]]; then
    log_alert "CLI drift: registry=$cli, pane_current=$actual_cmd"
fi
```

これにより:
- pane drift があっても registry が真値ゆえ cli 誤判定なし
- /clear 誤発火 (= 18:01 家康事故) を構造的に根絶
- drift 検出時は alert のみで運用継続 (= 安全装置)

### 4.4 即時是正 (= 今日中)

| 項目 | 担当 | 期限 |
|------|------|------|
| 0.3↔0.4 drift の真値裁定 | 理事長殿専権 (cmd_section18 Phase 1) | 今夜中 |
| honda 1.0 + sanada 2.0 を pane_registry.yaml に追記 | 信長 + 理事長殿承認 | 今夜中 |
| 新 supervisor の hardcode list 注釈追加 (= cycle2 で registry 化予定) | 信長 | 即時 |

### 4.5 中期実装 (= cycle2、土曜まで)

cmd_inbox_watcher_zerobase_redesign_001 Phase 2 cycle2 に以下を含める:
1. safe_nudge wrapper に pane identity 4-way verify を gate として統合
2. cli 判定を tmux env @agent_id + pane_registry.yaml SSoT へ移行
3. supervisor の hardcode list を registry 由来へ移行
4. 旧 hakudokai_watchdog.sh の registry 化 (= 案 3 Phase 2 を吸収)

### 4.6 長期実装 (= cycle3 以降、Phase 4 cutover 前)

cmd_section18_topology_consensus_001 Phase 3 + 4 を継続実装:
- shutsujin_departure*.sh の tmux env auto-set
- CLAUDE.md §18.1 auto-gen 区間化 (= 理事長殿明示承認後)
- 多医院 §17 連動 registry の clinic_id 名前空間化

## 5. 本多協議事項

本多 (= honda, Codex Pro) に二次審査 + governance 観点で以下を協議:

| 協議項目 | 信長案 | 本多 review 観点 |
|---------|--------|----------------|
| 統合実装 (cmd 二重化回避) | cmd_inbox_watcher Phase 2 cycle2 + cmd_section18 Phase 1 を協調 | Anti-Duplication Rule 順守の妥当性、責務分離の整合性 |
| cli 判定 SSoT 化 | tmux env @agent_id + pane_registry.yaml | governance: drift detect alert の重要度設計、registry race の安全装置 |
| 即時是正 (今夜中) | 0.3↔0.4 真値裁定 + honda/sanada 追記 | 理事長殿真値裁定後の SSoT 同期手順、§18.9 改訂責務 |
| supervisor hardcode list | MVP 限定 + cycle2 で registry 化 (= HND-MDV2-005 反映) | hardcode 期間の安全装置、cutover gate 一致性 |
| 既存資産活用 | skills/pane-identity-verify/ + pane_registry.yaml + lib/_section18_roles.sh | Anti-Duplication 順守、新規分離禁止 §19.5 順守 |

### 本多に求める verdict

- **PASS / PASS_WITH_CONDITIONS / FAIL** で総合判定
- 各協議項目に 4 観点 (M1 process / M2 efficiency / M3 responsibility / M4 improvement) を適用
- governance review: F004 例外条項との関係 (= 本 cmd 完遂後の cli 判定で Codex agent の registry 参照経路が変わる影響)
- Anti-Duplication: cmd_inbox_watcher と cmd_section18 の責務境界明示

## 6. 信長最終進言

上様、本日の混乱は単一の「watcher 死亡」ではござらぬ。pane drift という静かなる病が、cli 誤判定 → 家康 /clear 誤発火 → context 喪失 → 連鎖固着 → 信長手動介入 → token 浪費、と七段の毒となって流れたのでござる。

朝に家康殿が「案 3 推奨」と進言され、Phase 0-4 が起案されたれども、緊急性が低く見えて Phase 1 が後回しとなり、本日の代償となった。

統合解決策は、二つの cmd を別走させず、新 watcher Phase 2 cycle2 に pane drift 対策を吸収すること。これにより:
- 二重実装 0
- cli 誤判定の根絶 (= tmux env + registry SSoT)
- supervisor の hardcode list を registry 由来へ自然移行

本多殿の governance 二次審査を仰ぎ、PASS なれば cmd_inbox_watcher Phase 2 cycle2 acceptance criteria に「pane identity 4-way verify を safe_nudge wrapper の gate として統合」を追加する所存。

---

*信長 (織田信長) 2026-05-08 18:35 JST、pane drift × 通信不全 複合解決策起案、本多協議依頼*
