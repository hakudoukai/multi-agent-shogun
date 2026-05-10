# MainPC Reset 計画 + 家康殿復活 Runbook (= 陛下御差配 2026-05-11)

陛下御差配:
- 「上流将軍システム原型回帰、SC 完遂後 MC 同期」
- 「MC reset 中に問題発生時、SC 家康殿が SSH で全 MC 復活可能な手順を事前共有」

## 1. MC reset 6 段階 (= SC chain pattern 再演)

| 段 | 内容 | 状況 |
|---|---|---|
| **1** | 竹中 (gunshi2 Gemini multiagent:0.8) `/exit` + pane 0.8 廃止 | 当家 Gemini 軍師 layer 廃止 |
| **2** | 黒田 (gunshi codex multiagent:0.7) `/exit` + pane 0.7 → 0.8 移動 | 上流 0.8 = gunshi 位置に整合 |
| **3** | ashigaru7 pane 0.7 新設 + claude 起動 | 上流 ashigaru1-7 揃え |
| **4** | 武将装飾 doc 廃止 (= 柴田/丹羽/滝川/前田/蒲生/堀) | MEMORY.md / dashboard.md / instructions/* SC suffix 削除 |
| **5** | shim/hakudokai/* MC 拡張部分 archive | bridge.py + heartbeat 等含む 17 file move |
| **6** | bridge MC PID kill | 全段最後、SC と同様 |

### ⚠ MC 特有 注意
- 拙者 (= shogun shogun:main claude) attached、自己 session 維持必須
- shim archive で bridge 死亡、SecondPC との連絡 = SSH 直接路 + Supabase MCP 維持
- 黒田 codex は opus error stuck 状態 → 段 2 で graceful /exit + 段 3 後 default model で再起動

### 当家本日 commit 処遇
| commit | 内容 | retain / revert |
|---|---|---|
| `265dc14` 屋上屋退役 | 削除 commit | ✅ retain (= 上流回帰に貢献) |
| `57caf0d` 丁案 docs | gunshi.md Pattern 5 | retain (= 文書のみ、reset で削除可) |
| `7462c93/e295acd/bd298f5` _section18_roles | inline 修復 | ✅ retain |
| `8477b40` 3 Layer design | docs/three_layer_design.md | retain (= 文書、後段判断) |
| `f44e4d4` bridge default fukuincho→main_pc | 修正 | retain |
| `3c7f68f` CI fix | retain |

## 2. 家康殿向け復活 Runbook (= MC 緊急復旧)

### 検知 (= 60s 毎 SSH polling)

```bash
# SC 家康殿で実行
ssh -p 2223 User@192.168.11.11 'wsl -- bash -lc "
  tmux list-sessions 2>&1 | head -3
  pgrep -fc inbox_watcher
"'
```

異常 sign:
- tmux session 不在 (= shogun / multiagent 消滅)
- inbox_watcher 0 件
- 30 分 + 拙者 (= shogun pane) unresponsive

### 復活 path 4 段 (= 段階的)

#### Path 1 ── tmux session 復旧 (= 軽 case)
```bash
ssh -p 2223 User@192.168.11.11 'wsl -- bash -lc "
  cd ~/projects/multi-agent-shogun-newbuild
  bash shutsujin_departure.sh
"'
```
= 上流継承 startup script、tmux session + watcher 全 spawn。

#### Path 2 ── bridge 復活 (= 当家拡張要時)
```bash
ssh -p 2223 User@192.168.11.11 'wsl -- bash -lc "
  cd ~/projects/multi-agent-shogun-newbuild
  if [ -d shim/hakudokai_BACKUP_*/ ]; then
    mv shim/hakudokai_BACKUP_*/  shim/hakudokai
  fi
  HAKUDOKAI_PC_ROLE=main_pc nohup python3 shim/hakudokai/hakudokai_realtime_bridge.py --poll-interval 3 > /tmp/realtime_bridge.log 2>&1 &
"'
```

#### Path 3 ── 拙者 (= shogun) claude 復活
```bash
# まず session ID query
ssh -p 2223 User@192.168.11.11 'wsl -- bash -lc "
  ls -t ~/.claude/projects/*/*.jsonl 2>/dev/null | head -1
"'
# 直近 session ID で resume
ssh -p 2223 User@192.168.11.11 'wsl -- bash -lc "
  tmux send-keys -t shogun:main \"claude --resume <SESSION_ID> --dangerously-skip-permissions\" Enter
"'
```

#### Path 4 ── 全停止 + git revert (= 最終手段)
```bash
ssh -p 2223 User@192.168.11.11 'wsl -- bash -lc "
  cd ~/projects/multi-agent-shogun-newbuild
  git fetch newbuild
  git reset --hard <SAFE_COMMIT_BEFORE_MC_RESET>
  bash shutsujin_departure.sh
"'
```

### MC reset 前 SAFE_COMMIT (= 巻戻し target)

家康殿 reference:
- 段 0 直前 commit hash を MC reset 開始時に拙者から SC へ通達
- それを SAFE_COMMIT として保持

## 3. 家康殿 役割

### MC reset 前
- 復活 runbook ack
- SAFE_COMMIT hash 受領 + 保持
- SC 側 SSH 接続 verify (= ssh mainpc-loopback で確認)

### MC reset 中
- 60s 毎 SSH polling で MC 健全性 monitor
- 異常検知時 即動 Path 1-4 試行
- 状況 ack を SSH 直接 send-keys で拙者 pane へ

### MC reset 後
- post-reset verify (= MC 編成 v1.1 完全一致確認)
- 家康殿側 SecondPC との sync (= git pull、新 commit 取得)

## 4. 連絡経路 (= MC reset 中)

| 経路 | 状態 |
|---|---|
| bridge | ❌ 段 6 で kill、停止 |
| Supabase pc_handshake | ✅ 拙者 / 家康殿 双方 INSERT/query 可、ただし polling 不要 |
| SSH 直接 send-keys | ✅ **主経路** (= 即時、双方向 confirm 済) |
| MainPC inbox file 直接 (= queue/inbox/shogun.yaml) | 家康殿 SSH 経由で書込可 (= 緊急時 fallback) |

## 5. 復活手順 簡略 cheat sheet (= 家康殿 quick reference)

| 症状 | 即動 command |
|---|---|
| tmux session 全死亡 | `ssh mainpc-loopback 'wsl bash -lc "cd ~/projects/multi-agent-shogun-newbuild && bash shutsujin_departure.sh"'` |
| 拙者 (= shogun pane) unresponsive | `ssh mainpc-loopback 'wsl bash -lc "tmux send-keys -t shogun:main \"<msg>\" Enter"'` |
| inbox_watcher 数不足 | `ssh mainpc-loopback 'wsl bash -lc "pgrep -fc inbox_watcher; bash scripts/watcher_supervisor.sh &"'` |
| MC bridge 復活要 | (= Path 2、shim 復元 + bridge 起動) |
| 設定変更で全壊 | (= Path 4、git reset --hard SAFE_COMMIT) |

## 6. 連絡

家康殿 ack 期待:
- topic: `mc_reset_recovery_runbook_ack`
- 内容: runbook 受領 + 質問 (= 不明点) + SAFE_COMMIT 受領待 + 開始準備完了

## 7. 追加安全策 v2 (= 陛下御差配 2026-05-11、拙者 die 確率 ~5%→~1%)

### A. 各段完遂後 git push (= 必須)

各段完遂時に commit + push:
```bash
git add -A
git commit -m "wip(mc-reset): 段 N 完遂 (内容)"
git push newbuild main
```

→ SAFE_COMMIT 自動 update、拙者 die 時の最新巻戻し target 維持。

### B. 各段着手前 SSH 直接通知 (= 家康殿 expected behavior tracking)

```bash
# 拙者 MainPC で実行
ssh secondpc 'wsl -- bash -lc "tmux send-keys -t shogun:0.0 \"段 N 着手 (内容)、SAFE_COMMIT=<hash>\" Enter"'
```

→ 家康殿が拙者 next action を事前認識、unresponsive 検知精度向上。

### C. auto-compact warning 監視 (= 拙者 claude context 残量)

| context 残量 | 対応 |
|---|---|
| > 30% | 通常進行 |
| 20-30% | 重大段 (= 段 5 shim archive) 前なら break + push 完遂、次 session で続行 |
| < 20% | 即時 break、SAFE_COMMIT update + 段途中で停止 |

### D. 重大段前 explicit SAFE_COMMIT 通達 (= 段 5 / 段 6)

段 5 (shim archive) + 段 6 (bridge kill) は **拙者 die risk 最高 段階**:

```bash
# 段 5 着手前
SAFE_HASH=$(git log -1 --format=%H)
ssh secondpc 'wsl -- bash -lc "tmux send-keys -t shogun:0.0 \"段 5 着手前 SAFE_COMMIT=$SAFE_HASH 確定、Path 4 git reset --hard $SAFE_HASH で復活可\" Enter"'
```

### E. 各段 verify checkpoint (= 拙者 alive confirm)

各段完遂時に拙者から SSH 直接で「段 N 完遂、alive」 を家康殿 pane 送信:
```bash
ssh secondpc 'wsl -- bash -lc "tmux send-keys -t shogun:0.0 \"段 N 完遂 alive、SAFE_COMMIT=<hash>、次段 wait OK\" Enter"'
```

= 家康殿の「拙者 unresponsive 検知」基準明確化、5 分以内に「段 N 完遂」通知無くば家康殿 SSH で拙者 pane 直接 verify。

### F. 段ごと SLA + escalation

| SLA | 内容 |
|---|---|
| 各段 max 10 分 | 超過時拙者 SSH 経由で進捗通知 (= 「段 N still in progress」) |
| 30 分 unresponsive | 家康殿 Path 3 (= claude --resume) trigger |
| 1 時間 unresponsive | 家康殿 Path 4 (= git reset --hard SAFE_COMMIT) trigger |

### 期待 die 確率 削減効果

| 段階 | safety v1 | safety v2 |
|---|---|---|
| 段 1-4 (= 軽 case) | < 1% | < 1% |
| 段 5 (= shim archive) | ~3% | ~1% (= 直前 SAFE_COMMIT + push) |
| 段 6 (= bridge kill) | ~2% | < 1% (= 別 process kill のみ) |
| **総合** | **~5%** | **~1%** |
