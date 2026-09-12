## §的 ★patch を当てず 今の code が現に落ちる事を raw で示す ―― 負對照と其の対照（値 0 字・患者の字 0 字）★

## §A 頭（条㉝）
- 樹 ＝ /mnt/c/DentalBI（★讀取と取り込みのみ・書込 0★）／HEAD ＝ 53412b7bcda2f8ae／origin/main ＝ 0dba78e8de65ad59
- 当該 file は origin/main と ★差 0 行★（numstat の行 0）∴ 取り込んだ字は ref の字と同じ
- as_of ＝ 2026-09-12T15:23／親令 ＝ order342 a3.txt 28 行・符 sha256 先16 fd19d82e1ed23638／BASE ＝ a08cfcdb5138465a
- ★網の逐語（三つ）★ ＝ ㊀847 ＝ supabase/migrations 配下を ★再帰★ に取つた ★全 file★（拡張子を問はぬ）／㊁840 ＝ 同じ再帰の ★.sql のみ★／㊂778 ＝ ★直下（再帰せず）の .sql のみ★
- 三つとも ★己の網で数へ直し★ 家老の数と悉く一致した。令341 で己が書いた 847 は ㊀ の網である（条㉜に依り以後は数の傍に網を置く）
- 此の函を CREATE する file は ★一本のみ★・言及 3 行 ―― 己の網で再確認した
- 器 ＝ order342 negctl.py（席 dir 内・焚 1・残置）／走 ＝ 1 回（産出が出た ∴ 二度目は撃たず）

## §㋐ 撃つ前の門（撃つ前に字で確かめた）
- ⑴DB を叩くか ＝ ★叩かぬ★。RPC は L62-L71 と L108-L117 の二函の中のみ。負對照が呼ぶ二函は cache しか讀まぬ（L165-L168・L214-L217）
- ⑵env を要するか ＝ ★要らぬ★。但し L28-L29 が取り込みの時に dotenv を撃つ ―― ★己は env の鍵名も値も一切讀まず紙へも写して居らぬ★。逃げ道の env は一つも置いて居らぬ
- ⑶他の重い物 ＝ httpx と dotenv を頭で引く。無ければ取り込みが落ちる（門の唯一の懸念）―― 実測 ★通つた★

## §㋒ 負對照（raw）
- 場 A ＝ 三鍵とも null を set cache に差した（★陽性★）
- check unofficial abbreviations → 例外の型 ★TypeError★・落ちた行番 ★L171★・末尾 3 行 ＝ file と 171 と函名／for entry in corrections:／TypeError: NoneType object is not iterable
- check disease abbreviation detail → 例外の型 ★TypeError★・落ちた行番 ★L220★・末尾 3 行 ＝ file と 220 と函名／for abbr in detail required:／TypeError: NoneType object is not iterable

## §㋒-2 対照 ―― ★null と 不在は別★
- 場 B ＝ 三鍵とも ★不在★ → 二函とも例外 0・list を返し長さ 0 ∴ get の第二引数の既定が効く
- 場 C ＝ 三鍵とも空 list → 二函とも例外 0・長さ 0
- 場 D ＝ cache を clear → 二函とも例外 0・長さ 0（L165 と L214 の早期の戻り）
- ∴ 0 が出た所に陽性（A）と陰性（B・C・D）の両方を置いた。★落ちるのは値が null の時だけであり 鍵の不在では落ちぬ★

## §㋓ 三値
- ⑴★現に落ちる★（二箇所とも・例外の型は TypeError）
- 之では言へぬ事 ＝ ㊀実の DB が現に null を返すかは言へぬ（DB 0）／㊁本番の呼手が此の道を通る頻度は言へぬ／㊂patch を当てた後に場 A が例外 0 に変はるかは言へぬ（正對照は本弾の外）

## §㋔ 正對照の形（設計のみ・一行）
- py guard を当てた後に同じ器を同じ四場で撃ち 場 A が例外 0・長さ 0 に変はる事を見る（走らせて居らぬ・新設 0）

## §㋕ 残弾（3 から数へ直した・新出 二）
- ㊃ 作業樹の HEAD は origin/main と別の commit である（当該 file は差 0 行ゆゑ本弾に害は無い）／㊄ 取り込みの時に dotenv が撃たれる ∴ ★DB 0 と env に触れぬは別の事★ である

## §禁語
- > 網の語彙 ＝ password secret token api-key credential
- 生 1／境界の句と名を除いた数 0

## §床の実績
- 当て 0／apply の check 0／製品 code 書込 0／supabase 配下 書込 0／DB 0／MCP 0／install 0／fetch 0／find 0／rm 0／ssh 0／/mnt/c 書込 0
- 焚 1／走 1（上限 1・二度目は撃たず）／試験 0（pytest を一度も起こして居らぬ）／前紙は一字も書き換へて居らぬ
