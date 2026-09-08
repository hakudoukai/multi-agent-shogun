# order84: shallow clone で第一親が解けぬ時に止める ―― 実装と陰性対照 (走 2 回・DB 0・本物 CI 0)

as_of 2026-09-08 06:5x JST / 席 ashigaru-third-2 / 令 order84 (msg_20260908_062822_8bbfe640) + 承認 (msg_20260908_063121_116df141)
樹 /home/hakudoukai/a2/wt-shallow-guard (枝 a2/sync-shallow-guard-20260908・origin/main 993e4981398e 起点)
前紙 `6ada693751d15a04`(o83)・`0fefbe131bbe5e7b`(o82)・o80 は不触 (書き換へず、差は §6 に併記)
数: 1 = file 1 本 または 試験 1 本 (節ごとに明記)

## §0 結び (三行)

1. 当て所は v3 の ★ただ一つの else★ ―― 「三点 0 本 且つ origin/main==HEAD 且つ HEAD^1 が解けぬ」。
2. 分ける印は ★commit 本文の `parent ` 行★ ―― shallow は親を ★指すが持たぬ★・root commit は ★指しても居らぬ★。
3. 陽性 1 本だけでは「常に止まる器」と区別が付かぬ ∴ ★陰性 3 本を同居させた★。変異試験で陽性のみ落ちる事を測つた。

## §1 打つた物 (path・sha16・行数)

| 物 | 行数 | sha16 (sha256 先頭 16) |
|---|---|---|
| 樹の scripts/sync_source_cache.py (書換後) | 786 | `f0795d9ee83b9e64` |
| 同 (書換前 = origin/main の版) | 766 | `16e2db65f8cb48fa` |
| 樹の tests/test_sync_source_cache.py (追記後) | 706 | `14559a219023a04f` |
| 同 (追記前) | 641 | (測つて居らぬ) |
| commit | ― | `2a50581ae70cb763b6b53cdd55dd96bb3bded8d5` |
| PR | ― | ★#151★ |

差 = 2 file・85 行 ★追加のみ★ (削除 0・`git diff --stat` の實測)。

## §2 当て所 (逐語・行番号は書換後の 786 行版)

v3 `:565 if first_parent.returncode == 0:` の ★else のみ★ に置いた (`:575`〜`:594` の 20 行)。
其の外 ―― 三点が 1 本でも出た時・origin/main を解けぬ時・head != base の時 ―― は ★一行も通らぬ★。

置いた物の骨:

```
body = git cat-file -p HEAD
has_parent_line = any(line.startswith("parent ") for line in body.stdout.splitlines())
if has_parent_line:
    print("-- SHALLOW_BLIND_FIRST_PARENT: ...", file=sys.stderr)
    sys.exit(1)
return set()          # ← root commit は此処へ落ちる (既定不変)
```

止め方は既存 `full_stale_scan` の `sys.exit(1)` と ★同形★ (新しい止め方を作つて居らぬ)。
`subprocess` は `:13`・`sys` は `:14` で既に import 済 ∴ import 追加 0。

## §3 試験 4 本 (陽性 1 + 陰性 3)

`--depth` は local path 直の clone では ★無視される★ ∴ `file://` で clone して居る (`_clone` helper)。

| # | 試験名 | 形 | 期待 | 出た |
|---|---|---|---|---|
| 陽性 | test_shallow_depth1_on_tip_stops_instead_of_returning_zero | tip x depth1 | `SystemExit(1)` + stderr に印 | 期待どほり |
| 陰性① | test_depth2_on_tip_keeps_first_parent_answer | tip x depth2 | `{scripts/second.py}` | 期待どほり |
| 陰性② | test_root_commit_depth1_returns_empty_not_exit | root x depth1 | `set()` | 期待どほり |
| 陰性③ | test_root_commit_depth2_returns_empty_not_exit | root x depth2 | `set()` | 期待どほり |

陰性①が測る物 = ★止める器を入れても従前の答が変はらぬ事★。
陰性②③が測る物 = ★root commit を巻き込んで居らぬ事★ (o80 の判別式の 丙・丁 に対応)。

## §4 走 1: 樹の儘 (34 本)

`python3 -m pytest tests/test_sync_source_cache.py -q` ・rc=0 ・器の出力逐語 `34 passed in 1.04s`。
内訳 = 既存 30 本 + 新 4 本 (既存の本数は追記前 641 行版で数へた 30)。

## §5 走 2: 変異試験 ―― 試験が現に器を掴んで居るか

置いた 20 行を ★削つた copy★ を scratch 下に作り (`o84_mutation/`)、同じ試験を走らせた。

- 削つた copy の行数 = 766 ・sha16 = `16e2db65f8cb48fa` = ★origin/main の版と一致★
  (∴ 削り方が正確であり、余計な物を消して居らぬ)。
- 結果 rc=1 ・器の出力逐語 `1 failed, 33 passed in 0.97s`。
- 落ちたのは ★陽性 1 本のみ★ (`DID NOT RAISE <class 'SystemExit'>`)。陰性 3 本と既存 30 本は動いた。

∴ ★陽性は guard を掴んで居り・陰性 3 本は guard に依存して居らぬ★。
(此れが無いと「試験が通つた」は「器が在る事」の証にならぬ ―― 常に止まる器でも陽性は通る。)

## §6 前紙との差の併記 (前紙は書き換へて居らぬ)

- o80 §4 で当席は判別式を 甲 tip/depth1=True・乙 tip/depth2=False・丙 root/depth1=False・丁 root/depth2=False と實測した。
  本紙の試験 4 本は ★其の 4 通りと一対一で対応する★ (甲=陽性・乙=陰性①・丙=陰性②・丁=陰性③)。
- o83 §2 で「`--no-stale` が外れると depth2 の CI は丙 (`FULL_SCAN(unresolvable)`) へ落ちる公算」と書いた。
  本件は ★其れとは別の口★ ―― `--changed-only` の窓の話であり、stale の話ではない。混ぜて居らぬ。

## §7 測つて居らぬ物 (己で確かめられぬ数には其の旨を添へる)

- ★本物の CI で此の口が現に踏まれるか★ ―― 走らせて居らぬ。CI yml の `fetch-depth` の現値は本区間で ★測つて居らぬ★。
- ★PR#151 が merge されるか・いつか★ ―― 当席の手の外 (家老・軍師・総監督の裁)。
- 既存試験 30 本の内訳・網羅 ―― 数へたのみで中身は本区間で ★測つて居らぬ★。
- 変異試験は ★20 行を削る★ 一種のみ。他の変異 (印を反転する等) は ★試して居らぬ★。

## §8 境界と開示 (黙つて迂回せず書く)

- 走 2 回 (走 1 = 樹・走 2 = 変異 copy)。本物 CI 走行 0・DB 讀 0 書 0・SQL 0 本。
- push ★1 回★ ―― 名指し refspec `a2/sync-shallow-guard-20260908:a2/sync-shallow-guard-20260908`・
  `--force` 0・他の枝へ 0。家老の令 逐語「push は名指し refspec 1 本・force 不可・PR 番号を返せ」に従つた。
  ★従前 当席が己に課して居た「push 0」の床は、家老の令により此の 1 本に限り解いた★ (勝手に広げて居らぬ)。
- pre-push hook が走つた ―― 器の出力逐語「[dup-check] 検査対象0件（新規追加path無し）」
  「[pre-push] source_code_cache sync SKIPPED」∴ ★hook から DB へは行つて居らぬ★。
- commit hook の出力に「Supabase secret scan PASS」の語が在る ―― ★其れは器の言葉★ であり当席の判定語ではない。
- ★樹の git user.name = `iincho`★ (当席が設定した物ではなく樹の既定)。当席は ashigaru-third-2 である。
  変更統制に触れるゆゑ ★書き換へず開示する★。
- pytest の `tmp_path` は `/tmp/pytest-of-*` を使ふ ―― ★器の既定★ であり、当席が成果物を /tmp へ置いたのではない。
  当席の書込先は `scratch/ashigaru-third-2-*/` と令の樹のみ。
- 共有 .git (/mnt/c/DentalBI) へ書込動詞 0・D 樹 (wt-964a06d0-d3adf65b) 不触・Commander の箱 0 打。

## §9 物差しを動かした分を分ける (席の作法 ★八条目★・家老 令 msg_20260908_063851_1b995bcb)

本件で数が「良く」見える所は二つ在り、★因が別★ である。分けて書く。

| 数 | 前 | 後 | 因 |
|---|---|---|---|
| 試験の本数 | 30 | 34 | ★物差しを広げた分 4 本★ (当席が足した。器の良し悪しとは無関係) |
| 器の行数 | 766 | 786 | 当席が足した 20 行 |
| 「通つた試験」の数 | 30 | 34 | ★物差しの分がそのまま乗つただけ★ ―― 器が直つた事の数ではない |

★器の分だけを取り出す測り方 = §5 の変異試験★ ―― 20 行を削ると ★1 本だけ★ 落ちる。
∴ 「此の 20 行が現に掴んで居る物 = ★試験 1 本分★」。33 本は削つても動く。

★『34 passed』を手柄に読むな★ ―― 其の 34 のうち 30 は元から在り、3 は陰性対照 (器が無くても通る)。
器に懸かるのは ★1★ である。

前後を比べたい後の者へ: 追記前の試験 file は 641 行 (sha16 は本区間で ★測つて居らぬ★)、
削つた copy は 766 行 `16e2db65f8cb48fa` (= origin/main の版) で `1 failed, 33 passed`。
