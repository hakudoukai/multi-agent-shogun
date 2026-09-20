# km-249 ⑵/⑶ ―― 家老mac「保険」枝が眞かを己の器で檢めた記録

板鍵=未立（裁 seq341919）。本頁は km-249 の本命 ―― 家老macが張つた2本の「保険」枝
（`mac/disk-versions-20260920`＝commit 11a117c0dd48c64f96d741a42963c3ca8382bf63、
`mac/shared-index-rescue-20260920`＝commit 7844cae8063751da32d030ef9933f4a8922747fa）が、
`git checkout main`（裁341919⑷）で失はれ得る現disk內容を實際に護れるかを、
家老の言を信ぜず己の器で獨立に測つた記録である。

## (a) HEAD と 11a117c0 の差 ―― 家老の「50」を己の器で測り直す

```
git diff --name-status HEAD 11a117c0dd48c64f96d741a42963c3ca8382bf63
```
raw/01_diff_namestatus_head_vs_11a117c0.txt（67行）

內譯: **D=17 / M=50**（awk+sort+uniq -c で機械的に算出）。

- D=17 は悉く `docs/evidence/ashigaru-mac-1_km-247-sai341919-yon-ga-ushinau-utsuwa-17-mai-20260921/`
  配下 ―― ashigaru-mac-1 自身の km-247 束（HEADには在るが11a117c0の古い時點には無かつた）。
  ★之は當職の擔當外ゆゑ、之以上は調べず、唯「50の外」として除く事のみ記す★。
- **M=50 は家老の言(50)と★完全に一致★**（正の檢証結果・前段までの相違報告とは異なる型）。

## (b) 保険commitを detach worktree で確かめる

```
git worktree add --detach /Users/momizimac/wt/km249-insurance-check 11a117c0dd48c64f96d741a42963c3ca8382bf63
```
rc=0。raw/10_insurance_worktree_status.txt に「Not currently on any branch.」
「nothing to commit, working tree clean」「symbolic-ref rc=1」を記録 ―― 眞に detached。

`git worktree list` の生出力（raw/09_worktree_list_detached_evidence.txt）を見ると、
本repoには元々★16箇所★の detached worktree が他の座と共存して居り(a2-km186-t1〜t5,
a3-km224, karo-main-ff 等)、一件も lock 衝突を起こして居らぬ ―― 「--detach は他座の
checkout を塞がぬ」は文書の言ではなく★現に走つて居る repo の實態★で確認した。

## (c) 50枚全ての内容比較 ―― 二器(shasum+git hash-object)、母數50

対象: (a)で確定した M=50 の各path。比較先:
- 主樹の**現disk**（`/Users/momizimac/multi-agent-shogun/<path>`、未commitの現物）
- 保険worktreeの**11a117c0時點**（`/Users/momizimac/wt/km249-insurance-check/<path>`）

★器1・shasum -a 256★（raw/04_compare_shasum.txt）:
```
母數=50 一致=50 相違=0 主樹実体無=0 保険實体無=0
```

★器2・git hash-object★（raw/05_compare_hashobject.txt）:
```
母數=50 一致=50 相違=0
```

兩器とも★50/50 完全一致★。零相違・零缺・零實体無。

### 附記 ―― 此の50枚は「現作業木の未staged變更」と★同一集合★

```
git diff --name-only   # index(=HEAD相当)とdiskの差、未staged分
```
raw/06_unstaged_workdir_50.txt（50行）と raw/03_50files_list.txt を `diff` した結果
★完全一致(0行差分)★ ―― 之は偶然ではない。11a117c0が捕へたのは正に「HEADから
未commitで動いた現在の作業木の変更」其の物であり、家老の主張（此の枝が現disk危険域の
保険である）は★構造的に正しい対象を捕へて居る★事が數で示された。

## (d) 結語 ―― `git checkout main` の可逆性（打たず、數で決めた）

家老の言の對象(main への checkout)が實際に何を壞し得るかを、HEAD↔main差
（raw/02_diff_namestatus_head_vs_main.txt、33A/1416D/13M/其他rename數件）と
上記50枚の重なりで測つた。

50枚のうち、HEADとmainでも差が在る物は★8枚★のみ（raw/08_overlap_50_vs_headmain_8files.txt
＝D×1 `docs/evidence/.../MANIFEST.txt` + M×6 `scripts/*`）。殘る42枚はHEAD=main
（差分無し）ゆゑ、之等はcheckoutの對象外で觸れられぬ。

git の checkout は path毎に三方比較（workdir/index/target）を行ひ、
**index=target なら未staged編集はそのまま殘し、index≠targetなら(force無しでは)
「local changesが上書きされる」で★中止★する**（git本體の擧動、本repoでの新設ではない）。
∴:
- 42枚: main==HEADゆゑ最初から無風。
- 8枚: force無き `git checkout main` は其の場で★止まる★（黙つて壞さぬ ―― no-silent-failure
  の理に適ふ）。壞れるのは `-f`/`--force` または `git reset --hard` 等、★明示的に強制した時のみ★。

**∴ ★可逆★ ―― 假に強制實行で50枚(8枚を含む)全てが上書き・消失しても、其の内容は
commit 11a117c0dd48c64f96d741a42963c3ca8382bf63(枝 mac/disk-versions-20260920)に
byte単位で保存濟(本節(c)で二器實測濟)ゆゑ、下記手順で復元できる。**

### 復元手順（★書くのみ・打たぬ★）

```
# 前提: commit 11a117c0dd48c64f96d741a42963c3ca8382bf63 と
#       枝 mac/disk-versions-20260920 が削除されて居ない事を先に確認
git rev-parse --verify mac/disk-versions-20260920

# 50枚のpath一覧(本頁 raw/03_50files_list.txt と同一)を読み、1枚づつ復元
while IFS= read -r p; do
  git checkout 11a117c0dd48c64f96d741a42963c3ca8382bf63 -- "$p"
done < raw/03_50files_list.txt

# 復元後、diskが11a117c0と一致した事を再度二器で確認(本頁(c)と同じ手順)
```

## (e)/⑶ ―― 「5b66d552 = 現在の共有樹index」は眞か（己の器で測る・未測にせず）

```
git write-tree   # 現indexから木を計算・ref/workdir不変・read-only
```
→ `1b34cfc44ccff62b3c5226355e1818aaf42386e6`（raw/11_reachability_and_writetree.txt）

```
git diff --name-status 5b66d552dd673b5223d15f2ea4ea103ad48d4c27 1b34cfc44ccff62b3c5226355e1818aaf42386e6
```
raw/07_diff_5b66vs_currentindex_17.txt ―― **17行、悉くA(現indexにのみ在る)**。
ファイル數: 5b66d552=2849枚 / 現index=2866枚（差=17、一致）。

**結語 = ★等しくない★（「未測」ではなく、數で否と示した）**。17枚は悉く
ashigaru-mac-1 の km-247束（(a)節のD=17と★同一集合★、raw/07とraw/01の対象を
`comm -12`で突合し重複0を確認）。

**解釈**: `mac/shared-index-rescue-20260920`(7844cae8)は2026-09-21 00:48:56作成
（raw/11の`git log`該当行と一致）―― 其の後 ashigaru-mac-1 が km-247束を現indexへ
足した(17枚)ため、★作成時點では眞であつたであらう「index=枝」が、其の後の他座の
正常な作業進行により★現在は成立せぬ★。之は捏造ではなく★時間差による陳腐化★であり、
共通する2849枚については差分0(全てA、M/D無し)ゆゑ、其の部分の內容捕捉自體は正しい。

**∴ `mac/shared-index-rescue-20260920` を「現在の共有樹indexの完全な保険」として
扱ふのは誤り ―― 17枚(ashigaru-mac-1 km-247束)が缺けて居る。之は其の17枚の
擔當(ashigaru-mac-1)の裁量內であり、當職はこれ以上調べぬ(擔當外)。**

## 母數・器・rc・刻

- 母數: (a)=67行(D17/M50) / (c)=50(二器) / (e)=17(A限定、母17)
- 器: `git diff --name-status`(2回)・`shasum -a 256`・`git hash-object`・
  `git worktree add --detach`・`git write-tree`・`git rev-parse --verify`・
  `git cat-file -t`・`git for-each-ref`・`git ls-remote`
- rc: 全器 rc=0(異常終了無し) ―― `git write-tree`はread-only(index書換無し・
  ref/workdir不変、之を`git status`で確認: "nothing to commit, working tree clean"は
  worktree側の状態であり主樹には触れて居らぬ)
- 刻: 2026-09-21(本弾實施時刻、當職ローカル)

## 開示 ―― 未完了・限界

- 保険2枝は★local限定★(upstream無・origin未登録、raw/11)。ネットワーク障碍やdisk
  破損等で此のrepo自體が失はれれば保険も同時に失はれる(git commitの一般的性質であり、
  之は本檢証の對象外)。
- (a)で見た D=17(ashigaru-mac-1 km-247束)自體の妥當性は擔當外ゆゑ未調査(意図的)。
- 本檢証は主樹(`/Users/momizimac/multi-agent-shogun`)を★読取専用★で行ひ、
  `git checkout main` は一度も打つて居らぬ(禁則遵守)。
