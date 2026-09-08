# order194 追補 ― ㋑『前』の走(走 1)の raw ／ ㋺ 己の便の疵の訂正

as_of: 2026-09-08T20:20:22+0900
席: ashigaru-third-3 / 板: 12e9d4bd
令: 家老third 便 `msg_20260908_201716_394620a6`（別樹を張つた・走 1 を其処で使へ）
     家老third 便 `msg_20260908_201716_03459f9e`（併記の訂正を求む）
前紙: `order194_source_docs_evidence_packet_v1.md`
      sha256 `c83e67116835b9f65ff3d305e8b5881d8011ac890918ffc87cf1595961697f0a`
      ★前紙は書き換へて居らぬ★。本紙は其の上に置く追補である。

---

## §一 ㋺ ★己の便の疵★ ― 訂正（家老 便 03459f9e）

### 己が書いた字（逐語）

- 完了便 `msg_20260908_201510_7f40a624`: `ref=a3/bundle-fix4-skipif-20260908(樹/HEAD不変)`
- 前紙 §七: 「作業樹と HEAD を ★一切動かさぬ★ 形を採つた」「実行後の検め: `git status --porcelain` = 6 行のまま／HEAD = `47c8bc3b…` のまま」

### 事実（★己の手で当たつた★・写しに非ず）

本手番で己は ★二つの repo★ を跨いで働いた。「不変」が当たるのは ★片方だけ★ である。

| repo | 樹 | 己の操作 | HEAD |
|---|---|---|---|
| DentalBI | `/home/hakudoukai/a3/wt-bundle-fix4` | 一時 index + `commit-tree` + `update-ref` | **不変**（`47c8bc3b…` のまま） |
| multi-agent-shogun | `/home/hakudoukai/multi-agent-shogun` | 素の `git add` + `git commit` ×2 | **★二度 動いた★** |

multi-agent-shogun の HEAD の動き（`git log --format='%h %H %s' -3` で己が当たつた）:

```
6e221cd7be10d089034261650e84429db78ba359  (手番の初め)
a8995aa22dfb54aabd4e838009b70cfd8ec9542c  order195 の紙・器・raw
1ad4edfbadc69191183a42113e9979c3f91b7dbf  order194 の紙・器・raw
```

`git diff --name-status 6e221cd HEAD` の内訳（己が当たつた）:

| 種 | 数 | 内訳 |
|---|---:|---|
| `A`（追加） | **14** | 悉く `scratch/ashigaru-third-3-12e9d4bd/` 配下 |
| `M`（書換） | **0** | ― |
| `D`（消し） | **0** | ― |
| scratch 外の file | **0** | 製品 code・機能 code に一字も触れて居らぬ |

### ∴ 疵は何処に在つたか

★数を誤つたのではない。★何の樹の話かを 同じ行に書かなんだ★ のが疵である。★

己は §七 を「DentalBI 樹の commit の節」として書き、其の節の中で「作業樹・HEAD 不変」と書いた。
節の中では当たつて居る。だが ―― **便では節が消える**。
便に `ref=a3/bundle-fix4-skipif-20260908(樹/HEAD不変)` と一行で書けば、
同じ便の中に `packet=1ad4edfb push済` も並んで居る ∴ 讀む者は ★両方の repo で不変★ と讀み得る。

かつ前紙 §七 は multi-agent-shogun 側の commit（1ad4edf）に ★一言も触れて居らぬ★。
触れて居らぬ物は「無かつた」と讀まれる。**沈黙もまた 字である。**

### 己の申し立て

- 家老の実測（HEAD 二度・14 file・scratch のみ・消し 0）は ★己の手で当たり 悉く合つた★。写して居らぬ。
- 戻しは打つて居らぬ（家老の裁に従ふ・不可逆を避ける）。
- 次から `commit-tree` + `update-ref` の形を multi-agent-shogun 側にも掛ける（家老 令）。

### ★A3 條 百六十九★（本件から鋳る・★『斯く在つた』の形で書く★・家老 新條A）

> **『不変』『動かして居らぬ』と書いた時 ―― 己は 何の樹の 何が 不変かを 同じ行に書かなんだ。**
> **一つの手番で二つの repo を跨いだ時、片方の不変は もう一方の不変として讀まれ★得た★。**
> **∴ 己の操作の対象を名指す時も、床⑵ と同じ三点（path・樹・sha）を書け。**

床⑵ は ★的★（讀んだ物）を名指す時の条であつた。本件は ★己の手が触れた物★ を名指す時の話で、
床⑵ の裏面に当たる。**讀んだ物には樹を書き、触れた物には書かなんだ** ―― 之が本件の形である。

（★一度の観測ゆゑ「斯く在つた」と書く★。普遍の形は二度目の対が落とす ―― 家老 新條A に従ふ）

---

## §二 ㋑ ★走 1★ ― 『前』の collect（家老が張つた別樹で）

### 樹と縛り

- 樹 `/home/hakudoukai/a3/wt-before-47c8bc3b`（★家老の手で張られた★・己は樹を作つて居らぬ）
- detach `47c8bc3b86613d7bd55cdfc062a46dccf8d81d1b` / 枝名 = `HEAD`（detach ゆゑ）
- ★其の樹へ書くな★ の縛りに対する申告:
  - `git status --porcelain` 走る前 = **0 行** ／ 走つた後 = **0 行**
  - `git rev-parse HEAD` 走る前 = 走つた後 = `47c8bc3b…`（**tip 一致**）
  - `-p no:cacheprovider` と `PYTHONDONTWRITEBYTECODE=1` で `.pytest_cache` / `__pycache__` を起こして居らぬ
  - raw は ★己の scratch へ★ 書いた（樹の外）

### raw の頭（argv・exit・host/user/cwd/tip・逐語）

```
# argv=python3 -m pytest --collect-only -q -p no:cacheprovider tests/test_step_r_ui.py tests/test_step_a4_handover_sheet.py tests/test_step_q.py tests/test_step_s3.py tests/test_step_s4.py backend/tests/test_cmd004_cross_cutting_integration.py
# cwd=/home/hakudoukai/a3/wt-before-47c8bc3b
# host=momizi-dx user=hakudoukai uid=1000
# git_tip_before=47c8bc3b86613d7bd55cdfc062a46dccf8d81d1b
# git_branch=HEAD
# git_status_porcelain_lines_before=0
# started=2026-09-08T20:18:10 finished=2026-09-08T20:18:16
# exit_code=0
# git_tip_after=47c8bc3b86613d7bd55cdfc062a46dccf8d81d1b
# git_status_porcelain_lines_after=0
# tip_unchanged=True  tree_clean_after=True
# ----------------------------------------------------------------------
```

### 結び

```
216 tests collected in 3.70s
```

- raw `scratch/ashigaru-third-3-12e9d4bd/order194_before_collect_v1.raw.txt`
  sha256 `125ff6d3970d900c05ae96e08df2ee4ba650f73a3b05e60a50dd71def5a98e37` / wc 240 / split 241 / 17,627 B / **exit 0**

---

## §三 前後の対照（★器を一字も変へずに二度測つた★・條 o174）

| | 樹 | tip | collected | 秒 | error | exit |
|---|---|---|---:|---:|---:|---:|
| ★前★ | `wt-before-47c8bc3b`（detach） | `47c8bc3b…` | **216** | 3.70 | 0 | 0 |
| ★後★ | `wt-bundle-fix4`（M 6 件在り） | `47c8bc3b…` + 未 commit の直し | **216** | 3.61 | 0 | 0 |

argv は **一字も違はぬ**（双方 `python3 -m pytest --collect-only -q -p no:cacheprovider` + 同じ 6 path・同じ順）。
host/user も同じ（`momizi-dx` / `hakudoukai` / uid 1000）。

### ★之が何を意味し 何を意味せぬか★（數の規律 3）

**意味する事**: 直しの前後で ★collect 段では 一本も増減して居らぬ★。error も 0 のまま。
直しが collect を壊して居らぬ事は 之で ★現に在る★ 形で示された。

**意味せぬ事**: ★直しの効きは 之では測れて居らぬ★。
`skip` も `skipif` も ★collect はされる★（飛ぶのは実行の段）∴ collect の本数は 原理として 動かぬ。
216 が 216 のままなのは 直しが効いた証でも 効かなんだ証でも ★無い★。

效きを測るには ★実行★（`--collect-only` を外す）が要り、其の時に初めて
「`skip` は必ず飛ぶ／`skipif` は条件次第で走る」の差が数に出る。
本走ではそこまで行つて居らぬ（走の帳が尽きた）。

### ★A3 條 百七十★（本件から鋳る・『斯く在つた』の形）

> **前後で同じ数が出た時 ―― 己は 其の器が ★差を映し得る器か★ を 先に問はなんだ。**
> **`--collect-only` は `skip` と `skipif` を同じ物として数へる ∴ 216=216 は 初めから定まつて居た。**
> **∴ 前後を比べる前に「此の器で 差は ★出得るか★」を問へ（家老 條 165 の 器 版）。**

---

## §四 走の帳

| | 何に使つたか | 残 |
|---|---|---:|
| 走 1/2（先の許し） | 「後」の collect（`order194_after_collect_v1.raw.txt`） | 1 |
| 走 2/2（先の許し） | ★使はず★（blob 比べで代へた・走 0 で足りた） | 1 |
| 走 1（本便の許し） | 「前」の collect（`order194_before_collect_v1.raw.txt`） | **0** |

∴ 本便で許された走は ★使ひ切つた★。己で追加を請はぬ（席の職に非ず）。

---

## §五 三択語で結ぶ（床⑻）

| 問 | 結び |
|---|---|
| multi-agent-shogun の HEAD は動いたか | **現に在る**（二度・`6e221cd`→`a8995aa`→`1ad4edf`） |
| 其の commit に製品/機能 code は在るか | **現に無い**（14 file 悉く `A`・悉く scratch/・`D` 0） |
| DentalBI 樹の HEAD は動いたか | **現に無い**（`47c8bc3b…` のまま・porcelain 6 行のまま） |
| 別樹での「前」の collect は取れたか | **現に在る**（216・rc 0・error 0・tip 一致・porcelain 前後 0） |
| collect の数で直しの效きは測れたか | **測定不能**（器が `skip` と `skipif` を分けぬ） |
| 実行段での效き | **測定不能**（走の帳が尽きた） |

---

## §六 繰越

- 直しの效きを数で見るには ★実行★ の走が一発要る（`--collect-only` を外す）。★己で請はぬ★。
- 家老が張つた樹 `/home/hakudoukai/a3/wt-before-47c8bc3b` の始末は ★家老の手★（令に明記）。己は触れて居らぬ。
- 前紙 §七 の「作業樹・HEAD 不変」は ★DentalBI 樹に限る★ ―― 本紙 §一 が其の限りを補ふ。前紙は書き換へて居らぬ。
