## §的 ★測れぬと置いた列の型は 字で当たれるか ―― DB を一度も讀まず migration の字だけで何処まで言へるかを測る★
## §頭
- 令326 の紙の符（己が本窓で刷つた sha256 頭16）= 6e62a842789bc81a（家老の符と一致・床27）
- 何時 = as_of 2026-09-12T09:24 ／ 何を = /mnt/c/DentalBI の supabase/migrations 配下で表名を含む 10 file ＋ 呼手紙の当てる fixture 2 本
- 幾つ讀んだか = 讀取 4 打（令の紙 1・file 列挙 1・grep 2）・焚 0・走 0・当て 0・DB へ触れる打 0
- 對象樹 = /mnt/c/DentalBI HEAD = 53412b7bcda2f8ae（rev-parse で當たつた・枝 wp-a1-a3-3-20260723・git blob は LF）
- 家老が先に測つた母（10 file）は撃ち直さず起点とし 席が同じ網で再測して ★10 で一致★（新条28）
## §㋐ 立てた所
- 網の形 = git grep -lI で表名を含む file を supabase/migrations 配下に悉皆（一つ ＝ file 1 本）・其の各々へ CREATE TABLE|ALTER TABLE|DROP TABLE|is_active を /usr/bin/grep -nE で当てた
- 当該表の CREATE TABLE = 20260323114647_create_treatment_set_tables.sql の ★L70★（10 file 中 CREATE TABLE を持つは此の 1 file のみ・其の中に 5 件・当該表は 1 件）
- is_active の宣言 = 同 file ★L91★ 逐語 ―― is_active boolean DEFAULT true,
- ★型 = boolean ／ NOT NULL = 無し ／ DEFAULT = true★
- 同 file に同名の列が他に 2 件（L34 treatment_sets・L65 treatment_set_items）在るが 当該表の帯（L70-93）に在るは L91 の 1 件のみ
## §㋑ 後の書換へ（時系列）
- 網の形 = 10 file を file 名の頭の数で昇順に並べ 当該表を対象とする ALTER COLUMN|TYPE|DROP COLUMN|DROP TABLE|CREATE TABLE を悉皆に当てた（一つ ＝ 打 1 つ）
- 当該表への ALTER = 3 file・5 打 ―― 20260324024343 L41／20260405032824 L17／20260411081738 L3・L10（＋ RLS を立てる打 2 ＝ 20260415173651 L54・20260424232915 の動的な廻し）
- 其の 5 打は悉く ADD COLUMN IF NOT EXISTS（足す列 7 ＝ revision_code・valid_from・valid_to・source_finding_ids・source_checklist_ids・data_source・shikan_field_name）
- ★ALTER COLUMN 0 件 ／ DROP COLUMN 0 件 ／ DROP TABLE 0 件 ／ 当該表の再 CREATE 0 件★
- 是の 0 は「10 file の全行に 上の 5 語を /usr/bin/grep -nE で当てた網」での 0 である
- ∴ 型を変へる打は 0 ∴ ★最後に効くのは 20260323114647 L91 の宣言其の物★（時系列で最初かつ最後）
## §㋒ 噛むか
- 型が boolean である以上 令325 ㋒ の「文字の列なら空でない文字が悉く真に成る」の枝は ★字の上で消える★
- 89 行の取り方（相対41/絶対4335・get の返りを其の儘 真偽に取る）と boolean は ★噛む★ ―― 真は真・偽は偽で 2 値が其の儘通る
- 但し ★NOT NULL が無い★ ∴ 字の上では NULL が入り得る。NULL は偽の器を経て None で来る ∴ get の返りが None と成り 其の行は落ちる
- DEFAULT true が在る ∴ 明に NULL を入れぬ限り NULL には成らぬ。消えたのは文字列の枝のみで ★NULL の枝は 1 本残る★
- 呼手紙の当てる fixture 2 本は当該表を ★CREATE せぬ★（網 = 当該 fixture に CREATE TABLE を当て 0 件）∴ 試験の器の列の型も migration の字に由る
- ∴ 令325 で測れぬと置いた内 ㊀型が boolean か = ★言へる様に成つた★ ／ ㊁実の DB に其の型で在るか = ★依然 測れぬ★
## §㋓ 二つの別と三値
- ★「migration の字に其の型で在る」と「実の DB に其の型で在る」は 二つの別の主張である★
- ㋐ 立てた所 = 言へる（字の上・10 file 悉皆）／㋑ 後の書換へ = 言へる（字の上・時系列で並べて悉皆）
- ㋒ 噛むか = 言へる（字の上）・NULL の枝が残る事も 言へる ／ 実の型 = 測れぬ
- ㊁「実の DB に其の型で在る」は ★本紙では当てて居らぬ★ ―― 手で変へられた見込みが在り migration が悉く当たつて居る保証を本紙は持たぬ（DB 0・走 0）
- 條四百九十六 ―― 探して 0 件でも「無かつた」の証には成らぬ ∴ 本紙の 0 は悉く 網を名指した 0 として書いた
## §㋔ 残弾
- 令325 の 11 本 ― 閉ぢ 1（migration の字で列の型を当てる）＋ 立て 1（実の DB の列の型と NULL の実在を当てる）= ★残弾 11 本★
## §禁語（新条29・網の語彙を書く）
- > 席の網（17 語）= PASS 合格 充足 解消 緑 問題な 正常 良好 安全 改善 対策 推奨 べきである password 今夜 明日 後ほど
- > 家老の網 = password secret token api-key credential（家老の便には六語と在るが 名は 5 つ挙がる ∴ 1 語は己に見えぬ・確かめて居らぬ）
- 席の網 ―― ★生 = 2 件★（網を掛けた儘・己の宣言行と語彙行を含む）／★除 = 0 件★（語彙行 ＝ 上の 2 行を落とした数）
- 家老の網 ―― ★生 = 3 件★ ／ ★除 = 1 件★（同じ落とし方。除の 1 件は 下の行で網の名を一つ挙げた箇所であり 値は一字も無い ＝ 名の言及）
- 令325 の食ひ違ひの因 = 席の網に secret の名が無く 家老の網に在つた ∴ 数の誤りではなく ★網の差★ である（令325 の紙は不触）
## §床と守り
- 讀取のみ・讀取 4 打（上限 30）・焚 0（上限 1）・走 0・当て 0（git apply は --check も 0）・試験 0 本・find 0
- DB へ触れる打 0（SELECT 0）・DDL 適用 0・/mnt/c/DentalBI へ書込 0・製品 code へ一字も書かず
- 他席の箱・archive・家老の箱を開く 0（己の箱の讀みと己の未読の閉ぢのみ）・一時 file は席 dir 内の index 1 本（同じ打で消す）
- 識別の値・患者本文・鍵の類・set_code の個別値・表示名を一字も写して居らぬ（列名と file 名と行番のみ）
## §紙の頭
- 行数 = 本文 48 行 ／ wc -l 48 行 ／ split 片 49 片（一つ ＝ 改行で割つた片 1 つ）
