## §的 ★proposals の二本を snapshot の正本と逐語で突き合はせ 字の上だけで round trip を検める（DB 0・走らせず）★

## §A 頭（条㉝）
- 樹 ＝ /home/hakudoukai/karo3/wt-abbrev-guard-20260912（家老の樹・★讀取のみ・書込 0★）／HEAD ＝ 6b5ac1f730ba4f0c／main 起点 ＝ 0dba78e8de65ad59
- as_of ＝ 2026-09-12T16:04／親令 ＝ order344 a3.txt 22 行・符 sha256 先16 15b2a20afe4205e3／BASE ＝ 9426e4d9888a6b8b
- 讀んだ三本 ＝ snapshot（20260909170000・全 1318 行）／apply（proposals・全 48 行）／rollback（proposals・全 45 行）―― 網 ＝ ★行数は split の片数（wc の値に 1 を足した数）★
- 器 ＝ order344 roundtrip.py（88 行・席 dir 内・焚 1・残置）／走 ＝ 1 回（産出が出た ∴ 二度目は撃たず）

## §零-2 禁語の数が割れた因（家老の問ひへの答・新条㊺）
- 己の網の形 ＝ 器は grep の件数取り・単位は ★行★・母は ★紙 1 file のみ★（器の .py は母の外）。∴ 令343 の 生 2 は ★md 1 file の行数★ である
- 割れの因 ＝ ★網の語彙が違ふ★。己は判定の語も網に入れて居り 家老の器は入れて居らぬ ―― 己の 2 行の内 1 行は ★判定の語を含む raw の写し★ であつた
- ∴ 数は二つとも正しい。違ふのは ㊀語彙 ㊁単位（行か語か）㊂母（md 一本か md と py の二本か）の三つである

## §㋐ rollback の本体 と snapshot L722-L761
- 母の外に置いた頭註 ＝ rollback の L1-L4 の ★四行★（起点・出所・裁・対の註）。母 ＝ rollback L5-L44 の ★四十行★ 対 snapshot L722-L761 の ★四十行★
- 突き合せ ＝ ★差 0 行★。sha256 先16 も両塊で同値（ba12a6353d1f5355）∴ ★一字も違はぬ★
- 註 ＝ snapshot の L722 も rollback の L5 も 同じ形の帯の行であり 母の内に数へた（外したのは L1-L4 のみ）

## §㋑ apply と rollback の差
- 母 ＝ 両者の CREATE の行から末尾まで（apply は L9 から・rollback は L6 から・★共に四十行★）
- 差 ＝ ★十行★。内訳 ＝ ㊀中身の差 ★六行★（apply L17/L27・L28/L38・L39/L44 ＝ ★三鍵 × 開きと閉ぢの二行★）㊁★末尾の空白だけの差 四行★（apply L19・L24・L35・L41）
- ∴ ★COALESCE の三箇所の外にも差が在る★ ―― apply は snapshot が持つ ★行末の空白を四行分 落として居る★（apply 本体の行末空白 0 行／rollback と snapshot は 4 行）

## §㋒ round trip（字の上で）
- ⑴rollback は apply の逆ではなく ★snapshot の複製★ である ∴ apply を当てた後に rollback を当てれば ★snapshot の字へ戻る★（行末の空白四行も復る）
- ⑵戻らぬ所 ＝ ★無い★。但し「apply の字へ戻る」のではない ―― 戻る先は ★snapshot の字★ である

## §㋓ 三値
- ⑴★戻る★（字の上で・差 0 行）
- 之では言へぬ事 ＝ ㊀★DB で実際に戻るかは言へぬ★（DB 0・函の本体が DB 側でどう保たれるかを己は測つて居らぬ）／㊁二本が現に打たれた時の順序は言へぬ／㊂頭註が名乗る md5 と byte 数が実の函と合ふかは測れぬ

## §㋔ 残弾（3 から数へ直した・㊅ は残す・本弾の新出は ㊈㊉）
- ㊅ 旧い形の get が L81-L83 に三行残る（patch の網の外）／㊆ 枝の SQL 二本は本弾で字を測つた ∴ 閉ぢる／㊇ main へ merge された（総監督 hs 44fdb2b5・main dfa6cebe3）―― 己は讀んで居らぬ
- ㊈ apply が行末の空白を四行分 落として居る（当てた後の函の字は snapshot と此の四行で違ふ）／㊉ 頭註の md5 と byte 数は DB 0 の床の下では確かめられぬ

## §㋕ 禁語（行・語・母の三つ・新条㊺）
- > 網の語彙 ＝ password secret token api-key credential ―― 及び 判定の語 と 先送りの語 の一群（逐語は本紙に写さず 器の側に置いた）
- 単位 ＝ ★行★（器は grep の件数取り）／母 ＝ ★本紙 1 file のみ★（器の .py は母の外）
- 生 1 行／境界の句と名を除いた数 0 行

## §床の実績
- DB 0／MCP 0／psql 0／apply 0／当て 0／製品 code 書込 0／install 0／fetch 0／rm 0／find 0／ssh 0／/mnt/c 書込 0／家老の樹へ書込 0（讀取のみ）
- 焚 1／走 1（上限 1・二度目は撃たず）／試験 0（pytest を一度も起こして居らぬ）／前紙は一字も書き換へて居らぬ
