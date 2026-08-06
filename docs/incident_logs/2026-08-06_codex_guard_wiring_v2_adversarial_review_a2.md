# codex_exec_sandbox_guard 結線・再設計v2 反証 (足軽2号、2026-08-06・家老second下命 msg_20260806_090908_fafe122d)

**任**=足軽6号 再設計v2 (軍師second PASS済・commit ba62f7c) の穴を探す事。★同意を探さず反証を探した★。read-only・書込/commit一切せず。

## 境・限界・未測 (冒頭)

設計・guard本体・.claude/settings.json・.gitignoreいずれも編んでおらぬ。`audit_codex.sh`等を含め★一切のscriptを実行しておらぬ★
(grep/read/wc/sha256sum/git log/git status/git rev-parse/date/systemctl(read-only sub-command)/crontab -l/diff -q のみ使用)。
GO_RECORD は作成・参照とも行わず (作成=D-lane違反ゆえ絶対境界、参照=実在せぬ事のみ`ls`で確認)。
hakudokai-dev系worktreeへは一字も書いておらぬ。rcはpipeに通さず。grepは全て`/usr/bin/grep -r`系を使用。
`sudo -n crontab -l`は権限system側で拒否されたため未実施(root crontabは★未測★、下記に明記)。

測時 = 2026-08-06T09:17:07+0900 (`date -Iseconds`実行結果)。HEAD=`ba62f7cd9213dc6dfdcc12724b713c58260e8abc`(`git rev-parse HEAD`実行結果)。

★注記(断面の不安定性)★=着手時、下命本文が引く v2 の断面 (74行・sha256=a5abc7147d20a814…) は当職の着手時点で既に古かった。
当職が最初に`Read`した時点でも同じ74行版だったが、作業中に v2 doc へ「新穴①(systemd WorkingDirectory)実測」の追補が
加筆され(2026-08-06T09:12:40+0900・v2 doc内自己記載)、96行・sha256=`74fb78d5877347e7…`へ変わり、当職の作業中に
commit `ba62f7c`(軍師second PASS 09:15:03)として確定した。∴ 当職の反証は★96行・sha256=`74fb78d5877347e7…`版
(=現HEAD時点で確定・commit済の最終稿)★を対象とする。ここに断面を明記する(写しは scratchpad へ保全済)。

## 母集団宣言 (対象file・path/行数/sha256、当職実測)

| # | path | 行数 | sha256(先頭16) |
|---|---|---|---|
| v2再設計 | docs/incident_logs/2026-08-06_codex_guard_wiring_design_v2_a6.md | 96行 | 74fb78d5877347e7 |
| v1設計+追補 | docs/incident_logs/2026-08-06_codex_guard_wiring_design_a6.md | 151行 | b34de71a67819e17 |
| a1反証(v1向け) | docs/incident_logs/2026-08-06_codex_guard_wiring_adversarial_review_a1.md | 169行 | 7d264db7f3dc4f78 |
| 守本体 | scripts/checks/codex_exec_sandbox_guard.sh | 59行 | a98f6129b73e11a9 |
| 結線先① | scripts/audit_codex.sh | 136行 | b23888c3ea852563 |
| 結線先② | scripts/audit_meta_codex.sh | 349行(呼出周辺L147,158,253-264限定読解、a1と同一スコープ継承) | 7fb2fc322e05d16c |
| 結線先③④ | shim/hakudokai/hakudokai_audit_scheduler.sh | 193行(全文) | 70b7ab9ba07b3685 |

GO_RECORD (`/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record`) = ★不在確認済(ls実行・作成せず)★。

## (2) 反証 — 下命の問い ⒜⒝⒞⒟ に沿って回答

### ⒜ `$(pwd)`は誰のpwdか — v1と同じ罠の別形に落ちておらぬか

**★結論=落ちておる。但し v1(subshell)と同一機序ではなく、「現行コードを確かめずに『測っておらぬ』と決め打った」という
より根の同じ誤りである。★**

v2の中心命題(冒頭「誤りの因」+ ⒜)は「guardは現状、引数を★必須として受ける設計★であり、`$(pwd)`で自ら測る形へ
★改める必要がある★」というものである。しかし現行guard本体は以下の通り(当職`sed -n`実測、L17):

```
INTENDED_CWD="${1:-$PWD}"
```

**∴ guardは既に「引数省略時は自身の`$PWD`を既定値とする」設計になっている。v2が「新たに導入すべき」と
提案する挙動(引数省略時に自身のpwdを測る)は、★現行guard本体に既に存在する★。v2はこの1行を一度も
`sed`/`cat -n`等で引用しておらず、L11の使い方コメント`[intended_cwd]`(角括弧=一般に「省略可」を示す記法)
のみから「引数必須」と読み違えたまま設計を進めたと見える。**

**さらに重大な点**=この事実は★a1の反証(v1向け・軍師PASS済)が既に明記していた★。a1反証 ⒝ 節(L84-86)を
逐語引用する:

> 一方guard本体は`INTENDED_CWD="${1:-$PWD}"` (L17) であり、★引数を渡さねば$PWD (=まさに事故当日
> 危険だったinvoker実cwd) を既定で見る設計★になっている。設計案は明示的に`"$REPO_PATH"`を渡す事で、
> この既定の(より事故の実態に合った)挙動を★意図せず潰している★。

v1の追補(2026-08-06T09:00:23、「足軽1号の反証役レビューを受けて」と明記)はこのa1指摘を読了・応答した事が
本文からも明らかである(REPO_PATHがroot causeを代表しない、と認めた節がまさにこれへの応答)。★にも関わらず
v2は、a1が既に引用したguard.sh:17の`${1:-$PWD}`という具体的な事実を一度も引用せず、「guardを測る形へ
新たに改める」という、a1の指摘があれば不要と分かるはずの guard本体編集案を再提出した。★

**∴ v1の罠=「渡す値(REPO_PATH)が実cwdを代表しない」。v2の罠=「guardが既に実cwdを既定で見ている事実を
確かめずに、それを改めて導入しようとした」。形は違うが★『現行コードを実際に引用して確かめる前に設計を
書いた』という同じ根★に落ちている。**

**副次所見(⒞でも再掲)**=bashの`pwd`組込コマンドは既定で`-L`(logical、`$PWD`と同値を返す)であり、
`shopt`等の非標準設定が無い限り`$(pwd)`と`$PWD`は通常状態で★同一の値★を返す(当職はこれをbash一般知識で
記述しており、当PC上での`shopt`設定の実機確認はしていない=★未測★、下記自己申告に明記)。∴ `$PWD`→`$(pwd)`
の切替が実質的に防ぐ物があるとすれば「外部から`export PWD=/安全な偽path`のように注入され、実際にはcdして
いないのに`$PWD`が偽の値を持つ」ケースのみである。v2はこの脅威モデルを一度も述べておらず、★何を防ぐ変更
なのかの裏取りが無い★。

### ⒝ 4箇所の結線位置は現に其処で良いか — 己で確認

- `scripts/audit_codex.sh:92`直前 / `:93`=`npx @openai/codex exec`: 当職実測(`sed -n '88,94p'`)で一致。
  `REPO_PATH`絡みの`cd`(L33,41)は全て`$(cd "$REPO_PATH" && ...)`のsubshell内、L93は非subshell=v1/a1と同じ
  結論に達した(独自再確認・食い違いなし)。
- `scripts/audit_meta_codex.sh:263`=`npx @openai/codex exec`: 当職実測(`sed -n '253,262p'`)で一致。
  ★但し★=v2「L259直前」という記述は、`RETRY=0`(L257)`MAX_RETRY=3`(L258)`SLEEP_NEXT=1`(L259)
  `while`(L261)という並びの中で、L258とL259の間に当たる——変数初期化3行の途中に割り込む形であり、
  「loop突入直前」というなら本来はL260(空行)かL261(while)直前の方が自然である。機能上は誤りではない
  (loop外側1回・while到達前である事に変わりなし)が、v2自身が誤り根絶を掲げる文書としては挿入点の
  精度が粗い。★誤りとまでは言えぬ★ため軽微所見に留める。
- `shim/hakudokai/hakudokai_audit_scheduler.sh:125,176`: 当職実測(`/usr/bin/grep -n "^\s*cd "`)で
  非subshell `cd`は本file中★L83の1件のみ★と確認。**当職は初め「L83のcdがrun_weekly/run_on_commitの
  cwdも書き換えるのでは」と疑ったが、L83は`run_daily()`内(「5. Git unpushed check」節)にあり、
  末尾の`case "${1:-}" in daily) run_daily ;; weekly) run_weekly ;; on-commit) run_on_commit ;; esac`
  により1回の起動につき1関数のみが排他実行される事を確認し、この疑いを撤回した**(詳細は下記
  【本工区で己が直した誤り】)。∴ L125・L176の位置選択自体に構造的な欠陥は無い。

**但し★決定的な限界★=当職独自実測(`systemctl list-timers --all`・`systemctl list-units --all --type=service`・
`crontab -l`・`/etc/cron.d/`)いずれにも`hakudokai_audit_scheduler`/`audit_codex`/`audit_meta_codex`への
言及は0件(auditd.serviceのみヒットしたが無関係のLinux監査daemon)。∴ ③④の2箇所は★現に呼び手が存在しない★
——位置の当否そのものを実起動で検証する事が原理的にできない状態にある。「現に其処で良いか」という問いに
対する答は★位置は構造上妥当・但し実証はゼロ(呼び手が無い)★という、a6のv2自身の追補(09:12:40)が
`systemctl --user`限定で述べた結論と符合するが、当職は`--user`に加え root側`list-timers --all`/
`list-units --all`・`/etc/cron.d/`も確認し、より広い探索範囲で同じ結論(0件)に至った(重ねて確認=食い違いなし)。**

### ⒞ 自認3穴(WorkingDirectory依存・4箇所独立化・retry loop相互作用)で足りるか

**足りぬ。挙げられておらぬ穴を3件挙げる。**

1. **★最重要★=⒜で述べた「guardは既に`${1:-$PWD}`を持つ」という事実そのものがv2の自認穴リストに無い。**
   v2の「母集団漏れの自己申告」2件(systemd WorkingDirectory実測未了・error handling詳細設計未了)も
   この点に触れていない。設計の前提そのものが検証不足だった、という穴は、v2が自ら立てた3穴
   (⒞-1〜3)のどれとも異なる、より上流の穴である。
2. **`$PWD`→`$(pwd)`切替の脅威モデル不在**(⒜副次所見の再掲)=bashの`pwd`既定(`-L`)は`$PWD`と通常
   同値を返す。何を防ぐ変更なのかが書かれていない以上、実装時に「意味のない差し替え」と判断されて
   見送られるか、逆に「意味がある」と誤解されて本来触れるべきでない他の箇所(env注入対策等)まで
   手を広げるか、どちらの読み違いも起こり得る。
3. **③④(hakudokai_audit_scheduler.sh)は現に呼び手0件**(⒝で実測)=結線案自体は「机上で正しい」が、
   検証可能な実行経路が存在しない設計を「4箇所悉くへの結線」として1箇所目・2箇所目
   (audit_codex.sh・audit_meta_codex.sh、いずれも呼び手が明確に存在する)と同列に並べている。
   実運用への効果という観点では、4箇所は★検証可能な2箇所と検証不能な2箇所★に質的に分かれており、
   v2はこの区別を書いていない。

なお⒞-2(4箇所独立process化すべき)は当職の読解範囲では正誤いずれとも確認できず(実装されていない
設計案の当否は静的読解のみでは判定不能)、★誤りとは断じない★。

### ⒟ 誤りが無ければ「無い」と書いてよい旨について

該当せず。⒜⒞にて具体的な誤り・欠落を実測に基づき指摘した(上記参照、何を試してそう判じたかは
各節に`sed -n`/`grep -n`/`systemctl`/`crontab -l`等の実行結果を添えて記載済)。

## 【本工区で己が直した誤り】

`shim/hakudokai/hakudokai_audit_scheduler.sh` L83 の `cd "$SCRIPT_DIR"` (非subshell) を見た直後、
「run_weekly/run_on_commitのcwdもrepo rootへ固定されるのでは」と即断しかけた。しかしfile末尾の
`case "${1:-}" in daily) run_daily ;; weekly) run_weekly ;; on-commit) run_on_commit ;; esac` を
読み、L83が`run_daily()`関数内(「5. Git unpushed check」節)に限定され、1回の起動につき1関数のみが
排他実行される事を確認して、この即断を撤回した。関数境界を跨いで`cd`の影響を仮定するところであった
(これも「現行コードを実際に確かめずに設計/憶測を進める」という、本工区で摘発した誤りと同型の罠に
当職自身が一瞬落ちかけた例であり、正直に記す)。

## ★母集団漏れの自己申告★

1. `hakudokai_audit_scheduler.sh`の呼び手不在確認は、当PC(SecondPC)上の`crontab -l`(実行ユーザー
   hakudokaiのみ、root等他ユーザーの`crontab`は`sudo -n crontab -l`が権限system側で拒否され★未測★)・
   `systemctl --user`/`systemctl`(root含む全体)の`list-timers --all`/`list-units --all --type=service`・
   `/etc/cron.d/`に限定。他PC(main_pc/third_pc)経由の呼出、Windows側タスクスケジューラ経由の呼出は
   確認範囲外(★未測★、0件と断じない)。
2. `scripts/audit_meta_codex.sh`は349行中、呼出周辺(L147,158,253-264)のみ読み、全文は未読
   (a1の同一スコープ限定を継承・当職独自には広げていない)。
3. bash `pwd`組込の`-L`/`-P`挙動は一般知識(bash manページ相当)に基づく記述であり、当PC上のbashで
   `shopt`等の非標準設定が入っていないかは実機で`shopt -p`等を実行して確認していない(★未測★)。
4. `.claude/settings.json`のPreToolUse hookとしてguardが将来登録される経路(script直呼び以外)は
   本反証の範囲外(a1の自己申告と同一のスコープ限定を継承)。
5. `/home/hakudokai/multi-agent-shogun/`(本repo外の同名file)との`diff -q`は差分0件を確認したが、
   両者が独立clone/worktreeか symlink/hardlinkかまでは確認していない(★未測★、本工区の主題外と判断し
   深追いせず)。

## 総括

反証結果=★通す(PASS)★としては渡せぬ。中心理由=⒜=v2の中心命題「guardは現状測っておらぬので測る形へ
改める」は誤り(guard.sh:17に既定`${1:-$PWD}`が現に在る、当職`sed -n`実測)。この事実はa1の反証
(v2の設計者自身が読了・v1追補で応答済)に既に逐語引用されていたにも関わらず、v2はこれを一度も引用・
反映せず、不要な guard本体編集(★裁可要=下命でも編集を禁じている箇所★)を「新たな設計」として
再提出した。加えて結線先③④(hakudokai_audit_scheduler.sh)は現に呼び手が存在せず、位置の当否を
実証する経路が無い。裁定は当職の任ではない(下命「裁定するな」に従い、事実の指摘に留める)。

## 監査体制

暫定二者制(軍師second + Gemini)。Codex leg停止中(2026-07-21事案)。

以上、足軽6号 結線再設計v2への反証応答。実装・commit・裁定はいずれも行っていない。
