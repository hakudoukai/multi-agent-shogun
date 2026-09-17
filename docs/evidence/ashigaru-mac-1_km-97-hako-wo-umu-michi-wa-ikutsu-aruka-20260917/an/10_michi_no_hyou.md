# ㋐㋑㋒ ―― 箱を生み得る路の母數と、一路づつの判

## ㋐ 母數(歩く根と深さを先に宣す)

字 `queue/inbox` 又は `inbox_write` を持つ file を、根ごとに `/usr/bin/grep -l -F`(ugrep は .gitignore を読むゆゑ避けた)で拾つた。器=`driver/10_aruki.sh` `driver/15_aruki_R5.sh`、分類=`driver/60_bunrui.py`(規則は器の頭に刷つた)。

| 根 | 深さ・prune(★落とした物は此処に宣す★) | file 数 | hit | 器 | 試 | 控 | 紙 | rc |
|---|---|---|---|---|---|---|---|---|
| R1 repo 直下 | -type f / prune `.git/ queue/ logs/ node_modules/`(queue は箱の中身・logs は出力・.git は史) | 10060 | 1005 | 35 | 29 | 310 | 631 | find 0 / grep 0 |
| R2 `~/bin` | 深さ 1 | 78 | 7 | 6 | 0 | 1 | 0 | 0 / 0 |
| R3 `~/.claude` | 深さ 3 / prune `projects/`(session jsonl) | 7175 | 3591 | 0 | 0 | 3590 | 1 | 0 / 0 |
| R4 `~/Library/LaunchAgents` | 深さ 1(字に `inbox_watcher` を足した) | 25 | 0 | 0 | 0 | 0 | 0 | 0 / grep 1(陰性) |
| R5 `~/hermes-departments-mac` | prune `.git venv .venv node_modules __pycache__ site-packages`(★稼働 process の写しで見えた第五根★) | 185557 | 713 | 1 | 0 | 646 | 66 | 0 / 1(hits.err 空) |
| 稼働 process | `ps -axo`(母數 755 行・己の系譜 5 pid を ★pid で★ 除く) | ― | 17 | ― | ― | ― | ― | 0 |

- 控の内訳: R1 = `.claude/worktrees/` 267(他席の枝の写し)+ `.bak/.orig/backups/archive` 43。R3 = `file-history/` 3588 + `tasks/*.json` 2。R5 = `.hermes/ state/` 等。
- 紙の内訳: R1 = `docs/` 573 + md/instructions/skills 等 58。R3 = `history.jsonl` 1。
- 陽性対照(同じ器 `/usr/bin/grep -c -F 'scripts/inbox_write.sh'` を R1 hits に当てた): 8 行(本体 1・控 5・写し 2 を含む)、rc=0 ―― 門自身が歩きに拾はれて居る。
- ★第二歩き★(`driver/35_aruki_dai2.sh`・字 `inbox` 大小無視・器の根 253 file): any=121 / 第一歩きと同=45 / 差=76。差 76 の逐語(`raw/36_tei_kouho_gyou.txt`)を読んだ結果、箱に触るのは `scripts/slim_yaml.py`(乙・既存のみ)一本。残りは `cross_pc_inbox_*`(DB の topic 名)の字のみで箱に触れぬ。★稼働中の downlink watcher 三本(gunshi-mac / gakushu-bucho / ashigaru-mac-7)は DB→tmux paste-buffer で pane へ直貼りし、箱を読みも書きもせぬ(箱の外の路)★。

## ㋑ 一路づつの判 ―― 器 42 本(R1 35 + R2 6 + R5 1)を悉く

判の記号: 甲=inbox_write.sh を呼ぶ(門の下) / 乙生=箱を★生み得る★直書き(門を通らぬ) / 乙既=既存の箱のみ直書き(生まぬ) / 丙=読むだけ / 丁=判ぜられぬ / 無=字は在るが箱に触れぬ。「稼働」= 14:20 の ps 写し(`raw/20_ps_hits.txt`)に有るか。

| # | 器 | 判 | 逐語(path:行) | 宛名 / 生む名 | 稼働 |
|---|---|---|---|---|---|
| 1 | scripts/inbox_write.sh(門) | 乙生(門の後) | L273-275 `if [ ! -f "$INBOX" ]; then … echo "messages: []" > "$INBOX"` / L25 `INBOX="$SCRIPT_DIR/queue/inbox/${TARGET}.yaml"` | 白名簿を通つた名(★既存箱の名を含む★)・`IW_ALLOW_NAME` で新名 | 呼ばれる度 |
| 2 | scripts/inbox_watcher.sh | ★乙生★+甲 | L35 `INBOX="$SCRIPT_DIR/queue/inbox/${AGENT_ID}.yaml"`・L44-46 `if [ ! -f "$INBOX" ]; then mkdir -p …; echo "messages: []" > "$INBOX"`(AGENT_ID=argv$1・検め無) / L422-470 自箱へ python 追記(既存) / L553-613 期限切れ flip を `os.replace`(既存) / 甲 L939 karo-mac・L940 iincho・L1658 $AGENT_ID | argv$1 の名 | ★有★ 3 本(ashigaru-mac-1/2/3・cwd=repo 直下、`lsof -d cwd`) |
| 3 | scripts/watcher_supervisor.sh | 乙生 | L23-27 `ensure_inbox_file(){ … printf 'messages: []\n' > "queue/inbox/${agent}.yaml"` | 名簿の名(L68 shogun 等) | 無 |
| 4 | scripts/watcher_supervisor_third.sh | 乙生 | L21-25 同型 | 名簿の名 | 無 |
| 5 | shutsujin_departure.sh | 乙生 | L445 `echo "messages:" > "./queue/inbox/${agent}.yaml"`・L971 同(`for agent in nobunaga hideyoshi $_ASHIGARU_IDS_STR ieyasu` = ★旧名★)・L381-384 箱 dir を Linux FS へ移し symlink | 旧名の箱 | 無(起動 script) |
| 6 | shim/hakudokai/hakudokai_secondpc_setup.sh | 乙生 | L325-330 `INBOX_DIR="$SCRIPT_DIR/queue/inbox"; … echo "messages: []" > "$INBOX_DIR/${AGENT_ID}.yaml"` | AGENT_ID | 無(second_pc 用) |
| 7 | scripts/bulk_ack.sh | 乙既 | L82-84 `if [ ! -f "$INBOX" ]; then continue`・L117 `open(inbox_path, 'w')`・L88 `cp "$INBOX" "${INBOX}.bak…"`(箱 dir に控を生む) | 既存のみ | 無 |
| 8 | scripts/slim_yaml.sh → slim_yaml.py | 乙既 | slim_yaml.sh L34 `python3 … slim_yaml.py "$@"` / slim_yaml.py L199-201 `if not inbox_file.exists(): return True`・L242 `save_yaml(inbox_file, data)` | 既存のみ | 無 |
| 9 | ~/bin/inbox_mark_read.py | 乙既 | L64 `s = open(path…).read()`(錠の後・無ければ FileNotFoundError で落ち書かぬ)・L71 `open(path, 'w'…).write` | 既存のみ(argv) | 拙者が本弾で 1 度(己の箱・既読印のみ) |
| 10 | ~/bin/karo_mac_mark.py | 乙既 | L16 `open(p, "r")`・L21-22 `tmp = p + ".karo_tmp" … os.replace(tmp, p)` | 既存のみ | 無 |
| 11 | scripts/stop_hook_inbox.sh | ★甲(宛名固定)★+丙 | L174-176 `bash "$SCRIPT_DIR/scripts/inbox_write.sh" karo "$NOTIFY_CONTENT" "$NOTIFY_TYPE" "$AGENT_ID" &` / 丙 L144・L191・L261-288 自箱読 | ★`karo`(固定・mac の家老箱は karo-mac)★ | ★有★ `.claude/settings.json` L8 Stop hook(claude 席が止まる度) |
| 12 | scripts/agent_periodic_push.sh | 甲(宛名固定) | L109 `bash "$SCRIPT_DIR/scripts/inbox_write.sh" karo "$MSG" status_update shogun` | `karo` | 無 |
| 13 | scripts/agent_health_check.sh | 甲(宛名固定)+丙 | L203 `… inbox_write.sh shogun "$content" "$type" health_check` / 丙 L249-271 | `shogun` | 無 |
| 14 | scripts/ntfy_listener.sh | 甲 | L171 `… inbox_write.sh shogun`(L12-30 は queue/ntfy_inbox.yaml=箱 dir 外) | `shogun` | 無 |
| 15 | scripts/redundancy/shogun_report_watcher.sh | 甲 | L284/287 `"$INBOX_WRITE" shogun "$content" notification shogun_report_watcher` | `shogun` | 無 |
| 16 | scripts/karo_overload_monitor.sh | 甲+丙 | L351 `… "$INBOX_WRITE_CMD" takenaka`・L359 `… shogun` / 丙 L59 `KARO_INBOX=…/queue/inbox/karo.yaml`・L231 | `takenaka` `shogun` | 無 |
| 17 | scripts/fukuincho_report_poke_bundle.py | 甲 | L390-392 `"bash", inbox_write_path, target, _INBOX_WRITE_STDIN_PLACEHOLDER` | 引数 | 無 |
| 18 | shim/hakudokai/hakudokai_activity_monitor.sh | 甲 | L155・L188 `… inbox_write.sh shogun` | `shogun` | 無(second_pc) |
| 19 | shim/hakudokai/hakudokai_secondpc_receiver_poll.py | 甲 | L352 `"bash", …"inbox_write.sh"`(L358 `env["INBOX_CONTENT"]`) | DB 由来の target | 無(second_pc) |
| 20 | shim/hakudokai/hakudokai_fukuincho_reverse_poll.py | 甲 | L151 | fukuincho | 無(second_pc) |
| 21 | shim/hakudokai/hakudokai_fukuincho_poll.py | 甲+丙 | L125・L136 / 丙 L150-164 `queue/inbox/shogun.yaml` 読 | shogun | 無(second_pc) |
| 22 | shim/hakudokai/hakudokai_secondpc_watcher_poll.py | 甲 | L282 | target | 無(second_pc) |
| 23 | ~/bin/mac_send.py | 甲+丙 | L85 `subprocess.run(['bash', 'scripts/inbox_write.sh', opt['to'], …])` / 丙 L77-81 unread 読 | `--to` | 無 |
| 24 | ~/bin/karo_mac_template.sh | 甲 | L6 `iw(){ bash …/scripts/inbox_write.sh "$1" "$(cat "$2")" notification karo-mac; }` | $1 | 無 |
| 25 | scripts/agent_status.sh | 丙 | L199 `local inbox_file="$SCRIPT_DIR/queue/inbox/${agent_id}.yaml"` | ― | 無 |
| 26 | scripts/checks/inbox_alias_integrity.sh | 丙 | L27-29 alias 対(symlink 検・本日 symlink は 0 本 `ls -la|grep ^l` rc=1) | ― | 無 |
| 27 | scripts/checks/secondpc_dispatch.sh | 丙 | L32-33 `ssh … "stat -c %Y …/queue/inbox/${TARGET}.yaml"` | ― | 無 |
| 28 | scripts/karo_standby_dashboard.sh | 丙 | L26 `INBOX_DIR="$ROOT/queue/inbox"`・L52・L144-156 | ― | 無 |
| 29 | ~/bin/karo_mac_unread.py | 丙 | L4 | ― | 無 |
| 30 | ~/bin/orphan_inbox_trap.py | 丙 | L23 `inbox = os.path.join(base, "queue/inbox")`・L38 glob 読 | ― | 無 |
| 31 | ~/hermes-departments-mac/bin/boot-mac-fleet.sh | 丙+★起動者★ | L17 `grep -c "queue/inbox/${role}.yaml"`(session log 読) / L111 `for ag in karo-mac ashigaru-mac-1 ashigaru-mac-2 ashigaru-mac-3 ashigaru-mac-7`・L122 `nohup bash "$REPO/scripts/inbox_watcher.sh" "$ag" "$tgt" claude`(pane 無なら L115 skip) | #2 へ名を渡す | 起動時 |
| 32 | scripts/lib/inbox_path.sh | 丁 | L31-46 path を返すのみ。source する者は `scripts/archive/…` 4 本(控)のみ → 生きた呼び手が無い | ― | 無 |
| 33 | config/settings.yaml | 無 | L62・L102-127 註と名 | ― | ― |
| 34 | .claude/settings.json | 無(路の★起点★) | L63-64 permissions の字 / L8 Stop hook が #11 を呼ぶ | ― | 有 |
| 35 | shutsujin_departure_secondpc.sh | 無 | L129-135 prompt 文中の字 | ― | 無 |
| 36 | scripts/checks/symlink_aware_atomic_write.sh | 無 | L95 文言 | ― | 無 |
| 37 | scripts/lib/detect_stale.sh | 無 | L250 註のみ(inbox_write の実呼出 無・`grep -n inbox_write` は此の 1 行のみ) | ― | 無 |
| 38 | lib/cli_adapter.sh | 無 | L351 prompt 文 | ― | ― |
| 39 | shim/hakudokai/hakudokai_inbox_write.py | 無 | Supabase INSERT(箱に触れぬ) | ― | 無 |
| 40 | shim/hakudokai/hakudokai_secondpc_receiver.sh | 無 | L11 註 | ― | 無 |
| 41 | shim/hakudokai/hakudokai_pii_detector.py | 無 | L15 註 | ― | 無 |
| 42 | shim/hakudokai/hakudokai_init_agents.sh | 無 | L46 prompt 文 | ― | 無 |

集計(器 42): 甲 14 / 乙生 6(内 門自身 1 → ★門を通らずに箱を生む路 = 5 器 6 行★) / 乙既 4 / 丙 7 / 丁 1 / 無 10。

試 29 本: `tests/agent_selfwatch.bats` L176 `run bash "$INBOX_WRITE_SCRIPT" test_agent …` は ★実箱 `queue/inbox/test_agent.yaml` へ★ 門経由で書く(L194 で消す)。残り 28 本は tmp dir の写し門/写し箱(`tests/e2e/helpers/setup.bash` L29 `cp …/inbox_write.sh "$E2E_QUEUE/scripts/"`・`tests/test_inbox_write.bats` L32-44 等)で実箱に触れぬ ―― 読取で判じ★実走せず★。

## ㋒ 乙の各路 ―― 其の路で異名の箱が生れ得るか(一行づつ)

| 路 | 生れ得るか | 根拠 | 実走 |
|---|---|---|---|
| inbox_watcher.sh L44-46 | ★可★ | argv$1 を一切検めず `messages: []` を書く。名の源は起動者の名簿(boot-mac-fleet.sh L111 / supervisor)。現物: pane 無の `ashigaru-mac-4..7.yaml` が存在し `.lock` の刻は 9/3・8/23(生れた跡) | 実走せず |
| watcher_supervisor.sh L25 / _third L23 | 可 | 名簿の名で無条件に生む | 実走せず |
| shutsujin_departure.sh L445・L971 | 可(★旧名★) | `nobunaga hideyoshi … ieyasu` を無条件に生む(mac の正名に無い名) | 実走せず |
| hakudokai_secondpc_setup.sh L329 | 可 | AGENT_ID で無条件に生む(second_pc 用) | 実走せず |
| inbox_write.sh L273(門の後) | 新名=不可(69) / ★既存の異名=可(育てる)★ / `IW_ALLOW_NAME`=可 | 実走 7 対照(`raw/50_summary.txt`): ①読点 rc=69 ②空白 rc=69 ③未知 rc=69 ④生 pane karo-mac rc=0 NAME_PASS ⑤★pane 無・箱有の `karo` rc=0 NAME_PASS★ ⑥IW_ALLOW_NAME rc=0 NAME_PASS(註付) ⑦gunshi-mac rc=0 NAME_PASS(名の門は通る・死箱の門は L100 以降で本走時のみ)。箱の名列 sha16 前後同一(19 本) | ★実走(IW_NAME_TEST_ONLY=1 のみ)★ |
| bulk_ack.sh / slim_yaml.py / inbox_mark_read.py / karo_mac_mark.py | 不可 | 無い箱は飛ばす(continue / return)か読みで落ちる | 実走せず |
| tests/agent_selfwatch.bats L176 | 門経由 → 今は 69 で拒まれる筈(test_agent は pane にも箱にも無い) | 読取 | 実走せず |
