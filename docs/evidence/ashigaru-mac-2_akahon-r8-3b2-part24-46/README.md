# 段3b-2 衝突裁き Part24〜46 (赤本R8・板 291cdd53)

担当: ashigaru-mac-2(專任2・CC 足軽) ／ 発: goal file 2026-09-25 02:46(事業部長 fukuincho)
旧束: `queue/reports/ashigaru-mac-2_akahon_p24-46/`(100頁・記録は書き換へず本束へ取り込む)

## 母數
- 現 qc(mtime 2026-09-24 21:38〜39)で reconciled 無 Part の conflict = **112頁**(`_ki/remeasure.out`)。
- 旧束 100頁 ＋ 現 qc で新たに conflict に成った Part25 の12頁(361,363〜366,368〜373,375)。旧−現 = 0。
- 詳細と除外(reconciled 有 Part の 22頁・overrides/adjudications 交差 0)は `raw/input_note.txt`。

## 方法
- 各頁の原画像(`out/akahon/png/赤本R8_pNNNN.png`)を目視し、AI 本文・機械源(layer/ocr)の鍵と突き合はせた。
- 判: `AI`(AI 本文が原画像と一致)／`AI_要訂正`(AI が正しい側だが誤りあり・`ai_errors` に原画像逐語)／`両方欠`／(`machine` は0件)。
- 追加12頁は專任2 自身が直に目視(`adj_part25_add.jsonl`・器 `_ki/write_part25_add.py`)。旧100頁の by は `judgments_part24-46.tsv` の by 欄のとほり(自3・副agent 97)。

## 結果(`judgments_part24-46.jsonl` / `.tsv`・器 `_ki/combine.py`・`_ki/combine.out`)
| 区分 | AI | AI_要訂正 | 両方欠 | 計 |
|---|---|---|---|---|
| 全 | 26 | 85 | 1 | 112 |
| 旧束 | 24 | 75 | 1 | 100 |
| 追加(Part25) | 2 | 10 | 0 | 12 |
- machine を採った頁は 0。欠けた鍵の大半は頁番号(ノンブル)の偽警報。
- 追加12頁の主な誤り: 歯式の区切り線消失(366/368/375)・章題脱落(364/372/375)・語の脱字/誤読(361/363/365/369/370/372)。

## 突合
- `combine.py` が judgments の頁集合と現 qc の conflict 集合を突合: 重複0・未裁0・余剰0(assert 通過・rc=0)。

## 検め・未決
- 抜取検: 旧束の副agent 記録4頁を原画像で再検=4/4 一致(旧束 `spotcheck.jsonl`)。
- **仰ぎ**: p459(`両方欠`)と p513/p519(`AI_要訂正`)は同型(AI は表を持つが解説・Q&A を丸ごと欠く)で判が割れて居る。記録は書き換へず、どちらへ揃へるか家老の裁を仰ぐ。三頁とも再抽出が要る。
- 章題帯の欠落の記し方は頁により揃つて居ない(旧束 sub2 自申)=未検。

## 禁の遵守
- upload 0・DB UPDATE 0・`~/akahon-r8` への書込 0(読取のみ)・push/PR 0。歯式6file・design tokens・本番・secret に触れず。
- 本束を含む commit の40桁は納便で宣する(紙は己を含む commit を書けぬ)。
