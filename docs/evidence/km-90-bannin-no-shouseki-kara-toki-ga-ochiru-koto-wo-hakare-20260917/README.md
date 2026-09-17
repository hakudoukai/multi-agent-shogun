# 第80弾 ―― ★番人の証跡から刻が落ちる事を測れ★: `date -Is` は此の Mac(BSD date)で rc=1 ゆゑ、番人が /tmp に残す証跡の entry は★観測できる全 32 行が `[]`(刻無し)★。証跡の置き場 /tmp は macOS の `tmp_cleaner`(毎日 0 時・atime/mtime/ctime 三条件 3 日超)に掃かれ、★実在が証せる日次 log 7 本(9/2〜9/12)が既に消えて居る★= 実害。直しは紙にのみ(写しで実測済: `-Iseconds` で BSD/GNU 同字面・4/4 entry に刻が入る)

- 弾: km-90(家老便 msg_20260917_121906_04d9052e + 訂正便 msg_20260917_121942_43f0db3a・札 queue/tasks/ashigaru-mac-1.yaml sha16 e705bbb37a8c1508 6155B/70行 = 訂正便の正と一致)/ 束 docs/evidence/km-90-bannin-no-shouseki-kara-toki-ga-ochiru-koto-wo-hakare-20260917 / 書手 ashigaru-mac-1(專任1)/ 宛 karo-mac。
- 的: scripts/checks/dd169_kill_term_guard.sh ―― ★読むのみ★。版固定(`01`): sha256 3958f4fff3295e63…(sha16 = 家老の値と一致)・91 行・4228 B・最終 commit bbe9712 2026-06-01 21:26:58 +0900・working tree 差分無し。走らせたのは束内の写し 2 本(`_after/guard_copy.sh` = 生器と L22 LOG_DIR 一行のみ違ふ・`_after/guard_copy_fixed.sh` = 直し案を当てた写し)のみ。
- 刻: 着手便 12:20:xx(宣ETA 13:15)/ 紙を書いた刻 2026-09-17T12:40 / 實 = 納め最終便の timestamp(便が正・紙は己の刻を知らぬ)。
- 器: 束内 `_after/NN_*.txt` が生の出目(★此の束では `_after/` を測りの生の置き場に用ゐた ―― 慣例(`_after/` = 臺帳の後)と違ふ。疵宣 ㊈-6。臺帳の後に書く物は `_post/`★)。臺帳 = MANIFEST.txt(4 欄・束内相対・書き手は karo_mac_manifest_append.py のみ)。門控 = `_gate/`(員外)。
- ★塞ぐ側の語★: Bash の命令文へは一度も書いて居らぬ(此の紙にのみ論として書く)。写しへ渡した字面は札の指定通り「塞ぐ側の語を含まぬ枝」のみ。語の分割・符号化・別名化は行つて居らぬ。file 名 `dd169_kill_term_guard.sh` は下線区切りゆゑ番人の regex(L50 `(^|[[:space:]])(kill|pkill|killall)([[:space:]]|$)`)に当たらぬ ―― 之は躱しではなく、生器を cp/shasum する為に避けられぬ字面であり、生の番人が現に通した(本束の全 Bash 呼びが其の証)。

## ㊀ 結語を先に

1. ★㋐ L22/L24/L26 逐語(`02`・行番は家老の値と一致)★: L22 `LOG_DIR="/tmp/dd169_audit_log"` / L24 `LOG_FILE="$LOG_DIR/$(date +%Y%m%d).log"` / L26 `log() { printf '[%s] %s\n' "$(date -Is)" "$*" >> "$LOG_FILE"; }`。★此の機の `date -Is`(`03`)= rc 1・stdout 空・stderr `date: invalid argument 's' for -I`★(Darwin 25.5.0 / macOS 26.5.2 / /bin/date)。番人と同じ呼び方 `printf '[%s] %s\n' "$(date -Is)" probe` は `[] probe` を刷り rc 0 ―― ★失敗が stderr に出るのみで、刻は黙つて空になる★。
2. ★BSD と GNU の突合(`03` `12`)★: BSD `date -Iseconds` = `2026-09-17T12:25:38+09:00`、GNU `gdate -Is`(coreutils 9.11・/opt/homebrew/bin)= 同刻同字面 ―― ★一字ずつ突合 同一(len 25)・TZ 4 種(Tokyo/UTC/New_York/Kolkata)悉く同一★。`-Is` は GNU の略記(argmatch: `-Is` `-Isec` 通る)であり、BSD は完全語 `seconds` のみ(man 逐語: Valid FMT values are date, hours, minutes, seconds, and ns)。`+%FT%T%z` は 22 字目が `+0900`(コロン無し・24 字)で★GNU `-Is` と違ふ★。python3 `isoformat(timespec="seconds")` は同字面だが別 process 起動。
3. ★㋑ 既存証跡(`04` `13`・読取のみ)★: /tmp/dd169_audit_log/ に 3 本(20260913.log 45511B/333 行・birth 09-13T06:10:00、20260916.log 5186B/38 行、20260917.log 17916B/234 行・mtime 12:17:20)。全 605 行の内 行頭 `[` の entry 32(内 `[[`= input= の続き行 4)、★`[] ` 起しの entry 28・非空刻の entry 0★(BLOCKED 13 / ALLOWED 6 / ps_evidence 6 / PARSE_FAIL 3)。最古 = 20260913.log L1 `[] BLOCKED non-conforming kill: cd /Users/momizimac/multi-agent-shogun`、最新 = 20260917.log L172(同文)。★何時から空か★: 観測できる最古 entry(09-13T06:10 の file)から空。加へて、消えた log の中身が己の過去 session jsonl に写つて居り(`19c`)、★20260906/20260907/20260911 の entry も `[] BLOCKED …`★ ―― ∴ 少なくとも 9/6 から空、機構上は此の Mac で番人が最初に走つた時(≤ /tmp/claude-501 birth 08-06T17:01)から空である。
4. ★㋒ 両対照(`11` `11b`・写し・LOG_DIR は束内)= 13 組★: 陰性 3(echo hi / 下線 file 名 / 空白のみ)= rc 0・stdout 空・stderr 空・log 0 行。陽性 6(command 空 / `{{{` / `{"foo":1}` / `{"tool_input":{}}` / `null` / tool_input が文字列)= ★悉く rc 2・stderr 2 行(1 行目 `date: invalid argument 's' for -I`・2 行目 `[DD-169 guard] BLOCKED: …`)・log に 1 行 `[] PARSE_FAIL: … input=<入力逐語>`★。其の他: stdin 空(</dev/null)= rc 2・log `[] PARSE_FAIL … input=`;★stdin 閉ぢ(<&-)= 「止」★(素で走らせて 2 分 39 秒 眠り・gtimeout 5 で rc 124・log 0 行・stderr 空);巨大 JSON 300,000 字(通る側)= rc 0・90 ms;巨大かつ壊れ 300,000 字 = rc 2・86 ms・★log へ input= 全文 300,032 B が落ちる★。写し log 8 entry ★悉く `[]`★。実測 ms = 53〜90(hook timeout 5 秒に対し余裕)。
5. ★「止」の真因(`15`)★: fd0 を閉ぢて起動すると、`INPUT_JSON=$(cat)` の為に bash が作る pipe の★読み口が最小の空き fd = 0 に落ち★、cat が己の出口へ繋がる pipe を読んで永久に待つ(lsof: bash 78930 と cat 78933 が共に `0 PIPE`)。小再現: `bash -c 'cat' <&-` は即 `Bad file descriptor`(rc 1)、`bash -c 'x=$(cat)' <&-` は rc 124(止)。★但し Claude Code の PreToolUse は stdin JSON を常に渡す(公式 hooks reference・claude-code-guide 経由)ゆゑ、此の枝は hook 経路からは到達せぬ★(手打ち・他器からの呼びのみ)。併せて公式: ★hook が timeout すると tool 呼びは塞がれず進む(fail-open)・exit 2 のみが塞ぐ・timeout は秒★。
6. ★㋓ /tmp 置きの実害 = 在る(出目)★(`16` `17` `18` `19b` `19c`): 掃除器 = /usr/libexec/tmp_cleaner(sh script 1142B・launchd `com.apple.tmp_cleaner`・StartCalendarInterval Hour 0)。逐語: `daily_clean_tmps_days="3"`、file は `-atime +3 -mtime +3 -ctime +3 -delete`(三条件 AND・BSD find は 24 時間単位へ★切り上げ★)、dir は `-empty -mtime +3`。/private/tmp 直下の普通 file 4437 の内 ★次の 0 時に消える物 931★(同述語で今 数へた)。dd169 の 3 本は今は 0 本該当(20260913.log は atime 09-17T07:20:36 に誰かが読んだ為に生き延びて居る・mtime/ctime は 09-13T19:41)。★消えた証拠★: 己の過去 session jsonl(2.2GB・5052 本)に ★`ls` の出目(所有者・寸法・名)付きで 7 本★ = 20260902(12518B)/0903(18129B)/0906(701B)/0907(8493B)/0908(1143B)/0911(70904B)/0912(49631B)が写つて居り、disk には無い(20260824 は名の言及 1 のみ・ls 出目無し= 実在は証せぬ)。∴ ★DD-169 の存在理由である ALLOWED の ps 証跡は、書かれてから最短 4 日で消える★。20260913.log は次に 09-21 00:00(atime 07:20 09-17 が 3 日超に切り上がる日)に消える見込(其れまでに誰かが読めば延びる)。
7. ★㋔ 直し案(紙にのみ・写しで実測 `20`)★: 案A(刻)= L26 を `ts() { date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z'; }` + `"$(ts)"` へ。写しで 陽性 4/4 entry に `[2026-09-17T12:31:28+09:00]` が入り stderr の `date:` 行が消えた。GNU stub(PATH 先頭に gdate)= 同字面、-I 無しの旧 BSD stub = `+0900` 形(空にはならぬ)。案B(置き場)= `LOG_DIR="${DD169_AUDIT_LOG_DIR:-$HOME/.local/state/dd169_audit_log}"`(既存 /tmp の log は消さず・動かさず、`cp -p` で写すのみ・戻しは一行)。案C(止の柵)= `$(cat)` の前に `if ! { : <&0; } 2>/dev/null; then log …; exit 2; fi`(写しで rc 124 → rc 2・log 1 行 刻付き)。各案の ㋐塞ぐ穴 ㋑塞がぬ穴 ㋒誤鳴り ㋓戻し方 は ㊆。
8. ★㋕ 測れぬ枝★: 「塞ぐ側の語を含む命令を番人へ渡した時の振舞ひ」―― 其の字面を運ぶ Bash 呼び自体が生の番人に塞がれる為、此の席からは写しへも渡せぬ(躱さぬ)。★但し其の枝の出目は既存 /tmp 証跡(読取のみ)に現に在り★(BLOCKED non-conforming 10 / BLOCKED kill -9 2 / BLOCKED non-graceful 1 / ALLOWED 6・悉く `[]`)= 刻の欠落は其の枝でも同じである事を、己が何も送らずに示せる。
9. ★㋖ 疵 12(㊈)★。宣ETA 13:15(着手 12:19:06 起点で 56 分)。實は納め便の刻。

## ㊁ ㋐ 逐語と date の実測(`01` `02` `03`)

| 行 | 逐語(grep -n・家老の行番と一致) |
|---|---|
| L22 | `LOG_DIR="/tmp/dd169_audit_log"` |
| L24 | `LOG_FILE="$LOG_DIR/$(date +%Y%m%d).log"` |
| L26 | `log() { printf '[%s] %s\n' "$(date -Is)" "$*" >> "$LOG_FILE"; }` |

`date` の実測(`03`・/bin/date・12:21:24):

| 形 | rc | stdout | stderr |
|---|---|---|---|
| `-Is` | 1 | (空) | `date: invalid argument 's' for -I` |
| `-Isec` | 1 | (空) | `date: invalid argument 'sec' for -I` |
| `-Iseconds` | 0 | `2026-09-17T12:21:24+09:00` | |
| `-I` / `-Idate` | 0 | `2026-09-17` | |
| `-Ihours` | 0 | `2026-09-17T12+09:00` | |
| `-Iminutes` | 0 | `2026-09-17T12:21+09:00` | |
| `-Ins` | 0 | `2026-09-17T12:21:24,226776000+09:00` | |
| `+%Y-%m-%dT%H:%M:%S%z` | 0 | `2026-09-17T12:21:24+0900` | |
| `+%Y-%m-%dT%H:%M:%S%:z` | 0 | `2026-09-17T12:21:24:z`(★`%:z` は BSD に無く `:z` が字面で出る★) | |
| `gdate -Is`(GNU 9.11) | 0 | `2026-09-17T12:21:24+09:00` | |

∴ L24 の `date +%Y%m%d` は BSD でも通り(file 名の日付は正しい)、L26 の `date -Is` だけが落ちる。stderr は hook の stderr へ流れ(家老が 12:21 に見た行)、`$(…)` の値は空 → `[]`。

## ㊂ ㋑ 既存証跡の逐語(`04` `13`・読取のみ・根 /tmp/dd169_audit_log 深さ 1・刻 12:25:39)

| file | bytes | 行 | entry(行頭 `[`) | `[] ` 起し | 非空刻 | birth / mtime |
|---|---|---|---|---|---|---|
| 20260913.log | 45511 | 333 | 18(内 `[[` 4) | 14 | ★0★ | 09-13T06:10:00 / 09-13T19:41:36 |
| 20260916.log | 5186 | 38 | 3 | 3 | ★0★ | 09-16T22:39:24 / 09-16T22:39:35 |
| 20260917.log | 17916 | 234 | 11 | 11 | ★0★ | 09-17T04:53:47 / 09-17T12:17:20 |

- entry 28 の種別: BLOCKED non-conforming 10 / BLOCKED kill -9 (SIGKILL) 2 / BLOCKED non-graceful 1 / ALLOWED 6 / ps_evidence 6(内 1 は本文空 `[]   ps_evidence: `= 20260913 L15・PID 49575 の ps が空だつた) / PARSE_FAIL 3(`input={}`)。
- 全行 605 の内 entry でない 573 行は `input=$INPUT_JSON` の続き(他席の命令文・札の本文が其の儘 /tmp の 0644 file に落ちて居る ―― 之は問はれて居らぬが一行だけ: ★証跡が world-readable で、塞いだ命令の全文を含む★)。
- `[[` 起しの 4 行は memory の `[[name]]` link が input= の中に在るだけで entry ではない(`13` に逐語)。
- ★消えた log の中身★(`19c`・jsonl 内の `==> …/20260906.log <==` 見出しの直後): `[] BLOCKED non-conforming kill: kill 2756 2754 2>/…`(20260906・20260907 も `[]`)。

## ㊃ ㋒ 両対照(`10` `11` `11b`・写し guard_copy.sh・log_dir = `_after/guard_copy_log/`)

写し = 生器と `diff` で L22 一行のみ違ふ(`10`・写し sha256 5dedb93cff0d1bdd…)。

| # | 枝 | 入力 | rc | stdout | stderr 行 | log に落ちた行(逐語・先頭) |
|---|---|---|---|---|---|---|
| 陰① | 通る | `{"tool_input":{"command":"echo hi"}}` | 0 | 空 | 0 | (0 行) |
| 陰② | 通る | command = `cp scripts/checks/dd169_kill_term_guard.sh /dev/null`(下線 file 名) | 0 | 空 | 0 | (0 行) |
| 陰③ | 通る | command = `"   "`(空白のみ・`-z` に落ちず regex にも当たらず) | 0 | 空 | 0 | (0 行) |
| 陽① | 塞ぐ | command 空 | 2 | 空 | 2(`date: invalid argument 's' for -I` / `[DD-169 guard] BLOCKED: …`) | `[] PARSE_FAIL: stdin JSON parse 失敗 or command 空 (python_rc=0) input={"tool_input":{"command":""}}` |
| 陽② | 塞ぐ | `{{{` | 2 | 空 | 2(同上) | `[] PARSE_FAIL: … (python_rc=1) input={{{` |
| 陽③ | 塞ぐ | `{"foo":1}` | 2 | 空 | 2 | `[] PARSE_FAIL: … (python_rc=0) input={"foo":1}` |
| 陽④ | 塞ぐ | `{"tool_input":{}}` | 2 | 空 | 2 | `[] PARSE_FAIL: … (python_rc=0) input={"tool_input":{}}` |
| 陽⑤ | 塞ぐ | `null` | 2 | 空 | 2 | `[] PARSE_FAIL: … (python_rc=1) input=null` |
| 陽⑥ | 塞ぐ | `{"tool_input":"x"}` | 2 | 空 | 2 | `[] PARSE_FAIL: … (python_rc=1) input={"tool_input":"x"}` |
| 他① | stdin 空 `</dev/null` | (無) | 2 | 空 | 2 | `[] PARSE_FAIL: … (python_rc=1) input=` |
| 他② | stdin 閉ぢ `<&-` | (無) | ★止★(素: 2m39s 眠り・gtimeout 5: rc 124) | 空 | 0 | (0 行) |
| 他③ | 巨大 300,000 字(通る側) | `echo aaa…` | 0(90 ms) | 空 | 0 | (0 行) |
| 他④ | 巨大かつ壊れ 300,000 字 | `{…}xxxx…` | 2(86 ms) | 空 | 2 | `[] PARSE_FAIL: … (python_rc=1) input={"tool_input": {"command": ""}}xxxx…`(★1 行 300,032 B★) |

- 写し log = 8 entry・行頭分布 `[]` × 8・非空刻 0(`11b` 末尾)。
- 実測 ms(53〜90)は settings.json の `timeout: 5`(秒)に対し 50 倍以上の余裕。★hook timeout は fail-open(公式)ゆゑ、此の余裕は番人の効き目そのもの★。
- 他② の「止」は Claude Code 経路では到達せぬ(公式: stdin JSON は常に渡る)。手打ち・cron・他器からの呼びでのみ起こる。

## ㊄ ㋓ /tmp の実害(`05` `14` `16` `17` `18` `19` `19b` `19c`)

- ★掃除器★: `/System/Library/LaunchDaemons/com.apple.tmp_cleaner.plist` → `/usr/libexec/tmp_cleaner`(毎日 Hour 0・LowPriorityIO)。本文逐語(`18`): `daily_clean_tmps_dirs="/tmp"` / `daily_clean_tmps_days="3"` / `find -dx . -fstype local -type f -atime +3 -mtime +3 -ctime +3 -delete -print` / dir は `-empty -mtime +3`。launchctl: last exit code 0・state not running。★unified log(`log show`)からの最終実行痕は取れて居らぬ(`14` で 120 秒超・`18` で gtimeout 60 に空)= 測れぬ★。
- ★BSD find の丸め★(man 逐語): rounded up to the next full 24-hour period → 3 日と 1 秒でも 4 日と数へ `+3` に当たる。∴ 三つの刻が悉く「3 日超」になつた最初の 0 時に消える。
- ★齢分布(`17`・/private/tmp 直下 普通 file 4437)★: atime 最大 4.52 日 / mtime 最大 6.69 日 / ctime 最大 5.31 日 / birth 最大 41.21 日(dir の中に置かれた 2010 年 mtime の fixture も残る= dir は空でなければ消えぬ・中の file は三条件で消える)。★>5 日の file が atime 0 / ctime 6 / mtime 7 = 三条件 AND が効いて居る形★。次の 0 時に消える物(同述語で今数へた)= 931。
- ★dd169 の 3 本★: 同述語で今 0 本該当。20260913.log は mtime/ctime 09-13T19:41(3.7 日)だが atime が 09-17T07:20:36(誰かが読んだ・己ではない=己の読みは 12:21:34 で 20260917.log の atime のみ動かした)。∴ 09-18 00:00 は生き、★atime が切り上げで 4 日になる 09-21 00:00 に消える★(其れまでに読まれねば)。
- ★消えた物の実在証明(`19c`)★: 過去 session jsonl 5052 本(2.2GB)に `ls -la` の出目(`momizimac wheel <bytes> <月日 時分> 2026MMDD.log`)が写つて居る 7 本(9/2 12518B・9/3 18129B・9/6 701B・9/7 8493B・9/8 1143B・9/11 70904B・9/12 49631B)。陽性対照 = 同 regex が今在る 20260913.log の ls 出目(42196B → 45511B)も拾ふ。20260824 は名の言及 1 のみ(ls 出目無し)= 数へぬ。
- ★∴ 断★: 「監査証跡が消える」は疵であり実害である。DD-169 の番人が「通した時に ps 証跡を録る」為に在るのに、其の証跡は最短 4 日で機械的に消え、既に 7 日分が消えた。刻が空である疵と合はさると、★残つた証跡も「何時」を持たず、消えた証跡は「何が」も持たぬ★。
- 註(`05` の疵): `find /tmp -maxdepth 1 -mtime +3` は symlink /tmp を辿らず 1 を返した(→ /private/tmp で 982)。`05` の数は無効・`14` `17` が正。

## ㊅ 「止」の法医(`15`)

- ps: `bash guard_copy.sh`(78930・S・wchan -)と子 `cat`(78933)。lsof: 両者 `0 PIPE` `1 PIPE` `2w 11_err.tmp`、bash は `255r guard_copy.sh`。
- 機序: `bash file <&-` → bash は script を fd 255 へ移し fd 0 は閉ぢた儘 → `$(cat)` で pipe(2) → 読み口が★最小の空き fd 0★に載る → fork した cat の stdin は其の pipe の読み口 → 書き口は cat 自身の stdout → 誰も書かず EOF も来ず。
- 再現: `gtimeout 3 bash -c 'cat' <&-` = `cat: stdin: Bad file descriptor` rc 1(止まらぬ)/ `gtimeout 3 bash -c 'x=$(cat)' <&-` = rc 124(止)。fd0 probe script(`15_fd0_probe.sh`)= `ls: /dev/fd/0: Bad file descriptor`。
- 止めた手: harness の TaskStop(背景 task bmoet04cg)。塞ぐ側の語を Bash に書かずに済ませた。

## ㊆ ㋔ 直し案(据ゑず・写しで実測 `20`)

### 案A ―― 刻(L26)

```
ts() { date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z'; }
log() { printf '[%s] %s\n' "$(ts)" "$*" >> "$LOG_FILE"; }
```

- ㋐塞ぐ穴: BSD で刻が空になる穴。写し(`guard_copy_fixed.sh`)で 陽①②③・他① の 4 entry 悉く `[2026-09-17T12:31:28+09:00] PARSE_FAIL: …`。stderr から `date: invalid argument` 行が消える(塞いだ時の stderr が 2 行 → 1 行)。PATH 先頭に gdate(GNU)を置いた stub = `2026-09-17T12:31:34+09:00`(gdate -Is と同字面)。`-I` を持たぬ旧 BSD を模す stub = `2026-09-17T12:31:34+0900`(空にならぬ・コロン無し)。
- ㋑塞がぬ穴: 旧 BSD では `+0900` 形になり、GNU/新 BSD の `+09:00` 形と★二方言★になる(讀み手が厳密 ISO を要求すれば割れる)。/tmp の掃除・世界可読・input= 全文投棄・fd0 閉ぢの「止」は此の案の外。
- ㋒誤鳴りの実測: 陰① echo hi = rc 0・stderr 0・log 0 行(変はらず)。塞ぐ/通すの判定行(L50 以降)には一字も触れぬ。
- ㋓戻し方: L26 一行(+ts 一行)を元へ。log の形 `[%s] %s` は不変ゆゑ讀み手の変更不要。既存 log の `[]` 行は其の儘(遡つて刻は付かぬ・付けられぬ)。

### 案B ―― 置き場(L22)

```
LOG_DIR="${DD169_AUDIT_LOG_DIR:-$HOME/.local/state/dd169_audit_log}"
```

- ㋐塞ぐ穴: tmp_cleaner の三条件削除(`$HOME/.local/state` は掃除器の `daily_clean_tmps_dirs="/tmp"` の外)。★可逆★: env `DD169_AUDIT_LOG_DIR=/tmp/dd169_audit_log` で旧挙動・行の戻しは一行。★既存 log を消さぬ★: /tmp の 3 本は動かさず、据ゑる時に `cp -p` で新置き場へ写すのみ(原本は掃除器に任せる・己では消さぬ)。
- ㋑塞がぬ穴: 回転無し(観測最大 70,904 B/日 → 年 25MB 程・当面可)/ 0644 は其の儘(`umask 077` を mkdir の前に置けば塞がるが別件)/ input= 全文投棄は其の儘。
- ㋒誤鳴りの実測: path の差し替へのみ・判定に触れぬ(写しは既に束内 LOG_DIR で 13 組を通して居る = 同じ差し替へ)。
- ㋓戻し方: 一行戻し。新置き場の log は残る(消さぬ)。

### 案C ―― fd0 閉ぢの柵(L30 の前)

```
if ! { : <&0; } 2>/dev/null; then log "PARSE_FAIL: stdin closed (fd0 not open)"; echo '[DD-169 guard] BLOCKED: stdin closed (対称 fail-secure)' >&2; exit 2; fi
```

- ㋐塞ぐ穴: 「止」→ rc 2(写し: rc 124 → 陽④ と同形の即断)。log に刻付き 1 行。
- ㋑塞がぬ穴: Claude Code 経路には無い枝ゆゑ効き目は手打ち・他器のみ。timeout fail-open そのものは settings 側の話(番人の外)。
- ㋒誤鳴りの実測: 陰①・陽①②③・他① の出目は案A 単独と同一(`20`)。
- ㋓戻し方: 一行削除。

★優先★: 案A(刻・一行・誤鳴り 0)> 案B(置き場・env で可逆)> 案C。据ゑるのは家老の伺の後(生器・settings.json には触れて居らぬ)。

## ㊇ ㋕ 測れぬ枝

- 「塞ぐ側の語を含む命令を番人へ渡した時の振舞ひ」: 其の字面を運ぶ Bash 呼びが生の番人に塞がれる為、写しにも渡せぬ。躱さぬ。代はりに既存証跡(読取)に其の枝の出目 19 entry が現に在り(㊂)、刻の欠落は其処でも同じ。
- tmp_cleaner の最終実行刻(unified log): 取れず(㊄)。
- 20260824.log の実在: 名の言及のみ・ls 出目無し(㊄)。
- 己が読む前の /tmp log の atime: 録つて居らぬ(㊈-5)。

## ㊈ ㋖ 疵宣(12)

1. `cat -A` を BSD cat に打ち(illegal option)、`02_l22_l24_l26_catA.txt` が 0 byte に成つた → 臺帳前に消し、`02_…_grep_n.txt`(grep -n)を逐語の正とした。
2. `19` の参照探索は `ugrep` が此の shell に無く(rc 127)、pipe 越しの rc=0(uniq の rc)が其れを隠した ―― ★己の memory(rc を pipe 越しに取るな)を其の儘踏んだ★。`19b` で /usr/bin/grep・陽性対照を先に置いて引き直した(`19` は無効・残すのは疵の証として)。
3. `05` の `find /tmp …` は symlink を辿らず 1 を返した(→ `14` で /private/tmp 982)。`05` の数は無効。
4. 他②(stdin 閉ぢ)を timeout 無しで走らせ、2m39s 眠らせ、Bash 呼び全体が背景へ回つた(`11` は他① で切れて居る)。gtimeout 5 で `11b` に引き直した。「止」は第三の出目と知りながら柵を先に置かなんだ。
5. /tmp の log を読む前に atime を録らなんだ。読んだ後の実測では 13/16 の atime は 07:20:36(己の読み 12:21:34 より前・他者)で、己が動かしたのは 20260917.log のみ(当日 file ゆゑ寿命に影響無し)。
6. `_after/` を測りの生の置き場に用ゐた(慣例は臺帳の後)。名を変へると写しの LOG_DIR 逐語と食ひ違ふ為そのまま臺帳に載せ、臺帳の後の物は `_post/` へ置く。
7. `14` の `log show --last 45d` が 120 秒を超え Bash 呼び全体が背景送りに成つた(出目は其の前で揃つて居た)。`18` の `log show` も空。「log show rc=0」は tail の rc(疵 2 と同根)。
8. `04` の「行種別(第2語)分布」は続き行を含む雑音(entry 28 の内訳は `13` が正)。
9. `20_stub_gnu/date` は gdate への symlink であつた → 臺帳前に消した(出目 `20` に何であつたかは残る)。
10. 「rc=$?」を pipe の後に置いた箇所が `04` `14` `19` に複数在る ―― 其れらの rc は末尾の器の物であり、探索器の rc ではない。数は別途 陽性対照で裏を取つた物のみ結語に使つた。
11. 宣ETA 13:15(56 分)に対し實は納め便の刻。此の紙の刻 12:40 で 21 分・便までの残りは臺帳・門・便。
12. 生の出目を `>`/tee で取つた儘 臺帳へ載せ、門 all(12:43:04・`_gate/mon_km90_20260917T124304_all.log`)が 條②(末尾空白: `04` 1 行・`15` 4 行・`18` 5 行)と 條④(EOF 空行: `11`)で落ちた ―― ★己の memory「生の text は悉く正規化を通せ」を踏んだ★。末尾空白と末尾空行のみを剥ぎ(`_post/12_normalize_whitespace.txt` に前後 sha16・行数)、最初の臺帳(12:43:04 建て・便に未引用)を消して建て直し、門を再度通した(二度目の控は `_gate/mon_km90_<二度目の刻>_*`・最初の控も残す)。

## ㊉ 束の中身

- `_after/01_version_freeze.txt` 版固定 / `02_l22_l24_l26_grep_n.txt` 逐語 / `03_date_measure.txt` date 11 形 + gdate + python / `04_existing_log_readonly.txt` 既存 log の ls・stat・分布 / `05_tmp_cleanup_measure.txt`(無効・疵 3)/ `10_copy_diff.txt` 写しの diff / `11_copy_controls.txt` 両対照 陰①〜他①(他② で切れ)/ `11b_copy_controls_rest.txt` 他②③④ / `11_huge_300k.json` `11_huge_broken_300k.json` 巨大入力 / `12_bsd_gnu_same_instant.txt` 同刻突合 4 TZ / `13_existing_log_entries_verbatim.txt` 全 entry 逐語 / `14_tmp_age_distribution.txt` /private/tmp 齢 / `15_stuck_closed_stdin_forensics.txt` `15_fd0_probe.sh` 止の法医 / `16_tmp_sweep_mechanism.txt` 掃除機構探索 / `17_tmp_cleaner_rule.txt` plist・齢統計 / `18_tmp_cleaner_script_and_predicate.txt` 掃除器逐語・述語 / `19_…`(無効・疵 2)`19b_…` 引き直し `19c_…` 実在証明 / `20_fixed_copy_controls.txt` 直し写しの両対照 / `20_stub_oldbsd/date` 旧 BSD stub / `guard_copy.sh` 写し / `guard_copy_fixed.sh` 直し写し / `guard_copy_log/20260917.log` 写しの log(8 entry・300,711B)/ `guard_copy_fixed_log/20260917.log` 直し写しの log(4 entry)。
- `MANIFEST.txt` 臺帳(束内相対・4 欄)/ `_gate/` 門控(員外)/ `_post/` 臺帳の後(便の胴・門の rc)。
