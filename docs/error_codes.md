# エラーコード台帳

**目的**: トラブル時の短時間対応のため、全エラーに一意なコード採番。
**形式**: `ERR-{機能ドメイン}-{連番3桁}`
**改訂**: 信長直轄。新規エラー追加時は採番→台帳追記→コード反映の順。

## 機能ドメイン一覧

| ドメイン | 用途 | 採番範囲 |
|---------|------|---------|
| `EKARTE` | 電子カルテ入力・保存 | 001〜 |
| `AUTH` | 認証・認可 | 001〜 |
| `PDF` | PDF生成・テンプレート | 001〜 |
| `WATCHER` | watcher / receiver 系 | 001〜 |
| `SUPABASE` | Supabase 通信 | 001〜 |
| `CARTE` | カルテット連動 (.REQ/.TAB) | 001〜 |
| `INFRA` | インフラ層 | 001〜 |
| `KANBAN` | カンバン UI | 001〜 |
| `RECEPTION` | 受付・QRチェックイン | 001〜 |
| `BILLING` | 算定・請求 | 001〜 |
| `PASSPORT` | 恐竜王国パスポート | 001〜 |
| `HANDOVER` | 申し送り A4 | 001〜 |
| `CRM` | 患者CRM | 001〜 |
| `AUDIT` | 監査ログ | 001〜 |
| `MEISAI` | 明細入領収証 PDF 抽出基盤 | 001〜 |

## エラー定義

> ⚠ 本台帳は実装と完全同期せねばならぬ。新規エラー追加時は必ず採番してから実装すること。

### サンプル（実装時の雛形）

#### ERR-EKARTE-001
- **発生条件**: ekarte 入力時、Supabase visit 作成失敗
- **重要度**: ERROR
- **メール通知**: あり (system-admin宛)
- **ユーザー表示文言**: 「カルテの記録に失敗しました。再試行してください。」
- **対処法**:
  1. Supabase 接続確認 (`curl /api/health`)
  2. ローカルSQLite フォールバック動作確認
  3. `backend/api/ekarte_records.py` の `create_visit` ログ確認
- **発生時 dump 取得項目**: patient_id, clinic_id, visit_date, payload
- **関連 corr_id 検索**: dashboard "ERR-EKARTE-001 last 7days"

#### ERR-WATCHER-001
- **発生条件**: watcher の retry 上限到達 (5回失敗)
- **重要度**: ERROR
- **メール通知**: あり
- **ユーザー表示文言**: （ユーザー画面表示なし、内部通知のみ）
- **対処法**:
  1. `/tmp/<watcher名>.log` の最新50行確認
  2. dead-letter テーブル (pc_handshake.dead_lettered_at IS NOT NULL) の該当ID確認
  3. メッセージ内容を精査し、必要なら手動 ack または再送
- **発生時 dump 取得項目**: message_id, retry_count, last_error, full_payload
- **関連 corr_id 検索**: dashboard "ERR-WATCHER-001 last 24h"

#### ERR-CARTE-001
- **発生条件**: カルテット結果 (.TAB) 取込時の reconcile 失敗（DentalBI入力との齟齬）
- **重要度**: WARN（手動確認が必要、自動でクラッシュはしない）
- **メール通知**: なし（dashboard.md と患者画面バッジで表示）
- **ユーザー表示文言**: 「カルテットとの照合で差異が見つかりました。確認してください。」
- **対処法**:
  1. 患者画面の「カルテット差分」バッジから詳細表示
  2. DentalBI 入力 vs カルテット結果の差分一覧確認
  3. 正しい方を選択して再送信
- **発生時 dump 取得項目**: visit_id, dentalbi_data, quartetto_data, diff_summary

#### ERR-MEISAI-001
- **発生条件**: 明細入領収証 PDF が見つからない / 入力パスがファイルでない / Storage 経由取得失敗
- **重要度**: ERROR
- **メール通知**: なし (dashboard.md 表示)
- **ユーザー表示文言**: 「領収書 PDF を取得できませんでした。再試行してください。」
- **対処法**:
  1. Supabase Storage `receipts/{clinic_id}/{patient_no}/{visit_date}.pdf` の存在確認
  2. テンプレート `assets/明細入領収証.pdf` の存在確認 (fallback render 経路)
  3. `backend/api/meisai_receipt_api.py` の構造化ログ + corr_id を追跡
- **発生時 dump 取得項目**: clinic_id, patient_no, visit_id, visit_date, object_path, source
- **関連 corr_id 検索**: dashboard "ERR-MEISAI-001 last 7days"

#### ERR-MEISAI-002
- **発生条件**: pdfplumber が PDF を解析できない (corrupt bytes / 空ページ / retry 3回失敗)
- **重要度**: ERROR
- **メール通知**: なし (dashboard.md 表示)
- **ユーザー表示文言**: 「領収書の解析に失敗しました。時間をおいて再試行してください。」
- **対処法**:
  1. `/tmp/meisai_receipt_extractor.health` で extracted_total / failed_total 確認
  2. 失敗 PDF の sha256 / file size 確認
  3. retry cap = 3, backoff (0.1/0.3/0.7s) を超える障害は上流側 (renderer / storage) を調査
- **発生時 dump 取得項目**: file_hash, source, retry_count, last_error
- **関連 corr_id 検索**: dashboard "ERR-MEISAI-002 last 24h"

#### ERR-MEISAI-003
- **発生条件**: 患者本人 / 医院関係者でない JWT が `GET /api/receipts/{patient_id}/{visit_id}` を呼んだ
- **重要度**: WARN (RLS で正常に弾かれた状態)
- **メール通知**: なし
- **ユーザー表示文言**: 「対象の領収書を取得する権限がありません。」
- **対処法**:
  1. JWT の sub と karte_visits.clinic_id / patient_no の整合性確認
  2. patient_receipt_pdfs RLS policy (`receipts_staff_sel` / `patient_receipt_pdfs_sel`) を再確認
  3. 攻撃と判定される頻度であれば `audit_log` で送信元 IP を集計
- **発生時 dump 取得項目**: jwt_sub, clinic_id, patient_no, visit_id
- **関連 corr_id 検索**: dashboard "ERR-MEISAI-003 last 7days"

#### ERR-INFRA-001
- **発生条件**: pc_handshake テーブルの unack 件数が閾値（10件）超過
- **重要度**: CRITICAL
- **メール通知**: あり (理事長宛 + 管理者宛)
- **ユーザー表示文言**: （内部監視のみ、ユーザー画面なし）
- **対処法**:
  1. `docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md` を必ず参照
  2. unack内訳: `SELECT topic, COUNT(*) FROM pc_handshake WHERE acknowledged_at IS NULL GROUP BY topic`
  3. self-send / heartbeat / 暴走 watcher を疑う
- **発生時 dump 取得項目**: unack_count, top_topics, current_watcher_pids
- **関連 corr_id 検索**: dashboard "ERR-INFRA-001 last 7days"

---

## 採番規則

1. **採番禁止**: 既存番号の上書き・再利用 絶対禁止
2. **削除時**: コード削除でなく `[DEPRECATED]` プレフィックスを付与し、台帳に残す
3. **改訂**: 信長承認後、git commit で履歴を残す
4. **連番枯渇時**: 999 まで埋まったら新カテゴリ採番（例: `EKARTE2`）
5. **国際化**: コード自体は英数字のまま不変。エラー文言のみ多言語化

## 関連ドキュメント

- [CLAUDE.md §Error Design & Observability Mandate](../CLAUDE.md) — 設計原則
- [CLAUDE.md §9 エラーコード体系](../CLAUDE.md#9-エラーコード体系) — 本台帳の規約
- [docs/audit-framework.md §5 ジェミちゃん監査](./audit-framework.md) — observability_error_handling 観点
- [scripts/diagnose.sh](../scripts/diagnose.sh) — 診断ツール（実装予定）

---

## 追記: 符号体系の確定と新符号 (裁定235802⑵ / 2026-09-02 將軍third)

**本節は追記のみ。上記の既存行は一字も改めて居らぬ**（追記前 SHA256 = `6f0cca88f79f9ed895f5ec3fc5e9023615a7f76f325907c8709af9c89321fea2` / 7076 bytes、本 file の先頭 7076 byte は之と一致する）。

### 符号体系（確定）

- **形式**: `ERR-{ドメイン}-{3桁}` ―― ドメインは大文字英字、連番は 3 桁固定（`001`〜`999`）。
- **ドメイン**: 上記「機能ドメイン一覧」の 15 種を正とする。新ドメインの追加は本台帳の表への追記を以て行ふ（表の既存行は改めぬ）。
- **採番手順**: ①当該ドメインの最大連番 +1 を採る ②本台帳へ定義を追記する ③実装へ反映する ―― 順序を入れ替へてはならぬ。
- **再利用禁止**: 一度採つた番は削除しても再利用せぬ（既存「採番規則」1・2 に従ふ）。
- **区別**: 本符号は**製品面のエラー**に用ゐる。運用機構（配送器・監査器）の疵も、症状が現場に出る限り `INFRA` として採番してよい。

### 新符号

#### ERR-INFRA-002
- **発生条件**: 送信器が exit=0 を返したにも拘らず、便が受け手の箱に落ちて居らぬ（判定が標準出力の末尾一行に依存する為、死んだ経路でも緑と読める）
- **重要度**: ERROR
- **メール通知**: なし（上位席への便で報ずる）
- **ユーザー表示文言**: （内部機構ゆゑ患者向け文言なし）
- **対処法**:
  1. 受け手の箱を直に読み、当該便の id が在るかを確かめる（exit code を着弾の証に使はぬ）
  2. 落ちて居らねば、経路（宛先の箱名・別名解決）を確かめる
  3. 死箱であれば DEAD-INBOX-GATE の提示する正経路へ差し替へる
- **測定根拠**: 送信器の判定が末尾一行に依る事を實読で確認（將軍third・2026-08〜09）

#### ERR-INFRA-003
- **発生条件**: `git check-ignore --no-index` が大量 file 入力で異常終了し、判定不能が「0 件」として集計される
- **重要度**: WARN
- **メール通知**: なし
- **ユーザー表示文言**: （内部機構ゆゑ患者向け文言なし）
- **対処法**:
  1. 異常終了の有無を rc で分け、**「否」と「器の落ち」を同じ rc で受けぬ**
  2. 落ちた区間は「測定不能」と明記し、0 件と混ぜぬ
  3. 入力を分割して再測する
- **測定根拠**: git 2.43.0 にて約 4000 file で異常終了（index 窓 90000..94999、呼出 7982）を實測（將軍third・2026-09-02）

#### ERR-INFRA-004
- **発生条件**: 読手の去つた箱（死箱）へ便を書込み、機械上は成功するが誰にも読まれぬ
- **重要度**: ERROR
- **メール通知**: なし
- **ユーザー表示文言**: （内部機構ゆゑ患者向け文言なし）
- **対処法**:
  1. DEAD-INBOX-GATE の拒否と提示経路に従ふ（迂回の環境変数を用ゐぬ）
  2. 宛先の箱名を `ls -1 queue/inbox/` で実在確認してから送る
  3. 送出後は必ず読返しで宛先を確かめる（送信器の宛先表示を証に使はぬ）
- **測定根拠**: 死箱への書込を拒否する関門が導入済である事、及び読手不在の箱が現に在る事を實測（將軍third・2026-09）
