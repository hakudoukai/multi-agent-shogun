# SC inbox 整理 + persona 廃止 候補 plan

- task_id: `subtask_cmd020_persona_廃止_sc_inbox_整理`
- parent_cmd: `cmd_020`
- 起案者: `ashigaru4` (= 四番槍 大久保彦左衛門)
- 起案日: `2026-05-13T14:05:00+09:00`
- repo scope: `multi-agent-shogun-newbuild` only (= hakudokai-dev は本 task 範囲外)
- 本 文書 status: **plan 文書化のみ (= 実行禁、陛下御差配後の別 cycle で karo 起案 + 実行)**

## 1. 背景 + scope (= 範囲外厳守宣言)

### 1.1 背景
朝駆け cmd_020 next phase 規範下、`queue/inbox/` 配下に **live wired (file + watcher + agent) 10 体**
に加え、**orphan alias inbox 5 件** (= watcher process 不在の旧 alias / SC bridge / persona alias) が
滞留している。SessionStart hook (`scripts/session_start_hook.sh`) の `inbox_integrity_verify` 関数は
agent_id ↔ inbox_file ↔ inbox_watcher.sh args の三点整合を警告 #1/#2/#3 で出力するが、現状 alias
全件 retain で warning 発生は理論上のみ。本 plan は alias 整理 candidate + 実行手順 specification を起案
し、実行は陛下御差配経由別 cycle に委譲する。

### 1.2 scope 厳守事項 (= 本 task 不実行宣言)
| 種別 | 動作 | 状態 |
|---|---|---|
| live inbox file mutation (= rename / delete / merge / overwrite) | **禁** | 本 task 不実行 |
| watcher process 操作 (= kill / restart / reconfigure) | **禁** | 本 task 不実行 |
| SessionStart hook (`scripts/session_start_hook.sh`) 変更 | **禁** | read-only 解析対象 |
| `scripts/auto_forward_shogun_to_ieyasu.sh` bridge 起動 / 停止 | **禁** | 本 task 不実行 (= 別 cycle) |
| persona alias 廃止実行 (= 同一 agent の二重 alias 解消) | **禁** | specification のみ起案 |
| 新規 inbox file 作成 | **禁** | 本 task 不実行 |

## 2. 現行 state inventory (= 機械観測 evidence)

### 2.1 live wired inbox (= 通常運用 path、retain)
| agent_id | inbox file | watcher args (= ps aux 観測) | msg | unread | last_ts | cli |
|---|---|---|---|---|---|---|
| shogun | `queue/inbox/shogun.yaml` | `shogun shogun:main.0 claude` | 48 | 4 | 2026-05-13T13:49:05 | claude |
| karo | `queue/inbox/karo.yaml` | `karo multiagent:agents.0 claude` | 38 | 1 | 2026-05-13T13:59:50 | claude |
| ashigaru1 | `queue/inbox/ashigaru1.yaml` | `ashigaru1 multiagent:agents.1 claude` | 22 | 0 | 2026-05-13T13:58:34 | claude |
| ashigaru2 | `queue/inbox/ashigaru2.yaml` | `ashigaru2 multiagent:agents.2 claude` | 17 | 0 | 2026-05-13T13:49:40 | claude |
| ashigaru3 | `queue/inbox/ashigaru3.yaml` | `ashigaru3 multiagent:agents.3 claude` | 21 | 0 | 2026-05-13T13:49:40 | claude |
| ashigaru4 | `queue/inbox/ashigaru4.yaml` | `ashigaru4 multiagent:agents.4 claude` | 18 | 0 | 2026-05-13T13:58:34 | claude |
| ashigaru5 | `queue/inbox/ashigaru5.yaml` | `ashigaru5 multiagent:agents.5 claude` | 15 | 0 | 2026-05-12T11:10:35 | claude |
| ashigaru6 | `queue/inbox/ashigaru6.yaml` | `ashigaru6 multiagent:agents.6 claude` | 14 | 0 | 2026-05-13T13:49:40 | claude |
| ashigaru7 | `queue/inbox/ashigaru7.yaml` | `ashigaru7 multiagent:agents.7 claude` | 18 | 0 | 2026-05-13T13:49:40 | claude |
| gunshi | `queue/inbox/gunshi.yaml` | `gunshi multiagent:agents.8 codex` | 39 | 1 | 2026-05-13T14:00:51 | codex |

10 体 × (file + watcher + agent) 三点整合済、本 plan の **整理対象外**。

### 2.2 orphan alias inbox (= 整理候補、本 task は仕様化のみ)
| inbox file | msg | unread | last_ts | watcher | 真因 / 用途仮説 |
|---|---|---|---|---|---|
| `gunshi2.yaml` | 12 | 0 | 2026-05-10T18:39:09 | 不在 | 旧 2 軍師体制残骸 (= cmd_018_017 1 軍師再定義で廃止された alias) |
| `ieyasu.yaml` | 133 | **103** | 2026-05-12T11:03:59 | 不在 | `auto_forward_shogun_to_ieyasu.sh` (= 2026-05-12 23:05 御差配) bridge で shogun.yaml 自動転送、read 主体不在で滞留 |
| `shogun_from_main.yaml` | 9 | **9** | 2026-05-13T13:50:39 | 不在 | shogun の MC 経路 sub-inbox (= ieyasu → shogun chain での MC マーカー)、read 主体不在 |
| `shogun_from_sc.yaml` | 53 | **53** | 2026-05-12T11:45:31 | 不在 | shogun の SC 経路 sub-inbox (= 旧 SC 直接 push 経路名残)、read 主体不在 |
| `maeda.yaml` | 1 | **1** | 2026-05-13T13:42:53 | 不在 | 信長 → 本多 (= SC karo) SC pivot directive、persona alias 「本多」=「SC karo」用 |

合計 **未読 166 件 滞留** (= 5 alias inbox 合算)、現状 read 経路無し。

### 2.3 sender alias (= 自 inbox 無、provenance marker)
| sender_id | 出現先 | 用途仮説 | candidate_action |
|---|---|---|---|
| `karo_sc` | ashigaru1/3/4 inbox の from field、`scripts/test_validate_cross_pc_directive.py` 内 `via_agent="karo_sc"` | karo 同一実体の cross-PC provenance marker | **retain** (= agent 識別ではない、廃止対象外) |
| `shogun_from_main` | gunshi/ieyasu/karo/shogun inbox の from field | bridge mechanism identifier | alias 統合 plan と連動整理 |
| `auto_git_sync` | ieyasu/karo/shogun inbox の from field、`scripts/auto_git_sync.sh` (= systemd timer) 発信 | infrastructure daemon 通知経路 | **retain** (= 正当な daemon identity) |

## 3. alias 統合判定 (= 候補 specification)

### 3.1 候補 A: `gunshi2.yaml` 廃止
- **判定根拠**: 5/10 以降 traffic 0、現 1 軍師 (`gunshi`) で全 traffic 処理済、watcher 不在で発信側にも書き込み実害無し
- **alias 関係**: `gunshi` (現役) ↔ `gunshi2` (旧 2 軍師体制 alias、cmd_018_017 で廃止済 persona)
- **specification (= 別 cycle 実行手順案)**:
  1. karo 起案: `queue/archive/inbox_alias_廃止/` ディレクトリ新設 + `gunshi2.yaml` を `git mv` で移動
  2. 陛下御差配仰ぎ: archive 移動 + commit 承認
  3. SessionStart hook (`scripts/session_start_hook.sh`) line 64 の persona alias 例示は本 alias と無関係 (= 同行 'karo=hideyoshi、ashigaru4=maeda' 例示は他 alias)、変更不要
  4. 影響範囲: 0 (= 発信実績 5/10 で止、watcher 不在、read 主体不在)

### 3.2 候補 B: `maeda.yaml` 統合
- **判定根拠**: 5/13 13:42 信長発 SC pivot directive 1 件のみ、本文中 `to: maeda (= '本多殿 (= SC karo)')` で persona alias を明示、`session_start_hook.sh` line 64 例示 'ashigaru4=maeda' と同種 persona 二重化
- **alias 関係**: `karo` (現役 MC) ↔ `maeda` (= 本多正信、SC karo persona alias) — **同一 role の二重 alias、廃止候補**
- **specification (= 別 cycle 実行手順案)**:
  1. karo 起案: SC karo 専用 inbox の必要可否を陛下御差配仰ぎ判定
     - case 1 (SC karo 専用 inbox 必要): `karo_sc.yaml` を正規 inbox として新設 + watcher process 起動 (= live wired 化) → `maeda.yaml` 内容を `karo_sc.yaml` に移送 + archive
     - case 2 (SC karo 専用 inbox 不要): `maeda.yaml` 内容を `karo.yaml` に統合 + archive
  2. session_start_hook.sh の persona alias 例示 (= line 64 'ashigaru4=maeda') を実態整合に更新 (= karo alias 例示に変更 or 例示削除)
  3. 影響範囲: 信長発 SC pivot directive 経路のみ、karo 側読み込みで即解消可

### 3.3 候補 C: `ieyasu.yaml` + `shogun_from_main.yaml` + `shogun_from_sc.yaml` 整理
- **判定根拠**: ieyasu = 103 unread / shogun_from_main = 9 unread / shogun_from_sc = 53 unread、合計 **165 unread 滞留**、watcher 不在で read 主体無し
- **alias 関係**: `shogun` (現役) ↔ `ieyasu` (= 徳川家康 alias、`auto_forward_shogun_to_ieyasu.sh` bridge で shogun mirror) ↔ `shogun_from_main` (= MC 経路 sub) ↔ `shogun_from_sc` (= SC 経路 sub)、**4 alias 1 role**
- **specification (= 別 cycle 実行手順案)**:
  1. karo 起案 + 陛下御差配仰ぎ:
     - sub-decision 1: `auto_forward_shogun_to_ieyasu.sh` bridge 継続可否 (= 続行なら ieyasu inbox 用途明示 + read 主体配置、停止なら bridge 廃止 + archive)
     - sub-decision 2: shogun_from_main / shogun_from_sc は経路マーカー sub-inbox としての必要可否 (= 現状 read 主体無しで滞留)
  2. 廃止判定の場合:
     - `systemctl --user stop` で `auto_forward_shogun_to_ieyasu.sh` 起動 mechanism 停止 (= 信長殿のみ操作可、ashigaru/karo 範囲外)
     - `ieyasu.yaml` + `shogun_from_main.yaml` + `shogun_from_sc.yaml` を `queue/archive/inbox_alias_廃止/` に `git mv`
     - shogun.yaml 単一化、from field の `shogun_from_main` 識別子は provenance marker として retain
  3. 統合判定の場合: read 主体 (= gunshi or karo or 新 agent) を配置 + watcher process 起動 (= live wired 化)
  4. 影響範囲: shogun_audit_request chain (= cmd_020 新規範第 5 件) との接続確認必要

### 3.4 整理候補 summary 表
| inbox file | 整理 candidate | role 関係 | 推奨 action | 実行主体 |
|---|---|---|---|---|
| `gunshi2.yaml` | A | gunshi の旧 2 軍師体制 alias | archive | karo + 陛下御差配 |
| `maeda.yaml` | B | karo の SC alias (= 本多) | karo.yaml 統合 or karo_sc.yaml 新設 | karo + 陛下御差配 |
| `ieyasu.yaml` | C | shogun mirror (= bridge 経由) | bridge 停止 + archive (= 信長殿経由) | 信長 + 陛下御差配 |
| `shogun_from_main.yaml` | C | shogun MC 経路 sub | shogun.yaml 統合 + archive | karo + 陛下御差配 |
| `shogun_from_sc.yaml` | C | shogun SC 経路 sub | shogun.yaml 統合 + archive | karo + 陛下御差配 |

## 4. bridge mechanism (`auto_forward_shogun_to_ieyasu.sh`) 整理 path

### 4.1 現状 evidence
- script 在: `scripts/auto_forward_shogun_to_ieyasu.sh` (= 2026-05-12 23:05 御差配で装備)
- 動作仕様: `queue/inbox/shogun.yaml` の新規メッセージを `queue/inbox/ieyasu.yaml` に自動転送
- log 出力: `queue/reports/auto_forward_shogun_to_ieyasu.log`
- 起動 mechanism: systemd timer or supervisor 経由想定 (= 別 doc で詳細、本 task 範囲外)

### 4.2 整理 path specification (= 別 cycle 実行手順案)
1. karo 起案: `auto_forward_shogun_to_ieyasu.sh` の継続可否を陛下御差配仰ぎ判定
2. 継続判定の場合: ieyasu inbox の read 主体配置 + watcher process 起動で live wired 化
3. 廃止判定の場合:
   - 信長殿: `pkill` 全面禁 (= D006 ABSOLUTE BAN)、`ps -fp` で specific PID 特定 + `kill PID` (= D006-EXC 適用、shogun のみ permitted)
   - karo: bridge 停止 ack 後、`ieyasu.yaml` を `queue/archive/inbox_alias_廃止/` に `git mv`
   - 別 cycle で from field の `shogun_from_main` provenance marker 整理 + script archive

## 5. SessionStart hook warning #1 解消 path (= 5 step)

`scripts/session_start_hook.sh` の `inbox_integrity_verify()` 関数 (= line 43-121) は agent_id ↔ inbox_file
不在を warning #1 で出力する。**現状 alias retain で warning 発生は理論上のみ**、解消 path は alias 整理と
連動する。

### 5.1 解消 step (= specification)
1. **Step 1**: alias 統合判定 (= 本文書 §3 候補 A/B/C を karo + 陛下御差配で確定)
2. **Step 2**: karo が `queue/archive/inbox_alias_廃止/` ディレクトリ新設 + 廃止対象 inbox file を `git mv` で archive
3. **Step 3**: 陛下御差配仰ぎ commit 承認 + push (= F007 例外整合下手動)
4. **Step 4**: SessionStart hook (`scripts/session_start_hook.sh`) line 64 の persona alias 例示
   `'persona alias (例: karo=hideyoshi、ashigaru4=maeda)'` を実態整合に更新 (= 廃止済 alias 例示削除 or
   現役 alias 例示に置換)
5. **Step 5**: 全 agent (= shogun/karo/ashigaru1-7/gunshi) の SessionStart hook 出力で warning #1 不発を verify
   (= 起動 / `/clear` / compaction 全 matcher で機械確認)

### 5.2 受け入れ判定
- warning #1 が全 agent 起動経路で 0 件発生 (= log: `logs/session_start_hook.log` で機械確認)
- archive 対象 inbox file 全件が `queue/archive/inbox_alias_廃止/` 配下に存在
- session_start_hook.sh の persona alias 例示が現役 alias と整合

## 6. `inbox_watcher.sh` args 整合 verify 規範

### 6.1 現状 verify mechanism
SessionStart hook (`scripts/session_start_hook.sh` line 43-121) の `inbox_integrity_verify()` 関数が:
- **Check 1** (warning #1): `agent_id ↔ inbox_file` 不在検出
- **Check 2** (warning #2): `inbox_watcher.sh` 第 1 引数 (= agent_id) 該当 process 不在検出
- **Check 3** (warning #3): `inbox_watcher.sh` 第 2 引数 (= pane_target) と現在 pane drift 検出

`ps -eo args=` 経由厳密 parse (= `pgrep` 単独禁、家康 13:55 SC pivot 真因防止)。

### 6.2 操作禁則
warning 検出後の **訂正実行は ashigaru/gunshi 範囲外**:
- watcher process 再起動 → karo 経由 (= 信長殿 SC 復旧 trigger 含む)
- tmux pane 操作 → 信長殿経由
- persona 切替実行 → 陛下御差配経由

ashigaru/gunshi の役務は **warning 内容 ack + karo へ inbox_write 報告** で停止 (= F002 違反 risk 防止)。

### 6.3 機械 verify command (= 別 cycle 適用)
```bash
# 各 live wired agent について現行 watcher args ↔ session_start_hook 期待 args 整合を verify
ps -eo args= | grep -F 'inbox_watcher.sh' | grep -v ' grep ' \
  | awk '{print $2, $3, $4}'  # agent_id pane_target cli_type
# → 期待: shogun shogun:main.0 claude / karo multiagent:agents.0 claude / ashigaru1-7 multiagent:agents.1-7 claude / gunshi multiagent:agents.8 codex
```

## 7. 実行範囲外明示 (= 本 task は plan 文書化のみ)

| 項目 | 本 task 範囲 | 別 cycle 委譲先 |
|---|---|---|
| 現行 state inventory (= live wired 10 + orphan alias 5 件) | **実行** | — |
| alias 統合判定 specification 起案 | **実行** | — |
| persona 廃止候補 specification 起案 | **実行** | — |
| `inbox_watcher.sh` args 整合 verify 規範文書化 | **実行** | — |
| SessionStart hook warning #1 解消 path 文書化 | **実行** | — |
| static source-contract test 4 件起案 (= AC3) | **実行** | — |
| **live inbox file mutation (= rename / delete / merge / overwrite)** | **不実行** | karo + 陛下御差配経由別 cycle |
| **watcher process 操作 (= kill / restart / reconfigure)** | **不実行** | 信長殿 (= shogun) 経由別 cycle |
| **SessionStart hook 変更** | **不実行** | karo 起案 + 陛下御差配経由別 cycle |
| **`auto_forward_shogun_to_ieyasu.sh` bridge 起動 / 停止** | **不実行** | 信長殿経由別 cycle |
| **archive ディレクトリ新設 + `git mv` 実行** | **不実行** | karo + 陛下御差配経由別 cycle |

## 8. 完了基準

本 plan 文書は以下を全件充足:
- §2 で live wired 10 体 + orphan alias 5 件を機械観測 evidence 付き列挙済
- §3 で alias 統合判定候補 A/B/C を specification 化済 (= 各候補に判定根拠 + 実行手順案 + 影響範囲)
- §4 で `auto_forward_shogun_to_ieyasu.sh` bridge 整理 path specification 化済
- §5 で SessionStart hook warning #1 解消 path を 5 step specification 化済 + 受け入れ判定明示
- §6 で `inbox_watcher.sh` args 整合 verify 規範 + 操作禁則 + 機械 verify command 明示済
- §7 で実行範囲外を 11 項目 × 範囲 / 委譲先で明示済
- §1.2 で live inbox file mutation 0 件 + watcher process 操作 0 件 + SessionStart hook 変更 0 件を厳守宣言済

実行は陛下御差配経由別 cycle に委譲、本 task はここで完了。
