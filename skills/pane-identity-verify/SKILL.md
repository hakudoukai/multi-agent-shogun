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

拙者将軍が「multiagent:agents.4 = gunshi」と pane 番号だけで判定し、`tmux split-window` で agents.4 に重複 gunshi pane を新設。実際は agents.3 = gunshi で生存中だった。

詳細: [docs/incident_logs/2026-05-07_pane_misidentification.md](../../docs/incident_logs/2026-05-07_pane_misidentification.md)

教訓: **「pane index = agent 名」の暗黙マッピングを絶対に推測しない**。
