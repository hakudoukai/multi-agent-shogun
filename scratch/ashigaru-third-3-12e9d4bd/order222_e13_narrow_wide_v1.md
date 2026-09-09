# order222 ―― 弾倉 E13: 狭網と広網の差 1 を潰す（走 0）

## §零 頭（七条目・HEAD/tree 令・家老 新條）

- as_of 2026-09-09T10:35:45+09:00
- ★己は何処まで測つたか★（家老 新條・書く前の一行）:
  ㋐ 6 枚の前(blob)と今(作業樹)に ★三つの網★ を同じ走で当て、12 本を ★一本づつ★ 名指した（§三）。
  ㋑ 的の樹の追跡下 .py 1,484 枚に ast を当て、代入形の在処を悉く挙げた（§五・★別母★）。
  ㋒ 己の scratch の器 4 本の網を ★逐語で読み★、動く数を名指した（§六）。
  ㋓ ★走らせて居らぬ★ ∴ 「幾つの試験が現に飛ぶか」は本弾でも ★測定不能★。
- 何時・何を・幾つ讀んだか: 本弾で開いた己の器・紙 = o192 器 2 本・o192 紙・o193 器 2 本・o193 紙・o221 器 2 本 の ★8 本★。
- 樹の別（床⑵）:
  - 己の樹 = /home/hakudoukai/multi-agent-shogun
    HEAD=1ad4edfbadc69191183a42113e9979c3f91b7dbf / tree=d856e28815b149db4423b686926e5a42060c89c2 / porcelain=170 行
  - 的の樹 = /home/hakudoukai/a3/wt-bundle-fix4（讀むのみ・★一字も書いて居らぬ★）
    HEAD=47c8bc3b86613d7bd55cdfc062a46dccf8d81d1b / porcelain=6 行（走の前後で同じ）
- 走: ★製品走 0★（git 讀取動詞 show / ls-files と ast のみ）。★走 残 1 は費消せず★。

## §一 令（逐語・引用）

> 「[家老third→A3] ★E12 検収 PASS★=★『直す前』を ★commit 47c8bc3b の blob★ と定め(刻でも版でもない)先に書いたは令の通り★
> =★同じ語が別の物を指す轍を先に塞いだ★。★読めた 6/0・前後 sha 同 0/別 6・o193§九の 6 sha16 全一致★。
> ★自訴(狭網が pytestmark 代入形を落とす=広 12 と差 1)★も可。」（msg_20260909_102916_63b88a3f）

> 「[家老third→A3] ★次弾(走 0)＝★狭網と広網の差 1 を潰せ★★=①★pytestmark 代入形を狭網が落とす★の一件を
> ★網の側の疵か 定義の別かを分けよ★ ②★同じ形が他に無いかを 12 本悉くに当てよ★
> ③★『狭網で数へた過去の数』が動くなら 何処が動くかを名指せ(訂正は其の後)★。」（msg_20260909_102917_8eefc260）

## §二 三つの網の定め（★悉皆の語は網の形と対で★＝隊の条・床(30)）

| 網 | 何を一つと数へるか | 器の逐語 |
|---|---|---|
| N1 狭網 | ★行★（左空白を除いた行頭が飾りで始まる物） | `t.startswith("@pytest.mark.skip(")` |
| N2 広網 | ★字の出現★ | `text.count("pytest.mark.skip(")` |
| N3 ast網 | ★呼び出しの個数★（棲家を別に名指す） | `ast.Call` の func が `pytest.mark.<skip/skipif>` |

- 棲家（N3 が名指す）= `decorator_func` / `decorator_class` / `assign_module_pytestmark` / `assign_other` / `bare`。
- N1・N2 は ★行と字★ を数へ、N3 は ★構文★ を数へる ―― ★三つは初めから別の物を数へて居る★（床(31)「形は ast で」）。

## §三 12 本 悉くに（令②・母 = porcelain の 6 枚）

| side | file | line | name | 棲家 | 持ち主 |
|---|---|---|---|---|---|
| 前 | backend/tests/test_cmd004_cross_cutting_integration.py | 24 | skip | ★assign_module_pytestmark★ | pytestmark |
| 前 | tests/test_step_a4_handover_sheet.py | 377 | skip | decorator_func | test_10_pagination_fits_a4 |
| 前 | tests/test_step_q.py | 461 | skip | decorator_func | test_16_components_exist |
| 前 | tests/test_step_r_ui.py | 282 | skip | decorator_func | test_17_empty_state |
| 前 | tests/test_step_s3.py | 664 / 678 / 692 / 703 / 715 / 726 | skip ×6 | decorator_class ×6 | TestF07〜TestF12 |
| 前 | tests/test_step_s4.py | 742 / 758 | skip ×2 | decorator_class ×2 | TestF16 / TestF17 |
| 今 | backend/tests/test_cmd004_cross_cutting_integration.py | 28 | skipif | ★assign_module_pytestmark★ | pytestmark |
| 今 | tests/test_step_a4_handover_sheet.py | 377 | skipif | decorator_func | test_10_pagination_fits_a4 |
| 今 | tests/test_step_q.py | 461 | skipif | decorator_func | test_16_components_exist |
| 今 | tests/test_step_r_ui.py | 282 | skipif | decorator_func | test_17_empty_state |
| 今 | tests/test_step_s3.py | 664 / 681 / 698 / 712 / 727 / 741 | skipif ×6 | decorator_class ×6 | TestF07〜TestF12 |
| 今 | tests/test_step_s4.py | 753 / 772 | skipif ×2 | decorator_class ×2 | TestF16 / TestF17 |

★三網の和★:

| side | N1 狭 | N2 広 | N3 ast | 棲家の内訳（N3） |
|---|---|---|---|---|
| 前 | 11（skip 11） | 12（skip 12） | ★12★ | decorator_class 8 / decorator_func 3 / assign 1 |
| 今 | 11（skipif 11） | 12（skipif 12） | ★12★ | decorator_class 8 / decorator_func 3 / assign 1 |

- ★N3 − N1 = 1（前後とも）★ ―― 落ちた一本は ★assign_module_pytestmark★ ただ一つ。
- ★N2 − N3 = 0（前後とも）★ ―― ★本母では★ 字の数へは 註釈・文字列を拾つて居らぬ。★別母では未測★（§五 で ast のみ当てた）。
- ∴ ★同じ形（代入形）は 12 本の中に 他に 現に無い★（令②の内側の答）。

## §四 令①への答 ―― ★網の疵か 定義の別か★

★答＝両方が立つ。決めるのは網ではなく ★問ひ★ である。★

| 問ひ | 正しい網 | 11 の値打ち |
|---|---|---|
| 「skip の効きを与へる箇所は幾つか」（＝o193 の「単位」） | N3 ast（＝12） | ★狭網は 1 を落とす＝網の疵★ |
| 「飾り(@)の適用は幾つか」 | N1 狭（＝11） | ★定義通り＝疵に非ず★ |

- ∴ ★11 その物は誤りに非ず★。★己の疵は 11 を出した時に ★何れの問ひに答へた数か★ を同じ行に書かなんだ事★
  （隊の条「悉皆の語は網の形と対で」・床(30)「何を一つと数へたか」を ★己に掛け損ねた★）。
- 更に ★三網の何れも「幾つの試験が隠れて居るか」には答へぬ★ ―― 棲家が三つに割れ、
  ★class の飾りは 中の試験 N 本を覆ひ・func の飾りは 1 本・module の代入は file 悉くを覆ふ★。
  o193 は之を知つて居り ★「単位 24 / 覆ふ試験 31」と欄を分けて居た★。★己は分けて居らなんだ★。

## §五 12 本の外（令② の外側・★別母★）

- 別母 = 的の樹の ★追跡下 .py 1,484 枚★（今の姿のみ・ast を当てた）。
- 当たつた file 24 枚 / 呼び出し 43 個。棲家別 = decorator_func 27 / decorator_class 13 / ★assign 3★。
- 讀めなんだ 0 / ast が解せなんだ 0。
- ★代入形の在処 3 件（悉皆・名指し）★:
  1. backend/tests/test_cmd004_cross_cutting_integration.py:28（★本弾の 6 枚の内★）
  2. backend/tests/test_ba965236_real_auth_probe_dev.py:24（★12 本の外★）
  3. tests/test_step_p_supabase_live.py:34（★12 本の外★）
- ∴ ★「同じ形は他にも 現に在る」―― 12 本の外に 2 件★。
- ∴ ★別母に狭網を当てれば 43 でなく 40 と出る（差 3）★ ―― 将来 樹全体を狭網で数へた数は ★悉く 3 だけ低く出る★。

## §六 令③ ―― ★狭網で数へた過去の数は 何処が動くか★（★訂正は為して居らぬ★）

★己の器 4 本の網を 逐語で読んだ結果★:

| 器 | 網の逐語 | 行頭を問ふか | 動くか |
|---|---|---|---|
| order192_test_escape_census_v1.rule.py | `RE_B = mark\.skip\s*[\(\)]\|mark\.skip$` | ★問はぬ★ | ★動かぬ★ |
| order193_escape_surface_fix_v1.rule.py | `RE_B = mark\.skip\s*[\(\)]\|mark\.skip$`（同じ字） | ★問はぬ★ | ★動かぬ★ |
| order221_e12_before_blob_v1.rule.py | `t.startswith("@pytest.mark.skip(")` | ★問ふ★ | ★動く★ |
| order221_e12_before_blob_v2.rule.py | 同上 ＋ 広網を並べた | 問ふ（併記あり） | ★動かぬ（広 12 を同じ生に持つ）★ |

- ∴ ★動く数は ★order221 v1 の生に在る「狭 skip 11」 ただ一箇所★★。
- ★訂正を要する紙 = 0★ ―― order221 の紙 §五 は ★狭 11 / 広 12 を欄で分けて併記済★ かつ §十 に自訴済。
  但し ★本弾に依り 其の「狭 11」は ast 12 に対する ★下限★ と判つた★（前紙は書き換へず・本紙に併記＝★前紙は書き換へるな★）。
- ★o192 の 23・o193 の 23/24 は 動かぬ★ ―― ★数の見た目ではなく 器の網の逐語で判じた★。
  （之は「他の紙も疵かも知れぬ」と見えた所を ★悉皆に当てて 現に無いと言へた★ 一件である）

## §七 見込みの当否（★測る前に別 file へ置いた★・條 二百四十六）

- 置いた file = scratch/ashigaru-third-3-12e9d4bd/order222_e13_forecast_pre.md
  sha256 = 09eeed406810436ebe2378f92337d5b55034db081ec93a3cd94675075e291c91 / mtime 2026-09-09 10:30:44 +0900 / 47 行・3,824 B
- 令が着いた刻 10:29:17 ＜ ★見込みの mtime 10:30:44★ ＜ 生の mtime。∴ ★測るより前★ に在つた（★令より前ではない★）。

| 見込み | 実測 | 当否 |
|---|---|---|
| ㋐ 両方立つ・真の疵は「網を名指さなんだ事」 | §四 の通り | ★当たり★ |
| ㋑ 代入形 1 / 飾り 11・散らばり 1/1/1/1/6/2 | 現に其の通り | ★当たり★ |
| ㋒ 12 本の外の代入形は ★見当が付かぬ★ | ★2 件★（§五） | ★値に落ちた★ |
| ㋓ 訂正を要する紙 0・動くは o221 v1 の生のみ | 現に其の通り | ★当たり★ |
| ㋔（外れ得る道）class 水準が混じり単位が割れる | ★現に在つた（8/11 が class）★ | ★道が現に開いて居た★ |
| ㋕（外れ得る道）pytestmark の list 形 | 0 件 | ★現に無い★ |
| ㋖（外れ得る道）skip の儘の物が残る | 今 skip=0 | ★現に無い★ |
| ㋗（外れ得る道）他にも狭網の器 | v2・本弾の器のみ（両方併記済） | ★実害無し★ |
| ㋘（外れ得る道）広網が註釈・文字列を拾ふ | N2−N3=0（★本母のみ★） | ★本母では 現に無い★ |

## §八 測れなかつた物（母数と別値＝型⑧）

- ㋐ ★幾つの試験が現に飛ぶか★ ―― 走 0 ∴ ★測定不能★（class の飾りが覆ふ本数を数へるには収集が要る）。
- ㋑ ★別母 1,484 枚に対する N2 広網の値★ ―― 本弾では ast のみ当てた ∴ ★測つて居らぬ★。
- ㋒ ★別母の「前」の姿★ ―― blob を当てたのは 6 枚のみ ∴ ★測定不能★。
- ㋓ ★12 本の外の 2 件が 何時 入つた物か★ ―― 本弾では ★測つて居らぬ★。

## §九 負の対照（家老 165 ―― ★立つ／立たぬ の双方が現に出得るか★）

- 作り物（代入形 1 ＋ 飾り形 1）に三網を当て、★N1 狭 skip=0 なのに N3 ast に assign が在る★ 事を現に刷らせた
  ∴ 「狭網が代入形を落とす」は ★器の言でなく 器の出力★ である。
- 現に無い path を `git show` した rc = 128 ∴ 「讀めぬ」を判ずる口は現に立つ。
- 器は N2−N3 が 0 でない形も刷る口を持つ（差の欄を常に刷る）。本母では 0 と出た。

## §十 本弾で鋳た條

- ★二百五十六★「★単位を数へたら 覆ふ数を別の欄に置け。★ 一つの数が三つの棲家（class の飾り・func の飾り・module の代入）を
  跨ぐ時、其の数は『幾つ隠れて居るか』に答へぬ ―― class の飾りは N 本を、func の飾りは 1 本を、代入は file 悉くを覆ふ。
  o193 は『単位 24 / 覆ふ試験 31』と分けて居た。★己は分けずに 11 と書いた★。」
- ★二百五十七★「★網の疵か 定義の別かは 網でなく ★問ひ★ が決める。★ 同じ 11 が、問ひを変へれば 正にも 疵にも成る。
  ∴ 数を出す時は ★網★ ではなく ★問ひ★ を同じ行に書け ―― 網は問ひから従ふ。」
- ★二百五十八★「★『他の紙も動くか』を問はれたら 其の器の網を 逐語で読め。★ 数の見た目・書き手・刻では決まらぬ。
  本弾では o192/o193 の網が ★行頭を問はぬ★ 字であつたゆゑ 動かなんだ ―― ★読まねば『動くかも知れぬ』の儘であつた★。」

## §十一 型 8 項 と argv

| 項 | 置き所 |
|---|---|
| ① repo 相対 path | §五・§六・§十二 |
| ② 完全 SHA 64 桁 | §零（pin・HEAD）・§七（見込み file） |
| ③ argv 逐語 | `python3 scratch/ashigaru-third-3-12e9d4bd/order222_e13_narrow_wide_v1.rule.py` |
| ④ raw の完全 SHA と行数 | 完了便へ回す（自己参照ゆゑ） |
| ⑤ exit code | rc=0 |
| ⑥ host/user/cwd | cwd=/home/hakudoukai/multi-agent-shogun / user=hakudoukai / host=momizi-dx |
| ⑦ 正負の対照 | §九 |
| ⑧ 母数と測れなかつた数を別値 | §三（母 6 枚）・§五（別母 1,484 枚）・§八 |

## §十二 物の帳

| path（己の樹・repo 相対） | 何 |
|---|---|
| scratch/ashigaru-third-3-12e9d4bd/order222_e13_forecast_pre.md | ★測る前の見込み★（47 行） |
| scratch/ashigaru-third-3-12e9d4bd/order222_e13_narrow_wide_v1.rule.py | 器（三網を並べる・213 行） |
| scratch/ashigaru-third-3-12e9d4bd/order222_e13_narrow_wide_v1.raw.txt | 生（71 行） |
| scratch/ashigaru-third-3-12e9d4bd/order222_e13_narrow_wide_v1.md | 本紙 |

- 的の樹へ ★一字も書いて居らぬ★（HEAD・porcelain が走の前後で同じ）。一時 file 0（リダイレクトと tee を使はず）。
- ★order221 の器 v1（狭網のみ）は消して居らぬ★（WIP は消すな・狭網の証として残す）。

## §十三 繰越（★答の数には触れて居らぬ★＝家老163）

- ★E14★: o193 の「24 単位 / 覆ふ試験 31」を ★ast網★ で当て直す（走 0）。本弾で ★別母 43 個★ と出たゆゑ、
  o193 の 23（B 無条件 skip）と ★母も網も別★ である ―― ★足すな★。★本弾では一つも當て直して居らぬ★。
- ★E15★: 12 本の外の代入形 2 件が ★何を覆つて居るか★（file 悉くか・条件付か）を ast で見る（走 0）。
- 家老へ諮る物（★己で撃たぬ★）: ㋐器A2・A3 の悉皆の外を器に刷らせる ㋑A7 の分子（走が要る）。

as_of 2026-09-09T10:35:45+09:00
