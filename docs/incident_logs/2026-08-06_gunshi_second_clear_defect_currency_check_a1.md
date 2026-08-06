# gunshi-second /clear 未着火(07-16報告)の現況確認 — 足軽1号

- 下命: karo-second msg_20260806_204338_c6b6fc1d (2026-08-06T20:43:38)
- 前工区(群㈠仕分け): docs/incident_logs/2026-08-06_stalled_inbox_triage_g1_ashigaru1.md
  にて当該便(msg_20260716_061609_0ae175d2)は「便としては用済み濃厚」まで仕分け済。
  **本工区は便の要否ではなく、報告本文が名指した機構欠陥(race)が★今も実在するか★を問う。**
- 測時: 2026-08-06T20:50:00+0900(冒頭) 〜 20:50台(全実測)。
- 器: `git log/show/blame`(コード実測)・`tmux`各種読取専用サブコマンド(list-panes/display-message/show-options)・
  `ps`(プロセス木実測)・`/proc/<pid>/fd`(実ログ先特定)・`grep`(ログ/正本突合)。
  **`/clear`は一度も送っていない・watcherを操作していない・tmux send-keys等の書込操作は一切行っていない。**
- 範囲: `scripts/inbox_watcher.sh`全1728行のうち関数`get_unread_info`(449-529)・
  `process_unread`内 specials 処理(1310-1377)・`normalize_special_command`(297-318)・
  `send_cli_command`/`send_keys_verified`(613-770台)を実読。`queue/pane_registry.yaml`全行・
  `queue/inbox/gunshi-second.yaml`直近部・`/tmp/watcher-gunshi-second.log`全6621行・
  `logs/inbox_watcher_gunshi-second.log`(7行のみ・後述)。

## 結論(一行)

**07-16報告が名指した「specials消費のみでsend-keys前に読了化するrace」は、
commit `b9bec71`(2026-08-06T00:44:06、当職=足軽1号 起草、軍師second再監査PASS)で
根治済。同機構は本便の測時現在も生きている(コード上・ログ上とも確認)。
ただし「送れば必ず着くか」自体は★未検証(unconfirmed)★——本工区の禁により実送信していない。**

---

## ⒜ clear_command の経路(scripts/inbox_watcher.sh・行番号)

1. `get_unread_info()`(451-529)がinbox yamlを読み、`type in (clear_command, model_switch,
   cli_restart)`を`specials`として抽出(490-491)。
   **旧版(commit b9bec71の親)はここで即座に`read=True`を書き戻していた**
   (`git show b9bec71^:scripts/inbox_watcher.sh` 493-495行を実見=
   `if not m.get("read", False) and m.get("type") in special_types: m["read"] = True`)。
   これが07-16報告の root cause「specials自動read化がsend-keys前にclear_commandを消費するrace」
   と★文言レベルで一致★する。
   **現行版は493-500行のコメントで明示的に「W201 root-cause cure: specials are intentionally
   NOT marked read=True here」と書かれ、実装もその通り(読了化コードそのものを削除)。**
2. `process_unread()`のspecials処理ループ(1334-1377)で`clear_command`を個別分岐。
   busy中は`continue`で★未読のまま次サイクルへ持ち越し★(1354-1357、コメントに
   「W201 root-cause cure(発注②): 意図的に未読のまま残す」)。
3. `normalize_special_command()`(297-318)が`clear_command`→文字列`"/clear"`に正規化。
4. `send_cli_command()`(665-)が`get_effective_cli_type()`(269-296)で実効CLIを都度再判定し、
   `claude`ならそのまま、`codex`なら`/clear`→`/new`変換(711-734)、`copilot`ならCtrl-C+再起動
   (741-756)に分岐。
5. 実送信は`send_keys_verified()`(628-663)——C-u→本文→Enter→**capture-paneで送信残留の
   有無を確認し、残っていれば最大2回まで再試行**(651-655)。
6. 送信が`send_cli_command`から`rc=0`で返った時のみ`mark_message_processed()`(537-)を呼び、
   ★その時初めて★該当メッセージを`read=True`で確定書込み(1363-1365)。busy延期は`rc=2`で
   区別し(703-706)、失敗(送達不能)は`return_message_to_sender()`で差出人へ突き返す(1371)。

**→ 07-16報告時点の「消費のみ・送達確認なし」の設計は現在は存在しない。読了化は送達確認後の
一点のみに一本化されている。**

## ⒝ 名簿(queue/pane_registry.yaml)在否・pane解決可否

- `queue/pane_registry.yaml` 170-180行に`gunshi-second`のエントリ在り
  (`tmux_target: multiagent-second:0.8`, `agent_id: gunshi-second`, `status: 通常運用`)。
- pane実解決: `tmux list-panes -a` にて `%11 multiagent-second:0.8 gunshi-second` を実見
  (pane_id/@agent_id/pane_current_command全列挙、読取専用サブコマンドのみ使用)。
  **pane は現に引ける・agent_id取り違えも無い。**
- watcherプロセス生存: `ps aux`にて`bash scripts/inbox_watcher.sh gunshi-second
  multiagent-second:0.8 codex`(pid 2001735, Aug04起動, 現在も稼働中)を実見。

### 追加所見(本題とは別枠・混同せず明記)

pane_registry.yaml 175-176行は`gunshi-second`の`cli: claude`(`model: Opus`)と記すが、
**実際にpane %11で走っているプロセスは`ps --ppid`で辿ると`codex`本体
(`/home/hakudokai/.local/lib/node_modules/@openai/codex/.../codex --dangerously-bypass-approvals-and-sandbox`)
であり、tmux pane option`@agent_cli`も`codex`(実測値)**。
`get_effective_cli_type()`は起動引数(`codex`)とpane値(`codex`)が一致するため
「CLI drift detected」警告は発生しない(script内部の整合性チェックは通る)。
**乖離が在るのはscript内部ではなく「正本(pane_registry.yaml)の記述」と「稼働実態」の間**
——これは07-16報告のrace問題とは別件であり、本工区の裁定範囲(is="欠陥は今も在るか")
には直接含めないが、次工区以降の母集団として書き残す。当職は裁定しない。

## ⒞ 21.6日間に直った形跡

- `git log -S"W201 root-cause cure" -- scripts/inbox_watcher.sh` → commit `b9bec71`
  (2026-08-06T00:44:06+0900、コミット題「fix(watcher): W205 送出コマンド三点の根治」)。
- `git blame -L 493,500 scripts/inbox_watcher.sh` → 全行`b9bec71`(同日同時刻)に帰属。
- `git show b9bec71^:scripts/inbox_watcher.sh`で親コミット(修正前)の同箇所を実見し、
  上記⒜①の通り旧ロジック(即時read化)を確認済。
- 当該commitのcommit messageに「★W201 が clear_command で直した当の欠陥を
  model_switch/cli_restart で再生産する所であった★」との記述在り=
  W201(clear_command限定の根治)自体もこの一連の流れの中で成立したもので、
  本便が名指す症状の直接の治療に当たる。
- `docs/incident_logs/2026-08-04_w201_inbox_watcher_cure_a3.md`(足軽3号起草、W201設計文書)は
  実在するが、`grep -n "gunshi-second\|07-16\|0716\|325k\|race"`で0件
  =★この設計文書は07-16報告のmsg_id・PID・症状を直接引用してはいない★
  (根治対象の一般設計としては一致するが、個別便との紐付け記述は無い、という限度で報告)。
- 便の識別子(`0ae175d2`/`3859929`/`msg_20260716_061609`)を`docs/`・`queue/reports/`全体で
  grepした結果、ヒットは当職自身が前工区で書いた仕分け票1件のみ
  =★他の誰かが本便を名指して「直した」と明記した記録は見つからなかった(0件)★。
  **これは「探索して見つからなかった」であり「存在しないと断定する」ではない
  (grep対象はdocs/とqueue/reports/のみ・commit本文全体はSで別途検索済)。**

## ⒟ 「今`/clear`を送らば着くか」——unconfirmed

**送っていない(禁則順守)。以下はコード読解からの推測であり、実測ではない。**

- `/tmp/watcher-gunshi-second.log`(pid 2001735の実際の標準出力先、`/proc/2001735/fd/1`で特定)
  全6621行を`grep -n "clear_command|/new\\b|CLI-RESTART"`したが★0件★
  =このwatcherインスタンス起動(2026-08-04T20:42)以降、gunshi-secondへ`clear_command`が
  一度も届いていない(=修正後の経路が実戦で通った実例が無い)。
- ログは測時直前(20:50:10)まで連続稼働・自己watch(inotifywait)・throttle判定が動いている
  ことを確認=watcherは生きて回っている。
- コード上は⒜の通り「busy中は未読のまま持ち越し・送達確認後のみ既読化・codex実効時は
  `/clear`→`/new`へ自動変換し`send_keys_verified`で残留確認」という経路が揃っているが、
  **これは静的読解による推測(unconfirmed)であり、実際に送って確認した事実ではない。**

## ⒠ 己の手で為した事(実行コマンド・全て読取専用)

```
tmux display-message -t "$TMUX_PANE" -p '#{@agent_id}'
git log -S"W201 root-cause cure" --oneline -- scripts/inbox_watcher.sh
git log -S"mark_message_processed" --oneline --reverse -- scripts/inbox_watcher.sh
git blame -L 493,500 scripts/inbox_watcher.sh
git show --stat b9bec71 ; git log -1 --format="%B" b9bec71
git show b9bec71^:scripts/inbox_watcher.sh | sed -n '480,520p'
grep -n "gunshi-second" queue/pane_registry.yaml
tmux list-sessions ; tmux list-panes -a -F "..."
tmux show-options -p -t '%4'/'%11' -v '@agent_id'/'@agent_cli'
ps aux | grep inbox_watcher.sh | grep gunshi-second
tmux display-message -p -t multiagent-second:0.8 '#{pane_pid}'
ps -o pid,ppid,comm,args --ppid <pane_pid> (子プロセス木を1段ずつ)
ls -la /proc/2001735/fd/1 /proc/2001735/fd/2 ; readlink 同 ; cat /proc/2001735/cmdline
wc -l /tmp/watcher-gunshi-second.log ; tail -15 同 ; grep -n "clear_command|/new|CLI drift" 同(全行)
grep -n "type: clear_command" queue/inbox/gunshi-second.yaml
grep -rl "0ae175d2|3859929|msg_20260716_061609" docs/ queue/reports/
```

（`/clear`送出・watcher書換・tmux send-keys/C-u/Enter等の入力注入・lane(worktree)への接触・
本便/対象fileの書換・`read`立て——★いずれも実施していない★。）

## 母集団の自己申告

本票が実測した対象は「07-16報告1通が名指す機構(scripts/inbox_watcher.sh の clear_command
経路)」に限る。`queue/inbox/*.yaml`全体の他の停滞便・他agentのCLI drift事例の網羅調査は
本工区の範囲外につき未実施。pane_registry.yamlの`cli`欄が他agentでも実態と乖離しているか
は確認していない(gunshi-second 1件のみ実測)。

## ETA

即時提出。追加調査要なし(本票にて完結)。
