---
name: codex-cli-required-persona
description: 家康 (ieyasu) と本多 (honda) は Codex CLI 必須 persona、claude で誤起動された場合に advisory 警告で検知 (§19.3 ブロック禁止順守)
type: pre_action_check
---

# codex-cli-required-persona — Codex CLI 必須 persona の cli mismatch 検知

## 目的

家康 (ieyasu) と本多 (honda) は **Codex CLI (= デコポン、ChatGPT Pro)** 必須 persona。
claude などの別 CLI で誤起動された場合、**advisory 警告で検知** し、信長/家老/persona 自身に再起動を促す。

## 背景 (= 学習元事故)

2026-05-08 朝、家康が `claude --model opus` で 12 時間連続稼働 → audit session token 243.6k 累積 → context-limit menu → input lost。
真因: **Phase 5 (= 監査階層変更) 未実装で、家康が claude のまま稼働、token 蓄積問題が構造的に発生**。

本 skill は同型事故の再発防止、4 重防御 (= shutsujin / skill / agent_health_check / persona Session Start) の operate-time 検知層。

## §19.3 順守

- **絶対にブロックしない** (= `|| true` + exit 0)
- stderr 警告のみ
- timeout 5 秒
- 違反検知時も操作続行を妨げない

## 検知ロジック

1. tmux list-panes で全 pane を scan
2. `@agent_id ∈ {ieyasu, honda}` の pane を抽出
3. `pane_current_command` を確認
4. `codex` 以外なら stderr 警告 (= 「家康/本多 が claude で稼働、Phase 5 違反、再起動推奨」)
5. exit 0 (= ブロックなし)

## チェックスクリプト

`scripts/checks/codex_cli_required_persona.sh`

## PreToolUse hook 登録案

`.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "bash $CLAUDE_PROJECT_DIR/scripts/checks/codex_cli_required_persona.sh || true",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

`|| true` 必須、絶対にブロックしない。

## 期待される警告例

```
[codex-cli-required-persona] WARN: ieyasu pane (multiagent:0.3) is running 'claude' instead of 'codex'.
  Phase 5 violation. Restart with codex CLI to prevent token accumulation events.
  Re-launch via: tmux respawn-pane + codex
```

## 関連資産

- docs/cmd_phase5_codex_personas_immediate_001_draft.md (= 4 重防御 cmd)
- instructions/ieyasu.md (= 家康 persona)
- instructions/honda.md (= 本多 persona)
- shutsujin_departure.sh (= 入口防御、起動時 codex 強制)
- scripts/agent_health_check.sh (= 稼働中監視、Phase γ-3)
- skills/pane-identity-verify/SKILL.md (= 同系の §19 skill)
- memory/nobunaga_persona_strong_rule.md (= 信長強権境界、F001 順守)

## 改訂責務

本 skill の改訂は **理事長殿の専権事項**。信長・家老・家康は提案のみ可。
