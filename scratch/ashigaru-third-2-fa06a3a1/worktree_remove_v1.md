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
