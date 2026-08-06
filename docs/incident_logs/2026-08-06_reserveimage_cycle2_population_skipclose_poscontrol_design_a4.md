# 足軽4号 → 家老second/軍師second: population 3段再測 + ㈤skip閉鎖 + 陽性対照3種 設計

下命4通に対する一括応答:
- `msg_20260806_151546_b882c9a0`（15:15:46・pytest.skip差戻し）
- `msg_20260806_152532_b35fff23`（15:25:32・11の述語不一致・reactivate追加）
- `msg_20260806_152756_1f9a6b8a`（15:27:56・陽性対照3種の正本降下）
- `msg_20260806_153443_0c55ef39`（15:34:43・数の三段様式化）

★工区は変わらず（本便は設計＋閉鎖のみ。全11 writerの重複/欠落0の実走は
足軽1号のWeb F3 commit＋cancellation/no_show共通command化の後に願う、との下命を順守）★。

## §0 lane / worktree / commit

- lane owner=足軽4号（検証lane。実装ファイル一字も変更せず）
- worktree=`/tmp/resimg-verify4-cycle2-20260806`（継続）・branch=`ashigaru4-verify-cycle2-20260806`
- 断面commit=`8184b23`（本便の直前commit・§B参照）。当職の木は依然`8b95464`基準
  （`96aa31d`＝a1のWeb F3 commitは§A-1でpopulation再測目的のみ一時sync、§Bのtest実走は`8b95464`基準のまま）。
- 断面刻=`2026-08-06T15:47:32+09:00`

## §A 母集団の三段化（下命④・様式改訂への応答）

### §A-1 file predicate（当職独立再測・生→除外列挙→残）

母集団命令(丸ごと):
```
/usr/bin/grep -rln -E "(INSERT INTO appointments|UPDATE appointments|DELETE FROM appointments)" backend --include="*.py" | sort
```

⑴ 生の数（除外零）= **24**（当職実測・家老second殿の24と一致）
⑵ 除外規則を一つずつ:
   - 規則A=`/tests/`パスを除く → `/usr/bin/grep -v "/tests/"` → **12**（★当職の木は自作test file
     `test_reserveimage_cycle2_regression_f1f2f3_a4.py`を含むため、家老second殿の13より1少ない
     ——これは誤りでなく★母集団自体が違う★事に因る。後述§A-3で解消★）
   - 規則B=`migrations/`または`booking_concurrency_root`を含むpathを除く →
     `/usr/bin/grep -v -E "migrations/|booking_concurrency_root"` → **10**
⑶ 残った数=**10**（当職の木・自作test file 1件を除いた真の production writer file 数）

★除いた側（規則A適用前後の差）★= 12件（うち11件がa1側にも存在するtest file、1件が当職自作）。

### §A-2 96aa31d(a1最新)との突き合わせ（read-only・git objectのみ・a1の木は不触）

`git cat-file -t 96aa31d` で当該commitが当職の木のobject storeから解決可能な事を確認
（a1の作業ディレクトリには一切touchせず）。`96aa31d`の親=`8b95464`（直系・一commit差）。

★当職の木の該当3file（`booking.py`/`booking_service.py`/`test_phase2_2_booking.py`）を
`git show 96aa31d:<path> > <path>`で一時sync後、同一grep命令を再実行★:
```
$ /usr/bin/grep -rln -E "..." backend --include="*.py" | sort | wc -l
24   ← ★不変（8b95464でも96aa31dでも file-level集合は同一。差分は既存fileの中身のみ）★
```
∴ **家老second殿の24と当職の24は同じ集合**である事を確認済み（file setに変化なし）。

### §A-3 「13」との差の所在（★裁定を要さぬ・機械的に説明可能★）

当職の12（tests除外後）は「a1側11 file + 当職自作1 file」の合算。家老second殿の13は
当職の木に存在しない`/tmp/resimg-cycle2-f123-clean-20260806`（a1の実作業ディレクトリ、当職不触）
上の実測であり、★13-11=2件の差が当職からは検分できない★（a1の木を読む事自体が禁則）。
∴ ★当職はこれ以上この差を追えない（境界=足軽1号の木不触）事を明記し、以後は
「file predicate生24・test除外後12(当職自作込み)・migrations除外後10(production)」を
当職の正本数として使う★。家老second殿の13との差分解消は当職の権限外（上位判断を仰ぐ）。

### §A-4 function predicate（生の数を先に・下命④の直接要請）

母集団命令(丸ごと、当職作成・機械的抽出。手法=`def `をtop-levelから走査し、次のsame-or-shallower
indentの`def`までを関数bodyとしてgrep照合。ソース=本便添付scriptの通り、repo外scratchpad保存):
```python
# backend/ 配下 *.py を全走査し、関数bodyに INSERT/UPDATE/DELETE INTO appointments を含む
# ものを列挙(正規表現一致・importや呼出し先追跡はせず、bodyの字面一致のみ)
```
⑴ 生の数（除外零・全56関数の中に上記文字列一致を含む関数）= **56**
⑵ 除外を一つずつ:
   - 規則A=`/tests/`を含むpathを除く → **23**
   - 規則B=`migrations/`を含むpathを除く → **21**
⑶ 残った数=**21**（production関数・当職の機械的抽出のみ、意味的絞込み無し）

一覧（21件）:
```
appointment_detail.py:api_update_detail
appointment_grid.py:_execute_cancel / change_appointment_status / move_appointment
booking_manage.py:change_booking
cancel_stats.py:api_cancel_with_reason
email_parser.py:_create_appointment_from_parsed
next_appointment.py:book_next_appointment
appointment_service.py:cancel_appointment / create_appointment / transition_status / update_appointment
diagonal_service.py:cancel_linked_appointment / create_diagonal_appointment / propagate_status / update_linked_appointment
prediction_service.py:get_daily_prediction / save_prediction
booking_service.py:cancel_booking / create_booking / update_booking
```

★a1の「11(create2/inactivate5/reactivate1/move3)」は当職の21から★さらに絞られた数★であり、
どの規則で11件まで絞ったかは下命④の指摘通り★a1側に未だ明記されておらぬ★。
当職はこれ以上a1の絞込み規則を推測しない（推測は越権・母集団を歪める）。
★仮説（裁定せず提示のみ）★= 当職の21のうち、`api_update_detail`(個別field編集)・
`api_cancel_with_reason`(cancel_statsは統計記録目的でwriterとしては別経路の可能性)・
`prediction_service`の2件(score/date書込・slot操作ではない)・`diagonal_service`の一部
(linked appointmentの間接操作)などが「直接slot操作」の定義から外れ得ると当職は考えるが、
★これは当職の推測であり、正式な絞込み規則ではない★。

## §B ㈤ pytest.skip 閉鎖（下命①・最終受入不可への応答）

★pytest.skipを全廃し、実走testへ置換済（3件・test_47a/b/c）★。commit=`8184b23`。
sha256=`ca75aed8762a9353430cf430c851f6da81a2ac34d87a82e8d907b640ac4b5eeb`・447行。

### §B-1 test_47a（重複0・陽性対照①）= ★PASSED★
`log_appointment_action`をカウントpatchし、同一idempotency_keyでfirst+retry計2回呼出し。
実測=呼出し回数**1**（重複零）。replayが`idem_outcome=='completed'`でpost-commit code(L329〜)
より前段(L241-244)で早期returnする構造がそのまま効いている事を実走で確認。

### §B-2 test_47b（crash-after-core-commit→replayで欠落せぬ事の陽性対照②・本命）= ★FAILED（RED・欠陥実在）★
`log_appointment_action`を「core commit直後にプロセスが落ちる」形でSystemExit注入→
例外復旧後、★同一idempotency_keyでreplay★→ appointment自体は存続するが
`appointment_logs`行は**恒久的に0のまま**（replayが早期returnしL329以降へ到達しない構造ゆえ）。
```
F1_PC_CRASH_APPT_EXISTS=1 F1_PC_CRASH_AUDIT_LOG_ROWS_AFTER_REPLAY=0
```
★裁定③択のうち㈠(同transaction化)・㈡(outbox+replay復旧)いずれも★現状未実装★である事の
直接証拠。当職は検証laneゆえ実装できず、欠陥をRED相当のassertで固定するに留める。

### §B-3 分類提案（裁定せず・根拠のみ提示）
- `log_appointment_action`（audit log）: response契約に現れぬ(criterion㈢の字義には合致)が、
  ★書込みであり"read-only enrich"ではない★ため㈢の文言にそのまま乗らない。かつ元設計から
  best-effort(自関数内try/except)だが、★replay短絡により再試行の機会自体が失われる★のは
  idempotency配線が生んだ新しい穴であり、既存のbest-effort契約とは性質が違う。
  ∴ 当職の提案=★㈡(outbox化+replay時の再実行)が最も筋が良いが、実装要否は上位判断★。
- `diagonal_service.get_linked_info`/`prediction_service.calculate_prediction_score`:
  呼出し元(`create_appointment`本体)で既にtry/except best-effort、失敗時はresponseから
  黙って省く契約が★fresh呼出し時点で既に存在★（L358-378実測）。∴ replay時にこれらが
  cached_responseに含まれない事は、既存のbest-effort契約の延長であり新規の欠落ではない、
  というのが当職の提案（test_47cで実測・記録のみ・裁定せず）。★㈢に相当すると当職は考える★。

## §C 陽性対照3種の設計（下命①②・本部長裁定の正本に対する設計のみ・読取のみ）

★実走は足軽1号のWeb F3 commit＋cancellation/no_show共通command化の後に願う旨の下命に従い、
本節は設計のみ・実装/実走せず★。

### §C-1 共通の測定契約（3種すべてに適用）
各シナリオで以下を単一の実行から測る:
- `success_count`=成功応答1件のみである事
- `conflict_409_count`=衝突応答が1件のみである事（2件成功や2件409は不可）
- `active_count`=対象slot上のactiveな(cancelled/no_show以外)appointments行数=1
- `claims_count`=`appointment_slot_claims`上の当該(unit_id,slot_start)行数=正数（1、二重claimなら異常）
- 上記4値を★同一実行から★収集し、個別に独立測定しない（タイミング依存のraceを跨いで
  二度測ると別の実行になり意味を失うため）。

### §C-2 ⑴ key無し・Web対Web・真の2接続
- 目的=`_check_conflict`のSELECT→INSERTがTOCTOUである事(本部長裁定で名指し済)を、
  ★逐次呼出しでなく★実際に2つの独立DB接続・2 threadで同時実行して検出する。
- 設計=`threading.Barrier(2)`で両threadを同一start_time/end_time/unit_idの`create_booking`
  直前まで揃え、barrier解放と同時に発火。SQLiteは単一writerロックのため、片方は
  `sqlite3.OperationalError: database is locked`または後着側の`BookingConflictError`の
  いずれかで収束するはず——★どちらに転んでもactive=1・claims正数である事★を確認する
  (旧`_check_conflict`のみの実装ではSELECT時点でロックが無く、両threadが「空き」を見て
  両方INSERTに進み得る、というのが本部長裁定の指摘するTOCTOU)。
- 対象=完全実装後の共通persist domain command(Staff/Web共有)。現状の`booking_service.py`
  (96aa31d時点でidempotency配線済だがslot claim統合は未確認)に対しては、当職はまだ
  独立検証していない(§A-2のsync目的は population count限定・機能検証はせず)。

### §C-3 ⑵ Web対Staff・cross-entry・同枠
- 目的=Web(`booking_service.create_booking`)とStaff(`appointment_service.create_appointment`)
  が★同一unit_id・同一時間帯★へ同時に予約を試みた場合、入口が違ってもslot claim(共通root)
  により片方のみ成功する事を示す。
- 設計=2threadを異なる関数(`booking_service.create_booking` / `appointment_service.create_appointment`)
  へ向け、同様にbarrierで同時発火。両者が★同一`appointment_slot_claims`テーブル★を
  参照している事が前提(現状すでにそう・§0-1でbooking_concurrency_root.py共用を確認済)。
- 期待=success1/409(またはlock起因の例外)1/active1/claims正数は§C-2と同型。

### §C-4 ⑶ offset overlap
- 目的=完全一致でなく★時間帯が部分的に重なる★2件(例=09:00-09:15と09:10-09:25)が
  同一unit_idへ同時に来た場合の挙動。`_check_conflict`のSQL(`NOT (end<=start2 OR start>=end2)`)
  は理論上offset overlapを検出する設計だが、TOCTOU下での実走確認は未実施。
- 設計=§C-2と同型のbarrier並行実行、start_time/end_timeのみをずらす。

### §C-5 併せて: cancel/update後の解放と再claim
- 3シナリオ共通の後段として、成功した1件を`cancel_appointment`/`update_appointment`で
  解放後、★同一slotへの新規予約が成功する事(claims行が消えている事)★を確認する。
- ★reactivate経路(下命②③・`appointment_grid.change_appointment_status`のcancelled→confirmed
  復元枝)も同じ後段に追加する★＝解放後にreactivateした場合、再claimが正しく行われ
  claims行が復元される事を見る(a1の新発見・当職の回帰網に軸を追加する事に同意)。

## §D reactivate 経路（下命②③・スコープ追加の了解）

`appointment_grid.change_appointment_status`のcancelled→confirmed復元枝（唯一のreactivate経路、
a1発見）を当職の回帰網スコープへ追加する事を了解。§C-5に統合済。実装（共通command化）待ち。

## §E ETA・次のaction

- §A(母集団3段)・§B(skip閉鎖・test_47a/b/c実走)= ★本便で完了★。
- §C(陽性対照3種の設計)= ★本便で完了(design only)★。実走は a1のWeb F3 commit(96aa31d、
  済)＋cancellation/no_show共通command化(進行中)完了後、家老second殿の再走下命を待つ。
- ETA=次の再走下命が来次第、即着手（待機は下命に従う受動姿勢であり怠慢ではない旨、
  24時間ノンストップ原則に従い明記）。

## §F 禁則遵守

- 実装ファイルは一字も変更せず（test file 1本のみ変更・commit=`8184b23`）。
- 足軽1号の木(`/tmp/resimg-cycle2-impl-20260806`または`/tmp/resimg-cycle2-f123-clean-20260806`)
  は読取すら行わず。§A-2の`git show 96aa31d:<path>`は共有object storeからの独立取得であり
  a1のディレクトリへのアクセスではない。
- push/PR/main/本番=一切なし。local commit止まり。
- 新規nonce立てず(既存`HONBUCHO-RES-STAGE1-CYCLE2-GATES2-4-20260806-001`継承)。
