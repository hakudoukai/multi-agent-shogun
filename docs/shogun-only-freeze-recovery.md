# 将軍だけが落ちた時の再起動手順書

**対象読者**: 理事長殿 / 副医院長(Desktop+CLI) / クロちゃん家老 / 全エージェント
**作成**: 2026-05-05
**目的**: 将軍 (shogun pane) が単独でフリーズし、他のメンバー(家老・軍師・足軽1-8)は生きている状態で、将軍だけを安全に再起動する手順を明確化する。

---

## 📌 まず読むべき判定フロー

```
[何かおかしい]
    ↓
[将軍からの応答なし、handshake 30分以上届かない]
    ↓
[副医院長 SQL で診断 → §1.2]
    ├─ 他agentは生きている?
    │     ├─ YES → 将軍だけ落ちた  ← 本書の対象
    │     └─ NO  → 全停止 → docs/restart-and-mcp.md §0/§9
    │
    └─ ※ ntfy 通知も途絶えている? → §1.3
```

---

## 1. 「将軍だけが死んだ」と判定する方法

### 1.1 副医院長/クロちゃんから見える症状

- `pc_handshake` を main_pc 宛で送っても5分以上応答なし
- ただし 他agent (karo / ashigaru / gunshi) からの handshake INSERT は流れている
- ntfy 通知が「将軍由来のもの」だけ途絶える (file_sync_*, status_complete などはまだ流れている可能性)

### 1.2 副医院長による物理 SELECT 診断 (Supabase MCP 経由)

```sql
-- 過去30分の各 from_pc ごとの最終 INSERT 時刻
SELECT from_pc,
       MAX(created_at) AS last_insert,
       COUNT(*) AS n
FROM pc_handshake
WHERE created_at > NOW() - INTERVAL '30 minutes'
  AND topic NOT ILIKE '%heartbeat%'
GROUP BY from_pc
ORDER BY last_insert DESC;
```

判定:
- `main_pc` の last_insert が他より古い (例: 30分以上前) → 将軍が落ちている疑い濃厚
- `second_pc` が動いている → SecondPC は健在
- 全部古い → 全停止 (本書対象外、docs/restart-and-mcp.md §9 へ)

### 1.3 ntfy 経由のクロスチェック

副医院長 (Claude.ai Desktop) が ntfy アプリで:
- 将軍からの最新通知が30分以上前 → 落ちた疑い
- ただし `hakudokai-heartbeat.service` が systemd で動いていれば、heartbeat は別経路で流れる場合がある

---

## 2. 将軍だけ再起動する手順 (理事長殿 or MainPC物理アクセス可能な人)

### 前提
- MainPC は WSL2 (Ubuntu) + tmux で稼働中
- 将軍は `tmux:shogun:0.0` ペインで動いている
- 他のエージェント (家老/軍師/足軽1-7) は `tmux:multiagent:0.0〜0.8` で稼働中
- watchers は systemd (`hakudokai-departure.service` / `hakudokai-heartbeat.service`) で稼働中

### Step 1: 状況確認 (壊さない前にまず見る)

WSLターミナル(または Windows Terminal の Ubuntu) を開いて:

```bash
# 全Claudeプロセス確認
ps aux | grep claude | grep -v grep

# tmuxセッション一覧 (shogun と multiagent の2セッション必須)
tmux ls

# 各ペインの@agent_id確認
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} agent=#{@agent_id}'

# watcher稼働確認
systemctl --user status hakudokai-departure | head -5
systemctl --user status hakudokai-heartbeat | head -5
```

期待される状態:
- `tmux ls` で `shogun` と `multiagent` の2つが見える
- `multiagent` 配下の karo / ashigaru1-7 / gunshi は生きている
- `shogun:0.0` の Claude プロセスだけ反応していない

### Step 2: 将軍ペインに attach

```bash
tmux attach -t shogun
```

これで将軍ペインの中身が見える。フリーズしている Claude が見える状態。

**注意**: もし既に tmux 内にいる (プロンプトが `[shogun] 0:bash*` のように表示されている) なら、既に attach 済みなので **このコマンド不要**。エラー `sessions should be nested with care` が出たら既に中にいる証拠。

### Step 3: フリーズしている Claude を終了

将軍ペイン内で以下のいずれかを試す (上から順に):

```
Ctrl+C を2回押す       ← まずこれ
```

それでも反応しなければ:

```
Esc を3〜5回連打 → /exit と入力 → Enter
```

それでもダメなら:

```
Ctrl+\ (強制終了シグナル)
```

最終手段:

```bash
# 別ターミナルから claude プロセスをPID指定で kill
ps aux | grep claude | grep -v grep
kill <PID>
```

ターミナルプロンプト (`$`) が見えたら成功。

### Step 4: Claude を再起動 ★最重要★

**必ず multi-agent-shogun ディレクトリで実行**:

```bash
cd /mnt/c/Users/User/projects/multi-agent-shogun
claude --resume
```

直近セッション一覧が表示される。最新のものを矢印キー or Enter で選択。

**重要なポイント**:
- `--resume` だけで session_id 不要 (一覧が出る)
- `/home/user` など別ディレクトリで起動すると CLAUDE.md/skills/agents が読み込まれず「素のClaude」になり将軍として振る舞わない
- 直近セッションのタイトル例: 「Three-party audit of daily summary engine integration」 (55分前/16.6MB) など

### Step 5: --resume が使えない場合のフォールバック

```bash
cd /mnt/c/Users/User/projects/multi-agent-shogun
claude --dangerously-skip-permissions
```

ただしこれは「素のClaude」起動になる場合があるため、立ち上がったら **すぐに以下のメッセージを送る**:

```
将軍として復活してください。
CLAUDE.md と instructions/shogun.md を読み直し、戦国口調で再開せよ。
```

### Step 6: tmux から detach

将軍が応答するようになったら:

```
Ctrl+B → d (detach)
```

これで tmux セッションは残ったまま、将軍だけ自律稼働状態になる。

---

## 3. 副医院長/クロちゃんから将軍復活を確認する方法

### 3.1 副医院長から `urgent_stop` で状況把握要請

副医院長 (Claude.ai Desktop or fukuincho pane) が、将軍復活後に以下の handshake を INSERT:

```sql
INSERT INTO pc_handshake (
  message_type, from_pc, to_pc, topic, priority, content
) VALUES (
  'urgent_stop',
  'fukuincho',
  'main_pc',
  'shogun_recovery_confirmation_status_check',
  'urgent',
  '将軍 (shogun pane) へ。Desktop副医院長より復活確認。
状況把握+進行中task棚卸しを5分以内に実行+報告せよ。

# 機械的把握項目 (5分以内)
1. 未読pc_handshake確認 (SELECT to_pc=main_pc AND acknowledged_at IS NULL)
2. プロセス物理verify (ps aux | grep claude/watcher)
3. tmux状態 (tmux ls)
4. systemd状態 (systemctl --user status hakudokai-departure)

# 完走時の報告
pc_handshake INSERT (from_pc=main_pc, to_pc=fukuincho,
                     topic=shogun_recovery_status_complete)
'
);
```

### 3.2 将軍が5分以内に応答する

将軍は復活後、自動で `CLAUDE.md` → `memory/MEMORY.md` (将軍のみ) → `instructions/shogun.md` を読み込む。
inbox に urgent_stop が届いたら、上記4項目を機械的に実行し、`shogun_recovery_status_complete` を INSERT する。

### 3.3 副医院長/クロちゃんが完了確認

```sql
SELECT * FROM pc_handshake
WHERE topic = 'shogun_recovery_status_complete'
  AND created_at > NOW() - INTERVAL '15 minutes';
```

これで応答を確認できれば、将軍復活完了。

---

## 4. SecondPC側 (クロちゃん家老) は何をするか

**結論: 基本何もしない**。

- ashigaru2 (sakura) / ashigaru8 (kuro) はそのまま稼働継続
- cross_pc_inbox / file_sync は将軍復活後に自動再開
- 暴走の兆候 (cross_pc_inbox 1分70件超等) があれば SecondPC側で `~/.openclaw/global_disable` フラグを置いて全停止可能:
  ```bash
  ssh hakudokai@192.168.11.47
  touch ~/.openclaw/global_disable
  ```
- 復旧後は フラグ削除:
  ```bash
  rm ~/.openclaw/global_disable
  ```

---

## 5. 副医院長/クロちゃん側が落ちた場合 (おまけ)

### 5.1 副医院長 CLI (fukuincho pane = main_pc tmux:multiagent:0.0) が落ちた

```bash
tmux attach -t multiagent
# ペイン0(karo/fukuincho)を選択 → /exit → claude --resume
# (multiagent:0.0 はプロジェクト構成により karo or fukuincho、@agent_id で確認)
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} agent=#{@agent_id}'
```

### 5.2 副医院長 Desktop (Claude.ai) が落ちた

- ブラウザで claude.ai を再読込
- 直近スレッドを開く
- 「副医院長 (鬼番頭・性悪説監査) として復活、現状把握+進行中task棚卸し」と入力

### 5.3 クロちゃん家老 (SecondPC) が落ちた

```bash
# MainPC から SecondPC に SSH
ssh hakudokai@192.168.11.47

# tmux で multiagent セッションを attach
tmux attach -t multiagent

# 該当ペインで /exit → claude --resume
# SecondPC は ashigaru2 と ashigaru8 のみのため、ペイン番号で判別
```

### 5.4 さくら (ashigaru2 / SecondPC) が落ちた

クロちゃん家老から指示できる。クロちゃんも落ちている場合は §5.3 と同手順。

---

## 6. 立ち上がらない時のフォールバック

### 6.1 「素のClaude」が立ち上がってしまった場合
立ち上がったら即:
```
将軍として復活してください。
CLAUDE.md と instructions/shogun.md を読み直し、戦国口調で再開せよ。
直前のtaskは pc_handshake と queue/shogun_to_karo.yaml で確認可能。
```

### 6.2 `--resume` でも前のセッションが見つからない
全停止からの再起動 → `docs/restart-and-mcp.md §0 コールドスタート` 参照。
ワンライナー4行貼付:
```bash
cd /mnt/c/Users/User/projects/multi-agent-shogun
./shutsujin_departure.sh
bash shim/hakudokai/hakudokai_start_watchers.sh
tmux attach -t shogun
```

### 6.3 tmux session 自体が無い
全停止状態。`docs/restart-and-mcp.md §0` のコールドスタート手順を実行。

### 6.4 暴走後の容量制限到達による再起動
段階的再起動が必要。`docs/restart-and-mcp.md §9 段階的再起動手順 Phase A〜F` 参照。

---

## 7. 副医院長 memory #25 (FKI-OPERATIONAL-MANUAL-FIRST-01) との関係

副医院長は本書のような「現場操作手順」を尋ねられた際、手探りでご案内する前に必ず以下を物理SELECT先行確認すべし:
- `docs/` ディレクトリの手順書 (本書 + restart-and-mcp.md)
- Supabase `project_documents` (doc_type='runbook' or 'handover')
- `pc_onboarding_kit`

本書はこの memory #25 を構造的に保証するためのもの。**「将軍だけ落ちた」は2026-05-05 12:59 と 2026-05-05 ~15:30 の2回発生**しており、再発時は手探りゼロで本書を即参照すること。

---

## 8. 関連ドキュメント

- [CLAUDE.md](../CLAUDE.md) — プロジェクト全体ルール (§Watcher Design Principles 含む)
- [docs/restart-and-mcp.md](./restart-and-mcp.md) — 全停止/MCP接続/段階的再起動 完全手順書
- [docs/audit-framework.md](./audit-framework.md) — 三者監査・差分監査ルール
- [docs/runbooks/](./runbooks/) — エラーコード別 runbook 8件
- [docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md](./incident_logs/2026-05-05_secondpc_consumption_anomaly.md) — SecondPC暴走事件解析
- [memory/MEMORY.md](../memory/MEMORY.md) — 将軍永続メモリ
- [instructions/shogun.md](../instructions/shogun.md) — 将軍の役割定義

---

## 9. 改訂履歴

- 2026-05-05 v1.0 初版 (理事長殿御依頼により、本日2回の将軍フリーズの教訓を踏まえて整備)
