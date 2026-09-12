## §的 ★令339 追補（床は一字も変へず材料を足す）―― 正対照の併記と len の当たりを行番で当てる★

## §A 頭（条㉝）―― 前紙との関係・母の ref と path・as_of
- 本紙は v2 ＝ ★前紙 order339 coalesce need v1.md（本文 39・wc 50・符 sha256 先16 db83905d0927936b・tip16 6c698e3b274c3053）を一字も書き換へず併記して立てた紙★
- 追補の令（家老 14:30:59・便 id msg 20260912 143059 4f2da156）の逐語 二点 ＝ ㊀板の逐語に正対照が在る（get defense checks は COALESCE 済・家老main隊 a-2 実測 296643）∴ ㋑-2 に併記せよ ㊁板の主張の逐語（該当行 0 の日に NULL で返り消費側の len が落ちる）∴ ㋒ は len の当たりを行番で当たれ
- 母の ref（逐語）＝ origin/main ／ dir path（逐語）＝ /mnt/c/DentalBI ／ fetch は撃たず在る儘を讀んだ ／ 測つた tip16 ＝ 5722708374826c11（v1 と同じ）
- 消費側の path（逐語）＝ backend/utils/abbreviation checker.py（278 行・split 片 279）／定めの path（逐語）＝ supabase/migrations/20260909170000 snapshot live public functions.sql
- as_of ＝ 2026-09-12T14:35 ／ 當 repo の HEAD ＝ 1ad4edfbadc69191183a42113e9979c3f91b7dbf（不動）
- > 網㊀len の当たり ＝ 床18 の明示クラス（前後が英数字と単一下線でない）で len と開き括弧が続く行
- > 網㊁覆ひの判 ＝ ast の Try の行域が当該行を含むか
- > 網㊂包みの判 ＝ jsonb agg の在る行の直前行に字面 COALESCE が在るか（v1 と同じ網）

## §㋑-2 追補㊀ 正対照の併記（体系＝本紙 §A 網㊂）
- ★己の網でも正対照は当たつた★ ―― get defense checks の jsonb agg は ★8 本すべて包み済★（jsonb agg の行 ＝ L782 L796 L817 L831 L860 L869 L880 L901 ／ 包みの COALESCE は其の各直前行 ＝ L781 L795 L816 L830 L859 L868 L879 L900）
- 対して get abbreviation rules の jsonb agg は ★3 本すべて裸★（L732 L743 L754）―― 同じ一つの file の中で ★包む型と裸の型が共に在る★
- ★家老main隊 a-2 の実測 296643 そのものは己は讀んで居らぬ ∴ 確かめて居らぬ★（作法六条目）。而して ★己が独立に当たつた数は其の掲げる向きと同じ★ である

## §㋒ 追補㊁ len の当たりを行番で（体系＝本紙 §A 網㊀）―― 当たり ★行数 4／総出現 4★
- L81 L82 L83 ＝ ★三鍵を直に受ける三つ★（rules から鍵を引いた戻りに len を掛ける形・owner ＝ load abbreviation rules）
- L250 ＝ 並びの長さを見る一つ（owner ＝ normalize rpc result）―― 鍵の値に掛けるものではない ∴ 本件の筋から外れる
- ∴ ★板の掲げる len の当たりは L81 L82 L83 の三つ★ である

## §㋒-b ★而して覆ひが在る ―― 本紙の新たな所見★（体系＝本紙 §A 網㊁・ast の Try は当該 file に 2 つ）
- ★L81 L82 L83 は Try の行域 L61-L89 の中に在る★ ∴ 其処で立つ TypeError は L87 の except Exception が捕り L89 で空の辞書へ落ちる ―― ★呼手へは伝はらぬ★
- ★而して L77 は len の手前に在る★（rules を cache へ入れる行）∴ ★null を抱へた辞書が cache に残つた儘★ で L89 の空が返る
- ★覆ひの無い落ち所は二つ★ ―― L171（corrections を反復・owner ＝ check unofficial abbreviations・Try なし）と L220（detail required を反復・owner ＝ check disease abbreviation detail・Try なし）
- 加へて同期版 load abbreviation rules sync（L92-L128）は ★len を一つも持たぬ★（L121-L123 で正規化し cache へ入れる）∴ 同期経路では L81-L83 の落ちすら立たず null を抱へた cache が素通りする
- ∴ ★板の主張の逐語「len が落ちる」は 当たりの場所としては当たるが 落ちの届く先としては当たらぬ★ ―― 現に呼手へ届く落ちは ★L171 と L220 の反復★ である

## §㋒ 三択（v1 から変はらず）＝ ★⑵受け止めて居らぬ★
- 拠 ＝ L245-L247 の既定は鍵が無い時にしか効かず 定めは jsonb build object ゆゑ ★鍵は在り値が null★ ／ L236-L238 の空の辞書へ落ちる道は L252 のみ ／ 覆ひの無い L171 L220 が其の null を反復する

## §㋓ 三値（v1 から変はらず）＝ ★⑴要る★ ―― 本紙の追補で拠が一つ強まつた（落ちの所在が len ではなく反復と名指せた）

## §受入の逐語（令の側が渡した）―― 三鍵に COALESCE ／ 判定は軍師third（板の字）。★己は判定語を書かず 測つた数と行番のみを置く★

## §禁語の網 ―― ㊀生 ＝ 1（下の一行のみ）／㊁境界の句と名を除いた数 ＝ 0
- > 網の語彙は令の側が渡した六語 password secret token api-key api_key credential

## §㋔ 残弾 ＝ 追補を撃ち終へて ★0★。令430 に従ひ境界 clear で停まり次の令を待つ

## §床の実績 ―― 走 0／DB 0（讀取も書込も 0）／MCP 0／製品 code 書込 0／supabase 書込 0／install 0／find 0／rm 0／ssh 0／git は讀取動詞のみ（fetch 0）／作業樹は開かず ref の値のみ／他席の箱 0／前紙 v1 は一字も書き換へず／焚 1（v1 の器 order339 probe.py を再び用ゐ 席 dir 内に残す）
