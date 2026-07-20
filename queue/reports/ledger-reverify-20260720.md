# 台帳大掃除 個別再検証+裁定パッケージ v1 (seq131201実行)

- 発令: seq131201(委員長、相談役検分CONDITIONAL=seq131158の実行指示)。Commander再着火令(委員長令hs_56eefe2e)経由で2026-07-20処理再開。work_started=seq131308(ETA 21:30)。
- 拘束遵守: **一括UPDATE禁・台帳UPDATE/DELETE/schema変更は一切実行していない**。本書は再検証+パッケージ作成のみ。全項目にpre-apply再照合証拠(live SELECT/実git/実ls+取得時刻)を付す。
- live snapshot: task_tracker 247行+design_decisions 190行を2026-07-20 19:44 JSTにSELECT(scratchpad ledger_reverify_snapshot.json)。以下「live」は全て本snapshot+個別追照合。
- 相談役への応答分類: [accept-repair]=指摘受入れ+是正 / [missing-evidence]=証拠提示依頼 / [proof-objection]=反証(証拠付)。
- 注: Hermes詳細report(docs/audits/hermes-ledger-cleanup-classification-audit-seq131122-20260720.md sha256=9e20532e…)はmain_pc到達可能な全repo(hakudokai-dev/DentalBI/multi-agent-shogun 各origin全branch)+project_documentsに不在。本書はseq131201本文の反証抜粋に対して応答した。追加条件が詳細reportにある場合はrelayを依頼する。
- 記録者: 将軍main(shogun-main:0.0)2026-07-20

## §1 ①個別再検証9件の確定

### #3 DD-134族(ebfe81f9+19f0fec8/4d0bf797/908d924a) — 分類C維持・根拠差し替え [accept-repair]
- 相談役反証「origin/mainにekarte-v3実在で前提不成立」= **正しい**。git実測(DentalBI origin/main, 2026-07-20): `frontend/src/features/ekarte-v3/` 含む28ファイル現存。分類表の「ekarte-v3は現行コードベースに不在」記載は**誤りとして撤回**する。
- 是正後の根拠: (i)カルテ正史=V6 EkarteV6Layout(正本DD b0401126)でありDD-134はekarte-v3前提のまま2026-04-27以降15週停滞(live: ebfe81f9=abandoned/S13収束済, designing3件=04-25更新のまま副医院長承認待ち・当該承認プロセスは体制改編で消滅) (ii)後継レーン無し。→ タスク行のC(廃止)分類は維持。
- 派生論点(新規): ekarte-v3コード実体28ファイルの残置/削除は本裁定と別件。V6レーン(4037ec1f/a38a3564)側での扱い確認を§2-補に提案。

### #5 06-20 desktop自動化族 — 一括C撤回→個別確定 [accept-repair]
- 相談役反証(seq67719/67905)を実読(2026-07-20): Hermes監査verdict=「urgent経路fire_pane統一済/通常high経路(dispatcher→safe_nudge)未統一/pane_enter_watcher LIVE=0」。
- 個別確定:
  - **7a36ffb6**(T-A本番反映独立検証)=**D**(検証タスクとして完遂。成果=上記verdict納品済、証跡=seq67719/67905実在+内容整合=強)。未統一gap(通常high経路)はwatcher恒久化レーン(957414e7/d73cc946)へ引き継ぎ註記。
  - **e566b6db**(DB制約横展開監査)=**C維持**(個別根拠: 三重ロック真因把握済の行内記録後15週停滞・監査対象の旧listener体制は凍結済。証跡=中・単線と明示)。
  - **e841db83/5ff0d3b9**=C候補だが行内に**理事長GO(「キルスイッチ→上り送信の順で実装」稼働順序指示)が実在** → 廃止には理事長の失効宣言が必要。**§2理事長GOパッケージへ移管**(追加2件)。
  - **poke4件(fd10db2d/fc419890/3e4046cf/ed5b6137)**=**裁定不要が判明**: live実測で4件とも2026-07-11にabandoned(superseded)処理済・行内に委員長GO seq119092【3】記録。#1/#5の裁定対象から除外(既決)。

### #6 B-dash族5件 — C維持(個別再確認済) 
- live: 47ea1b8a/946150af/bdc3cfea/8b47a342=not_started(04-27〜04-29更新のまま)、1cfc6da3=not_started(副医院長Q6待ち・当該Q6プロセスは体制改編で消滅)。前提チェーン(B''-1→2→3→4)の起点未着手のまま15週。
- 混同防止(補足版#6注記の実物確認): Stop Hook実装は**別資産として実在**=`multi-agent-shogun/scripts/stop_hook_inbox.sh`+`tests/unit/test_stop_hook.bats`(実ls 2026-07-20)。廃止対象は構想タスク行のみでフック実装に触れない。
- 証跡強度=中(停滞+現行watcher/dispatcher代替の単線)のまま — 相談役の重点検分対象類型(c)として反証歓迎を維持。

### #8 レセコン凍結族 — 部分是正 [accept-repair]
- Quartetto Stage2-5(ff259f8e/ad3eaf92/d27af58d/2a04506b)=blocked live確認、**C(凍結棚)維持**。DD-149=pending live、凍結維持。
- **DD-186=既にactive(live: status=active, codex🟢passed, 07-20 14:15更新)** → 分類表の「pending・A(凍結注意)」は陳腐化=**対象から除外(既決)**。
- 58d2e2ad=in_progress(macレーンstopped)→凍結棚維持。
- **fd5a9958=D候補(green待ち)へ再分類**(行内: mac実装完了・#999→#6b7280 AA 4.83:1・tsc0/vitest22pass・patch回収済。残=二重監査)。
- **29ef43cb=分類A撤回→D(クローズ済)**: 行内に**Commanderクローズ裁定2026-07-12(再現なし・仕様意図)**実在。residual note(SheetKarteLedger L102 loading固着=非blocking)は改善backlogへ。
- bdbcf340=#10で扱う(重複排除)。

### #9 D確定7件 pre-apply再照合 — 相談役反証どおり混在を確認 [accept-repair]
| id | live status(19:44) | 再照合結果 |
|---|---|---|
| 4e54f890 | **completed(07-13)** | **既にcompleted**(GREEN-TRUTH green確定・委員長裁定hs_0cbc524c行内記録)→反映不要(no-op) |
| f9fbf06d | in_progress | 行内「1→0件修復完了(**working tree差分・未commit**)」→completed化**不可**。残=commit/push+green。**A(残作業あり)へ格下げ** |
| 6e7b46ec | blocked | D維持(blocker欄自認=DD-127 Phase Dで再実装済)。completed化はFKI-AUDIT-GREEN-TRUTH証跡規程裁定と連動(行内明記どおり) |
| 29236fb2 | blocked | D維持。ただし証跡は外部系統のみ(f46d46a9根治=相談役PASS seq129664+PR#53)で行内自体に完了記録なし、と明示 |
| 75d04ac1 | in_progress | 行内「PR#41 merge済(73b65143)・**軍師green待ちのみ**」→**D確定→D候補(green待ち)へ移動** |
| 64ed6037 | in_progress | 行内=案B確定止まり(06-20以降更新なし)。運用定着の確証なし→**D候補(条件=案B経路の実施実例1件提示)へ格下げ**(相談役「設計70%」該当と推定) |
| f46d46a9 | reviewing | 行内「相談役4往復PASS+PR#53 merge+全PC周知・**軍師green待ちのみ**」→**D候補(green待ち)へ移動** |
- **再照合後の即反映可=6e7b46ec/29236fb2の2件のみ**(前者はGREEN-TRUTH規程裁定に従属)。「D確定7件一括completed化」の当初提案は**撤回**。

### #10 D候補9件 — 既completed 2件検出 [accept-repair]
- **ac046435=completed(07-13)** / **aa437254=completed(本日07-20 11:29, GREEN-TRUTH green確定 hs_0bd2d8e6+gunshi再検証PASS)** → 対象から除外(既決)。
- **ef9b4540**: 確保自体は済(11本+SHA256+理事長承認=行内)。ただし06-04指定の後続(PNG化→`tests/visual/baseline/handover_*`配置)は**DentalBI origin/mainに不在(git実測0件)** → **A(残作業=baseline配置)へ格下げ**、または「物理確保」(完了)と「baseline配置」(未了)の行分割を提案。
- green待ちD候補の確定リスト(verdict一括回収バッチ対象)=**8件**: 55f99184/529c52af/947eb280/f83dedaa/7f98a1fa/bdbcf340/75d04ac1/f46d46a9(全件live再確認済・各行に監査提出先/報告sha記録あり)。回収後にのみcompleted化。

### #13 DD-167/168 — C維持(変更なし)
- live: DD-167=pending+codex🟡failed(07-10)、DD-168=pending。是正なしで放置状態を再確認。廃止/縮小再設計の択一は委員長裁定(§3)へ。証跡=中(単線)のまま。

### #14 統治正本21件final化 — 監査要件記載を是正 [accept-repair+missing-evidence]
- **是正1(出典誤記の撤回)**: 分類表のGemini廃止出典「正本85b541b5§8」は**誤り**。live実測: 85b541b5(委員長/副委員長切り分け規律v1.0)の§8=上りメッセージ表記規則でありGemini言及ゼロ。**正=seq110495委員長裁定(2026-07-08 09:33、理事長指摘による裁定修正)**: 「audit_gemini.sh=decommissioned(廃止確定)/以後の二重監査標準=Codex(軍師)+Hermes(相談役)/過去DD・指示書のCodex+GeminiはGemini部分をHermes読み替え・個別裁定不要/例外=研修部長gemini-3.5-flash別系統」— 全文再取得済(2026-07-20)。
- **是正2(監査構成)**: 分類表の「Codex単独監査で順次final化」は**撤回**。標準はCodex+Hermes**二者**(seq110495)。main_pcのHermes leg断(4db5b9ac)は#17と連動。
- **相談役指摘との整合**: 「文書上のGemini監査必須と衝突」は、seq110495の読み替え条項が個別裁定不要で解消する建付け。ただし**同裁定が正本文書化されていない**gapは実在 → §2に「seq110495のDD化/正本反映」を先行条件として追加提案。
- [missing-evidence] 相談役引用の「AGENTS.md:333+audit-frameworkのGemini監査必須」: main_pc到達可能な全AGENTS.md(hakudokai-dev origin/master 541行版含む=L333は研修課長規律、Gemini言及はL298のGO境界のみ/origin/main 268行版=言及なし/DentalBI・multi-agent-shogun版=言及なし)で該当条項を確認できず。**該当file@commit:lineの提示を依頼**(受領次第、当該文書の読み替え/改訂をパッケージへ追補)。
- 21件のlive status再確認済(pending 8/provisional_active 13、変動なし。SPY-SENTINELの正式コード=DAISHOGUN-SPY-SENTINEL-20260702)。final化バッチ提案自体は維持。

### #16 Gemini前提族 — 根拠強化+個別是正 [accept-repair]
- **bff83c77**(audit_gemini.sh根治)=C維持、証跡**強**へ格上げ(seq110495に「audit_gemini.sh=decommissioned」明文)。
- **DD-174**: live=**provisional_active**(分類表のpending表記を訂正)→ 廃止はdemote手続き前提のC維持。
- **DD-154/155**(pending): seq110495読み替えで当面矛盾なし → 「廃止」単純化をやめ、**(a)新標準+source_code_cache体制で再定義 / (b)読み替え運用のままレーン完了時supersede** の2択で委員長へ(§3でなく§2に含めず、委員長判断事項として§3補記)。
- **DD-120**(pending)=C維持(管理者共通綱領v1.0=129721が上位互換)。

## §2 ②理事長GO用裁定パッケージ(6件+追加)

各1行: **現状→提案処分→根拠→リスク**

1. **#2 DD-138族+副院長保留4件**: 現状=旧体制残骸7行(live: 0b1585a4/c1dfeaec/409c606a=not_started、c0c7d72c/1a41b982/7ac7d0ba/3e7cc47d=blocked、04-05月更新のまま)→提案=一括廃止→根拠=29236fb2の実需はf46d46a9根治(相談役PASS seq129664+PR#53)で消化済・残行は旧Stage3a/claude.exe削除等の環境前提消滅→リスク=保留者(副院長)への失効確認を経ない廃止となる点のみ(反証余地は補足版#2どおり)。
2. **#4 DD-091族(eb645a15/95a4370b/92af0a72)**: 現状=04-19理事長保留のまま13週(live=blocked/not_started)→提案=失効宣言(再上程枝は凍結棚)→根拠=保留主体=理事長本人であり失効宣言は理事長専権・Stage1 DDL適用ニーズの再主張なし→リスク=将来DDL適用時に再起草コスト(小、設計文書は残置)。
3. **#7 3af99f58 no-show予測AI**: 現状=not_started構想のみ→提案=将来棚(製品roadmap)へ隔離(DD-184と同処遇)→根拠=着手実績ゼロ・自動化基盤前提消滅、ただし製品価値判断は理事長領分→リスク=棚移動は可逆・実質ゼロ。
4. **#11 DB整合性族DDL優先順位**: 現状=T10(424f36a9)/T11(7055f6b9)/T12(4b66c94e)+関連(b0cef740/dceed06e/bbcb5b27)がGO待ち、84f47aed=旧5区分DDL構想→提案=T10→T11→T12の順で**各段個別理事長GO**(一括GO不可)+84f47aed廃止+bbcb5b27(tooth_events調査)は読み取り専用のため先行可→根拠=T11はdraft+local verify済(seq115376)=最も準備が進捗・DDL適用はスキーマ不可逆→リスク=DDL実施はhigh(だからこそ各段GO設計を維持)。
5. **#17 4db5b9ac Hermes監査環境(main)**: 現状=Copilot unauthorized/gpt-4.1 unlicensed(2026-07-11当職実測)でDual Green第2leg欠→提案=環境部長へライセンス調達指示+当面はmain分をCodex(軍師)+相談役routing(hermes2経由)で代替→根拠=#14の標準構成(Codex+Hermes二者=seq110495)充足に必須→リスク=調達まで監査スループット低下(現状既に発生中)。
6. **#18 小粒4件**: 現状=bb31269c(スマホ承認=理事長「予定」発言のみ)/DD-187(Context7導入可否未判断)/DD-129(暫定領収書=DD-044完成までの暫定の要否)/9f30de06+a1506500(DD-061コンプラ2件=ZDR契約確認+問診AI同意文言、担当未指名)→提案=個別5分裁定(やる/やらない/担当指名)→根拠=全件行内記録のみで停滞・裁定コスト極小→リスク=DD-061 2件のみ予約フローA匿名遮断仕様に触れるため裁定時にDD-061本文参照要。
7. **【追加】e841db83+5ff0d3b9 失効宣言**(#5からの移管): 現状=06-20理事長GO(稼働順序指示)付きのままin_progress停滞15週→提案=GO失効宣言+C(廃止)→根拠=旧fukuincho_listener自動化体制は現行dispatcher+watcher凍結体制で代替済→リスク=キルスイッチ構想の実需が将来再燃時は新規起草(小)。
8. **【追加】seq110495裁定の正本文書化**(#14前提): 現状=Gemini廃止+Codex+Hermes標準+読み替え規則がhandshake裁定のみで文書正本未反映→提案=DD化(または監査正本へ追記)を#14 final化バッチの先頭に置く→根拠=相談役検分が「文書上のGemini監査必須との衝突」を指摘=文書側の未追随が実害化→リスク=なし(記録整備)。

### ④DD-179 親吸収mapping案(相談役条件: parent/child acceptance mapping固定)
- parent=**008df0d0(画像管理親レーン, live=in_progress, 指示書v1.3 is_current)** / child=**DD-179(pending)**+**6423cea3(blocked, B吸収)**。
- mapping(childの受入項目→parent側工程→受入証拠):
  | child項目 | parent側受け皿 | acceptance証拠 |
  |---|---|---|
  | DD-179【1】(a) 既存5テーブルRLS verify | 画像レーンP0基盤穴工程(指示書v1.3) | RLS verify結果report+sha |
  | DD-179【1】(b) Edge Function+4段階防御verify | 同上 | verify結果report+sha |
  | DD-179【1】(c) asset_usage_context population | 同上(D系禁則: population=空テーブル投入のみ可) | 投入行数+SELECT実測 |
  | DD-179【1】(d) Storage bucket 'assets' RLS整合 | 同上 | verify結果report+sha |
  | DD-179【2】DD-164専権2件(injection auth log/OAuth credential)配備 | **parentへ移さない**(理事長専権のため理事長直轄のまま) | 理事長配備指示の発出記録 |
  | 6423cea3残(003_asset_fk_hardening適用) | 同上P0基盤穴工程と同梱 | migration適用log+FK実在SELECT |
- close条件: 上記(a)-(d)+fk_hardeningのacceptance証拠が揃った時点でDD-179→superseded(先行DD or レーン完了DD)、6423cea3→completed。DD-164専権2件は独立残置。
- 註記: DD-179本文の監査mandate「Codex+Gemini(c04130e4)」はseq110495読み替えでCodex+Hermesとして執行。

## §3 ③委員長裁定可3件

1. **#1 abandoned正式廃止**: 対象は11件中**7件**(50949c50/c40b90f7/14f7bd36/7068dfa8/ebfe81f9/36bd5f11/d20f535c)— poke4件(fd10db2d/fc419890/3e4046cf/ed5b6137)は**07-11委員長GO seq119092で処理済(live行内記録)のため除外**。証拠=status=abandonedはDB実測値+各行に停止経緯記録。提案=正式廃止(archive扱い)承認。
2. **#12 O-2族(ba913f37/463cc151/0bc2cd14)**: 栓=fork実装(1c31ecc+232commits、当職git実測)の扱い質問**9cc171f9未回答**のみ(再督促seq121326済)。裁定B=566f8f99確定済。提案=委員長から回答の督促or回付(回答は不可逆作業を含まない)。
3. **#15 DD-189**: **no-op確認**=相談役実測どおり。live(2026-07-20 19:44): status=**provisional_active**+codex=**🟢/passed**(07-12更新)。当職07-14実測(全10プロセス8080-only)とも一致。単独の追加作業なし。正式final化は#14バッチと同時で足る。
- 補記: DD-154/155の処遇2択((a)再定義/(b)読み替え運用のままsupersede)は§1-#16のとおり委員長判断を仰ぐ。

## §4 手法・制約遵守
- 本工区でのDB書込=pc_handshake INSERT(報告)のみ。task_tracker/design_decisions/schemaへの書込ゼロ。
- 全live照合=2026-07-20 19:44 JST snapshot+個別追SELECT。git照合=DentalBI/hakudokai-dev/multi-agent-shogun各origin(2026-07-20 fetch済)。
- 適用フェーズ(裁定後)も「1項目ずつ+直前pre-apply再照合」の相談役条件に従う。
