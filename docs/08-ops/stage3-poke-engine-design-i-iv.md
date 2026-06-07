# 段階3 設計章節 (i)-(iv) — fukuincho 自動 poke エンジン root spec (task ae8083dd 本実装用)

> 起草: 足軽 (ashigaru-third-3, raw row msg_20260607_161123) / 監査: 軍師 (gunshi-third) Codex 6軸 + Gemini 8観点 dual
> base_commit: 206ffe2 / parent_cmd: cmd_thirdpc_p1_fukuincho_desktop_poke_stage1_diag_plus_stage3_engine_001
> 規律: DD-157 役職名のみ / F002 / V5 (8012f18c) 保護 / FKI-AUDIT-GREEN-TRUTH-01 / Watcher Design Principles

本書は段階3 (cron/SLA 連動 + 着火 ack リトライ再送エンジン) の root spec を確定し、
軍師 8 観点 (O1-O8) dual audit の監査対象 artifact として供する。素案値は ★要御差配★ 印を付す。

## (i) cron / SLA 連動

- 既存 `fukuincho_watch` detect_stale を **継承** (新規 cron poller を新設しない — FKI-NO-DUP 第4条 採用案順守)。
- SLA 超過時に自動 poke 発火 trigger。
- cron 間隔素案: **60 秒** (P1 黄取りこぼし優先 / 過剰 poll 抑制のバランス)。
- SLA 閾値素案: **stale = 120 秒** (Commander 操作 timeout 目安、★要御差配★)。

## (ii) 着火 ack リトライ再送 (黄取りこぼし克服)

- poke 後 **N = 15 秒** (素案、★要御差配★) 内に chat 進行を検知。
  - 検知信号案: window title 変化 / focus 移動 / Edit・Document content 増分。
- 検知不可なら最大 **M = 3 回** (素案、★要御差配★) 再送。
- 再送間隔: exponential backoff **30s / 60s / 120s**。
- root spec 命題: ack timeout 検出 + 単調 backoff 再送 = 黄取りこぼし克服。

## (iii) 短時間多重 poke 抑制 (dedupe)

- 直近 **T = 60 秒** (素案) 以内の同窓重複 poke を抑止。
- dedupe key 案: **(window_handle, poke_kind, T_bucket)** の三項組。
- root spec 命題: 同一 SLA 違反に対する double-fire 防止 (Watcher Design Principles 重複検知/idempotency 順守)。

## (iv) 応答中 skip 誤爆防止 (Commander 入力途上保護)

- **editing 中検出**:
  - input control `get_value()` 非空。
  - focused 状態 (set_focus 直前確認)。
  - IME composition active (`WM_IME_COMPOSITION` 検出)。
- **submission inflight 検出**:
  - submit button disabled / spinner 表示 / progress indicator active。
- skip ルート: 上記いずれか真 → poke 中止 + retry queue 末尾へ re-enqueue。
- root spec 命題: ★Commander 入力途上での誤爆絶対防止★ (副院長殿との連絡途絶誘発禁)。

## 絶対前提順守 (a3-3 raw row 実証済)

- V5 (handshake 8012f18c) 触接 ★ゼロ★ (V5 = WSL file render、Windows デスクトップ窓非占有)。
- 本送信 (--send 系) ★ゼロ★ / --dry-run・focus 奪取 自発 ★ゼロ★ / --diagnose 1 回のみ。
- F002 順守 (報告経路 = gunshi-third → karo-third → shogun-third → commander-third → 副院長殿)。
- DD-157 役職名のみ (戦国 persona 禁、副院長令 3efc70d2 整合)。

## 軍師 8 観点 (O1-O8) dual audit 対象マッピング

| 観点 | 評価対象 | 監査 lens (Codex 軸 / Gemini 観点) |
|------|----------|-----------------------------------|
| O1 cron 間隔 + SLA 閾値 根拠 | (i) 60s / 120s の fukuincho_watch 整合 | Gemini spec_compliance / completeness |
| O2 ack timeout N + リトライ M 根拠 | (ii) N=15s / M=3 / backoff 30-60-120 の定量化 | Gemini completeness / Codex bugs |
| O3 dedupe key 設計 | (iii) (window_handle, poke_kind, T_bucket) | Gemini side_effects / Codex duplication |
| O4 応答中検出方法 | (iv) editing + submission inflight signature | Gemini side_effects / completeness |
| O5 V5 (8012f18c) 保護整合 | cron/poke が V5 capture を踏まない保証 | Gemini system_relations |
| O6 F002 順守 | 報告経路 root spec 整合 | Gemini spec_compliance |
| O7 観察可能性 | 構造化 JSON / correlation_id (docs/error-design-medical.md §14) | Gemini observability_error_handling |
| O8 anti-duplication | 既存 fukuincho_watch / ccflare 経路との重複検出 | Codex duplication / Gemini system_relations |

## 完了条件

Codex 6軸 + Gemini 8観点 双方 GREEN → O1-O8 全 PASS と判定。
1 観点でも RED → status: blocked + 即家老 escalate (a3-3 設計差替 or ae8083dd 着手 spec 改訂)。
最終 PASS は副院長殿照合後 (provisional まで)。
