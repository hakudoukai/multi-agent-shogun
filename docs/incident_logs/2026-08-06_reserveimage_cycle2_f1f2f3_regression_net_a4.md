# 足軽4号 → 家老second/軍師second: F1/F2/F3 回帰の網 (実走・検証lane owner)

下命: `queue/inbox/ashigaru4.yaml` msg_20260806_141548_72ff7d0e（家老second→足軽4号、14:15:48）。
本便は★実走★（設計のみに非ず）。実装ファイルは一字も変更していない。

## §0 lane / worktree / branch (下命⑦形式)

- lane owner = 足軽4号（検証 lane。実装には触れず）
- worktree = `/tmp/resimg-verify4-cycle2-20260806`（★新設・足軽1号の `/tmp/resimg-cycle2-impl-20260806` とは別木★）
- branch = `ashigaru4-verify-cycle2-20260806`（新規ローカルbranch。base=`7d463edae84c704edabbd9da5465078dc62e55b1`）
- 適用patch = `/home/hakudokai/hermes-departments/honbucho/reports/reserveimage-cycle2-gate2-4-handoff-20260806.patch`
  （★足軽1号の木を読取・改変せず、同一patchを自分の隔離木へ独立適用★。`git apply --check`で無傷確認後apply）
- 境の再確認 = 下命本文で家老second殿が独立測定した境界（/tmp書込のみ・/mnt/c非連結・remote在るがpush禁）を継承。
  当職も `git -C /tmp/resimg-verify4-cycle2-20260806 remote -v` で同一remote（`git@github.com:hakudoukai/hakudokai-dev.git`）を確認済——push一切せず。
- ★baseline（七項⑵の再現手順・家老second殿 msg_20260806_144535_e5defbf0 ④要請への回答）★=
  `git -C /tmp/resimg-stage1-runtime-20260806 worktree add -b ashigaru4-verify-cycle2-20260806
  /tmp/resimg-verify4-cycle2-20260806 7d463edae84c704edabbd9da5465078dc62e55b1` の後、
  `git apply /home/hakudokai/hermes-departments/honbucho/reports/reserveimage-cycle2-gate2-4-handoff-20260806.patch`
  （足軽1号木への直接連結・写しではなく★同一patch fileを自木へ独立適用★）。
  ∴ `booking_concurrency_root.py`が足軽1号木と★中身同一(sha16=50641e23ac1062b9)★なのは
  ★裁定「既存prototypeは土台」に適う独立適用の結果★であり、木の連結・流用ではない
  （家老second殿の独立測定=impl木mtime 08:16:35 早・当職木mtime 14:22:28 遅、両者ともpatch適用時刻の差を表すのみ）。

## §1 母集団宣言 (下命③㈠ writer全数)

母集団命令（貼りそのまま、head不使用）:
```
/usr/bin/grep -rl "INSERT INTO appointments\b\|INSERT INTO \"appointments\"\|UPDATE appointments\b" \
  --include=*.py . 2>/dev/null | sort
```
→ 35件ヒット（test file・migration DDL含む）。うち production writer（非test・非DDL）へ絞込:

| # | file | 操作 | 備考 |
|---|---|---|---|
| 1 | `backend/services/appointment_service.py` | INSERT(L217)/UPDATE(L386,429,486,592) | ★staff主writer・F1対象★ |
| 2 | `backend/services/web_reservation/booking_service.py` | INSERT(L218)/UPDATE(L345,400) | ★web主writer・F2/F3対象★ |
| 3 | `backend/db/migrations/booking_concurrency_root.py` | INSERT(L241, rename経由)/UPDATE(idempotency表) | ★F2本体★（今回patchで新設） |
| 4 | `backend/api/appointment_detail.py` | UPDATE(L107) | 個別項目編集 |
| 5 | `backend/api/appointment_grid.py` | UPDATE(8箇所: L504,512,522,551,562,731,820,834) | grid上のstatus/移動系 |
| 6 | `backend/api/booking_manage.py` | UPDATE(L279) | 予約時刻変更 |
| 7 | `backend/api/cancel_stats.py` | UPDATE(L105) | キャンセル系 |
| 8 | `backend/api/email_parser.py` | INSERT(L109) | ★メール経由の新規作成・Web/Staffいずれとも別の第三の作成経路★ |
| 9 | `backend/routers/next_appointment.py` | INSERT(L71) | 次回予約提案からの作成 |
| 10 | `backend/services/diagonal_service.py` | INSERT(L117,146)/UPDATE(6箇所) | ななめ予約リンク（当職W20260806a4で既発見の呼出先） |
| 11 | `backend/services/prediction_service.py` | UPDATE(L299,386) | 予測score書込（当職既発見の呼出先） |

除外・理由:
- `reports/reservation_r_a_visual_proof_20260702/e1_proof_script.py`（INSERT検出）= 一回性の検証scriptで本番importグラフ外、writer母集団から除外。
- `backend/services/appointment_lock.py` = `appointments`はSELECTのみ（実測=`grep -n appointments`→L26 SELECT一件のみ）、writerでない。
- `backend/api/web_reservation/booking.py` = `booking_service.create_booking`を呼ぶ薄いrouterで直接SQL writeなし。

★新規発見（本便で追加）★: #4-9・#10-11 は当職の前回工区（`_create_appointment_commit_boundary_a4.md`、`/mnt/c/Projects/hakudokai-dev`側の別branch実測）でも一部言及したが、本便は★cycle2 branch (`stage1/reservation-cycle2-concurrency-idempotency`) 側での独立再確認★であり、`email_parser.py`・`next_appointment.py`・`appointment_grid.py`・`cancel_stats.py` は前回工区の母集団に含まれていなかった（前回はcreate_appointmentの呼出木限定）。∴ 本便が写しでなく★母集団を広げた独立測定★である。

## §2 RED の提示 (下命③㈡・実走)

成果物: `backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py`（278行・
sha256=`b3a4d65d5ed3017f544aa93c390cbafde74cb0aef2829c0249d475e51a901d65`・当職実測）。
実行コマンド: `/tmp/resimg-stage1-runtime-venv/bin/python -m pytest backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py -v`

```
test_39_f1_staff_retry_returns_409_not_same_id_red          PASSED（documentary=409実測の記録）
test_40_f1_staff_retry_should_return_same_id_red             FAILED（★F1 RED本体★）
test_41_f2_fk_check_failure_leaves_schema_committed_red       FAILED（★F2 RED本体★）
test_42_f2_dangling_row_survives_failed_migration_documents_defect  PASSED（documentary）
test_43_f3_keyless_replay_should_409_not_silently_succeed_red FAILED（★F3 RED本体★）
test_44_f3_keyless_replay_actual_behavior_documents_conflict_with_a1 PASSED（documentary）

3 failed, 3 passed in 1.33s
```

★grepの0ではなく、pytestを現に走らせた上でのFAILED 3件★（下命の禁則「grepの0はREDの証に成らぬ」に対応）。

### §2-1 F1（staff経路idempotency未配線）

oracle（本部長裁定・shogun_second_state_snapshot_1130.md L24）=「first=success／retry=same ID／active=1／extra=0、409をGREENと数えぬ」。
- 実測: `appointment_service.create_appointment` を同一paramsで2回呼ぶと、1回目success・2回目は
  `HTTPException(status_code=409, detail="ダブルブッキング: DB slot claimが競合しました")` を送出（
  `claim_appointment_slots`のPK衝突→本patchが新設したtry/exceptで捕捉）。
- ★本patchはF1を完全修復していない★＝slot claim PKによる物理的重複防止（active=1は成立）は追加されたが、
  「retryが同一appointment_idを返す」という真の idempotent retry は staff側に未実装（`CreateAppointmentRequest`/
  `create_appointment`いずれにも`idempotency_key`概念が無い、実測=`grep -n idempotency_key backend/api/appointments.py backend/services/appointment_service.py`→0件）。
- ∴ oracle「409をGREENと数えぬ」に照らせば★現状もなおF1は未解消★。

### §2-2 F2（apply_booking_concurrency_root fk_check失敗時 自己rollback無し）

設計出所=足軽2号 `_f2_direct_regression_test_design_a2.md`（紙上設計・未実行）を当職が実装・実走。
- 仕込み: `appointment_history`へ`appointment_id=999`（存在せぬ参照）の行を`PRAGMA foreign_keys=OFF`下でINSERT。
- 実測: `apply_booking_concurrency_root`は`RuntimeError("foreign_key_check failed: 1")`を送出するが、
  desired contract（fk_check失敗時はroot tables=`booking_idempotency`/`appointment_slot_claims`が
  commitされたまま残ってはならぬ）に反し、`root_tables_present(conn)`が★True★のまま
  （L284の`conn.commit()`がtry節内・L293のfk_checkがtry/except/finallyの外という構造上、
  例外送出時点で既にスキーマ変更がcommit済＝§1のa2独立再算出と一致）。

### §2-3 F3（idempotency_key未使用時のexisting簡易replay早期returnが「key無しは409」契約に反する）

oracle（本部長裁定）=「F3は『key無しは409』の負契約」。
- 実測: `create_booking`をidempotency_key無しで同一内容2回呼ぶと、2回目は`existing`一致により
  例外を上げず既存appointmentを返却（`booking_service.py` L270-278実測の早期return）。
- `pytest.raises(BookingConflictError)`ブロックが「DID NOT RAISE」で失敗＝現状は409を返さない。
- ★重要な食い違い（裁定せず記録のみ）★: 足軽1号の既存test
  `test_exact_request_replay_returns_same_appointment_id`（`test_phase2_2_booking.py`）は
  ★同一シナリオ（key無し・同一内容2回）を「retry==first・エラー無し」が正しい仕様として
  既にGREENで固定している★。本便のoracle（本部長裁定「key無しは409」）と★直接矛盾★する。
  当職はどちらが正か裁定せず、家老second/軍師second/本部長殿への確認事項として提示する。

## §3 回帰の網 (下命③㈢・実装後に走らせるべきtest一覧)

母集団＝F1/F2/F3 いずれかの対象file（staff writer・web writer・booking_concurrency_root）に
対する既存test file、当職が実走しbaseline確立済（1件も未実施のまま「既存test」と書かぬ、下命規律に従う）:

```
$ /tmp/resimg-stage1-runtime-venv/bin/python -m pytest \
    backend/tests/test_appointment_api.py \
    backend/tests/test_appointment_service.py \
    backend/tests/web_reservation/test_phase2_2_booking.py \
    backend/tests/test_booking_concurrency_root_migration.py \
    tests/test_booking_validator.py -q
113 passed, 2 warnings in 226.12s
```

| file | 件数(baseline全green) | 対象 |
|---|---|---|
| `backend/tests/test_appointment_api.py` | test_db fixture含め39定義（test_01〜test_38＝★既存最大番号38★） | staff API層 |
| `backend/tests/test_appointment_service.py` | (baseline内数を含む) | staff service層 |
| `backend/tests/web_reservation/test_phase2_2_booking.py` | 足軽1号追加のitem13 2 detector + durable idempotency含む | web service層 |
| `backend/tests/test_booking_concurrency_root_migration.py` | gate2/gate3系6test | F2本体の既存test（今回のF2 REDとは別枠・a2§5参照） |
| `tests/test_booking_validator.py` | 6段階バリデーション | staff/web共通validator |
| ★本便新設★ `backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py` | RED 3 + documentary 3 = 6 | F1/F2/F3三値 |

★test採番★: `test_appointment_api.py`の既存最大番号=`test_38`（test_dbフィクスチャ含め39定義、実測
`grep -n "def test" backend/tests/test_appointment_api.py`→39件、うち`def test_db`が1件・番号付test_01〜test_38が38件）
∴ 同fileへ新規追加する場合は`test_39`以降（下命指定どおり・当職は本便では★別新規file★としたため
番号衝突なし。ただし本便内のtest名は`test_39`〜`test_44`の通し番号を独自に付与——同一repo内の
他fileとの採番一致を意図した物ではなく、本file内の可読順序のみを目的とする★）。

## §4 禁則遵守の確認

- 実装ファイル（`appointment_service.py`/`booking_service.py`/`booking_concurrency_root.py`等）は
  ★一字も変更していない★（`git diff --stat`で本便が変更したのは新設testfile 1本のみ、実測済）。
- どこにacquireを置くべきかは書いていない（委員長殿裁定待ちの論点に触れず）。
- 足軽1号の木（`/tmp/resimg-cycle2-impl-20260806`）には一切触れていない（読取すら行わず、
  同一patchを自分の木へ独立適用したのみ）。
- push/PR/main/本番/実患者/公開変更 = 一切なし（local commit止まり）。
- 新規nonceは立てていない（既存 `HONBUCHO-RES-STAGE1-CYCLE2-GATES2-4-20260806-001` を継承）。
- git fetch は行っていない（既存worktreeの既存refをそのまま使用）。

## §5 次報の様式（下命⑦・七項）— 本便時点で埋まる範囲

⑴ lane owner=足軽4号 ⑵ worktree=`/tmp/resimg-verify4-cycle2-20260806` ⑶ branch=`ashigaru4-verify-cycle2-20260806`
⑷ ★修正前RED★=本便§2+§7（3 FAILED実測済）⑸ ★修正後GREEN★=★未定（足軽1号の修正待ち・本便はRED提示までが範囲）★
⑹ local commit=`07b1fbea7e69277058fab2783f5862f35779b0a4`
⑺ 成果path+SHA=`backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py`（349行・
sha256=`a9a162c6f06cda645abfc2a7ae4a5dd89ece1358e6de9c5085efc435277622da`）

★GREENのみの報は受理されぬ、との下命に従い、本便は★RED提示までを完了として申告し、GREENは
足軽1号の修正commit後、当職が同じtestを再実行して追って報じる★（⑷⑸の対を後日埋める）。

## §6 追補: F1方式裁定（14:32:00・両方式直交採用）の五点を回帰網へ織込み

家老second殿 msg_20260806_143200_2de225e4 受領。以下★実走★（追加test 4件・
`test_45`〜`test_47`+`test_46`差替え、commit=`07b1fbea7e69277058fab2783f5862f35779b0a4`）。

| 裁定 | 受入条件 | 織込test | 結果 |
|---|---|---|---|
| ㈠ | Header無し＝ledgerを通らず通常409 | `test_39`（既存） | GREEN(documentary)＝現状ledger自体が無く、物理slot衝突のみが409を出す。ledger未実装ゆえ「ledgerを通らず」は自明に成立（消極的な意味での充足） |
| ㈠追記 | ★家老second殿の再検(14:38:33)により階が絞られた★＝§2-3のF3矛盾（a1の`test_exact_request_replay_returns_same_appointment_id`はWeb入口・位置引数のみでidempotency_key不渡し）は★覆らず★、問いが「どちらが正か」から「共通契約はWeb入口にも及ぶか」へ一段絞られた。当職は裁定せず、本部長殿裁定待ちとして記す |
| ㈡㈢ | 同key同hash=同一ID／異hash=409 | `test_45_f1_idempotency_key_interface_absent_red` | GREEN(documentary)だが★挙動以前にinterface自体が不在★と実測——`create_appointment(...,idempotency_key=...)`は`TypeError`（実測=`grep -n "hashlib\|idempotency_key\|request_hash" backend/services/appointment_service.py backend/api/appointments.py`→0件）。`test_40`は挙動レベルのRED（409送出）・`test_45`はinterfaceレベルの証跡、両方で二重に裏付け |
| ㈣ | acquire→INSERT→slot claim→history→…→commit一単位、途中commit除く | `test_46_f1_mid_sequence_failure_rolls_back_appointment_insert_too` | GREEN(documentary・退行防止ガード)——★当職の別branch実測(`_create_appointment_commit_boundary_a4.md`、/mnt/c側dfa3ac77)にあった「appointments/history 2 commit分離」問題は、★本cycle2 branch(patch適用後)では既に解消済み★と判明（実測=create_appointment本体L123-290内`conn.commit()`は L233の1件のみ）。動的にもslot claim段で例外を注入しrollbackで appointments行が消える事を確認済（=先行独立commitが無い証）。残欠=acquire/complete_idempotencyがこの単位に未だ組込まれていない事のみ(㈡㈢と同根) |
| ㈤ | post-commit副作用はoutbox又は同transaction化を示せ | `test_47_f1_post_commit_side_effects_outbox_unmeasured` | ★UNMEASUREDのまま明記(pytest.skip)★——log_appointment_action等はretry未配線ゆえ「retry時に重複するか」を実走で確かめられぬ。㈡㈢実装後に当職が追走する事を申し送る |

★裁定原文は一字も噛み砕いていない★（家老second殿の指示どおり）。不明語は生じなかった。

## §7 己が本工区で直した誤り

無し（新規実測のみ。前回工区(`_f1f3_greenonly_causal_analysis_a4.md`)の「F1/F3はREDを構成する
入力が存在せぬ」という結論は、当時のoracle定義（重複行そのものの発生）の下では今も正しいが、
★本部長殿が今回oracleを再定義した（409をGREENと数えぬ／key無しは409）ことで、別のoracleの下では
F1/F3ともRED化可能である★ことが判明した。これは前回結論の誤りではなく、oracleが変わった事による
帰結の違いであり、その旨を明記する）。

---
断面（初版）: 2026-08-06T14:33:08+09:00／断面（§6追補・`date -Iseconds`実測）: 2026-08-06T14:39:28+09:00。
base_commit(hakudokai-dev cycle2, /tmp/resimg-verify4-cycle2-20260806起点)=`7d463edae84c704edabbd9da5465078dc62e55b1`。
本repo(multi-agent-shogun)側の断面は本便commit時のHEADを参照されたし。
提出先: karo-second + gunshi-second。
