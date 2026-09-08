# main d83839730 と X head fffd757f2 の差 悉皆(讀取のみ) v1

令: subtask_thirdpc_fa06a3a1_a2_requirements_and_harness_diff_census_main_vs_xhead_readonly_001
親裁: 総監督裁 seq281040
席: ashigaru-third-2 / 樹: /mnt/c/DentalBI(讀取のみ・worktree新設0・checkout0・commit0・push0)
動詞: git diff --stat / git diff --unified=0 / git show / git grep / git cat-file -e のみ

## 節一 母数(令の範囲を一度に測つた数)
- `git diff --stat d83839730 fffd757f2 -- 'requirements*.txt' backend/tests/`
  = 45 files changed, 4016 insertions(+), 1695 deletions(-)
  (1 と数へたもの=git が列挙した file 一件)
- 上の内、本令が名指しした 2 種のみを以下で分ける。

## 節二 requirements 指名測定(pathspec を陽に二本書いた)
- `git diff --stat ... -- requirements.txt backend/requirements.txt`
  = 2 files changed, 159 insertions(+), 158 deletions(-)
  - `requirements.txt | 315`
  - `backend/requirements.txt | 2 +`
- 註: `'requirements*.txt'` 一本では backend/ 配下に当たらぬ(top-level のみ)。故に二本書いた。

## 節三 requirements.txt の行末(315 行の因)
| 版 | bytes | 行数(改行の数) | CRLF 行数 | pkg 行数 |
|---|---|---|---|---|
| main | 3072 | 158 | 0 | 157 |
| X | 2974 | 157 | 157 | 157 |
- pkg 行=空行でも `#` 始まりでもない行を 1 と数へた。
- 測つた事: main は LF、X は CRLF。全 157 行が行末で違ふ。
- 測つて居らぬ事: 何故 CRLF になつたか(生成経路)は測つて居らぬ。

## 節四 requirements.txt を pkg ごとに(main の値 / X の値 / 片側のみ)
| pkg | main の値 | X の値 |
|---|---|---|
| psycopg2-binary | ==2.9.10 | ==2.9.12 |
| pywin32 | ==311; sys_platform == "win32" (行末に註記コメント有) | ==311 |
- どちらにしか無い pkg: main のみ 0 件 / X のみ 0 件。
- 値が違ふ pkg = 2 件(pkg 名を鍵に突合し、値文字列の不一致を 1 と数へた)。
- difflib opcodes(equal 以外) = 3 件:
  1. insert  X[89:90]  = `psycopg2-binary==2.9.12`
  2. replace main[113:114] / X[114:115] = 上表 pywin32 の行(main 側は註記コメント付)
  3. delete  main[156:158] = 註記コメント 1 行 + `psycopg2-binary==2.9.10`
- 即ち main は psycopg2-binary の宣言が末尾寄りに在り、X は上寄りに在る。位置と版の双方が違ふ。

## 節五 backend/requirements.txt
| 版 | bytes | 行数 | CRLF 行数 | pkg 行数 |
|---|---|---|---|---|
| main | 421 | 14 | 14 | 12 |
| X | 662 | 16 | 16 | 14 |
- 値が違ふ pkg = 0 件。main のみ = 0 件。
- X のみ = 2 件: `anthropic`、`bcrypt`(何れも行末に「root requirements.txt と同版へ固定」旨の註記コメント付)。
- difflib opcodes(equal 以外) = 1 件: insert X[9:11]。
- 両版とも CRLF。此の file には行末の違ひは無い。

## 節六 harness file(本令が名指しした 1 本)
- path: backend/tests/test_c1_dml_migration_pkg_isolated_harness.py
- 両版に実在(`git cat-file -e` 何れも exit 0)。
- 行数: main 702 / X 642。
- `git diff --stat` = 1 file changed, 12 insertions(+), 72 deletions(-)。
- hunk 数(`--unified=0` の `^@@` を数へた) = 5。
- hunk の頭(逐語):
  1. `@@ -82,8 +81,0 @@ import pytest`
  2. `@@ -292,52 +283,0 @@ def _expect_raise_exception(conn, sql, message_substring):`
  3. `@@ -635,9 +575,6 @@ def test_09_concurrent_two_session_reapply_creates_no_duplicates(conn, dsn):`
  4. `@@ -646 +583,3 @@ def test_10_resolver_integration_kensa_comment_items_resolve_to_single_active_ro`
  5. `@@ -648,2 +587,3 @@ def test_10_resolver_integration_kensa_comment_items_resolve_to_single_active_ro`
- 消えた class/def 名(main に在り X に無い): `_FakeExecuteResult`, `_FakeQueryBuilder`(`select`/`eq`/`order`/`execute`), `_FakeSupabaseClient`(`table`), 及び test 名 `test_10_resolver_integration_kensa_comment_items_resolve_to_single_active_row`。
- 生じた def 名(X に在り main に無い): `test_10_migration_leaves_one_unambiguous_active_kensa_row`。
- 本文写しは上の hunk 頭 5 行のみ(150 字で切る令に従ひ、本文の逐語引用は行つて居らぬ)。

## 節七 import 先 module
- X 版 harness の import 行 = 標準 module + `psycopg2` + `psycopg2.errors` + `pytest`。repo 内 module の import = 0 件。
- main 版 harness は上に加へ 1 件: `from backend.api.treatment_validation import (_resolve_comment_documentation_field_id,)`(hunk 1 で消えた 8 行に含まれる。同 8 行には `sys.path.insert` の 3 行も含む)。
- 依て「import 先 module」は main 側にのみ 1 本在る: backend/api/treatment_validation.py。
  - 両版に実在。行数 main 15009 / X 14896。
  - `git diff --stat` = 1 file changed, 18 insertions(+), 131 deletions(-)。hunk 数 = 12。
  - 消えた def 名(main に在り X に無い): `_image_guidance_code_for_date`, `_exclude_same_month_photo_guidance`。
  - 生じた def/class 名 = 0 件。

## 節八 測つて居る途中で当たつた食ひ違ひ(黙つて迂回せぬ為に記す)
- main 版 harness が名指しで import して居る `_resolve_comment_documentation_field_id` は、
  main の backend/api/treatment_validation.py に 0 件(文字列出現も 0、`import *` 行も 0)。
- main 全樹(`git grep -- '*.py'`)で同名の `def` 定義 = 0 件。同名が現れる file = 1 本のみで、
  其れは harness 自身(即ち import 側の行)である。
- 依て測つた事: main 版 harness の当該 import は、main の樹に定義先を持たぬ。
- 測つて居らぬ事: 之が collection 時に何を起こすかは走らせて居らぬ(本令は讀取のみ)。X 版は当該 import を持たぬ。
- 本節は測つた事の列挙のみであり、何を為すべきかは書いて居らぬ。

## 節九 本紙が測つて居らぬ事
- backend/tests/ の残り 43 file の中身(母数として数のみ)。
- 行末が CRLF になつた経路、psycopg2-binary の版差が何に由来するか。
- 何れの版が正しいか(判定は本席の職分に非ず)。

as_of: 2026-09-07T05:50:44+09:00
