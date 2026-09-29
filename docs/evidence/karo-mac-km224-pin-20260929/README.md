# KM-224: 現在の門の版とpin案（Mac家老）

- Board: `f1c9b1b5-6990-4491-ad41-dceb32ed048e`。今回読み戻し: `assigned`, `assigned_pc=mac_pc`, `owner_role=karo-mac`。受入条件はdisk/HEAD/mainの門SHA三様を実測しpin案を示すこと。
- 固定参照：前回の専任3提出 `fbdf94cad7b976f31e29b869735dfdaacf23ce60`（reports/evidence/km-224-mon-sanyou-saisoku-20260926）。そのREADMEとraw 5点をこの束へ無改変複写。原本ハッシュは `SHA256SUMS` と `raw/05_previous_blob_digests.txt` を参照。
- 今回の再確認: `origin/main` tip `b9573b2d376e9a0a372234b696a733677feb7919` の対象gate blob=`04672e15b1edf4a02b7cea1f4f32cfb9a64e34d5`。固定ref HEAD `10000ff89716da925a14ff6e6fed57e626fbf8ee` のgate blob=`9cd550fc2cf963ca0475b3448bb33483b9aede6b`。両blobの内容を採取してsha256/bytes/line数を再計測し、rawに保存。
- Shared-tree disk版の前回報告値はSHA `2b8449bccd608a1a7f24c888b2e1857ad2af98065fdfb1d3077bf08cdbe6f685`（blob `054c442eaee3886b2283f98f7c3a1ab8cb813b68`）。今回は共同作業treeの未追跡・変更物を誤編集しないためdisk対象を直接再読せず、再測値としては主張しない。よって今回のdisk/HEAD/main三者完全再測定は未了。

## pin提案

1. 実行命に、正のref（例: `origin/main` の固定tipまたは明示許可された別正本）とblob40/full SHA-256を記す。
2. 門を `git cat-file blob <blob40>` で専用artifact/worktreeへ取り出し、実行直前にblob/SHA/bytesが命の値と一致する場合だけ実行。異なる時はfail-closedし、共有diskの門へfallbackしない。
3. 実行した門blob・SHA・測定時刻を当該成果束に記録する。
4. shared-tree disk gateの更新は器/共有treeの変更に当たるため、変更統制の別承認・実施者へ切り分け、本作業では行わない。

## 検証境界

本runで固定refのHEAD/main二者は独立再測。共有disk値は前回固定束からの参考値であり、今回の三者同時再測ではない。gateの実行、別ref全体のcensus、shared tree/diskへの変更は行っていない。改変・push・merge・DB適用なし。
