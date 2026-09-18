# km-191 ―― 変数名が多byte 文字を呑む形を数へよ(紙のみ・直さぬ・据ゑぬ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `tsugi_no_tama_191_20260918T2040`(task_id km-191・家老mac 発・家老自身の疵を種・板は起票後に家老が焼く)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T20:39:42+0900 / 着手便 20:36(宣ETA 21:20)/ 測り 20:35〜20:38
- 枝 = `ashigaru-mac-1/km-191-tabyte-ga-hensuumei-wo-nomu-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km191)。押さず。束名は家老の指定 `docs/evidence/km-191-tabyte-ga-hensuumei-wo-nomu-20260918/`(席の冠無し)。
- 出所 = 家老が 20:30 に `say "… rc=$rc★"` と書き、`set -u` ゆゑ `rc★: unbound variable` で門が止まつた。★無ければ空文字に化けて通つて居た。★

## ㋐ 結語

1. ★bash は現場の locale(C.UTF-8・raw/22)で ★ 。 ） 、 » あ é 😀 全角空白 を ★悉く★ 変数名に呑む(raw/24)。C(素)では呑まぬ。zsh は字(あ・é・Ａ)だけ呑み記号は呑まぬ。★ 呑まれるのは ★多byte の先頭 byte だけ★(bash は byte 単位で isalnum を判ずる)ゆゑ、set -u 無では「値が消え・字が壊れる」(`rc=★` → `rc=��`・raw/20・24)= ★鳴らぬ疵★。
2. census(㋐): 己の樹(origin/main)の sh/bats 149 file で 甲(`${名}`+多byte)65・★乙(裸 `$名`+多byte)7★・丙(`"$名"`+多byte)0。~/bin(家老の器・除かず)甲 18・★乙 1★・丙 0。共有樹(比較)甲 125・乙 14(家老の樹の写し込み)。乙 の内 註 1(樹B)・heredoc 0。★重なり(km-184/187/188)0★。
3. 乙 code 7(樹B 6 + ~/bin 1)の分け(㋑): ⑴ `set -u` 在る器の中 = ★5★(到達すれば即 rc 127 で止まる)⑵ 無い器の中 = ★2★(黙つて空・字が壊れる=危い)⑶ 到達せぬ行 = 0(悉く到達し得る路・条件は ㋒ の表)。
4. 實射(㋒): 己の写しで同じ一行を set -u 有/無で走らせ rc と字面を並べた。`${名}` に直せば無事、半角の後続(`$rc:`)は起きぬ(陰性対照)。乙 7 行の各々も切り出して走らせ ★7/7 が bash・C.UTF-8 で壊れた★(raw/23・25)。
5. 案は ㋔(据ゑず)。

## ㋑ census の作り方(raw/01・10・12・13・14)

- 器 = raw/01_walk_dollar_multibyte.py(己・python os.walk・読むのみ)。根 = 樹の頂・除外 .git/node_modules/.venv/__pycache__/queue/docs/evidence・bak 名除く。sh/bash/bats のみ(py は `$名` を持たぬ)。深さ 樹B 10・~/bin 1・樹C 13。rc 0。刻 20:35。
- 網: 乙 = `(?<![\\$])$名(?=非ASCII)` / 甲 = `${名…}(?=非ASCII)` / 丙 = `"$名"(?=非ASCII)`。行が註(`#` 始まり)か heredoc(`<<'EOF'` は展開無・`<<EOF` は展開有)かを印す。file 単位で `set -u`/`-eu`/`-euo`/`set -o nounset` の有無。
- 陽性対照(raw/12): 己の種 5 形(乙 code・甲・半角・丙・註の乙・展開無 heredoc の乙)= 悉く期待通りに分かれた。
- ★網の限り★: `$名` の直後が非ASCII の行しか拾はぬ。`$名` の直後に半角記号が来て其の後に多byte が続く形は安全(呑まれぬ)ゆゑ拾はぬで正。変数展開を `eval`/`envsubst` で行ふ形・python の f-string は網の外。

## ㋒ 乙 code 7 行の判(raw/23・25)

| 器:行 | 直後の字 | set -u | 到達の条件 | 切り出し實射(bash 3.2・C.UTF-8/ja_JP.UTF-8) | 判 |
|---|---|---|---|---|---|
| scripts/checks/codex_exec_sandbox_guard.sh:58 | `$INTENDED_CWD。` | 有 | ★成功路(OK を刷つて exit 0)= 毎回★ | set -u: rc 127 `INTENDED_CWD�: unbound` / 無: `cwd=��Codex…` | ★止まる(成功路で門が死ぬ)★ ―― 但し此の器が bash+UTF-8 で現に呼ばれて居るかは測れぬ |
| scripts/karo_overload_monitor.sh:338 | `$m5。` | 有 | 輻輳検知の alert 路 | 全長で再走: rc≠0 `m5�: unbound` | 止まる(alert が飛ばぬ)・器は不走(pgrep 0) |
| tests/checks/pretooluse_stdin_json/smoke_test.sh:124 | `$fires、` | 有 | pass 路(fallback 経路で発火した時) | rc 127 | 止まる(通つた試験が落ちる) |
| tests/smoke/test_enter_restart_watchdog.sh:190 | `$enter_count、` | 有 | pass 路(cap halt) | rc 127 | 止まる |
| ~/bin/fleet_liveness_check.sh:73(家老の器) | `$ok。` | 有 | ALERT=1 の路(役職 pane 不在) | rc 127(多行文字列の中) | ★止まる = 不在の警報が飛ばぬ(鳴らぬ番人)★ |
| first_setup.sh:196 | `$NODE_VERSION）` | ★無★ | Node <18 の warn 路 | 無: rc 0 `（現在: ��` | ★黙つて壊れる(版が消え字が壊れる)★ |
| shutsujin_departure.sh:264 | `$SHELL_OVERRIDE）` | ★無★ | -shell に bash/zsh 以外を渡した時 | 無: rc 0 `（指定値: ��` | ★黙つて壊れる(指定値が消える)★ |

- 註の乙 1(樹B: 註行)は効かぬ。heredoc の乙 0。
- ⑵ の 2 本が「鳴らぬ疵」: 値は消え、刷られた字は壊れ、rc は 0。
- ★到達せぬ行 = 0★ と書くが「常に到達する」でもない: 到達の条件を表に書いた(推量でなく code の読み)。

## ㋓ 何処までが名か(raw/21・24・實測・推量に非ず)

| 直後の字 | bytes | bash 3.2 / 5.2(C) | bash(C.UTF-8 = 現場) | bash(ja_JP.UTF-8) | zsh(C) | zsh(C.UTF-8) |
|---|---|---|---|---|---|---|
| a / 9 / _ | 61/39/5f | 呑 | 呑 | 呑 | 呑 | 呑 |
| - / : / . | 2d/3a/2e | 否 | 否 | 否 | 否 | 否 |
| ★ 。 ） 、 » 😀 全角空白 | e2../e3../ef../c2../f0..| 否 | ★呑★ | ★呑★ | 否 | 否 |
| あ é Ａ | e381../c3a9/efbca1 | 否 | ★呑★ | ★呑★ | 否 | ★呑★ |

- bash: UTF-8 locale では多byte の ★先頭 byte★ が isalnum と判じられ名に呑まれる(出目 `72633d9885` = `rc=` + 残り 2 byte・★先頭 e2 が消えて居る★)。∴「多byte は呑まれぬ」は誤り。★呑まれるのは先頭 1 byte のみ★ ―― ゆゑに set -u 無では値が空に化け字が壊れる。
- zsh: 字を単位に判じ、字(alnum)は呑み記号は呑まぬ。
- 隣の形(㋓): 半角英数・下線は周知の通り呑む。`-`・`:`・`.` は呑まぬ(陰性対照)。

## ㋔ 案(★紙のみ・据ゑぬ・委員長の許可の後★)

1. 撲つ検め器: raw/01 の乙の網(`$名` の直後が非ASCII・註と展開無 heredoc を除く)を shellcheck の後に一つ置き、乙 ≥1 で rc 1(出す前門の條に足す形でなく ★独立の器★として)。
2. 直し方は一律 `${名}` で足りる(甲は 65+18 本 現に在り・壊れぬ)。7 行の一行づつの差は `$名多byte` → `${名}多byte`。
3. 併せて `set -u` の無い 2 器(first_setup.sh・shutsujin_departure.sh)は `${名}` にせぬ限り黙る ―― 検め器は set -u の有無に依らず字面で撲つ。

## ㋕ 測れぬ物

- 各器が現に bash・C.UTF-8 で呼ばれるか(hook から呼ばれる codex_exec_sandbox_guard は Claude Code の bash の locale に依る・此処では env を測れぬ)。
- 他 PC(Linux)の locale と bash 版・/bin/sh(dash)の判じ方。
- 共有樹の乙 14 は家老の樹の写し込み 6 を含む(重複・数へたが判じぬ)。

## ㋖ 疵

⑴ 着手便 300 字超 1 度(352)⑵ 「何処までが名か」の初版は字面(unbound)で判じ bash 5.2 の日本語 message を取り落し 否 と誤つた → byte で判じ直した(round1 控)⑶ 切り出し實射で 150 字で切つた行が syntax error に成つた(全長で再走・raw/25)。

## 宣⇔實

宣ETA 21:20。實 = 納め便の刻(紙の外・20:4x 見込み)。
