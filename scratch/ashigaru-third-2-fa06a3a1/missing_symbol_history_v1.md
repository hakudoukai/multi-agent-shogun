# `_resolve_comment_documentation_field_id` の来歴(讀取のみ) v1

令: subtask_thirdpc_fa06a3a1_a2_missing_resolver_symbol_history_git_log_s_readonly_001
親裁: 総監督裁 seq280975(X 版正)・order15 節八 の食ひ違ひ
席: ashigaru-third-2 / 樹: /mnt/c/DentalBI(讀取のみ・worktree 新設 0・checkout 0・commit 0・push 0・走行 0)
動詞: git log -S / git show / git show -s / git diff-tree --name-only / git rev-list --count / git merge-base --is-ancestor

## 節一 母数
- `git log -S_resolve_comment_documentation_field_id --oneline --all -- backend/` = **7 commit**
  (1 と数へたもの=git が列挙した commit 一件)
  59b9f4dd8 / 8a23afa8a / 7f39168d3 / c6ea84e56 / 7f3f371b9 / db86b2099 / 4b9912e6c

## 節二 定義が生じた commit
- `git log -S'def _resolve_comment_documentation_field_id' --all -m -- backend/api/treatment_validation.py`
  = **1 件のみ**(merge も -m で見た上で 1 件)。
- sha **59b9f4dd8** / date 2026-07-23 00:34:22 +0900
  件名: `feat(karte_visit_items): D1b identity/lineage columns + R8 comment attribution (WP-C1)`
  touched file 数 4 / 内 symbol 出現 file = backend/api/treatment_validation.py
  当該 commit の diff: `+def` 1 行・`-def` 0 行。

## 節三 「定義を消した commit」を探した結果
- 上の `-S'def …'` の該当は 59b9f4dd8 の 1 件のみ。**定義を消した commit = 0 件**(測つた範囲)。
- 各 tree での `def` の数(`git show <rev>:backend/api/treatment_validation.py` を数へた):
  | rev | def 数 |
  |---|---|
  | 59b9f4dd8 | 1 |
  | 8a23afa8a | 1 |
  | 7f39168d3 | 1 |
  | c6ea84e56 | 0 |
  | 7f3f371b9 | 0 |
  | db86b2099 | 0 |
  | 4b9912e6c | 0 |
  | main d83839730 | 0 |
  | X fffd757f2 | 0 |
- 祖先関係(`git merge-base --is-ancestor`):
  - 59b9f4dd8 は main の祖先 **で無い** / X の祖先 **で無い**
  - 7f39168d3 は main の祖先 **で無い** / X の祖先 **で無い**
  - c6ea84e56 は main の祖先 **で無い**
  - 7f3f371b9 は **main の祖先** かつ **X の祖先**
  - db86b2099 は main の祖先 **で無い** / **X の祖先**
  - 4b9912e6c は main の祖先 **で無い** / X の祖先 **で無い**
- 依て測つた事: 定義は「消された」のではなく、**定義を持つ系統(59b9f4dd8→7f39168d3)が main / X の祖先に入つて居らぬ**。
- 測つて居らぬ事: 其の系統が何故 merge されなかつたか(経緯は git の外に在る)。

## 節四 harness 側の import が現れた commit と、其の commit が定義側を触れたか
- harness file の symbol 出現数(`git show <rev>:backend/tests/test_c1_dml_migration_pkg_isolated_harness.py` を数へた):
  | rev | 出現 |
  |---|---|
  | 7f39168d3 | 4 |
  | c6ea84e56 | 4 |
  | 7f3f371b9 | 4 |
  | db86b2099 | 0 |
  | 4b9912e6c | 7 |
  | main d83839730 | 4 |
  | X fffd757f2 | 0 |
- **7f3f371b9** / date 2026-09-02 22:38:22 +0900
  件名: `salvage(safe): third-PC 甲樹の生きた成果のうち ★既存fileを一字も上書きせぬ 28本★ のみを live main 直上に載せる`
  touched file 数 28 / 内 symbol 出現 file 4 本(harness 3 種+当該 harness、名は下記)
  - backend/tests/test_c1_dml_migration_pkg_isolated_harness.py
  - backend/tests/test_migration_049_ddl_isolated_harness.py
  - backend/tests/test_migration_050_051_karte_visits_confirm_cas_isolated_harness.py
  - backend/tests/test_migration_052_karte_visits_date_amendment_isolated_harness.py
  - 同 commit は backend/api/treatment_validation.py を **触れて居らぬ**(touched 名に無し)。
    件名の「既存 file を一字も上書きせぬ」と整合する(新規 file のみ載せた)。
- 即ち harness(import 行を含む)は main 系統へ載つたが、import 先の定義は同系統に無い。

## 節五 「取り残された」区間(first / last)
- main 系統で当該 harness を触つた commit = `git log --oneline d83839730 -- <harness>` の該当 **1 件のみ**(7f3f371b9)。
- first = **7f3f371b9**(2026-09-02 22:38:22 +0900、出現 4 で登場)
- last  = **d83839730**(2026-09-07 05:25:30 +0900、live main、出現 4 のまま)
- 区間の commit 数 = `git rev-list --count 7f3f371b9..d83839730` = **833**。
- 此の 833 の間、main 系統で harness を触つた commit は 0 件。

## 節六 X 枝側(order15 既測の再刷)
- **db86b2099** / date 2026-09-05 15:15:05 +0900 / 件名 `test(backend): restore isolated harness collection`
  touched file 数 3 / 当該 harness の symbol 出現を 4 → **0**(diff の `-出現` 4・`+出現` 0)。db86b2099 は X の祖先。
- X head **fffd757f2** の harness 出現 = **0**(order15 節七と同数を再測して一致)。
- 別途 **4b9912e6c**(2026-09-07 04:39:22、件名 `test(c1-dml-harness): collection error を 0 にする ―― 廃止済 private resolver の import を importorskip+getattr 護りへ替へ、当該 1 test のみ skipif`)は
  出現 7 を持つが、main / X いづれの祖先でも無い。

## 節七 本紙が測つて居らぬ事
- 走行は行つて居らぬ(讀取のみの令)。collection 時に何が起きるかは測つて居らぬ。
- 59b9f4dd8 系統が merge されなかつた経緯、及び 833 commit の中身。
- 何れの版を採るべきかは書いて居らぬ(本席は測つた事のみを記す)。

as_of: 2026-09-07T05:56:10+09:00
