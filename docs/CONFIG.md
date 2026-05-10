# 設定 File 階層 — multi-agent-shogun-newbuild

竹中半兵衛 (謀の眼) 監査指摘 f2 への対応 (= 2026-05-10)。
設定 file の役割分担と優先順位を明示、SSoT 原則の曖昧さ解消。

## 設定 File 一覧

| File | 種別 | 用途 | 真実源 (SSoT) | git 管理 |
|------|------|------|---------------|---------|
| `config/settings.yaml` | YAML | **agent CLI 定義** + 編成 + tmux 構成 + 通信路 | ✅ 全 PC 共通 | ✅ commit |
| `config/settings.local.yaml` | YAML | PC 個別 override (= screenshot.path 等) | local 優先 | ❌ gitignored |
| `.claude/settings.json` | JSON | **Claude Code hook + permission** | ✅ 全 PC 共通 | ✅ commit |
| `.claude/settings.local.json` | JSON | PC 個別 Claude Code override | local 優先 | ❌ gitignored |
| `config/ntfy_auth.env` | env | ntfy push 通知認証 (= secret) | ✅ PC 個別 | ❌ gitignored |
| `config/ntfy_auth.env.sample` | env | ntfy_auth.env の template | — | ✅ commit |

## 優先順位 (= merge 順序)

### YAML 系 (config/settings.yaml)

```
config/settings.yaml (= base, 全 PC 共通)
    ↓ override (= local 優先)
config/settings.local.yaml (= PC 個別)
```

読込側 script の責務 (= 慣例):
```bash
# 例: 通常設定読込
cfg=$(cat config/settings.yaml)
# local override が存在すれば merge
[ -f config/settings.local.yaml ] && cfg=$(yq -y '. * (input)' config/settings.yaml config/settings.local.yaml)
```

### JSON 系 (.claude/settings.json)

```
.claude/settings.json (= base、Claude Code 自動読込)
    ↓ override
.claude/settings.local.json (= PC 個別、Claude Code 自動 merge)
```

Claude Code は両 file を**自動 merge**、後者優先。手動 merge logic 不要。

## 各 File の責務 詳細

### config/settings.yaml — 全 PC 共通 真実源

```yaml
language: ja
shell: bash

cli:
  default: claude
  agents:
    shogun: claude
    karo: claude
    ashigaru1: claude
    # ... ashigaru6
    gunshi: codex      # 軍師1 一次監査 (黒田/直政)
    gunshi2: gemini    # 軍師2 二次監査 (竹中/阿茶)

tmux:
  sessions: [...]

supabase:
  project_id: ...
  pc_handshake_required: true

github:
  repo: hakudoukai/multi-agent-shogun-newbuild
  remote: newbuild
  upstream_repo: yohey-w/multi-agent-shogun

screenshot:
  path: /mnt/c/Users/User/Pictures/Screenshots/  # default、PC 個別なら local で override

clinic_id: hakudoukai_main
```

**SSoT 適用**: `lib/agent_pane_mapping.sh` (= 竹中 f1 是正で追加) は本 file の `cli.agents` を唯一の真実源として agent → pane 解決。

### config/settings.local.yaml — PC 個別 override (= 任意)

例: SecondPC で Windows username が `Taro` の場合:
```yaml
screenshot:
  path: /mnt/c/Users/Taro/Pictures/Screenshots/
```

例: ある PC でだけ別 ntfy_topic 使用:
```yaml
ntfy_topic: hakudoukai-test-secondpc
```

存在しない場合は base の値が使われる、何も書かなくて良い。

### .claude/settings.json — Claude Code 全体設定

```jsonc
{
  "hooks": {
    "SessionStart": [...],   // session 開始時注入
    "Stop": [...]            // turn 終了時 inbox 処理
  },
  "permissions": {
    "allow": [...],          // 許可する Bash パターン
    "deny": [...]            // 禁止する Bash パターン (= D001-D008)
  },
  "spinnerVerbs": {...},     // 戦国風 spinner
  "enableAllProjectMcpServers": true
}
```

**path は `$HOME` 動的展開で両 PC 対応** (= 2026-05-10 commit 57c7f42)。

### .claude/settings.local.json — PC 個別 Claude Code override

絶対 path / 特殊 hook を PC 別に持ちたい時のみ。Claude Code が自動 merge。
通常は不要 (= `$HOME` 展開で大半 cover)。

## 関連 doc

- `skills/shogun-ssh-cross-pc/SKILL.md` の「Cross-PC Portability」section — 3 段戦略 (相対 path / `$HOME` / settings.local) の使い分け
- `lib/agent_pane_mapping.sh` — settings.yaml `cli.agents` を SSoT として agent → pane 解決
- `skills/shogun-system-coherence/SKILL.md` — 三者整合性検査 (settings.yaml ↔ tmux ↔ ps)

## 鉄則 (= 竹中 f2 是正の精神)

1. **同一 key を複数 file に記載しない** — 真実源を曖昧化する
2. **PC 個別差分は local file へ** — base file は git で全 PC 共有
3. **設定読込は lib helper 経由** — 個別 script で yaml parse 禁
4. **新 key 追加時は本 doc 更新** — 役割不明な孤児 key を作らぬ

## 監査 (= 竹中の眼)

本 doc 不在時 (= 2026-05-10 朝以前) の状況:
- `screenshot.path` が hardcoded だが PC 別必要かつ override 機構不在
- `.claude/settings.json` の `command` path が絶対 hardcode で MainPC 限定
- 新 yaml key 追加が個別判断で SSoT 原則曖昧

→ 本 doc + commit 57c7f42 ($HOME 展開) + commit 7418ed7 (settings.local.yaml convention) で構造的に解消。
