# audit_codex.sh 書込inventory (足軽6号、2026-08-06・家老second下命 msg_20260806_100000_20f8ebf8)

## 境・限界・未測 (冒頭)

読取のみ。走らせず・編まず・stub不設置。hakudokai-devへ一文字も書いていない。rcはpipe越しに読んでいない。
`/usr/bin/grep -r`使用。★codex exec行(L93)自体は下命により本inventoryから除外★——但し、その除外の意味
(exec自体はagenticにlive repoを書換え得る、という別次元のリスク)は末尾に明記する。

測時=2026-08-06T10:01:03+09:00(date -Iseconds実行結果)。git rev-parse HEAD=292bcf264ec45ee57b8178d7eb0ab0afb0c95d22。
対象=`scripts/audit_codex.sh` 136行 sha256=b23888c3ea8525636d5a56d448d245926eff77ebbe0d10872b14ae2a7fae8fab
(提出直前に再測)。

## 判定基準

「live repoを変え得る物」= `$REPO_PATH`(既定=`/mnt/c/Users/User/Documents/DentalBI`、L20)配下の
filesystemを変更し得る操作。これに対し、`/tmp`配下(`$OUTPUT`・`$LOG`・`$PROMPT_FILE`)への書込は
★live repo外★であり、下命の対象(live repoを変え得る物)には該当しないが、参考として別掲する
(⒝節)。git操作は「読み系(diff等)」と「書き系(add/commit/checkout/push/reset/rm/mv/apply/stash/clean等)」
を分けて判定する。

## ⒜ live repo (REPO_PATH配下) を変え得る行 — 悉く挙げる

**該当0件。**

理由(実測・行番号+逐語で示す):

- `/usr/bin/grep -nE 'mkdir|touch |mv |rm |chmod|tee |sed -i' scripts/audit_codex.sh` の結果=
  L98 `    rm -f "$PROMPT_FILE"` / L112 `rm -f "$PROMPT_FILE"` の2件のみ。両方とも対象は
  `$PROMPT_FILE`(L46 `PROMPT_FILE=$(mktemp)` — mktemp既定は`/tmp`配下、REPO_PATH外)であり、
  ★live repo配下ではない★。mkdir/touch/mv/chmod/tee/sed -iは0件。
- `/usr/bin/grep -nE 'git (add|commit|checkout|push|reset|rm|mv|apply|stash|clean)' scripts/audit_codex.sh`
  の結果=★0件★。git書き系コマンドは本fileに一切出現しない。
- git呼出しは全部で2件のみ、いずれも読み系: L33 `DIFF=$(cd "$REPO_PATH" && git diff "${BASE_COMMIT}..${HEAD_COMMIT}" -- . $EXCLUDE_PATTERN 2>/dev/null)`、
  L41 `CHANGED_PATHS=$(cd "$REPO_PATH" && git diff --name-only "${BASE_COMMIT}..${HEAD_COMMIT}" -- . $EXCLUDE_PATTERN 2>/dev/null | tr '\n' ' ')`。
  両方とも`git diff`(read-only)であり、`cd "$REPO_PATH"`は★subshell(`$(...)`内)に限定★——本体scriptの
  実cwdには影響せず、かつgit diff自体もrepoを書き換えない。
- 書込リダイレクト(`>`)は全4件、悉くREPO_PATH外の`$OUTPUT`(`/tmp/codex_audit_...json`)を対象とする:
  L36 `echo "{...\"overall_verdict\":\"fail\"...}" > "$OUTPUT"` /
  L47 `cat > "$PROMPT_FILE" <<EOF`(対象=`$PROMPT_FILE`、/tmp) /
  L99 `echo "{...\"overall_verdict\":\"fallback_required\"...}" > "$OUTPUT"` /
  L115 `echo "{...\"overall_verdict\":\"invocation_error\"...}" > "$OUTPUT"`。
  いずれもREPO_PATH配下ではない。

**∴ codex exec行(L93)を除いた全行のうち、live repoを変え得る操作は0件。**

## ⒝ 参考=REPO_PATH外(/tmp)への書込・削除 (下命の対象外だが文脈として記す)

| # | 行番号 | 逐語 | 対象 |
|---|---|---|---|
| 1 | L36 | `echo "{\"task_id\":\"$TASK_ID\",...}" > "$OUTPUT"` | `/tmp/codex_audit_<task_id>_cycle<cycle>.json` |
| 2 | L46 | `PROMPT_FILE=$(mktemp)` | `/tmp`配下の一時file生成 |
| 3 | L47-87 | `cat > "$PROMPT_FILE" <<EOF ... EOF` | 同上PROMPT_FILEへの書込 |
| 4 | L98 | `rm -f "$PROMPT_FILE"` | 同上PROMPT_FILEの削除(usage limit分岐) |
| 5 | L99 | `echo "{...\"fallback_required\"...}" > "$OUTPUT"` | `$OUTPUT`(同上) |
| 6 | L112 | `rm -f "$PROMPT_FILE"` | 同上PROMPT_FILEの削除(retry loop終了後) |
| 7 | L115 | `echo "{...\"invocation_error\"...}" > "$OUTPUT"` | `$OUTPUT`(同上) |

いずれも`$TASK_ID`/`$CYCLE`という呼出し引数由来の文字列を含むpathだが、path自体は`/tmp`固定prefixで
組み立てられており(L28-29)、REPO_PATHとは独立した名前空間。

## ⒞ 除外したcodex exec行(L93)について — 別次元のリスクである事の明記

下命により本inventoryの対象から除外したが、家老second殿の便(2)が引用する将軍second裁の因
(「audit_codex.shのcodex execはinvokerのcwdでagenticに動き、絶対pathでlive repoを書換え試行する」)は、
★このinventoryが検めた「script自身が書くリテラルな操作」とは別次元★である事を明記する。L93の
`npx @openai/codex exec --json --output-last-message "$OUTPUT" < "$PROMPT_FILE" 2>"$LOG"`は、
codexという★agentic CLIプロセスに、プロンプト経由で任意の指示を渡す★行であり、そのプロセスが実行時に
どのfilesystem操作を行うかは、★このscriptの静的なコード(⒜⒝で検めた範囲)には現れない★。
∴ ⒜の「0件」は「このscript自身が書くコマンドとしては0件」を意味するに留まり、★L93が起動する
codexプロセス自体の書込能力を否定するものではない★——2026-07-21事故の実体が正にこれ(guard L8の
コメント「Codex audit live-repo write near-miss」)である事を、本inventoryの限界として明記する。

## ⒟ 三分岐(将軍second裁)への素材としての整理

家老second殿の便(4)が示した三分岐のうち、本inventoryが直接答えるのは第1分岐の前提のみ:

- 「残る書込が零」→ ⒜の実測=このscript自身が書く★live repo向けのリテラルな書込コマンドは0件★。
- 但し⒞の通り、L93のcodexプロセス自体が持つagentic書込能力は、このinventoryの対象外(静的読取では
  測れない)——∴「stubを当てても残る書込が在るか否か」という問いへの答は、★stub適用対象がL93一行のみで
  あれば、script自身のリテラル書込という意味では残らない★が、★stub適用後もL93以外の実file実行
  (subshell内git diff等)は現に走る事自体は変わらない★(前工区で既述の懸念そのもの)。
- 第2・第3分岐(一つでも在る場合／裁定の逐語がaudit_codex.shの実行を名指す場合)への当てはめは、
  当職の権限・下命の範囲を超える為、判断せず上位の裁に委ねる。

## ⒠ 零・根拠の明記

- 「live repo (REPO_PATH配下)を変え得る行」=0件。根拠=⒜節の3種のgrep実測(mkdir/touch/mv/rm/chmod/tee/sed -i、
  git書き系、git呼出し全数)いずれも該当0件、かつ全4件の`>`書込リダイレクトが悉く`/tmp`配下の`$OUTPUT`/
  `$PROMPT_FILE`を対象とする事を個別に確認済み。

## 監査体制

暫定二者制(軍師second+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、audit_codex.sh書込inventoryへの応答。走らせていない・編んでいない・stub未設置。
