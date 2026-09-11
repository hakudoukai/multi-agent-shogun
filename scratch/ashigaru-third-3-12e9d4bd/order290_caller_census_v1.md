## §的 ★令289 の函の呼手を独立に数へ、陽性対照を添へて 0 と 1 を分ける★

## §A 頭
- as_of: 2026-09-11T09:06:17+0900（紙を書き終へた後に date で取つた）
- 的の樹 = /mnt/c/DentalBI（作業樹・CRLF）。HEAD = 53412b7bcda2f8aec4c5f5cdd157e819e8e91c02（git の id ≡ sha1）、tree = d57a2e0b2ffc4a525f579d8766be7d86182b7b2b（同じく sha1）。
- 讀んだ紙 = 1 本（scratch/k3_orders/order290_a3.txt／9 行(wc 改行数)／10 片(split)／1,724 B／sha256 頭16 56c2518b5663b236）。己の compact 境界 = 本窓の頭で一度（前窓の残務 = 令289 の復命便から継いだ）。
- 打数 = git 讀取動詞の起動数 9／上限 12。焚（.rule.py の起動数） 0／上限 1。走 0。製品 code 書込 0。find 0。/mnt/c 書込 0。★押す前に一度 同じ path で鋳り直した（41 行 → 40 行・数と結びは不変）★。

## §B 引いた命と陽性対照（逐語）
- 命 ㋐（名の悉皆・識別子境界形）: `git -C /mnt/c/DentalBI grep -nE '(^|[^A-Za-z0-9_])_resolve_comment_documentation_field_id([^A-Za-z0-9_]|$)' -- backend/` → 当たり 4 行・1 file。
- 命 ㋑（def 形）: `git -C /mnt/c/DentalBI grep -nE '^[[:space:]]*def[[:space:]]+_resolve_comment_documentation_field_id([^A-Za-z0-9_]|$)' -- backend/` → ★当たり 0 行★。
- ★陽性対照★（㋑ と同じ形・名だけ替へた）: `... def[[:space:]]+_select_comment_template_key([^A-Za-z0-9_]|$) ... -- backend/` → `backend/api/treatment_validation.py:12418:def _select_comment_template_key(` ★ 1 行★。
- ∴ ㋑ の 0 は「命が効いて居らぬ」のではなく、★def が現に無い★（対照付き）。家老の先測と 同値を 己が独立に得た。

## §C 呼手の全数（名の当たり 4 行・L86 のみ 別命 ㋒ から）
| 行 | 棲家 | 逐語（頭） | 引数の数と位置 |
|---|---|---|---|
| 86 | import 文 | `from backend.api.treatment_validation import (  # noqa: E402` | ― |
| 87 | import の名 | `    _resolve_comment_documentation_field_id,` | ― |
| 636 | 三重引用の帯 | `finding001の最終証明: 本物の _resolve_comment_documentation_field_id を` | ― |
| 641 | ★呼出★ | `resolved_id_1 = _resolve_comment_documentation_field_id(fake_client, "TS_P_KENSA")` | 2 位置（第三は省略） |
| 642 | ★呼出★ | `resolved_id_2 = _resolve_comment_documentation_field_id(fake_client, "TS_P_KENSA", None)` | 3 位置（第三 = None） |
- file は `backend/tests/test_c1_dml_migration_pkg_isolated_harness.py` 一枚のみ。棲家を別々に名指した（床(24)）= import 1・帯の中 1・★呼出 2★。
- 令289 の patch の def（己の紙 dir・order289_third_c_resolver_restore_v1.patch の 9-10 行目・逐語）: `def _resolve_comment_documentation_field_id(` ／ `client, set_code: str, field_name: Optional[str] = None`。
- 突合 = ★合致★。第一 client・第二 set_code は両呼出とも位置で渡り、第三 field_name は 641 で省略・642 で None を明示。∴ ★既定値 None は 641 が現に要求して居る★。

## §D 同じ函を import する file の数（二 pathspec）
- 命 ㋒: `git -C /mnt/c/DentalBI grep -lE '(^|[^A-Za-z0-9_])_resolve_comment_documentation_field_id([^A-Za-z0-9_]|$)' -- backend/tests/ backend/api/` → ★ 1 file★（harness のみ）。∴ harness 以外に此の名を書く file は ★現に無い★（0）。
- ★陽性対照★（同じ二 pathspec・module 名で当てた）: `... grep -nE 'from[[:space:]]+backend[.]api[.]treatment_validation[[:space:]]+import' -- backend/tests/ backend/api/` → ★ 4 file★（harness 86／test_denture_new_rpc_reconcile.py 11／test_findings_to_conditions.py 13／test_treatment_validation_tooth_quantity.py 6）。∴ 命は効いて居る。
- 範 = backend/tests/ と backend/api/ の二つのみ。backend/ 全体（㋐）でも 当たりは同じ 1 file。backend/api/ の当たりは 0 行 = ★製品 code からの呼手は現に無い★。

## §E 走らせて居らぬ
- 令171 に従ひ ★当該 test を一度も走らせて居らぬ★。現に落ちるか否かは ★測定不能★。
- 形からのみ述べる = import 先（backend/api/treatment_validation.py）に def が現に無い ∴ L86-88 の import は ★名を解き得ぬ形★ に在る。之は ★形の話★ であり 実行時の結果ではない。

## §F 三別と 数が意味せぬ事
- ★現に在る★: harness 1 file の中の 名の当たり 4 行（import 1・帯 1・呼出 2）／module を import する 4 file／treatment_validation.py の private def の対照 1 行。
- ★現に無い★: backend/ 全体の def （0 行・対照付）／harness 以外で名を書く file（0・対照付）／backend/api/ の当たり（0 行）。
- ★測定不能★: 当該 test が現に落ちるか（走らせて居らぬ）／的の樹の頂 dir 29 中 27（一度も当たつて居らぬ）。
- ★数が意味せぬ事★: 「呼出 2」は ★試験の中の呼出行の数★ であり、★実行時の呼出回数★ でも ★製品の呼手の数★ でもない（床(22)）。
