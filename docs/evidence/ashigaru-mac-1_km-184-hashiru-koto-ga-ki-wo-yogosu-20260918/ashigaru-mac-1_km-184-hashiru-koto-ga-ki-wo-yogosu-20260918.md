# km-184 ―― 走らせる事が樹を汚す器と、stderr を捨てる形(直さぬ・据ゑぬ・紙のみ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `km-184-hashiru-koto-ga-ki-wo-yogosu-20260918`(家老mac 発・裁332455・㋑は裁333488⑵で狭まる・据ゑ 19:30)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T19:47:47+0900 / 着手便 19:42(宣ETA 21:00)/ 測り 19:42〜19:46
- 枝 = `ashigaru-mac-1/km-184-hashiru-koto-ga-ki-wo-yogosu-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km184・km-181/182 と混ぜず)。押さず。
- 先に家老の疵(㋐)を受ける: 臺帳の名は `<件名>_manifest.txt`・正 32 行 = 當席の 30(path 行)と合ふ。當席の 19 は誤りで正は 20(裁333488・訂正便 seq333526)。

## ㋐ 結語

1. ★㋑ 20 本表(raw/10)★: 20 本の内 19 本は mtime ★19:20:31★ で unit 全走の窓(19:20:26〜19:22:04)の内 = tests/unit/test_build_system.bats → scripts/build_instructions.sh が書いた(diff は各 +数十〜+300/−数十〜−100 行)。残る 1 本 docs/runbooks/ERR-EKARTE-001.md は mtime 19:14:18(樹を切つた刻)= ★case-fold の双子★であり走りの手ではない。20 が正(裁)・差の一本は之。
2. ★㋒ 走るだけで樹へ書く器★: 静的網(raw/20・字面)は候補を sh 8 file / bats 13 file / py 20 file と出すが、★本例の test_build_system.bats は静的網に 0★(書くのは呼ばれた script で、test の字面に書く形が無い)。動的實射(raw/21・己の束の写しの根)で ★build_instructions.sh を走らせるだけで 19 の出力候補の内 16 本の sha が変はり、rc 1 で落ちても書く★。∴ 「試験は読むだけ」ではない實例。
3. ★㋓ stderr を捨てる形★: scripts/lib/hooks の `2>/dev/null` = ★367 行 / 54 file★(raw/30)。形① `$( … 2>/dev/null | wc -l)` 7 行(数へる番人の前で捨てる=失敗が 0 に化ける)/ 形② `if … 2>/dev/null; then` 8 行 / 形③ subshell 末尾 `) 200>… 2>/dev/null` 3 行(悉く inbox_watcher.sh)/ 形④ 全捨て 3 行。★實射で鳴らぬ事を示した一件★ = ephemeral_worktree_hygiene.sh L19: git が fatal(rc 128)を吐く dir を 2>/dev/null が黙らせ wc -l が 0 → 「掃ける」に落ちる(raw/31)。二件目 = inbox_watcher.sh L400 の形③(km-181 で WARN が捨てられた實例・raw/50 round1)。
4. 案は ㋔(据ゑず・変更統制の形)。

## ㋑ 20 本表(raw/10_nijuu_pon_hyou.tsv・源 = hosei_181 の控 /Users/momizimac/wt/a1-km181-hosei-bak-20260918T194028/12_mae_sha_bytes_mtime.tsv)

列 = path / mtime / HEAD(f2c62730)との diff 行数(+/−) / bytes / sha256(16) / 書いた走り。要約: 19 本 = 19:20:31・unit 全走の窓の内・書き手 test_build_system.bats→build_instructions.sh / 1 本 = docs/runbooks/ERR-EKARTE-001.md・19:14:18・case-fold 双子。數の是非は論ぜぬ(裁 seq333488⑵)。hosei_181 で 20 本を名指し restore 済(後 porcelain 1 行 = 双子)。

## ㋒ 走るだけで作業樹へ書く器(raw/20・21)

- 静的網: 己の器(python os.walk・根 = 樹の頂・除外 .git/node_modules/.venv/__pycache__/queue/docs/evidence・file 517・深さ 10・rc 0)。字面 = `> $PROJECT_ROOT…`/tee/cp/mv/sed -i/git add|commit|mv|rm|checkout|restore(sh・bats)、open(…,'w')/yaml.dump/write_text/shutil/os.replace(py)。同行に tmp の印(BATS_TMPDIR/mktemp/TEST_TMPDIR/tempfile)が無い行を「REPO?」候補に。
  | kind | 行 | file | REPO? |
  |---|---|---|---|
  | sh | 25 | 8(first_setup.sh 10・shutsujin_departure.sh 5・tests/e2e/helpers/setup.bash 5・他 5 本 1 づつ) | 25 |
  | bats | 33 | 13(e2e 11・unit 2 = test_ntfy_ack/test_ntfy_auth: 何れも `cp $PROJECT_ROOT/… $mock_dir/` = 読む方向・誤検出) | 33 |
  | py | 63 | 20(tests/*.py 6・shim/hakudokai 8・scripts/checks/karo_mac_manifest_append.py 4 …) | 63 |
  ★静的網は「書く形」を持つ行を拾ふだけで「何処へ書くか」を判じ得ぬ★(REPO? は候補)。★本弾の實例 test_build_system.bats は 0 行★ ―― 書くのは呼ばれた build_instructions.sh(ROOT_DIR/instructions/generated へ `>`・raw/21 の呼び手欄)。∴ 呼び手の鎖を辿らぬ静的網は此の型を捕へられぬ(疵として名指す)。
- 動的實射(raw/21・★己の束の内★): scripts/build_instructions.sh と instructions/・AGENTS.md・.github/copilot-instructions.md・agents/default/system.md の写しを raw/seed_build/ に置き(ROOT_DIR = dirname(SCRIPT_DIR) ゆゑ写しの根に書く)、走らせるだけ → ★rc 1(  ⚠️  CLAUDE.md not found. Skipping AGENTS.md generation.)★ なのに 出力候補 19 の内 ★16 本の sha と mtime が変はつた★(instructions/generated/*.md 16 本)。AGENTS.md 等 3 本は rc 1 で其処へ届かず不変。⑴書く物 = instructions/generated/*.md(+AGENTS.md・copilot-instructions.md・system.md)⑵呼び手 = tests/unit/test_build_system.bats L44 `run bash "$BUILD_SCRIPT"`(PROJECT_ROOT = repo の根・tmp 無し)と .github/workflows/test.yml(build-check)⑶ 實射 = 前後の mtime/sha raw/21_build_mae.txt・21_build_ato.txt。
- tmp を全く使はぬ bats = 4 紙(test_build_system / test_codex_guard / test_safe_nudge / tests/test_section18_roles)。内 書くのは build のみ(他は読む)。

## ㋓ stderr を捨てる形(raw/30・31)

- 母數: `/usr/bin/grep -rnE '2>\s*/dev/null' scripts lib hooks --include=*.sh *.py *.bash`(bak 除く)= 367 行 / 54 file。上位 = inbox_watcher.sh 78・switch_cli.sh 23・ratelimit_check.sh 20・agent_health_check.sh 19・cli_adapter.sh 19・karo_overload_monitor.sh 17・pane_identity.sh 15。悉くを一件づつ判ずるのは本弾の器では成らぬ(★367 の各々に番人が在るかは測つて居らぬ★)。形で分けた:
  | 形 | 行 | 捨てられる告げ | 依る番人 | 盲か |
  |---|---|---|---|---|
  | ① `$( … 2>/dev/null \| wc -l)` | 7(hygiene L9/L19/L20・switch_cli L68・inbox_watcher L1029・box_pdf L30・archive dead_letter L136) | 命令の失敗(fatal/権限/無い path) | 数(0 か否か)で判ずる if | ★現に盲★(下 實射)―― 失敗が「0 本」に化ける |
  | ② `if … 2>/dev/null; then` | 8 | 失敗の理由 | rc | 半盲(rc は残る・理由は消える) |
  | ③ `) 200>"$LOCKFILE" 2>/dev/null` | 3(inbox_watcher.sh L400/528/567) | subshell の中の ★悉くの stderr★(python の例外・WARN) | log を読む人・番人 | ★現に盲★(km-181: WARN が捨てられ負テスト A1 が落ちた・raw/50 round1) |
  | ④ `>/dev/null 2>&1` | 3 | 全て | ― | 意図した黙り(判じぬ) |
- ★實射(raw/31)★ 器 = ephemeral_worktree_hygiene.sh L19。種 = 己の束の raw/seed_hyg/.claude/worktrees/tmp-brokengit(`.git` file が無い gitdir を指す)。直に `git -C 種 status --porcelain` → ★fatal: not a git repository: (null)・rc 128★。器の中では 2>/dev/null が之を捨て `wc -l` = 0 → dirty=0 → mtime 新なら「生きて居る 1」・2 日前なら ★「掃ける 1」★。∴ git が判じ得ぬ dir を「中身 commit 済」と数へる番人が現に盲。v1(raw/31 round1)は種を己の樹の内の素の dir にした為 git が親 repo へ遡り fatal に成らず「持主の言 1」と鳴つた(疵・控を残す)。
- 対照(鳴る側): 2>/dev/null を外した同じ命令は stderr を立て rc 128。

## ㋔ 案(★紙に書くのみ・据ゑぬ・変更統制 = 委員長の事前許可★)―― 器ごと 何を/なぜ/戻し方

1. tests/unit/test_build_system.bats: 何を = build を走らせる前に PROJECT_ROOT の instructions/ と出力 4 種を $BATS_TEST_TMPDIR へ写し、$BUILD_SCRIPT の写しを其処から走らせる(ROOT_DIR は SCRIPT_DIR の親ゆゑ写しの根に書く)/ なぜ = unit 走が作業樹の 19 紙を書き換へる(km-181 raw/70・本弾 raw/21)/ 戻し方 = test の setup を元へ(1 file の revert)。直さぬ = build_instructions.sh 本体。
2. scripts/checks/ephemeral_worktree_hygiene.sh L19: 何を = `git -C $d status --porcelain` の rc を別に取り、rc≠0 なら「判じ得ぬ」として OWNED に数へる(2>/dev/null は残してよい・rc を捨てぬ)/ なぜ = fatal が dirty=0 に化け「掃ける」に落ちる(raw/31)/ 戻し方 = 一行を元へ。直さぬ = 閾・exit 0。
3. scripts/inbox_watcher.sh L400/528/567 形③: 何を = `2>/dev/null` を `2>>"$SCRIPT_DIR/logs/inbox_watcher_${AGENT_ID}.stderr.log"` 等の log へ(捨てず溜める)/ なぜ = python の例外・WARN が悉く消える(km-181 實例)/ 戻し方 = 3 行を元へ。★稼働中の watcher は古い inode を読む・止めぬ・入れ替へぬ★。
4. 静的網の穴: 何を = 「呼び手の鎖」(test → script)を辿る器か、動的に「bats を走らせた前後の porcelain+ls-files --others --ignored の差」を取る器を CI の unit step の後に置く/ なぜ = 本型は字面で捕へられぬ/ 戻し方 = step を外す。

## ㋕ 意味せぬ事・測れぬ物

- 367 行の 2>/dev/null の各々に番人が在るかは測つて居らぬ(形で分け、實射は 1 件+km-181 の 1 件)。
- 静的網の REPO? は候補であり書く先を判じて居らぬ(ntfy 2 紙は読む方向の cp = 誤検出と読んだ・他は判じぬ)。
- 動的實射は build_instructions.sh のみ。e2e 11 紙・first_setup.sh・shutsujin_departure.sh は走らせて居らぬ(走らせれば樹の外へ書く恐れ)。
- rc 1 の因は写しの根に不足が在るか main の build の疵か判じぬ(raw/21_build_run.out の末尾を紙に写した)。

## ㋖ 疵

⑴ 着手便 300 字超 2 度(350/330)⑵ hygiene 實射 v1 で種を素の dir にし git が遡つた(round1 控)⑶ 静的網は本例を 0 と数へた(穴を名指した)⑷ raw/seed_hyg は `.git` file を持つゆゑ commit・臺帳の外(消さず)。

## 宣⇔實

宣ETA 21:00。實 = 納め便の刻(紙の外・19:5x 見込み = 約 1 時間 早い)。
