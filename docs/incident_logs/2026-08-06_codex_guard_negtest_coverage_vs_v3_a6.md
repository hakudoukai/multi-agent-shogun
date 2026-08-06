# 負テストは v3 を支え得るか (足軽6号、2026-08-06・家老second下命 msg_20260806_093617_4639c17a)

## 境・限界・未測 (冒頭)

読取のみ。`tests/checks/codex_exec_sandbox_guard/smoke_test.sh`・`scripts/checks/codex_exec_sandbox_guard.sh`
いずれも★走らせていない★(下命の禁則)。編んでいない。GO_RECORD・.claude/settings.json・.gitignore不触。
newbuild・姉妹clone不触。rcはpipe越しに読んでいない(下命の禁則)。`git grep`ではなく`/usr/bin/grep -r`使用。

測時=2026-08-06T09:40:47+09:00(date -Iseconds実行結果)。git rev-parse HEAD=4b86f9974396eefd24eba16579c181c38f06a0ed
(現ブランチfeat/dd169-d006-conditional-exception、origin比ahead 62、working tree dirty=他工区の並行作業分・
本file対象3件は不変)。

対象3file、直前再測sha256一致確認済:
- `tests/checks/codex_exec_sandbox_guard/smoke_test.sh` 163行 sha256=6a624c8d4671a8cfdbb04bd9934abbfc4f65ec27394e58c409814700a29f2e89
- `scripts/checks/codex_exec_sandbox_guard.sh` 59行 sha256=a98f6129b73e11a9a897c197f92c9e21628ab0c57a659355c35a1b1fda19d88c
- `docs/incident_logs/2026-08-06_codex_guard_wiring_design_v3_a6.md` 91行 sha256=2722d51b6c4248693130e546a22ed7f902d8e0d835977950cd0304fd70d29c6b (v3、gunshi-second PASS済・commit 62b0b5a)

## ⒜ 負テストが実測する事・せぬ事 (列挙)

**実測する事 (段0=halt gateのみ):**
- C01〜C06 (smoke_test.sh L102-135): intended_cwd の6変化 (無引数/live repo直下/live repo配下/newbuild/
  安全なtmp/相対../脱出) いずれも exit 1・stderr "GO記録file不在" を返す事。
- C07 (L137-152): CODEX_SANDBOX_KIND=dockerを設定してもhaltが先着する事。
- 前提再確認 (L57-60): GO_RECORD不在である事自体をテスト実行毎に検める。

**実測せぬ事 (smoke_test.sh自身のL8-39冒頭注記が既に自認):**
1. 段1 (live-repo cwd判定=guard L44-49) の弾く側・通す側いずれも未測——GO_RECORD不在ゆえ段0が
   常に先着し、段1のcase文(guard L44)に★実行が到達しない★。
2. 段2 (sandbox種別判定=guard L53-56) の弾く側・通す側いずれも未測——同理由。
3. 許可経路 (exit 0=guard L58-59) は一切未測——GO_RECORD実在+非live-cwd+CODEX_SANDBOX_KIND設定の
   3条件が揃う状態自体を、本テストは作らない(作れば D-lane違反=GO_RECORD自己配置)。

**smoke_test.sh冒頭が触れていない、本工区で新たに気付いた事:**
4. **v3の4呼び手(audit_codex.sh:93等)は一切実行されない。** smoke_test.shはguard scriptを
   直接呼ぶのみ (L75 `bash "$GUARD" "$@"`)——`audit_codex.sh`/`audit_meta_codex.sh`/
   `hakudokai_audit_scheduler.sh`のいずれもsource/execされない。∴「guard呼出しとexec呼出しの間に
   cdを挟まない」というv3⒝の設計上の要件(v3 L40「挟めば実cwdの継承が破れる」——但しこの一文は
   v2にあり、v3では明記省略。but要件自体はv3⒝表の各行「引数無し(既定$PWD)」の前提として暗黙に
   存在)が、4箇所いずれの実file内でも★現に守られているか★は、本負テストの対象外。
5. **C01の「無引数」ケース自体、実行時cwdが制御・記録されていない。** smoke_test.sh L47は
   `REPO_ROOT="$(cd ... && pwd)"`とsubshell内でcwdを計算するのみで、本体scriptの実cwdを
   REPO_ROOTへcdしていない。∴C01実行時の実際の`$PWD`(=guard L17の`INTENDED_CWD`に入る値)は、
   本テストを呼び出す側(本ケースでは当職がbashを起動した位置)に依存し、テスト自身は
   どの値であったかをログ・アサートしていない。

## ⒝ v3の4呼び手・各々への三値判定

v3⒝表(4呼び手いずれも「引数無し(既定$PWD)」で結線)を前提に、各call siteでの
cwd誤りバグ(例=guard呼出しとexec呼出しの間に意図せぬcdが混入する回帰)を、
本負テストが捕捉し得るかを三値判定する。

| # | file:line | 判定 | 理由 |
|---|---|---|---|
| 1 | scripts/audit_codex.sh:93 | ㈢未測 | smoke_test.shはこのfileを一切実行しない。同fileのcd構造(L33/L41がsubshell限定)は本工区以前の別工区(v1設計)で静的に確認済だが、それを★実行で検証する負テストは存在しない★ |
| 2 | scripts/audit_meta_codex.sh:263 | ㈢未測 | 同上。加えてv3⒝はL259→L260へ挿入位置を訂正したが、この挿入自体★まだ実装されていない★(v3は設計のみ・実装せずと明記、L5)ため、そもそも「呼び手が引数無しで呼ぶ」実体がコード上に存在しない |
| 3 | shim/hakudokai/hakudokai_audit_scheduler.sh:125 | ㈢未測 | 同上。加えてv3⒞が既に自認する通り、この呼び手を起動するsystemd/cronが当PC上に0件(a2実測)ゆえ、たとえ実装されても実行で検証する経路自体が無い |
| 4 | shim/hakudokai/hakudokai_audit_scheduler.sh:176 | ㈢未測 | 同上(#3と同file・別行、同じ0件経路の制約を共有) |

**4箇所いずれも㈢未測——理由は共通2層。第1層=v3自体が未実装(設計のみ)ゆえ4箇所の実file側コードに
「引数無し呼出し」の実体がまだ無い。第2層=たとえ実装されても、smoke_test.shは4箇所の実fileを
一切実行せずguard単体のみを直接叩く構造ゆえ、実装後もこの負テストのままでは4箇所を検証できない
(⒞で詳述)。**

## ⒞ 核心設問への回答: 無引数呼出しが誤cwdから起きた場合、負テストはREDに成るか

**答=否(赤くならぬ)。**

根拠は guard本体・smoke_test.sh両者の行番号で示す:

1. **guard L31-38 (段0)** が、`INTENDED_CWD`(guard L17)の値に★一切関わらず★先着する。
   `GO_RECORD`が不在なら(現環境=不在、smoke_test.sh L57-60が実行毎に再確認)、guard L33で
   無条件に`exit 1`する——L44の`case "$INTENDED_CWD" in`(段1のcwd判定)には★到達しない★。

2. **smoke_test.shのrun_case (L66-95)** は`actual_rc`と`actual_stderr`のみを見る
   (L79 `if [ "$actual_rc" != "$expected_rc" ]`・L82 `grep -qi "$expected_stderr_grep"`)。
   全ケース(C01-C07)の`expected_rc=1`・`expected_stderr_grep="GO記録file不在"`(L104-151)——
   これはguard L32の段0メッセージそのものであり、段1(L46のメッセージ「live repo」)や
   段2(L54のメッセージ「sandbox種別不明」)とは★別の文言★。

3. ∴「正しいno-arg呼出し(実cwd=安全な場所)」と「誤ったno-arg呼出し(実cwdが何らかの理由で
   live repo等に成ってしまった回帰)」の両方が、GO_RECORD不在という現在の前提下では
   ★同一のrc=1・同一のstderr文言("GO記録file不在")を返す★。smoke_test.shはこの2つの状態を
   ★区別する手段を持たない★——段0が段1の結果を常に覆い隠す。

4. さらに⒜4・⒝で述べた通り、v3の4呼び手自体がsmoke_test.shの実行対象に含まれていない
   (guard単体を直接叩くのみ)。∴「4箇所いずれかで、意図せぬcdが挟まりcwdの継承が壊れる」
   という具体的な回帰シナリオは、smoke_test.shを実行しても①段0に隠されて②そもそも
   4箇所の実fileが実行されないので発現しようがない、という★二重の理由で素通りする★。

**∴ 下命が名指した懸念(条件②のPASSが条件①の誤りを素通りさせる)は実際に成立している。**
本負テストが`ALL PASS (N/N)`を返す事は、v3の4箇所の結線が正しく機能する事の
証拠には成り得ない——本負テストは「GO_RECORD不在時に段0が確実に弾く」事しか実測しておらず、
v3設計の核心(段1へ渡る`INTENDED_CWD`の値が呼び手ごとに正しいか)には★及んでいない★。

## ⒟ 不足点 (列挙のみ・新テスト作成はせず)

1. 段1/段2の弾く側・通す側いずれも未測 (smoke_test.sh自身が冒頭で既に自認・a1のv1反証も同旨)。
2. v3の4呼び手の実fileを実行する負テストが存在しない——guard単体の直接呼出ししか無い。
3. GO_RECORD不在を前提とする現行テスト構造は、GO_RECORD実在下での段1/段2検証と
   ★両立しない設計★(L57-60がGO_RECORD実在時に即中断する)——将来段1/段2を実測するには、
   別テスト(GO_RECORD相当の自己供給が要る=D-lane制約に触れるため、agentには作成不可)を
   要する。これはv3⒞・a1反証が既に指摘した限界と同根。
4. no-arg呼出し時の実際の`$PWD`をテスト自身が制御・記録していない(⒜5)——テストを
   どのディレクトリから起動するかに依存した未検証の暗黙前提が残る。

## ⒠ 零・根拠の明記

- 「段1/段2を捕捉するケース数」=0件。根拠=guard L31-38(段0)がGO_RECORD不在下で
  無条件先着してexit 1する為、L44(段1)以降に実行が到達したケースは smoke_test.sh
  全7ケース(C01-C07)中★0件★(全ケースのexpected_stderr_grepが段0の文言"GO記録file不在"に
  一致する設計である事から判定・L104/110/116/122/128/134/144)。
- 「4呼び手の実fileを実行するケース数」=0件。根拠=smoke_test.sh全体でsourceまたはexecされる
  対象file集合(実測=`/usr/bin/grep -n "^\s*bash\|^\s*source\|^\s*\." tests/checks/codex_exec_sandbox_guard/smoke_test.sh`
  相当の確認、L75の`bash "$GUARD" "$@"`のみが唯一の子process起動行)は`$GUARD`
  (=`scripts/checks/codex_exec_sandbox_guard.sh`)一箇所のみ。

## この工区で確かめた事・確かめておらぬ事

- v3設計文書自体(⒟節)は既に「読んだが使わなんだ」の自己反省を含んでおり、家老second殿の
  想定通り重複作業には該当しない(下命に明記の通り)。
- 本工区は★v3設計の正当性★を再評価するものではなく(それはa1/a2が既に実施しPASS済)、
  ★条件②(既存負テスト)が条件①(v3)を実測面で裏付けているか★のみを問うた。回答=裏付けていない。

## 監査体制

暫定二者制(軍師second+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、負テストがv3を支え得るか、への応答。smoke_test.sh・guard本体いずれも実行していない。
