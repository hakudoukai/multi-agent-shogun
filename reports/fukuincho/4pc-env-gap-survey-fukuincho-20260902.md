# 4PC環境差調査（監督独立測定）

- 発令: `seq234964`
- 基準: 2026-09-02 08:16–08:4x JST
- 独立性: Commanderとの相談・成果参照なし
- 方法: third/secondは同一read-only probe、mainはSSHで小さいread-onlyコマンド、Macは既存正本・実測報を使用。測れない値はUNMEASURED。
- mutation: 設定変更・restart・停止・secret読取=0
- Raw:
  - third `/tmp/fukuincho-env-third2.json` SHA `56abcd75f5fa8211e4c89198f39baf300a21172b2c387c7b2ea419ea6ae4ee1c`
  - second `/tmp/fukuincho-env-second.json` SHA `aa93c96d1065c27c69aa1203f2f34a9fa7ca96522f5c1882d7ac353e08cb510f`
  - Mac直SSH: main経由hostname `mac` はDNS解決不能。直接値はUNMEASURED。

## 重要差一覧

| # | 比較 | third実測 | 他PC実測 | 重要性 | 可逆な解決提案（未実行） |
|---|---|---|---|---|---|
| 1 | WSL interop | third=`yes` | main=`no`; second=`yes`; Mac=N/A | mainは`cmd.exe`/Task Scheduler APIを使えずwatchdog検分がB4化 | mainのWSLInterop登録状態を人間/環境ownerがread-only診断し、復旧は別GO。Windows側collectorを正規化 |
| 2 | repo位置 | third=`/home/hakudoukai/multi-agent-shogun` | main=`/mnt/c/Users/user/projects/multi-agent-shogun`; second=`/home/hakudokai/multi-agent-shogun` | `/mnt/c`は権限・性能・path表記差、成果共有失敗の原因 | PC別`REPO_ROOT`を正本化し、便に絶対path+PCを必須化 |
| 3 | repo HEAD | third=`5 commits ahead`の別branch（開始時snapshot） | second=`ca2bc2a...`, branch main; main HEADはprobe timeoutでUNMEASURED | source/configの同一名異版が起きる | 変更前に`HEAD/branch/path`三点readbackを必須化。配布はdiffで行い丸ごと上書き禁止 |
| 4 | tmux席数 | third=16 panes | main=12 panes; second=11 panes; Mac=UNMEASURED | 母数不一致で巡回・coverageがずれる | 役職母数をPC別registryから生成し、固定10席/33席等の用途を分離 |
| 5 | Hermes CLI PATH | third=venv内`hermes`あり | main=`command -v hermes`空; second=PATH空だがrun/current実体あり | dispatch/canaryがlogin shellで127になる | launcherでvenv/binを絶対指定。PATH依存を禁止するcanaryを追加 |
| 6 | Kanban config実体 | third=7 config PASS | main=4、second=3、Mac=3; Mac残7はpath不存在B4 | dispatcher展開coverageに直接影響 | 新規configを勝手に作らず、自然respawn対象の実在Hermes席だけに1席ずつ装着 |
| 7 | Kanban値の明示 | thirdは`dispatch=true/60/auto=false`をconfig明示 | secondはconfig明示`auto=false`のみ、他2値はbuild既定; Mac/Mainは席ごと差 | build更新で既定が変わると挙動ドリフト | 3値を全実体configへ明示する案を別GOで実施。重複キーlint必須 |
| 8 | auto_decompose重複 | third部長3configで重複`false`/`true`を実測し今回false一本化 | 他PCは全件未悉皆 | YAML後勝ちで意図に反し自動分解が有効化され得る | `kanban.auto_decompose`重複key検査を配布前gateへ |
| 9 | watcher数 | third probe=25関連process | second=16; mainは小probe未取得; Mac=UNMEASURED | watcher欠落/重複は死箱・未着・暴走を生む | process名ではなく役職×source×targetのregistry表とat-most-once検査を作る |
|10| local inbox実体数 | third repoで多数（probe初回root誤認後、現repoにqueue/inbox） | second probe=`1`（probeが`/home/hakudokai/multi-agent-shogun`を選んだ結果） | repo rootの取り違えで「箱が無い」偽判定になる | 起動時cwd/repo正本を固定し、probeに陽性対照box名を要求 |
|11| pane registry | third現repoに存在 | second存在; mainは小probe未確認; Mac=UNMEASURED | 名札空欄で本人が規律停止した実害（honbucho %83） | `@agent_id`とregistryを起動postcheckでread-only照合し、不一致は作業前B4 |
|12| SSH鍵のHOME差 | third active profile HOMEでは`~/.ssh/daishogun...`不在（実接続は外側HOME/agent依存） | second同probeで不在; main接続はagent/既存鍵で成功 | `~`解決差により同じcommandが警告・認証拒否 | 鍵pathはlauncherが絶対注入し、秘密値を表示せず`test -r`だけ検査 |
|13| Windows watchdog観測 | thirdからmain `/mnt/d/ccflare/watchdog.ps1`を読め、HTTP health/curl_exit_N確認 | main WSLはinteropなし、Task 4値を自力取得不能 | 不調owner自身が診断器を使えない | Windows側read-only collectorを作りDB便へ4値だけ返す。task変更は別GO |
|14| filesystem/case/path | third/second repoはLinux home | mainはWindows mount; MacはBSD/macOS path | stat/sha/find/mtimeコマンド差でsilent failure（Mac `stat -c`実害） | OS判別wrapperを共通化。GNU/BSD両対照testを追加 |
|15| hook互換 | third Linux hookは稼働 | Macは`context_usage_warn.sh`のGNU `stat -c`で警告沈黙死報告あり | context飽和予防がPCで無効 | portable `stat` wrapperへ。Mac実機4対照後に配布 |
|16| 上りhelper/envelope | thirdは`from_pc=third_pc`＋sender_agent分離 | main軍師は`from_pc=gunshi-main`混入で36h発信0、修理済 | DB CHECKで上りが完全停止 | helper引数`--from-pc/--sender`必須・format validatorを全PCへ |
|17| receiver/watcher経路 | thirdはDB+専用bellが主 | second本部長は旧local watcher残骸/inbox1、viewer-unify未完; Macは複数旧箱 | 未読大量・誤配・死箱を生む | DB専用downlinkへ先に向き直し、STOP-AUTH 8欄後に旧watcher退役 |
|18| 実行バージョン | third role群はv2026.8.19 runが多い | secondは0.20.5/currentとv2026.8.3が混在; mainはHermes PATHなし; Mac未測 | config schema/既定値/機能差が大きい | version-line canonの自然respawn窓で揃える。強制respawnは禁止 |
|19| ユーザー/命名 | third=`hakudoukai` | second=`hakudokai`（綴り差）、main=`user` | path/hardcode/SSH userの事故源 | PC別`USER_HOME/REPO_ROOT`をregistryから解決し、文字列直書きをlint |
|20| Mac到達性 | third→Mac正規直接SSHはALL-SSH固定3endpointに含まれず | main経由hostname `mac`もDNS解決不能（今回実測） | Mac環境の独立再測ができず報告依存になる | 新endpointを増やさず、既存Commander採取→SHA-bound mirrorを正式read-only経路にする |

## 優先順位

1. **P0**: main WSLInterop/Windows collector、receiver経路統一、helper envelope validator。
2. **P1**: version-line統一、repo root/HEAD/path正本化、Kanban 3値明示・重複key gate。
3. **P2**: OS portable hook、watcher registry、Mac SHA-bound mirror。

## 注意

- main full probeは`Path.home().rglob(config.yaml)`が120秒timeout。これはhome全域探索が重過ぎる環境差の証拠でもある。小probeへ切替えた。
- Macは直接測定不能。既存報の引用は「既存証拠」と札を付け、現在値と断定しない。
- Commander成果は一切参照していない。
- 解決提案は全て未実行。

## 完了判定

20項目。各項に実測差・重要性・可逆提案あり。read-only。Macの未測値は0件扱いしていない。
