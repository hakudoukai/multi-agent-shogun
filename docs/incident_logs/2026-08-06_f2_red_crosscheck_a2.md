# F2 RED 独立クロスチェック——足軽4号の実装が当職の§2設計と同じ物を測るか (足軽2号)

下命=家老second msg_20260806_144535_ec026c88 (2026-08-06T14:45:35・
先便 msg_20260806_143527_f18623d3(14:35:27)からの役替え)。
「作り手→検め手」への役替え。★読取のみ・worktree新設せず・実装せず・testを走らせず★
（本便もこの禁を守り、走らせていない）。

**冒頭・様式（下命の指示どおり）**: どちらが正かは書かぬ。㈠一致／㈡食い違い／㈢三値のみ。
裁は家老second殿ないし上へ上げる。足軽4号を咎める記述は含まぬ（同人は移管指示14:36:34より
★前★の14:32:56に実装しており、重複は刻の問題にすぎぬ）。

## §0 対象 (読取のみ・実行なし)

- 当職の設計: `docs/incident_logs/2026-08-06_reserveimage_cycle2_f2_direct_regression_test_design_a2.md`
  (commit `f5c2cc9`・軍師second PASS 10:39:46・261行)
- 足軽4号の実装: worktree `/tmp/resimg-verify4-cycle2-20260806`、
  `backend/tests/test_reserveimage_cycle2_regression_f1f2f3_a4.py`
  (commit `07b1fbea7e69277058fab2783f5862f35779b0a4`時点=349行・
  sha256=`a9a162c6f06cda645abfc2a7ae4a5dd89ece1358e6de9c5085efc435277622da`、
  ★当職が`git show 07b1fbea:<path>|wc -l`/`sha256sum`で独立再測し一致確認済★)。
  F2該当部=235-305行(`_seed_dangling_fk_for_negative_test_only`/`test_41`/`test_42`)。
  ★§6追補(14:39:23コミット・07b1fbea)はF1のみ対象(test_45/46/47)——`git diff a694ae9 07b1fbea`
  で確認済、F2該当行(235-305)は`a694ae9`時点から無変更★。
- 足軽4号の報告: `docs/incident_logs/2026-08-06_reserveimage_cycle2_f1f2f3_regression_net_a4.md`
  (git未追跡=`??`・現況185行)。
- 補助読取: `booking_concurrency_root.py`内`root_tables_present`定義
  (128-130行、当職grep実測=`{"booking_idempotency","appointment_slot_claims"}.issubset(names)`)。

## §1 ㈠ 一致する所

1. **仕込み手順の核**=`_seed_dangling_fk_for_negative_test_only`関数——★関数名まで一致★。
   `PRAGMA foreign_keys=OFF`→`appointment_history`へ`appointment_id=999`のINSERT、
   という手順が当職§2-2手順3・§6疑似コードと文字通り一致。
2. **『他testから再利用しない』命名意図の継承**=当職§4-3「用途を名前に刻み、他testからの
   流用を能動的に思い留まらせる命名とする事」を、同人はdocstring内で「§4-3を継承」と
   明記した上でそのまま採用。
3. **単一dangling行のみ**=当職§2-2手順4「他のFK参照table(`appointment_reminders`/
   `prediction_log`)へは行を入れない」——同人のtest_41/42いずれも`appointment_history`のみ。
4. **tmp_path専用**=当職§4-1「固定pathを一切使わない」——同人は`tmp_path / "f2.db"`
   (test_41)/`tmp_path / "f2b.db"`(test_42)、固定path無し。
5. **§4点2の予防線(pragma既定値依存の脆さ対策)**=「INSERT直前にPRAGMA foreign_keys=OFFを
   自testが打つ」——同人の実装も`_seed_...`内でINSERT直前にPRAGMA発行、順序一致。
6. **test_42の断定内容**=当職§6疑似コードのassert群(`_appointments_pre_root`消失・
   `appointment_slot_claims`存在・dangling==1)と、同人のtest_42のassert群が
   ★ほぼ逐語で一致★(`"_appointments_pre_root" not in tables`/`root_tables_present(conn)`/
   `dangling == 1`)。同人はこれを「documentary(GREEN)」と明記——当職の§6コメント
   「これはassert成立=欠陥が実在する事の記録であり、直った証拠ではない」と同じ位置づけ。
7. **担保の根拠**=当職§3(コード上の固定順序=commit(284,try内)→finally(289-291)→
   fk_check(293-295,try外)、並行性非依存)を、同人の§2-2も同一構造として引用・同意している
   (「§1のa2独立再算出と一致」と同人便に明記)。

## §2 ㈡ 食い違う所

1. **RED化を実現する主assert(test_41)は当職の設計に★存在しない★**。
   当職§6疑似コードの単一testは、assert群が「commit済のまま(=欠陥の実在)」を確認する形
   ——これは★現行(欠陥)codeの下でPASSする形★であり、単独では「RED」ではなく
   「documentary(欠陥実在の記録)」になる(同人の言う「documentary」と同じ位置づけ)。
   ∴ 当職の§4-4「本testは現行codeの欠陥を前提としたRED期待testである」という★地の文の
   記述★と、当職自身の§6疑似コードの★assertの極性★は、当職の便の中で★整合していなかった
   (当職の自己矛盾。同人の落度ではない)★。
   同人はこの間隙を埋めるため、当職の設計に無い★新規のassert★
   (`assert not root_tables_present(conn)`=「fk_check失敗時はroot tablesが存在してはならぬ」
   という★desired contract★)を持つ`test_41`を追加で書き、当職のassert群はそのまま
   `test_42`(documentary/GREEN)として温存した——★1つの設計を2つのtestへ分割した★形。
2. **schema構築の範囲**=当職§2-2手順1「`APPOINTMENT_TABLES`全体を空DBへ適用」に対し、
   同人のtest_41/42は`("units","appointments","appointment_history")`の★3 tableのみ★を
   `APPOINTMENT_TABLES`から名指しで抽出して適用(235-238行相当のfixture内)。同fileの
   他test(`_apply_all_appointment_tables`)は全件loopを行っているが、test_41/42はそちらを
   使わず個別3 tableに絞っている。
3. **`units`行の要否**=同人はappointments INSERT前に`units`テーブルへ1行(`unit_id=1`)を
   仕込んでいる。当職の設計(§2-2手順2)は`units`に一切言及していない
   (appointments.unit_idのFK先である可能性が高いが、当職はこの依存を書いていなかった)。
4. **appointments INSERT文の充足**=当職§6は「省略部分`...`は当職が今回列挙していない…
   既存fixtureヘルパを流用すれば省略できる可能性が高いが、当職はそのヘルパの中身を
   読み切っていない」と★未確定★のまま申し送った。同人は既存ヘルパを流用せず、
   独自に全カラム(`clinic_id,patient_id,unit_id,start_time,end_time,duration_minutes,
   status,source,created_by`)を明示したINSERT文を書いて解決している。
5. **DB接続の開き方**=当職§6は`_open_file_db(tmp_path / "f2_regression.db")`
   (既存fixtureヘルパの流用)を想定したが、同人は`sqlite3.connect(tmp_path / "f2.db")`を
   直接呼んでいる(ヘルパ不使用)。
6. **配置先**=当職§6は「配置先案: `backend/tests/test_booking_concurrency_root_migration.py`
   (患部patch内に既存・diff763行目〜)への新規class追加」を想定したが、同人は
   ★別の新規file★(`test_reserveimage_cycle2_regression_f1f2f3_a4.py`、F1/F3と同居)へ実装した。
   (★項13 detectorとの別枠は保たれている★=同人のfileはitem13の2 detectorとは別file。
   当職§5の「別枠」宣言そのものへの抵触ではない)。
7. **§4点4の申し送り(是正後の手動書換え要件)の継承有無**=当職§4は「直った時にこのtestが
   自動GREEN化する事の意味」として、是正後に★docstring/assert意味の手動書換えが要る事★を
   申し送り事項として明記したが、同人の便(§2-2/§5次報様式)には★この申し送りへの言及が
   見当たらない★(当職の読取範囲内。見落としの可能性は当職側にも残る)。

## §3 ㈢ 三値 (裁定に要る材料・当職からは断じない)

1. **UNMEASURED**: test_41の`assert not root_tables_present(conn)`という★desired contract★
   (fk_check失敗時はroot tablesが存在してはならぬ=完全rollbackが正)が、本部長裁定または
   他の正本にすでに明記された契約か、同人が今回独自に定めた物かは、当職未確認
   (当職の読取範囲=下命本文+当職§0記載の2 fileのみ。§6追補が引く裁定便
   `msg_20260806_143200_2de225e4`はF1のみを扱っており、F2のdesired contractの出所は
   ★別途確認が要る★)。
2. **待ち**: §2-1(RED実現方式の分岐)が「当職の設計の不備を同人が埋めた」のか「当職の
   設計とは別の裁定判断が新たに要る」のかは、当職からは裁定できぬ——上へ上げる。
3. **見得ぬ**: 当職はpytestを実行していない(下命の禁=「走らせるな」に従う)ため、
   test_41/42が★現時点で実際にFAILED/PASSEDのままか★は、同人の便に記された実測値
   (14:32:56時点のFAILED/PASSED)を★引用するのみ★であり、当職の独立実測ではない。
4. **引き直せぬ**: 当職§4-4とa2便自体の記述矛盾(上記§2-1)は、当職の便(f5c2cc9・
   軍師second PASS済)を今から書き換える事はできぬ(監査済sha確定済)。訂正するなら
   ★追補として別途出す★必要があると判ずる(本日の条「提出した物は審査終了まで己の物に非ず」
   に準じ、当職からは訂正の要否も含め判断を仰ぐに留める)。

## §4 対に成る他工区

- `docs/incident_logs/2026-08-06_reserveimage_cycle2_f2_direct_regression_test_design_a2.md`
  (当職・261行・commit f5c2cc9)——本件の設計出所。
- `docs/incident_logs/2026-08-06_reserveimage_cycle2_f1f2f3_regression_net_a4.md`
  (足軽4号・185行、git未追跡)——本件の実装出所。
- `docs/incident_logs/2026-08-06_f2_red_duplication_check_stop_a2.md`
  (当職・108行)——本工区の前段(worktree新設前の重複検知・停止報告)。

## §5 本工区で己が直した誤り

無し（新規実測=§0のsha/行数独立再確認・§1-2の逐語突合のみ。訂正すべき当職の落度は
§2-1で見出したが、それは★過去便(f5c2cc9)の内容★に関する物であり、本工区自体の誤りではない
——訂正の要否は上へ問う）。

## §6 禁則遵守の確認

読取のみ(git show/diff/grep -n)。worktree新設・実装・pytest実行のいずれも行っていない。
足軽4号の木への書込は一切なし。push/PR/main/本番/公開変更なし。

---
断面: 2026-08-06T14:48:58+0900 (`date -Iseconds`実測)。
本repo(multi-agent-shogun) HEAD参照時点=直前commit `555baae`系列(本便は未commit・提出用)。
対象worktree(`/tmp/resimg-verify4-cycle2-20260806`)側参照=commit `07b1fbea7e69277058fab2783f5862f35779b0a4`
(読取時点)。
提出先: 家老second + 軍師second(監査義務)。
