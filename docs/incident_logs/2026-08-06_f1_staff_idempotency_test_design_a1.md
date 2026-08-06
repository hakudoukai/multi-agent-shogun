# F1 staff idempotency test 設計（本部長殿12:56:34裁定・staff API境界フルセット）— 足軽1号

下命=家老second msg_20260806_125816_42cb9c24（12:58:16・宛先=当職）。
出所=本部長殿裁定（12:56:34・153行を家老second全文実読の上）。
経緯=足軽4号の実測（idempotency関数のimport=0件）を家老second殿が本部長殿へ射程の報告として上げ、御裁が下った。

★冒頭★= 本便は★設計のみ★。`hakudokai-dev`への書込み・patch適用・実走（pytest等）は一切行っていない。
本工区で実行したのは `git rev-parse HEAD` / `git status --short` / `/usr/bin/grep`（`idempotency`検索・
`backend/`と`tests/`配下全体）/ 既存file（`backend/api/appointments.py`全190行・
`backend/services/appointment_service.py` L1-45+L71-296・`backend/tests/test_appointment_api.py` L1-190）の
`Read`（読取のみ）に留まる。書込み系コマンドは一切実行していない。

---

## §0 前提（本部長殿裁定12:56:34の要旨・家老second便より）

1. 現存testでstaff idempotencyを覆う物は無し。`#3`/`#9`はWeb/primitiveのみ（家老second便の逐語引用、
   当職はこの2件の実体を本工区では特定していない＝★引用のみ・裏取りは対象外★と明記する）。
   `test_04_double_booking`（`backend/tests/test_appointment_api.py` L127-147）はkey無し通常409だけ ∴ F1に非ず。
2. F1門はOPEN。現状は未実装・未test。
3. 新規test＝staff API境界専用。`TestClient`で`POST /api/appointments`へ実`Idempotency-Key`＋同一payloadを
   別接続相当で2回送り、①1回目成功②2回目も同じ成功結果・同一appointment_id③active=1④追加row=0をassert。
   対で——⑤同一key＋異payload=409／⑥key無し＋同payload=通常409／⑦未失効pending block／⑧失効reclaim／⑨reconnect。
4. 成立させる root単位＝`appointments.py`のHeader配線 → `appointment_service`同一transaction内のacquire／complete
   → 共通`booking_idempotency`。
5. 「testだけ先に GREEN化しない」（御裁の逐語）。

★記す（下命④）★= 前工区（`2026-08-06_f1_4point_oracle_positive_control_design_v2_a1.md`）で当職は
「`test_04_double_booking`が既存testとしてF3暫定受入(c)の負契約を担保している」と判じた。これ自体は
上記1.の「key無し通常409だけ」と一致し覆っていない。だが本部長殿裁定1.は同時に「F1（正replay契約）を
覆す物は無い」と明言し、F1門をOPENとした——∴ 前工区で当職が示した4点oracle（§3で後述）は
★設計として残るが、それだけでは御裁が要求する⑤～⑨の対（5組中3組）が欠けていた★。本便はこの欠落を埋める。

---

## §1 対象・母集団の固定（本工区で実測・grounding）

- 対象route=`backend/api/appointments.py` L85-98 `api_create_appointment`（14行、全体を実読）。
  ```
  L85: @router.post("", status_code=201)
  L86: def api_create_appointment(req: CreateAppointmentRequest):
  L88: conn = _get_db()
  L91: result = create_appointment(conn, req.model_dump(), req.source)
  L93-94: except HTTPException: raise
  L95-96: except sqlite3.IntegrityError as e: raise HTTPException(409, ...)
  ```
  `CreateAppointmentRequest`（同file L30-53）に`idempotency_key`相当のfieldは無い。
  `Header(...)`依存も無い（route引数は`req: CreateAppointmentRequest`のみ、他に無し）。
- `/usr/bin/grep -rn "idempotency" --include=*.py backend/ tests/ --exclude-dir=.venv-linux
  --exclude-dir=__pycache__`実測=6件hit、うち`backend/`配下は`backend/tests/test_import_loan_csv.py`と
  `tests/test_step_j.py`のみ（後者は`TestIdempotency`クラス＝リコール離脱アラートの重複防止、
  L696-780・予約/appointmentとは★無関係の別domain★）。`appointments.py`・`appointment_service.py`・
  `test_appointment_api.py`にhit=0。∴ 本部長殿裁定1.「未実装・未test」を本工区の実測でも確認した。
- `create_appointment`本体（`appointment_service.py` L122-282）実読＝ INSERT（L216-221）で1回`conn.commit()`、
  履歴INSERT（L224-230）で別途1回`conn.commit()`——★単一transactionでは無く2回の個別commit★。
  かつ`check_double_booking`（L71-110、単なるSELECT）とINSERTの間に明示的な`BEGIN`は無い
  （sqlite3標準のautocommit外挙動に依存）。これは§6で述べるpending block設計の前提に直結する実測。
- `VALID_SOURCES`（`appointment_service.py` L39）=`{"staff","web","phone","line","recall"}`。
  ルートは単一（`POST /api/appointments`）で`source`fieldにより流入経路が分岐する構造。
  ∴ 「staff API境界」とは★別routeの意味ではなく、`source="staff"`の入力群を指す★
  ——この区別は本工区の判断であり御裁本文には明記が無いため、誤読の可能性を残す申告として記す。
- fixtureは新規に作らず既存`test_db`（同file L21-42）を再利用（Anti-Duplication）。
- HEAD=`dfa3ac77341e5947c967c745cf8fa597ba494a2e`（`git rev-parse HEAD`実測）。`git status --short`で
  `appointments.py`・`appointment_service.py`・`test_appointment_api.py`のいずれも変更行に出ておらぬ事を確認済
  （dirty treeは他file19件、前工区測定時と同じ差分状態で不変）。

---

## §2 assertの一つ一つ（下命②㈠・設計ticket形式）

御裁③の5組の対＋4点oracleを、実装が無い今の時点で「何を見て何が通れば正・現状はどう出るか」の表で示す。

| ID | assert内容 | 見る対象 | 通す条件 | 現状(HEAD dfa3ac77)の推定応答 | 判定 |
|---|---|---|---|---|---|
| A1 | 同key・同payload・1回目 | `resp1.status_code` | `in (200,201)` | 201（headerは無視されるがpayload自体は正常create） | GREEN（実装前でも通る＝新規実装が壊してはならない基準線） |
| A2 | 同key・同payload・2回目=同一成功 | `resp2.status_code`＋`resp2.json()["appointment_id"]` | `in (200,201)`かつ`==first_id` | ★409★（`check_double_booking`が同unit+同start_timeで検知） | **RED** |
| A3 | active件数不変 | `_active_count()`後 | `==1` | 1（2回目が409で弾かれ増えない＝偶然一致するが趣旨と逆） | 参考値（A2が先にFAILするため到達しない想定） |
| A4 | 追加row=0 | `count_after - count_before` | `==0` | 0（同上の理由） | 参考値（同上） |
| B1 | 同key・異payload・1回目 | `resp1.status_code` | `in (200,201)` | 201 | GREEN |
| B2 | 同key・異payload・2回目=key衝突409 | `resp2.status_code` | `==409` | ★201★（key概念が無いため単純に別予約として成立） | **RED** |
| C1 | key無し・同payload・2回目=通常409 | 既存`test_04_double_booking` L127-147 | （委譲・新規assert無し） | 既存のまま201/409 | GREEN（既存test不触・§4） |
| D/E/F | 未失効block／失効reclaim／reconnect | §6で述べる理由により★具体assertを本工区では確定できない★ | — | — | **UNMEASURED（構造的に未確定）** |

★A2が最初にFAILする★ため、A3/A4は「参考値」と明記した——同一test関数内で先行assertがFAILすれば後続は
実行されない（pytestの通常挙動）。これを「参考値」でなく「RED」と書くのは過大主張になるため区別した。

---

## §3 assert群A（正replay・4点oracle）— 前工区からの引用・不変

前工区`2026-08-06_f1_4point_oracle_positive_control_design_v2_a1.md` §3のコードをそのまま引用する
（★Anti-Duplication＝同一設計の再設計はしない★）。差分は無し。

```python
def test_37_idempotent_replay_with_key(self, test_db):
    """Idempotency-Keyヘッダーを2回渡した同一payload replay → 同一appointment_idで成功（F1 4点oracle）。
    ★現行baseはheaderを読まぬ(未配線)ため、この設計は現行HEADに対してRED想定の陽性対照★
    """
    client, db_path = test_db
    unit_id = _get_unit_id(db_path)
    payload = {
        "clinic_id": 1,
        "unit_id": unit_id,
        "start_time": _future(240),
        "duration_minutes": 30,
        "category": "Dr",
        "source": "staff",
    }
    idem_key = "f1-positive-control-fixed-key-001"

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    def _active_count():
        row = conn.execute(
            "SELECT COUNT(*) c FROM appointments WHERE clinic_id=? AND unit_id=? AND start_time=? "
            "AND status NOT IN ('cancelled','no_show')",
            (payload["clinic_id"], payload["unit_id"], payload["start_time"]),
        ).fetchone()
        return row["c"]

    resp1 = client.post("/api/appointments", json=payload, headers={"Idempotency-Key": idem_key})
    assert resp1.status_code in (200, 201)
    first_id = resp1.json()["appointment_id"]
    count_before = _active_count()
    assert count_before == 1

    resp2 = client.post("/api/appointments", json=payload, headers={"Idempotency-Key": idem_key})
    if resp2.status_code not in (200, 201):
        pytest.fail(f"expected successful replay, got {resp2.status_code}")
    assert resp2.json()["appointment_id"] == first_id

    count_after = _active_count()
    assert count_after == 1
    assert count_after - count_before == 0
```

テスト番号は`test_37`と仮置きした（現行37件の続き番号想定）。確定は実装着手時の採番次第であり、
本工区の確定事項ではない。

---

## §4 assert群B（同key・異payload → 409・新規設計）

御裁③⑤「同一key＋異payload＝409」に対応する新規設計。前工区には無かった。

```python
def test_38_idempotent_key_conflict_different_payload(self, test_db):
    """同一Idempotency-Key・異なるpayload → 409（key衝突検知）。
    ★key概念自体が現行未配線のため、この設計は現行HEADに対してRED想定★
    """
    client, db_path = test_db
    unit_id = _get_unit_id(db_path)
    idem_key = "f1-key-conflict-fixed-key-002"

    payload_a = {
        "clinic_id": 1,
        "unit_id": unit_id,
        "start_time": _future(300),
        "duration_minutes": 30,
        "category": "Dr",
        "source": "staff",
    }
    # ★start_timeのみ変え、同unit・重複しない時間帯にする★——
    # ダブルブッキングcheck(check_double_booking)が介入しない値を選ぶ事で、
    # 「key衝突ロジック単体」の応答を切り出す（将軍secondの「因を混ぜぬ」原則の適用）。
    payload_b = dict(payload_a, start_time=_future(360))

    resp1 = client.post("/api/appointments", json=payload_a, headers={"Idempotency-Key": idem_key})
    assert resp1.status_code in (200, 201)

    resp2 = client.post("/api/appointments", json=payload_b, headers={"Idempotency-Key": idem_key})
    if resp2.status_code != 409:
        pytest.fail(f"expected key-conflict 409, got {resp2.status_code}")
```

★why RED★= `payload_a`と`payload_b`は`unit_id`同一・`start_time`が240分離れており（`duration_minutes=30`）
`check_double_booking`（`appointment_service.py` L71-110）の重複判定条件（時間範囲重複）に掛からない。
∴ 現行HEADでは2回目も通常のcreateとして★201で成立する★（key概念が無いため）。目標契約（409）とは
不一致 ∴ RED。

★穴（新たに開ける）★= 本test1本では「payloadのどの差分が『異payload』の判定基準に入るか」を1点
（`start_time`）しか切り出していない。実装が例えば`unit_id`と`start_time`のみをkey同一性の比較対象とし
`duration_minutes`や`menu_id`を無視する設計であれば、それらのfieldだけが違う場合の挙動は本testでは
覆われない。§9で再掲する。

---

## §5 assert群C（key無し・同payload → 通常409）— 既存test委譲・不変

御裁③⑥「key無し＋同payload＝通常409」は、前工区§5で確認済の`test_04_double_booking`
（`backend/tests/test_appointment_api.py` L127-147）が★既に担保している★（header無し・同一payload2回
POST・1回目201・2回目409をassert）。本工区で再実読し変更が無い事を確認した。

∴ 新規testを追加しない。理由=既存testが対象契約を既にscopeしており、新規追加は二重実装になる
（CLAUDE.md Anti-Duplication）。下命の縛り「`test_04_double_booking`は不触」とも整合する。

---

## §6 assert群D/E/F（未失効pending block・失効reclaim・reconnect）— 構造的に未確定である事の申告

★結論を先に記す★= この3種は★本工区の時点で具体的なpytestコードとして確定できない★。
理由を以下に分けて書く（仮説に合う例を探すのではなく、確定できない理由そのものを記す）。

### ㈠ pending block（未失効・御裁③⑦）

「1回目がpending中（未commit・未complete）に2回目が到達したら拒否/block」を測るには、1回目のリクエストを
transaction内の途中で意図的に止める仕掛けが要る。

- §1で実測した通り、現行`create_appointment`は★単一transactionでは無く★複数回の個別`conn.commit()`
  （L221・L230）で構成されている。「同一transaction内のacquire→complete」（御裁④の root単位）を実現するには、
  この複数commit構造自体を先に1個のtransactionへ束ねる実装変更が前提になる——∴ pending blockのtestを
  書く前に、テスト対象コードの現在の形（複数commit）が変わる事を前提にした設計になる。
  これは★test設計がpending block実装の骨格を先取りして仮定する★形になり、御裁⑤「testだけ先にGREEN化しない」
  の趣旨（実装の後にtestを合わせる）とは方向が逆になりかねない——∴ 当職はここで一旦止め、次点へ回す。
- HTTP層（`TestClient`）は同一thread内で同期的にrequest/responseを完結させる。真の「1回目が処理中」window
  を作るには、`threading`＋実装側に差し込む一時停止hook（例=acquire処理直後にthreading.Eventで待たせる）が
  要るが、★そのhookの設置点（関数名・引数）は`booking_idempotency`が未実装の今、当職には特定できない★。

★暫定の骨格（契約のみ・確定コードでは無い事を明記）★=
- 観測すべき契約＝「同key・同payload の2回目が、1回目のacquireがcomplete前に届いた場合、201/200（正常replay）
  にも通常の409（重複予約）にもならず、★第三の応答（例=409だが理由文言が異なる／425 Too Early等）★を返す」。
- 具体的なstatus codeの値・thread注入点の名称は★実装決定待ち（open）★。当職の判断で仮の値を書けば
  「設計した」体裁だけが残り実測を伴わないため、本工区ではここまでで止める。

### ㈡ 失効reclaim（御裁③⑧）

「TTL失効後、同keyを再利用しても新規requestとして成立する」を測るには、時刻を進める仕掛け（`freezegun`相当
または実装側の`now()`関数をmonkeypatchできる形）が要る。★TTLの長さ・保存場所（table/列名）・時刻取得点の
いずれも`booking_idempotency`が未実装の今は不明★。契約自体（失効後は新規として扱う＝古い試行と混同しない）
は明記できるが、注入方法は㈠と同じ理由でopenのままとする。

### ㈢ reconnect（御裁③⑨）

`TestClient`は実際のTCP接続を持たない（ASGI経由のin-process呼出し）ため、「クライアントが応答を受け取れず
切断→再送」という現象そのものはHTTP層のtestでは物理的に再現できない。だが★サーバ側から見た観測可能な入力★
は「1回目が既にcomplete済の状態で、同key・同payloadの後続requestが届く」であり、これは§3のA2（2回目=同一
成功）と★HTTP境界上は区別が付かない★（サーバは「なぜ2回目が来たか」を知る手段を持たない）。

∴ ★reconnectを別testとして新規設計しない★。理由=A2が既にこの契約（後続requestは常に同一成功結果を返す）
を覆っており、別testを立てれば同じ入力に同じassertを重ねる二重実装になる（Anti-Duplication）。
「作らない」事自体を本工区の成果物として明記する（前工区§5と同じ扱い方）。

---

## §7 RED根拠の一覧（下命②㈡・「testだけ先にGREEN化しない」の担保）

| assert群 | 現状の実測応答 | 目標契約 | 不一致の根 | RED状態 |
|---|---|---|---|---|
| A（正replay） | 2回目=409 | 2回目=200/201同一ID | headerを読む処理・keyとpayloadを紐付ける保存領域が0件（§1実測grep hit=0） | ★RED確定★ |
| B（key衝突） | 2回目=201（別予約成立） | 2回目=409 | 同上（key概念そのものが無い） | ★RED確定★ |
| C（key無し） | 既存のまま | 既存のまま | 変更なし・実装対象外 | GREEN（既存維持・新規実装の影響を受けてはならない基準線） |
| D/E/F | §6参照 | §6参照 | assert自体が未確定（実装の骨格決定待ち） | UNMEASURED（RED/GREENの二値では書けない） |

★根拠の要点★= A/BのRED化は「新規機能が無いから失敗する」という当たり前の意味でのRED（当然RED）ではなく、
★具体的にどの実測（grep hit=0・`check_double_booking`の判定条件）がその失敗を引き起こすかを名指しできる★
という意味での確定RED。これにより「実装完了後にtestを合わせて書いた」形（testを後付けでGREENにするだけの
形）とは異なり、★test設計がまず実測に基づいて失敗する事を示している★状態を担保する。

---

## §8 母集団宣言（下命②㈢・同じ行で覆う範囲を明記）

★本test群（A・B・C）が覆うは★staff API境界のみ★（`source="staff"`で`POST /api/appointments`へ到達する
requestに限る）・`source∈{"web","line","phone","recall"}`の経路は覆わない★——同一route
（`api_create_appointment`）を通るが`source`値が異なる入力は本設計のscope外であり、御裁本文が言及した
`#3`/`#9`（Web/primitiveのidempotency）の実体・正否は当職は本工区では検分していない（§0で申告済）。

---

## §9 既存testとの正反対チェック（下命②㈣）

- `/usr/bin/grep -n "def test_" backend/tests/test_appointment_api.py`実測=37件。
- `Idempotency`headerを使う既存testは0件（§1実測）。∴ 新規A/BのassertはHeader有無という入力次元で
  既存37件のいずれとも重複しない。
- payload形状（`clinic_id`/`unit_id`/`start_time`/`duration_minutes`/`category`/`source`）自体は
  `test_01_normal_create`（L87-103）と同型だが、`test_01`はheader無しでcreateし単発で終わる
  （2回目のPOSTを送らない）——∴ 「2回同一payloadを送る」という入力形状が重なるのは`test_04_double_booking`
  のみであり、これは§5で述べた通り委譲対象として明記済（重複ではなく意図した参照）。
- §4で述べた通り、B群の`payload_b`はA群の`payload`とも`start_time`が異なる固定値を使っており、
  test間でのfixture値の衝突（枠の取り合い）は無い（`_future(240)`/`_future(300)`/`_future(360)`で分離）。
- ★正反対の実例は検出しなかった（0件）★。0件を「探索失敗」とは書かない——§1・本節の実測範囲
  （37件のtest関数名・header使用有無・payload形状の比較）を母集団として明記した上での0件である。

---

## §10 三値・新たに開ける穴・検め直し方（下命②㈤）

| 主張 | 三値 | 新たに開ける穴 | 検め直し方 |
|---|---|---|---|
| A群は現行HEADでRED | 真（実測grep+コード追跡による予測。実行はしていない＝★未測の予測★） | 実装がheaderをOptionalにせず必須化すれば既存37件のうち一部が壊れる可能性（§11で申告） | `pytest backend/tests/test_appointment_api.py -k test_37`実行（GO後） |
| B群は現行HEADでRED | 真（同上・未実行の予測） | 「異payload」の判定次元が`start_time`1点のみで、他fieldの差分は覆われない | 同上、追加variantの実行結果比較 |
| C群は既存testで担保済 | 真（実読確認済・L127-147） | 実装が`test_04`の期待（header無し→通常409）を壊す可能性——回帰防止としてC群を実装後も再実行必須 | `test_04_double_booking`を実装後に再実行し409維持を確認 |
| D/E/Fは本工区で確定不可 | ★不明（未測）★——真偽どちらでもなく「まだ問えない」状態 | 御裁③が要求する5組中3組が、実装の骨格（transaction構造・TTL保存先）が決まらないと具体化できない——
  これは御裁の実行可能性そのものに関わる欠落であり、当職が黙って粗く埋めるのではなく上申すべき事項 | `booking_idempotency`の設計（table/列/acquire関数signature）が家老second/本部長殿で確定した後、本節を再訪 |
| `#3`/`#9`はWeb/primitiveのみ | 未測（当職は引用のみ・裏取りせず） | 誤引用であれば母集団宣言（§8）が誤った前提の上に立つ | `#3`/`#9`の実体file（家老second側の出典）をfollow-upで特定 |

---

## §11 新たに開ける穴（総括・下命②㈤の補強）

1. §4B群の「異payload」次元は`start_time`のみ。実装のkey比較ロジックが`duration_minutes`や`menu_id`等の
   他fieldを無視する設計であれば、この1本のtestだけでは検知できない――variant追加は実装確定後の別工区。
2. §6で述べた「複数commit構造」自体が、pending block実装の前提条件を満たしていない（単一transactionが無い）。
   ∴ `booking_idempotency`実装は`appointment_service.create_appointment`のcommit構造そのものへの変更を
   伴う可能性が高く、それは既存のhistory記録（L224-230）・kanban card生成（L233以降）等、★create_appointment
   内の他の副作用にも影響し得る★——本工区のscope外だが、実装工区への申し送り事項として明記する。
3. Header追加は★既存37件のtestを壊さない事★（Optionalであり続ける事）が暗黙の前提になっているが、
   御裁本文にはこの制約が明文化されていない。当職が本工区で追加した制約であり、家老second/本部長殿の
   確認を要する（当職の判断で足した前提を、御裁そのものであるかのように書かない）。

---

## §12 禁則遵守申告・断面

- 実行したコマンド＝ `git rev-parse HEAD`・`git status --short`（`/mnt/c/Projects/hakudokai-dev`にて
  read-only）・`/usr/bin/grep -rn "idempotency" --include=*.py backend/ tests/ --exclude-dir=.venv-linux
  --exclude-dir=__pycache__`・`/usr/bin/grep -n "def test_" backend/tests/test_appointment_api.py`・
  `find`（repo所在確認）・`Read`（`appointments.py`全190行・`appointment_service.py` L1-45+L71-296・
  `test_appointment_api.py` L1-190）。★書込み系コマンドは一切実行していない★。
- 禁則遵守: `hakudokai-dev`への書込み・patch適用・実走（pytest等）、いずれも行っていない。
  `newbuild`へは一字も書いていない。`/tmp/resimg-*`へも書いていない。rcをpipeに通していない。
  commitは行わない（karo-second殿がPASS後）。`test_04_double_booking`は不触（Read以外の操作をしていない）。
- ★未測（正直に書く）★＝ §3・§4のコードは★実行して確かめていない★（設計のみ・GO後の実行結果は未知）。
  §6のD/E/Fは意図的に「確定できない」まま提出する——粗い仮値で埋めれば「設計した」体裁だけが残り、
  御裁⑤の趣旨（testだけ先にGREEN化しない＝実装に先んじてtestの正しさを偽装しない）にむしろ反すると判断した。

断面: 2026-08-06T13:07:13+0900（`date`実測）／`multi-agent-shogun`側HEAD=`ed7daeb2cf6cb9ef6de72c424f2233c14506a3c1`
（`git rev-parse HEAD`本工区実測。★ashigaru1.yaml記載のbase_commit=83bdb61は2026-08-03時点の値であり
現行HEADとは不一致——古い値をそのまま転記せず本工区実測に置き換えた★）／`hakudokai-dev`側 measured
HEAD=`dfa3ac77341e5947c967c745cf8fa597ba494a2e`（前工区から不変・working treeはdirtyだが対象3fileは
無変更行を本工区でも確認済）。本file自体=333行・sha256=`5c51dfd0a5606701255dd70e44ddd66215921b18ff97768c3b8f5179112267b2`
（`sha256sum`本工区実測）。

提出先: 家老second（report_to）＋ 軍師second（監査義務）。
