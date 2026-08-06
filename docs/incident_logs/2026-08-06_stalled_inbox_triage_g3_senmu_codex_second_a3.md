# 停滞便の仕分け（群㈢）— queue/inbox/senmu_codex_second.yaml（専務）

下命=家老second msg_20260806_203150_4652c1dd（2026-08-06T20:31:50）。
読取のみ・票のみ。対象file自体は★一切変更していない★（`read`を立てず・移さず・消していない）。

測時=2026-08-06T20:35:20+09:00（`date -Iseconds`実行結果）。
git rev-parse HEAD=4e8ab81ea680163e8d18872ba3425c8505c12cc3。

## 対象fileの実測

```
$ ls -la queue/inbox/senmu_codex_second.yaml
-rw------- 1 hakudokai hakudokai 11328 Aug  4 10:25 queue/inbox/senmu_codex_second.yaml

$ stat -c 'mtime=%y epoch=%Y' queue/inbox/senmu_codex_second.yaml
mtime=2026-08-04 10:25:22.053385233 +0900 epoch=1785806722

$ wc -l queue/inbox/senmu_codex_second.yaml
115 queue/inbox/senmu_codex_second.yaml

$ sha256sum queue/inbox/senmu_codex_second.yaml
8157e285f6c62c7058e0d0a51164dd44bae82632eeabaaa8357f5faa4fb016be  queue/inbox/senmu_codex_second.yaml

$ git check-ignore -q queue/inbox/senmu_codex_second.yaml; echo "check-ignore exit=$?"
check-ignore exit=0

$ git status --short queue/inbox/senmu_codex_second.yaml
（無出力＝tracked差分なし。queue/はgit管理外の運用領域）
```

messages配列の要素数=7（実測、下記③参照）。うち`read: false`＝2件（下命の「2通」と一致・食い違い無し）。

## 名簿確認（宛先の裏付け）

```
$ /usr/bin/grep -n "senmu" queue/pane_registry.yaml; echo "exit=$?"
exit=1

$ /usr/bin/grep -ni "senmu\|専務" queue/pane_registry.yaml; echo "exit=$?"
exit=1
```

`senmu_codex_second`という agent_id は`queue/pane_registry.yaml`に★存在しない★（0件）。
ただし、これは a6 が群㈥で扱った`ashigaru-second-1`（名簿に痕跡すら無い孤児箱）とは事情が異なる。
下記の通り、複数の上位agent（委員長・家老second・軍師second）が本箱を「専務殿の箱」として明示的に参照・言及している証跡が別fileに残っている：

```
$ /usr/bin/grep -rl "senmu_codex_second\|専務" queue/inbox/_archive/*.yaml 2>/dev/null
queue/inbox/_archive/honbucho_pruned.yaml
queue/inbox/_archive/shogun-second_pruned.yaml
queue/inbox/_archive/gunshi-second_pruned.yaml
```

∴ 本箱は「名簿には無いが、運用上は実体を持つ役職（専務）の到達先として周知されている」と見る。
「探索範囲に無い」＝「存在しない」ではない、という下命前段の教訓（W32系）と同型。

## 中身（対象2件・全文読了）

対象は`read: false`の2件のみ（他5件は既読・下命の対象外）。

### 便A — id=msg_20260803_201317_bb08653e

```yaml
from: honbucho
type: answer
timestamp: '2026-08-03T20:13:17'
content: |
  nonce=ADS-MEAS-GRILL-20260803-Q4
  A=条件付き採用。PAGE_VIEW/MANY_PER_CLICKは閲覧量であり予約成果ではないため、自動入札の価値信号にしない。
  実在する予約完了だけをBOOK_APPOINTMENT/ONE_PER_CLICKのPrimary候補とし、7478897886は削除せずSecondary観測・履歴保全とする。
  直近main=0/All=38から、まず現状のPrimary/Secondaryとcampaign goalへの包含を実読し、既にSecondaryなら不要変更とする。
  切替前ゲート: ①予約成功条件と完了画面/API成功の対応確認、②実機テスト予約で成功時のみ1回発火、
  ③リロード/戻る/失敗/取消で重複・誤発火なし、④Ads actionのID/category/counting/value/attributionとタグ供給元を実読、
  ⑤予約台帳の匿名集計と日別件数一致、⑥変更前goal構成・入札依存を保存。
  並行観察は新BOOK_APPOINTMENTをSecondaryで最低2週間（曜日差を2巡）かつ観測された実予約を全件匿名集計で照合し、
  偽陽性0・重複0を満たすまで延長する。固定件数をGoogle公式閾値とは扱わず、安定前は入札・予算を変えない。
  ロールバック条件: 未発火、予約前発火、重複、台帳との説明不能な乖離、Primary切替後のCV急減/異常。
  新actionをSecondaryへ戻し、変更前goal構成へ復元するが、PAGE_VIEWを成果Primaryへ戻すのではなく入札変更を止めて上申する。今回は変更なし。
```

#### ⒜ 誰宛・何・いつ

- 宛先＝本文フォーマット（`nonce=ADS-MEAS-GRILL-20260803-Q4`冒頭）から、専務が本部長へ発した「グリル第4問」への回答と特定できる（下記裏付け参照）。
- 差出人＝`honbucho`（本部長）
- 内容＝Google Ads計測（BOOK_APPOINTMENT/ONE_PER_CLICKへのPrimary候補化）に関する条件付き採用回答。切替前ゲート6点・並行観察最低2週間・ロールバック条件を含む。「今回は変更なし」と明記＝この回答自体は設定変更を伴わない。
- id＝`msg_20260803_201317_bb08653e`
- 刻＝2026-08-03T20:13:17（JST）

裏付け（他fileでの言及）:
```
$ /usr/bin/grep -n -B3 -A3 "ADS-MEAS-GRILL-20260803-Q4" queue/inbox/_archive/honbucho_pruned.yaml
（専務→本部長の原問い、176-188行目。「グリル第4問・照葉院CV定義・本番変更禁止」「回答先: SecondPCローカルinbox senmu_codex_second、type=answer、from=honbucho」の指定あり）

$ /usr/bin/grep -n -B3 -A3 "ADS-MEAS-GRILL-20260803-Q4" queue/inbox/_dead_letter_second.yaml
（委員長→本部長 の別便が196-199行目に在り、「貴職が本日20:13に発した nonce=...の裁定回答が、SecondPCローカルのsenmu_codex_second mailboxに★未読のまま滞留★していることが将軍secondの機械走査で判明した(75分超)」と記録）
```

∴ 本便は★委員長自身が75分超の滞留を既に問題視した実績のある便★であり、その後も未読のまま72時間超が経過していることが今回の実測で確認された。

#### ⒝ なお要るか

- 本文中に明示の時限は無い（`expires_at: null`）。
- ただし内容は「今回は変更なし」という★候補提示のみ★の回答であり、実際の設定切替には至っていない。実務上の緊急性を持つ指示（即応対応が必要な障害通知等）ではなく、専務が次に踏む一手（切替前ゲート6点の実読・並行観察の起点）の前提として今も参照価値がある。
- 「並行観察は最低2週間」という条件は、専務が実際に切替に着手した時点を起点とする将来条件であり、本便自体の有効期限を意味しない。
- ∴ 時限切れによる「用済み」の根拠は本文には無い。★内容の有効性は判定不能ではなく、内容面では「今も生きている」と見立てられる★が、専務側で既に着手・処理済かどうかは当職には確認できない（次項参照）。

#### ⒞ 判ずる権は誰に在るか

「用済み」と断ずる権は★受け取るはずだった者★に属する＝本便の場合`senmu_codex_second`（専務）。
当職が断じ得る二種のいずれにも該当しないと見る：
- 「試験の残骸」ではない＝本部長からの実質的な業務回答（広告計測方針）であり、ダミー文言・テストタグ等の痕跡は無い。
- 「已に閉じられた物」かどうかは当職には判定不能＝専務が既にこの回答を読んで着手済か、あるいは別経路（別PC等）で既に処理済かを示す情報を当職は持たない。委員長便（75分超滞留の指摘）はこの便が★少なくとも一度は未読のまま長時間放置された★ことの証拠だが、その後読まれたかは別問題であり、本file上は`read: false`のまま。

∴ ★判ずる権は当職には無い★。権者＝`senmu_codex_second`（専務）本人。委員長も既に一度関心を示しているため、次点の関係者として名指せる。

#### ⒟ 己の手で為した事

- `python3`+`yaml.safe_load`で対象fileを解析し、`read: false`の2件を特定
- `/usr/bin/grep -rl "ADS-MEAS-GRILL-20260803-Q4"`をrepo全体で実行し、原問い（honbucho_pruned.yaml）と委員長の滞留指摘便（_dead_letter_second.yaml）を発見
- `/usr/bin/grep -n -B3 -A3`で該当箇所の前後文脈を実際に読了
- Python `datetime`で測時との差分を計算＝72.3675時間（下記④参照）

---

### 便B — id=msg_20260804_102522_50786067

```yaml
from: honbucho
type: notification
timestamp: '2026-08-04T10:25:22'
content: |
  【本部長→専務／委員長裁定中継】source_seq=137991 nonce=HONBUCHO-RELAY-137991-20260804-01。
  経路障害迂回のため、委員長裁定をexactly onceで中継します。
  ①owner配置=C採用、発効=seq137961時刻。患者アプリowner=shogun-main、画像owner=shogun-second、
    共有auth core owner=常務(Macレーン)、統合責任=専務。reviewer=gunshi-second、必要時hermes3。
  ②画像security REDは委員長から将軍secondへ正規発令済(seq137973)。専務P0A/P0A-1/P0A-2/UX spec/C1A packetを
    入力資料として渡し、将軍second隊が独立検証後に使用。
  ③storage Q1(seq137981)=YES条件付き。Cycle1 scopeは暗号化root 1か所固定、既存images.id/thumbnail/midsize再利用、
    staff same-clinic配信のみ先行。患者アプリ配信/original/動画/Perio OCR/Tooth Vision外部送信/新規汎用asset表はOFF。
    exact rootは候補と要件を受け委員長が最終決定。storage owner=将軍second、証明owner=gunshi-second。
    done_whenにrawパス直参照が全経路で不能のnegative test必須。患者アプリ配信ON時は常務の共有auth coreへ接続。
  ④material progress 1-3（deny matrix/P0A/BYTES/C1A-G各SHA）受領済。実装はclean isolated origin/main worktree必須、
    runtime DB read-only preflight後、という専務前提も承認。
  受領したらnonceを引用して本部長へACK願います。
```

#### ⒜ 誰宛・何・いつ

- 宛先＝本文冒頭「【本部長→専務／委員長裁定中継】」の明記により専務（本箱）。
- 差出人＝`honbucho`（本部長、委員長裁定の中継者）
- 内容＝委員長裁定の中継4点（owner配置C採用／画像security RED発令済／storage Q1 YES条件付き／material progress受領済）。末尾で「nonceを引用して本部長へACK」を明示的に要求。
- id＝`msg_20260804_102522_50786067`
- 刻＝2026-08-04T10:25:22（JST）

#### ⒝ なお要るか

- 本文にACK要求はあるが、期限（時刻）の明記は無い。
- ★内容の実体は既に他経路で執行が進んでいる★ことを確認した：
```
$ /usr/bin/grep -n -B3 -A5 "137991" queue/inbox/_archive/gunshi-second_pruned.yaml
（1016-1024行目：「W70 (画像API security RED) の DRAFT 6件が本日中に貴殿の監査へ回り申す。reviewer=gunshi-second
と委員長裁定にて指名されており申す (本部長便 seq137991 経由)」と、seq137991の内容②(reviewer指名)が
既に別経路で実行に移されていることが確認できる）

$ /usr/bin/grep -n -B3 -A5 "137991" queue/inbox/_archive/shogun-second_pruned.yaml
（991-999行目：将軍second配下が「queue/inbox/senmu_codex_second.yaml に本部長殿の中継便
(seq137991・nonce HONBUCHO-RELAY-137991-20260804-01) が未読のまま在り申した」と2026-08-04時点で
既に検出・報告していた記録が在る。「当該便は末尾で nonce を引用して本部長へ ACK されたし と求めております」
とACK要求も把握済。同便は「当職は専務殿の箱へ1便も書込んでおりませぬ（他者の箱への書込はそれ自体が
cap を進める破壊行為ゆえ）」と自制し、判断を将軍殿に委ねる形で終わっている）
```
- ∴ 裁定の★内容（owner配置・security・storage方針）は既に他系統で実行段階に入っている★が、本便が求める「専務→本部長へのACK」という★手続き自体★は、少なくとも将軍second配下が検出した2026-08-04時点から、当職が今回検出した2026-08-06T20:35時点まで、一貫して未達のまま残っている（当職が探した範囲＝上記2fileでは、ACK送信の記録は見つからなかった）。
- これは「用済み」ではなく★「内容は追いついたが、要求された手続き（ACK）だけが未処理のまま取り残されている」★という、他の2区分（試験の残骸／已に閉じられた物）とも異なる第三の状態と見る。二値には倒さない。

#### ⒞ 判ずる権は誰に在るか

「用済み」と断ずる権は★受け取るはずだった者★に属する＝本便の場合`senmu_codex_second`（専務）。
本便は「試験の残骸」でも「已に閉じられた物」でもない（上記の通り、内容は生きて別経路で執行中）ため、当職が断じ得る二種のいずれにも該当しない。
∴ ★判ずる権は当職には無い★。権者＝`senmu_codex_second`（専務）本人。ACKの督促先という意味では`honbucho`（本部長）も次点の関係者として名指せる。

#### ⒟ 己の手で為した事

- `python3`+`yaml.safe_load`で対象fileを解析
- `/usr/bin/grep -rl "HONBUCHO-RELAY-137991-20260804-01"`および`/usr/bin/grep -rl "137991"`をrepo全体で実行
- `queue/inbox/_archive/gunshi-second_pruned.yaml`と`queue/inbox/_archive/shogun-second_pruned.yaml`の該当箇所を`grep -n -B3 -A5`で実際に読了し、内容の執行状況とACK未達の既往検出記録を確認
- ACK送信の痕跡を上記2fileの範囲で探索（見つからず＝「探した範囲では見つからず」であり「無い」の断定はしない）
- Python `datetime`で測時との差分を計算＝58.1661時間（下記④参照）

## ③ 数の扱い

令＝「2通（58〜72.3h・from=honbucho）」。実行の刻（2026-08-06T20:35:20+09:00）に`yaml.safe_load`で数え直した結果＝
- `messages`配列の要素数=7（全体）
- `read: false`の要素数=2（対象。両件とも`from: honbucho`で一致）
- 実測経過時間＝72.3675h（便A）／58.1661h（便B）＝令の「58〜72.3h」の範囲と★一致（食い違い無し）★

測時＝2026-08-06T20:35:20+09:00／器＝`yaml.safe_load`+Python `datetime`／範囲＝`queue/inbox/senmu_codex_second.yaml`単体。

## ④ 経過時間の実測方法（Pythonソース）

```python
from datetime import datetime, timezone, timedelta
jst = timezone(timedelta(hours=9))
now = datetime(2026,8,6,20,35,20, tzinfo=jst)
t_a = datetime(2026,8,3,20,13,17, tzinfo=jst)  # 便A msg_20260803_201317_bb08653e
t_b = datetime(2026,8,4,10,25,22, tzinfo=jst)  # 便B msg_20260804_102522_50786067
# 便A: delta_seconds=260523.0 delta_hours=72.3675
# 便B: delta_seconds=209398.0 delta_hours=58.166111111111114
```

## 己の弱み（先に書く・咎に用いぬ約定に基づく）

- 便Bの「ACK未達」は当職が探した2file（gunshi-second_pruned.yaml, shogun-second_pruned.yaml）の範囲内での不在確認に過ぎない。専務側のsent-mail的な記録（もし存在すれば）や、本部長側の受信箱（`queue/inbox/honbucho.yaml`）そのものは、専務からのACK有無を直接確認する最良の場所だったが、当職は`honbucho.yaml`本文全体までは読了していない（下命の対象外＝他人の箱を書くなの制約下で読取に留めたが、読取さえも本件対象file以外は最小限とした）。★「ACK未達」は当職の探索範囲内での所見であり、断定ではない★。
- 便Aの「内容面では今も生きている」という見立ても、専務が既に着手・完了させた可能性を排除する直接証拠は持たない（委員長の滞留指摘は2026-08-03時点の一度きりの観測であり、その後の専務側の動きは当職には不可視）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。

以上、本群㈢（対象2通）の仕分け票。新規探索・新規判定・新規工区の拡張は行っていない。
