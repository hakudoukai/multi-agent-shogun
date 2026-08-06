# target 4a0e9036 の断面における B1／B2 の 到達可能性と phantom 有無（足軽6号・独立測）

下命=karo-second msg_20260807_023331_39442ca6 工区②。足軽5号の述語①票（PASS 2026-08-07T02:28:47）を
★読まず★、target=4a0e9036ed94022d79baa4a1e2cf88d5827eec12 のsourceを己で実読して母集団・手順を独立に立てた
（534独立検証と同型の作法）。

対象＝
- **B1** = `backend/services/diagonal_service.py::propagate_status` の no_show 経路
- **B2** = `backend/routers/next_appointment.py::book_next_appointment` の create 経路

## 対象（a1の木・読取専用）

場所=/tmp/resimg-verify4-cycle2-matrix2-20260807（HEAD=4a0e9036 detached、work_started前後で `git status --short`
不動＝当職着手前から存在する未追跡4件（a4/a5の既存artifact・docs/incident_logs/）のみ、当職はこれらに一字も触れず）。

## 己が実読で組み立てた仮説（a5の票を見ずに構築）

- B1: `propagate_status`内、linkedへのstatus書込は raw UPDATE（未委譲=真）だが、no_show枝は
  `concurrency_root.release_appointment_slots`を経由（claim解放は委譲済）。かつ冒頭guard
  `linked_row["status"] not in (cancelled,no_show,completed)`ゆえ、既にinactiveなlinkedを
  対象にできない＝534型「inactive→active復帰でclaim作られず」の再現路は構造的に無い、との仮説。
- B2: `appointments`へのINSERT自体は raw SQL だが、直後同一transactionで
  `concurrency_root.claim_appointment_slots`を呼ぶ（コード内コメントに2026-08-06修正済と明記）。
  claim欠落型phantomは起こり得ぬ、との仮説。

いずれも実測で検証した（読解のみで結論とせず）。

## 独立test（own tree・own file・own母集団、a5の既存test file不使用）

場所=/tmp/resimg-b1b2-independent-a6-20260807（a1木からの`cp -r`物理複製、`diff -rq`で複製直後の完全一致
確認）。file=`backend/tests/test_b1_b2_reachability_phantom_a6.py`（275行、sha256=
2169e667835963cc4ee732ea2d00421fcd150ddbbaa8ab472abc3b0078e8abdc）。venv=既存資産。6 test、6 passed。

### B1（no_show経路）実測結果

| test | 実測 |
|---|---|
| 到達可能性（POST /api/appointments/{id}/no-show） | HTTP200・linked側status→no_show（実際に到達・伝播した） |
| phantom有無（no_show枝） | linked claims=0（statusもno_show=非活動ゆえ★整合★・phantom-activeの定義(活動的status×claim無し)に該当せず） |
| 陽性対照（arrived枝、既にactiveなlinkedへ） | claims_before=2/claims_after=2（不変、claim操作を行わぬ設計通り） |
| guard実測（linkedが既にcancelled状態でno_show伝播を試行） | linked status=cancelled のまま不変・claims=0のまま（★冒頭guardが機能し534型のinactive→active復帰路は実際に閉じている事を実測で確認★） |

**結論（B1）**: 到達可能性＝**真**（実HTTPで到達・実際にstatusが動く）。phantom-active＝**偽**
（構造的guardと委譲済claim解放により、534型の状態不整合は生じない事を4点の実測で裏付け）。

### B2（create経路）実測結果

| test | 実測 |
|---|---|
| 到達可能性（POST /api/next-appointment/{id}/book） | HTTP200・appointment作成 |
| phantom有無 | status=confirmed・claims=2（★活動的statusとclaimが同一transactionで揃って作られる事を実測確認★） |

**結論（B2）**: 到達可能性＝**真**。phantom-active＝**偽**（claim_appointment_slotsが同一transaction内に
既に組み込まれている事を実測で確認、raw INSERTである事自体はGate3型「未委譲」分類には該当し得るが、
それとphantom-activeの有無は別軸——本工区は後者のみを測る）。

## 副次的発見（測定方法論・境界外・欠陥数へ混ぜず別枠として記す）

B2のtest構築中、`backend/routers/next_appointment.py`が
`from backend.db.sqlite_connection import DB_PATH, get_connection`と★値でimport★しており、
`monkeypatch.setattr("backend.db.sqlite_connection.DB_PATH", ...)`（他routerの`_get_db()`経由test群では
機能する定石）が本routerには効かない事を実測で発見した（初回実行時、appointment_idが返るのに直後の
SELECTで行が見つからず判明——原因を推測で済ませず、`sqlite_connection.py`のDB_PATH定義と
next_appointment.pyのimport文を実読して特定）。書込先は当職の隔離scratch内
（/tmp/resimg-b1b2-independent-a6-20260807/dentalbi_local.db、a1木や主repoとは無関係）に留まった事を
`find`で確認済（漏出0）。本件はtest isolation上の落とし穴であり、本番でDB_PATHを実行時に差し替える事は
無いため実運用上のphantom-active/未委譲問題には該当しない——★測定完了後の副次観測として記すのみで、
本工区の到達可能性／phantom有無の判定・欠陥数には混ぜない★。当職test側で
`monkeypatch.setattr("backend.routers.next_appointment.DB_PATH", ...)`を追加してtest自体を成立させた
（app code不改変、measurement-onlyの範囲内）。

## 境の遵守

- 実装fix=0・commit=0・push=0・merge=0・DDL=0・migration=0。line534・propagate_status・
  book_next_appointmentのいずれも一字も改変せず（読むのみ）。
- a1の木（/tmp/resimg-verify4-cycle2-matrix2-20260807）＝終始read only。work_started前後で
  `git status --short`＋HEAD不動を実測確認。a4・a5の既存artifact（4件）は未読・未使用。
- 自前複製（/tmp/resimg-b1b2-independent-a6-20260807）内のみで新規test file作成・実行。
  副次発見のstray write先もこの隔離scratch内に閉じている事を`find`で確認。

## 数の扱い

測時=2026-08-07T02:3x〜03:0x+09:00（JST）。器=`git status`/`cp -r`/`diff -rq`/`sha256sum`/pytest 9.1.1
（既存venv）。範囲=当職新規作成6 test（B1×4・B2×2）、悉くPASS。判定＝B1到達可能性=真・B1 phantom有無=偽、
B2到達可能性=真・B2 phantom有無=偽。欠陥数へは混ぜず（下命の禁則通り）。以上（読めぬfileは無かった）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。
