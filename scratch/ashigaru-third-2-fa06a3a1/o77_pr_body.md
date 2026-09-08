## 何を直したか

`--changed-only` の窓 (どの file を同期するか) の算出を `main()` から
`changed_paths_from_git(repo_root)` へ括り出し、
★三点 `origin/main...HEAD` が 0 本 且つ origin/main と HEAD が同じ commit の時のみ★
第一親 `HEAD^1 HEAD` の差へ落とす。落ちた時は `-- CHANGED_ONLY_FIRST_PARENT:` を stderr へ出す。

## 理由 (PR#140 merge 後の Upserted 0)

PR#140 を main へ merge した後の初回 CI は success・`STALE_SKIPPED`・表の行数不変なるも
★Upserted 0★ であつた。因は三点記法である ―― 「合流点から HEAD まで」を見るゆゑ、
HEAD が origin/main 其の物 (= main へ押した後に CI が走る形) では ★己と己の差 = 0 本★ になる。
且つ ★空でも rc=0★ ゆゑ、既存の fallback (`rc != 0` の時のみ `HEAD~1 HEAD`) は発火せぬ。

実測 (作り物の小 repo・merge commit を origin/main に置いた形):

```
三点 origin/main...HEAD: rc=0 本数=0 []
第一親 HEAD^1 HEAD:      rc=0 本数=1 ['scripts/added.py']
```

本樹の PR#140 merge commit でも同じ形であつた (order75 で実測・三点 0 本 / 第一親 3 本)。

## 既定は不変

- 枝の上 (三点が 1 本でも出る) ―― 従前どほり三点の答。
- origin/main を解けぬ時 (rc≠0) ―― 従前どほり `HEAD~1 HEAD` の fallback。
- 三点 0 本でも origin/main と HEAD が別 commit ―― 従前どほり 0 本 (第一親へ落ちぬ)。
- `HEAD^1` が無い (親無しの commit) ―― 0 本。

## test

1 本 (三枡)。`30 passed / 0 skipped` (`python3 -m pytest tests/test_sync_source_cache.py -q`)。

## 戻し方

此の commit を revert すれば `origin/main...HEAD` のみの窓へ戻る。
★code の書換だけでは DB の行は動かぬ★ ―― 動くのは次に CI が走つた時ゆゑ、
merge 前なら戻しに副作用は無い。

## 境界

書換は本枝の 2 file のみ (v3 +52/−12 行・test +41 行)。DB 讀 0 書 0・SQL 0・
fetch 0・force push 0・push は指された refspec 1 本のみ。merge は総監督殿。
