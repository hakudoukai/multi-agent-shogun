# hook の command が相対 path である事は、cwd が動いた席で門を開く

刻 = 2026-09-17 11:51〜11:53 / 席 = 家老mac / 束の根 = 本dir(臺帳の根は束内相対・裁 seq322699)

## 宣(何を測つたか)

`.claude/settings.json` が宣する hook 6本の `command` は悉く ★repo 根からの相対 path★ である。
Claude Code の Bash 器は `cd` を跨いで cwd を保つ ∴ 席が束の中へ降りた後は、
hook の起動そのものが「No such file or directory」で落ちる ―― 是を実測で確かめた。

## 実測(raw/21_hakaru_v2.txt ―― 器 = ki/20_hakaru.sh)

| cwd | 6本の出目 |
|---|---|
| repo 根 | 悉く起動する(stop_hook_inbox は `{"decision":"block","reason":"inbox未読2件あり…"}` を返す) |
| 束の中 | ★6/6 が起動せぬ★ rc=127(bash 4本) / rc=2(python 2本) |

- 呼ばれる器は ★6本悉く実在★(16434/4982/2390/4228/6709/1786 byte)。∴「器が無い」のではなく「呼び方が相対」である。
- 絶対 path 冠(`/` `$` `~`)を持つ command = ★0/6★。

## 現に起きて居る事(席の盤・読取のみの実視 11:47)

- 專任2: `PreToolUse:Bash hook error` / `Failed with non-blocking status code: /bin/sh: scripts/checks/pretooluse_bash_guard.sh: No such file or directory`
- 專任3: 同上 `bash: scripts/checks/dd169_kill_term_guard.sh: No such file or directory`

∴ ★DD-169 破壊語の番人(PreToolUse)と、未読で止める Stop hook が、其の席で黙つて開いて居る。★
PreToolUse は rc=2 のみが「止」であり、127 は「非閉塞の誤り」＝★通す★。是が fail-open の機構である。

## 此の紙が意味せぬ事

1. 「hook が壊れて居る」とは言つて居らぬ ―― 器は健全で、呼び方だけが相対である。
2. 「席が破壊語を打つた」とは言つて居らぬ ―― 番人が居らぬ事を示しただけで、実害の有無は測つて居らぬ。
3. 6本の内、どれが何時から開いて居たかは測つて居らぬ(cwd が動いた時刻を持たぬ)。
4. repo 根での dd169 の rc=2 と `date: invalid argument 's' for -I` は ★別の疵★(BSD date)であり本件と混ぜぬ。

## 直し(紙のみ・据ゑず) ―― 案二つ

- **案甲 (薦む)**: 6本の command へ `$CLAUDE_PROJECT_DIR/` を冠する。
  例: `bash $CLAUDE_PROJECT_DIR/scripts/stop_hook_inbox.sh`。
  当 repo に既に用例が在る(`scripts/checks/codex_cli_required_persona.sh:10` の冠註、
  `scripts/checks/context_usage_warn.sh:80` は `${CLAUDE_PROJECT_DIR:-$HOME/multi-agent-shogun}`)。
  ★戻し方 = 同 file の 6 行から冠を外すのみ(可逆・患者非接触)。★
- **案乙**: 各器の頭で `cd "$(dirname "$0")/.."` させる。
  ★短所★: 呼び方が相対である限り `$0` すら解決せぬ ∴ 本件の因を塞がぬ。**乙は本件を直さぬ**。

## 疵宣(家老mac 自過失)

- **疵①**: v1 の測り器(`ki/20_hakaru_v1_kizu.sh`)は `rc=$?` を `| head -1` の後で取つた ∴
  rc 欄が悉く 0 と出て「fail-open」の証に見えた。★測れて居らぬ物を測つた事にした★。
  v2 で mktemp へ落として pipe を外し、真の 127/2 を得た。v1 は消さず束に残す。
- **疵②**: 便 seq324908 で「紙13/生器10」と報じたが、差の相手を main に取つたため
  両向きの差を己の物と数へた誤りであつた。合流点基準で「紙のみ14/生器 path を足す12」へ訂正(seq324922)。
