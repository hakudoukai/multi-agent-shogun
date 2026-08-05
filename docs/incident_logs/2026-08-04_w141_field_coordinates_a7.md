# W141 — テンプレート座標改竄の生成文書への波及 追跡 — 足軽7号 (2026-08-04)

★実施＝稼働直前 (委員長解釈・理事長裁定待ち)★。本件は findings のみ。patch・diff・行番号つき置換文は含まない (Phase B 繰延、理事長令)。

[lane=W141]

参照した正本: hakudokai-dev origin/main 0698a2c888158efd29381406d2af281740e72ca6
断面確認時刻=2026-08-04T15:37:28+0900 (rev-parse実行時刻、末尾§6)
- backend/pdf/field_coordinates.py (blob=0033ec3f5796e660a665d54e1109e24040058b79、4479行)
- backend/api/documents.py L84-95 (`_compute_document_hash`), L150-238 (`_get_renderer`)

手段=`git -C /mnt/c/Projects/hakudokai-dev <read-only subcommand>`のみ。cd/fetch/
checkout等0件。hakudokai-devへ1字も書いていない・DB実査/実装/実行0件。

## 対に成る他工区欄

W137 (足軽7号自身、判定不能の性質を「書込対象」から「データフロー終点までの追跡」へ移した工区) が直接の前工区。W132 (spoofable role check の発見) とは「監査証跡の真正性」という主題を共有するが手法は独立。他工区との明示的な接続確認は探索していない (探した範囲=自分のW128/W131/W132/W137系列のみ)。

## §0 母集団導出法・陽性対照 (先に書く)

母集団= `backend/pdf/field_coordinates.py`内で、W128/W137が対象とした4関数
(`update_field_coordinates`/`delete_fields`/`restore_fields`/`add_field`) が
実際に何を書き換えるかを、関数本体の直接精読 (機械grepではなく読解) で
特定した。陽性対照= 同fileに`write_text`という文字列が実在し、かつ4関数
それぞれの本体に1回ずつ出現することを`grep -c`で確認し (末尾§6)、
「精読で見つけた書込先」が「機械カウントでも同数存在する」ことの相互検算とした。

## §1 波及する。何が起き得るかを具体的に書く

### 1-1 発見= 4関数は DB ではなく Pythonソースファイル自体を rewrite する

`update_field_coordinates`(3205) のdocstring: 「field_coordinates.pyの
ソースを直接書き換えてフィールド座標を更新する」。実装 (3228-3229):
```python
file_path = Path(__file__)          # field_coordinates.py 自身
content = file_path.read_text(encoding="utf-8")
```
以降、正規表現で`FieldSpec("name", x, y, w, h, ...)`というPythonコード中の
数値リテラルを置換し、最終行 (3596)で:
```python
file_path.write_text(new_content, encoding="utf-8")
```
同一fileへ書き戻す。同型のwrite_textが`delete_fields`(3687)・
`restore_fields`(3745)・`add_field`(3837)の4箇所に存在する
(§0で機械カウント済・4件一致)。

∴ これはDB row の書換ではなく、backendアプリケーションのsource code
そのものを、認証なしのHTTP POSTから書き換えられるという発見である。

### 1-2 波及経路 (source→render まで追跡)

1. `field_coordinates.py`は`FieldSpec(name, x_mm, y_mm, width_mm, height_mm,
   font_size, font_weight, ...)`のリストをmodule-level変数として定義し
   (推定=`_FORM1_INITIAL_FIELDS`等、`get_field_map(form_type)`(3161)が
   これを`FIELD_MAPS`辞書経由で返す構造と読める)、これは「方式A:
   テンプレートオーバーレイ」の各renderer (`Form1InitialRenderer`等、
   `documents.py` L154-187 でimport) が書類テンプレート画像上のどの
   座標にどのフィールド値を描画するかを決める設計データである。
2. `generate_document`(documents.py L244-294)・`regenerate_document`
   (L296-337) は`_get_renderer()`(L150-238) 経由で上記rendererを取得し、
   `renderer.render()`を呼んでPDF bytesを生成する。
3. ∴ `field_coordinates.py`の座標を書き換えれば、以降このmoduleが
   (再)importされた時点から、生成されるPDF上で各フィールドの値が
   描画される位置・文字サイズ・太さが変わる。

### 1-3 具体的に何が誤表示され得るか (真正性の観点)

- 座標を近接する他フィールドの位置へ変更= 例えば「病名」欄の座標を
  「患者氏名」欄の座標へ書き換えれば、同じdocument_records行 (form_data)
  の中身は一切変わらないまま、印刷・表示される書類上では病名が氏名欄に
  現れる (逆も然り)。これは患者を取り違えた記録に見えかねない。
- 座標をページ外・他要素と重なる位置へ変更= 情報がテンプレート上で
  見えなくなる (欠落したように見える)、または他の文字と重なり判読
  不能になる。
- font_size/font_weightの改変= 重要な値 (例: 患者の同意欄・警告文言)
  を極小フォント・低視認性へ変更すれば、実際には存在するが事実上
  読めない書類を作れる。
- これらいずれも、書類のDB上のデータ (`form_data`) は改竄されていない
  ため、通常のデータ監査 (DB row精査) では検出できない。

### 1-4 最も重い発見= 改ざん検知hashが座標改竄を検出しない

`finalize_document`(documents.py L1474)が呼ぶ`_compute_document_hash()`
(L84-95、全文精読済) は:
```python
parts = [record["patient_id"], record["form_type"], record["record_date"],
         record["form_data"], record["auto_data"]]
content = "|".join(parts)
return hashlib.sha256(content.encode()).hexdigest()
```
∴ この「改ざん検知」ハッシュは`document_records`テーブルの列のみを
対象とし、field_coordinates.pyの内容 (座標・フォント設定) は一切
ハッシュへ含まれない。finalize時点のdocument_hashが有効なまま、
座標改竄によって実際に印刷・表示される書類の見た目だけが変わり得る、
というtamper-evidence機構の死角を発見した。

★なお、当時点で別レーン (足軽5号・足軽6号 W144系) が示した「finalize系は
role check+SHA-256 hash+revision snapshot+audit log の4点セットが実在するが、
document_hash 列は書込のみで読み返し照合箇所が0件=実質無力化」という知見と、
本件は同一の性質 (書くだけで検証しない安全網) を指す。★
★★己は検めておらぬ★★= 上記4点セット・照合箇所0件の実測は当職が直接
`log_audit`呼出/`document_hash`列の読み返し箇所を再確認したものではなく、
足軽5号・足軽6号の報告を運んだのみである (W179 §3-1 参照)。

## §2 波及せぬ場合はあるか — 構造的な留保 (限界)

波及自体は§1で確定したが、いつ波及するか (即時か、次回import/再起動時か)
は当職には確認できない:

- Pythonのmodule importは通常プロセス起動時に1度だけ行われ、以後
  `sys.modules`にcacheされる。∴ `field_coordinates.py`のsource file書換えは、
  当該moduleが次に (再)importされるまでは、稼働中プロセスのメモリ上の
  値には反映されないというのがPythonの一般的挙動である。
- ∴ 波及のタイミングは「プロセス再起動」または「auto-reload機構
  (開発サーバでよく使われるfile監視による自動再起動)」の有無に依存する。
  当職はhakudokai-devのデプロイ構成 (uvicorn --reloadの使用有無・
  本番運用形態) を確認する手段を持たず (実行環境の確認は本工区の
  権限外)、即時反映か次回起動時かは言えぬ。
- 然れど、たとえ即時反映でなくとも、source fileへの書込自体が
  既に成立している以上、次回のプロセス再起動 (通常のデプロイ・
  メンテナンス再起動を含む) で改竄が有効化されることは変わらない。
  ∴ 「即時ではないから安全」という結論にはならない。

## §3 健全例 (最低一つ)

`_compute_document_hash`が対象とする5項目 (`patient_id`/`form_type`/
`record_date`/`form_data`/`auto_data`) 自体は正しくハッシュ化されており、
これらの列に対する改竄 (例えば`form_data`の直接DB UPDATE) は
finalize時点のhash再計算と食い違うため理論上検出し得る設計になっている
(照合が実施されるか否かは別問題として既に他レーンが指摘済=§1-4末尾)。
∴ 本件は「hash機構が全く無意味」ではなく「hash機構の対象範囲が
座標データを含まない」という★対象範囲の死角★である。

## §4 限界の自己開示 (どこまで判ってどこから判らぬか)

- `field_coordinates.py`のFIELD_MAPS定義部分 (推定1-3160行) は
  module-level dict/list literalの詳細構造までは全文精読していない
  (4479行全文の精読は時間内に不能。3161行以降の関数定義部分と、
  4関数それぞれのwrite_text到達経路を優先して精読した)。
- 各`Form*Renderer`クラス (form1_initial.py等) 自体の実装は読んでいない。
  `get_field_map`/`FIELD_MAPS`を実際にどう消費するかの詳細
  (キャッシュの有無等) は推定に留まる。★∴ ここが「なお判らぬ」境目=
  レンダラー実装本体を読めば、波及の具体的なレンダリング挙動 (座標の
  上限下限チェックの有無・例外処理の有無等) がさらに精密化できる★。
- デプロイ環境のauto-reload設定は確認していない (§2)。
- 実際にこの経路が悪用された痕跡は調査していない (D-lane相当・
  本工区の対象外)。

## §5 W128以来の分類への影響 (裁定ではなく申し送り)

W128/W131時点で「テンプレート/座標設定6件は患者個別recordではないため
優先度を下げた」という当職の判断は、書込対象がDB rowか否かという観点では
正しかったが、被害の実質 (真正性への影響) という観点では見直しが要る
可能性がある — source code書換えという性質上、被害は「1文書」ではなく
プロセス再起動後に生成される全ての当該form_type文書に及び得る
(potentially broader than a single patient record)。裁定はしないが、
優先順位表 (W128/W131) の見直しを上位へ申し送る。

## §6 確認方法 (再現手順) — patch ではなく検証手段として記す

以下はコードの適用可能な変更ではなく、上記§1の発見を第三者が独立に
再現・検証するための読取専用の手順である。

```bash
git -C /mnt/c/Projects/hakudokai-dev rev-parse origin/main
git -C /mnt/c/Projects/hakudokai-dev show origin/main:backend/pdf/field_coordinates.py \
  > <scratchpad>/field_coordinates.py
/usr/bin/grep -n "^def \|write_text" <scratchpad>/field_coordinates.py
# → def update_field_coordinates(3205)/delete_fields(3627)/restore_fields(3697)/add_field(3754)
#   write_text: L3596/3687/3745/3837 (4関数×各1箇所、陽性対照=機械カウントと精読結果が一致)

git -C /mnt/c/Projects/hakudokai-dev show origin/main:backend/api/documents.py
# → L84-95 _compute_document_hash (patient_id/form_type/record_date/form_data/
#   auto_dataのみをhash対象とし、field_coordinatesを含まないことを確認)
```

## §7 為し得たのに為さなんだ事

レンダラー実装本体 (`backend/pdf/form*.py`) を今回精読する時間があれば、
「波及するかどうか」に留まらず「波及の具体的な閾値・例外処理の有無」まで
本工区で閉じられた可能性がある。時間配分の判断で見送った。

## §8「直った物」「壊した回数」

design-only・追跡調査のみにつきZ概念なし。実装0件・実行0件・
壊して直した回数=0/0 (該当なし)。壊れる試験の件数=0 (実装を伴わないため該当なし)。

## 着地に誰の承認を要するか

本件は findings/調査/畳み込みに区分される (実装・patchではない)。
Phase B 繰延 (理事長令) の下でも継続可能な区分とkaro-secondより指示済。
実施＝稼働直前 (委員長解釈・理事長裁定待ち)。

## 稼働直前チェックリストへの畳み込み

| 元区分 | 畳み込み後 |
|---|---|
| before/after diff | 是正案(prose)= `_compute_document_hash`の対象列に座標・フォント設定由来の値 (または`field_coordinates.py`のcontent hash) を含める設計とすべき、という方向性のみ示す。具体的な実装コードはここに書かない。 |
| 負テスト | 確認方法(再現手順)= §6 のread-only git手順で、write_text到達経路とhash対象列の非包含を第三者が独立に再現できる。 |
| 開ける穴 | そのまま= §1-4 (hashが座標改竄を検出しない)・§2 (反映タイミング不明)。 |
| 件数 | 影響範囲= 座標書換えは「1文書」ではなく「次回プロセス再起動後に生成される、当該form_typeを用いる全患者文書」に及び得る (母集団=当該form_typeの生成対象患者数、当職は未算出)。 |

以上いずれもread-only git subcommandのみ。cd/checkout/commit/push/fetch/実装/実行/
DB実査 等0件。裁定はしていない (§5は申し送りに留める)。以上。report_to: karo-second。

判定不能事項の要約 (どこまで判ってどこから判らぬか): 「テンプレート/座標は
共有設定であり患者個別recordではない」ことは確定。「その改竄が生成文書へ
どう波及するか」は§1で機構としては確定 (source rewrite→render pipelineの
入力データ)。「実際にどの程度の視認性劣化・誤表示が起こり得るか」の定量的な
限界は、レンダラー実装本体未読のため判定不能のまま (§4)。
