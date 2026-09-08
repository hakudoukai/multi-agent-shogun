# order200 ―― ★E5(strict か)＋E6(何の床を見るか)＋E7(assert の前か後か) を ast 一発で★ ＋ o199 の打ち直し

## §零 紙の頭 (作法 七条目・HEAD/tree 令・條 百七十三)

- **何時** : as_of = `2026-09-09T05:18:37+09:00`
- **何を** : 対象樹 `/home/hakudoukai/a3/wt-bundle-fix4` の `*.py` **悉皆 1,484 枚** ＋ 己の席 dir の紙・規
- **幾つ讀んだか** : 規 2 本 (`order192…rule.py` / 己の `order200…rule.py`) ・ 紙 1 本 (`order192…md`) ・ config 5 名 (内 現に在る 1) ・ 樹の py 1,484

### 二つの樹を 分けて書く (床(2))

| 何の樹 | HEAD | branch | porcelain |
|---|---|---|---|
| **本 repo** `multi-agent-shogun` | `1ad4edfbadc69191183a42113e9979c3f91b7dbf` | `ashigaru-third-3/audit-framework-hermes-canon-revision-20260721` | raw3 header に **170 行** (本弾で一行も増やして居らぬ) |
| **対象樹** `/home/hakudoukai/a3/wt-bundle-fix4` | `47c8bc3b86613d7bd55cdfc062a46dccf8d81d1b` | `karo-third/a3-bundle-fix4-pin-20260908` | **6 行** (下に名指し) |

対象樹の porcelain 6 行 (條 百七十三 ―― HEAD は測つた物の外に在る分):
```
 M backend/tests/test_cmd004_cross_cutting_integration.py
 M tests/test_step_a4_handover_sheet.py
 M tests/test_step_q.py
 M tests/test_step_r_ui.py
 M tests/test_step_s3.py
 M tests/test_step_s4.py
```

### 走の帳

**製品走 0**・DB 0・network 0・書込 0・DDL 0。git は讀取動詞 (`rev-parse` / `status --porcelain`) のみ。
`ast` は **讀取** である ∴ 走の帳に数へて居らぬ。**走 残 0 は不変**。

---

## §一 令と 己が 分けた事

令の逐語:

> ★順 4 承認(order200・走 0・ast 一発)★=E5(xfail が strict か)／E6(何の床を見るか)／E7(assert の前か後か)
> ⇒★107 行中 60 行が測定不能から型へ落ちる★。★E5 が strict なら ―― ★『直つた事が赤に成る＝直しの向きが
> 逆に成り得る』を ★上へ回す材★ として明記せよ★★。★o199 の打ち直し(o183/o189 の併記表)を同じ紙に置くも
> 正(★前紙は一字も書換へず★)★。

**己は 先づ 数を分けた** (床(30) ―― 何を一つと数へたか):

| 何 | 群 | 数 | 何が落ちるか |
|---|---|---|---|
| **E6** | C `mark.skipif` | 20 (o192 の紙) | **型へ落ちる** |
| **E7** | D `pytest.skip(` | 40 (o192 の紙) | **型へ落ちる** |
| 小計 | | **60** | ← 令の「60 行」 |
| **E5** | E `mark.xfail` 9 ＋ F `pytest.xfail(` 5 | **14** | **型ではなく ★色★ の判じ** |
| 和 | | **74** | |

**己は前便で「107 行の内 60 行が型に落ちる」と書いた。之は C+D の 60 を指して居り E/F の 14 は含まぬ。**
**此処で分けた。** ―― 己の言ひ方が粗かつた分の自訴である。

---

## §二 ★正の対照★ ―― o192 の規 ★其の物★ を 一字も変へず 走らせた (條 o174)

己は第二段で「o192 の器を一字も変へず」と書きながら **★正規を 己の器へ 写して★ 走らせた**。
之は 條 o174 の破りである ∴ 第七段で **o192 の規 其の物** を `subprocess` で走らせ直した。

- o192 規 sha16 = `0b2cee9e453d8ed6` / wc 219 / split 220
- o192 の `ROOT` 逐語 = `/home/hakudoukai/a3/wt-bundle-fix4` ―― 己の `ROOT` と **同じ**
- 正規 8 本の逐語も **己の写しと一致** (raw2 に 8 行 悉く)

| 群 | **o192 の規が 今日 出した数** | **o192 の紙 (:35-42) の数** | 三択 |
|---|---|---|---|
| A `importorskip` | 3 / file 3 | 3 | **現に在る** (一致) |
| **B `mark.skip` 無条件** | **11 / file 9** | **23** | **合はぬ** |
| **C `mark.skipif` 条件付** | **32 / file 15** | **20** | **合はぬ** |
| D `pytest.skip(` | 40 / file 20 | 40 | **現に在る** |
| E `mark.xfail` | 9 / file 3 | 9 | **現に在る** |
| F `pytest.xfail(` | 5 / file 2 | 5 | **現に在る** |
| G `except ImportError` | 30 / file 25 | 30 | **現に在る** |
| H `collect_ignore` | 1 / file 1 | 1 | **現に在る** |

母数 8 / 一致 6 / 合はぬ 2。

### ★B と C の 和が 双方で 43★

- 紙 : B 23 ＋ C 20 = **43**
- 器 : B 11 ＋ C 32 = **43**

正規は排他である (`mark\.skip\s*[\(\)]|mark\.skip$` は `mark.skipif` に当たらぬ ―― `skip` の次が `i` ゆゑ
`\s*[\(\)]` にも `$` にも合はぬ)。∴ **和 43 = `mark.skip` で始まる行の総数** が 紙・器 双方で 同じ。

**∴ 紙と器の食ひ違ひは ★母数の差ではなく 分け方の差★ である。**
**何方が正か** ―― **器が正**。器は今日 走つて字を出した。紙は写しである (**條 百七十六** の第二例)。
**★但し 紙が書かれた刻に 樹が今と同じであつたかは 測定不能★** (己は当時の樹を持たぬ)。

---

## §三 ★E5 ―― xfail が strict か★

### ㋐ 床 (config)

| 名 | 三択 | 中身 |
|---|---|---|
| `pytest.ini` | **現に在る** | wc 2・逐語 `[pytest]` / `addopts = --ignore=reports`・`xfail_strict` **0 件** |
| `setup.cfg` | **現に無い** | ― |
| `pyproject.toml` | **現に無い** | ― |
| `tox.ini` | **現に無い** | ― |
| `conftest.py` (樹の根) | **現に無い** | ― |

- 樹の悉皆で `xfail_strict` = **0 件 / file 0**
- ★陽性対照★ `xfail` 語 = **20 件 / file 5** ∴ 器は効いて居る (條 o178)

**∴ `xfail_strict` の床は 現に無い ⇒ pytest の既定 (strict False) が効く。**

### ㋑ 行ごとの `strict=` を ast で (床(31))

ast が見た `xfail` の Call = **13**

| 形 | 数 |
|---|---|
| `strict=True` | **4** |
| `strict=False` | **4** |
| `strict` 無し | **5** |

**`strict=True` 4 件の在処** (ast の lineno = `@pytest.mark.xfail(` の行・逐語は其の継続行):

| path:行 (ast) | 逐語の在る行 |
|---|---|
| `backend/tests/test_v6_root_fix_fail_fixtures.py:132` | `:133 strict=True,` |
| `backend/tests/test_v6_root_fix_fail_fixtures.py:163` | `:164 strict=True,` |
| `backend/tests/test_v6_root_fix_fail_fixtures.py:181` | `:182 strict=True,` |
| `backend/tests/test_v6_root_fix_fail_fixtures.py:198` | `:199 strict=True,` |

**四件は悉く 同じ一枚 (`test_v6_root_fix_fail_fixtures.py`) に在る。**

`strict=False` 4 件 = `test_patient_members_list_red.py:285/321/341` ＋ `test_selection_http_matrix.py:340`
`strict` 無し 5 件 = `test_selection_http_matrix.py:367/402` ＋ `test_selection_http_matrix_live.py:147/183/190`

### ㋒ ★上へ回す材★ (家老の令の逐語に応ふ)

**★E5 は strict である ―― 但し 14 の内 4 だけが★**

1. **`strict=True` の 4 件は ★直したら 赤に成る★。** 令の逐語「直つた事が赤に成る＝直しの向きが逆に成り得る」
   が **現に立つ**。file 名は `..._fail_fixtures.py` ゆゑ「わざと失敗させる」意図が読めるが ―― **★其の 4 件に
   手を入れて 通る様にした者は 赤を受け取る★** 事に変りはない。**何処に其の断りが書かれて居るか** =
   同 file `:4` の註 (下記) のみ。**★註は 走らぬ★** ∴ 直す者が `:4` を讀まねば 向きは伝はらぬ。
2. **`strict=False` 4 件 ＋ `strict` 無し 5 件 = ★9 件★ は 裏返しの害を持つ。**
   o192 の紙 `:105` の逐語 ―― 「E/F xfail : 失敗を ★予期された失敗★ に変へる ⇒ strict でなければ
   ★直つた事★ も ★壊れた事★ も同じ色。」 **∴ 9 件は ★直しても 誰にも見えぬ★。**
3. **∴ 14 行は 二つに割れる ―― 4 は「直すと赤」・9 は「直しても見えぬ」・1 は Call に非ず (下記 §四)。**

---

## §四 ★母数の突合★ (床(4) ―― 何れの評価器から見た N か)

| 評価器 | 見た物 | 数 |
|---|---|---|
| 正規 `mark\.xfail` | 行 | **9** |
| 正規 `pytest\.xfail\s*\(` | 行 | **5** |
| 正規 和 | 行 | **14** |
| **ast** | `xfail` の **Call** | **13** |
| 差 | | **1** |

**差 1 の在処 (逐語)**:
```
backend/tests/test_v6_root_fix_fail_fixtures.py:4 | pytest.mark.xfail(strict=True) によりスイートは green を維持しつつ、
```
**★之は 三重引用の帯 (docstring) の中の 名の言及であり Call ではない★** ―― **條(21)㋑** と **床(24)㋑** の実例。
正規は字を見る ∴ 拾ふ。ast は木を見る ∴ 拾はぬ。**★双方 正しい★** ―― 見て居る物が違ふ。

### `xfail` 語の file 数が 三つ在る (床(4) の第二例)

| 打ち方 | file 数 |
|---|---|
| 前窓の己 (`/usr/bin/grep -rl xfail <樹>` ・除外無し) | **51** |
| 同じ打の内 `*.py` のみ | **5** |
| 今日の器 (`os.walk` ・除外 `node_modules/.git/.venv/venv/__pycache__` ・`*.py` のみ) | **5** |
| 内 除外 dir 配下に在つた物 | **0** |

**∴ 前窓の 51 は ★`.py` でない file (紙・記録等) を含む数★ であり 誤りではない ―― ★何れの評価器から見た N か
を 同じ行に書かなんだ★ のが 己の疵である。** 除外 dir の効きは **0** (即ち 51→5 の差は 拡張子のみで説明が付く)。

---

## §五 ★E6 ―― C `mark.skipif` 32 行が 何の床を見るか★ (ast・床(31))

母数 (ast の `skipif` Call) = **32**  ／ 二軸以上に掛かつた Call = **0** ∴ 下の和 = 母数 ぴたり

| 軸 | 数 |
|---|---|
| **㋐ file の在否** (`.exists()` / `_has_text` / `Path(`) | **24** |
| ㋑ platform (`os.name` / `'nt'`) | **4** |
| ㋒ env (`environ` / `getenv`) | **1** |
| ㋔ 道具の在否 (`_installed` / `ffmpeg`) | **2** |
| ㋕ secret の有無 (`_KEY` / `_URL`) | **1** |
| ㋖ 何れにも当たらぬ | **0** |

### ★第四段の軸は 粗かつた ―― 第八段で 打ち直した (條 百九十七・併記)★

第四段 (先に打つた粗い軸) は **「その他 31 / env 1」** を出した。`os.name == 'nt'` も `.exists()` も
「その他」へ落ちた ―― 己の `platform` 正規 (`platform|sys\.platform|darwin|win32|linux`) が
**`os.name == 'nt'` に当たらなんだ** ゆゑ。**★第四段は消して居らぬ★** (raw に残る)。

### ★上へ回す材★

**★C 32 行の条件が見る物の最大群 24 は ―― 床 (env/version/platform) ではなく ★物 (fixture file・道具) の在否★
である★。** 逐語の例:

- `tests/test_step_e.py:224` `not SHAHO_FULL.exists()`
- `tests/test_step_o_pipeline_integration.py:42,77,94,123,155,188` (**6 行**) `not SHAHO_FIXTURE.exists()` / `not KARTE_TAB_FIXTURE.exists()`
- `tests/test_step_s3.py:664,681,698,712,727,741` (**6 行**) `not (ROOT / 'frontend' / … ).exists()`
- `tests/test_video_processor.py:45,63` `not _ffmpeg_installed`

**∴ 24 行は ★床の違ひで飛んで居るのではない★ ―― ★物が置かれて居らぬ★ ゆゑ飛んで居る。**
**其の物を置けば 走る** ―― 之は o192 の逐語 `:103` (下に引く) とは **別の形** である。

> C mark.skipif : 条件 (OS/env/version/flag) が真の床でのみ飛ぶ ⇒ ★或る床でのみ★ 緑が嘘に成る。

**加へて config 側の逃げ道が 現に在る**: `pytest.ini:2` 逐語 `addopts = --ignore=reports`
―― o192 が「除外」として名指した類の物が **現に一つ 在つた**。

---

## §六 ★E7 ―― D `pytest.skip(` 40 が assert の前か後か★ (ast)

母数 (ast の `pytest.skip` Call・**関数体の中**) = **40** ―― o192 の紙の 40 と **一致**

| 形 | 数 | 何を意味するか |
|---|---|---|
| **assert の ★前★** (検め前に降りる) | **25** | 一つも検めずに降りる |
| **assert 無し** (検め 0) | **13** | 其の関数に検めが無い (fixture / helper が多い) |
| **assert の ★後★** (検め了へて降りる) | **2** | 検め了へて降りる ―― **半端でない** |
| assert の ★間★ (半端な検め) | **0** | ― |

**★母数 40 が ぴたり ∴ 関数体の外 (module 直下) に在る `pytest.skip(` は 0★** (器の断り書きが空振りした ―― 之も自訴)

「assert の後」2 件 = `backend/tests/test_meisai_receipt.py:465,480`
「assert 無し」13 件の内 `def` が `_skip_if_*` / `pg_dsn` / `prod_db` / `live_db` の形 = **8** (fixture・helper)

**∴ o192 の逐語 (下に引く) は ―― 40 の内 ★25★ に当たる。**

> D pytest.skip( : 試験の途中で飛ぶ ⇒ ★assert に達する前★ に緑 ―― 半端な検めが全検めに見える。
**残る 15 の内 13 は ★検めが元より無い関数★ (fixture/helper) ・2 は ★検め了へて降りる★。**

---

## §七 ★o199 の打ち直し★ (家老 條 百九十七・令の明示承認)

order199 で **A3 = −7 が正**・**−9 は literal の写し** と定まつた (o180 が `len()` から `%d` で計算)。
∴ −9 を持つ紙に 條 百九十七 が掛かる。**★前紙は 一字も 書き換へて居らぬ★** ―― 此処に **併記表** を置く。

### 導出で書く (己が鋳た 條 百七十四 ―― 列挙で書けば 漏れが古い儘 生き残る)

**導出の定め** : 「己の席 dir (`scratch/ashigaru-third-3-12e9d4bd/`) の `*.md` と `*.rule.py` を悉皆に当て、
下の三つの字を含む物を **機械で** 挙げる」

| 字 | 度数 | 物 |
|---|---|---|
| `A3 = ★-9★` (紙の形) | 4 | `order183_frame_precision_v1.md` ×1 / `order189_falsepos_cure_v1.md` ×1 / `order199…rule.py` ×1 / `order200…rule.py` ×1 |
| `A3 = -9` (規の literal 形) | 15 | `order199…md` ×6 / `order182…rule.py` ×1 / `order183…rule.py` ×1 / `order199…rule.py` ×6 / `order200…rule.py` ×1 |
| `\| A3 \| −7 \| −7 \| −9 \|` (o185 の食ひ違ひ表) | 4 | `order185_karo159_additivity_v1.md` ×1 / `order189…md` ×1 / `order199…rule.py` ×1 / `order200…rule.py` ×1 |

**★打ち直しの対象 = 上の三行の内 ★紙 (`*.md`)★ に在る物★** ―― 導出すると:

| 紙 | 在る形 | **正しい数** | 何故 |
|---|---|---|---|
| `order183_frame_precision_v1.md` | `A3 = ★-9★` | **A3 = −7** | o183 の規 `:309` は `A3 = -9` を **literal** で刷る (左に format 子 0 個)。計算は o180 が `%d` で行ひ **17/24 ⇒ −7** |
| `order189_falsepos_cure_v1.md` | `A3 = ★-9★` ＋ o185 表 | **A3 = −7** | 同上 (o183 からの写し) |
| `order185_karo159_additivity_v1.md` | o185 表 `| A3 | −7 | −7 | −9 |` | **三欄とも −7** | 第三欄の −9 が写し ―― 之が「隊の帳に残る唯一の未決の数」であつた |
| `order199_root_rules_reconcile_v1.md` | `A3 = -9` ×6 | **書換不要** | ★之は「−9 が写しである」と述べる為に −9 を引いた紙★ ∴ 打ち直しの対象に非ず |

**∴ 打ち直しを要する紙 = ★3 枚★ / 引いただけの紙 = ★1 枚★ / 規 = ★3 本 (o182・o183・o199)★。**
**★何れも 本弾では 一字も 書き換へて居らぬ★** ―― 併記のみ (令の逐語「前紙は一字も書換へず」)。

---

## §八 己の疵 (自訴)

1. **★第二段で「o192 の器を一字も変へず」と書きながら 正規を写して 己の器で走らせた★** (條 o174 の破り)。
   第七段で o192 の規 其の物を走らせて直した。**★而して 直した結果 紙との食ひ違ひ 2 件が出た★**
   ―― 即ち **己が写しで済ませて居たら B/C の食ひ違ひは 見付からなんだ**。
2. **★第四段の軸が粗く `os.name == 'nt'` (4) と `.exists()` (24) を「その他」へ落とした★**。
   第八段で軸を細かくして打ち直した (第四段は消さず)。
3. **★第八段の「strict=True の在処」の打ちが粗く `zip(..., strict=True)` と `Path.resolve(strict=True)` まで拾つた★**。
   之は `xfail` の strict ではない。**ast (第三段) の 4 件が正**。
   ―― **★同じ keyword 名が 別の関数の引数として 現に居る★** (下記 條 百七十八)。
4. **★第五段の器に「module 直下の物は落ちる」と断つたが 母数 40 が ぴたり ∴ 落ちた物は 0 であつた★**。
   断り書きが空振りした ―― 断りは残すが **「落ちた数 = 0」を同じ所に書く**。
5. **★前便で「107 行の内 60 行が型に落ちる」と書き E/F の 14 を含めぬ事を明記しなんだ★** (§一で分けた)。

---

## §九 見込みの外れの帳 (作法 四条④・條 o179-a・條 o180)

| 度 | 何を見込んだか | 実測 | 外れ | 向き |
|---|---|---|---|---|
| 一 | (o180 の帳) | | 外れ | 少なく |
| 二 | 〃 | | 外れ | 少なく |
| 三 | 〃 | | 外れ | 少なく |
| 四 (o199) | A3 = −7 | −7 | **外れず** | ― |
| **五 (本弾)** | **「`xfail_strict` が 0 ∴ ★悉く★ 非 strict」** | **`strict=True` が ★4 件★** | **外れ** | **★少なく★** |

**★之を「癖が消えた」と読んで居たら 五度目で 戻つた★** ―― 家老 新條A (一度の観測から普遍を鋳るな) の実例。
**四度目が外れなかつたのは ★一度の対★ に過ぎず 癖の消滅ではなかつた。**

**外れの因 (己で名指す)**: 己は **床 (config) を見て 行 (ast) を見ずに** 見込みを字にした。
**★床が無い事は 行に無い事を意味せぬ★** ―― `xfail_strict` は **既定を変へる** 鍵であり、
`strict=True` は **一行ごとに 既定を上書きする** 鍵である。**二つは 別の階に在る。**

---

## §十 母数と 測れなかつた数 (型 8 項⑧)

| 何 | 母数 | 測れた | **測れなかつた** | 何故 |
|---|---|---|---|---|
| 樹の py | 1,484 | 1,484 | 0 | ― |
| o192 の 8 群 | 8 | 8 | 0 | ― |
| 群の数の一致 | 8 | 一致 6 / 合はぬ 2 | ― | ― |
| E/F の Call | 14 (正規) | ast 13 | **1** | 三重引用の帯の中の言及 ∴ Call に非ず |
| C の Call | 32 | 32 | 0 | ― |
| D の Call | 40 | 40 | 0 | ― |
| **紙 o192 が書かれた刻の樹** | ― | ― | **★測定不能★** | 己は当時の樹を持たぬ ∴ B/C の食ひ違ひが「写しの誤り」か「樹の変化」かは **落ちて居らぬ** |
| **−9 の真の初出** | ― | ― | **★測定不能★** (o199 から繰越) | mtime が紙の方が後 ∴ 書換への証 (條 百七十五) |
| **A2 = −6 を計算する規** | ― | ― | **★測定不能★** (o199 から繰越) | 己が讀めた 9 本に無し |

---

## §十一 三択語で結ぶ (床(8))

1. `xfail_strict` の床は **現に無い** (樹の悉皆 0・陽性対照 20 件で器は効いて居る)
2. `strict=True` の行は **現に在る** ―― **4 件・悉く `test_v6_root_fix_fail_fixtures.py`**
3. `strict=False` ＋ `strict` 無しの行は **現に在る** ―― **9 件**
4. C `mark.skipif` が見る物の最大群は **現に在る** ―― **file の在否 24 / 32**
5. C が env を見る物は **現に在る** ―― **1 件のみ**
6. D `pytest.skip(` が assert の前に降りる物は **現に在る** ―― **25 / 40**
7. D が assert の間 (半端な検め) で降りる物は **現に無い** ―― **0 件**
8. o192 の紙と器の食ひ違ひは **現に在る** ―― **B と C の 2 群** (和 43 は一致)
9. 紙 o192 が書かれた刻の樹は **測定不能**
10. config 側の逃げ道 (`addopts = --ignore=reports`) は **現に在る** ―― **1 件**

---

## §十二 條 (本弾で鋳た ―― 「斯く在つた」と書く・家老 新條A)

### ★A3 條 百七十八★

> **★同じ keyword の名が 別の関数の引数として 現に居る★ ―― 名だけで数へるな。**
> 斯く在つた ―― `strict=True` を字で当てたら **16 行**出たが、其の内 `xfail` の物は **4 行**であり、
> 残りは `zip(…, strict=True)` (python 3.10 の引数) と `Path.resolve(strict=True)` であつた。
> **∴ 引数を数へる時は ★親の Call を ast で名指せ★。字で当てるなら ★親の名を 同じ行に書け★。**
> (之は 床(12)「呼出を悉皆に当てる時 pattern に引数名を含めるな」の **裏** である ―― 引数名だけで取ると
> 別の関数の同名引数を拾ふ。)

### ★A3 條 百七十九★

> **★床の設定が無い事は 行の指定が無い事を意味せぬ★ ―― 既定を変へる鍵と 一行ごとに既定を上書きする鍵は 別の階に在る。**
> 斯く在つた ―― `xfail_strict` は config で **0 件**であつたが、`strict=True` は行で **4 件**在つた。
> **∴ 「床が無い ⇒ 悉く既定」と書く前に ★行を ast で当てよ★。**

### ★A3 條 百八十★

> **★写しで済ませた器は 写した分だけ 食ひ違ひを 隠す★。**
> 斯く在つた ―― 己が o192 の正規を **写して** 己の器で走らせた時は「合はぬ」は見えず、
> o192 の規 **其の物** を走らせて初めて B 11/23・C 32/20 の食ひ違ひが出た。
> **∴ 條 o174 「器を一字も変へずに二度測れ」の ★一字も★ は ―― ★器を丸ごと呼べ★ の意である。**

---

## §十三 型 8 項 (軍師third REVISE 291807 への応へ)

| 項 | 何 |
|---|---|
| ① repo 相対 path | 本紙・器・raw 悉く `scratch/ashigaru-third-3-12e9d4bd/` 配下 (下表) |
| ② 完全 SHA 64 桁 | 下表 |
| ③ argv 逐語 | raw3 header `argv = ['/usr/bin/python3', '/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-3-12e9d4bd/order200_escape_shape_ast_v1.rule.py']` |
| ④ raw の完全 SHA と行数 | 下表 |
| ⑤ exit code | **0** (raw / raw2 / raw3 悉く) |
| ⑥ host/user/cwd | raw3 header に (host / user / uid / cwd) |
| ⑦ 正負の対照 | §十四 |
| ⑧ 母数と測れなかつた数を別値 | §十 |

---

## §十四 ★正負の対照★ (型 8 項⑦・條 o178)

| 何を疑つたか | ★否★ の打 | ★是★ の打 (陽性対照) | 判じ |
|---|---|---|---|
| `xfail_strict` が 0 なのは器の疵か | 樹の悉皆 `xfail_strict` = **0** | 同じ打で `xfail` = **20 件 / file 5** | 器は効いて居る ∴ **0 は真** |
| B/C の食ひ違ひは己の写しの疵か | 己の器 B 11 / C 32 | **o192 の規 其の物** も B 11 / C 32 | 己の写しは正しい ∴ **紙と器が合はぬ** |
| 51 file と 5 file の差は除外 dir か | `os.walk` (除外あり) = **5** | `/usr/bin/grep -rl` (除外なし) = **51** / 内 `.py` = **5** / 内 除外 dir 配下 = **0** | **差は拡張子で説明が付く** ∴ 除外 dir の効きは 0 |
| D の母数が関数体の外で落ちるか | 器に断り書き | ast の母数 **40** = o192 の紙 **40** | **落ちた物は 0** |
| `strict=True` 16 行は悉く xfail か | 字で 16 行 | ast の `xfail` Call の keyword = **4** | **12 行は別の関数の同名引数** |

---

## §十五 物の帳

| path (repo 相対) | sha256 (64 桁) | wc | split | bytes |
|---|---|---|---|---|
| `scratch/ashigaru-third-3-12e9d4bd/order200_escape_shape_ast_v1.rule.py` | `30c78efc29f0e07ddfc54bc39f48f1a775c86c2fb6ff4c2c83623428759d2019` | 366 | 367 | 21,484 |
| `scratch/ashigaru-third-3-12e9d4bd/order200_escape_shape_ast_v1.raw.txt` | `2c290a9c91a5a4875b917fc79a239e6744b4c88a0b44177c77b518430f1e3b7d` | 178 | 179 | 14,660 |
| `scratch/ashigaru-third-3-12e9d4bd/order200_escape_shape_ast_v1.raw2.txt` | `9eb1cb53561b769ad923841f72ded6ee1251bd365d5a41b940e7530ab4847bbb` | 378 | 379 | 36,852 |
| `scratch/ashigaru-third-3-12e9d4bd/order200_escape_shape_ast_v1.raw3.txt` | `88c902319ab00db6a3b5e4f4b416a099b4b4488030b5f2ff93f76f0396670696` | 414 | 415 | 39,647 |
| `scratch/ashigaru-third-3-12e9d4bd/order200_escape_shape_ast_v1.md` (本紙) | 下の完了便に記す | 下記 | 下記 | 下記 |

**行数は `wc -l` (改行数) と `split(chr(10))` 片数 の 併記** (床(32))。差は常に 1。

**★raw は三本とも残す★** ―― raw1 = 第一〜六段 (粗い軸を含む) / raw2 = ＋第七段 / raw3 = ＋第八段。
**★前の raw を 消して居らぬ★** (家老 條 百九十七 ―― 直した器の前の数も 遡れる様に)。

---

## §十六 枝

- ref : `a3/order200-ast-escape-typing-20260909`
- 鋳り方 : **別 index → `commit-tree` → `update-ref`** (本 repo **HEAD 不動**・総監督裁 `hs_00c5a537` の範)
- tip / remote 一致 : 完了便に記す (己で當て直す ―― 家老 條 二百)

---

## §十七 繰越 (次弾の材)

| # | 何 | 何故 落ちて居らぬか |
|---|---|---|
| 1 | **紙 o192 の B/C を 打ち直す** | 器が正と判じたが **紙が書かれた刻の樹は測定不能** ∴ 「写しの誤り」か「樹の変化」かが割れて居らぬ |
| 2 | **B 11 行の中身** | 悉く `tests/integration/phase5/` の 無条件 skip (reason に「Phase 6 Step 6-2 Phase 2: 残N件」)。**★N の和★** を数へれば 「隠れて居る試験の数」が出る (箱二 X10 と同じ的) |
| 3 | **G `except ImportError` 30 行** | E5/E6/E7 の外 ∴ 本弾では型に落として居らぬ |
| 4 | **A `importorskip` 3 行** | 同上 |
| 5 | **`addopts = --ignore=reports` が落とす試験の数** | **走 0 では測定不能** (collect を要する) ∴ 箱二 (手の外) |
| 6 | o199 繰越 : A2 = −6 の規 / −9 の真の初出 / A6 = −4 が紙に無し | 悉く **測定不能** の儘 |
