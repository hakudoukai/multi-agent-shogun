# order226 / E21 ―― ★「網が回る 0」は 器の疵に因る 0 であつた★

as_of: 2026-09-09T11:54:57+09:00
席: ashigaru-third-3 (板 12e9d4bd) / host=momizi-dx(third_pc) / user=hakudoukai
cwd: /home/hakudoukai/multi-agent-shogun
HEAD: 1ad4edfbadc69191183a42113e9979c3f91b7dbf (不動) / porcelain 170
押しの BASE: 7534154b68582bd0ce0ad0f789640ac299306c30 (E17 の tip)

## §零 ★何時・何を・幾つ讀んだか★（作法 七条目）

- 本弾で走らせた器 = 2 本（order226 v1 / v2）。★製品走 0★・DB 0・走行は本席 dir の中のみ。
- 器が當たつた母 = 本席 dir の .py ―― v1 走時 88 枚 / v2 走時 89 枚（増 1 は ★己が書いた v2 自身★）。
- 源として實讀した他席の器 = `three_nets_outside_v1.rule.py` L36-40 / L59-62、`kensu_reconcile_v1.rule.py` L30-34（★己で當たつた・写しに非ず★）。
- 走 = ★残 1・本弾でも一發も費消せず★（製品走 0）。

### /tmp の置き物（消さず控へた・床⑴）

| 名 | 刻 | 大きさ | sha16 |
|---|---|---|---|
| /tmp/a3-tree.txt | 2026-09-08 09:46:12 +0900 | 3,183 B | 103ae1650945d18f |
| /tmp/a31_respawn_cmd.txt | 2026-09-07 21:15:02 +0900 | 318 B | 425e5b00bde28e4b |

★己が作つた物か否かは 測定不能★（本弾の器は /tmp へ一つも書いて居らぬ ―― `*o226*` の当たり 0 を機械に言はせた）。

## §一 ★書く前に「己は何処まで測つたか」★（家老 新條）

測つた = ㋐ 21 件の内 ★包む輪が現に在るは幾つか★（門）／㋑ 器が四つの形を ★現に出分けるか★（検出力）／㋒ 門を通つた件の ★何が回つて居るか★。
★測つて居らぬ★ = 回る事が ★誤りを生むか否か★（本弾は形の帳のみ・是非を問はず）。

## §二 ★撃つ前に測らなんだ事（先に自訴）★

一發目（v1）で 己は ★門と検出力を先に測る器★ を鋳た ―― 立条は守つた。
而して ★検出力の測りそのものが偏つて居た★。

負の対照に置いた作り物は ★For 文の網回り★（`for p in PATS:` … `re.search(p, s)`）のみであり、
★内包の網回り★（`any(re.search(p,l) for p in DECL)`）を ★一つも試して居らなかつた★。

∴ v1 が出した ★「網が回る 0」★ は、★口が在る形についての 0★ ではなく、
★試さなかつた形については 口が無い 0★ であつた。

## §三 ★因（器の何処が拾へて居なかつたか）★

v1 の輪の辿りは `ast.comprehension` 節点を親に持つ時のみ 輪として拾つた。
而して ★内包の `elt` に居る当たりは `comprehension` を親に持たぬ★ ―― 親は `ListComp` / `GeneratorExp` 本体である。

```
any(re.search(p,l) for p in DECL)
    ^^^^^^^^^^^^^^  <- 此の当たりの親は GeneratorExp であつて comprehension ではない
```

∴ v1 は ★内包で回る網を 悉く取り落した★。

## §四 ★直し（網は一字も変へず・條 二百七十一）★

v2 で直したは ★輪の辿り（`enclosing_loops`）★ と ★負の対照★ の二つのみ。
★網・分け（`call_name` / `build_parent` / `classify` ―― E16 器 L21-L72 の逐語の写し 1,916 字）は 一字も変へて居らぬ★。

器自身に言はせた（`assert` と `print`）:

```
order226_e21_gate_and_power_v1.rule.py  True 1916
order226_e21_gate_and_power_v2.rule.py  True 1916
```

∴ ★分けの逐語の差 = 0★（双方に E16 器 L21-L72 が逐語で含まれる）。v1↔v2 の行差 = 25 行（悉く 輪の辿りと負の対照と出力先の名）。

## §五 ★何の単位が動いたか★（家老 新條 ―― 「差」でなく「単位」を先に問へ）

| 単位 | v1 | v2 | 動いた因 |
|---|---|---|---|
| 母（.py の枚） | 88 | 89 | ★己が v2 を書いた★（一族を母から外して居らぬ） |
| ㋐値を取る（件） | 21 | 21 | ★不動★ ―― 己の一族から ㋐ は 現に出て居らぬ |
| 門（包む輪が在る・件） | 14 | 17 | ★器の直しのみ★ |
| 門の外（件） | 7 | 4 | 同上 |
| 網が回る（件） | 0 | ★4★ | 同上 |
| 双方が回る（件） | 0 | ★2★ | 同上 |
| 母が回る（件） | 7 | 6 | 同上 |
| 何れも回らぬ（件） | 7 | 5 | 同上 |

★∴ 網は動かず・母集団の中身も動かず（㋐ は 21 で不動）・動いたは ★器★ である。★

## §六 ★一件づつの移り（14 件 + 門外 3 件）★

### ㋐ v1 の門内 14 件 ―― ★3 件が改まり・11 件が不動★

| path:line | v1 の判 | v2 の判 | v2 の包む輪 |
|---|---|---|---|
| kensu_reconcile_v1.rule.py:33 | 何れも回らぬ | ★双方が回る★ | GeneratorExp+GeneratorExp+comprehension+ListComp |
| three_nets_outside_v1.rule.py:39 | 母が回る | ★双方が回る★ | GeneratorExp+comprehension+ListComp+For |
| three_nets_outside_v1.rule.py:61 | 何れも回らぬ | ★網が回る★ | GeneratorExp+For+For |
| index_fix_all_six_v1.rule.py:25 | 何れも回らぬ | 何れも回らぬ | For |
| kugi68_dedup_close_v1.rule.py:14 | 母が回る | 母が回る | For+For |
| order184_rule_number_ledger_v1.rule.py:28 | 母が回る | 母が回る | For |
| order184_rule_number_ledger_v1.rule.py:100 | 何れも回らぬ | 何れも回らぬ | For |
| order196_magazine_v1.rule.py:24 | 何れも回らぬ | 何れも回らぬ | For |
| order197_head_reproof_v1.rule.py:42 | 何れも回らぬ | 何れも回らぬ | For |
| otsu_runtime_probe_v1.rule.py:97 | 何れも回らぬ | 何れも回らぬ | For |
| unmeasurable26_census_v1.rule.py:12 | 母が回る | 母が回る | For |
| unmeasurable26_census_v1.rule.py:22 | 母が回る | 母が回る | For |
| unmeasurable26_status_triage_v1.rule.py:12 | 母が回る | 母が回る | For |
| unmeasurable26_status_triage_v1.rule.py:53 | 母が回る | 母が回る | For |

### ㋑ v1 が ★門の外★ と断じ v2 で門内へ入つた 3 件 ―― ★悉く「網が回る」★

| path:line | v1 | v2 の判 | v2 の包む輪 | 逐語 |
|---|---|---|---|---|
| boolop39_genexp3_shape_and_ledger_audit_v1.rule.py:23 | 包む輪が無い | ★網が回る★ | GeneratorExp | `next(i for i,v in enumerate(g.values) if v is PA[id(c)])` |
| kensu_reconcile_v1.rule.py:19 | 包む輪が無い | ★網が回る★ | GeneratorExp | `re.search(p, s)` |
| three_nets_outside_v1.rule.py:18 | 包む輪が無い | ★網が回る★ | GeneratorExp | `re.search(p,s)` |

★∴ 網が回る 4 = 門外から入つた 3 + 門内で改まつた 1（three_nets:61）★
★∴ 双方が回る 2 = 門内で改まつた 2（kensu:33 / three_nets:39）★

## §七 ★検出力（v2 の負の対照 ―― 6 本を作り物で當てた）★

```
作り物 => ('㎐', '網が回る', ['p'], [])            for p in PATS:  re.search(p, s)
作り物 => ('㎐', '母が回る', [], ['l'])            for l in LS:    re.search(PAT, l)
作り物 => ('㎐', '何れも回らぬ', [], [])            for k in KS:    re.search(PAT, s)
作り物 => ('㎐', '★双方が回る★', ['q'], ['q'])      for q in QS:    re.search(q, q)
作り物 => ('㎐', '網が回る', ['p2'], [])           any(re.search(p2, s) for p2 in DECL)
作り物 => ('㎐', '★双方が回る★', ['p3'], ['x'])    [x for x in XS if any(re.search(p3,x) for p3 in DECL)]
```

（`㎐` は ★㋐値を取る★ の畧。四つの形が ★現に出分けた★ ―― 出分けた種 = 4）

★下二本が v1 に無かつた形★ である。之を足して初めて 内包の網回りに ★口が開いた★。

## §八 ★自訴★

㋐ ★検出力を測つたつもりで 測つた形が偏つて居た★ ―― For 文の網回りのみ試し、内包の網回りを試さなんだ。
   ∴ v1 の「網が回る 0」は ★現に無い★ ではなく ★測定不能★ であつた。
   （幸ひ v1 の紙は未だ書いて居らぬ ―― 封じるべき前紙は無い。）
㋑ ★己の一族を母から外す定めを 本器に置き忘れた★ ―― E17 で條 二百七十五 を鋳りながら 己の次の器に掛け損ねた。
   母は 88→89 と己が増やした。而して ㋐ は 21 で不動ゆゑ ★判には触れて居らぬ★（之も実測で確かめた）。
㋒ ★v1 の §一 に刷つた語が 器の実装より広かつた★ ―― 「包む輪(for / comprehension)」と刷つたが、
   実は `ast.comprehension` 節点しか見て居らなんだ。★紙の語が 器より広い★ のは 紙の疵である。
㋓ 本弾は 同じ問ひに ★二度 器を當てた★（v1 / v2）。★器を変へた上での比較★ ゆゑ 條 百七十四（一字も変へず二度測れ）の
   形には当たらぬ ―― 而して ★何を変へたか（輪の辿りと負の対照のみ）★ を §四・§五 に明記して 之を補つた。

## §九 ★測れなかつた物★

1. 回る事が ★誤りを生むか否か★ ―― 本弾は形の帳のみ。是非は測つて居らぬ。
2. `ast.comprehension` / 内包本体 以外の輪の棲家（`while` の中の代入で回る形など）―― ★試して居らぬ形★ ゆゑ 測定不能。
3. 門の外 4 件が ★真に回らぬ★ か ―― 本器が ★未だ思ひ付いて居らぬ輪の形★ に居る可能性は 消せて居らぬ（㋐ と同じ疵の残り）。
4. 己の一族（order226_ 2 枚）を母から外した時の数 ―― 外して走らせ直して居らぬ ゆゑ 測定不能。
   （㋐ が 21 で不動である事から ★判に触れて居らぬ★ とは言へるが、★数そのもの★ は測つて居らぬ。）

## §十 ★條★

- ★二百七十六★ ―― ★0 の意味は 門と検出力を先に測つたか否かで決まる★。測つた上での 0 は「現に無い」、測らぬ 0 は「測定不能」。
- ★二百七十七★ ―― ★負の対照は 己が思ひ付いた形しか試さぬ★。「口が在る」と言へるは ★試した形について★ のみである。
  ∴ 二百七十六 は ★之で狭められる★ ―― 門と検出力を測つた上での 0 でも、★測つた形が偏つて居れば 現に無い とは言へぬ★。
- ★二百七十八★ ―― ★輪は二つの棲家を持つ★。内包の当たりは 其の親に `comprehension` を持つとは限らぬ
  （`elt` に居る当たりの親は ★内包本体★ である）。木を辿る器は ★節点の名でなく 意味で★ 拾へ。
- ★二百七十九★ ―― ★「器の疵に因る 0」と「現に無い 0」は 器を直して初めて分かれる★。直さぬ限り 双方は ★同じ 0★ に見える。

## §十一 ★型 8 項★

1. path = 上記悉く repo 相対（`scratch/ashigaru-third-3-12e9d4bd/…`）。
2. 完全 SHA = §十二 に列挙。
3. argv 逐語 = `python3 order226_e21_gate_and_power_v1.rule.py` / `python3 order226_e21_gate_and_power_v2.rule.py`（cwd = 本席 dir）。
4. raw の完全 SHA と行数 = §十二。
5. exit code = ★双方 rc=0★。本弾では NameError / SyntaxError を一つも出して居らぬ。
6. host/user/cwd = momizi-dx(third_pc) / hakudoukai / /home/hakudoukai/multi-agent-shogun。
7. 正負の対照 = §七 に 6 本（★4 種が現に出分けた★）＋ 現に無い path で `exists=False`。
8. 母数と測れなかつた数 = 母 88（v1）/ 89（v2）・㋐ 21・門 17・門外 4 ／ 測れなかつた数 = §九 の 4 件（★別値★）。

## §十二 ★物の帳★（作業樹 = WSL ext4・LF）

| file | wc -l | split 片 | bytes | sha256 |
|---|---|---|---|---|
| order226_e21_gate_and_power_v1.rule.py | 231 | 232 | 9,725 | 8d5424539f5051880720a5972602c9d08a15abd696f61065f8d20760353a0d27 |
| order226_e21_gate_and_power_v1.raw.txt | 104 | 105 | 5,163 | 3187de107de02978e6031aba06ae076dd9d7a11f0a336bb0e2cfa2b5e375bc96 |
| order226_e21_gate_and_power_v2.rule.py | 244 | 245 | 10,561 | f4ccd8824ff9f2bab0b88cb1cf99fdf689f3343f03f1fd8af9c65862fadbcaf9 |
| order226_e21_gate_and_power_v2.raw.txt | 125 | 126 | 6,333 | b3cd9b60364c98028cfe5c69f7eff0ca9148d492262af53e855c73e5c84e210f |

（`wc -l` = 改行の数／`split(chr(10))` 片 = 其の +1。床(32)）

## §十三 ★繰越★

- **E20** ―― E17 §五 の 6 件（母が全文）に ★現に 2 件以上 当たる母が在るか★。走が要るか否かを先に判ずる（★走 残 1 は温存・家老へ諮る★）。
- **E18** ―― ㊀ `order223_e14_relabel_v1.rule.py:170` ＋ ㊁ `unmeasurable26_status_triage_v1.rule.py:12` を直す。★家老の令を待つ（己から撃たぬ）★。
- **E22（本弾で生じた）** ―― 門の外 4 件が ★真に回らぬか★（§九-3）。輪の棲家を もう一つ二つ 作り物で試してから當てる。
- **E23（本弾で生じた）** ―― 己の一族を母から外した時の数（§九-4）。
- **E19** ―― `order196:24` の母が空である因。
- **E15** ―― 12 本の外の代入形 2 件が何を覆ふか（走 0 で何処まで言へるか）。
- 弾倉 = E2・E3・E4。

## §十四 ★三択語★

- ㋐ の内 ★内包で網が回る形★ = ★現に在る★（4 件・§六）。
- v1 が出した「網が回る 0」= ★測定不能★（器の疵に因る 0 であつた）。
- 門の外 4 件が真に回らぬか = ★測定不能★（試して居らぬ輪の形が残る）。
- 己の一族を外した時の数 = ★測定不能★（走らせ直して居らぬ）。

