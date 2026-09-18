# km-192 ―― 旗が胴を食ふ形 ―― 便が黙つて壊れる呼び方を数へよ(紙のみ・直さぬ・据ゑぬ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `tsugi_no_tama_192_20260918T2040`(task_id km-192・家老mac 発・家老自身の疵を種・板は起票後に家老が焼く)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T20:47:15+0900 / 着手便 20:44(宣ETA 21:35)/ 測り 20:42〜20:46
- 枝 = `ashigaru-mac-1/km-192-hata-ga-dou-wo-kuu-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km192)。押さず。束名は家老の指定 `docs/evidence/km-192-hata-ga-dou-wo-kuu-20260918/`。
- 出所 = 家老が `sb-karo-mac write letter --to iincho "<本文>" --parent-seq 333753` と打ち、三通(seq333833/333834/333835)の胴が「--to」の 4 字で保存された。器は rc 0・宛も parent_seq も正しかつた。

## ㋐ 結語

1. ★機序★: agent_letter.py は胴を ★`letter` の直後の位置引数 `args[3]`★ から取り、`--to` は `args.index("--to")+1` で別に読む(raw/23 ⒜・L141-145/L189-193 の写し)。∴ 旗を胴の前に置くと ★胴=「--to」(4 字)・宛は正しく・parent_seq も正しく・rc 0★ = 偽の成功。写しの實射で 正 25 字 / 乙 4 字。家老の現物 seq333833/834/835 は ★悉く content=「--to」4 字★(sb read・raw/23 ⒝)。當席の正しい語順の現物 seq333926 は 276 字(対照)。
2. census(㋐・raw/10・13・14): 位置引数を取る helper の呼出 = 己の樹(origin/main)97 件(code 16・例文 81・悉く inbox_write.sh・★乙 0★)、~/bin 35 件(code 8・例文 27・乙 0)、共有樹 218 件(code 30・例文 188・乙 0)。★乙(旗が胴より前)は書かれた器・紙の中に 0★ ―― 家老の疵は ★手で打つた命令★ に在り、script にも例文にも無い。陽性対照の種 2 形の乙は 2/2 当たる(raw/12)。
3. 器の側の守り(㋑・raw/20): agent_letter.py/sb-* = ★受ける(rc 0・偽の成功)★ / inbox_write.sh(旗を持たぬ器)= 受ける(胴「--to」を通す・rc 0)/ board_write.py = 撥ねる(REJECT column・rc 3)/ inbox_mark_read.py = 印を打たぬ(未命中=--to)が ★rc 0★(fail-closed だが黙る)。★既に守りの器が一つ在る★: ~/bin/km_send.sh(家老の私器・胴が旗で始まれば rc 2 で送らず・位置引数が 2 つ以上でも rc 2・渡す argv を刷る)。
4. 告げ口の形(㋓): 送り手の側で捉へ得る徴 = ⑴ agent_letter が刷る「本文 N字 ―― 100字を超えた」の註が ★出ぬ★(胴 4 字ゆゑ)―― 但し短い胴でも出ぬゆゑ弱い徴 ⑵ km_send.sh の「胴=N字 ―― 送る」の行(N=4 で気づける)。「胴の字数が複数便で揃ふ」以外に ★送り手の側の徴は上の二つのみ★。受け手の側の徴は無い(宛・parent は正しい)。
5. 案は ㋔(据ゑず)。

## ㋑ census の作り方(raw/01・10・12・13・14・15)

- 器 = raw/01_walk_helper_calls.py(己・python os.walk・読むのみ)。根 = 樹の頂・除外 .git/node_modules/.venv/__pycache__/queue/docs/evidence・bak 名除く。深さ 樹B 10・~/bin 1・樹C 13。rc 0。刻 20:43。
- 母數の器 = sb / sb-karo-mac / sb-ashigaru-mac-N / sb-gunshi-mac / sb-shogun-mac / sb-gakushu-bucho / agent_letter.py / inbox_write.sh / board_write.py / inbox_mark_read.py(家老の器を外さず)。
- 判: sb 系・agent_letter = `write letter` の後、最初の旗より前に位置引数(胴)が在れば 甲、無ければ ★乙★、語順を読めぬ(usage 文・註・変数のみ)なら 丙。旗を持たぬ器(inbox_write.sh・board_write.py・inbox_mark_read.py)は旗の字面が引数に在れば 丙(有れば)・無ければ 甲。
- 勘定は「器(code)」と「紙(usage/例文・md/yaml/txt・註)」を別欄に。

| 樹 | code 件 | 内 乙 | 例文 件 | 内 乙 | 丙 |
|---|---|---|---|---|---|
| B = 己の樹(origin/main) | 16(悉く inbox_write.sh) | 0 | 81(悉く inbox_write.sh の例文) | 0 | 0 |
| ~/bin | 8(agent_letter 3・inbox_mark_read 3・sb read 2) | 0 | 27(usage 行 7 甲・註 13 丙 等) | 0 | 14(丙 = usage の説明文・註 = 呼出でない・raw/15 で紙に判じた) |
| C = 共有樹(読むのみ) | 30 | 0 | 188 | 0 | 7 |

- 丙 14+7 を紙で判じた(raw/15): 悉く「呼出でない」(器の docstring・usage 文・由来の註・dashboard の引用)。∴ 乙 0 は網の粗でなく實。
- ★網の限り★: 手で打たれた命令(pane の履歴・session jsonl)は歩いて居らぬ ―― 家老の疵は其処に在つた。script に無い事は「手で打つ時に起きぬ」を意味せぬ。

## ㋒ 器の側の守り・實射(raw/20・21・22・23)

| 器 | 旗の字面が胴の位置に来た時 | rc | 偽の成功を刷るか |
|---|---|---|---|
| agent_letter.py(sb-* 経由) | 受ける(胴=「--to」4 字・宛・parent は正) | 0 | ★刷る★(「★<宛> へ送出した★ seq=N」・dry-run の封筒にも胴は出ぬ) |
| ~/bin/km_send.sh(家老の私器) | ★撥ねる★(「★拒★ 胴が旗で始まる」/ 位置引数 2 つ以上) | 2 | 刷らぬ(渡す argv を刷る) |
| scripts/inbox_write.sh | 受ける(旗を持たぬ器ゆゑ「--to」は正当な胴) | 0 | 刷る(DEFERRAL_PASS・箱へは IW_DEFERRAL_TEST_ONLY で送らず) |
| ~/bin/board_write.py | 撥ねる(REJECT column=x / bad arg) | 3 | 刷らぬ |
| ~/bin/inbox_mark_read.py | 印を打たぬ(★未命中★=--to・fail-closed) | ★0★ | 半ば(marked=0 を刷るが rc 0) |

- ㋒ 實射: 宛を己(--to ashigaru-mac-1)にした試し打ちは ★対応表に無く拒まれた(rc 2・raw/20 ⑶)★ ゆゑ、送らずに二路で示した: ⒜ 器の取り方(L141-145/L189-193)を写して両語順に当て 正 25 字 / 乙 4 字(raw/23)⒝ 家老の現物 seq333833/834/835 を sb read → 悉く 4 字・target iincho。dry-run(raw/21・22)は封筒(to_pc/topic/target/parent)のみで胴を刷らぬ ―― ★dry-run でも此の疵は見えぬ★。
- 上役の箱・本番の板へは打たず。

## ㋓ 告げ口の形

- 在る(送り手側・弱い): agent_letter の「本文 N字 ―― 100字を超えた」註の ★不在★。100 字未満の正当な胴でも不在ゆゑ、単独では判じ得ぬ。
- 在る(送り手側・強い・但し km_send.sh 経由のみ): 「胴=N字 ―― 送る」「渡す argv: write letter <胴 N字> …」の行。
- 無い: 受け手側(宛・parent・topic 悉く正)・rc・seq の有無。∴ 「胴の字数が複数便で揃ふ」以外で送り手が持てる徴は上の二つ。推量で「在る」とは書かぬ。

## ㋔ 案(★紙のみ・据ゑぬ・委員長の許可の後★)

⑴ 呼ぶ側の作法(三行): 胴は `letter` の直後に一つ・旗は悉く胴の後 / 打つ前に `--dry-run` … は胴を刷らぬゆゑ ★頼らぬ★ / 送つた後 `sb read seq N` で胴の字数を読み返す(第八の番人・當席は今日の全便で行つた)。
⑵ 器の側の守り(三行): agent_letter.py に「`args[3]` が `--` で始まれば die(rc 2)」を一行足す(km_send.sh L13-14 と同じ検め・戻し = 其の一行を消す)/ dry-run の封筒に `content_len=N` を一行刷る(戻し = 一行)/ sb-* の wrapper は触らず(agent_letter 一箇所に置けば全 wrapper に効く)。
- ★家老の km_send.sh は既に此の守りを持つ★ ―― 家老自身が sb-karo-mac を直に打つた時に踏んだ。∴ 器の守りは「経路を一つに絞る」事と対である。

## ㋕ 測れぬ物・意味せぬ事

- 手で打たれた命令の履歴(pane・session jsonl)は歩いて居らぬ ―― 家老の疵の母體は其処。
- 他 PC の helper(post_and_ring.py 等)の守りは走らせて居らぬ。
- 「乙 0」は書かれた器・紙の中の話。
- km-191 との重なり = 0(旗の字面に多byte 無し)。

## ㋖ 疵

⑴ 着手便 300 字超 3 度(355/314/301)―― ★同じ壁★ ⑵ 器の守りの初版で rc を管(| head)から取り 0 と読んだ(round1 控・取り直し)⑶ 己宛の試し打ちが対応表で拒まれ、實射を写しと現物の読みに代へた(命の字面「己宛」は満たせず)。

## 宣⇔實

宣ETA 21:35。實 = 納め便の刻(紙の外・20:5x 見込み)。
