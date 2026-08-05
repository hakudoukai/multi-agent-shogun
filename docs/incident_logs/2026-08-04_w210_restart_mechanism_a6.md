# W210 — 認可された再読込/再起動手順の存否(足軽6号、2026-08-04)

★★本工区は`inbox_watcher.sh`の入替(W201是正の適用)に関する読取専用の事前調査であり、
process操作(停止/再起動/signal/kill)は一切試みていない。全ての確認は`grep`・`Read`・
`systemctl --user status/list-units/list-timers`(いずれも状態照会のみ、制御コマンドではない)
に限定した★★。★実施=稼働直前(委員長解釈・理事長裁定待ち)。理事長のGOはなお有効★。

★対になる他工区★= W201(是正本体、書き上がり済だが未適用)。将軍second殿の一問が本工区の端緒。

参照した正本: `scripts/inbox_watcher.sh`(全文grep+該当箇所読取)/ `scripts/switch_cli.sh`/
`scripts/watcher_supervisor.sh`・`scripts/watcher_supervisor_third.sh`/
`shim/hakudokai/hakudokai_watchdog.sh`/ `~/.config/systemd/user/*.service`(状態照会のみ)。

断面凍結=2026-08-04T19:0x頃(実測`date`)、base_commit=502cbfe(HEAD一致・working tree
clean、本報告作成前後で再確認)。

---

## ①母集団(「再読込/再起動」に関わり得る経路、当職が導出)

`inbox_watcher.sh`自体・それを起動/監視する周辺script・関連systemd unit、を対象とした。

---

## ②陽性対照(必達、先に示す)

★`cli_restart`(inbox message type)→`switch_cli.sh`は★実在し、認可された再起動手順として
機能している★(`inbox_watcher.sh:312-316`が`__CLI_RESTART__:`マーカーを発行、
`inbox_watcher.sh:623-632`の`send_cli_command()`が`switch_cli.sh`へ委譲)。★∴ 当職の探索
手法は「実在する認可済み手順」を正しく1件発見できている(探し方が悪いのではない)★。

★然れど重大な限定★= `switch_cli.sh`が再起動するのは★エージェントのCLIセッション(tmux pane
内のclaude/codex/copilot)★であり、★`inbox_watcher.sh`という監視process自体ではない★
(`switch_cli.sh`全文中に`inbox_watcher`への言及は★一切無い★、grep実測)。★∴ 端緒便が示唆した
「己を再起動する経路が既に在る公算」という仮説は、★実際にはcli_restartとは別対象を指しており、
そのままでは成立しない★。

---

## ③三値判定(必達、0件を健全と読むな)

★本来の対象=『inbox_watcher.shというprocess自体を、既存の認可された手順で再読込/再起動できるか』★

| 分類 | 判定 | 根拠 |
|---|---|---|
| ①認可された手順として現に在る | **無し(該当なし)** | `inbox_watcher.sh`全文grepで
  `exec $0`・`SIGHUP`・自己mtimeチェック等の★自己再読込/自己再起動コードは1件も見当たらず★。
  外部からの明示的な「再起動しろ」という認可されたAPI/コマンドも見当たらない。 |
| ②在るが認可が明示されておらぬ | **該当(watcher_supervisor.sh系)** | `watcher_supervisor.sh`
  ・`watcher_supervisor_third.sh`・`hakudokai_watchdog.sh`はいずれも
  `pgrep -f "inbox_watcher.sh ${agent}"`で★プロセス不在を確認した場合のみ★
  `nohup bash inbox_watcher.sh`で再起動する、という★受動的respawnパターン★を実装している
  (`watcher_supervisor.sh:52,57`/`hakudokai_watchdog.sh:444,530,566,624`実測)。★然れど
  これらのscript自体が★いつ・誰の権限で実行されるか(cron/timer/手動)が当職の探索範囲では
  特定できなかった★。かつ`hakudokai_watchdog.sh`を起動する`shogun_watchdog.service`は
  `systemctl --user status`実測=★disabled・inactive(dead)★——★現在は動いていない★。 |
| ③無い(reload=processを殺さぬ形) | **無し** | `inbox_watcher.sh`内にSIGHUP等のシグナル
  ハンドラや設定再読込ロジックは見当たらなかった(grep実測=`reload`の唯一のヒットは
  `/clear`がCLAUDE.mdを再読込む、という★別文脈★)。★『再起動』候補(②)はあるが『再読込』
  (processを殺さぬ形)は当職の探索範囲では★存在しない★。 |
| ④判定不能 | — | `watcher_supervisor.sh`系がどの経路(人力実行/未発見のcron)で実際に
  定期起動されているかは特定できなかった。 |

---

## ④『再読込』と『再起起動』の分離(必達)

★再読込(processを殺さぬ)候補=0件(③参照)★。★再起動(kill後にrespawn)候補=
watcher_supervisor.sh系の受動的respawnパターンのみだが、これは★「processが既に死んでいる
場合に限り再起動する」という設計であり、★「生きているprocessを能動的に再起動させる」認可された
手段ではない★。∴ W201是正を効かせるには、①誰かがinbox_watcher.shを本当に終了させ、
②watcher_supervisor系が(稼働していれば)それを検知して新codeで再起動する、という経路しか
当職の探索範囲では見当たらなかった。★これはD006条件⑤(shared watcher/supervisor配下は
例外に含まれない)に照らし、当職(足軽)が独断で実行してよい操作ではない★。

---

## ⑤健全例(最低一つ)

`hakudokai_watchdog.sh`の`pgrep -f "inbox_watcher.sh ${agent}"`パターン(重複起動防止の
チェックを経てから起動する設計)自体は、★二重起動を防ぐ健全な設計★である(実測=
`watcher_supervisor.sh:52`・`watcher_supervisor_third.sh:63`で同一パターンが繰り返し
採用されている=一貫した健全設計)。

---

## ★この工区が新たに開ける穴★

1. **『既にあるはず』という前提の危うさ**= 端緒便の仮説(cli_restartが自己再起動経路である
   公算)は、名称(`cli_restart`)の類似から生じた★早すぎる推測★であった可能性がある。
   ★対象(CLIセッション vs 監視process)を取り違えると、存在する手順を誤って「これで足る」
   と判断してしまう危険がある★(本日何度も現れた「同じ名/番号が別の物を指す」型の亜種)。
2. **watcher_supervisor.sh系の起動権限が不透明**= これらのscriptが実際にどの経路
   (人力/cron/未発見のtimer)で動いているかを当職は特定できず、★『誰がこの再起動権限を
   認可しているか』という問いへの答えを本工区は出せていない★。是正を適用する際、この不透明性
   自体が「認可」の判断を困難にする。

## ★母集団漏れの自己申告★

1. `queue/pane_registry.yaml`駆動の起動経路(`hakudokai_watchdog.sh`冒頭コメントに言及あり)
   の詳細までは読み込んでいない。
2. watcher_supervisor.sh系スクリプトの呼び出し元(誰が・いつ手動実行するか)を特定できなかった。

---

## 禁止事項遵守確認

裁定 — 一切なし(既存の認可された手順の存否を報告するのみ)。process操作 — 一切なし
(stop/start/restart/signal/kill、いずれも実行していない。`systemctl --user status/
list-units/list-timers`は状態照会のみで制御コマンドではない)。他者成果物の書換え — 一切
なし。実装/commit/push/stage — 一切なし。hakudokai-devへの接触・DB接続 — 一切なし。

## 補足(working tree観測、当職の変更ではない事の明記)

本工区の調査中、`git status --short`実測で`scripts/inbox_watcher.sh`が★modified(121行追加・
14行削除)★として現れる事を確認した。★当職はこのfileをRead/grepでのみ読んでおり、Edit/Write
は一切使用していない★。差分内容(`git diff`実測)を確認した所、コメントに「W201 root-cause
cure」と明記されており、★端緒便が述べた「W201の是正は書き上がり申した」の実体そのものと
一致する★。∴ このworking tree差分は当職の作業とは無関係の、既存の(他者による)未commit状態
であることをここに明記する。

## 監査体制

★暫定二者制 (軍師+Gemini)。Codex leg 停止中 (2026-07-21事案)★。本DRAFTは軍師second殿へ監査提出する。

以上、W210直命への応答。
