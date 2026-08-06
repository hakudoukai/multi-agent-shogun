# 『読む者が居らぬ場所に置かれた報せ』全件×判定・queue/配下(inbox/*.yaml除く) (足軽5号、2026-08-06)

## ★境・未測・限界(先に書く)★

- **lane(worktree)には一字も触れておらぬ**。freeze継続と無関係(下命通り)。
- **queue/には一切書込んでおらぬ**——`_dead_letter_second.yaml`は下命の「触れるなの令」に従い**開いておらぬ**
  (存在とsizeのみ本票に記す)。`_unroutable`・`_pending_notice`・`orders`・`packets`・`archive`・`metrics`・`watchers`・
  `tasks`・`reports`はいずれも**読取のみ**(mtime/内容とも無変更)。
- **`queue/reports/`(md 799+yaml 29=828件)・`queue/tasks/`(16件)は個別に全件手読みしておらぬ**——
  下記㈤の理由(既存の読取経路が有ると判じた根拠)を示した上で**未測のまま置く**。
  ⇒ **本票の「全件×判定」は「全ファイルを開いた」ではなく「全カテゴリを類別し、類別の根拠を示した」の意**。
- **iincho・fukuincho・gunshi(第一世代)本人への確認は行っておらぬ**——判ずる権の限界は各節に明記。
- `queue/reports/`は生きて増え続ける母集団(測定中に7212→7216へ増加を実測)——**断面は測時のもの**。

## 測時・断面

```
$ date -Iseconds
2026-08-06T20:48:22+09:00
$ git rev-parse HEAD
a02c00a9fe872aaa05d03749ac2a91d0cd7cafb1
$ git status --short --branch
## feat/dd169-d006-conditional-exception...origin/feat/dd169-d006-conditional-exception [ahead 133]
?? docs/incident_logs/2026-08-06_task_yaml_clear_survival_sweep_a6.md
```
(porcelain上記1行=他工区a6の未提出成果物、本工区に非ず)

## 下命(要約・原文は karo-second msg_20260806_203930_a84ea5da 20:39:30)

端緒=`queue/dead_letter/_pending_notice/shogun-second.log`(将軍second宛・`queue/inbox/`の外・`.log`形式・
鐘鳴らず・箱の測りにも掛からず18時間)。工区=`queue/`配下(`inbox/*.yaml`を除く)に在る**人へ宛てた報せ**を
全件×判定=⒜path/形式/mtime/宛名 ⒝読む経路が在るか(無ければ沈黙と同義) ⒞『書いた事で果たしたとした』
機構を名指せ(機構を咎めよ・人を咎めるな) ⒟己の手で為した事。軍師secondが已に5class立てた既存監査票
(`gunshi_second_queue_message_holding_paths_audit_20260806.md`)は**引くな・己の手で索き直せ**。
禁=書くな・消すな・readを立てるな／`_dead_letter_second.yaml`は開くな(存在とsizeのみ)／lane不触。
数=測時・器・範囲を併記、実行の刻に数え直せ。軍師secondへ監査提出(3行必須)。

## ㈠ 母集団(階ごとに列挙・合算しない)

```
$ for d in archive dead_letter inbox_v2 metrics orders packets reports tasks watchers; do
    n=$(find "queue/$d" -type f 2>/dev/null | wc -l); echo "$d: $n"; done
archive: 1
dead_letter: 13
inbox_v2: 0
metrics: 25
orders: 16
packets: 1
reports: 7216
tasks: 16
watchers: 5

$ find queue/inbox/_archive -type f | wc -l
17    ($1$つは README.md、$1$つは _prune_events.log、残り15は *_pruned.yaml/*_legacy_*.yaml)

$ ls -la queue/inbox/_dead_letter_second.yaml
145585 bytes (★触れるなの令ゆえ開かず・存在とsizeのみ★)
```
測時=2026-08-06T20:48:22／器=`find -type f`・`ls -la`／範囲=`queue/`配下・`inbox/`直下の
`*.yaml`(実agentの生箱・.lock・.bak・.tmp)を除く全ディレクトリ。

## ㈡ 類別(下命が求める「人へ宛てた報せ」か否かを先に分ける)

| 分類 | 対象dir | 母集団 | 「報せ」か | 理由 |
|---|---|---|---|---|
| A 生きた滞留報せ | `dead_letter/_pending_notice` | 1(+lock) | ★是★ | 端緒そのもの |
| B 已に閉じた墓場 | `dead_letter/_unroutable` | 11 | ★是★(処理済) | 己の手で53823cbにて仕分け済(下記㈣) |
| C 令書(orders) | `orders` | 16 | ★是★ | 特定agent/役職名がfilenameに現れる指示文 |
| D 束(packets) | `packets` | 1 | ★是★ | 参照先が在り宛先性を持つ |
| E アーカイブ内の生残骸 | `inbox/_archive` | 17file/32194通(true5348+false26846で計算・下記㈢で内訳訂正) | ★是★(過去分) | 己の手で構造確認、下記㈢参照 |
| F 触れるな対象 | `inbox/_dead_letter_second.yaml` | 1 | 不明(開かず判定不能) | 令により未測のまま |
| G 自己遠隔測定 | `metrics/*_selfwatch.yaml` | 25 | ★非★ | 内容=agent自身のread統計(下記実測)、宛先=当該agent自身の自己観測、「人へ宛てた報せ」の型に非ず |
| H 生存心拍 | `watchers/*.health` | 5 | ★非★ | instructions/honda.md・ieyasu.md に「5分超staleness→自動enable」の読取経路明記済(下命⒝を充足) |
| I task定義 | `tasks/*.yaml` | 16 | ★是★だが読取経路有 | CLAUDE.md「Rebuild state from primary YAML data (queue/, tasks/, reports/)」+ /clear Recovery Step3「Read queue/tasks/{your_id}.yaml」で経路明記済 |
| J 監査/報告成果物 | `reports/*.md`(799)+`*.yaml`(29) | 828 | ★是★だが読取経路有 | CLAUDE.md「軍師: Check queue/reports/ashigaru{N}_report.yaml…when waiting」で経路明記済 |
| K 機械遠隔測定 | `reports/`内 json+sha256(6384)+log(25)+patch/sh/txt/diff/sql等(87) | 6496 | ★非★ | 内容=periodic monitor snapshot・raw test evidence(親mdから参照される付属物)、宛先性なし |
| L 単発スナップショット | `archive/`(top,1) | 1 | ★半(過去)★ | 2026-05-04付、下記実測で単発手動バックアップと判定 |

## ㈢ Eの内訳訂正——「読んだ」を効かせず数だけ見ると過大に成る実例(己で発見)

```
$ /usr/bin/grep -c "read: false" queue/inbox/_archive/*.yaml
_test_cap_rotation_pruned.yaml:0
ashigaru1_pruned.yaml:0 ashigaru2_pruned.yaml:1 ashigaru3_pruned.yaml:0 ashigaru4_pruned.yaml:0
ashigaru5_pruned.yaml:0 ashigaru6_pruned.yaml:0 ashigaru7_pruned.yaml:0
gunshi-second_pruned.yaml:0 honbucho_pruned.yaml:2 karo-second_pruned.yaml:5 shogun-second_pruned.yaml:4
fukuincho_legacy_deadletter_20260702_131339.yaml:25993
gunshi_legacy_generic_20260702_141415.yaml:31
shogun_legacy_generic_20260702_135247.yaml:810
```
**当初この12件(a2=1/honbucho=2/karo-second=5/shogun-second=4)を「アーカイブ内の未読」と読みかけたが、
現物を開いて確認したところ全12件が偽陽性**——`content:`本文が`read: false`という★語そのものを
話題にした一節★(例=`honbucho_pruned.yaml:1449`「msg_..._b240431c read: false ← 本線復帰の令」は
過去のtriage票の引用が本文に埋込まれた物、`karo-second_pruned.yaml:37627`は「grep結果53件で一致」を
論じた一節)であり、**トップレベルYAMLキーとしての`read: false`ではない**。∴ **正規archive(15file中12file)
の実測はfalse=0**。

**残る3file(`*_legacy_*`)は構造を直接開いて確認**——`content:/from:/id:/read:/timestamp:/type:`が
正規messageと同じ並びで実在(下記コマンドで裏取り)。∴ **此処のfalse合計26834件は本物**。
```
$ sed -n '1,10p' queue/inbox/_archive/fukuincho_legacy_deadletter_20260702_131339.yaml
messages:
- content: クロちゃん受領(msg_20260504_184632_b9c39d36)。...
  from: ashigaru8
  id: msg_20260504_184858_c534b802
  read: false
  timestamp: '2026-05-04T18:48:58'
  type: task_clarification
```

> ### **★「read: false」という文字列一致は、正規fieldか本文中の引用かを区別せぬ——開いて構造を見るまでは数に成らぬ★**
> ([[tool-output-is-not-tool-verdict]]の当てはまり——検査(grep -c)自体の的中率を己で検めた)

## ㈣ 各対象・下命の4点

### A `dead_letter/_pending_notice/shogun-second.log`(端緒)

⒜ path=`queue/dead_letter/_pending_notice/shogun-second.log`／形式=`.log`(1行のテキスト、YAML/MDに非ず)／
mtime=2026-08-06T02:02:41／宛名=shogun-second(filename)。内容(己の手で全文Read)=
「FROM不明の便を墓場へ落とした / .../unroutable_20260806_020241_2f3af34c.yaml
(target== from=sha256=44dbeb3e... reason=unroutable_target_and_unresolvable_from)」。

⒝ 読む経路=★無し★。`scripts/inbox_watcher.sh`のinotifywait対象を実査:
```
$ /usr/bin/grep -n "inotifywait.*inbox" scripts/inbox_watcher.sh | head -3
957:    done < <(pgrep -f "inotifywait.*inbox/${AGENT_ID}.yaml" 2>/dev/null)
1641:        inotifywait -q -t "$INOTIFY_TIMEOUT" -e modify -e close_write "$INBOX" 2>/dev/null
```
→ **watcherの監視対象は`inbox/${AGENT_ID}.yaml`一本のみ**、`dead_letter/`配下は構造的に対象外。
CLAUDE.md・instructions/*.mdにも`queue/dead_letter`を定期走査する手順の記載は無い(既に検索済・0件)。
∴ ★沈黙と同義★——鐘が鳴る機構自体が存在せぬ。

⒞ 機構名指し=`scripts/inbox_write.sh`の`_notify_pc_dispatcher_of_unroutable`関数(L385-446)。
```
$ /usr/bin/grep -n "_notify_pc_dispatcher_of_unroutable\|_pending_notice" scripts/inbox_write.sh
385:_notify_pc_dispatcher_of_unroutable() {
394:    local notice_dir="${INBOX_WRITE_DISPATCH_NOTICE_DIR:-$SCRIPT_DIR/queue/dead_letter/_pending_notice}"
```
実装(己の手でRead、L393-427)=不明from便が発生する度にbufferへ1行append、**count≥5枚 または
age≥300秒 の時のみ**その場でflushして`shogun-second`の生inboxへ実便を書く設計。
**flushの引き金は「次にこの関数が呼ばれた時」のみ**——独立のcron/systemd timerは:
```
$ crontab -l 2>/dev/null | /usr/bin/grep -i "inbox_write\|pending_notice\|flush"
(該当0件・crontab自体が未設定)
$ find / -maxdepth 6 -iname "*pending_notice*" -o -iname "*dispatch_notice*" 2>/dev/null | /usr/bin/grep -v queue
(該当0件)
```
**確認=存在せぬ**。∴ **不明from便が1件しか起きなければ、その1件は age≥300秒 を満たす2件目の
不明from便が★偶然★起きるまで永久にbufferの中で待たされる**——本件は2026-08-06T02:02:41から
測時20:48:22まで**約18時間45分**、後続の不明from便が無いままbufferに単独で留まり続けた。

> ### **★『書いた事で果たしたとした』は`_pending_notice`という名の受動的bufferそのもの
> ——flushを次の同種事象に依存させた設計は、事象が疎(まれ)な時ほど沈黙が長引く★**

⒟ 己の手で為した事=`Read`で全文取得、`scripts/inbox_write.sh`をL380-454読取、`grep -n`で
inotifywait対象・pending_notice関連行を特定、`crontab -l`・`find /`で独立flush機構の不在を実査。

### B `dead_letter/_unroutable/*.yaml`(11件)

⒜⒝⒞⒟=**已に閉じられた物**。己の手でcommit実在を確認:
```
$ git show --stat 53823cb 2>&1 | head -5
commit 53823cba49daf6570e36891a20585a690f08cf98
Author: hakudoukai <hakudoukai@gmail.com>
Date:   Thu Aug 6 20:17:17 2026 +0900
    docs(triage): dead_letter/_unroutable 11file=8便の仕分け票=用済み4/発信者判断3/委員長判断3/便に非ず1
    (将軍second令⑦・読取のみfile不変・軍師second PASS 20:15:38)
```
**当職自身の手による過去の成果物**(closed_by=ashigaru5、commit本文に明記)、軍師second PASS済。
本工区の20分前(20:17:17)に完了しており、下命の対象2箱(群㈤)とは別の工区(将軍second令⑦)である。
target内訳(己の手で全11file`grep -E "^(target|from|reason):"`済)=honbucho×6/hermes×3/test_agent×1/
「=」(shell被食い残骸)×1——上記commit本文の内訳(用済み4/発信者判断3/委員長判断3/便に非ず1)と対応。

### C `orders/*.md`(16件)

⒜ 全16件のpath/filename/mtimeを`find`+`stat`で己の手で実測(下記表)。宛名=filenameに現れる
役職/agent名(karo-second/shogun-second/fukuincho)。

⒝ 己の手で全16件について「queue/inbox/配下(生箱+_archive)のいずれかに、その令書のfilenameを
含む便が過去に在ったか」を`grep -rl`で実査:
```
$ for f in queue/orders/*.md; do base=$(basename "$f");
    c=$(/usr/bin/grep -rl "$base" queue/inbox/ 2>/dev/null | wc -l); echo "$base: $c"; done
fukuincho-secondpc-hold-release-work-order-20260715.md: 0
fukuincho-secondpc-residual-repair-work-order-20260715.md: 0
karo-second-secondpc-canon-cure-order-20260803.md: 5
shogun-second-a6-readonly-go-relay-20260721.md: 0
shogun-second-fix3-iincho-ruling-relay-20260721.md: 0
shogun-second-fki-lane-a-order-20260721.md: 1
shogun-second-hermes-leg-fix4-order-20260721.md: 0
shogun-second-hold-release-integration-report-20260715.md: 0
shogun-second-p0-decomp-plan-order-20260720.md: 0
shogun-second-p0-impl-draft-launch-order-20260721.md: 0
shogun-second-p0-onesha-fix1-order-20260721.md: 0
shogun-second-p0-onesha-order-20260721.md: 0
shogun-second-p15-2b-integrity-design-revision-order-20260720.md: 0
shogun-second-residual-repair-integration-report-20260715.md: 0
shogun-second-selfcheck-guard-order-20260721.md: 0
shogun-second-stale-detector-minext-order-20260721.md: 1
```
**16件中13件、filenameを引いたinbox便が(生箱・archive通じて)0件**。CLAUDE.md・instructions/*.mdにも
`queue/orders/`を定期走査する手順の記載は無い(検索済・0件)。∴ **13件は⒝の意味で読む経路が
確認できず**(=令書の発行それ自体が「果たした」の代わりに使われた可能性が在る、が下記限界参照)。
残3件(canon-cure=5・fki-lane-a=1・stale-detector-minext=1)は経路確認済。

⒞ 機構名指し=**「令書をfileとして`queue/orders/`へ置くこと」自体を、下命内容の伝達完了と
同一視する運用慣行**(inboxへの明示pointer送付を必須手順として強制する機構が存在せぬ)。
但し★これは断定ではない★——13件のうち何件が「口頭/tmux send-keys等inbox以外の経路で
既に伝達済」かは、当職の器(`grep -rl` inbox限定)では判定できぬ(下記限界)。

⒟ 己の手で為した事=16件全てを`find`+`stat`で列挙、16件全てについて`grep -rl`をinbox全体
(生箱17+archive17=34file)に対し個別実行、結果を上記表としてそのまま提示(要約に頼らず)。

**★限界★**: orders/16件は日付が2026-07-15〜08-03(3週間以上前)であり、その大半(13件)は
「未読」ではなく「作られた当時のtmux直接投入や口頭経由で已に消化され、inbox pointerを
経由しなかっただけ」の可能性が高い——特に`shogun-second-hold-release-integration-report`
`shogun-second-residual-repair-integration-report`はfilenameが「integration-report」であり
★令書ではなく完了報告の控え★の可能性が在る(内容までは今回読んでおらぬ・未測)。
∴ **本票は「orders 13件=inbox pointer 0件」という★構造上の事実★のみを報告し、
「13件が今なお未対応」とは断定しない**(⒞と同じ理由——判ずる権は各令の発令者に在る)。

### D `packets/image-27routes-source-packet-20260804.md`

⒝ 読む経路=有り(`grep -rl`でinbox内6file参照を確認)。∴ 本票の対象外(下命①⒝「なお要るか」の
判定基準に照らし、読む経路が現に有るため「沈黙」に該当せぬ)。

### E `inbox/_archive/`内legacy 3file(合計26834件・read:false)

⒜ path=`queue/inbox/_archive/fukuincho_legacy_deadletter_20260702_131339.yaml`(227133行・
25993件false)+`shogun_legacy_generic_20260702_135247.yaml`(6180行・810件false)+
`gunshi_legacy_generic_20260702_141415.yaml`(568行・31件false)。形式=multi-document YAML
(README.md注記の通り)。mtime=file自体は2026-07-02付与だが、内包するmessage群のtimestampは
下記の通り分散。宛名=filenameの人物(fukuincho/shogun/gunshi=いずれも★現存する役職★、
CLAUDE.md本文に現行節が在り(fukuincho)、`queue/inbox/gunshi.yaml`・`shogun.yaml`も現存)。

```
$ /usr/bin/grep "^\s*timestamp:" .../fukuincho_legacy_deadletter_....yaml | head -1
  timestamp: '2026-05-04T18:48:58'
$ ...| tail -1
  timestamp: '2026-07-02T07:13:56'
$ /usr/bin/grep "^\s*type:" .../fukuincho_legacy_....yaml | sort | uniq -c | sort -rn | head -3
  25978   type: shogun_report
      8   type: report_received
      4   type: answer
$ /usr/bin/grep "^\s*from:" .../fukuincho_legacy_....yaml | sort | uniq -c | sort -rn | head -4
   6998   from: main_pc
   6522   from: commander
   6298   from: second_pc
   5863   from: third_pc
```
(shogun_legacy: timestamp 2026-05-07〜07-01、type上位=audit_missing 770/status_update 17。
 gunshi_legacy: timestamp 2026-05-04〜07-01、type上位=report_received 18/audit_request 8、
 from=ashigaru2/5/6/7/8・maeda・fukuinchoなど★実agent発★も含む)

⒝ 読む経路=★無し★。この3fileは`queue/inbox/_archive/_prune_events.log`(通常のcap-rotation記録、
2026-08-06分のみ記録・己の手で`tail -20`確認済)に一切登場せぬ——**通常の自動アーカイブ経路とは
別筋(2026-07-02付の一括移行/過去dead-letter取込みと推定)**。README.md(己の手でRead)は
「multi-doc YAMLの正しい読み方」のみ記し、「誰が・いつ・何のためにこの3fileを読むか」の
手順は記載無し。CLAUDE.md・instructions/*.mdにも該当無し。∴ 沈黙と同義。

⒞ 機構名指し=**cap-rotation機構(README.md記載の正規archiveフロー)とは別に、2026-07-02前後に
実施された過去dead-letterの一括取込み(legacy import)**——取込み自体が「保存した事」を
「対応した事・以後誰かが読む事」と同一視した形跡(取込み後の読取経路が一切設計されておらぬ)。
但し★取込みを行った主体・意図は当職の器では追跡不能(未測・以上)★。

⒟ 己の手で為した事=17file全てに`grep -c "read: false/true"`を実行(内訳㈢参照)、偽陽性12件を
`sed -n`で個別に開いて本文が引用である事を確認、legacy3fileは構造を`sed -n '1,20p'`で直接検分し
正規messageと同じfield並びである事を確認、`from:`/`type:`/`timestamp:`の分布を各fileごとに実測、
`_prune_events.log`の`tail -20`でこの3fileが通常経路に登場せぬ事を確認。

**★限界(重い)★**: 26834件は★個別に手読みしておらぬ★(母集団が桁違い、㈠と同型の限界)。
type分布(shogun_report 99.9%・audit_missing大半)から**大部分が人間向けの個別対応を要する
文面ではなく自動監視の定型通知と推定**されるが、これは★推定であり全数確認ではない★。
timestamp最新が2026-07-02である事から、**2026-07-02以降に稼働体制が変わった可能性**
(gunshi→gunshi-second、当PC全体のSecondPC化等、既知の経緯と符合)があり、
**現に「読むはずだった者」がもう存在しない(体制交代で宛先自体が消滅)可能性も排除できぬ**
——これも当職の器では判定不能、権者(iincho/fukuincho本人)に残す。

### F `inbox/_dead_letter_second.yaml`

⒜ path=`queue/inbox/_dead_letter_second.yaml`／size=145585 bytes(己の手で`ls -la`のみ実行、
中身は★開いておらぬ★=下命の禁則遵守)。

⒝⒞⒟=判定不能。**開かずに判定するのは、この一件に限り下命が明示的に求めた形**
(「存在とsizeのみ記せ」)——∴ 未測のまま置く事自体が正しき従い方(過去のkaro-second/
shogun-second便でも同fileは「ParserError・当職も同じく読み得申さぬ」「未測のまま置き申す」と
扱われている=己の判断ではなく既定の扱いを踏襲)。

## ㈤ G〜Kが対象外である理由(己の手で確認・下命が求める形=引くな索き直せに従う)

- **G(metrics/)**: `ashigaru5_selfwatch.yaml`を己の手でRead(head -8)。フィールド=
  `agent_id/timestamp/unread_latency_sec/read_count/bytes_read/estimated_tokens`——
  **当該agent自身が己の受信状況を記録した自己観測ログ**であり、「他者が誰かへ宛てた報せ」の
  型に該当せぬ。全25file、命名規則(`<agent>_selfwatch.yaml`)が一様である事を`find -printf`で確認。
- **H(watchers/)**: `instructions/honda.md`・`instructions/ieyasu.md`に`queue/watchers/<agent>.health`
  staleness 5分超で自動enableする記載を`grep -n`で発見・引用(下命が引用を要求する形に従い
  該当行番号を明記=`honda.md:285`・`ieyasu.md:82`)。読む経路(自動判定)が明文で存在する。
- **I(tasks/)**: CLAUDE.mdを`grep -n`で実査、L110「Rebuild state from primary YAML data
  (queue/, tasks/, reports/)」を発見。加えて`/clear` Recovery手順Step3にも明記
  (既存CLAUDE.md本文に現存、本票冒頭のsystem-reminderで確認可)。
  但し2件の異例=`rh_blocked_note_20260706.yaml`(実agent名に非ず、GO待ちblocker、
  己の手でcat確認=理事長GO待ちである事を既に自己申告済の生きた記録)と
  `karo-second.yaml.historical_maeda_import_removed_20260702083328`
  (filename自体が「removed」=已に閉じられた歴史片、5行、maeda旧state)——
  **2件とも既に自己の状態を明示しており「沈黙」ではない**。
- **J(reports/md+yaml)**: CLAUDE.md「軍師: Check queue/reports/ashigaru{N}_report.yaml and
  queue/reports/gunshi_report.yaml when waiting」を`grep`で確認(将軍 Mandatory Rules §3)。
  828件は個別に手読みしておらぬ(★未測・以上★)——但し経路の有無は制度として確認済。
- **K(reports/内機械遠隔測定)**: 拡張子分布を実測(`sha256`3163/`json`3141=periodic monitor、
  `log`25=raw evidence)。ファイル名`alive_to_productive_monitor_v0.2_periodic_*`は
  既知の欠陥持ち監視artifact(当職の既存memoryに「グローバルartifact汚染で偽陽性化」の記録有)——
  ★これは今回新たに検証した事ではなく既知情報の援用★と明記する。
- **L(archive/top,1)**: `queue/archive/inbox_ashigaru8_20260504234639.yaml`を己の手でhead確認、
  23行・2026-05-04付・JSON埋込のtask配信記録1件——単発の手動backupと推定(命名規則が
  cap-rotationの`_pruned.yaml`と異なる)。★推定であり断定はせぬ★。

## ㈥ 三値まとめ

| 対象 | ⒝読む経路 | ⒞機構 | 判定 |
|---|---|---|---|
| A `_pending_notice/shogun-second.log` 1件 | 無し(実査済) | `_notify_pc_dispatcher_of_unroutable`のreactive flush(独立timer不在を実査済) | ★沈黙と同義・18時間45分滞留中★ |
| B `_unroutable/` 11件 | (処理済ゆえ不問) | ― | ★已に閉じられた物(53823cb・PASS済)★ |
| C `orders/` 13件(16中) | 未確認(inbox pointer 0件) | 令書file化=伝達完了と同一視する運用慣行(推定) | ㈢判じ得ぬ(要=発令者への確認、当職権限外) |
| C `orders/` 3件(16中) | 有り(inbox pointer確認済) | ― | 該当せぬ |
| D `packets/` 1件 | 有り | ― | 該当せぬ |
| E `_archive/`legacy 26834件 | 無し(実査済) | 2026-07-02一括legacy取込み(取込み後の読取経路未設計、主体は未測) | ★沈黙と同義・個別内容は未測(推定=大半が自動定型通知)★ |
| E `_archive/`正規12件 | (該当せぬ) | ― | ★偽陽性(本文中の引用・トップレベルfieldに非ず)★ |
| F `_dead_letter_second.yaml` | 判定不能(開かず) | ― | 未測(令により意図的) |
| G/H/I/J/K/L | 有り、または「報せ」の型に非ず | ― | 該当せぬ(㈤根拠済) |

## 【本工区で己が直した誤り】

**当初`inbox/_archive`内の12件("read: false")を「未読の滞留」として数えかけたが、
現物を`sed -n`で開いて全12件が本文中の引用(偽陽性)である事を確認し、㈢節で訂正した**
(下命⑤「引くな索き直せ」の精神を己のgrep結果自体にも当てた)。これは提出前の自己点検で
発見・訂正した物であり、提出後の訂正ではない。

## この工区が新たに開ける穴

- **legacy 26834件の個別内容は未測**——「大半は自動定型通知」は推定であり、この中に
  当時の実agent(ashigaru2/5/6/7/8・maeda)発の★人間が書いた実質的な報せ★が混在する事は
  `from:`分布で確認済(僅少だが0ではない)。この僅少分を特定する追加工区が要る可能性。
- **orders 13件の伝達実態(口頭/tmux直接投入で已に消化済か、真に孤立か)は当職の器では
  分からぬ**——inbox pointerの有無のみを実測し、それ以上の断定を避けた。
- **G(metrics)・H(watchers)は「読む経路が有る」と判じたが、其の経路が現に機能しているか
  (staleness検知が実際に走っているか)までは検証しておらぬ**——設計の存在≠稼働の証跡。

## 対に成る他工区

- `queue/reports/gunshi_second_queue_message_holding_paths_audit_20260806.md`(軍師second、
  既存5class監査票——★本票は之を引かず己の手で索き直した★。事後に照合されたし)
- `queue/orders/karo-second-secondpc-canon-cure-order-20260803.md` §28(cap-rotation根治の一次記録)
- commit `53823cb`(当職、dead_letter/_unroutable既済triage)
- 群㈠〜㈣・㈥(他足軽が並行担当、本票の範囲外)

## 監査体制

暫定二者制(Codex leg停止中、SAFETY裁定seq132707)。軍師secondへ本票を監査提出する。

## 各主張の検め直し方(軍師second向け)

- 同意を探すな、潰しに掛かれ。
- ㈠母集団の各数(archive17/dead_letter13/orders16/packets1/reports7216/tasks16/metrics25/watchers5)は
  `find`をそのまま再実行して照合されたし。
- ㈢の「12件偽陽性」は`sed -n`で該当行番号(例=`karo-second_pruned.yaml:37627`)を直接開き、
  トップレベルfieldでなく引用である事を目で確認されたし。
- ㈣Aの「独立flush機構なし」は`crontab -l`と`scripts/inbox_write.sh`のL385-446を己の手で
  再読し、当職の読解(reactiveのみ・独立timer無し)が正しいか判じられたし。
- ㈣Cの「orders 13件0参照」は`grep -rl`をqueue/inbox/全体に再実行し、当職の数と一致するか
  確認されたし——この主張は当職の語の引用ではなく、当職が示したcommand自体の再実行で
  検められる形にしてある。
- 被監査者(当職)の語を引いて『成立』と書くな——引くなら己が引き直したと明記せよ。

## 禁則遵守の申告

- lane(worktree)不触=履行。
- `queue/`への書込み=無し(全て読取のみ)。`_dead_letter_second.yaml`=未開封(存在・size明記のみ)。
- `_unroutable`・`_pending_notice`・`orders`・`archive`・`inbox/_archive`のいずれも移動・削除・
  `read`変更を行っておらぬ。
- hakudokai-devへの実装・commit・push・secret/患者情報の出力=無し。
