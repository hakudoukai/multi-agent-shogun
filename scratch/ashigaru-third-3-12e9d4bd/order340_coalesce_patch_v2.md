## §的 ★令340 v2 追補 ―― SQL の COALESCE だけで L171/L220 の落ちが止むかを字で測り 要る手当てを patch に鋳る（当てず・適用せず）★

## §A 頭（条㉝）
- 母の ref ＝ origin/main／樹 ＝ /mnt/c/DentalBI（讀取のみ）
- path ㊀ ＝ backend/utils/abbreviation checker.py ―― 実 path は下線形（wc 278／split 279）
- path ㊁ ＝ supabase/migrations/20260909170000 snapshot live public functions.sql（令340 本体で測り済）
- as_of ＝ 2026-09-12T14:57
- 網㊀ ＝ 識別子境界 ―― 英数と下線を除く一字で挟む形／網㊁ ＝ 字面 get の直後の丸括弧
- 器 ＝ order340b probe.py（讀み）／order340c pypatch.py（鋳り）―― 二本とも席 dir 内・焚 2
- patch ＝ order340 py guard.patch（席 dir 内）
- 前紙 order340 coalesce patch v1.md は一字も書き換へず併記する

## §零 追補の受け
- 総監督裁 hs 25a1eba2 ㊂ の字（板の受入⑴が len でなく L171/L220 の落ちへ直る）は家老の便の逐語を写した。★己は板の字を讀んで居らぬ ∴ 確かめて居らぬ★
- 令339 v2 の己の実測（len の当たり L81-L83 は Try 61-89 に覆はれ 落ちは呼手へ伝はらぬ／現に届く落ちは L171 と L220）は己が当たつた

## §㋑-3 追加項の答 ―― ★SQL の COALESCE だけでは止まぬ・python 側の手当ても要る★
- 拠㊀ L168 と L217 は get の第二引数に空 list を置く形である。此の既定値は ★鍵が無い時にのみ★ 効く。鍵が在つて値が null なら None が返り L171／L220 の反復が落ちる
- 拠㊁ 正規化器 normalize rpc result の L245・L246・L247 も同じ形 ∴ RPC が null を返せば素通しする
- 拠㊂ set cache（L131-L135）は無検査で辞書を差し込む ∴ DB を経ずに null 入りの値が cache へ入る道が残る。tests/test abbreviations.py L54-L58 の autouse fixture が現に此の道を通る
- ∴ SQL の COALESCE が塞ぐのは ★RPC の出口ただ一つ★ であり L171／L220 に届く値の出所を悉くは覆はぬ

## §測り（己が当たつた行・origin/main）
- 三鍵の識別子境界の当たり ＝ official 5 行（42,80,81,238,245）／corrections 7 行（43,80,82,168,171,238,246）／detail required 7 行（44,80,83,217,220,238,247）
- 字面 get の直後の丸括弧 ＝ 12 行。うち三鍵に係るは L81,L82,L83（len の中）・L168・L217・L245,L246,L247 の八本
- 空の辞書を返す empty rules（L236-L238）は三鍵を悉く空 list で置く ∴ 例外経路（L59・L89・L105・L128）からは null が来ぬ
- cache を讀む口は L165-L168（check unofficial abbreviations）と L214-L217（check disease abbreviation detail）の二つのみ

## §patch（席 dir 内・当てず・適用せず）
- order340 py guard.patch ―― 32 行／1,157 B／符 sha256 先16 8e10480b81ebdf9d／削 5 足 5／hunk 3（L165-L171・L214-L220・L243-L249）
- 直し ＝ 三箇所の get の第二引数の空 list を 落として or の形へ移す（None も空も悉く空 list に落ちる）
- anchor は器の中で origin/main の実物と一字一句の一致を先に確かめてから組んだ（三本とも一致・実測 ANCHORS OK=3）
- ★当ては確かめて居らぬ★ ―― apply の check の弾は令340 本体で上限 2 回を撃ち尽くした ∴ 本 patch には一度も撃つて居らぬ
- 前の patch order340 coalesce 3keys.patch（48 行・符 bac29134242ea12e）は不触。二本は ★併せて当てる★ 形（SQL が入口を塞ぎ python が出口を守る）

## §㋓ 三値 ―― patch は GO の門へ出せる形に成つたか
- ⑴成つた（二本とも席 dir 内・repo へは一字も書いて居らぬ）。★但し python 側の一本は当ての検査を撃つて居らぬ★

## §禁語
- > 網の語彙 ＝ password secret token api-key api underscore key credential
- 生 1／境界の句と名を除いた数 0

## §床の実績
- 焚 2（order340b probe.py・order340c pypatch.py）／走 ＝ git の讀取動詞のみ／apply の check 0 回
- DB 0／MCP 0／製品 code 書込 0／supabase 配下へ書込 0／install 0／find 0／rm 0／ssh 0／fetch 0／試験 0
- 他席の樹 /home/hakudoukai/a1/wt-handover-fe-2 へは一字も書いて居らぬ
