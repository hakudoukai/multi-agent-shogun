# sync_file_list.txt +122 行 の分類（讀取のみ・order23）

席: ashigaru-third-2 ／ 令: subtask_thirdpc_a2_sync_file_list_diff_122_lines_census_readonly_001
対象: /mnt/c/DentalBI/scripts/sync_file_list.txt（共有樹・追跡下・working tree が HEAD と相違）
用: 総監督の裁材（戻す/commit する/放置 の裁は当席の職に非ず・本紙に裁は書かぬ）

## 一. 母数（1 = diff の追加行 1 本）

- `git diff --numstat` = `122	0	scripts/sync_file_list.txt` ／ `--stat` = `1 file changed, 122 insertions(+)` … 測つた
- 追加行 122 本 / 削除行 0 本 / hunk 53 個 … 測つた
- 令の云ふ母数 122 と当席の実測 122 は同じ数である … 測つた
- 追加 122 本の中に重複する行は 現に無い（相異なる 122 本） … 測つた

## 二. 行の形（1 = 追加行 1 本）

- `=` を含む行 0 本 ／ 空白を含む行 0 本 ／ `[A-Za-z0-9._/-]` 以外の文字を含む行 0 本 … 測つた
- 行長 最短 22 字 / 最長 114 字。全 122 本が repo 相対 path の形であり、値を持つ行は 現に無い … 測つた

## 三. dir 別の本数（1 = 追加行 1 本・和が母数）

| top dir | 本数 |
|---|---|
| frontend | 37 |
| backend | 33 |
| scripts | 27 |
| supabase | 21 |
| tests | 3 |
| .claude | 1 |
| **和** | **122** |

- 和 122 = 母数 122 … 測つた

## 四. 実在・不在（1 = 追加行 1 本）

- 共有樹に file が 現に在る = 122 本 ／ 現に無い = 0 本（`os.path.exists`） … 測つた

## 五. 追跡・未追跡（1 = 追加行 1 本・`git ls-files` 全集合との突合）

- 追跡下 = 85 本 ／ 未追跡 = 37 本 … 測つた
- 追跡 85 の内訳: scripts 26 / backend 24 / supabase 21 / frontend 10 / tests 3 / .claude 1（和 85） … 測つた
- 未追跡 37 の内訳: frontend 27 / backend 9 / scripts 1（和 37） … 測つた
- ∴ 此の一覧は git の追跡下に無い file 37 本を含んで居る … 測つた
- 其の 37 本が何故未追跡か（.gitignore か未 add か）は 測つて居らぬ

## 六. 冠正本 path の有無

- `.claude/` 配下・`/rules/` を含む・`CLAUDE.md` に当たる行 = 1 本。逐語 `.claude/rules/no-repo-copies-worktree-only.md` … 測つた
- 右の 1 本は `git ls-files` に 現に在る（追跡下）。中身は開いて居らぬ（本令は path の分類のみ） … 測つた

## 七. secret の掃き出し（当席の禁: secret 0 字）

- 追加 122 本の中に値の形（`=` 付き・空白付き）は 現に無い … 測つた
- 名に `token` を含む path = 2 本（`backend/services/designer_chat_tokens.py`・同 tests 版）。
  ★是は file 名であり値ではない。当席は右 2 file を開いて居らぬ★ … 測つた
- `.env` / `secret` / `credential` / `password` / `apikey` / `.pem` / `.key` に当たる名 = 0 本。本紙に secret の値は 0 字 … 測つた

## 八. file の形（参考・1 = file の行 1 本）

- HEAD 版 4026 行 → 作業樹 4148 行（差 122）。両版とも昇順に整列して居る … 測つた
- 追加 122 本は末尾一括ではなく 53 箇所へ挿入（初 hunk `@@ -53,0 +54 @@`・終 hunk `@@ -3901,0 +4022,2 @@`） … 測つた
- 追加 122 本の中に HEAD 版へ既出のものは 0 本 … 測つた
- 作業樹 sha256 `5913ace7888714336d12fb5ae514cc5a1aec7cfa51c22819ed28f34f1c369d3f`（225889 byte）／ HEAD blob `ce4fba084c20faefc85b388c37aacee7199a69f9` ／ `git status --porcelain` = ` M scripts/sync_file_list.txt` … 測つた

## 九. 禁の遵守

- `git checkout`/`restore`/`add`/`stash` = 0 回 ／ file 編集 0 ／ hook 実行 0 ／ D 樹（a2/wt-964a06d0-d3adf65b）0 打
- 共有樹への書込 0 ／ push・remote 書込 0 ／ pytest 走行 0 ／ 本令の範囲外（増えた因・戻す手立て）は書いて居らぬ

## 十. 結び（三択）

- 母数 122・dir 別の和 122・実在 122/不在 0・追跡 85/未追跡 37・冠正本 path 1 本 = 測つた
- 未追跡 37 本の未追跡たる理由 = 測つて居らぬ
- 此の差分を残すか戻すかの裁 = 当席の職に非ず（総監督の裁を待つ）

as_of: 2026-09-07T06:35:33（当席 third_pc 実測時刻）
