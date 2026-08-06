# appointment_grid.py:534 phantom-active 独立再検証（足軽6号）

下命=karo-second msg_20260807_022337_6404d2e7 工区③。足軽4号の動的実測（軍師second PASS 2026-08-07T02:16:31）を
★読まず・追認せず★、当職自身が target=4a0e9036ed94022d79baa4a1e2cf88d5827eec12 のsourceを実読して
母集団・手順を独立に立て直した（前回のa1 old-RED/target-GREEN独立再現と同型の作法）。

## 対象（a1の木・読取専用）

- 場所=/tmp/resimg-verify4-cycle2-matrix2-20260807（HEAD=4a0e9036 detached、work_started時点・終了時点とも
  `git status --short` は当職着手前から存在する未追跡3件（`detect_undelegated_occupancy_mutation_a4.py`／
  `verify_b2_status_only_a4_ephemeral.py`／`docs/incident_logs/`）のみで不動。当職はこれらに一字も触れず）。
- 実読箇所=`backend/api/appointment_grid.py` L454-478（`CancelAppointmentRequest`/`StatusChangeRequest`/
  `_FRONT_TO_BACK_STATUS`）、L480-566（`change_appointment_status`本体）、L822以降（`_execute_cancel`）。

## 己が実読で組み立てた母集団・仮説（a4の票を見ずに構築）

`_FRONT_TO_BACK_STATUS` マップ実測：
```
"booked"  → (new_status="confirmed", new_visit_status=None)
"arrived" → (new_status=None,        new_visit_status="arrived")
```
`change_appointment_status`のif/elif評価順（L508-566）実読：
1. `new_status=="cancelled"` → 委譲（`appointment_lifecycle.deactivate_appointment`）
2. `new_status and new_visit_status` → raw UPDATE（両方指定時のみ）
3. `elif new_status:` (**L532-539、当該534行はこの枝の中**) → raw UPDATE のみ、委譲なし
4. `elif apt["status"]=="cancelled":` (L540-546) → 委譲（`appointment_lifecycle.reactivate_appointment`）
5. `else:` → visit_statusのみ raw UPDATE

★分岐は上から評価される★ため、cancelled化した予約へ front-status="booked"（→new_status="confirmed"、
new_visit_status=None）を投げると、★真に必要な枝4（cancelled再活性化委譲）へ到達する前に枝3で消費される★
——ここに委譲欠如の根が在ると当職自身のsource読解のみで結論した（a4の主張を先に見ての後追いに非ず）。

## 独立test（own tree・own file・own母集団）

場所=/tmp/resimg-534-phantom-independent-a6-20260807（a1木からの`cp -r`物理複製、`diff -rq`で複製直後の
完全一致を確認、その後 __pycache__ 生成分の差分のみ発生＝実体差分に非ず）。
file=`backend/tests/test_grid_status_reactivation_asymmetry_a6.py`（163行、sha256=
4c2348dfde10157935977597de82348062a0aec282473187c14d5059a04b602e、当職新規作成・a4の既存test file不使用）。

母集団を「grid cancel APIで正規にキャンセルさせ、claim=0を実測確認した本物のcancelled予約」1件×2シナリオ
（陰性用/陽性対照用で個別に新規作成、使い回さず）とした。venv=/tmp/resimg-stage1-runtime-venv（既存資産）。

### 実測結果

| ケース | 投げたstatus | HTTP | status_after | claims_after |
|---|---|---|---|---|
| 陰性 | booked | 200 | confirmed | **0** |
| 陽性対照 | arrived | 200 | confirmed | **2** |

`2 passed`（pytest実行ログより、標準出力に実測値をprint済で丸め無し）。

## a4の主張との突合（合わせに行かず、実測をそのまま記載）

- a4主張=「line534 booked分岐＝旧B-2のまま未委譲」→当職実読でも同一枝を委譲なしと確認＝**一致**。
- a4主張=「動的陰性＝HTTP200なれどclaim0件＝phantom-active」→当職独立test実測でも
  `http=200, claims_after=0`＝**一致**。
- a4主張=「陽性対照＝status=arrivedではclaim作成を確認」→当職独立test実測でも
  `http=200, claims_after=2`（cancel前と同じ30分予約ゆえ2 slot分）＝**一致**。

∴ **独立測と a4 の実測は悉く一致した**。食い違いは無い（合わせに行った結果ではなく、
独自に立てた母集団・手順・test file・仮説導出経路のいずれもa4のものを経由せずに到達した一致）。

## 境の遵守

- 実装fix=0・commit=0・push=0・merge=0・DDL=0（line534は一切変更せず、読むのみ）。
- a1の木＝終始read only（`git status --short`＋HEAD=4a0e9036、work_started前後で不動）。a4の既存artifact
  （detect_undelegated_occupancy_mutation_a4.py／verify_b2_status_only_a4_ephemeral.py）も未読・未使用。
- 自前複製（/tmp/resimg-534-phantom-independent-a6-20260807）内のみで新規test file作成・実行。

## 数の扱い

測時=2026-08-07T02:2x〜02:3x+09:00（JST）。器=`git status`/`cp -r`/`diff -rq`/`sha256sum`/pytest 9.1.1
（既存venv）。範囲=当職新規作成2 test（陰性1・陽性対照1）、悉くPASS。以上（読めぬfileは無かった）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。
