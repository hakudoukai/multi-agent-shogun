# ★双子を一本にする案★(km-186 ㋔ ／ 委員長裁 seq333611)

刻 = 2026-09-18T20:47:09+0900 ／ 席 = ashigaru-mac-2(專任2) ／ 固定 = `6bde7170ce574090a6139ba2dfe3aa4cb6db8634`
枝 = `ashigaru-mac-2/km-186-futago-no-kesu-jun-20260918` ／ commit = `4cb05b976ec0060796840e02dd579f1551d89841` ／ ★未 push・PR 未出・gh 未使用★

## 一 ★何を★

`docs/runbooks/ERR-EKARTE-001.md`(大文字・2596 bytes・blob `e6de627b…`・2026-05-05)を ★樹から外す★。
`docs/runbooks/err-ekarte-001.md`(小文字・3471 bytes・blob `de00cbd9…`・2026-05-29)は ★一字も変へぬ★。
彫つた実際 = ★1 file changed, 79 deletions(-)★(`raw/50_shime.txt` 逐語)。

## 二 ★何故★(数で)

| 根拠 | 数 | 紙 |
|---|---|---|
| 委員長が正と定めた | 裁 seq333611(正=小文字) | ―― |
| canon の索引が指す名 | ★小文字 2 行 4 当り ／ 大文字 0★ | `raw/20_*` `raw/25_*` |
| 版の新旧 | 小文字 = 5/29 新版 3471B ／ 大文字 = 5/5 旧版 2596B | `raw/10_kumi_git.tsv` |
| 此の Mac の disk | ★二つの名が同じ inode(10724954)★ ―― 実体は ★一本★ | `raw/10_disk.tsv` |
| 其の一本が抱く中身 | ★大文字の blob(2596B)★ ―― ★3471B は此の disk に一度も無い★ | `raw/25_kuichigai.tsv` |

∴ ★索引は正しい名を指して居るのに、此の Mac の読者が受け取る中身は旧版である。★
  link は壊れて居らぬ故、★誰も気付かぬ★。是が直すべき害である。

## 三 ★如何に戻すか★(★戻し方を先に書く★)

★戻す時も順が要る★ ―― 消す時と同じ理由(case を畳む disk では二つの名が一つの実体を指す)。

1. ★PR を出す前★: 枝を捨てるだけで足りる ―― `git worktree remove /Users/momizimac/wt/a2-km186` + `git branch -D ashigaru-mac-2/km-186-futago-no-kesu-jun-20260918`。
   remote には ★一行も無い★(`git ls-remote origin refs/heads/<当枝>` = 0 行・陽性対照 main = 1 行)。
2. ★merge した後★: `git revert 4cb05b976ec0060796840e02dd579f1551d89841` ―― blob `e6de627b…` は git の中に残つて居る故、
   ★中身は失はれぬ★。revert が大文字の名を同じ中身で戻す。
3. ★手で戻す時(★此処が罠★)★: `git checkout 6bde7170 -- docs/runbooks/ERR-EKARTE-001.md` を
   ★単独で打つな★ ―― case を畳む disk では ★其れが小文字の実体を 2596B で上書きする★。
   必ず ★其の後に `git checkout -- docs/runbooks/err-ekarte-001.md` を打て★(3471B へ戻す)。
   ―― ★消す時の ⑴⑵ と同じ形の順序が、戻す時にも要る。★

## 四 ★此の案が直さぬ事★

* `ERR-EKARTE-001`(`.md` の付かぬ ★error code★)19 当りには ★一指も触れぬ★。code は消えぬ。
* 小文字 file の ★中身も名も変へぬ★。
* ★他の双子は 0 組★(固定 commit 548 path ／ 全 ref 378 本・別々の樹 306 本を歩いて 1 組のみ)。
  ∴ 此の案は ★此の一組だけの話★ である。

## 五 ★判定と merge★(裁333611 ㋗)

* PR を出すのは ★當席★。判定 = ★軍師mac★。merge = ★委員長★。
* ★然るに當席は push も gh も禁じられて居る★(裁332449 ／ km-172 ㋕⑶)。
  ∴ 彫つた枝は ★己の worktree の中に在る★。★出し方の御下知を仰ぐ★(km-185 の便 q_pr=333805 と同じ壁)。

## 六 ★命の字義から外した唯一の点★

裁333611 ㋓⑷ は「`git add -f` の後 `git commit --only <同じ path>`」と定める。
★此の双子では字義通りでは彫れぬ★ ―― `--only <大文字>` も `add -f`+`--only` も
★rc=1「no changes added to commit」で HEAD が動かなかつた★(`raw/40_shiken.tsv` `raw/41_shiken2.tsv`)。
因 = `--only` は ★worktree の其の path を読み直す★ が、case を畳む disk では ★大文字の名がまだ開ける★ 故、
git は「消えた」ではなく「modified」と見る。
∴ ⑷ のみ ★素の `git commit`★ を用ゐた ―― ★index に `D <大文字>` 一行しか載つて居らぬ事を先に assert★ してから。
★⑴と⑵の順は一字も変へて居らぬ。⑵も飛ばして居らぬ。★
