# km-187 ―― 数へる流れに stderr を混ぜる器(`2>&1`)の census(紙のみ・直さぬ・据ゑぬ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `km-187-kazoeru-nagare-ni-stderr-wo-mazeru-utsuwa-20260918`(家老mac 発・裁332455・L4・据ゑ 19:53)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T19:57:49+0900 / 着手便 19:52(宣ETA 20:40)/ 測り 19:52〜19:56
- 枝 = `ashigaru-mac-1/km-187-kazoeru-nagare-ni-stderr-wo-mazeru-utsuwa-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km187・km-184 と混ぜず)。押さず。
- 出所 = 家老の疵(`git show <ref>:<束>/MANIFEST.txt 2>&1 | grep -c ''` が fatal の 1 行を数へ「臺帳=1 行」・正 32)。★km-184 ㋓(`2>/dev/null` = 悲鳴を捨てる)とは別の形 = `2>&1`(悲鳴を数に混ぜる)。同じ器が両方持つ物は両紙に別々に書く。★

## ㋐ 結語

- 母數(raw/10・11・13): `2>&1` の行 = 樹B(origin/main) 169 行 / 樹C(共有・読むのみ) 317 行 / ~/bin 5 行。其の内 ★数へる流れへ繋ぐ形★(grep -c・wc・sort -u・変数へ捕へて比べる)= ★樹B 22 行 / 9 file・樹C 27 行 / 16 file・~/bin 1 行 / 1 file(家老の器 karo_mac_template.sh)★。python の `stderr=subprocess.STDOUT` は三根とも 0。
- 判(㋑): 載る 3 件(karo_mac_gate4.sh L20・diagnose.sh L278・家老の手本の形)/ 条件付 2 件(karo_mac_dasumae_gate.sh L154・~/bin/karo_mac_template.sh L12)/ 載らぬ 17 件(意図した stderr 捕へ・表示のみ・rc のみ)。
- 實射(㋒・己の束のみ): ⑴家老の手本 = 正 5 行の種 manifest を誤つた名で `2>&1 | grep -c ''` → ★1★(偽)・`2>/dev/null` → 0(km-184 の形)・rc 素採り → 1・err 別 file → 数 0 + err 1 行(raw/20)⑵ karo_mac_gate4.sh を壊れ git 種で → 「條④ diff --check が落ちた ―― ★1 行★」= git の fatal を末尾空白の行と数へた(正 0・但し rc≠0 で止まる=fail-closed・raw/22)⑶ diagnose.sh の管を写して → checks 数 ★3★(正 2・ls の悲鳴が name=output の check に・status info ゆゑ赤く成らぬ・raw/23)。
- 案(㋕)は器ごとに「rc 素採り」か「out/err 別 file」かを分けて ㋔ に。据ゑず。

## ㋑ 母數の作り方

- 器 = raw/01_walk_stderr_into_count.py(己・python os.walk・ugrep/.gitignore に依らぬ・読むのみ)。根 = 樹の頂(除外 .git/node_modules/.venv/__pycache__/queue/docs/evidence・bak 名除く)。深さ 樹B 10・樹C 13・~/bin 1。file 樹B 517・樹C 1595・~/bin 93。rc 0。刻 19:52〜53。
- 「数を取る流れ」の網 = 同じ行で `2>&1` の後ろに `| grep -c`/`| wc -l|-c`/`| sort -u`/`| uniq -c`/`| head|tail`(count_pipe)、又は `var=$( … 2>&1 … )`(var_capture・後で比べ得る)、py は `stderr=subprocess.STDOUT`。★網の外★: 別行で捕へた変数を数へる形(`x=$(cmd 2>&1)` の次の行で `wc`)は var_capture で拾ひ文脈で判じたが、pipe を跨ぐ多行の形・`exec 2>&1` の形は拾へぬ(測れぬ)。
- 陽性対照(raw/12): 己の種 raw/seed_ctrl/positive_control.sh(5 形)+ .py(1 形)= 6/6 当たる。

## ㋒ 各件の判(樹B 22 行 + 樹C のみ + ~/bin)

| 器:行 | 形 | 混ざつた stderr は数に載るか | 譯 |
|---|---|---|---|
| scripts/checks/karo_mac_gate4.sh:20-23 | `out=$(git diff --cached --check 2>&1); rc=$?; n=$(… grep -c .)` | ★載る★ | git の fatal/warning が「條④ の行数 n」に足される(實射 raw/22: 正 0 → 1)。rc≠0 で止まるゆゑ方向は安全側だが ★数は偽★ |
| scripts/diagnose.sh:278-292 | `diag_output=$(bash -c … 2>&1 \|\| true)` → python が行毎に checks を積む | ★載る★ | 悲鳴の行が name=output・status=info の check に成り checks 数が増える(写しの實射 raw/23: 2 → 3)・赤く成らぬ |
| scripts/checks/karo_mac_dasumae_gate.sh:154 | `fks=$(python3 … 2>&1); fks_rc=$?` → `fk2=${fks%% *}` を数と検める | 条件付 | rc 0 で stderr に警告(例 DeprecationWarning)が出れば fks の頭が非数 → 「測れぬ・default-deny」で止まる=偽の止(数には載らず・通しもせぬ)。rc≠0 は先に止まる |
| scripts/checks/karo_mac_dasumae_gate.sh:251(樹C 233・家老樹 90 は写し) | `out=$(check_one_file 2>&1); rc=$?` | 載らぬ | out は rc≠0 の時 stderr へ刷るのみ・数へぬ |
| scripts/inbox_write.sh:40(樹C 83) | `_DG_OUT=$(… python3 "$_DG" 2>&1) \|\| _DG_RC=$?` | 載らぬ | _DG_OUT は rc 10 の時の文言のみ・判は rc |
| first_setup.sh:266/275/433 | `X=$(python3 --version 2>&1)` 等 | 載らぬ | 表示と `*"not found"*` の字面比べ(意図した stderr 捕へ・数でない) |
| scripts/box_pdf_to_png.sh:19・visual_env_setup.sh:29/48 | `cmd -v 2>&1 \| head -1` | 載らぬ | 版の表示のみ(head は count でない・網が拾つた=網の粗) |
| scripts/checks/tests/karo_mac_dasumae_gate_negative_test.sh:53〜143(10 行) | `e=$(… 2>&1 >/dev/null); rc=$?` | 載らぬ | ★stdout を捨て stderr だけを捕へる意図★・grep -q で字面を検める・数でない |
| tests/checks/dd169_kill_term_guard/smoke_test.sh:35 | `actual_rc=$(… >/dev/null 2>&1; printf '%d' $?)` | 載らぬ | rc のみ |
| ~/bin/karo_mac_template.sh:12(家老の器・除かず) | `raw=$(sh ~/bin/sb read seq "$1" 2>&1 \| grep -E '^  content:' \| cut -c12-); n=$(… grep -o '"' \| grep -c .)` | 条件付 | 悲鳴は `^  content:` の網で落ちるゆゑ普段は載らぬ。sb が壊れ stderr に `  content:` で始まる行を吐く路は無い(読んだ限り)→ 載らぬに近いが、sb の失敗時 raw が空に成り n=0 が「引用符 0」と読まれる(失敗と 0 の区別無し)= 条件付 |
| 樹C のみ: reports/mac/20260907/ashigaru-mac-3_B6-8_20260907/dino-check.sh:23〜106(6 行) | `VITEST_OUT=$(npx vitest … 2>&1)` → `grep -E "Test Files\|Tests"` で要約 | 条件付(記録・席3 の紙の中の script・配られた器ではない=別勘定) | 要約は grep の網で絞る・rc は別に採る(VITEST_RC)= 載らぬ寄り。走らせぬ(DentalBI の npx) |

載る 2(+手本 1)/ 条件付 3 / 載らぬ 17。

## ㋓ 實射(己の束のみ・raw/20・22・23)

- 手本(raw/20): 種 raw/seed_ctrl/km187_manifest.txt(5 行)。`cat 誤名 2>&1 \| grep -c ''` = ★1★ / `2>/dev/null` = 0 / rc 素採り = 1(無い)/ `2>err.txt \| grep -c ''` = 0 + err 1 行。★偽の数 1 と正の数 5 を並べた。★ git 形 `git show HEAD:<束>/MANIFEST.txt 2>&1 \| grep -c ''` も 1(fatal)。
- gate4(raw/22): 種 raw/seed_ctrl/brokengit(`.git` file が無い gitdir を指す・末尾空白 0 本)→ 器の告げ「條④ diff --check が落ちた ―― 1 行」+ fatal。正の数 0・偽の数 1。対照 = 己の樹では「條④ diff --check = 0」。
- diagnose(raw/23): 器は env/引数を要し其の儘走らせぬゆゑ ★同じ管を写した★(条件付の實射)。`echo a=1; ls /nonexistent; echo b=2` → checks 3(正 2)。

## ㋔ 案(★紙のみ・据ゑぬ・変更統制★)―― 何を / なぜ / 戻し方 / どちらの法が合ふか

1. scripts/checks/karo_mac_gate4.sh L20: 何を = `out=$(git diff --cached --check -- "$@" 2>err); rc=$?` の様に ★err を別 file(又は別変数 `2> >(…)`)★ にし、n は out だけで数へ、err が非空なら「判じ得ぬ」として別の行で止める / なぜ = 悲鳴が 條④ の行数に化ける / 戻し = 1 行を元へ。★合ふ法 = out と err を別に★(数は out にしか無い)。rc 素採りは既に在る(rc=$?)。
2. scripts/diagnose.sh L278: 何を = `bash -c … 2>"$err_tmp"` にし err は checks に status=error で一つの項として積む / なぜ = 悲鳴が info の check に化ける / 戻し = 1 行を元へ。★合ふ法 = 別 file★(構造化する器ゆゑ混ぜると構造が壊れる)。
3. scripts/checks/karo_mac_dasumae_gate.sh L154: 何を = `fks=$(… 2>"$err")` にし err 非空なら「測れぬ」の告げに err の頭を添へる / なぜ = 今は非数で止まるが理由が読めぬ / 戻し = 1 行。★合ふ法 = rc 素採り(既在)+ err 別★。止まる方向は今も正。
4. ~/bin/karo_mac_template.sh L12(家老の器・案のみ・當席は触らぬ): 何を = `sb read` の rc を素で採り rc≠0 なら n を出さず「読めぬ」と刷る / なぜ = 失敗と 0 の区別が無い / 戻し = 函数 1 本。★合ふ法 = rc 素採り★(数は grep の網で守られて居る)。
5. 家老の手本(手順・器でない): 臺帳を数へる時は `git show ref:path > out 2> err; rc=$?` の三点(rc・out・err)を別に採る。★合ふ法 = 両方★。

## ㋕ 測れぬ物(推量で埋めぬ)

- 走らせられぬ器: scripts/diagnose.sh(env・引数)・first_setup.sh(sudo/apt)・visual_env_setup.sh(npx)・席3 の dino-check.sh(DentalBI の npx/playwright)・~/bin/karo_mac_template.sh(sb の DB 読み・家老の器)。判は code の読み。
- 他 PC の器(main/second の scripts・~/bin)は歩いて居らぬ。
- 網の外の形: 多行で捕へて数へる形・`exec 2>&1`・関数の中で stderr を stdout に流す形。
- 樹C の other 290 行・樹B 147 行の `2>&1`(数へぬ形)は数へたが一件づつ判じて居らぬ。

## ㋖ 疵

⑴ 網が `\| head -1` を count と拾つた(表示の 3 行・粗・紙で除いた)⑵ 種 brokengit は `.git` file を持つゆゑ commit・臺帳の外(消さず・raw/seed_ctrl の他の紙は臺帳に載す)。

## 宣⇔實

宣ETA 20:40。實 = 納め便の刻(紙の外・20:0x 見込み)。
