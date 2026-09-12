## §的 ★令340 の patch 二本を 総監督の GO の門へ出す一枚 ―― 当てる順序・戻しの形・当てた後の確かめを字で鋳る（当てず・適用せず）★

## §A 頭（条㉝）
- 母の ref ＝ origin/main／樹 ＝ /mnt/c/DentalBI（★讀取のみ★）／as_of ＝ 2026-09-12T15:07
- path ㊀ supabase/migrations/20260909170000 snapshot live public functions.sql（split 1318）／㊁ backend/utils/abbreviation checker.py（split 279）／㊂ tests/test abbreviations.py（split 141）―― 実 path は悉く下線形
- 網 ＝ 識別子境界（英数と下線を除く一字で挟む形）／器 ＝ order341 probe.py（席 dir 内・焚 1・残置）
- 前紙 order340 coalesce patch v1.md・v2.md と patch 二本は ★一字も書き換へず併記する★

## §㋐ 当てる順序 ―― ★py guard を先・3keys を後★
- 拠㊀ py guard 単独で落ちは悉く止む。反復するのは corrections（L171）と detail required（L220）の二鍵のみで、for 行に現れる鍵は此の二本だけ（実測）。両方とも本 patch が覆ふ
- 拠㊁ migration は ★DB へ適用するまで効かぬ★ ∴ file を置いた丈では振舞ひが一字も変はらぬ
- 選ばぬ道（3keys を先）の害 ＝ ⑴効かぬ窓が生じる ⑵其の窓の間 set cache 直挿しの経路は覆ひ無しの儘 ⑶「置いた」を「止んだ」と取り違へ得る

## §㋑ 戻しの形
- py guard ＝ apply の R で足る（既存 file・hunk 3・新規 file では無い）。戻し先の字 ＝ L168・L217・L245-L247 の三所
- 3keys ＝ file は apply の R で消える（新規 file ゆゑ）。★然し DB へ当てた後は file を消しても函は戻らぬ★
- ∴ DB を戻すには前の定義を撃ち直す要が有る。★前の定義の在り処 ＝ snapshot の L723（CREATE の頭）から L761（尻）まで 39 行・頭註は L722★
- migration 847 本を識別子境界で悉皆に当たり、此の函を CREATE するのは ★此の一本のみ★（言及は L21・L722・L723 の三行）

## §㋒ 当てた後の確かめ（三つ・各々に「之では言へぬ事」を添へる）
- ㊀ file の字 ＝ patch の符と当て先の行の一致 ―― 之では ★DB に当たつたかは言へぬ★
- ㊁ DB の函の定義を引く（pg get functiondef 等）―― ★DB 0 の床の下では己は測れぬ★ ∴ 名指すのみ。之では python 側が守られたかは言へぬ
- ㊂ 負テストの設計 ＝ set cache に三鍵とも null を差し 二函が例外を投げず空 list を返す事を見る。足す先 ＝ tests/test abbreviations.py（def 8 ＝ fixture 1 と試験 7）―― 之では DB 側の COALESCE が効いて居るかは言へぬ。★設計のみ・新設 0・走 0★

## §㋓ 当てぬ道
- 落ちを止めるだけなら ★py guard 一本で足る★（反復する二鍵を悉く覆ふゆゑ）
- 然し板 354dc26f の受入の逐語は 3 鍵に COALESCE である ∴ ★板の字を満たす道としては 3keys を外せぬ★
- ∴ 二本とも当てぬ道は ★無い★。一本で済ます道は在るが板の字を満たさぬ

## §㋔ 三値
- ⑴GO を仰ぐ形に成つた

## §㋕ 残弾（0 から数へ直した・新しく見えた物のみ 三）
- ㊀ supabase/migrations/proposals/ の副 dir が在る ∴ 刻の尻の測りは「直下」か「proposals 込み」かで変はる（令339・令340 で書いた尻 20260909170000 は ★直下★ の話である）
- ㊁ official 鍵は for 行に一度も現れぬ ∴ 今の code では official の null は落ちを生まぬ（当たりは L81 の len のみで Try 61-89 に覆はれる）
- ㊂ migration 847 本のうち此の函を CREATE するのは一本のみ（戻し先が一意である事の拠）

## §禁語
- > 網の語彙 ＝ password secret token api-key credential
- 生 1／境界の句と名を除いた数 0

## §床の実績
- 焚 1（order341 probe.py）／走 ＝ git の讀取動詞のみ／apply の check 0 回・apply 0 回
- 製品 code 書込 0／supabase 配下 書込 0／DB 0／MCP 0／install 0／find 0／rm 0／ssh 0／fetch 0／試験 0／他席の樹へ書込 0
