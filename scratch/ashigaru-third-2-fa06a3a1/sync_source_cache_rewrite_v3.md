# sync_source_cache patch v3 ―― 投入側を git 追跡簿基準へ + EXCLUDE 帯 (order36 產)

as_of 2026-09-07 15:0x JST / 席=ashigaru-third-2 / 令=karo-third order36。実装と試験は ★自席樹のみ★
(/home/hakudoukai/a2/wt-v3-1fbd0aa0・枝 a2-fa06a3a1-sync-rewrite-v3)。DB 接続0・網0・push0・D 樹不触。
三択語=測つた/測つて居らぬ/測れぬ。1 = file 1 本 (数の後に何を 1 と数へたかを書く)。

## §1 base と 2 commit
base = ★1fbd0aa0fe362d2498ad090bd46f5d6fe5cd2345★ (`git rev-parse HEAD` 実測)。前紙 o34/o35 の時点は
59ef7ecd0 で、其の後 ★2 commit★ 進んで居た。対象 2 file に触れた commit は其の 2 の内 ★0★
(`git log --oneline 59ef7ecd0..HEAD -- scripts/sync_source_cache.py tests/test_sync_source_cache.py`
が 0 行・測つた)。∴ v2 patch は新 base でも `--check` rc=0 で当たつた。
- ce3b08dbe = v2 (stale 判定を git 差分基準へ畳む + 試験24本) ―― 前紙の 0002 patch を其の儘
- 3155e8dc0 = v3 (本紙の主題) ―― 投入側 + 帯 + 試験3本

## §2 本命 (案1): collect_files の入口を git の追跡簿へ
v2 まで `repo_root.glob(INCLUDE_PATTERNS)` ―― ★git を一切見ぬ★ ゆゑ追跡外の
`backend/.venv/**/*.py` が `backend/**/*.py` に当たつて表へ入つた (2026-07-19 の 1 走行で 15,288 行)。
v3 は母集合を `git ls-files -z` の追跡済 path に替へ、INCLUDE/EXCLUDE の掛け方は従前どほり残す。
matcher は stale 側と同じ `matches_include_patterns` を使ひ、★入口と出口で glob の意味を 1 本に揃へた★
(v2 で入れた `_glob_pattern_to_regex` の再利用・新しい照合器は足して居らぬ)。

## §3 no-silent-failure の形 (退避を作らぬ)
`list_tracked_files()` は git を通せぬ時 ★例外で止まる★。作業樹 glob への無言の退避を置かぬ。
- `FileNotFoundError` (git 実行体が無い) → `RuntimeError("git を実行できぬ: <root>")`
- `CalledProcessError` (repo でない/壊れて居る) → `RuntimeError` に ★rc と stderr を載せる★
退避を置けば「git の無い環境では従前どほり追跡外も入る」形になり、直した筈の道が黙つて戻る。
∴ 止まる方を選んだ (床 no-silent-failure)。走らせる側から見れば ★失敗が音を立てる★。

## §4 帯 (案2): EXCLUDE_DIRS に名前でも止める
```
EXCLUDE_DIRS = {"node_modules", "__pycache__", "dist", ".git",
                ".venv", ".venv-linux", "venv", ".codex_audit"}
```
追跡簿基準が主の止め、名前は ★外側の帯★。万一 venv を git add した場合にも入らぬ。
令に在つた 3 名 (.venv/.venv-linux/.codex_audit) に加へ `venv` も置いた (同じ物の別名ゆゑ)。

## §5 試験 3 本 (★既存 file へ追加・新規 file 0★)
足した先 = `tests/test_sync_source_cache.py` (472 行 → 535 行)。既存 24 本は 1 本も消して居らぬ。
1. `test_collect_files_excludes_untracked_venv_paths` ―― tmp 樹に `backend/.venv/...` `.venv-linux/...`
   `.codex_audit/...` を置き ★git add せず★、列挙に出ぬ事。併せて帯 3 名が EXCLUDE_DIRS に在る事。
2. `test_collect_files_keeps_tracked_include_paths` ―― 追跡済かつ INCLUDE 一致は出る事
   (`scripts/kept.py` `backend/app.py` の 2 本ちやうど = 意味を保つた事の裏)。
3. `test_collect_files_raises_when_git_unusable` ―― `subprocess.run` を塞ぎ、git 実行体不在と
   rc=128 の両方で `RuntimeError` が上がり、文面に rc と stderr が載る事。
DB 接続0・網0 (httpx へは一切触れて居らぬ・git は tmp 樹の小 repo のみ)。

### 走行の生 (raw = order36_pytest_raw.txt sha16 3e9058da3dc9efaf 8 行)
```
$ python3 -m pytest tests/test_sync_source_cache.py -p no:cacheprovider --basetemp=<自席> -rsxX -q
...........................                                              [100%]
27 passed in 0.66s      rc=0
```
27 = 試験関数 1 本を 1 と数へた総数 (v2 の 24 + 本紙の 3)。★skip = 0★ ―― raw 全文に `skip` の語が
★0 回★ (`-rsxX` は skip/xfail が在れば 1 行づつ出す指定・出て居らぬ)。fail 0・error 0。

## §6 --dry-run 新旧 byte 比較 (v2 と ★同条件★・同じ樹・同じ囮)
自席樹に追跡外の囮 4 本 (`.venv` 2 / `.venv-linux` 1 / `.codex_audit` 1) を置き、script だけを
v2↔v3 で入れ替へて `--dry-run` を 2 度走らせた (DB 接続0・SQL は標準出力へ出るのみ・実行 0)。
| | 列挙 file 数 | 生成 SQL の byte |
|---|---|---|
| v2 | 4,117 | 181,271,004 |
| v3 | 4,113 | 181,271,705 |
- ★file 数の差 = 4★ = 囮 4 本ちやうど。集合を突き合はせると ★v2 のみ = 囮 4 本／v3 のみ = 0 本★。
  ∴ ★git 追跡分は同一★ で、減つたのは追跡外分だけである (測つた)。
- byte は v3 が ★701 多い★。内訳 = 自身 `scripts/sync_source_cache.py` が v3 で太つた分
  ★+2,280★ − 囮 4 本の SQL ★1,579★ = ★701★ ―― ★実測差と 1 byte も残らず合ふ★
  (囮の SQL は走行が埋めた commit_hash `3155e8dc0` で数へ直した)。
  ∴ byte が増えたのは「追跡外が減らなかつた」ではなく「同期対象の自分自身が長くなつた」ゆゑ。

## §7 器と後片付け
- patch = `0003-sync_source_cache-v3-tracked-index-plus-exclude-belt.patch` (base 1fbd0aa0f)。
  base へ detach して `git apply --check -v` ★rc=0★・`--stat` = 2 files changed,
  556 insertions(+), 21 deletions(-)。検分後 枝へ戻し `status --porcelain` は空 (測つた)。
- 囮 4 本と 181MB×2 の dry-run 出力は ★消した★ (大きさは上表に控へた)。pytest の basetemp も消した。
- 樹は本紙送出後に `git worktree remove` する。★枝 (ref) は残す★・push 0。

## §8 ★開示★
1. `EXCLUDE_DIRS` の照合を ★絶対 path の parts → repo 内 rel の parts★ へ狭めた。従前は repo_root 自身の
   親 dir 名が "dist" 等だと全 file が落ちる形だつた。意味を広げてはをらぬが ★令に無い直しである★。
2. commit 時に hook が `Supabase secret scan PASS: no tracked secret values detected.` と出した
   ―― ★hook の語であり当席の判定語ではない★。
3. 走らせたのは `tests/test_sync_source_cache.py` の 1 file のみ。★suite 全体は走らせて居らぬ★
   (他 file は DB/網に触れる物が在るか ★測つて居らぬ★)。
4. `.codex_audit` が実際に表へ入つた証跡は依然 ★測つて居らぬ★ (囮で道が在る事は示したが、
   07-19 の走行で入つたかは当席の器では測れぬ)。
5. 15,288 (総監督実測) と 15,271 (order33 の引き算) の ★17 の食ひ違ひ★ は未だ詰まつて居らぬ。
6. export/DELETE は打つて居らぬ (家老裁「v3 軍師の検分の後」に従ふ)。DB の器は当席に 0 本の儘。

## §9 sha 再測 (床(27)・as_of 15:0x)
c05138103db14f7b 678 行 0003…v3.patch / 3e9058da3dc9efaf 8 行 order36_pytest_raw.txt /
83842dd17d680485 119 行 o35 紙 / b99e75d8d356ec46 554 行 0002 patch(v2)
