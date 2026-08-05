# codex_exec_sandbox_guard 結線・設計のみ (足軽6号、2026-08-06・家老second下命)

## 境・限界・未測 (冒頭)

設計のみ・実装せず。audit_codex.sh・settings.json・.gitignoreいずれも編んでいない。走らせていない。
newbuild不触・姉妹clone読取すら不可。本設計は★案★であり、実装・適用は理事長殿GOおよび上位裁を経てから。

測時=2026-08-06T07:25:18+0900(date -Iseconds実行結果)。HEAD=d76b025c0c5346b7c938305dbeca2fbb29cd139f
(git rev-parse HEAD実行結果)。

## 前提2件の検算

$ grep -n "codex_exec_sandbox_guard\|sandbox\|guard" scripts/audit_codex.sh
(該当なし・0件、前々工区と同じ結果を再確認)
**∴ 前提「呼び手が無い」=正しい(不変)。**

$ wc -l docs/incident_logs/2026-08-06_codex_guard_positive_control_a1.md && sha256sum 同file
219行 sha256=ea12db232fa6ac04032e53a3c3f030333eeb73d5fda01e30033acb3132e2982a
**∴ 前提「a1が219行で通す側を実測済」=正しい。** 内容実読=3条件(GO_RECORD実在+marker一致・
非live cwd・CODEX_SANDBOX_KIND非空)を満たす合成環境でguardがexit 0を返す事を実測(実路上では
未実行、合成条件での検証)。

## 呼ぶ位置 (設計案)

$ grep -n "npx @openai/codex exec" scripts/audit_codex.sh
93:  CODEX_RAW=$(npx @openai/codex exec --json --output-last-message "$OUTPUT" < "$PROMPT_FILE" 2>"$LOG")

$ sed -n '89,94p' scripts/audit_codex.sh
89: # Invoke Codex with retry logic
90: RETRY=0
91: MAX_RETRY=3
92: while [ $RETRY -lt $MAX_RETRY ]; do
93:   CODEX_RAW=$(npx @openai/codex exec ...)

**案=L92の直前(while loop に入る直前・retry loop の外側1回のみ)。**

理由=①L93はretry loop内で複数回呼ばれ得るが、guardが確認する条件(sandbox種別・cwd)は
retry間で変化しない性質の物であり、loop内で毎回呼べば無駄な重複チェックになる
②script冒頭(L1直後)ではなくL92直前を選ぶ理由=script冒頭には「呼ばれる意味を持たぬ前処理」
(DIFF生成・PROMPT_FILE作成等)が多数在り、guardの本義(「codex execを起動する前に」)には
「起動する其の場所」に置く方が字義に忠実(SKILL.md記載の意図=「起動前に呼び」と直結する)。

## exit codeの扱い (fail-secureの要)

$ grep -n "^exit" scripts/checks/codex_exec_sandbox_guard.sh
33,37,47: exit 1 / 55: exit 2 / 59: exit 0

**設計案=`if ! bash scripts/checks/codex_exec_sandbox_guard.sh "$REPO_PATH"; then` の形で
呼び、非0(=1でも2でも)なら停止分岐へ入れる。** ★「2を進むに倒さぬ」を担保する具体的な形★=
`case $? in 0) ;; *) echo "guard blocked or undetermined, exit=$?" >&2; exit 1 ;; esac`のように
0以外を★一括して★停止側に倒す(1と2を個別分岐で書くと、片方だけ「進む」に倒す実装ミスの
余地が生まれる=本日確立の「二値に倒すな」とは別の意味で、ここは★意図的に二値化する方が安全★
=「0か否か」の一点のみで判断すれば、2を誤って進む側に倒す実装ミスが構造的に起こり得ない)。

## 引数(intended_cwd)の取得元

$ grep -n "REPO_PATH=" scripts/audit_codex.sh
20: REPO_PATH="${5:-/mnt/c/Users/User/Documents/DentalBI}"

**設計案=audit_codex.sh側の`$REPO_PATH`(第5引数、既定値あり)をそのままguardへ渡す
(`bash scripts/checks/codex_exec_sandbox_guard.sh "$REPO_PATH"`)。** 理由=guard自身が
「[intended_cwd]」を唯一の引数として設計されており(script冒頭コメント参照)、
audit_codex.sh側で新たな変数を起こさず既存の`$REPO_PATH`をそのまま渡すのが最小差分。

## 陽性対照が結線後も生きるか (a1の219行との接続)

a1のtest(2026-08-06_codex_guard_positive_control_a1.md)はguard単体を合成環境で叩いた物であり、
audit_codex.sh経由の呼出しは検証していない(a1自身も「通す側実証はこれで満たすが」と担当範囲を
明示している)。**∴ 結線後に要る追加検証(設計のみ・当職は実施せず)=audit_codex.shに
「REPO_PATHを渡してguardを呼ぶ」行を足した★版★に対し、a1と同じ3条件合成環境を用意した上で、
guard呼出し行が実際にexit 0を通し、後続のnpx呼出しへ処理が進む事を確認する統合test。**
これは実装後に別途書かれるべき負テスト/正テストであり、本設計doc自体はテストを書かない。

## 不採用案とその理由

1. **script冒頭(L1直後)で1回呼ぶ案**=不採用。理由=上記(呼ぶ位置)参照、意味的に「起動前」から遠い。
2. **retry loop内(L93直前)で毎回呼ぶ案**=不採用。理由=sandbox状態はretry間で変わらぬ性質の
   条件であり、繰り返しチェックは無駄(唯一の例外=sandbox状態が実行中に変化し得るなら再考要、
   だが当職の読取範囲ではそのような可変性の記述は見当たらず)。
3. **guard呼出しの戻り値を`|| true`で握り潰す案**=不採用。理由=CLAUDE.md §19.3
   mandateは「PreToolUse hookで呼ばれる場合」に限定した規定であり、本件はPreToolUse hookでは
   なくscript内の直呼びである為、この規定は適用されない——むしろ本件こそ`|| true`を
   ★付けてはならない★(付ければguardの停止判定が意味を失う)。

## 【本工区で己が直した誤り】

初稿で「呼ぶ位置」をretry loop内(L93直前・毎回)と書きかけたが、guardが確認する条件の性質
(sandbox種別・cwdは実行中に変化しない)を考え直し、loop外側1回のみへ書き直した
(無駄な重複呼出しを避ける方が正しいと判断を改めた)。

## ★母集団漏れの自己申告★

1. `npx @openai/codex exec`自体が非0 exitを返した際の既存のretry判定ロジック(L94以降)と、
   guard由来の停止(新設)がどう共存すべきかは、本設計では踏み込んでいない(既存retry loopの
   意味を変えぬよう、guardのチェックはloop突入★前★の一回勝負とする設計に留めた)。
2. `intended_cwd`としてREPO_PATHをそのまま渡す事の妥当性(guard側が期待する値の形式と
   REPO_PATHの実際の値が一致するか)は、guard本体のコメント読解のみに基づき、実行しての
   確認はしていない(下命の禁=実装するな・走らせるな、に従った結果)。

## 監査体制

暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、codex_exec_sandbox_guard結線・設計のみへの応答。実装は一切行っていない。
