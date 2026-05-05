---
error_code: ERR-PDF-001
severity: WARN
title: "PDF 抽出/生成エラー"
auto_fix: true
retry_cap: 3
escalation: "inbox:shogun"
night_mode: defer
---

# Runbook: ERR-PDF-001 (PDF 抽出/生成エラー)

## 症状 (検知パターン)

- PDF テンプレートの読み込み失敗
- pdfplumber/reportlab によるパース・生成エラー
- 出力 PDF が空白 or 文字化け
- カルテ PDF のページ番号・レイアウト崩れ

## 自動診断コマンド

```bash
# 1. Python PDF ライブラリ確認
python3 -c "import pdfplumber; print(f'pdfplumber={pdfplumber.__version__}')" 2>/dev/null || echo "PDFPLUMBER_MISSING"
python3 -c "import reportlab; print(f'reportlab={reportlab.Version}')" 2>/dev/null || echo "REPORTLAB_MISSING"

# 2. フォントファイル確認
ls /usr/share/fonts/truetype/noto/ 2>/dev/null | head -5 || echo "NOTO_FONTS_MISSING"
ls /mnt/c/Windows/Fonts/msgothic.ttc 2>/dev/null || echo "MSGOTHIC_MISSING"

# 3. テンプレートディレクトリ確認
DENTALBI="/mnt/c/Users/User/Documents/DentalBI"
ls "${DENTALBI}/backend/templates/" 2>/dev/null | head -5 || echo "TEMPLATES_DIR_MISSING"

# 4. /tmp 空き容量 (PDF生成には一時ファイル必要)
df -h /tmp | tail -1 | awk '{print "TMP_USAGE=" $5}'

# 5. 直近エラー
grep -c "ERR-PDF" /tmp/fastapi-server.log 2>/dev/null || echo "0"
```

## 自動修復手順 (冪等、retry cap=3)

```bash
# Step 1: Python ライブラリ再インストール
pip3 install --quiet --upgrade pdfplumber reportlab 2>/dev/null
echo "$(date -Iseconds) PDF libraries reinstalled" >> /tmp/runbook_actions.log

# Step 2: /tmp クリーンアップ (古い一時 PDF 削除)
find /tmp -name "*.pdf" -mtime +1 -delete 2>/dev/null
find /tmp -name "diagnose_dump_*" -mtime +7 -delete 2>/dev/null
echo "$(date -Iseconds) /tmp cleaned" >> /tmp/runbook_actions.log

# Step 3: テスト生成
python3 -c "
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
c = canvas.Canvas('/tmp/test_pdf_gen.pdf', pagesize=A4)
c.drawString(100, 750, 'PDF Generation Test OK')
c.save()
print('PDF_GEN_TEST=OK')
" 2>/dev/null || echo "PDF_GEN_TEST=FAIL"
```

## 手動対応 (自動修復失敗時)

1. フォントファイルの存在確認・再インストール
2. テンプレートファイルの破損確認 (git checkout で復元)
3. Python 仮想環境の再構築: `pip install -r requirements.txt`
4. 見本カルテ PDF との比較テスト

## エスカレーション基準

- 診療時間中に PDF 生成不能 → ERROR 昇格 (カルテ印刷停止)
- テンプレートファイル消失 → ERROR (git からの復元必要)
- 通常は WARN レベル (次回操作で再試行可能)
