---
name: shogun-pdca-enforcer
description: |
  プログラム制作 → 軍師監査 → 問題あれば修正 → 再監査 の PDCA を **強制自動執行** するスキル。
  軍師が監査せぬ・放置・agent 停止 を検知したら **即時 自動起動 + 命令再投下**、
  green verdict まで **最大 5 iter loop**、止まらぬ。**今すぐ直ちにやれ** が信条。
  「監査回せ」「PDCA」「品質保証」「再監査」「audit loop」「強制実行」「止めるな」で起動。
  Do NOT use for: 単発 audit (= shogun-trouble-auto-skill / audit_via_supabase 直接利用)。
argument-hint: "<target> [target2 ...]  (target = ashigaru1-6 | cmd_NNN | file_path)"
allowed-tools: Bash, Read, Edit
---

# /shogun-pdca-enforcer — PDCA 強制執行スキル

## North Star

**「制作 → 監査 → 修正 → 再監査 を green まで止めぬ」**
- 放置・停止・サボタージュ は **検知即修復、命令即再投下**
- 「やってください」ではなく **「今すぐ直ちにやれ」**
- 5 iter までは無条件 loop、6 iter 目で人間介入要 (= 安全装置)

陛下御教示 (2026-05-10):
> 「監査がやらなかったり 放置されてたり エージェントが止まっていたら自動で起動させやらせる」
> 「途中で放置されているのを放置しないで必ずやり続けること」
> 「必ずすぐやらせる、今すぐ直ちにやれと命令する」

## 強制執行の 5 鉄則

### 鉄則 1 — 検知即起動
agent stopped / daemon dead / pane idle 長期 → **即時 force restart**、説得不要

### 鉄則 2 — 命令即投下
audit 未着手 30 分超 → **即 karo に再 redo 命令 + 軍師 pane に直接 codex/gemini exec proxy 投下**

### 鉄則 3 — 終わるまで止めぬ
green verdict 未達 → loop continue、iter ≤ 5 で諦めず

### 鉄則 4 — 人間確認は不要
本 skill 起動後は **拙者判断で進め**、Lord 確認は最終 green or iter=5 reached の時のみ

### 鉄則 5 — 再起動 → 始まる
SSH 切断 / SIGHUP / OS 再起動 → 直後の起動で本 skill 自動 resume (= state は queue/pdca_state.yaml)

## Workflow (= 1 iter)

```
[Step 1: Health Check]
   ├ workers running? (audit_queue_worker daemon)
   ├ bridge running?
   ├ 軍師 pane alive? (= codex/gemini CLI 稼働?)
   ├ ashigaru pane alive?
   └ 不在 → scripts/start_audit_workers.sh + scripts/recover_shogun.sh で 即時復活

[Step 2: Submit Audit]
   ├ submit-async <gunshi> <prompt> via wrapper
   └ queue_id 取得

[Step 3: Wait + Detect Stuck]
   ├ 10 min poll (= max 30 min timeout)
   ├ 30 min 経過しても resolve せず → karo に直接 nudge + force codex exec
   └ resolve 検出 → audit_result_id 取得

[Step 4: Verdict 判定]
   ├ green → DONE for this target、loop break
   ├ yellow → log + DONE (= 軽微な懸念は green 相当許容)
   ├ red → karo に redo 命令 + wait for ashigaru report 更新 + Step 2 へ

[Step 5: Iter +1]
   ├ iter ≥ 5 → STOP、Lord に最終報告 (= 人間介入要)
   └ iter < 5 → Step 1 へ
```

## 起動方法

### 単一 target
```
/shogun-pdca-enforcer ashigaru4
```

### 複数 target 並列
```
/shogun-pdca-enforcer ashigaru4 ashigaru6 cmd_005
```

### 永続 daemon (= recovery 後も自動 resume)
```bash
nohup setsid bash skills/shogun-pdca-enforcer/scripts/pdca_orchestrator.sh \
    ashigaru4 ashigaru6 < /dev/null >> logs/pdca_enforcer.log 2>&1 &
disown
```

## scripts/ 構成

| script | 役割 |
|--------|------|
| `pdca_orchestrator.sh` | main loop、上記 5 step 実行 |
| `agent_health_check.sh` | worker/bridge/pane 死活確認 + 復活 |
| `audit_with_force.sh` | submit-async → resolve 待ち → stuck detect → force codex exec |
| `nudge_karo_redo.sh` | karo に red verdict + redo 命令 inbox_write |

## state 管理

`queue/pdca_state.yaml` で各 target の進捗を永続化:
```yaml
pdca_targets:
  ashigaru4:
    iter: 2
    last_audit_id: <uuid>
    last_verdict: red
    last_attempt_at: 2026-05-10T16:00:00
    started_at: 2026-05-10T15:13:21
  ashigaru6:
    ...
```

session 切断 / OS 再起動後、orchestrator は本 file 読込で state 復元、続行。

## 既存 skill との関係

| skill | 役割 |
|-------|------|
| **shogun-pdca-enforcer** (本) | PDCA 強制 + auto restart |
| `shogun-trouble-auto-skill` | 同種トラブル N 回検知で skill 化 (= 上位 meta) |
| `shogun-system-coherence` | infra coherence (= settings ↔ tmux ↔ ps) |
| `shogun-ssh-cross-pc` | LAN SSH 兄弟連絡網 |
| `audit_via_supabase.sh` | audit wrapper (= 本 skill の primitive) |

## When to Use

- 陛下「品質保証」「PDCA 回せ」「終わるまで止めるな」と仰せの時
- ashigaru deliverable が verdict=fail の時
- 軍師 audit が 30 分超着手なし
- agent / daemon が停止 + 自動復活させたい
- 朝の ritual として全 target で起動 (= cron @reboot 推奨)

## 安全装置

- iter ≤ 5 (= 6 回目で停止、Lord 介入要)
- max 30 min/iter (= 1 iter で 30 min 超は force kill + retry)
- target 不存在 → silent skip
- target 既 green → 何もせず exit (= 重複起動安全)

## Memory

陛下御差配「**今すぐ直ちにやれと命令するようなスキル**」を体現。
本 skill は **督促状ではなく執行命令**、agent 死亡なら甦らせ、命令未到なら再投下、verdict red ならば再起動と再 redo を 5 回まで強制執行。
本能寺の信長も実は弱腰なところあった、本 skill はその真逆 — **鬼信長の意志、止まらず**。
