# 裏付け零11件のうち primary未転記の旧項 — 写せる形への整理・足軽2号

下命=家老second msg_20260806_213402_3beacb04（2026-08-06T21:34:02）。
端緒=`queue/tasks/karo-second.yaml`の`human_go_pending_20260806`に7件が既に転記済（`08271dd`収載後）。
残る対象=当職の「零11件」から★既に転記された00Kの3系統（dead_letter 3通12:11後／legacy 26,834+86／dead_letter_second parse不能）を除いた10件★
（00C／00C-orig／1／3／4／5／7／10／11／12）——家老second令の列挙と数え直しの結果、一致した。

測時=2026-08-06T21:37:15+09:00。git rev-parse HEAD=08271dd（前回commit・本便着手時点で新規commitなし）。
読取のみ・是正なし（写すは家老secondの役目）。己の箱の既読化のみflock/id明示で行う（他箱は不触）。

## ⒜ 各項一行（問い／権／生死）

| 項 | 問い（何を待っておるか） | 誰の権か | 今なお生きておるか |
|---|---|---|---|
| 00C | （★済★のため問いなし・下記⒝参照） | 委員長殿（裁定済） | ★済（✅裁定済 2026-08-05 10:5x とdashboard自身が明記）★ |
| 00C-orig | （★済★のため問いなし・00Cの裁定前記述） | — | ★済（00Cに吸収された旧記述・保存のみ）★ |
| 1 | GitHub default branch(master≠main)の裁定＋prod /api全断の infra修復要否 | 委員長殿／理事長殿（branch裁定・deploy GO） | `unconfirmed` — ★但し同項が前提とする「prod /api全断」は、`rh_blocked_note_20260706.yaml`のprior_noteで委員長殿が2026-08-03 read-only GET実測により否定済（401即応=サーバ稼働・認証壁が正常）。★同一の前提を共有する箇所ゆえ、本項も同様に陳腐化している疑いが強いが、branch裁定(master≠main)自体の生死は当職からは未確認★ |
| 3 | API.txt live鍵棚卸し実施可否／R-G CSV export clinic_id認可修正(Phase B該当)可否 | 理事長殿（明示GO） | `unconfirmed` |
| 4 | R-B認証必須画面のE2E認証情報提供可否／B2 fix(冪等ALTER)のD-lane設計裁定 | 理事長殿（human GO・D-lane） | `unconfirmed` |
| 5 | send_reminders_batch偽送信記録=findings-only据置か実送信実装(Phase B)へ進めるか | 理事長殿（Phase B GO） | `unconfirmed`（★患者影響大と明記・重大度は高いが生死は未確認★） |
| 7 | E-1個別はgate通過済(✅)だが、包含するbatch1のdeploy GOは依然凍結（branch/infra未解決） | 理事長殿／委員長殿 | `unconfirmed` — ★項目1と同根の待ち（deploy凍結）が残存。E-1自体は解決だがdeploy GOという上位の待ちは別物★ |
| 10 | QUARTETTO三方向統合phantom=consumer実装(患者アプリ/日計表leg)着手GO・canon案件裁定 | 理事長殿／副院長殿（canon案件・DD-042並列） | `unconfirmed` |
| 11 | （★済★のため問いなし・下記⒝参照） | FUKUINCHO／Commander（裁定済） | ★済（「T15=UNVERIFIED/NOT GREEN 確定」と明記・claim-vs-reachable乖離bounded・今後のGREEN主張規律を制定し全lane周知済＝決着している）★ |
| 12 | SEC-001/SEC-002未認証クロステナントPII露出の修復実施GO要否(Security Phase B凍結との関係) | 理事長殿（明記「理事長GO要否裁定要」） | `unconfirmed`（★最優先SEC・findings-onlyのまま★） |

## ⒝ 已に済んだ物（写すと生き返らせてしまう危険がある2件）

- **00C**＝dashboard自身が「✅裁定済(2026-08-05 10:5x・委員長殿)」と明記。hold自体は解かれていないが「渡し先ができた」状態で当職の権限外の後続(足軽5号本人の判断)に移っている。★human_go_pending へ生きた待ちとして転記すれば、済んだ裁定を未決に見せてしまう★。
- **11(T15)**＝「確定」「決着」の語が明記され、後続は規律周知のみ（新たな裁定を待っていない）。★同様に転記すれば決着済の話が未決に見える★。

## ⒞ `unconfirmed`（生死判ぜず・推して埋めず）

1／3／4／5／7／10／12 の7件は、当職の検索範囲内では★現況の生死を確認する一次情報に当たれなかった★ため、いずれも`unconfirmed`とした。7のみ関連情報（項目1と同根の可能性）を併記。

## ⒟ 型②6件（今回対象外・理由一行）

- **00x**＝karo-second.yaml L62のヒットはkaro-second自身の08-04 21:04 /clear事案の説明であり、dashboard 00xが指すgunshi-second saturation事案とは別incident＝★今回の「primaryに写す」対象たり得るか自体が別途要判定のため除外★
- **00**＝DentalBIのpath/アクセス手段に関する言及はあるが、merge/push方針(非FF乖離)というclaimへの直接言及は見つからず＝★型②のまま・写す先の是非は判じられぬため除外★
- **2**＝「SoT」の語は他タスクのacceptance_criteria等で汎用的に使われており、Q1-Q5正本確定という特定claimへの言及ではない＝★除外★
- **6**＝gunshi.yamlの「三者ゲート」言及は2026-07-08付step4_rebatch_cycle2という別batchの話＝★除外★
- **8**＝maeda.yamlの「phantom」は2026-05-08付の別事案(ashigaru7 phantom inbox nudge anomaly)＝★DD-042とは無関係・除外★
- **9**＝gunshi.yamlのquartetto_pdf_watcher.py言及は2026-07-08付step4_rebatch_cycle2のセキュリティ監査(symlink/traversal是正検証)であり、item10(consumer実装GO)とは別論点＝★除外★

## ⒠ 己の手で為した事

- `queue/tasks/karo-second.yaml`をReadツールで実読、`human_go_pending_20260806`の7件（`理事長殿_院長_待ち`3件＋`委員長殿_副委員長殿_筋`4件）を確認し、当職の「零11件」からこれに対応する00K系3系統を除外して10件に絞った。
- 00Cと11(T15)については、前便（`2026-08-06_dashboard_primary_secondary_crosscheck_a2.md`／`_part2.md`）で既に実読済のdashboard.md該当節本文を再確認し、「✅裁定済」「確定」の明示語の有無で済/生存を判定した。
- 1については`rh_blocked_note_20260706.yaml`のprior_note（前便で実読済）を想起し、「prod /api全断」という共有前提の陳腐化可能性を関連付けた（新規grepは行っていない・前便の実読結果の再利用）。
- 3/4/5/7/10/12については、当職の検索範囲（queue/tasks 13file・queue/inbox 30file）に一次情報が無いことを前便の網羅的検索結果（型②判定含む）から確認し、新規の追加検索は行っていない（前便で既に尽くしたと判断）。
- 是正（primaryへの転記）は一切行っていない。書込先は本票のみ。

以上（母集団=前便で確定した零11件から00K系除外後の10件、範囲=前便の検索結果の再利用＋dashboard.md該当節の再実読）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。
