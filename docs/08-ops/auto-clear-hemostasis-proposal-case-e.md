# 自動 /clear 止血 案 E — 三重改修統合設計 (CLAUDE.md + inbox_watcher.sh + agent_health_check.sh)

> 起草: 軍師 (gunshi-third) / task: `subtask_thirdpc_p0_auto_clear_hemostasis_proposal_e_integrated_design_001`
> parent_cmd: `cmd_thirdpc_p0_auto_clear_stop_bleeding_001` / parent_handshake: shogun-third `msg_20260607_184412_655f8d95` (handshake=80cb63c5 seq=36380)
> base_commit: `2d0a1e48175854c0f3b5114947b4be454b90485e` (実機照合 HEAD=`8d923785`、差分は本 docs 追加のみ→inbox_watcher.sh の line number は base と同一)
> ★D-lane 警告: 本書は ★設計文書 + diff 草案のみ★。実 script (CLAUDE.md / inbox_watcher.sh / agent_health_check.sh) の改変は理事長承認後の ★別 task★。本 task で 3 file は一切 touch しない★
> 規律: DD-157 役職名のみ / F002 報告経路 (karo-third 経由) / FKI-NO-DUP (既出 7 changes 再利用) / FKI-AUDIT-GREEN-TRUTH-01 / Watcher Design 6 原則 / [[commander-third-failsafe-redrive]] / [[third-pc-inbox-watcher-stall]] / [[stop-hook-grep-unanchored-false-positive]] / [[third-pc-agent-id-suffixed-inbox-and-phantom-inbox1]]
> 前身: `docs/08-ops/auto-clear-hemostasis-proposal.md` (既出 7 changes、inbox_watcher.sh 単一 file)

---

## 0. Critical-Thinking 補正 — task 前提の 2 件の事実誤認 (★証拠付き、phantom 排除★)

本 task description は三重改修対象として `scripts/watchdogs/agent_health_check.sh` の「L488 busy guard」を挙げるが、実機照合の結果 ★2 件の事実誤認★ を検出した。仮 green / phantom diff を撃たぬため (FKI-AUDIT-GREEN-TRUTH-01)、まず正本事実に補正する。

| # | task 前提 | 実機事実 (証拠) | 補正 |
|---|---|---|---|
| E0-1 | `scripts/watchdogs/agent_health_check.sh` | 当該 path ★不在★。実在は `scripts/agent_health_check.sh` (389 行)。`scripts/watchdogs/` は enter_restart 系 watchdog のみ | path を `scripts/agent_health_check.sh` に補正 |
| E0-2 | 「L488 busy guard」が agent_health_check.sh にある | agent_health_check.sh は 389 行で ★L488 不在★、`busy` 文字列 0 件、`/clear` actuator ★皆無★ (monitor/alerter)。「busy guard L488」の実体は ★`scripts/inbox_watcher.sh:483-494`★ (`send_cli_command` の shogun-guard + `/clear`&busy defense-in-depth) | busy guard 真因修正は ★inbox_watcher.sh 側★ に配置 (本書 Change 8) |

### E0-3 agent_health_check.sh の auto-clear への ★実際の★ 関与 (read 確認、touch 禁)

| 行 | 実体 | auto-clear 関与 | 判定 |
|---|---|---|---|
| L150-160 `send_shogun_inbox_alert` | shogun inbox へ ntfy/alert append | 通知のみ。/clear 送出なし | 非破壊 |
| L224 `grep -c 'read: false' ...inbox/${a}.yaml` | 未読数カウント | ★unanchored grep★ ([[stop-hook-grep-unanchored-false-positive]] 同族) → message 本文の literal `read: false` を誤カウントしうる | alert 数の偽陽性のみ。/clear には ★無関与★ |
| L303-356 Phase F (ERR-TOKEN-WARN/CRITICAL-001) | token≥200k/240k で「auto-clear escalation 即時要」を shogun へ ★助言通知★ | ★人間 (理事長/将軍) が判断する advisory★。スクリプトは /clear せず、idle 強制もしない | 非破壊・正当 (温存) |

→ ★結論★: agent_health_check.sh は ★busy guard を持たず、自動 /clear も idle 強制もしない★。task が想定する「agent_health_check.sh の busy 判定が busy>300s を stale-busy→idle 強制」は ★誤り★ — その挙動 (stale-busy net) は `inbox_watcher.sh:1119-1148` にあり、既出 7 changes の Change 7 (Phase 3 busy 再検査) で既に止血対象。ゆえに本書は agent_health_check.sh に ★phantom な busy-guard diff を捏造しない★。代わりに (a) 真の busy guard 真因 = inbox_watcher.sh:483 を Change 8 として修正、(b) agent_health_check.sh は ★現状温存 (Phase F advisory は正)★、L224 unanchored grep は ★Boy-Scout 別 task 候補として flag のみ★ (hemostasis 非該当、scope creep 回避)。

---

## 1. Part A — 既出 7 changes 再評価 + superset/subset 判定

### A-1 既出 7 changes verbatim quote + line range (実機 inbox_watcher.sh、1384 行)

前身 `docs/08-ops/auto-clear-hemostasis-proposal.md` §3 の 7 changes を ★再利用 (FKI-NO-DUP)★。各 anchor を ★本日実機で再照合済★ (line number 一致確認):

| Change | 対象 line (実機照合) | verbatim 主旨 | 根治対象 |
|---|---|---|---|
| **C1** new helper | `get_effective_cli_type()` (L269) 直後 | `agent_role()`=`${AGENT_ID%%-*}` / `is_command_layer_agent()` / `is_shogun_agent()` 新規 (grep 確認、重複なし) | suffix-aware 基盤 |
| **C2** send_context_reset guard | L625 `if [ "$AGENT_ID" = "shogun" ] \|\| ... "karo" \|\| ... "gunshi" ]` → `is_command_layer_agent` | RC-2 (suffix-blind 指揮層) | 自動 reset 経路 |
| **C3** busy-defer gate | L628(`fi`)〜L630(`local reset_cmd`) の間 (=L629) に `if agent_is_busy; then ... return 1` 挿入 | RC-1 (busy 貫通) | 自動 reset 経路 |
| **C4** caller defer 尊重 | L1157-1173 caller、`send_context_reset` を `if send_context_reset; then ... else (defer) fi` 化 | RC-1 (caller 側) | 自動 reset 経路 |
| **C5** busy guard suffix-aware | L1122 `if agent_is_busy && [[ "$AGENT_ID" != "shogun" ]]` → `! is_shogun_agent` | 任意整合 (shogun-third 即時 ntfy) | escalation dispatch busy guard |
| **C6** Phase3 guard suffix-aware | L1223 `elif [ "$AGENT_ID" = "shogun" ] \|\| ...` → `is_command_layer_agent` | RC-2 (Phase 3) | escalation /clear 経路 |
| **C7** Phase3 /clear 前 busy 再検査 | L1228-1233、`send_cli_command "/clear"` を `if agent_is_busy; then Escape+nudge else /clear fi` で包む | RC-1 + 補助 (stale-busy net) | escalation /clear 経路 |

★実機再照合 evidence★: `grep -n` で C2=L625 ✅ / C5=L1122 ✅ / C6=L1223 ✅ / C7=L1230 (`send_cli_command "/clear"`) ✅ / C4 caller=L1157-1158 ✅ / send_context_reset def=L617 ✅。全 anchor 一致 (phantom diff なし)。

### A-2 各 change の意図要約

- **C1**: third_pc の `-third` suffix で bare 名一致が破綻する根本 ([[third-pc-agent-id-suffixed-inbox-and-phantom-inbox1]]) を、単一 choke-point helper で吸収。
- **C2/C6**: 指揮層 (shogun/karo/gunshi, 任意 PC suffix) を ★自動 /clear 完全除外★ (RC-2 根治)。
- **C3/C4/C7**: busy 中は自動 /clear せず ★非破壊 (待機/Escape+nudge)★ に降格、配送は inbox + Stop hook + ae8083dd Stage B が保証 (RC-1 根治 + stale-busy net 補助)。
- **C5**: shogun-third も bare shogun と同等の busy 例外 (即時 ntfy)。core 安全性は C6 が担うため ★任意★。

### A-3 案 E (三重改修) coverage 判定 — ★既出 7 = SUBSET / 案 E = SUPERSET★

| 案 E 改修対象 | 既出 7 の cover | 判定 |
|---|---|---|
| **inbox_watcher.sh** 自動 reset / Phase 3 /clear (RC-1+RC-2+補助) | C1-C7 で ★完全 cover★ | **subset (= 既出が内包)** |
| **inbox_watcher.sh** L488 busy guard 真因 (`send_cli_command` shogun-guard suffix-blind) | ★未 cover★ (既出は send_context_reset / Phase 3 のみ。L483 send_cli_command は対象外) | **disjoint → 案 E 追加 (Change 8)** |
| **CLAUDE.md** L205-211 Escalation 表 | ★未 cover★ (既出は script のみ、doc 不変) | **disjoint → 案 E 追加 (Doc-R)** |
| **agent_health_check.sh** | ★該当機能なし★ (busy guard / /clear 不在、E0-2/E0-3 参照) | **vacuous (改修対象は実在せず)** |

→ ★総合判定★: 既出 7 changes は 案 E が要求する inbox_watcher.sh hemostasis の ★真部分集合 (proper subset)★。案 E は既出を ★継承 (重複設計禁)★ し、(i) Change 8 (L488 真因)、(ii) Doc-R (CLAUDE.md 改訂)、(iii) agent_health_check.sh の ★scoping note (改修なし、温存 + Boy-Scout flag)★ を加える ★superset★。

### A-4 既出で不足する箇所 (明示列挙)

1. **CLAUDE.md L205-211 Escalation 表**: 「4 min+ で /clear sent」単行が、suffix-aware/busy-defer 化後の実挙動と ★矛盾 (phantom canon)★。doc 改訂草案が必要 (Doc-R)。
2. **inbox_watcher.sh:483-494 (L488 busy guard 真因)**: `send_cli_command` の shogun-guard (L483) が ★bare 名一致★ → shogun-third が manual `clear_command` 経路で /clear 注入されうる (RC-2 と同根、既出 C2/C6 は本 path 未 cover)。Change 8 が必要。
3. **agent_health_check.sh**: 改修対象機能が ★実在しない★ → 改修なし。E0-3 の事実認定 + L224 unanchored grep の Boy-Scout flag のみ。

---

## 2. Part B — 三重改修 案 E 統合設計 (★設計文書のみ、実 script touch 禁★)

### B-1 (File 1) CLAUDE.md L205-211 Escalation 表 改訂案 — ★markdown raw 起草のみ、編集禁★

#### 現行 (L205-211 verbatim)

```markdown
**Escalation** (when nudge is not processed):

| Elapsed | Action | Trigger |
|---------|--------|---------|
| 0〜2 min | Standard pty nudge | Normal delivery |
| 2〜4 min | Escape×2 + nudge | Cursor position bug workaround |
| 4 min+ | `/clear` sent (max once per 5 min) | Force session reset + YAML re-read |
```

#### 改訂案 (Doc-R、★起草、未適用★)

```markdown
**Escalation** (when nudge is not processed):

| Elapsed | Action (ashigaru) | Action (command-layer: shogun/karo/gunshi, 任意 PC suffix) | Trigger |
|---------|-------------------|------------------------------------------------------------|---------|
| 0〜2 min | Standard pty nudge | Standard pty nudge | Normal delivery |
| 2〜4 min | Escape×2 + nudge | Escape×2 + nudge | Cursor position bug workaround |
| 4 min+ | **idle 時のみ** `/clear` (max once / 5 min)。**busy 中は /clear せず Escape+nudge に降格** | **`/clear` を一切送らない** (Escape+nudge のみ。指揮層は running context 保持が正) | Force session reset + YAML re-read |

> ★不変条件★ (本表は `scripts/inbox_watcher.sh` の suffix-aware 化と一体):
> 1. 指揮層 (shogun/karo/gunshi, `-third`/`-second`/`-main` suffix 含む) は ★自動 /clear を一切受けない★ (RC-2 根治)。
> 2. busy 中の agent には ★自動 /clear を送らない★ = 待機。配送は inbox flock append + Stop hook + ack 再送 (ae8083dd Stage B) が ★非破壊で★ 保証 (RC-1 根治)。
> 3. 明示 `clear_command` (manual kill switch) は本表の ★自動 escalation 対象外★。ただし shogun (任意 suffix) への CLI command 注入は人間操作温存のため抑止 (Change 8)。
```

### B-2 (File 2) scripts/inbox_watcher.sh — 既出 7 継承 + 案 E 追加 Change 8

#### B-2-a 既出 7 changes = ★継承 (verbatim 再掲せず、§1 A-1 表 + 前身 doc §3 を正本参照、重複設計禁)★

案 E は C1-C7 を ★無改変で継承★。FKI-NO-DUP 順守ゆえ diff の再掲はしない (前身 `docs/08-ops/auto-clear-hemostasis-proposal.md` §3 が唯一正本)。

#### B-2-b Change 8 (案 E 新規) — L488 busy guard 真因: send_cli_command shogun-guard を suffix-aware 化

★真因★: `send_cli_command` 冒頭 (L483) の shogun CLI-injection guard が ★bare 名一致★。shogun-third では false → guard すり抜け → L491 busy guard (idle なら通過) → manual `clear_command` 経路で shogun-third に /clear 注入 = 指揮層 context 破壊。bare shogun は L483 で完全保護される非対称を是正する (C1 helper 再利用、重複なし)。

実機現状 (L483-494):

```bash
    # Safety: never inject CLI commands into the shogun pane.
    if [ "$AGENT_ID" = "shogun" ]; then
        echo "[$(date)] [SKIP] shogun: suppressing CLI command injection ($cmd)" >&2
        return 0
    fi

    # Busy guard: never send /clear when agent is actively processing.
    if [[ "$cmd" == "/clear" ]] && agent_is_busy; then
        echo "[$(date)] [SKIP] Agent is busy — /clear deferred to next cycle (agent=$AGENT_ID)" >&2
        return 0
    fi
```

unified diff 草案 (★未適用★):

```diff
@@ scripts/inbox_watcher.sh:483 (send_cli_command 冒頭の shogun guard)
     # Safety: never inject CLI commands into the shogun pane.
-    if [ "$AGENT_ID" = "shogun" ]; then
+    # bare 名一致だと shogun-third 等 (PC suffix) がすり抜け、manual clear_command 経路で
+    # 指揮層 context が /clear 破壊される ([[third-pc-agent-id-suffixed-inbox-and-phantom-inbox1]])。
+    # C1 の is_shogun_agent (suffix-tolerant) で bare shogun と同等保護に揃える。
+    if is_shogun_agent; then
         echo "[$(date)] [SKIP] shogun: suppressing CLI command injection ($cmd)" >&2
         return 0
     fi
```

注: 本 change は ★shogun (任意 suffix) のみ★ に作用。karo/gunshi/ashigaru の manual `clear_command` kill switch は ★温存★ (invariant 4)。L491 busy guard 自体は無改変 (defense-in-depth として正)。

#### B-2-c suffix-blind 全 site の網羅監査表 (scope 線引き、scope creep 回避)

| line | 式 | actuator | /clear 破壊性 | 案 E scope |
|---|---|---|---|---|
| L483 | `= "shogun"` (send_cli_command) | CLI 注入 (manual /clear) | ★あり★ | **Change 8 (対象)** |
| L625 | `\|\|` 三者 (send_context_reset) | 自動 /clear | ★あり★ | C2 (継承) |
| L1122 | `!= "shogun"` (escalation busy guard) | nudge skip 制御 | 間接 | C5 (継承・任意) |
| L1223 | `\|\|` 三者 (Phase 3) | 自動 /clear | ★あり★ | C6 (継承) |
| L866 | `!= "shogun"` (send_wakeup busy 例外) | nudge (ntfy) | ★なし★ (非破壊) | 範囲外 (Boy-Scout flag) |
| L948 / L1028 / L1255 | `= "shogun"` (nudge/pane guard) | nudge/Escape | ★なし★ | 範囲外 (Boy-Scout flag) |
| L1067 | `!= "shogun"` (clear_command busy guard) | /clear defer | 間接 | 範囲外 (busy で defer する正挙動、suffix 無関係) |
| L1353 | `!= "shogun"` (CLI restart guard) | restart | 別系統 | 範囲外 |

→ ★hemostasis (出血=破壊的 /clear) に直結する actuator は L625 / L1223 / L483 のみ★。L625/L1223 は既出 C2/C6、L483 が案 E の Change 8。残りは ★非破壊 (nudge/Escape) ゆえ本 task scope 外★ とし、別 Boy-Scout task に flag (自走 over-engineering 禁、task 禁止事項順守)。

### B-3 (File 3) scripts/agent_health_check.sh — ★改修なし (温存) + 事実認定 + Boy-Scout flag★

E0-2/E0-3 の通り、本 file に busy guard / 自動 /clear / idle 強制は ★存在しない★。よって案 E は本 file を ★改変しない★ (phantom diff 捏造禁)。

- **温存 (改修対象外)**: Phase F (L303-356) の token-pressure advisory (ERR-TOKEN-WARN/CRITICAL-001) は ★人間判断の助言通知★ であり、自動 /clear ではない → 正常動作、無改変。「busy>300s→idle 強制」は本 file に ★なく★、inbox_watcher.sh:1119-1148 の stale-busy net (既出 C7 で止血済) の責務。
- **Boy-Scout flag (別 task 候補、hemostasis 非該当)**: L224 `grep -c 'read: false'` が ★unanchored★ ([[stop-hook-grep-unanchored-false-positive]] 同族)。修正方向 (参考) = `grep -c '^  read: false$'`。alert カウント精度のみに作用し /clear 経路へ無関与 → ★本 task の auto-clear 止血スコープ外★。理事長/家老差配で別 Boy-Scout task として起票推奨。

> ★案 E の三重改修の正体★: 「3 file を全部 diff る」のではなく、(File1=CLAUDE.md doc 改訂) + (File2=inbox_watcher.sh の既出7+Change8) + (File3=agent_health_check.sh は ★事実認定により改修不要と確定させる★) の三層整合。File3 を無理に触ると anti-duplication / phantom diff 違反になるため ★触らないことが正解★。

### B-4 三者連動 invariants (Phase 1-4) — verbatim

- **不変条件 Phase 1 (RC-2 根治)**: command-layer (shogun/karo/gunshi、任意 PC suffix) は ★自動 /clear を一切受けない★。担保 = inbox_watcher.sh C2 (L625) + C6 (L1223) + Change 8 (L483 manual path の shogun)、CLAUDE.md Doc-R 表の command-layer 列「`/clear` を一切送らない」。
- **不変条件 Phase 2 (RC-1 根治)**: busy 中は ★自動 /clear せず Escape+nudge に降格★。担保 = inbox_watcher.sh C3 (send_context_reset busy-defer) + C4 (caller 尊重) + C7 (Phase 3 busy 再検査)、CLAUDE.md Doc-R 表 ashigaru 列「busy 中は /clear せず降格」。
- **不変条件 Phase 3 (補助根治)**: stale-busy net (inbox_watcher.sh:1126) が busy>300s を「false-busy」と断じて idle flag を立てても、★Phase 3 が /clear 直前に実 busy を再検査して非破壊降格する★。担保 = C7。agent_health_check.sh は ★本 invariant に無関与★ (idle 強制機能を持たない、E0-3)。
- **不変条件 Phase 4 (kill switch 温存)**: 明示 `clear_command` (inbox_watcher.sh の clear_command dispatch、L1063-1075) は manual_override path として ★温存★。ただし shogun (任意 suffix) への CLI 注入は人間操作保護のため Change 8 で抑止 (= bare shogun の既存挙動 L483 に揃える、非対称解消)。

---

## 3. Part C — 統合監査仕様 (三者監査 ALL GREEN 必達)

本書は ★doc 起草★ ゆえ監査 head = 本 doc commit。実 script (CLAUDE.md/inbox_watcher.sh/agent_health_check の確定) diff の dual audit は ★理事長承認後の適用 task で別途★。

### C-1 Codex 6 軸 audit invocation (手書き禁、`scripts/audit_codex.sh` 経由、audit_duration ≥60s)

```
bash scripts/audit_codex.sh subtask_thirdpc_p0_auto_clear_hemostasis_proposal_e_integrated_design_001 1 2d0a1e48 <head_commit> /home/hakudoukai/multi-agent-shogun
```

### C-2 Gemini 8 観点 audit invocation (手書き禁、`scripts/audit_gemini.sh` 経由、同上)

```
bash scripts/audit_gemini.sh subtask_thirdpc_p0_auto_clear_hemostasis_proposal_e_integrated_design_001 1 2d0a1e48 <head_commit> /home/hakudoukai/multi-agent-shogun
```

> Gemini 注意 ([[gemini-delta-only-deletion-false-positive]]): 本書は doc のみで code 削除ゼロ。誤検知 (helper 削除でテスト破壊 等) が出たら家老-third が git grep で import-verification の上 採否。

### C-3 軍師 governing audit — ★別 ashigaru 起票 (gunshi-third 自身は本書起草者ゆえ自作自演禁)★

gunshi-third は ★governing dual audit の集約・裁定★ は担うが、本書の起草者であるため ★一次監査の実施は別 ashigaru★ に起票させる (FKI-AUDIT-GREEN-TRUTH-01 自作自演禁)。家老-third に対し governing audit assignee の指名を要請。

### C-4 ALL GREEN 後の routing

```
Codex 6軸 GREEN ∧ Gemini 8観点 GREEN ∧ 軍師 governing GREEN
  → 副院長 governing 検証印
  → 理事長 D-lane 承認 (実 script 改変許可)
  → 実適用 task 起票 (CLAUDE.md Doc-R 反映 + inbox_watcher.sh C1-C7+Change8 適用)
  → 実 script diff の dual audit (Codex+Gemini 再走、適用 task base_commit で)
  → land
```

---

## 4. 副作用評価 (案 E 追加分。既出 C1-C7 の S1-S6 は前身 doc §5 を正本参照、重複せず)

| # | aspect | impact | severity | mitigation |
|---|---|---|---|---|
| SE1 | Change 8 で shogun-third の manual clear_command が ★no-op 化★ | shogun-third を inbox 経由で /clear リセット不可に | low(意図) | bare shogun は既に L483 で同挙動 = ★非対称解消★。shogun の reset は理事長/Commander の ★pane 直接操作★ で行う設計 (L482「信長 is controlled by the Lord」)。kill switch は karo/gunshi/ashigaru で温存 |
| SE2 | CLAUDE.md Doc-R と script の ★乖離リスク★ (片方のみ適用) | doc が実挙動と不一致な phantom canon に戻る | medium | ★適用 task で doc + script を ★同一 commit/同一 land★ に束ねる★。本書 C-4 routing に明記 |
| SE3 | agent_health_check.sh を「改修不要」と確定したことで、将来真の busy 監視を足す余地を閉じる懸念 | なし | none | 本書は ★現時点で busy guard が実在しない★ 事実認定のみ。将来要件は別途設計 (本 task scope は既存 hemostasis) |
| SE4 | L224 unanchored grep を別 task に flag → 放置リスク | alert カウント偽陽性が残存 | low | /clear 経路に ★無関与★ ゆえ hemostasis を阻害せず。家老-third が Boy-Scout backlog に登録 |

---

## 5. watcher-design.md 6 原則 整合判定 (案 E 全体)

| 原則 | 判定 | evidence |
|---|---|---|
| 1. retry 無限ループ禁 | ✅ | 配送 retry は ae8083dd 5 回上限 + human_required (既出継承)。Change 8/Doc-R は新 retry 不導入 |
| 2. self-send 即 ack | ✅ | 本案無関係 (inbox_write.sh guard 不変) |
| 3. 手動停止フラグ尊重 | ✅ | clear_command kill switch 温存 (invariant 4)。Change 8 は shogun 限定で人間操作保護 |
| 4. 重複検知 | ✅ | C1 helper 単一 choke-point 再利用、Change 8 は既存 helper 流用 (重複定義なし) |
| 5. idempotency | ✅ | Change 8 は guard 条件式の置換のみ、副作用なし。Doc-R は doc のみ |
| 6. 専用テーブル分離 | ✅ | 本案無関係 (log は既存 stderr 構造化) |

---

## 6. 検証戦略 (★SKIP=0 必達、CLAUDE.md Test Rule 1★)

- **unit (bash)**: C1 helper を `AGENT_ID=shogun-third/karo/gunshi-third/ashigaru-third-3/ashigaru3` で `is_shogun_agent` / `is_command_layer_agent` 真偽表明。Change 8 期待: `AGENT_ID=shogun-third` で send_cli_command が `[SKIP] shogun` 早期 return。
- **integration (dry-run, tmux send-keys mock)**: `send_cli_command "/clear"` を `AGENT_ID=shogun-third` で呼び ★send-keys 発火なし★。`AGENT_ID=karo` で発火あり (kill switch 温存)。
- **doc 整合 test**: CLAUDE.md Doc-R 表の不変条件 1-3 が inbox_watcher.sh の C2/C6/Change8/C3/C4/C7 と ★一対一対応★ することを適用 task の review checklist で確認。
- **manual (理事長承認後・適用 task)**: shogun-third に clear_command 投函 → `./logs/inbox_watcher_shogun-third.log` に `[SKIP] shogun: suppressing CLI command injection (/clear)` を確認、/clear send-keys 不在を確認。

---

## 7. rollback 戦略

| 項目 | 内容 |
|---|---|
| trigger | 適用後に (a) 配送停滞 (b) shogun-third が pane 直接操作でも復旧不能 (c) command-layer 想定外 reset 観測 |
| steps | `git revert <適用 commit>` (doc+script 同一 commit ゆえ一括復帰) → 該当 supervisor で inbox_watcher 再起動 (旧挙動 reload) |
| owner | 適用実施者 (理事長承認下の別 task)。gunshi-third は案出しのみ |
| 安全網 | 変更は CLAUDE.md (doc) + inbox_watcher.sh (helper 流用 + 条件式置換) のみ。agent_health_check.sh は ★無改変★ ゆえ blast radius さらに局所、data migration なし → 無損失 revert |

---

## 8. 改訂責務

本 doc (止血 ★案 E★) の提案レベル改訂は本職 (gunshi-third) 可。★実 script (CLAUDE.md/inbox_watcher.sh) 適用判断は理事長殿の専権 (D-lane)★。CLAUDE.md Escalation 表 (Doc-R) は ★CLAUDE.md「Communication Protocol」配下の正本★ ゆえ、その確定改訂も理事長承認 + 副院長検証印 (FKI-CANON-GUARDIAN-01) を経る。agent_health_check.sh は本書で ★改修不要と認定★、将来要件発生時は別 task で設計。
