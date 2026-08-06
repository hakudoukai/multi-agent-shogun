# Cycle2 段取り書 (書込GOが下りた刹那 走らせる形、足軽4号、2026-08-06・家老second下命 msg_20260806_104108_23f614aa)

## 境・限界・未測 (冒頭)

**設計のみ・段取り書のみ。本工区では何も走らせていない・apply していない・DB に触れていない・
`hakudokai-dev`・`newbuild` へ一字も書いていない。** 参照は `Read`/`sha256sum`/`wc -l`/`git rev-parse`/
`/usr/bin/grep -n`(単発・pipe未使用)のみ。

測時=2026-08-06T10:48:59+09:00 (`date -Iseconds`実測)。本repo HEAD=`a19cf01aa13a30389dd472deeba531c742e19db4`
(working tree は dirty だが対象参照4fileのいずれも変更行に出ておらぬ)。

**★冒頭で明かす動く前提★** = 本工区の起草中、依拠すべき F1 設計が**改訂版 (v2) へ差し替わった**
(足軽1号 msg_20260806_104810_17babd31、10:48:10 提出・測時直前)。下命が引いた旧 F1 (sha=23d5af10…)
は★消えておらぬが、§2・§3 の設計内容は v2 が実質置換している★ (足軽1号自身の申告どおり)。
本段取り書は★旧版でなく v2 を正本として組む★。かつ v2 は★本工区起筆時点で二者制監査 (軍師second+Gemini)
が未着手★ (`queue/reports/`・`queue/inbox/karo-second.yaml` を検索し PASS/FAIL いずれの記録も0件)。
∴ 本段取りの ⒜段2 は「v2 の監査が揃うこと」を明示ゲートとして持つ。

## 参照表 (path+sha+行数+一行要約・当職が己で測り直した値)

| 役割 | path | 行数/sha256 | 中身の一行要約 |
|---|---|---|---|
| F1 (旧版・保存のみ) | docs/incident_logs/2026-08-06_f1_4point_oracle_positive_control_design_a1.md | 161行 sha256=23d5af108ad6380e508d3023a079ab7e775839cbd0eeabb93d929fa3c069ccd7 | service層直呼び・同一payloadをkeyの代用にした旧設計。catchせず例外伝播でRED。★10:35:10裁定で覆された側★、消さず保存のみ |
| F1 v2 (現行候補・★未監査★) | docs/incident_logs/2026-08-06_f1_4point_oracle_positive_control_design_v2_a1.md | 230行 sha256=7327fe4bafc5f07c81edfb64a2c9fa4e72e3eea2b6238630f38c22c427ee61cd | API層(TestClient)・実Idempotency-Keyヘッダー2回渡し。②はresponse.status_code検分+`pytest.fail(f"...got {actual}")`で明示FAIL化。key無し負契約は既存`test_04_double_booking`(test_appointment_api.py L127-147)へ委譲・新規test不要と判断(Anti-Duplication) |
| F2 (★軍師PASS済・Gemini leg未確認★) | docs/incident_logs/2026-08-06_reserveimage_cycle2_f2_direct_regression_test_design_a2.md | 261行 sha256=3b0e8754ab10112e845ec2eae50516e306451e36c205609a8613ae9eee3c0fd6 | 現行patch自体(`apply_booking_concurrency_root`)の回帰test。dangling FK 1件を`appointment_history`へ仕込み、`PRAGMA foreign_keys=OFF`区間でtry内commitが確定した後にfk_checkが走る固定順序ゆえdeterministic REDと設計 |
| F3 (材のみ・裁定なし) | docs/incident_logs/2026-08-06_f3_compatibility_requirement_search_a5.md | 117行 sha256=c9c5cc784b8d19f6c821347c344245abe35deed3e73609e9a76155c161031d97 | 「key無しsilent replay」の独立先行要件は探索範囲で見つからず。既存コメント/新規testは本patch自身が書いた自己整合であり外部契約でないと明記。本部長暫定受入の材料 |
| 6path×受入matrix (当職自身) | docs/incident_logs/2026-08-06_reserveimage_cycle2_acceptance_matrix_a4.md | 80行 sha256=d994d90f7e596d06fbc015523e6f920b569a1e882f286c0353eb4c77368d4553 | F1=staff経路idempotency未配線(受入⑤⑥でstaff側0/5)・F2=SHA一致判定コード0件(受入③未強制)・F3=⑦(陽性対照RED維持)と同根gapとして記録した対応表 |

**裁定・裁の逐語 (本文書中に転記・要約せぬ理由=下命形式要件⒟)**:

- 本部長殿裁定 (10:35:10、家老second→shogun-second経由の転記、`queue/inbox/karo-second.yaml`
  message id=`msg_20260806_103624_567e846c`①節): 「F3=独立の先行要件は見つからず、暫定受入=key無し重複は409／同一key+同一payloadのみ同一成功結果へreplay」
  「F1 test は同一payloadを同一keyの代用にするな——実Idempotency-Key headerを2回渡せ」
  「旧staff APIはheader/key未配線∴2回目409でRED。target=200/201同等成功+same appointment_id+active=1+extra=0」
  「409をERROR放置するな——catchしpytest.fail(expected successful replay, got 409)へ明示FAIL化。catchしてGREENには絶対にするな」
  「key無し同一payloadのtestは別の負契約として409をassert」「書込GO後に将軍隊が実装・実走。本部長は書かない」。
- 将軍second見立て (同便③節・★仮説・裁定に非ず・別軸と明記して渡す★): 「catchの射程が広ければ409以外(500/422/接続断)も同じ文言で落ち、読む者が因を取り違える。実際のstatus codeを文言に埋めよ(`got {actual}`)。409以外は別の文言か再送出とし因を混ぜぬ」。
- 委員長裁定 (10:43:37、`queue/inbox/karo-second.yaml` message id=`msg_20260806_104337_cfe14b73`、type=grant_permission、宛先=将軍second経由・P0文脈で発出): 「pytest実行=可。錠は一つ=hakudokai-devのrepo/branchへ成果物を書き・commitする事のみが禁。`.pytest_cache`/`__pycache__`/test用DBは一時物であり正本を汚さぬ。/tmpの隔離worktreeの中は自由に使ってよい」。★本裁定はP0文脈で出されたが、本段取りではCycle2側の`/tmp/resimg-cycle2-impl-20260806`worktreeへも援用する——この援用の妥当性は当職の判断であり裁定ではない事を⒡2で明記する★。

## ⒜ 順 — 何から走らせるか、何が通らねば次へ進まぬか

| # | 段 | 内容 | 通らねば |
|---|---|---|---|
| 0 | 前提確認 (⒝) | 書込GOの一次出所確認 + patch適用sha自測 + 実行境界(委員長裁定)の再確認 | ★いずれか一つでも欠ければ待機継続★、以降の段へ進まぬ |
| 1 | F2 実行 | `/tmp/resimg-cycle2-impl-20260806`内でF2設計(dangling FK 1件仕込み→`apply_booking_concurrency_root`呼出)を実走 | F2は★既に軍師PASS済(Gemini leg未確認)★ゆえ設計自体の待ちは無いが、★二者制が揃うまでは「参考実行」に留め正式結果扱いにせぬ★事を明記。実行結果がRED(想定通り=欠陥実在の確認)なら次段へ。★GREEN(想定外)なら即abort・報告(⒞4)★ |
| 2 | F1v2 監査確認ゲート | 軍師second+Geminiの二者PASSが揃った事を確認 | ★揃わねば、F1・F3負契約(既存`test_04_double_booking`)いずれも実行せず、UNMEASUREDのまま段0-1の結果のみ先に報告★(P0側a6の「1箇所の失敗で他を止めぬ」原則の逆版=「1箇所の未着手が他を止めぬ」) |
| 3 | 実装レビュー (⒠の的中確認) | F1v2 §3②のコード(`resp2.status_code`検分+`pytest.fail(f"...got {resp2.status_code}")`)が★実際に`{actual}`を埋め込んでいる事★を実物バイトで確認 | ★409固定文言(埋込なし)になっていれば、将軍second見立ての穴がそのまま実装に残っている事になる∴実行前に差戻し・報告★ |
| 4 | F1v2 + 既存F3負契約 実行 | 段2-3が通った場合のみ、`/tmp/resimg-cycle2-impl-20260806`内で①`test_XX_idempotent_replay_with_key`(新規・F1v2 §3) ②`test_04_double_booking`(既存・F3負契約委譲先) の2testを実行 | ①②いずれかがERRORなら別掲(FAIL/PASSと混同せぬ)。①がGREEN(現行baseでも成功)なら想定外として即報告(header未配線という前提の実測結果と矛盾するため) |
| 5 | 集計 | 段1・段4の結果(+段2で止まった場合は段1のみ)を⒡の四値で集計 | — |

**段1(F2)を段2-4(F1v2+F3負契約)より★先★に置く理由** = F2の対象(`apply_booking_concurrency_root`、
P5=migration script)は、staff/web両経路のランタイムより★前段(スキーマ適用そのもの)★に位置する。
migration自体がfk_check失敗時に已にcommit済のまま止まる欠陥を持つ事は、患者6pathの下流(P1-P4/P6)
がどう動くかとは独立に確認できる事実であり、かつ★実apply判断に直結する安全情報★(是正されていない
欠陥がある事の確認)であるため、待たせる理由が無い段から先に走らせる。F1v2・F3負契約は
「idempotency-key軸のランタイム挙動」という★F2より一段上位の関心事★であり、かつ設計そのものが
本工区起筆時点でなお未監査(v2)ゆえ、揃うまで足止めするのは合理的である。

## ⒝ 前提 — 書込GOが現に下りた事・patchが現に当たった事を何で確かめるか

1. **書込GOの一次出所** = ★「本部長殿が可と申した」「委員長殿が可と申した」等、当隊内の伝聞・要約のみでは
   確認済としない★。`Cycle2 実走` の owner は一貫して★実user殿★と記録されており (`queue/inbox/karo-second.yaml`
   複数便で「owner=実user殿・書込GO」と反復記載、本工区起筆時点で最新の記録も同じ)、実行してよいか否かの
   一次出所は★実userの発言そのもの (message id・timestamp が specific に示せる形)★でなければならない。
   ★当職はこれを本工区で確認していない (未着のまま=本文書の起筆理由そのもの)★。段取り書起草は
   「GO不要」(下命冒頭の指摘どおり)だが、★実行段(⒜段1以降)はこの一次出所確認を欠いたまま進めてはならない★。
2. **patch適用の自測** = 期待shaを事前に断定しない(P0側a6の教訓を継承——適用ツールが挿入する空行等で
   byte単位のshaは揺れ得る)。代わりに`/tmp/resimg-cycle2-impl-20260806`側で
   `git rev-parse HEAD`を自測し、直前の読取工区群(足軽1号v2工区=`dfa3ac77341e5947c967c745cf8fa597ba494a2e`、
   足軽2号F2工区=`7d463edae84c704edabbd9da5465078dc62e55b1`)と★一致するか、あるいは書込GO後に
   新たなHEADへ進んだ事が明示されているか★を実行直前に測り直し、断面として記録する。
3. **実行境界の再確認 (委員長裁定の射程)** = `/tmp/resimg-cycle2-impl-20260806`内でのpytest実行
   (`.pytest_cache`/`__pycache__`/test DB生成を含む)は委員長裁定(10:43:37)により★可★。
   ★変わらぬ境界★= 当repo(`multi-agent-shogun`)・`hakudokai-dev`のrepo/branch本体・`newbuild`
   へは一字も書かぬ・commitせぬ(委員長が運ぶ)。稼働pidへ手出しせぬ。★worktree外への波及が
   一切無い事を実行前後で`git status --short`により確認する事を実行者の義務とする★。

## ⒞ 中止条件 — 何が起きたら止めて上げるか (重い順)

1. **書込GOの一次出所が実userの言葉まで遡れぬまま実行に踏み込みそうになった時** — 最重要。
   遡れぬ限り⒜段1以降へ進まぬ。伝聞を出所として実行を始めてはならぬ。
2. **patch適用sha自測が期待(直前工区群の測定値、または明示された新HEAD)と不一致の時** — 即STOP・報告。
3. **worktree外(当repo本体・`hakudokai-dev`のrepo/branch・`newbuild`・稼働pid)への波及の兆候が
   `git status --short`等で検出された時** — 即STOP。これは委員長のみが運ぶ領域であり当隊の権限外。
4. **F2実行がGREEN(想定外)で返った時** — 即STOP・報告。設計の前提(F2は必ずRED)が崩れた兆候として扱う。
   裁定はせぬ(「直った」のか「仕込みが効かなかった」のか判じるのは当隊の役目でない)。
5. **F1v2 §3②の実装が`{actual}`を埋め込まず409固定文言になっている事を段3で検めた時** — 実行前に
   差戻し・報告。将軍second見立ての穴がそのまま残った状態で走らせてはならぬ。
6. **二者制監査(軍師second+Gemini)のいずれかがF1v2へFAILを返した時** — その工区のみ差戻し、
   段1(F2)側の実行・報告は止めぬ(独立させる)。

## ⒟ 本部長裁定の織込み (逐語は上記参照表末尾に転記済・ここでは実装要件として再確認)

1. 同一payloadを同一keyの代用にするな→★F1v2は実Idempotency-Key headerを2回渡す設計へ改訂済(確認済)★。
2. 409をERROR放置するな・catchしてGREEN化するな→★F1v2はresponse.status_code検分+明示`pytest.fail`
   へ翻訳済。この翻訳(TestClientはHTTPExceptionを生例外として渡さぬ、という実測に基づく)が
   下命の字義とどう対応するかは⒜段3で実装バイトを検める★。
3. key無し同一payloadは別の負契約として409をassert→★F1v2は新規testを追加せず既存
   `test_04_double_booking`への委譲を選んだ(Anti-Duplication)。この判断の当否そのものは
   当隊の権限外であり、二者制監査(⒜段2)の結果に委ねる★。
4. 書込GO後に将軍隊が実装・実走、本部長は書かない→★本段取り書自体がその実走準備であり、
   本部長が書くべき領域(hakudokai-dev本体)には一切触れない★。

## ⒠ 将軍second見立て (仮説・別軸・実装要件への落とし込み)

将軍second自身が「本部長殿の御指図に反しない・別の軸」と明記した通り、当職もこれを裁定と
混ぜずに扱う。F1v2 §6は`{resp2.status_code}`を文言へ直接埋め込む形で対応済と自己申告しているが、
★当職はこの申告を段3で実物バイトを読んで確認する事をゲートに据えた(上記⒜段3)★。将軍second見立ての
核心=「catchの射程が広ければ因を取り違える」は、F1v2が採った「except節を持たず`status_code`を
直接検分する」形であれば、409以外の未知例外(F1v2 §4末尾の留保が明記する通り)はTestClient/ASGI層まで
生のまま伝播しERRORになる——★これはFAILと混同されずERRORとして正しく可視化される設計★であり、
将軍second懸念(誤った説明が沈黙より悪い)への一つの回答形になっている、と当職は読む(裁定はせぬ)。

## ⒡ この段取りが新たに開ける穴

1. **F2先行・F1v2後回しの順が「F1v2は後回しでよい/優先度が低い」と誤読され得る** — 対策として
   ⒜段2で「揃わねばUNMEASUREDのまま段0-1のみ先に報告」と明記したが、実行者が報告時にF1v2の状態を
   省略すれば「F2だけで完了」と読まれる危険が残る。報告時は★段2で止まった旨を必ず名指しで書く事★を
   実行者への要件として重ねて明記する。
2. **委員長裁定(pytest実行可)をP0文脈からCycle2文脈へ援用した事** — 裁定原文はP0側の質問
   (「その worktree内でのpytest実行も併せて可か」)に答えた形であり、対象repo/worktreeが異なる
   Cycle2側(`/tmp/resimg-cycle2-impl-20260806`)へそのまま適用してよいかは★当職の判断であり
   裁定そのものではない★。境界の文言(「hakudokai-devのrepo/branch」「/tmpの隔離worktree」)は
   worktree名を特定していない一般則として読めるため援用したが、実行前に家老second経由で
   この援用が正しいかの一言確認を得る事を推奨する(段取り自体はこの確認を待たずに用意しておく)。
3. **F1v2が「旧F1版に手を触れず別fileとする」形を採った事の副作用** — 参照表・下命双方が旧F1のsha
   (23d5af10…)を引いたまま流通し続けており、実行者が誤って旧版(service層直呼び・同一payload代用)
   の方を実行してしまう取り違えリスクが構造的に残る。対策として本段取りは⒜表・参照表いずれも
   ★v2のsha(7327fe4b…)を主・旧版shaを「保存のみ・実行対象でない」と明記する形★を採ったが、
   file名自体(`..._a1.md`と`..._v2_a1.md`)が似ておりコピペ事故の余地は残る。
4. **F2の二者制監査がGeminiレグ未確認のまま「軍師PASS済」を主要な根拠として段1を先行させた事** —
   当職の検索(`queue/reports/`・`queue/inbox/karo-second.yaml`の該当語grep)でGemini側の記録が
   見当たらなかった事を「無い」でなく「見当たらぬ」と書いたが、実行前にはこの確認を再度取る事を
   要件とする(見当たらぬまま実走に踏み込めば、下命の「二者PASS」要件を段1側でも満たさぬまま進める
   事になる)。
5. **本段取り書自体が未監査のまま「即応可能」として置かれる事** — 書込GOが実際に来た時、軍師second
   の監査がまだ終わっていなければ、未監査の段取りをそのまま実行してよいかが新たな問いとして生じる。
   当職は判断せず、上位の裁を仰ぐべき事項として明記するに留める(P0側a6の同型の留保をCycle2側でも
   踏襲)。

## 確かめた事・確かめておらぬ事

- 確かめた= F1が旧版から改訂版(v2)へ差し替わっている事(足軽1号自身の申告+file実在+sha実測)、
  F2が軍師second監査でPASS済である事(監査報告書 実測)、委員長がpytest実行を可とした裁定の
  逐語(実測)、書込GOのownerが一貫して実user殿と記録され続けている事(複数便の実測)。
- 確かめておらぬ= 書込GOが実際に下りたか否か(本工区起筆時点で未着のまま)、F1v2の二者制監査結果
  (本工区起筆時点で未着手)、F2のGeminiレグ監査の存在(検索範囲では見当たらず、不在の証明ではない)、
  F1v2 §3②実装が`{actual}`埋込を実際に維持しているか(本工区では設計文書の記述のみを確認し、
  実行時の実物バイト再確認は⒜段3として先送りとした)。

## 監査体制

暫定二者制 (軍師second + Gemini。監査モデル gpt-5.4 暫定)。Codex leg は SAFETY裁定 seq132707 により停止中。
「二者PASS」を「三者PASS」と書かない (委員長殿裁定)。

以上、Cycle2 GO刹那 走らせる段取り書。何も走らせていない・apply していない・DBに触れていない・
`hakudokai-dev`・`newbuild`へ一字も書いていない。提出先=家老second+軍師second。

---

## 追記 (家老second下命 msg_20260806_110149_8ac62267 対応・追記のみ・旧記述は消さず)

測時=2026-08-06T11:03:06+09:00。本repo HEAD=`a19cf01aa13a30389dd472deeba531c742e19db4`(不変)。

### 追記① F2節への註 — 足軽3号の反証(違反件数は必ず1件ではない)

足軽3号「F2設計(a2)反証役」(`docs/incident_logs/2026-08-06_reserveimage_cycle2_f2_design_adversarial_review_a3.md`、
195行、sha256=`aa49d0785043d0f02a0e0d89cdcba219ab6363d93f905e845c3cfb7357501084`)が、a2 §2-2手順4の
明記claim「仕込む dangling 行は悉皆1件のみ・`PRAGMA foreign_key_check`の返す違反件数を必ず1件に固定する」
へ反証を出した。核心=`appointments`テーブル自体が`unit_id INTEGER NOT NULL REFERENCES units(unit_id)`という
別のFKを持つが、a2 §2-2手順1の「schema構築」は`units`テーブルをスキーマとしては作るが**行を1件も
挿入していない**。この状態で手順2の`appointments(unit_id=1, ...)`をINSERTすれば`unit_id=1`が`units`に
存在せぬ参照となり、手順3で仕込む`appointment_history`側の1件と合わせて**実際は2件のFK違反**になる。
∴ ★上記⒜段1の「F2実行」で`PRAGMA foreign_key_check`の返す違反件数を検分する場合、期待値は
「1件」ではなく「2件」として扱う事★。ただし足軽3号自身が明記する通り、`apply_booking_concurrency_root`
が`RuntimeError`を送出するか否か(deterministic RED の核心)自体はこの誤りの影響を受けない
(293-295行の分岐は「0件なら何もしない・1件以上ならraise」であり、1件でも2件でも同じくraiseする)。
∴ 上記⒞4(F2実行がGREEN(想定外)で返った時は即STOP)の判定基準は不変のまま有効。
★変更点は「違反件数の期待値」のみであり、「REDになるか否か」の判定には影響しない事を明記する★。
本註は⒜段1・参照表F2行の**追記**であり、当職はこの一件を上記各所で書き換えていない。

### 追記② 問いへの回答(三値) — 書込GOの一次出所を「遡れた」と断ずる手順

**未だ手順に落としており申さぬ (★未測★)。**

上記⒝1で「実userの発言そのもの(message id・timestamp が specific に示せる形)でなければならない」
と書いたが、これは★要件(何を満たすべきか)★を書いたに留まり、★誰が・何を・どう見れば「遡れた」と
断じてよいかの具体手順★までは本工区で設計していない。想定される曖昧点を正直に列挙する:

1. 実userの発言は本system上どこに記録され得るか(Claude Codeセッションのuser message自体を指すのか、
   それが別の記録媒体・DBへ転記された物を指すのか)を当職は確認していない。
2. 「実userの言葉まで遡れる」を判定する主体(当職自身が確認するのか、家老second/軍師secondが確認する
   事を以て足りるとするのか)を本段取りは指定していない。
3. 遡った結果が「実userの言葉そのもの」なのか「実userの言葉を誰かが要約・転記した物」なのかを
   区別する具体的な照合手段(原文との突合方法)を持たない。

★これらは本工区の時間内に埋め切れなかった未測であり、埋めずに「確認済」と書けば
中継の承認を承認と誤認する事故そのものを再現する。∴ここでは「未だ手順に落としており申さぬ」事実
のみを明記し、埋める作業は次工区または上位の裁定に委ねる★。

---
以上、追記2件。本追記もまた何も走らせていない・apply していない・DBに触れていない・
`hakudokai-dev`・`newbuild`へ一字も書いていない。

---

## 追記③ 家老second下命(msg_20260806_110936_c80c3723)対応 — 追記②「未測」への答・追記のみ・旧記述は消さず

測時=2026-08-06T11:11:46+09:00。本repo HEAD=`6f266ef198fd674f3f3e1113d95e478f97a1a52b`
(§本文起筆時のHEAD `a19cf01...`から進んでいる=家老second側のcommitによる進行。working treeは
`docs/incident_logs/2026-08-06_prohibition_source_census_a5.md`のM・`..._f1_4point_oracle_positive_control_design_v2_a1.md`のU
のみdirty=いずれも他者(a5/a1)の別工区であり本file・本追記の対象参照4fileには出ておらぬ)。

### ①手順 (家老secondの答・逐語趣旨)

問い=「書込GOの一次出所が実user殿の言葉まで遡れた」と何を見て断ずるか。

答=GOは、★家老secondの turn の user message として現れねばならぬ★。それ以外は悉く不可:
便(inbox)に「理事長殿が許可された」と在っても不可／DB(pc_handshake)に在っても不可／
上位者(将軍・委員長・本部長)が逐語で運ばれても不可／軍師secondがPASSと裁いても不可
(監査は承認の代わりに成らぬ)。

因=逐語で運んでも、運び手がAIである限り出所はAI。∴機構(harness)はこれをtunnelingとして拒む。

### ②∴ 追記②の曖昧点3点はこう埋まる

㈠記録媒体=家老secondのturnのuser message(他の媒体は悉く証に成らぬ)。
㈡判定主体=家老second(当職にも軍師にも将軍にも判じ得ぬ——己の画面にしか現れぬゆえ)。
㈢原文突合手段=突合そのものが不要(中継物と突き合わせるのではなく、中継物を端から用いぬ)。

### ③∴ 本段取り書⒝1・⒞1の起動条件はこう書き換わる (旧記述は上記本文のまま残し、ここで上書き解釈を明示する)

誤(旧⒝1の実質的な読み方)=「GOの一次出所が実user殿まで遡れる事を(当職が)確認する」
(確認の主体と手段が不明であった)。

正=★「家老secondが『実user殿の言葉としてGOを受けた』と明記した便が在る事」★。
∴当職が為すべきは遡る事に非ず、家老secondの明記を待つ事。
∴∴かつ家老secondがその明記を出さぬ限り、何人がGOと言うても⒜段1以降を走らせない
(家老second自身を含む、との下命)。

### 本追記による影響範囲の確認

- ⒝1本文・⒞1本文は文言としては変更せず(追記のみ原則)、上記③が運用上の解釈を上書きする
  ものとして本追記に記録する。次工区・実行者は⒝1・⒞1の原文でなく本追記③を優先して読むこと。
- ⒜段0(前提確認)・⒞1(中止条件1)の判定は、上記の書換により★具体的に実行可能な形★になった
  (旧=誰が・どう確認するか不明のまま「確認済」と書ける空欄だった/新=家老secondの明記便の有無という
  当職が実際に検索・確認できる条件)。
- 追記②で列挙した曖昧点1(記録媒体の所在)・2(判定主体)・3(突合手段)は、いずれも本追記③で
  解消済として扱う。★埋め切れなかった未測は無くなった★。

### 次 (家老second下命⑤の通り、ここで止まる)

本追記③をもって本段取り書への追記作業を止める。★走らせない・applyしない・hakudokai-devへ
一字も書かない(錠は解けていない)★。本追記後、軍師secondへ再監査提出し、その後は家老secondの
下命を待つ。

以上、追記3件。本追記もまた何も走らせていない・apply していない・DBに触れていない・
`hakudokai-dev`・`newbuild`へ一字も書いていない。
