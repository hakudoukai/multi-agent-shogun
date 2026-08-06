# dashboard.md「🚨要対応」× primary 突合（続・残21項目）— 足軽2号

下命=家老second msg_20260806_212252_8313748a（2026-08-06T21:22:52・未読のまま着手——禁則「readを立てるな」継続）。
前便=`docs/incident_logs/2026-08-06_dashboard_primary_secondary_crosscheck_a2.md`（要対応31項目中10項目=000/00A/00B/00D/00E/00F/00G/00H/00I/00J）を完了済。
本便=残り**21項目**（00C/00C-orig/00F-b/00K/00L/00M/00N/00x/00/1〜12）を★同じ器★（`/usr/bin/grep -r`・母集団=queue/tasks 13file全件＋queue/inbox 30file・`_dead_letter_second.yaml`は今回★明示除外リスト方式★で除いた——前便での自白を受けた家老second令③に従う）で続行。

測時（着手）=2026-08-06T21:23:49+09:00。git rev-parse HEAD=6777fc881e5c8954e7d6cbfcf56cd767676cd14a
（★前便測時のHEAD=70caeeeから進んでいる★=断面が延びた証。dashboard.mdのsha256先頭16=94a5db7f39d97129は前便と★同一★＝本便が対象とする要対応節の中身は変わっていない）。
読取のみ。書かず・消さず・read立てず。lane不触。是正は一切行っていない（前便同様、家老secondの役目に留保）。

## 器・範囲（前便と揃えた・変えていない）

- primary=`queue/tasks/*.yaml`（13 file）＋`queue/inbox/*.yaml`（31 file中`_dead_letter_second.yaml`を除いた30 file）。
- 除外方式=`ls queue/inbox/*.yaml | /usr/bin/grep -v "_dead_letter_second" > (safe list file)`で事前に file 一覧を作り、以後の`grep`は★globではなく安全 list 変数展開★で対象を指定（家老second令③「globを使う時は`--exclude`か明示listで除け」に順った）。
- 各項目、要約から1〜3語の検索語を選び`/usr/bin/grep -rl -E`で hit file を得た後、hit した file を`grep -n`で個別に開き★内容が dashboard の claim と実際に一致するか★を目視判定した（前便と同じ二段構え）。

## ⒜ 要対応（残21項目）→ primary

| 項 | 内容(要約) | 検索語 | 結果 |
|---|---|---|---|
| 00C | 足軽5号成果物61行の docs/ 収録・委員長殿裁定(uplink id 9ae5c6af) | `9ae5c6af`／`渡し先が できた` | ★裏付け零★＝0 hit |
| 00C-orig | 同上・裁定前の記述(足軽5号 hold) | `61行` | 表面上2 hit(ashigaru3/6)だが★実読の結果いずれも別内容★（reserveimage設計書の行数・commit 6b37ad8の行数）= ★裏付け零★(型③=文字列一致のみ・内容無関係) |
| 00F-b | 同じ箱(karo.yaml)に書く道(local直書き)と読む道(cross-PC bridge)が別・400エラー | `karo\.yaml`／`書く道` | ★裏付け有★＝`queue/inbox/karo.yaml`自体・`queue/tasks/ashigaru4.yaml`等で言及確認 |
| 00K | 滞留=file 36／便33「以上」 | `滞留`／`file 36`／`便 33` | 複数hitあるが実読の結果★claim(file36/便33の具体数字)と一致する記述は見つからず★=別件(a1の`_pending_notice`個別調査等)への言及=★裏付け零★ |
| 00L | dashboard.md自身がgit外(`git check-ignore -q`=0) | `dashboard\.md`+`git外/check-ignore` | ★裏付け有★＝`queue/inbox/honbucho.yaml`(L4,7,858,862,881等)に同一の`git check-ignore -q dashboard.md`実測と★同一の主張・同一の3件セット(A/B/C裁定・a7一打鍵・dashboard git外)★が記載 |
| 00M | 発令書式=数を書くなら「実行の刻に数え直し…」を同じ行に | `実行の刻に 数え直し` | ★裏付け有★＝ashigaru1〜6のtask/inbox計14 file・共通書式として広く伝播済(本工区の下命自体にも同文言が付されている) |
| 00N | 盤の数の欄=測時／器／範囲を必ず添えよ(将軍second令20:24) | `測時／器／範囲` | ★裏付け有★＝`queue/inbox/shogun-second.yaml`L496に「①令④履行＝★00N新設★」と明記(dashboardのnote欄と一致する原文) |
| 00x | watcher guard改善=is_no_auto_clear_agentがexplicit clear_commandも遮断(gunshi-second 100%飽和で/clear不能) | `is_no_auto_clear_agent`／`watcher guard` | 1 hit(`karo-second.yaml`L62)だが★実読の結果=karo-second自身の08-04 21:04 /clear事象の説明であり、gunshi-secondの事案とは★別件★(同じ関数名を指すが別incident)=型②(指す先はあるが中身が違う) |
| 00 | DentalBI merge/push方針=local 7commit ahead・非FF乖離 | `DentalBI`／`feat/lane1` | 2 hit(`karo.yaml`・`ashigaru8.yaml`)だが★実読の結果=DentalBIリポジトリのpath/アクセス手段の話であり、merge/push方針(非FF乖離)への言及ではない★=型②(同一プロダクト名を指すが別claim) |
| 1 | deploy本番反映blocker(GitHub default=master≠main・prod /api全断) | `Vercel`／`origin/main`／`origin/master`／`SPA fallback` | hitはあるが★実読=別文脈(base commit実測・証拠基準に関する規律)★=関連claimへの言及なし=★裏付け零★ |
| 2 | 設計裁定session=多ドメイン正本(SoT)確定(Q1-Q5等) | `SoT`／`Q1-Q5` | hitあるが★実読=別のSoT用法(新task acceptance_criteria・CeremonyOverlay API契約)★=同語だが別対象=型② |
| 3 | security=API.txt live鍵／R-G CSV export clinic_id認可ゼロ | `API\.txt`／`R-G CSV`／`clinic_id認可`／`live鍵`／`multi-tenant` | ★裏付け零★＝0 hit(全パターン) |
| 4 | human GO=R-B認証必須画面／B2 fix(冪等ALTER) | `R-B`／`B2`／`冪等ALTER` | hit(`ashigaru8.yaml`)は★「KB2:」という別の見出しへの部分一致★(false positive)=★裏付け零★ |
| 5 | send_reminders_batchが偽の送信済記録を作る(R-K) | `send_reminders_batch`／`reminder_service\.py`／`リマインダー` | ★裏付け零★＝0 hit(全パターン) |
| 6 | batch1三者ゲート更新(FUKUINCHO裁定456b002e) | `batch1`／`三者ゲート`／`gemini_exempted` | hit(`gunshi.yaml`)は★2026-07-08付step4_rebatch_cycle2という別batchの話★=型②(同語「三者ゲート」使うが対象batchが違う) |
| 7 | E-1 created_by三者ゲート通過(recall_patients.py) | `E-1 created_by`／`recall_patients\.py`／`created_by`／`X-Operator` | ★裏付け零★＝0 hit(全パターン) |
| 8 | DD-042 GREEN撤回(FUKUINCHO seq105493) | `DD-042`／`4f008d5`／`phantom` | hit(`maeda.yaml`)は★2026-05-08付の別事案(ashigaru7 phantom inbox nudge anomaly)★=型②(「phantom」という語のみ一致・DD-042とは無関係) |
| 9 | A lane(会計待ちゼロ)前提崩れ=quartetto_pdf_watcher配線GO要裁定 | `quartetto_pdf_watcher`／`watcher_service\.py` | hit(`gunshi.yaml`)は★2026-07-08付step4_rebatch_cycle2のセキュリティ監査(symlink/traversal是正の検証)★=型②(同一fileを指すが「配線GO可否」という本件claimとは別論点) |
| 10 | QUARTETTO三方向統合phantom(consumer 0件) | `QUARTETTO`／`output_for_patient_app`／`daily_summary`／`三方向` | ★裏付け零★＝0 hit(全パターン) |
| 11 | T15=UNVERIFIED/NOT GREEN確定(clinics.specialty_mode列不存在) | `T15`／`specialty_mode`／`DD-115` | 表面上5 hitだが★全て`T15:xx:xx`という時刻表記の部分一致(false positive)★＝除去後★裏付け零★ |
| 12 | SEC-001/SEC-002未認証クロステナントPII露出(appointment_form.py) | `SEC-001`／`SEC-002`／`appointment_form\.py`／`patient-search`／`クロステナント`／`PII` | hit多数(ashigaru1〜8 task file)は★全て共通禁則文「患者PII・credential不触」という定型句への一致(false positive)★＝除去後★裏付け零★ |

### ⒜ 集計（今回21項目・実行の刻に数え直し済）

- ★裏付け有★＝**4件**（00F-b／00L／00M／00N）
- ★裏付け零★（検索語ヒットが無い、または hit を実読の結果 false positive と判明したもの）＝**11件**（00C／00C-orig／00K／1／3／4／5／7／10／11／12）
- ★型②（同一語・同一fileは在るが claim の中身が別）★＝**6件**（00x／00／2／6／8／9）
- 合計＝4＋11＋6＝**21**（母集団と一致・数え直し済）。

（00C-orig／00K／4／11／12は当初の広域grep段階では非0 hit に見えたが、実読の結果すべて false positive と判明し「零」へ算入した。false positive の中身は上表各行に記載済。）

## ⒝ primary → 要対応（再確認・新規markerの有無）

前便で発見した構造化マーカーは2種=①`queue/tasks/*.yaml`の`status: blocked`フィールド（全13file）②`queue/tasks/karo-second.yaml`の`awaiting_ruling:`リスト（5件）。
今回、他の構造化キー（`blocked_reason:`／`awaiting_ruling:`／`pending_decision:`／`human_GO_required:`）で primary全体（43file）を再検索した結果、★新規のヒットは無し★（前便で発見した2 file=`karo-second.yaml`・`rh_blocked_note_20260706.yaml`のみ）。
∴ ⒝の結果は前便から★変わらず★＝3件が要対応節に無し(R-H／B案peer経路／二重watcher B-87)・1件判定不能(W201)。

## ⒞ 向きを分けた数（意味が逆ゆえ合算しない・累計）

- ⒜（要対応にあるがprimary裏付け零）＝前便3件(00D/00F/00I)＋本便11件＝**累計14件**（要対応31項目中、検索済31項目全件に対して）
- ⒜のうち型②（同語・同fileはあるがclaim内容が別）＝本便6件（前便では型②の分類を用いていない・今回新設した第三の判定区分。前便の「裏付け有」判定の中に型②相当が紛れていないかは★再検証していない★=未確認のまま残す）
- ⒝（primaryにblocked/awaiting_rulingがあるが要対応節に無い）＝**3件**（前便から変わらず）
- 両者は別母集団ゆえ合算しない（前便と同じ規律）。

## ⒟ 己の手で為した事

- `ls queue/inbox/*.yaml | /usr/bin/grep -v "_dead_letter_second"`でsafe listを作成(30file)・`ls queue/tasks/*.yaml`で13fileを確認・以後の全grepをこのlist変数展開で実行(globを直接渡していない)。
- 21項目それぞれについて1〜6語の検索パターンで`/usr/bin/grep -rl -E`を実行、hitしたfileを`/usr/bin/grep -n`で個別に開いて文脈を目視確認した（false positive 8件を実読で検出=00C-orig/00K/1/4/6/8/9/11/12の一部）。
- `date -Iseconds`・`git rev-parse HEAD`・`sha256sum dashboard.md`で断面を再固定(HEADが前便から進んでいるがdashboard.md sha256は不変=対象は変わっていない事を確認)。
- ⒝方向の再検索(構造化キー4種)を43file全件に対して実行、新規markerが無いことを確認。

## 未確認の範囲（判らぬまま残す）

- ⒜の「型②」判定と「裏付け有」判定の境界は当職の目視判断であり、機械的な基準ではない。他者が同じ検索語で追試すれば異なる判定になり得る（★これは弱さとして明記する★）。
- 自由文（構造化フィールドでない通常のメッセージ本文）からの「blocked/待ち」相当の網羅的抽出は、今回も実施していない（前便と同じ限界）。
- 型②に分類した6件について、「本当に primary に裏付けが無い」のか「当職が探した語が悪く、正しい語なら見つかる」のかは★区別できていない★。次に読む者が別の検索語で追試されたし。

以上（母集団=要対応節31項目全件検索完了・primary=queue/tasks 13file全件・queue/inbox 30file(_dead_letter_second.yaml除く)）。新規判定は行ったが是正は行っていない。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。
