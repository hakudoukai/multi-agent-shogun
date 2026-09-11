## §的 ★由来樹に本物の函が在つたかを 樹を歩かず pickaxe で測り、令289 の patch の def と突合せる★

## §A 頭
- as_of: 2026-09-11T09:13:27+0900（紙を書き終へた後に date で取つた）
- 的の樹 = /mnt/c/DentalBI（作業樹・CRLF）。HEAD 53412b7b… / tree d57a2e0b…（共に git の id ≡ sha1）は ★令290 で測つた値を写した・本令では再測して居らぬ★。讀んだ紙 = 1 本（scratch/k3_orders/order291_a3.txt／9 行(wc 改行数)／10 片(split)／2,090 B／sha256 頭16 c3787a725d091b96）。
- 打数 = git 讀取動詞の起動数 12／上限 12。焚（.rule.py の起動数） 1／上限 1。走 0・書込 0（製品 code / /mnt/c 共に）・find 0・★樹を歩かず（cd 0・禁3樹へ入らず）★。押す前に一度 同じ path で鋳り直した（42 行 → 40 行・数と結びは不変）。
- ★自己申告★: 一打だけ `> /dev/null` を用ゐた（在否 probe の一打）。一時 file は作られて居らぬが ★床⑾ の文言（リダイレクト禁）に触れる★ ゆゑ此処に記す。

## §B 撃つた pickaxe と 陽性対照（逐語）
- 命 ㋐: `git -C /mnt/c/DentalBI log --all --oneline -S'_resolve_comment_documentation_field_id' -- backend/api/treatment_validation.py` → ★当たり 1 符★。
- ★陽性対照★ 命 ㋑（㋐ と同じ形・名だけ 令290 で L12418 に見た同形別名へ替へた）: `... -S'_select_comment_template_key' -- backend/api/treatment_validation.py` → ★当たり 2 符★。∴ 命は効いて居る（対照付き）。

## §C 当たつた符と 之を含む ref
- 符 = `59b9f4dd85c1c03b608a1637c3e6f6d7d632cf73`（git の id ≡ sha1）。日 = 2026-07-23 00:34:22 +0900。
- 題（逐語）= `feat(karte_visit_items): D1b identity/lineage columns + R8 comment attribution (WP-C1)`
- 之を含む ref = ★1 本のみ★ `refs/heads/wp-c1-a3-5-20260723`（`git for-each-ref --contains` で数へた）。
- 其の符の当該 file に於ける名の当たり = 2 箇所（def 1・呼手 1）・def は ★L4295★。∴ ★本物の函は 由来樹（甲樹）に 現に在つた★。

## §D 本物の def と 令289 の patch の def の突合
| 軸 | 甲樹の本物（59b9f4dd8・L4295 以降 逐語） | 令289 の patch の def | 突合 |
|---|---|---|---|
| 引数の数 | ★2★ `client: Any, set_code: Optional[str]` | ★3★ `client, set_code: str, field_name: Optional[str] = None` | ★不合致★ |
| 第三引数と既定 | 現に無い | `field_name` ＝ 既定 None | ★不合致★ |
| 複数行の扱ひ | `.order("doc_order")` ＋ `.limit(1)` で ★先頭 1 行を採る★ | 2 行以上なら ★409 を投げる★ | ★不合致★ |
| 例外の扱ひ | `try` / `except Exception` → `logger.warning` して None を返す | try は現に無い | ★不合致★ |
| 行が 0 の時 | None | None | 合致 |
- ∴ 五軸のうち 四つが ★不合致★・一つが合致。★令289 の patch は「本物の復元」ではなく「己が形から起こした別物」であつた★（前紙は書き換へず、此処で正す）。
- 且つ ―― live main の harness は L642 で ★位置引数 3 つ★ を渡す（令290 §C）。∴ ★本物を一字も違へず戻しても L642 は形の上で受からぬ★。之は形の話であり、実行時の結果ではない。

## §E 家老の先測の独立再測（salvage 符 7f3f371b94b535ad301a06ea0b29e98817ba4268）
- 題（逐語）= `salvage(safe): third-PC 甲樹の生きた成果のうち ★既存fileを一字も上書きせぬ 28本★ のみを live main 直上に載せる`。日 = 2026-09-02 22:38:22 +0900。
- name-only の file 数 = ★28★。harness は ★17 番目★（`backend/tests/test_c1_dml_migration_pkg_isolated_harness.py`）。
- `backend/api/treatment_validation.py` は 28 本に ★現に含まれぬ★。∴ 家老の先測と ★同値★ を己が独立に得た ―― harness だけが運ばれ、函は「既存 file を一字も上書きせぬ」床ゆゑ運ばれなんだ。

## §F 走らせて居らぬ・三別・数が意味せぬ事
- 令171 に従ひ ★何も走らせて居らぬ★。当該 test が現に落ちるか否かは ★測定不能★。
- ★現に在る★: 甲樹の本物の def（1 符・1 ref・L4295）／対照 2 符／salvage 28 file・harness 17 番目。
- ★現に無い★: salvage 28 本の中の treatment_validation.py（0）／本物の def に於ける第三引数と 409（0）。
- ★測定不能★: 59b9f4dd8 の harness に於ける呼手（当たり 0 行だが ★file の在否を測つて居らぬ★ ∴ 0 の意味は断じ得ぬ）／甲樹が今も歩ける形か（樹を歩いて居らぬ）。
- ★数が意味せぬ事★: 「当たり 1 符」は ★名の在る側へ数が変つた符の数★ であり、★函が生きて居た期間★ でも ★呼ばれた回数★ でもない（pickaxe は差分の数を数へる）。
