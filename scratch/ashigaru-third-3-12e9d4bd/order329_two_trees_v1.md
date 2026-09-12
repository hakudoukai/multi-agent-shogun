## §的 ★二つの版は別系統である ―― HEAD では呼手紙が 存在せぬ函を呼んで居る事を 字の上で確かめる★

- 令の紙 = scratch/k3_orders/order329_a3.txt 符 d3d85cf99a7f4ba3 ―― 己が刷つた符も同じ（61 行 wc・4,241 B）
- 讀んだ刻 as_of 2026-09-12T10:11 ／ 己が当たつた（写しに非ず）
- 讀取 3 打（git 讀取動詞のみ）／ 焚 0 ／ 走 0 ／ git apply は --check すら 0 ／ DB 0 ／ /mnt/c へ書込 0
- ★以下の逐語で 〔〕 は二重引用符を表す★
- 樹 = /mnt/c/DentalBI（cd 0・git -C で当たつた）

## §母（己が当たつた実測・家老の母と突き合はせた）

- 版㊀ 符 7f39168d3 ―― 源 backend/api/treatment_validation.py = 5,687 行(wc)
- 版㊁ 符 53412b7bcda2f8ae（HEAD）―― 源 = 15,009 行(wc)
- ★HEAD の repo 全体で 函名が当たる file は 呼手紙 1 本のみ・4 件（git grep -c の出力 1 行）★
- ★HEAD の源 file 中の 函名の当たり = 0 件（git grep -n を源に限つた出力 0 行）★
- 網の形（悉皆・引数名を含めず識別子そのもので取つた）:
- > git -C /mnt/c/DentalBI grep -n 函名 <符> -- <path>

## §㋐ HEAD の呼手紙 L87 を含む import 帯の逐語 ―― 何処から import して居るか

逐語（符 53412b7bcda2f8ae・backend/tests/test_c1_dml_migration_pkg_isolated_harness.py・行番は同版の物）:

- 符 53412b7bcda2f8ae L086 = from backend.api.treatment_validation import (  # noqa: E402  (path setup above is required first)
- 符 53412b7bcda2f8ae L087 = 函名 ―― 括弧の中の唯一の名
- 符 53412b7bcda2f8ae L088 = )
- 符 53412b7bcda2f8ae L082-084 = REPO の根を求めて sys.path の頭へ挿す三行（帯の直前）

★module の path = backend.api.treatment_validation ―― 即ち file は backend/api/treatment_validation.py★

版㊀ でも同じ形である: 符 7f39168d3 L076 = 同じ from 行 ／ 符 7f39168d3 L077 = 函名 ／ 符 7f39168d3 L078 = )

## §㋑ 其の module が HEAD に在るか・中に函名が何件在るか

- 在る。符 53412b7bcda2f8ae の ls-tree が backend/api/treatment_validation.py を 1 行返した
- ★其の中の 函名の当たり = 0 件★（def も 0 件・言及も 0 件 ―― 名の悉皆で 0 行）
- 版㊀ では 符 7f39168d3 L4295 に def が在る（前弾 令328 で 89 行の鎖を引いた）

## §㋒ HEAD で走らせたら どの段で落ちるか ―― 字の上の当て（走らせて居らぬ）

★集める段である★。理由を三つ:

- ㊀ L086-088 の import は 函の中ではなく ★module の頭（字下げ 0）★ に在る ∴ module を読み込む其の時に走る
- ㊁ 読み込む先の module は HEAD に現に在る ∴ 落ちるのは module が見付からぬ形ではなく ★名が見付からぬ形★ である
- ㊂ 試験の器は file を集める段で module を読み込む ∴ 読み込みで挙がつた物は ★collection の段の誤り★ として挙がる

∴ 実行する段（test の本体）へは ★一つも到らぬ★。函を呼ぶ test は 1 本（符 53412b7bcda2f8ae L635 の test）だが、import は file の頭に在る ∴ ★同 file の全 test が 集める段で落ちる★。

★但し 之は「字の上の当て」である ―― 走らせて居らぬゆゑ 実際の出力は測定不能★

## §㋓ 令323 の patch を HEAD へ当てたら ㋒ は解けるか（当てて居らぬ・字の上）

- patch = scratch/ashigaru-third-3-12e9d4bd/order323_transplant_v1.patch 100 行(wc)・符 8f11b2f9b61998b9
- patch の 7 行目 = 加へる行 def 函名( ―― ★patch は 函の def を足す★
- 足す先の file = backend/api/treatment_validation.py（patch の 1-2 行目が同じ path を指す）

∴ ★㋒ の「名が見付からぬ」は 字の上では 立たなく成る★。import は通る形に成る。

★然し 之は 集める段の話に限る★ ―― 実行する段では 試験が 実の DB への繋ぎ（conn の受け口）を要する。其れが在るかは 走 0 の床の下では ★測定不能★ である。∴ ★「patch を当てれば 試験が当たりを出す」とは書かぬ★。

## §㋔ 令323 で apply --check の rc 0 を得たのは どの版に対してか（--check を打つて居らぬ）

patch の頭の当て先（逐語）= @@ -12441,6 +12441,97 @@ ―― 当て先を示す行は 1 本のみ

- 符 53412b7bcda2f8ae L12441 = return next(iter(templates.keys()))  ← ★patch の直前の文脈行と 逐語で一致★
- 符 53412b7bcda2f8ae L12444 = @router.get(〔/points〕)  ← ★patch の直後の文脈と噛み合ふ★
- 符 7f39168d3 の源は 5,687 行(wc) ∴ ★L12441 が 現に存在せぬ★（其の行域を引いた出力は 0 行）

∴ ★rc 0 を得たのは 版㊁（HEAD の系統）に対してである★。版㊀ に対しては 当て先の行が無い ∴ 噛み合はぬ。

★之は 令323 の測りが 誤りであつた事を意味せぬ★ ―― 意味するのは ★「当てた先の版を 紙に書いて居なかつた」事★ のみである。

## §㋕ 2 打が触れる出口 ―― 二つの版で同じか違ふか

出口 7 つは 令328 の表（相対行 30・40・43・59・60・74・75／return 4・raise 3・相対 1 = 符 7f39168d3 の L4295）。

HEAD の 2 打（逐語）:

- 符 53412b7bcda2f8ae L641 = 函名(fake_client, 〔TS_P_KENSA〕) ―― 第三の引数を ★省いた★
- 符 53412b7bcda2f8ae L642 = 函名(fake_client, 〔TS_P_KENSA〕, None) ―― 第三の引数に ★明示の None★

版㊀ の 2 打（逐語）:

- 符 7f39168d3 L554 = 函名(fake_client, 〔TS_P_KENSA〕)
- 符 7f39168d3 L555 = 函名(fake_client, 〔TS_P_KENSA〕, None)

★二つは 字の上で 同じである★（引数の数も・値も・順も 一致。違ふのは 行番のみ ―― 641/642 と 554/555）。

何れの打でも 第三の引数は None に定まる（省いても 既定が None・明示しても None）∴ 触れ得る出口は:

- 相対30 return None ―― ★到達不能★（相対29 の条件は 引数が空でない文字列ゆゑ 偽が定まる）
- 相対40 return None ―― 到達し得る（返る列が空の時）
- 相対43 raise 409 ―― 到達し得る（活きる行が 0 の時）
- 相対59 return 一致した行 ―― ★到達不能★（相対56 の条件が None ゆゑ偽）
- 相対60 raise 409 ―― ★到達不能★（同じ帯の中）
- 相対74 return 唯一の活き行 ―― 到達し得る
- 相対75 raise 409 ―― 到達し得る

★触れ得る出口 = 4 つ（相対 40・43・74・75）／ 触れぬ出口 = 3 つ（相対 30・59・60）★
★二つの版で 此の数は 同じである（4 と 3）★

何を一つと数へたか = ★函から出る一つの文（return か raise）を一つと数へた★。

## §㋖ 二つの別の主張

★「定義が repo に無い」は 源の字を測つた主張であり、「試験が落ちる」は 走らせた時の振舞ひの主張である ―― 前者は後者の因に成り得るが、後者は他の因（受け口・環境・料）でも起こる ∴ 二つは 別である★

## §残り・三択

- 版㊀ が HEAD の祖先か = ★現に無い★（家老が先に測つた。己は merge-base を撃たず 其れを起点とした ―― 新条㉘）
- HEAD の源に函の def が在るか = ★現に無い★（己が当たつた）
- patch を当てた後に 試験が当たりを出すか = ★測定不能★（走 0 の床）
- 令323 の rc 0 が 版㊀ に対して得られたか = ★現に無い★（行が存在せぬ）

## §禁語

網の語彙（令の側が渡した 5 つ）:
- > password / secret / token / api-key / api_key / credential

- ㊀生の数（網を掛けた儘・己の境界宣言行も数へた）= 1 件
- ㊁境界の句と名を除いた数 = 0 件 ／ 除く形 = 行頭が ハイフン 大なり 空白 で始まる行を落とした

## §残弾

- 残弾 8（前弾 9 から 1 を引いた）

## §頭（何時・何を・幾つ讀んだか）

- as_of 2026-09-12T10:11 ／ 讀んだ file = 3 本（源・呼手紙・令323 の patch）／ 讀取 3 打 ／ 焚 0 ／ 走 0
- 本紙 本文 82 行 ／ wc 128 行 ／ split 129 片 ／ 8387 B
