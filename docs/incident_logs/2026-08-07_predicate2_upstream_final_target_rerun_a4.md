# 述語② 上流側 — 新 final target 再走 (足軽4号)

測時(執筆開始)=2026-08-07T02:44:05+09:00・測時(script実行)=別途下記コマンド出力参照・base=下記

## §0 経緯・指示

karo-second msg_20260807_023716_3c3cfac4 (2026-08-07T02:37:16) ＝ 本部長殿逐語令
「最終commitの後に a2/a4/a5/a6 全述語再走 → 軍師監査」を受け、旧断面
(target=4a0e9036ed94022d79baa4a1e2cf88d5827eec12) にて完了済の述語②上流側測定
(commit 0・成果物 /tmp/resimg-verify4-predicate2-upstream-20260807.txt) を、
新 final target (target=ae1d2a9932ace06693a02b81e20a15284858826b・足軽1号
E-3⑤ 完了後) にて引き直したもの。

**旧票の結論を継がず、新targetにて母集団・判定・陽性対照を引き直した**
（karo-second令④「対照が外れておれば外れておると書け・期待値へ寄せるな」に従い、
結果を確認する前に期待値を書かない方針で実行した）。

## §1 木・base (実測)

```
$ GIT_OPTIONAL_LOCKS=0 GIT_NO_LAZY_FETCH=1 git -c gc.auto=0 -c maintenance.auto=false \
    -C /tmp/resimg-verify4-final-target-20260807 log -1 --format='%H %ci %s'
ae1d2a9932ace06693a02b81e20a15284858826b 2026-08-07 02:32:29 +0900 fix(appointment): E-3⑤ residual raw SQL 機械一貫性根拠 + appointment_detail end_time drift根治
```

- worktree = `/tmp/resimg-verify4-final-target-20260807` (★己で新規作成・detached HEAD★、
  a1の木 `/tmp/resimg-cycle2-f123-clean-20260806` は不触・読取すらせず)
- 作成コマンド = `GIT_OPTIONAL_LOCKS=0 GIT_NO_LAZY_FETCH=1 git ... worktree add --detach
  /tmp/resimg-verify4-final-target-20260807 ae1d2a9932ace06693a02b81e20a15284858826b`
  (2026-08-07T02:40台・GIT_NO_LAZY_FETCH=1 下・promisor partial clone対策)
- HEAD = `ae1d2a9932ace06693a02b81e20a15284858826b` (target と完全一致・実行前後で不変)
- tracked diff = 0 (`git status --short` は untracked のみ・下記§4)
- **tmp_pack 発生 = 0** (`find /tmp -maxdepth 1 -iname '*tmp_pack*' -o -iname '*.pack'` 空)
  ★karo-second令⑤の懸念事象（promisor remote下でのlazy fetch誘発）は本worktree作成では
  発生せず★（GIT_NO_LAZY_FETCH=1 が効いたと見る・断定はせず「発生せず」の実測のみ記す）

## §2 母集団の定義 (先に固定・新target断面で再確認)

- `appointments.status` の全域 = `backend/db/migrations/appointment_tables.py:89` の
  CHECK制約 9値 = `tentative/confirmed/arrived/in_progress/billing/completed/
  cancelled/no_show/late`。★新target断面でも不変（file実読・行番号一致）★。
- terminal (本コードベース自身の語彙) = `appointment_lifecycle.py` のエラー文言
  `"inactive appointment"` と一致する2値のみ = `('cancelled', 'no_show')`。
  ★旧target断面では L172、新target断面では L46 (E-3根治で行番号が移動・
  `InactiveAppointmentSlotMoveError` 型として専用化されたが判定ロジック自体
  `row["status"] in ("cancelled", "no_show")` は不変・実コード直読で確認)★。
- 残り7値は non-terminal として陽性対照に用いる。

## §3 対象コード (新target断面・実読)

`backend/services/appointment_lifecycle.py:162` (`move_appointment_slot`、旧target
断面では `:140`)。

```python
row = conn.execute(
    "SELECT status FROM appointments WHERE appointment_id = ?",
    (appointment_id,),
).fetchone()
if row is not None and row["status"] in ("cancelled", "no_show"):
    raise InactiveAppointmentSlotMoveError(appointment_id, row["status"])
concurrency_root.release_appointment_slots(conn, appointment_id)
concurrency_root.claim_appointment_slots(...)
```

★新target断面での変化点（実コード直読）★:
- 例外型が素朴な `ValueError` → 専用型 `InactiveAppointmentSlotMoveError(ValueError)`
  へ変わった (`ValueError` の subclass ゆえ `except ValueError` は引き続き捕捉可・
  旧script改変不要)。
- 判定式自体 (`row["status"] in ("cancelled", "no_show")`) は**不変**。

## §4 動的反例 (実行・新target断面)

script = `backend/tests/verify_predicate2_upstream_a4_ephemeral.py` (uncommitted・
旧target版から複製し、target表記のみ新target断面へ書き換え。判定ロジック自体は
不変ゆえ検証手法は同一)。

```
$ python3 backend/tests/verify_predicate2_upstream_a4_ephemeral.py
```

出力 (全文・sha256=1f403929f320c63589d05ac53484461c445551774908501ceb5ff9e515702be3・
保存先=/tmp/resimg-verify4-predicate2-final-target-20260807.txt・exit=0):

```
=== predicate2-upstream / target=ae1d2a9932ace06693a02b81e20a15284858826b / move_appointment_slot direct call ===
status       terminal?  raised                                        mutated
tentative    False      -                                             True
confirmed    False      -                                             True
arrived      False      -                                             True
in_progress  False      -                                             True
billing      False      -                                             True
completed    False      -                                             True
cancelled    True       cannot move slot for inactive appointmen...   False
no_show      True       cannot move slot for inactive appointmen...   False
late         False      -                                             True

terminal population n=2 all_rejected=True
non-terminal population n=7 all_mutated(positive control)=True
VERDICT predicate2-upstream-present = True
```

## §5 判定

**target ae1d2a9932ace06693a02b81e20a15284858826b の断面における述語②上流側 = 成立
(present)**。

- terminal population (n=2: cancelled/no_show) = 全件 reject (raise・mutation無し)。
- non-terminal population (n=7) = 全件 mutation 成功 (**陽性対照** — 検出手法自体が
  「常に拒否」の偽陽性を出していない事の確認。karo-second令④⒜「陽性対照は毎回現に
  陽性を出す事を確かめよ」に対応)。

## §6 旧断面との比較 (令③「答が変わったら其の一行を書け」対応)

**旧target (4a0e9036ed94022d79baa4a1e2cf88d5827eec12) 断面の判定 (present/True) から
変化なし**。判定式・母集団・陽性対照の全てが新target断面でも同一構造で再確認された。
行番号のみ移動 (140→162、terminal文言判定行 172→46) し、例外型が
`InactiveAppointmentSlotMoveError` へ専用化された点のみが差分 (§3 記載)。

## §7 境界順守 (実測)

- 実装fix 0 / commit 0 / push 0 / merge 0 / DDL 0 / migration 0 (本worktreeは
  detached HEAD・tracked file変更なし・untracked scratch 1件のみ = 本script自身)
- a1の木 (`/tmp/resimg-cycle2-f123-clean-20260806`) には一字も触れず(読取すらせず)
- 他の resimg lane (32 dir/file、a2/a5/a6分) には触れず

## §8 己の手で為した事

- `git worktree add --detach` で新木を己で作成 (§1 コマンド実測)
- `backend/services/appointment_lifecycle.py` を新target断面で直読 (§3)
- ephemeral scriptを新target断面で実行し出力を保存・sha256を己で算出 (§4)
- 旧target時の出力ファイル (`/tmp/resimg-verify4-predicate2-upstream-20260807.txt`)
  と本票の出力を突合し、判定・母集団構造が同一である事を確認 (§6)

## §9 判らぬ・第四値

- `InactiveAppointmentSlotMoveError` 専用型化が呼び手側 (`appointment_service.py`
  update_appointment等) の HTTPステータス整形にどう写像されているかは、本工区
  (述語②上流側=domain command本体のみ) の射程外ゆえ ★未確認 (unconfirmed)★。
  呼び手側の受け取りは別述語 (呼び手guard/status-only site系) の射程と見る。
