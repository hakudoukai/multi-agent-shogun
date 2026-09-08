# 追跡 file を書かぬ設計への patch 案（order25・apply --check まで）

席: ashigaru-third-2 ／ 令: subtask_thirdpc_a2_pre_push_hook_no_tracked_file_write_patch_proposal_apply_check_only_001
親裁: 総監督 hs_6e741edf ／ 材: order24 紙 sha16 `96d6b5e02dc90fcc`（書込 1 箇所・code 側読手 0）
★適用 0・commit 0・push 0・hook 実行 0・script 実行 0・.gitignore 編集 0★

## 一. 患部（当席が今 measure し直した数）

- file `/mnt/c/DentalBI/scripts/sync_source_cache.py` sha256 `0d5a2258ef1adccb4c4093b82568d575d1a566e1a67eb03254d9b367e00f47a3`・455 行 … 測つた
- `git status --porcelain -- scripts/sync_source_cache.py` は 0 行（作業樹と index が同じ） … 測つた
- 患部 = L436(註)・L437(path 組立)・L438(再走査)・L439(write_text)・L440(印字) の 5 行 … 測つた

## 二. 樹と sha の食ひ違ひ（★令の言と実測が違ふ★）

- 令は「main d83839730」と記す。実測: `main` = `3165e90450f3de740775ff39fda1f5fee2d034f8` … 測つた
- `origin/main` = `ed311f1b899554cc47a5ba80ce4136b774150905` ／ 作業樹 `HEAD` = `07f068b1ca84e6ae71b7a49b364f919909cc86a1`（枝 `wp-a1-a3-3-20260723`） … 測つた
- `d83839730` は commit として 現に在るが、`for-each-ref --contains` が返す枝は `refs/heads/wp-a1-a3-3-20260723` であり main ではない … 測つた
- 当該 file は main と HEAD で 1 行違ふ（`@@ -137,2 +137,3 @@` の 1 行増・当席の患部とは別処） … 測つた
- ∴ apply の当否は「共有樹の作業樹」と「main の版」の 2 つで別々に測つた（下記 五・六） … 測つた

## 三. 置き場の候補（1 = 候補 1 本・可否は三択語）

| # | 置き場 | 無視規則の逐語（`git check-ignore -v`） | dir の現況 | 可否 |
|---|---|---|---|---|
| ① | `.git/` 配下 | 規則に当たらぬ（git は `.git` を初めから見ぬ） | 共有樹では dir | 追跡され得ぬ = 測つた。★但し linked worktree では `repo_root/.git` は file であり（a2/wt-964a06d0-d3adf65b で実測）、dir 作成が当たらぬ★ |
| ② | `tmp/` | `.gitignore:86:tmp/` | 現に在る | 追跡外 = 測つた。INCLUDE_PATTERNS に当たる glob 現に無い = 測つた |
| ③ | `.cache/` | `.gitignore:85:.cache/` | 現に無い（作成要） | 追跡外 = 測つた。★但し `.cache/audit_redo/**/*.txt` が INCLUDE_PATTERNS(L82-83) に在り、其の配下は cache へ送られる★ |
| ④ | `logs/` | `.gitignore:123:logs/` | 現に在る | 追跡外 = 測つた |
| ⑤ | `run/` | `.gitignore:122:run/` | 現に在る | 追跡外 = 測つた |
| ⑥ | `tmp_sync/` | `.gitignore:87:tmp_sync/` | 現に無い（作成要） | 追跡外 = 測つた |
| ⑦ | repo 外（例 `~/.cache/...`） | .gitignore 不要 | 測つて居らぬ | `repo_root` 相対では辿れず絶対 path が要る = 測つた |

- ★.gitignore は 1 字も触れて居らぬ★（sha256 `218d04468255aae9c69e89cb7bf799dd1cf7ff5bdcf8cd00ba997e366e0b018b`・2987 byte・126 行、読んだだけ） … 測つた
- 本 patch は ② `tmp/` を採る。因 = 既に無視規則に載る(L86)・dir が 現に在る・INCLUDE_PATTERNS に当たらぬ・`.git` と違ひ linked worktree でも同じ形で当たる … 測つた

## 四. patch の逐語（`scratch/ashigaru-third-2-fa06a3a1/hook_state_file_v1.patch`）

```
--- a/scripts/sync_source_cache.py
+++ b/scripts/sync_source_cache.py
@@ -433,11 +433,12 @@
     except Exception as e:
         print(f"-- WARNING: stale cleanup failed: {e}", file=sys.stderr)
 
-    # 同期対象リストをsync_file_list.txtに自動更新（参照用）
-    list_path = repo_root / "scripts" / "sync_file_list.txt"
+    # 同期対象リストを追跡外 state file へ更新（参照用・追跡 file は書かぬ）
+    list_path = repo_root / "tmp" / "sync_file_list.txt"
+    list_path.parent.mkdir(parents=True, exist_ok=True)
     all_files = collect_files(repo_root)
     list_path.write_text("\n".join(all_files) + "\n", encoding="utf-8")
-    print(f"-- Updated sync_file_list.txt: {len(all_files)} files", file=sys.stderr)
+    print(f"-- Updated {list_path}: {len(all_files)} files", file=sys.stderr)
 
     # 最終カウント表示
     try:
```

- patch sha256 `90dd8d513c07d1d9215a94e6fabecb61d3bfd3c225e2a95f528291d056babfe6`・18 行・881 byte … 測つた
- 変へたのは 5 行 → 6 行（`mkdir(parents=True, exist_ok=True)` の 1 行増）。他の hunk は 現に無い … 測つた
- order24 で code 側の読手が 0 本と測れて居るゆゑ、旧 path を読む側の互換配慮は本 patch に要らぬ … 測つた

## 五. `git apply --check`（共有樹・作業樹 HEAD `07f068b1`）の逐語

```
$ git -C /mnt/c/DentalBI apply --check -v <patch>
Checking patch scripts/sync_source_cache.py...
exit=0
```

- 逆当て `--reverse` は `error: patch failed: scripts/sync_source_cache.py:433` / `error: ... patch does not apply` / exit=1
  ∴ 此の patch は★まだ当たつて居らぬ★（既適用ではない） … 測つた

## 六. main 版への当否（別測・`git apply` は作業樹しか見ぬゆゑ GNU patch で測つた）

- `git show main:scripts/sync_source_cache.py` を scratch 配下 `mainprobe_20260907/` へ取り出した（共有樹への書込 0）。取り出した版 sha256 `cdbf22fcbb0cca54cb4197ef3851265c2c8d6afd5fbda5e96f7bc0add49404fc`・16841 byte … 測つた
- 逐語: `checking file scripts/sync_source_cache.py` / `Hunk #1 succeeded at 432 (offset -1 lines).` / exit=0
  ★"succeeded" は GNU patch の語であり当席の判定語に非ず★ … 測つた
- ∴ main の版でも同じ hunk が 1 行ずれ（offset -1）で当たると 測つた

## 七. 本 patch が★含まぬ★もの（所在のみ・裁は監督 lot）

- 既に追跡下に在る `scripts/sync_file_list.txt` を消す・戻す・commit する事 = 含まぬ（総監督裁 hs_b784474a で放置と決まつた由を令に読んだ）
- `.gitignore` の編集 = 含まぬ（`tmp/` は既に L86 に在る）
- pre-push hook 本体（`.git/hooks/pre-push` sha256 `6284d288f4f4e21de5ea3d4c6e56f24c75a450e8b0c0ad7858915670a01a7d49`）の編集 = 含まぬ
- 移行後に旧 file を読む者が現れた時の道 = 測つて居らぬ

## 八. 禁の遵守

- 適用 0 ／ commit 0 ／ push 0 ／ hook 発火 0 ／ script 実行 0 ／ `.gitignore` 編集 0 ／ 共有樹への書込 0（取り出しは scratch 配下） ／ D 樹 0 打 ／ secret の値 0 字 … 測つた

## 九. 結び（三択）

- 患部 5 行・候補 7 本の無視規則と可否・patch の当否（作業樹 exit=0／main 版 offset -1 で当たる）・逆当て不可 = 測つた
- 令の云ふ「main d83839730」と実測の main sha の食ひ違ひ = 測つた（d83839730 は wp-a1-a3-3 の commit）
- 何処へ移すかの最終の裁・適用の可否 = 当席の職に非ず（監督 lot の裁を待つ）

as_of: 2026-09-07T06:54:50（当席 third_pc 実測時刻）
