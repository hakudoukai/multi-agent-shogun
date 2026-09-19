# km-214 ―― pane_identity.sh の二疵: ⑴session の前方一致 → 完全一致 ⑵期待表を registry から引く(委員長裁 seq337507⑶疵②・seq337388㋑)

- 帳 = queue/tasks/ashigaru-mac-1.yaml `tsugi_no_tama_214_20260919T1825`(task_id subtask_mac_km214_pane_identity_kanzen_icchi_registry_001・板 None)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙 2026-09-19T18:35:28+0900 / 着手便 18:27(len 288・一度目 326 で撥ね)/ 宣ETA 19:40 / 測り・是正 18:26〜18:34
- 枝 = `ashigaru-mac-1/km-214-pane-identity-kanzen-icchi-to-registry-20260919`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・~/wt/a1-km214)。押さず。

## 己の疵(先に)

⑴ 着手便 300 字超 1(326 → 288)。⑵ 触る前の tmux 実測の一つ目を zsh で打ち、`=multiagent` が zsh の `=` 展開(命令の path 解決)に食はれて eval が落ちた ―― bash で打ち直した(raw/20)。⑷ 試験 round1 は後版が★一行も刷らず rc 0★で終はつた ―― 是正の疵ではなく、己の樹(origin/main)の `lib/_section18_roles.sh` が `declare -A`(L108)で bash 3.2 + set -u に落ち source が死ぬ為(raw/33・34)。生きた樹の lib(148 行・未 commit)は直つて居る。round2 は env `SECTION18_ROLES_LIB` で生きた lib を指した(round1 は raw/31_tests_round1・30_*_round1 に残置)。⑸ C4(python 無し)は round2 で PATH を空にし dirname も無く器が期待表の前で落ちた(rc 127・出目無し)―― 要る外部命令だけを link した PATH で取り直した(raw/03・31_c4_rerun)。其の対照(python3 を symlink で足す)は venv を symlink 経由で呼ぶと site-packages(yaml)を見失ひ parse_error に成つた = 試験の癖・器の疵ではない(python 有りの陽性対照は B_after_ok)。⑺ ★版の事★: 命の行は生きた共有樹の pane_identity.sh(509 行・未 commit・mtime 07:20:55・家老の bash 3.2 表化 seq337297)に在り、origin/main 版(474 行)には `declare -A` の旧表が在る。∴ km-213 と同じく★先づ生きた版を其の儘写して commit(前 33a37e49)し、次に是正だけを commit(16cd90d1)★。共有樹の器・lib・pane・箱は不触。⑻ 門 round1(first/second・rc 1・同出目)は 條④ で 8 file に鳴つた(raw/30_*.out 7 本と raw/32_live_run.out・器の stdout の尾に空行 2〜3)―― 己の正規化が尾の空要素を一つしか剥がぬ形であつた。尾の改行を悉く剥ぎ一つに揃へ(raw/40_r2_normalize_koku)、8 行を臺帳から落として器で組み直し(append.r2 log)、門は取り直す。round1 の門 log(gate.first/second)は残置。⑼ ★門の版★: round1 の門は生きた樹の scripts/checks/karo_mac_dasumae_gate.sh(321 行・sha256 2b8449bc…・HEAD 363d5fb0 + 未 commit の手)で打つて居た。己の枝(origin/main c0220128・PR#27・裁 seq330497 ④「末尾は全空白行を見る」)の門(339 行・sha256 3b8b7182…)で打ち直すと、空の出目を一行の改行だけで置いた 13 本(30_*_round1 の .out/.err 10・30_C4_no_python.out・30_C4_no_python_round1.out・30_dbg_round1.out)が「末尾行が不可視のみ」で落ちる(r4first/r4second・rc 1・同出目)。生きた樹の門は同じ 13 本を通す(旧形 條④=末尾二字)= ★二つの門で顔が変はる★。裁 310228⑶ は 0 byte を禁じ、裁 330497④ は空行のみの末尾を禁ずるゆゑ、空の出目は可視の一行札 `(空 0byte)` に替へた(raw/41_r3_kara_fuda_koku・原本は悉く 1 byte の改行のみで在つた事を替へる前に器で確かめた)。途中の r2first/second(_usage: 門へ file 列を渡さず usage 落ち rc 2)と r3first/second(_zshsplit: zsh で $FILES が一語に成り 63 本が「file が無い」)も己の疵として残置。最終の門は r5first/r5second。

## 裁(逐語・帳の hon より)

seq337507⑶疵②:「前方一致で生きた%72を掴む形」「-t は =名 か %N へ。固定寫像は該当session無ければ fail-closed」。seq337388:「★㋑を採る★＝期待表を queue/pane_registry.yaml から引く・理『手で表へ足せば腐る』」。

## ㋐ 母數宣言

- 歩いた = 器 `scripts/checks/pane_identity.sh` 生きた版 509 行の全行(`-t` を持つ行 5: L141・142・153・218 と source C/D の grep は tmux でない)/ `queue/pane_registry.yaml` 196 行(panes 19・鍵 tmux_target/agent_id/persona/pc/role/status 各 19・cli 6・note 8・migration_status 8・model 5・MainPC 9・SecondPC 10・mac を名指す席 0)/ 生きた tmux(session 4: gakushu-bucho・hermes-drm・hermes-gunshi-mac・multiagent-mac・読取のみ)。
- 除いた(歩いたが触らぬ) = source C/D(watchdog・§18.1 の grep・tmux でない)・L142 の `list-panes -a`(`-a` は全 session を列べるゆゑ -t の完全一致に依らず Mac の pane も刷る ―― Pane Identity Map の顔・命の外・㋔)・`lib/_section18_roles.sh`(bash 3.2 に落ちる旧版・命の外・raw/34)。
- 歩いて居らぬ = 他の器(agent_status.sh 等・命で禁)・SecondPC の tmux。

## ㋑ 三値(raw/10・12)

| | sha256 | bytes | 行 |
|---|---|---|---|
| origin/main 6bde7170 版 | c1d1ece4371021cd44e2c2a6a7b6a77efa8df48263f8e10c17c960851bc79205 | ― | 474 |
| 前 = 生きた版(写し commit 33a37e49) | db1ce339534e8bcb82e142047d42da4d991abe44dcafc373ebbe063940236db2 | 21636 | 509 |
| 後 = 是正 commit ★16cd90d1096e43e333fd2fbb5115e8b5daf58d96★ | b26f6df4050e85e3fb348cfccc06def2975511b3be9e058b64ad63260885d7af | 25367 | 571 |

diff 前→後 +/- 81 行(raw/11)・`bash -n` rc 0(前後とも)。

## 是正の中身(逐語は raw/11)

- 疵⑴: `has-session -t "$s"` → `-t "=$s"`(session loop)。★実測(raw/20・21)★: `has-session -t multiagent` rc 0(前方一致・multiagent-mac を掴む)/ `-t =multiagent` rc 1。但し `display-message`/`list-panes` は `=` を付けても目標が無い時★TMUX の中では今の client の session/pane へ黙つて落ちる(rc 0・空)★ ―― 之が「前方一致で生きた %72 を掴む」の第二の路。∴ pane を問ふ前に `has-session -t "=$sess"` で session の実在を確かめ、無ければ★比較せず「⚠ session が無い(完全一致)―― 比較せず」★を刷る(warnings)。source A も `has-session -t =multiagent &&` を先に置き `-t "=multiagent"` へ。
  - ★宣★: session が真に無い時を violation でなく ★warning★ に置いた。理: 此の Mac には MainPC の session が設計上 存在せず、violation にすれば毎 hook が偽の違反を数へる(鳴りすぎる鐘)。fail-closed の趣旨(掴み違ひで別 session を比べぬ)は「比較せず」で満たす。判は家老・委員長へ。
- 疵⑵: 手書き `EXPECTED_TABLE`(5 行)を `queue/pane_registry.yaml` から引く。引く手 = `${PYTHON:=$REPO_ROOT/.venv/bin/python3}` → 無ければ PATH の python3 → 其れも無ければ★fail-closed★。対象 = `pc: MainPC` かつ `status: 通常運用`・鍵 = `tmux_target` 逐語・値 = persona(無ければ agent_id)。四形を `EXPECTED_TABLE_STATE` に分け、比較の前に刷る: `ok`(▷ 期待表 = … N 席)/ `no_python`・`no_registry`・`parse_error`・`empty` は★各々別の ❌ 行 + violations++★。bash 3.2(改行区切りの表 + table_get/table_keys)を保つ。
  - ★表の顔の変化(黙つて変へぬ・宣す)★: 手書き 5 席 → registry 7 席。鍵の綴り `multiagent:agents.N` → `multiagent:0.N`・`shogun:main.0` → `shogun:0.0`(registry 逐語)。増 = `multiagent:1.0=honda`・`multiagent:2.0=sanada`(status 通常運用)。減 = 無し。除かれた MainPC 席 = `multiagent:0.4=ashigaru3`(非常時 +1)・`multiagent:0.5=takenaka`(持ち場準備中)。shogun の空 @agent_id 許容は `case shogun:*)` へ(綴りの変化に随ふ)。

## ㋒ 両対照(同一 run `bash raw/02_run_tests.sh` round2・18:32:26・raw/31・30_*・cwd 束の根・rc は file へ・TMUX の中・SECTION18_ROLES_LIB=生きた lib)

| 札 | 器 | env | rc | 出目 |
|---|---|---|---|---|
| A_before(陽性対照=疵が鳴る) | 前版の写し | registry=己の樹 | 2 | ★❌ 10・偽の掴み 4★(`0 karo-mac hideyoshi ❌ DRIFT` …= 前方一致で Mac の pane を MainPC の期待と比べた)・「❌ 4 件の整合性違反 + 4 件の 4-way drift」 |
| B_after_ok(陰性対照=正しい配置で鳴らぬ) | 後版 | registry=己の樹・PYTHON=.venv | 1 | `▷ 期待表 = … から 7 席 (MainPC・通常運用) を引いた`・★❌ 0・偽の掴み 0★・⚠ 9(session shogun/multiagent が無い・7 席とも「比較せず」)・「⚠ 9 件の warning」 |
| C1_no_registry | 後版 | PANE_REGISTRY=無い path | 2 | `❌ 期待表を引けぬ: registry 不在 …` |
| C2_parse_error | 後版 | 壊れた yaml(raw/seed) | 2 | `❌ 期待表を引けぬ: registry を parse できぬ …` |
| C3_empty / C3b_no_mainpc | 後版 | panes: [] / SecondPC のみ | 2 / 2 | `❌ 期待表を引けぬ: registry に MainPC・通常運用 の席が 0` |
| C4b_no_python(raw/03・31_c4_rerun) | 後版 | PATH=要る命令のみ・python3 無し・PYTHON=無い path | 2 | `❌ 期待表を引けぬ: python3 が無い (.venv/bin/python3 も PATH も)` |

四形は悉く★別の顔★で、悉く rc 2(violations)。前版 4 の偽の掴み → 後版 0。

## ㋓ 条の逐語

上「裁」節。加へて 変更統制(理事長令 2026-08-11)= 本弾は裁の許した一器。第一条 = 出所不明の未 commit(生きた版 509 行・lib 148 行)は味方の物として消さず写した。

## ㋔ 案(★紙のみ★)

- `lib/_section18_roles.sh` の bash 3.2 化(生きた樹の 148 行・未 commit)を commit せねば、origin/main から切つた樹では pane_identity.sh が★黙つて rc 0 で死ぬ★(raw/33・34)―― 家老の手(己の未 commit)。
- L142 `list-panes -t "=$s" -a`: `-a` は全 session を列べ -t を無視する。Map の顔として Mac の pane が出る。完全一致に揃へるなら `-a` を外す(別弾)。
- source B の hand parser(L234〜)は yaml を使はぬ・本弾の期待表は yaml 使用 ―― 二つの読み方が同 file に並ぶ。揃へるなら別弾。
- registry の `status` の値(通常運用/非常時 +1/持ち場準備中)を期待表の対象の判に使つた ―― 値の語彙は registry の側で固定されて居らぬ(自由文)。

## 判定の束 ①〜⑦(seq335106)

- ① 対象 tuple: 器 `scripts/checks/pane_identity.sh`・前 = 生きた版の写し commit 33a37e4978038348ea1394875c35859551cd0ec3・後 = 是正 commit ★16cd90d1096e43e333fd2fbb5115e8b5daf58d96★(1 file +72/−10)・束 = 本紙の commit(納め便に)。
- ② 成果物: 後の器 sha256 b26f6df4050e85e3fb348cfccc06def2975511b3be9e058b64ad63260885d7af。raw は臺帳(束内相対)に全行(10・11・12・20・21・33・34・02・03・31・31_c4・30_*・seed の registry 三本)。写し raw/utsushi/pane_identity.before.sh(db1ce339…)と raw/seed/bin_* の symlink は臺帳外。
- ③ 実走 raw: 表の通り(argv は raw/02・03 の逐語・rc は `.out/.err` と行に)。
- ④ 依存: /bin/bash 3.2.57・tmux 3.7b・.venv/bin/python3 3.9.6 + PyYAML 6.0.3(homebrew python3 3.14.6 にも yaml 6.0.3・/usr/bin/python3 には無し)・coreutils timeout。lockfile 無し・install receipt 未測(install 無し)。外部 symlink 参照: raw/seed 配下に★57★(bin_no_python 28・bin_with_python 29・差は python3 のみ・find で実測)。的=絶対 path 群 /bin/{cat,date,ls,mkdir,mv,rm}・/usr/bin/{awk,basename,cut,dirname,env,head,mktemp,readlink,sed,sort,stat,tail,touch,tr,uniq,wc}・/opt/homebrew/bin/{timeout,tmux}・bin_with_python のみ /Users/momizimac/multi-agent-shogun/.venv/bin/python3 + 自己名の相対壊れ fixture 4種(false/grep/printf/true・両側)。悉く raw/seed の試験 fixture であり本体の実行時外部依存ではない(raw/44_revise_kotae.txt 一)。
- ⑤ 正・意味負: 前版 偽の掴み 4(陽性)/ 後版 0(陰性)・fail-closed 四形 4 run 悉く rc 2 別の顔 / 期待表 7 席(陽性)・後版 ⚠ 9。
- ⑥ 復元: 共有樹の器・lib・registry・pane 不触(読取のみ)。己の樹 `git status --porcelain -uall --ignored` は束 commit の後 raw/40 に(双子 1 行 + 未 add の raw/40 自身を除き空)。復元後 sha256(実測・raw/44_revise_kotae.txt 二): pane_identity.sh(生きた版)=db1ce339534e8bcb82e142047d42da4d991abe44dcafc373ebbe063940236db2・lib/_section18_roles.sh=8473838e23bbcee8132b1e7fc16d36ae00d480e1e78d0b3f1c620a74ec488db0・queue/pane_registry.yaml=1c807cb4ae8603da9d32c4a70730be5ae06bebb3953ab4cfff51702c7cf3c874 ―― 悉く着手前(raw/10・raw/34)と同値、不触を確認。再正(raw/44 三): raw/02・raw/03 を raw/30_→raw/43_ へ非破壊で写して取り直し、7 形(A_before/B_after_ok/C1〜C3b/C4b_no_python)★7/7★ rc・件数・期待表文言一致(raw/42_saisai_jikkou.*・raw/42b_c4_saisai.*)。
- ⑦ 法令根拠: seq337507⑶疵②・seq337388㋑・seq337297(bash 3.2 表化)・裁 335122⑶(束は git へ)・322699・336241・333060⑶・第一条。

## 宣⇔實

宣 19:40・實 = 報告便の刻(紙の外)。
