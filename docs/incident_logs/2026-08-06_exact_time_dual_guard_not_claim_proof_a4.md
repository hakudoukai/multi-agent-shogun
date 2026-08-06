# 足軽4号 → 家老second: exact-timeはclaimの証に非ず・陽性対照の錨はoffset overlap（短票）

下命=17:24:19便（家老second・令㈠㈡③）に対応。順「②の票明記(短し)→導出→台帳」の②のみ扱う
（導出は前便で完了済）。

## §0 三sha+worktree欄

- worktree path=`/tmp/resimg-verify4-cycle2-20260806`
- 修正前HEAD=`51f644f30aab22f67ef344fdff49209dc060e95c`
- 提出直前HEAD=`git rev-parse HEAD`実測=下記

```
$ date -Iseconds
2026-08-06T17:26:35+09:00
$ git rev-parse HEAD
21f7a7692ddb06b1cc04fa642c86c68a746afb22
```
機械path+sha:
```
231358df9af32d3bc5904b2a73f590c1ebb9c61edfa331c15fd48d9ad4a5b243  backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py
```

## §1 令㈠ 陽性対照の錨=offset overlap

現RED/GREEN対(`test_offset_overlap_barrier_RED_on_pre_root_schema`↔
`test_offset_overlap_barrier_true_concurrent_partial_conflict`)は既にoffset overlapに
打たれている(前便で構造化済)——現状のまま錨=offset、対応済。

## §2 令㈡ exact-timeのGREENに「二重guardゆえclaimの証に非ず」を明記

`test_web_vs_web_barrier_RED_exact_time_blocked_by_independent_guard`のdocstringへ追記
(commit 21f7a76)。要旨:
- `uq_appointments_active_exact_start`(booking_concurrency_root.py L252-256)は
  `ON appointments(clinic_id,unit_id,start_time)`——start_time完全一致のみを守り、
  offset overlapには効かない。∴ exact-time=claim+indexの二重guard／offset overlap=claimのみ。
- ★本testのsuccess_count==1は「claimが塞いだ証」ではなく「二重guardのどちらかが塞いだ証」に
  留まる★——exact-timeは構造上claimの陽性対照になり得ない(claim/index双方無害化でも
  harnessを測るのみでclaimの効きは測れない為)。

## §3 ③ 因を分かった(裁定せず記録の先)

陽性対照でREDが出ない時の因=「守りが二重」/「harnessが効かぬ」の二通り。offset overlap
(claimのみのguard)でRED→GREEN対を測り直した結果(§1、両testともPASS=claimのみで競合が
止まる事を実測)、exact-timeが「RED化できない」理由は★守りが二重だから★であり
★harnessが効かないからではない★と因を分かった(docstringに明記・commit 21f7a76)。

## §4 GREEN再確認

```
$ pytest backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py -v -s
============================== 5 passed in 17.44s ==============================
```
docstring追記のみ・assert/挙動は無変更(5件PASS維持)。

## §5 次

台帳(⑶site ID／reachable cases／委譲先／test + 分母の増減理由(一件ずつ) + 断面(いつ・どの木))
へ進む。次便で提出する。

## §6 禁則遵守

test fileのみ変更。productionコード不触。push/PR/main/本番=一切なし。
