# 足軽4号 → 家老second: 6path ↔ 受入①〜⑨ 対応表（read-only・紙上設計のみ）

断面: 2026-08-06T09:1x JST（当職 実測）。本便は read-only。apply/worktree新設/DB/実走 一切なし。

## §0 母集団宣言

- **6path**: patch内 `diff --git` 出現順に P1〜P6 と番号付け（実測=`grep -n '^diff --git' <patch>`）。
  - P1=`backend/api/web_reservation/booking.py`（L1-12）
  - P2=`backend/services/appointment_service.py`（L13-59）
  - P3=`backend/services/web_reservation/booking_service.py`（L60-311）
  - P4=`backend/tests/web_reservation/test_phase2_2_booking.py`（L312-455）
  - P5=`backend/db/migrations/booking_concurrency_root.py`（L456-762）
  - P6=`backend/tests/test_booking_concurrency_root_migration.py`（L763-932）
  （L番号=patch file内の行番号、実測。前回監査 §1 の6path一致と同一）
- **受入①〜⑨**: 本部長殿便（`queue/inbox/shogun-second.yaml` msg_20260806_083105_4fea0002・nonce=HONBUCHO-RES-STAGE1-CYCLE2-GATES2-4-20260806-001）より逐語転記。裁定・言い換えはせぬ。
- **危うき3件**（前工区・己の申告）: F1=staff経路idempotency未配線／F2=fk_check失敗時already-committed自己rollback無し／F3=idempotency_key未使用時のexisting簡易replay早期return。

## §1 6path × 受入①〜⑨ 対応表

凡例: ●=直接担う（実装/testを実測で確認） ○=部分的に担う（非対称・片側のみ等） —=担わぬ

| 受入 | P1 booking.py | P2 appointment_service | P3 booking_service | P4 test_phase2_2 | P5 concurrency_root | P6 test_migration |
|---|---|---|---|---|---|---|
| ①全6path実読し誤り修正 | ●読了(誤り0) | ●読了(誤り0・F1記録) | ●読了(誤り0・F3記録) | ●読了(誤り0) | ●読了(誤り0・F2記録) | ●読了(誤り0) |
| ②門2 non-PII scan・重複1ならapply停止 | — | — | — | — | ●`scan_active_overlaps`/`scan_slot_granularity`定義(L54,L82 相対) | ●`test_gate2_baseline_scan_zero_and_15_minute_grid` + **`test_gate2_duplicate_stops_before_any_schema_mutation`**(直接該当・前回監査で未記載だった新規発見) |
| ③rollback backup SHA一致後のみapply | — | — | — | — | ○`apply_booking_concurrency_root`定義のみ・**SHA照合コード0件**(実測=`sha`/`backup`文字列 grep 0hit) | ○`test_gate3_rehearsal_schema_backfill_and_exact_rollback`はfile-levelバックアップ**復元の演習**のみ・SHA一致判定はtest内にも無し |
| ④13項matrixを明示matrixで全走 | — | — | — | ○(item2,3,5相当の個票あり) | — | ○(item1,4,6,8,9,12相当の個票あり) |
| ⑤TTL block/reclaim/409/reconnect/orphan0 | ●`Idempotency-Key`header中継(L9) | **—(F1: 0件・importにも無し)** | ●`acquire_idempotency`/`complete_idempotency`呼出(L171,L240相対) | ●`test_exact_request_replay_returns_same_appointment_id`/`test_durable_idempotency_key_and_slot_claims_after_migration` | ●`acquire_idempotency`/`complete_idempotency`定義(L161,L198相対) | ●`test_idempotency_reconnect_mismatch_and_stale_pending_does_not_block_slot` |
| ⑥staff/Web create/update/cancel slot claim契約 | — | ○**createのみ**(`claim_appointment_slots`呼出・update/cancel対象外diff) | ●create/update/cancel 3関数とも touch(L27,L212,L245相対@@見出し実測) | — | ●`claim_appointment_slots`/`release_appointment_slots`定義 | ●`test_slot_claims_block_offset_overlap...`/`test_cancel_release_allows_slot_reuse` |
| ⑦migration後 旧code+新testで陽性対照2件RED維持 | — | — | — | — | — | —(**gap・item13と同一根**) |
| ⑧pre/post overlap=0・FK/integrity OK | — | — | — | — | ●`PRAGMA foreign_key_check`呼出（**ただし已にcommit後=F2**） | ○baseline系testでoverlap=0確認のみ・FK整合性testは無し |
| ⑨local commit可・push/PR厳禁 | — | — | — | — | — | — |
（すべての path・test に**共通の運用制約**であり、単一pathが「担う」性質の物ではない） |

## §2 ★誰も担っておらぬ条件★（眼目）

- **②の一部**: scan自体は P5/P6 で担われるが、**scanを「clean隔離DB」上で走らせる事**（受入②の`clean隔離DB`要件）はどのpathにも実装が無く、**運用手順（人が隔離DBを用意する事）に依存**。patch自体はDB隔離を強制しない。
- **③（全体）**: rollback backup **SHA一致判定コードは6path中0件**。ロールバック手順書（`reserveimage-cycle2-ddl-rehearsal-rollback-20260806.md`、患者6pathの対象外の別file）に**手順として**書かれているのみ。∴ **「SHA一致後のみapply」を機械的に強制する物はpatchの中に無い**（前回監査F2「fk_check失敗時already-committed」と同根＝P5のapply関数はSHA確認を待たずにcommitへ進む設計）。
- **⑤（staff側）**: **F1と直結**。受入⑤の5項目（TTL block/reclaim/409/reconnect/orphan0）は**Web経路（P1/P3/P4/P6）でのみ担われ、staff経路（P2）は0/5**。staffはidempotency_key自体を受け取れないため、⑤はstaffに対して構造的に不成立（「未実装」であって「不合格」ではないが、受入文言は経路を区別していないため字面上は staff 側 gap として現れる）。
- **⑥（staff側update/cancel）**: 受入⑥は「staff/Web **create/update/cancel**」と明記するが、**staff側でslot claim契約が触れられているのはcreateのみ**（P2のdiffはcreate_appointment関数のみ、update_appointment/cancel_appointment相当は本patchのdiff対象外＝実測=P2範囲(L13-59)に`def `新設・変更が1関数のみ）。∴ **staffのupdate/cancelにおけるslot claim契約は、本patch6pathのどこにも担われておらぬ**。
- **⑦・item13**: 「移行後も既知欠陥snapshotへ陽性対照を当ててRED維持」を検証するtestは6path中に0件（前回監査§4 item13と同一gapの再確認）。

## §3 危うき3件との対応（下命(3)②の通り織り込み）

- **F1（staff idempotency未配線）** → 上表 ⑤列P2「—」および ⑥列P2「○createのみ」の**両方**として現れる。**「担われておらぬ条件」の形＝受入⑤・⑥ともにstaff側で構造的欠落**（下命の予告「⑤⑥のどれを誰も担っておらぬか」と一致）。
- **F2（fk_check失敗時already-committed・自己rollback無し）** → 上表 ③列P5「○」・⑧列P5「●(ただし)」の**注記**として現れる。受入③の「SHA一致後のみapply」を強制する機構がP5に無い事の直接の裏付け。
- **F3（existing簡易replay早期return・idempotency_key未使用時）** → 上表には独立の列を割かず、**⑦（陽性対照RED維持・gap）と同根の懸念**として記録に留める：idempotency_keyを送らないWeb clientの`_check_conflict`未通過という経路が、⑦のような陽性対照testで検出される保証が無い（⑦自体が6path中0件のため）。

## §4 13項matrixの走らせ方（★紙上のみ・実走せぬ★・下命(3)④準拠）

出所=前回監査 §4（`docs/incident_logs/2026-08-06_reserveimage_cycle2_patch_readonly_audit_a4.md`）。本節では**走らせる順序**のみを紙上で並べる（実行はせぬ）。

| 走行順 | item | 前提 | 走らせる場所 |
|---|---|---|---|
| 1 | ①baseline duplicate scan | 隔離DB用意 | P5 `scan_active_overlaps`/`scan_slot_granularity` を最初に走らせ overlap=0 を確認できねば以降を試みない |
| 2 | ②同key/同payload | 1がGREEN | P6 `test_gate2_duplicate_stops_before_any_schema_mutation`（apply未実施のまま重複検知を先に確認） |
| 3 | ③同key/異payload | 2がGREEN | P4 `test_durable_idempotency_key_and_slot_claims_after_migration` 後半 |
| 4 | ⑫migration rollback演習 | 1-3がGREEN・migration未適用のまま | P6 `test_gate3_rehearsal_schema_backfill_and_exact_rollback`（rollback手順を**先に**演習し、backup経路が機能する事を確認してからのみ次段=実apply相当のstepへ進む設計） |
| 5 | ⑤真の2接続same slot | 4がGREEN | P4 `test_true_two_connection_same_slot_only_one_active_row` |
| 6 | ⑥offset overlap / ⑧confirmed/tentative | 5がGREEN | P6 `test_slot_claims_block_offset_overlap_and_partial_index_blocks_status_bypass` |
| 7 | ⑨cancel後のslot再利用 | 6がGREEN | P6 `test_cancel_release_allows_slot_reuse` |
| 8 | ④restart/reconnect後のretry | 7がGREEN | P6 `test_idempotency_reconnect_mismatch_and_stale_pending_does_not_block_slot`（「真のprocess再起動」は未検証である旨を走行前提として記録した上で走らせる） |
| 9 | ⑦T/space cross-channel | **gap・新規test要設計** | 6pathに無いため、走行順に置くなら8の後＝新設試験が要る事を明示した上でplaceholder化 |
| 10 | ⑩reschedule atomic rollback | **gap・新規test要設計** | 同上。前回監査finding（release→claim順序ゆえclaim失敗時に旧claimが戻らぬ）を再現するpositive-control相当として9の次に置く設計 |
| 11 | ⑪staff/Web同一contract評価 | 5-8がGREEN | slot claims=真／idempotency=偽 の2軸評価。既存testの結果を突き合わせるのみ（新規実行不要） |
| 12 | ⑬既知欠陥への陽性対照RED維持 | **gap・新規test要設計** | migration適用前snapshotへの陽性対照。9・10と同様、6pathに無いためplaceholder |
| — | ②/③のSHA/隔離DB運用要件 | 全体の前提 | **コードでなく運用手順**（rollback runbook）としてのみ存在。matrix走行順の中には組み込めぬ＝走行順の**外側**に置く運用ゲートとして別途記録 |

**総括**: 走行順1-8は6path内の既存testで直接紙上設計が可能。9・10・12（受入⑦・item13含む）は**新規test設計が前提**であり本監査の範囲外（設計のみ・作成せず）。11は実行不要（突合のみ）。②/③のSHA・隔離DB要件は**matrixの走行順そのものに乗らない運用ゲート**である事を明記する（走らせる対象が無い＝「担い手が無い」の別形）。

## §5 己が本工区で直した誤り

無し（read-onlyゆえ直す手を持たぬ）。

---
生成: ashigaru4 / 2026-08-06 / read-only・紙上設計のみ・apply/worktree/DB/実走 一切なし。

## 附記 (家老second下命による保全・scratchpad→docs移し)

写し前sha256(scratchpad)=d5f9a0c819951f3e6dd12b7fccadd70a0b94f677bfb811d2769258daae3fad8b（76行） / 写し後sha256(本file・移し直後・本附記追加前)=d5f9a0c819951f3e6dd12b7fccadd70a0b94f677bfb811d2769258daae3fad8b（同一・一致） / 移し元=`/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/11d54616-ba60-4c72-ad20-0ea81b1b78d9/scratchpad/w_ashigaru4_6path_acceptance_matrix_20260806.md`。
