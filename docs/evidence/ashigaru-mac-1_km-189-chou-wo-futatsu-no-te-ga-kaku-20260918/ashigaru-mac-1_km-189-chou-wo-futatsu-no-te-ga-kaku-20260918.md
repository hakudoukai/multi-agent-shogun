# km-189 ―― 帳を二つの手が書く窓を測れ(紙のみ・直さぬ・据ゑぬ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `km-189-chou-wo-futatsu-no-te-ga-kaku-mado-wo-hakare-20260918`(家老mac 発・裁332455/333060/329271・L4・据ゑ 20:20)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T20:28:52+0900 / 着手便 20:25(宣ETA 21:40)/ 測り 20:25〜20:27
- 枝 = `ashigaru-mac-1/km-189-chou-wo-futatsu-no-te-ga-kaku-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km189)。押さず。
- 出所 = 家老が 20:16 に開けた窓(帳を読んだ 149087 B/鍵 65 → 書く直前 150475 B/鍵 66・當席が km187_nou を足した)。咎でなく測る。

## ㋐ 結語

1. ★帳(queue/tasks/*.yaml)に錠は無い。箱(queue/inbox/*.yaml)には mkdir 式の錠が在る(inbox_write.sh・inbox_watcher.sh・~/bin/inbox_mark_read.py の三器が同じ `<箱>.lock.d` を守る)。★
2. 帳へ書く器 = ⑴家老の焼き器 = Claude Code の Read→Edit/Write(code の外・~/bin にも repo にも帳を書く script は 0)⑵當席の納め = python `open(p,'w')` の読→足→書(錠無し・自認)⑶scripts/slim_yaml.py save_yaml(IDLE_STUB を tasks へ・錠無し・但し此の Mac では `agent_id=='karo'` の時のみ tasks を書く)。三つとも ★三手(読→足→書)・錠無し★。
3. 實射(己の写し・raw/20): 錠無しで二手を重ねると ★鍵が 1 本消えた(senmu1_nou_B・69→70・期待 71)★。mkdir 錠を掛けると 71/71・消え 0。當席の python 形の窓は 0.41〜0.82 ms(150KB・20 回)。家老の焼き器の窓は Read→思考→Edit ゆゑ ★秒〜分の桁(測れぬ・今日の 20:16 の窓に當席が書けた事が證)★。
4. ㋓ 箱の錠は帳を守らぬ ―― 錠の名は `<箱の path>.lock.d` で箱ごと・帳の path には誰も mkdir せぬ。★「箱に錠が在る」は帳の安全の證に成らぬ。★
5. 案は器ごと(㋔・据ゑず・委員長の許可の後)。

## ㋑ census(raw/10)

根 = repo(scripts/lib/hooks・.sh/.py/.bash・bak 除く)+ ~/bin(全拡張子・語 tasks)+ hook(.claude/settings.json の command 4 本)+ watcher(inbox_watcher.sh)。深さ 2〜3。rc 0。刻 20:26。陽性対照 = 語 tasks の網が slim_yaml.py(`queue_dir / 'tasks'`)と inbox_watcher.sh(`os.path.join(…,"tasks",…)`)を拾ふ(km-177 で検めた網)。

| 器 | 書く先 | ⑴三手か | ⑵錠 | ⑶書く手 | ⑷己/他席 | 同時に走り得るか |
|---|---|---|---|---|---|---|
| 家老の焼き器(Claude Code Read→Edit/Write) | queue/tasks/<席>.yaml(他席の帳) | ★三手★(読→足(思考)→書) | ★無し★(Edit 器は「読んだ後に変はつた」を撥ねる仕様が在ると聞くが ★此処では測れぬ★) | Write/Edit 器 | ★他席の帳を書く★ | 在る(人=家老 と 席=當席の納め) |
| 當席の納め(本会話の python) | queue/tasks/ashigaru-mac-1.yaml(己の帳) | ★三手★ | ★無し★ | python open('w') | 己のみ | 在る(家老の焼きと) |
| scripts/slim_yaml.py save_yaml | queue/tasks/*.yaml(IDLE_STUB・archive) | 三手(load→判→dump) | ★無し★(tmp+os.replace は km-181 の案・main には未) | python | 全席(★但し `agent_id=='karo'` の字面のみ・此の Mac の karo-mac は走らぬ★) | 判じ得ぬ(走る席が無い) |
| scripts/inbox_write.sh | queue/inbox/<宛>.yaml | 三手(read→append→write) | ★有★ flock -w 5(Linux)/ mkdir `<箱>.lock.d`(macOS・時限 5 秒)・取れねば失敗 | python(shell 内) | 他席の箱 | 在る(錠で直列) |
| scripts/inbox_watcher.sh(L322/453/541 の subshell) | queue/inbox/<己>.yaml(read 印・auto-recovery 便) | 三手 | ★有★ flock -x 200 / mkdir `${LOCKFILE}.d`(時限 ★無限に近い★=sleep 0.1 の while・回数の上限は行の続きに在るか測れぬ) | python | 己の箱 | 在る(watcher と席) |
| ~/bin/inbox_mark_read.py(家老の器) | queue/inbox/<席>.yaml(read: true) | 三手 | ★有★ mkdir `<箱>.lock.d`・時限 5.0 秒・★fail-closed(取れねば印を打たぬ)★ | python | 他席の箱 | 在る |
| scripts/karo_overload_monitor.sh | /tmp の state/health/dump | ― | 無し | shell | ― | 帳・箱は書かぬ(母數の外・数へた) |
| lib/cli_adapter.sh L886 | config/settings.yaml の history | 三手 | 無し | python yaml.dump | ― | 帳・箱は書かぬ(母數の外・数へた) |
| hook 4 本(stop_hook_inbox・pretooluse_bash_guard・dd169_kill_term_guard・context_usage_warn) | 帳・箱を書くか → stop_hook_inbox は箱を ★読む★のみ(km-177 raw/21)・他 3 本は帳・箱に触れぬ | ― | ― | ― | ― | 書かぬ |

★家老の器を外さぬ★: inbox_mark_read.py(錠有・箱)・karo_mac_manifest_append.py(臺帳へ書く・帳でない・錠無し・tmp+replace で全か無か)・焼き器(Write/Edit・錠無し・帳)。

## ㋒ 實射(raw/20・己の写し raw/seed/utsushi_chou.yaml = 己の帳の写し・160929 B・鍵 69)

| 形 | 手A(家老の形・読んでから 200 ms 後に書く) | 手B(當席の形・読んでから 50 ms 後に書く) | 鍵数(後) | 消えた鍵 |
|---|---|---|---|---|
| ⒜ 錠無し | 読 t=0 → 書 t=200ms | 読 t=10ms → 書 t=60ms | ★70★(期待 71) | ★senmu1_nou_B 1 本★(A が古い読みで上書き) |
| ⒝ mkdir 錠(`<帳>.lock.d`・時限 5 秒・inbox_mark_read.py と同じ形) | 錠を取り 読→書→放す | 錠待ち → 取り → 読→書 | 71 | 0 本・錠 dir 残 0 |
| ⒞ 窓 | 當席の python 形「読む→書く」遅延無し 20 回: ★min 0.41 / median 0.47 / max 0.82 ms★ | ― | ― | ― |

- 窓の意味: 當席の器の窓は 1 ms 未満 ―― 家老の Edit が此の 1 ms に落ちる確率は小さい。★危いのは逆向き★ = 家老の窓(Read→思考→Edit・秒〜分)の中に當席の 1 ms の書きが落ちる事で、今日 20:16 は現に落ちた(消えなかつたのは家老が書く直前に読み直したから)。
- 写しの本体は不変(sha256 前後一致)。共有の帳は触れず。

## ㋓ 箱の錠は帳を守るか

守らぬ。錠は `<箱の path>.lock.d`(inbox_write.sh L26/L249・inbox_watcher.sh L322・inbox_mark_read.py L38)で箱ごとに立ち、帳 `queue/tasks/<席>.yaml` の path に対して mkdir する器は ★0★(census)。∴「箱に錠が在る」事は帳の安全の證に成らぬ ―― 守られて居るのは箱だけである。

## ㋔ 案(★据ゑず・紙のみ・委員長の許可の後★)―― 器ごと

1. 家老の焼き器(Write/Edit): ★「書く直前に読み直して差分のみ足す」★ ―― 何を = 焼く時は Edit の old_string を鍵の末尾でなく「己が足す塊」だけにし、直前 Read で鍵数を数へてから書く / なぜ = Edit は人の思考を挟み窓が長い・錠を Claude Code の器に掛ける術は無い / 戻し = 手順の話ゆゑ無し。理由 = 錠は掛けられぬ器ゆゑ、範囲を狭める法が合ふ。
2. 當席の納め(python): ★「錠を足す」★ ―― 何を = 帳へ書く時 `<帳>.lock.d` の mkdir 錠(時限 5 秒・取れねば書かぬ)を掛け、家老側も同じ錠を見る約束が要る(片側だけの錠は錠でない) / なぜ = 己の形は 1 ms だが家老の窓に落ちる / 戻し = 錠の函数を外す。★但し家老の Edit が錠を見ぬ限り片錠★ → 実効は「書く直前に読み直し己の鍵のみ足す」(範囲を己の鍵に限る)の方が確か。
3. scripts/slim_yaml.py: ★「錠を足す」+ tmp+os.replace★(km-181 の案と同じ) ―― 走る席が此の Mac に無いゆゑ急がぬ。
4. 箱の三器: 既に錠有・据ゑる要無し。★inbox_watcher.sh の mkdir 錠の時限(while sleep 0.1 の上限)は測れぬ★=名指す。

## ㋕ 測れぬ物

- Claude Code の Edit 器が「Read の後に file が変はつた」事を撥ねるか(器の内部仕様・此処では走らせて測れぬ)。
- 他 PC の器(hakudokai の task_sync 等)・稼働中 watcher の錠の時限(★触らぬ★)・人の手(vim 等)で帳を編む場合。
- 家老の焼き器の窓の幅(秒〜分の桁と書いたが数は無い・20:16 の一件は幅の下限 = 當席の書きが挟まる程には長い)。

## ㋖ 疵

⑴ 己の帳の写し(160KB)を束に置いた(實射の種・臺帳に載す)⑵ 「同時に走り得るか」の slim_yaml は走る席が無く判じ得ぬ(0 に丸めず)。

## 宣⇔實

宣ETA 21:40。實 = 納め便の刻(紙の外・20:3x 見込み = 約 1 時間 早い)。
