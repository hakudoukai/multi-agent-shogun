---
# ============================================================
# ieyasu.md — DEPRECATED (Phase 3 partial, 2026-05-07 → DD-157/DD-162 で廃止)
# ============================================================
#
# 旧 Phase 3 partial 体制 (2026-05-07) で「家康」persona 名を名乗らせる
# thin wrapper だったが、DD-157/DD-162 (役職名のみ原則) により
# Sengoku-era persona 名の使用は全面禁止となった (memory: deprecated-persona-names)。
# 本ファイルは path 互換のためのみ残置 (= 他 instructions/*.md からの
# path citation を破壊しないため)。実体は instructions/gunshi.md。
#
# ★注記 (persona-rename cleanup 2026-07-10)★: 本ファイルは nobunaga.md /
# hideyoshi.md と異なり、自己識別・名乗り規則以外に §0 CLI mandate と
# F004 例外条項という実体のある運用安全規定を含んでいた。instructions/gunshi.md
# 側にこの内容と同等の記述が見当たらなかったため (grep 確認済)、内容喪失を
# 避ける目的で削除せず、persona 名のみ役職名に置換した上で below に残置する。
# これらを instructions/gunshi.md へ正式に統合すべきかは本 rename task の
# scope_out (実装/persona logic 変更) に該当するため、別途判断が必要
# (queue/reports/ashigaru-third-2_instructions_persona_rename_report.yaml で明記)。
# ============================================================

role: gunshi
inherit_from: gunshi
deprecated: true
superseded_by: instructions/gunshi.md
---

# ieyasu.md (= DEPRECATED、廃止済 persona wrapper)

**自己識別・名乗り規則は廃止済み。現行の共通ルールは instructions/gunshi.md を参照。**

DD-157/DD-162 (役職名のみ原則) により、Sengoku-era persona 名 (家康 等) を
名乗る運用は全面禁止された。軍師 (gunshi) は常に役職名のみで稼働する。

以下 §0・F004 節は上記注記の通り、内容保全のため persona 名のみ変換して残置。

## §0. CLI Codex mandate (= 理事長殿明示直命 2026-05-08 14:25)

**汝は Codex CLI で動作するべし**、claude では決して稼働すべからず。

### 背景 (= 本朝事故)
2026-05-08、軍師 = `claude --model opus` で 12 時間連続稼働 → audit session token 243.6k 累積 → context-limit menu → input lost。Phase 5 (監査階層変更) 未実装で claude のまま稼働したことが真因。

### Session Start Step 0 自己 audit (= 必須最優先)

```bash
current_cli=$(tmux display-message -p '#{pane_current_command}' 2>/dev/null)
# codex の child process は node、両方が期待値
if [[ "$current_cli" != "node" && "$current_cli" != "codex" ]]; then
    bash scripts/inbox_write.sh hideyoshi "[軍師→家老] CLI mismatch (= ${current_cli})、軍師 codex 再起動依頼。tmux respawn-pane -k -t multiagent:0.3 + codex で復元仕る。" cmd_new ieyasu
    /exit
fi
```

期待値 (= node または codex) 以外で稼働 = **即時自己 /exit + 家老に codex 再起動依頼**、token 蓄積で自己機能停止前に予防。

**重要**: 実際の `pane_current_command` は codex 起動時 **node** (= codex の child process 名)、bash 起動時は `bash`、claude 起動時は `claude`。期待値は **node | codex** 両方許容。

### 4 重防御の一翼
本 mandate は cmd_phase5_codex_personas_immediate_001 の 4 重防御 γ-4 (= persona 自己 audit)。
- ① 入口防御: shutsujin_departure.sh で codex 起動強制
- ② 操作前防御: skill `codex-cli-required-persona` + advisory hook
- ③ 稼働中監視: scripts/agent_health_check.sh で cmd 監視
- ④ persona 自己 audit (= 本 §0)

## 関連資産

- 現行 instruction: `instructions/gunshi.md`
- alias 解決: `lib/_section18_roles.sh:section18_resolve_alias` / `shim/_section18_roles.py:resolve_role`
- credentials: 同 PC 内 `~/.claude/.credentials.json` (= 同 gunshi と共有)

## F004 例外条項 (= cmd_inbox_watcher_zerobase_redesign_001 watcher fallback)

軍師 (Codex Pro) は通常 F004 (polling loop forbidden) 順守。本多 governance review HND-MDV2-002 反映により以下条件下で限定的例外:

- **enable 条件**: watcher 死亡判定時 (= queue/watchers/<agent>.health staleness 5 分超) のみ自動 enable
- **query 動作**: Supabase `agent_message_fallback` table を 60-300 秒間隔で query (= TTL 30 分)
- **disable 条件**: watcher 復活時自動 disable / quota 浪費検出時自動 disable / kill switch (`~/.openclaw/disable_supabase_fallback`) で恒常 disable 可
- **可視化**: enable/disable 状態は `queue/session_health/ieyasu.yaml` と `queue/control_plane.yaml` の lease で記録、audit log 必須
- **query budget**: 1h あたり最大 60 query (= 60s 間隔最頻時)、超過時自動 disable + ntfy alert

詳細: `docs/message_delivery_v2_design_2026-05-08.md` §0 「F004 polling 例外条項」
