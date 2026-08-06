# P0三種テスト実走結果への追補 — 各段のGREEN/FAIL定義(測る前に定義済であった事の明示) (足軽6号)

## 境・限界・未測 (冒頭)

対象=`docs/incident_logs/2026-08-06_p0_three_test_execution_result_a6.md`(161行 sha256=0ee65c918cc060118eff341fc94e130661f157067ac566eb9fbb4b7c4010a50c)への追補。
本追補自体は新規実行を伴わず、既に段取り書(`2026-08-06_p0_three_test_runbook_a6.md`、151行
sha256=7abead49882cb04735c7db4078bf102be7edf1461400e6fe1dbd196be245f189)⒜表に★実行前に★定義済で
あった各段のGREEN/FAIL基準を再掲するのみ。

測時=2026-08-06T12:38:42+09:00(date -Iseconds実行結果)。git rev-parse HEAD=f694438e78ac2e5c5007a9d510544938581e71da。

## 各段のGREEN/FAIL定義 (段取り書⒜より再掲・実行前に既に定義済であった事の証)

| 段 | GREEN(何を見た時か。rc=0ではない) | FAIL(何を見たら根治しておらぬと断ずるか) |
|---|---|---|
| 段1構文gate | `bash -n`と`py_compile`の両方がexit 0。★但しこれ自体は根治の証にならぬ(bash -nは埋込Pythonを見ぬ、家老second/将軍second指摘の通り)。構文gateのGREENは「実行に進んでよい」の意のみ★ | いずれかがexit非0 |
| 段3陽性対照(old・実物) | ★`ast.parse`が`SyntaxError`を投げる、または(Step2の様に)構文的に妥当でも注入したpython文(`import os,sys; sys.stderr.write(...)`等)が字面上そのまま出現する事★——いずれも「悪性値が生のまま埋め込まれた」事を示す実出力 | old版に悪性値を与えても実出力に変化が現れない(=検査手法自体が古い脆弱性を検出できていない、陽性対照そのものの実効性欠如) |
| 段4負テスト(new・実物) | ★悪性値使用時と良性値使用時とで、抽出heredoc本体のsha256が完全一致(diff=0)——「値がheredoc本体に一切影響しない」実出力★ | 悪性値使用時と良性値使用時でheredoc本体に差分が生じる(=quote化またはenv経由化が機能していない) |
| 段5機能テスト(new・実物+実HTTP) | ★scriptの`print`出力ではなく、★受け口(ローカルHTTPサーバ)が実際に捕獲したPOST body/request pathの実file★に、投入した良性sentinel値が文字列として現れる事★ | 受け口の実捕獲file に sentinel値が現れない、または受け口自体が起動・受信に失敗する(ERRORとして別記) |
| 段6systemd健全性 | pre/post で対象timer 3本の`enabled`/`active`状態が完全一致 | いずれか1本でも状態が変化 |

## 実際の測定結果との対応 (実走結果doc該当箇所への参照)

- 段3: 4箇所悉く上記GREEN条件を満たした(Step0/7/8=SyntaxError実測、Step2=構文的に妥当だが注入文が
  字面通り出現=これも「悪性値が生のまま埋め込まれた」証としてGREENに該当、但し性質の違いは実走結果doc
  「★重要知見★」節に明記済)。
- 段4: 4箇所悉くsha256完全一致でGREEN(実走結果doc⒟節)。
- 段5: 4箇所悉く実捕獲file(`step0/7/8_captured.json`・`step2_captured_path.txt`)にsentinel値が現れGREEN
  (実走結果doc⒠節)。
- 段6: pre/post差分無しでGREEN(実走結果doc⒡節)。

## 監査体制

暫定二者制(軍師second+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、GREEN/FAIL定義の再掲追補。新規実行は行っていない。
