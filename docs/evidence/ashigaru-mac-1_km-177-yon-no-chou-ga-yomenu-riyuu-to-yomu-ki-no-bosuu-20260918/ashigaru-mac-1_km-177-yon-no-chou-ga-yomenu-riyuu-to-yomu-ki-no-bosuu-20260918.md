# km-177 ―― queue/tasks/ashigaru-mac-4.yaml が parse 出来ぬ真因と、読む器の母數(測るのみ・直さぬ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `km-177-yon-no-chou-ga-yomenu-riyuu-to-yomu-ki-no-bosuu-20260918`(家老mac 発・板外 裁332455・据ゑ 17:40)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T18:09:56+0900 / 着手便 18:05(宣ETA 18:50)/ 測り 18:04:35〜18:08:24
- 的 = `queue/tasks/ashigaru-mac-4.yaml`: 114132 byte・857 行・CR 0・sha256 `a727520c45e7b8e7e284932612363887769621e915910a65b6c5b6b3f9c96ddc`・mtime 2026-09-03T17:22:30・★git 追跡外★(blame 不可)。raw/10・15。
- ★直さぬ・消さぬ・戻さぬ★(第一条・変更統制)。治し方は ㋕ に案として書くのみ。

## ㋐ 結語

1. ★真因 = 根(document root)の block mapping の途中に block sequence の項が 4 本、col 1 に置かれて居る★(L275 `- saitei_z45:` / L292 `- task:` / L379 `- task_id: km-a4-…` / L418 `- id: saitei_z69`)。PyYAML は根を mapping と決めた後に `-` を見て `expected <block end>, but found '-'` を投げる(raw/11 逐語)。memory「YAML block sequence + trailing keys = unparseable」の鏡像(彼は sequence の後に鍵・此は mapping の後に sequence・同じ「根で二種の node を混ぜる」形)。
2. ★読む器の母數★: 帳を「席名で開く器」は 6 本(scripts/inbox_watcher.sh・slim_yaml.py・agent_status.sh・karo_overload_monitor.sh・checks/secondpc_dispatch.sh・lib/cli_adapter.sh の文言)。其の内 ★mac-4 の帳を今の Mac で実際に読み得る物は 0★: watcher は mac-4 に無く(pgrep 0・tmux pane 0・log は 09-03 16:36 で止まる)、slim_tasks は `agent_id == 'karo'`(字面)の時のみ全帳を歩き此の Mac の家老は `karo-mac` ゆゑ走らず、agent_status は §18 配列(karo/gunshi/a1-3/a5-8)を歩き mac-4 を含まず、overload_monitor は grep 読み(parse せず・不走)、secondpc_dispatch は -f/stat のみ、cli_adapter は起動 prompt の文言。
3. ∴ ★parse 不能は「今は誰も踏まぬ残骸」であり、★踏む道が二つ眠つて居る★: ⓐ 誰かが `slim_yaml.sh karo` を此の樹で走らせれば stderr に「Error parsing …」を出し {} を返して ★黙つて飛ばす★(raw/29 実測)。ⓑ mac-4 に watcher が立てば auto-recovery の status guard が `except Exception: pass`(inbox_watcher.sh L463)で ★黙つて guard を素通り★し、cancelled/idle でも再着手便を打つ。両方 fail-open。

## ㋑ ⑴ 真因(raw/11・12・13・14)

- 例外逐語(pyyaml 6.0.3・python 3.14.6): `while parsing a block mapping / in "queue/tasks/ashigaru-mac-4.yaml", line 1, column 1 / expected <block end>, but found '-' / in "…", line 275, column 1`。context_mark = L1(`agent_id: ashigaru-mac-4` = 根 mapping の始まり)・problem_mark = L275 col 1。
- L270-280 逐語は raw/12。L274 は `# ════` の註、L275 `- saitei_z45:` から 4 空白下げの鍵(timestamp/from/title/body)が続く = ★家老の裁の便を「sequence 項」として根に追記した形★。同形が L292・379・418 に計 4 本。L482 以降は再び根の鍵(`saitei_z76:` 等 21 本・raw/14)に戻る ∴ 「mapping → sequence → mapping」。
- 何が壊したか = ★形の混在★であり、字(全角・CR・TAB)ではない(CR 0・safe_load は L275 の `-` で止まる)。L275 の `- ` を `  `(2 空白)や鍵名に替へれば根 mapping に戻る筈だが ★当てて居らぬ★(直すな)。

## ㋒ ⑵ 読む器の母數(raw/20〜29)

- 歩いた根(宣): scripts/lib/hooks/config/tests/bin/instructions/shim/agents/skills/docs/.claude/CLAUDE.md/AGENTS.md/dashboard.md + ~/bin。★歩かぬと宣した物★: queue/(13.2GB)・docs/evidence・.git・node_modules・.venv。python の os.walk(ugrep/.gitignore に依らず)・file 1018・最大深さ 13・rc 0(raw/20)。
- 網 三重(排他ではない・各々の陽性対照を書く):
  | 網 | 字面 | 出目 | 陽性対照 |
  |---|---|---|---|
  | 一 | literal `ashigaru-mac-4` | 108 行 / 19 file(dashboard.md 84・settings.yaml 2 + bak 6・docs 3・scripts/karo_standby_dashboard.sh 1・~/bin karo_mac_read.py 1 + bak 11) | settings.yaml L138 agents 一覧に在る(既知)= 拾つた |
  | 二 | `queue/tasks/<var>.yaml` | 336 行 / 107 file(.claude 157・instructions 121 = 指示書の文言・scripts 12・lib 1) | inbox_watcher.sh = 拾つた(但し L470 の文言で) |
  | 三 | 語 `tasks`(join 形も拾ふ・scripts lib hooks ~/bin の .sh/.py/.bash・bak 除く) | 10 行 / 6 file | ★slim_yaml.py(`queue_dir / 'tasks'`)= 網一・二では 0 行 → 網三で 2 行★(raw/23・25) |
- ★網一・二の穴★: path を `os.path.join(…, "tasks", …)`・`queue_dir / 'tasks'` と組む器は `queue/tasks` の字面を持たぬ。網三で埋めたが、変数名で組む器(`$TASKS_DIR/$f`)は語 `tasks` を持つゆゑ拾へる。持たぬ形(例: 定数を別 file から import)は ★測れぬ★。
- 器 6 本の読み方(raw/21・24・26・28・29):
  | 器 | 何を読む | parse? | mac-4 を読むか(今の Mac) | 失敗時 |
  |---|---|---|---|---|
  | scripts/inbox_watcher.sh L449-463 | auto-recovery 時に `tasks/{agent_id}.yaml`(己の席のみ) | safe_load | ★否★(mac-4 の watcher 0・pane 0・log 09-03 止) | `except Exception: pass` → guard 素通り(fail-open) |
  | scripts/slim_yaml.py slim_tasks L96-140 | `tasks/*.yaml` ★全席★ | safe_load(load_yaml) | ★否★(`agent_id == 'karo'` 字面の時のみ・此の Mac は karo-mac) | stderr「Error parsing …」+ {} → `continue`(飛ばす・rc 0)= raw/29 実測 |
  | scripts/agent_status.sh L175-193 | `tasks/${agent_id}.yaml`(§18 配列の席) | safe_load | ★否★(配列に mac-4 無し) | `except Exception: print('--- ---')` |
  | scripts/karo_overload_monitor.sh L317 | `$TASKS_DIR/ashigaru*.yaml` 全席 | ★grep のみ★(`status: assigned`) | 読み得る(mac-4 L6 `status: assigned` を数へる)が ★不走★(pgrep 0) | parse せぬゆゑ壊れに気づかぬ |
  | scripts/checks/secondpc_dispatch.sh L24 | `tasks/${TARGET}.yaml` | -f と stat のみ | 手動 | ― |
  | lib/cli_adapter.sh L351 | 起動 prompt の文言「Read queue/tasks/…」 | ― | ― | ― |
- 零の札: 「mac-4 を今読む器 0」= 根 上記・深さ 13・rc 0・刻 18:04〜18:08・陽性対照 = 同じ網が a1-3 の watcher(pgrep 3・pane 3)と slim_yaml.py を拾つた。

## ㋓ ⑶ 他席との形の差(raw/30)

| 帳 | safe_load | 行 | byte | 根の鍵(`^key:`) | 根の `- ` | `---` |
|---|---|---|---|---|---|---|
| ashigaru-mac-1 | OK(dict・54 鍵) | 1023 | 112427 | 41 | ★0★ | 0 |
| ashigaru-mac-2 | OK(dict・39) | 714 | 70794 | 31 | ★0★ | 0 |
| ashigaru-mac-3 | OK(dict・36) | 680 | 74798 | 27 | ★0★ | 0 |
| ashigaru-mac-4 | ★ParserError L275★ | 857 | 114132 | 54 | ★4★ | 0 |

差は一つ: 根に `- ` 項が在るか否か。大きさ・鍵数・CR・`---` は因でない(mac-1 の方が大きく鍵も多い)。

## ㋔ ⑷ 陽性対照(raw/50)

mac-1 の帳の写し(parse OK)を mktemp dir に置き、末尾に根の sequence 項 `- kowashi_z99:` を足す → 同じ `ParserError … expected <block end>, but found '-'`(problem L1026 col 1・context L1)。写しは /tmp(消した)・出目は束に写した。無傷の写しは OK ∴ 器は「根の `- `」に鳴る。

## ㋕ 治し方の案(★据ゑぬ・家老が伺を立てる★)

- 案 A: L275/292/379/418 の `- ` を外し(`saitei_z45:` 等の根の鍵に)、4 塊の内側を 2 空白へ揃へる = 他 3 席の形に合はせる。可逆(git 追跡外ゆゑ写しを取つてから)。
- 案 B: 席が孤児(pane 0・watcher 0)ゆゑ帳を queue/archive/tasks へ退避し、tasks/ には idle stub を置く。読む器が現れた時に黙つて飛ばされる残骸を無くす。
- 併せて: slim_yaml.py load_yaml と inbox_watcher.sh L463 の fail-open(黙つて飛ばす/素通り)は ★別件★として名指すのみ。

## ㋖ 意味せぬ事・測れぬ物

- 「読む器 0」は今の Mac の process と配列の話。他 PC(main/second)で `slim_yaml.sh karo` が走れば此の帳(が同期されて居れば)を読む ―― 他 PC は測つて居らぬ。
- 網三は語 `tasks` に依る。定数を import で受ける器は拾へぬ(上記)。
- logs/*.log は 9 本悉く 1MB 以上ゆゑ ★歩かなかつた★(mac-4 の watcher log 437 行のみ読み ParserError 0)。
- 誰が L275 の形を書いたかは git 追跡外ゆゑ blame 出来ぬ(mtime 09-03 17:22・内容から家老の裁便の追記と読めるが断じぬ)。

## ㋗ 疵

⑴ 着手便 300 字超 1 度 ⑵ 網一・二の陽性対照(slim_yaml)が 0 行で落ち、網三を足した(網の穴を先に見つけたのは対照) ⑶ pgrep -fl が己の sed の argv を拾つた(`inbox_watche[r]` で取り直し・raw/42→43)⑷ find の根を `.` にして queue/reports の無権限 fixture を踏み stderr 1 行(出目に影響無し)。

## 宣⇔實

宣ETA 18:50。實 = 納め便の刻(紙の外・18:1x 見込み)。
