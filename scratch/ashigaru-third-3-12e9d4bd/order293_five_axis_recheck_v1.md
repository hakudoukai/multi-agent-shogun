## §的 ★令291 §D の五軸突合を 正しい符（甲樹の頂 wp-c1-a3-5-20260723）で測り直す ―― 前紙は書き換へず 此処に併記して正す★

## §A 頭
- as_of: 2026-09-11T09:46:46+0900（紙を書き終へた後に date で取つた）。的の樹 = /mnt/c/DentalBI（git -C のみ・★cd 0・樹を歩かず★）。符は悉く git の id ≡ sha1。作業樹 HEAD `53412b7bcda2f8ae`／tree `d57a2e0b2ffc4a52`。頂 `wp-c1-a3-5-20260723` = `e799ca077649a10c`／tree `2084483d8306a85a`。`main` = `3165e90450f3de74`／tree `aa4a4801e8cdf4c3`。
- 讀んだ紙 = 2 本 ―― ㋐令 `scratch/k3_orders/order293_a3.txt`（8 行(wc 改行数)／9 片(split)／1,694 B／sha256 頭16 `1a0260f7d21b4874`）㋑己の patch `scratch/ashigaru-third-3-12e9d4bd/order289_third_c_resolver_restore_v1.patch`（37 行(wc)／38 片／1,353 B／sha256 頭16 `c3d8dcfff87c57d1`・當 repo の作業樹）。
- 打数 = git 讀取動詞の起動 ★6／上限 12★。焚（.rule.py の起動） 0／上限 1。走 0・当て 0・製品 code 書込 0・/mnt/c 書込 0・find 0・★リダイレクト 0★。床の超過 現に無し。

## §B 頂の def の逐語（def の頭から終端まで・行番付き）
- 在処 = `wp-c1-a3-5-20260723:backend/api/treatment_validation.py` ★L4295〜L4381★（87 行）。終端の根拠 = 次の頂点定義 L4384 `@router.get("/points")` を器に言はせて取つた（L4382/L4383 は空行）。
- 頭: L4295 `def _resolve_comment_documentation_field_id(`／L4296 `client: Any, set_code: Optional[str], field_name: Optional[str] = None`／L4297 `) -> Optional[str]:`
- docstring = L4298〜L4322（25 行）。本体 = L4323〜L4381 ―― L4323-4324 `if not set_code:` → `return None`／L4325-4331 `.select("id,field_name,is_active").eq("set_code", set_code).order("doc_order").execute()`（★`.eq("is_active", True)` を使はず★）／L4332-4334 `rows = resp.data or []` → `if not rows: return None`／L4335 `active_rows = [r for r in rows if r.get("is_active")]`／L4336-4349 `if not active_rows:` → 409 `comment_documentation_no_active_row`／L4350-4366 `if field_name:` 絞つて丁度 1 件なら返し、然らずば 409 `comment_documentation_identity_mismatch`／L4367-4368 `if len(active_rows) == 1:` → `return active_rows[0].get("id")`／L4369-4381 然らずば 409 `comment_documentation_identity_ambiguous`。
- ★try/except は本体に現に無い★・★logger の呼出も本体に現に無い★（引いた 87 行の全域で）。

## §C 五軸突合（頂 ⇔ 令289 patch）
| 軸 | 頂（逐語・行番） | patch（逐語・行番） | 別 |
|---|---|---|---|
| ⑴引数の数と名 | `client: Any, set_code: Optional[str], field_name: Optional[str] = None`（3 つ・L4296） | `client, set_code: str, field_name: Optional[str] = None`（3 つ・patch L10） | 数 3・名 3・順 同 ＝ ★合致★／而して型註釈は ★不合致★（client 無註釈・set_code が `str`） |
| ⑵第三の既定 | `field_name: Optional[str] = None`（L4296） | 同（patch L10） | ★合致★ |
| ⑶複数行の扱ひ | active 2 件以上＋field_name 無 → 409 ambiguous（L4369-4381）／field_name 有で丁度 1 件でなければ 409 mismatch（L4354-4366） | `if len(rows) > 1:` → 409（detail は文字列一本・patch L29-33） | ★不合致★（409 を投げる点は同じ・★条件と detail の形が別★＝頂は dict 5 鍵＋condition 名） |
| ⑷例外・logger | HTTPException ★3 箇所★・try/except 0・logger 0 | HTTPException ★1 箇所★・try/except 0・logger 0 | try/except と logger は ★合致★（共に 0）／HTTPException の箇所数は ★不合致★（3 対 1） |
| ⑸行 0 件の扱ひ | ★二別★ ―― 行 0 件＝None（L4333-4334）／行は在るが active 0 件＝409（L4336-4349） | `.eq("is_active", True)` で絞つた後の `if not rows:` → `return None`（patch L22・L27-28） | ★不合致★（patch は二つを ★分けて居らぬ★） |

## §D live main の現 def
- 命（識別子境界形・対照を同じ一打に同梱）: `git -C /mnt/c/DentalBI grep -nE -e '(名A の境界形)' -e '(名B の境界形)' main -- backend/api/treatment_validation.py` → 出でた行 ★2★ ―― 共に ★対照の名★（L11418 def／L12398 呼出）。★`_resolve_comment_documentation_field_id` は 0 行★。
- ∴ live main の当該 file に 此の函は ★現に無い★（`def` どころか名すら 0）。∴ 五軸の各軸は「live 側に比べる物が現に無い」。頂に在つて live に無いのは ★函の全体 87 行★ と 其れが持つ ★409 三種★。

## §E 陽性対照
- ㋐ `^def _select_comment_template_key` を 二符（頂・main）へ同じ一打で撃ち → 頂 L4269・main L11418 の ★2 行★。同じ一打の `^def _resolve_comment_documentation_field_id` は 頂 L4295 の ★1 行のみ★（main は出ず）。∴ 命は両樹で効いて居る。
- ㋑ 併せて記す ―― 令290 で作業樹を grep した時 対照の def は L12418、今回 main の blob では L11418。★樹が違へば行番も違ふ★（作業樹 ≠ main）。§B/§D の行番は悉く ★blob の行番★ である。

## §F 実測／見込み／確かめて居らぬ ＋ 数が意味せぬ事
- ★実測★: 頂の def L4295-4381（87 行・己が引いた）／HTTPException 3 対 1／行 0 件の二別の有無／main の 0 行と対照 2 行／符 6 本（作業樹 HEAD と tree・二符と其の tree）。
- ★見込み★: 現に無し（本紙に推し量りで埋めた升は一つも無い）。
- ★確かめて居らぬ★: 令289 patch が 板 fa06a3a1 の当てとして ★現に当たるか★（本令では 当て 0・走 0）／頂の docstring が述べる契約が ★実行時に其の通り振舞ふか★（★走らせて居らぬ★）。
- ★数が意味せぬ事★: 「87 行」は ★def の頭から次の頂点定義の直前までの行数★ であり、★函の論理の大きさ★でも ★patch が足すべき行数★でもない（patch 側の当該域 26 行と直に引き算するな ―― docstring 25 行が頂の側にのみ在る）。「HTTPException 3 対 1」は ★raise の箇所数★ であり ★返る status_code の種類数★ ではない（共に 409 の一種）。
