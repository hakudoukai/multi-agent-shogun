# 板 a51340c6 ―― lot3 AI欠け38頁を原画像から読んだ候補表（★未投入★）

- 席: ashigaru-mac-3（專任3）／枝: ashigaru-mac-3/a51340c6-akahon-lot3-ai-missing-38-yomi-20260925（origin/main b9573b2d376e9a0a372234b696a733677feb7919 から切った）
- 母数: `raw/ai-missing-pages.txt`（lot3 証跡 docs/evidence/akahon-r8-lot3-20260924/ の写し）＝ 38頁。候補行 38行・頁の重複 0・欠け 0（lot3 の一覧と突き合わせて一致）
- 境界: ★DB 書込なし・本番なし・push なし★。reference_book_content への INSERT/UPDATE はしていない。この束は候補であり、投入の判断は上位に委ねる

## 何を作ったか
| file | 中身 |
|---|---|
| candidates_38.jsonl | 1行=1頁。source_file / source_page / title / content_text は reference_book_content の行の形。そのほか page_kind・confidence・illegible_count・numbers_checked・numbers_corrected_in_selfcheck・excluded・notes・image_path |
| candidates_table.md | 38頁の一覧（頁・Part・題・種別・確度・判読不能数・字数・撮影 path・sha256） |
| image_sha256.txt | 撮影 png 38枚の sha256（shasum の形）。`raw/image_sha256_check.out` で 38/38 OK、rc=0（`raw/image_sha256_check.rc`） |
| PROMPT.md | 読み手に渡した転記の指示（推測で数を埋めず 〔判読不能〕 と書く、など） |
| pipe_escape_log.tsv | 下の「機械の直し」で触った表の行 42行の記録 |
| raw/agent_out/cand_0..3.jsonl | 読み手4者が出した生の出力（直す前のもの） |
| raw/ocr_hint/ | 読み手に参考として渡した OCR 文字（正は画像。OCR は補助に過ぎない） |
| raw/batches/ | 4組への頁の割り振り |

source_file は `赤本R8_PartNN.pdf`（NN = ceil(頁/15)）。撮影は `/Users/momizimac/akahon-r8/out/akahon/png/赤本R8_pNNNN.png`（dpi 200。lot3 README の manifest sha256 2af9ee4e… と一致する撮影集）。

## どう読んだか
38頁を4組（10/10/9/9）に分け、読み手の agent 4者が各頁の原画像を見て転記した。各者は表の点数を印刷の「計」と足し合わせて照合し、数を画像と読み直した。
- 判読不能 0頁・confidence low 0頁。medium は 1頁（797。歯式の書き方と、読み手が自ら直した1語のため）
- 印刷の計と明細の和が合わない頁が ★1頁★: **849（症例273）** は印刷が 計1,716点、明細の和は 1,717点。★己で画像を開いて各点数を読み直した★（272+12 / 48 / 30 / 11 / 1,080 / 42+11+4 / 6×3 / 59+1+2 / 59+1+2 / 42+11 / 6×2）。転記は画像どおりで、差は原本側のもの。印刷どおり 1,716 と書き、差を notes に残した
- ★己の抜き取り★: 849 と 797 は画像と候補を突き合わせ、点数は全て一致（797 の和 2,508 = 印刷の計）。★38頁全部を己で目視したのではない★。残る36頁は読み手の照合（計との一致）に拠っている

## 機械の直し（中身は変えていない）
歯式の縦線 `|`（例 `|67 部`・`6|`）が markdown の表の列を割っていた行が 42行（9頁: 736・783・797・828・855・863・887・934・935）。列の数が見出しと食い違う行に限り、区切りでない `|` を `\|` へ置いた。直した後は列の数の食い違い 0。字の置き換えは `\` の足し込みだけ。直す前の生の出力は raw/agent_out/ にある。

## 知っておくべきこと（限界）
- **p801・p806** は lot3 の一覧では「欠け」だが、AI の JSON には本文がある（1207字・1129字）。この束では原画像から改めて読んだ。AI 版とどちらを採るかは判じていない
- **歯式**は平文で表しきれない（上下顎を示す線・隅の括弧）。読み手ごとに ┼/┬/⌊/⌋/｜ の使い方が揃っていない。各頁の notes に印刷の形を書いてある。投入の前に表記を一つに揃えるかどうかは上位の判断
- 題（title）の形が揃っていない: 「195 …」「症例 214 …」の両形がある。806 と 969 は見出しの無い解説頁で、題は読み手が付けたもの（notes に明記）
- 812 は本文が文の途中で終わり、813 へ続く
- 読み手の一者が scratch に下書き（_a0/）を残した。束には入れていない。scratch は repo の外にある

## 未測
- 残る36頁を己の目で画像と照合すること: 未測（時間の都合で2頁の抜き取りのみ）
- DB の既存行との重複: 未測（DB を読み書きしない境界のため）
