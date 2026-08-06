# create_appointment commit境界 実測 (足軽4号・W20260806a4)

## §0 断面・母集団・除外

- 木＝`/mnt/c/Projects/hakudokai-dev`（★他木は本工区の対象外。/tmp配下7本・当木内の他複製は開いておらぬ★）
- 断面（自測・2026-08-06T13:5x前後）＝ HEAD=`dfa3ac77341e5947c967c745cf8fa597ba494a2e` / branch=`feat/lane1-playwright-daily-report-kanban-1f8ae1ea`
- 主file＝`backend/services/appointment_service.py`＝740行／sha256冒頭16=`3f12ab3cd03b68a4`（★家老second実測と一致。断面ズレ無し★）
- 従file＝`backend/services/booking_validator.py`＝693行／sha256冒頭16=`b03efeb3c4dbef34`
- 実読の過程で create_appointment から呼ばれる先を辿り、以下4fileを新たに開いた（母集団を当職が拡げた理由＝下命㈢㈣に「acquireを置ける点／置けぬ点」を答えるには呼出先の書込有無を測らねば答えられぬため）：
  `appointment_log_service.py`(72行/`30af5fec0e6c8f09`)・`diagonal_service.py`(445行/`20df9fcaeb1f8181`)・`prediction_service.py`(575行/`302104152651126e`)・`appointment_lock.py`(37行/`9ce1715ce1c1b692`・★create_appointmentからは呼ばれず。update_appointment専用と確認のみ★)
- 以下 全ての行番号引用は「(木=/mnt/c/Projects/hakudokai-dev, file=<名>, sha16=<値>, L###)」の形を毎回添える（母集団の警めに従う）。

## ㈠ create_appointment の本体範囲

- 定義開始＝L122 `def create_appointment(` (file=appointment_service.py, sha16=3f12ab3cd03b68a4)
- 定義終了＝L282 `return result` (同file・同sha16)。L283は空行、次関数 `def get_appointment` はL284から (同file・同sha16)。
- 定め方＝`/usr/bin/grep -n "^def "` で全関数境界を列挙し、L122の次に出現する定義行(L284)の直前までを本体とした。実行文の最後は282のreturnであり、283は本体に属さぬ空行。

## ㈡ 本体内のcommit境界

### (a) 同file内・create_appointment本体(122-282)に属する commit()

| 行 | 直前の文 | 確定する内容 |
|---|---|---|
| L221 (appointment_service.py, sha16=3f12ab3cd03b68a4) | L216-219 `INSERT INTO appointments (...)` | appointmentsテーブルへの1行が耐久化。`appointment_id`(L220 `cursor.lastrowid`)が他connからSELECT可能になる境界 |
| L230 (同file・同sha16) | L224-229 `INSERT INTO appointment_history (...)` | 同appointment_idの作成履歴1行が耐久化 |

家老second実測の「同file内 commit()出現行＝221 230 389 398 432 500 559 613 727」のうち、L221/L230の2件のみがcreate_appointment本体(122-282)に属する。残る7件は以下の別関数内であり本体に非ず（`^def `境界で確認）：
`update_appointment`(297-456)＝L389,398,432 ／ `cancel_appointment`(457-531)＝L500 ／ `transition_status`(532-663)＝L559,613 ／ `create_kanban_card`(685-733)＝L727。

### (b) ★同file内には現れぬが、create_appointmentの実行時に呼出先で発生するcommit()★（下命の母集団=同file限定を超える発見。§0参照）

本体内で呼ばれる関数の実体を辿ったところ、以下4件が create_appointment の呼出木の中で追加のtransactionを確定させていた。いずれも appointment_service.py の外の別fileである。

| 呼出元（appointment_service.py内） | 呼出先の実際のcommit()行 | 確定する内容 | 呼出元が try/except で囲うか |
|---|---|---|---|
| L233-257 `log_appointment_action(...)`（appointment_log_service.py, sha16=30af5fec0e6c8f09） | L70 `conn.commit()`（同file） | appointment_logsへの1行 | ★囲まぬ★。ただし呼出先自身がL42-72で全体をtry/exceptしており例外を外へ出さぬ（L71-72「except Exception as e: logger.warning」）ため、呼出元から見ても失敗は不可視 |
| L262-268 `try: get_linked_info(...)`（diagonal_service.py, sha16=20df9fcaeb1f8181） | `_ensure_diagonal_columns()`内 L36 `conn.commit()`（同file。L392でL27の`_ensure_diagonal_columns`を呼ぶ） | appointmentsテーブルへのALTER TABLE（無条件でPRAGMA読取後に毎回commit。列が既存でも実行される） | 囲む（appointment_service.py L262-268 `try:`...`except Exception as e: logger.warning`） |
| L269-281 `try: calculate_prediction_score(...)`（prediction_service.py, sha16=302104152651126e） | `_ensure_prediction_columns()`内 L35 `conn.commit()`（同file。L253で呼ばれる） | prediction関連列のALTER TABLE（同上・無条件commit） | 囲む（appointment_service.py L269-281） |
| 同上 `save_prediction(...)`（appointment_service.py L277） | `_ensure_prediction_columns()`再呼出＝L35（prediction_service.py・L295で再度呼ばれる） | 同上（★L269-281の中で2回目★） | 囲む（同上） |
| 同上 `save_prediction(...)` | `_ensure_prediction_log_table()`内 L53 `conn.commit()`（prediction_service.py・L296で呼ばれる） | prediction_logテーブルのCREATE TABLE IF NOT EXISTS確定 | 囲む（同上） |
| 同上 `save_prediction(...)` | L322 `conn.commit()`（prediction_service.py・save_prediction自身の最終commit） | appointments.prediction_score/label のUPDATE ＋ prediction_logへのINSERT が耐久化 | 囲む（同上） |

∴ create_appointment 1回の呼出で実際に発生し得るcommit()は、同file内2件(L221,L230)に加え、他fileで最大6件（1〜3件は無条件ALTER TABLEのため列が既に存在すれば実質no-opだが`conn.commit()`自体は毎回実行される）。合計で最大8commit。

## ㈢ acquireを置ける点／completeを置ける点

★下命の禁に従い「どこに置くべきか」は書かぬ。実測で成立する候補点のみ列挙する★

### acquire候補（置ける点＝ここに書込を足せば、既存の後続処理を壊さず独立してcommitさせられる場所）

- **L191直後〜L213の間**（appointment_service.py, sha16=3f12ab3cd03b68a4）＝バリデーション（L137-191）が全て通過し、かつINSERT準備（L193-213）がまだDBへ何も書いていない区間。ここは純Python処理のみでconn.execute()が無い（L208のPRAGMA table_infoのみ＝読取）。この区間に書込＋独立commitを足しても、既存のL214以降の処理には影響せぬ（実測＝この区間にconn.execute系呼出は0件・PRAGMA読取のL208のみ）。
- **L214-219と同一transaction内**＝L216-219のINSERT INTO appointmentsと同じcommit(L221)で確定させる形。この場合acquireは独立した点ではなく、appointments行の確定と不可分になる（L214の直前に書込文を足せば、L221のcommitで両方が同時に耐久化される）。

### complete候補（置ける点＝既存のガード無し経路として関数からraiseされずに到達する最終点）

- **L230直後**（appointment_service.py, sha16=3f12ab3cd03b68a4）＝appointments行(L221)とappointment_history行(L230)の両方が確定した直後。この点に到達する前にraiseされれば全体が失敗として呼出元へ伝播する（L145-190の各validateはHTTPExceptionをraiseし、L221/L230のいずれのcommitより手前でしか起きぬ＝実測、L191-220間にraise文は無し）。★L230以降(L232-281)はいずれも例外を外へ伝播させぬ構造（㈡(b)表の右列）ゆえ、L230は「raiseされずに必ず通る最後の点」である★。

## ㈣ 置けぬ点と、置けぬ理由

| 点 | 置けぬ理由 | 分類 |
|---|---|---|
| L214-219（appointment_service.py, sha16=3f12ab3cd03b68a4・INSERT文の実行行そのもの） | commit前ゆえ未耐久・他connから見えぬ。ここ単独を「点」として使えば、L221のcommitが失敗した場合に何も残らぬ | 情報の欠ではない（sqlite3の仕様上の物理的事実。測れば分かる） |
| booking_validator.py（sha16=b03efeb3c4dbef34）内、L174-186から呼ばれる`validate_booking`の全経路 | 同fileに`.commit(`が0件（実測＝`/usr/bin/grep -c ".commit("` = 0）。SELECT専用のためcommit境界が存在せぬ | 情報の欠ではない（実測で確定） |
| L282（appointment_service.py, sha16=3f12ab3cd03b68a4・`return result`）を「関数全体の完了点」として使う事 | ㈡(b)の通り、L230からL282の間に最大6件の独立commitが呼出先fileで発生し得るが、いずれも例外を外へ伝播させぬ形で書かれている。∴ L282に到達した事は「appointments行とappointment_history行が確定した事」しか保証せず、ログ・ななめ予約リンク・予測スコアの各commitが実際に起きたか否かをL282到達の事実だけから判別できぬ | ★裁の欠★＝「complete」を「中核(appointments+history)の確定」と読むか「副作用(ログ/リンク/予測)まで含めた到達」と読むかは、本工区の実測だけでは定まらぬ。当職は材料のみ示し、どちらを取るかは裁定せぬ |
| `_ensure_diagonal_columns`(diagonal_service.py L27-36)・`_ensure_prediction_columns`(prediction_service.py L26-35)の各commit | 呼出元(L262-281)がtry/exceptで囲んでおり、かつこれらのALTER TABLE自体が「列が既に存在すれば実質no-op」の無条件commitである。acquire/completeの意味を持たせるには不適（列追加の有無に関わらず毎回commitが起きる＝ビジネス上の完了とは無関係な整合性維持のcommit） | 情報の欠ではない（実測で確定。ただし「不適」の判断は当職の言及に留め、置くか置かぬかの決定はせぬ） |

## ㈤ 三値

- D/E/F（足軽1号F1設計 §6・pending block/失効reclaim/reconnect）との対応付け＝★UNMEASURED（己は測っておらぬ）★。理由＝本工区は下命上 `booking_idempotency` の設計内容(table/列/acquire関数signature)を対象に含まぬ。当職はappointment_service.py側の実測のみを行った。
- 「L221とL230が同一transactionか否か」＝★実測済＝別transaction（2件の独立conn.commit()）★。足軽1号F1設計 a1・L210-213（`docs/incident_logs/2026-08-06_f1_staff_idempotency_test_design_a1.md`）が同じ実測結果（「単一transactionでは無く複数回の個別conn.commit()」）を独立に述べており、当職の実測と一致した（★陽性対照的な相互確認。写してはおらぬ＝当職は先にsource自体を読み、その後この既存記述と突合した★）。
- 呼出先6commit(㈡(b))が実際に本番で毎回起きるか（DBに既に列が存在する場合の頻度等）＝当職は未測。★UNMEASURED★（測るにはDBスキーマの現況を見る必要があり、本工区は`appointment_service.py`/呼出先ソースの実読のみを範囲としたため）。

---
report path: `docs/incident_logs/2026-08-06_create_appointment_commit_boundary_a4.md`
（sha256/行数は本人が書けば読了偽装になるため記さず。読了/検証する者が己で `sha256sum` を打たれよ）
