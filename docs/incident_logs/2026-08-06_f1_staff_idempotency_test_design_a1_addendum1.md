# F1 staff idempotency test 設計 追補1（自己発見の引用訂正＋RED/GREEN/正反対の三対）— 足軽1号

対象=`2026-08-06_f1_staff_idempotency_test_design_a1.md`（335行・sha256=
`6ae76bbf436266a2d8ca21ad303102833abae93344fda4ba07673a6607b7a6b6`・既に家老second＋軍師secondへ
提出済）。★旧版は消していない・書き換えていない★（旧版自体が当職の初回設計思考の記録として単独で価値を
持つため。W14での自己訂正前例と同じ扱い方）。本追補が旧版§1・§4・§7の一部を実質的に補正・拡充する。

下命=家老second msg_20260806_130242_6c1d48c0（13:02:42・「先の下命に一つ足す」＝将軍second条
「具体は誤っていても訂され、曖昧は正しくても検められない」の適用・㈡を㈠㈡㈢の三対へ拡張）。
★本追補は当職の自発的提出★——karo-second殿の次便（13:12:37 msg_20260806_131237_6ad18195）は既に
旧版を賞して「軍師secondの裁を待つ・新工区は出さぬ」としているが、13:02:42便の要求（三対）は
旧版では未だ満たしていない（旧版§7は㈠のみで㈡㈢は別節に分散していた）。賞された事に安んじて
未回答の下命を放置しない為、当職の判断で本追補を出す。

★冒頭★= 本便も★設計のみ★。`hakudokai-dev`への書込み・patch適用・実走は本工区でも一切行っていない。
本工区で新たに実行したのは`Read`（`booking_validator.py` L1-90 + L340-390）と`/usr/bin/grep -rn
"check_double_booking\b" --include=*.py .`（`.venv-linux`/`__pycache__`除外）のみ。

---

## §1 自己発見の引用訂正（旧版§1・§4・§7の補正）

★誤★= 旧版は「A2/B2のRED根拠＝`check_double_booking`（`appointment_service.py` L71-110）」と書いた。

★正★= 本工区の再実測で判明——`check_double_booking`（`appointment_service.py` L71-110）は
`create_appointment`の通常create経路からは★呼ばれていない★。呼び手は`diagonal_service.py`のみ
（`/usr/bin/grep -rn "check_double_booking\b"`実測＝L16 import・L107-108・L255・L270、いずれも
diagonal_service.py内、ななめ予約連結の専用経路）。

`POST /api/appointments`の通常create（`api_create_appointment`→`create_appointment`）が実際に
ダブルブッキングを検知する経路は★別関数★——

1. `appointment_service.py` L174: `from backend.services.booking_validator import validate_booking`
2. `appointment_service.py` L175-186: `validation = validate_booking(conn=conn, clinic_id=..., ...)`
3. `booking_validator.py` L35-79 `validate_booking()`のステップ4（L66-67）＝
   `_check_double_booking(conn, result, clinic_id, unit_id, start_time, end_time, exclude_appointment_id)`
4. `booking_validator.py` L348-373 `_check_double_booking()`本体——時間範囲重複判定
   （`start < other.end AND end > other.start`、L358-364）。重複ありなら
   `result.add_error(4, "double_booking", ...)`（L373）で`result.is_valid=False`にする。
5. `appointment_service.py` L187-191: `if not validation.is_valid: raise HTTPException(409,
   {"message": "予約を作成できません", "errors": validation.errors})`。

★結論への影響★= RED判定そのもの（A2/B2が現行HEADで期待と不一致になる事）は★変わらない★——
機構の名前を誤っていただけで、「2回目が409で弾かれる／別予約として201で通る」という★観測される
振舞いの予測は補正の前後で同一★。だが「なぜ」の説明を誤った関数に帰していた事は、下命が求める
㈡（GREENに何が要るか＝どこにhookするか）の設計精度に直結する誤りであり、放置すれば実装工区が
誤ったfileを見に行く事になる。∴ 訂正する。

`test_04_double_booking`（既存・不触）も同一経路（validate_booking→step4）を通っている——
これは旧版§5の委譲判断（Anti-Duplication）を★裏付ける方向に働く★（同一機構である事が今回で
より正確に確認できた）。旧版§5の結論自体は不変。

---

## §2 A群（正replay）の三対——㈠なぜ今RED／㈡何が入ればGREEN／㈢正反対チェック

㈠★なぜ今RED★= `create_appointment`は`validate_booking()`（§1で正引用）を★INSERTより前に★呼ぶ
（`appointment_service.py` L174-191はL193「# INSERT」より前）。A2（同key・同payload・2回目）は
1回目と時間範囲が完全一致 ∴ ステップ4が重複を検知 ∴ `validation.is_valid=False` ∴ 409。
2回目のrequestは★validate_bookingを一度も迂回できない★——idempotency判定を差し込む処理が
現行コードに存在しない為。これが「必ずRED」の機械的根拠（旧版§1のgrep hit=0と本追補§1の経路特定
の2点で裏付け済）。

㈡★何が入ればGREENになる筈か（具体的hook点を名指し）★=
- `appointments.py` L86 `api_create_appointment(req: CreateAppointmentRequest)`に
  `idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")`相当の引数を追加。
- `appointment_service.py` L174（`validate_booking`呼出しの直前）に、`idempotency_key`が
  非Noneの場合の★lookup分岐★を挿入——`booking_idempotency`（未実装・仮称）に該当keyの既存record
  があり、かつ記録されたpayload hashが今回のpayloadと一致し、かつstatus="completed"なら、
  `validate_booking`もINSERTも一切呼ばず、記録済`appointment_id`から`get_appointment(conn,
  appointment_id)`相当の結果を★そのまま返す★（L259の`get_appointment`呼出しと同型の戻り値形状）。
- ∴ GREENの必要十分条件＝「validate_bookingより前段でのlookup分岐が存在し、かつ1回目のcomplete後に
  その分岐がヒットする状態になっている」事。この2点のうち1点でも欠けば旧版A2は依然RED——∴ この
  条件は★反証可能な形★で書けている（下命の「RED→GREENの遷移が予言できて初めて証になる」に応じる）。

㈢★正反対チェック★= 旧版§9で実施済（既存37件はいずれもHeader未使用・2回POSTする形は`test_04`
のみで委譲対象として区別済）。本追補の引用訂正は§9の結論（0件）を変えない——§9は「Header入力次元」
の比較であり、今回訂正した「どの関数が409を出すか」という機構の内訳とは別軸の主張だった為。

---

## §3 B群（同key異payload→409）の三対

㈠★なぜ今RED★= `payload_a`と`payload_b`は`start_time`が240分離れ・`duration_minutes=30`のため
`_check_double_booking`の時間範囲重複判定（L358-364、`start < other.end AND end > other.start`）に
掛からない（Aの終了=開始+30分、Bの開始=Aの開始+240分 ∴ 重複なし）。ステップ1-3・5も`menu_id`/
`staff_id`未指定・通常payloadゆえ通過する想定（既存`test_01_normal_create`が同型payloadで201を
得ている実績と同条件）。∴ 現行HEADでは2回目も検証を素通りし★201で新規appointmentが成立★する。
目標契約（409）とは不一致 ∴ RED。

㈡★何が入ればGREENになる筈か★=
- §2㈡のlookup分岐に、「keyが既存recordにhitしたが、今回のpayload hash≠記録済payload hash」の
  分岐を追加——この場合は`validate_booking`もINSERTも呼ばず、`HTTPException(409, "idempotency key
  conflict: payload mismatch")`相当を即時raiseする。
- ∴ GREENの必要十分条件＝「payload hash比較に基づく専用409分岐が、通常のdouble-booking 409分岐
  （§1で正引用したstep4）とは★別の判定順位で★lookup直後に存在する」事。§1で機構を正確に特定した
  からこそ、「専用409分岐はstep4より前に置かねば、B2がstep4の判定（重複なし→通過）を経て正常に
  201で終わり、専用分岐に到達する前に処理が終わってしまう」という★配置順序の要件★が明確に書ける
  ようになった（旧引用のままでは、この配置順序要件を正しく導けなかった）。

㈢★正反対チェック★= 旧版§9・§4の結論を継承。`payload_b`は`payload_a`とも既存37件のいずれとも
時間帯が重ならない固定値であり、fixtureの枠取り合いによる偽陽性/偽陰性の混入は無い。

---

## §4 D/E/Fへの影響（変更なし・申告のみ）

§1の引用訂正はD/E/F（旧版§6）の結論（構造的に未確定）には影響しない——D/E/Fの未確定理由は
「`create_appointment`が複数commit構造で単一transactionを持たない」事（L216-221とL224-230が別々の
`conn.commit()`）であり、これは`validate_booking`か`check_double_booking`かという関数名の訂正とは
★独立した別の実測★（旧版§1で既に確認済・本追補で再確認不要）。karo-second殿13:12:37便の
「D/E/Fはacquireの設置点が定まってから（GO待ち）」の理解と一致する。

---

## §5 断面・提出

本工区で新たに実行=`Read`（`booking_validator.py` L1-90+L340-390）・`/usr/bin/grep -rn
"check_double_booking\b" --include=*.py .`（`/mnt/c/Projects/hakudokai-dev`、`.venv-linux`/
`__pycache__`除外、read-only）。書込み系コマンドは一切実行していない。`hakudokai-dev`への書込み・
patch適用・実走・`newbuild`/`/tmp/resimg-*`への書込み・rcのpipe通過、いずれも行っていない。
`test_04_double_booking`は本工区でも不触。

断面: 2026-08-06T13:20頃（本工区着手直後の`date`実測は本文中に埋め込まず、以下ファイル自身の
測定値を正本とする——★自己参照の書き順回避★=行数・sha256は`Write`完了後に別コマンドで実測し
別便（家老second/軍師secondへの報告本文）に記載する。本file内には埋め込まない）。
`hakudokai-dev`側HEAD=`dfa3ac77341e5947c967c745cf8fa597ba494a2e`（不変）。
`multi-agent-shogun`側HEAD=`ed7daeb2cf6cb9ef6de72c424f2233c14506a3c1`（不変・本工区でcommitしていない）。

★木の名（karo-second殿13:26:31指摘への応答・追記のみ・§1-§4の中身は不変）★= 本file・旧版とも測定対象は
`/mnt/c/Projects/hakudokai-dev`一本のみ（`/mnt/c`に他2本・`/tmp`に7本の同名木が別途在るとの報告を
karo-second殿より受けたが、当職はそれらを一度も読んでいない）。当該木の実測sha256冒頭16桁＝
`booking_validator.py`=`b03efeb3c4dbef34`（67行呼出・348行定義はこの木限定の値。karo-second殿の
指摘通り`/tmp/resimg-cycle2-base-audit`は68行呼出・355行定義であり本追補の行番号はそちらには当たらない）。
`appointment_service.py`=`3f12ab3cd03b68a4`（karo-second殿の独立実測と一致）。`appointments.py`=
`343b4595bc1b08ba`。`test_appointment_api.py`=`f83d0bdf8e25427e`。HEAD=`dfa3ac77341e5947c967c745cf8fa597ba494a2e`
（4file共通）。

提出先: 家老second＋軍師second（旧版の監査に添えて読まれたし。旧版のみでの判定は§1の誤引用を
含んだ状態での判定になる為、本追補を★先に★読んだ上での監査を希望する）。
