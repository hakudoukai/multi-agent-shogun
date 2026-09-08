# order194 追補 其の二 ―― 己が自訴した二つの穴を埋めた紙（走 0・讀取のみ）

## §零 頭（何時・何を・幾つ 讀んだか）

- as_of: 2026-09-08T21:35:57+0900
- 席: ashigaru-third-3 ／ 板 12e9d4bd ／ 令 = 総監督 WORK-PULL（「板の自分owner最上段…22:00 夜間休止までに区切りを commit し産出を1行」）
- 何を埋めたか = 前紙 `order194_source_docs_evidence_packet_v1.md`（sha256 `c83e67116835b9f65ff3d305e8b5881d8011ac890918ffc87cf1595961697f0a`）§十二 の ★己の自訴 2 件★
  - 自訴1 = `reports/` 82 行の内訳を ★数へて居らぬ★
  - 自訴2 = walk 漏れ 1,360 の内訳を ★分けて居らぬ★
- 的の樹 = `/home/hakudoukai/a3/wt-bundle-fix4`（DentalBI 樹・remote `hakudoukai/hakudokai-dev.git`）
- 測つた時の HEAD = `47c8bc3b86613d7bd55cdfc062a46dccf8d81d1b` ／ 作業樹 porcelain = 6 行（★汚れ在り★）
- 紙の在処 = multi-agent-shogun 樹（別 repo）。★二つの樹を跨ぐ ∴ 何れの樹の話かを各行に書く（A3 條 百六十九）★
- 讀んだ数（今走） = walked_files **16,972** ／ scanned_text_files **15,632** ／ 讀めなんだ **1,340**
- 走行 0（製品を走らせて居らぬ）・DB 0・書込は `scratch/ashigaru-third-3-12e9d4bd/` の内のみ・本番 code へ一字も書いて居らぬ

## §一 自訴2 を埋む ―― walk 漏れ 1,340 の内訳（★器が返した例外の型★・推し量りに非ず）

母数 = walked 16,972 枚。utf-8 で讀めなんだ = **1,340 枚**。

| 例外の型 | 枚 |
|---|---:|
| UnicodeDecodeError | 1,340 |

★型は 一種のみ★ ―― 権限（PermissionError）も IsADirectoryError も **現に無い**。
∴ 前紙が「binary / 権限 / decode」の三つに分かれ得ると書いたのは ★己の推し量り★ であり、器は **decode 一種** を返した。

拡張子ごと（UnicodeDecodeError 1,340 の内訳・器の出力そのまま）:

```
      .png             751
      .pdf             258
      .xlsx            173
      (拡張子なし)          41
      .webm            24
      .docx            21
      .zip             20
      .txt             15
      .csv             14
      .jpeg            7
      .xml             4
      .md              3
```

合計 = 751+258+173+41+24+21+20+15+14+7+4+3 = **1,331**。★1,340 との差 9 は 上位 12 種のみ刷つた事による★（器は上位のみ print）。
∴ 「拡張子の全内訳」は 本走では **測定不能**。型の内訳（1,340 悉く UnicodeDecodeError）は **現に在る**。

`.txt` 15 枚・`.csv` 14 枚・`.md` 3 枚が decode で落ちて居る ―― ★text の顔をして utf-8 でない file が 32 枚 現に在る★。
之は「binary ゆゑ落ちた」ではない ∴ 前紙の言ひ方（binary/権限/decode）では捉へられなんだ物である。

## §二 自訴1 を埋む ―― `reports/` 82 行の内訳

前紙は `reports/` を「写しの山ゆゑ母数から ★名指しで除外★」した（床⑼）。其の除外した中身を 此処で数へる。

- reports_files = **15 枚** ／ reports_lines = **82 行**
- 82 行 ★悉く BOUNDED★（識別子境界形 `(^|[^A-Za-z0-9_])source_evidence_ids([^A-Za-z0-9_]|$)` に当たる）・UNBOUNDED = **0**

| rel（樹 = wt-bundle-fix4） | sha256 64 桁 | wc | split | 当たり行 |
|---|---|---:|---:|---:|
| `reports/_tmp_touyaku_t3_v4/treatment_validation.py` | `cebe5c0097ffc0503cc5e6e483f89070de9baa351a5e8fb0c0fb35ea58c22c8c` | 5545 | 5546 | 1 |
| `reports/_tmp_touyaku_t3_v5/backend/api/treatment_validation.py` | `65fad6b31b777ebebcf94b23ce8462b80a99482cb237c3011eb11e4b56b19dba` | 5568 | 5569 | 1 |
| `reports/v6-calculation-engine-redesign-visit-context-plan-20260628.md` | `cafbbd467b9ab4cc515a03f7d1cf0a341efe8a15f29f318819a5065791ec1ce9` | 495 | 496 | 3 |
| `reports/v6-ce-browser-positive-debug-20260629.json` | `b034678e97f530ecd04bd6b84f49288d735aab045377f35671bcc07b7cbc0fb4` | 288 | 289 | 1 |
| `reports/v6-ce-requirements-gate-preflight-20260629.json` | `20dc45a378ff39ee0dd54e8137616c96549533d67cc9bb37d8b6b551ccd89b5b` | 938 | 939 | 4 |
| `reports/v6-ce-requirements-gate-preflight-20260629.md` | `8cf32cbfe88db92cd9b1824473b4b88008a137086280d8525ab9736b1774d4b7` | 636 | 637 | 1 |
| `reports/v6-core-build-up-direct-resin-ui-save-payload-db-e2e-20260628.json` | `c7bc63a8af1c73dbee3e424776247bd415f64d059d7fa7cf84496d5726111e65` | 1221 | 1222 | 6 |
| `reports/v6-core-build-up-ui-save-payload-db-e2e-20260628.json` | `2d39d6fd87712770421a5b1fd74ef4b8766a68306206ba040413bea03f5ab464` | 737 | 738 | 1 |
| `reports/v6-nigo-fact-rule-row-contract-20260628.md` | `bd76f801c9ba3ef9fb62df2dfbe56cd3725f24954b3b84d268621b5e0a480ed9` | 119 | 120 | 3 |
| `reports/v6-phase2d-code-evidence-for-hermes-20260628.md` | `edfed1ad7f8af4eaf876d7ef3f0334e10bfbabef9755e0137586853594c2c9d5` | 1127 | 1128 | 19 |
| `reports/v6-phase2d2-clean-evidence-packet-20260628.md` | `7241dbfeba307360d31ace412bb6aa6ad456d48b3333ea2a92504fc186d5f4a8` | 862 | 863 | 23 |
| `reports/v6-phase2d2-nigo-api-response-shape-20260628.json` | `3de7e1df3a66e763d2d59e1f0a03b6d43e0e6b155c629813f71e1687a0965bb8` | 70 | 71 | 1 |
| `reports/v6-r8-init-visit-save-temporal-probe-20260629.json` | `2beee0a833ad3194fdbf74d37226e2da6d1ad47671249a7f7b8592a25100f68b` | 1213 | 1214 | 12 |
| `reports/v6-saho-debug-20260629.json` | `553d90cbbe9bc34f124d942c8bec66258e44c4c7fff3ca26470947c18d161a04` | 219 | 220 | 1 |
| `reports/v6-srp-master-backed-save-e2e-20260629.json` | `c9b3f513dd702d74f4e5829dad20db17b7336b5d3db3a3dbb5dea8a8360e9b50` | 696 | 697 | 5 |

逐語 82 行は raw に悉く収めた（`order194_gap_fill_v1.raw.txt`）。紙には ★型の別★ のみ記す:

- `source_evidence_ids=[...]` の形（python の kwarg）と `"source_evidence_ids": [...]` の形（json の鍵）の二種が在る。
- `reports/_tmp_touyaku_t3_v4/treatment_validation.py` と `.../v5/backend/api/treatment_validation.py` は ★.py の写し★ ―― 即ち reports/ の中に ★本番 code の複製が 2 枚 現に在る★。
- ∴ 前紙が reports/ を母数から外した事は、★本番 code の複製 2 枚も同時に外して居た★。之を 此処に記す（前紙は書き換へぬ）。

## §三 ★前紙と今走で 数が食ひ違つた（scanned 15,612 → 15,632・差 20）★ ―― 因を当てた

| | 前紙（§零） | 今走 | 差 |
|---|---:|---:|---:|
| walked_files | 16,972 | 16,972 | 0 |
| scanned_text_files | 15,612 | 15,632 | **+20** |
| 讀めなんだ | 1,360 | 1,340 | **−20** |

★因の候補を 器で潰した★（`order194_walkdiff_v1.rule.py`）:

- 疑ひ㋑「except 節の広狭の差」（源器 = `(OSError, UnicodeDecodeError)` ／ 今器 = `Exception`）
  → **同じ走の中で 両形を並べて讀んだ**。結果 = `A_ok=15632  B_ok=15632` ／ `A_only=0  B_only=0` ／ `escaped_from_narrow_except=0`。
  ∴ ★except の差では説明が付かぬ（現に無い）★。
- 疑ひ㋺「母数の刈り込みの差」→ 六つの接頭辞（backend/ tests/ docs/ reports/ src/ frontend/）の下 = 12,210 枚・外 = 4,762 枚。walked は両走とも 16,972 で ★一致★ ∴ 刈り込みの差でもない。

∴ 残る説明は一つ ―― ★時の差★。walked（枚数）は不変のまま、★中身が変はつた file が 20 枚 現に在る★。
的の樹は作業樹であり porcelain 6 行の汚れを持つ。**HEAD pin `47c8bc3b…` は git の object を固定するが、作業樹の byte は固定せぬ。**

### ★A3 條 百七十一（『斯く在つた』の形）★

> **紙の頭に「樹 pin」を書いた時 ―― 己は 其の pin が ★作業樹の byte まで固定する★ かの如く書いた。**
> **然れど 汚れを持つ作業樹の上で測つた数は、同じ pin・同じ器でも 時が違へば変はる（実測 scanned 15,612→15,632・walked は不変）。**
> **∴ 作業樹で測つた数には ★pin だけでなく 測つた刻★ を同じ行に書け。pin が効くのは blob の数であつて 作業樹の数ではない。**

（家老 條 百九十七「器の偽陽性は 其の器で出した数 悉くに及ぶ」の裏 ―― 器は正しく、★足場が動いて居た★ 事例である。）

## §四 正負の対照

| 見た事 | 正（現に在る） | 負（現に無い） |
|---|---|---|
| walk 漏れの型 | UnicodeDecodeError 1,340 | PermissionError 0・IsADirectoryError 0・其の他の型 0 |
| reports/ の当たり | BOUNDED 82 行 | UNBOUNDED 0 行 |
| reports/ 15 枚の中身 | `.py` の写し 2 枚・`.md` 4 枚・`.json` 9 枚 | ―― |
| 差 20 の因 | 時の差（作業樹の byte が動いた） | except の差 0・刈り込みの差 0 |

## §五 母数と 測れなかつた数（別値）

| 何 | 数 |
|---|---:|
| walk した file | 16,972 |
| 讀めた text file | 15,632 |
| 讀めなんだ file | 1,340 |
| reports/ の当たり枚 | 15 |
| reports/ の当たり行 | 82 |
| ★測れなかつた★ 拡張子の残 | 9（上位 12 種のみ刷つた ∴ 残 9 枚の拡張子は測定不能） |
| ★測れなかつた★ 動いた 20 枚の名 | 測定不能（本走は前後の file 名を保つて居らぬ） |

## §六 器と raw（型 8 項）

| 何 | path（樹 = multi-agent-shogun） | sha256 64 桁 | wc | split | byte |
|---|---|---|---:|---:|---:|
| 器 | `scratch/ashigaru-third-3-12e9d4bd/order194_gap_fill_v1.rule.py` | `f20e04dab69b061c64fac40243b707ca958fe7181726b4ec580d0854047789ad` | 92 | 93 | 3983 |
| raw | `scratch/ashigaru-third-3-12e9d4bd/order194_gap_fill_v1.raw.txt` | `578c698ff1fa1c5c6405104efda9a53d89ef9f489ee266cd72900841ba3af347` | 134 | 135 | 13656 |
| 器 | `scratch/ashigaru-third-3-12e9d4bd/order194_walkdiff_v1.rule.py` | `02359e1e17a9a39d07e99bccb808bad2a3420e6bbe92cdb3139bca2f013eb2e5` | 64 | 65 | 2643 |

- argv 逐語 = `python3 /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-3-12e9d4bd/order194_gap_fill_v1.rule.py`
- cwd = `/home/hakudoukai/multi-agent-shogun` ／ host = `momizi-dx` ／ user = `hakudoukai` ／ uid = 1000
- exit_code = **0**
- 走の帳 = ★製品走 0★（己の讀取器のみ・家老が許した走 1 は前紙で使ひ切り 残 0 のまま動いて居らぬ）

## §七 自訴

1. 拡張子の内訳は ★上位 12 種のみ★ 刷つた ∴ 残 9 枚は測れて居らぬ。器の print を絞つたのは己である。
2. 差 20 の「動いた 20 枚」の ★名を保つて居らぬ★。因の型（時の差）は当てたが、file 名は測定不能。
3. `reports/` 逐語 82 行は raw に在るが ★紙には写して居らぬ★（紙の嵩を抑へた ―― 己の裁量である）。
4. 前紙は ★一字も書き換へて居らぬ★。本紙は追補として置いた。
5. `order194_walkdiff_v1.rule.py` は raw を残して居らぬ（画面出力のみ）。∴ 其の数は ★己が写した数★ である（席の作法 六条目）。

## §八 三択語で結ぶ

- walk 漏れ 1,340 が悉く UnicodeDecodeError である事 ―― **現に在る**
- 権限による漏れ ―― **現に無い**
- `reports/` 82 行が悉く境界形である事 ―― **現に在る**
- 前紙との差 20 が except/刈り込みに因る事 ―― **現に無い**
- 差 20 が ★何の file か★ ―― **測定不能**
- 拡張子の全内訳 ―― **測定不能**（上位 12 種のみ）

## §九 繰越

1. 動いた 20 枚の名（前後の file 名 + sha を保つ器を足せば測れる・走 0 で足る）
2. 拡張子の全内訳（print の絞りを外すのみ）
3. 「匿名」の定めが令と合ふか否か ―― ★席の裁を超える（家老へ）★
4. 直しの效きを実行段で見る一発（`--collect-only` を外す）―― ★己で請はぬ★
