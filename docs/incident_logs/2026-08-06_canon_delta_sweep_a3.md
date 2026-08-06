# 2026-08-06 canon delta sweep (a3)

発令: karo-second msg_20260806_135319_28ca18a8 「canon delta 174件を掃き、当隊に掛かる物を選り出せ(裁定は書くな・材料のみ)」
実施者: 足軽3号 / 対象木: /mnt/c/Projects/hakudokai-dev (read-only)

## 0. 母集団宣言(命令の出力そのまま)

```
$ cd /mnt/c/Projects/hakudokai-dev && git rev-list --count 78573ba7..feb945cf
174

$ git log 78573ba7..feb945cf --format='%h|%s' | grep -ic canon   # 件名(subject)にcanonを含む数
141
```

窓 = `78573ba7..feb945cf` / 木 = `/mnt/c/Projects/hakudokai-dev`(read-only、fetch/checkout/reset一切為さず)。

**★母集団の階を自己訂正(作法⑩に該当)★**: 当初 `git log --grep='canon' -i`(git本体の--grep=**全文**照合)で試した所 **142件** が返り、発令書の指定(件名=**141件**)と食い違うた。
差分1件(`65cef914`)は本文にcanonを含むが件名には含まぬ(件名照合では対象外)。∴以後 **件名(subject)のみへの `grep -i canon` 照合(141件)** を正本母集団とし、`65cef914` は母集団外として扱う。
両者の出力:
```
$ git log 78573ba7..feb945cf --grep='canon' -i --format='%h' | wc -l   # 全文照合
142
$ git log 78573ba7..feb945cf --format='%h|%s' | grep -ic canon        # 件名照合(正本)
141
$ comm -23 <(全文照合sha一覧) <(件名照合sha一覧)
65cef914
```

## 1. 特筆事項(裁定にあらず・事実のみ)

### 1-1. 委員長作68条1653行が同日中に全削除された(5c2842aa)

`5c2842aa canon(理事長令 2026-08-06): 不要なものを全部削る=本日追加の1,653行・68条を削除し「自立と節度」1枚に置換`

実測diffstat:
```
 .claude/rules/autonomy-and-restraint.md |   40 +
 .claude/rules/no-silent-failure.md      |  358 ---------
 docs/rules/auditor-character-canon.md   | 1295 -------------------------------
 3 files changed, 40 insertions(+), 1653 deletions(-)
```

理事長逐語(commit本文より):「不要なものは全部削って、それぞれが自分で考え、自立して、節度をもって動くようにしてください」「破壊的行為や危険な行為のみ行わないようにしてもらえればいいです」「止まらない 止まらない進む進む」。

由来として本文に明記: 「2026-08-05、委員長が一日で正本へ1,653行・68条を追加した(ほぼ全てが『疑え・測れ・出所を検めよ』)。結果、足軽が『これは実利用者の指示ではない』と言い出して止まり、艦隊が動かなくなった」。

**当隊pin(78573ba7)基準の純増分は0ではない**: `git diff --stat 78573ba7 feb945cf` で auditor-character-canon.md=+692行 / no-silent-failure.md=+518行(実測)。∴当隊pin時点より後、両fileは一旦2084行/876行相当まで膨張し、その後789行/518行(今朝の版)へ差し戻された。

**checkpoint実測による生存判定**: line-count trace(`git show <sha>:<path> | wc -l` を全68条touching-commitへ逐次実行)で、auditor-character-canon.mdは`c0cfb364`(789行)、no-silent-failure.mdは`3d9c043b`(504行、後に`908e87d2`で518行=tip一致)を境に、それ以前(または境界=checkpoint自身+post-revert追加)は現存、それ以降5c2842aa直前までは削除済と判明(`git diff <checkpoint> feb945cf -- <path>` = 0行で裏取り済)。本表の各行の判定にこの生存/削除区分を反映した。

### 1-2. 当隊の一principleの逐語源または並行同型が本削除対象に含まれていた(292c2c11)

`292c2c11 canon(no-silent-failure): 決着=逐語で運んでも運び手がAIである限り出所はAIである(機構が実測で答えた)`

本文(該当箇所逐語):
> 実利用者の許可を要する操作は、実利用者ご自身の発話でしか解けない。AIが「許可が下りた」と伝えることでは解けない。別の言い回しで通そうとするな。それこそがtunnelingである。

当隊memory `relayed-approval-is-not-user-approval` の核心(「実ユーザーの承認はuser messageにのみ現れる」「言い換えて通そうとする事自体が違反」)と極めて近い。

**★生存判定★**: 292c2c11はcheckpoint(`3d9c043b`)より後に位置し、5c2842aaで**削除済(REVERTED確認済)**。条文としては現存せず。
**但し核は生存**: 5c2842aaの代替file `.claude/rules/autonomy-and-restraint.md` 42行目に
```
$ git show feb945cf:.claude/rules/autonomy-and-restraint.md | grep -n '別経路\|拒んだ'
42:- 機構（分類器・門）が実際に拒んだ操作を、別経路で通すこと
```
という形で、tunneling禁の核(「機構が拒んだ操作を別経路で通すな」)は生存が確認できた。

∴ 当隊の二条のうち「中継の承認では動かぬ」に相当する条は、**詳細な条文としては消えたが、原則の核(拒まれた操作の別経路通過禁)は生き残っている**、という二層の答えになる。**裁定はせぬ**——これが当隊の条をどう変えるかは karo-second/軍師の判断に委ねる。

### 1-3. 「誰が裁くかの条を裁が下りたと読むな」に相当する条は見当たらず(読了範囲内)

検索語(逐語): `裁が下りた` / `裁定.{0,10}下り` / `裁定.{0,10}読む` / `判定者.{0,10}名` / `判事` / `裁く者` を141件の全commit本文(`git log ... -p`)へ照合、**該当0件**。
★『無い』と断定はせぬ★——本検索は上記キーワード群に限定した拾い読みであり、別の言い回しで同義の条が存在する可能性は排除できない。

### 1-4. 予約・画像事業部の新設は当隊の現工区と directory一致(d0c05de0ほか)

`d0c05de0 canon(事業部制): 予約・画像事業部 憲章v1.0=第1号パイロット(理事長設計2026-08-05)`

実査結果:
```
$ git show feb945cf:docs/rules/completed-features-registry.yaml | grep -n reservation -A30
...owns:
  - backend/api/appointment
  - backend/services/appointment
  - backend/services/booking_
  ...(他11path)

$ find . -iname '*booking_validator*' -o -iname '*appointment_service*'
./backend/services/appointment_service.py
./backend/services/booking_validator.py
```
当隊F1 idempotency/booking_validator.py/appointment_service.py/create_appointmentの現工区は、上記registry記載の`reservation.owns`配下に**directory一致**する。新設された事業部体制(事業部長→委員長へ報告/本部長=企画執行/将軍second=実装差配/専務=テスト/環境部長=横断保守、委員長は統括・赤信号裁定・main統合専権に絞る)が、当隊現工区の指揮系統・監査経路にどう関わるかは**karo-second/軍師の判断事項**(当職は材料提示のみ)。

### 1-5. 軍師の承認権限が理事長令で拡張された(19f05dfb)

`19f05dfb canon(approval): 破壊的でない低レベル承認は担当の軍師が判断して進める(理事長令2026-08-06)`

新設file: `.claude/rules/gunshi-approval-authority.md` + hakudokai-dev側 `CLAUDE.md` 改修。判定基準=「元に戻せるか/患者の記録に触れるか」の2問。「機構が拒んだ操作は軍師承認でも通せない」と明記(tunneling禁との整合が本文中に明示)。

## 2. 全141件 三値判定表

凡例: 掛かる/掛からぬ/判じ得ぬ の三値。★は「実読」(git show --no-patch/-p でcommit全文を読了)、無印は「機械判定」(件名は141件全数精読済+`git show --name-only`によるfile-touch確認、本文は拾い読み未実施)。

| # | sha | 件名 | 判定 | 目安 | 根拠(引いた命令+要旨) |
|---|---|---|---|---|---|
| 1 | `9d4f864b` | canon(rule): 静かな失敗の禁止 ALL-NO-SILENT-FAILURE-01 制定 + §35窓で数えるな | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 2 | `cb89965d` | canon(rule): §35-b 型で漉すな — filterの形が母集団を静かに削る | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 3 | `bd022e22` | canon(rule): 第4実例=鳴っているのに緒の切れた鐘 / 通知の自己適用検定 / §36上位の訂正こそ根拠を見よ | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 4 | `4b6d1586` | canon(rule): 第5実例=門の手前に溜まった完成品(本日3件目の同型) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 5 | `ac167217` | canon(rule): §37 「手が足りない」と「入力待ち」を区別せよ | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 6 | `2fc28ec9` | canon(rule): §35-c 陽性対照は方法を検定するが範囲は検定しない | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 7 | `c9449f47` | canon(rule): §35-d 切り口が母集団を決める / §36-b 要件は新旧に同じ物差しで | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 8 | `0ec6ab81` | canon(rule): §35-e 位置で同定するな内容で同定せよ + §36見出し復旧 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 9 | `bcc47304` | canon(rule): 第6実例=入力欄にtextが残ったまま「ready」 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 10 | `6c42c5dc` | canon(rule): §35-f 認可は列挙で与えるな性質で与えよ | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 11 | `fd1ff35c` | canon(rule): 第7実例=偽ACKが矛盾する二重発令を生んだ(現行犯) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 12 | `31352553` | canon(fix): 第7実例の帰責を訂正 — 家老ではなく将軍secondの撤回漏れ | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 13 | `36e69f1d` | canon(rule): §35-g 不一致を見たら まず同一対象性を疑え | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 14 | `ebdf430b` | canon(rule): 差配一本化原則に鉄則2(c)(d)追補 + 鉄則3のtopic指定を廃止(配送正本との衝突解消) | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' ebdf430b (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 15 | `4adde504` | canon(fix): 鉄則2(c)を同日中に是正 + (c-2)衝突は安く済ませよ + (e)repo名必須 | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' 4adde504 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 16 | `d8997a2d` | canon(rule): §35-h 直ったの隣に残数を書け / §35-i 読んだ上で今なお正しいかを問え | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 17 | `fc4a9a7e` | canon(rule): 「済んだ」に判定者を併記 / 止めの判別基準(実測か先行決定か) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 18 | `bdadcb3f` | canon(rule): §35-j 権限を表す語は分解して書け | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 19 | `64616e2e` | canon(rule): 台帳書式に「対象」を足す(判定者・時刻だけでは足りない) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 20 | `a761a514` | canon(rule): enforcement-over-documentation に実測された代価を追加 — 書いた後に8割が失われた | **判じ得ぬ** | 不明 | 機械判定=git show --name-only --format='' a761a514 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。enforcement-over-documentation.md等の規律執行系file変更。本文拾い読み未実施。 |
| 21 | `0698a2c8` | canon(rule): §36-c 上位が全部背負うな量刑を分けよ / 「読まれた数」を測る形 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 22 | `1dd5115f` | canon(rule): 10-c 上が先に誤りを出す — 全規律が立っている一点 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 23 | `29afd7a2` | canon(rule): §35-g に「単位」軸と「列挙は世界が動けば古くなる」/ 台帳書式に「版」 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 24 | `3dbeecdd` | canon(fix): 鉄則1のdone_whenを二段へ是正 + 基準は自動では当たらない | **判じ得ぬ** | 不明 | 機械判定=git show --name-only --format='' 3dbeecdd (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。enforcement-over-documentation.md等の規律執行系file変更。本文拾い読み未実施。 |
| 25 | `653fb965` | canon(rule): 第8実例=配送を直す当人の受信経路が死んでいた | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 26 | `746fc7fe` | canon(fix): done_whenの三つ目の穴(試した形しか保証されぬ) + 断面は秒まで書け | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 27 | `5089d2f2` | canon(rule): 着地版「実在M件のうちN件」/ 列挙に断面併記 / 10-c-2 序列は梯子ではなく円 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 28 | `ab98a0f5` | canon(rule): §35族の総括「何を1と数えるか」/ 機構は己が最も破る所へ / 禁じた正本は二つあった | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 29 | `bd74fe56` | canon(rule): 本日の結論 — 艦隊が新たに得たのは知識ではなく測定である | **判じ得ぬ** | 不明 | 機械判定=git show --name-only --format='' bd74fe56 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。enforcement-over-documentation.md等の規律執行系file変更。本文拾い読み未実施。 |
| 30 | `a6492366` | canon(rule): 第9実例=迂回が成立すると故障が見えなくなる | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 31 | `d1375ef1` | canon(rule): 設計された冗長もまた故障を隠す(第9実例の一段深い形) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 32 | `cd91ce38` | canon(rule): SKIPは異常なしと同じ顔をする / 階層①へ上がる問いの立て方 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 33 | `c3dd84e5` | canon(rule): desktop役職(専務・常務)宛の封筒規約を配送正本へ登録 | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' c3dd84e5 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 34 | `352303c1` | canon(rule): 着地M/NをX/Y/Zへ三分割 / 収束を積極的証拠に / 半分だけの迂回 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 35 | `80acc001` | canon(rule): 不在は既定で成功の顔をする / 自己適用検定は機構ごと / 止血に賢さを持ち込むな / 違反頻度の実測 | **判じ得ぬ** | 不明 | 機械判定=git show --name-only --format='' 80acc001 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。enforcement-over-documentation.md等の規律執行系file変更。本文拾い読み未実施。 |
| 36 | `f96f8c1b` | canon(rule): 第10実例=「済んだのに告げぬ」(本主題の裏返し) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 37 | `786cdbc9` | canon(rule): 第11実例=「いつ」を定めても「誰が」が無ければ願いである / Phase判定の機械的な線 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 38 | `6f417d39` | canon(new): 稼働の門(go-live gate)を新設 — 先送りを実行可能にする器 | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' 6f417d39 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。github-governance.md/go-live-gate.md/comms-all-green-goal.md。件名・path上で四目安いずれにも該当せず(読了範囲内、本文拾い読み未実施)。 |
| 39 | `3ea99a3a` | canon(rule): 配送機構の第一原則=宛先不明は送り主へ返せ(理事長令 2026-08-04) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 40 | `4ef49de7` | canon(rule): 承認は見た者だけが為すべきである(将軍second具申) | **判じ得ぬ** | ⑵候補 | 実読=git show --no-patch 4ef49de7(全文)。「見えない命令を承認するな・見た者だけが承認」将軍second具申。当隊memory[[relayed-approval-is-not-user-approval]]と主題近接だが同一条か別条かは射程外ゆえ判断保留(裁定禁)。★no-silent-failure.md checkpoint(3d9c043b)以前ゆえ現存(survived)確認済。 |
| 41 | `c3ad861b` | canon(rule): 検知器が「承認待ち」を「処理中」と読んでいた | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 42 | `5ab49e0e` | canon(rule): 第12実例=台帳は正しい、それでも届いていない(本主題の最も純粋な形) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 43 | `7098f3e6` | canon(rule): desktop役職宛にtask UUID相関を必須化(副委員長設計・委員長承認+精緻化) | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' 7098f3e6 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 44 | `f01d1823` | canon(rule): 返信先(reply_to)を書かなければ返しは戻らない(理事長令 2026-08-04) | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' f01d1823 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 45 | `55d2f915` | canon(rule): なぜdesktop役職だけ規約が違うのか(理事長 2026-08-04) | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' 55d2f915 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 46 | `7a2f896d` | canon(rule): 電子メールでは常識だった — 40年前に解決済みの問題を作り直していた(理事長) | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' 7a2f896d (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 47 | `26b6e049` | canon(delivery-protocol): v2.0 全面改訂=電子メールの体系に統一(理事長令 2026-08-04) | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' 26b6e049 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 48 | `4c432348` | canon(delivery-protocol): 新規便の宛先=§3-b 箱とベルを分離(理事長指摘 2026-08-04) | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' 4c432348 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 49 | `54bcd57a` | canon(lane-single-dispatcher): §3-b 理事長直命はレーン司令官へ同報せよ(2026-08-04実害) | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' 54bcd57a (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 50 | `dc8907ac` | canon(no-silent-failure): 第8実例に再発を追記(同じ相手・4時間後・最優先便が未着) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 51 | `f005861a` | canon(enforcement): 3-c追補=作った者だけが機構の外に居た(2026-08-04 18:21実例) | **判じ得ぬ** | 不明 | 機械判定=git show --name-only --format='' f005861a (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。enforcement-over-documentation.md等の規律執行系file変更。本文拾い読み未実施。 |
| 52 | `8cd68fdc` | canon(rule): 知識格差警告義務 v1.1 + ALL-SEARCH-BEFORE-CREATE-01追補(理事長令 2026-08-04) | **判じ得ぬ** | 不明 | 機械判定=git show --name-only --format='' 8cd68fdc (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。enforcement-over-documentation.md等の規律執行系file変更。本文拾い読み未実施。 |
| 53 | `df8b590d` | canon(enforcement): 四つ目の実証=稼働18分で実態の40倍で鳴った(2026-08-04 18:51) | **判じ得ぬ** | 不明 | 機械判定=git show --name-only --format='' df8b590d (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。enforcement-over-documentation.md等の規律執行系file変更。本文拾い読み未実施。 |
| 54 | `3d9c043b` | canon(no-silent-failure): 裏返しの教訓=経路を疑う癖は観測を疑わない癖になる(2026-08-04 19:00) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 55 | `02acf53a` | canon: 通り道の数(3-e) + 測り方5条(§38-§41,§35-d-2) 2026-08-04夕 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 56 | `dfafa3c4` | canon(auditor): §42 禁は「触れる層」でなく「壊れる物」で括れ/過剰な禁止は静かな失敗 | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 57 | `1e876d41` | canon(auditor): §43 測定の限界を先に開示せよ/開示が検定を呼ぶ(2026-08-04実証) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 58 | `19615c98` | canon: 決定の一本化≠実行の独占 / 同一再試行の回避≠事情の再確認(2026-08-04・将軍second) | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' 19615c98 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 59 | `2058bc51` | canon(auditor): §38-b 「知らぬ」と書くことは知らぬまま決める許しにならぬ(将軍second自己申告・裁定自撤回) | **判じ得ぬ** | 不明 | 実読=git show --no-patch 2058bc51(全文=本文空・件名のみ)。§38-b「知らぬと書く事は知らぬまま決める許しにならぬ」将軍second自己申告+裁定自撤回。★auditor-character-canon.md checkpoint(c0cfb364)以前ゆえ現存(survived)確認済。当隊の「誰が裁くかの条を裁が下りたと読むな」との異同は本文が件名のみで判じ得ず。 |
| 60 | `c0cfb364` | ledger: 経路3(third_pc移植)CLOSED=8/12 / canon §44 残す物と読ませる物は別(将軍second) | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 61 | `f92ffc48` | canon: 組織図と連絡経路を実測で正本化(理事長令 2026-08-04) | **判じ得ぬ** | ⑴⑷候補 | 機械判定=git show --name-only --format='' f92ffc48 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。fleet-composition-manifest.yaml変更。同fileはashigaru-second/second_pcを明示的に記載(grep実査済=当隊の名がある台帳)だが、本commit個別差分内容は未実読ゆえ判じ得ず。 |
| 62 | `dfe4ae74` | canon(rule): Hermes人格 標準規律ブロック v1.0(理事長令「人格統一 GO」2026-08-04) | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' dfe4ae74 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。Hermes人格統一専用file。当隊(Claude Code系ashigaru/karo/gunshi)はHermes人格の対象外(CLAUDE.md記載の役職と別体系)。 |
| 63 | `ba5c2421` | canon+skill: 受信規律(既読水位の自己申告)を全Hermesの標準義務へ(理事長裁定) | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' ba5c2421 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。Hermes人格統一専用file。当隊(Claude Code系ashigaru/karo/gunshi)はHermes人格の対象外(CLAUDE.md記載の役職と別体系)。 |
| 64 | `9306a29a` | canon: 人格統一 11/13体 適用完了(理事長令GO)・適用台帳をSHA付きで記録 | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' 9306a29a (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。Hermes人格統一専用file。当隊(Claude Code系ashigaru/karo/gunshi)はHermes人格の対象外(CLAUDE.md記載の役職と別体系)。 |
| 65 | `1c5c518e` | canon: 軍師2体のHermes化完了 + 人格統一13/13 + 宛先表更新(理事長goal) | **判じ得ぬ** | ⑴⑷候補 | 機械判定=git show --name-only --format='' 1c5c518e (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。fleet-composition-manifest.yaml変更。同fileはashigaru-second/second_pcを明示的に記載(grep実査済=当隊の名がある台帳)だが、本commit個別差分内容は未実読ゆえ判じ得ず。 |
| 66 | `43b333d9` | canon(auditor): §45 ファイルの状態からプロセスの状態を推すな(2026-08-05・委員長の入替漏れ7本) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 67 | `b8164388` | canon(no-silent-failure): 過剰な検知もまた静かな失敗である(理事長裁定・PIIガードv3) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 68 | `4835201d` | canon: 受信規律ゲートv1=通知を門へ(理事長裁定「この方法では不合格」) | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' 4835201d (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。Hermes人格統一専用file。当隊(Claude Code系ashigaru/karo/gunshi)はHermes人格の対象外(CLAUDE.md記載の役職と別体系)。 |
| 69 | `a92a277f` | canon: 受信規律ゲート=「POP before SMTP」と命名(理事長)+設計の第一問を制定 | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' a92a277f (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 70 | `012a12b6` | canon(no-silent-failure): 確かめる前に動くな=副作用は判定より先に起きる(専務の自己調査) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 71 | `8263af49` | canon(裁定台帳): 理事長設計の裁定一覧＋30分警報＋発信門を装着(起点2026-08-05 10:00) | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' 8263af49 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。Hermes人格統一専用file。当隊(Claude Code系ashigaru/karo/gunshi)はHermes人格の対象外(CLAUDE.md記載の役職と別体系)。 |
| 72 | `803d8f37` | canon(監査規範): §45-b 近くの測り易い物を代わりに測るな / §35-c-2 陽性対照自体が範囲誤りで死ぬ | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 73 | `6a535196` | canon(静かな失敗): 第13実例=偽ACKは「残る借り」を済んだに見せる(将軍second実測) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 74 | `28fdef7a` | canon(配送第一原則): 「戻せない理由は無い」を訂正=差出人欄が退役済みの箱を指す型③ | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 75 | `94679ea8` | canon(GitHub統治): mainへの統合は委員長専権を再確認+git名義の誤りを是正(理事長令) | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' 94679ea8 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。github-governance.md/go-live-gate.md/comms-all-green-goal.md。件名・path上で四目安いずれにも該当せず(読了範囲内、本文拾い読み未実施)。 |
| 76 | `97321c3c` | canon(静かな失敗): 対照実験でしか見えぬ欠陥+書いた本人が同日に同じ型を二度踏んだ | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 77 | `f7f1232a` | canon(配送): §1-b 便とテレメトリを分ける=pc_handshakeが二用途を兼ねていた | **判じ得ぬ** | ⑵候補 | 機械判定=git show --name-only --format='' f7f1232a (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。docs/rules/delivery-protocol.md等の配送規約file変更。grep -in "inbox_write\|queue/inbox" で0件=当隊現行mailbox実装への直接言及は見当たらず(読了範囲内)。上位の配送思想として重なる可能性は排除できず。 |
| 78 | `d0c05de0` | canon(事業部制): 予約・画像事業部 憲章v1.0=第1号パイロット(理事長設計2026-08-05) | **掛かる** | ⑶⑷ | 実読=git show --no-patch d0c05de0(全文)+completed-features-registry.yaml実査(git show feb945cf:...)。理事長設計「予約・画像事業部」憲章v1.0新設。registry reservation.owns に backend/services/appointment* / backend/services/booking_* を確認、当隊F1/create_appointment現工区の実file(backend/services/appointment_service.py・booking_validator.py、find実測で実在確認済)と directory一致。 |
| 79 | `8a16b0ab` | canon(事業部制): 憲章v1.1=一流企業の実践に当てて9つの抜けを補強+理事長GO 2点反映 | **掛かる** | ⑶⑷ | 機械判定=git show --name-only --format='' 8a16b0ab (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。予約・画像事業部憲章/事業部構築ルールブック系file変更。d0c05de0の実読知見(registry owns一致)を同系列commitへ準用。 |
| 80 | `314d8330` | canon(監査規範): §35-d-3 健全例こそ母集団を疑え=異常は声を上げるが健全は黙って誤る | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 81 | `1bf1d0a8` | canon(監査規範): §46 三つの短条(規律と嘘の担保/閉じる前に今を問え/褒は機構へ落とせ) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 82 | `a8725b3c` | canon(監査規範): §47 memoryと帰属の五条(未報告欠陥の一覧/現物照合/害と因/出所/自罰の検め) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 83 | `1cafae19` | canon(監査規範): §47-c但し書き+§47-f索引は本文より古びる+§47-g篩は対照と対で配れ | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 84 | `e78e1037` | canon(監査規範): 訂正=17件は二重計上・正は12件+§47-h 発見を次の一手に当てたか | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 85 | `bdac4612` | canon(監査規範): §48 新しい条を作る事が古い条を忘れさせる(委員長の二重実装指示) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 86 | `5f54fcf4` | canon(監査規範): §48-b 正本は問い毎に定めよ+§48-c 検査は守る物であって守られる物ではない | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 87 | `b699273a` | canon(監査規範): 訂正=「14」は記憶由来・実測5+§48-d引用は断面+§48-e条文は根拠より長生き | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 88 | `3aead90d` | canon(監査規範): §48-e根拠差し替え(誤診→母集団の範囲)+§48-f条が当てはまった時こそ検めよ | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 89 | `e215c814` | canon(監査規範): §48-g 手順は理由より長生きする(家老second・本日の総括) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 90 | `091510bb` | canon(監査規範): §48-dへ門の三値勘定を追記=門/半/零(在るが呼ばれぬ) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 91 | `d164bdb1` | canon(監査規範): §48-d-2 配った条を配った日に配った当人が破る——時刻もまた断面 | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 92 | `01a011f4` | canon(監査規範): §48-d-2へ機序確定/門の射程外(零)/後始末+§48-d-3 条は立てた領域の外へ伸びない | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 93 | `cb78a0c0` | canon(監査規範): 手順「命令を貼れ」の限界+門と手順は重ならない(将軍secondが配布直前に止めた) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 94 | `62c03807` | canon(監査規範): §48-d-4 配布の到達を箱で測るな+§48-d-5 証拠はfenceの外へ+機構の射程 | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 95 | `fbdcf063` | canon(監査規範): §48-e-2 器官が無い物は外から借りよ+五段は止まり難さの順であって効き目の順でない | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 96 | `d9b27480` | canon(監査規範): §48-d-6 検収は常に上限を持つ(形は測れ出所は測れぬ)+窓検定と族の四つ目 | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 97 | `ac80b720` | canon(訂正): 門が捕らえた者に合わせて門を緩めようとした+§48-d-7〜d-10(順序を問え/条は立てた直後が最も引かれぬ/検収は一時点/検収の道具が偽りの機会を作る) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 98 | `3235189b` | canon(監査規範): §48-d-11〜13 手順の形/押し通す誘惑は裁定の合図/未決には二種 | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 99 | `9028a821` | canon(監査規範): §48-d-14 repo名を添えよの裏返し(読む側は確かめよ)+§48-d-15 判定は終了コード | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 100 | `ec00fd06` | canon: 誤った説明は沈黙より悪い(第15実例)+§48-d-16 義務は見る仕掛けで成る+§48-d-17 安価さは越権の理由に成らぬ | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 101 | `634d0860` | canon(監査規範): §48-d-18〜20 一つの仕掛けで二つを測るな/案は己で試してから出せ/述語は一つの関数に集約せよ | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 102 | `0215404b` | canon: 成功もまた黙る(裏面)+§48-d-20-b 述語の二重実装は数の違いでしか露れぬ+§48-d-21 遅いのは判ずる者の位置 | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 103 | `295e95b4` | canon(監査規範): §48-d-22〜25 数の一致は集合の一致を証さない/母集団は起きた物から/独立には経路の条件/過小は生き残る/段ごとに正しくても全体は止まる/正直は上流から | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 104 | `d447ee4f` | canon(no-silent-failure): 最上段の同じ病=委員長の命令もまた受け手からは出所を検められぬ便である | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 105 | `01dc7117` | canon(監査規範): §48-d-26 commitを数えるのはgitに入った物を数えるに過ぎない+§48-d-27 第四値(取れなかった/無かった) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 106 | `f8347aa3` | canon(監査規範): §48-d-28 測ったは正しく運ばれたを証さない(対の九つ目)+§48-d-29 問いが裁定を動かす | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 107 | `8c4d4d01` | 訂正+canon: 「6分で1件戻る」は事実でなかった(委員長が四人目)+§48-d-30 正直の値段/§48-d-31 運んだ者が重い/§48-d-32 codeが遺した物/§48-d-33 機会と行為 | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 108 | `1de611e2` | canon(監査規範): §48-d-34 是正は常に「これから」にしか効かない+§48-d-35 共有できぬ場所は保全でない+§48-d-36 門を通る限りにおいて安全 | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 109 | `7556a01c` | canon(監査規範): 保全は四要件(④復元し得るが目的・①②③は手段)+要件を束ねるな+§48-d-37 在らぬ物を指す行は偽の値+§48-d-38 出所の規律は功にも及ぶ | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 110 | `e3ad2072` | canon(監査規範): §48-d-39 条は新しい欄へ自ら移らない(五値へ改訂)+§48-d-40 未測の前に下限を問え+§48-d-41 0件は実測で出し意味を限れ | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 111 | `82ef9530` | canon(監査規範): §48-d-42 検査もまた母集団を持つ(手法は伝播する・母集団は伝播しない)+§48-d-43 識別子照合の第三値=未取得 | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 112 | `10221858` | canon(監査規範): §48-d-44 数える者と許す者は別(閾の裁定)+§48-d-45 限界の列挙も網羅の主張+§48-d-46 母集団を手法に縫い付けて配れ+§48-d-47 委員長が己の門を己へ締めた | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 113 | `cdea3ddf` | canon(監査規範): §48-d-48 裁定にも門/半/零が在る+§48-d-49 実装者は裁定を満たし得ぬ点を先に述べよ+§48-d-50 二者択一は軸が一本足りない | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 114 | `9299a933` | canon(監査規範): §48-d-51 条件と命令を書き分けよ+§48-d-52 階層は意志の介在量(二つの尺を一本に束ねた)+§48-d-53 規律の賞には費用を問え | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 115 | `82bbfa5c` | canon(監査規範): §48-d-54 道具の既定出力は母集団を切る(見えた数と在る数は別)+§48-d-55 予定を完了形の顔で書くな | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 116 | `ac684845` | canon(監査規範): §48-d-56 復元可能性は忠実さの検査になる+§48-d-57 待つと放置は別(因を述べて待つは差配) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 117 | `8bc207e9` | canon(監査規範): §48-d-58 識別子は共有する者の間でしか意味を持たない(中継者は意味の担保者である) | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 118 | `776679d9` | canon(監査規範): §48-d-59 誤りを探す目は誤りでない物をも誤りに見せる(過剰訂正)+§48-d-60 経路の段を数える前に数えよ+§48-d-61 検める者の適性が一往復で出た | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 119 | `3436f7d7` | canon(監査規範): §48-d-62 隔離cloneで試し実測後に削除する(実測せよと触れるなの解)+§48-d-63 理屈による保証と実行による保証は別物 | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 120 | `6016b30f` | canon(監査規範): §48-d-64 設定fileの実在は機構が働いている証拠にならない(零の設定版)+§48-d-65 経路の異なる二者検算は互いの盲点を埋める | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 121 | `292c2c11` | canon(no-silent-failure): 決着=逐語で運んでも運び手がAIである限り出所はAIである(機構が実測で答えた) | **掛かる** | ⑵★特筆★ | 実読=git show -p 292c2c11(全文)。★当隊memory[[relayed-approval-is-not-user-approval]]の逐語源または並行同型★=「実利用者の許可を要する操作は実利用者ご自身の発話でしか解けない。AIが許可が下りたと伝えることでは解けない。別の言い回しで通そうとするな。それこそがtunnelingである」。★但し本commit自体の条文はcheckpoint後(3d9c043b以降)＝5c2842aaで削除され現存せず(REVERTED確認済)★。★核である「機構が実際に拒んだ操作を別経路で通すこと」禁は autonomy-and-restraint.md 42行目に survived形で現存(grep実査済)★。∴条文は消えたが原則の核は生きている、という二層の答えになる。 |
| 122 | `62b4a2ac` | canon(監査規範): §48-d-66 同じ欠陥が二度目=106分間 艦隊は実在しない滞留を追った | **掛からぬ** | 不明 | 機械判定+checkpoint実測。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は★5c2842aaで削除され現存せず★(checkpointより後・revert commit手前の区間)。★但し「理事長がこの日この量の規律を書いては全削除した」という事実そのものは残る(⑴の背景情報として)★。 |
| 123 | `f9c6ddd4` | canon(委員長identity): 足軽・部長級の承認ダイアログは委員長が判断する(理事長令2026-08-05) | **掛かる** | ⑴⑷ | 実読=git show --no-patch f9c6ddd4(全文)。理事長令2026-08-05「足軽・部長級の承認ダイアログは委員長が判断」= .claude/rules/iincho-identity-and-auto-notification.md新設(削除対象外path)。当隊の権限dialog停止時対応主体に直結し得る。 |
| 124 | `5c2842aa` | canon(理事長令 2026-08-06): 不要なものを全部削る=本日追加の1,653行・68条を削除し「自立と節度」1枚に置換 | **掛かる** | ⑴⑷ | 実読=git show --no-patch 5c2842aa (全文)。理事長令で委員長作68条1653行(auditor-character-canon.md 1295行+no-silent-failure.md 358行)を全削除し.claude/rules/autonomy-and-restraint.md(40行)へ置換。diffstat実測=1file 40+/2files 1653-。当隊が服する規律の量そのものが本日動いた最大の事象。 |
| 125 | `28490ca3` | canon(事業部憲章 改訂 2026-08-06 理事長令): 事業部に権限を与える=計画承認制を廃止し、上げるのは破壊的・危険のみ | **掛かる** | ⑶⑷ | 機械判定=git show --name-only --format='' 28490ca3 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。予約・画像事業部憲章/事業部構築ルールブック系file変更。d0c05de0の実読知見(registry owns一致)を同系列commitへ準用。 |
| 126 | `50767cab` | canon(事業部憲章): 役割分担を明記(方向性=委員長/実装=事業部/管理監督=5名で常時チェック・理事長令2026-08-06) | **掛かる** | ⑶⑷ | 機械判定=git show --name-only --format='' 50767cab (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。予約・画像事業部憲章/事業部構築ルールブック系file変更。d0c05de0の実読知見(registry owns一致)を同系列commitへ準用。 |
| 127 | `c5eaff2c` | canon(理事長令2026-08-06): 通信全経路グリーン=完成の定義。owner=環境部長(修理)+Commander(ループ) | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' c5eaff2c (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。github-governance.md/go-live-gate.md/comms-all-green-goal.md。件名・path上で四目安いずれにも該当せず(読了範囲内、本文拾い読み未実施)。 |
| 128 | `1d0e7692` | canon(理事長令2026-08-06): 「2回やらない」の誤読を訂正=禁止は同一再試行だけ。失敗したら理由を調べて別の手を打つ。諦めの許可ではない | **掛かる** | ⑴ | 実読=git show --no-patch 1d0e7692(全文=本文空・件名のみ)。理事長令2026-08-06「禁止は同一再試行だけ。失敗したら理由を調べて別の手を打つ。諦めの許可ではない」。当隊memory[[dev-root-cure-01-broadcast-obligation]]「同一再試行禁」と直結。 |
| 129 | `181f1504` | canon(comms-all-green): 本体は「受け手が忙しい時どうするか」=ベル不発61件(委員長宛・10時間・61%)の実測を主題に据える | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' 181f1504 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。github-governance.md/go-live-gate.md/comms-all-green-goal.md。件名・path上で四目安いずれにも該当せず(読了範囲内、本文拾い読み未実施)。 |
| 130 | `56621769` | canon(comms-all-green): 真因は「見送る」でなく「見送って委ねない」+受信面の点検を定例へ | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' 56621769 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。github-governance.md/go-live-gate.md/comms-all-green-goal.md。件名・path上で四目安いずれにも該当せず(読了範囲内、本文拾い読み未実施)。 |
| 131 | `acf9e850` | canon(fleet): エルメス稼働台帳2026-08-06 — 旧個体4体/休眠7体を名指し、環境部長1体が艦隊通信の73%と実測 | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' acf9e850 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。Hermes人格統一専用file。当隊(Claude Code系ashigaru/karo/gunshi)はHermes人格の対象外(CLAUDE.md記載の役職と別体系)。 |
| 132 | `0665daf3` | canon(fleet): 台帳を実測で訂正 — 休眠7体は存在せず、全員が詰まって待っていた | **掛からぬ** | 該当なし | 機械判定=git show --name-only --format='' 0665daf3 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。Hermes人格統一専用file。当隊(Claude Code系ashigaru/karo/gunshi)はHermes人格の対象外(CLAUDE.md記載の役職と別体系)。 |
| 133 | `eab17844` | canon(fleet): repoの実体をmanifestへ追加＋条(e-2)別木を見たらremoteを問え | **判じ得ぬ** | ⑴⑷候補 | 機械判定=git show --name-only --format='' eab17844 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。fleet-composition-manifest.yaml変更。同fileはashigaru-second/second_pcを明示的に記載(grep実査済=当隊の名がある台帳)だが、本commit個別差分内容は未実読ゆえ判じ得ず。 |
| 134 | `a8ae3bbc` | canon(fleet): P0注入口を疑いから確定へ — 逐語実測(seq149194)を記録 | **判じ得ぬ** | ⑴⑷候補 | 機械判定=git show --name-only --format='' a8ae3bbc (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。fleet-composition-manifest.yaml変更。同fileはashigaru-second/second_pcを明示的に記載(grep実査済=当隊の名がある台帳)だが、本commit個別差分内容は未実読ゆえ判じ得ず。 |
| 135 | `b279f777` | canon(autonomy): 己で止まったと機構が拒んだを分けよ＋repo外は裁の出所を先に問え | **掛かる** | ⑴⑵ | 実読=git show --no-patch b279f777(全文)。将軍second seq149205指摘=「拒まれたら言い換え再送も委員長経由の迂回もしない。上位者は迂回路ではない」。当隊memory[[relayed-approval-is-not-user-approval]]の「変えての再試行は迂回」「門の応答は語でなく理由で判ぜよ」と主題直結、同日(2026-08-06)発生の同種事案由来。 |
| 136 | `602d3340` | canon(fleet): second_pcのSSH portはmain_pcと逆(2223=Linux)＋WSL mount鍵は600複製が要る | **判じ得ぬ** | ⑴⑷候補 | 機械判定=git show --name-only --format='' 602d3340 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。fleet-composition-manifest.yaml変更。同fileはashigaru-second/second_pcを明示的に記載(grep実査済=当隊の名がある台帳)だが、本commit個別差分内容は未実読ゆえ判じ得ず。 |
| 137 | `19f05dfb` | canon(approval): 破壊的でない低レベル承認は担当の軍師が判断して進める(理事長令2026-08-06) | **掛かる** | ⑵ | 実読=git show --no-patch 19f05dfb(全文)+git show --name-only。理事長令2026-08-06「破壊的でない低レベル承認は担当の軍師が判断」新設(.claude/rules/gunshi-approval-authority.md新設+CLAUDE.md改修・auditor/no-silent両fileとは別path=削除対象外・現存確実)。軍師の承認権限拡張=当隊監査・承認経路(gunshi-second)に直結。 |
| 138 | `b9a22f85` | canon(fleet): 監査役の実態を訂正 — hermes-agent v0.19.0・設計上BLOCKEDのまま未配線(理事長令で立て直し) | **判じ得ぬ** | ⑴⑷候補 | 機械判定=git show --name-only --format='' b9a22f85 (機械判定・件名は全141件精読済だが本文拾い読みは未実施)。fleet-composition-manifest.yaml変更。同fileはashigaru-second/second_pcを明示的に記載(grep実査済=当隊の名がある台帳)だが、本commit個別差分内容は未実読ゆえ判じ得ず。 |
| 139 | `908e87d2` | canon(no-silent-failure): 委員長の自己違反を記録 — 読んでいない416件に受理印を押した | **判じ得ぬ** | 不明 | 機械判定+checkpoint実測(diff 78573ba7..feb945cf line-count trace)。auditor-character-canon.md/no-silent-failure.mdのうち本commitの追加分は5c2842aa後も★現存(survived)★=checkpoint(auditor:c0cfb364/789行、no-silent:3d9c043b→908e87d2/518行)より手前(またはpost-revert追加)。内容は生きているが四目安該当は本文拾い読み未実施ゆえ判じ得ず。 |
| 140 | `574322e1` | canon(division): v1.2 誰がチェックし誰が直すかを明記(理事長ご下問2026-08-06) | **掛かる** | ⑵⑷ | 実読=git show --no-patch 574322e1(全文)。「検める者は直さない・直す者は検めない」「REDは部長も本部長も覆せない」を明文化=事業部内監査独立性原則。当隊の軍師監査義務(CLAUDE.md Audit Obligation節)と同型原則。 |
| 141 | `feb945cf` | canon(division): 事業部構築ルールブック v1.0 — Supabase正本c2e5d0e8のミラー(理事長令2026-08-06) | **掛かる** | ⑴⑷ | 実読=git show --no-patch feb945cf(全文)。事業部構築ルールブックv1.0新設、§4に文脈飽和監督(85%予告/95%注入/100%手遅れ・担当=実行責任者=距離で決める)を新設。当隊CLAUDE.md「飽和自己申告義務」と同一主題の並行規範(理事長令由来同士)。 |

## 3. 読了・母集団の内訳

- 母集団(canon件名一致): **141件**(rev-list全体174件中)
- 全文実読(git show --no-patch/-p でcommit本文まで読了): **11件**=5c2842aa, 4ef49de7, 19f05dfb, 2058bc51, f9c6ddd4, d0c05de0, 574322e1, feb945cf, 292c2c11, b279f777, 1d0e7692
- 件名(subject)読了: **141件/141件(全数)**
- 本文(body)は141件中 **11件を実読、残り130件は拾い読み(file-touch機械判定+checkpoint生存判定による間接推定)**

三値内訳(分母=141):
- 掛かる: **12件** / 141件
- 掛からぬ: **61件** / 141件
- 判じ得ぬ: **68件** / 141件

★分母の無い件数は意味を成さぬ、との指示に基づき全て /141件 を明記した。

## 4. 当隊の二条への抵触チェック(結論)

- 「中継の承認では動かぬ」相当条: **§1-2参照。条文(292c2c11)は5c2842aaで削除されたが、核(機構が拒んだ操作の別経路通過禁)はautonomy-and-restraint.mdに生存。限定/覆しではなく『詳細化が消え骨格が残った』形。**
- 「誰が裁くかの条を裁が下りたと読むな」相当条: **見当たらず(読了範囲内、§1-3のキーワード群に限定した拾い読み)。断定はせぬ。**

## 5. 禁の遵守記録

- 書込・fetch・checkout・reset: 一切為さず(`show`/`log`/`diff`/`rev-parse`/`find`のみ使用)。
- 裁定: 本票は材料提示に徹し、当隊がどう対応すべきかの結論は一切書いていない。
- 人の咎め: 委員長の行動への評価的言及は避け、commit本文の逐語引用に留めた。
- 実装・patch・test実行: 零。