# F1 陽性対照 — 4点oracleに沿った test 設計（設計のみ・未実行）— 足軽1号

下命=家老second msg_20260806_102448_f4044718（10:24:48・宛先=当職）。
出所=本部長殿裁定便 msg_20260806_102049_e6c63cd2（10:20:49・将軍second経由で当職が受領。原文は
queue/inbox/karo-second.yaml L140-208 に将軍second転記あり、当職が該当箇所を直接照合済み）。

★冒頭★= 本便は★設計のみ★。`hakudokai-dev`への書込み・patch適用・実走（pytest等）は一切行っていない。
本工区で新たにgit show/grep等を実行してもいない（前回工区=`2026-08-06_f1_split_thirdread_verification_a1.md`、
sha256=`4685cfb6be213320b2abd82e3275206fd593590d4938d508b3cabd478164f2cb`、171行の実測結果を引用するに留める）。

---

## §0 前提（本部長殿裁定の逐語・当職が照合した原文）

queue/inbox/karo-second.yaml L162-174（将軍second→家老second、10:20:12付、本部長殿裁定の転記）:

> 「F1の陽性対照oracleを『active rowが2件になる』に置くのは誤り」
> 「idempotencyの契約は単なる二重row防止ではなく、同一key+同一payload再送が
>  同じappointment_id／同じ成功結果へ収束し、追加row 0になること」
> 「旧staff APIはkey未配線ゆえ、UNIQUE/事前checkで2回目409なら期待200＋同一IDに対してRED となる」
> 「正しいF1陽性対照は①first=success ②retry=same success/same ID ③active=1 ④extra=0 の4点」
> 「409をGREENと数えない」

かつ同便L153「UNIQUEと事前_check_double_bookingの実在は確定」——これは当職の前回工区§2実測
（sha256=4685cfb6…、appointment_tables.py L111のUNIQUE制約／booking_validator.py L355-380の
_check_double_booking、いずれもbase・現行で無改変）を裁定の根に用いたもの、と将軍second便に明記あり。

**再解釈の要点**: 当職の前回実測（UNIQUE制約+_check_double_bookingが実在する事）自体は動いていない。
動いたのは意味づけ——「これらが2回目の重複を★守っておる★」ではなく「これらが働くゆえ2回目が★409を返し、
それがRED★」という読み替えである。

---

## §1 対象・前提の固定

- 試験対象＝`backend.services.appointment_service.create_appointment`（旧/base、commit
  `7d463edae84c704edabbd9da5465078dc62e55b1`）。staff経路。
- fixture＝前回工区§2-2で確認済の正しい対応先＝`backend/tests/test_appointment_service.py`
  （L14-18で`APPOINTMENT_TABLES`import、L31-45の`db` fixtureで全DDL実行後seed）。
  ★a3が使った`_open_file_db`/`file_db_path`は別module（booking_service側）の借用で対応先が違う★
  ——前回工区§2-2で既指摘、本設計はこの誤りを踏まない。
- ★重要な設計制約★= この経路には`idempotency_key`という引数・概念自体が存在しない（旧staff API
  key未配線、裁定文にも明記）。∴ 本設計における「同一key」は★同一payload（全引数の値が完全一致）★
  で代用する。これは§4（未測2件の影響）で再度触れる設計上の弱点でもある。

---

## §2 (a) 4点の示し方

同一`payload`（dict、深いコピーで使い回し値を固定）を用意する。

**①first=success**
- `first_result = create_appointment(**payload)` を1回目実行。
- 判定: 例外を投げず、戻り値が成功系（201または200相当、`appointment_id`を含む）である事をassert。
- `first_id = first_result["appointment_id"]`（または相当のkey）を保持。

**②retry=same success/same ID**
- 全く同一の`payload`で`create_appointment`を2回目実行。
- 判定: 例外を投げず、戻り値が①と同じ成功系であり、`appointment_id`（または相当のkey）が
  `first_id`と完全一致する事をassert。
- ★例外を握る分岐を一切書かない★（詳細は§3(b)）。

**③active=1**
- SQL: `SELECT COUNT(*) FROM appointments WHERE clinic_id=? AND unit_id=? AND start_time=?
  AND status NOT IN ('cancelled','no_show')`
- 1回目呼出し直後に`count_before`として測定し1である事をassert。
- 2回目呼出し直後にも同一SQLで`count_after_retry`として再測定し1である事をassert（④の差分計算にも使う）。

**④extra=0**
- `count_after_retry - count_before == 0` をassert。
- ★絶対値でなく差分で書く★——既存データが混在する環境でも成立させる為の一般化。

---

## §3 (b)「409をGREENと数えない」の書式化

★核心=②のretry呼出しを`try/except HTTPException`や`pytest.raises(HTTPException)`の類で
一切★包まない★★。例外が飛ぶならテスト関数自身がその例外で失敗する形にする。

- 理由: `pytest.raises(HTTPException)`で包み「409が飛べばOK」と書くと、旧codeの409という
  ★欠陥の兆候そのもの★を「期待仕様」として飲み込みGREEN化する——本部長殿が正した誤りの
  再発形そのものである。
- 設計例（未実行・pseudo）:
  ```
  retry_result = create_appointment(**payload)  # 例外を捕らえない
  assert retry_result["status"] in (200, 201)
  assert retry_result["appointment_id"] == first_id
  ```
  2回目呼出しが`HTTPException(409, ...)`を投げれば、この`assert`行に到達する前に例外伝播
  → pytestがFAIL/ERRORとして報告 → RED。例外を捕らえる分岐を書かない事自体が
  「409をGREENと数えない」の実装形である。
- 追加原則: 将来responseオブジェクト形に実装が変わった場合も`assert response.status_code == 200`
  のように★完全一致★でassertし、`in (200, 409)`のような曖昧な許容比較を書かない事を設計原則として
  明記する。

---

## §4 (c)「欠陥が在れば必ずRED か」

- 本設計は逐次呼出し（1回目→2回目、非並行）。並行race由来の不確実性は対象外
  （それはF2/並行test側の役目であり本設計のscope外）。
- 前回実測（sha=4685cfb6…）で確定済: base側に`_check_double_booking`
  （booking_validator.py L355-380）と`UNIQUE(clinic_id, unit_id, start_time, status)`
  （appointment_tables.py L111）が★idempotency_keyの有無に関わらず無条件に★存在する。
- **経路A**: `create_appointment`はINSERT前に必ず`validate_booking()`を呼ぶ
  （appointment_service.py L165-180、無条件呼出し）。2回目呼出し時、1回目でコミット済の行を
  `_check_double_booking`のSELECTが検出すれば`is_valid=False`→`HTTPException(409,...)`。
  §3の書式であれば②のassertion前に例外伝播→RED。
- **経路B**: 万一`_check_double_booking`が検出し損ねても（未測①）、INSERT自体がUNIQUE制約に
  抵触し`sqlite3.IntegrityError`相当を投げる。これが上位でtry/exceptに捕捉されず伝播するなら
  （未測②）、②のassertion前に別種の例外伝播→これもRED。
- ∴ 経路A・経路Bいずれであっても、②を例外を握らずに書く限り「①と同じ成功」には到達し得ない
  構造になっている。逐次実行かつ両機構が無条件、という2点により、「欠陥が在れば必ずRED」は
  ★書ける★と判断する。

**書けぬ物（留保）**:
1. `_check_double_booking`のSELECT条件（時間range重合判定`start < other.end AND end > other.start`）
   が、設計側の与えるpayloadの`start_time`/期間次第では理論上一致しない可能性が残る。
   完全同一payloadを使う事で対処する設計にしてあるが、★実行して確かめてはいない★（未測①と同根）。
2. 経路Bが発生した場合、pytest上は「FAIL」でなく「ERROR」に分類され得る。人間が見ればどちらも
   RED扱いのはずだが、★もし上位ゲート機構がFAILのみをカウントしERRORを見逃す設計なら★、
   本4点test単体は「必ずRED」であっても、それを消費する側が取りこぼす余地がある。
   これは本test設計自体の欠陥ではなく上位ゲート側の受理条件の問題であり、
   本設計のscope外として切り分けて書く（裁定はせぬ）。

---

## §5 (d) 未測2件が本設計にどう効くか

前回工区§4で自己申告した未測2件:
1. `_check_double_booking`が2回目呼出しを確実に409で止めるか（紙上の条件一致確認に留まり、
   実行して確かめてはいない）。
2. base側`create_appointment`のINSERT自体がUNIQUE違反時にtry/exceptで囲まれているか
   （該当箇所に`try`が無い事は`git show`目視で見えたが、上位呼出し元でのcatchまでは未追跡）。

- 未測①は§4の経路Aの信頼性に直結する。もし実行して検出し損ないが判明すれば、防御は経路B単独に
  委ねられる形になる。∴ 本設計は経路Aに単独依存せず、経路Bも同一の書式（§3・例外を握らない）で
  受け止める形にしてある——未測①がどちらに転んでも構造上REDを保つ為の意図的な二重化。
- 未測②は経路Bが「クリーンな409」になるか「生のIntegrityError伝播」になるかを左右する。
  ②のassertionが「同じID」への完全一致を要求する設計にしてある為、もし将来
  「例外を握り潰し新規appointment_idで200を返す」実装が存在すれば②のID不一致で検出できる。
  逆に「握り潰し1回目と同一IDをでっち上げて200を返す」実装は考えにくいが理論上否定しきれず、
  この一点は実行して確かめる以外に確定できない、と明記する。
- ★§1の設計制約（同一keyの代用＝同一payload）とも連動する★——本経路にidempotency_keyという
  概念自体が無い為、②の「同一payload」判定はpayloadの生成方法（timestampを含む値を都度生成する
  実装だとpayloadが毎回微妙に変わり得る）に依存する。実装側でpayload生成をtest内で固定する事を
  設計注記として明記する。

---

## 母集団宣言・禁則遵守申告

- 本工区で新たに読んだfile＝0件。前回工区（§4記載の読了範囲）の実測結果を引用するに留めた。
- 本工区で新たに実行したコマンド＝無し（設計のみ）。
- 禁則遵守: `hakudokai-dev`への書込み・patch適用・実走（pytest等）、いずれも行っていない。
  `newbuild`へは一字も書いていない。rcをpipeに通していない。
  `/usr/bin/grep -r`は本工区では使用機会が無かった（0件は0件と書く）。commitは行わない
  （karo-second殿がPASS後）。

断面: 2026-08-06T10:29:36+0900（`date`実測）／base_commit（測定時HEAD）=`89685bf202cedef63f30638010116f817ab9ea5d`
提出先: 家老second + 軍師second
