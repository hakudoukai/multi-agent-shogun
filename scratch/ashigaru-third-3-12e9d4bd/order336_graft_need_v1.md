## §的 ★押枝が別の手で同じ役を果たして居るかを測り 移植の要否を分ける★

## §A 頭（条㉝ ―― 母の ref と path を逐語で・as_of・網の逐語・数）
- 母の dir の path（逐語）＝ /mnt/c/DentalBI ―― 作業樹（CRLF の系）。測りは悉く git の讀取動詞で ref から取り 樹の file は一つも開いて居らぬ
- 押枝 ref（逐語）＝ karo-third/fa06a3a1-treatment-validation-20260912（tip a6c73b30eb01d2b0・本紙で引いた行番 L13064）
- 原器 ref（逐語）＝ 7f39168d3（符 7f39168d3c064bd4・本紙で引いた行番 L4668）
- 母の file（逐語）＝ backend/api/treatment_validation.py ／ as_of ＝ 2026-09-12T13:35
- > 網の逐語㊀ def の網 ＝ 行頭の空白の後に async を任意で挟み def と一つの空白を置く形
- > 網の逐語㊁ field id の網 ＝ field と id を任意の一字で繋ぐ形（大小文字を問はぬ）
- > 網の逐語㊂ documentation の網 ＝ documentation の逐語
- 形の測りは ast（床31）・行数は wc と split の併記（床32）・焚は 1（ast の器を python で一度起こした）

## §㋐ 母を数へ直した（網＝§A の網㊀・体系＝本紙 §㋐）
- 押枝 総 15100 行 ／ def 総数 251 ／ save_treatment は L13064 の 1 本 ―― 三つとも家老の先測と当たつた
- 原器 総 5687 行 ／ def 総数 152 ／ save_treatment は L4668 の 1 本 ―― 三つとも当たつた
- ★己が足した母★ save_treatment の域を ast で取り直す ―― 押枝 L13064-14983 ＝ 1920 行 ／ 原器 L4668-5570 ＝ 903 行
- ★自己申告★ 令335 の紙（符 88f5bc4955563b9b）で己は押枝の域を L13064-14988 ＝ 1925 行と申告した。之は次の字下げ 0 の行までを目で切つた数であり ast の 1920 行と 5 行違ふ。前紙は書き換へず本紙に併記する（作法九条・令321）

## §㋑ 押枝の save_treatment の中に field id を解く処理が何行在るか（体系＝本紙 §㋑・網＝§A の網㊁㊂）
- field id の網の当たり ＝ ★0 行★（域 L13064-14983 の中）
- 押枝の file 全体でも field id の網は L12444 と L12448 の 2 行のみ ―― 是は移植した def の頭部（def の域 L12444-12530 ＝ 87 行）
- documentation の網の当たり ＝ 4 行（L14776・L14875・L14881・L14906）・宛の函名 ＝ required_documentation_fields を讀む処理
- ★同じ 4 行は原器の save_treatment にも在る（L5440・L5462・L5468・L5493）★ ∴ 押枝に固有の手ではない
- 押枝の save_treatment が呼ぶ名で原器の save_treatment に無い物 ＝ 49（内 本 file に def を持つ物 37・残 12 は組込か卓の method）
- 其の 37 の本文に field id の網が当たる物 ＝ ★0★
- documentation の網が当たる物 ＝ 2 ―― 函名 _compose_r4_p_same_day_support_items（L822・域 1241 行）／_conditions_for_request（L5567・域 90 行）・両者とも field id の網 0
- ★到達★ 押枝の save_treatment から辿れる def ＝ 216（本 file の def 総数 246 の内）・移植した _resolve_comment_documentation_field_id は ★辿れぬ★・本 file 内の呼手 0・module 級の言及 0

## §㋒ 原器 L5152 の呼手（令335 の測りを引いた・本弾で再測せず）
- 宿函 ＝ save_treatment（原器 L4668）・引数 ＝ 3 ―― 出所は本席の紙 order335_caller_gap_v1.md（符 88f5bc4955563b9b）

## §㋓ 三値
- ★⑵果たして居らぬ（∴呼手の追加が要る）★
- 因㊀ 原器では required_documentation_fields の 4 行と L5152 の呼手が★併存★して居る ∴ 其の 4 行は呼手の代はりに非ず
- 因㊁ 押枝にのみ在る呼手 49 名の内 field id の網に当たる本文を持つ物 0（§㋑ の数）
- 因㊂ 移植した def は押枝の save_treatment の到達集合 216 に入らぬ・本 file 内の呼手 0
- ★測れぬ一点（分けて書く）★ 別 file・別 module が同じ役を果たす見込みは本 file の ast では測れぬ。令335 で新函名を押枝の全樹に当てた時は 2 本（api 1 ＝ def ／ harness 4）で 名の上では他に無い。而して「名の違ふ別函が同じ役を果たすか」は名では測れぬ

## §㋔ 残弾
- 3 から本弾を撃つ ∴ 残 2

## §禁語（網の逐語は令の側が渡した）
- > password / secret / token / api-key / api_key / credential
- ㊀ 生の数（網を掛けた儘・己の宣言行を含む）＝ 1 ／ ㊁ 境界の句と名を除いた数 ＝ 0

## §床の実績
- 走 0 ／ 当て 0（apply は --check も打たず）／ DentalBI へ書込 0 ／ git は讀取動詞のみ（show と rev-parse）／ DB 0 ／ ssh 0 ／ find 0 ／ 他席の箱と archive と家老の箱を開く 0 ／ as_of 2026-09-12T13:35
