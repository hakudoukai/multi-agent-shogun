k1094 e5a28bc9 read-only 設計紙 v1（令=K1094_e5a28bc9_readonly_design_a3.txt・61行/3895B/sha16=f2d708a3de888578・二器一致）

■零 K1091 紙の始末（令■先づ 節、逐語遵守）
  scratch/ashigaru-third-3-3daed1f1/k1091_does_an_order_name_its_instrument_v1.md は★書き換へず其の儘殘した★。
  本紙は之と★別帳★（事業部長の帳＝e5a28bc9設計紙）である。K1091は當職(家老third)の帳に殘る。

■一 goal 逐語引用
  出處 = queue/goals/ashigaru-third-3.yaml（自席の經路・DBを經ず直讀）。
  開けた刻 = 2026-09-23T09:25:04+0900（`date '+%Y-%m-%dT%H:%M:%S%z'`実測）。
  逐語（outcome欄・改行はfile通りに保持）:
    ```
    outcome: "板 e5a28bc9: DD-PQ-HOLD-702: a2「dict」保持弾を読取設計へ切出し（現在の段: seq355662 reissue: ashigaru-third-3 receives bounded DD-213 a2 dict read-only design goal; output path to data_location; implementation/GO/accept/close=0.）／受入=受入条件は板の行（current_step）を正とする。産出は自席 worktree の commit sha（40桁）＋path で家老（不在なら事業部長）へ返し、判定は分野の軍師へ1件1回。"
    verify: "なし"
    constraints: "自席 worktree の枝のみ。同じ file を他席と同時に触らない（1担当=1境界）。歯式6file・design tokens・本番・secret に触れない。main へ push しない（代行 push は総監督）。"
    stop_when: "blocker4（root_cause/owner/next_safe_action/human_GO_required）を家老か事業部長へ上申した時、または総監督の STOP-AUTH のみ。"
    board_id: "e5a28bc9-633a-4eea-a578-2ddef6431c8c"
    ```
  ★家老third自身も 2026-09-23T09:20:35 便（msg_20260923_092035_bd5f8115）で「current_stepはgoal file自身に逐語で在る」「之が板の行の正本ゆゑpsql不要」と明示。∴■一の「己の經路」＝此のgoal fileであり、DBを開く必要は無い。
  乍し出處欄自身が引く「seq355662」は★board(task_tracker)の生行の識別子★であり、goal fileの逐語がboardの★写し★である事は明記されて居るが、写しが生行と一字一句一致する保証は當職の經路からは検められぬ（psql/DB禁ゆゑ）。之は■三⑶へ回す。

■二 「a2「dict」保持弾」の同定 ―― ★決め打たず、候補を證跡付きで列擧★
  （家老third 2026-09-23T09:20:35便「當職も確かめて居らぬ。決め打つな。候補をpath+行番號の證跡付きで列擧し各々「未確認」と記せ」に從ふ）

  探索法＝ashigaru-third-2 の scratch 樹 `scratch/ashigaru-third-2-fa06a3a1/*.md` を「dict」「辞書」「保持弾」の三語で全文grep（讀取のみ・書込0）。

  候補①（未確認・最有力）:
    出處 = scratch/ashigaru-third-2-fa06a3a1/k1060_db_to_yaml_bridge_v1.md:11（同紙=30行/4208B/sha16=8b12a2c34fa41a8c）。
    逐語: 「器Bの配り先=固定dict(L24-28逐語): ROLES={'reserveimage':'hermes-reserveimage.yaml','handoverdocs':'hermes-handoverdocs.yaml','bianalytics':'hermes-bianalytics.yaml'}。」
    指す実体 = /home/hakudoukai/hermes-departments/bin/dept_downlink_bridge.py の L24-28（`ROLES = {...}` 辞書リテラル、下記■三⑵で再掲）。
    有力とする根拠: ⑴「dict」の語がa2自身の紙に逐語で在り実在のPython dict object一つを名指して居る（AST内包の型名としての「Dict」ではなく、コード中の具体的なdict変数）。⑵ DD-213/downlink-bridge（本board系統の題材）と直接同一の橋の話である。⑶ 家老thirdのK1091令(下記候補③②の出處と同じ捜索範囲)でも他に「dict」+橋/経路文脈で一致する紙は見付からなんだ（下記候補②③参照）。
    ★未確認★＝之が事業部長の意図する「a2「dict」保持弾」其の物である事は、事業部長本人か家老third自身の逐語確認を經て居らぬ。

  候補②（未確認・弱・却下寄り）:
    出處 = scratch/ashigaru-third-2-fa06a3a1/jun346_naiho_no_kamae_wa_ikutsu_atta_ka_v1.md:3,6,8。
    逐語(:3): 「ListComp/SetComp/DictComp/GeneratorExp四型悉く食違0(実測5801/11/52/1638)。」
    逐語(:6): 「型別1個以上=List3155・Set11(★全数=絞り無し0★)・Dict12・Gen479。」
    逐語(:8): 「型別=List266・Set0・Dict7・Gen50。」
    却下理由: 「Dict」はPythonのAST内包表記の型名（DictComp=辞書内包）の集計項目であり、a2が「保持」する一個の実体的dictを指さぬ（内包表記の出現本数の集計題であり、DD-213/downlink-bridgeとは無関係の別題「巡346=内包の構へ」）。

  候補③（未確認・弱・却下寄り）:
    出處 = scratch/ashigaru-third-2-fa06a3a1/jun353_lambda_kazu_to_hikisuu_kazu_v1.md:8。
    逐語: 「他のCallへ渡す113件(callee別内訳: chk38/(其の他keyword『key』以外)13/xb10/grp8/cx2 8/grp7 7/cx4/cxj4/tally3/ne2/by2/argmax2/dist2/bnd2/blk2/grpj2/cnt2/defaultdict1/subn1)。」
    却下理由: 「defaultdict」はlambdaの引数として渡されたCallee名一覧の中の1件（延べ1件）に過ぎず、a2が設計上「保持」する構造物ではない。題も「lambda個数と引数個数」で無関係。

  參考(不採用・別語): scratch/ashigaru-third-2-fa06a3a1/jun318_py617_wa_itsu_ni_umareta_ka_v1.md:2 に「保持弾」の語自体は逐語で在る
    （「家老が保持弾"相異なる日三日以上"を条⑵で捨てた由」）が、之は日付差の判定条件の話であり★dictと無関係★（"保持弾"は本会話系で家老が発する令一般に指す語であり、"dict保持弾"という複合語では無い一般語法として使はれて居る）。

  ∴ 當職の探索範囲（a2 scratch樹の全md、dict/辞書/保持弾の三語）を尽くした限りに於いて、候補①が唯一「dictという実体」と「DD-213系統の題材」の両方を満たす。而して★決め打たず★、④の四點確認を要する。

■三 設計（非secretで爲し得る部分）―― 候補①を前提とした讀取設計（★未確認前提つき★）
  ⑴ 対象 = /home/hakudoukai/hermes-departments/bin/dept_downlink_bridge.py
     （140行/5897B、sha256=09f4b75a55a4042928240f1ffa246eb99d742476b8dda9630e4ac8e03862f932。
      二器一致: `sha256sum`実行時刻と`python3 hashlib`実行時刻の二回、同値。此のsha256はk1060紙(2026-09-22時点)の引用値と★一字一句一致★=k1060以降無変更と確認。）
     ★秘匿値は0件★＝本fileはSUPABASE_URL/SUPABASE_SERVICE_ROLE_KEYを`os.environ.get()`で讀むのみ(L36-40 `env()`関数)、値そのものはfile内に一切書かれて居らぬ(讀んで確認済・値は本紙へ一切轉記せず)。
  ⑵ ROLES辞書の構造（L24-28、逐語）:
     ```
     ROLES = {
         'reserveimage': 'hermes-reserveimage.yaml',
         'handoverdocs': 'hermes-handoverdocs.yaml',
         'bianalytics':  'hermes-bianalytics.yaml',
     }
     ```
     - 固定3key・値=固定filename文字列（`queue/inbox/`配下、INBOX定数(L18)と結合して使用、L78 `p = INBOX / fname`）。
     - key(role名)からtopic文字列を機械的に導出: L69/L72 `f'cross_pc_inbox_{role}'`（roleがそのままtopic接尾辞になる＝coreの命名規約）。
     - 使用箇所は1関数`main()`内のみ(L54-137)、L60 `for role, fname in ROLES.items():` の一箇所からループ参照。他に此のdictへの書込・再代入は本file全体を通じて0件（讀んで確認・grep該当なし）。
  ⑶ 拡張点の設計上の性質（構造から従ふ・d1）:
     - 新規roleを追加するには、本ROLES dictへ`key: filename`の一組を追加する以外の経路は無い（L60のループがdict.items()を機械的に走査する構造ゆゑ）。
     - filename値は★機械導出ではなく明示指定★（key文字列から自動生成される訳ではない）。∴役職追加時はfilenameを個別に指定する設計であり、命名規則の自動整合性は保証されない（設計上の注意点として指摘可能・非secret）。
     - `ashigaru-third-N`という文字列は本file全体でgrep該当0件（讀んで確認）。∴現行のROLES dictは3部長(reserveimage/handoverdocs/bianalytics)専用であり、ashigaru系役職の配り先を含む設計にはなって居らぬ（此の事実は本file単体の讀取のみで判定可能・db/secret不要・d1）。
  ⑷ 「切り出し」の設計案（非secretで書ける範囲）:
     board outcome の「読取設計へ切出し」を、本fileの静的構造の抽出＝「ROLES dictの仕様書化」（key/value/導出規則/使用箇所/拡張時の注意点を独立した設計note化）と解釈するならば、本■三の⑴〜⑶が其の切出し内容そのものである。
     ★之は候補①が正しいとの前提の上に立つ暫定設計であり、■四⑵の確認が済むまでは★正式な切出し成果としては用ゐぬ★（令■四禁「實裝するな」の精神を延長し、確定前の別解釈への差し替へ可能性を残す）。

■四 secret / DB / 確認 を要する部分（各々四點・★出來ぬの表明であり失點ではない★）

  項目A: task_tracker板 e5a28bc9 の current_step 生行をDBから直接検める事
    owner: karo-third または 事業部長（DB/psql権限を持つ者）
    root_cause: 當職(ashigaru-third-3)は標準ルールによりDB/psql/secret接續を一切禁じられて居り、board生行を読む承認済み経路(script/tool)を保有せぬ（scripts/内を捜索済・該当0件、dashboard-viewer.py以外に無し）。
    next_safe_action: 家老thirdまたは事業部長が current_step の生行を逐語で本席へ中継するか、非secretな読取専用の中継script（例=k1060の器Bのやうな非secret構造読取に限る物）を新設し當職へ権限委譲する。
    human_GO_required: 否（DB read-only中継はkaro-third/事業部長の権限内で完結し得ると見るが、新規権限付与そのものは委員長裁定が要るかもしれぬ＝要確認）。

  項目B: 「a2「dict」保持弾」の同定確定（■二の候補①〜③のいづれか、又は他か）
    owner: 事業部長（原命令者）並びに karo-third（並行確認中と自ら明示・09:20:35便）
    root_cause: 事業部長の指示文言「a2「dict」保持弾」に対応する一意の逐語文書が、當職の探索範囲(a2 scratch樹)に存在せぬ（最有力候補①はa2自身の紙が「dict」を名指すが、之が事業部長の指す物と一致するとの確認は無い）。
    next_safe_action: 事業部長またはkaro-thirdが候補①〜③のいづれか（又は当職未発見の第四の候補）を名指しで確定するか、board task_trackerのcurrent_step生行に候補を一意に特定できる逐語（file path等）が在ればそれを中継する。
    human_GO_required: 否（役職間の確認で完結し得る）。

■五 用ゐた母・器・樹（各數値行併記・二器一致は括弧内に明記）
  - K1094令: 61行/3895B/sha16=f2d708a3de888578（`wc -l`+`wc -c`+`sha256sum`の三器・家老third引用値と一致）。
  - goal file(queue/goals/ashigaru-third-3.yaml): 9行/1314B/sha256=67837a2585a7646cdf65fbb6f0b7330707bd589997ec146db223f797153f8653（`wc -l`+`wc -c`+`sha256sum`・當職自身の実測、開いた刻=2026-09-23T09:25:04+0900）。
  - dept_downlink_bridge.py: 140行/5897B/sha256=09f4b75a55a4042928240f1ffa246eb99d742476b8dda9630e4ac8e03862f932（`wc -l`+`sha256sum`(初回)+`python3 hashlib`(再測・二器一致)）。k1060紙引用値と一字一句一致（差分0）。
  - k1060紙(a2): 30行/4208B/sha16=8b12a2c34fa41a8c（`wc -l`+`wc -c`+`sha256sum`・當職の実測。a2自身の自測「30行/4208bytes」と一致）。
  - jun346紙(a2): 該当行=3,6,8のみ引用（全體の行數/bytesは本紙の論旨に不要ゆゑ未測・確かめて居らぬ）。
  - jun353紙(a2): 該当行=8のみ引用（同上・未測）。
  - jun318紙(a2): 該当行=2のみ引用（同上・未測）。
  - 樹＝全て讀取のみ、`git -C /home/hakudoukai/multi-agent-shogun`配下および`/home/hakudoukai/hermes-departments`配下（後者はrepo外の隣接ディレクトリ、書込は一切行はず）。

■六 遵守事項（■no-silent-failure・已に觸れた物の開示）
  - 已に讀んだ物: /home/hakudoukai/hermes-departments/bin/dept_downlink_bridge.py（全140行、値は非secret=env名のみで秘匿値は無し）、a2の scratch/*.md 複数（讀取のみ、書込0）、queue/goals/ashigaru-third-3.yaml（讀取のみ）、queue/inbox/ashigaru-third-3.yaml（自席の箱、read:trueへの更新のみ・本令とは別便の處理）。
  - env/DB/psql/secret/接續文字列＝一切開かず（`os.environ`呼出のコード上の存在は確認したが、値そのものは一度も参照・出力して居らぬ）。
  - board(task_tracker)への書込＝0件（運轉者専権と承知）。
  - commit/push/staging＝本紙作成時点では未実施（■七にて別途、自席worktreeへcommitのみ行ふ予定・pushはせぬ）。
  - K1091紙＝一切書き換へず（令■先づ節の指示通り）。
  - 令(K1094)本文に誤り・矛盾は見付からず（★誤り無し★と正直に記す。無理に瑕疵を探さず）。

■自測 = 106行/13757bytes（書き終へた後に數へた・`wc -l`+`wc -c`と`python3`のnewline計數、二器一致）
