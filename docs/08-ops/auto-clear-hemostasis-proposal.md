# 自動 /clear 止血案 — busy 対処 /clear → 待つ + ack リトライ (ae8083dd) 置換 設計提案

> 起草: 軍師 (gunshi-third) / task: subtask_thirdpc_p0_auto_clear_hemostasis_proposal_design_001
> parent_cmd: cmd_thirdpc_p0_auto_clear_stop_bleeding_001 / parent_handshake: 7201f89f seq=36353
> base_commit: 2d0a1e48175854c0f3b5114947b4be454b90485e
> ★D-lane 警告: 本書は案 + diff 草案のみ。実適用は理事長承認後の別 task。本 task で script 改変・configuration 変更は一切行わない★
> 規律: DD-157 役職名のみ / F002 報告経路 / FKI-NO-DUP (ae8083dd 再利用) / FKI-AUDIT-GREEN-TRUTH-01 / Watcher Design Principles 6 原則 / [[commander-third-failsafe-redrive]] / [[third-pc-inbox-watcher-stall]] / [[stop-hook-grep-unanchored-false-positive]] / [[third-pc-agent-id-suffixed-inbox-and-phantom-inbox1]]

## 0. 出典 (実態 grounding — speculation 排除)

| 出典 | 内容 |
|------|------|
| `scripts/inbox_watcher.sh` (実機, 1384 行) | 自動 /clear の唯一の発火元。2 経路: **CONTEXT-RESET** (`send_context_reset` L617-684, 呼出 L1157-1173) と **Phase 3 escalation** (L1213-1240) |
| `lib/agent_status.sh` (実機) | busy/idle 判定 (`agent_is_busy_check` L31, `get_pane_state_label` L94)。★role 判定 helper は存在しない (grep 確認)★ → 新規 helper は FKI-NO-DUP 非抵触 |
| `docs/08-ops/ack-retry-omni-engine-design.md` (実機, ae8083dd) | ack 再送共通エンジン root spec。Stage A/B confirm + SLA 30/120/300s + backoff×2 + 上限5。★(iv) で「独自 nudge/Escape/clear を一切送らず受領側 wake は inbox_watcher に委譲」と明記★ |
| 実機 log `./logs/inbox_watcher_shogun-third.log` | shogun-third が 17:53:59 / 17:56:45 / 18:11:42 に CONTEXT-RESET /clear (毎 task_assigned、busy 中 "proceeding anyway") |
| 実機 log `./logs/inbox_watcher_ashigaru-third-3.log` | a3-3 が 17:06 / 17:43 / 17:53 に CONTEXT-RESET /clear (busy 中) |
| `docs/01-architecture/watcher-design.md` | 6 原則 (retry 無限ループ禁 / self-send 即 ack / 手動停止フラグ尊重 / 重複検知 / idempotency / 専用テーブル分離) |

## 1. 真因認定 (★task 仮説の Critical-Thinking 補正★)

task description (b) は「真因 = busy 対処 4 min+ で Phase 3 /clear」と仮置きするが、★実機 log 照合の結果、本日の context 消失 2 件の支配的経路は Phase 3 ではなく CONTEXT-RESET 経路★ である (FKI-AUDIT-GREEN-TRUTH / ALL-EVIDENCE-BEFORE-ABSENCE 順守、log 実物証に基づく補正)。

### RC-2 (支配的・shogun-third 消失の真因): suffix-blind command-layer guard

`send_context_reset()` L625 の command-layer 保護は ★bare 名 完全一致★ を用いる:

```bash
if [ "$AGENT_ID" = "shogun" ] || [ "$AGENT_ID" = "karo" ] || [ "$AGENT_ID" = "gunshi" ]; then
```

third_pc の実 AGENT_ID は ★`-third` suffix 付き★ (`shogun-third` 等、[[third-pc-agent-id-suffixed-inbox-and-phantom-inbox1]])。ゆえに `"shogun-third" = "shogun"` は **false** → 保護が外れ、shogun-third は task_assigned 着信の度に CONTEXT-RESET /clear を受ける。同 bug は Phase 3 L1223 / busy guard L1122 にも存在 (計 3 箇所 bare-name)。

→ 17:53/17:56/18:11 の shogun-third 消失 = この経路。指揮層 (将軍/家老/軍師) は複雑な running context を保持し ★自動 reset 対象外★ であるべき (L621-624 の設計意図そのもの) が、suffix で無効化されていた。

### RC-1 (a3-3 消失の真因): 「busy ≠ 異常」— busy 中でも /clear が貫通

CONTEXT-RESET /clear (`send_context_reset` L661) は ★busy 検査なしに /clear を送出★ し、その後 idle を待つだけ (L670-683) で、busy のままでも "proceeding anyway" (L681-683)。task_assigned が届いた瞬間、受領者が前 task で実働中 (busy) でも context を破壊する。

→ a3-3 (ashigaru、新 task の context reset 自体は正当) が前 task 実働中に /clear され work loss。これが「a3-3 poke 中断」。

長時間 task は busy であり ★正常★。busy を異常と見なして reset するのが誤り。

### 補助 (Phase 3 経路): stale-busy safety net → /clear

L1125-1132 の stale-busy net は busy>300s を「false-busy」と断じ idle flag を強制 → fall-through → Phase 3 /clear (L1230)。長時間正当 busy を reset しうる。本日 2 件の直接原因ではないが同根 (busy≠異常) ゆえ併せて止血する。

## 2. 止血方針 (busy 対処 = /clear → 待つ + ack リトライ ae8083dd 置換)

中核命題: **message は inbox_write.sh の flock append で既に「配送済」**。busy な claude agent は Stop hook (`stop_hook_inbox.sh`) が turn 終了時に未読を配送する。ゆえに「起こす」ための /clear は ★不要かつ破壊的★。「本当に読まれたか」の保証は ae8083dd の Stage B confirm + SLA 再送が ★非破壊で★ 担う。

3 不変条件:

1. **指揮層 (shogun/karo/gunshi, 任意 PC suffix) は自動 /clear を一切受けない** (RC-2 根治、suffix-aware 化)。
2. **busy 中は自動 /clear を送らない = 待つ** (RC-1 根治)。配送は inbox + Stop hook + ae8083dd Stage B が保証。
3. **明示 /clear (clear_command, L488-509) は kill switch として温存** — 自動 escalation 経路 (本案の対象) とは別物、無改変。

## 3. 修正候補 file enumeration + diff 草案 (unified, ★未適用★)

対象 file は `scripts/inbox_watcher.sh` ★単一★。新規 transport / 新規 poller を作らない (ae8083dd 再利用、FKI-NO-DUP)。

### Change 1 — suffix-aware role helper 新規 (重複なし、grep 確認済)

`get_effective_cli_type()` (L269) 直後あたりに追加:

```diff
+# ─── Role detection (PC-suffix tolerant) ───
+# AGENT_ID は third_pc 等で "-third"/"-second"/"-main" suffix を持つ
+# ([[third-pc-agent-id-suffixed-inbox-and-phantom-inbox1]])。
+# bare 名完全一致だと shogun-third 等が指揮層保護をすり抜けるため、
+# 先頭ハイフンまでを base role として抽出する。
+agent_role() {
+    # shogun-third→shogun / karo→karo / gunshi-third→gunshi / ashigaru-third-3→ashigaru / ashigaru3→ashigaru3
+    echo "${AGENT_ID%%-*}"
+}
+is_command_layer_agent() {
+    case "$(agent_role)" in
+        shogun|karo|gunshi) return 0 ;;
+        *) return 1 ;;
+    esac
+}
+is_shogun_agent() {
+    [ "$(agent_role)" = "shogun" ]
+}
```

注: `ashigaru3` (ハイフンなし) は `${AGENT_ID%%-*}` で `ashigaru3` のまま → command-layer 非該当 (正)。`ashigaru-third-3` → `ashigaru` (正)。bare `karo` → `karo` (正)。

### Change 2 — send_context_reset 指揮層 guard を suffix-aware 化 (RC-2 根治)

```diff
@@ scripts/inbox_watcher.sh:625 (send_context_reset)
-    if [ "$AGENT_ID" = "shogun" ] || [ "$AGENT_ID" = "karo" ] || [ "$AGENT_ID" = "gunshi" ]; then
+    if is_command_layer_agent; then
         echo "[$(date)] [SKIP] $AGENT_ID: suppressing context reset (command-layer agent)" >&2
         return 0
     fi
```

### Change 3 — send_context_reset に busy-defer gate 追加 (RC-1 根治)

command-layer guard 直後 (L628 と L630 の間)、/clear 送出 (L661) より ★前★ に:

```diff
@@ scripts/inbox_watcher.sh:628-630 (send_context_reset, command-layer guard の直後)
     fi
+
+    # busy-defer: 受領者が実働中 (busy) の間は context reset を ★送らず延期★。
+    # message は inbox に配送済 (Stop hook が turn 終了時に配送、ae8083dd Stage B が
+    # 受領確認)。busy≠異常 ゆえ /clear で work loss させない。return 1 = 延期 (caller が次 cycle 再試行)。
+    if agent_is_busy; then
+        echo "[$(date)] [DEFER] $AGENT_ID busy — context reset 延期 (非破壊、Stop hook+ack-retry が配送保証)" >&2
+        return 1
+    fi
 
     local reset_cmd
```

注: 既存 L670-683 の post-/clear idle poll は ★/clear が idle 時のみ送出される★ ようになるため、そこでの "still busy" は /clear 自体の processing を指す (正常)。無改変。

### Change 4 — caller が defer 戻り値を尊重 (RC-1 根治、caller 側)

```diff
@@ scripts/inbox_watcher.sh:1157-1173 (Context reset before new task)
     if [ "$has_task_assigned" = "1" ] && [ "$NEW_CONTEXT_SENT" -eq 0 ] && [ "$clear_seen" -eq 0 ]; then
-        send_context_reset
-        NEW_CONTEXT_SENT=1
-        LAST_NUDGE_TS=0
-        LAST_NUDGE_COUNT=""
-        LAST_CLEAR_TS=0
-        echo "[$(date)] [POST-RESET] Sending immediate post-reset nudge to $AGENT_ID" >&2
-        send_wakeup "$normal_count"
-        FIRST_UNREAD_SEEN=$now
-        return 0
+        if send_context_reset; then
+            NEW_CONTEXT_SENT=1
+            LAST_NUDGE_TS=0
+            LAST_NUDGE_COUNT=""
+            LAST_CLEAR_TS=0
+            echo "[$(date)] [POST-RESET] Sending immediate post-reset nudge to $AGENT_ID" >&2
+            send_wakeup "$normal_count"
+            FIRST_UNREAD_SEEN=$now
+            return 0
+        else
+            # busy で延期 (return 1)。NEW_CONTEXT_SENT は立てず次 cycle 再試行。
+            # 破壊的 /clear を撃たず、未読は Stop hook + ae8083dd Stage B で配送保証。
+            echo "[$(date)] [DEFER] $AGENT_ID context reset 延期 (busy) — 待機、未読は配送済" >&2
+            FIRST_UNREAD_SEEN=$now
+            return 0
+        fi
     fi
```

### Change 5 (任意・整合) — busy guard を suffix-aware 化

```diff
@@ scripts/inbox_watcher.sh:1122
-        if agent_is_busy && [[ "$AGENT_ID" != "shogun" ]]; then
+        if agent_is_busy && ! is_shogun_agent; then
```

shogun-third も shogun と同じ busy 例外 (ntfy 即時配送) を得る。core 安全性には Change 6 が効くため ★任意★。

### Change 6 — Phase 3 command-layer guard を suffix-aware 化 (補助根治)

```diff
@@ scripts/inbox_watcher.sh:1223 (Phase 3 escalation)
-                elif [ "$AGENT_ID" = "shogun" ] || [ "$AGENT_ID" = "karo" ] || [ "$AGENT_ID" = "gunshi" ]; then
+                elif is_command_layer_agent; then
                     echo "[$(date)] [SKIP] ESCALATION Phase 3: $AGENT_ID suppressed (command-layer agent, ${age}s). Using Escape+nudge." >&2
                     FIRST_UNREAD_SEEN=$now
                     send_wakeup_with_escape "$normal_count"
```

### Change 7 — Phase 3 /clear 直前に busy 再検査 (RC-1 根治、escalation 経路)

stale-busy net が idle flag を強制した後でも、Phase 3 で実 busy を再確認し /clear を非破壊 nudge に downgrade:

```diff
@@ scripts/inbox_watcher.sh:1228-1233 (Phase 3 else branch, ashigaru /clear)
                 else
+                    # busy 再検査: stale-busy net が idle flag を立てても、実働中なら /clear せず待つ。
+                    if agent_is_busy; then
+                        echo "[$(date)] [DEFER] ESCALATION Phase 3: $AGENT_ID busy — /clear 抑止、Escape+nudge で待機 (ack-retry が配送保証)" >&2
+                        FIRST_UNREAD_SEEN=$now
+                        send_wakeup_with_escape "$normal_count"
+                    else
                     echo "[$(date)] ESCALATION Phase 3: Agent $AGENT_ID unresponsive for ${age}s. Sending /clear." >&2
                     send_cli_command "/clear"
                     LAST_CLEAR_TS=$now
                     FIRST_UNREAD_SEEN=0
                     NEW_CONTEXT_SENT=0
+                    fi
                 fi
```

(適用時に else ブロック全体を 1 段インデントする。上記は概念差分。)

## 4. retry 設計 (ae8083dd 既存機構の再利用 — ★新設禁★)

止血後、「busy で /clear しない」分の配送保証は ★ae8083dd ack 再送共通エンジンに委譲★ する。inbox_watcher に独自 retry loop を新設しない (FKI-NO-DUP、ae8083dd (iv) の「watcher へ wake 委譲」と対称)。

| 要素 | 値 | 出典 / 根拠 |
|---|---|---|
| **interval** | Stage A: append 直後 + 2s。Stage B: SLA checkpoint t=30s / 120s / 300s | ae8083dd (ii)(iv)、副院長 verbatim 固定 checkpoint |
| **backoff** | 固定 30/90/180s → t=300s 以降 `gap×2` (360→720s)。jitter±20% は再投函時刻のみ (固定 checkpoint は判定時刻ゆえ非適用) | ae8083dd (iv) 状態遷移表 (唯一正本) |
| **cap** | 再送 5 回上限 → 到達後 ★自動再送停止★ + human_required (`type: request_permission`) | ae8083dd (iv) / Watcher Design「無限 retry 禁」 |
| **ack_path (既存再利用)** | Stage A = `inbox_write.sh` 返却 id を `yaml.safe_load` で id 一致 entry 読返し (grep substring 不使用、[[stop-hook-grep-unanchored-false-positive]])。Stage B = 同 correlation_id の posted_ids いずれかが `read==true`。受領側 wake = inbox_watcher の ★非破壊 nudge★ に委譲 | ae8083dd (ii)(iv) |
| **manual_override** | 明示 `clear_command` (L488-509) は kill switch として温存。自動 escalation /clear のみ抑止 | 本案 §2 不変条件 3 |

inbox_watcher の役割は縮小: **busy 時は非破壊 nudge (Escape+nudge) のみ**、/clear は ★genuinely idle かつ ashigaru かつ真に unresponsive★ の時のみ。配送保証は ae8083dd が負う。

## 5. 副作用評価

| # | aspect | impact | severity | mitigation |
|---|---|---|---|---|
| S1 | 真に stuck (jam/crash) な ashigaru の auto /clear 復旧を失う | busy 偽装 stuck は自動 /clear されなくなる | medium | (a) Escape+nudge で jam 解除 ([[commander-third-failsafe-redrive]] の Esc/C-u 経路) (b) ae8083dd human_required (5 再送後 human 通知) (c) 明示 clear_command kill switch。★auto /clear on busy の喪失は意図的 trade-off★ (正当 work 破壊コスト > 稀な stuck 自動復旧便益) |
| S2 | command-layer が新 task で stale context を持ち越す | shogun-third 等が前 task context を保持 | low | 設計意図通り (指揮層は running context 保持が正、L621-624)。必要時は明示 clear_command |
| S3 | busy-defer で context reset が遅延 | idle 化まで新 task 着手が遅れる | low | message は配送済、Stop hook が turn 終了時に配送。延期は cycle 単位 (≤timeout 間隔) |
| S4 | `agent_role` の suffix 仮定が将来命名で破綻 | `-` を含む新 role 命名で誤抽出 | low | 現行命名 (shogun/karo/gunshi/ashigaru[N]/-pc suffix) で検証。命名規約変更時は helper 更新 (単一 choke point ゆえ局所) |
| S5 | escalation chain (2-4min Escape / 4min+ /clear) への影響 | 4min+ の destructive 段が busy 時 Escape+nudge に降格 | low(意図) | non-destructive 段 (Escape+nudge) は不変。destructive 段のみ busy gate 追加 |
| S6 | stop_hook / supervisor との競合 | なし (本案は send-keys 経路を ★減らす★ のみ、新 actuator なし) | none | [[third-pc-inbox-watcher-stall]] の supervisor 動的解決と独立 |

## 6. watcher-design.md 6 原則 整合判定

| 原則 | 判定 | evidence |
|---|---|---|
| 1. retry 無限ループ禁 | ✅ | 配送 retry は ae8083dd 5 回上限 + human_required。inbox_watcher 側は独自 retry 不新設 |
| 2. self-send 即 ack | ✅ | 本案無関係 (inbox_write.sh 既存 guard 不変) |
| 3. 手動停止フラグ尊重 | ✅ | 明示 clear_command kill switch 温存。本案は自動経路のみ抑止 |
| 4. 重複検知 (dedupe) | ✅ | busy-defer は NEW_CONTEXT_SENT を立てず再試行するのみ、/clear の二重送出はむしろ減少 |
| 5. idempotency | ✅ | return 1 延期は副作用なし。再 cycle で idle 化後に 1 度だけ reset |
| 6. 専用テーブル分離 | ✅ | 本案無関係 (log は既存 stderr 構造化、ae8083dd ack event log は別設計) |

## 7. 検証戦略

- **unit (bash)**: `agent_role` / `is_command_layer_agent` を AGENT_ID=shogun-third/karo/gunshi-third/ashigaru-third-3/ashigaru3 で表明テスト (bats or 簡易 assert)。期待: command-layer 該当/非該当の真偽値。
- **integration (dry-run)**: `send_context_reset` を AGENT_ID=shogun-third + busy stub (agent_is_busy=0) で呼び、★/clear send-keys が発火しない (return 1 or return 0 skip)★ ことを tmux send-keys を mock して確認。ashigaru-third-3 + busy で return 1 (延期)、idle で /clear 1 回。
- **manual (実機・理事長承認後)**: shogun-third に task_assigned を投函 → log に `[SKIP] ... command-layer` が出て /clear send-keys が無いことを `./logs/inbox_watcher_shogun-third.log` で確認。busy な ashigaru に task_assigned → `[DEFER] ... busy` を確認、idle 化後に 1 度 reset。
- ★SKIP=0 必達 (CLAUDE.md Test Rule 1)★。

## 8. rollback 戦略

| 項目 | 内容 |
|---|---|
| trigger | 適用後に (a) 配送停滞 (未読滞留) (b) stuck agent が復旧不能 (c) command-layer が想定外 reset を観測 |
| steps | `git revert <適用 commit>` で inbox_watcher.sh を base_commit 2d0a1e4 状態へ即時復帰 → `scripts/watcher_supervisor_third.sh` (or 該当 supervisor) で watcher 再起動して旧挙動 reload |
| owner | 適用実施者 (理事長承認下の別 task 担当)。本職 (gunshi-third) は案出しのみ |
| 安全網 | 単一 file 変更ゆえ blast radius 局所。helper 追加 + 条件式置換のみで data migration なし → revert は無損失 |

## 9. Codex + Gemini 三者監査仕様

標準呼出し (手書き禁、`docs/audit-framework.md` 順守、audit_duration ≥60s、base_commit 記録):

```
bash scripts/audit_codex.sh  subtask_thirdpc_p0_auto_clear_hemostasis_proposal_design_001 1 2d0a1e48 <head> /home/hakudoukai/multi-agent-shogun
bash scripts/audit_gemini.sh subtask_thirdpc_p0_auto_clear_hemostasis_proposal_design_001 1 2d0a1e48 <head> /home/hakudoukai/multi-agent-shogun
```
(本書は doc 起草ゆえ head = 本 doc commit。実 script 改変は ★別 task / 理事長承認後★ につき、その diff の dual audit は適用 task で別途。)

監査 6 軸 / 8 観点 着目:

| 軸/観点 | 評価対象 |
|---|---|
| 重要度 / 仕様準拠 | RC-1/RC-2 認定が log 実物証と一致、busy≠異常 命題の妥当性 |
| 正確性 / データフロー | diff の line range が実 file (1384 行) と整合、phantom diff 無し |
| 実装妥当性 / システム整合性 | `agent_role` suffix 抽出の網羅性 (ashigaru[N] / -pc suffix / bare)、return 1 延期 contract |
| 副作用 / 網羅性 | S1 stuck 復旧喪失 trade-off の妥当性、ae8083dd 委譲で配送保証が閉じるか |
| テスト容易性 / 観察可能性 | §7 検証戦略の SKIP=0 実現性、DEFER log の構造化 |
| audit-framework 整合 / ドキュメント | FKI-NO-DUP (ae8083dd 再利用) / DD-157 役職名 / 明示 clear_command 温存の文書化 |

PASS まで PDCA、自作自演禁、双方 GREEN 必達。RED は起草修正 + 再 audit。

## 10. 改訂責務

本 doc (止血 ★案★) の改訂は提案レベルでは本職可。★実 script への適用判断は理事長殿の専権 (D-lane)★。CLAUDE.md「Communication Protocol → Delivery Mechanism」節の改訂草案 (boy_scout) は適用承認後に反映。
