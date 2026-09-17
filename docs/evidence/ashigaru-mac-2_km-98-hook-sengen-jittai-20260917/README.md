★門控(提出前)★ 出す前門 `karo_mac_dasumae_gate.sh` ★rc=0★ / ★條① 一致=54・母數=54★(相違0・実体無0・読めぬ行0) ‖ `karo_mac_gate7.sh` ★rc=0★(七欄 悉く通) ‖ ★的の母數(hook の command)=6本★。此の四數は `grep` で `_after/40_gateC.*`・`_after/41_gate7C.*`・`_raw/11_hooks_base.err` から引いた逐語であり、その控は `_after/42_ichigyo_tenki.txt` に在る。★byte和と gate7 の甲乙丙は此の行を書けば動く數ゆゑ一行目に置かず、控の節に書いた ―― 紙は己を含んだ數を先には書けぬ。★

# km-98 ―― hook の宣言と実体を一本づつ測る(專任2・2026-09-17)

- 席 = ashigaru-mac-2(`tmux display-message '#{@agent_id}'` で自己識別・rc=0)
- 刻 = 2026-09-17T14:18:19+0900(測り始め)〜 14:24:49+0900(測り終り)。`date` で取り、書いてから送らぬ。
- 的 = 「settings.json が宣した hook は、悉く実体を持つか」★一件のみ★。★直さぬ。測る。★
- 固定基点 = `1da2b6b9fb7fcf9a4a51be2c495b3a0fef386424`(親 `3b413b7e`)。`git cat-file -t` = commit(rc=0)。
- 出所の優先則 ―― 食ひ違ひたる時は ★現物(git tree と disk)が勝つ★。紙の宣言は負ける。
- 転記の則 ―― 本紙の數は悉く `_raw/*.err` `_raw/*.rc` からの ★転記★ とする(則)。零に就いては `grep` で引いた逐語を
  `_after/12_zero_tenki.txt` へ別立てに焼き、本紙の各行から其れを指した。
- 印: ①=測定 ②=器の出力の転記 ③=推論(根拠を併記) ④=未測。

---

## ㋐ 母數 ―― hook の command は ★6本★

器 = `_inst/10_hooks_from_rev.py <rev>`(json.loads で読む・字面で数へぬ)。出目 `_raw/11_hooks_base.*`、rc=0。

| | rev | settings.json bytes | 行(改行数 wc -l) | 行(grep -c '') | hook command 本数 |
|---|---|---|---|---|---|
| ① | 1da2b6b9(据ゑた) | 37396 | 1107 | 1108 | ★6★ |
| ① | main 363d5fb0 | 36574 | 1088 | 1089 | 4 |
| ① | disk(未commit) | 37524 | 1109 | 1110 | 6 |

sha256(base) = `0e2a3391a9d560daaa917c788bca37c55f9123a707bfcd99f77932f406365735` ―― 家老の宣(1108行/37396byte/同sha)と ★一致★。
「1108行」は `grep -c ''` の方言、`wc -l` なら 1107。上表の `grep -c` 欄は ★三本とも実測★(`_raw/95`)であり、
推した数は一つも無い。三本とも末尾1byte = `7d`(`}`) ∴ ★EOF 改行 無し★(`xxd` で実測)。

event 別内訳(base 6本):PreToolUse=2 / Stop=2 / StopFailure=1 / UserPromptSubmit=1。

★字面で数へてはならぬ理由(実測)★ ―― `grep -c '"command"'` は base で ★12★ を返す(`_raw/96`)。
`"type": "command"` が同じ字面を持ち ★二重に数へる★ からである。`grep -c '"type": *"command"'` なら 6。
∴ 母數の出所は json のみ。上の grep は ★交叉検め★ であつて出所に非ず。

## ㋑ 一本づつの判 ―― 据ゑた commit では ★甲=6・乙=0・丙=0・丁=0★(器=`_inst/20_classify.py`、`grep -o` で `_raw/21_class_base.err` から転記・`_after/12`)

器 = `_inst/20_classify.py <rev> <hooks.tsv>`。tree=`git cat-file -e`、disk=`os.path.exists`、遮断=`git check-ignore -v`。
出目 `_raw/21_class_base.tsv`、rc=0、母數=6、和=6(母數と一致)。

| no | event | 判 | path(展開後・repo相対) | tree(1da2b6b9) | disk | 遮断の則:行 |
|---|---|---|---|---|---|---|
| 1 | PreToolUse | 甲 | scripts/checks/pretooluse_bash_guard.sh | 有 | 有 | ― |
| 2 | PreToolUse | 甲 | scripts/checks/dd169_kill_term_guard.sh | 有 | 有 | ― |
| 3 | Stop | 甲 | scripts/stop_hook_inbox.sh | 有 | 有 | ― |
| 4 | Stop | 甲 | scripts/goal_stop_hook.py | 有 | 有 | ― |
| 5 | StopFailure | 甲 | scripts/goal_stopfailure_hook.py | 有 | 有 | ― |
| 6 | UserPromptSubmit | 甲 | scripts/checks/context_usage_warn.sh | 有 | 有 | ― |

path は悉く `${CLAUDE_PROJECT_DIR:-/Users/momizimac/multi-agent-shogun}` の形。本席で `CLAUDE_PROJECT_DIR` は ★未設定★
(`python3 -c` で実測)∴ 既定側が効く。展開は器が一段だけ行ひ、註欄に `CLAUDE_PROJECT_DIR=既定` と刷つた。

### 零の四札(乙=0・丙=0・丁=0 の裏書 ―― 器=`_inst/20_classify.py`、数は `grep -o` で stderr から転記)

1. ★陽性対照 其の一(現物)★ ―― 同じ器 `_inst/20_classify.py` に ★親 tree 3b413b7e★ を当てると
   `_raw/40_pos_parent.*` rc=0 で ★甲=4 乙=2 丙=0 丁=0★(`grep -o` 転記)。鳴つた2本 =
   `scripts/goal_stop_hook.py`(tree無 rc=128/disk有/遮断 `.gitignore:7:*`)、
   `scripts/goal_stopfailure_hook.py`(同)。∴ 器は ★乙を鳴らせる★。之が本 commit の塞いだ疵そのもの。
2. ★陽性対照 其の二(仕掛)★ ―― `_fixture/50_fixture_hooks.tsv`(5行・★現物に非ず★・母數に算入せぬ)を通すと
   `_raw/51_pos_fixture.*` rc=0 で ★丙=1 丁=4★。丁の四つの理由は逐語で
   「path らしき token 無し(tok=1)」「${ が閉ぢぬ」「shlex 分割不能: No closing quotation」「KM98_NAI_HENSUU 未設定かつ既定無し」。
   ∴ 器は ★丙も丁も鳴らせる★。
3. ★陰性対照★ ―― 現物 6本(`_raw/21`)と main 4本(`_raw/32`)で 乙丙丁 が ★鳴らぬ★(rc=0)。
4. 根と深さ = 判ずる対象は「settings.json の hooks 鍵の下の command 悉く」であり、
   走査の根は tree/disk の二面。rc は上記の通り悉く 0。刻は冒頭に記した。

### ★器の疵(自白)★ ―― 丙の「遮断」欄は読むに堪へぬ

`_raw/51` の F1 行は disk にも tree にも無い path であるのに、遮断欄に `.gitignore:7:*` と出た。
`git check-ignore` は ★実体の有無を問はず則の当たりだけ★ を答へるからである。
∴ ★丙の行の遮断欄は意味を持たぬ★。乙の行でのみ読め。本紙の表では丙の現物が0ゆゑ実害は無いが、器の註として残す。

## ㋒ main との差 ―― 「4→6」では足らぬ。★増えた2本の名★ と ★形の変化4本★ である

器 = `_inst/37_diff_hooksets_v2.py`(鍵 = event × ★repo相対 path★)。出目 `_raw/38_*`、rc=0。

- ★増えた2本(名指し)★
  1. `Stop` : `python3 ${CLAUDE_PROJECT_DIR:-…}/scripts/goal_stop_hook.py`
  2. `StopFailure` : `python3 ${CLAUDE_PROJECT_DIR:-…}/scripts/goal_stopfailure_hook.py`
  併せて ★event `StopFailure` 其の物が新設★(main には存在せぬ event 名)。
- ★減つた hook = 0本★ ―― `grep -E '^# (main|1da2b6b9|両方)' _raw/38_diff_main_base_v2.txt` の逐語「main のみ = 0」より(`_after/12`)
- ★形だけ変つた4本★ ―― 相対 path ⇒ `${CLAUDE_PROJECT_DIR:-絶対}`。
  `scripts/checks/pretooluse_bash_guard.sh` / `scripts/checks/dd169_kill_term_guard.sh` /
  `scripts/stop_hook_inbox.sh` / `scripts/checks/context_usage_warn.sh`。
- 両方に在り ★字面同一=0★(4本悉く字面が変つた) ―― 同じ `grep` の逐語「両方に在り 字面同一=0 / 字面違ふ=4」より。

### ★器が一度 嘘を吐いた(自白)★

初版 `_inst/35_diff_hooksets.py` は鍵に ★展開後の生の path★ を用ゐた。main は相対・base は絶対ゆゑ
鍵が一つも重ならず、出目は「main のみ=4 / base で増えた=6」―― ★増減を六と四に水増しした★。
其の出目は消さず `_raw/36_diff_NAIVE_bad_key.txt` に残す。鍵を repo 相対へ直した v2 が上の表である
(`diff` で置換の当たりを数へ ★5行★ を確認済)。★數を刷る器の方が誤り得る★。

### ★第五の目 ―― 甲であつても呼べば落ちる(tree/disk の軸では捕へられぬ)★

`_raw/80_cwd_resolution.txt`(器 = `os.path.exists`・★hook は走らせず path 解決だけ★ を測る):

| 宣言の形 | cwd=repo根 | cwd=/Users/momizimac | cwd=/ |
|---|---|---|---|
| main の相対4本 | 解ける | ★解けぬ★ | ★解けぬ★ |
| base の絶対6本 | 解ける | 解ける | 解ける |

∴ main の4本は ★甲(tree有・disk有)でありながら、cwd が repo 根を外れた席では呼べぬ★。
前席の実測が同じ物を見て居る ―― `~/.claude/projects/…/memory/reference_settings_json_declares_hooks_cwd_relative.md` に
2026-09-12 の pane 逐語「`PreToolUse:Bash hook error / Failed with non-blocking status code:`
`bash: scripts/checks/dd169_kill_term_guard.sh: No such file or directory`」が残る(②転記・本席での再現は行はず)。
★本 commit の形の変化4本は、此の第五の目を塞ぐ手当であつた★ ―― 「2本増えた」より重い。

## ㋓ 乙・丙が呼ばれた時に何が起きるか

現物(1da2b6b9)の乙・丙 = ★0本★ ∴ 本問に該当する現物は無い。以下は ①実測 と ②器の逐語 のみで書く。

- ★実体の無い path を interpreter に与へた時の rc(実測・`_raw/70_interp_probe.txt`)★
  `python3 <実体無>` → ★rc=2★(逐語「can't open file … [Errno 2] No such file or directory」)
  `bash <実体無>` → rc=127 / 直接実行 → rc=127。
- ★rc=2 が Stop で何を意味するか(器の逐語)★ ―― `scripts/goal_stop_hook.py:4`
  「exit 2で停止を差し戻し続行させる(公式仕様: exit2="Prevents Claude from stopping")」。
  `scripts/goal_stopfailure_hook.py:4` 「⑵exit2で自己再駆動を試みる」。
- ∴ ③推論(根拠=上の実測 rc=2 と 逐語):★`python3` で呼ぶ Stop/StopFailure hook が丙に落ちると、
  interpreter が返す rc=2 が「停止させるな」と読まれ、席は黙つて止まれなくなる★。
  即ち ★丙は「黙つて通る」側ではなく「落ちて止める」側へ倒れる★。今回塞いだ2本は正しく此の2本である。
- 対して `bash` で呼ぶ4本が丙に落ちた時は rc=127(≠2)。`scripts/checks/pretooluse_bash_guard.sh:52-53`
  は「§19 観点・hook はブロック禁: 必ず exit 0」と書き、己は 0 で出る。127 を runner が如何に扱ふかは
  ★本席では未測(④)★ ―― 前席の逐語は "non-blocking" と述べるが、本紙では測つた物としては数へぬ。
- ★乙(disk有・tree無)が呼ばれた時★:disk に在るゆゑ ★此の機では普通に走る★。壊れるのは
  ★clone した先★ である。∴ 乙は「今日は何も起きぬ」顔をして、他所で丙に化ける。之が最も見付け難い。

## ㋔ 「宣言と実体の乖離」を機械で捕へる検査(草案・★据ゑぬ★)

名 = `hook_declaration_vs_reality.py`(実体は本弾の `_inst/20_classify.py` を据ゑ直す物であり、新規に作らぬ)。

- ★当てる先★:commit を作らうとする其の tree(pre-commit なら index、CI なら push された commit)。
- ★判定★:hooks 鍵の下の command 悉くに就き ―― 乙 or 丙 が1本でも在れば ★落とす(rc≠0)★。
  丁 は ★落とさず名指しで刷る★(判定不能を「疵無し」とも「疵有り」とも言はぬ)。
- ★併せて見る二つ★(本弾で見付けた、path の有無では捕へられぬ物):
  ⑴ 相対 path の宣言 = ★警め★(cwd 依存・㋒の第五の目)。⑵ event 名が既知の集合に無い = ★警め★
  (`StopFailure` が runner に届いて居るかは本席 ★未測★。宣言された event を誰も dispatch せねば
   hook は永久に発火せず、之も乖離の一種である)。
- ★陽性対照★ = `3b413b7e`(親)。此れを食はせて ★乙=2 を鳴らし rc≠0 で落ちねば器に非ず★(本弾 `_raw/40` で実演済)。
  併せて `_fixture/50_fixture_hooks.tsv` で 丙=1・丁=4 を鳴らす事(本弾 `_raw/51` で実演済)。
- ★陰性対照★ = `1da2b6b9`(据ゑた commit)と `main`。★鳴らずに rc=0★ である事(本弾 `_raw/21`・`_raw/32` で実演済)。
  ★対照は二つとも、判定に使ふ器そのもの★ を通す ―― 別の器で対照を取れば何も保証せぬ。
- ★偽陽性の見積★:現物10本(base 6 + main 4)の丁 = ★0/10★(実測)。偽陽性の主な源は ★inline 一行式★ で、
  `scripts/checks/pretooluse_bash_guard.sh:4` が「旧 inline (.claude/settings.json) は `if … then … fi; exit 0` の
  一行式」と逐語で述べる通り ★かつて実在した★。之が戻れば丁へ落ちる(=落とさず刷る側)。
  ∴ 現時点の偽陽性見積は ★0/10。inline 復活時に丁が増えるのみで、rc は汚さぬ設計とする。★

### ★裁へ出す一文(草・294字)★

> 据ゑた 1da2b6b9 の settings.json は hook 6本、悉く tree に在り 乙0丙0丁0(器=20_classify.py rc=0、陽性対照 親3b413b7e で乙2 が鳴る)。main との差は「4→6」に非ず ―― 増2本は Stop=goal_stop_hook.py と StopFailure=goal_stopfailure_hook.py、減0、残4本は相対から絶対形へ変つた。丙の python3 hook は rc=2、goal_stop_hook.py:4 曰く exit2 は停止差戻 ∴ 黙つて通らず席を塞ぐ。検査案は紙のみ、据ゑず。

字数は ★python3 の `len` で数へた(=294字・條は300字)★。実体 = `_after/20_sai_ichibun.txt`。
本文は上の引用と同一 byte であり、引用の `> ` は門 gate7 が除く冠である。

## 附 ―― 的の外だが測れてしまつた事(隠さず一行づつ)

- disk の `.claude/settings.json`(37524 byte / sha `73cc9cb3…`)は ★据ゑた commit と別物★。
  `diff -u` の差は ★hook 節の外★ で、`permissions.allow` に2行(`Bash(bash scripts/inbox_write.sh:*)` 他)が
  ★disk にのみ在る★(`_raw/94`)。hook 6本は disk と commit で ★完全に同一★(`_raw/91`・`_raw/92` rc=0 甲=6)。
- 据ゑた settings.json は ★EOF 改行を持たぬ★(末尾 `7d`)。
- 本 worktree の HEAD は枝 `ashigaru-mac-3/km-51-…` であり、家老の据ゑた枝 `karo-mac/settings-hook-abs-20260917` ではない。
  本弾は ★読取のみ★ ―― settings.json を書かず、hook を走らせず、add/commit/push を行はず、worktree を汚さぬ。

## 紙を出す前に手を入れた事 ―― ★悉く宣する(黙つて直さぬ)★

1. ★空の stderr を一行にした(4本)★ ―― `_raw/70_*_missing.err` 等 4本は元 ★0 byte★ で、門 條④
   (EOF 改行 丁度1)に鳴つた。消さず・作り直さず、★「元は 0 byte」と宣する一行★ を各々に書いた。
   ∴ 之等の file は ★器の出目そのものではなく、出目が空だつた事の宣言★ である。数=`_after/03_zero_byte.txt`。
2. ★門の argv から 1本を宣して除いた★ ―― `_raw/93_base_settings.json` は据ゑた settings.json の
   ★byte 完全な写し★ であり、EOF 改行を持たぬ(=元が持たぬ)。改行を足せば sha が
   `0e2a3391…` から動き、固定基点の写しでなくなる。∴ ★條④ の argv から除き、臺帳には残した★。
   両側が同一 sha である事は `_after/04_jou4_jogai.txt` に焼いた。★除いた物も母數には数へる。★
3. ★分類器を直し、5つの判を悉く取り直した★ ―― 末尾の空欄が tab のまま残り 條② に鳴つた。
   `_inst/20_classify.py` を `-` 詰めへ直し(置換の命中数を assert)、base/main/親/仕掛/disk の
   ★5つ悉く再走★。判(甲乙丙丁)は ★一つも動かなかつた★(`_after/02_matsubi_kuuhaku.txt`)。
4. ★門の取違ひを宣する★ ―― 任は「門控 = `~/bin/karo_mac_gate7.sh` を通し ★rc と母數と條①の数★ を書け」と言ふ。
   併し `karo_mac_gate7.sh` は ★七欄を刷る sourced 関数 `gate7()` であり、rc も母數も條①も出さぬ★(21行・実読)。
   rc/條① を出すのは `scripts/checks/karo_mac_dasumae_gate.sh`(出す前門)である。
   ∴ ★勝手に読み替へず、両方を通し、両方の出目を一行目に書いた。★
5. ★員外(臺帳の外)★ ―― 束を歩いた file=74 / 臺帳の實體行=54 / ★員外=20★
   (`_after/21_ingai.txt`・器=同 file 内の walk・`__pycache__` と symlink を除く)。
   員外は `README.md` `MANIFEST.txt` と `_after/` の 18本 ―― 悉く ★臺帳を焼いた後に生まれた物★ である。
   ★此の数は歩いた刻の函数であり、最後の門を通した後は更に増える★(門の出目 file が後から生まれる為)。

## 門を通した控 ―― ★四度 通した。動く數と動かぬ數を分ける★

| # | 走 | 出す前門 rc | 條① 一致/母數 | 條⑤ byte和 | gate7 rc | gate7 七欄 |
|---|---|---|---|---|---|---|
| 1 | A `_after/32_gateA.*` `_after/34_gate7A.*` | 0 | 54/54 | 46219 | 0 | 甲=6 乙=1 丙=12 |
| 2 | B `_after/37_gateB.*` `_after/36_gate7B.*` | 0 | 54/54 | 46249 | 0 | 甲=7 乙=0 丙=12 |
| 3 | C `_after/40_gateC.*` `_after/41_gate7C.*` | 0 | 54/54 | 46813 | 0 | 甲=7 乙=1 丙=13 |
| 4 | D `_after/43_gateD.*` `_after/44_gate7D.*` | 0 | 54/54 | 46782 | 0 | 甲=7 乙=0 丙=13 |
| 5 | E `_after/45_gateE.*` `_after/46_gate7E.*` | 0 | 54/54 | 48667 | 0 | 甲=7 乙=4 丙=13 |
| 6 | F `_after/49_gateF.*` `_after/48_gate7F.*` | 0 | 54/54 | 48667 | 0 | 甲=7 乙=4 丙=13 |
| 7 | G `_after/51_gateG.*` `_after/50_gate7G.*` | 0 | 54/54 | 49007 | 0 | 甲=9 乙=0 丙=15 |

- ★動かぬ數★ = rc(0) と 條①(一致54・母數54)。∴ 之のみを一行目へ置いた。
- F は ★E と同じ紙★ を通した走である(直前の置換が assert で止まり、紙が一字も動かなかつた)。
  ∴ F と E の數が悉く同じ事は ★偶然ではなく、門が同じ入力へ同じ出目を返した證★ である。
- 此の表を書いた後にも一度通す ―― 其の出目は `_after/52_gateH.*`・`_after/53_gate7H.*` に在り、
  ★紙には載せぬ(載せれば又動く)★。★rc と 條① は七度とも 0 と 54/54 で不動である。★
- ★動く數★ = 條⑤ byte和 と gate7 の甲乙丙 ―― ★紙を一字書けば動く★。A→B は `grep` で名指した零主張6行へ器名を付けた分、
  B→C は一行目を焼いた分、C→D は其の一行目を書き直した分である。
- A で 乙=1・C で 乙=1 と鳴つたのは ★本紙自身の行★ であり、`_after/35_otsu_line.txt` に名指しで焼いた。
  ⑴A の1本 = 「転記の則」の行(`grep` を同じ行へ寄せて解いた)。⑵C の1本 = 一行目其の物
  (`grep` で引けば、零を並べた其の行に器名が無かつた)。★門は己を測る紙にも鳴る。★
  ⑶E の4本 = 此の控の表そのもの(1欄目が數字でなく走名ゆゑ門が「表」と見ず本文と見た)。∴ 1欄目を ★數字★ に直した。
- 條⑤の閾 `DASUMAE_MAX_BYTES` は ★未設定★ ゆゑ既定 10485760 が使はれた事を門自身が刷る(`_after/43_gateD.err:2`)。
- 門の argv は ★54本★(`_after/31_gate_argv_A.txt`)。臺帳54行から `_raw/93_base_settings.json` を除き、
  代りに本紙 `README.md` を加へた物である。★前回の控 `_after/05_gate_argv.txt` は README.md を書き落として居た(53行)★ ――
  併し實際に通した本数は當時も54本で、byte和の差 3574 が ★本紙の肥り分と丁度一致する★事で之を検めた(`_after/33_bytesum_kensan.txt`)。

## 納め便の控 ―― ★送つた事ではなく、着いた胴で言ふ★

- 宛 = ★家老mac★(`queue/inbox/karo-mac.yaml`)。軍師mac は死箱ゆゑ監査は家老が代送する(任の通り)。
- 胴 = ★297字★(`python3` の `len` で測つた・條は300字)。控 = `_after/60_osame_body.txt`。
- `scripts/inbox_write.sh` rc=0(`_after/62_send.rc`)。★併し rc は「送つた」であつて「着いた」ではない。★
- ∴ 箱を読み返した ―― 行数 621→632、着いた便 `id=msg_20260917_144033_a63defd5` /
  `from=ashigaru-mac-2` / `type=report_received`(`_after/63_box_after.txt`)。
- 更に ★胴そのものを突き合はせた★ ―― 送 297字 と 着 297字、sha256 は両側 `07b123d1…` で ★一致★
  (`_after/64_body_readback.txt`・器=`python3 yaml.safe_load`)。箱は YAML 折返しで見た目が変はるが ★字は一つも動いて居らぬ★。

## 器と出目の控

| 器(`_inst/`) | 何を測るか | 出目(`_raw/`) | rc |
|---|---|---|---|
| 10_hooks_from_rev.py | rev の settings.json から hook command を json で取る | 11(base)・31(main) | 0・0 |
| 12_hooks_from_file.py | 同じ物を disk の file から取る(10 との差4行) | 91(disk) | 0 |
| 20_classify.py | 甲乙丙丁 の判 | 21(base)・32(main)・40(親=陽性)・51(仕掛=陽性)・92(disk) | 悉く 0 |
| 35_diff_hooksets.py | ★鍵を誤つた初版★(控として残す) | 36_diff_NAIVE_bad_key | 0 |
| 37_diff_hooksets_v2.py | main と base の hook 集合の差(repo相対の鍵) | 38 | 0 |

`_fixture/50_fixture_hooks.tsv` は ★人の手で作つた仕掛★ であり、現物の母數(6・4)には ★算入せぬ★。
但し「除いた」は「歩いて居らぬ」の意に非ず ―― 器には確かに食はせ、其の出目が上の陽性対照である。

---

# ★REVISE ―― 軍師mac の三指摘の治し(2026-09-17 第二便)★

軍師の三つ ⑴束が untracked ⑵固定 commit/tree に束が無い ⑶到達 ref 無し は、
★紙の中身の疵ではない★。「束が commit の中に無い」一事から出て居る(家老mac が同じ疵を PR#20 で解き、手順を渡した)。
★CI は本件の要件から外れた★(請求起因で全 job 未起動・dev_qa#1099・裁 seq326349)ゆゑ CI 緑は待たぬ。

## ① 頭を固定して器を再走した ―― ★提出済 `_raw/` は一字も触れて居らぬ★

固定した頭(紙が宣した物と同じ):

| 名 | sha | 何に使ふ |
|---|---|---|
| 基点 | `1da2b6b9fb7fcf9a4a51be2c495b3a0fef386424` | 現物の測り |
| 親 | `3b413b7ef7ae871908ce4d74a4d939fdfbd8ade1` | 陽性対照(甲=4・乙=2) |
| `main` | `363d5fb060845171338c067ef42bfcbef8ad9188` | 再走時に `git rev-parse main` で実測。`_raw/30_main_sha.txt` と同じ ∴ ★動いて居らぬ★ |

- 器 = `_saisou/10_saisou.py`。★argv は手の記憶でなく出目から復元した★ ――
  `_raw/<幹>.tsv` の頭行 `tree(<rev[:8]>)` が classify の第一引数を、`_raw/11_hooks_base.err` の `rev=` が
  `10_hooks_from_rev.py` の引数を、`_raw/91_hooks_disk.err` の `rev=.claude/settings.json` が
  `12_hooks_from_file.py` の引数を、`_raw/36|38.txt` の頭行 `# main = 4 本 / 1da2b6b9 = 6 本` が
  diff 四引数の並びを、各々 ★名指して居る★。
- 出目 = `_saisou/` の同じ名(新しい置場)。★10 幹 × 3 面(本体/err/rc)= 30 本★。rc≠0 = 0。
- 前→後 = `_saisou/20_cmp.py` → `_saisou/21_cmp.txt`。**突合せ 30 本 / 同=30 / ★異=0★**。
- 生捕りの出目は `_saisou/12_kaki.py` で末尾を揃へた(歩き根が `_saisou` でなければ ★拒んで落ちる★ ―― `_raw/` を触らぬ為)。直した=0。

### ★母數の宣 ―― 30 は 48 ではない★

`_raw/` の現物は 48 本。其の内 ★器が産んだのは 30 本★ であり、残る 18 本
(`70_*` の interp 探り 4・`71_hook_gyakugo`・`80_cwd_resolution` 3・`90_disk_settings` 3・`93_base_settings.json`・
`94_settings_diff` 2・`95_gyou_kazoekata`・`96_kousa_jimen` 2・`30_main_sha`)は ★手で測つた物★ で器が無い。
∴ 本弾の的から外した。★「外した」は「無い」の意に非ず。★

### ★不動の證 ―― 代替と、其の弱さ(隠さず)★

家老の手順① は「元の raw は `git cat-file -p <枝>:<path>` で戻して sha 不動を證せ」と言ふ。
★此の路は通れなかつた。★ km-98 の束は一つの commit にも ref にも入つて居らぬからであり、
★其れこそが今治す疵の本体★ である(手順① は「既に枝に在る束」を前提に書かれて居る)。

代りに据ゑたのが `_saisou/00_zen_sha.py` ―― ★再走の前に★ 束の全現物 144 本の sha256 を録り
(`_saisou/01_zen_sha.tsv`・刻 `2026-09-17T16:13:28`)、再走の後に `_raw/` の 48 行を突き合はせた。
**前=48 / 今=48 / 不動=48 / 動いた=0 / 消えた=0 / 増えた=0**(`_saisou/21_cmp.txt` 乙)。

★此の證は git より弱い。録つたのが己自身だからである。★ git なら第三者の object store が言ふ所を、
此処では當席の表が言つて居るに過ぎぬ。③ が通つた後は ★同じ事を git が言へる★ ようになる。

### 零の四札(異=0・動=0 の裏書)

1. ★陽性対照★ = `_saisou/20_cmp.py` 丙。必ず異なる二本(`11_hooks_base.tsv` と `31_hooks_main.tsv`)を
   ★同じ比較路★ へ通し、`★異★` と鳴つた。∴ 甲・乙 の零は ★鳴る路の上で測つた零★ である。
2. ★根と深さ★ = 歩き根は束の根 `docs/evidence/ashigaru-mac-2_km-98-hook-sengen-jittai-20260917/`、
   `os.walk` で深さ無制限。symlink は辿らず、非 regular は別に数へた(=0)。
3. ★rc★ = `10_saisou.py` rc=0(幹 10 / rc≠0 の幹 0)、`20_cmp.py` rc=0、`12_kaki.py` rc=0。
4. ★刻★ = 録り `16:13:28` / 再走 同日 16:14 台 / 突合せ 同日 16:15 台。

## ② 臺帳は append のみ ―― 既存 54 行は一 byte も動いて居らぬ

- ★束の中から★ 呼んだ(`cd <束>` してから `karo_mac_manifest_append.py MANIFEST.txt _saisou/<名>…`)。
  裁 seq322699「臺帳の根は束内相対」ゆゑ、門は `KM_GATE_MANIFEST_BASE=.` を要する。
- 書いた=38 行 / 母數=38 / 括つた=0、rc=0(`_after/72_append.{out,err,rc}`)。臺帳は **54 → 92 行**。
- ★不動の證★ = 追記前の写し `_after/70_manifest_before.txt`(56 行 = 2冠 + 54行)と、追記後の頭 56 行
  `_after/74_manifest_head.txt` を `cmp` ―― **rc=0**(`_after/75_cmp_kekka.txt`)。
  ★rc は pipe を通さず直に拾つた★(`cmp; rc=$?`)。
- ★陽性対照★ = 同じ写しの 3 行目 `path=` を一字だけ全角 `path＝` へ換へた物を当てると
  `cmp rc=1` / `differ: char 200, line 3`(`_after/77_taisho_cmp.txt`)。∴ 上の rc=0 は ★鳴る cmp の rc=0★ である。

## ③ 束を枝へ据ゑる ―― ★共有 index と HEAD を汚さぬ plumbing で★

| 項 | 値 |
|---|---|
| 枝(★一字も縮めぬ★) | `refs/heads/ashigaru-mac-2/km-98-hook-sengen-jittai-20260917` |
| 親 | `1da2b6b9fb7fcf9a4a51be2c495b3a0fef386424`(=紙が宣した固定基点。新枝ゆゑ「基点」を親に取る) |
| 路 | `GIT_INDEX_FILE` を私物へ振り → `read-tree <親>` → `hash-object -w` → `update-index --add --cacheinfo` → `write-tree` → `commit-tree` → `update-ref <新> <旧値を名指す>` |
| 触らぬ物 | 共有 index・HEAD・他席の枝・`.gitignore`(裸の `*` は書換へぬ。plumbing は則を通らぬゆゑ `-f` も要らぬ) |
| 検め | `git -C <repo根> ls-tree -r --full-tree --name-only <新sha> -- <束>/` の出目と disk の差 = 0 |

★家老が踏んだ疵を此方も踏まぬ為の註★: `ls-tree` の pathspec は ★cwd 相対★ である。束の中から呼ぶと
★0 本を rc=0 で返す★ ―― 之は「無い」ではなく「見て居らぬ」。ゆゑに `git -C <根>` を噛ませ `--full-tree` を付け、
★出目に既知の一本が在るか★ を対照に置く(無ければ止まる)。`<rev>:<path>` の方は ★根相対★ であり、
此の二つは ★別の約束★ である。

### ★此の紙に新 sha を書けぬ理由★

新 commit は ★此の紙を含む★。己を含む commit の名を己の中へ書く事はできぬ
(臺帳の数を紙が一度で書けぬのと同じ形である)。∴ ★新 sha は便に書く★ ―― ⑤ の形の通り。

## ④ push せぬ

push は ★總監督の代行が正路★ ゆゑ、當席は commit 迄で止める。便には ★枝名を一字も縮めず★ 書く
(家老が短縮形で書き、代行を一度空振らせた ―― seq326424。同じ轍は踏まぬ)。

## ★自白 ―― 本弾で當方が踏んだ疵 二つ★

### 疵 其の一 ―― 着手便が ★358字★(己の宣した條 300字 を 58字 超えた)

`assert len(s) <= 300` は ★確かに rc=1 で落ちた★。★併し `;` で継いだ鎖の後段 `inbox_write.sh` が
其の儘走つた★ ∴ 358字の便が箱へ永久に残つた(`id=msg_20260917_160841_48742b95`)。
箱は append のみで消せぬ ―― ★出した物は消えぬ★ ゆゑ、消さずに此処へ書く。

之は ★既知の疵の再発★ である(「鎖の護りは尾まで覆へ」= `a && b; c; d` の形)。二度目ゆゑ ★字を重くする★:

> ★護りは尾まで覆へ。`;` は護りを跨ぐ。assert と送信は同じ `&&` の鎖か、同じ python の中に置け。★

治し = 本弾の ② 以降は `set -e` と `&&` で継いだ。⑤ の便も ★測つてから送る★ を同じ器の中で行ふ。

### 疵 其の二 ―― 家老の手順① の git 路が通らなかつた

上の「不動の證」に書いた通り。★手順が悪いのではなく、束が commit に無いから通らぬ★ のであり、
③ が通れば次回からは手順①の路がそのまま使へる。

## ⑤ 便の形(家老の指定)

「枝 `<實の ref 名>`＝`<新sha>`」+ 再走の數(前→後)+ 門 rc + 到達(紙 n/n)。
