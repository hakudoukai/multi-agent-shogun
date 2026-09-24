# 板 fae4680a ―― 段3b-3 衝突裁き（赤本R8 Part47〜68）

- 担当: ashigaru-mac-3（付替元 se4-3）／ 下命: queue/goals/ashigaru-mac-3.yaml（2026-09-24 15:46 iincho）
- 枝: ashigaru-mac-3/fae4680a-akahon-part47-68-shogotsu-sabaki-20260924（origin/main b9573b2d から）
- ★投入無し・UPDATE 無し・~/akahon-r8 へは一字も書かず（讀取のみ）★。結果は dr-m へ渡す材料。

## 母数の定義（測刻 2026-09-24 15:48 +0900）
- 母数 = `~/akahon-r8/out/akahon/qc/赤本R8_Part{47..68}_qc.jsonl` の record のうち `tag == "conflict"` の頁。
- Part47〜68 の record 計 325 = machine_ai_agree 159 ＋ **conflict 128** ＋ ai_missing 38。
- ★本母数に含めぬ物★: ai_missing 38頁（AI 読みが無い＝裁く相手が無い・本段の範囲外）、machine_ai_agree 159頁。
- 入力の sha256: raw/input_sha256.txt（qc 22 本・ai 22 本・ocr 22 本 ＝ 66 行）。母数の頁一覧 = raw/conflicts.jsonl。

## 裁きの結果（128/128 頁）
| 採用 | 頁数 |
|---|---|
| ai（AI 読みが原画像に本文として忠実） | 34 |
| neither（AI にも本文の疵あり・疵を名指し＝SE 再読要） | 94 |
| ocr（OCR の方が忠実） | 0 |

- 正本: `adjudications.jsonl`（1頁1行・page/source_file/adopted/reason/ai_defects/missing_token_class/values_checked/values_mismatched）
- 人が讀む表: `adjudications_table.md`（頁・source_file・採用・根拠1行）
- ★ocr=0 の意味★: OCR は表・丸数字でほぼ全頁崩れて居り、本文を AI より正しく持つ頁は無かつた。
  ただし neither の頁で ★AI が落とした節を OCR が（崩れつつ）持つ★ 例は在る（p0719/0777/0803/0904/0972 等・ai_defects に記す）。
- ★neither の意味（何を意味せぬか）★: 「AI 読みが全面に誤り」ではない。多くは 1〜数語の置換
  （例: 暫間歯冠補綴装置→暫間固定冠補綴装置、腫瘤→腫瘍、疑義解釈→疑義解説）や歯式の丸数字/正中線の誤り。
  点数値は大半の頁で原画像と一致した。数値の疵が在るのは少数（例: p0985 加算1 50点→150点、p0979、p1001、p0841）。
  厳格基準（本文の語・歯式を一字でも変へたら ai にせぬ）を採つた ―― p0753/0755/0815 等は一字の差で neither。
  境界の緩めは dr-m / 軍師の判に委ねる（各頁の ai_defects に疵を具体に書いてあるゆゑ再分類できる）。

## 欠け鍵（nums_missing_in_ai）の正体（367 鍵）
- page_number 120（印刷頁番号＝頁−142）／ footer_legend 21（「随時改定対象（令和8年4月…）」）／ ocr_misread 44 ／ body 182
- ★body 182 は「AI が落とした」を意味せぬ★: batch0（p691〜713 ブリッジ一覧）で歯式の数字列が連結された鍵が多く、
  AI が丸数字・区切りを付けて持つて居る物も含む。1,250点 が「250点」に割れる類（桁区切りの分断）は ocr_misread に入れた席と body に入れた席がある。
- 己の対照: QC の鍵抽出 KEY_RE は「加算 1, 歯科」を「1歯」と拾ふ（raw/self_control_1ha.txt）＝ QC 器の偽陽性の一因。器は触らず記すのみ。

## 手法
- 128頁を 16頁×8 に割り（raw/batch0..7.txt）、同一の指示書 raw/PROMPT.md で補助 agent 8本が各頁の PNG を目視し、
  OCR 文・AI 文と突き合はせて raw/verdicts_0..7.jsonl を書いた。己が併合・検算した（欄・頁集合・source_file・欠け鍵集合を conflicts.jsonl と照合＝疵0）。
- 抜き取り検め: raw/spotcheck.md（AI 側 10 件＋原画像 2 頁＋己の対照 1 件＝13 点、悉く agent 判と一致）。
- p0691 は既存の adjudication（se4_required）と third_read を参照した上で画像から判じた（third_read の訂正にも歯式の誤りあり）。

## 限界（未測・理由）
- 全128頁を己が目視したのではない（抜き取り13点）。values_checked/mismatched は agent の抜き取り計数で全数ではない。
- 本段は「どちらを採るか」の裁きまで。正しい本文の作り直し（neither 94頁の SE 再読）は範囲外。
