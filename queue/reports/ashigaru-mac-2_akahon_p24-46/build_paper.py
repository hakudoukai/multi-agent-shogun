# -*- coding: utf-8 -*-
"""裁きの jsonl 5本を束ね、母數との突合と件数を刷り、紙(md)を書く。usage: python3 -B build_paper.py <out.md>"""
import json, sys, glob, collections, datetime
from pathlib import Path
D = Path(__file__).parent
want = [int(l) for l in open(D / "conflict_pages.txt") if l.strip()]
recs = []
for f in ["adjudication_p24-46.jsonl"] + sorted(glob.glob(str(D / "adj_batch*.jsonl"))):
    for l in open(D / Path(f).name, encoding="utf-8"):
        if l.strip(): r = json.loads(l); r["_file"] = Path(f).name; recs.append(r)
got = collections.Counter(r["page"] for r in recs)
dup = sorted(p for p, n in got.items() if n > 1); miss = sorted(set(want) - set(got)); extra = sorted(set(got) - set(want))
dec = collections.Counter(r["decision"] for r in recs)
spot = [json.loads(l) for l in open(D / "spotcheck.jsonl", encoding="utf-8") if l.strip()] if (D / "spotcheck.jsonl").exists() else []
print(f"母數={len(want)} 記録={len(recs)} 重複={dup} 欠={miss} 余={extra}"); print("decision:", dict(dec))
recs.sort(key=lambda r: r["page"])
L = [f"# 赤本R8 衝突裁き Part24〜46 ―― 専任2 (ashigaru-mac-2)", "",
     f"- 板: 291cdd53 / 親 5b93a143 / 下命 seq359283・seq363994", f"- 作成: {datetime.datetime.now().astimezone().isoformat(timespec='seconds')}",
     "- 境界: 投入0・UPDATE0・`~/akahon-r8` 共有樹への書込0（overrides.jsonl / adjudications / reconciled 不触）。数値の再計算・補完はせず、原画像との相違を列記したのみ。", "",
     "## 母數と件数", "",
     f"- 母數 = Part24〜46 の qc.jsonl で tag=conflict かつ未 reconciled の頁 = **{len(want)}頁**（Part24/28/29/30/33 は前任の `_qc_reconciled.jsonl` が在るゆゑ除外・Part37 は conflict 0・Part25 は15頁悉く ai_missing で conflict 0）",
     f"- 記録 = {len(recs)} 行 / 重複 {len(dup)} / 母數に在つて記録に無い頁 {len(miss)} / 母數外 {len(extra)}",
     "- decision 内訳: " + " / ".join(f"{k}={v}" for k, v in sorted(dec.items())), "",
     "decision の意: AI=AI読みが原画像と一致(機械源の崩れ・偽の警報) / AI_要訂正=AI側が正だが具体の誤りあり(ai_errors に列記) / machine=機械源が正 / 両方欠=どちらも本文を欠く", "",
     "## 方法", "",
     "- 1頁ごとに `show_page.py`（読取専用）で qc 行・欠けた鍵・AI 本文を刷り、原画像 png を目視して突き合わせた。",
     "- 目視者: p376/377/379 は専任2 自身。残97頁は専任2 が起こした副 agent 4本（by 欄 `ashigaru-mac-2/subN`）。",
     f"- 抜取検: 専任2 が副 agent の記録 {len(spot)} 頁を原画像で再検 → " + ", ".join(f"p{s['page']}={s['result']}" for s in spot) + "（`spotcheck.jsonl`）", "",
     "## 偽の警報の主因（件数は記録から）", "",
     f"- 欠けた鍵が頁番号(ノンブル=page−142)のみ: 事前分類で 65頁。qc の `_keys` は頁下のノンブルも鍵に数へるため、AI がノンブルを写さぬと conflict に倒れる。",
     "- 裸の数字(例 120)と AI の『120点』は別鍵と数へられる。", "",
     "## AI 読みの繰り返す誤りの型（再抽出・後段 QC の的）", "",
     "- 『慢化』→『慢性』（傷病名 C3慢化 Per を悉く慢性へ）／片仮名『ロ』→漢字『口』・『□』",
     "- 結合セルの分割・行ずれ（表の点数や部位が隣の行へ／『—』化）",
     "- 段・頁の切れ目での文の重複、または頁末で切れた文の作文補完（例 p647/p653）",
     "- 欄外注『随時改定対象（令和8年4月の金属価格で試算）』・章題・Q&A 出典の脱落",
     "- 表に無い合計（『＝232点』等）の付加・原本誤植の黙つた訂正（p640）",
     "- 数値そのものの誤読は稀（p377 の行ラベルずれ・p651/666 の結合セル起因のみ）。", "",
     "## 判定の揺れ（軍師 mac に裁を仰ぐ）", "",
     "- p459 は sub4 が『両方欠』、p513/p519 は sub1 が『AI_要訂正』と記録した。三頁とも AI は表を正しく持つが解説・Q&A 等の領域を丸ごと欠き、機械源も崩れて居る＝同型。記録は書き換へず、どちらへ揃へるかを仰ぐ。いづれにせよ三頁は再抽出が要る。",
     "- 章題帯・頁上の節帯(例『H-①充填・インレー修復』)の欠落は、頁により記したり記さなかつたりして居る（sub2 自申）。数値・本文の突合には影響せぬが、帯の有無は全頁で揃つて検めて居らぬ＝未検。",
     "- 『随時改定対象（令和8年4月の金属価格で試算）』の欄外注の欠落は真の欠落（machine の 令和8年4月 鍵の出所）として AI_要訂正 に数へた（p640/658/664/665/668/679 等）。",
     "- p640: 原本自身の誤植『窩洞形式』を AI が黙つて『窩洞形成』へ直して居る（sub3 記）。忠実転記を採るなら誤り。", "",
     "## 別件: ai_missing", "", "- Part24〜46 の素の qc.jsonl で tag=ai_missing = 39頁（Part24:1/25:15/26:1/27:1/29:2/30:1/31:1/32:1/35:2/38:3/39:2/40:1/41:2/43:1/44:1/45:4）。うち前任が reconciled 済の Part24/29/30 の4頁を除くと 35頁。AI 読みそのものが無く、本裁きの対象外。再抽出が要る。", "",
     "## 頁ごとの裁き", "", "| 頁 | Part | 裁 | 根拠 | AI の誤り(原画像→AI) | 目視 |", "|---|---|---|---|---|---|"]
esc = lambda s: s.replace("|", "｜").replace("\n", " ")
for r in recs:
    L.append(f"| {r['page']} | {r['part']} | {r['decision']} | {esc(r['reason'])} | {esc(' ／ '.join(r['ai_errors'])) or '―'} | {r['by']} |")
Path(sys.argv[1]).write_text("\n".join(L) + "\n", encoding="utf-8"); print("wrote", sys.argv[1], len(L), "lines")
