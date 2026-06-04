# §18. PC × アカウント × エージェント配置ルール

**原則: PC ごとに別アカウントを使い、quota を完全分離する。1アカウントに大量エージェントを集めると quota 共食いで暴走する。**

出典: CLAUDE.md (元 §18) からの移設実体 (副院長令 7de922ec 裁定 X-1+X-4、2026-06-04 Commander)。改訂責務は理事長殿の専権事項。

## 背景 (なぜこのルールが必要か)

過去事故 — 2026-05-05 SecondPC 暴走事件 (26分38%):
- SecondPC で信長配下のエージェント (家老・家康・足軽群) をすべて SecondPC ローカルアカウントで起動
- 1アカウント × 10エージェント並列で quota 共食い
- 26分で月間 quota の 38% を消費 → API 暴走 → 容量オーバーで停止
- 根本原因: アカウント分離の不徹底
- 詳細: [docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md](../incident_logs/2026-05-05_secondpc_consumption_anomaly.md)

この事故を恒久対策するため、**PC × アカウント × エージェントの対応関係を本ルールで明文化** する。

## §18.1 配置表 (恒久ルール)

### MainPC (sasebo@sasebo.or.jp / Claude Max 20x)

| 区分 | エージェント | tmux pane |
|------|------------|-----------|
| **通常運用 (5体)** | 信長 (shogun) | shogun:0.0 |
|  | 家老 (karo) | multiagent:0.0 |
|  | 家康 (gunshi) | multiagent:0.4 |
|  | 足軽1 (ashigaru1) | multiagent:0.1 |
|  | 足軽2 (ashigaru2) | multiagent:0.2 |
| **非常時 (+1体)** | 足軽3 (ashigaru3) | multiagent:0.3 |

**MainPC 上限: 通常 5体 / 非常時 6体**

### SecondPC (hakudoukai@gmail.com / Claude Max 20x)

| 区分 | エージェント | tmux pane |
|------|------------|-----------|
| **通常運用 (3体)** | 足軽5 (ashigaru5) | multiagent:0.0 |
|  | 足軽6 (ashigaru6) | multiagent:0.1 |
|  | 足軽7 (ashigaru7) | multiagent:0.2 |
| **非常時 (+1体)** | 足軽8 (ashigaru8) | multiagent:0.3 |

**SecondPC 上限: 通常 3体 / 非常時 4体**

### 番号体系の原則

- **足軽1〜3**: MainPC 専属 (sasebo@sasebo.or.jp)
- **足軽4**: **欠番** (PC 境界の視覚的区切り)
- **足軽5〜8**: SecondPC 専属 (hakudoukai@gmail.com)
- **信長・家老・家康**: MainPC 専属 (指揮系統を1つに集約、SecondPC で起動禁止)

## §18.2 厳守事項 (Tier 1 ABSOLUTE)

| ID | 禁止事項 | 違反時の影響 |
|----|---------|-------------|
| A001 | MainPC で `hakudoukai@gmail.com` にログイン | quota 混在、配置追跡不能 |
| A002 | SecondPC で `sasebo@sasebo.or.jp` にログイン | 同上 |
| A003 | SecondPC で 信長/家老/家康 を起動 | 指揮系統分裂、過去事故再発 |
| A004 | MainPC で 足軽5/6/7/8 を起動 | 配置混乱、quota 暴走 |
| A005 | 1 PC で通常上限 + 非常時上限を超えて起動 | quota 共食い、暴走 |
| A006 | アカウント切替を無断で実行 | 監査不能 |

違反検知時は **即座に該当エージェントを `/exit`** し、本ルール準拠で再起動。

## §18.3 起動前チェック (義務)

各エージェント起動前に必ず実行:

```bash
# Step 1: アカウント確認 (~/.claude/.credentials.json)
jq -r '.claudeAiOauth.subscriptionType, .claudeAiOauth.rateLimitTier' ~/.claude/.credentials.json
# 期待: max / default_claude_max_20x

# Step 2: claude --version
claude --version

# Step 3: claude 起動後に /status コマンドで email 確認
/status
# MainPC 期待: Account: sasebo@sasebo.or.jp Claude Max 20x
# SecondPC 期待: Account: hakudoukai@gmail.com Claude Max 20x
```

不一致時は起動中止。`claude logout` → `claude login` で正しいアカウントへ切替。

## §18.4 quota 監視

各 PC で日次累積消費を /usage で確認:

| PC | 通常時の上限 | 12時の警戒ライン | 警戒時の対応 |
|----|------------|----------------|------------|
| MainPC (5-6体) | Claude Max 20x | 50% | 足軽3 を停止し通常 5体 に絞る |
| SecondPC (3-4体) | Claude Max 20x | 50% | 足軽8 を停止し通常 3体 に絞る |

50% 超過時は信長へ即報告 (dashboard.md + ntfy)。

## §18.5 クロス PC 通信

MainPC ↔ SecondPC のエージェント間通信は以下の経路のみ許容:

1. **Supabase pc_handshake** (推奨): 認証不要、堅牢、retry/dedupe 標準対応
2. **SSH (Tailscale または LAN)**: 緊急時のみ、SSH key 認証

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
ssh hakudokai@192.168.11.47
cd /home/hakudokai/projects/multi-agent-shogun
./shutsujin_departure_secondpc.sh   # 足軽5/6/7 を tmux で起動
```

(SecondPC 起動スクリプトは Phase B 整備項目)

## §18.7 違反時の即時対応

- 違反検知 → 該当エージェントを `/exit` → アカウント確認 → 正しい配置で再起動
- 再発時は dashboard.md に記録し、信長が原因究明
- 月次で違反履歴を理事長殿へ報告

## §18.8 関連ルール

- §17 他院展開時もこの配置原則を踏襲 (各医院 = 1 アカウント, HQ 信長 = 別アカウント)
- §16 トラブル自動応答パイプライン (アカウント quota 異常時の自動アラート)
- 過去事故 [docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md](../incident_logs/2026-05-05_secondpc_consumption_anomaly.md)
- FKI memory: FKI-OPERATIONAL-MANUAL-FIRST-01, FKI-RECIPIENT-RULE-01

## §18.9 改訂責務

本ルールの改訂は **理事長殿の専権事項**。信長・家老・家康は提案のみ可。
変更時は本セクション + 関連 docs ([docs/restart-and-mcp.md](../restart-and-mcp.md)) + memory (`account_pc_allocation.md`) を同時に更新する。
