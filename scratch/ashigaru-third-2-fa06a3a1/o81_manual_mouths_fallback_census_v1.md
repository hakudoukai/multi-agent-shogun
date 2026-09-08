# order81: 手打ち 4 箇所が現に危険側へ落ちるかの實測 (讀取のみ・main() 不走・DB 0・push 0・書換 0)

as_of 2026-09-08T06:1x JST / 席 ashigaru-third-2 / 令 order81 (msg_20260908_060540_4d24e811)
底本 v3 = origin/main 抽出 766 行 `16e2db65f8cb48fa` / 前紙 o78 `e2fef4b05c09f3b5`・o79 `3f1f8c2f45e55e1f`・o80 `0070f41f46323d2a` 不触
repo = /mnt/c/DentalBI (共有樹)。走 = 0 回 (本紙は讀取のみ ∴ 通算 3/5 の儘)

## §0 結び (二行)
★state file 経路は現に死んで居る★ ―― `<repo>/tmp/sync_last_commit.txt` は ★共有樹にも 当席の作業樹にも 在らぬ★。
∴ 手打ちの旗無し走行が差分側へ行くか全表側へ落ちるかは ★DB の 1 行だけに懸かつて居る★ (綱が 1 本)。

## §1 何を 1 と数へたか / 網の形
1 = 口 1 箇所 / file 1 本 / 行 1 行。
「口」= 人が其の儘打てば v3 が走る形で書かれて居る行。単なる言及 (script の名を挙げるだけの散文) は数へぬ。
網 = `grep -n 'sync_source_cache.py'` を CLAUDE.md・docs/setup_secondpc.md・scripts/git-hooks/pre-push に当てた。
落した行 (言及であつて口では無い): setup_secondpc.md:39 (env 名の差の説明)・:130 (file 一覧)。

## §2 分れの鎖 (v3 逐語・旗無しで走らせた時)
`:583-588` 旗の讀み → `:693` `if no_stale:` (旗無しゆゑ入らぬ) → `:697` `all_local_paths = collect_files(repo_root)`
→ `:701` `prev_commit = get_last_sync_commit_from_db()` (:331-347 = 最新 1 行の commit_hash を 1 request)
→ `:706` 空なら `read_last_sync_commit_from_state(repo_root)` (:311 = `<repo>/tmp/sync_last_commit.txt` を讀む)
→ `:708` 得ても `commit_exists` (:350 = `git cat-file -e <rev>^{commit}`) で解けねば `-- STALE_FALLBACK_FULL_SCAN: reason=prev_commit_unresolvable` を出して None へ
→ `:713` `if full_stale_scan or not prev_commit:` → ★全表★ `compute_stale_paths(cached_paths, all_local_paths)`
→ 然らずんば `:721` `stale_paths_from_git(...)` = ★差分★。
`repo_root` は `:579 Path(__file__).parent.parent` ∴ ★走らせた script の在る樹★ が repo_root になる (作業樹から打てば其の作業樹)。

## §3 state file の生死 (實測)
| 検め | 實測 |
|---|---|
| 定義 | `:123 LAST_SYNC_COMMIT_FILE = "sync_last_commit.txt"` / `:308 repo_root / "tmp" / …` |
| 共有樹 /mnt/c/DentalBI/tmp/sync_last_commit.txt | ★在らぬ★ (ls = No such file or directory) |
| 当席の作業樹 (wt-first-parent) の同 path | ★在らぬ★ |
| 追跡されるか | ★されぬ★ (.gitignore:86 `tmp/`) ∴ clone・worktree・CI runner へ ★travel せぬ★ |
| 何時書かれるか | `:754 if exit_code == 0:` の時のみ `:755 write_last_sync_commit` ∴ ★全件が通つた走行の後だけ★ |
∴ 初めて手打ちする者の樹には ★必ず無い★。CI runner も毎回新しいゆゑ ★必ず無い★ (CI の守りは `--no-stale` 一本)。

## §4 手打ち 4 箇所 (一つづつ)
| # | file:行 | 逐語 (要) | 旗 | state file | 落ちる先 |
|---|---|---|---|---|---|
| 1 | CLAUDE.md:528 | 手動で全件同期したい場合: `python scripts/sync_source_cache.py` | ★無し★ | 在らぬ | ★DB 次第★ (返し且つ解ければ差分・然らずんば全表) |
| 2 | docs/setup_secondpc.md:90 | `SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_ROLE_KEY" python scripts/sync_source_cache.py` | ★無し★ | 在らぬ | ★DB 次第★ |
| 3 | docs/setup_secondpc.md:108 | `python scripts/sync_source_cache.py` が `Errors: 0` で完走 (点検表の 1 行) | ★無し★ | 在らぬ | ★DB 次第★ |
| 4 | scripts/git-hooks/pre-push:67 | 失敗時の文言 `run 'python scripts/sync_source_cache.py' manually` | ★無し★ | 在らぬ | ★DB 次第★ |
∴ ★4 箇所とも旗を持たぬ★。而して 4 箇所とも state file には頼れぬ ∴ ★4 本とも同じ 1 本の綱 (DB) に懸かる★。

## §5 測れぬ物 (測れぬと書く)
- ★DB が現に何を返すか★ = 測れぬ (当席は DB を讀まぬ)。返さねば・或いは返した commit が此の樹で解けねば ★全表★ へ落ちる。
- ★他 PC (main/second/mac) の樹に state file が在るか★ = 手が届かぬ ゆゑ測れぬ。
- ★D 樹 (a2/wt-964a06d0-…) の同 path★ = 軍師判定待ちゆゑ ★触れて居らぬ★ (測つて居らぬ)。

## §6 全表へ落ちた時に消え得る本数 (元素を揃へる)
消える集合 = `compute_stale_paths(cached_paths, all_local_paths)`
 = ★DB の file_path 集合★ − ★現樹 collect_files★ の内 INCLUDE に当たる物 (`:256`)。
∴ ★元素は「DB の行」である★。
- ★当席の proxy 1,722 / 1,724 (o78) を此処へ代入してはならぬ★。彼は ★git の path★ 元素 (局所 ref 236 本の合併 − 現樹) であり、
  DB に無い path は消えぬし DB にしか無い path は proxy に出ぬ ∴ 上限にも下限にもならぬ。
- DB 行元素での見積り = 残 ★5,668 行★ (総監督殿 實測 seq285143) − 現樹 ★4,185 本★ (当席 git 数へ) = ★1,483★。
  ★但し★ 之は「現樹 4,185 本が悉く DB に在る」時のみ成り立ち、且つ 2 つの數は ★別人・別器の實測★ ゆゑ差を取るのは近似である。
- ∴ ★現に何本消えるかは 当席には測れぬ★。述べ得るのは「元素は DB 行であり、見積りは 1,483 (前提つき)」までである。

## §7 境界
讀取のみ・v3 の main() 不走・走 0 回 (通算 3/5)・DB 讀 0 書 0・SQL 0・push 0・製品 file 書換 0・fetch/pull/prune 0・Commander の箱 0 打・D 樹 不触。
