# ★令270 ―― get_abbreviation_rules を現行写しで置き直し 3 鍵に COALESCE★

## §的 ★的一行★

★2a4291af の migration は無引数 sql ゆゑ現行の plpgsql 函には当たらぬ。∴ 総監督が pg-get-functiondef で実読した現行定義の写しを土台に書き直し、3 鍵にのみ COALESCE を置いた ―― 写しと本 migration の定義部の差は 6 行（3 対）のみで、COALESCE を剥がすと一字違はず一致する。★

## §zero 帳の頭（何時・何を・幾つ讀んだか）

- as_of = 2026-09-10T15:10:09+0900
- 本弾の Bash 呼出 = 11（前窓 3 ＝ 前提讀み ／ 本窓 8 ＝ 書き 1・測り 2・直し 1・走 2・枝 2）
- 走 = 2/2 ―― ⑴ python -m pytest → rc=127（器 python は現に無い） ⑵ python3 -m pytest → rc=0
- 焚 = 0（本弾は .rule.py を一本も鋳て居らぬ・令の定めの通り）
- 讀んだ物 = 4 file（現行写し 43 行／前の migration 91 行／試験 208 行／樹の頭）
- 樹 = /home/hakudoukai/a3/wt-abbrev-coalesce-20260910（枝 dry/a3-abbrev-coalesce-20260909）
- 樹の HEAD（書く前）= 2a4291af276080a48804dedc1619d8fb600eb03b
- 樹の HEAD（commit 後）= c9c25390e1a37ccf70793d90f001a7b5d57198da
- 樹の porcelain（commit 後）= 0
- 本 repo の HEAD = 1ad4edfbadc69191183a42113e9979c3f91b7dbf（本 repo へは紙と raw を置いたのみ・commit 0・push 0）

## §ichi 令の逐語（家老 令270・詳細 order270_a3.txt 四）

> 一 総監督の逐語＝「2a4291af の migration は get_abbreviation_rules() ★無引数・sql★ で定義しており、現行は ★get_abbreviation_rules(p_diagnosis_date date DEFAULT CURRENT_DATE)・plpgsql・in_revision_scope 付き★＝CREATE OR REPLACE では別 overload が増えるだけで現行は直らない。直し=この定義を写し 3 鍵の (SELECT jsonb_agg…) を COALESCE((…),'[]'::jsonb) で包むだけ（引数・言語・search_path・in_revision_scope・列は不変・GRANT/COMMENT は不要）。同枝に押し直し→総監督が適用（rollback=同 file）。」
> 四 手順: ⑴ migration を写しの定義で書き直す（頭の註は「現行 plpgsql 定義を写し 3 鍵に COALESCE を置いた」と一行・COALESCE の行番号を註に）⑵ 写しと migration の diff が「COALESCE( と ,'[]'::jsonb) の 3 対＋註」だけで在る事を diff で実測し raw へ ⑶ 試験 file は ★L146 が無引数の signature を assert して居る＝新 signature（p_diagnosis_date date DEFAULT CURRENT_DATE・LANGUAGE plpgsql）へ直せ★・他の assert も新形で通るかを讀んで直す ⑷ 走1＝python -m pytest backend/tests/test_abbreviation_rules_coalesce.py（DB 不要の SQL 文面試験なら走らせよ・DB 要なら走らせず「DB 要ゆゑ未走」と書け）⑸ 此の樹で 1 commit（枝の儘・push は家老が名指し refspec force0 で代行）。

## §ni 名指された物（讀んだ物・完全 sha256）

| 何 | path | 行（wc / 片） | B | sha256 |
|---|---|---|---|---|
| 現行定義の写し（不触） | scratch/iincho/get_abbreviation_rules_current_20260910.sql | 43 / 44 | 1,836 | 00fd1a16fa92b2539cb07db6a2ae6a4b5df520d16a1605aea1dc761501a4d919 |
| 前の migration（置換前） | 樹 supabase/migrations/20260909183000_fix_get_abbreviation_rules_coalesce.sql | 91 / 92 | 4,627 | 頭16 d172d02775975a09 |
| 試験（直す前） | 樹 backend/tests/test_abbreviation_rules_coalesce.py | 208 / 209 | 6,701 | 頭16 fe98ccb853d61e45 |

## §san 書き直した migration

- path = 樹 supabase/migrations/20260909183000_fix_get_abbreviation_rules_coalesce.sql
- 行 = ★49 wc / 50 片★（註 10 片 ＋ 定義 40 片）・2,264 B・sha256 頭16 ★6fd24fde6d7eddfd★
- COALESCE を置いた行（本 file の行番号・開き / 閉ぢ）= official L19 / L29 ・ corrections L30 / L40 ・ detail-required L41 / L46
- 不変 = 引数（p_diagnosis_date date DEFAULT CURRENT_DATE）・言語（plpgsql）・STABLE・search_path・in_revision_scope・列の並び
- 置かぬ物 = GRANT と COMMENT（現行定義に現に無い ∴ 家老の明示に従ひ置かぬ）

## §shi diff の実測（★比べた相手を同じ行に★）

- 写しの定義部（40 片） 対 新 migration の定義部（40 片）= minus 6 / plus 6 ＝ ★3 対★（開き 3 ＝ COALESCE(( ／ 閉ぢ 3 ＝ ), '[]'::jsonb)）
- 新 migration から COALESCE を剥がして写しの定義部と比べる = 一字違はず一致（tootta）
- 註 = 写し 4 片 → 新 migration 10 片（増えた 6 片 ＝ 因・写し元 sha・COALESCE の行番号・適用と rollback の所在）
- ★別の数★ ―― 前の migration 対 新 migration は git の stat で 54 挿入 / 91 削除 ＝ 145 行が動いた。「6 行」と「145 行」は食ひ違ひに非ず ―― ★前者は写しと比べた数・後者は前の migration と比べた数★（條 481）。

## §go 試験の直しと走り

- 試験 file = 樹 backend/tests/test_abbreviation_rules_coalesce.py ・ ★213 wc / 214 片★ ・6,885 B・sha256 頭16 ★8bf0a8fcd73c1e7e★（前は 208 wc / 209 片・6,701 B・fe98ccb853d61e45）
- 直した所 = L146 の一行（無引数 signature を見て居た当て）を新 signature の当てへ。加へて LANGUAGE plpgsql と in_revision_scope の当てを二本足した ＝ 1 行 → 6 行
- 讀んで検算し ★直さずに残した★ 当て（新形でも当たるゆゑ）:
  - 頭の一つで切る当て ＝ 切つた片は 2（新形でも切れる）
  - 窓 400 字の当て ＝ '[]'::jsonb の現れる位置は official 357 字目・corrections 380 字目・detail-required 217 字目 ∴ ★余白は 43 / 20 / 183 字★（現に収まる。corrections の余白 20 字は薄い ―― 自訴 3）
- 走 = python3 -m pytest backend/tests/test_abbreviation_rules_coalesce.py -q → ★rc=0 ・ 10 件が通つた ・ 0.25 s★
- 走らせ得た因 = 本 file の当ては ㋐ SQL の文面を讀む物 ㋑ httpx を差し替へた呼手の振舞ひを見る物 の二種のみで、DB へ繋ぐ物が現に無い

## §roku commit（枝の儘・push 0）

- commit sha = ★c9c25390e1a37ccf70793d90f001a7b5d57198da★
- 触れた file = 2 本のみ（migration と試験）・54 挿入 / 91 削除
- 枝 = dry/a3-abbrev-coalesce-20260909（枝の儘・己は push を打つて居らぬ ＝ 家老が名指し refspec force0 で代行）
- rollback = 同 file（家老明示）

## §nana 之が意味せぬ事（三つ）

1. ★適用を意味せぬ★ ―― DDL を DB へ当てるのは総監督である。席は DB を讀む口を持たぬ ∴ 本弾の測りは悉く file の文面である。
2. ★overload の数を意味せぬ★ ―― 現に幾つの get_abbreviation_rules が DB に在るかは DB 側の事実であり、本 file からは ★測定不能★。
3. ★rc=0 は函が直つた事を意味せぬ★ ―― 本試験は SQL の文面と差替へた呼手の振舞ひを測るのみで、DB 上の函の返りは一度も測つて居らぬ。

## §hachi N の一表（母は己が書く前に測る・條 471）

- 母の定義 = scratch/ashigaru-third-3-12e9d4bd/order*.md ・ 四形の網（甲・甲2・乙・丙）に当たり値の門 100〜999 を通つた行
- 刻 = ★書く前★（本紙と raw を置く前に測つた）
- 母 = 112 枚 / 23131 行 ・ 網 = 265 本 ・ ★N = 263★（N ＝ 網に当たつた ★相異なる番の数★・幅 169〜471）
- ★令269 の N=307 と比べぬ★ ―― 彼は order269_route.rule.py で測つた数、本弾は焚 0 ゆゑ紙を書く器の中で測つた数である。條(o174)「器を一字も変へずに二度測れ」を満たして居らぬ ∴ 比べる資格が無い（自訴 4）。

## §kyuu 新條（★四百八十から★・令269 の 467〜 と衝突させぬ）

- ★四百八十★ ＝ 同名の函でも signature が違へば別物である。CREATE OR REPLACE は名で当たらず signature で当たる。∴ 「置き換へた」と書く時は ★引数の並び★ を同じ行に書け。
- ★四百八十一★ ＝ diff の大小は ★何と比べたか★ で変はる（写しと比べれば 6 行・前の migration と比べれば 145 行）。∴ diff の数を書く時は ★比べた相手★ を同じ行に書け。
- ★四百八十二★ ＝ 当てが通る事は ★余白★ を言はぬ。窓 400 字の当ては 357・380・217 字目で当たつた（余白 43・20・183 字）。∴ 通つた当てにも ★余白を測つて★ 書け。
- ★四百八十三★ ＝ 器の名は環境ごとに違ふ（python は現に無く python3 は現に在る）。∴ 走の上限を数へる時は ★名の食ひ違ひで消えた一発★ も走に数へよ。
- ★四百八十四★ ＝ 切り口の文字列は註にも棲む。CREATE OR REPLACE で切つたら註の三行目に当たつた。∴ anchor は ★定義の頭まで伸ばし★、count が 1 である事を確かめてから切れ（床(28)の延長）。

## §juu 自訴

1. diff の切り口を CREATE OR REPLACE で取つた所、写しの註の三行目に当たり、定義部が 42 片 対 40 片 と出た。CREATE OR REPLACE FUNCTION まで伸ばし count==1 を確かめて取り直した（條 484）。★最初の数は棄てた★。
2. 走の一発目 python -m pytest が rc=127 に終つた（器 python は現に無い）。走 2 の内 1 を器の名の食ひ違ひで費した（條 483）。
3. 窓 400 字の当ては corrections で余白が 20 字しか無い。令 ⑶ は「新形で通るかを讀んで直す」ゆゑ ★通る当ては直さずに残した★ ―― 窓を広げるべきか否かは家老の裁を仰ぐ（繰越 乙12）。
4. 母の数を令269 の器で測り直して居らぬ（焚 0 の定めゆゑ）。∴ §hachi の N は令269 の N と ★比べて居らぬ★。
5. commit の折、hook が地の文を一行刷つた（secret 走査の行）。己が書いた語ではない ―― 逐語は raw に > 付きで置いた。
6. 令269 は境界で止めた儘である ―― 紙 228 行・raw 100 行・器 151 行は disk に在り、押しと復命は打つて居らぬ。本令の後に再開する。

## §juuichi 物の帳

| 何 | path | 行（wc / 片） | sha256 頭16 |
|---|---|---|---|
| 書き直した migration | 樹 supabase/migrations/20260909183000_fix_get_abbreviation_rules_coalesce.sql | 49 / 50 | 6fd24fde6d7eddfd |
| 直した試験 | 樹 backend/tests/test_abbreviation_rules_coalesce.py | 213 / 214 | 8bf0a8fcd73c1e7e |
| 本紙 | scratch/ashigaru-third-3-12e9d4bd/order270_abbrev_revise_v1.md | 115 / 116 | 書いた後に測る ＝ 完了便に記す |
| raw | scratch/ashigaru-third-3-12e9d4bd/order270_raw_v1.txt | 68 / 69 | 16cccb081a96a6b1 |

## §juuni 繰越

- 乙3 常設器は案の儘（委員長の GO 待ち・鋳るな）
- 乙4 E46 の 124/206 の内 A1 の 124 は未だ數へ直して居らぬ
- 乙5 基底 120 を「軸外」と「軸に載らぬ」へ分ける
- 乙6 m2 の 16 行を儀礼と事例に ★数で★ 分ける
- 乙8 板 354dc26f（優先1）＝ 本弾で手を着けた（commit c9c25390・適用は総監督）
- 乙9 弾倉 E2・E3・E4
- 乙10 條463 に従ひ F2 の各番に就き「何番目の見出し行を取つたか」を器の欄に持たせる
- 乙11 kenshu_bucho の「書けるが読まれぬ」箱の扱ひは家老の裁を仰ぐ
- 乙12（新）試験の窓 400 字を広げるべきか否か（corrections の余白 20 字）は家老の裁を仰ぐ
- 乙13（新）令269 の押しと復命（枝 a3/order269-grill-route-20260910・BASE 352f058c360a30345959f6123c81e93a2b8397af）を本令の後に打つ
