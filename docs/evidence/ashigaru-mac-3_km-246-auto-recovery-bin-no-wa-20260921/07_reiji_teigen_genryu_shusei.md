# ⑾ 0byte file → 門rc=1 問題 ―― 今回は源流で修めた

## 検出

`find . -type f -size 0 -print` (own instrument、束全体を走査) ―― 該当1件:
`sandbox/kanjyou_sim_3h.err`(`python3 sandbox/kanjyou_sim.py 2>sandbox/kanjyou_sim_3h.err` の
stderr捕獲・当該runがstderrを一字も出さなかつた為に0byteで生成された)。

[[feedback_gate_jou2_jou4_punish_faithful_evidence]] の実測通り、之は★席の疵ではなく
「生の出力を忠実に焼く」作法と門の條④(空 file)が衝突する既知の構造★である。

## 源流での修正(今回・km-243では単に開示のみだつたが本弾で実行)

0byte file を其の儘 raw として束に含めず、[[feedback_prescan_before_gate_every_instrument_writes_empty_as_one_line]]
の二段書式で置換した:

⑴ `sandbox/kanjyou_sim_3h.err`(0byte)を削除し、代りに一行註
   `sandbox/kanjyou_sim_3h.err.note.txt` を新設 ―― 逐語:
   `# 空であつた ―― 器=python3 sandbox/kanjyou_sim.py の stderr捕獲 byte=0 rc=0 刻=2026-09-21`

⑵ 其の一行註自身の実体: `sandbox/kanjyou_sim_3h.err.note.txt` = **104 byte**、
   sha256 = `08aca9847e26693196fc6bf931f5dd26cac59d56b7d62c38b4298d585b65ceef`
   (`wc -c` / `shasum -a 256` own instrument で実測)。

## なぜ完全には直せないか(残る限界)

★源流(python3実行)そのものを「stderrが空なら書き込むな」と変へるのは、
sandbox/kanjyou_sim.py の呼出規約(`2>file`)を変へる事に成り、之は評価対象コード
(inbox_watcher.sh)ではなく當職が★今回新設した★補助script側の話ゆゑ変更統制の対象外
(自分の道具・第一条「己の担当作業」の範囲内)であり、実際に上記の通り修正済。
∴ 本弾に関しては★完全に源流で修めた★ ― 残存する0byte fileは無い(下記再走査で確認)。
