# km-182 ―― porcelain に凭れて居る器を歩き出し、盲の条件を實射で示す(直さぬ・据ゑぬ・紙のみ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `km-182-porcelain-ni-motareru-utsuwa-20260918`(家老mac 発・裁332455・板の行は家老が起票を乞ふ seq333230・据ゑ 19:15)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T19:35:06+0900 / 着手便 19:29(宣ETA 20:15)/ 測り 19:28〜19:33
- 枝 = `ashigaru-mac-1/km-182-porcelain-ni-motareru-utsuwa-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km182・km-181 の枝と混ぜず)。押さず。
- 出自 = km-180: 共有樹 150 束の内 差>0 133 束 12382 本・盲(差>0 且つ porcelain 0 行)96 束。因 = .gitignore:7 の裸 `*` と porcelain が追跡外 dir を一行に畳む二つ。本弾は「誰が凭れて居るか」。

## ㋐ 結語

- ★repo(origin/main 6bde7170)の中で porcelain / -s / --short を呼ぶ ★器★ は 2 本★: ⑴ scripts/checks/ephemeral_worktree_hygiene.sh L19 ⑵ shim/hakudokai/hakudokai_git_guard.py L160/L212/L360(3 箇所)。他は紙(md 1)と記録(txt 1)。共有樹(席3 の枝・読むのみ)では同じ 2 本 + 其の写し(.claude/worktrees/karo-mac-a1 = 家老の樹・触らず)、紙 md 31 行/25 file・記録 other 18 行/13 file(reports/mac の raw・backups・gate の manifest.txt)。~/bin(家老・総監督の器)は 0 行。
- ★實射★: 器⑴ は盲 ―― 伏せられた追跡外 1 本を抱いた樹を dirty=0 と数へ「生きて居る」→ 24 時間経てば ★「掃ける」★ に落とす(raw/20 状態C)。追跡済を一字直せば「持主の言が要る」1 で鳴る(状態B)。器⑵ は盲 ―― `status` の「Uncommitted changes: 0」(disk には追跡外 2 本・raw/21)。但し ★器⑵ の auto_pull / wip_commit の盲は害が薄い★(㋒)。
- 代器へ移す案(据ゑぬ)= ㋓。

## ㋑ 問ひ㋐ 母數(raw/01・10・11・12・13)

- 歩き = 己の器 raw/01_walk_porcelain_callers.py(python os.walk・ugrep/.gitignore に依らぬ)。根 = 樹の頂。除外 = .git / node_modules / .venv / __pycache__ / ★queue(13.2GB)★ / ★docs/evidence(束)★。深さ: 樹B 10・樹C 13。file: 樹B 517・樹C 1595。rc 0。
- 網 二重: 網一 = `git [-C x] status … (--porcelain|-s|--short)` の字面 / 網二 = python の list 形 `"status", "--porcelain"`(★網一だけでは器⑵を 0 と数へた★ = 疵⑵)。陽性対照 = 己の種 raw/seed_ctrl/positive_control_forms.txt(7 形・7/7 当たる・raw/12)。
- 勘定は file の拡張子で分ける(md の中の引用は器ではない・別勘定):

| 樹 | sh(.sh/.bash/.bats) | py | md(紙) | yaml | other(txt/bak/manifest) |
|---|---|---|---|---|---|
| B = 己の樹(origin/main 6bde7170) | 1 行 / 1 file | 3 行 / 1 file | 1 行 / 1 file(CLAUDE.md L489 の文言) | 0 | 1 行 / 1 file(docs/codex_audits/…txt) |
| C = 共有樹(席3 の枝・読むのみ) | 2 行 / 2 file(同じ器と其の家老樹の写し) | 6 行 / 2 file(同) | 31 行 / 25 file | 0 | 18 行 / 13 file |
| ~/bin | 0 行(bak 含めても 0 file) | | | | |

器の逐語(樹B): `dirty="$(git -C "${d}" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"`(hygiene L19)/ `status = run_git("status", "--porcelain", "-z")`(guard L160 auto_pull)/ `status = run_git("status", "--porcelain")`(L212 wip_commit・L360 show_status)。全行 = raw/10_callers_treeB.tsv・11_callers_treeC.tsv。--ignored を併記する行は樹B 0・樹C 2(共に dashboard.md の紙)。

## ㋒ 問ひ㋑ 實射(raw/14・20・21)

- 種 = 己の束の内に作つた scratch git repo `raw/seed_repo/.claude/worktrees/tmp-seed`(.gitignore は裸 `*` のみ・追跡 2 本)。★束の内に「伏せられぬ追跡外の紙」は作れぬ★(raw/14: 束下の仮想 path は悉く .gitignore:7:* rc0)ゆゑ、二形は「伏せられた追跡外」と「追跡済を一字直す」で示した。
- 器⑴ ephemeral_worktree_hygiene.sh(REPO=種の親・実の DentalBI/.claude/worktrees は歩かせず):
  | 状態 | porcelain 行 | ls-files --others --ignored | 器の出目 |
  |---|---|---|---|
  | A 伏せられた追跡外 1 本 | 0 | 1 | 一時樹 1(掃ける 0 / 持主の言 0 / ★生きて居る 1★)rc0 |
  | B 追跡済を一字直す | 1 | 1 | ★持主の言が要る 1★(鳴る) |
  | C A に戻し mtime を 2 日前に | 0 | 1 | ★掃ける 1★ ← 盲の實害の形: 伏せられた紙を抱いた樹が「中身 commit 済」と数へられ掃く候補に |
  ∴ 器⑴ は現に盲。「掃ける」の定義(L13「中身が commit 済(porcelain 0)」)が porcelain に凭れて居る。
- 器⑵ hakudokai_git_guard.py(写しを種 repo に置き PROJECT_ROOT=種・action は `status` のみ・auto-pull/wip-commit は remote と /tmp の log に触るゆゑ走らせぬ):
  状態A(伏せられた追跡外 2 本)→ `Uncommitted changes: 0`(盲)/ 状態B(追跡済一字)→ 1(鳴る)/ 戻し → 0。
  ★呼んで居るが盲に成らぬ(害の薄い)理由★: auto_pull は「porcelain 空なら pull」―― 伏せられた追跡外は pull で壊されぬ(追跡外は merge の対象外)ゆゑ盲でも安全側。wip_commit は「porcelain ≥3 行で WIP commit」―― 伏せられた紙は数へられぬが ★伏せられた紙を WIP commit すべきでもない★ゆゑ盲が正しい側に働く。show_status の数だけが人を誤らせる(0 と言ふ)。
- 片付け: 種 repo は ★入れ子 .git を持つゆゑ commit に入れず・臺帳にも入れず(raw/seed_repo は臺帳外と宣す)★。消すは家老の裁(消さぬ・第一条)。

## ㋓ 問ひ㋒ 代器へ移す案(★紙に書くのみ・据ゑぬ・変更統制=委員長の事前許可が要る★)

km-180 で 155/155 一致した三本: `git ls-files --others --exclude-standard` / `--others --ignored --exclude-standard` / `--deleted`。

- 器⑴ scripts/checks/ephemeral_worktree_hygiene.sh L19
  ⑴ 直す = `dirty` を「porcelain 行数 + `git -C $d ls-files --others --ignored --exclude-standard | wc -l`」の和に(逐語: `dirty=$(( $(git -C "${d}" status --porcelain 2>/dev/null | wc -l) + $(git -C "${d}" ls-files --others --ignored --exclude-standard 2>/dev/null | wc -l) ))`)→ 伏せられた紙を抱いた樹は「持主の言が要る」に落ちる。
  ⑵ 戻し = 其の一行を元へ(git revert / 元の行を cp)。
  ⑶ 直さぬ = 24 時間の閾・warn の閾(20Gi・10 本)・GATE の検め・「止めぬ(exit 0)」の性質。
  捕へられぬ物(除いて明示・母數には数へる)= 追跡済の改め(porcelain が数へる=併用で捕へる)/ 入れ子 .git(ls-files は境で止まる → 種 repo の様な入れ子は「中身 0」と見える)/ symlink 先 / 空 dir / 改行名(行数器)。
- 器⑵ shim/hakudokai/hakudokai_git_guard.py show_status L360
  ⑴ 直す = 「Uncommitted changes」の隣に `ignored-untracked: N`(`run_git("ls-files","--others","--ignored","--exclude-standard")` の行数)を一行足す。auto_pull(L160)・wip_commit(L212)は ★直さぬ★(盲が安全側に働く・㋒)。
  ⑵ 戻し = 足した一行を消す。
  ⑶ 直さぬ = auto_pull / wip_commit の判・閾 WIP_MIN_CHANGES 3・/tmp の health/log の置場(別件)。
  捕へられぬ物 = 器⑴ と同じ + hakudokai(second PC)で走る器ゆゑ ★此の Mac の實射は写しの出目であり、実機の cwd/PROJECT_ROOT では測つて居らぬ★。
- ★据ゑる手は打つて居らぬ。★ 本紙は許可を請へる形(逐語の差・戻し・直さぬ物・捕へられぬ物)まで。

## ㋔ 意味せぬ事・測れぬ物

- 「器 2 本」は origin/main の樹と共有樹の走査。~/bin は 0 だが、別 PC(main/second)の器・cron・hook は歩いて居らぬ。
- 網一・二の外の形(例: `git status` を変数に組む `$GIT status $OPTS`・`porcelain` を別行に置く)は拾へぬ。
- md 31 行は紙の引用であり、其の紙の主が porcelain に凭れて判を書いたかは別問(数へたが判じぬ)。
- 器⑵ の auto-pull / wip-commit は走らせて居らぬ(remote・/tmp log)。判は code の読みに依る。

## ㋕ 疵

⑴ 着手便 300 字超 3 度(360/324/276)―― ★km-180 と同じ壁を叩いた★ ⑵ 網一だけで器⑵(list 形)を 0 と数へ、陽性対照の種で穴に気づいて網二を足した ⑷ 陽性対照の初回は根を束全体にし己の tsv を雑音に拾つた(種 dir だけで取り直し・raw/12)⑸ 種 repo の入れ子 .git を束に残した(臺帳外・消さず)。

## 宣⇔實

宣ETA 20:15。實 = 納め便の刻(紙の外・19:3x 見込み = 宣より約 40 分 早い)。
