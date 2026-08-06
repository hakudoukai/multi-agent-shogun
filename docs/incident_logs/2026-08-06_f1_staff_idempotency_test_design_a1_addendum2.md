# F1 staff idempotency test 設計 追補2（正本refでの引き直し・比較可能sha・RED再判定）— 足軽1号

下命=家老second msg_20260806_133506_22b96c61（13:35:06）。前提=追補1（140行・sha256冒頭16=`f30ba77f254aee66`）
がPASS（軍師second 13:32:30・commit `9de69e5`）と別に、当職が「木の名」として書いた
`/mnt/c/Projects/hakudokai-dev`は★正本ではなかった★という指摘。当該checkoutはbranch
`feat/lane1-playwright-daily-report-kanban-1f8ae1ea`・HEAD=`dfa3ac77`（2026-07-19断面）であり、
正本は`origin/wp-a1-a3-3-20260723`（karo-second殿測定時点=`78573ba7`・2026-08-04）。
★追補1は書き換えていない★（旧版は残す・下命通り）。本便が別fileとして正本での引き直しを行う。

★冒頭★= 本便も設計のみ。`hakudokai-dev`への書込みは無し。実行したのは`git fetch`（無断可・読取専用）と
`git show <ref>:<path>`（read-only、blob内容取得）・`sha256sum`・`diff`のみ。checkout/pull/merge/
patch適用は一切行っていない。

---

## §1 正本refの固定（再現可能な形で）

`git -C /mnt/c/Projects/hakudokai-dev fetch origin wp-a1-a3-3-20260723`実行後、
`git rev-parse origin/wp-a1-a3-3-20260723`=`feb945cf...`（本工区時点の最新tip）。

★branchは活きて動いている★——karo-second殿測定時点（13:35頃）の`78573ba7`から本工区までに
174 commit進んでいる（`git log --oneline 78573ba7..origin/wp-a1-a3-3-20260723 | wc -l`実測）。
∴ 「正本」を一意に指すには★refの名前だけでは足りず、pin留めした個別commitのsha★が要る。

★当職の判断★= karo-second殿が明記した`78573ba79221fb195a1fc026f304812949836c0a`
（2026-08-04T08:18:20+0900、`git log -1`実測）に★pin留め★する——同殿の測定と直接比較可能にする為。

★但し確認済★= 上記174 commitのうち、当設計に関わる4fileを変更した物は★0件★
（`git log --oneline 78573ba7..origin/wp-a1-a3-3-20260723 -- <4file>`実測=0行）。かつ
`git show 78573ba7:<path> | sha256sum`と`git show origin/wp-a1-a3-3-20260723:<path> | sha256sum`を
4file全てで直接比較し★完全一致★を確認した。∴ pin留め先を`78573ba7`にするか最新tipにするかで、
本追補の結論は変わらない（念の為の実測であり、当てにした前提ではない）。

再現手順（誰でも同じ値を引ける形）=
```
git -C /mnt/c/Projects/hakudokai-dev show 78573ba79221fb195a1fc026f304812949836c0a:<path> | sha256sum
```
（`git show`はgit blob内部表現を返す為、working treeのCRLF変換を経ない——これが§2の「比較し得る値」の理由）。

---

## §2 4fileの正本sha（比較可能形）・local(/mnt/c)産shaとの対比

| path | 正本sha16 | 正本行数 | local(/mnt/c)産sha16 | 差の性質 |
|---|---|---|---|---|
| `backend/api/appointments.py` | `a16a09a09456e33f` | 190 | `343b4595bc1b08ba` | CRLF差のみ（`diff <(sed s/\r$//)`で完全一致確認済） |
| `backend/services/appointment_service.py` | `2aa999da70fe8405` | 740 | `3f12ab3cd03b68a4` | CRLF差のみ（同上） |
| `backend/services/booking_validator.py` | `5c30548b93a06285` | 700 | `b03efeb3c4dbef34` | ★CRLF＋実内容差7行★（§3で詳述） |
| `backend/tests/test_appointment_api.py` | 未算出（§4参照） | 793 | `f83d0bdf8e25427e`（旧測定・693行相当） | ★CRLF＋実内容差110行★（§4で詳述） |

★appointment_service.pyの正本sha16=2aa999da70fe8405はkaro-second殿13:26:31便の独立実測と一致★。
本追補で当職が独立に引き直した値であり、写しではない。

`test_appointment_api.py`の正本sha16は本表では意図的に空欄にした——理由=カラム名「正本sha16」の
比較対象がpathであり、行数（793）自体がCRLF差でなく★実内容差110行★を含む事が先に判明した為、
sha一致/不一致の一言だけでは何を測ったか読み手に伝わらぬと判断し、§4で内容を示した上でsha値を記す。

---

## §3 booking_validator.py の実内容差7行——RED結論への影響を判定

`diff`実測（local `/mnt/c`版のCRLF除去後 vs 正本）=追加7行のみ、削除0行。差分の実体=

1. import 1行追加＝`from backend.services.staff_shift_availability import staff_is_available`。
2. `_check_basic`（ステップ1、正本L83-193）内・`if staff_id is not None:`ブロック（正本L171-193）の
   末尾に6行追加＝`staff_is_available(conn, clinic_id, staff_id, st, et)`が偽なら
   `result.add_error(1, "staff_shift_unavailable", ...)`。

★この追加は`staff_id is not None`の場合のみ実行される（正本L171でguard済）★。当職の§3・§4設計
（A群・B群双方のpayload）は`provider_id`（staff_id相当）を★一度も指定していない★——旧版・追補1
いずれも`payload`/`payload_a`/`payload_b`に`provider_id`fieldは無い。∴ `staff_id=None`となり、
この新規追加ブロックは★A群・B群のいずれのtestでも実行されない★。

`_check_double_booking`本体（正本L355-410、ステップ4）は当職が§1で引用した内容と★1文字も違わない★
（`diff`で当該関数の範囲を個別比較し完全一致を確認済）。呼出し位置＝`validate_booking()`
（正本L36-79）内L68。旧引用（`booking_validator.py` L348-373）は行番号のみ古く（local `/mnt/c`は
2026-07-19断面）、正本では★L355-410★に相当する——★機構・ロジックは完全一致、位置のみ移動★。

∴ ★当職の判定（下命により当職が断ずる事とされた点）＝A2/B2のRED結論は正本でも成立する★。
根拠＝(a) 差分7行は`staff_id`必須のガード内にあり当設計のpayloadには無関係、(b) ダブルブッキング
検知の本体ロジックは完全一致、(c) `appointment_service.py`・`appointments.py`は正本でも完全一致
（§2）、(d) `Idempotency`関連の文字列は正本4fileでも★hit=0★（`grep -in idempotency`実測）。

---

## §4 test_appointment_api.py の実内容差110行——delegate先(test_04)への影響を判定

`diff`実測=追加110行、削除0行。差分の実体=

1. import 2行追加＝`import csv`・`import io`（ファイル冒頭、これが後続全体を2行分shiftさせている）。
2. ファイル末尾に module-level test 2件を新規追加＝`test_37_appointments_export_returns_bom_csv_with_
   expected_columns`（正本L720-）・`test_38_appointments_export_honors_status_and_staff_filters`
   （正本L760-）。DD-RESERVE-010（予約CSVエクスポート）関連、idempotencyとは★無関係の別機能★。

`test_db`fixture（正本L24-45、旧引用L21-42から2行shift）・`_future`/`_get_unit_id`helper・
`test_04_double_booking`本体（正本L129-149、旧引用L127-147から2行shift）は★内容が1文字も違わない★
（`diff`で個別比較・完全一致確認済）。

★既存test件数の訂正★= 旧版・追補1は「既存37件」と書いたが、正本では★39件★（新規2件を含む為）。
∴ 旧版§3・追補1で当職が新規test番号として仮置きした`test_37`/`test_38`は★正本の既存test番号と
衝突する★（正本の`test_37`/`test_38`は既にCSV export testとして実在する）。実装工区で採番する際は
`test_39`以降を使うべきである——これは当職が旧版で「実装着手時の採番次第」と留保していた通りの
懸念が、正本参照で★具体的に的中した★形である。

∴ ★委譲判断（§5・test_04_double_bookingへの委譲）そのものは正本でも成立する★
（内容完全一致・不触の対象として引き続き有効）。既存件数の記述のみ39件へ訂正が要る。

---

## §5 旧版・追補1の行番号引用に対する正本対応表

| 旧引用（local `/mnt/c`断面） | 正本（`78573ba7`断面）での対応 | 内容差 |
|---|---|---|
| `appointments.py` L85-98 `api_create_appointment` | 同一（L85-98） | 無し（CRLFのみ） |
| `appointment_service.py` L122-282 `create_appointment` | 同一（L122-282） | 無し（CRLFのみ） |
| `appointment_service.py` L174-191（validate_booking呼出＋raise） | 同一（L174-191） | 無し |
| `booking_validator.py` L35-79 `validate_booking` | L36-79（1行shift） | 無し（本体） |
| `booking_validator.py` L66-67（step4呼出） | L68（2行shift） | 無し |
| `booking_validator.py` L348-373 `_check_double_booking`本体 | L355-410 相当（7行shift） | 無し（本体は完全一致） |
| `test_appointment_api.py` L21-42 `test_db` fixture | L24-45（2行shift） | 無し |
| `test_appointment_api.py` L127-147 `test_04_double_booking` | L129-149（2行shift） | 無し |
| 「既存37件」という記述 | ★正本は39件★ | ★件数の記述を訂正要★ |
| 新規test仮番号`test_37`/`test_38`（旧版§3・追補1） | ★正本の実在testと番号衝突★ | ★`test_39`以降へ変更要★（実装工区での採番時） |

---

## §6 禁則遵守申告・断面

実行=`git fetch origin wp-a1-a3-3-20260723`（読取専用・無断可）・`git rev-parse`・`git log`・
`git show <ref>:<path>`（4file×2ref分）・`sha256sum`・`diff`・`grep -in idempotency`。
いずれも`/mnt/c/Projects/hakudokai-dev`にて read-only。checkout/pull/merge/patch適用/実走、
一切行っていない。取得したblob内容は`/tmp`のscratchpad配下に一時保存したのみ（repo外・当該session
専用領域、`hakudokai-dev`側には一切書き込んでいない）。

★未測（正直に書く）★= 正本4fileの内容は本工区で`Read`はしていない（`git show`出力を直接比較・
grep・diffで検分したのみ、行単位の全文目視読了はbooking_validator.py・test_appointment_api.pyの
差分箇所のみに限定。appointments.py・appointment_service.pyは完全一致確認をdiffの0件出力に
依拠しており、当職が正本の全行を人力で読み直した訳ではない——diffツールの出力を根拠とする段の
限界として申告する）。

断面: 2026-08-06T13:52頃（本file自身の行数・sha256は自己参照を避け本文に埋め込まず、提出便に記す）。
`multi-agent-shogun`側HEAD=`ed7daeb2cf6cb9ef6de72c424f2233c14506a3c1`（前工区から不変・本工区で
commitしていない）。`hakudokai-dev`側 正本pin=`78573ba79221fb195a1fc026f304812949836c0a`
（`origin/wp-a1-a3-3-20260723`、2026-08-04T08:18:20+0900・現tip=`feb945cf`だが§1実測で当設計対象
4fileには差分無し）。local `/mnt/c`断面=`dfa3ac77341e5947c967c745cf8fa597ba494a2e`（2026-07-19、
参考値として残すのみ・以後の判断根拠には用いない）。

提出先: 家老second＋軍師second（追補1に続けて読まれたし。旧版・追補1の行番号引用は§5の対応表で
正本へ読み替え可能——旧版・追補1自体は書き換えていない）。
