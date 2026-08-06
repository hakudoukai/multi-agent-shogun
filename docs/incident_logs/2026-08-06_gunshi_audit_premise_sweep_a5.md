# 軍師second監査帳PASS前提未検め掃き (足軽5号)

## 境・未測・限界 (冒頭に置く)

読取のみ。file を一つも書き換えていない。軍師second を咎める形には書いていない
(下命の禁則どおり——本工区は人でなく機構を測る)。
実装零・patch零・test走らせず。/mnt/c配下(hakudokai-dev)へ一字も書いていない。

★最大の限界を先に書く★=本工区の母集団は延べ約700件 (下記㈠) に及ぶが、
本工区で実際に手読みしたのは ★6件のみ★ (既知2件の再検め+当職選定4件)。
残り約694件は ★UNMEASURED★ (未読)。数を出すに留め、欄は作っていない。

## 測時・断面

測時=2026-08-06T13:49:49+09:00。HEAD=9b23680971a971e31e29deaaee827a4a6c8d6e5b。

## 下命 (逐語の要点)

家老second msg_20260806_134438_8043d360 (13:44:38)。
「軍師second の監査帳を通しで一度掃き、PASSが前提を検めなんだ件を列挙せよ」。
既知2件を引き直して検め、かつ他を探せ、との下命。

## ㈠ 母集団 (測る前に列挙して貼れ・出力そのもの)

下命が指定した掃く先=最低三つ (queue/reports/gunshi_second_*.md・queue/reports/gunshi_report.yaml・
queue/inbox/karo-second.yaml+_archive/karo-second_pruned.yaml)。★階を分けて出す (測った階と言うておる階を揃えよ)★。

### A階=監査票file (queue/reports/gunshi_second_*.md)

```
$ find queue/reports -maxdepth 1 -name "gunshi_second_*.md" | wc -l
366
$ /usr/bin/grep -l "PASS" $(find queue/reports -maxdepth 1 -name "gunshi_second_*.md") | wc -l
346
```
366件 (全期間・全日付)、うち literal "PASS" を含む file=346件。20件はPASS不在
(FAIL/保留/他verdict、または未verdict文書)。

### B階=ledger (queue/reports/gunshi_report.yaml)

```
$ wc -l queue/reports/gunshi_report.yaml
46
$ /usr/bin/grep -c "PASS" queue/reports/gunshi_report.yaml
3
```
★件数と最大値は別の述語★=これは「PASSという文字列を含む行数」であり「監査件数」ではない
(1エントリが複数行に跨る/1行に複数PASSが乗る可能性は未検証)。階を混ぜぬ為そのまま報告する。

### C階=inbox便 (from: gunshi-second のメッセージ)

`queue/inbox/` は .gitignore 対象ゆえ `/usr/bin/grep -r` のみ用いた (git grep/包まれたgrep不使用)。
現行箱は single-doc YAML、archiveは multi-doc YAML (`safe_load_all`使用)。python3実行結果=

```
current_karo_second_total_msgs 38
current_gunshi_second_msgs 10
current_gunshi_second_msgs_PASS 10
archive_total_msgs 1906
archive_gunshi_second_msgs 284
archive_gunshi_second_msgs_PASS 247
COMBINED_gunshi_second_msgs 294
COMBINED_gunshi_second_msgs_PASS 257
```
(現行箱は往来中ゆえ測る度に増える。上記は13:49断面の値)。

### 母集団の総括

A=366 (PASS含346) + B=46行 (PASS含3行) + C=294通 (PASS含257通)。
★三階は互いに独立集計であり、単純合算すると同一監査が複数階に重複計上され得る
(例=file本文とそれを告げるinbox便は同一監査の異なる現れ)。合算値は出さない★。

## ㈡ 手読み方法と結果 (28→6件)

366件を全件手読みするのは本工区の時間内で不可能。★第一次選別 (未検証の機械的heuristic)★を
以下のとおり行い、その限界を明示した上で、選別後の一部のみ手読みした。

heuristic=「PASSを含み、かつ本文に'正本'/'実読'/'断面'/'母集団'/'行番号'/'実測'/'実物'の
いずれも含まぬfile」。A階366件中、この条件に該当=28件。

```
total 366 / no_pass 20 / has_marker(PASS+premise語) 318 / no_marker(PASSのみ) 28
```

28件中、本日 (20260806) 日付のfile=4件のみ。この4件を手読みした。加えて既知2件を
主典拠 (原document・karo-second.yaml該当行・commit) から再検めた。計6件。

★heuristic自体の欠陥を1件確認した (下記(2))★=キーワード不在は「前提未検め」の証にならぬ、
という当職自身の第一次選別への反証。

## ㈢ 一覧 (日時/対象/commit/監査の逐語/何が検められなんだか)

### 【既知1】2026-08-06 13:13:40／足軽1号 F1設計335行／commit 877f2444935ec4499a902a905df782343674991c

主典拠=`queue/reports/gunshi_second_f1_staff_idempotency_test_design_audit_20260806.md`
+ `docs/incident_logs/2026-08-06_f1_staff_idempotency_test_design_a1_addendum1.md`。
commit 877f244 を `git show --stat` で実在確認済 (13:14:29コミット、当該監査票の内容と一致)。

監査逐語 (原PASSのFindings 3)=「RED根の詰め方も良い。…A/BがA/Bが現状HEADに対し確定REDである
理由を『新規機能が無いから』で済ませず、具体code path不在へ落としておる」。

何が検められなんだか=旧版はA2/B2のRED根拠を`appointment_service.py`内`check_double_booking`と
書いたが、実際にダブルブッキングを検知する経路は別関数
(`validate_booking()`→`booking_validator._check_double_booking()`)であった。原PASSは
「REDと言う結論」の論理的整合は見たが、「その結論を導く機構名指しが実際のcode pathと一致するか」
という外の事実までは検めていなかった。誤りは足軽1号自身が addendum1 (commit 9de69e595f…、
13:30:48) で発見・自己申告。結論 (RED不変) は動かず、gunshi-secondも「Addendum Follow-up」で
PASS不変と裁いた。

判定=㈡無し (前提未検め、確認済)。

### 【既知2】2026-08-06 13:32:30／同 追補1 140行／commit 9de69e595fffabee1e6c7ba9465549b9dc60ec67

主典拠=`queue/inbox/karo-second.yaml` msg_20260806_133230_23492c01 (gunshi-second→karo-second)。
commit 9de69e5 を `git show --stat` で実在確認済 (13:30:48コミット、
「木の名+4file sha16+HEAD を追記 131行->140行」と一致)。

監査逐語=「足軽1号のF1 staff idempotency設計票 追補1木名明記版を再監査し、PASS不変と裁いた。
booking_validator.py行番号引用が/mnt/c/Projects/hakudokai-devの実読木に限ると明記されたのみで、
A/B RED・C既存委譲・D/E/F UNMEASUREDの四群整理は不変にござる。」

何が検められなんだか=足軽1号は「どの木を読んだか」を明記した (改善)。だが軍師secondのPASSは
「木を明記したか」だけを検め、「その木が正本か」は検めなかった。3秒前 (13:32:27)、
shogun-secondが独立実測で/mnt/c/Projects/hakudokai-devが正本branch (origin/wp-a1-a3-3-20260723)
とは別物 (feat/lane1-…、2026-07-19断面) であり、足軽1号自身がこの非正本木の行番号(348行)を
引用していたことを発見していた。gunshi-secondのPASS判定 (13:32:30) はこの発見の直後に出ており、
反映していなかった可能性が高い (時系列上、間に合わなかった可能性を排除できていない=判じ得ぬ)。
その後この論点は addendum2 (149行、正本commit `78573ba79221fb195a1fc026f304812949836c0a`へpin留め)
で解消され、gunshi-secondの「Addendum Follow-up 3」で改めてPASS不変と裁かれている
(同一票内での自己修復が確認できる)。

判定=㈡無し (前提未検め、確認済)。★自己修復済み★の付記あり。

### 【当職選定1】2026-08-05 02:41:06／足軽3号 CAP Rotated Owner Notice／
queue/reports/gunshi_second_cap_rotated_owner_notice_audit_20260805.md

逐語=「target_file: scripts/inbox_write.sh」「target_file_sha256: fd90c6aa…」と票冒頭に記すのみ。
本文Findings中に「着手前sha、探索コマンド、sandboxでの四形検証…まで揃えており」とあるが、
これは★提出者側の証跡が揃っていたと評した★文であり、軍師second自身がtarget_file_sha256を
独立に再計算して一致を確認したとは明記されていない。

判定=㈢判じ得ぬ (独立再計算の有無が本文から判別不能。UNMEASURED)。

### 【当職選定2】2026-08-05 03:01:32／足軽2号 Clear Ledger Inbox Drift Selfreport／
queue/reports/gunshi_second_clear_ledger_inbox_drift_selfreport_audit_20260805.md

逐語 (Findings 2)=「`queue/tasks/ashigaru2.yaml`は本日工区を一切動かしておらず、実際に動かしたのは
inbox本文であった、との核所見も逐語引用つきで閉じておる。単なる感想でなく、台帳本文とinbox本文の
二本を並べて示せておる」。

これは軍師secondが★台帳file (queue/tasks/ashigaru2.yaml) の実際の中身★という外の事実を
提出者の主張と突き合わせて検めた証跡であり、前提検めが★在った★事例である。

判定=㈠在り (前提を検めた事例)。★当職のheuristicの false negative★=キーワード('正本'等)を
含まぬのに実質は前提検めを行っていた。第一次選別は絶対の判定にならぬ事の実例として明記する。

### 【当職選定3】2026-08-06 09:29:43／足軽6号 Codex Guard Wiring Design v3／
queue/reports/gunshi_second_codex_guard_wiring_design_v3_audit_20260806.md

逐語 (Findings 2-3)=「`scripts/checks/codex_exec_sandbox_guard.sh:17`の既存`INTENDED_CWD…`を
正面から受け入れ」「足軽2号反証が指した`audit_meta_codex.sh`挿入位置も、v2の`L259`から`L260`へ
訂正済みにござる」。

行番号を精密に指摘・訂正しており、単なる書面上の整合検めを超えている印象は強いが、
「軍師second自身がこれらのfileをReadで開いて現物の行番号を確認した」と明記する一文は
見当たらない (足軽2号の反証内容を経由して評価した可能性も排除できない)。

判定=㈢判じ得ぬ (独立実読の明記なし。UNMEASURED)。

### 【当職選定4】2026-08-06 12:02:20／足軽3号 Gate Invocation Audit／
queue/reports/gunshi_second_gate_invocation_audit_audit_20260806.md

逐語 (Scope Note)=「本票は…実行実証そのものの有無をPASS/FAILの軸にせぬ」。

これは「前提を検め忘れた」のではなく、★対象の性質 (文面読解監査) 上、実行実証という種類の
外の事実は最初から範囲外と宣言している★設計上の除外である。下命の定義
(「後から誰かが外の事実を測ってPASS後に覆った/限定が付いた」)には現時点で該当しない
(覆り・限定の事実が今のところ無い)。

判定=該当せぬ (前提未検めの類型に非ず。宣言済scope除外)。

## ㈣ 三値まとめと分母

手読み6件の内訳 (分母=6、母集団366+46行+294通のうち):
- ㈡無し (前提未検め・確認済)=2件 (既知1・既知2)
- ㈠在り (前提を検めた事例・当職heuristicのfalse negative)=1件 (選定2)
- ㈢判じ得ぬ (独立検め有無が本文から判別不能)=2件 (選定1・選定3)
- 該当せぬ (宣言済scope除外・前提未検め類型でない)=1件 (選定4)

未読 (UNMEASURED)=A階366-6=360件 (うち今日日付のno-marker候補は残り24件)、
B階46行 (未着手)、C階294通中287通 (未着手)。

★本工区で新たに確定できた「既知2件を超える新規事例」=0件★。当職選定4件のうち
新規に「㈡無し・確認済」へ入る事例は見出せなかった。既知2件が今のところ唯一の確定事例。

## 【本工区で己が直した誤り】

無し (読取のみ・新規の判断のみ・書換なし)。但し★己が本工区内で立てたheuristicの限界を
本工区内で発見・自己申告した★ (選定2、上記㈡在り)。

## この工区が新たに開ける穴

1. heuristicによる28件選別は「キーワード不在」を根拠にしており、選定2で示した通り
   false negative が在る。逆に「キーワードは在るが実質は検めていない」false positive の
   可能性も未検証 (318件の has_marker 側を一件も手読みしていない)。
2. C階294通・B階46行はいずれも未着手。既知2件はいずれもA階+C階の組み合わせで見つかった
   ものであり、B階 (ledger) 単独からの発掘は本工区で一度も行っていない。
3. 「対象file同士の合算値」を意図的に出さなかった (階の重複計上を避ける為) が、これにより
   「延べ何件PASSが在るか」という単純な総数は本工区の成果物からは得られない。将軍secondが
   総数を欲する場合は別途、階を跨いだ重複排除の設計 (audited_target のpath正規化による
   突合等) が要る。

## 対に成る他工区

家老second msg_20260806_134438_8043d360 が示した既知2件の出所
(`docs/incident_logs/2026-08-06_f1_staff_idempotency_test_design_a1_addendum1.md` 第2節、
`queue/inbox/karo-second.yaml` msg_20260806_133230_23492c01) 自体。

## 監査体制

暫定二者制 (軍師second + Gemini)。Codex leg は禁令 (2026-07-21事案・SAFETY裁定 seq132707) により停止中。

## 各主張の「どう検め直すか」

- A/B/C階の母集団数=上記コマンドをそのまま再実行 (find|wc -l, /usr/bin/grep -c, python3 safe_load_all)。
- 既知2件のcommit実在=`git show --stat 877f244` `git show --stat 9de69e5`。
- 選定1-4の判定=各fileをReadし、Findings節で「独立実読/独立sha再計算」を明記する一文の有無を
  目視確認する。

## 禁則遵守の申告

軍師secondを咎める形には書いていない。欄は作っていない (数を出すに留めた)。
実装零・patch零・test走らせず。/mnt/c配下へ書込零。
