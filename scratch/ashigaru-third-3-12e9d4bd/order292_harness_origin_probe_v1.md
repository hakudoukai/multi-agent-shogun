## §的 ★三位置引数は何処から来たか ―― harness の初出符を在否 probe と pickaxe で当て、令291 §D を正す★

## §A 頭
- as_of: 2026-09-11T09:30:41+0900（紙を書き終へた後に date で取つた）。的の樹 = /mnt/c/DentalBI（git -C のみ・★cd 0・樹を歩かず★）。符は悉く git の id ≡ sha1。
- 讀んだ紙 = 1 本（scratch/k3_orders/order292_a3.txt／9 行(wc 改行数)／10 片(split)／2,112 B／sha256 頭16 0307fbaabd704d70）。押す前に同じ path で ★四度★ 鋳り直した（38→37→36→35 行・数と結びは不変）。
- 打数 = git 讀取動詞の起動数 ★11／上限 12★。焚（.rule.py の起動数） 0／上限 1。走 0・当て 0・書込 0（製品 code / /mnt/c 共に）・find 0・★リダイレクト 0★。床の超過 現に無し。

## §B 在否 probe（対照付き）
- 命 ㋐: `git -C /mnt/c/DentalBI cat-file -e 59b9f4dd8:backend/tests/test_c1_dml_migration_pkg_isolated_harness.py` → ★rc=128★・生の一行 `fatal: path '...' exists on disk, but not in '59b9f4dd8'`
- ★陽性対照★ 命 ㋑（同じ形・path だけ替へ）: `... cat-file -e 59b9f4dd8:backend/api/treatment_validation.py` → ★rc=0★ ∴ probe は効いて居る。∴ ★harness file は 符 59b9f4dd8 に 現に無い★。

## §C harness の初出符（`log --all --diff-filter=A` ・対照付き）
| 符 | 日 | 題（頭） |
|---|---|---|
| `7f39168d3` | 2026-07-23 15:37:11 +0900 | `test(c1-dml-migration-pkg): durable commit of forward/rollback fixtures + isolated harness (finding007 cycle4)` |
| `c6ea84e56` | 2026-09-02 21:20:56 +0900 | `salvage(third/backend): 甲樹の眠る成果を file 単位で origin/main 直上へ持込 (38 file)` |
| `7f3f371b9` | 2026-09-02 22:38:22 +0900 | `salvage(safe): ... ★既存fileを一字も上書きせぬ 28本★ のみを live main 直上に載せる` |
- ★陽性対照★（同じ命の形・path を替へ）: `-- backend/api/treatment_validation.py` → `157e8c4da`（2026-03-31）★1 符★ ∴ 命は効いて居る。
- ★初出 = 7f39168d3★（最古）。之を含む ref は ★1 本のみ★ `refs/heads/wp-c1-a3-5-20260723`。且つ `merge-base --is-ancestor 59b9f4dd8 7f39168d3` → ★rc=0★ ＝ 函の初版は harness の ★祖先★。

## §D 初出符に於ける呼出の逐語（行番付き・棲家別）
- L77 = import の名／L549 = 三重引用の帯の中の言及／★呼出は 2 行★ ―― L554 `resolved_id_1 = _resolve_comment_documentation_field_id(fake_client, "TS_P_KENSA")` ＝ ★位置引数 2★、L555 `resolved_id_2 = _resolve_comment_documentation_field_id(fake_client, "TS_P_KENSA", None)` ＝ ★位置引数 3（第三に None を渡す）★。∴ ★三位置引数は live main で生えたのではなく、harness が生まれた其の日から既に在つた★。

## §E ★令291 §D の訂正★（前紙は書き換へず 此処で正す）
- 第三引数を入れた符 = `8a23afa8a`（2026-07-23 01:14:03・題 `fix(karte_visit_items): G1 cycle1 REDO是正 Finding1/2/3/4 (D1b/R8, a3-5)`）。函の初版 59b9f4dd8 は同日 00:34 ―― ★40 分後に是正されて居た★。
- 7f39168d3 と 枝の頂 `wp-c1-a3-5-20260723` の def は共に L4295 `client: Any, set_code: Optional[str], field_name: Optional[str] = None` ＝ ★引数 3・第三の既定 None★。
- ∴ 令291 §D の「引数 2 対 3 ＝ 不合致」は ★符の取り違へ★（初版を甲樹の答と見た）。★甲樹の最終形と 令289 patch の 引数の形は 合致★。
- 而して 0 件の扱ひは今も ★不合致★ ―― 頂の契約は「行 0 件＝None／行は在るが active 0 件＝★409★」と分けるが、令289 patch は `.eq("is_active", True)` で絞つた後の 0 件を一律 None に落とし ★二つを分けて居らぬ★。
- ■三 の問ひ ＝ ★判ずる★: live main の L642 が 3 位置引数を渡す因は 8a23afa8a の契約変更に在る（harness は初出から其の形）。

## §F 三別と 数が意味せぬ事
- ★現に在る★: harness の初出符 7f39168d3（1 符・含む ref 1 本）／第三引数を入れた符 8a23afa8a（1 符）／頂の def の 3 引数／対照 2 件（probe rc=0・log 1 符）。
- ★現に無い★: 符 59b9f4dd8 に於ける harness file（rc=128）／甲樹の頂の def と 令289 patch の 0 件の扱ひの一致。
- ★測定不能★: 頂の def の 4346 行目以降（引いて居らぬ）／当該 test が現に落ちるか（★走らせて居らぬ★）。
- ★数が意味せぬ事★: 「初出符 3 行」は ★path が新規追加として現れた符の数★ であり、★file が三度作られた★ でも ★三つの別物★ でもない（salvage 二本は同じ file を別の樹へ載せ直した符）。
