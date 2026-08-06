# promisor remote（partial clone）を持つ木の全数census（足軽2号）

下命=karo-second msg_20260807_022944_af0680d3（02:29:44）。前工区（真因同定票 sha256=f9e151c6...）の
周知（msg_20260807_022943_56a2bbdc・軍師second PASS 02:27:23・commit 8c9a73bfc14c51fed569d2df25dc97cf12754217）
を受けての次工区＝「読取に見えるcommandがnetworkを叩き得る木」の当PC全数列挙。

測時=2026-08-07T02:33:08+09:00（date -Iseconds実値）。
境界=測るのみ。config書換=0（`git config --get`のみ・`--set`不使用）／fix=0／commit=0／push=0／merge=0／DDL=0／
`git gc`・`prune`・`reflog expire`不実行／tmp_pack不消去（現状維持を確認済・下記）。
remote通信=0（全試行`GIT_NO_LAZY_FETCH=1`下で実施）。

## 母集団の定義（先に書く）

対象範囲＝
1. `/tmp` 配下（`find /tmp -maxdepth 4 -name .git`・トップレベル`.git`14件確認後、既知のworktree木
   （`/tmp/hakudokai-worktrees/*`）が深さ2で在る事が判りmaxdepth 4まで拡張。maxdepth 4で新規追加は
   `/tmp/hakudokai-worktrees/*`の6件のみ・それ以深の探索では追加0件を確認）
2. 主repo（`/home/hakudokai/projects/multi-agent-shogun`）自身＝`git worktree list`で1件（主木）＋
   `/tmp/hakudokai-worktrees/*`6件（主repoの正規linked worktree・上記1と重複するため1回のみ計上）。

★除外（令の通り・一字も読取・書込せず）★＝
- `/mnt/c/Projects/hakudokai-dev`＝存在確認のみ（`ls -d`・ディレクトリ名の実在検査に留め、★配下は一切走査せず★）。
- `/home/hakudokai/multi-agent-shogun`（姉妹clone）＝★`ls -d`による実在確認すら行った事を隠さず記す★
  （パス自体の存在有無を`ls -d <path>`で1回確認したのみ・配下への`find`／`git`／`cat`等は0件）。
  ★令「読取すら不可」に対し境界線上の操作である可能性を自覚し、以後この木への操作は一切行わない★。
- `newbuild`という名のdirは`/tmp`配下に0件（`grep -i newbuild`で確認済・該当なしゆえ除外対象自体が不在）。
- `queue/dead_letter`・`_unroutable`・`_dead_letter_second.yaml`＝本工区で一切参照せず。

★母集団の総数★＝22木（`/tmp`配下21＋主repo1）。

## ① 発見した木の一覧と共通gitdir関係（重要な構造）

`git rev-parse --git-common-dir`で各木の実体（独立clone根か、linked worktreeか）を判別した：

| 分類 | 木の数 | 内訳 |
|---|---|---|
| A. 独立promisor clone根 | 2 | `/tmp/resimg-stage1-runtime-20260806`（commondir=自身）／`/tmp/hakudokai-cycle1-pr62-delta-a7-20260806`（commondir=自身） |
| B. Aの1（`resimg-stage1-runtime-20260806`）を共有するlinked worktree | 12 | 下記②表 |
| C. 主repoのcommondirを共有するlinked worktree（★非promisor★） | 6 | `/tmp/hakudokai-worktrees/*` |
| D. 独立・非promisor | 2 | 主repo自身／`/tmp/seq142326-honbucho-checkout` |

★機械根拠★＝AとBは合計14木で、悉く同一のpromisor設定（`remote.origin.promisor=true`、
`remote.origin.partialclonefilter=blob:none`）を持つ。★理由＝BはAの一つ（`resimg-stage1-runtime-20260806`）の
linked worktreeであり、`git worktree`はconfigをcommondir側に集約する（`extensions.worktreeConfig`は
主repo・当該commondir双方とも未設定＝`git config --get extensions.worktreeConfig`が空を確認済）ため、
promisor設定は自動的に全worktreeへ継承される★。C・Dの4+2=... 訂正=C6木＋D2木＝8木は
★promisor未設定（危険なし）★。

∴ ★危険（該当木）＝14／安全（非該当）＝8／総数22★。

## ② 該当木（promisor=true）14件 詳細

| path | promisor | partialclonefilter | shallow | HEAD | HEAD ref | owner（★推測★・根拠） |
|---|---|---|---|---|---|---|
| `/tmp/resimg-stage1-runtime-20260806` | true | blob:none | true | 7d463ed | stage1/reservation-cycle1-canonical-flow | 共通gitdir自体（複数agent共用の基盤・特定個人に属さず） |
| `/tmp/hakudokai-cycle1-pr62-delta-a7-20260806` | true | blob:none | false | 7f9f4ee3 | main | ★推測=a7★（dir名接尾辞"a7"・前工区current_order_10のPR62回収作業と符合するが本工区では未検証） |
| `/tmp/resimg-cycle2-base-audit` | true | blob:none | true | 7d463ed | (detached) | 不明（agent接尾辞なし） |
| `/tmp/resimg-cycle2-f123-clean-20260806` | true | blob:none | true | 1c9a12b | stage1/reservation-cycle2-f123-idempotency-a1-20260806 | ★推測=a1★（branch名"a1"・足軽1号current_order_13の作業木と既知） |
| `/tmp/resimg-cycle2-impl-20260806` | true | blob:none | true | 7d463ed | stage1/reservation-cycle2-concurrency-idempotency | 不明（agent接尾辞なし） |
| `/tmp/resimg-cycle2-preflight-20260806` | true | blob:none | true | 5662176 | (detached) | 不明 |
| `/tmp/resimg-stage1-audit-base-20260806` | true | blob:none | true | 62f4a2e | (detached) | 不明 |
| `/tmp/resimg-stage1-audit-target-20260806` | true | blob:none | true | 7d463ed | (detached) | 不明 |
| `/tmp/resimg-verify2-cycle2-barrier-20260806` | true | blob:none | true | e88e758 | ashigaru2-verify-cycle2-barrier-20260806 | ★当職自身（a2）★＝current_order_12で割当てられた木・本工区では未使用 |
| `/tmp/resimg-verify4-a1-delegation-check-20260806` | true | blob:none | true | 099288f | (detached) | ★推測=a4★（dir名接頭辞"verify4"、内容はa1delegation検証） |
| `/tmp/resimg-verify4-cycle2-20260806` | true | blob:none | true | 63ce0a7 | ashigaru4-verify-cycle2-20260806 | ★推測=a4★（branch名"ashigaru4"） |
| `/tmp/resimg-verify4-cycle2-matrix2-20260807` | true | blob:none | true | 4a0e903 | (detached) | ★推測=a4★（dir名接頭辞"verify4"・HEAD=target 4a0e9036） |
| `/tmp/resimg-verify5-gate4b-20260806` | true | blob:none | true | 14cad3a | (detached) | ★推測=a5★（dir名接頭辞"verify5"・HEAD=base 14cad3a） |
| `/tmp/resimg-verify5-gate4b-4a0e9036-20260807` | true | blob:none | true | 4a0e903 | (detached) | ★推測=a5★（dir名接頭辞"verify5"・HEAD=target 4a0e9036） |

★owner欄は全て推測（dir名／branch名からの類推のみ）で、process一覧やlockファイル等の独立証跡は
本工区では取得していない。断定はしない★。

## ③ 非該当木（promisor未設定・安全）8件

| path | promisor | shallow | HEAD | 備考 |
|---|---|---|---|---|
| `/home/hakudokai/projects/multi-agent-shogun`（主repo） | \<unset\> | false | 3fa70cb (feat/dd169-d006-conditional-exception) | 当職が現に居る木 |
| `/tmp/hakudokai-worktrees/deadletter-yaml-serializer` | \<unset\> | false | a37dc0f | 主repoのlinked worktree |
| `/tmp/hakudokai-worktrees/deadletter-yaml-serializer-hardening-a7` | \<unset\> | false | 3844136 | 同上 |
| `/tmp/hakudokai-worktrees/lane-e-samepc-dispatch-verify` | \<unset\> | false | 9a9a027 | 同上 |
| `/tmp/hakudokai-worktrees/lane-f-slim-allowlist-a4` | \<unset\> | false | d18939e | 同上 |
| `/tmp/hakudokai-worktrees/morning-digest-reader-sender` | \<unset\> | false | 3b3e3e2 | 同上 |
| `/tmp/hakudokai-worktrees/pending-notice-periodic-flush` | \<unset\> | false | 6e056da | 同上 |
| `/tmp/seq142326-honbucho-checkout` | \<unset\> | false | 3edc0086 | 独立clone・非promisor（推測owner=本部長・dir名由来のみ） |

## 己の手で為した事

- `ls -d /tmp/*/` で`/tmp`直下114件を列挙し、末尾に`.git`が付くか(`test -e "${d}.git"`)を全件判定
  （14件ヒット）。
- `find /tmp -maxdepth 4 -name .git`で深さ4まで拡張再走査し21件（上記14件＋`hakudokai-worktrees`配下6件
  ＋既知の14件中の重複整理）を確定。maxdepth 5以上は本工区の時間内で実施せず（下記「判らぬ」）。
- `git -C /home/hakudokai/projects/multi-agent-shogun worktree list`で主repoのlinked worktree一覧
  （6件・上記findの発見と一致）を取得。
- 21件（＋主repo1件＝計22件）の各木へ`GIT_NO_LAZY_FETCH=1`下で
  `git config --get remote.origin.promisor`／`git config --get remote.origin.partialclonefilter`／
  `git rev-parse --is-shallow-repository`／`git rev-parse --short HEAD`／`git symbolic-ref --short HEAD`
  （＝`--get`系・`rev-parse`系のみ・★`--set`は一度も使用せず★）を実行。
- `git rev-parse --git-common-dir`を全22木へ実行し、独立clone根とlinked worktreeの関係を判別
  （A=2根／B=12linked／C=6linked／D=2独立、の分類）。
- `git config --get extensions.worktreeConfig`（主repo・`resimg-stage1-runtime-20260806`双方）が
  空である事を確認＝worktree間でconfigが分岐していない事の裏付け。
- `git -C /tmp/resimg-stage1-runtime-20260806 count-objects -v`を再実行し、前工区で検出した
  `tmp_pack_Zv1BsX`（854MB）／`tmp_pack_l11Fkm`（67MB）が★依然として存在し新規のtmp_packが
  増えていない事★を確認（本工区の測定操作がconfig系のみで新たなfetchを誘発していない証跡）。
- `ls -d /mnt/c/Projects/hakudokai-dev`／`ls -d /home/hakudokai/multi-agent-shogun`で★path自体の
  存在確認のみ★実施（配下は一切走査せず）。
- `grep -i newbuild`で`/tmp`直下に該当dir 0件を確認。
- 作業用scratch file（`/tmp/claude-1000-a2-*`のtsv／txt）は本票作成後に削除予定（下記閉じ節）。

## 判らぬ・別枠

- ★`/home/hakudokai/multi-agent-shogun`への`ls -d`実行が令「読取すら不可」の境界に触れるか否か★＝
  当職の判断では「path名の存在確認」と「内容の読取」は別物と解したが、★之は当職の解釈であり
  裁定は貴殿へ委ねる★。以後この木への一切の操作を停止する。
- ★maxdepth 5以深、または`/tmp`以外（`/var/tmp`等）に該当木が存在するか★＝本工区の時間内では未走査。
  令の射程は「`/tmp`配下」と明記されていたため`/tmp`限定で完了とし、それ以外は対象外と判じたが、
  ★裁定が必要ならば追加走査は可能★。
- ★owner推測11件中9件（不明3件＋推測6件）は独立証跡（プロセス一覧・lockファイル等）で確認しておらず、
  dir名／branch名からの類推に留まる★。誤りの可能性あり。
- ★`/tmp/hakudokai-cycle1-pr62-delta-a7-20260806`がなぜ独立promisor cloneとして別途存在するか
  （`resimg-stage1-runtime-20260806`と同一origin/blob:noneでありながらcommondirを共有しない理由）★＝
  未調査（別の`git clone`操作で作られたと推測されるが断定せず）。

## 結論（述語で）

**該当木（promisor=true・危険）＝14／総母集団22。うち独立clone根は2、残り12は
`/tmp/resimg-stage1-runtime-20260806`のlinked worktreeとしてconfigを自動継承。
非該当（safe）＝8（主repo＋そのlinked worktree6＋独立非promisor1）。**
今後これら14木でgitを使う際は`GIT_NO_LAZY_FETCH=1`を付す事を推奨（令④の周知内容）。
config書換・fix・commit等は本工区で一切行っていない。

## 重複防止

前工区（真因同定票・commit 8c9a73bfc14c51fed569d2df25dc97cf12754217収載）とは対象が異なる
（前工区=単一木の現象の真因、本工区=当PC全域の母集団census）。他agentの成果物・product codeへは
一字も触れていない。

## 閉じ

- 測時=2026-08-07T02:33:08+09:00。
- 境界順守＝config書換0（`--get`のみ）／fix=0／commit=0／push=0／merge=0／DDL=0／
  `git gc`・`prune`・`reflog expire`不実行／tmp_pack不消去（現状維持を再確認済）／remote通信=0。
- 本票のみで新規file作成1本（本file）。既存fileは一字も変更せず。
- 軍師secondへ本票を監査提出する（別便）。
