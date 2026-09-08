# order13 記録 ―― wt-fa06a3a1-collect の退避と remove の試み (v1)

令: subtask_thirdpc_fa06a3a1_a2_worktree_collect_raw_evacuate_and_remove_001 (order_in_seat=13・assigned 2026-09-07T05:29+09:00・家老third)
席: ashigaru-third-2 / 樹: /home/hakudoukai/a2/wt-fa06a3a1-collect

## 節一 tip の local ref 実在 (令 step1)

- `git -C /mnt/c/DentalBI cat-file -e a2-fa06a3a1-collect-fixed` → exit **0**
- `rev-parse` → `4b9912e6c3d69cae6e231b628678e3db4de3a75c`
- ∴ 樹を消しても当席版 tip は辿れる。**1 と数へたのは branch ref 1 本**(push 0・upstream 無し=order11 紙に既測)。

## 節二 remove 前の樹の姿 (実測 05:29)

- `git worktree list` の**行数 10**(1 と数へたのは list の出力 1 行=登録 worktree 1 本)。当該樹は其の 1 行として在り、HEAD は `fffd757f216d1412f3b586cc8eba38538de3dbba`(X head・detached)。
- `git -C <樹> status --porcelain` の**行数 3**(1 と数へたのは status の 1 行=file 1 個)。三行悉く `??`(未追跡)であり、**追跡下の変更行は 0**:
  - `?? reports/_scratch/fa06a3a1_collect_a2_20260907.log`
  - `?? reports/_scratch/fa06a3a1_xhead_collect_a2_20260907.log`
  - `?? reports/_scratch/fa06a3a1_xhead_collect_a2_20260907_rerun.log`
- ∴ 令 step2 の言ふ「未追跡 raw 3本」と status の 3 行は**名まで一致**する。

## 節三 raw の退避 (令 step2)

写し先: `/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/raw_fa06a3a1/`

| # | file 名 | SHA256 (源) | SHA256 (写し) | 一致 | byte | 行数 |
|---|---|---|---|---|---|---|
| 1 | fa06a3a1_collect_a2_20260907.log | d240c833e10bf79669efef0c1015d115df8ff02c114c8976729a1773ccf3accb | 同左 | 是 | 5556 | 89 |
| 2 | fa06a3a1_xhead_collect_a2_20260907.log | a636f09e8289e50121cb70b821747967cce415843e408e642217e57bb7d4e9fd | 同左 | 是 | 2718 | 36 |
| 3 | fa06a3a1_xhead_collect_a2_20260907_rerun.log | 6ca2014c9fe465d588b5642fbd11fd6b4d0e911bb240c17df291b691cf3e2495 | 同左 | 是 | 2620 | 35 |

- **写した file の数 3**(1 と数へたのは file 1 個)。**令外の file を写した数 0** ―― order12 の deviation_1(令外 90 file の写し)は繰返して居らぬ。写し先 dir の entry 数も **3**(実測 listdir)。
- #2・#3 の sha256 は order11 紙 `rebase_onto_x_v1.md`(sha16 `1ca8897ff4bff7b9`・85 行)に載る値と**当席が今 measure し直して一致**(床(27))。#1 は order8 期の collect raw。
- 源 file は**触れて居らぬ**(mtime・内容とも不変。写しのみ)。

## 節四 plain remove の試み (令 step3)

command: `git -C /mnt/c/DentalBI worktree remove /home/hakudoukai/a2/wt-fa06a3a1-collect`

実文(逐語):
```
fatal: '/home/hakudoukai/a2/wt-fa06a3a1-collect' contains modified or untracked files, use --force to delete it
```
exit = **128**

- 令は「--force 不可・dirty なら止めて報」と明記する故、**--force は打つて居らぬ**(打つた回数 0)。
- 拒みの因は節二の未追跡 3 file であり、追跡下の変更に因るものではない(status の `??` 以外の行 0)。

## 節五 止まりと、令の欠の開示

- **令 step2 は「写し」(cp)であり「移し」(mv)ではない**。写しただけでは樹は未追跡 3 file を抱へたままゆゑ、**step3 の plain remove は原理として成らぬ**。此れを黙つて迂回せず、令の欠として開示する(order12 は同じ形で `--force` を家老裁の下に用ゐて成つた)。
- 当席が自ら選べる形は二つ在るが、何れも令の禁または令の外に触れる故、**家老の裁を仰ぐ**:
  - 甲: `--force` を許す(order12 と同形。消えるのは節三で sha256 一致を採つた 3 file のみと当席は測つて居る)。
  - 乙: 退避済の 3 file を樹内から消して樹を clean にし、plain remove を打つ(--force は不要となる。消す対象は名指しの 3 file のみ)。
- 当席は何れを採れとも勧めぬ(勧める語 0)。裁が届くまで樹は**現状のまま**保つ。

## 節六 三択

- **測つた**: ref の実在と値・list 10 行・status 3 行と其の名・写し 3 本の sha256 両側一致と byte/行数・plain remove の実文と exit 128。
- **測つて居らぬ**: 当該樹の disk 使用量、`reports/_scratch` 配下の追跡下 file の数、X head と当席 tip の差分の中身(order11 紙に既載ゆゑ再測せず)。
- **測れぬ**: 家老が甲乙何れを採るか。上の裁が届くまで当席の器では決し得ぬ。

## 節七 禁の遵守

- `git worktree prune` を打つた回数 **0**。
- 共有 checkout(/mnt/c/DentalBI)への checkout/reset/commit/push の回数 **0**(讀取 command のみ)。
- D 樹 `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` に触れた回数 **0**(軍師 D PASS まで不触)。
- commit 0・push 0・remote 書込 0・secret 0 字・患者本文 0 字。
- 判定語(PASS/合格/緑 等)0・先送り語 0・勧める語 0。

as_of: 2026-09-07T05:31:18+09:00

---

# 追記 (v2) ―― 家老裁「乙」に依る決着

本節より上は v1(sha256 163b60504e0142219b5d72cc74fff7a968bd3e185c1d1e7168d2e4f2cd1fbac0・70 行・as_of 2026-09-07T05:31:18+09:00)の**逐語**であり、一字も書き換へて居らぬ。v1 の file 自体も不触(当席が今 measure し直して同 sha256)。

## 節八 家老の裁 (便 msg_20260907_053230_8b3ac089・05:32:30)

裁 = **乙**。曰く「家老も退避先3本の sha256 両側一致を実測した(SAME×3)。樹内の未追跡3本を名指しで rm(rm -rf 禁・glob 禁・3 file のみ)→plain worktree remove→list 9・dir 不在を紙に併記(v1 不触・v2 で)。--force は打つな」。

## 節九 消す直前の再検 (床(27))

消す前に、樹内の 3 本と退避先 3 本の sha256 を当席が改めて突き合はせた。**3 組とも SAME**(1 と数へたのは file 1 個):

| # | file 名 | sha16 | byte | 判 |
|---|---|---|---|---|
| 1 | fa06a3a1_collect_a2_20260907.log | d240c833e10bf796 | 5556 | SAME |
| 2 | fa06a3a1_xhead_collect_a2_20260907.log | a636f09e8289e501 | 2718 | SAME |
| 3 | fa06a3a1_xhead_collect_a2_20260907_rerun.log | 6ca2014c9fe465d5 | 2620 | SAME |

家老の実測(SAME×3)と当席の実測は**同じ 3 組で一致**する。

## 節十 名指しの削除 (令 乙・第一段)

- 消した対象は上表の **3 file のみ**(1 と数へたのは file 1 個)。**一本づつ名を指して**消し、**再帰の削除(rm -rf 相当)は打つた回数 0**・**glob を使つた回数 0**・**dir を消した数 0**。
- 各本につき削除後の存在確認を採り、三本とも **exists=False**。
- 消した後の `git -C <樹> status --porcelain` の**行数 0**(=樹は clean)。

## 節十一 素の remove (令 乙・第二段)

command: `git -C /mnt/c/DentalBI worktree remove /home/hakudoukai/a2/wt-fa06a3a1-collect`

- exit = **0**(v1 節四で exit 128 を返した同じ command が、樹が clean となつて通つた)。
- **`--force` を打つた回数 0**(v1 節四・本節を通じて通算 0)。

## 節十二 remove 後の姿

- `git worktree list` の**行数 9**(前 10・1 と数へたのは list の 1 行=登録 worktree 1 本)。消えたのは `/home/hakudoukai/a2/wt-fa06a3a1-collect` の 1 行のみで、他 9 本の path・commit・branch 表示は前後で同一。
- `test -e /home/hakudoukai/a2/wt-fa06a3a1-collect` → exit **1** = **dir 不在**。
- `git cat-file -e a2-fa06a3a1-collect-fixed` → exit **0**(当席版 tip `4b9912e6c3d69cae6e231b628678e3db4de3a75c` は樹を消した後も辿れる)。
- `git cat-file -e fffd757f216d1412f3b586cc8eba38538de3dbba` → exit **0**(X head の object も健在)。
- 退避先 `scratch/ashigaru-third-2-fa06a3a1/raw_fa06a3a1/` の entry 数 **3**・sha256 は節九の表と**削除後も同値**(消えたのは樹内の本のみ)。
- D 樹 `/home/hakudoukai/a2/wt-964a06d0-d3adf65b`(HEAD `d3adf65b9`)は list に**在るまま**=不触。当席の樹は **2 本 → 1 本**。

## 節十三 三択 (追記分)

- **測つた**: 消す直前の 3 組 SAME・削除 3 本と各 exists=False・status 0 行・素 remove exit 0・list 10→9・dir 不在(test -e exit1)・ref と X head の cat-file exit 0・退避先 3 本の削除後 sha256。
- **測つて居らぬ**: 消した 3 本が他所(他席・DB・報告)に写しを持つか否か。当席の退避先 1 箇所しか測つて居らぬ。
- **測れぬ**: 消した後の樹の中身を今から見る事(dir が無い故、当席の器では最早測れぬ)。

## 節十四 禁の遵守 (追記分)

- `rm -rf` 相当・glob 削除・dir 削除 = 各 **0**。`--force` **0**。`git worktree prune` **0**。
- 共有 checkout(/mnt/c/DentalBI)への checkout/reset/commit/push **0**(worktree remove は登録の解除であり、共有 checkout の作業樹は触れて居らぬ)。
- commit 0・push 0・remote 書込 0・secret 0 字・患者本文 0 字。判定語 0・先送り語 0・勧める語 0。
- v1 は不触(上の逐語部と file の双方)。

as_of (v2): 2026-09-07T05:34:01+09:00
