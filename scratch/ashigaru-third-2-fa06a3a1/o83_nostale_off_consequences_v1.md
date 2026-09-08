# order83 ―― `--no-stale` が外れた時に何が起こるか (走 2 回・DB へ 0 回・本物 CI 0)

as_of 2026-09-08 06:3x JST / 席 ashigaru-third-2 / 令 order83
前紙 `0fefbe131bbe5e7b`(o82)・`c24ae7c7451f1c7b`(o81)・`0070f41f46323d2a`(o80)・`3f1f8c2f45e55e1f`(o79) 不触。
底本 = `origin/main:scripts/sync_source_cache.py` sha16 `16e2db65f8cb48fa` 766 行 (抽出 = `o78_v3_originmain.py`)。

## §0 結び (先に置く)
`--no-stale` が外れると、CI の形 (shallow・fetch-depth 2) では ★高い公算で全表枝へ落ちる★。
落ちた先で消えるのは ★「DB に在り・現樹に無く・且つ fnmatch を通る」path★ ―― ★三条件の三つ目が効く★。
而して ★消える本数は SQL の上限より小さい★。作り物で測つた比は 上限 6 に対し実数 1 であつた (§3)。
★但し其の比を実 DB へ掛けてはならぬ★ ―― 元素が違ふ (§5)。

## §1 模擬と実測の区分け (★令の縛り★)
| 事 | 種別 |
|---|---|
| 作り物 repo を CI の形 (checkout@v4 相当 + `--depth=2`) で建て、`collect_files`・`commit_exists`・`compute_stale_paths`・`stale_paths_from_git` を ★現に呼んだ★ | ★実測★ |
| `get_last_sync_commit_from_db` が返す値 | ★模擬★ ―― 返り値を差し込んだ (DB へ 0 回・関数を呼んで居らぬ) |
| 作り物 DB の 11 行 | ★模擬★ ―― 当席が組んだ集合であり、実 DB の中身ではない |
| 実 repo `/mnt/c/DentalBI` の `collect_files` と fnmatch 通過数 | ★実測★ (讀取のみ) |
| `main()` の走行・`delete_stale` の呼出 | ★行つて居らぬ★ |
∴ ★本紙で「実測」と書いた行のみが実測である。分れの鎖 (`v3:698-722`) は当席が写した driver で辿つた★。

## §2 走 1 ―― 分れの四つ (作り物 repo・CI の形・depth2)
作り物: 3 commit。TIP `51bb96782` / 第一親 `e8594e81c` / 其の親 `898115bea`。
実測: `commit_exists(第一親)=True` / `commit_exists(其の親)=False` ∴ ★depth2 の clone で解けるのは 2 個のみ★。

| 枝 | 器の道 (逐語の印字名) | stale 本数 | 中身 |
|---|---|---|---|
| 甲 `--no-stale` 在り (CI の現形) | `STALE_SKIPPED` (`v3:694`) | ★0★ | ―― |
| 乙 外れ + DB が返さぬ | `FULL_SCAN(source=none)` (`v3:715`) | ★1★ | `frontend/src/other/branch_only.ts` |
| 丙 外れ + 返つた commit が clone の外 | `FULL_SCAN(source=unresolvable)` (`v3:710`) | ★1★ | 同上 |
| 丁 外れ + 返つた commit が clone に在る | `GIT_DIFF(source=db)` (`v3:721`) | ★0★ | ―― |

★読み★: 丁だけが消さぬ。丁に入る条件 = ★DB の commit_hash が「現 HEAD か其の第一親」である事★ ―― 
CI は `fetch-depth: 2` ゆゑ ★他の commit は悉く丙になる★。前回 CI 走行以降に main へ 2 本以上積まれて居れば丙である。
★実 DB が現に何を持つかは測つて居らぬ★ (§7)。

## §3 走 1 ―― 二段の網 (元素 = ★DB の行★・作り物 11 行)
| 数へ方 | 本数 | 中身 |
|---|---|---|
| 一段目のみ (現樹に在らぬ = ★SQL で数へられる上限★) | ★6★ | `README.md` / `backend/gone.py` / `docs/notes.txt` / `frontend/src/other/branch_only.ts` / `notes/free.md` / `scripts/branch_only.py` |
| 二段目まで (fnmatch も通る = ★器が現に消す★) | ★1★ | `frontend/src/other/branch_only.ts` |
| 差 (入るが消せぬ) | ★5★ | 上の 6 から 1 を除いた分 |

★驚いた所を書く★: `scripts/branch_only.py` と `backend/gone.py` が ★消えなかつた★。
pattern は `scripts/**/*.py` / `backend/**/*.py` で在るのに、である。
因 = `fnmatch` は `/` を特別扱ひせぬが ★pattern 中の `/` は literal で残る★ ∴ `scripts/**/*.py` は
`scripts/<何か>/<何か>.py` (2 階層以上) にしか当たらず、★直下の `scripts/x.py` には当たらぬ★。
是は o82 §5-c で当席が ★紙の上で述べた事★ が ★現に起きた★ 例である。器の側にも逐語で在る (`v3:389-391`
「fnmatch と glob は `**` の意味が違ふ」)。

## §4 走 2 ―― 実 repo で二段の網を測る (讀取のみ・DB へ 0 回)
repo = `/mnt/c/DentalBI` (枝 wp-a1-a3-3-20260723 / HEAD 4a7e1891e)。元素 = ★path 1 本★。

| 数へ方 | 本数 |
|---|---|
| 一段目 glob が拾ふ (`collect_files`) | ★4,113★ |
| 二段目 fnmatch も通る | ★3,492★ |
| 二段目で落ちる (入るが消せぬ) | ★621★ |
| 比 (通る / 拾ふ) | ★0.8490★ |
`INCLUDE_PATTERNS` の本数 = ★35★ (実測)。

落ちる 621 本の先頭階層: `scripts` 212 / `docs` 203 / `tests` 175 / `tools` 25 / `backend` 4 / `frontend` 2。
先頭 2 階層の上位: `docs/codex_audits` 166 / `docs/gemini_audits` 26 / `docs/audits` 11。
落ちる分のうち ★1 階層目の直下 file★ = ★416 / 621★。
∴ 落ちる形は ⑴`tests/x.py`・`scripts/x.sh` 等の ★直下 file★ と ⑵`docs/codex_audits/x.md` 等の
★pattern が 2 階層以上を要求する所の直下★ の二つである。

## §5 元素を混ぜぬ (0.8490 を上限へ掛けるな)
- ★0.8490 は「現樹の path」を元素にした比★ である。
- SQL の `would_delete_upper` (o82 §5-a) が数へるのは ★DB にのみ在る行★ ―― ★別の元素★ である。
- ∴ ★0.8490 を上限へ掛けて実数を出してはならぬ★。DB にのみ在る path の通過率は ★測つて居らぬ★ (DB を讀まぬゆゑ)。
- ★方向だけを見込みとして書く★: o50 で㋑ (他の枝にのみ在る path) の内訳は frontend 951 が最大であつた。
  `frontend/src/**/*.ts(x)` は 2 階層以上を要求するが `frontend/src/<何か>/<何か>.ts` は其れを満たす ∴
  ★通過率は現樹の 0.8490 より高い側に寄る★ と ★見込む★。是は見込みであつて実測ではない。

## §6 前紙との差 (書き換へず併記する)
| 前紙の数 | 本紙の数 | 当席の言ひ分 |
|---|---|---|
| o50/o81 で現樹 ★4,185★ (git 数へ) | 本紙 ★4,113★ (`collect_files` 実測) | ★別の時点・別の網の實測★ である。差 ★72★ の因は ★測つて居らぬ★ |
| o82 §7 「INCLUDE_PATTERNS は 22 本まで数へ終端まで数へて居らぬ」 | 本紙 ★35 本★ (実測) | 数へ切つた ∴ o82 の「測れぬ」は 1 つ解けた |
| o81 見積 ★1,483★ (残 5,668 − 現樹 4,185) | 本紙は数を出さぬ | 二段目が効く ∴ ★1,483 は上限側の数である★ と読み直す。実数は其れ以下 |

## §7 測れぬ物 (測れぬと書く)
- 実 DB の commit_hash が現に何であるか ―― DB へ 0 回 ∴ 丙か丁かは ★決められぬ★。
- 実 DB にのみ在る path の fnmatch 通過率 ―― 同上。
- 本物の GitHub runner での挙動 ―― 当席の再現であり ★本物の CI は 0 回★ 走らせて居らぬ。
- 現樹 4,185 と 4,113 の差 72 の因。
- 他 PC の樹での `collect_files` の数。

## §8 境界
走 ★2 回★ (上限 3・各 180 秒以内)・本物 CI 0・DB 讀 0 書 0・SQL 0 本・push 0 (作り物 bare へ clone 1 回のみ)・
製品 file 書換 0・fetch/pull/prune は ★作り物 repo に対してのみ★ (共有 `.git` へ 0)・`main()` 不走・`delete_stale` 不呼・
D 樹 `a2/wt-964a06d0-d3adf65b` 不触・Commander の箱 0 打。
数の 1 = ★path 1 本 / 行 1 行 / commit 1 個 / pattern 1 本★ (混ぜて居らぬ)。
