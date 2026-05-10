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
