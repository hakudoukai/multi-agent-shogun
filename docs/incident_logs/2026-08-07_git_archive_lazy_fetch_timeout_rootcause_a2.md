# git archive exit=124 (timeout) 真因同定 — AST機械再走の失敗原因（足軽2号）

下命=karo-second msg_20260807_021704_9fc90892（02:17:04）。前工区（docs/incident_logs/2026-08-07_gate5_predicate5_residual_sql_new_target_a2.md
sha256=d40212c8cdd97203dc02e16cedaa82254e15d22b570952c9bdd6c9ab41e8d623）③節で「AST機械再走
（git archive）がexit=124（timeout）で失敗・原因未特定」と自己申告した件の真因究明。

測時=2026-08-07T02:23:03+09:00（date -Iseconds実値）。
境界=測るのみ。fix=0・commit=0・push=0・merge=0・DDL=0・product codeに一字も触れず。
remote通信=当職は本工区中一切実施せず（下記の通り`GIT_NO_LAZY_FETCH=1`で全試行を無効化）。

## 対象repo・対象commit

`/tmp/resimg-stage1-runtime-20260806`（共通gitdir・読取専用コマンドのみ使用）。
target=`4a0e9036ed94022d79baa4a1e2cf88d5827eec12`（足軽1号 current_order_13）。
元試行の原コマンド=`git -C /tmp/resimg-stage1-runtime-20260806 archive 4a0e9036... backend -o /tmp/verify2_backend_archive.tar`（30秒timeoutで単離試験・前工区③節記載）。

## ① repoがshallow＋partial（promisor）cloneである事を機械確認

```
$ git -C /tmp/resimg-stage1-runtime-20260806 rev-parse --is-shallow-repository
true
$ git -C /tmp/resimg-stage1-runtime-20260806 config --get-regexp 'remote\..*'
remote.origin.url git@github.com:hakudoukai/hakudokai-dev.git
remote.origin.fetch +refs/heads/main:refs/remotes/origin/main
remote.origin.promisor true
remote.origin.partialclonefilter blob:none
```

★機械根拠★＝`partialclonefilter=blob:none`ゆえ、blob（ファイル実体）の大半はclone時に取得されず、
必要になった時点で`promisor.origin.url`（github.com）へ遅延fetchする設計である。

## ② `git archive`が要求する少なくとも1個のblobがlocalに不在である事を実測

`GIT_NO_LAZY_FETCH=1`（遅延fetchを無効化＝★networkへ一切接続しない設定★）を付して同一コマンドを再試行：

```
$ timeout 10 env GIT_NO_LAZY_FETCH=1 git -C /tmp/resimg-stage1-runtime-20260806 \
    archive 4a0e9036... backend -o /tmp/claude-1000-a2-archive-test-20260807.tar
warning: lazy fetching disabled; some objects may not be available
fatal: could not fetch 2fd1bc29cf65936a3286393b205277446720cd69 from promisor remote
（exit=128・即時失敗・hangせず）
```

★機械根拠★＝network接続を遮断した状態では、同一コマンドは30秒を待たず即座に（exit=128）失敗する。
∴ 元のexit=124（timeout）は「CPU処理が重くて終わらなかった」のではなく、
★lazy fetch機構がnetworkへ接続を試みてその接続が完了しなかった★事によるものと機械的に特定できる。

## ③ 不在blobは対象pathspec（backend/）の外にあり、pathspecの絞り込みでは回避不能である事を確認

不在blob `2fd1bc29cf65936a3286393b205277446720cd69` の実体を特定：

```
$ git -C /tmp/resimg-stage1-runtime-20260806 ls-tree -r 4a0e9036... | grep 2fd1bc29
100644 blob 2fd1bc29...	.agents/skills/supabase-postgres-best-practices/SKILL.md
```

★backend/配下ではない★（`.agents/skills/...`）。念のためbackend/tree配下の全blob（858件）を
`GIT_NO_LAZY_FETCH=1`下で`cat-file -e`により悉皆点検した結果、★858件悉くlocalに存在（missing=0）★
——不在は`.agents/`側の1件のみで、backend/自体のblobは1件も欠けていない。

さらに、pathspecを単一fileへ極限まで絞っても（`backend/services/appointment_lifecycle.py`のみ）、
同じ不在blob（`.agents/skills/.../SKILL.md`）への到達を試み同一エラーで即時失敗した：

```
$ timeout 8 env GIT_NO_LAZY_FETCH=1 git ... archive 4a0e9036... backend/services/appointment_lifecycle.py -o ...
fatal: could not fetch 2fd1bc29... from promisor remote
```

★機械根拠★＝`git archive`はpathspecで指定した範囲外のblobにも到達しようとする内部動作を持ち、
pathspecを絞る事では本現象を回避できない。★この内部動作がなぜpathspec範囲外のblobを要求するのか
（属性計算の全木走査か、promisor側のbatch fetch挙動か）は当職の実測では特定できず、判らぬまま残す（下記）★。

## ④ 遅延fetchが実際にnetworkへ到達し大容量転送中であった証拠（未完のtmp_pack）

```
$ git -C /tmp/resimg-stage1-runtime-20260806 count-objects -v
warning: garbage found: .git/objects/pack/tmp_pack_Zv1BsX
warning: garbage found: .git/objects/pack/tmp_pack_l11Fkm
...
$ ls -la .git/objects/pack/tmp_pack_*
-r--r--r-- 1 hakudokai hakudokai 854589439 Aug  7 01:58 tmp_pack_Zv1BsX
-r--r--r-- 1 hakudokai hakudokai  67452927 Aug  7 02:00 tmp_pack_l11Fkm
```

★機械根拠★＝854MB＋67MB（合計約922MB）の★未完成pack file★が`.git/objects/pack/`に残存している。
mtime（01:58／02:00）は前工区の測時（2026-08-07T02:00:21）の直前〜同時刻に一致する。
`git index-pack`は転送完了前のpackを`tmp_pack_*`のまま残し、完了せねば正式pack（`.pack`+`.idx`）へ
昇格しない——ゆえに★これらは「接続すらできなかった」のではなく「接続し転送が開始されたが、
30秒のtimeoutで強制終了された際に中断された、未完成の受信データ」である★。

∴ ★真因＝「blob:noneのpartial clone」＋「git archiveがpathspec外の1blobを含め遅延fetchを要求」＋
「その遅延fetchは実際にgithub.comへ接続し大容量（≥922MB分、単一blobの想定サイズを大きく超える）の
転送を開始したが、30秒のtimeout値では完了せず強制終了された」★。
「hang（無応答）」ではなく「時間内に終わらない転送」であった、という点が★前工区③の推測
（`lazy fetching disabled`警告と同系の可能性、断定せず）よりも一歩具体化した機械根拠★である。

## 己の手で為した事

- `git rev-parse --is-shallow-repository`／`git config --get-regexp 'remote\..*'` で
  shallow＋partial（promisor=true・partialclonefilter=blob:none）を機械確認。
- `GIT_NO_LAZY_FETCH=1`を付した同一`git archive`コマンドを実行し、即時失敗（exit=128）を確認
  （★network接続は一切試みていない★——このENV varはlazy fetch自体を無効化する）。
- `git ls-tree -r`で不在blob`2fd1bc29...`の実体パスを特定（`.agents/skills/.../SKILL.md`）。
- backend/tree配下の全858 blobへ`GIT_NO_LAZY_FETCH=1 git cat-file -e`を悉皆実行し、missing=0を確認。
- pathspecを単一fileへ絞った再試行でも同一blobへの到達要求が起きる事を確認。
- `git count-objects -v`で`tmp_pack_*`garbage 2件を検出し、`ls -la`でsize/mtimeを機械取得。
- 自己が作成した検証用tar（0 byte・失敗のため実体なし）およびscratch fileは全て削除済（rm実行・
  product code・既存fileには一字も触れず）。

## 判らぬ・別枠

- ★なぜ`git archive`がpathspec範囲外の`.agents/skills/.../SKILL.md`のblobへ到達しようとするのか★
  （属性・export-ignore計算のための全木走査か、promisor remoteのbatch fetch実装上の挙動か）は
  当職の実測では特定できず。git内部実装の追加調査（ソース読解）は本工区のscope外と判じ実施せず。
- ★tmp_pack 2件（854MB／67MB）が単一の`git archive`試行由来か、共通gitdirを使う他agentの操作由来かは
  完全には切り分けられず★。mtimeが前工区の測時と近接する事から★強い相関はあるが、当職はその場で
  リアルタイム監視していた訳ではなく、事後のforensic相関に留まる★（断定はしない）。
- ★30秒のtimeout値を伸ばせば完走するか★は未検証（境界＝再試行は行わない・当職はlive network試行を
  一切行わないため、之を検証する事自体が禁に触れる＝measured試行の範囲外として残す）。
- ★partial cloneの設計自体（なぜこのcommon gitdirがblob:noneで運用されているか）の当否・改善要否★は
  裁定せず（測るのみの立場）。

## 結論（述語で）

**真因＝partial clone（blob:none）+ `git archive`のpathspec外blob到達要求 + 遅延fetchが実際に
大容量transferを開始し30秒timeoutに収まらず強制終了、という複合要因。単純な「hang」ではなく
「時間内に終わらない実transfer」である事を機械根拠（即時失敗との対比・tmp_pack実体サイズ）で示した。**
直せずとも同定できれば可、との令に従い、修正（fix）は一切行っていない。

## 重複防止

本工区は前工区（同ashigaru2作成 sha256=d40212c8...）③節で自己申告した未解明点の追加調査であり、
述語⑤（residual raw SQL）の結論そのものへは触れていない（既に確定済・不成立）。他agentの成果物・
product codeへは一字も触れていない。

## 閉じ

- 測時=2026-08-07T02:23:03+09:00。
- 分離＝測るは当職・直すは足軽1号（本工区は直し得る対象ではなくinfra/repo設定の観測）。
- fix=0・commit=0・push=0・merge=0・DDL=0・remote通信=0（全て`GIT_NO_LAZY_FETCH=1`下で実施）。
- 本票のみで新規file作成1本（本file）。既存fileは一字も変更せず。
- 軍師secondへ本票を監査提出する（別便）。
