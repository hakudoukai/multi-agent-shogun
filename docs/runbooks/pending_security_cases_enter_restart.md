# enter_restart 系 Phase B 繰越セキュリティ機械追跡 registry

**根拠**: 副院長令 baabd1ca【enter_restart RED 修正 Phase A 即修正】「Phase B 繰越=S1/S2 (pane base64 ログ漏洩) は pending_security_registry 登録し凍結」順守、Codex audit `e7e28c7a-1a77-4c31-bd6a-44176099075e` (cycle2 ffa89df red) S1+S2 medium fix。

**目的**: enter_restart watchdog 系で Phase A では即時解消しないが将来の機密漏洩リスク要件強化時に解消必須のセキュリティ課題を、「単なるコメント」ではなく機械追跡可能な markdown + 復活条件付きで保管。Phase B 復活条件成立時の修正漏れを副院長殿/Operator が機械的に検知できる経路として機能。

**運用**: 各 entry に `id` / `phase_a_status` / `phase_b_restoration_trigger` / `current_implementation_file_line` / `restoration_action` を必須記載。Phase B 要件強化時 (例: HIPAA / 内部監査 / 機密 token 検出強化) には対応 entry を `restored` 化 (削除 or status 更新) する責務を担う。

---

## entry-001: S1 — pane tail base64 ログ漏洩 (commander 版)

| 項目 | 値 |
|------|-----|
| id | `S1_commander_pane_tail_base64_log` |
| phase_a_status | **deferred_phase_b** |
| source_audit | Codex `e7e28c7a-1a77-4c31-bd6a-44176099075e` (cycle2 ffa89df) Axis 1 Security S1 medium |
| current_implementation | `scripts/watchdogs/enter_restart_common_watchdog.sh` L143 (cycle3 D1 統合後の共通実装) |
| detail | tmux pane 末尾 3 行と最終入力行を base64 エンコードして永続ログ (`%h/.local/share/enter_restart_commander/$(date +%Y%m%d).log`) に記録する。Claude TUI 上の未送信入力 (機密 token、API キー、患者 PII 等) が pane に表示中の場合、ローカルログに base64 形式で残留するリスク。 |
| phase_a_rationale | (i) third_pc local 番人ゆえ pane log は third_pc filesystem 内で完結、外部送信なし。(ii) label-match strict のデバッグ時に base64 log が原因究明の重要証跡。(iii) Phase A 時点では third_pc 単一 PC 運用、機密漏洩経路が極小。(iv) cycle3 修正 4 件 (B1/B2/T1/D1) は systemd 起動契約・smoke test・コード重複を優先解消、本件は副院長令明示で Phase B 繰越凍結。 |
| phase_b_restoration_trigger | (a) third_pc が main_pc/second_pc と SSH 経由連携を開始 (副院長令 e6b027a6 §(γ) SSH 開設は保留 → 解除時)、(b) HIPAA / 患者 PII 取扱規程強化により pane log への base64 残留が監査対象化、(c) 内部監査 / 副院長殿御差配で機密漏洩防止優先度引き上げ |
| restoration_action | (1) `enter_restart_common_watchdog.sh` Step 3 の `printf '%s' "$PANE_TAIL" | base64 -w0` 記録を撤廃、(2) `label_match=0/1` + `label_reason` のみ記録、(3) pane tail / last_line 全体は log file に保存しない (in-memory のみ判定用)、(4) Codex S1 fix_suggestion 通り「prompt 一致結果のみ記録、必要なら長さ・ハッシュ・判定理由に限定」 |
| ci_check | 機械追跡 CI gate は `scripts/checks/pending_security_enter_restart_check.sh` (cycle4+ 候補) で envvar `ENABLE_PHASE_B_SECURITY=1` ON 時に本 entry が `deferred_phase_b` のままなら fail 設計 (cycle3 mandate 範囲外、副院長殿御差配後に実装) |

## entry-002: S2 — pane tail base64 ログ漏洩 (shogun_third 版)

| 項目 | 値 |
|------|-----|
| id | `S2_shogun_third_pane_tail_base64_log` |
| phase_a_status | **deferred_phase_b** |
| source_audit | Codex `e7e28c7a-1a77-4c31-bd6a-44176099075e` (cycle2 ffa89df) Axis 1 Security S2 medium |
| current_implementation | `scripts/watchdogs/enter_restart_common_watchdog.sh` L143 (cycle3 D1 統合後の共通実装、entry-001 と同箇所) |
| detail | entry-001 と同じ問題が shogun_third 版 watchdog にも存在。cycle3 D1 共通化以降は ★同一実装★ ゆえ S1 と S2 は本質的に同じ entry。本 registry では監査時の Codex finding 識別子 (S1 vs S2) を維持するため両 entry を別記、修正時は entry-001 restoration_action で同時解消。 |
| phase_a_rationale | entry-001 と同じ。 |
| phase_b_restoration_trigger | entry-001 と同じ。 |
| restoration_action | entry-001 restoration_action と同じ (cycle3 D1 共通化により 1 箇所修正で両 entry 同時解消、behavior drift 不可能化)。 |
| ci_check | entry-001 と同じ。 |

---

## 改訂責務

本 registry の改訂は **副院長殿** の専権事項。Commander / karo / 家康 / 家康 は提案のみ可。Phase B 復活トリガー成立時の優先度判断は副院長殿の御差配。
