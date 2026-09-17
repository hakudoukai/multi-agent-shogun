# 第75弾 ―― 閾の母數を四つの定義で確定せよ: 甲(呼出)・乙(定義 file)・丙(文言)・丁(${NAME:-數} の口)を別々の表で数へ、裁の「20箇所6file」が何れで立つかを名指す

- 弾: km-77(家老便 msg_20260917_093017_d2d78833・札 sha16 0071c1170585d43d 77 行= 追記 msg_…_093133 の正)/ 束 docs/evidence/km-77-shikii-no-bosuu-wo-yotsu-no-teigi-de-kakutei-seyo-20260917 / 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻: 2026-09-17T09:40(紙を書いた刻)/ 着手便 09:32:53(宣ETA 10:15・起点= 着手便 timestamp・端点= 納め最終便 timestamp)/ 凍結点 ★HEAD 6ba8fcb2★ ―― 但し ★的の樹は disk と HEAD で 8 file 違ふ(`00`)★。生器は disk・家老の器(rev 無しの git grep)も disk ゆゑ ★主= disk・副= HEAD★ を毎表に併記する。
- 器: 讀むのみ。scripts/ .claude/ ~/bin/ へ 0 字・箱へは家老便 3 通の既讀印のみ・watcher 不觸・send-keys 0・DB便 0。生は `raw/`(以下 `NN`)。臺帳・門控は別 file(門控は員外)。
- ★㋗★: 專任3 の束 km-52-shikii-no-bosuu-wo-kakutei-seyo-20260917 は ★此の紙を書いた時点で一字も讀んで居らぬ★(ls で名を見た丈)。突合は納めの後 `_after/70` と追ひ便で行ふ。

## ㊀ 結語を先に

★㋑ 裁の「20箇所6file」は ★甲′(fix_threshold の語を含む行の総数= 定義+呼出+註)を HEAD 6ba8fcb2 で数へた時★ に丁度立つ(20 行 / 6 file・`git grep -c fix_threshold 6ba8fcb2 -- scripts .claude`= 4+3+3+3+2+5)。disk では 22 行 / 7 file(shogun_report_watcher.sh が未 commit で加はつた)。甲(呼出行のみ)・乙(定義 file)・丙・丁の ★何れでも 20 と 6 は同時に立たぬ★。★㋒ 番人無しの口(丁閾 23 口の内)= A 5 口/2 file + A′ 1 口(他 file が守る)+ B 4 口/2 名 ―― 家老の「4 file」は stop_hook が ★別形の番人(case…既定へ倒す)★ を持つゆゑ 3 file+A′ 1 に直る。B は ASW_PROCESS_TIMEOUT に加へ ★ASW_NO_IDLE_FULL_READ★ が同じ形で守られて居らぬ(家老の見立に無い)。★㋓ 番人無し ∧ 數比較器(-lt 等)へ入る口= ★0★ ―― 現に fail-open し得る口は無い(水増しせず)。★

## ㊁ 定義甲 ―― fix_threshold の呼出(`10` / 10_kou.tsv)

條: 行頭空白+`fix_threshold`+空白 を ★呼出行★・`^fix_threshold(){` を定義・`#` 起しを註。器= `git grep -n -E fix_threshold [rev] -- scripts .claude`(git 追跡 file 全深・archive/ 含む)。

| rev | 総行 | 定義 | 呼出行 | 内 loop 行 | 註 | 呼出 file | ★守る名(明示+loop list)★ |
|---|---|---|---|---|---|---|---|
| disk | 22 | 7 | ★14★ | 1(inbox_watcher:177) | 1 | 7 | 13 + 10 = ★23★ |
| HEAD 6ba8fcb2 | 20 | 6 | 13 | 1(:165) | 1 | 6 | 12 + 10 = 22 |

- loop list(inbox_watcher `for _t in … ; do` の 10 名)= APPROVAL_ALERT_COOLDOWN ASW_PHASE ESCALATE_COOLDOWN ESCALATE_PHASE1 ESCALATE_PHASE2 INOTIFY_TIMEOUT MAX_TYPING_SKIP NUDGE_COOLDOWN_SEC NUDGE_COOLDOWN_SEC_CLAUDE NUDGE_COOLDOWN_SEC_CODEX。
- 家老の 09:26「甲 13 行」は ★HEAD の呼出行 13★ と一致し disk の 14 と食ひ違ふ ―― 差= shogun_report_watcher.sh:78(未 commit)。「13 の内 :177 は loop」も其の儘。
- 零の札: 陽性= 同じ器が disk 22/HEAD 20 行(rc 0)・陰性= 樹に無い語 ZZ_KM77_NEGATIVE_9x7q 0 行 rc 1・根と深さ= scripts .claude 全深・刻= `10` の頭。

## ㊂ 定義乙 ―― fix_threshold() の定義を持つ file(`10` / 20_otsu.tsv)

| rev | file | 名 |
|---|---|---|
| disk | ★7★ | agent_health_check / checks/context_usage_warn / checks/karo_mac_dasumae_gate / checks/karo_mac_gate4 / inbox_watcher / ★redundancy/shogun_report_watcher★ / watchdogs/enter_restart_common_watchdog |
| HEAD | 6 | 上から shogun_report_watcher を除く |

- 家老の「乙 7 本」= disk と一致。條= `^fix_threshold(){`(行頭・関数定義の一形のみ ―― `function fix_threshold` の形は樹に 0 ゆゑ取り零し無し・陽性 7 陰性 0 rc 1)。

## ㊃ 定義丙 ―― 「既定へ倒す」/「fail-closed」の文言(`10` / 30_hei.tsv)

條= ERE `既定[^ \t]{0,8}へ倒す|fail-closed`(1 行 1・一行に二度出ても 1)。

| rev | 行 | ★file★ | file ごとの行(註・文字列) |
|---|---|---|---|
| disk | 48 | ★11★ | health 6(1・5)/ codex_exec_sandbox_guard 3(3・0)/ ctxwarn 5(1・4)/ dasumae 6(3・3)/ gate4 4(1・3)/ commander_send_shogun_second 1(1・0)/ inbox_watcher 6(1・5)/ inbox_write 1(1・0)/ shogun_report_watcher 6(1・5)/ stop_hook 4(1・3)/ common_watchdog 6(1・5) |
| HEAD | 27 | 9 | shogun_report_watcher・stop_hook が無く、health/ctxwarn/watcher/watchdog が各 3 |

- 家老の「丙 11 file(1〜6)」= disk と一致(file ごとの数も 1〜6)。★但し丙は「番人」の數ではない★: codex_exec_sandbox_guard(3)・commander_send_shogun_second(1)・inbox_write(1)は ★註のみ★(文言が在るだけで倒す器が無い)。丙 11 の内 ★倒す器を持つ file= 8★(註のみの 3 を引く)。

## ㊄ 定義丁 ―― `${NAME:-數}` の口(`40` / 40_tei_all.tsv・40_tei_shikii.tsv)

條(全)= ERE `\$\{[A-Za-z_][A-Za-z0-9_]*:-[0-9]+\}` 1 出現 1 口(一行に複数可)。條(閾)= ★名が `^[A-Z][A-Z0-9_]*$` ∧ 既定 ≥ 1 ∧ 註行でない★ ―― 家老の「閾らしき名」を ★語感でなく此の條★ に置き換へた。別條(大文字名・註除く・既定 0 も含む)も併記し、條の取り方で數が動く事を示す。

| rev | 丁全(口) | 内 註 | file | 内 archive/ | 別條(大文字・既定 0 含む) | ★丁閾(口)★ | ★file★ |
|---|---|---|---|---|---|---|---|
| disk | 86 | 2 | 18 | 3 file(6 口) | 69 | ★23★ | ★6★ |
| HEAD | 79 | 2 | 17 | 3 | 66 | 22 | 7 |

- 丁閾 23 口の file(disk)= dasumae 2 / inbox_watcher 12 / detect_stale 1 / pane_enter_watcher_supervisor 4 / stop_hook 2 / commander_watchdog 1 … HEAD は其れに shogun_report_watcher:29(旧形 `COOLDOWN_SEC="${…:-60}"`)が加はり inbox_watcher が 1 少ない。
- 家老の「丁 22 口 / 8 file」とは ★口も file も一致せぬ★(己 23/6・HEAD 22/7)。家老の條が書かれて居らぬゆゑ「どちらが正」は言へず ★「口の條(既定 ≥1 か・註を除くか・archive を除くか)と file の條が違ふ」★ と書く。同じ樹で 86→69→23 と條ごとに動く數ゆゑ、條の無い 22 は突き合はせに使へぬ。
- 零の札: 陽性 disk 80 行/HEAD 73 行 rc 0・陰性 0 行 rc 1・根と深さ= 同上・刻= `40` の頭。

## ㊅ ㋑ ―― 裁の「20箇所6file」は何れで立つか(`10`)

| 定義 | disk | HEAD | 20 と 6 が同時に立つか |
|---|---|---|---|
| 甲 呼出行 / file | 14 / 7 | 13 / 6 | ✗(6 は立ち 20 は立たぬ) |
| ★甲′ 語を含む総行 / file★ | 22 / 7 | ★20 / 6★ | ★HEAD で立つ★ |
| 乙 定義 file | 7 | 6 | ✗ |
| 丙 文言 file | 11 | 9 | ✗ |
| 丁閾 口 / file | 23 / 6 | 22 / 7 | ✗ |
| (第74弾 ㋒)四器の倒す行 / 6 file の倒す行 | 20 / 32 | ― | ✗(20 は立つが file は 4) |

∴ ★裁の 20/6 は「甲′= `git grep -c fix_threshold` を HEAD で足した數」と読める★(4+3+3+3+2+5= 20・file 6)。之は定義・呼出・註を混ぜた語の數であつて「番人の箇所」でも「閾の口」でもない。委員長へ持つて行くなら ★「20箇所6file は fix_threshold の語の行数(HEAD)。disk では 22/7。番人の口は丁閾で 23/6」★ の三行で。

## ㊆ ㋒ ―― 番人無しの口(`40` / 45_bannin.tsv・disk)

判定條を先に: **A**= file に fix_threshold の定義も呼出も無し / **A′**= 己は無しだが ★他 file が同じ名を fix_threshold で守る★(env で渡る)/ **B**= 呼んで居るが其の名が arg1 にも for list にも無し / **C**= 守られて居る / **C′**= fix_threshold ではなく `case "$X" in … 既定へ倒す` の ★別形の番人★(口の後 6 行内に丙の文言)。

| 態 | file:line | 名 | 受け皿 |
|---|---|---|---|
| A | scripts/lib/detect_stale.sh:33 | DETECT_STALE_STALE_SEC | var(★樹全体で此の行以外に現れぬ= 死んだ閾★) |
| A | scripts/pane_enter_watcher_supervisor.sh:50 ×2 | STALE_SEC / POLL_SEC | log 文字列 |
| A | scripts/pane_enter_watcher_supervisor.sh:52 ×2 | STALE_SEC / POLL_SEC | env→子 pane_enter_watcher.py:131/134 |
| A′ | scripts/watchdogs/enter_restart_commander_watchdog.sh:35 | ER_THRESHOLD_MIN | export → exec common_watchdog.sh:120 `fix_threshold ER_THRESHOLD_MIN 10` が守る |
| B | scripts/inbox_watcher.sh:219 / :470 | ★ASW_NO_IDLE_FULL_READ★ | var / 同行 `= "1"` |
| B | scripts/inbox_watcher.sh:224 / :1599 | ASW_PROCESS_TIMEOUT | var / 同行 `= "1"` |
| C′ | scripts/stop_hook_inbox.sh:52 / :177 | STOP_HOOK_STDIN_TIMEOUT / MASS_UNREAD_THRESHOLD | case L53-56 / L184-187 で「數でない→既定へ倒す」 |
| C | 残り 11 口(dasumae 20,75・inbox_watcher 197,199,215,295,297,301,899,1067,1535) | ― | fix_threshold |

計: A 5 / A′ 1 / B 4 / C′ 2 / C 11 = 23。家老の見立との差: ⑴ stop_hook は「番人無し」でなく ★C′★ ⑵ commander_watchdog は ★A′★(守るのは別 file)⑶ B は ASW_PROCESS_TIMEOUT だけでなく ★ASW_NO_IDLE_FULL_READ★ も(同じ形・同じ file)。

## ㊇ ㋓ ―― 下流に數比較器が在るか(`40` / 47_hikaku.tsv・disk)

條: 受け皿 var が口の後の行で `[ … -lt/-le/-gt/-ge/-eq/-ne … ]` か `(( ))` に入る行番号(一段の経由 `x=$VAR` も辿る)/ 同行比較・同行算術は其の行 / env→子は子 file で名が出る行。★fail-open し得るのは數比較器へ入る口のみ★。

| 口 | 比較器 | 番人 | 疵か |
|---|---|---|---|
| supervisor:52 STALE_SEC/POLL_SEC → 子 .py:131/134 `int(os.environ.get(...))` | 子で int() | A | ★否★ ―― 數でない値は ValueError で ★落ちる(止)★・黙つて通らぬ。但し supervisor の while が再起動を繰り返す(別種・本弾の的外) |
| supervisor:50 ×2 | 無(log) | A | 否 |
| detect_stale:33 | 無(使はれぬ) | A | 否(死んだ閾) |
| commander_watchdog:35 | 無(己)・common_watchdog:120 が守つて比較 | A′ | 否 |
| inbox_watcher:219/470 ASW_NO_IDLE_FULL_READ | `= "1"`(文字列) | B | ★否(-lt 型でない)★ ―― 但し 1 以外の値は黙つて「否」側(full read せず)へ分岐する= 静かな分岐(fail-open ではない・註) |
| inbox_watcher:224/1599 ASW_PROCESS_TIMEOUT | `= "1"`(文字列) | B | 同上(1 以外は黙つて event-only へ) |
| stop_hook:52 → L70 `-ge` / :177 → L194 `-gt` | 有 | C′ | 否(別形番人が先に倒す) |
| C の 11 口 | 有 10(dasumae:20→243・watcher 215→216,217・295/297/301→307・899 同行・1067→1068・1535→1564・197 経由 295→307・199 経由 297→307)/ 無 1(dasumae:75 timeout の秒) | C | 否 |

★∴ 番人無し(A/A′/B)∧ 數比較器 有 = 0 口。現に fail-open し得る口は無い。★ 比較器 有 14(C 10・C′ 2・A の env→子 2)/ 無 9(A 3= log 2・死んだ閾 1 / A′ 1 / B 4= 文字列比較 / C 1= timeout の秒)―― 無は ★疵ではない★。

## ㊈ ㋔ ―― ~/bin 別表(`48`・★的ではない・持ち主= 環境部長・触らぬ★)

母數 .sh .py 30 本(深さ 1)/ `${NAME:-數}` 6 口 / 2 file(fleet_liveness_check.sh:28 FLEET_MIN_PANE_WIDTH:80 ・ idle_backlog_wake.sh:61,130,154,157,205)。内 大文字 ∧ 既定 ≥1 = 2 口(:28・:130)。器= python re(repo 外ゆゑ git grep 不可)・陽性= 同じ re が inbox_watcher.sh で 40 口・陰性 0。裁 seq324404 に従ひ ★本弾の數には足さぬ★。

## ㊉ ㋕ ―― 本弾が意味せぬ事(七)

1. 「甲′ で 20/6 が立つ」≠「裁が甲′ で数へた」 ―― 裁の器は書かれて居らぬ。己は「立つ定義が一つ在る」と言つた丈。
2. 「番人無し ∧ 數比較器 = 0」≠「fail-open が無い」 ―― 丁の條は `${NAME:-數}` の形のみ。`${NAME-}`・`${NAME:=}`・`NAME=${NAME:-$OTHER}`(既定が變数)・python の `os.environ.get` 直讀は ★母數の外★(supervisor→子で一つ見た丈)。
3. 「C 守られて居る」≠「値が正しい」 ―― fix_threshold は非負整数へ倒す丈。上限・妥当域は見ぬ。
4. 「disk」≠「走る器」 ―― 第74弾で見た通り走る watcher は旧 inode。disk の 22/7 も HEAD の 20/6 も ★走つて居る版とは限らぬ★。
5. 「B= 文字列比較ゆゑ疵でない」≠「無害」 ―― 1 以外の値で黙つて分岐する。之を疵と呼ぶかは委員長の條(本弾は ㋓ の條=-lt 型のみ に從ひ疵に数へぬ)。
6. 「丁閾 23/6」≠「閾の全部」 ―― 條は名の形と既定 ≥1。`${X:-0}` で受ける閾(ASW_DISABLE_ESCALATION 等・既定 0)は別條 69 に居て閾條 23 に居らぬ。
7. 「~/bin 6 口」≠「~/bin の番人の數」 ―― 別表は口の數のみ。番人・比較器は測つて居らぬ(的ではない)。

## ㊊ ㋖ ―― 宣と根

宣ETA 10:15(着手便 09:32:53 起点・端点= 納め最終便 timestamp)。根= 第74弾 實 16.2 分 / 器 8 本 = 2.0 分/器 → 本弾 器 10 本(00 10 40 48 50 60 62 70 + 紙 + 便)= 20 分 + 紙 10 + 便 5 = 35 分、第73弾の過小(實 29.5/宣 4)を見て +7 分= 42 分。★實は納め 5/5 に書く(器あたりの實分も)。★

## ㊋ 疵(己の器が倒れて直した所・`.first` に残す)

1. `10` .first: git grep の ERE に `\s` は無く(macOS regcomp)、`for _t in` の續き行 2 本を落として loop list が 3 に縮んだ(守る名 16)→ file 本文から `; do` まで讀んで 10(23)に直した。
2. `40` .first: 同じ `\s` が「他 file の番人」を 0 に落とし(commander_watchdog:35 が A に見えた)→ `[ \t]` に直して A′ が立つた。
3. `40` .first: env 行が `\` で續く時(supervisor:52)子の path が次行に在り「用途」へ落ちた → 續き 2 行を継いで env→子 と子の行 131/134 を引いた。
4. 着手便に「器 10 本」と書いたが実際の器は 00/10/40/48/50/60/62/70 の 8 本+紙+便 ―― 宣の根に書いた本数と一致(10)、疵に非ず。

## ㊌ 員外の宣(㊆⑷)

臺帳に載せぬ物: 臺帳其の物 / 門控 `…_gate.txt` / `raw/50_build_manifest.*` / `raw/50_sengen.txt` / `_after/*`(門の出目・納め便・突合 `70` は臺帳の後の器)。`.first` は員内(倒れた走を消さぬ・⑺)。
