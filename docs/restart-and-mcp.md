# Claude Code 再起動・MCP接続 完全手順書

**対象**: multi-agent-shogun プロジェクトを操作する全ての人（理事長・将軍・家老・足軽含む）
**作成**: 2026-05-05（再起動騒動の教訓を反映）

---

## 0. 電源OFFからの完全起動（コールドスタート）

PCを完全に電源OFFした後、または再起動した後、システム全体を立ち上げる手順。

### 全体の流れ

```
Windows起動
  ↓
WSL2 ターミナルを開く
  ↓
プロジェクトディレクトリへ移動
  ↓
出陣スクリプト実行（tmux + 全エージェント起動）
  ↓
ウォッチャー起動（メッセージ配信・監視）
  ↓
将軍ペインにアタッチ → Claude Code 起動
  ↓
（必要なら）SecondPC 接続
  ↓
（必要なら）DentalBI ローカルサーバー起動
```

### 手順 ①: WSL2 ターミナルを開いてプロジェクトへ

Windows のスタートメニューから「Ubuntu」または「WSL」を開く。

```bash
cd /mnt/c/Users/User/projects/multi-agent-shogun
```

### 手順 ②: 出陣スクリプトで tmux + エージェント一括起動

```bash
./shutsujin_departure.sh
```

このスクリプト1本で以下が全て実行される：
- Python venv チェック・自動作成
- tmux セッション `shogun`（1ペイン）作成
- tmux セッション `multiagent`（9ペイン: karo + ashigaru1-7 + gunshi）作成
- 各ペインで Claude Code を起動
- 各ペインに `@agent_id` を設定
- 起動プロンプトを各エージェントに投入

**所要時間**: 約30秒〜1分

オプション：
| オプション | 用途 |
|-----------|------|
| なし | 通常起動（前回の状態を維持） |
| `-c` | キューをリセット（クリーンスタート） |
| `-s` | tmux のみ作成・Claude 起動なし |
| `--auto-mode-on` | Claude permission 自動承認 |

### 手順 ③: ウォッチャー（メッセージ配信デーモン）を起動

```bash
bash shim/hakudokai/hakudokai_start_watchers.sh
```

これで以下が全て起動：
- `fukuincho_watcher` (Supabase → 将軍 inbox、5秒間隔)
- `inbox_watcher` × 4 (karo, ashigaru1, gunshi, shogun)
- `fukuincho_reverse_watcher` (将軍 → Supabase)
- `secondpc_watcher` (SecondPC ↔ MainPC)
- `kuro_desktop_watcher` (Desktop kuro ↔ MainPC)
- `task_sync` (タスクYAML自動同期)
- `activity_monitor` (忍び — エージェント死活監視)
- `watchdog` (ウォッチャー自体の死活監視・自動再起動)

**前提**: `~/.hakudokai/env` に `SUPABASE_URL` と `SUPABASE_SERVICE_ROLE_KEY` が記載されていること。

確認：
```bash
ps aux | grep -E "watcher|monitor|task_sync|watchdog" | grep -v grep
```

### 手順 ④: 将軍ペインにアタッチ（理事長が操作する場所）

```bash
tmux attach -t shogun
```

将軍ペインが表示されたら、Claude Code はもう起動済み。
理事長は普段通りメッセージを入力すればよい。

**他のエージェントを見たい場合**:
```bash
tmux attach -t multiagent
# Ctrl+B → 数字キー(0-8) でペイン切替
# 0=karo, 1-7=ashigaru1-7, 8=gunshi
# Ctrl+B → d でデタッチ
```

### 手順 ⑤（任意）: SecondPC 接続

SecondPCも使う場合：
```bash
bash shim/hakudokai/hakudokai_secondpc_setup.sh
```

SSH (192.168.11.47) で SecondPC に接続し、向こう側でも tmux + Claude を起動する。

### 手順 ⑥（任意）: DentalBI ローカル開発サーバー起動

UI開発・画面確認をする場合：

```bash
# Vite (フロントエンド)
cd /mnt/c/Users/User/Documents/DentalBI/frontend
nohup npx vite --host 0.0.0.0 --port 5173 > /tmp/vite-dev-server.log 2>&1 &

# FastAPI (バックエンド)
cd /mnt/c/Users/User/Documents/DentalBI
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/fastapi-server.log 2>&1 &
```

確認：
```bash
curl -s -o /dev/null -w "Vite: %{http_code}\n" http://localhost:5173
curl -s -o /dev/null -w "FastAPI: %{http_code}\n" http://localhost:8000/api/patients/01_010766
```

### 💡 ワンライナー（4行まとめて貼り付けOK）

慣れたら、以下4行をターミナルに**まとめて貼り付け**で全工程実行可能：

```bash
cd /mnt/c/Users/User/projects/multi-agent-shogun
./shutsujin_departure.sh
bash shim/hakudokai/hakudokai_start_watchers.sh
tmux attach -t shogun
```

各コマンドはシーケンシャル実行（前が完了してから次へ）なので順序問題は起きない。

**注意**: 初回実行時のみ、`shutsujin_departure.sh` がエラーや確認プロンプトを出す可能性があるため1行ずつ実行を推奨。2回目以降は4行貼り付けでOK。

### コールドスタート 全体チェックリスト

```
□ WSL2ターミナル開いた
□ ./shutsujin_departure.sh 実行 → tmux 2セッション + 10エージェント起動
□ hakudokai_start_watchers.sh 実行 → 全ウォッチャー稼働
□ tmux attach -t shogun で将軍ペインに入った
□ 将軍が「準備完了」と返事した
□ （必要なら）SecondPC接続
□ （必要なら）Vite/FastAPI起動
```

### よくある初回トラブル

| 症状 | 対処 |
|------|------|
| `tmux: command not found` | `sudo apt install tmux` |
| `python3 -m venv に失敗` | `sudo apt install python3-venv` |
| `inotifywait not found` | `sudo apt install inotify-tools` |
| `SUPABASE_URL required` | `~/.hakudokai/env` を作成（SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY） |
| `tmux session multiagent already exists` | 既存セッションを `tmux kill-session -t multiagent` で削除してから再実行 |
| 将軍が応答しない | `tmux attach -t shogun` でペイン直接確認 → Claude起動失敗ならペイン内で `claude` 手動実行 |

---

## 1. なぜ再起動が必要になるのか

Claude Code には3種類の「持続性レイヤー」がある：

| 種類 | 範囲 | 再起動の影響 |
|------|------|---------------|
| **会話コンテキスト** | 今のセッションだけ | 失われる（→事前に保存） |
| **memory/MEMORY.md** | 全セッション共通 | 残る |
| **MCPサーバー接続** | 起動時に確立 | 再接続される（途中で追加・修正したMCPは再起動必須） |

**MCPサーバーは起動時にしか接続を試みない**。
途中で `claude mcp add` した場合、そのセッションでは使えず、再起動して初めて使えるようになる。

---

## 2. 再起動前のチェックリスト（重要）

会話の続きを失わないため、再起動前に必ず以下を実行：

### ① 進行中の作業を memory に保存

```
/mnt/c/Users/User/projects/multi-agent-shogun/memory/MEMORY.md
```

将軍に以下を依頼：
> 「現在の作業状況をMEMORY.mdに保存してください。次回セッションでこの続きから再開できるように」

将軍は以下を保存する：
- 何をやっていたか（ファイル名・行番号レベル）
- 次のステップ
- 起動中のサーバー・プロセス（Vite/FastAPI/tmuxなど）
- 解決済み・未解決の問題

### ② tmux セッションの状態確認

```bash
tmux list-sessions
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} agent=#{@agent_id}'
```

エージェント（家老・足軽・軍師）は tmux pane で動いているので、Claude Code 再起動の影響は受けない。
**再起動するのは将軍ペインの Claude Code だけ**。

### ③ ローカルサーバーは継続稼働

Vite (5173)・FastAPI (8000) などは別プロセスなので、Claude Code 再起動しても止まらない。

```bash
ps aux | grep -E "vite|uvicorn|tmux" | grep -v grep
```

で動作確認。

---

## 3. 再起動の手順

### A. 将軍ペイン（shogun:0.0）の Claude Code を再起動

```bash
# 現在のセッション内で
/exit
```

または `Ctrl+C` を2回。

ターミナルプロンプト（`$`）が表示されたら：

```bash
claude
```

これだけ。

### B. 再起動後の最初のメッセージ

```
MEMORY.md を読んで、前回の続きから再開してください。
```

将軍が memory を読み込み、即座に作業状態を復元する。

---

## 4. MCP サーバーの確認・追加

### 現在接続されている MCP を確認

```bash
claude mcp list
```

出力例：
```
playwright: npx @playwright/mcp@latest - ✓ Connected
agentation: npx -y agentation-mcp@latest - ✓ Connected
higgsfield: https://mcp.higgsfield.ai/mcp - ! Needs authentication
claude.ai Supabase: https://mcp.supabase.com/mcp - ✓ Connected
```

| 状態 | 意味 |
|------|------|
| ✓ Connected | 正常に接続中 |
| ✗ Failed to connect | 接続失敗（再起動 or 設定確認） |
| ! Needs authentication | 認証が必要（初回ログイン未実施） |

### MCP サーバーを追加

```bash
# プロジェクトスコープに追加
claude mcp add <name> -- <command> <args...>

# 例: Playwright MCP
claude mcp add playwright -- npx @playwright/mcp@latest
```

**追加後は必ず再起動**しないと使えない。

### 設定ファイルの場所

| スコープ | パス | 用途 |
|----------|------|------|
| ユーザー | `~/.claude/settings.json` | 全プロジェクト共通 |
| プロジェクト | `.claude/settings.local.json` | このプロジェクトのみ |
| Claude Code 内部 | `~/.claude.json` | claude mcp add の保存先 |

---

## 5. 主要 MCP サーバー一覧（このプロジェクト）

| MCP | 用途 | 接続先 |
|-----|------|--------|
| **playwright** | ブラウザ操作・画面確認（理事長のChromeに「Claude (MCP)」タブとして接続） | `npx @playwright/mcp@latest` |
| **agentation** | DentalBI のUI修正指示（画面右下のツールバー経由） | `npx -y agentation-mcp@latest` |
| **higgsfield** | 動画生成（恐竜キャラアニメーション） | `https://mcp.higgsfield.ai/mcp` |
| **claude.ai Supabase** | Supabase DB操作（project_documents等） | `https://mcp.supabase.com/mcp` |
| **memory** | エージェント間共有メモリ | 内蔵 |

### Playwright MCP の動作確認

再起動後、ToolSearch に以下のツールが現れれば成功：
- `mcp__playwright__browser_navigate`
- `mcp__playwright__browser_take_screenshot`
- `mcp__playwright__browser_snapshot`
- `mcp__playwright__browser_click`
- 等

確認方法（将軍に依頼）：
> 「Playwright MCP のツールが読み込まれているか確認してください」

---

## 6. トラブルシューティング

### 症状: 再起動したのに Playwright MCP が動かない

**原因A**: 設定の保存先が違う
```bash
# 確認
cat ~/.claude.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('projects',{}).get('/mnt/c/Users/User/projects/multi-agent-shogun',{}).get('mcpServers',{}), indent=2))"
```
無ければ：
```bash
claude mcp add playwright -- npx @playwright/mcp@latest
# 再起動
```

**原因B**: Playwright のブラウザバイナリ未インストール
```bash
npx playwright install chromium
npx playwright install-deps chromium
```

**原因C**: ヘッドレス環境のライブラリ不足（WSL2でよく発生）
```bash
npx playwright install-deps chromium  # 自動修復
```

### 症状: tmux のエージェントが応答しない

将軍ペインの再起動とエージェントペインは独立。
エージェント側で問題があれば：

```bash
# エージェントペインの状態確認
tmux capture-pane -t multiagent:0.0 -p | tail -20
```

### 症状: Vite/FastAPI が落ちている

```bash
# プロセス確認
ps aux | grep -E "vite|uvicorn" | grep -v grep

# Vite 再起動
cd /mnt/c/Users/User/Documents/DentalBI/frontend
nohup npx vite --host 0.0.0.0 --port 5173 > /tmp/vite-dev-server.log 2>&1 &

# FastAPI 再起動
cd /mnt/c/Users/User/Documents/DentalBI
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/fastapi-server.log 2>&1 &
```

---

## 7. 「Claude (MCP)」タブの正体（誤解しやすい）

理事長のChromeに「Claude (MCP)」というタブが表示されるが、これは：

- **Chrome拡張ではない**
- **Playwright MCP が Chrome に接続して開いたタブ**

そのため：
- Playwright MCP が未接続だと「Claude (MCP)」タブも開けない
- Chromeの拡張一覧を探しても「Claude (MCP)」拡張は見つからない

---

## 8. 関連ドキュメント

- [CLAUDE.md](../CLAUDE.md) — プロジェクト全体ルール
- [memory/MEMORY.md](../memory/MEMORY.md) — 永続メモリ（将軍のみ）
- [docs/philosophy.md](./philosophy.md) — システム哲学
- [instructions/shogun.md](../instructions/shogun.md) — 将軍の役割定義

---

## 9. 段階的再起動手順（暴走事件・容量制限到達後）

**過去事故 2026-05-05**: watcher 暴走で API 容量を 26分で38%消費。原因解析 [docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md](./incident_logs/2026-05-05_secondpc_consumption_anomaly.md)

容量制限到達後の **5pm(JST) リセット後の段階的再起動手順**：

### Phase A: 安全確認 (停止維持)

1. `~/.openclaw/global_disable` 等の停止フラグを **置いたまま**
2. Supabase で確認:
   ```sql
   -- unack 件数 (10件以下が安全)
   SELECT COUNT(*) FROM pc_handshake WHERE acknowledged_at IS NULL;
   -- 過去5分のINSERT件数 (5件以下が安全)
   SELECT COUNT(*) FROM pc_handshake WHERE created_at > NOW() - INTERVAL '5 minutes';
   ```
3. Phase B には進まない: heartbeat / fukuincho_reverse_watcher / watchdog はP0 hotfix 投入後にのみ起動

### Phase B: inbox 掃除

各エージェントの inbox 重複・古い指示を整理:

```bash
# バックアップ
cp queue/inbox/ashigaru2.yaml queue/inbox/ashigaru2.yaml.bak.$(date +%s)
cp queue/inbox/ashigaru8.yaml queue/inbox/ashigaru8.yaml.bak.$(date +%s)

# 最新タスク以外を read:true に (バーストや古い指示を整理)
# Pythonスクリプトで安全実施 — 削除でなく既読化
```

その後、家老が「最新の1件のみ処理せよ」と新規発令。

### Phase C: 必要最小限の watcher のみ起動

```bash
# 起動順 (1体ずつ、5-10分観察してから次へ)
nohup bash scripts/inbox_watcher.sh karo multiagent:0.0 claude >> /tmp/inbox_watcher_karo.log 2>&1 </dev/null &
sleep 600  # 10分観察、新規消費なしを確認
nohup bash scripts/inbox_watcher.sh ashigaru1 multiagent:0.1 claude >> /tmp/inbox_watcher_ashigaru1.log 2>&1 </dev/null &
sleep 600
# ... 必要な足軽のみ順次
```

### Phase D: 同期系のみ起動 (双方向 inbox はまだ起動しない)

```bash
nohup bash shim/hakudokai/hakudokai_task_sync.sh --interval 2 >> /tmp/hakudokai_task_sync.log 2>&1 </dev/null &
# reports_sync (SecondPC側)
ssh hakudokai@192.168.11.47 "nohup bash ~/projects/multi-agent-shogun/shim/hakudokai/hakudokai_reports_sync.sh --interval 2 >> /tmp/hakudokai_reports_sync.log 2>&1 </dev/null &"
```

5-10分観察、unack件数が増えないことを確認。

### Phase E: P0 hotfix 投入後にのみ復活させる watcher

以下は **コード修正完了後のみ** 起動:
- `hakudokai_heartbeat.py` (Bug B修正後 — 専用 `pc_handshake_heartbeat` 経由)
- `hakudokai_fukuincho_reverse_watcher.sh` (Bug A修正後 — self-send 即 ack)
- `hakudokai_watchdog.sh` (Bug C修正後 — 手動停止フラグ尊重)
- `hakudokai_secondpc_watcher.sh` (Bug D修正後 — dedupe + retry cap)

### Phase F: 起動後の継続監視

毎30分:
```bash
# unack 件数監視
echo "$(date) unack=$(...)" >> /tmp/restart_health.log
# 異常検知 (10件超過、5分INSERT 5件超過)
```

異常検知時は即 Phase A に戻す（全停止 → 原因調査）。

---

## 10. 関連ドキュメント

- [CLAUDE.md](../CLAUDE.md) — プロジェクト全体ルール (§Watcher Design Principles 含む)
- [docs/audit-framework.md](./audit-framework.md) — 三者監査・差分監査ルール
- [docs/incident_logs/](./incident_logs/) — 過去事故ログ
- [memory/MEMORY.md](../memory/MEMORY.md) — 永続メモリ（将軍のみ）
- [docs/philosophy.md](./philosophy.md) — システム哲学
- [instructions/shogun.md](../instructions/shogun.md) — 将軍の役割定義

---

## 11. 今後この手順書が古くなったら

このファイルは将軍が随時更新する。
新しい問題に遭遇したら：
1. トラブルシューティング章に追記
2. memory/MEMORY.md にも要点を保存
3. CLAUDE.md からのリンクが切れていないか確認
