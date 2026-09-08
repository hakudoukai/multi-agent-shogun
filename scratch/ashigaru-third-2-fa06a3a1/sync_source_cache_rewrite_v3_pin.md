# v3 patch の再固定 (order40 產・軍師 REVISE seq284661 の cure・★commit 0・push 0★)
as_of 2026-09-07 15:2x JST / 席=ashigaru-third-2 / 令=karo-third order40 / repo=/mnt/c/DentalBI (讀取のみ)。1 = commit 1 個 / file 1 本 / 行 1 本。三択語=測つた・測つて居らぬ・測れぬ。

## §1 系譜表 (全て `git rev-parse` と `git log -1` で再測つた)
| 役 | 40 桁 | tree | 題 |
|---|---|---|---|
| base | 1fbd0aa0fe362d2498ad090bd46f5d6fe5cd2345 | 60c13d2cf | 引き継ぎ: 9/7 14:5x 到達点 |
| 親 (v2) | ce3b08dbeb0f9d42bec9ed79ac45d5f6da8c9020 | cb73a05d8 | v2: stale 判定を git 差分基準へ + 試験24本 |
| fixed (v3) | 3155e8dc0893f3ff40eb809d9fcae0c08f97875c | 3c5fd202c | v3: 投入側を git 追跡簿基準へ + EXCLUDE 帯 + 試験3本 |
親子=base → ce3b08dbe → 3155e8dc0 (`git log -1 --pretty=%h %p` で親を測つた)。fixed は ★動かして居らぬ★。

## §2 0004 (本 order の產)
| 事 | 値 |
|---|---|
| file | 0004-sync_source_cache-v3-full-base1fbd0aa0f-to-3155e8dc0.patch |
| 作り方 | `git diff 1fbd0aa0f… 3155e8dc0…` の出力を ★其の儘★ python `write_bytes()` で置いた (shell `>` 不使用) |
| 大きさ | 29,248 byte / 674 行 |
| file の sha256 前16 | ★7e13a766854ced5b★ |
| `git diff` 出力の sha256 前16 | ★7e13a766854ced5b★ (同値・byte 比較も True) |
| 軍師の値 7e13a766 | ★一致した★ |
| 中身 | 2 file (scripts/sync_source_cache.py + tests/test_sync_source_cache.py)・556 insertions(+)・21 deletions(-) |
註釈行は ★1 行も置いて居らぬ★ (置けば sha が `git diff` と違ふ物に成る為)。

## §3 base の樹での `git apply --check`
`git worktree add --detach /home/hakudoukai/a2/wt-base-1fbd0aa0 1fbd0aa0f…` で ★自席 1 本★ を作つた
(同時に在つた当席の樹 = D 樹 と 本樹 の 2 本以内)。逐語:
```
$ git -C <base樹> apply --check -v 0004-...patch
Checking patch scripts/sync_source_cache.py...
Checking patch tests/test_sync_source_cache.py...
rc=0
$ git -C <base樹> apply --check -v 0003-...patch      # 比較の為
Checking patch scripts/sync_source_cache.py...
Checking patch tests/test_sync_source_cache.py...
rc=0
```
検め後 `git worktree remove` を打ち、樹は 7 本 → 6 本・★prunable 0 本★・汚れ 0 行 (測つた)。
a2/ 配下に残るは D 樹 `wt-964a06d0-d3adf65b` のみ (判定待ちゆゑ ★触れて居らぬ★)。

## §4 0003 と 0004 の別 (★0003 は消さず残した★)
| | 0003 | 0004 |
|---|---|---|
| 大きさ | 29,581 byte / 678 行 | 29,248 byte / 674 行 |
| file の sha256 前16 | c05138103db14f7b | 7e13a766854ced5b |
| 頭 | ★`#` 註釈 4 行★ (base・枝・当て方) | 註釈 0 |
| `diff --git` 以降の本体 | 29,248 byte・sha256 前16 ★7e13a766854ced5b★ | 同左 (★byte 同一・比較 True★) |

## §5 試験
fixed = 3155e8dc0 を動かして居らぬゆゑ ★再走は要らぬ★。既測 = order36_pytest_raw.txt
(3e9058da3dc9efaf・8 行・`27 passed in 0.66s`・`skip` 語 0)。本 order で試験は ★走らせて居らぬ★。

## §6 ★開示 ―― 軍師 REVISE の前提と当席の測りが食ひ違ふ★
1. REVISE は「0003 は commit 1 個分(親 ce3b08dbe)で base→fixed の tree diff と不一致」と申される。
   当席が測つた `git diff ce3b08dbe 3155e8dc0` は ★7,404 byte / 155 行 / sha256 前16 442ddb06ebd24451★ で、
   0003 の本体 (29,248 byte / 7e13a766…) と ★別物★ である。∴ ★0003 の中身は commit 1 個分ではなく全差分★ (測つた)。
2. 誤りを招いた因は中身でなく ★註釈と名★ と見る: 0003 の L3 が「commit = ce3b08dbe (v2) -> 3155e8dc0 (v3)」と
   ★範囲の様に読める★ 書き方で、file 名も `0003-` と format-patch 風であつた。何れも当席の書き方の欠である。
3. ∴ 令の cure (全差分を 0004 として再固定し sha を突き合はせる) は ★果たした★ が、其れは
   「中身を直した」のではなく ★sha で示せる形に直した★ 事である。判定は軍師と家老の物にてござる。
4. commit 0・push 0・fixed 不変・DB 0・本樹の作業樹への書込 0。
