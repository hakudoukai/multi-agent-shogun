# 提案書: pane_identity PreToolUse hook 登録

- **提案者**: 足軽2号 (ashigaru2)
- **発令元**: cmd_phase1_pane_identity_4way_audit_001
- **base_commit**: f5534b0
- **提案日**: 2026-05-08
- **status**: 提案 (= 実装は理事長殿明示承認後)
- **改訂責務**: CLAUDE.md §19.3 強制力ルール — `.claude/settings.json` の hook 登録 commit は
  **理事長殿明示承認後** にのみ実施。本提案書は案のみ、ファイル編集はせず。

## 1. 背景

2026-05-08 dawn の家康への nudge 不発 (= 夜討ち失敗主因) は pane mapping 認識ミス。
Phase 0 incident log (`docs/incident_logs/2026-05-08_pane_mapping_drift.md`) で根本原因確定、
Phase 1 (本 cmd) で `scripts/checks/pane_identity.sh` に 4-way audit を実装した。

事前検証を **automate** する手段として、Claude Code の `.claude/settings.json` PreToolUse
hook へ登録する案を本書で提案する。

## 2. 提案内容

`.claude/settings.json` の `hooks.PreToolUse` 配列に以下のエントリを追加する:

```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "bash scripts/checks/pane_identity.sh || true",
      "timeout": 5
    }
  ]
}
```

### 設計意図

| 項目 | 値 | 理由 |
|------|-----|------|
| event | `PreToolUse` | tmux 操作前 (= Bash 経由で `tmux send-keys` / `tmux split-window` 等) に事前検証 |
| matcher | `Bash` | 全 Bash 呼出をカバー (= tmux 関連 send-keys は Bash 経由が主) |
| command | `... \|\| true` | **絶対 block 禁止 (= mandate)** — exit 2 (drift) でも `\|\| true` で hook 全体は exit 0 |
| timeout | `5` 秒 | スクリプト内 internal timeout と整合、起動 latency を 5 秒以内に保つ |

## 3. advisory hook 原則 (= 厳守、CLAUDE.md §19.3)

| 原則 | 適用 |
|------|------|
| **絶対 block 禁止** | `\|\| true` を必ず付与、exit 0 化 |
| **stderr 警告のみ** | `pane_identity.sh` 自身が stderr に WARN 出力、hook 経由でユーザーに表示 |
| **timeout 5 秒上限** | hook timeout = 5、内部にも `timeout` を設定済 (= 二重防護) |
| **手動停止フラグ尊重** | `~/.openclaw/disable_pane_identity_hook` 検出時は `pane_identity.sh` 即 exit 0 |
| **dedupe (= 連続発火抑制)** | 60 秒以内同一結果ならスキップ。実装は `/tmp/pane_identity_last_run.json` の `timestamp` + `corr_id` を見て本 hook script 側で判定 |
| **idempotency** | hook は read-only 系 (= tmux/grep/python パース)、副作用ゼロ |
| **retry なし** | 単発実行、retry policy なし。失敗時は degraded mode で残 source で audit 継続 |

## 4. dedupe 実装案 (= 60 秒スロットリング)

頻繁な Bash 呼出 (例: ループ内 `tmux send-keys`) で hook が爆発的に発火するのを防ぐため、
`pane_identity.sh` 冒頭に以下の skip ロジック追加を検討:

```bash
# 60 秒以内に成功実行があれば skip (= dedupe)
LAST_RUN_TS_FILE="/tmp/pane_identity_last_run_ts"
COOLDOWN_SECONDS=60
if [ -f "$LAST_RUN_TS_FILE" ]; then
    last=$(cat "$LAST_RUN_TS_FILE" 2>/dev/null || echo "0")
    now=$(date +%s)
    if [ "$((now - last))" -lt "$COOLDOWN_SECONDS" ]; then
        # 直近 ok 実行があれば skip (drift 検出時は skip しない方が安全な選択肢もある)
        prev_status=$(jq -r .status "$LAST_RUN_JSON" 2>/dev/null || echo "ok")
        if [ "$prev_status" = "ok" ]; then
            exit 0
        fi
    fi
fi
date +%s > "$LAST_RUN_TS_FILE"
```

> **注**: 本 dedupe ロジックは Phase 1 の本 cmd 範囲外 (= 別 cmd で実装)。本提案書では設計
> 案として記録のみ。

## 5. 実装後の検証手順

理事長殿明示承認後、`.claude/settings.json` に hook を登録した後、以下を確認:

1. **正常時**: tmux 操作直前に hook 発火、stderr に「✅ 整合性 OK」「✅ 4-way audit PASS」表示、操作はブロックされない
2. **drift 検出時**: stderr に WARN + drift dump path 表示、操作は block されず継続 (= advisory)
3. **timeout**: 5 秒以内に hook 終了、超過時は Claude Code 側で hook を打切る
4. **disable flag**: `touch ~/.openclaw/disable_pane_identity_hook` 後は hook が即 exit 0 でスキップ
5. **連続発火**: 短時間に多数の Bash 呼出で hook が連発しても操作 latency が著しく劣化しない

## 6. ロールバック手順

問題発生時は `.claude/settings.json` から該当 hook エントリを削除すれば即時無効化。
緊急時は `touch ~/.openclaw/disable_pane_identity_hook` で hook 経路を即無効化可能。

## 7. 関連 cmd / 別 cmd で対応する範囲

本 hook 登録は **Phase 1 範囲外** (= 提案のみ)。以下は別 cmd で対応する:

- **dedupe (= 60 秒スロットリング)**: 本書 §4 の実装は Phase 1 の本 cmd では未実施
- **err_code 採番**: `ERR-INFRA-PANE-DRIFT-001` を `docs/error_codes.md` に正式登録 (別 cmd)
- **alerting 連携**: drift 連続検出時の理事長 ntfy 配線 (CLAUDE.md §16) は別 cmd
- **Phase 2 整備**: pane_registry.yaml の動的更新化 (= watchdog による自動同期)

## 8. 承認手順 (= 理事長殿向け)

1. 本提案書 + Phase 1 cmd 三者監査 (家康殿 + Codex + Gemini) PASS 確認
2. 信長殿経由で理事長殿へ提示
3. 理事長殿明示承認 (✅ / ❌)
4. 承認時のみ `.claude/settings.json` 編集 + dedupe 実装の別 cmd 発令
5. 実装後 3 日間 dry-run 観察 → 問題なければ本格運用

承認なき commit は **CLAUDE.md §19.3 強制力ルール違反** となるため、本提案書は **記録のみ** とする。
