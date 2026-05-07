# Incident Log: pane mapping drift (認識ミス) 2026-05-08

## 概要

| 項目 | 値 |
|------|----|
| 発生時刻 | 2026-05-08 01:10 JST (= 信長補完 watcher 起動時) |
| 検知時刻 | 2026-05-08 07:36 JST (= 朝の戦果報告 self-audit) |
| 修正完了 (応急) | 2026-05-08 07:45 JST (= ieyasu watcher を pane 0.3 で再起動) |
| 影響継続 | 約 6 時間半 (= 夜討ち時間) |
| 重要度 | ERROR (= 三者監査経路停止、夜討ち失敗の主因) |
| エラーコード候補 | ERR-PANE-002 (ERR-PANE-001 = 既往 2026-05-07) |
| 検知者 | 信長 (= 朝の戦果報告 self-audit) |
| 修正者 (応急) | 信長 (= ieyasu watcher を pane 0.3 で再起動) |
| 軍師審査 | 家康 8 観点審査完遂、案 3 推奨判定 (msg_20260508_075934_7cee9b09) |

## 影響

### 通信路停止
家康 (= ieyasu) inbox 5 unread 滞留:
- ashigaru1 Phase 6 cycle2 fix 三者監査依頼 (秀吉発、re-audit)
- ashigaru2 v2 cycle2 re-audit 依頼
- その他 cycle 進捗報告複数

### 業務阻害
- 三者監査回路 完全停止 (= 家康 nudge 不発)
- 朝までの撃破目標 5 件中、達成 1 件 (ashigaru2 v2 PASS) のみ
- 4 件未着手:
  - ashigaru1 Phase 6 cycle2 三者監査 (= 別件 commit 不在問題と cascade で更に阻害)
  - SecondPC 軍 (前田 + ashigaru5/6/7) 初陣全失敗
  - cmd_phase4 close 通知未完
  - §19 残 6 件 manual review 未着手

### 信長補完 watcher の早期死亡
- 01:22-01:25 起動の 6 体 watcher (= nobunaga/hideyoshi/ashigaru1/ashigaru2/ashigaru3/ieyasu) 全て死亡
- watchdog (= 旧名対応のみ) が新名 watcher を生死監視せず、自動復活なし

## 5 Why 分析

| # | 質問 | 答え |
|---|------|------|
| 1 | なぜ pane mapping 誤認? | 信長が CLAUDE.md §18.1 を信じて pane 0.4 で ieyasu watcher 起動、実 tmux pane = 0.3 |
| 2 | なぜ CLAUDE.md と実 tmux が乖離? | CLAUDE.md §18.1 表が「軍師=0.4」と記述、shutsujin_departure.sh で実態 0.3 に配置 (= 設計 doc と実装 script の drift) |
| 3 | なぜ drift が放置? | pane mapping を 4-5 箇所 (CLAUDE.md §18.1 / instructions/{nobunaga,hideyoshi,ieyasu,maeda}.md / hakudokai_watchdog.sh INBOX_AGENTS / lib/_section18_roles.sh / shutsujin_departure*.sh) で独立記述、Single Source of Truth (SSoT) 不在 |
| 4 | なぜ SSoT 不在? | 設計時に「人手 doc + script hardcode」の二重管理を採用、tmux env `@agent_id` を SSoT として活用しなかった |
| 5 | なぜ tmux env を活用しなかった? | shutsujin_departure*.sh で env 設定 (`tmux set -p @agent_id <name>`) は実施したが、watcher / watchdog / scripts 側に env 動的読込ロジックを組まず、「設定したが使わなかった」状態 |

## 根本原因 (root cause)

**Pane mapping の Single Source of Truth 不在 + tmux env `@agent_id` の活用不足**:
- runtime SSoT (= tmux env、動作時の真値) 未活用
- persistent SSoT (= queue/pane_registry.yaml 等) 未存在
- 結果: 4-5 箇所の独立記述が drift 不可避、人間の認知ミスが事故化

## 既往の同型事故

- 2026-05-07 pane 番号誤認事故 = skills/pane-identity-verify/SKILL.md に記録、対策スキル + check スクリプト整備済
- 本日 (2026-05-08) は別 pattern で再発 = 既存 skill の検出範囲が「pane 番号 vs @agent_id」の単 pane 単位に限定、4-way mapping drift を捕捉できず

## 家康 8 観点審査結果 (= msg_20260508_075934_7cee9b09 抜粋)

### 推奨案: 案 3 (= tmux env + registry 併用、Phase 0-4 段階実装)

8 観点評価:

| 観点 | 案 1 (env のみ) | 案 2 (registry のみ) | **案 3 (併用)** | 案 4 (watchdog のみ) | 案 5 (audit skill のみ) |
|------|---|---|---|---|---|
| 仕様準拠 | ◎ | ◎ | **◎** | ○ | △ |
| 網羅性 | △ | ○ | **◎** | △ | △ |
| ドキュメント | ○ | ○ | **◎** | △ | △ |
| UX | ◎ | ○ | **◎** | ○ | △ |
| system_relations | ◎ | ○ | **◎** | △ | △ |
| side_effects | ○ | ○ | ○ | ◎ | ◎ |
| observability | ◎ | ○ | **◎** | △ | ◎ |

採用根拠:
- runtime SSoT (tmux `@agent_id` env) で **動作時の真値が常に正解**、虚空 nudge を構造的に根絶
- persistent SSoT (queue/pane_registry.yaml) で **起動失敗時の audit base + fallback** を担保
- §18.1 表 auto-gen 化で 4-5 箇所 hardcode drift を恒久排除

### 家康追加 risk (= 7 件、設計時必ず織り込む)

1. **registry YAML race**: shutsujin 書込中の watcher 読込で inconsistent state → `flock` 必須
2. **registry vs tmux env drift**: registry 更新後 env 反映漏れ → 案 5 (4-way audit) で必ず検出
3. **多医院 §17 配信問題**: HQ ↔ 医院 PC で registry 同期問題 → clinic_id 接頭辞で名前空間分離 (Phase 4)
4. **watcher 自動再起動 §15 SH6 危険パターン回避**: registry 更新中は手動停止フラグ尊重 (`~/.openclaw/registry_updating` 等)
5. **CLAUDE.md auto-gen blast radius**: §18.1 表は理事長殿が読む人手 doc。`<!-- AUTOGEN BEGIN/END -->` マーカーで分離必須、auto-gen 区間外は理事長殿専権編集
6. **tmux pane renumber 追従**: kill/respawn で pane 番号振替 → @agent_id env が pane 紐付き、renumber 追従検証必須 (Phase 1 試験項目)
7. **§19 重複生成禁止**: 案 5 を新規 skill 化すると `skills/pane-identity-verify/` と重複 → **既存拡張一択** (CLAUDE.md §19.5 順守)

### 家康改修順序: watchdog → shutsujin

(1) Phase 2 watchdog.sh 先行: INBOX_AGENTS hardcode 撤廃 → registry 読込化。読み取り専用ゆえ safety 高、即効性あり
(2) Phase 3 shutsujin_departure.sh 後行: pane 起動責務 + registry 書き込み + tmux env 設定の三重責務、影響大。Phase 2 動作確証後に書き込み側改修

## 対策方針 (= 信長 + 家康 合意)

### Phase 0 (= 即時、本ファイル) — 信長直筆完遂
本 incident log 起案 (5 Why + 真因 + 家康審査 + 対策)、§19 mandate 順守

### Phase 1 (= 1-2 日) — Phase 1 cmd で発令
`skills/pane-identity-verify/` **既存拡張** (新規分離禁止、§19.5):
- 従来 check: pane 番号誤認 (single pane 単位)
- 拡張 check: **4-way mapping 整合性**:
  1. tmux 実態 (= `list-panes -F '#{@agent_id}:#{session}:#{window}.#{pane}'`)
  2. queue/pane_registry.yaml (= persistent SSoT、Phase 2 で雛形手動編集ベース運用開始)
  3. shim/hakudokai/hakudokai_watchdog.sh INBOX_AGENTS
  4. CLAUDE.md §18.1 表
- advisory hook 化 (PreToolUse、`|| true` 必須、絶対ブロック禁止)
- timeout 5 秒上限、stderr 警告のみ、exit 1 予約

### Phase 2 (= 3-5 日) — 別 cmd
`shim/hakudokai/hakudokai_watchdog.sh` 改修:
- INBOX_AGENTS hardcode 撤廃 → `queue/pane_registry.yaml` 読込化
- 旧名 (karo/gunshi) 廃止 → 新名 (hideyoshi/ieyasu) 対応
- 不在 pane (= multiagent:0.8) 廃止
- 新名 ashigaru2/3/maeda 監視対象追加
- registry race 対策 = `flock` (= 家康 risk 1 対応)
- 手動停止フラグ尊重 (= 家康 risk 4 対応)

### Phase 3 (= 1-2 週間) — 別 cmd
`shutsujin_departure.sh` + `shutsujin_departure_secondpc.sh` 改修:
- pane 起動時に `tmux set -p @agent_id <name>` 確実実施
- `queue/pane_registry.yaml` auto-generate
- watcher / watchdog / scripts を tmux env @agent_id 動的解決ベースに移行
- CLAUDE.md §18.1 表を auto-gen 区間化 (= 家康 risk 5 対応、理事長殿明示承認後)
- tmux pane renumber 追従検証 (= 家康 risk 6 対応)

### Phase 4 (= 1 ヶ月、§17 連動) — 別 cmd
多医院展開準備:
- registry の clinic_id 名前空間化 (= 家康 risk 3 対応)
- HQ ↔ 医院 PC 同期方式設計

## 検出方法 (= 自動化)

### scripts/checks/pane_identity.sh 拡張 (= 既存、Phase 1 で実装)

4-way audit ロジック:
```bash
# 1. tmux 実態取得
tmux_panes=$(tmux list-panes -a -F '#{@agent_id}:#{session_name}:#{window_index}.#{pane_index}')

# 2. registry 読込
registry=$(yq '.panes' queue/pane_registry.yaml 2>/dev/null)

# 3. watchdog INBOX_AGENTS 解析
watchdog_agents=$(grep -oE 'INBOX_AGENTS=".*"' shim/hakudokai/hakudokai_watchdog.sh)

# 4. CLAUDE.md §18.1 表 解析
claude_table=$(awk '/§18.1/,/^## /' CLAUDE.md | grep -oE '\| [a-z_]+ \| (multiagent|shogun):[0-9]+\.[0-9]+ \|')

# 5. 4-way 整合性確認、drift 検出時 stderr WARN
```

### PreToolUse hook 候補

`scripts/inbox_watcher.sh` / `scripts/inbox_write.sh` 実行前に `pane_identity.sh` を advisory check:
```json
{
  "matcher": "Bash",
  "command_pattern": "scripts/inbox_(watcher|write)\\.sh",
  "command": "bash scripts/checks/pane_identity.sh || true"
}
```

## 再発防止 (= Boy Scout Rule §14)

新機能追加時、関連 pane mapping 記述箇所も整備対象:
- CLAUDE.md §18.1 編集時、auto-gen 区間遵守
- shutsujin_departure*.sh 編集時、registry 同期
- watchdog.sh 編集時、INBOX_AGENTS 廃止チェック

## 関連資産

- `skills/pane-identity-verify/SKILL.md` (= 既存 §19 skill、Phase 1 拡張対象)
- `scripts/checks/pane_identity.sh` (= 既存、Phase 1 拡張対象)
- `shim/hakudokai/hakudokai_watchdog.sh` (= Phase 2 改修対象)
- `shutsujin_departure.sh` + `shutsujin_departure_secondpc.sh` (= Phase 3 改修対象)
- `CLAUDE.md §18.1` (= 理事長殿専権、Phase 3 で auto-gen 区間化検討)
- `queue/pane_registry.yaml` (= Phase 2 で新設、雛形手動編集ベース)
- `lib/_section18_roles.sh` + `shim/hakudokai/_section18_roles.py` (= Phase 3 で registry 経由に統一)

## §19 mandate 順守

- 本 incident log = §19.1-19.4 即時起案 mandate により commit (= 理事長殿事後承認可)
- skill 拡張 (= Phase 1) commit は理事長殿明示承認後 (= §19.5)
- skill **新規生成禁止** (= 既存 skills/pane-identity-verify/ 拡張一択、§19.5 + Anti-Duplication)

## §15 self-healing pattern 適用

| pattern | 該当箇所 | 安全装置 |
|---------|---------|---------|
| SH3 (fallback) | registry 不在時、tmux env を fallback として優先使用 | retry cap 3、fallback 復旧後の同期 |
| SH4 (stale lock) | registry.yaml.lock 30 分以上残存時の自動解除 | lock holder ヘルスチェック必須 |
| SH6 (self-restart) | watcher 死亡検知時の再起動 | **手動停止フラグ尊重 + 再起動上限 5/h + escalation** (= 本朝事故再発防止の核心) |

## 信長 + 家康 合意事項

- 案 3 (= tmux env + registry 併用) を採用
- skills/pane-identity-verify/ 既存拡張 (= 新規分離禁止)
- watchdog → shutsujin の順
- Phase 0 本ファイル → Phase 1-4 順次別 cmd 発令
- 各 Phase 別 cmd 発令、家老 (秀吉) が分解 + 足軽 dispatch
- 三者監査全 PASS 必須

## 信長案 監査階層変更との関係 (= 別 cmd、後続)

理事長殿 (2026-05-08 朝) 御命令: 監査階層を Codex メイン (家康) + Gemini セカンド (服部半蔵 等、徳川軍家臣) + Claude 議長 (黒田官兵衛 等、信長家中) に変更。但し **pane mapping 解決を優先**、監査階層変更は本対策完遂後に別 cmd で発令。

---
*記録: 信長 (織田信長) — 2026-05-08 08:05 JST、家康 8 観点審査回答受領後*
