# -*- coding: utf-8 -*-
"""45 紙を書く器(第74弾)―― 生 00/05/07/10/20/30 の txt から数を引き(轉記の出所を行で指す)、kaki で束の根へ紙を置く。"""
import sys, os, re, time
D = sys.argv[1]; E = D + '/raw'; sys.path.insert(0, E); import kaki as K
def rd(n): return open(E + '/' + n, encoding='utf-8').read()
T00, T05, T07, T10, T20, T30 = (rd(n) for n in ('00_start.txt', '05_chakushu.txt', '07_chukan.txt', '10_yomite.txt', '20_bytegiri.txt', '30_bannin.txt'))
num = lambda pat, txt, alt='?': (re.search(pat, txt) or [None, alt])[1]
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
paper = f'''# 第74弾 ―― 印の川下を測る: 据ゑた乙(␊)の下流に byte 切りは在るか・印は値に戻るか・閾の番人 20箇所6file に己の㋓㋔は何処で当たるか

- 弾: km-74(家老便 msg_20260917_085508_7c3d0548・着手 08:55:08 の札)/ 束 docs/evidence/km-74-shirushi-no-kawashimo-wo-hakare-20260917 / 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻: {koku}(紙を書いた刻)/ 着手便 msg_20260917_085635_a4d1049b(08:56:35)/ 中間便 3 通 09:07:38-39(`07`)/ 凍結点 ★commit 6dbe09e6★(git show で引く・disk と一致 4/4 `00`)
- 器: 讀むのみ。scripts/ へ 0 字・箱へ書かず(己の箱の read:true は家老便 2 通の既讀のみ)・watcher 不觸・send-keys 0・DB便 0。生は `raw/`(以下 `NN`)。臺帳・門控は別 file(門控は員外)。
- ★前提の入れ替へ★: 第72/73弾で引いた四器の sha16(cac867f8/b224557e/6493c1d7/897412b0)は ★捨てた★。本弾の四器= 15ac9f97 / f92cd54e / 7d11ba9f / 3010defd(`00`・git show 6dbe09e6)。

## ㊀ 結語を先に

★㋐ 四器が刷る `_th_say` の行の下流に byte 切りは ★現に 0 本★ ―― 但し「無い」ではなく「讀む器が無い」(讀み手 0/母數 三根)。㋑ 印(␊␍␉)が log の下流で値に戻る路= ★0★(讀む器 0・`$( )` で捕る行 0)。㋒ 閾の番人= 四器の倒す行 20・番人 6 file の倒す行 32 ―― 己の ㋔ が当たる 4 箇所は乙門で ★閉ぢた★、乙が未だ当たらぬ 2 箇所(dasumae_gate:59・gate4:92)を ★先に★ 名指す。★

## ㊁ ㋐ ―― 下流の byte 切り(`10` `20`)

| 問 | 出目 | 器・母數 |
|---|---|---|
| `_th_say` の落ち先 | watcher/health/ctxwarn= stderr(`>&2`)・watchdog= `tee -a $LOG`+stdout(`10` ⑴) | git show 6dbe09e6・源の行 125/73・76/86/32 |
| 落ち先を讀む器(凍結版 repo) | ★0 行★(inbox_watcher log 0・watchdog log 0・health 0・ctxwarn 0) | git grep -n -E 6dbe09e6 -- scripts .claude(書き手の `>>` は除く)・rc 1 |
| 同(~/bin) | ★0 本★/母數 30(.sh .py・深さ 1) | python re・四器の出目を指す語 |
| 同(Mac 起動器) | 書き手のみ(stderr を /tmp/inbox_watcher_$ag.log へ)・讀まぬ | boot-mac-fleet.sh 160 行 |
| 走る process の落ち先 | 己の箱 pid 9826: fd1/fd2 → logs/inbox_watcher_ashigaru-mac-1.log・fd255 → ★旧 inode 20564860★(disk は 22062559) | lsof(`10` ⑸・`00`) |
| 讀み手の中の byte 切り | ★0 本(母數 0)★ ―― 讀み手が無い | ― |
| 四器の中の byte 切り | 4 本(watcher:439 `hex[:8]`・:744 `${{startup_prompt:0:80}}`・watchdog:223 `[:80]`・health:361 `${{sid:0:8}}`)―― ★悉く _th_say の行ではなく閾の値でもない★ | `20` ⑴・形 8 種 |

零の四札: 陽性対照= 同じ git grep が `inbox_watcher.sh` を 7 file 拾ひ、同じ讀み方が ~/bin で `queue/inbox` を 3/30 拾ひ、切りの形は凍結版 scripts 全体で 2 file(pane_identity.sh 3・shogun_report_watcher.sh 1)を拾ふ(`10` `20`)／根と深さ= 凍結版の樹(scripts+.claude)・~/bin 深さ 1・起動器 1 本／rc= 零の grep は悉く 1／刻= `10` `20` の頭。

★己の第73弾 ㋓(18/66)は「切れば割れる」の實證であつて「現に切る器が在る」の證ではなかつた ―― 本弾で其の差を書く。★ ㋓ は凍結版では潜在(讀み手が現れた時に開く)。但し ★人の端末と Claude(hook の stderr を受ける側)は器の外★ ゆゑ数へて居らぬ ―― 其処で切られるか否かは本弾の母數の外。

## ㊂ ㋑ ―― 印が値に戻る路(`10` `30` の 40)

- 四器の中で `_th_say` を `$( )` で捕る行= ★0★(陽性対照= `$(` の総 157/22/31/7)。印は stderr へ出た後、同じ process では値に戻らぬ。
- log を讀んで値を取り出す器= ★0★(㊁)。watchdog の `log()` は tee で stdout へも出し service の `StandardOutput=append:…/service.log` へ落ちるが、其れを讀む器も 0(`10` ⑵)。
- 走る watcher は旧 inode ゆゑ、6dbe09e6 の `_th_say` は ★一度も走つて居らぬ★: logs/inbox_watcher_ashigaru-mac-1.log 43378 行に「閾」0(陽性 `unread` 17196 行)。∴ 印が log に現に在るかは ★未だ測れぬ(respawn の後)★。
- ∴ ㋑= 印を値として讀み返す路は ★器の中に 0★。讀み返すのは人と Claude(紙・端末)。其処での曖昧(元から ␊ が在る値)は乙門(㊃)が入口で消す。

## ㊃ ㋒ ―― 閾の番人 20箇所6file と ㋓㋔ の当たる箇所(`30`)

| file | 閾行 | 倒す行 | 値を刷る行 | 乙門 `*␊*` | 乙置換 |
|---|---|---|---|---|---|
| inbox_watcher.sh | 10 | 5 (149,153,154,161,164) | 164 | 161 | 163 |
| watchdogs/enter_restart_common_watchdog.sh | 14 | 6 (59,100,104,105,112,115) | 115 | 112 | 114 |
| agent_health_check.sh | 11 | 5 (110,114,115,122,125) | 125 | 122 | 124 |
| checks/context_usage_warn.sh | 11 | 4 (60,61,68,71) | 71 | 68 | 70 |
| checks/karo_mac_dasumae_gate.sh | 13 | 7 (38,54,55,56,59,76,80) | ★59 `「${{raw}}」`★ | ★0★ | ★0★ |
| checks/karo_mac_gate4.sh | 10 | 5 (70,87,88,89,92) | ★92 `「${{raw}}」`★ | ★0★ | ★0★ |
| (karo_overload_monitor.sh 2 / fukuincho_desktop_poke.py 1) | 註・表示のみ | 0 | 0 | 0 | 0 |

- 母數= `git grep -l 閾 6dbe09e6 -- scripts` 8 file(内 番人 6)。★裁 323062⑷「20箇所6file」との照らし★: 四器の倒す行の和= ★20★・6 file の倒す行の和= ★32★。「20」は四器の和と一致し「6」は dasumae/gate4 を足した数と一致するが ★二つは同時には立たぬ★ ―― 裁の定義は己の器では一つに閉ぢぬ(家老 km-74 紙 95 行目「閉じて居らぬ」と同じ)。二つの数を並べて置く。
- ★㋔(値に元から ␊)が当たる箇所★= 値を刷る 4 行(164/115/125/71)―― 其の直前の乙門(161/112/122/68)が「入力に ␊␍␉ が既に在れば値を刷らず倒す」(裁 323980⑵・己の ㋔ 12/20 が産んだ一条)ゆゑ ★四器では閉ぢた★。
- ★乙が未だ当たらぬ 2 箇所★= `karo_mac_dasumae_gate.sh:59` と `karo_mac_gate4.sh:92`(`say "…「${{raw}}」…"`・乙置換 0・乙門 0)―― 閾に `\\n` を含めれば stderr の札が二行に割れる(第72弾の形)。★家老が枝で当てる順は此の 2 箇所を先★(番人の残り)。
- ★㋓(byte 切り)が当たる箇所★= 値を刷る 6 行 悉く ―― 但し ㊁ で下流の切りは 0 ゆゑ潜在。

## ㊄ 意味せぬ事(十)

1. 「讀み手 0」≠「讀まれぬ」 ―― 人と Claude が讀む。器の母數の外。
2. 「byte 切り 0」≠「切れぬ」 ―― 第73弾 ㋓ の 18/66 は切れば割れる實證。器が現れれば開く。
3. 「log に閾 0」≠「_th_say は鳴らぬ」 ―― 走る器が旧 inode(00)。respawn の後に測り直す物。
4. 「四器で ㋔ 閉ぢた」≠「番人 全部で閉ぢた」 ―― dasumae:59・gate4:92 は乙 0。
5. 「20 と 32」≠「裁が誤り」 ―― 定義が書かれて居らぬ。己は二数を並べた丈。
6. 「$( ) 捕り 0」≠「値に戻らぬ」 ―― pipe(`2>&1 | while read`・watcher:606)は switch_cli の stderr であつて _th_say ではない。他の捕り方(ファイル経由)は讀む器 0 で消えるが、母數は凍結版 repo と ~/bin・起動器に限る。
7. 「起動器は /tmp へ結ぶ」≠「走る器は /tmp へ書く」 ―― 走る器は logs/ へ(lsof)。起動元 未特定。
8. 「disk が凍結版と一致」≠「走る器が凍結版」 ―― inode 20564860≠22062559。
9. 「四器内の切り 4 本」≠「疵」 ―― uuid・startup_prompt・topic・session id の切りで閾の値ではない。ASCII なら割れぬが、topic(:223)は多 byte を含み得る ―― 本弾の問の外ゆゑ数へた丈。
10. 「宣の式」≠「實」 ―― 式は根を見せる為であつて當たりを約さぬ(㊅)。

## ㊅ 宣⇔實(`05` `07`)

- 宣ETA 11:00(着手便 08:56:35 起点・端点= 納め最終便の timestamp)。式= 器 8 本×10 分=80 + 紙 25 + 便 19 = 124 分(中間便 3/3)。
- 實は納め便の刻で閉ぢる(納め便に書く)。中間便は 09:07:38-39(課= 09:50 迄・達)。

## ㊆ 疵の申告(己)

⑴ 着手便が ★744 字★(300 字の條を越えた・`05`)―― 中間便から 300 字以内に割つた(231/281/194)。⑵ `20` の結びを初版で「2 本」と頭で書き、器の数 4 に直した(`20` に残す)。⑶ `05` 初版は yaml module 無しで倒れ、箱を鍵で割く形に直した(箱は 08:58:26 に回転し着手便は archive へ落ちて居た ―― 両方を引く)。⑷ `30` 初版は f-string の backslash で倒れ、数へてから文にする形に直した。⑸ 中間便 初版 2 通は 344/322 字で門に落ち、3 通に割つた(`07` の門は 0 鳴で通)。⑹ 員外(臺帳の頭で宣す): `_after/*`(門の出目)・`50_build_manifest.*`(臺帳の後)。
'''
K.kaku(D + '/ashigaru-mac-1_km-74-shirushi-no-kawashimo-wo-hakare-20260917.md', paper); print('紙', len(paper.split(chr(10))), '行')
