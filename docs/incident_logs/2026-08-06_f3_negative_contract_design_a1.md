# F3 負契約 test 設計 — Web create_booking 経路（key無し・同一payload 二度目=409）— 足軽1号

下命=家老second `msg_20260806_120322_639f411f`（12:03:22・宛先=当職）。
出所=本部長殿御回答（11:59:56）。当職の前回 Anti-Duplication 判断（F3 は既存 `test_04_double_booking` が
担保済ゆえ新規 test 不要）は本御回答により覆った。

★冒頭★= 本便は★設計のみ★。`hakudokai-dev`・`newbuild` への書込み・patch適用・実走（pytest等）は
一切行っていない。本工区で実行したのは `git rev-parse HEAD` / `git status --short` / `/usr/bin/grep -n` /
既存 file の `Read`（読取のみ）に留まる。走らせるなの禁を遵守した。

---

## §0 前提（本部長殿裁定・逐語）

家老second便より（内容は前工区で当職が受領した本部長殿原文の転記）:

> ㈠「同じ code path では御座らぬ——`test_appointment_api.py:129-149`＝staff共通 `POST /api/appointments`
> → `api/appointments.py:24,85-96` → `appointment_service.create_appointment` → 同枠2回目409。
> 足軽5号の対象＝Web `create_booking` → `booking_service.py:258-278` の key無し heuristic early return →
> `:280` の `_check_conflict` を迂回する別経路」
>
> ㈡「暫定受入『key無し同一payloadは409』は後者（Web経路）を指す」
>
> ㈢「F3の期待＝key無し時に `:270-278` で silent成功せず、`:280` の通常conflictへ進み409。
> 同一key＋同一payloadのみ durable replay成功。staff testの409契約は変更せぬ」

観測断面（本部長殿引用）＝`/tmp/resimg-cycle2-impl-20260806`・base HEAD
`7d463edae84c704edabbd9da5465078dc62e55b1` ＋ 未commit prototype。

### §0.5 追記（家老second `msg_20260806_120912_c9352560`・12:09:12・将軍second裁12:06 転記）

1. 将軍second裁＝当職が前回「`test_04_double_booking`が担保する」とfile+行番号を書いた記述が、
   本部長殿がその testの経路（staff経由）を特定する★唯一の発見経路★だった。「重複を作る誤りは見えるが
   欠落を作る誤りは見えない」——根拠を書かねば「不要」の結論だけが残った。★覆ったのは結論のみ・
   為し方（file+行番号を書く事）は是★。
2. F3の格＝「割れ」→「欠陥・是正要」へ変更（将軍second裁）。受入＝Web経路の409／実装＝L270-278で
   silent成功 ∴ 実装が受入未達。silent成功＝「音の無い側」の誤りゆえseverityも一段上。
3. ★但し実走は書込GO待ち★——本便は設計まで進め、適用（patch適用・pytest実行）は待つ。§2-§4の
   設計内容・§7の禁則遵守はこの位置付けを前提とする（変更なし）。

---

## §1 実測（当職が本工区で確認した事実・行番号つき）

### 1-1 断面

測時=2026-08-06T12:08:41+09:00。本repo（`multi-agent-shogun`）HEAD=
`5eaf27785a9f8d3c8ac794913dfc12df38afd93c`（branch `feat/dd169-d006-conditional-exception`）。
対象snapshot=`/tmp/resimg-cycle2-impl-20260806`。当該worktreeの `git rev-parse HEAD` =
`7d463edae84c704edabbd9da5465078dc62e55b1` — 本部長殿引用のbaseと★一致★（`git status --short` で
5件の作業中差分〈`booking.py`/`appointment_service.py`/`booking_service.py`/`test_phase2_2_booking.py`
の M4件＋root migration関連の未追跡2件〉も現存を確認）。
**検め直し方**: `cd /tmp/resimg-cycle2-impl-20260806 && git rev-parse HEAD && git status --short`。

### 1-2 Web経路の code path（本部長殿㈠の再確認）

`backend/services/web_reservation/booking_service.py`:

- L249-256: `if root_enabled and idempotency_key:` → `acquire_idempotency` → `state=="completed"` なら
  `return replay`（同一key durable replay 成功経路）。
- L258-278: key無し heuristic。`existing`（同clinic・同patient・同unit_id=1・同source='web'・
  status非cancelled/no_show・同start/end/content）を検索し、L270
  `if existing and not (root_enabled and idempotency_key):` が真なら L271-278 で既存予約を
  そのまま成功として `return`。
- L280: `_check_conflict(conn, clinic_id, start_dt, end_dt)` — clinic全体の時間帯重複を見て
  `BookingConflictError` を送出しうる（`_check_conflict` 本体はL179-190、SQLは
  patient不問・clinic単位の時間帯overlap判定）。
- `booking.py` L59-60: `except BookingConflictError as e: raise HTTPException(status_code=409, ...)`。
  ∴ Web経路で409が出るのは `_check_conflict` に到達した場合のみ。

**検め直し方**: `grep -n "" backend/services/web_reservation/booking_service.py | sed -n '245,300p'`
（本工区実測と同一出力になるはず）。

### 1-3 staff経路（本部長殿㈠・触るなの確認）

`backend/tests/test_appointment_api.py` L128-148 `test_04_double_booking`＝
`POST /api/appointments` を同一枠で2回叩き、1回目201・2回目409を assert。idempotency-key/heuristic
replayの語は一切登場せず、`appointment_service.create_appointment` 経由（本便の対象外）。
**検め直し方**: `grep -n "idempot\|Idempot" backend/tests/test_appointment_api.py`（0件のはず）。

### 1-4 RED根の精密化（本部長殿㈤・足軽5/6号実測の裏付け）

L270 `if existing and not (root_enabled and idempotency_key):` は、`idempotency_key is None` の時
（Web APIでヘッダ未送信時のデフォルト、`booking.py:56` 参照）、`root_enabled` の真偽に★関わらず★
`(root_enabled and idempotency_key)` は常に `False` ∴ `not (...)` は常に `True`。
∴ **key無しの2回目は、DB migration（`apply_booking_concurrency_root`）の有無に関係なく、常にL271-278の
silent成功に落ちる**——`_check_conflict`（L280）へは到達しない。これがRED根。
**検め直し方**: `python3 -c "print(not (False and None), not (True and None))"` → 両方 `True` になる
ことで論理を機械的に確認できる（実行はしていない・設計上の恒真式）。

---

## §2 設計（下命③㈠-㈤ 準拠）

### ㈠ 対象

`backend/services/web_reservation/booking_service.create_booking`（Web `create_booking` 経路）。
`test_04_double_booking`（staff共通POST）とは★別関数・別test file★——取り違え防止のため、新規testは
既存 `backend/tests/web_reservation/test_phase2_2_booking.py` に追加する設計とする（既存fixture
`db`/`file_db_path`/`_open_file_db` を再利用——Anti-Duplication）。

### ㈡ 契約（負契約・RED期待）

key無し（`idempotency_key` 省略）・同一payload（同clinic・同patient_no・同menu_id・同start_time・
同treatment_content）での2回目呼出しは、L270-278で silent成功せず、`BookingConflictError` を送出する
（HTTP層では `booking.py` 経由で409になる — サービス層testでは例外送出を直接assertする設計とする。
既存test群がサービス層直接呼出しで統一されているため、これに倣う——Anti-Duplication）。

### ㈢ 対照（同一key+同一payloadは409に非ず）

★これは新規実装が不要★——**この test（`test_durable_idempotency_key_and_slot_claims_after_migration`
L432-453）が覆うは「Web create_booking経路・同一idempotency-key・同一payload」の母集団のみ。
key無しケース（§2㈡の対象）は覆わず**（`apply_booking_concurrency_root(db)` 適用後、同一key2回目は
`retry == first` を assert・例外なし——但しkey自体を渡していない呼出しはこのtestの対象外）。
新規testを設計する際は★この既存testを重複実装しない★——参照するに留める。
（★書式=将軍second裁12:06・「既に在るゆえ作らぬ」は覆う経路・母集団を同じ行に書け、に準拠★）

### ㈣ staff test不触の確認

`test_04_double_booking`（`test_appointment_api.py` L128-148）は本設計で1文字も参照・変更しない。
§1-3の実測により、そもそも別test file・別関数であり取り違えの余地がないことを確認済み。

### ㈤ RED根の明記

§1-4に記載の通り。新規test docstringには「現状はL270-278の heuristicにより成功が返る
（silent replay）。本testはL280への到達＝409を要求する負契約であり、現状実装に対しては
RED（意図的）」と明記する設計とする。

---

## §3 ★重大な衝突★（既存testとの直接矛盾・裁定はしない）

足軽5号の先行調査（`docs/incident_logs/2026-08-06_f3_compatibility_requirement_search_a5.md`
§「新規test」・当職はこの発見を★再利用し重複実装しない★——Anti-Duplication）が既に指摘した通り、
`test_phase2_2_booking.py` L408-429 `test_exact_request_replay_returns_same_appointment_id` は——

```python
def test_exact_request_replay_returns_same_appointment_id(file_db_path):
    first = booking_service.create_booking(first_conn, 1, "000001", "menu_01_001", "2035-05-01 15:00")
    retry = booking_service.create_booking(retry_conn, 1, "000001", "menu_01_001", "2035-05-01 15:00")
    ...
    assert retry["appointment_id"] == first["appointment_id"]
    assert active_count == 1
```

★§2㈡で設計した新規negative testと★呼出しパターンが完全に同一★（同clinic・同patient・同menu・
同start_time・key無し2回）でありながら、期待結果が★正反対★（この既存testは成功+同一idを要求、
新規testは409を要求）。当職の実測では、この2つのtestを両方とも実装すると★どちらか一方が必ずFAILする★
（同一入力に対して排他的な期待を持つため）。

a5号の限定注記（この既存testはbase commitには存在せず、本Cycle2 patchが実装と★同一patch内★で
新規追加したもの——外部の先行契約ではなく自己整合testである）を当職も追認する。
**検め直し方**: `cd /tmp/resimg-cycle2-impl-20260806 && git show 2d3eeaa2^:backend/tests/web_reservation/test_phase2_2_booking.py 2>&1 | grep -c test_exact_request_replay`
（0件になるはずだが、当職はこのcommand自体は実走していない——a5号の既報を引用するに留める。
自ら検めるなら上記commandで可）。

★裁定はしない（下命の縛り）★——但し事実として記す: 本命令③㈡を実装する際、L408-429の既存testを
★変更せずに済ませる道はない★（同一シナリオで排他的なassertを両立できないため）。「設計のみ・
既存に触るな」の指示と「既存testと矛盾しないnew testを作れ」は、この一点において★両立しない★。
どちらを優先するか（既存testをsupersede/修正するか、新規testの条件をさらに絞り別シナリオに分けるか）は
家老second／軍師second／本部長殿の判断を要する——当職が勝手に決めない。

---

## §4 提案test（未適用・設計のみ・pytest未実行）

```python
def test_no_key_duplicate_request_returns_409_not_silent_success(db):
    """F3負契約: key無し・同一payloadの2回目はL270-278の silent成功に落ちず409。
    現状実装に対してはRED（意図的・§1-4のRED根参照）。
    ★L408-429 test_exact_request_replay_returns_same_appointment_id と排他的（§3参照）——
    両立させるには既存testの側の扱いが家老second/軍師second/本部長殿の裁定を要る。★
    """
    apply_booking_concurrency_root(db)
    first = booking_service.create_booking(
        db, 1, "000001", "menu_01_001", "2035-05-01 15:00",
    )
    with pytest.raises(BookingConflictError):
        booking_service.create_booking(
            db, 1, "000001", "menu_01_001", "2035-05-01 15:00",
        )
    active_count = db.execute(
        "SELECT COUNT(*) FROM appointments WHERE clinic_id=1 AND patient_id='01_000001' "
        "AND start_time='2035-05-01 15:00:00' AND status NOT IN ('cancelled','no_show')"
    ).fetchone()[0]
    assert active_count == 1  # 1回目のみ生存、2回目は例外で未insert
```

`apply_booking_concurrency_root(db)` は§2㈢の対照testと環境を揃えるための選択（§1-4の通り
root_enabledの真偽自体はこのRED根には影響しないため、plain `db` でも成立する設計——移植性を優先し
migration適用側を採った）。

---

## §5 各主張の検め直し方（本日の条・再掲まとめ）

1. base commit一致 → §1-1のcommand。
2. code path行番号 → §1-2/1-3のgrep/sed command。
3. RED根の恒真式 → §1-4のpython評価（未実行・設計上の恒真式であり実行不要で真偽が定まる）。
4. 既存test衝突 → §3のgit show command（当職は未実行、a5号既報の引用）。
5. 対照testの非重複 → `grep -n test_durable_idempotency_key_and_slot_claims_after_migration backend/tests/web_reservation/test_phase2_2_booking.py`。

---

## §6 母集団宣言・限界

- 読んだ範囲: `booking_service.py` 全152-333行（関数`create_booking`本体＋`_check_conflict`＋
  `BookingConflictError`定義）／`booking.py` 全1-90行／`test_phase2_2_booking.py` 全1-90行
  （fixture）＋338-525行（idempotency/replay系test群）／`test_appointment_api.py` L110-155
  （`test_04_double_booking`周辺）。
- 読んでいない範囲: `test_phase2_2_booking.py` 91-337行（空き枠・変更・キャンセル系test、本件に
  無関係と判断し省略）／`appointment_service.py`（staff側実装本体、本部長殿㈠の引用で経路確認済のため
  再読していない）／frontend側（a5号が既に`useWebBooking.ts`をgrep済・重複回避のため未読）。
- 未実行: pytest実走・DB migration適用・HTTPレイヤーのTestClient経由test（設計は
  サービス層直接呼出しに統一——理由§2㈡）。

## §7 禁則遵守の申告

実走せず（pytestコマンドを一度も呼んでいない）。`hakudokai-dev`・`newbuild`へは一字も書いていない。
`/tmp/resimg-cycle2-impl-20260806`への書込み・commit・patch適用も一切なし（読取のみ）。
`docs/incident_logs/`配下の既存file（旧F1設計v2 230行・旧版161行含む）は1文字も変更していない。
`rc`はpipeに通していない。`/usr/bin/grep`／`sed`／`git`（read系サブコマンドのみ）を明示使用した。

---

行数・sha256は自己参照の循環を避けるため本file内には埋め込まず、家老second／軍師secondへの提出便
（inbox本文）で別途報告する（測時＝提出直前の `wc -l`／`sha256sum` 実測値）。
