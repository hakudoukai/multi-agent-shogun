# 第81弾 ―― ★宣した閾が一度も讀まれぬ事を示せ★: `scripts/lib/detect_stale.sh` の `DETECT_STALE_STALE_SEC`(設計 §1.2 verbatim 120s)は repo 全体で ★口 1 行・讀手 0 行★(器A 根 1079 file / 器B git grep 9 行= 生 1 + 先例の束 8・陽性対照 DETECT_STALE_LOG 口 3/讀手 7・陰性 ZZ_KM92_NEG 0 行 rc 1)。振舞ひでも死: 閾を 999999 / abc にしても now-1s が STALE(30 姿G)。★当機 /bin/date -d は rc1★ ゆゑ verbatim 行は 12 入力中 12 が `[0]`= 正しい時刻も悉く ANOMALY(30 姿B)。★非數の番人は無い★: date -d の出目へ非數 8 形(abc/空/-5/0/2^63/1e3/改行/出力+rc1)を注ぐと ★6/8 が STALE 候補へ落ち CLI が enqueued=1(auto-poke)★(ANOMALY へ落ちたのは -5 と 0 だけ)。直し(㋓・写し・自枝 commit 463c388c1751): 閾を讀ませ(同じ演算子で検め・倒す時は名指す)・date -d → python3 fromisoformat・出目を 數字のみ + [ -gt 0 ] && [ -le 253402300799 ] で検む → 両対照 45/45 ○・既存 test 二本 GNU 姿/BSD+flock 姿 PASS

- 弾: km-92(家老便 msg_20260917_125748_9dfcc5e2(clear_command・家老の呼称「第57弾」)・札 queue/tasks/ashigaru-mac-1.yaml sha16 16c0eed1b235ac2a 78 行)/ 束 docs/evidence/km-92-sengen-shita-shikii-ga-ichido-mo-yomarenu-koto-wo-shimese-20260917 / 書手 ashigaru-mac-1(專任1)/ 宛 karo-mac(監査 gunshi-mac へ sb・PASS は待たぬ= 裁 seq324831)/ 親裁 seq324588 順⑶(番人無し 4 file の一本)
- 據: 專任2 km-83「數値の閾は ER_THRESHOLD_MIN の一つだけ」→ 順⑵ ASW_PROCESS_TIMEOUT(宣のみ)と同型の疑ひを家老が 12:56 に当てた。本弾は其れを ★己の器で引き直し★(食ひ違ひ= 家老表の空・2^63 行)、直しまで。
- 刻: 起 2026-09-17T13:02:48+0900 / 着手便 msg_20260917_130521_54d5c7ec(13:05:21・宣ETA 120〜300 分(幅)・起点= 着手便 timestamp・端点= 納め最終便 timestamp)/ 紙 2026-09-17T13:26:06+0900 / 凍結点 HEAD 0039e1321654・main 363d5fb06084 / 枝(作業樹) ashigaru-mac-3/km-51-…(共有)・★直しの枝 ashigaru-mac-1/km-92-sengen-shita-shikii-ga-ichido-mo-yomarenu-koto-wo-shimese-20260917★
- 器: ★生器へ 0 字★(00 が固定した生 sha16 de4fefbdadb2be63 = 札の宣・45 の後も不変)。測りは写し raw/utsushi/(前)と raw/40_utsushi/(後)。stub= raw/stub_gnu(date→gdate 9.11・flock)/ stub_inj(date -d へ注ぐ)/ stub_inj2(python3 の parser 呼出へ注ぐ)/ stub_flock。稼働 watcher・supervisor・settings.json 不觸。kaki.py は km-86 逐語。臺帳= MANIFEST.txt(★50 の .py 其の物を載せる= km-86 追紙 2★)・門控= _gate/(員外)・_after/ は臺帳の後。
- ★母數の根(逐語)★: 器A= repo 根 `/Users/momizimac/multi-agent-shogun` / 深さ無制限 / 除外を宣す(.git・queue(13GB)・node_modules・.venv・__pycache__・backups・.claude/worktrees・docs/evidence/)/ 追跡・未追跡を問はず(scripts/*.bak も歩く)/ 通常 file ★1079 本 110800977 bytes★ / 非通常 0 / 刻 2026-09-17T13:04:20+0900。器B= `git grep -n -I -e <名> -- .`(追跡 file のみ・docs/evidence/ 含む)。根1′= docs/evidence/(先例の束 5380 file・己の束除く)。根3= ~/bin(77 file)。

## ㊀ 結語を先に

1. ★㋐ 零の四札★: `DETECT_STALE_STALE_SEC` は 器A 根1 で ★1 行★= 宣其の物(`DETECT_STALE_STALE_SEC="${DETECT_STALE_STALE_SEC:-120}"`)のみ・★讀手 0 行★(展開 `$X`/`${X` を、宣の RHS `${X:-…}` を除いて数へた)。陽性対照= 隣の宣 DETECT_STALE_LOG が同じ器で口 3/讀手 7(`>> "$DETECT_STALE_LOG"` 等)= 器は讀手を拾へる。陰性対照= ZZ_KM92_NEG 0 行・器B rc 1。根と深さ= 上。刻= 2026-09-17T13:04:20+0900。器B(git grep)= 9 行= 生 1 + 先例の束 8(km-53/77/78/83 の紙と写し= 讀手ではない)。~/bin 0・crontab 無し・此の席の env 0。★振舞ひの証★(30 姿G): `G_now-1s_SEC999999` と `G_now-1s_SECabc` が共に STALE rc0 = ★閾を何にしても出目が変はらぬ★。同型の隣人: `scripts/fukuincho_desktop_poke.py` の `STALE_THRESHOLD_SEC = 120` も git grep 1 行= 宣のみ(的の外・紙にのみ)。
2. ★㋑ 方言(20・12 入力)★: `/bin/date -d X +%s` は ★12/12 が rc1★(`illegal option -- d`・正しい時刻でも)。BSD 形 `-j -f '%Y-%m-%dT%H:%M:%S%z'` が通るのは ['past_+0900'](±hhmm のみ・Z / +09:00 / naive を拒む)。GNU 形(gdate 9.11)が通るのは ['past_Z', 'past_+09:00', 'past_+0900', 'naive_space', 'future_Z', 'empty', 'epoch_@', 'now_word'](★空文字を今日の 0 時に読む★・`now` `@epoch` も通す)。python fromisoformat が通るのは ['past_Z', 'past_+09:00', 'past_+0900', 'naive_space', 'future_Z']。★verbatim 行 `$(date -d … || echo "0")` は当機で 12/12 が `[0]`★= 正しい時刻も 0 に成る(gdate の PATH では正しい epoch)。
3. ★㋒ 函数の出目(30・前)★: 姿G(Linux の姿)は陰性 ○(2020→STALE・2099→FRESH・abc→ANOMALY・空→ANOMALY)。姿B(当機)は ★正しい時刻 2 件が悉く `[ANOMALY] deadline_malformed`★= 当機で層①は一度も STALE を出せぬ。姿S(date -d の出目へ注ぐ 10 形): ★8 形が STALE + CLI enqueued=1(auto-poke)★= ['S_abc', 'S_empty', 'S_2^63', 'S_010', 'S_1e3', 'S_space7', 'S_out+rc1', 'S_newline_inj']／ANOMALY へ落ちたのは 2 形 ['S_neg5', 'S_zero'](負と 0 だけ・`-le 0` が偶々真)。註 L218-224「parse 不能 → ANOMALY」は嘘であつた: `[ "abc" -le 0 ]` rc2 → if 偽 → `[ now -lt abc ]` rc2 → 偽 → inflight → STALE。stderr の `integer expression expected` は cron では誰も讀まぬ。既存 test(31): 単体 姿B PASS=36 FAIL=6 SKIP=0(落ちた ['5.1', '5.6', '6.3', '6.4', '7.1', '7.2'])/ 姿G PASS・CLI 姿B rc 1(CLI-5 落ち)/ 姿G rc 0。
4. ★㋒ 家老表との照合★: 家老の「空 → le0 rc0 / lt rc1」「2^63 → le0 rc1 / lt rc0」は ★/bin/bash 3.2 では再現せず(共に rc2/rc2・abc と同じ側)★。同じ二行は ★zsh の `[ ]`★ で逐語一致(zsh は 18 桁で切り `number truncated after 18 digits` と言ふ)= 家老は zsh で測つた(宣は bash 3.2.57)。∴ 家老の見立「2^63 は永久 FRESH」は逆で、★bash では STALE 候補へ落ち auto-poke★(30 S_2^63: rc0・enqueued=1)。★家老補① msg_20260917_130832_8bb7204d(13:08:32)= 家老自身が両殻(bash 3.2.57 / zsh 5.9)で七値×二試を測り直し、二行を zsh の出目と認めて取消した ―― 己の 30 姿S の bash 値と逐語一致(空・2^63 とも (2,2))。★
5. ★㋓ 直し(40・写し raw/40_utsushi・diff +63 -6・bash -n rc 0・349 行 17560B sha16 0964e9a02e655799)★: 一= 宣 `:-`→`-` と既定 `_DETECT_STALE_STALE_SEC_DEFAULT=120` 一本化 / 二= `_detect_stale_stale_sec()` が閾を ★比較器そのもの `[ -ge 0 ]` で検め★(裁 seq323062⑷ 甲)、空/空白のみ/非數/負/桁溢れを ★名指しの WARN★ と共に既定へ倒す(乙)/ 三= `date -d` → python3 fromisoformat(本 lib が json で既に依る= 新依存 0・`enter_restart_common_watchdog.sh` L221 と同 idiom・Z / ±hh:mm / ±hhmm / naive を受ける)、出目は ★數字のみ★ + `[ -gt 0 ] && [ -le 253402300799 ]`(9999-12-31T23:59:59Z)、stale= `now - sec < deadline` → FRESH(桁溢れを避ける形)。★捨てた側= 宣を消す★: 設計 §1.2 の承認値(50a1b936 verbatim)を実装から消す事に成り、正本と器の食ひ違ひを「器を正本へ」でなく「正本を無かつた事に」で解く形ゆゑ・且つ宣は唯一の外からの調整口(消せば焼き込み)。捨てた側 2= date -d を残し BSD -j -f を fallback: 方言二本を保ち、-j -f は Z/naive を拒む(㋑)= 三本目が要る。
6. ★㋓ 両対照(41・三走・45 case)= ○ 45 / × 0★: 陰性= 正しい時刻 4 形(Z / +09:00 / +0900 / naive)が姿 B でも G でも宣どほり・★閾の前後★ now-115s → FRESH / now-125s → STALE(閾 120)・閾 30 で -25s FRESH / -35s STALE・閾 0 で旧の振舞ひ・閾 999999 で -125s も FRESH= ★閾が讀まれる★。陽性= abc / -5 / now / 2^63 / 年 10000 / `$(echo INJ92)` → 悉く ANOMALY・parser の出目へ注ぐ S2 13 形の内 ANOMALY 11(010 は 8 秒= 正しく STALE・上限 253402300799 は FRESH・+1 は ANOMALY)。閾の毒 7 case が名指しの `[WARN] stale_sec_(empty|blank|malformed|out_of_range)` と共に 120 へ倒れた。既存 test(42): 単体 姿BF rc 0 PASS・姿G rc 0 PASS・CLI 姿BF rc 0 PASS・姿G rc 0 PASS。姿B(flock 無し)の落ち ['7.1', '7.2'] + CLI-5 は ★flock 不在(当機)★= 的の外(31 でも同じ二本が落ちる)。
7. ★㋓ commit(45)★: 枝 `ashigaru-mac-1/km-92-sengen-shita-shikii-ga-ichido-mo-yomarenu-koto-wo-shimese-20260917` / ★full sha 463c388c1751b5392b195902a1f65d2938d4a791★ / 親 main 363d5fb0 / 変はつた file 1 本(的のみ)/ 直し sha256 0964e9a02e655799c250930223332192a424c4528678c7a42b341f1c0f9d323e / porcelain 前後 一字も変はらず(一致)(1017 行・sha16 一致)/ 生 detect_stale.sh 不変(worktree を讀まぬ hash-object + update-index --cacheinfo)。push は請はぬ。
8. ★付(km-86 疵二つ)★: 追紙 TSUIGAMI_km86.md(束の根・臺帳に載せる)。一行= 臺帳を建てる器(50)と検める器(60)は臺帳の前に書かれるのが必然。加へて隠さぬ点= 50 の .py を臺帳に載せなかつたのは慣行であり必然ではない → 本弾の 50 は己の .py を載せる。
9. ★疵 12(㊈)・便= 着手 1 + 納め 5(_after/62)+ 監査 1(_after/64)。★

## ㊁ ㋐ 名の口(10 / 10_meisho.txt)

| 名 | 器A 根1(1079 file) | 内 口(代入) | 内 讀手(展開) | 器B git grep(追跡・束含む) | 根1′ docs/evidence | 根3 ~/bin |
|---|---|---|---|---|---|---|
| ★DETECT_STALE_STALE_SEC★ | ★1★ | 1 | ★0★ | 9(生 1 + 束 8) | 255(束別 km-53-hitotsu-no-aruki-ne-de-file-suu-wo-soroe-20260917 8, km-77-shikii-no-bosuu-wo-yotsu-no-teigi-de-kakutei-seyo-20260917 13, km-78-bannin-naki-kuchi-ga-honto-ni-hiraku-ka-20260917 22, km-79-futatsu-no-mon-he-otsu-wo-ateru-20260917 1, km-83-shikii-de-wa-mamorenu-tane-wo-mitsuke-yo-20260917 209, km-86-na-no-kuchi-wo-repo-zentai-de-kazoe-doku-ga-atesaki-wo-kaeru-koto-wo-shimese-20260917 2) | 0 |
| DETECT_STALE_LOG(陽性) | 13 | 3 | 7 | 21(生 11 + 束 10) | 322 | 0 |
| ZZ_KM92_NEG(陰性) | 0 | ― | ― | 0(rc 1) | 0 | 0 |
| STALE_THRESHOLD_SEC(隣人・poke.py) | 1 | 1 | 0 | 1 | 0 | 0 |

- 器A の 13 行には `scripts/agent_health_check.sh.bak-shikii-zoku2-20260917T022513`(未追跡 .bak)の 2 行を含む(器A は追跡を問はぬ・器B は含まぬ= 11)。
- 「讀手」の則= 行から宣の RHS `${X:-…}` を落とした後に `$X` / `${X` が残るか(逐語 regex は 10_meisho.py)。宣の RHS は「己を讀む」が、其の値は下流で消費されぬ。

## ㊂ ㋑ date の方言(20 / 20_date.tsv・20_date.txt)

- 表は 20_date.txt(12 入力 × 6 列)。要点= ① /bin/date -d: 12/12 rc1 / ① BSD -j -f: 通るのは ['past_+0900'] / ② gdate -d: 通るのは ['past_Z', 'past_+09:00', 'past_+0900', 'naive_space', 'future_Z', 'empty', 'epoch_@', 'now_word'] / ③ py: ['past_Z', 'past_+09:00', 'past_+0900', 'naive_space', 'future_Z'] / verbatim 行(/bin/date): `[0]` が 12/12 / verbatim 行(gdate): 正しい 5 形が正しい epoch・空文字が 1789570800(★今日の 0 時★)・`now` `@1757000000` も通る・abc/2^63/-5/injection が `[0]`。
- ∴ 旧 impl の `|| echo "0"` は当機で「常に 0」を作り、GNU では「parse 不能の時だけ 0」を作る。空文字は `-z` の番人が先に止める故 gdate の「今日 0 時」は届かぬ(陰性 G_empty → deadline_empty)。

## ㊃ ㋒ 函数の出目(30 / 30_kansu.tsv・30_kansu.txt・30_env/*.log 逐語)

| 姿 | 入力 | rc | log | CLI enqueued | 宣(註)との差 |
|---|---|---|---|---|---|
| G | 2020 / 2099 / abc / 空 | 0 / 1 / 2 / 2 | STALE / FRESH / ANOMALY / ANOMALY | 1 / 0 / 0 / 0 | 無し(Linux の姿は宣どほり) |
| G | now-1s / now-119s / now-121s | 0 / 0 / 0 | STALE ×3 | 1 ×3 | ★閾 120 が効いて居らぬ★ |
| G | now-1s + SEC=999999 / SEC=abc | 0 / 0 | STALE / STALE | 1 / 1 | ★閾を変へても不変= 死★ |
| B | 2020 / 2099 | 2 / 2 | ANOMALY ×2 | 0 / 0 | ★正しい時刻が malformed★(当機) |
| S | abc / 空 / 2^63 / 1e3 / garbage+rc1 / 5␊0 | 0 ×6 | STALE ×6 | ★1 ×6★ | ★非數が auto-poke★ |
| S | -5 / 0 | 2 / 2 | ANOMALY ×2 | 0 / 0 | 偶々(`-le 0` が真) |
| S | 010 / ' 7' | 0 / 0 | STALE ×2 | 1 / 1 | 數(8 / 7 秒)= 過去= 正 |

## ㊄ ㋓ 直しと両対照(40 / 41 / 42 / 45)

- diff 全文= raw/40_diff.txt(三 hunk)。初走(.first)は上限無し → 41 二走 S2_max_int(2^63-1)が★永久 FRESH★ → 二走で上限を足した(疵④)。
- 41 の表= 41_kansu_after.txt(45 case・判の則= log の札・rc・WARN の有無と名)。初走 .first は now を起動時に一度だけ取つた疵(②)で 6 case ×(実齢 122〜131 s= STALE が正)、二走 .second は上限前、三走が本。
- 42= 既存 test 二本を写しの樹で。31(前)との差: 単体 姿B PASS=36 FAIL=6 SKIP=0 → PASS=40 FAIL=2 SKIP=0(残る ['7.1', '7.2'] は flock)・CLI 姿B CLI-5 は前後とも flock で落ちる・姿BF/G は前後とも PASS(前は G のみ・BF は本弾で足した姿)。
- 45= 温 recipe 逐語(read-tree main → hash-object -w 直し → update-index --cacheinfo → write-tree → commit-tree -p main → update-ref)。porcelain 前後 sha16 一致・1017 行。

## ㊅ 此の紙が意味せぬ事

- third_pc(Linux)の gdate・python3 の版は測つて居らぬ(当機 gdate 9.11 / python 3.14.6)。fromisoformat の Z と ±hhmm は 3.11+ で素で通るが、直しは Z→+00:00・±hhmm→±hh:mm を己で正規化する故 3.7+ で通る筈(★筈= 測れぬ★)。
- 姿 G の flock は stub(取れたと答へるだけ)。排他は測つて居らぬ(的の外)。
- 閾の意味= 「response_by_time 超過 120s」を「deadline の後 120 秒で stale」と読んだ(設計 §1.2 表・L137 は `now > response_by_time` とだけ言ふ)。別の読み(deadline の中に 120 が既に含まれる)なら `DETECT_STALE_STALE_SEC=0` で旧の振舞ひに戻る(41 B_now-1s_SEC0 で実測)。★何れの読みかは軍師/家老の裁★。
- 姿B で CLI が enqueued=0 なのは flock 不在(ERROR flock_acquire_failed)= 当機の事情。auto-poke の判は評価 rc 0 で置いた。

## ㊆ 疵(己の・順に)

- ★疵①★ 着手便が 304 字で門(300 字の條)が鳴り送れず、二走で 288 字にした(01_letter.py は二走の形・raw/01_letter.txt は二走)。
- ★疵②★ 41 初走: now を器の起動時に一度だけ取り、各 case は其の 3〜12 秒後に走つた → now-119s の 6 case が実齢 122〜131 s で STALE(正)なのに × と判じた。二走で「時刻は case 毎・閾との差 ±5 s」へ(.first に残す)。
- ★疵③★ 41 二走の patch: regex で `iso(now - 121)` を組へ替へた後に naive 二 case の `[:19]` が組に掛かり落ちた(AttributeError)。錨を逐語にして手で直した。
- ★疵④★ 40 初走の直しに上限が無く、parser の出目へ 2^63-1 を注ぐと ★永久 FRESH★(41 二走 S2_max_int)。二走で `[ -le 253402300799 ]` を足し 41 三走で ANOMALY。
- ★疵⑤★ 60_gate_run.py を sed で km-86 から写した時、註の一行(初走の門控名)が壊れた(mon_km92_…T111110= 存在せぬ)。手で直した。
- ★疵⑥★ 器A は部分一致(語境界無し)ゆゑ多めに出る側= 零なら真に零だが、DETECT_STALE_LOG 13 の内訳は註 3 行を含む(口 3 讀手 7 註 3)。
- ★疵⑦★ 家老表との食ひ違ひ(空・2^63)は家老の器(zsh)の疵であり己の疵ではない ―― が、初めは「家老が値を直に入れた」の宣を信じ /bin/bash で引き直すまで気付かなかつた(引き直したから出た)。
- ★疵⑧★ 30/41 の scratch(inflight marker・lock= 0 byte)は讀んだ後に消した(門 條④)。log は残す(先頭一行は器の印・lib の追記が続く)。41 は三走ゆゑ 41_env / .first / .second の三組が在る。
- ★疵⑨★ 42 初走(.first)は 40 初走の写しで走つた(上限無し)。二走が本。差は S2_max_int にのみ効く(既存 test に其の case は無い)。
- ★疵⑩★ 宣ETA 120〜300 分(幅)⇔ 實は 62 の出目(㊀9・便 5)。
- ★疵⑪★ 家老補①(13:08:32・着手便の 3 分後)を ★門を通した後(13:25)★ に讀んだ= 「箱は弾の前に讀め」を犯した。補①は己の出目と一致し要求は「bash の値で組め」(既に其の形)ゆゑ紙の中身は変はらぬが、此の一行を足す為に臺帳を建て直し門を再走した。
- ★疵⑫★ 其の建て直しの一走目で、47 への patch が門の錠(raw/ 0444)に弾かれ(PermissionError)、★補①の無い紙★で臺帳と門(mon_km92_20260917T132533)を走らせた。錠を解いてから patch し三走目が本。初走 T132416・二走 T132533 の門控と臺帳の写し(_gate/MANIFEST.first.txt・.second.txt)は _gate/ に残る。
