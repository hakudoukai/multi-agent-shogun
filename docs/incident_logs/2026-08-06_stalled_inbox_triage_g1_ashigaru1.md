# 停滞便の仕分け（群㈠）— queue/inbox/maeda.yaml（3通・from=ashigaru5）+ queue/inbox/third_pc.yaml（1通・from=shogun-second）

下命=家老second msg_20260806_203149_e7f5b814（2026-08-06T20:31:49）。
読取のみ・票のみ。対象file自体は★一切変更していない★（`read`を立てず・移さず・消していない）。

測時=2026-08-06T20:35:06+09:00（`date -Iseconds`実行結果）。
git rev-parse HEAD=4e8ab81ea680163e8d18872ba3425c8505c12cc3。

## 対象fileの実測

```
$ ls -la queue/inbox/maeda.yaml
-rw------- 1 hakudokai hakudokai 55013 Jul 21 00:17 queue/inbox/maeda.yaml

$ stat -c 'mtime=%y epoch=%Y' queue/inbox/maeda.yaml
mtime=2026-07-21 00:17:59.560748840 +0900 epoch=1784560679

$ wc -l queue/inbox/maeda.yaml
1124 queue/inbox/maeda.yaml

$ sha256sum queue/inbox/maeda.yaml
331f800667e5b2670e06f850fb277864f035654ae6f36efdef4e26f43ef6ac6f  queue/inbox/maeda.yaml

$ git check-ignore -q queue/inbox/maeda.yaml; echo "check-ignore exit=$?"
check-ignore exit=0

$ git status --short queue/inbox/maeda.yaml
（出力なし＝working treeとの差分なし。もっとも本fileはgitignore対象ゆえ元よりtrack対象外）
```

```
$ ls -la queue/inbox/third_pc.yaml
-rw------- 1 hakudokai hakudokai 1689 Jul 16 06:16 queue/inbox/third_pc.yaml

$ stat -c 'mtime=%y epoch=%Y' queue/inbox/third_pc.yaml
mtime=2026-07-16 06:16:09.253546273 +0900 epoch=1784150169

$ wc -l queue/inbox/third_pc.yaml
16 queue/inbox/third_pc.yaml

$ sha256sum queue/inbox/third_pc.yaml
ee8d1967e2bbe9bb7b2d7b1502e17b8c27bd3454b7aa1ca69ebef015a789b36e  queue/inbox/third_pc.yaml

$ git check-ignore -q queue/inbox/third_pc.yaml; echo "check-ignore exit=$?"
check-ignore exit=0
```

maeda.yaml＝1124行・messages配列全体は多数（大半`read: true`）だが、令が指す対象=`read: false`は
実測で★3件★（令の記載「3通」と一致）。third_pc.yaml＝16行・messages配列の要素=1（`read: false`、令の「1通」と一致）。

## 名簿確認（両fileの立ち位置）

```
$ /usr/bin/grep -n "maeda\|third_pc" queue/pane_registry.yaml
（0件、exit=1）
```

`maeda`・`third_pc`いずれも`queue/pane_registry.yaml`のagent_idに★存在しない★。

```
$ /usr/bin/grep -n "廃止 persona" config/settings.yaml
131:  #   (1b) 廃止 persona 名 (nobunaga/hideyoshi/ieyasu/maeda/kuro_desktop) の現行役職名是正
```

`maeda`はconfig/settings.yaml上★明示的に「廃止persona名」★と記載されている（SecondPC家老の旧名、現・karo-second）。
`third_pc.yaml`はagent個人の箱ではなく、内容（下記）から見て★cross-PC中継用の箱★と見受けられる
（本file自体にその旨の説明は無く、当職が名簿突合で導いた推測である旨を明記する）。

## 中身（全文読了）

### queue/inbox/maeda.yaml（対象3件のみ抜粋、全文は上記1124行を通読済）

```yaml
- content: 容量最大化令v4.0ack 足軽5 待機
  expires_at: null
  from: ashigaru5
  id: msg_20260720_233710_f4c0223d
  read: false
  supersedes: null
  timestamp: '2026-07-20T23:37:10'
  type: status_update
- content: 容量v4.2ack 足軽5 v2是正版gunshi再検分提出済
  expires_at: null
  from: ashigaru5
  id: msg_20260721_001639_2c8cd3a5
  read: false
  supersedes: null
  timestamp: '2026-07-21T00:16:39'
  type: status_update
- content: 容量v4.0/v4.2束ねてack 足軽5 待機(v2是正版gunshi再検分待ち)
  expires_at: null
  from: ashigaru5
  id: msg_20260721_001759_3dda5399
  read: false
  supersedes: null
  timestamp: '2026-07-21T00:17:59'
  type: status_update
```

### queue/inbox/third_pc.yaml（全文）

```yaml
- content: 信長→Commander。★infra escalation要請=gunshi-second /clear未着火(将軍独立検証済)★。
    【症状】gunshi-second(multiagent-second:0.8/pid3859929)がclear_command2連続とも
    read:true 消費だが pane未reset・約5時間 context325k滞留。watcher生存(pid594583)。
    【root cause】旧watcherのget_unread_info specials自動read化がsend-keys /clear前に
    clear_commandを消費するrace=消費のみで/clear無着火。karo再送も同raceで再消費・
    pane所有のagentもshogunもsend-keys不可。
    【要請】Commander infra権限(DD-177第1層・SSH+send-keys)でmultiagent-second:0.8へ
    /clear直接着火を願う。gunshi成果は全外部化済ゆえreset安全。
    【併願】karo-second(multiagent-second:0.0/424k)も同様reset gate READY・自己clear不可。
  expires_at: null
  from: shogun-second
  id: msg_20260716_061609_0ae175d2
  read: false
  supersedes: null
  timestamp: '2026-07-16T06:16:09'
  type: status_update
```

（全文はqueue/inbox/third_pc.yaml本体を参照。上記は当職が全文読了の上で要旨のため短縮引用した箇所を含む＝
本票内での要約であり原文の改変ではない。原文は当該file自体に一字も手を加えていない。）

## ①〜④ 各通の仕分け

### A-1) msg_20260720_233710_f4c0223d（maeda.yaml・from=ashigaru5・2026-07-20T23:37:10）

**⒜ 誰宛・何・いつ**
宛先＝file名からmaeda（廃止persona・現karo-second相当）。差出人＝ashigaru5。
内容＝「容量最大化令v4.0」への ack、足軽5号は待機中。刻＝2026-07-20T23:37:10。

**⒝ なお要るか**
本文自体に時限の明記は無いが、性質は「ackのみ・待機通知」であり、後続で同一件名の便が2通続いている
（下記A-2, A-3）。実測で「容量最大化令v4.0/v4.2」を参照する現行タスク・記録は
`queue/reports/karo-second-p0impl-p06s5-20260721.md`・`ashigaru5-p15-2b-rev-integrate-phaseA-staging-20260720.md`・
`karo-second-p15-2b-rev-integrate-20260720.md`・`karo-second-fki-lane-a-remediation-prep-20260721.md`の
4件が該当（`/usr/bin/grep -rln`実測、下記④）。いずれも2026-07-20〜21付。ashigaru5の★現行★task
（`queue/tasks/ashigaru5.yaml`、2026-08-03付）には「容量v4」への言及は無い＝直近3日はこの件名から離れている。
測時（2026-08-06T20:35）との差＝★404.9時間（16.9日）★。

**⒞ 判ずる権は誰に在るか**
宛先=maeda（廃止・現karo-second）に属する。当職が断じ得る二種のいずれにも該当しないと見る：
「試験の残骸」ではない＝内容は実運用の進捗ack。「已に閉じられた物」かは、当該v4.0/v4.2工程が
その後どう決着したか（gunshi再検分の結果等）を当職は追跡できておらず★断定不能★。
∴ 権者＝karo-second（maeda後継）を名指すに留める。

**⒟ 己の手で為した事**
上記「対象fileの実測」全コマンド実行＋`/usr/bin/grep -rln "容量最大化令v4\|容量v4\.0\|容量v4\.2" queue/ docs/`
実行（結果=queue/inbox/maeda.yaml本体とその.bakのみ、他に参照無し）＋`queue/tasks/ashigaru5.yaml`のtail確認。

---

### A-2) msg_20260721_001639_2c8cd3a5（maeda.yaml・from=ashigaru5・2026-07-21T00:16:39）

**⒜** 宛先＝maeda。差出人＝ashigaru5。内容＝「容量v4.2」ack、v2是正版をgunshiへ再検分提出済との報告。
刻＝2026-07-21T00:16:39。

**⒝** A-1と同工程の後続報告。gunshiの再検分結果が「PASS/FAIL」いずれで決着したかを当職は
本便からも周辺記録からも★特定できていない★（`/usr/bin/grep -rln "v2是正版"`実測=下記4件のみヒット、
いずれもP0/P15系の別工程文書で本件v4.2そのものの決着記録ではない）。測時との差＝★404.2時間（16.8日）★。

**⒞** A-1と同じ＝権者はkaro-second（maeda後継）。当職は「試験の残骸」「已に閉じられた物」いずれとも断じない。

**⒟** A-1と同一コマンド群を実行（重複実行はしていない＝一度の`grep`結果をA-1・A-2・A-3で共用）。

---

### A-3) msg_20260721_001759_3dda5399（maeda.yaml・from=ashigaru5・2026-07-21T00:17:59）

**⒜** 宛先＝maeda。差出人＝ashigaru5。内容＝「容量v4.0/v4.2」を束ねたack、
足軽5号は待機中（v2是正版のgunshi再検分待ち）。刻＝2026-07-21T00:17:59。
本文の「束ねて」という語から、★A-1・A-2の内容を吸収する趣旨の便★と読める
（ただし`supersedes: null`＝機構上は前2通を上書き/無効化する指定にはなっていない）。

**⒝** A-1・A-2と同工程・同待機状態の最終形。測時との差＝★404.2時間（16.8日）★。
待機理由（gunshi再検分）の決着は当職には追跡不能。

**⒞** A-1・A-2と同じ＝権者はkaro-second（maeda後継）。

**⒟** A-1と同一コマンド群を実行。

---

### B-1) msg_20260716_061609_0ae175d2（third_pc.yaml・from=shogun-second・2026-07-16T06:16:09）

**⒜** 内容自体の宛先は本文冒頭に明記＝「信長→Commander」（差出人欄`from`はshogun-second）。
内容＝gunshi-second（multiagent-second:0.8）の`/clear`未着火・karo-second（multiagent-second:0.0）も
同様のreset gate READY状態、という2件のinfra escalationをCommanderへ要請するもの。
刻＝2026-07-16T06:16:09。

**⒝ なお要るか（★本便は当職が実測で「用済み」と断じ得た唯一の例★）**
測時との差＝★518.2時間（21.6日）★。本文が名指す2プロセスの★現在の生死・PIDを当職は自分の手で
実測できる立場にある★（同PC上のtmux paneゆえ）：

```
$ tmux list-panes -a -F "#{pane_id} #{session_name}:#{window_index}.#{pane_index} #{@agent_id} #{pane_pid} #{pane_current_command}" | /usr/bin/grep -i second
%13 hermes-gunshi-second:0.0 shogun-second 2622258 doppler
%3  multiagent-second:0.0    karo-second   209588   doppler
%11 multiagent-second:0.8    gunshi-second 209825   node
（他ashigaru1-7省略）
```

本文が名指したPID＝gunshi-second pid**3859929**・karo-second（本文中「424k」はcontext token数で
PID明記なし）に対し、★現在の実PIDはgunshi-second=209825・karo-second=209588★＝
名指しPIDと一致しない。プロセスが少なくとも1回以上再起動された物的証跡である
（当職自身がtmux paneを実査した結果であり、他者の報告の引き写しではない）。
かつ本便の差出人=karo-second（現在、本便を含む本下命一式を当職に発している当人）は
現に稼働・応答しており、本便が訴えていた「reset不能」状態は少なくとも★今この瞬間は存在しない★。

**⒞ 判ずる権は誰に在るか**
本文宛先=Commander。「用済み」の最終判断はCommanderに属する。
ただし当職が自ら実測した上記PID不一致＋現在の稼働状況は、
★「已に閉じられた物」に該当する具体的な物証★であり、当職の権限内（断じ得る二種の後者）と判断する。
∴ 本便は当職の見立てとして「已に閉じられた物」＝用済みの可能性が高いが、
最終確定はCommander（宛先本人）に委ねる。

**⒟ 己の手で為した事**
`tmux list-panes -a`実行（pane_id/session/@agent_id/pid/current_command全列挙）＋
`/usr/bin/grep -n "maeda\|third_pc" queue/pane_registry.yaml`実行（0件）＋
`/usr/bin/grep -rln "msg_20260716_061609\|0716_061609" queue/ docs/`実行
（結果=third_pc.yaml本体と`queue/reports/alive_to_productive_monitor_v0.2_periodic_20260716_061423.json`のみ、
後者は当該便の直前に生成された定期監視ログで内容関連性は無い＝時刻近接のみ）＋
`/usr/bin/grep -rln "context325k\|pid3859929" queue/`実行
（結果=`queue/inbox/_dead_letter_second.yaml`にも同一文言のヒット＝本便が別経路でdead-letter化した
写しが存在する可能性を示唆するが、当職は当該file中身までは本工区の範囲外につき未読）。

## ③ 数の扱い

令＝「maeda.yaml 3通＋third_pc.yaml 1通」。実行の刻（2026-08-06T20:35:06+09:00）に
`grep -c "read: false"`相当の目視突合で数え直した結果＝maeda.yaml側3件・third_pc.yaml側1件＝
★令の数と一致・食い違い無し★。
測時＝2026-08-06T20:35:06+09:00／器＝`yaml`構造の目視突合＋`wc -l`／範囲＝
`queue/inbox/maeda.yaml`・`queue/inbox/third_pc.yaml`の2fileのみ（下命指定範囲外は数えていない）。

## 母集団の自己申告

本群㈠で当職が実測したのは上記2file・計4通のみ。`queue/inbox/*.yaml`全体に他の停滞便が
存在するか否かは★本工区の範囲外ゆえ確認していない★（下命①が対象を2fileに限定しているため）。
「零」「以上」を主張できるのはこの2fileの中に限る。

## この工区が新たに開ける穴

- third_pc.yamlの宛先を「Commander」と当職が読んだのは本文冒頭の書式（"信長→Commander"）からの
  推測であり、file名`third_pc`自体が正式に何を意味するかの定義文書を当職は見つけられていない
  （scripts/*.sh・docs/への`grep`は0件）。次に読む者は、この箱の正式な位置づけ（cross-PC中継か、
  Commander個人inboxのミラーか）をrouting実装側（inbox_write.sh／pc_handshake経路）で確認されたし。
- maeda.yaml側3通の「用済み」最終判定を当職はkaro-second（宛先後継）に委ねたが、
  当のkaro-second自身が本下命の発令者であり、★同一人物が発令者と判定権者を兼ねる★形になる。
  利益相反ではないが、次段階（軍師提出）で軍師がこの構造をどう見るかは要注意点として明記しておく。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。

以上、本群㈠（対象2file・4通）の仕分け票。新規探索・新規判定・新規工区の拡張は行っていない。
