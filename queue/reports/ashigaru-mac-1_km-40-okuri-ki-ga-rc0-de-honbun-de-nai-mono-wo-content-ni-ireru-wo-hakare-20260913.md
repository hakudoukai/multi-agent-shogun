# 第40弾 ―― 答を先に四つ: ㊀ ★「送り器が rc=0 を返しながら本文でない物を content に保存する」は艦隊の規模で ★19 通★(母數 11,417 通・seq 300000〜313055・2026-09-10 22:04〜09-13 13:15 JST・`sb read seqs` 68 呼 rc≠0 0)★ ―― 四つの数を別々に: ⑴ content 12 字以下 ★19★ / ⑵ `--` で始まる ★16★ / ⑶ 既知の役職名と完全一致 ★2★(R1 = agent_letter.py の ROLE_PC 31 名でも R2 = R1 ∪ 掃きに現れた役職の形の名 54 でも同じ 2)/ ⑷ PC 名と完全一致 ★0★(P1 4 名でも P2 10 名でも 0)。席 × 日: ★karo-mac 9(悉く本日)★ / reserveimage 7(本日・`--to`→fukuincho)/ karo-third 1(09-12・`--help`)/ gakushu-bucho 1(09-11・`--help`)/ karo-second 1(09-11・「probe2」6 字 = 本文らしき短文)。⑴ の語は「--to」13 / 「--help」3 / 「karo-mac」2 / 「probe2」1。★家老の便は現物で 9 通★(task yaml が名指す 6 = 313000・312967 = 「karo-mac」8 字、312930・312928・312927・312851 = 「--to」4 字 ―― ★yaml の「312967 content=--to」は現物が「karo-mac」であり、席の一度目の對照が此の違を捕へた★ / yaml に無い 3 = 311680・311681「--to」07:30・311778「--help」07:53)。宛は iincho 6 / gunshi-mac 3(死箱)。∴ 之は karo-mac 一席の癖ではなく ★四席・三日に亘る器の形の疵★であり、`--help` の 3 通は「使ひ方を訊いた語がそのまま便として飛んだ」形である。㊁ 送り器 ~/bin/agent_letter.py(sha16 27ec1cf5099e96dc・写さず其の path の儘・urlopen を偽物にして ★網へ 0 byte★)へ fixture 15 本: 重複前置(家老の形)は ★rc 0 で content=「karo-mac」★、`--to` を本文の前に置けば content=「--to」、本文が役職名/PC 名なら其の儘 content、本文 空だけは器が止める(rc 2)。★重複前置では 親の門(L121)・空の検し(L133)・300 字の上限(L142)・先送り門(L146)・100 字の註(L147)が悉く args[3]=「karo-mac」に掛かり、真の本文(args[6])には一つも掛からぬ★(「明日」を含む本文も 400 字の本文も seq を引く本文も rc 0 で通る・正形の對照は各々 rc 10 / 2 / 2 で鳴る)。`--dry-run` は 8 鍵を刷り ★content を刷らぬ★(15/15)∴ 空撃ちでは取り違へが見えぬ。案 6 つは §2⑷(文のみ・据ゑず)。㊂ 己の器 30_hougen.py:24 の境の一本(空白のみの行)を v2 で「落ち」として別に印字する形へ直し、fixture 8 本(空白/tab/U+3000/NBSP/改行の無い末尾/空行/清い/ZWSP)で v1 は悉く「実体行 2」と刷つて落ちを一度も印字せず、v2 は落ちを 1/1/1/1/1/0/0/0 と印字した(ZWSP は str.strip の定義の外 ―― 実体行に入り讀めぬ行に成る事を印字)。本日の臺帳 41 に落ち 0。前弾の失 7 件の再発 ★4/7★(②陽性對照の選び違ひ ③緩い鍵 ④器の再配置で根を失ふ ⑥API 呼を對照の前に ―― ②③④は對照・落ちが捕へ、⑥は己の申告)。㊃ 臺帳に宣行(本数・byte和)を置き、宣 ⇔ 実測の一致を 60 で印字した。DB へ POST/PATCH/DELETE 0・禁域へ 0 byte・門 rc は門控。

**專任1(足軽mac1号 / ashigaru-mac-1)／task_id `km-40-okuri-ki-ga-rc0-de-honbun-de-nai-mono-wo-content-ni-ireru-wo-hakare-20260913`／round 40(prev 39・錨 c100ad59bdb79aae / 臺帳 36e59aeb6989f897 / 門控 1a632b1a051d417f ―― 己の手で三 sha を測り悉く一致)**

## ★三項(本弾の全ての数が此れに従ふ)★
| 項 | 本弾の宣 |
|---|---|
| ①経路の列挙 | ⓐ DB 便 pc_handshake ―― `sb read seqs`(200 刻み 68 呼・raw/20)+ 束の前の `sb read seq/seqs` 凡そ 20 呼(session のみ・00_start に名を写した)・resolved_at を問はぬ・全 sender ⓑ mac の disk(~/bin/agent_letter.py・~/bin/sb・~/bin/deferral_gate.py を讀む / agent_letter.py は runpy で走らせ urlopen を偽物にした / queue/reports 直下の臺帳 41 本を讀む)ⓒ task yaml(家老の記述・讀むのみ) |
| ②母數の本数 | 便 11,417 通(seq 300000〜313055・2026-09-10T22:04:28〜2026-09-13T13:15:22 JST・created_at は悉く +09:00・日別 09-10 656 / 09-11 5,366 / 09-12 2,865 / 09-13 2,530 ―― 09-10 と 09-13 は部分日)/ karo-mac 発 本日 85 通 / 役職名 R1 31・R2 54 / PC 名 P1 4・P2 10 / 送り器 fixture 15 + dry-run 15 / 己の器 fixture 8 / 本日の臺帳 41 / 前弾の失 7 |
| ③器の名 | raw/20_sweep.py・21_toku.py(㊀)/ 30_fx_driver.py・30_fx_letter.py(㊁)/ 32_hougen_v2.py(㊂)/ 40_saihatsu.py(失)/ 50・59・60・99(臺帳・門・後歩き・第39弾を写した)/ kaki.py(書き器) |
★數を書く時、上の三項の外の数は無い。★

## ★測れぬ(先頭に置く・各項に『何が在れば測れるか』)★
1. **content の「字数」は讀み器の出目** ―― content_len は karo_mac_read.py L220 の `len(content)`(Python の文字数・byte ではない)。⑴ の「12 字」は此の数で判じた。定まる条件 = 字数の定義を「Python の len」と宣す(本紙で宣した)。
2. **切つた本文** ―― raw/20 は content を頭 160 字で切つた(門 條⑤ 10MB の為・切つた entry 5,507・切つた字数を行末に記す)。⑴〜⑷ は content_len と頭 160 字で定まる(完全一致 = content_len == len(名) ∧ 頭 == 名)ゆゑ切りは数を動かさぬが、★160 字より後ろの本文は席の raw に無い★。定まる条件 = `sb read seq N` で引き直す(器は在る・本弾は 313000・312930・312809 の 3 通を引き直した)。
3. **他席の送り器** ―― reserveimage(third_pc・`--to` 7 通)/ karo-third / gakushu-bucho / karo-second が agent_letter.py を通したかは席には測れぬ(ctx の鍵の集合が同じでも器の同一は推定)。定まる条件 = 各席が「此の seq は此の器・此の argv で出した」と一行返す。
4. **消された便** ―― 掃きは「今 DB に在る便」のみ。400 で落ちた便・消された便は母數に無い。定まる条件 = 総監督が削除の履歴を一行返す(席には無い)。
5. **家老の「五通」の内訳** ―― task yaml は「五通」と書き 6 つの seq を名指し、内 1 つ(312967)は content が yaml と違ふ(「--to」でなく「karo-mac」)。現物は 9 通(iincho 宛 6・gunshi-mac 宛 3)。「五」が何を数へたかは席には測れぬ。定まる条件 = 家老が「五通」の seq を列挙する。
6. **受け手が空の便を讀んだか** ―― resolved_at・受け手の pane は本弾で見て居らぬ。定まる条件 = 宛先席が返す。
7. **fixture の rc は runpy の SystemExit から採つた** ―― 実 process の exit code と同値の筈だが(main の return → sys.exit・die の 2・先送り門の 10)、subprocess で ~/bin/agent_letter.py を其の儘走らせると creds が要り網へ出る故、席は runpy を選んだ。定まる条件 = 委員長裁で creds 無し + `--dry-run` の subprocess を打つ(但し dry-run は content を刷らぬ ―― ㊁ の通り)。
8. **local の箱(inbox_write.sh)の同類** ―― 本弾は pc_handshake のみ。queue/inbox の便に同じ形(本文が flag)が在るかは測つて居らぬ。定まる条件 = 次弾で箱 19 本を鍵で歩く。
9. **09-10 以前** ―― 掃きは seq 300000(09-10 22:04)から。其れ以前の便に同類が在るかは測つて居らぬ(器は在る・`sb read seqs` を前へ延ばせば足りる・約 60 呼/日)。
10. **⑴ の「probe2」(karo-second 302115・6 字)** ―― 本文らしき短文であり flag でも役職名でもない。⑴ は「12 字以下」の形で数へた故に入る。「本文でない」と断じられぬ(意図は席には測れぬ)。

刻(起) raw/00_start.txt L1(2026-09-13T13:14:32+0900・`date` 直採)/ 歩き根 `/Users/momizimac/multi-agent-shogun` / HEAD f2bfa26 / uid 501 / python 3.14.6 / pane %72
器(前・不触) 門 `scripts/checks/karo_mac_dasumae_gate.sh` sha16 8df3d070fb4f9a3e / 照合器 1f001531b681d1bf / `.gitignore` 3ccfcf1c05e82b58 / `.claude/settings.json` b135e8f17b3be9d5 / `.git/index` mtime 2026-09-10T19:55:51 / ~/bin/sb 2670b305a432e552 / ~/bin/agent_letter.py 27ec1cf5099e96dc(mtime 2026-09-09T17:05:13)/ ~/bin/karo_mac_read.py 5e3bcfe768390a2c / ~/bin/deferral_gate.py 5019b84a8fa2677d。★本弾は DB へ POST/PATCH/DELETE 0(sb write 0 回・讀みは sb read のみ・30 の POST は偽の urlopen が捕へ網へ出て居らぬ)、scripts/ .gitignore ~/bin/ instructions/ .claude/settings.json 他席の yaml へ 0 byte(~/bin/__pycache__ の pyc 5 本は悉く本弾より前の mtime・python は悉く -B)、git は rev-parse のみ。fixture は己の束 raw/fx/ に置いた(㊇ 員外・byte 其の儘)。★
添状の形: ★添状無し ―― 報は便 N 通(karo-mac・inbox_write・各 300 字以内)+ 監査提出 1 通(karo-mac 宛・gunshi-mac の箱は死箱ゆゑ)。id の列は raw/63_sent.txt(紙の凍結後に生れる・門控で名を宣す)。★ 着手報 = raw/01_chakushu.txt(13:15:51・283 字 ―― 送る前の assert が 418 字・318 字を二度止めた)。ETA は着手報で 14:10 と宣した。実測は門控の刻で示す。

## §0 家老 karo_hyou への返し
- ⑴〜⑸ 受領。本弾も同じ形を保つ: 家老の記述(task yaml の 6 seq)を疑はず陽性對照に据ゑ ―― ★其れが現物と違つた(312967)★。對照が捕へ、独立の器(`sb read seq 312930`)で見た便へ替へた(§4②)。家老の疵の表(katei_karo_no_kizu)は本弾で ★現物と一致 5/6★・違ひ 1/6 を示す(§1⑶)。
- note_karo「家老の便の内容を測る事を憚るな」受領 ―― 本弾は家老の便 85 通を他席と同じ器で数へた。

## §1 ㊀ 艦隊の規模(raw/20・21)
### 對照(數の前・21_toku.out 逐語の要旨)
述語の單体 8 本(陽 3・陰 5): 「karo-mac」→⑴⑶a⑶b / 「--to」→⑴⑵ / 「mac_pc」→⑴⑷a⑷b / 「karo-mac.」→⑴のみ / 13 字→無 / 「-x」→⑴のみ / 頭 karo-mac で全長 297(切られた便の形)→無 / clen −1→無 ―― 悉く期待と一致(★一度目は「--to」→⑶b が True を出した ―― R2 に「--to」が混じつて居た(下)★)。掃きの對照: 陽 313000(karo-mac・sb read seq で独立に見た)/ 陽 312930(--to・同)/ 陰 312809(297 字)/ 陰 ZZZZ_NOT_PRESENT 0・seq 999999999 無。器の頭の取得和 11,417 = 解けた entry 11,417。
### ⑴〜⑷ を別々に(束ねず)
| 数 | 定義 | 艦隊 | 席 × 日(0 でない物のみ) |
|---|---|---:|---|
| ⑴ | content_len ≤ 12 | ★19★ | karo-mac 09-13 9 / reserveimage 09-13 7 / karo-second 09-11 1 / gakushu-bucho 09-11 1 / karo-third 09-12 1 |
| ⑵ | 頭が `--` | ★16★ | reserveimage 09-13 7 / karo-mac 09-13 7 / karo-third 09-12 1 / gakushu-bucho 09-11 1 |
| ⑶a | R1(ROLE_PC 31 名)と完全一致 | ★2★ | karo-mac 09-13 2 |
| ⑶b | R2(R1 ∪ 掃きの sender/target のうち役職の形 `[a-z0-9][a-z0-9_-]{1,31}` を通り PC 名でない物・54 名)と完全一致 | ★2★ | 同上 |
| ⑷a | P1(mac_pc/main_pc/second_pc/third_pc)と完全一致 | ★0★ | ― |
| ⑷b | P2(P1 ∪ 掃きの from_pc/to_pc・+commander/director/fukuincho/hermes/hermes2/iincho)と完全一致 | ★0★ | ― |
重なり(參考・上の数は束ねて居らぬ): ⑴∧⑵ 16 / ⑴∧⑶ 2 / ⑵∧⑶ 0 / 何れか 19。日計: 09-10 0 / 09-11 2 / 09-12 1 / 09-13 16。⑴ の内訳 字数: 4 字 13(悉く「--to」)/ 6 字 4(「--help」3・「probe2」1)/ 8 字 2(「karo-mac」)。
### ⑶ 家老の便 ―― 現物の seq(21_hits.tsv・karo-mac 発 本日 85 通のうち ⑴ 9 / ⑵ 7 / ⑶ 2 / ⑷ 0)
| seq | 刻 | 宛 | content | 字 | yaml の記述 | 現物との一致 |
|---|---|---|---|---:|---|---|
| 313000 | 13:04:49 | iincho | karo-mac | 8 | karo-mac(8字) | ★一致★ |
| 312967 | 12:53:13 | iincho | karo-mac | 8 | --to(4字) | ★違ふ★(席の一度目の對照が捕へた) |
| 312930 | 12:39:12 | iincho | --to | 4 | --to | 一致 |
| 312928 | 12:38:45 | gunshi-mac | --to | 4 | --to | 一致(宛は死箱) |
| 312927 | 12:38:45 | gunshi-mac | --to | 4 | --to | 一致(宛は死箱) |
| 312851 | 12:21:36 | gunshi-mac | --to | 4 | --to | 一致(宛は死箱) |
| 311778 | 07:53:40 | iincho | --help | 6 | (無) | yaml に無い |
| 311681 | 07:30:33 | iincho | --to | 4 | (無) | yaml に無い |
| 311680 | 07:30:30 | iincho | --to | 4 | (無) | yaml に無い |
∴ 家老の空の便は ★9 通★(iincho 宛 6・gunshi-mac 宛 3)。yaml の「五通」は席には数へ直せぬ(測れぬ 5)。312809(297 字)・312806(148 字)・312803(221 字)は本文が載る(yaml と一致)。
### ⑷ 他席の同類(參考・四つの数の外)
- reserveimage(third_pc)→fukuincho「--to」7 通(312055〜312335・08:58〜09:57)―― 一時間に七度、同じ形。器は測れぬ 3。
- 「--help」3 通(gakushu-bucho 304400 / karo-third 308449 / karo-mac 311778)―― 使ひ方を訊いた語が便として飛んだ形。三 PC(mac/third)三席。
- ★封筒の側の同類★(content は本文だが sender_agent が役職でない): sender_agent=「--to」2 通(300648 from_pc=fukuincho / 300649 from_pc=iincho ―― 役職が from_pc に、flag が sender に)/ sender_agent=「third_pc」6 通(305288〜305794・PC 名が sender に)。之は「位置の取り違へ」の同じ類が ★別の器(agent_letter.py は sender=「--to」を作れぬ ―― resolve_role_pc は宛先しか検めぬが sender は args[0] を其の儘書く故、作れる)★ に在る事を示す ―― 断ぜぬ(測れぬ 3)。
### ⑸ DB 書込 0
sb write 0 回・POST/PATCH/DELETE 0。讀みは `sb read seqs` 68 呼(raw/20 の頭に逐語)+ 束の前の凡そ 20 呼(00_start・失⑥)+ 對照の `sb read seq` 2 呼(313000・312930)。

## §2 ㊁ 器の側を fixture で(raw/30_fx_driver.py・30_fx_letter.py・30_fx_letter.out・.log 逐語)
### ⑴ 方法(送らず・据ゑず)
~/bin/agent_letter.py を写さず其の path の儘 `runpy.run_path` で走らせ、`urllib.request.urlopen` を偽物に差し替へて POST の body(器が DB へ書かうとした封筒・content 欄を含む)を捕へた。GET(親の解決)も偽物。creds は偽の文字列(~/.sb_env は讀まぬ)。網へ 0 byte。sb wrapper(~/bin/sb L9)は `karo-mac mac_pc` を前置して exec する故、各 fixture は「sb write の後の語」で書き、前置を足して渡した。rc = 器の SystemExit の code。
### ⑵ 表(15 本・逐語は 30_fx_letter.out)
| # | sb write の後の語 | rc | content(POST body 実測) | 判 |
|---|---|---:|---|---|
| F01 正形(陰性) | letter 本文 --to iincho | 0 | 本文 | 本文が載る |
| ★F02 重複前置(家老の形)★ | letter karo-mac mac_pc letter 本文 --to iincho | ★0★ | ★「karo-mac」★ | 本文でない物が content に |
| ★F03 flag が本文の位置★ | letter --to iincho 本文 | ★0★ | ★「--to」★ | 同上(宛は iincho に解ける) |
| F04 本文 空 | letter "" --to iincho | 2 | (POST 無) | 器が止めた(L133) |
| ★F05 本文 = 役職名★ | letter iincho | ★0★ | 「iincho」 | 本文でない物が content に |
| ★F06 本文 = PC 名★ | letter mac_pc --to iincho | ★0★ | 「mac_pc」 | 同上 |
| F07 args < 4 | letter | ★0★ | (POST 無) | ★rc 0 で送らず(__doc__ を刷る)★ ―― 「送つた」とも「止めた」とも見えぬ |
| ★F08 重複前置 + 真の本文に先送り語「明日」★ | … letter 明日やる --to iincho | ★0★ | 「karo-mac」 | ★先送り門(L146)が真の本文に掛からぬ★ |
| F09 正形 + 「明日」(對照) | letter 明日やる --to iincho | 10 | (POST 無) | 門が鳴る |
| ★F10 重複前置 + 真の本文 400 字★ | … letter あ×400 --to iincho | ★0★ | 「karo-mac」 | ★上限(L142)が真の本文に掛からぬ★ |
| F11 正形 400 字(對照) | letter あ×400 --to iincho | 2 | (POST 無) | 上限で止まる |
| F12 重複前置 + --parent-seq 312809 | … --parent-seq 312809 | 0 | 「karo-mac」 | 親は解け(GET 1 呼・偽)content は取り違へた儘 |
| ★F13 --urgent を本文の位置に★ | letter --urgent 本文 --to iincho | ★0★ | 「--urgent」 | flag が content に・priority は urgent に成る |
| ★F14 重複前置 + 真の本文が seq を引く★ | … letter 親=312809 へ返す --to iincho | ★0★ | 「karo-mac」 | ★親の門(L121)が真の本文に掛からぬ★ |
| F15 正形 + seq を引く(對照) | letter 親=312809 へ返す --to iincho | 2 | (POST 無) | 親の門が鳴る |
`--dry-run`(15/15): rc は本走と同じ(0/2/10)・stdout 9 行・刷る鍵 = to_pc topic message_type priority target_agent sender_agent reply_to_topic parent_message_id の 8 つ・★「content」の語 0/15★。∴ 家老が空撃ちで確かめようとして見えなかつたのは器の形である(L206-214)。
### ⑶ 讀み(器の行を引く)
- L110 `if len(args) < 4 or args[2] != "letter"` ―― 三語目が letter か・四語在るか、の二つしか見ぬ。重複前置(F02)は三語目が letter ゆゑ通り、L113 `body_text = args[3]` で「karo-mac」が本文に成る。
- L121-128(親の門)・L133(空)・L142(300 字)・L146(先送り門)・L147(100 字の註)は悉く `body_text` = args[3] に掛かる ∴ ★重複前置では真の本文に門が一つも掛からぬ★(F08/F10/F14 が rc 0・對照 F09/F11/F15 は鳴る)。
- L169-171 `--to` は args の何處に在つても拾ふ(index)∴ F03 は宛先が正しく解け、本文だけが「--to」に成る ―― 封筒が正しい故に受け手は「本文が無い便」を受ける。
- L229 の印字「★iincho へ送出した★ seq=N」は封筒の宛先を映すが content を映さぬ(2026-08-19 の是正は to_role のみ)。∴ 家老は rc 0 と此の印字を送達の證と読んだ ―― ★器は「何を送つたか」を一度も刷らぬ★。
- L111-112 `print(__doc__); return 0` ―― 引数が足りぬ時 rc 0 で「送らず」。之は ★rc 0 が「送つた」も「送らなんだ」も意味する★ 形(F07)。
### ⑷ 据ゑる案(★文のみ・据ゑず・委員長裁★)
㋐ **送つた物を刷る**(最も安い・L229): `★iincho へ送出した★ seq=N content=「<頭 40 字>」(<字数>字)` ―― 家老の 9 通は送つた刻に見えた。㋑ **重複前置の検し**(L113 の直後): `args[3:6] == [role, from_pc, "letter"]` なら die「前置が二重(sb が role pc を既に前置する)」。㋒ **本文が flag/役職名/PC 名の検し**(同所): `body_text.startswith("-")` 又は `body_text in ROLE_PC` 又は `body_text in set(ROLE_PC.values())` なら die ―― F03/F05/F06/F13 が止まる(本文が「-」で始まる正当な便は `--` の後に置く逃がしを設ける)。㋓ **dry-run に content を刷る**(L208): 鍵 8 つに `content(頭 40 字・字数)` を足す ―― 空撃ちで取り違へが見える。㋔ **引数不足は rc 2**(L111-112): `return 0` を `return 2` に ―― rc 0 が「送らず」を意味せぬ様に。㋕ **sb の usage**(~/bin/sb L10): `sb write letter "本文" [--to 役]` を刷る(役・PC を書かぬ事を明示)。何れも ~/bin の直しゆゑ委員長裁。席は 0 byte。

## §3 ㊂ 己の器の境の一本(raw/32_hougen_v2.py・.out・fx/hg_*.txt)
### ⑴ 直し
第39弾 raw/30_hougen.py:24 `body = [l for l in lines if l.strip() and not l.startswith('#')]` は空白のみの行を実体行にも讀めぬ行にも数へず、落ちを印字せぬ。v2 は行を四つに分ける ―― 実体行 / 註(#)/ 空行(長さ 0)/ ★落ち = 空白のみの行(空でなく str.strip() で空に成る行)★ ―― 落ちを別の数で必ず印字し、落ち ≥1 なら rc 1。併せて「行頭空白の実体行」と「閉ぢ(行 = 四つの和)」を印字する。空白の定義 = str.strip() が剥ぐ物(' ' '\t' U+3000 U+00A0 等)と宣し、定義の外(ZWSP U+200B)を fixture で示した。
### ⑵ fixture 8 本(byte 其の儘・fx/・員外 ㊇)
| fixture | 何 | 期待 落ち | v1 実体行(落ちの印字 無) | v2 行/実体/註/空/★落ち★/行頭空白/讀めぬ/閉ぢ | 判 |
|---|---|---:|---:|---|---|
| hg_01 | 空白 3 つの行 | 1 | 2 | 3/2/0/0/★1★[行2]/0/0/True | 正 |
| hg_02 | tab の行 | 1 | 2 | 3/2/0/0/★1★[2]/0/0/True | 正 |
| hg_03 | U+3000 の行 | 1 | 2 | 3/2/0/0/★1★[2]/0/0/True | 正 |
| hg_04 | NBSP の行 | 1 | 2 | 3/2/0/0/★1★[2]/0/0/True | 正 |
| hg_05 | 改行の無い末尾の空白行 | 1 | 2 | 3/2/0/0/★1★[3]/0/0/True | 正 |
| hg_06 | 空行(長さ 0) | 0 | 2 | 3/2/0/1/★0★/0/0/True | 正(空行は落ちでない) |
| hg_07 | 清い 2 行(陰性) | 0 | 2 | 2/2/0/0/★0★/0/0/True | 正 |
| hg_08 | ZWSP の行 | 0 | 3 | 3/3/0/0/★0★/0/1/True | 正(定義の外 ―― 実体行に入り讀めぬ行 1 に成る・印字される) |
★v1 は 8 本悉く「実体行 2」(hg_08 は 3)と刷り、落ちを一度も印字せぬ ―― 数が正しく見える事は形が正しい事の證にならぬ(前弾の掟の実演)。★
### ⑶ 本番
母數 = queue/reports 直下・名が _manifest.txt(839)のうち mtime 本日 = ★41★ / utf-8 不可 0 / ★落ちを持つ臺帳 0(行 0)★ / 行頭空白の実体行 0 / 閉ぢぬ 0。席 × 形(v2): 專任1 B 17 / 專任2 A 11 / 專任3 A 3・B 5・D 1・E 4(第39弾の 38 から 3 本増・專任3 が E を 2 本足した)。
### ⑷ 前弾の失 7 件の再発(raw/40_saihatsu.out)―― 母數 7 / ★再発 4★
| # | 前弾の失 | 本弾 | 再発 |
|---|---|---|---:|
| ① zsh `:s` | git は rev-parse のみ・`$r:` を書いて居らぬ(申告) | 0 |
| ② 陽性對照の選び違ひ | ★21 の一度目は yaml の記述(312967 = --to)を陽性に据ゑ、現物(karo-mac)と違つて對照が鳴つた★ → 独立に見た 312930 へ替へた | ★1★(對照が捕へた) |
| ③ 緩い鍵の偽陽性 | ★21 の一度目は R2 を掃きの sender∪target 悉くで組み、sender_agent=「--to」の 2 通が R2 に混じつた★ → 役職の形の regex を通る物に限つた。二度目の直し(P2 で除く)は iincho 等まで junk に落し 398KB を刷り、三度目で P1 に限つた | ★1★(對照が捕へた) |
| ④ 器の再配置で根を失ふ | ★32 の一度目は ROOT を cwd 相対で書き raw/ から走らせ FileNotFoundError★ → 器の在處から導いた | ★1★(落ちて気付いた) |
| ⑤ 着手報 300 字超 | 送つた本文 283 字。送る前の assert が 418 字・318 字を二度止めた(「送つた」で数へれば 0・「書いた」で数へれば 2 ―― 前弾の失は「送つた 420 字」ゆゑ「送つた」で数へる) | 0 |
| ⑥ API 呼を對照の前に | ★束を作る前に sb read を凡そ 20 呼(seq 313000・312809・seqs の probe・語彙)打ち、出目は session にしか無い(00_start に申告)★ | ★1★(捕へられて居らぬ) |
| ⑦ 母數を欠いた「無い」 | 本弾の 0 は悉く母數と陽性對照を伴ふ(⑷ 0 / 落ち 0 / pyc 0)| 0 |
失 7 件の外: 20 の stdout を `>` で生に捕つた(cmp で kaki 経由の物と同一を確め消した・記憶の掟の再発 1)/ task yaml の assigned_at 13:12:00 は mtime 13:09:18 より後(家老の手書きの刻・席は mtime を採つた)。

## §4 ㊃ 宣行と ㊄ 門 ―― 臺帳・門控で示す
臺帳の末尾に `# 宣(註・家老の DECL に合ふ形): 本数 N / byte和 M` を置き、60 が 條① の母數と 條⑤ の byte和で「宣 ⇔ 実測」を印字する(門控)。第39弾 §2⑵補 の通り ★三器は宣行で止まらぬ★(照合器は # 行を跳ぶ・錨器は真偽を印字するのみ)∴ 宣 ⇔ 実測の一致は ★席の器 60 が印字する★ 物であり、門の rc ではない ―― 之を偽の緑と混ぜぬ為に紙に書く。

## §5 己の失(本弾)
① 着手報を 300 字内に収めるのに三度掛かつた(assert が二度止めた)。② 陽性對照を yaml の記述で選んだ(§3⑷②)。③ R2 の定義が二度緩んだ/狭まつた(§3⑷③・398KB の列)。④ 32 を cwd 相対で書いた(§3⑷④)。⑤ 束の前に約 20 呼(§3⑷⑥)。⑥ 20_sweep.stdout の生の捕り(消した)。⑦ 21 の頭の「junk の便」の列が一度目 398KB に膨れた ―― 器の出目の寸法で気付いた(印字の母數を先に見る形が己に無い)。

## 之が意味せぬ事
- 「19 通」は「19 の失」の意ではない ―― 「probe2」(6 字)は本文らしく、⑴ は形(12 字以下)で数へた。flag と役職名に限れば 18。
- 「karo-mac 9」は「家老が九度誤つた」の意ではない ―― 同じ形が三日で四席に在り、器が送つた物を刷らぬ限り誰でも踏む(§2⑶)。
- 「⑷ 0」は「PC 名が本文に成る形が無い」の意ではない ―― F06 は rc 0 で「mac_pc」を content にした。掃きの範囲(3 日)に其の便が無かつた丈である。
- 「reserveimage の 7 通は同じ器」とは言つて居らぬ(測れぬ 3)。
- 「落ち 0」は「境の一本を落す器が無い」の意ではない ―― v1 は fixture 5 本で落ちを黙つた。本日の臺帳に其の行が無かつた丈である。
- 「再発 4/7」は「4 つが外へ出た」の意ではない ―― 3 つは對照・落ちが数の前で捕へ、1 つ(⑥)は己の申告。
