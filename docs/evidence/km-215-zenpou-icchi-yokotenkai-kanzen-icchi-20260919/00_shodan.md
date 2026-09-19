★km-215 ―― 前方一致の横展開 ―― 專任2 納め紙(改訂版・裁 seq339623 REVISE 対応)★

■改訂の經緯
  初版は雛形①〜⑦を受入条件⑴〜⑺に一對一で對應させた爲、①③④⑤⑥が字面の上で
  消えて見えた(裁 seq339623 REVISE 逐語「⑥再正欠」・十項目指摘)。
  本改訂は★雛形①〜⑦★と★受入条件⑴〜⑺★を★別立ての節★に分け、雙方を漏れなく充たす。

────────────────────────────────────────────────────
■判定束 ①〜⑦(雛形v1.1・委員長 seq335106 逐語準據)

① ★対象 tuple★
  ★本節には書かぬ★ ―― 紙は己を含む數(本弾の最終commit/tree/parent)を書けぬ故、
  最終彫り(本改訂の commit)確定後、LETTER(`sb-ashigaru-mac-2 write letter`)にて
  ref・commit40・tree40・parent を宣する(karo-mac 明示指示・裁 seq339623)。
  ★對象file自體の前後sha256★(自己言及に非ず・既に確定濟の事實)は下記②及び
  ■受入条件⑵に實體を掲げる:
    scripts/switch_cli.sh: 前 sha256=392936c92eed7e66c365dd42b1190d9639562a575fa675fa924a34e39534acd0(415行)
      → 後 sha256=707400f223764b5a106e9baf9eb70cc41bfbf5b9f6ac701b1f623dac58f5f462(422行)
    scripts/watcher_supervisor_third.sh: 前 sha256=1f468a0707db4351fc89636c949001666877b5c15381e11a6f7607014ce8af9a(88行)
      → 後 sha256=4f2433e7395e9bc7209a2a487683c23ad371cf72022e8a99c8e9b321074395c8(91行)
    ★此の二器は現HEAD(2681f9f2)に既に載る★ ―― `git diff HEAD --` で差分0行、
    `git show HEAD:<path> | shasum -a 256` が disk と一致(本弾で再確認濟)。

② ★成果物 repo path + sha256★
  束 docs/evidence/km-215-zenpou-icchi-yokotenkai-kanzen-icchi-20260919/ の臺帳。
  manifest.txt に紙ごとの sha256 を載せる(80_daichou.py・本改訂の彫り確定後に再生成)。

③ ★実走 raw 同一 run・argv/rc(pipe不使用)★
  raw/60_taisho_to_sanchi_go.txt: 兩對照(has-session 陽性rc=0/陰性rc=1)+
    據ゑ後三値(sha256/bytes/行)+bash -n(兩器とも rc=0)を★同一run★で採る。
  raw/50_hakaru_hikisuu_ari.out: switch_cli.sh側・resolve_pane()實引数呼出
    (ashigaru2/ashigaru-mac-2/gunshi)。
  raw/55_hakaru_third.out: watcher側・resolve_agent_pane()實引数呼出
    (ashigaru-third-1/gunshi-third)。
  何れも cwd/argv/rc逐語、rcはsubprocess.returncodeから直取り(pipe非使用)。

④ ★依存は repository-local・lockfile★ = ★未測(理由: 對象二器は shell script で
  あり、当repoに shell 依存の lockfile が存在せぬ)★。代りに★對象二器が實行時に
  實際に呼ぶ経路★(`bash <script>` の子process)を通して在処と版を引いた
  (raw/65_izon_kyoukai.txt):
    bash  在処=/bin/bash  rc=0  版=GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25)
    tmux  在処=/opt/homebrew/bin/tmux  rc=0  版=tmux 3.7b
    grep  在処=/usr/bin/grep  rc=0  版=grep (BSD grep, GNU compatible) 2.6.0-FreeBSD
  ★注意(自己検証で発見)★: 對話 zsh session の裸 `grep` は函數(ugrep 7.8.4 を
  claude 経由で呼ぶ)へ解決されるが、此の函數は★shell固有★で對象二器を起動する
  `bash <script>` の子process へは継がれぬ。∴ 上記は★`bash -c` を通した実測★
  であり、對話shellの解決(ugrep)と混同せぬ(raw/65に自己検証の逐語)。
  何れも★系(Mac本體)の器★であつて repository-local ではない。★之は本弾で
  直した事ではない★。

⑤ ★正・意味負の件数(母數を明記)★
  ㋐ WARN發火實測 ―― 母數=5實引数呼出(switch_cli.sh側3=ashigaru2/ashigaru-mac-2/gunshi、
     watcher側2=ashigaru-third-1/gunshi-third)。
     正(鳴るべき時に鳴つた)=5/5(switch_cli.sh側は1呼出につきL68・L92相當の2箇所=
     計6行、watcher側は1呼出につきL43相當の1箇所=計2行、逐語はraw/50・raw/55)。
     意味負(鳴るべきに鳴らなかつた)=0件。
  ㋑ 兩對照(甲・raw/60) ―― 母數=2(陽性/陰性)。正=2/2(陽性rc=0・陰性rc=1、期待通り)。
  ㋒ bash -n(構文檢査) ―― 母數=2(器数)。正=2/2(rc=0)。
  ★塞がぬ穴★: raw/50のresolve_pane()呼出はrc=1で戻るが、之は§18分岐(本弾の外)を
  最小stubで塞いだ人爲の副作用であり、正常系のrc値そのものを測つた物ではない
  (新WARNが鳴る事のみを實測の主眼とした・raw/50に明記)。

⑥ ★復元★
  ★blob=disk一致★: 現HEAD(2681f9f2)の對象二器blobと disk 現物の sha256 が一致
    (本弾で `git show HEAD:<path> | shasum -a 256` を再實行し確認濟・上記①参照)。
  ★clean★ = `git status --porcelain -uall --ignored`(--ignored必須)。
    本改訂時点=6行 ―― 内譯: 本改訂で書いた未commit4件(driver/60の再タグ引數化・
    driver/65・raw/65・raw/62)、本repo無關係の他ファイル1件(docs/runbooks/
    ERR-EKARTE-001.md ―― 著者hakudoukai・本弾は一指も觸れて居らぬ・git log確認濟)、
    及び本節の元となる queue/inbox/karo-mac.yaml(既存の運用差分・本弾外)。
    對象二器自體は差分0行(上記①)。
  ★再正★ = 復元(blob=disk sha256一致)後、★同じ仕掛(driver/60_taisho_to_sanchi_go.py、
    再タグ引數化により元器を觸らず再實行)★で正を撃ち直した:
    raw/62_saisei_taisho.txt ―― raw/60_taisho_to_sanchi_go.txtと★sha256完全一致★
    (712c7cdd145e868cc1cd79e434afc74196eddd07f494139e805ef630736554c9)。
    元raw/60は `git diff --stat` 空 ―― 觸れず維持したまま再正を得た。

⑦ ★法令根拠★ = ★未測(理由: 本弾は queue/inbox/ の外・shell script二本の
  session一致精度を測る内部器であり、患者データにも本番にも觸れぬ。法令
  (医療情報3省2GL等)の適用面が無い)★。
  代りに当艦隊の条を挙げる = `.claude/rules/no-silent-failure.md`(★静かな失敗の禁止★)
  ―― 本弾の對象箇所(前方一致 miss 時に黙つて0へ落ちる形)は正に同条が禁ずる形で
  あり、本弾はWARN追加により其れを鳴る形へ改めた。

────────────────────────────────────────────────────
■受入条件の充足 ⑴〜⑺(下命 raw/70_jou_no_chikugo.txt 逐語・雛形とは別數)

⑴ ★36の仕分けが排他かつ和が36★ ―― ○
  下命の grep(literal `-t multiagent`) = 36箇所/4file(家老の先測り「5file」は
  字面の外・agent_status.shは變數形のみ使用ゆゑliteralには映らぬ・raw/10_bosuu.txt)。
  raw/15_shiwake.txt: ⑴真に危ふい(前方一致し得る執行行)=29 ⑵危ふからぬ(echo文中/
  comment/字面が別物)=7。29+7=36(母數と一致)・重複0・漏れ0。
  塞がぬ穴: 「危ふい29」は讀取のみ/変更・制御を混ぜた一群(raw/15の自己注記)ゆゑ、
  29の内譯(read-only何本・mutating何本)は本弾では割つて居らぬ。

⑵ ★据ゑた二器の前後sha256/byte/行★ ―― ○
  觸る前(■㋑): switch_cli.sh sha256=392936c9...4acd0 bytes=15296 行=415
    watcher_supervisor_third.sh sha256=1f468a07...af9a bytes=2926 行=88
  據ゑ後(raw/60): switch_cli.sh sha256=707400f2...5f462 bytes=15755 行=422(+7)
    watcher_supervisor_third.sh sha256=4f2433e7...5c8 bytes=3173 行=91(+3)
  塞がぬ穴: 変數形(既に=錨済の30箇所・5file)は前後三値を取つて居らぬ(其の對象は
  本弾の二器では無い・raw/10に明記)。

⑶ ★bash -n rc=0★ ―― ○
  根拠: raw/60_taisho_to_sanchi_go.txt(兩器・assert文で自檢)。
  塞がぬ穴: bash -nは構文のみ ―― switch_cli.shは實行時にL39(lib/_section18_roles.sh
  source)で此のMac(/bin/bash 3.2・homebrew bash不在)ではdeclare -A未對應ゆゑ
  `set -u`下で即死する事が別途判明(既知疵pane_identity.shと同根・別箇所・
  km-215二器の外・raw/75に提案のみ記載・本弾では觸れず)。構文0疵は「動く」事を
  意味せぬ。

⑷ ★兩対照raw(cwd/argv/rc逐語、rcはpipe不使用)★ ―― ○
  raw/60(has-session陽性rc=0/陰性rc=1・subprocess.returncode直取り)・
  raw/50(switch_cli.sh側・引數入り實測、§18依存を明示stub化)・
  raw/55(watcher側・引數入り實測、stub不要)。
  塞がぬ穴: raw/50のresolve_pane()呼出はrc=1で戻るが、之は§18分岐(本弾の外)を
  stubで塞いだ人爲の副作用であり、正常系のrc値そのものを測つた物ではない。

⑸ ★判定の束①〜⑺(雛形v1.1)★ ―― ○
  根拠: 本紙上段「■判定束①〜⑦」節が其れ(本節とは別立て・自己言及に非ず)。

⑹ ★押すな・PRを立てるな・ghを叩くな★ ―― ○
  根拠: 本session中 git push・gh・PR作成コマンドを一度も呼んで居らぬ(呼出履歴に
  該當行0 ―― 本弾全體で確認可能な唯一の反證法は「呼んだ記録が無い事」)。
  塞がぬ穴: 「呼んで居らぬ事」は事後に呼ばぬ事を保證せぬ ―― 本納め後、家老mac側の
  commit/PR作業を妨げぬ(其れは家老の専權)。

⑺ ★稼働中のpaneへsend-keysを一度も打たぬ★ ―― ○
  根拠: 本弾で呼んだtmuxサブコマンドはhas-session/list-panes/display-message/
  show-options の讀取四種のみ(raw/50,55,60,65の逐語argv參照)。send-keysは0回。

────────────────────────────────────────────────────
■禁の遵守
  main非觸・git reset非使用・git add --all非使用・證papers悉く docs/evidence 下
  (/tmp非使用)・行番號は逐語で示し焼き込み(patch自體)はstr.replaceの文脈一致で
  行つた(ハードコードの「行番號決め打ち」ではなく本文字面一致)・他席の枝と樹に
  非觸・稼働中watcher停止せず。

■㋓条逐語・㋔案は紙のみ ―― raw/70, raw/75 参照(内容は初版と不変)。
