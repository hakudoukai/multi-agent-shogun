# 陽性対照 不変識別子 対照表 — target ae1d2a99 (足軽4号)

測時=2026-08-07T02:52:51+09:00

## §0 経緯

karo-second msg_20260807_024231_6a1971a2 (2026-08-07T02:42:31) ＝ 将軍second殿提案
「陽性対照三つを不変識別子で指し直す対照表」＋ task YAML current_order_13
★本部長殿②逐語★:

> 陽性対照は⒜+⒝採用。行番号を廃止し、関数名＋transition契約＋test名で再定義。
> a4はsourceから独立map、fix0/commit0。appointment_service E-3はknown protected
> control。stale diagonal 317/375は実関数/契約/testへ置換。appointment_grid
> change_appointment_status のbooked branch（旧534）は陽性対照から外し、B
> inactive→active phantom-activeの必須RED反例として保持、修正後に回帰testへ昇格。

★本票は「対照が外れておれば外れておると書け・期待値へ寄せるな」の令に従い、
各識別子の実測結果をそのまま記す（全て正であっても・負であっても加工しない）★。

## §1 木・base (実測・§1と同一木を継続使用)

- worktree = `/tmp/resimg-verify4-final-target-20260807` (己で新規作成・detached HEAD)
- HEAD = `ae1d2a9932ace06693a02b81e20a15284858826b` (実測・不変)
- ★target安定性の注記★: task YAML current_order_13 に「本部長殿02:41:03にて
  未受入・supersede予定。a1新commitが出れば其方が新final」と明記あり。★本票は
  本測時点で存在する最新targetに対する断面であり、a1側で新commitが積まれれば
  ★再走が要る★ことを明記して残す（隠さず）★。
- tracked diff = 0・untracked scratch 3件のみ (下記§2-§4のscript)・tmp_pack発生0

## §2 識別子1: `diagonal_service.cancel_linked_appointment` (cancel_both=True 経路)

旧識別子=diagonal_service.py:317 (line番号のみ・stale)。★新識別子=関数名
`cancel_linked_appointment` + transition契約「両方キャンセル時、各appointmentを
`appointment_lifecycle.deactivate_appointment`(共通command)へ委譲」★。

script = `backend/tests/verify_diagonal_positive_controls_identifier_a4_ephemeral.py`
(uncommitted・exit=0・sha256=e59f37e185235f3a2b0108244e85142fc94717e7ce98ae43954866d0c9c4cf0f
・保存先=/tmp/resimg-verify4-diagonal-controls-20260807.txt)

実測 (linked appointment a1/a2 に各2件ずつslot claim済・cancel_both=Trueで呼出):

```
before claims a1=2 a2=2
after  claims a1=0 a2=0  status_a1=cancelled status_a2=cancelled
positive(both released+cancelled) = True
```

**判定 = 陽性 (positive・両者ともstatus=cancelled化+slot claim解放を確認)**。

## §3 識別子2: `diagonal_service.propagate_status` (target_status="no_show" 経路)

旧識別子=diagonal_service.py:375 (line番号のみ・stale)。★新識別子=関数名
`propagate_status` + transition契約「主appointmentがno_show化した時、linked先の
statusをno_showへ伝播しslot claimを解放する」★。

同script (§2と同一実行・出力継続)。

実測 (linked b1/b2に各2件slot claim済・b1へpropagate_status(target_status="no_show")呼出):

```
before claims b2=2  after claims b2=0  status_b2=no_show
positive(linked released+no_show propagated) = True
```

**判定 = 陽性 (positive・linked先のstatus=no_show化+slot claim解放を確認)**。

★備考(推さず記す)★: `propagate_status` はarrivedの場合は元来slot操作を行わない設計
(コード内コメント「非active集合の外(=active)のままclass D(slot-op無し)」)。
本票はno_show経路のみを測っており、arrived経路の陽性/陰性は本票の射程外
(未測・unconfirmed)。

## §4 識別子3 (旧534): `appointment_grid.change_appointment_status` booked-branch

★本部長殿②逐語に従い、本識別子は★陽性対照から除外★し、代わりに★B
inactive→active phantom-activeの必須RED反例★として、現に再現するかを実測する
（陽性対照の枠には含めない）。

新識別子=関数名 `change_appointment_status` + transition契約
「`_FRONT_TO_BACK_STATUS["booked"] = ("confirmed", None)` を受けた際、
new_visit_statusがNoneゆえ `elif new_status:` 分岐(raw UPDATE・
`reactivate_appointment`等の共通commandを経由しない)へ入る」。

script = `backend/tests/verify_b_phantom_active_identifier_a4_ephemeral.py`
(uncommitted・exit=0・sha256=d15961e49b62676d85c2a4181465399772beddae87104dbc17e7e13b60129e33
・保存先=/tmp/resimg-verify4-b-phantom-identifier-20260807.txt)

実測 (cancelled行に対し、①booked-branchのraw UPDATEをそのまま再現 vs
②共通command `reactivate_appointment` を通した場合、を並べて対照):

```
[陰性/RED期待] booked-branch raw UPDATE: before_claims=0 after_claims=0 status_after=confirmed
[陽性対照]      reactivate_appointment:  before_claims=0 after_claims=2 status_after=confirmed

RED(phantom-active)_still_reproduces = True
positive_control_fires = True
```

**判定 = RED(phantom-active) は target ae1d2a99 断面でも依然 再現する
(未修正)**。同じDB層・同じ検出手法で `reactivate_appointment` 経由なら
claim が作成される事 (positive_control_fires=True) を併記し、「検出器が
常にclaim=0を返すだけの偽陽性」でない事を示した。

## §5 まとめ表

| 識別子 (新・不変) | 旧line参照 | 判定 (target ae1d2a99) | 種別 |
|---|---|---|---|
| `diagonal_service.cancel_linked_appointment` (cancel_both=True) | :317 (stale) | 陽性 (positive) | 陽性対照 |
| `diagonal_service.propagate_status` (no_show経路) | :375 (stale) | 陽性 (positive・no_show経路のみ測定。arrived経路は未測) | 陽性対照 |
| `appointment_grid.change_appointment_status` booked-branch | :534 (stale・旧B-2) | RED再現 (未修正・phantom-active) | ★陽性対照から除外・B必須RED反例として保持★ |

## §6 己の手で為した事

- 3識別子それぞれについて対象コードを新target断面で直読し、旧line参照が
  何を指すかを確認 (§2-§4本文の関数抜粋・実コード直読)
- 2本のephemeral scriptを新targetの木で実行し、shaを己で算出
- HEAD不変・tracked diff 0・tmp_pack発生0を実行前後で実測

## §7 境界順守

実装fix 0 / commit 0 / push 0 / merge 0 / DDL 0 / migration 0 / 入口 patch 禁
(§4のRED反例は測るのみ・直さず) / a1の木は不触 / GIT_NO_LAZY_FETCH=1下
