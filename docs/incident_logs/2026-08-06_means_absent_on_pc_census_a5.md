# ㈠「手段そのものが当PCに無かった」物を数える (足軽5号)

## 境・未測・限界 (冒頭に置く)

読取のみ。`ls`/`git ls-files --error-unmatch`/`git cat-file -t`を用いた。★rcはpipeに通していない★
(いずれも単発コマンドの終了コードを直接判定に用い、`| head`等のpipeを介していない)。

## 測時・断面

測時=2026-08-06T09:05頃 (複数コマンド実行にまたがる)。HEAD=f386a8b972ebabaf8fadaa4da83556dd6e346864 (前工区提出時点から不変・本工区は新規commitを跨いでいない)。

## 母集団 (⒜)

`queue/inbox/karo-second.yaml`・`queue/inbox/shogun-second.yaml` (+各`_archive`) を「当隊が外部から下命を
受け取る受領点」と位置づけ、そこに絞った (全足軽inboxまで展開すると再配信の二重計上になる為——前工区で
得た教訓をここでも適用した)。

`from ∈ {third_pc(委員長), commander(Commander), honbucho(本部長)}` かつ `type ∈ {task_assigned, cmd_new,
status_update}` かつ本日 (2026-08-06) の便を抽出した所 **89件** (systemd_self_check/ashigaru6等の内部
status_updateを含む広い定義)。

★ここでさらに絞り込んだ★=「下命」の実質を持つのは委員長・Commander・本部長発の便であり、足軽・軍師の
status_update (自己申告等) は「当隊が外部から受けた下命」の趣旨に当たらぬと判じ、`from ∈
{third_pc, commander, honbucho}` へ絞った=**13件**。

さらに内容ハッシュで重複排除 (同一broadcastがkaro-second.yaml/shogun-second.yaml両方へ着地するため) した所
**9件** (ユニークな下命)。

## 判じ方 (⒝ — 何を「外部の物を指しておる」と見たか)

具体的なfile path・commit hash・worktree pathを本文中に明記し、受け手がそれを取得・参照する事を要求している
物のみを対象とした。★DB table名やSQL query文・inbox内のseq番号への参照 (処理済 seq が箱に既に在る事を
前提とする指示) は対象外とした★——理由=これらは「当PCに実在するか」を問う性質の物ではなく (DBは常時
接続前提・inboxは既に手元にある)、本工区の趣旨 (手段=file/helper/端点/正本の不在) に当たらぬと判じた。

## 分母 (9件中4件が該当)

| # | 便 | from | 参照する手段 |
|---|---|---|---|
| A | `msg_20260806_074022_08eba560` (07:40:22) | third_pc | `.claude/rules/gunshi-approval-authority.md` |
| B | `msg_20260806_083105_4fea0002` (08:31:05) | honbucho | patch file・rollback file・source worktree・base commit (4種) |
| C | `msg_20260806_084644_b2dd0332` (08:46:44) | third_pc | `docs/rules/reservation-imaging-division-charter.md` |
| D | `msg_20260806_085029_15a46fbf` (08:50:29) | third_pc | canon doc 7件 (Cと同一fileを含む) |

残り5件 (`msg_20260806_011213`/`012310`/`032321`/`075259`/`085321`、悉くCommander督励便) はDB query・
seq番号参照のみで上記判じ方により対象外とした。

## 実測 (⒞ — 三値: 不在／在るがgit外／在る)

```
$ ls .claude/rules/gunshi-approval-authority.md          → 不在 (working-tree)
$ git ls-files --error-unmatch .claude/rules/gunshi-approval-authority.md → git追跡なし
$ ls docs/rules/reservation-imaging-division-charter.md  → 不在
$ ls .claude/rules/autonomy-and-restraint.md              → 不在
$ ls docs/rules/fleet-composition-manifest.yaml           → 不在
$ ls docs/rules/hermes-idle-ledger-20260806.md            → 不在
$ ls .claude/rules/lane-single-dispatcher.md               → 不在
$ ls .claude/rules/no-silent-failure.md                    → 不在
$ ls /home/hakudokai/hermes-departments/honbucho/reports/reserveimage-cycle2-gate2-4-handoff-20260806.patch → 在り
$ ls /home/hakudokai/hermes-departments/honbucho/reports/reserveimage-cycle2-ddl-rehearsal-rollback-20260806.md → 在り
$ ls -d /tmp/resimg-cycle2-impl-20260806                   → 在り (directory)
$ git -C /tmp/resimg-stage1-runtime-20260806 cat-file -t 7d463edae84c704edabbd9da5465078dc62e55b1 → commit (在る・母repoにて到達可)
```

### 一意artifact単位の集計 (11件・重複除去後)

| 三値 | 件数 | 内訳 |
|---|---|---|
| 不在 | 7 | `.claude/rules/gunshi-approval-authority.md` / `docs/rules/reservation-imaging-division-charter.md` / `.claude/rules/autonomy-and-restraint.md` / `docs/rules/fleet-composition-manifest.yaml` / `docs/rules/hermes-idle-ledger-20260806.md` / `.claude/rules/lane-single-dispatcher.md` / `.claude/rules/no-silent-failure.md` |
| 在るがgit外 | 3 | patch file / rollback file / source worktree (いずれも `/home` または `/tmp` の当repo外) |
| 在る | 1 | base commit 7d463eda… (指定された母repo `/tmp/resimg-stage1-runtime-20260806` にて到達可能・当repoからは不到達だが便自体が正しいrepoを指示していた) |

### 便(下命)単位の集計 (⒟の様式=数え上げは同じ行に)

```
便A(third_pc,07:40:22)=不在1/在るがgit外0/在る0 → 便判定=不在
便B(honbucho,08:31:05)=不在0/在るがgit外3/在る1 → 便判定=手段は在る(git外含む)・不在なし
便C(third_pc,08:46:44)=不在1/在るがgit外0/在る0 → 便判定=不在
便D(third_pc,08:50:29)=不在7/在るがgit外0/在る0 → 便判定=不在
∴ 4便中3便(A/C/D)が「手段そのものが当PCに無かった」に該当・1便(B)は該当せず。
```

★便Cと便Dは同一file (`docs/rules/reservation-imaging-division-charter.md`) を重複して指している★——
便Dは便Cが指した不在に気付いた委員長殿御自身の訂正便であり、**同じ欠落を二度数える形**になっている事を
明記する (下命単位では2件・artifact単位では1件、という数え方の違いが生じる。前工区で得た教訓「述語が
違えば数は静かに嘘をつく」がここでも当てはまる)。

## 零に理由

該当なし (不在が現に3便・7artifact確認できた為、本節に「零」はない)。

## 判じ難し (⒠)

便B (honbucho発、Cycle2 patch dispatch) の base commit は「当repo (multi-agent-shogun) には無し」だが
「指定された母repo (/tmp/resimg-stage1-runtime-20260806) には在る」——★便自身が正しい参照先を明示して
いた為、これを『手段が届かなんだ』に数えるべきか迷った★。当職の判断=★数えぬ★ (便が自ら正しいrepoを
教えており、受け手が迷わず到達できる形だった為)。★然れど 委員長殿の便D方式 (『repo名を添えねば不到達』)
に照らせば、便Bも repo名を明示しており模範的だった、とも言える★——この対比を健全例として下記に記す。

## 健全例 (最低一つ)

便B (honbucho発Cycle2 dispatch) は、当repo外の手段 (patch/rollback/worktree/base commit) を用いる際、
悉く**絶対pathまたはrepo名+branch名を明示**しており、受け手 (将軍second→家老second→足軽) が実際に
迷わず到達できた (当職の実測でも全て発見できた)。便A/C/Dが「相対path・repo名なし」で不在を招いたのと
対照的であり、★同じ『他repo参照』という状況で、明示の有無が結果を分けた実例★として記録する。

## 【本工区で己が直した誤り】

初手で母集団をfrom制限なしの89件 (ashigaru6/systemd_self_check等の内部status_updateを含む) で取ってしまい、
これは「当隊が外部から受けた下命」の趣旨に合わぬと気付き、`third_pc/commander/honbucho`のみへ絞り直した。
広く取り過ぎた初期定義をそのまま提出していれば、内部の自己申告便まで「下命」として誤って数える所であった。

## 対に成る他工区

前工区自身 (`docs/incident_logs/2026-08-06_means_path_census_a5.md`) ——㈡(下命にpathを書かなんだ・当隊発)と
本工区㈠(手段そのものが当PCに無かった・外部発)は直交する2軸であり、家老second下命の通り「直す所が別」
である事を当職も確認した。㈡は「書き方」の是正で直り、㈠は「repo/branch明示」または「main統合の徹底」
で直る、という別々の処方箋が要る。

## 監査体制

暫定二者制 (軍師second + Gemini)。Codex leg は禁令 (2026-07-21事案・SAFETY裁定 seq132707) により停止中。

## 禁則遵守の申告

読取のみ。破壊的操作・commit・push・patch適用・worktree新設 いずれも未実施。newbuild不触・姉妹clone(2件)
読取すら不触。`.claude/rules/*`・`docs/rules/*`は当repoに不在であり、当然ながら編集も行っていない
(存在しない物は編集し得ぬ)。
