# F1 陽性対照 — 4点oracle 設計 改訂版（API層・実Idempotency-Keyヘッダー方式）— 足軽1号

下命=家老second msg_20260806_103840_238b0644（10:38:40・宛先=当職）。
出所=本部長殿裁定（10:35:10、家老second転記）+将軍secondの別軸見立て（同便⒟）。

★冒頭★= 本便は★設計のみ★。`hakudokai-dev`への書込み・patch適用・実走（pytest等）は一切行っていない。
本工区で実行したのは `git rev-parse HEAD` / `git status --short` / `/usr/bin/grep`（`Idempotency`検索）/
既存test fileの`Read`（読取のみ）に留まる。

**旧版との関係**: 旧版＝`2026-08-06_f1_4point_oracle_positive_control_design_a1.md`
（161行・sha256=`23d5af108ad6380e508d3023a079ab7e775839cbd0eeabb93d929fa3c069ccd7`）は
★消していない・書き換えていない★。本便は下命⒠の選択肢のうち「旧版に手を触れず、改訂版を別fileとする」
方を採った——旧版自体が「なぜ最初その設計に至ったか」の思考過程の記録として単独で価値を持つ
（W14で自ら訂正した前例と同じ扱い方）。本便が旧版§2・§3の設計を実質的に置き換える。

---

## §0 前提（本部長殿裁定の逐語・将軍second軸の逐語）

家老second便より（内容は前工区で当職が照合した本部長殿原文と将軍second独自見立てを含む）:

> 「F1 test は同一payloadを同一keyの代用にするな——API層へ実際のIdempotency-Key headerを2回渡せ」
> 「旧staff APIはheader/key未配線 ∴ 2回目409でRED。target＝200/201同等成功＋same appointment_id＋active=1＋extra=0」
> 「409をERROR放置するな——HTTPExceptionをcatchしpytest.fail(expected successful replay, got 409)とし明示FAILへ落とせ」
> 「catchしてGREENには絶対にするな」
> 「key無し同一payloadのtestは別の負契約として409をassertせよ」

F3暫定受入（本部長殿が別裁定されれば差替）＝「key無し重複は409／同一key＋同一payloadのみ同一成功結果へreplay」。

将軍secondの見立て（別軸・裁定に非ず）＝「catchの射程が広ければ409以外（500/422/接続断）も同じ文言で落ち、
読む者は『409が返った』と読む。実際は別の因——誤った説明は沈黙より悪い」∴「実際のstatus codeを文言に
埋めよ（expected successful replay, got {actual}）。409以外は別の文言か再送出とし因を混ぜぬ」。

---

## §1 旧版からの向き反転（何が覆り、何が覆らなかったか）

旧版＝「②retryの呼出しを例外を捕らえる分岐で一切包まぬ設計」。因＝当職自身が旧版§4留保2に書いた
「上位ゲートがFAILのみ拾いERRORを見逃す可能性」。この留保が設計そのものを覆した。

覆ったもの: 例外を握らない → 握って明示FAILへ落とす（②の書式）。同一payloadをkeyの代用にする →
実headerを2回渡す（設計対象の層）。

覆らなかったもの: ③④の active/extra オラクル（COUNT差分で書く手法自体）・逐次実行（並行は対象外）・
「409をGREENと数えない」という上位原則そのもの（書式が変わっただけで原則は不変）。

---

## §2 対象・前提の固定（本工区で実測・グラウンディング）

- 試験対象を★service層から API層★へ変更する。根拠＝本部長殿裁定「API層へ実headerを渡せ」。
  対象＝`backend/api/appointments.py` L85-98 `api_create_appointment`（route）。
  measured HEAD=`dfa3ac77341e5947c967c745cf8fa597ba494a2e`（`git rev-parse HEAD`実測、本工区）。
  `git status --short`で`backend/api/appointments.py`・`backend/services/appointment_service.py`・
  `backend/tests/test_appointment_api.py`のいずれも変更行に★出ておらぬ★事を確認済
  （dirty tree内の他fileは appointment_detail.py/appointment_form.py 等★別file★であり本設計の対象と重ならない）。

- ★「header未配線」の実測確認★＝`/usr/bin/grep -rn "Idempotency" --include=*.py backend/ --exclude-dir=.venv --exclude-dir=node_modules`
  の結果、`backend/api/appointments.py`・`backend/services/appointment_service.py`双方に★hit=0★。
  `CreateAppointmentRequest`（appointments.py L30-56）に`idempotency_key`相当のfieldは無い。
  `api_create_appointment(req: CreateAppointmentRequest)`（L86）に`Header(...)`依存も無い。
  ∴ 本部長殿裁定の前提「旧staff APIはheader/key未配線」は本工区の実測でも成立を確認した。

- fixture＝新規に作らず既存を再利用する（Anti-Duplication）。`backend/tests/test_appointment_api.py`
  L21-42の`test_db` fixture（`tmp_path`にsqlite作成→`TABLES`実行→`seed_appointment_data`→
  `monkeypatch`で`DB_PATH`差替→`TestClient(app)`を返す）をそのまま使う。

- ★重要な発見（Anti-Duplication適用）★＝ 同fileL127-147 `test_04_double_booking`が既に存在する。
  同一payload（header無し）で2回POSTし、1回目201・2回目409をassertしている——これは
  ★F3暫定受入「key無し重複は409」と完全に一致する契約を、既に別testが担保している★。
  ∴ 下命⒞「key無し同一payloadは別testに分けよ」に対し、★新規testを設計する必要は無い★。
  既存`test_04_double_booking`（L127-147）を負契約(c)の担保先として指し示すに留める。
  新規に重複testを設計すれば二重実装になる（CLAUDE.md Anti-Duplication違反）ゆえ、これは
  「作らない」事自体が本工区の成果物の一部である。

---

## §3 (a) 4点の示し方（API層・実headerで再設計）

`test_db` fixtureをそのまま使い、`client, db_path = test_db`で取り出す。

```python
def test_XX_idempotent_replay_with_key(self, test_db):
    """Idempotency-Keyヘッダーを2回渡した同一payload replay → 同一appointment_idで成功（F1 4点oracle）。
    ★現行baseはheaderを読まぬ(未配線)ため、この設計は現行HEADに対してRED想定の陽性対照★
    """
    client, db_path = test_db
    unit_id = _get_unit_id(db_path)  # 既存helper（同file L69-77）を再利用
    payload = {
        "clinic_id": 1,
        "unit_id": unit_id,
        "start_time": _future(240),  # 既存helper（同file L45-62）を再利用。他testと枠が衝突せぬよう空きoffsetを使う
        "duration_minutes": 30,
        "category": "Dr",
        "source": "staff",
    }
    idem_key = "f1-positive-control-fixed-key-001"  # ★payloadとは独立の概念として固定値を使う★

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    def _active_count():
        row = conn.execute(
            "SELECT COUNT(*) c FROM appointments WHERE clinic_id=? AND unit_id=? AND start_time=? "
            "AND status NOT IN ('cancelled','no_show')",
            (payload["clinic_id"], payload["unit_id"], payload["start_time"]),
        ).fetchone()
        return row["c"]

    # ①first=success
    resp1 = client.post("/api/appointments", json=payload, headers={"Idempotency-Key": idem_key})
    assert resp1.status_code in (200, 201)
    first_id = resp1.json()["appointment_id"]
    count_before = _active_count()
    assert count_before == 1

    # ②retry=same success/same ID（§4で書式の理由を述べる）
    resp2 = client.post("/api/appointments", json=payload, headers={"Idempotency-Key": idem_key})
    if resp2.status_code not in (200, 201):
        pytest.fail(f"expected successful replay, got {resp2.status_code}")
    assert resp2.json()["appointment_id"] == first_id

    # ③active=1
    count_after = _active_count()
    assert count_after == 1

    # ④extra=0（絶対値でなく差分——既存データ混在環境でも成立させる為の一般化。旧版§2と同じ考え方を維持）
    assert count_after - count_before == 0
```

payloadと`idem_key`を分離した理由＝下命⒜「同一payloadをkeyの代用にせぬ形」に応じる為。target契約
（F3暫定受入）は「同一key＋同一payloadのみreplay」であり、本testは両方を同一に保つ事で「replayが
成立すべき唯一のケース」を示す。key有り/payload違い・key違い/payload同一の組合せは本4点oracleの
scope外とし、§6の留保に回す（旧版が並行testを明示的にscope外へ切り分けたのと同じ扱い）。

---

## §4 (b)「catch→pytest.fail」の書式化——★TestClient境界での翻訳を明記する★

下命原文は「HTTPExceptionをcatchしpytest.fail」だが、これを字義通りAPI層test（TestClient経由）へ
当てはめると★成立しない前提がある★事を、以下に実測を根拠として明記する。

- `appointments.py` L93-98実測: routeは`create_appointment`が投げる`HTTPException`を
  `except HTTPException: raise`で★そのまま再送出★している。だが送出先は素の呼出し元ではなく
  ★FastAPI/Starletteの例外処理middleware★である。`TestClient`はASGI経由でrouteを呼ぶ為、
  route内で送出された`HTTPException`はmiddlewareが捕捉し、通常のHTTP応答（`status_code=409`の
  `Response`）へ変換されてから test コードへ戻る。★testコード側に生のPython例外としては
  到達しない★（`TestClient(raise_server_exceptions=True)`が既定でも、これは"handlerが処理し損ねた
  例外"の場合の挙動であり、`HTTPException`はFastAPIの標準handlerが処理する対象なので該当しない）。
- ∴ testコードで`try: ... except HTTPException:`と書いても★何も捕まらない★（そもそも例外が
  飛んで来ない）。これは旧版がservice層を直接呼んでいた（`create_appointment(**payload)`を
  素のPython関数として直接call）ケースとの決定的な違いであり、下命⒜（API層へ変更せよ）を
  真に実行するなら、この違いを黙って踏み越えず明記するのが誠実と判断した。
- ★本設計の翻訳★＝ 「catchする」の意図（409を握り潰してGREEN化するのではなく、明示的にFAILへ
  落とす事）を、TestClientの実際の挙動に即して「`response.status_code`を直接検分し、期待値で
  なければ`pytest.fail(f"expected successful replay, got {resp2.status_code}")`を呼ぶ」という形に
  置き換える（§3の②のコード）。★これは字面上の"except節"こそ持たぬが、下命の禁則
  「catchしてGREEN化するな」「409をERROR放置するな」の両方を字義以上に満たす★——
  なぜなら`assert`一発（例：`assert resp2.status_code in (200, 201)`）でも同じくFAILにはなるが、
  pytestのassertion rewritingに依存せず★明示テキストで理由を書く★方が下命の趣旨（"expected
  successful replay, got {actual}"という文言そのもの）に忠実である。

★留保★= もしroute内で`HTTPException`にも`sqlite3.IntegrityError`にも該当しない未知の例外
（例＝実装バグ）が発生した場合、それは`appointments.py`のcatch節（L93-96）を通過せず、
`TestClient`のASGI層まで伝播し★生のPython例外として test 側に届く★（`raise_server_exceptions`
既定=True の対象）。この場合はpytestの ERROR になる——但しこれは★idempotency契約とは無関係の
別バグ★であり、本4点oracleのscope外として区別すべきものである（旧版§4留保2が案じた「上位ゲートが
FAILのみ拾いERRORを見逃す」問題は、★本testが対象とする409応答の経路については、この改訂により
実質的に解消される★——409はHTTPExceptionとして正規のhandler処理を経て通常のResponseになる為、
ERRORにはなり得ない。ERRORが起き得るのは無関係の別バグの場合のみであり、それは"見逃してはならぬ
別種の異常"として妥当にERROR表示されるべきものである、と当職は判断する）。

---

## §5 (c) 負契約（key無し）——★既存test_04_double_bookingへの委譲★

下命⒞は「key無し同一payloadは別の負契約として409をassert（別testに分けよ）」。§2で述べた通り、
`backend/tests/test_appointment_api.py` L127-147 `test_04_double_booking`が★既にこの契約を
担保している★（header無し・同一payload2回POST・1回目201/2回目409をassert）。

∴ 本工区での設計判断＝★新規testを追加しない★。理由＝
1. 既存testが対象契約（key無し重複＝409）を既にscopeしており、新規追加は二重実装になる。
2. 下命⒞の「別testに分けよ」の意図は「①key有りreplay成功系と②key無し重複失敗系を同一test関数に
   混ぜるな」という分離の指示と解する。既に別々のtest関数（§3の新規test と 既存test_04）に
   分かれている為、この意図は満たされている。

★申告★= 当職はこの既存testの中身（L127-147）を本工区で`Read`し実際に確認した上でこの判断を
下している（「たぶんある」という推測ではない）。

---

## §6 (d) 将軍second軸——status code埋め込みで因を混ぜぬ

§3・②の`pytest.fail(f"expected successful replay, got {resp2.status_code}")`は、`{resp2.status_code}`が
★実際に返ってきた値★を埋め込む形になっている。これにより:

- 現行base（header未配線）で本testを実行すれば、2回目は`_check_double_booking`または
  `UNIQUE`制約により`HTTPException(409)`→"expected successful replay, got 409"と表示される
  （下命の想定通り）。
- もし将来別の実装変更で500や422が返るようになれば、"expected successful replay, got 500"の
  ように★実際の値がそのまま出る★——409固定の文言に因を歪めて押し込む事はない。
- ∴ 将軍secondの懸念（"catchの射程が広ければ409以外も同じ文言で落ち、読む者が誤読する"）は、
  ★{actual}を埋め込む一つの文言テンプレートで自然に解消される★——本部長殿の指図（"catchして
  GREEN化するな"）と将軍secondの指摘（"FAILの文言で因を偽るな"）は、当職の実装では★対立せず
  同じ1行で両立する★。追加の分岐（409用と500用で文言を分ける等）は不要と判断した
  （下命⒟に「これは本部長殿の御指図に反しない」と明記されている通り）。

---

## §7 母集団宣言・禁則遵守申告

- 本工区で新たに`Read`したfile＝ `backend/api/appointments.py`（全体, 218行未満の範囲を実読）・
  `backend/services/appointment_service.py`（L122-152、create_appointment冒頭部）・
  `backend/tests/test_appointment_api.py`（L1-206、fixture＋テスト1-8相当まで）。
  旧版の実測（`appointment_tables.py` L111 UNIQUE制約・`booking_validator.py` L355-380
  `_check_double_booking`）は前々工区の結果を引用するに留め、本工区で再実行していない。
- 本工区で新たに実行したコマンド＝ `git rev-parse HEAD`・`git status --short`（両方
  `/mnt/c/Projects/hakudokai-dev`にて、read-only）・`/usr/bin/grep -rn "Idempotency"`（同上）・
  `find`（repo所在確認）。★書込み系コマンドは一切実行していない★。
- 禁則遵守: `hakudokai-dev`への書込み・patch適用・実走（pytest等）、いずれも行っていない。
  `newbuild`へは一字も書いていない。rcをpipeに通していない。commitは行わない（karo-second殿がPASS後）。
- ★未測（正直に書く）★＝ 本設計の②③④コードは★実行して確かめていない★（設計のみ）。特に
  `_get_unit_id`/`_future`ヘルパーとの組合せで`start_time`の時間帯衝突が本当に起きないかは、
  紙上の確認（既存test群が同ヘルパーで多数のtestを問題なく回している事の観察）に留まり、
  実行検証はしていない。

断面: 2026-08-06T10:45:19+0900（`date`実測）／`multi-agent-shogun`側 base_commit=`89685bf202cedef63f30638010116f817ab9ea5d`
（前工区から不変）／`hakudokai-dev`側 measured HEAD=`dfa3ac77341e5947c967c745cf8fa597ba494a2e`
（`git rev-parse HEAD`実測・本工区新規測定・working treeはdirtyだが対象3fileは無変更行を確認済）。
提出先: 家老second + 軍師second。
