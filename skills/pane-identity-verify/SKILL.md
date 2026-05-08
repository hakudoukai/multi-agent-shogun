---
name: pane-identity-verify
description: tmux pane を操作する前に必ず @agent_id を確認し、agent の意図と pane の実態が一致することを検証する。割り当てミスによる重複 pane 作成・他 agent の誤操作を防止。pane 番号からの推測は禁止。
---

# Pane Identity Verify

## いつ使う (= mandatory)

以下の **特定 agent を狙った tmux 操作** を実行する直前に必ず invoke:

- `tmux split-window` — 新 pane 作成 (= 隣接 pane の @agent_id 確認必須)
- `tmux kill-pane` — pane 削除 (= 削除対象が意図通りか確認必須)
- `tmux respawn-pane` — pane 内プロセス再起動
- `tmux send-keys -t multiagent:agents.N` — 特定 agent への入力送信 (= N が意図 agent か確認必須)
- `tmux set-option -p -t multiagent:agents.N @agent_id "..."` — 属性設定 (= 既に別 agent が居たら衝突)

## 使わない (= 偽陽性回避)

- `tmux capture-pane` — 読み取り専用、副作用なし
- `tmux list-panes` — 一覧表示のみ
- `tmux list-sessions` / `list-windows` — pane 単位ではない
- 全 pane への broadcast — 各 pane で同じ内容なら識別不要

## 必須チェック手順

### 単発の操作前 (= 1 pane 限定)

```bash
target="multiagent:agents.4"      # 操作対象
expected_agent="gunshi"            # 自分が操作したい agent

actual=$(tmux display-message -t "$target" -p '#{@agent_id}' 2>/dev/null)

if [ -z "$actual" ]; then
    echo "[WARN] $target に @agent_id が設定されていない (= 旧 pane / 新規未割当 / 不在)" >&2
    # 新規 split で意図的に作る場合は OK、既存 pane を期待していたなら abort
fi

if [ -n "$actual" ] && [ "$actual" != "$expected_agent" ]; then
    echo "[ABORT] $target は @agent_id=$actual。$expected_agent ではない。" >&2
    echo "        全 pane 配置: bash scripts/checks/pane_identity.sh" >&2
    exit 2
fi
```

### 全体配置の確認

```bash
bash scripts/checks/pane_identity.sh
```

期待される §18 通常 4 panes 配置:

| pane | @agent_id |
|------|-----------|
| `multiagent:agents.0` | karo |
| `multiagent:agents.1` | ashigaru1 |
| `multiagent:agents.2` | ashigaru2 |
| `multiagent:agents.3` | gunshi |
| (非常時 +1) `multiagent:agents.4` | ashigaru3 |

## 推測禁止事項

- ❌ 「pane index 4 だから gunshi だろう」
- ❌ 「shutsujin が立ち上げたから期待通りに違いない」
- ❌ 「前回確認した時はこうだった」
- ❌ 「設計記述 (CLAUDE.md / shutsujin コメント) にこう書いてある」

→ **すべて `tmux display-message -p '#{@agent_id}'` で実態を確認してから操作**。

## 失敗時の正しい行動

| 状況 | 正しい行動 |
|------|-----------|
| 期待 agent と異なる @agent_id | 操作中止、配置を再調査、誤認の根源を特定 |
| @agent_id 空 (新規 pane) | 期待した agent を新たに割り当てる前に supervisor 側設定確認 |
| pane 不在 | 全 pane list-panes で実態確認、勝手に新設しない |
| 設計記述と乖離 | **実態を真実とする** (= ドキュメントは古い可能性) |

## 過去事例

### 2026-05-07 21:14 — gunshi 重複作成事件

拙者信長が「multiagent:agents.4 = gunshi」と pane 番号だけで判定し、`tmux split-window` で agents.4 に重複 gunshi pane を新設。実際は agents.3 = gunshi で生存中だった。

詳細: [docs/incident_logs/2026-05-07_pane_misidentification.md](../../docs/incident_logs/2026-05-07_pane_misidentification.md)

教訓: **「pane index = agent 名」の暗黙マッピングを絶対に推測しない**。

### 2026-05-08 dawn — 家康 nudge 不発 (= 夜討ち失敗主因)

家康への nudge が pane 認識ミスにより不発、夜討ち失敗の主因となった。pane mapping の SSoT が
複数箇所 (CLAUDE.md §18.1 / watcher_supervisor.sh / lib/_section18_roles.sh / 実 tmux) に
散在し、相互 drift が発生していたことが根本原因。

詳細: [docs/incident_logs/2026-05-08_pane_mapping_drift.md](../../docs/incident_logs/2026-05-08_pane_mapping_drift.md)

教訓: 単発 self-identification では検出できぬ「systemic drift」がある。Phase 1 (本拡張) で
4-way audit を導入し、SSoT 二層化 (CLAUDE.md §18.1 + queue/pane_registry.yaml) で構造的
根絶を図る。

## §X. 4-way mapping audit (Phase 1 — cmd_phase1_pane_identity_4way_audit_001)

単発 pane の self-identification (= 上記 §「必須チェック手順」) に加え、**全体配置の
SSoT 整合性** を 4 source 横断で検証する仕組みを `scripts/checks/pane_identity.sh` に統合。

### 目的

pane mapping 認識ミスの構造的根絶 — 単発 check は「自分の pane」しか見ぬが、systemic drift
は複数 source 間の不整合として現れる。4-way audit は次の 4 source を横断比較し、drift を
事前検出する。

### 4 source

| source | 内容 | 役割 |
|--------|------|------|
| A. tmux 実態 | `tmux list-panes -t multiagent -F '#{pane_index}=#{@agent_id}'` | **現実 (= 真値)** |
| B. queue/pane_registry.yaml | 静的 mapping 雛形 (= 本 cmd で作成) | machine-readable mirror |
| C. watchdog 配置 | `scripts/watcher_supervisor.sh` の `start_watcher_if_missing` 行 | watcher 配置 SSoT |
| D. CLAUDE.md §18.1 | 配置表 markdown (= human-readable SSoT) | **設計 SSoT (真の SoT)** |

すべて persona alias (= shogun→nobunaga, karo→hideyoshi, gunshi→ieyasu) で正規化してから比較。

### 実行

```bash
# 整合性検証 + 4-way audit を一括実行
bash scripts/checks/pane_identity.sh
```

期待される動作:

| 状況 | exit | stderr |
|------|------|--------|
| 全 source 整合 | 0 | (なし) |
| warning (= session 不在等) | 1 | warning 一覧 |
| drift 検出 (= source 間不整合) | 2 | `[WARN] pane drift detected at index N: A=... B=... C=... D=...` |

drift 検出時は `/tmp/pane_identity_drift_<corr_id>.json` に dump 保存、
`/tmp/pane_identity_last_run.json` に最終実行情報を保持。

### advisory hook 原則 (= mandate、CLAUDE.md §19.3)

本 audit は **advisory only**。以下を厳守する:

| 原則 | 内容 |
|------|------|
| **絶対 block 禁止** | exit code は 0/1/2 のいずれか、絶対に他の操作を block しない (= mandate) |
| **stderr 警告のみ** | drift 検出時は stderr に WARN を出力するのみ、副作用なし |
| **手動停止フラグ尊重** | `~/.openclaw/disable_pane_identity_hook` 検出時は即 exit 0 でスキップ |
| **timeout 5 秒上限** | 各 source 読込に internal `timeout` を設定、合計 5 秒以内 |
| **degraded mode** | 4 source 中 1 つ以上取得失敗時はその source を skip して残 source で audit 継続 |
| **dedupe** | hook 連続発火時の抑制は呼出側 (= PreToolUse hook 提案書) に委譲 |

### PreToolUse hook 化 (= 提案、実装は理事長殿明示承認後)

`scripts/checks/pane_identity.sh` を `.claude/settings.json` の PreToolUse hook
(matcher: Bash) に登録する案 (= **advisory のみ、絶対 block しない**) を策定。

提案書: [docs/proposals/pane_identity_pretool_hook_proposal.md](../../docs/proposals/pane_identity_pretool_hook_proposal.md)

実装は **理事長殿明示承認後** にのみ実施 (= CLAUDE.md §19.3 強制力ルール厳守)。

### Phase ロードマップ (= 本 SKILL は Phase 1 範囲)

| Phase | 範囲 | 担当 |
|-------|------|------|
| Phase 0 | incident log + 根本原因確定 | 信長 (完遂、HEAD f5534b0) |
| **Phase 1** | **4-way audit + pane_registry 雛形 + advisory hook 提案** (= 本 cmd) | **足軽2** |
| Phase 2 | watchdog 動的更新 + drift 通知化 (pane_registry auto-update) | 別 cmd 発令予定 |
| Phase 3 | shutsujin_departure*.sh 改修 + §18.1 表 auto-gen 化 | 別 cmd (理事長専権部分含む) |
