# 二 repository 跨ぎの sha 対応表 (2026-08-06・家老second)

## なぜ在るか

本 repo (`multi-agent-shogun`) に収める票が、lane worktree の sha を **repo 名なしで** 引いていた。
lane は **別 repository** (`hakudokai-dev`) の clone ゆえ、**本 repo に立つ者は永久に引けない**。

```
(主 repo) git rev-list --max-parents=0 HEAD  = 5621b658f4b37054f02a26dfa362900abff51391
          origin = git@github.com:hakudoukai/multi-agent-shogun.git
(lane)    git rev-list --max-parents=0 HEAD  = 62f4a2e1a690f44be52d53155c7c80bdeeb5160b
          origin = git@github.com:hakudoukai/hakudokai-dev.git
(主 repo) git cat-file -t 099288f / afcc870 / e1ace1c / 21f7a76
          -> fatal: Not a valid object name  (4/4 解決不能)
```

> **sha は「引き直せる印」に見えて、repo を跨げば嘘をつく。**
> 既存条「git 外の sha は嘘をつく」の **git 内・別 repo** の顔。
> **境は「git か否か」ではなく「我らの木か否か」。**

履歴の書換 (amend/rebase) は禁ゆえ、**過去の commit は直さず、本表を残す**
(「破れた後は、戻すより先に残して報せよ」)。

## 対応表 — 全て `hakudokai-dev` repo (lane worktree)。**本 repo では解決しない**

| lane sha | 主題 | 引いている本 repo commit |
|---|---|---|
| `7f49218` | 2fe4ed9 production snapshot を lane へ materialize (a4) | — |
| `411368c` | 47b independent re-run GREEN + test_47d KeyboardInterrupt (a4) | `17f9cc9` |
| `990e5ad` | barrier 真並行 陽性対照 3種 新設 (a4・本部長令 16:35:49/16:48:01) | `17f9cc9` |
| `51f644f` | offset overlap RED/GREEN worker を helper 一本へ導出 (a4) | `20f1126` |
| `21f7a76` | exact-time GREEN は claim の効きの証に非ず docstring (a4) | — |
| `099288f` | 層外 writer 8箇所 → 共通 command 委譲 (a1) | `c36e5be` |
| `e1ace1c` | uq_appointments_active_exact_start は offset に構造上無力 (a4) | — |
| `afcc870` | booking_concurrency_root.py:255 index DDL を ACTIVE_SQL 参照へ (a1) | — |
| `2fe4ed9` | 47b same-transaction audit log (a1) | `17f9cc9` |

## 以後の書式 (拘束)

1. lane の sha を本 repo の票・commit 本文で引く時は **repo 名を明示** —
   `hakudokai-dev repo の e1ace1c` の形。**裸の sha を書かない。**
2. **かつ逐語を添える** — sha だけでは本 repo に立つ者が解決できない。
   既存条「git 外 → 逐語」を **別 repo にも広げる**。
3. 収載 commit の欄には **sha と併せて刻** を書く (`e1ace1c 17:45:15` の形)。
   欄は増やさず、既存の段に畳む。

## 併せて測った事 (禁の射程の判断材料・当職は射程を決めない)

- `git log --branches --not --remotes` = **8 commit 悉く remote に無し** ⇒ **push 零**
- `/mnt/c/Projects/hakudokai-dev` の mtime = **Aug 4 10:18** (二日 不触・読取のみで確認)
- lane = `/tmp` の partial clone (origin=GitHub、`/mnt/c` 由来ではない)、一 clone に複数 worktree
- ∴ 禁の文言 (path 指定「`/mnt/c/…` への書込」) は**面上 破れていない**。
  **而して repo は同一**ゆえ射程は当職が決めない (狭めも広げもせず上げる)。

Co-Authored-By: Claude <noreply@anthropic.com>

---

## ★訂正1 (2026-08-06 18:0x・家老second 自己申告)★ — 上の「8 commit」は **26** が正

将軍second の実測により、上記「併せて測った事」の一行

> `git log --branches --not --remotes` = **8 commit 悉く remote に無し**

が **誤り**と判明した。**正しくは 26**。

```
$ git -C /tmp/resimg-stage1-runtime-20260806 log --branches --not --remotes --oneline | wc -l
26      (a1系 6 / a4系 20)
```

**結論 (push 零) は不変。むしろ強まる — 露出は三倍。**

### なぜ 8 と書いたか (因は道具でなく、己が道具に渡した引数)

当職が走らせた命令は `... log --branches --not --remotes --oneline 2>&1 | ★head -8★`。
**返り 8 行を「世の数」として報じた。その 8 は己が head に渡した引数だった。**

> ### **★数を報ずる命令に `head` / `tail` を繋ぐな。★数と抜粋は別の命令★**

**重いのは、同じ形を同じ日に二度踏んだ事** — memory `reader-side-truncation-looks-like-loss`
に「`head -10` を世の数と報じた」が既に在り、**それを書いた当人が再び踏んだ**。
∴ **「知っている」では止まらない。書式 (欄) に落ちねば止まらない。**

### 書式として固定する (拘束)

1. **数を出す命令は `| wc -l` で終える。** 抜粋が要るなら **別の命令**として走らせる。
2. 抜粋を貼る時は **「抜粋 N / 全 M」**と明示する。M は 1 の命令から取る。
3. **報ずる数には命令を丸ごと貼る** (貼れば `| head -N` が己の目に入る)。
   ※ 本件はこの 3 を守っていたが**貼った先が上申文でなく作業ログ**で、己が読み返さなかった。
   ∴ 3 は 1・2 の代替にならない。

### 併せて — lane の母集団も過小だった

上で「一 clone に複数 worktree」と書いたのは**この 3 本については正**
(`git rev-parse --git-common-dir` が三本とも `/tmp/resimg-stage1-runtime-20260806/.git`)。
**而して `/tmp` 直下の `.git` は 10 本在る** (列挙で確認)。
∴ 「lane = 一 clone」は**当職が見た 3 本についての事実**であって、**lane 全体の事実ではない**。

> ### **★見た範囲の事実を、範囲を書かずに一般の顔で書くな★**

Co-Authored-By: Claude <noreply@anthropic.com>
