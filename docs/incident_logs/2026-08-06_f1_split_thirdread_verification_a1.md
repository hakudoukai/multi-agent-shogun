# F1割れ 第三の独立読み — 足軽1号

下命=家老second msg_20260806_100641_275e2dd7（10:06:41・宛先=当職＋軍師second）。
★冒頭——裁定を求めぬ★。「どちらを採るべきか」は書かぬ。双方の根拠を検め、どちらが何を見ておらぬかのみ示す。
本便は read-only。`hakudokai-dev`へは一字も書いておらぬ・apply/走らせる/rcをpipeに通す、いずれも行っていない。
grepは全て`/usr/bin/grep`使用（`which grep`実測で確認、alias/wrapper無し）。

---

## §1 双方が読んだ断面の確認（⒜・逐語で示す）

### §1-1 対象2文書のsha256/行数を再測（改変検知）

| doc | 主張された sha256(先頭16桁) | 行数 | commit | 当職の再測 |
|---|---|---|---|---|
| a4 `2026-08-06_reserveimage_f1f3_greenonly_causal_analysis_a4.md` | `c6ab1e8c96cab921` | 143 | `20024df` | ★一致★（`sha256sum`/`wc -l`実測） |
| a3 `2026-08-06_reserveimage_cycle2_red_positive_control_design_a3.md` | `1530f54a4c1483da` | 202 | `e1bd5d7` | ★一致★（`sha256sum`/`wc -l`実測） |

両文書とも改変なし。以下は全文読了の上での引用。

### §1-2 a4が読んだ物（逐語）

a4本文 L5-6:
> 「参照先固定: base=`7d463edae84c704edabbd9da5465078dc62e55b1`……コード実読は既存worktree
> `/tmp/resimg-cycle2-impl-20260806`（前工区で他者が用意した物・当職が新設せず）への**読取のみ**」

★実測★（当職）: `/tmp/resimg-cycle2-impl-20260806`の`git status --short`は

```
M backend/api/web_reservation/booking.py
M backend/services/appointment_service.py
M backend/services/web_reservation/booking_service.py
M backend/tests/web_reservation/test_phase2_2_booking.py
?? backend/db/migrations/booking_concurrency_root.py
?? backend/tests/test_booking_concurrency_root_migration.py
```

★HEADは`7d463ed`（base）のままだが、working treeにはpatchが未commitで適用済み★。
∴ a4が「読取のみ」と申告した対象は、**working treeの実ファイル＝patch適用後（現行）の内容**であり、
`git show base:path`で得られる純粋なbase内容とは異なる。a4はこの区別を本文中で明示していない
（「base=…」の直後に「worktreeへの読取のみ」と続けており、両者が同一であるかの様に読める書き方）。

### §1-3 a3が読んだ物（逐語）

a3本文 §0:
> 「`git -C /tmp/resimg-stage1-runtime-20260806 show 7d463edae84c704edabbd9da5465078dc62e55b1:<path>`
> で読取のみ取得できることを実測で確認した」

★実測★（当職）: a3は`git show <sha>:<path>`を一貫して用いており（§3-1/§3-2/§3-3で明記）、
これは working tree の状態に関わらず**該当commitのgit-object内容のみ**を返す。
`/tmp/resimg-stage1-runtime-20260806`自体は別branch（`stage1/reservation-cycle1-canonical-flow`）
かつclean（当職`git status`実測）で、単なる`git show`実行台として使われているのみ。

### §1-4 ⒜への回答

★確認済★——a4とa3は★別の断面★を見ている。a4=`/tmp/resimg-cycle2-impl-20260806`のworking tree実体
（HEAD=base commitだが★未commit差分としてpatchが適用済★）。a3=`git show base:<path>`による
★純粋base（working tree差分の影響を受けぬ）★。家老second殿の見立て（「a4=patch適用後／a3=patch適用前」）
は★方向として正しい★が、正確には「a4=working tree実体（コミット状態でなく差分適用状態）」であり
「base commit」そのものではない、という一段階の精密化が要る。

---

## §2 足軽3号の「UNIQUE制約 未確認」を検めた（⒝）

a3本文 §3-1:
> 「当職は`appointments`テーブルのDDL（`CREATE TABLE`文そのもの）を本工区の時間内には読んでいない——
> `(clinic_id, unit_id, start_time)`相当のUNIQUE制約が旧schemaに別途存在すればこのtestはGREENになり得る。
> ∴ ㈠書ける、ただし確度は……未確認1点に懸かる」

★実測結果★（当職・base側/現行側の双方で確認）:

```
git show 7d463ed:backend/db/migrations/appointment_tables.py | sed -n '77,111p'
```
→ `appointments`テーブルDDLに **`UNIQUE(clinic_id, unit_id, start_time, status)`**（L111）が★存在する★。
`status`列は`DEFAULT 'confirmed'`（L88相当）。
`git diff --stat 7d463ed -- backend/db/migrations/appointment_tables.py`は★無出力★
（=このfileはbase/現行worktree間で無改変・両断面で同一内容）。

**a3が未確認と自己申告した点は、当職の実測で「存在する」と判明した。** かつa3自身が本文で書いた
条件文（「UNIQUE制約が別途存在すればこのtestはGREENになり得る」）に、実測結果を代入すると
——★GREEN側に倒れる★。a3の提案test（`test_staff_exact_retry_creates_duplicate_on_old_code`）は
同一payload（`status`を明示せず、default='confirmed'が両呼出しで一致）を2回投げる設計であるため、
このUNIQUE制約は2回目のINSERTを直接ブロックし得る。

### §2-1 ★双方とも見ていなかった第三の機構★（当職が本工区で新規発見）

a3もa4も`backend/services/appointment_service.py`の`create_appointment`が呼ぶ
`backend/services/booking_validator.py`の`validate_booking()`を検分していない。実測:

```
git show 7d463ed:backend/services/appointment_service.py | sed -n '165,180p'
```
→ `create_appointment`はINSERT前に`validate_booking(...)`を無条件呼出し、
`if not validation.is_valid: raise HTTPException(409, ...)`。

`validate_booking`のステップ4（`_check_double_booking`、`booking_validator.py` L355-380）は
`clinic_id/unit_id`一致・`status NOT IN ('cancelled','no_show')`・時間range重複
（`start < other.end AND end > other.start`）でSELECTし、該当あれば`add_error`→`is_valid=False`。
**a3の提案testの2回目呼出し（同一start/end/status='confirmed'）はこの条件に一致するため、
INSERTへ到達する前に409で止まる可能性が高い。**

`git diff --stat 7d463ed -- backend/services/booking_validator.py`は★無出力★
（=`_check_double_booking`はbase・現行の両方に無改変で存在——patchが追加した物ではない）。

### §2-2 実際にF1テストが動く経路のschemaを実測（自己検算）

a3の疑似コードは`_open_file_db`/`file_db_path`という名を使うが、これは
`backend/tests/web_reservation/test_phase2_2_booking.py`（`booking_service`側のtest）の既存fixtureの
借用であり、`create_appointment`（`appointment_service`側）の実テストが実際に使う fixture ではない。
`create_appointment`の実テストは`backend/tests/test_appointment_service.py`にあり、そのL14-18で
`from backend.db.migrations.appointment_tables import APPOINTMENT_TABLES`を明示import、
`db`fixture（L31-45）で`TABLES`（`APPOINTMENT_TABLES`含む）を全DDL実行してからseedしている。
このfileも`git diff --stat 7d463ed -- backend/tests/test_appointment_service.py`は★無出力★
（base・現行で無改変）。∴ アプリの実schemaでF1testを組めば、UNIQUE制約は初めから盤面に在る。

---

## §3 三値判定（⒞）

| 対象 | 判定 | 根拠 |
|---|---|---|
| ⒜「別の断面を見ていたか」 | **㈠該当**（確認済） | §1-4。a4=worktree実体（patch適用済working tree）／a3=`git show base:path` |
| F1の実体判定（a3㈠書ける vs a4㈡構造上不能） | **㈡いずれかに誤りの根拠あり** | 下記詳述 |
| ⒝「UNIQUE制約 有無」 | **確定**＝★在る★（base・現行とも無改変で存在） | §2 |

**F1の実体判定について**——a3が明示した自己条件（「UNIQUE制約が存在すればGREENになり得る」）に
実測結果（存在する）を当てはめると、a3自身の推論の帰結は㈠書ける寄りではなく反対方向へ動く。
かつa3・a4いずれも見ていなかった`_check_double_booking`（base・現行とも無改変で存在）が、
a3の提案test設計に対して独立に同じ方向（2回目呼出しをINSERT前に止める）へ働く。

ただし★これはa4の判定が正しいと裁定する物ではない★——a4が挙げた根拠
（`appointment_slot_claims`のPK制約）はpatch新規追加であり★base側には存在せず★（`git show base:path`
→`fatal: path ... does not exist`、当職再確認済）、a4の論拠それ自体はbase側には適用できない。
a4は「実在するcallerにretry機構が無い」という部分（`appointments.py`・`useAppointmentForm.ts`は
base/現行とも無改変ゆえ両断面で真）は妥当だが、「重複を止める機構」として挙げたのは現行のみに
存在する新設機構であり、baseで実際に重複を止め得る機構（UNIQUE制約＋`_check_double_booking`）
とは★別物★である。

∴ ★双方とも、実際にF1の帰趨を決める機構（base側のUNIQUE制約＋事前二重予約check）を
文書内で一度も検分していない★。これが本工区で当職が示せる最も確度の高い所見である。
「どちらを採るべきか」への回答ではなく、「両者がまだ見ていない盤面が存在する」という報告に留める。

---

## §4 母集団宣言・未測事項

- 読了範囲: a4 doc 全143行／a3 doc 全202行（冒頭から末尾まで、共に既存sha256一致確認後に全文読了）。
- 実測コマンド: `git show`（読取専用）・`git diff --stat`・`git status --short`・`sed -n`・`/usr/bin/grep -n`
  のみ。apply/checkout/merge/実走（pytest等）は一切行っていない。
- ★未測1件★: `_check_double_booking`が2回目呼出しを確実に409で止めるか（実行して確かめてはいない
  ——紙上での条件一致の確認に留まる。真の並行（thread同時実行）シナリオでの挙動、および
  base側`create_appointment`のINSERT自体がUNIQUE違反時に未捕捉の`sqlite3.IntegrityError`を
  投げっぱなしにするか＝try/exceptで囲まれているかは、当職は本工区で確認していない
  （該当箇所に`try`が無い事は`git show`目視で見えたが、上位呼出し元でのcatchまでは追っていない）。
- F2/F3についてはa3・a4の現象判定が一致（F2=現行への直接testとして双方合意／F3=旧codeに
  該当経路自体が無い、で現象一致）しており、当職は追加の反証を見出していない
  （`booking_service.py`のdiffを当職も再確認したが、a3の「baseにBEGIN IMMEDIATE・early-return無し」
  の実測に不一致は無い）。

## 禁則遵守の申告

`hakudokai-dev`への書込み・apply・走らせる（pytest実行等）・rcをpipeへ通す——悉く行っていない。
`/usr/bin/grep -r`不使用（本工区は対象2fileの逐語読了＋`git show`によるDDL/service読取が中心で、
再帰grepを要する場面が無かった——0件は0件と書く）。commitは当職では行わぬ（karo-second殿がPASS後）。

---

断面: 2026-08-06T10:14:31+0900（`date`実測）／base_commit（測定時HEAD）=`e1bd5d7c81491e1cb25e5ca46ba4d5349fe99e31`
提出先: 家老second + 軍師second
