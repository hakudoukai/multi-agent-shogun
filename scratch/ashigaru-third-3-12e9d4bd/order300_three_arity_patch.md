## §的 ★3 受け口版を patch に鋳り ＋ 8a23afa8a の main 到達を決める（当ては --check のみ）★
## §A 頭
- as_of 2026-09-11T11:08:29+0900 ／ 母 ＝ origin/main 50a9e20c3e978d2e ／ 令 ＝ order300_a3.txt 16行 501b764a4871fff1（己が刷つた）
- 打数 ＝ 讀取 6／12 ・ 焚 0（本弾では要さず）・ 走 0 ・ ★当ては --check のみ 4 回（-p1 2 ・ -p0 2）／ apply 0★ ・ 製品樹 書込 0 ・ DB 0 ・ cd 0 ・ redirect 0
- 讀んだ物 ＝ 8a23afa8a の当該 py ／ origin/main の当該 py と其の blob 符 ／ merge-base ・ branch -r の二形
## §B ㋐ 8a23afa8a の到達 ―― 三値 ＝ ★到達せぬ★
- 形1 ＝ merge-base --is-ancestor 8a23afa8a origin/main ＝ rc ★1★
- 形2 ＝ branch -r --contains 8a23afa8a ＝ 出力 ★0 行★
- ∴ ★blob は現に引ける（令299 で L4295-4383 を実読した）が 遠隔の枝には乗つて居らぬ★
## §C ㋑ 塊の扱ひ
- 8a23afa8a の当該 py L4295-4383（89 行）は ★己の紙へ一字も写して居らぬ★ ―― patch の中へのみ入れた（値・表示名を伏せる床は継続）
- 塊の末の空行 2 を剥がし 中身 ★87 行★ ＋ 区切りの空行 2 ＝ ★足す行 89★
## §D ㋒ 鋳た patch
- 名 ＝ order300_three_arity_restore_v1.patch（scratch/ashigaru-third-3-12e9d4bd/ の下）
- 足す先 ＝ origin/main の当該 py L12418 の直前（anchor を実物で当てた ＝ def _select_comment_template_key の頭）・令297 と同じ所
## §E ㋓ 実測
- 行数 ＝ ★98（wc）／ 99（split 片）★ ・ byte ＝ ★4,800★ ・ sha256頭16 ＝ ★dbf36ed5cf1c50fa★ ・ ★生の行末 ＝ LF（CR 0 行）★
- hunk ＝ ★1 つ★（@@ -12412,6 +12412,95 @@）・ 足す行 ＝ ★89★
- ★見積 99 行前後 との差 ＝ wc で −1 ・ split 片で ±0★（令299 §F の見積は当たつて居た）
## §F ㋔ apply --check
- 根 ＝ /mnt/c/DentalBI ・ 剥がし数 ＝ -p1（條493 に従ひ同じ行に）・ rc ★0★ ・ 出力 ★0 行★ ・ ★apply は打つて居らぬ★
- 併記 ＝ 母の blob 符 ＝ b23c0298ebfaf5c1（作業樹 HEAD の同 file と同符 ∴ --check が測る中身は origin/main と同じ）
## §G ㋕ 陽性対照（同じ patch ・ 同じ根 ・ 剥がし数のみ替へた）
- -p1 ＝ rc ★0★ ・ 出力 ★0 行★
- -p0 ＝ rc ★1★ ・ 出力 ★1 行★（b/ 付きの path が見付からぬ旨）
## §H ㋖ 締め
- 受け口 ＝ client ・ set_code ・ field_name（既定値 None）の ★3★
- harness L641 の渡し ＝ 2 ∴ 第三は既定値で埋まる形 ―― ★数は合ふ★
- harness L642 の渡し ＝ 3（位置3 ＝ None）∴ 第三へ直に None が入る形 ―― ★数は合ふ★
- ★「通る」とは書かぬ★ ―― 本弾は 走 0 ・ apply 0 ゆゑ 現に走らせて居らぬ（因の推し量りは書かぬ）
## §I 見込み（★本節のみ見込み★）
- 令297 の 2 受け口版（43行 67db351e5480d002）と 本弾の 3 受け口版（98行 dbf36ed5cf1c50fa）は ★同じ足す先を争ふ ∴ 二つを同時には当てられぬ★。何れを採るかは家老／監督の裁
## §J 繰越
- 8a23afa8a は遠隔の枝に乗つて居らぬ ∴ ★之を main へ運ぶ道は本弾では測つて居らぬ★
- 本弾で当てたは --check のみ ・ ★patch は二本とも当てて居らぬ★
