# 令309 未追跡の開き ―― 99 行が何本に開いたか
## §的 ★308 ㋑ の自開示「99 は行の数であり file の数ではない」を実 file 数で埋め ■五の問ひに符で答へる★
## §A 頭書
- 何時 as_of 2026-09-11T18:33:36+0900・HEAD 1ad4edfbadc69191（短 1ad4edf・本弾でも不動）・樹＝作業樹 /home/hakudoukai/multi-agent-shogun
- 何を幾つ讀んだか ―― 令の逐語 1 本（scratch/k3-orders の order309 の txt・8 行(wc)/9 片・sha256頭16 20de18b1172e4c55・己が実読）・己の箱 1 本・讀取 8 打（床の上限 12）
- 走 0・焚 0・DB 0・当て 0・作業樹へ書込 0（己の紙 1 本を除く）・scratch の file は一本も消さず移さず touch せず・mtime は走ゆゑ打たず（令264 ■〇-2 の裁を継ぐ）
## §B ㋐ 実 file 数（git status --porcelain -uall の 未追跡行）
- 実 file 数 ＝ ★2,471★（一つと数へたのは「未追跡行 1 行 ＝ file 1 本」・-uall ゆゑ dir 畳みは起きぬ）
- dir 別（第1segment・11 種）＝ scratch 2408／tests 15／docs 14／shim 12／scripts 12／reports 5／dentalbi 1／council-board 1／config 1／backend 1／.claude 1 ―― 和 2,471（file 名は一本も挙げぬ）
- ★path のクォート形を剥がして畳んだ★ ―― porcelain は非 ASCII を含む path を二重引用で囲む。剥がす前は 7 件が別 dir に化けて居た（前後の引用を落として scratch へ統合した）
- 308 の 99 行の内訳 ＝ dir 畳み行 45 ＋ file 行 54。∴ ★45 行が 2,417 本に開いた★（2471 引く 54 ＝ 2417）
## §C ㋑ scratch 配下の本数と 己の紙の在り処
- scratch 配下の実 file 数 ＝ ★2,408 本★（㋐の 2,471 のうち scratch 外は 63 本）
- ★己の席 dir scratch/ashigaru-third-3-12e9d4bd/ は 未追跡行に 0 件★ ―― 之は「現に無い」ではない。--ignored を足すと同 dir は 無視行 605 件（悉く file・dir 畳み 0）として現れる
- 因 ＝ 冠の .gitignore は whitelist 型（全 447 行）。L7 の 星 一字が全除外・L10 の 除外解き が dir の探索のみ許し・L13 以降が path 名指しで個別に許す。己の紙は L7 に当たる（check-ignore -v が rc=0 で L7 を指した）
- 他席の scratch が 未追跡行に出る因 ＝ 名前だけの除外解き行（L10・L16・L13・L69）と 他席 dir 内の入れ子 .gitignore 3 本に当たる為
- 席 dir 別（第2segment）では上位 3 席で 1,809 本（988／505／316）を占める ―― 席名は挙げぬ
- ★一本も消さず・移さず・touch して居らぬ。本節は積みを測つただけである★
## §D ㋒ M 66 本と ignore の型
- M 66 本を check-ignore --stdin に流した ―― 当たり 0 本（rc=1）∴ ★現に無い★
## §E ㋓ 308 ㋔ の三値の更新
- 三値 ＝ ★断じ得ぬ★ のまま ―― ★動かぬ★
- 本弾で得た符は三つ（己の紙は無視され git の目に入らぬ／他席 scratch が 2,408 本積む／M 66 本は無視の型に当たらぬ）。★何れも「未 commit の差を誰の手が書いたか」を証さぬ★
- 足らぬもの一行 ＝ 未 commit の差に書き手を結ぶ符を git が持たぬ事（符は commit の時に初めて生まれる）
## §F ㋔ ■五 家老の問ひ ―― 枝が HEAD 直に生えて居るのは常の作法か
- 答 ＝ ★常の作法ではなく 混在である★
- 実測 ―― refs/heads/a3 の下を 100 本数へ、各 tip の親を一つづつ引いた。親が HEAD 1ad4edf ＝ 27 本／親が別の符（前弾の tip に連なる鎖）＝ 71 本／親を引けぬ（根の符）＝ 2 本。和 100
- 直前の四弾（order304→305→306→307）は鎖であり、order307 の tip 5f26885 の親は order306 の tip 46120df である。★order308 のみ HEAD 直に戻つた★
- 因 ＝ 押しの形の BASE に HEAD の符を直書きして居る為である。鎖に成るのは前弾の tip を BASE に写した弾のみ
- 紙の重なりも測つた ―― order307 の樹は己の席 dir に 54 本を持ち、order308 の樹は 15 本を持つ。★HEAD 直の弾は前弾の紙を樹に載せぬ★（之が家老の六段の当て先に響く）
## §G 床の守り
- 讀取 8 打（上限 12）・焚 0・走 0・DB 0・当て 0・stage 0・checkout 0・stash 0・clean 0・restore 0・git add -A 0（己の紙 1 本のみ add）・一時 file 0・リダイレクト 0・tee 0
- 判定語 0・三択語で結んだ（㋒＝現に無い／㋓＝断じ得ぬ）・他席の箱へ書込 0
