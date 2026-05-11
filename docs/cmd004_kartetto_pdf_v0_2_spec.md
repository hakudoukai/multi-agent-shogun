# cmd_004 機能② カルテッド PDF v0.2 検査値抽出精度向上 — spec

- task_id: subtask_cmd004_kartetto_pdf_v0_2_spec
- 起案者: ashigaru6 (鳥居/平岩)
- 起案日: 2026-05-11
- parent_cmd: cmd_004「会計待ち時間ゼロ」
- 範囲: spec のみ。実装 commit は本 task 範囲外 (constraints L8)
- 評価原則: 本能寺戒め厳格遵守、機械 evidence のみ評価

---

## 1. 目的

カルテッド (Quartetto) 印刷 PDF 由来の検査値・点数・患者ヘッダー抽出精度を v0.1 比で大幅に向上させ、`会計完了 → カンバン billing 自動移動` の信頼性を回復する。

v0.1 は pdfplumber + 単行正規表現に依存しており、(a) スキャン画像 PDF / (b) 折り返し・複数列レイアウト / (c) 半角全角・濁点ゆれを含む明細行 / (d) 検査値 mapping 揺れ — を一切吸収できない。本 spec は v0.2 で上記 4 失敗類型を体系的に解消する設計と検証手段を定める。

## 2. v0.1 現状 inventory (AC1)

機械 evidence: `/mnt/c/Projects/hakudokai-dev/backend/etl/` 直下の現行実装。

| ファイル | 行数 | 役割 |
|---|---|---|
| `quartetto_pdf_watcher.py` | 471 | フォルダ A 監視・コピー・5 方向出力パイプライン |
| `quartetto_pdf_parser.py` | 463 | pdfplumber テキスト抽出 + 正規表現解析 |
| `quartetto_extraction_rules.yaml` | 70 | 抽出正規表現と 14 区分マッピング設定 |
| `backend/tests/test_quartetto_pdf_parser.py` | 543 | モックテキストベース unit test |

### 2.1 watcher 主要関数 (file:line)

- `quartetto_pdf_watcher.py:48-71` `wait_until_stable` — サイズ安定判定 (poll 1s, timeout 15s, 連続 2 回)
- `quartetto_pdf_watcher.py:76-95` `copy_and_rename` — `{YYYYMMDD_HHMMSS}_{基底名}.pdf` で out_dir/processed/ に複製
- `quartetto_pdf_watcher.py:100-154` `output_for_patient_app` / `output_for_daily_summary` / `output_kanban_notification` — 三方向 JSON 出力
- `quartetto_pdf_watcher.py:185-238` `trigger_kanban_billing_move` — `backend.api.kanban.register_payment_completed` 経由でカンバンを billing レーンへ移動 (例外時は warning + watcher 継続)
- `quartetto_pdf_watcher.py:243-261` `output_common_patient` — `backend.utils.patient_format.normalize_from_pdf` で `no=clinic_id_zeroPaddedPatientNo` 形式に正規化
- `quartetto_pdf_watcher.py:266-299` `trigger_receipt_render` — meisai_receipt_renderer ブリッジ用中間 JSON 生成
- `quartetto_pdf_watcher.py:307-331` `process_pdf` — 5 方向同時出力本体
- `quartetto_pdf_watcher.py:336-381` `QuartettoPdfHandler` — watchdog `on_created`/`on_modified` ハンドラ、`_processing` set で同 path 二重処理を `threading.Lock` で排他

### 2.2 parser 主要関数 (file:line)

- `quartetto_pdf_parser.py:32-45` `load_extraction_rules` — YAML 読込 + キャッシュ
- `quartetto_pdf_parser.py:106-113` `ReceiptLineItem` dataclass (category/item_name/points/count)
- `quartetto_pdf_parser.py:116-196` `ExtractedReceiptData` dataclass + `to_dict` (20 行までフラット化) + `to_common_patient` (§4 共通データ型)
- `quartetto_pdf_parser.py:202-218` `extract_text_from_pdf` — **pdfplumber.open → page.extract_text の単純連結。OCR 経路なし**
- `quartetto_pdf_parser.py:224-285` `_compile_patterns` — header / totals / detail_line / grid_line 正規表現コンパイル
- `quartetto_pdf_parser.py:305-321` `_resolve_visit_date` — 令和判定 (year_raw<100 → +2018)
- `quartetto_pdf_parser.py:324-424` `parse_receipt_text` — 単行 regex finditer ベース解析
- `quartetto_pdf_parser.py:430-463` `parse_quartetto_pdf` — public entry point

### 2.3 抽出ルール YAML 抜粋

```yaml
detail_line:
  pattern: '^({categories})\s+(.+?)\s+(\d+)\s*(?:(\d+))?\s*$'   # 単行・空白区切り前提
grid_line:
  pattern: '^({categories})\s+(\d+)\s*$'                         # 区分名 + 点数のみ
```

15 カテゴリは 14 区分 + 「その他」。`_load_kubun_map` (parser.py:62-83) で `grid_field` (英字スネークケース) にマップ。

## 3. v0.1 抽出精度評価 (AC2)

**機械 evidence の限界**: 現リポジトリ・hakudokai-dev tree のいずれにも実 PDF サンプルおよび 抽出結果 log は存在しない (`find` 結果: `*quartetto*sample*` / `*quartetto*fixtures*` ともに 0 件)。よって本評価は **コード仕様面の脆弱性分類** であり、実 PDF 入力 件数 × 成功率は **本 spec の §6 regression test fixture 整備後に初測定** する。

### 3.1 既知の失敗 pattern 分類

| ID | 失敗類型 | 起源 (file:line) | 影響 |
|---|---|---|---|
| **F-A: スキャン画像 PDF** | `extract_text_from_pdf` は pdfplumber テキストレイヤのみ取得。OCR 経路なし | parser.py:202-218 | テキスト = 空文字列 → `parse_warnings` 1 行のみで 5 方向出力すべてが ID 不在の壊れた JSON になる。カンバン billing 移動も `missing_patient_or_date` で skip (watcher.py:201-206) |
| **F-B: 折り返し / 複数列レイアウト** | `detail_line` 正規表現は `^({categories})\s+(.+?)\s+(\d+)\s*(?:(\d+))?\s*$` 単行・MULTILINE | parser.py:278-280 / rules.yaml:42 | 治療行為名が改行を含む場合カテゴリ次行へ漏れ、`finditer` は 0 件マッチ。grid 集計が全 0 化 |
| **F-C: 文字化け / 半角全角ゆれ** | カテゴリ名は YAML 文字列の完全一致 (`re.escape(c)` で固定化) | parser.py:48-57 | 「初･再診料」「初・再診料」「初・再診料」(中黒の Unicode 差) で別物扱い、明細 0 件化。同様に「氏 名」全角空白も `patient_name` regex ですれ違う |
| **F-D: 検査値 mapping ズレ** | `_load_kubun_map` は厚労省 14 区分の表記前提。カルテッド独自カテゴリ (例「歯科疾患管理」「指導料」) は `sonota` に丸められる | parser.py:62-83, 384 | grid_totals の集計欠落 + daily_summary 不整合 |

### 3.2 数値検査値の固有リスク

カルテッド PDF は明細行 = `category + treatment + points + count` のみで、検査結果値 (例: HbA1c, GLU) 抽出経路は未実装。**v0.2 では「点数抽出」と「検査結果値抽出」を分離設計** する必要がある (§4)。

## 4. v0.2 精度向上 spec (AC3)

### 4.1 設計方針

1. **テキスト経路と画像経路の二段構え**: pdfplumber テキストレイヤを第一経路、空文字または閾値未満なら OCR 経路に fallback。
2. **レイアウト anchor + 表抽出**: pdfplumber の `page.extract_tables()` をカテゴリ anchor (左端カラム値) で構造化し、複数列レイアウトを救済。regex 1 本に依存しない。
3. **検査値正規化 ruleset**: カテゴリ名・空白・濁点・半角全角を NFKC + カスタム変換表で吸収。
4. **検査結果値 (lab values) 抽出は別 entry**: 点数明細とは別 dataclass (`ExtractedLabValues`) を新設し、患者番号・診療日でひも付け。watcher の 5 方向出力には患者アプリ JSON にのみ同梱。
5. **回帰可能な golden test**: 実 PDF (匿名化済) を fixture 化し、現行 unit test と独立した E2E suite を追加。

### 4.2 OCR engine 比較

スキャン画像 PDF (F-A) 救済用 fallback の候補。**選定は本 spec の決定対象ではなく、§6 PoC benchmark の結果で決定** する。3 候補をそれぞれ評価。

| engine | 強み | 弱み | 想定コスト | ライセンス |
|---|---|---|---|---|
| **tesseract (`pytesseract`)** | OSS、ローカル完結 (PII 流出ゼロ)、jpn 学習済モデルあり、CI で再現可 | 縦書き混在・小フォント・低解像度に弱い。レイアウト保持なし | OSS + 計算リソース | Apache 2.0 |
| **PaddleOCR** | レイアウト保持 + 表抽出 (`PP-StructureV3`) が強い、jpn モデル整備、ローカル完結 | モデル ~300MB、初回 cold start ~5s、依存が重い | OSS + GPU 推奨 | Apache 2.0 |
| **Claude Vision (`anthropic` SDK)** | レイアウト解釈・文脈推論で揺れ吸収が圧倒的、表 → JSON 直返し可 | 外部 API → PII 越境、コスト/枚、blocked_env (`ANTHROPIC_API_KEY` 未設定) | API 課金 + ネット | 商用 |

**初期推奨**: 一次は **tesseract** (PII 完全ローカル) + 表抽出は **PaddleOCR** を fallback。Claude Vision は **保険外検査値の不確実 case のみ陛下御差配で有効化** (PII 越境につき opt-in 既定 OFF)。

PoC benchmark の指標 (§6 で測定):

- 文字認識精度 = `正しく抽出された文字数 / 期待全文字数` (per-field)
- 表構造保持率 = `正しい (row, col) に格納された cell 数 / 期待 cell 数`
- 処理時間 = `page あたり median ms`
- 失敗 case の混乱パターン (混同表)

### 4.3 レイアウト anchor 検出

```
入力: pdfplumber.Page
処理:
  1. page.extract_tables() を試行
     - 表が取れる → anchor = 左端カラム値、各行を (category, treatment, points, count) にマッピング
  2. 表抽出 0 件 / 列数不一致時:
     - page.extract_words(use_text_flow=True, keep_blank_chars=False)
     - x0 のクラスタリング (k=4: category | treatment | points | count) で疑似列推定
  3. 1 と 2 両方とも失敗:
     - 旧 regex finditer に fallback (互換維持)
出力: list[ReceiptLineItem]
```

検証指標 (§6): F-B サンプル (複数列・折り返し) で extract_tables 経路の grid_totals 一致率を 95% 以上に。

### 4.4 検査値正規化 ruleset

新規ファイル `backend/etl/quartetto_normalize.py` を導入。

| step | 処理 | 対象 |
|---|---|---|
| 1 | `unicodedata.normalize("NFKC", s)` | カテゴリ・項目名・全フィールド |
| 2 | 連続空白 (`\s+` 全角含む) → 1 空白 | 同上 |
| 3 | カテゴリ表記揺れ変換表 (例: 「初・再診料」「初･再診料」「初・再診料」「初再診料」→ 正規表現に依らず辞書 → "初・再診料") | カテゴリ列のみ |
| 4 | 濁点・半濁点合成 (NFC) | 患者氏名 |
| 5 | 数値: 全角数字・カンマ・「，」を半角・除去 | 点数・金額 |

設定は `quartetto_extraction_rules.yaml` に `normalization:` キーを追加し、コード変更不要で表記揺れを追加可能。

### 4.5 dataclass 追加

```python
@dataclass
class ExtractedLabValues:
    patient_no: str = ""
    visit_date: str = ""
    items: list[LabItem] = field(default_factory=list)
    parse_warnings: list[str] = field(default_factory=list)

@dataclass
class LabItem:
    code: str = ""        # 例 "HbA1c"
    value: str = ""       # 例 "6.5"
    unit: str = ""        # 例 "%"
    ref_low: str = ""
    ref_high: str = ""
    flag: str = ""        # "H" / "L" / ""
```

watcher.py:307 `process_pdf` から検査値経路を `output_for_patient_app` 側 JSON に同梱。

### 4.6 OCR fallback 経路

```
extract_text_from_pdf_v2(pdf_path) -> tuple[str, str]:
    text = pdfplumber 連結
    if len(text.strip()) >= TEXT_MIN_CHARS (= 50):
        return (text, "text_layer")
    ocr_text = _ocr_fallback(pdf_path, engine=cfg.OCR_ENGINE)
    return (ocr_text, "ocr:" + cfg.OCR_ENGINE)
```

- `source = "ocr:tesseract"` 等を `ExtractedReceiptData.source_file` の隣接フィールド `extraction_source` に格納し、下流 (daily_summary 等) で信頼度フラグとして利用可。
- OCR engine は `quartetto_extraction_rules.yaml` の `ocr.engine` で切替 (default: `tesseract`)。

### 4.7 後方互換

- `parse_quartetto_pdf` の戻り値 `ExtractedReceiptData` は **新 field 追加のみ**、既存 field 削除なし。
- `extract_text_from_pdf` は v0.1 シグネチャ維持 (戻り値は `str`)、v0.2 は `extract_text_from_pdf_v2` を別関数として並走。
- 設定 YAML version は `1.0` → `2.0` に bump。

## 5. 検査値正規化 ruleset 詳細

```yaml
# rules.yaml v2.0 追記分
normalization:
  apply_nfkc: true
  whitespace_collapse: true
  category_aliases:
    "初・再診料": ["初・再診料", "初･再診料", "初・再診料", "初再診料"]
    "歯冠修復・欠損補綴": ["歯冠修復・欠損補綴", "歯冠修復･欠損補綴", "歯冠修復欠損補綴"]
    "リハビリテーション": ["リハビリ", "リハ"]
    # ... 全 15 カテゴリ ...
  numeric_normalize:
    fullwidth_digit_to_halfwidth: true
    strip_thousands_separator: ["，", ",", " "]
ocr:
  engine: "tesseract"   # "tesseract" | "paddleocr" | "claude_vision"
  min_text_chars: 50
  tesseract_lang: "jpn+eng"
  paddleocr_lang: "japan"
  claude_vision_opt_in: false   # PII 越境ゆえ既定 OFF
```

## 6. regression test suite (AC3 必須)

### 6.1 fixture 整備

`backend/tests/fixtures/quartetto/` に下記 3 系統 × 各 N=10 件 (匿名化必須) を配置:

| 系統 | 想定失敗類型 | 期待挙動 |
|---|---|---|
| `text/` テキスト埋め込み PDF | F-C / F-D | text_layer 経路で grid_totals 完全一致 |
| `scanned/` スキャン画像 PDF | F-A | OCR fallback 起動、`extraction_source == "ocr:tesseract"` |
| `layout/` 複数列・折り返しレイアウト | F-B | extract_tables 経路で行数 = 期待値 |

匿名化規範: 患者番号 → `9999_NNNN`、氏名 → 「テスト N 郎」、生年月日 → 1900-01-01 固定。実 PDF 取込みは陛下御差配 + RLS gate 通過後のみ。

### 6.2 golden test

新規 `backend/tests/test_quartetto_pdf_v0_2.py`:

```python
@pytest.mark.parametrize("pdf, expected_json", load_fixtures("text"))
def test_text_layer_golden(pdf, expected_json):
    actual = parse_quartetto_pdf(pdf)
    assert actual.to_dict() == expected_json   # 完全一致 (除く timestamp)

@pytest.mark.parametrize("pdf, expected_json", load_fixtures("scanned"))
def test_ocr_fallback_golden(pdf, expected_json):
    actual = parse_quartetto_pdf(pdf)
    assert actual.extraction_source.startswith("ocr:")
    _assert_fields_within_tolerance(actual, expected_json, tolerance=0.95)
```

### 6.3 metric 計測

CI で毎 PR ごとに以下 metric を `queue/reports/quartetto_v0_2_metrics.yaml` へ追記:

- `text_layer_pass_rate` (目標 ≥ 0.99)
- `ocr_pass_rate` (目標 ≥ 0.85)
- `layout_pass_rate` (目標 ≥ 0.95)
- `median_ms_per_page` (text / ocr 別)

閾値割れで PR を block。

### 6.4 contract test (受入条件)

| acceptance | 検証 |
|---|---|
| AC-T1 | F-A: スキャン画像 PDF 投入 → `extraction_source == "ocr:tesseract"` + patient_no 抽出 |
| AC-T2 | F-B: 折り返しレイアウト → grid_totals 期待値完全一致 |
| AC-T3 | F-C: カテゴリ表記揺れ 5 種 → 全て同一 grid_field に集約 |
| AC-T4 | F-D: 未知カテゴリ「指導料」→ `sonota` に集計 + parse_warnings 1 行 |
| AC-T5 | v0.1 unit test (test_quartetto_pdf_parser.py) 全 pass を維持 |

## 7. 段階導入計画 (非実装、参考)

| phase | 範囲 | gating |
|---|---|---|
| P1 | 正規化 ruleset + extract_tables 経路導入 (F-B / F-C / F-D) | 既存 unit test green + 新 layout fixture green |
| P2 | OCR fallback (tesseract 一本) (F-A) | scanned fixture pass_rate ≥ 0.85 |
| P3 | PaddleOCR 切替・PoC benchmark | metric YAML 閾値比較 |
| P4 | Claude Vision opt-in (陛下御差配) | RLS gate 通過 + PII 影響評価書 添付 |

## 8. 既知のリスクと回避

| risk | 影響 | 回避 |
|---|---|---|
| 実 PDF サンプル不在で精度の絶対値が言えない | 評価が定性のみ | §6.1 fixture 整備を P1 着手前提条件に格上げ |
| OCR fallback 経由で `total_points` が `copay_amount` と矛盾 | カンバン billing 移動が誤動作 | watcher.py:201-206 の skip 条件に `extraction_source == "ocr:*" and total_points == 0` を追加 |
| Claude Vision で PII 越境 | 法令違反リスク | default OFF + 陛下御差配明示 + per-PDF audit log |
| pdfplumber/PaddleOCR の依存重量化 | watcher の cold start 増加 | OCR 経路は lazy import (`def _ocr_fallback(): ...` 内で import) |

## 9. 本 spec が答えない事項 (本実装 task で別途決める)

- 実 PDF fixture の収集 / 匿名化手順の運用フロー (情報セキュリティ担当との調整)
- カンバン billing 自動移動の判定基準を `extraction_source` で分岐するか否か
- Claude Vision opt-in 時の課金管理 (per-clinic limit)

---

## 10. 参照ファイル一覧 (機械 evidence)

| path | 役割 |
|---|---|
| `/mnt/c/Projects/hakudokai-dev/backend/etl/quartetto_pdf_watcher.py` | watcher 本体 (改修対象外、interface 維持) |
| `/mnt/c/Projects/hakudokai-dev/backend/etl/quartetto_pdf_parser.py` | parser 本体 (v0.2 改修対象) |
| `/mnt/c/Projects/hakudokai-dev/backend/etl/quartetto_extraction_rules.yaml` | 抽出ルール (v2.0 bump 対象) |
| `/mnt/c/Projects/hakudokai-dev/backend/tests/test_quartetto_pdf_parser.py` | 既存 unit test (AC-T5 で全 pass 維持) |

以上、cmd_004 機能② カルテッド PDF v0.2 検査値抽出精度向上 spec。
