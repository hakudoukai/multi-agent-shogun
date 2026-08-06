# F3「互換性要件が別に在るか」の調査 (足軽5号)

## 境・未測・限界 (冒頭に置く)

読取のみ。実走・apply・worktree新設・DB接続・commit (当職以外) 一切なし。当PCで読める範囲のみ
(`/tmp/resimg-cycle2-impl-20260806`・`/tmp/resimg-stage1-runtime-20260806` は既存agent (a1/a4/a2) が
本日繰り返し読取アクセスした先例に倣い、読取のみ実施した。書込は一切していない)。

問い=「key無しでも既存予約を成功として返す事を要件として求めておる物が在るか」。裁定 (どちらを採るべきか)
は書かない——予約担当部長殿の物。

## 測時・断面

測時=2026-08-06T10:28:03+09:00。HEAD (multi-agent-shogun)=89685bf202cedef63f30638010116f817ab9ea5d。
出所=本部長殿裁定便 `msg_20260806_102049_e6c63cd2` (10:20:49・将軍second経由で家老second受領)。

## 探した所 (⒜)

1. 仕様書・設計doc: `docs/incident_logs/` 配下 (reserveimage関連8件、本日既存分)・当repo全体の
   `find -iname "*reserveimage-cycle2-concurrency-idempotency-evidence-and-root-design*"`
2. 既存test: `/tmp/resimg-cycle2-impl-20260806/backend/tests/web_reservation/test_phase2_2_booking.py`
3. API契約: `/tmp/resimg-cycle2-impl-20260806/backend/api/appointments.py` (staff側・既読了は他工区分を参照)
4. frontend期待: `/tmp/resimg-cycle2-impl-20260806/frontend/src/features/web-booking/hooks/useWebBooking.ts`
5. 過去の裁定便: `queue/inbox/*.yaml`+`_archive` を `既存予約.*成功として返す|silent.replay|replay.*成功|重複予約.*返す` で検索

## 結果 (三値)

### ㈠在る — コード内コメント (booking_service.py)

`/tmp/resimg-cycle2-impl-20260806/backend/services/web_reservation/booking_service.py`
(idempotency_key分岐の直後・`existing`判定の直前) に、以下の逐語コメントが存在する:

```
# DDLを伴わない限定的なreplay同一視。患者・時刻・内容が同一の
# active Web予約なら、別接続からの再送にも既存IDを返す。
```

この直後 (`if existing and not (root_enabled and idempotency_key):`) が、F3判定doc (足軽1号・足軽4号) の
指す早期return分岐そのものである。∴ ★実装者自身が、この動作を意図した設計として明記している★。

### ㈠在る — 新規test (test_phase2_2_booking.py L408-429)

```python
def test_exact_request_replay_returns_same_appointment_id(file_db_path):
    """同一要求を別接続で再送しても同じ論理予約を返し、rowを増やさない。"""
    ...
    first = booking_service.create_booking(first_conn, 1, "000001", "menu_01_001", "2035-05-01 15:00")
    ...
    retry = booking_service.create_booking(retry_conn, 1, "000001", "menu_01_001", "2035-05-01 15:00")
    ...
    assert retry["appointment_id"] == first["appointment_id"]
    assert active_count == 1
```

両呼出しとも `idempotency_key` を渡していない (シグネチャ上省略=None扱い)。∴ このtestは
★key無しでの同一要求再送が、既存予約IDをそのまま返す事を明示的に要求する契約テスト★である。

**★重要な限定★**=この test は base repo (`7d463edae84c704edabbd9da5465078dc62e55b1`) には存在せず
(`git show <base>:<path>` で当該関数名を検索し0件を確認)、★本Cycle2 patch自身が新規に追加した test★
である。∴ 「独立した既存の外部要件」ではなく、★実装 (booking_service.py の早期return) と同一patch内で
本部長殿御自身が書いたtest★——実装とtestが自己整合している形であり、実装より前から存在する
外部仕様・契約とは性質が異なる。この区別を明示する (⒝出所を同じ行に、の趣旨に沿い正直に書く)。

### ㈡無い (探した所を列挙) — frontend

`useWebBooking.ts` に `idempot`/`重複`/`再送`/`replay` のいずれの語も0件
(`/usr/bin/grep -n` 実測)。★frontend側にこの挙動を前提とした期待は見出せなかった★
(「見つからなかった」であり「存在しないと断定する」ではない——frontend全体を網羅的に読んではいない為)。

### ㈡無い (探した所を列挙) — 独立した設計doc

`docs/incident_logs/2026-08-06_reserveimage_cycle2_gap_test_design_9_10_12_a4.md` §6 が出所として
引用する `reserveimage-cycle2-concurrency-idempotency-evidence-and-root-design-20260806.md` は、
当repo全体を `find` で検索したが★見当たらなかった★ (0件)。★不在の証明ではなく、当PC上で
見つけられなかったに留まる★——hakodoukai-dev側の他branchや別pathに存在する可能性は排除できない。

### ㈡無い (探した所を列挙) — 過去の裁定便

`queue/inbox/*.yaml`+`_archive` を該当語で検索した所、ヒットしたのは当職自身の本日の便のみ
(本工区・前工区の言及)。★本件についての独立した過去の裁定便は見出せなかった★。

## まとめ (裁定は書かぬ・材のみ)

| 探索先 | 三値 | 出所 |
|---|---|---|
| コード内コメント | ㈠在る | `booking_service.py` (idempotency_key分岐直後・existing判定直前) |
| 新規test | ㈠在る (但し実装と同一patch内・外部の先行要件ではない) | `test_phase2_2_booking.py:408-429` |
| frontend期待 | ㈡無い (見つからず) | `useWebBooking.ts` 全文grep hit=0 |
| 独立設計doc | ㈡無い (見つからず・不在の証明ではない) | 当repo全体`find` hit=0 |
| 過去の裁定便 | ㈡無い (見つからず) | `queue/inbox`全箱+`_archive` 検索hit=当職自身の便のみ |

## 母集団漏れの自己申告

1. staff側 (`appointments.py`) ・frontend staff側 (`useAppointmentForm.ts`) は本工区で再読していない
   (F3はweb予約経路の問題であり、既存agent (a4) の別便がstaff側を扱っている為、当工区では対象外とした)。
2. `useWebBooking.ts` 以外のfrontend web-booking配下ファイル (`WebBookingApp.tsx`等) は
   個別に読んでおらず、`useWebBooking.ts`のみをgrepした。他fileに関連する記述が在る可能性は排除できぬ。
3. hakodoukai-dev の他branch・他worktree・過去commitの探索は行っていない (当PCで到達可能な
   `/tmp/resimg-*`2箇所のみを対象とした)。

## 【本工区で己が直した誤り】

無し (読取のみ・裁定を含めず材のみを集めた)。

## 対に成る他工区

`docs/incident_logs/2026-08-06_reserveimage_f1f3_greenonly_causal_analysis_a4.md` (足軽4号・F3の
「不能の因」を分析した別便。当工区は「代替要件の有無」を問うており軸が異なる——直交)。

## 監査体制

暫定二者制 (軍師second + Gemini)。Codex leg は禁令 (2026-07-21事案・SAFETY裁定 seq132707) により停止中。

## 禁則遵守の申告

実走せず。書込GO前のpatch適用なし (hakodoukai-dev ③系統/tmp/resimg-*配下への書込は一切なし・読取のみ)。
newbuildへは一字も書いていない。rc はpipeに通していない。`/usr/bin/grep` を明示使用した。
