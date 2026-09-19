★km-215 ―― 前方一致の横展開 ―― 專任2 納め紙★

■㋐母數宣言
  下命の grep(literal `-t multiagent`) = ★36 箇所／4 file★(家老の先測り「5 file」は
  字面の外・agent_status.sh は變數形のみ使用ゆゑ literal には映らぬ ―― raw/10_bosuu.txt)。
  變數形(`-t "$…"`)は別に 5 file 計 30 箇所 在り、★此の 36 には含めぬ★(未測・raw/10 明記)。

■㋑觸る前の三値(据ゑる二器)
  scripts/switch_cli.sh: sha256=392936c92eed7e66c365dd42b1190d9639562a575fa675fa924a34e39534acd0
    bytes=15296 行=415
  scripts/watcher_supervisor_third.sh: sha256=1f468a0707db4351fc89636c949001666877b5c15381e11a6f7607014ce8af9a
    bytes=2926 行=88

■㋒兩對照(read-only・同一run・raw/60)
  陽性(前方一致 `-t multiagent`) rc=0 ―― multiagent-mac を誤つて掴む證
  陰性(完全一致 `-t =multiagent`) rc=1 err="can't find session: multiagent" ―― 正しく掴まぬ證

■其の一 排他仕分け(raw/15_shiwake.txt)
  ⑴真に危ふい(前方一致し得る執行行) = 29
  ⑵危ふからぬ(echo文中/comment/字面が別物) = 7
  29+7=36(母數と一致)・重複0・漏れ0

■其の二 据ゑ(二器のみ)
  scripts/switch_cli.sh L68(pane_count 取得)・L72(display-message)・L74(戻り値)・
    L92(pane_base 取得)・L105(戻り値) を `=` 錨で完全一致化。
    L68/L92 に★新規 WARN(fail-closed 宣言)★を追加 ―― 完全一致で session が見つからぬ時、
    黙つて0のまま Phase 2 へ落ちず、必ず stderr へ理由を鳴らす(raw/70 に選択理由の逐語)。
  scripts/watcher_supervisor_third.sh L43-45(resolve_agent_pane)を `=` 錨で完全一致化・
    同様の WARN を追加。
  據ゑ後 三値(raw/60):
    switch_cli.sh: sha256=707400f223764b5a106e9baf9eb70cc41bfbf5b9f6ac701b1f623dac58f5f462
      bytes=15755 行=422
    watcher_supervisor_third.sh: sha256=4f2433e7395e9bc7209a2a487683c23ad371cf72022e8a99c8e9b321074395c8
      bytes=3173 行=91
  bash -n rc=0(兩器・raw/60)

■switch_cli.sh 引数を與へた實測(裁337393⑶「未測を残すな」・raw/50)
  resolve_pane() を實引数(ashigaru2/ashigaru-mac-2/gunshi)で呼び、新WARN 二行が
  ★毎回 stderr へ鳴る事★を實測(rc=1・§18分岐は本弾の外ゆゑ最小stubで置換・逐語で明記)。
  ★新発見(本弾で初めて刷る)★: switch_cli.sh は L39 で lib/_section18_roles.sh を source
  するが、此の Mac(/bin/bash 3.2・homebrew bash 不在)では同 lib L108 の `declare -A` が
  未対応ゆゑ `set -u` 下で即死する。∴ ★script 全體を素の儘走らせても resolve_pane() へ
  到達し得ぬ★(此の疵は pane_identity.sh の既知疵と同根・別箇所・km-215 二器の外・
  raw/75 に提案のみ記載・★本弾では觸れず★)。

■watcher_supervisor_third.sh 引数を與へた實測(raw/55)
  resolve_agent_pane() を實引数(ashigaru-third-1/gunshi-third)で呼び、新WARN が
  ★毎回 stderr へ鳴る事★を實測(rc=0・戻り値は空 ―― 完全一致で session 無き故)。

■判定束①〜⑦(雛形v1.1・受入条件⑴〜⑺に一對一で對應)
  ①36仕分け排他かつ和36 ―― ○
    根拠: raw/15_shiwake.txt「29+7=36(★母數36と一致★)・重複0行・漏れ0行」。
    塞がぬ穴: 「危ふい29」は★讀取のみ/変更・制御を混ぜた一群★(raw/15の自己注記)ゆゑ、
      29の内譯(read-only何本・mutating何本)は★本弾では割つて居らぬ★。
  ②前後sha256/byte/行 ―― ○
    根拠: 本紙■㋑(觸る前)・■其の二(據ゑ後)。switch_cli.sh 415→422行(+7)・
      watcher_supervisor_third.sh 88→91行(+3)。
    塞がぬ穴: 変數形(既に=錨済の30箇所・5file)は★前後三値を取つて居らぬ★(其の對象は
      本弾の二器では無い―― raw/10に明記)。
  ③bash -n rc=0 ―― ○
    根拠: raw/60_taisho_to_sanchi_go.txt(兩器・assert文で自檢)。
    塞がぬ穴: bash -n は★構文のみ★ ―― switch_cli.sh は実行時に L39
      (lib/_section18_roles.sh source)で此のMacでは死ぬ事が別途判明(下記④参照・raw/50)。
      構文0疵は「動く」事を意味せぬ。
  ④兩對照raw(cwd/argv/rc逐語・rcはpipe不使用) ―― ○
    根拠: raw/60(has-session 陽性rc=0/陰性rc=1・subprocess.returncode直取り)・
      raw/50(switch_cli.sh側・引数入り実測、§18依存を明示stub化)・
      raw/55(watcher側・引数入り実測、stub不要)。
    塞がぬ穴: raw/50のresolve_pane()呼出はrc=1で戻るが、之は★§18分岐(本弾の外)を
      stubで塞いだ人為の副作用★であり、正常系のrc値そのものを測つた物ではない
      (新WARNが鳴る事のみを實測の主眼とした)。
  ⑤判定の束①〜⑦(雛形v1.1) ―― ○
    根拠: 本節が其れ(自己言及ゆゑ「本節を以て充つ」と宣する)。
  ⑥押す/PR/gh 皆無 ―― ○
    根拠: 本session中 git push・gh・PR作成コマンドを一度も呼んで居らぬ
      (呼出履歴に該当行0 ―― 本弾全體で確認可能な唯一の反証法は「呼んだ記録が無い事」)。
    塞がぬ穴: 「呼んで居らぬ事」は事後に呼ばぬ事を保証せぬ ―― 本納め後、家老mac側の
      commit/PR作業を妨げぬ(其れは家老の専権)。
  ⑦稼働中paneへsend-keys皆無 ―― ○
    根拠: 本弾で呼んだtmuxサブコマンドは has-session/list-panes/display-message/
      show-options の★読取四種のみ★(raw/50,55,60 の逐語argv参照)。send-keysは0回。

■禁の遵守
  main非觸・git reset非使用・git add --all非使用・證papers悉く docs/evidence 下(/tmp非使用)・
  行番號は逐語で示し焼き込み(patch自體)は str.replace の文脈一致で行つた(ハードコードの
  「行番號決め打ち」ではなく本文字面一致)・他席の枝と樹に非觸・稼働中watcher停止せず。

■㋓条逐語・㋔案は紙のみ ―― raw/70, raw/75 参照。
