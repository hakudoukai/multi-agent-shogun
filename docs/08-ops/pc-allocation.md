# §18. Claude/ChatGPT アカウント運用ルール (ccflare 正本 v3.8 整合)

**【枠の真実】Claude(Anthropic Max)の実体契約は 2 つだけ (sasebo系 / hakudoukai系)。各 PC の ccflare が両契約を集中管理し priority + auto-fallback で分配・共有する。「PC ごと別アカウント完全分離」=ccflare 導入前の旧モデルで誤り (v3.8、2026-06-04 理事長令確定)。ChatGPT 系 (codex/Hermes) のみ 1PC/1プロセス/1契約厳守 (v3.7)。**

出典: CLAUDE.md (元 §18) からの移設実体 (副院長令 7de922ec X-1+X-4 裁定 2026-06-04 Commander 移設) + 副院長令 695293a5 によりccflare 正本 v3.8 整合書換 (2026-06-04)。改訂責務は理事長殿の専権事項。**実 ccflare 設定 (account/priority/fallback/経路) の変更は DD-164 副院長承認必須・本書は文言整合のみ**。

## 背景 (なぜこのルールが必要か)

過去事故 — 2026-05-05 SecondPC 暴走事件 (26分38%):
- SecondPC で多数エージェントを 1 PC に集約稼働
- 26分で月間 quota の 38% を消費 → API 暴走 → 容量オーバーで停止
- 詳細: [docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md](../incident_logs/2026-05-05_secondpc_consumption_anomaly.md)

**防止策の真因 (v3.8 整合)**:
- (a) ccflare の priority + auto-fallback による枠分配 (Claude 側)
- (b) 1PC / 1pane への負荷集中禁止
- (c) account 追加 / priority / fallback / 経路変更は副院長承認必須 (DD-164)
- (d) 状態は verify のみ可

★旧記述「アカウント分離の不徹底が根本原因」は誤り (v3.8 訂正)。Claude 側に「別アカウント分離」は当てはまらず、ccflare 集中管理が現行の正である。事故防止は集中管理 + 負荷分散 + 副院長承認制で達成する。★

## §18.1 配置表 (恒久ルール)

★アカウント列は ccflare 経由 (両 PC とも 2 契約共有)、PC 専属の email 1:1 割当ではない (v3.8)。★

### MainPC (ccflare :8080 / Claude 2 契約集中管理: sasebo系+hakudoukai系)

| 区分 | エージェント | tmux pane |
|------|------------|-----------|
| **通常運用 (5体)** | 信長 (shogun) | shogun:0.0 |
|  | 家老 (karo) | multiagent:0.0 |
|  | 家康 (gunshi) | multiagent:0.4 |
|  | 足軽1 (ashigaru1) | multiagent:0.1 |
|  | 足軽2 (ashigaru2) | multiagent:0.2 |
| **非常時 (+1体)** | 足軽3 (ashigaru3) | multiagent:0.3 |

**MainPC 上限: 通常 5体 / 非常時 6体**

### SecondPC (ccflare :8081 / Claude 2 契約集中管理: sasebo系+hakudoukai系)

| 区分 | エージェント | tmux pane |
|------|------------|-----------|
| **通常運用 (3体)** | 足軽5 (ashigaru5) | multiagent:0.0 |
|  | 足軽6 (ashigaru6) | multiagent:0.1 |
|  | 足軽7 (ashigaru7) | multiagent:0.2 |
| **非常時 (+1体)** | 足軽8 (ashigaru8) | multiagent:0.3 |

**SecondPC 上限: 通常 3体 / 非常時 4体**

### ThirdPC (ccflare :8080 / Claude 2 契約集中管理: sasebo系+hakudoukai系、v3.3 で 8082 単一→8080 2契約化)

Commander (third) 配備。詳細 = ccflare 正本 v3.4 実機 verify (sasebo-3 + hakudoukai-3)。

### 番号体系の原則

- **足軽1〜3**: MainPC 配備 (ccflare :8080 経由で 2 契約共有)
- **足軽4**: **欠番** (PC 境界の視覚的区切り)
- **足軽5〜8**: SecondPC 配備 (ccflare :8081 経由で 2 契約共有)
- **信長・家老・家康**: MainPC 配備 (指揮系統を 1 PC に集約、SecondPC で起動禁止)

## §18.2 厳守事項

### A001-A006 再分類 (v3.8 整合)

| ID | 旧記述 | v3.8 整合判定 |
|----|--------|--------------|
| A001 | MainPC で hakudoukai@gmail.com にログイン禁 | **★旧モデル (廃止)★** ccflare 経由で両契約共有が現行。直接ログインで分離する運用ではない。 |
| A002 | SecondPC で sasebo@sasebo.or.jp にログイン禁 | **★旧モデル (廃止)★** 同上。両 PC とも ccflare 経由で 2 契約共有。 |
| A003 | SecondPC で 信長/家老/家康 を起動 | **有効** 指揮系統分裂防止のため (アカウントとは別の規律)。 |
| A004 | MainPC で 足軽 5/6/7/8 を起動 | **有効** 配置混乱防止のため (アカウントとは別の規律)。 |
| A005 | 1 PC で通常上限 + 非常時上限を超えて起動 | **有効** 1PC/pane への負荷集中禁が ccflare 防止策の核。 |
| A006 | アカウント切替を無断で実行 | **有効・強化** account/priority/fallback/経路変更は DD-164 副院長承認必須。 |

★A001/A002 は ccflare 導入前の旧モデル記述ゆえ Tier 1 ABSOLUTE 断定を廃止する。A003-A006 は配置/負荷集中/承認制の規律として有効★。

違反検知時の対応は §18.7 参照。

## §18.3 起動前チェック (義務)

各エージェント起動前に必ず実行 (ccflare v3.8 整合):

```bash
# Step 1: ccflare 接続性確認
curl -s http://localhost:8080/api/stats | jq '.accounts | length'
# MainPC / ThirdPC 期待: 2 (sasebo系 + hakudoukai系)
curl -s http://localhost:8081/api/stats | jq '.accounts | length'
# SecondPC 期待: 2 (sasebo系 + hakudoukai系)

# Step 2: claude --version
claude --version

# Step 3: ANTHROPIC_BASE_URL が ccflare endpoint を指しているか確認
echo $ANTHROPIC_BASE_URL
# MainPC / ThirdPC 期待: http://localhost:8080
# SecondPC 期待: http://localhost:8081
```

不一致時は起動中止。**直接 claude login で OAuth 再認証する場合は DD-164 副院長承認必須** (ccflare 集中 refresh の R14 競合回避を破壊するリスクがあるため)。

## §18.4 quota 監視

各 PC で ccflare /api/stats と /usage で消費を確認:

| PC | endpoint | 通常時の上限 | 警戒ライン | 警戒時の対応 |
|----|----------|------------|----------|------------|
| MainPC (5-6体) | :8080 | ccflare 経由 2 契約共有 | 12時 50% | 足軽3 を停止し通常 5体 に絞る |
| SecondPC (3-4体) | :8081 | ccflare 経由 2 契約共有 | 12時 50% | 足軽8 を停止し通常 3体 に絞る |
| ThirdPC (Commander) | :8080 | ccflare 経由 2 契約共有 | 50% | 副院長へ報告 |

50% 超過時は信長へ即報告 (dashboard.md + ntfy)。実 ccflare 設定の priority/fallback 変更は **DD-164 副院長承認必須** (本書では監視のみ可)。

## §18.5 クロス PC 通信

MainPC ↔ SecondPC ↔ ThirdPC のエージェント間通信は以下の経路のみ許容:

1. **Supabase pc_handshake** (推奨): 認証不要、堅牢、retry/dedupe 標準対応
2. **SSH (ProxyJump 経由)**: 緊急時、SSH key 認証 (DD-176/DD-177 + ALL-SSH-NO-NEW-ENDPOINT-01 順守)

**エージェント本体の PC 越境起動は禁止**。タスク発令はメッセージ経由のみ。

## §18.6 起動順序 (recommended)

### MainPC 朝の起動 (5体)

```bash
cd /mnt/c/Users/User/projects/multi-agent-shogun
./shutsujin_departure.sh        # tmux session + 5 panes 自動起動
# 各ペインで claude --resume (信長は cd 先で対話再開)
```

### SecondPC 朝の起動 (3体)

```bash
# MainPC から SSH 経由で起動指示
ssh -i ~/.ssh/daishogun_cef2002e5d -p 2223 hakudokai@192.168.11.47
cd /home/hakudokai/projects/multi-agent-shogun
./shutsujin_departure_secondpc.sh   # 足軽5/6/7 を tmux で起動
```

### ThirdPC (Commander) の起動

Commander 配備。SSH は third → main/second の ProxyJump 経由 (ALL-SSH-NO-NEW-ENDPOINT-01 順守)。

## §18.7 違反時の即時対応

- 違反検知 → 該当エージェントを `/exit` → 配置確認 → 正しい配置で再起動
- account/priority/fallback/経路変更を伴う場合は ★副院長殿に承認申請 (DD-164)★、Commander 以下が自走で実施するのは禁止
- 再発時は dashboard.md に記録し、信長が原因究明
- 月次で違反履歴を理事長殿へ報告

## §18.8 関連ルール

- **ccflare 正本 v3.8**: `project_documents id=59a1b69b-5421-40a5-b1b0-92307fa50449` (Claude 2 契約集中管理 + ChatGPT 1 契約分離 が確定された最上位の正)
- **v3.7 FKI-ENGINE-ONE-AUTH-PER-PC-01**: ChatGPT 系 (codex/Hermes) は 1PC/1プロセス/1契約厳守
- **v3.6 R14 機構**: ccflare 集中 refresh で competing refresh 競合回避
- §17 他院展開時もこの ccflare 集中管理原則を踏襲
- §16 トラブル自動応答パイプライン (quota 異常時の自動アラート)
- 過去事故 [docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md](../incident_logs/2026-05-05_secondpc_consumption_anomaly.md)
- FKI memory: FKI-OPERATIONAL-MANUAL-FIRST-01, FKI-RECIPIENT-RULE-01, FKI-CANON-GUARDIAN-01

## §18.9 改訂責務

本ルールの改訂は **理事長殿の専権事項**。信長・家老・家康・Commander は提案のみ可。
変更時は本セクション + 関連 docs ([docs/restart-and-mcp.md](../restart-and-mcp.md)) + memory (`account_pc_allocation.md`) + ccflare 正本 (project_documents 59a1b69b) を同時に更新する。
**実 ccflare 設定 (account/priority/fallback/経路) の変更は DD-164 副院長承認必須**。文言整合と実機操作を混同するな。
