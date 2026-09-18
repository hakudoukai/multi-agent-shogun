# km-188 ―― 管を通した rc を数へよ(管の左の失敗が rc に出ぬ器・紙のみ・直さぬ・据ゑぬ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `km-188-kuda-wo-tooshita-rc-wo-kazoe-yo-20260918`(家老mac 発・裁332455/333060/329271・L4・据ゑ 20:16)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T20:22:43+0900 / 着手便 20:21(宣ETA 21:15)/ 測り 20:20〜20:23
- 枝 = `ashigaru-mac-1/km-188-kuda-wo-tooshita-rc-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km188)。押さず。
- 出所 = 家老の掟「rc を管を通して取るな」の第三の面。km-184(`2>/dev/null` 捨てる)・km-187(`2>&1` 混ぜる)とは別の面 = ★管の左の失敗が右の rc に隠れる★。

## ㋐ 結語

- 母數(㋐): 己の樹(origin/main)の sh/bats 149 file を歩き、管の行で形①〜③・⑤に当たる行 ★242 行 / 62 file★。~/bin(家老・総監督の器・除かず) ★34 行 / 10 file★。共有樹(読むのみ・席3 の枝)475 行 / 121 file(比較・raw/14)。形④ pipefail: 己の樹 有 67 / 無 82 file、~/bin 有 3 / 無 24。hit 行の内 pipefail 無の file の行 = 139(樹B)・28(~/bin)。
- 重なり(㋓・黙つて外さぬ): 同じ行に `2>/dev/null`(km-184)48+10 行、`2>&1`(km-187)9+1 行 → ★外した数 57(樹B)+11(~/bin)★。∴ 本弾固有の母數 = ★185(樹B)+ 23(~/bin)★。双方に重なる行 0。
- 判(㋑・機械の一次判を紙で代表検め): 樹B 242 = ★載る 105 / 載らぬ 111 / 判じ得ぬ 26★、~/bin 34 = 載る 16 / 載らぬ 16 / 判じ得ぬ 2。「載る かつ pipefail 無 かつ 他弾と重ならぬ」= 樹B 65・~/bin 6。
- 實射(㋒・己の束): 無い file を左に置き ⒜素の管 rc=★0★ n=0(偽の rc)⒝ pipefail 有 rc=1 n=0 ⒞ ${PIPESTATUS[0]}(bash)/${pipestatus[1]}(zsh)= 1。bash 3.2・bash 5.2・zsh 5.9 の三 shell とも同じ出目。加へて 形③: `seq 1 100000 | head -1` は pipefail 有で rc=★141★(SIGPIPE が rc を汚す)・PIPESTATUS=[141 0](raw/20)。
- 案は器の種類で分ける(㋔・据ゑず)。

## ㋑ 形と排他(raw/01・10・12・13・14)

- 器 = raw/01_walk_pipe_rc.py(己・python os.walk・読むのみ)。根 = 樹の頂・除外 .git/node_modules/.venv/__pycache__/queue/docs/evidence・bak 名除く。註行と `#` 以降は見ぬ。深さ 樹B 10・~/bin 1・樹C 13。rc 0。刻 20:20。
- 形の網: ①count = `| wc -l|-c|-w` / `| grep -c` / `| uniq -c` / `| sort -u` / `| awk … NR` / `| tr -cd`。②subst = `$( … | … )`。③head = `| head|tail -N`。⑤rc_after = 管の行の ★直後行★ に `$?`(PIPESTATUS/pipestatus を除く)。④pipefail = file 単位で `set -o pipefail`/`set -euo pipefail` の有無。py は歩かぬ(shell の管を持たぬ・`subprocess(shell=True)` の中の管は ★測れぬ★)。
- ★形は互ひに排他でない★: 一行が ①+② / ②+③ / ①+⑤ に同時に当たる。樹B: 延べ 332(①35・②214・③83・⑤0)≠ 行 242、多重形の行 90。~/bin: 延べ 46 ≠ 34、多重 12。陽性対照の種(raw/seed_ctrl/positive_control.sh・7 行)でも 延べ 8 ≠ 行 6。形⑤は樹B・~/bin で 0(種では 1 = 網は生きて居る)。
- 陽性対照(raw/12): 種 6 行/6 当たる(定数 `echo constant | wc -l` も①に当たる=網は「失敗し得るか」を判じぬ → ㋒ の判で分ける)。

## ㋒ 判(raw/11_judgment.tsv・機械の一次判・代表を紙で検めた)

- 判の法: 管の左の命令を切り出し、`printf`/`echo` の定数なら「載らぬ(失敗し得ぬ)」、外の状態を読む命令(git/tmux/ls/cat/find/grep <file>/ps/pgrep/stat/…)なら「載る(失敗し得る)」、函数・複合(`cd … && git …`)・切り出せぬ物は「判じ得ぬ」(0 に丸めぬ)。
- 載る の左の命令 上位: grep 51・pgrep 16・tmux 14・find 10・ls 5・git 5・ps 5(合計 121)。
- 代表(載る・pipefail 無・他弾と重ならぬ・形①)= raw/15_noru_daihyou.txt(網に当たつた 4 行=樹B で形①かつ載るかつ pipefail 無かつ重なり無は 4 行のみ・多くは形②のみか他弾と重なる)。例: scripts/checks/karo_mac_gate4.sh:31 `n_staged=$(git diff --cached --name-only -- "$@" | grep -c .)` ―― git が失敗すれば n_staged=0 → 「staged が 0 file」と止まる(方向は安全側・理由は消える)。scripts/inbox_watcher.sh:1029 `tmux list-clients … 2>/dev/null | wc -l`(km-184 とも重なる)―― tmux が無ければ 0 client と読む。
- 載らぬ(111+16)の大半 = `printf '%s\n' "$x" | grep -c …`(捕へた文字列を数へる・左は失敗し得ぬ)。家老の器 karo_mac_gate7.sh の 10 行は悉く此の形 → 載らぬ(但し `f=$(cat "$@" | grep -v …)` の L5 は cat が失敗し得る → 載る 1)。
- 判じ得ぬ 26+2: 左が `cd … && git diff …`(hakudokai 系)・`cmd.exe /C …`・切り出せぬ複合。

## ㋓ 實射(raw/20・己の束)

種 = 無い file(左の `cat` は必ず rc 1)。三 shell(/bin/bash 3.2.57・~/wt/tools bash 5.2.0・/bin/zsh 5.9)で:
| 形 | rc | n | 註 |
|---|---|---|---|
| ⒜ 素の管 `n=$(cat 無 \| wc -l)` | ★0★ | 0 | 偽の rc=0(右 wc の rc)・数 0 は「空」でなく「失敗」 |
| ⒝ `set -o pipefail` 有 | 1 | 0 | 左の失敗が rc に出る |
| ⒞ bash `${PIPESTATUS[0]}` / zsh `${pipestatus[1]}` | 1(左)/ 0(右) | ― | ★名が shell で違ふ★: bash で `${pipestatus[1]}` は空・zsh で `${PIPESTATUS[1]}` は空(raw/20 に両方刷つた) |
| 形③ `seq 1 100000 \| head -1`(pipefail 有) | ★141★ | ― | SIGPIPE が rc を汚す(`yes \| head -1` も 141・PIPESTATUS=[141 0])→ pipefail は head の管には合はぬ |

## ㋔ 案(★紙のみ・据ゑぬ・変更統制★)―― 器の種類で選ぶ(一律にせぬ)

- 数へる器(形①・左が外を読む・例 karo_mac_gate4.sh:31・inbox_watcher.sh:1029・ratelimit_check.sh の 33 行の類): ★rc を素で取る形へ★ = 左の出目を先に変数へ(`out=$(git …); rc=$?`)、rc≠0 なら「判じ得ぬ」に分け、数は out から取る。理由 = 数へる器は「0」と「失敗」を分けねば偽の 0 を刷る。pipefail は `$( )` の中では効かせにくく、head を含む管では 141 を呼ぶ。
- 読む器(形③ head/tail で表示・例 ~/bin/compact_drain_inject.sh の `tmux capture-pane | tail -8`): ★${PIPESTATUS[0]}(bash)/${pipestatus[1]}(zsh)を読む★か、そのまま(表示のみ・数に載らぬ)。理由 = pipefail を置くと head の SIGPIPE 141 で偽の赤に成る。
- 定数を数へる形(載らぬ 111+16): 直す要無し(左は失敗し得ぬ)。
- 形④ pipefail 無の file 82+24: 一律に `set -o pipefail` を足すのは ★薦めぬ★(head の管が 141 で落ち、既存の `|| true` の意味が変はる)。数へる器に限り置く。
- 形⑤(管の直後の `$?`)は樹B・~/bin で 0 行 ―― 家老の掟が既に路に成つて居る面(陽性対照の種でのみ当たる)。

## ㋕ 測れぬ物

- /bin/sh の実体(macOS は bash 3.2 の sh 互換・Linux は dash)で `PIPESTATUS` が無い事は此処では走らせて居らぬ(bash/zsh のみ)。
- Linux 側に zsh が無い件・他 PC の器(main/second)・hakudokai 系の `cd … && …` の複合(判じ得ぬ 26 の大半)。
- py の `subprocess.run(…, shell=True)` の中の管・多行に割れた管・`eval` の中の管。
- 242+34 行の各々を走らせて偽の 0 を出す事はして居らぬ(實射は種の 1 形 × 3 shell + 形③ 1 件)。

## ㋖ 疵

⑴ 着手便 300 字超 1 度(318)⑵ 網は「失敗し得るか」を判じぬゆゑ定数の `echo | wc` も拾ふ(判で分けた・機械の一次判の誤りは紙で検めた代表の外では残り得る)。

## 宣⇔實

宣ETA 21:15。實 = 納め便の刻(紙の外・20:3x 見込み)。
