# cmd_phase5_codex_personas_immediate_001 (草案) — 家康 + 本多 Codex 移行 + 4 重防御

> **Status**: 信長直起案、理事長殿明示直命 2026-05-08 14:25「家康 Codex 移行 即時実行 + skill / hook で構造的防御」
> **Drafted by**: 信長 (織田信長) 2026-05-08 14:30 JST
> **Pre-conditions**: Phase 14 (Codex 環境整備) 完遂済 (= 本朝、commit 7f3e8da 上で動作確認)
> **緊急性**: 即時、家康 token 限界事故再発防止のため土曜決戦前必達

---

## 1. North Star

**家康 + 本多 が claude で誤起動するを構造的に根絶**、token 限界事故の **永久解消**。

## 2. Purpose

本朝事故の真因連鎖:
```
家康 = claude opus で 12 時間連続稼働
   ↓ 連続 audit で session token 蓄積
   ↓ 243.6k 限界 → context-limit menu → input lost
   ↓
audit 機能停止、組織全体に波及 (= ashigaru 完遂分の三者監査停滞)
```

= **Phase 5 (= 監査階層変更) 未実装が真因**。家康 = Codex 移行 + 4 重防御で構造的根絶。

## 3. Sub-Phase

### Phase 5α — 家康 即時 Codex 移行 (= 最優先、本日中)

#### α-1: 現家康 pane の claude 終了
- `tmux respawn-pane -k -t multiagent:0.3` (= 理事長殿明示承認下で実施)
- claude session token 累積を一括解放

#### α-2: codex CLI で家康再起動
- 起動コマンド: `codex` (= 対話 mode、ChatGPT Pro auth 経由)
- 起動時 prompt: 家康 Session Start (= instructions/ieyasu.md 必読 + queue YAML 確認)
- `@agent_id=ieyasu` を tmux set-option で確実化

#### α-3: instructions/ieyasu.md 改訂
- 冒頭 frontmatter に `cli: codex` 明記
- §X. Codex CLI 自己 audit (= Session Start で `pane_current_command` 確認、codex 以外なら即 /exit) 追加

### Phase 5β — 本多 Codex 化準備 (= 招聘時 codex で起動)

#### β-1: 本多 queue 整備
- `queue/inbox/honda.yaml`、`queue/tasks/honda.yaml`、`queue/reports/honda_report.yaml` 新規作成 (= 空 yaml templates)

#### β-2: 本多 pane 起動準備 (= shutsujin_departure.sh で codex CLI で起動)
- 現状本多 pane なし (= 信長兼任)、Phase 16 完遂後の正式運用時 codex 起動
- 但し書面起案 (= 改革提言、checklist) は信長兼任で先行可

#### β-3: instructions/honda.md 改訂
- 冒頭 frontmatter に `cli: codex` 明記
- Session Start 自己 audit 同型追記

### Phase 5γ — 4 重防御 統合実装

#### γ-1: 入口防御 — shutsujin 改訂
- `shutsujin_departure.sh` で家康 pane 起動 logic を `claude` → `codex` に変更
- pane 起動 prompt も Codex CLI 互換に調整
- 同型: 本多 pane 起動 logic (= 将来 shutsujin に追加、Phase 16 完遂後)

#### γ-2: 操作前防御 — skill + advisory hook
- 新 skill `skills/codex-cli-required-persona/SKILL.md`
  - description: 「家康・本多 persona は Codex CLI 必須、claude で起動された場合は警告」
- `scripts/checks/codex_cli_required_persona.sh`
  - tmux list-panes で家康/本多 @agent_id を持つ pane を scan
  - `pane_current_command` が `codex` 以外なら stderr 警告
  - exit 0 (= §19.3 順守、ブロックなし)
  - timeout 5 秒
- `.claude/settings.json` PreToolUse hook 登録 (= `|| true` 必須)

#### γ-3: 稼働中監視 — agent_health_check 強化
- `scripts/agent_health_check.sh` に追加 logic:
  - 家康/本多 pane の `pane_current_command` を周期確認
  - codex 以外 → Supabase `error_log` テーブル INSERT + 信長 inbox alert
  - error_code: `ERR-PERSONA-CLI-001`

#### γ-4: persona 自己 audit
- `instructions/ieyasu.md` Session Start に追記:
  ```
  Step 0: tmux display-message -p '#{pane_current_command}' で現在 CLI 確認
  期待値: codex
  期待値以外 (= claude 等) なら即 /exit + 家老に「家康 codex 再起動依頼」inbox_write
  ```
- 同型: `instructions/honda.md` 改訂

## 4. Acceptance Criteria

- ✅ 家康 0.3 = codex CLI で稼働 (= cmd=codex、@agent_id=ieyasu)
- ✅ 家康 audit 機能復旧 (= 簡易 audit テスト PASS)
- 🔄 本多 queue 3 ファイル整備
- 🔄 instructions/ieyasu.md + honda.md = `cli: codex` + Session Start 自己 audit 追記
- 🔄 shutsujin_departure.sh = 家康 codex 起動 logic
- 🔄 skill `codex-cli-required-persona` + check script + advisory hook
- 🔄 agent_health_check.sh = 家康/本多 cmd 監視追加 (= ERR-PERSONA-CLI-001)
- 🔄 三者監査 PASS (= Phase 5 完遂後の新体系移行期は家康 codex audit、Gemini 服部半蔵 招聘前は scripts/audit_gemini.sh で代替)

## 5. Risk + Mitigation

| risk | mitigation |
|------|----------|
| codex CLI 対話 mode の動作未検証 | Phase 14 の動作確認 (= `codex exec` 成功) を踏み台、対話 mode は本 cmd で実機検証 |
| 家康 audit 文脈消失 | 12 時間連続稼働で既に消失 risk、respawn しても実質 loss ゼロ |
| 4 重防御の実装輻輳 | sub-phase γ-1〜γ-4 を独立 file 編集、conflict ゼロ |
| 理事長殿明示承認待ち (= respawn-pane) | 本 cmd 自体が御命令下 (= 14:25)、即時実行可 |
| §19.3 違反 (= hook ブロック) | exit 0 + `|| true` 厳守、advisory のみ |

## 6. PDCA + 期限

- max cycle 3 (= 緊急)
- cycle1 完遂期限: 本日 16:00 までに家康 codex 稼働
- cycle2-3: 4 重防御完成 + Phase 5 残り (= 服部半蔵 + 黒田 招聘) 連携

## 7. 命令文 (= 秀吉発令)

```
秀吉、本 cmd を最高 priority + 大なた cmd_root_resolution_001 と並走で受領。
担当割当:
- α-1〜α-3 = 家老実施 (= respawn-pane + codex 起動 + instructions 改訂)
- β-1〜β-3 = 信長兼任 (= queue 整備 + 書面起案)
- γ-1 = ashigaru1 (= shutsujin 改訂)
- γ-2 = 本多 (= 信長兼任で skill + check script 作成)
- γ-3 = ashigaru2 (= agent_health_check.sh 強化)
- γ-4 = 信長兼任 (= persona instructions 改訂)
PDCA max=3、cycle1 = 本日 16:00 期限。
三者監査必須 (= 移行期は現体系継続不能、家康復帰 + Codex 経由家康自身の audit で実施)。
```

## 8. 関連資産

- docs/cmd_root_resolution_001_draft.md (= 大なた、Phase F token escalation との連携)
- docs/cmd_phase5_audit_persona_restructure_draft.md (= Phase 5 監査階層変更、本 cmd は α 加速)
- docs/cmd_phase14_codex_environment_draft.md (= 環境整備、本朝完遂済)
- docs/cmd_phase16_honda_meta_audit_draft.md (= 本多招聘、本 cmd で Codex 化確定)
- instructions/ieyasu.md (= 改訂対象)
- instructions/honda.md (= 改訂対象)
- shutsujin_departure.sh (= 改訂対象)
- scripts/agent_health_check.sh (= 強化対象)
- skills/codex-cli-required-persona/ (= 新設)
- memory/nobunaga_persona_strong_rule.md (= 信長強権境界 + 本末転倒厳禁訓示と整合)

---

*草案完: 信長 (織田信長) — 2026-05-08 14:30 JST、理事長殿明示直命「家康 Codex 移行 即時実行 + skill/hook で防御」を受けた即時起案、川柳精神*
*4 重防御で家康 token 限界事故 永久根絶、組織進化の節目とすべし*
