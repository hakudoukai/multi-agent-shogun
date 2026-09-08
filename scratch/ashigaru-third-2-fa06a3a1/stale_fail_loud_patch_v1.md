# stale 削除失敗の fail-loud 化 patch 案 v1 (order26)

席: ashigaru-third-2 / 板: fa06a3a1 / 令: subtask_thirdpc_fa06a3a1_a2_sync_source_cache_stale_failure_fail_loud_patch_proposal_001
親裁: 総監督 hs_6fe6f3bf (親 282416) / 起点紙: sync_source_cache_census_v1.md sha16=96d6b5e02dc90fcc 90 行

## 0. 令と実測の食ひ違ひ (先に開示)

- 令 base 記載 = 「共有樹 commit e2cfb09ab」。**実測**: e2cfb09ab は実在 (2026-09-07 07:02:30 の commit) だが、
  共有樹の現 HEAD は **25e417fe4a2b8d5b20e2a8456434429b90060282** (branch wp-a1-a3-3-20260723)。
  e2cfb09ab は HEAD の祖先 (`git merge-base --is-ancestor` exit=0)。
  当該 file の差分は **`git diff --numstat e2cfb09ab HEAD -- scripts/sync_source_cache.py` の出力が空**
  ＝ e2cfb09ab..HEAD の 2 commit は当該 file を変へて居らぬ。∴ base 差は本作業に及ばぬ (患部は同一 byte)。
- 令 起点紙記載 = 「order21 紙 sync_source_cache_census_v1(75123d04)」。**実測**: 当席の同名紙は
  **order24** の産で sha256=96d6b5e02dc90fccf4a6f71c95c3be85822569603f7b58ca4c1a5711ab7e20dc (90 行)。
  75123d04 なる sha16 を持つ file は当席 dir に**現に無い** (当席が作つた紙 4 本の sha は下記 §6)。
  75123d04 が何を指すかは**測つて居らぬ** (家老・総監督の手元の別紙かもしれぬ)。

## 1. 患部 (共有樹 25e417fe / scripts/sync_source_cache.py)

- file 実測: sha256=25a7b0a9ea4f0b0e219a8ff1df0c2507164d5ba7edaae21c961d7d30cf03e59c / 16961B / 456 行
  / `git status --porcelain -- scripts/sync_source_cache.py` 出力空 = 作業樹は HEAD と同一
- stale 三点 (行番は 456 行版):
  - `compute_stale_paths` L190-205 (純関数・例外を投げ得るのは fnmatch のみ)
  - `delete_stale` L266-284 (httpx DELETE・`resp.raise_for_status()` L283・timeout 30)
  - 呼出 L420-434 (`try:` L424 / `except Exception as e:` L433 / WARNING 印字 L434)
- 逐語 3 本 (計 132 字・≤150):
  - L418 `    exit_code = 1 if errors else 0`
  - L433 `    except Exception as e:`
  - L434 `        print(f"-- WARNING: stale cleanup failed: {e}", file=sys.stderr)`
- 現状の振舞ひ (measured by reading, 走らせて居らぬ):
  - L433-434 は `Exception` を総取りし、stderr へ WARNING を 1 行出すのみ。`exit_code` (L418 で確定) には触れぬ。
  - ∴ **upsert が全件成功 (errors=0) で stale 削除が全滅しても、この script の返値は 0**。
  - 併せて L444-448 の最終カウントも同型に握り潰す (本令の範囲外ゆゑ patch せず・存在のみ記す)。

## 2. patch (stale_fail_loud_v1.patch)

- sha256: f4ae488a5ab2f094ae8ed40a5b2bc0f8a5bce4c481c0013b512f8f1a577fe733 / 40 行 / 2144B / hunk 2
- 変更行数 (patch 本文の +/- 行を 1 行と数ふ): **追加 12 行 / 削除 4 行** (context 行は数へず)
- 適用後の file: 456 行 → **464 行** (+8 行)
- 何を足したか (4 点):
  1. `stale_attempted` / `stale_deleted` / `stale_cleanup_failed` の 3 変数を try の前に 0 初期化
  2. `stale = compute_stale_paths(...)` の直後に `stale_attempted = len(stale)`
  3. `except` を **`exit_code = 1` を立てる fail-loud** へ。印字を WARNING から
     `-- STALE_CLEANUP_FAILED: attempted=N deleted=M not_deleted=N-M error=…` へ (件数を stderr に出す)
  4. 末尾 L451 の FAILED 行に `stale_cleanup_failed={0|1}` を併記 (exit 非 0 の理由が upsert か stale かを読める様に)
- 既存の局所変数 `deleted` は `stale_deleted` へ改名 (印字文言の数字の出所を 1 つにするため)。他の呼出箇所は**無い**
  (`git grep -n 'deleted' -- scripts/sync_source_cache.py` の該当は当 block 内のみ)。

## 3. exit code の設計 (両案併記・当席は選ばぬ)

計上の単位: 「stale 削除の試み」= try block 1 回を 1 と数へ、「失敗」= 例外 1 個を 1 と数ふ。

- **案①(本 patch の形)**: stale 失敗を既存の `exit_code` へ合流させ **1** を返す。
  - 非 0 になるもの: upsert errors>0 ∪ stale 例外。0 に残るもの: それ以外全て。
  - pre-push hook は非 0 で **止まる** (push が通らぬ)。stale は cache 側の掃除ゆゑ、
    「同期本体が全件成功でも push が止まる」形になる。
- **案②(別 code 分離・本 patch では実装せず)**: `exit_code = 1` の代りに
  `exit_code = exit_code or 2` とし、2=stale 専用 code。hook 側で `1` は止め `2` は警告のみ、等の選り分けが可能。
  - 実装差分は 1 行 (`exit_code = 1` → `exit_code = exit_code or 2`)。hook 側 (`.git/hooks/pre-push` 等) の
    分岐追加が別途要る。hook 側の現行実装は**開いて居らぬ**ゆゑ、要る変更量は**測つて居らぬ**。
- どちらを採るか (= pre-push を止める是非) は総監督裁。当席は測つた事実のみ置く。

## 4. 数の限界 (この patch が数へられぬもの)

- `attempted` は `compute_stale_paths` 到達後に入る。∴ `get_cached_paths()` (L425) や `collect_files` (L426) で
  落ちた場合は `attempted=0 deleted=0 not_deleted=0` と出る。**「0 件試みた」ではなく「算出前に落ちた」**
  である事は、同時に出る `error=…` 本文でしか読めぬ。段階名 (stage) を持たせれば分離できるが、
  最小差分を優先して入れて居らぬ (入れるなら +4 行程度)。
- `delete_stale` は「何件消えたか」を DB から取り直して居らぬ (L284 は `len(stale_paths)` を返す)。
  ∴ `deleted` は**要求件数**であり、DB 側の実削除数は**測つて居らぬ**。

## 5. 検し (raw・逐語)

- `git -C /mnt/c/DentalBI apply --check -v <patch>` →
  `Checking patch scripts/sync_source_cache.py...` / exit=0
- `git -C /mnt/c/DentalBI apply --check -R <patch>` →
  `error: patch failed: scripts/sync_source_cache.py:421`
  `error: scripts/sync_source_cache.py: patch does not apply` / exit=1 (＝現 file には未適用)
- `python3 -m py_compile stale_fail_loud_probe_20260907/sync_source_cache_patched.py` → exit=0
  (適用後の姿を scratch に作つて通した。共有樹には適用して居らぬ)
  - 適用後 file: sha256=1bb2eb405e0781ccd6c0309ee8e6fcc99ff133c3e17db9d78c13c5166db1a9c1 / 464 行
- 事後の共有樹: `git status --porcelain -- scripts/sync_source_cache.py` 出力空 /
  sha256=25a7b0a9ea4f0b0e219a8ff1df0c2507164d5ba7edaae21c961d7d30cf03e59c (作業前と同一)

### 語の註

本紙に現れる `FAILED` / `STALE_CLEANUP_FAILED` は **script 自身の literal** (既存 L451 の印字文言と
本 patch が足す印字文言) であり、当席の判定語ではない。当席は当 patch の可否を判じて居らぬ。

## 6. 禁の実測

適用 0・commit 0・push 0・network 0・script 走行 0 (python は py_compile のみ)・hook 発火 0・
共有樹書込 0 (書いたのは当席 scratch dir のみ)・secret 0 字 (env は名も値も引いて居らぬ)・D 樹 0 打。

当席 dir の紙/patch (sha256 再測・床27):
- sync_file_list_diff_census_v1.md 398ceb23e7c21400… 75 行
- sync_source_cache_census_v1.md 96d6b5e02dc90fcc… 90 行
- hook_state_file_v1.patch 90dd8d513c07d1d9… 18 行 (総監督が共有樹へ適用済 commit e2cfb09ab)
- hook_state_file_patch_v1.md 25476cd2bb354d76… 98 行
- stale_fail_loud_v1.patch f4ae488a5ab2f094… 40 行 (本紙の産)

as_of: 2026-09-07T07:16:33+09:00 (註追記の後に押し直した)
