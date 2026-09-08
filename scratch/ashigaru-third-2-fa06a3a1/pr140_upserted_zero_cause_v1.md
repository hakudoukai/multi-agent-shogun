# PR#140 初回 CI の Upserted 0 —— 因の名指しと直しの案文 (讀取のみ・DB 0・fetch 0)

as_of 2026-09-08T05:02+09:00 / 席 ashigaru-third-2 / 令 order75 (総監督 下命・家老 経由)
前紙: `pr140_post_merge_check_v1.md` 61行 sha16 `a77a761351050de5` / `ci_sync_unify_design_v1.md` 80行 sha16 `3c3329b0010f273f` —— ★何れも不触★
與へられた事実 (家老便): merge 済 main `3d770ab5a`・初回 CI success・`STALE_SKIPPED`・表 4,249 行 不変 (減 0)・★Upserted 0★

## §1 因 (三値で名指す)
| 問ひ | 三値 | 根拠 (行番号・實測) |
|---|---|---|
| ① `HEAD~1` の親の取り方 | ★現に無い★ | `HEAD~1` は ★使はれて居らぬ★。L541 の fallback は ★`returncode != 0` の時のみ★ 発火し、空の diff は ★rc=0★ (實測) ゆゑ通らぬ |
| ② include 判定 | ★現に無い★ | merge の 3 本を v3 の器で当てた: `scripts/sync_source_cache.py`=INCLUDE 真・EXCLUDE 偽 / `tests/test_sync_source_cache.py`=同 / `.github/workflows/sync-source-cache.yml`=INCLUDE 偽 (v3 の目に `.github` は無い) ⇒ ★2 本は目に入つて居る★ |
| ③ 其の他 = ★三点比較が自分自身との比較になつた★ | ★現に在る★ | L536 `git diff --name-only origin/main...HEAD`。main への push では CI の `origin/main` と `HEAD` が ★同じ commit★ ゆゑ merge-base=HEAD ⇒ 差分 0 本 |

★一行で★: ★`origin/main...HEAD` は「枝から見た main との差」を測る形であり、main 自身への push では ★己と己の差=0★ になる。而して空でも rc=0 ゆゑ fallback が起きず、拾ふ file が 0 本 ⇒ Upserted 0。★

## §2 再現 (讀取のみ・fetch 0・走行 0)
局所に既に在る ref のみで測つた (`git cat-file -t 3d770ab5a`=commit)。
```
git -C /mnt/c/DentalBI log -1 --format='%h parents=%p' 3d770ab5a
  → 3d770ab5a parents=d7f0895ca ce83b5c0d   (第一親=merge 前の main tip・第二親=当席の枝)
git -C /mnt/c/DentalBI diff --name-only 3d770ab5a...3d770ab5a   → ★0 本★ rc=0   (CI が測つた形)
git -C /mnt/c/DentalBI diff --name-only 3d770ab5a^1 3d770ab5a   → ★3 本★        (第一親から見た形)
```
1 = file 1 本。3 本の内訳 = workflow yml / v3 本体 / 試験。∴ ★第一親で測れば 2 本が目に入る★ (yml は v3 の目の外)。

## §3 直しの案文 (★書換 0・push 0・GO の後★)
| 案 | 中身 | 広さ | 既定への障り |
|---|---|---|---|
| ★B (当席の見立て=最も狭い)★ | `changed_only` の diff が ★空★ かつ `origin/main` と `HEAD` が同一 commit の時に限り `HEAD^1..HEAD` で測り直す (3〜7 行) | v3 に 1 箇所 | 枝の push は三点が非空ゆゑ ★通らぬ=従前の儘★ |
| C | `--changed-since <rev>` の旗を足し CI は `--changed-since HEAD^1` を渡す | 旗が 1 本増える | 旗を付けねば従前の儘 (但し器の面が広がる) |
| D | CI から `--changed-only` を外す (全同期) | CI 側 1 行 | ★3,531 本/push の書込★ ―― 09-07 の止血に反す |
- B の細目 (案文): 第一親が無い時 (単根 commit・浅すぎる clone) は `git` が rc≠0 を返すゆゑ ★空の儘とし落ちぬ★ 形にする。
- B が効いた後に起きる事: merge ごとに ★2 本前後★ の upsert が入り 表は増える方向。減 0 の検算は order74 の規で見る (増は減を隠さぬ形にしてある)。
- ★測つて居らぬ事 (見込み)★: `fetch-depth: 2` の CI で merge commit の第一親が現に在るか。深さ 2 なら両親を含む筈だが ★CI で測つて居らぬ★ ―― B を入れるなら初回走行の log で `Changed-only mode: N of M` の N を見る事。

## §4 今 起きて居る事 (直さぬ間)
- CI は ★main への push で常に 0 本★ を書く ⇒ ★一本化は「消さぬ」形では効いて居るが「書く」形では未だ効いて居らぬ★。
- 表 4,249 行が不変だつたのは ★書かなかつたから★ でもある (減 0 の検算とは別の話・四条③: 二つの数を混ぜぬ)。
- 枝 (`feature/**`) への push では三点が非空ゆゑ ★従前どほり書く★ 筈 (measure 0・見込み)。

## §5 境界
DB 讀 0・書 0・SQL 実行 0 / 走行 = v3 を ★import して include 判定を 2 関数呼んだのみ★ (network 0・POST 0・DELETE 0) /
fetch・pull・clone・push・prune 0 (局所に在つた ref のみ) / 製品 file へ 0 字 (書換は GO の後) / PR・枝へ手を入れて 0 /
shell `>` `>>` `tee` 0 (書込は python `open()`) / secret の値 0 (名のみ・.env の中身は印字して居らぬ) / 患者本文 0 /
他席の inbox へ書込 0 / Commander の箱 0 打 / 旧樹 wt-964a06d0 不触。
