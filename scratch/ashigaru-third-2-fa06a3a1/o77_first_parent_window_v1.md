# --changed-only の窓を第一親へ落とす条件を当てた (裁 288198 案 B・実測と逐語)

as_of 2026-09-08 05:3x JST / 席 ashigaru-third-2 / 令 order77
枝 `a2/sync-changed-only-first-parent-20260908` (樹 wt-first-parent・origin/main 61885f9d0 起点)・commit `cf33dd4a6f0dfb0e` (1 本)
PR ★#143★ (base=main・merge は総監督殿)。規: `o77_first_parent_repro.py` (49 行)。前紙 (不触): order75 `0549eff2d58e1a95`・order76 `499b845d768a5c03`

## §1 当てた条件 (何を 1 と数へたか: 1 = file 1 本)

`scripts/sync_source_cache.py`: `main()` に埋まつて居た窓の算出を `changed_paths_from_git(repo_root)` へ括り出し、
★三点 `origin/main...HEAD` が 0 本 且つ origin/main と HEAD が同じ commit の時のみ★ `HEAD^1 HEAD` の差へ落とす。
落ちた時は `-- CHANGED_ONLY_FIRST_PARENT: three_dot=0 origin/main==HEAD (<sha9>) first_parent_files=<n>` を stderr へ出す (黙つて変へぬ)。
触れた file ★2 本★ ―― v3 (+64/−12 行)・test (+41 行)。合せて 93 挿入 / 12 削除。

## §2 既定が動かぬ事 (4 枡・test で釘付け)

| 枡 | 窓の出所 | 本弾で動いたか |
|---|---|---|
| 枝の上 (三点が 1 本以上) | 三点 `origin/main...HEAD` | 動かぬ |
| origin/main を解けぬ (rc≠0) | 従前の fallback `HEAD~1 HEAD` | 動かぬ |
| 三点 0 本 且つ origin/main ≠ HEAD | 0 本 | 動かぬ |
| ★三点 0 本 且つ origin/main == HEAD★ | ★`HEAD^1 HEAD`★ | ★此の枡のみ★ |

## §3 実測 (作り物の小 repo・規 script の出力 逐語)

```
三点 origin/main...HEAD: rc=0 本数=0 []
第一親 HEAD^1 HEAD: rc=0 本数=1 ['scripts/added.py']
```
本樹の PR#140 merge commit `3d770ab5a` でも同じ形であつた (order75 で實測・三点 0 本 / 第一親 3 本)。

## §4 test の逐語 (`python3 -m pytest tests/test_sync_source_cache.py -q`)

```
..............................                                           [100%]
30 passed in 0.85s
```
※ 上の 1 行は ★pytest の生出力★ である。SKIP は ★0★ (29 → 30 へ 1 本増えた分が本弾の test)。
足した test は 1 本 `test_changed_paths_first_parent_only_when_three_dot_empty_and_same_commit` ―― §2 の 4 枡の内 3 枡 (押した形・枝の上・祖先) を釘付けする。
親無し commit の枡は `HEAD^1` が rc≠0 ゆゑ 0 本へ落ちる形で、test には入れて居らぬ (★確かめて居らぬ★・六条)。

## §5 戻し方・危険

- 戻し方: commit `cf33dd4a6f0dfb0e` を revert すれば三点のみの窓へ返る。★code の書換だけでは DB の行は動かぬ★ (動くのは次に CI が走つた時) ∴ merge 前なら戻しに副作用は無い。
- 危険①: merge 後の初回 CI は第一親の差 (PR で入つた file) を upsert する ∴ ★其の走で Upserted が 0 から増える★ ―― 増える側であり消す側ではない (CI は `--no-stale`)。
- 危険②: main へ ★push した直後ではない★ 走 (例へば手打ちで main の古い commit を見る形) では従前どほり ―― 此の条件は origin/main と HEAD の一致を要るゆゑ広がらぬ。
- 危険③: `HEAD^1` は第一親ゆゑ、squash でない merge で ★第二親側にしか無い変更★ は差に出る (第一親からの差ゆゑ出る)。逆に octopus merge (親 3 つ以上) の第三親以降も第一親からの差に含まれる。

## §6 境界

書換は本枝の 2 file のみ・force push 0・push は指された refspec ★1 本★ のみ (`refs/heads/a2/sync-changed-only-first-parent-20260908`・新枝)。
DB 讀 0 書 0・SQL 0・fetch 0・merge 0 (総監督殿の手)。走行は pytest と規 script のみ ―― ★v3 本体 (main) は走らせて居らぬ★ ∴ 実際の CI での Upserted 本数は ★確かめて居らぬ (六条)★。
pre-push hook の出力 (dup-check 0 件・sync SKIPPED・secret scan) は ★hook の生の言葉★ であり当席の判定に非ず。
