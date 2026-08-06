# F3 負契約 test 設計 追補1 — 本部長殿御裁反映（L408-429 置換案）— 足軽1号

★本設計は★未見の断面★に対する受入文言を根とする★（家老second `msg_20260806_121929_61c3a56b`・
将軍second裁12:16準拠）: 御裁（本部長殿12:15:34）が対象とした `/tmp/resimg-cycle2-impl-20260806`＋
未commit prototypeの断面は、当隊が独自に「欠陥」と認定したものではない——★本部長殿がその断面において
実装が受入に達しておらぬと示された★のであり、当職は同殿の言を根に本設計を進める。
但し★本便§1-1・§1-2・§3・§4の実測（HEAD一致・行番号・grep結果）は当職自身が
`/tmp/resimg-cycle2-impl-20260806`を直接読んで得た一次実測であり★、これは「借り物」ではない
——書込GO後の実走（pytest）のみが未実施であり、その一点についてのみ「借り物」の語を当てる。
「F3は欠陥」ではなく「本部長殿の断面において実装が受入未達、と同殿が示された」と読め。

★断面（新書式・索引 `2026-08-06_rules_index_a2.md` §G 準拠）★:
測時=2026-08-06T12:21:11+0900。本repo（`multi-agent-shogun`）HEAD=`148ac247303cf58ce0cbc96920cc5296ef308558`
（branch `feat/dd169-d006-conditional-exception`）。対象snapshot=`/tmp/resimg-cycle2-impl-20260806`、
当該worktree `git rev-parse HEAD`=`7d463edae84c704edabbd9da5465078dc62e55b1`（旧便§1-1と★同一★、
本裁が対象とした断面から動いていない事を確認済）。
**本裁が動けば本便は引き直す要あり——この一行を必ず添えて引用せよ。**

★前版へ導線★: 本便は `docs/incident_logs/2026-08-06_f3_negative_contract_design_a1.md`
（227行・sha256=`b2c8679cd94b569eaf19860aa261552aa880f0cddb832219223930d6bbf0fc78`・上記sha一致再確認済）の
★追補★。旧版は1文字も変更していない。旧版§3で「裁定はしない」と留保した衝突点に、本便が下命
（家老second `msg_20260806_121701_6a9a21a7`・12:17:01・出所=本部長殿御裁12:15:34）を反映する。

★冒頭★= 本便も★設計のみ★。`hakudokai-dev`・`newbuild`・`/tmp/resimg-*`への書込み・patch適用・
実走（pytest等）は一切行っていない。本工区で実行したのは `git rev-parse HEAD` / `git status --short` /
`/usr/bin/grep -n` / `sed -n` / 既存 file の `Read`（読取のみ）に留まる。走らせるなの禁を遵守した。
`test_04_double_booking`（staff test）は本便でも1文字も参照・変更していない。

---

## §0 御裁の要旨（下命①、逐語は家老second便 `msg_20260806_121701_6a9a21a7` 参照）

㈠ 旧版§3で衝突を指摘した `test_phase2_2_booking.py` L408-429
`test_exact_request_replay_returns_same_appointment_id` は、key無し silent replay という
DDL無しの一時緩和を検める★自己整合test★（本Cycle2 patchが実装と同一patch内で新規追加・
外部の先行契約ではない）——現行root契約では★superseded側★、独立先行要件ではない。

㈡ 新規条件を絞って両立させるのではなく、既存L408-429を★置換／改名して負契約に★せよ。
同一key+同一payloadのL432-453 durable testは★正★として残す。可能ならAPI境界の実
Idempotency-Keyで補強。同一入力に正反対のtestを併存させない。

㈢ staff `test_04_double_booking` は不触・409契約維持。

㈣ 全入口回帰（Web key有/無・staff key有/無・真の2接続競合・slot claim全writer）。

㈤ 修正適用は将軍隊・独立監査は軍師second。実走・適用は依然GO待ち（本便も設計と差分案まで）。

---

## §1 ㈠置換／改名案（下命③㈠）

### 1-1 対象箇所の再確認

`backend/tests/web_reservation/test_phase2_2_booking.py`（`/tmp/resimg-cycle2-impl-20260806`、
525行、`wc -l`実測）:

- L408: `def test_exact_request_replay_returns_same_appointment_id(file_db_path):` — 旧名・置換対象。
- L432: `def test_durable_idempotency_key_and_slot_claims_after_migration(db):` — 不変（§2参照）。
- L454: `def test_available_slots_invalid_date(db):` — 次関数（置換範囲の下限確認）。

**検め直し方**: `grep -n "^def test_exact_request_replay_returns_same_appointment_id\|^def test_durable_idempotency_key_and_slot_claims_after_migration\|^def test_available_slots_invalid_date" backend/tests/web_reservation/test_phase2_2_booking.py`
→ `408:` `432:` `454:` の3行が返ることを本工区で実測済（cwd=`/tmp/resimg-cycle2-impl-20260806`）。

### 1-2 置換案（旧名・新名・置換後の期待）

| 項目 | 旧（L408-429） | 新（置換後） |
|---|---|---|
| 関数名 | `test_exact_request_replay_returns_same_appointment_id` | `test_web_no_key_duplicate_returns_409_not_silent_replay`（案。「exact_request_replay」の語を残すと同一key版=L432-453と紛らわしいため「no_key」を明記） |
| 呼出しパターン | 同clinic・同patient・同menu・同start_time・key無し2回（`file_db_path`跨ぎ接続） | ★不変★（御裁は呼出しパターンではなく期待を反転する指示のため） |
| 期待（旧） | `retry["appointment_id"] == first["appointment_id"]` かつ `active_count == 1`（silent成功） | ★削除★ |
| 期待（新） | — | 2回目呼出しで `BookingConflictError` を送出（HTTP層では`booking.py`経由409）。`active_count == 1`（追加row無し、旧版§1-4のRED根解消後の意図する挙動）。docstringに「旧版はsilent replay成功を期待していたが本部長殿御裁12:15:34によりkey無し経路は409契約へ置換」と明記。 |
| fixtureシグネチャ | `(file_db_path)` | ★不変★（旧版が2接続跨ぎを`file_db_path`で表現しており、これは維持すべき——同一DBファイルへの別コネクションという構図自体はL432-453のin-memory `db`単一接続とは異なる検証軸のため） |

★置換後コード案（未適用・設計のみ）★:

```python
def test_web_no_key_duplicate_returns_409_not_silent_replay(file_db_path):
    """F3負契約（本部長殿御裁2026-08-06T12:15:34）: Web経路・key無し・同一payloadの
    2回目はBookingConflictErrorを送出し、silent replay成功にならない。
    旧版（test_exact_request_replay_returns_same_appointment_id）はsilent成功+同一IDを
    期待していたが、御裁によりkey無し経路はL432-453の同一key durable replayとは
    ★別契約（409）★として扱うことが確定した——本testはその置換。
    ★覆う母集団=Web create_booking経路・key無し・同一clinic/patient/menu/start_time★
    （同一key+同一payloadの母集団はL432-453の対象——重複しない）。
    """
    first_conn = _open_file_db(file_db_path)
    first = booking_service.create_booking(
        first_conn, 1, "000001", "menu_01_001", "2035-05-01 15:00"
    )
    first_conn.close()

    retry_conn = _open_file_db(file_db_path)
    with pytest.raises(BookingConflictError):
        booking_service.create_booking(
            retry_conn, 1, "000001", "menu_01_001", "2035-05-01 15:00"
        )
    active_count = retry_conn.execute(
        "SELECT COUNT(*) FROM appointments WHERE clinic_id=1 AND patient_id='01_000001' "
        "AND start_time='2035-05-01 15:00:00' "
        "AND status NOT IN ('cancelled','no_show')"
    ).fetchone()[0]
    retry_conn.close()

    print(f"NO_KEY_409_ACTIVE_ROWS={active_count} FIRST_ID={first['appointment_id']}")
    assert active_count == 1  # 1回目のみ生存、2回目は例外で未insert
```

★旧版§4で当職が提案した `test_no_key_duplicate_request_returns_409_not_silent_success`
（新規追加案）は本追補で★撤回★し、この置換案に一本化する——御裁㈡「新規の条件を絞って両立させるな」
に従い、併存ではなく置換とする（Anti-Duplication: 同一シナリオの契約を2つの関数に分けない）。

**検め直し方**: 置換後の`assert active_count == 1`が成立するには、実装側`booking_service.py`
L270の条件式（旧版§1-4のRED根）を先に直す要がある——本便は設計のみでありこの実装修正は
将軍隊の担当（御裁⑤）。実装未修正のままこのtestを適用すればRED（意図通り）。

---

## §2 ㈡ L432-453 durable testは正（下命③㈡）

`test_durable_idempotency_key_and_slot_claims_after_migration`（L432-453、旧版§2㈢で確認済の
関数、行番号は本工区で再実測=L432開始・L453終了〈次関数L454直前〉）は★不変・正として残す★。

★覆う母集団★（同じ行に明記=将軍second裁12:06の書式）: **Web create_booking経路・
`apply_booking_concurrency_root`適用後・同一idempotency-key（"TEST-KEY-1"）+同一payloadの
2回目呼出しのみ**。§1の置換testが覆う母集団（key無し）とは★排他的で重複しない★。

**検め直し方**: `sed -n '432,453p' backend/tests/web_reservation/test_phase2_2_booking.py`
（本工区実測、内容は旧版§には未転記のため今回`/tmp/resimg-cycle2-impl-20260806`で直接確認——
`retry == first`／`appointments`count==1／`appointment_slot_claims`count==2／
`booking_idempotency.state=="completed"`／異なるpayload+同keyは`match="different payload"`で
BookingConflictError、の5 assertを持つ）。

---

## §3 ㈢ API境界の実Idempotency-Key補強（下命③㈢・三値）

**判定=可**（下記精度で「可」——但し新規実装は未着手、根拠のみ本便に記す）。

根拠:
1. `backend/api/web_reservation/booking.py` L59: `request.headers.get("Idempotency-Key")` を
   `booking_service.create_booking` へそのまま渡す実装が★既存★。ヘッダ→service層引数の配線は
   既に存在し新規配線は不要。
2. `backend/tests/web_reservation/test_phase2_2_api.py`（`TestClient`使用、L11で
   `client = TestClient(app)`）に、booking POST自体のHTTPテストは★既存★
   （L68 `test_create_booking_without_auth`: `client.post("/api/web/booking", ...)`）——
   但しこれは★未認証401のみ★を検め、認証済み成功パスのHTTPテストは同fileに★無い★
   （`grep -c "def test_"` で本fileを実測すれば全件が401/422系のバリデーションtestである
   ことが確認できる——本工区では目視確認に留め、gunshi側で再カウント推奨）。
3. 認証cookie取得の前例は同fileのL94/127/135に★既存★（`client.post("/api/web/auth/login", ...)`）
   ——ログイン→cookie→booking POST（Idempotency-Keyヘッダ付）という合成は、既存の2つの
   パターン（ログイン済cookie取得＋booking POST）を★組み合わせるだけ★で新規fixtureや
   dependency overrideを要さない。

**未測の残り**: 実際にこの合成testを書いて通した実績は無い（本便も設計のみ・実装未着手）。
「可」は「配線と前例から見て実装コストが低い」という判定であり、「既に動作確認済」ではない。
**検め直し方**: `grep -n "TestClient\|client.post\|Idempotency-Key" backend/tests/web_reservation/test_phase2_2_api.py`
（cwd=`/tmp/resimg-cycle2-impl-20260806`）で本便の実測（L7/L11/L68/L94/L127/L135にTestClient関連、
`Idempotency-Key`は0件=未実装の確認）を再現できる。

---

## §4 ㈣ 全入口回帰一覧（下命③㈣）

| 入口 | 現に在るtest | 無い物（新規要） |
|---|---|---|
| Web key有 (service層) | `test_durable_idempotency_key_and_slot_claims_after_migration` L432-453（有） | — |
| Web key有 (HTTP層) | 無 | ★新規要★＝§3の合成test（ログイン→cookie→POST /api/web/booking with `Idempotency-Key` header、2回目が同一結果を返すことをHTTPレベルで確認） |
| Web key無 (service層) | §1置換後の `test_web_no_key_duplicate_returns_409_not_silent_replay`（設計のみ・未適用） | 実装修正（`booking_service.py` L270条件式）が先に要る——本便対象外（将軍隊担当） |
| Web key無 (HTTP層) | 無 | ★新規要★（`client.post("/api/web/booking", ...)`を認証済cookieで2回、2回目409を確認） |
| staff key有 | ★概念自体が不在★（`grep -n "Idempotency-Key\|idempotency_key" backend/api/appointments.py backend/services/appointment_service.py` = 0件、本工区実測） | ★三値では測れぬ第四値★＝「該当なし（staff APIはIdempotency-Keyヘッダを受理する設計になっていない）」——新規要か否かは御裁の射程外、将軍隊/本部長殿の設計判断を要する |
| staff key無（通常2度打ち） | `test_04_double_booking`（`test_appointment_api.py` L128-148、HTTP層・`TestClient`使用・有） | — |
| 真の2接続競合・Web | `test_true_two_connection_same_slot_only_one_active_row`（L355-404、`threading.Barrier`で実競合を作る・有） | — |
| 真の2接続競合・staff | 無（`test_04_double_booking`は`client.post`を★逐次★2回呼ぶのみ・`threading`未使用——本工区で該当fileを目視確認、`grep -n "threading" backend/tests/test_appointment_api.py`=0件） | ★新規要★（staff経路にも同種の`threading.Barrier`同期testが無い——Web側にあってstaff側に無いのは非対称。将軍second裁12:06の「重複は見えるが欠落は見えぬ」に該当する型の欠落） |
| slot claim・Web writer | `claim_appointment_slots`呼出=`booking_service.py` L294/L446、testは`test_durable_idempotency_key_and_slot_claims_after_migration`が`appointment_slot_claims`count==2を確認（有） | — |
| slot claim・staff writer | `claim_appointment_slots`呼出=`appointment_service.py` L223（有＝コードは呼んでいる）。**但し`appointment_slot_claims`のrow数を検めるtestは`grep -rln "appointment_slot_claims" backend/tests/`の結果=`test_booking_concurrency_root_migration.py`（migration関数の単体test、staffのAPI経由ではない）と`test_phase2_2_booking.py`のみ——staff API（`test_appointment_api.py`）側に`appointment_slot_claims`を参照するtestは0件（本工区実測）** | ★新規要★（staff経路でも予約作成時に`appointment_slot_claims`へ実際にinsertされているかをHTTP層またはservice層で確認するtestが無い——コードは書いているのにその効果を検めるtestが無い状態） |

★所見★: 6項目中、既存で担保できているのは3項目（Web key有service層／staff key無HTTP層／
真の2接続競合Web／slot claim Web writer——実質4項目）、★新規要が2項目（真の2接続競合staff／
slot claim staff writer）★、HTTP層は Web key有無ともに0件、staff key有は概念不在で第四値。
**staff側の「真の競合」と「slot claim効果」の両方に無テストが集中している**——これは
Web側（本Cycle2 patchの主対象）を厚く測り、staff側（既存機能・不触指示のため触れなかった）が
相対的に薄くなった結果と見る。これ自体は御裁の射程外（新規testの要否は将軍隊/本部長殿判断）
だが、事実として記録する。

---

## §5 母集団宣言・限界（本追補分）

- 読んだ範囲（本追補で新たに読んだ箇所）: `booking.py` 全1-90行（旧版で既読・再確認）／
  `dependencies.py` 全1-33行（新規）／`test_phase2_2_api.py` L1-140（新規、認証・CSRF・
  バリデーション系test群）／`appointment_service.py` L195-235（新規、`claim_appointment_slots`
  呼出箇所）／`booking_concurrency_root.py` L130-155,260-300（新規、claim/release定義とmigration
  backfill）／`test_appointment_api.py` L120-150（旧版で既読・再確認、`threading`不在の確認）／
  `test_booking_concurrency_root_migration.py`はgrep結果のみ（本文未読）。
- 読んでいない範囲: `test_phase2_2_api.py` L140-末尾（menu/available-slots系、本件に無関係と
  判断）／`appointment_service.py`のL235以降（rollback/error handling、本件の主眼=slot claim
  呼出箇所の確認で足りると判断）。
- 未実行: pytest実走・DB migration適用・§3の合成HTTPテスト（未着手・設計提案のみ）。
- ★開ける穴の自己申告★: 本追補は「staff側の2項目」を新規要と指摘したが、★その新規testを
  実際に書いてはいない★——「無い事の指摘」と「埋める事」は別工程であり、次の下命（将軍隊/
  本部長殿の判断待ち）を要する。

## §6 禁則遵守の申告

実走せず（pytestコマンドを一度も呼んでいない）。`hakudokai-dev`・`newbuild`へは一字も書いていない。
`/tmp/resimg-cycle2-impl-20260806`への書込み・commit・patch適用も一切なし（読取のみ、
`git rev-parse HEAD`と`git status --short`で不変を確認したのみ）。`docs/incident_logs/`配下の
既存fileは1文字も変更していない（本fileは新規追加）。`test_04_double_booking`
（`test_appointment_api.py`）は参照のみで1文字も変更していない。`rc`はpipeに通していない。

---

行数・sha256は自己参照循環を避けるため本file内には埋め込まず、家老second／軍師secondへの
提出便（inbox本文）で別途報告する（測時＝提出直前の`wc -l`／`sha256sum`実測値）。
