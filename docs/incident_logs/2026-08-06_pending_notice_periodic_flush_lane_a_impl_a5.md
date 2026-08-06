# Lane A: _pending_notice 定期flush 入口 実装 (足軽5号)

## 下命

karo-second msg_20260806_212616_312e26af (2026-08-06T21:26:16)。当職が同日21:07票
(`docs/incident_logs/2026-08-06_26834_count_to_events_material_a5.md` 内「reactive-flush-stalls-in-quiet-periods」節)
で己の手で測った欠陥——`_notify_pc_dispatcher_of_unroutable()` (`scripts/inbox_write.sh`) の
cap=5/age=300s 束ね判定は「関数が呼ばれた時」にしか評価されず、独立timer/cron が無いため
事象が疎らな時期は buffer が無期限に stall し得る（実測18時間45分・将軍second宛notice単独滞留）
——への実装GO。本部長殿令21:19:27／Commander裁定`seq152276`＋将軍second追加四つを転記した下命。

**追令**: karo-second msg_20260806_212919_ff250a49 (2026-08-06T21:29:19、本部長殿21:23:26 RED gate仕様の転記)。
「18時間45分の現物」「出口0件」はRED の種(構造的裏付け)であってRED本体ではない——修正前検出器の実行RED
を別に必須、単なるimport ERRORや件数PASSで閉じるな、との明示指摘。この追令は当職が最初のcommit(4ff4d91)
提出「後」に着信していたため気付くのが遅れ、追加commit(e1c9c00)で反映した(下記§2参照)。

**補修三令**: karo-second msg_20260806_221926_c656c7f8 (2026-08-06T22:19:26、本部長殿22:10:17判定の転記)。
当職が§【この修正が新たに開ける穴】で自己申告した「fake clock env var名を本番実行時に誤設定すればage判定を
偽装できる新規(小さな)面」を、本部長殿が**契約違反**と裁定——自己申告は加点(書かねば永久に露れなんだ)なれど、
文書化のみで終わらせず実コード修正を要すとの由。⒜TEST_MODE gating（閾値固定でなくstartup拒否側で実装）
⒝invalid/unset/negative/overflowのRED→GREEN追加 ⒞旧base mv REDに復元SHA+porcelain clean証拠化。
追加commit(`c2bcf1d`)で反映(下記§6参照)。

## 回収材料

- **owner**: 足軽5号
- **branch**: `feat/pending-notice-periodic-flush`
- **base**: `4061f26128a3c824061f941b746c1bfdff2b76fd`
- **worktree**: `/tmp/hakudokai-worktrees/pending-notice-periodic-flush`（clean隔離・`git worktree add`・`/tmp`配下）
- **commit**: `3c28377`（`c2bcf1d`の直後子・`e1c9c00`→`4ff4d91`が先行・local commitのみ・push/deploy/DB操作 悉く0）。`4ff4d91`=最初の実装、`e1c9c00`=RED gate仕様反映、`c2bcf1d`=補修三令⒜⒝反映、`3c28377`=残欄㈠(真並行競合実測)追加commit。
- **RED gate実走（契約本体）**: 下記§2参照（fake clock+isolated store・old-base自己判定・§2〜§10 全17assertion PASS。entry script不在(旧base相当)を`mv`で模した際は正しくFAIL(exit1)になる事も確認済み）
- **構造的裏付け（RED seed）**: 下記§1参照（旧実装を機械抽出し実際に呼んで再現）
- **補修三令⒜⒝⒞（契約違反是正）**: 下記§6参照（TEST_MODE gating・invalid/negative/overflow/no-test-mode拒否の5節追加・old-base mv REDの復元SHA+porcelain clean証拠化）
- **残欄㈠（真並行2本競合）**: 下記§7参照（no-lock変異体RED・実物GREEN・5回連続PASS）
- **残欄㈡（TEST_MODE対設定の機械実測）**: 下記§8参照（★未閉鎖と明記・閉じたと書かず★）
- **artifact path＋SHA256**（`3c28377`断面）:

| path | 行数 | sha256 |
|---|---|---|
| `scripts/pending_notice_flush.sh` | 169 | `e34dcf9837adb053b7191d3a164c9d474985570acb651b0a95f757b4a935684b` |
| `tests/pending_notice_flush_sandbox_test.sh` | 307 | `dd96fb6922ba3b9ae5824c050206a6ad9a5ebd521b625c828ffeae32a308d5e0` |
| `tests/pending_notice_flush_concurrency_race_test.sh` | 155 | `82ca6363080a24625149ec913e60792fd2c1d48e7e2eab8a37b7f959ac2c4084` |
| `scripts/pending_notice_flush_artifacts/README.md` | — | `eb712351d64f4bc616857b5702017ccd6be0bfbdebeb96646c043b93f522b073` |
| `scripts/pending_notice_flush_artifacts/pending-notice-flush.service` | — | `a151eb5b5deb93220b117751ceb13bf50f5f9cda80c291078ffc8f074953a391` |
| `scripts/pending_notice_flush_artifacts/pending-notice-flush.timer` | — | `8f7b3f183d7873c9412d85156077a4c0620b0fa184b6aaf526288a1b2be626d0` |
| `scripts/pending_notice_flush_artifacts/crontab.example` | — | `6959a92bcf2737f184445c94d549984c64368071490e0a820efc2e2836f76c49` |

測時=2026-08-06T23:44:22+09:00。本 doc 自体は主リポジトリ(`feat/dd169-d006-conditional-exception`)へ保全、実コードは上記隔離branchに存在（両者混同せぬ事）。

## 実装内容

- `_notify_pc_dispatcher_of_unroutable()` (scripts/inbox_write.sh) は **一切書き換えていない**（追加のみ）。
- 新規 `scripts/pending_notice_flush.sh`: 既存と同一の buffer file規約(`<dispatcher>.log`)・同一lock規約(`${buffer}.lock`/`${lockfile}.d`)・同一cap/interval既定(5件/300s、同一env変数名で上書き可)を再利用し、`queue/dead_letter/_pending_notice/*.log` を**次事象非依存**に走査してflush判定する入口。flush送信は `inbox_write.sh` を既存の`_write_message`呼出と同一argv形(TARGET/CONTENT/TYPE/FROM一致・expires/supersedes空)で呼ぶため、通知経路が生む便のバイトは既存の反応的経路と実質同一（本文header行にのみ「定期flush・次事象非依存」の由を追記——読む側の解析形は壊さぬ設計）。
- idempotent: buffer clear は lock保持中に行い、送信はlock解放後(buffer既に空)に行う。再実行・空dir実行いずれも二重送信0（§2下部の idempotent確認1/2で実証）。
- ㈠ systemd/cron へは装着せず。`scripts/pending_notice_flush_artifacts/` に unit file (`*.service`/`*.timer`) と cron例を **参考artifactとしてのみ** 配置（README.mdに未装着を明記）。GREENの立て方は entry script を試験が直に呼ぶ形（時計に頼らない）。
- ㈡ ログ出力は dispatcher名(非患者の安定ID)・件数・interval/cap数値・rcコードのみ。患者本文・実path・token・鍵は一切出力していない。
- ㈢ worktreeに CLAUDE.md 8行差分は現れず（`git diff 4061f26 -- CLAUDE.md` 差分0で確認済・正常）。
- ㈣ `/tmp/resimg-*` (hakudokai-devのlane) は不触（探索・確認のみ、書込0）。

## §1 構造的裏付け（RED seed・旧実装を機械抽出して実際に呼ぶ）

★本部長殿の指摘（追令）に従い、これは RED gate 本体ではなく「構造的裏付け」として明示区別する★。

`_notify_pc_dispatcher_of_unroutable()` を自筆写しでなく `awk`で自己位置決め抽出（2026-08-05 a2先例と同一手法）し、依存先(`_acquire_lock2`/`_release_lock2`/`_write_message`)を最小stub化した上で実際に呼び出した。旧関数を単発事象で1回呼ぶ→buffer 1行(cap/interval未到達で当然未flush、これ自体はバグでない)。これが「事象が起きた瞬間にしか評価されない」旧実装の構造そのものの裏付け。

## §2 ★RED gate契約本体★（fake clock + isolated store・old-base自己判定）

本部長殿仕様「新enqueue無し・age>300・flush entry一回→exactly1dispatch」を、実clock/実storeに一切依存しない形で明示テスト化した。

- **fake clock**: `PENDING_NOTICE_FLUSH_NOW_EPOCH`環境変数を`scripts/pending_notice_flush.sh`へ追加(実clock`date +%s`のfallbackのみ既存動作に使用・試験時は固定epoch定数で完全決定的)。
- **isolated store**: `mktemp -d`隔離dirに1件だけ事前配置(=過去のenqueue1件のみ・以後追加enqueue無し)。
- **old-base自己判定**: `scripts/pending_notice_flush.sh`の有無を試験自身が検知。不在なら「契約を充足する手段そのものが無い」を明示FAILとして返す(クラッシュではなく判定可能な形)。

実測: `mv`で`scripts/pending_notice_flush.sh`を一時隠し旧base相当の断面を作った所、§2が正しく `FAIL(契約・構造的): flush entry (scripts/pending_notice_flush.sh) が本 snapshot に不在` を出し exit code=1 になる事を確認。復元後は再び全PASS(exit0)に戻る事も確認済み(このverify自体はcommit対象外の一時操作、実装ファイルは最終的に復元済み・`git status --short`で無変更確認)。

```
=== §1 構造的裏付け(seed evidence): 旧関数を機械抽出して実際に呼ぶ ===
    (★これ自体はRED本体ではない★——契約RED本体は§2。本部長殿仕様の明示区別に従う)
ok: §1: 旧関数を1回(単発事象)呼んだ直後は1行(cap/interval未到達で当然未flush)
ok: §1: 単発事象では _write_message は呼ばれぬ(正常な挙動・これ自体はバグでない)
    (§1は実測18h45mの構造的裏付けのみ・§2の契約RED本体とは別に評価する)

=== §2 ★契約 RED gate 本体★ (fake clock + isolated store・old-base自己判定) ===
    前提: enqueue 1件のみ(以後追加なし)・fake_event_epoch=1800000000・fake_now_epoch=1800000400(age=400>interval=300)
ok: §2 GREEN: flush entry一回(fake clock age>interval・新enqueueなし)→exactly 1 dispatch
ok: §2 GREEN: flush後 isolated store は空(0行)
ok: §2 GREEN: 送信先が isolated store 名(=dispatcher)と一致
ok: §2 idempotent: 二回目呼出は追加dispatch 0(依然1のまま)

=== §3 idempotent 確認: 空store(何も無い状態)での実行は安全に no-op ===
ok: §3: 空store実行の exit code=0
ok: §3: 空store実行後も dispatch は増えぬ(0のまま)

=== §4 陽性対照: cap=5到達での定期flush(fake clock・次事象非依存でも件数条件は機能する事) ===
ok: §4: cap=5到達(age=0でも)で1回flush(束ねてtarget=cap_targetへ1通)

=== §5 陰性対照: cap/interval いずれも未到達なら flush しない(fake clock) ===
ok: §5: cap未到達(2<5)・interval未到達(age=0)なら flush 0回
ok: §5: 陰性対照: buffer は2行のまま残る(未flushで正)

=== 判定 ===
snapshot: target(実装あり) — §2以降がRED gate契約に照らしGREENである事を確認する断面
=== ALL PASS ===
```

実 `queue/dead_letter/`・実 `queue/inbox/*.yaml` は本試験中 一切不触（`mktemp -d`隔離sandbox＋`inbox_write.sh`をstub化）。bats は使わず plain bash のみで完結（2026-08-05 a2先例踏襲）。§2以降は§4/§5含め実clockを一切用いず fake clock のみで決定的に動作する(§1のみ旧関数内部が実clockを使う点は不変—旧関数自体を書き換えられないための制約、限界として明記)。

## 【この修正が新たに開ける穴】

- 本 script 自体をsystemd/cronへ実際に装着していない現時点では、**この定期flushは誰かが手動で呼ばぬ限り作動しない**——設計上の欠陥は塞いだが、運用上の欠陥（誰も呼ばねば同じ穴が開いたまま）はまだ塞がっていない。装着判断は理事長殿の専権であり、当職の権限外。
- 新script と旧反応的経路は同一lockを取るため相互排他は効くが、**両者が同一buffer上で極めて近接したタイミングで動いた場合の挙動（片方がlockを取っている間もう片方は最大5秒待ってから諦める）は sandbox 上の逐次実行でしか確認していない**——真の並行実行(同時プロセス2本)での競合は本試験の範囲外(未測)。
- flush送信を`inbox_write.sh`のCLI経由(argv)で行うため、**cross-PC bridge の事前チェックを新たに経由する**(旧反応的経路は`_write_message`を直接呼びcross-PC bridgeをスキップしていた)。dispatcher(shogun-second)がローカル宛の場合は実質無害と判断したが、**pc_mapping設定次第で挙動が変わる可能性は実測していない**(未測、限界として明記)。
- ~~fake clock(`PENDING_NOTICE_FLUSH_NOW_EPOCH`)は本番実行時は未設定(=実clock使用)ゆえ本番挙動には影響せぬ設計だが、この環境変数名を知る者が本番実行時に誤って設定すれば意図的にage判定を偽装できる——新たな(小さな)攻撃面。~~
  **→本部長殿22:10:17判定により契約違反と裁定・§6の補修三令で是正済**。`PENDING_NOTICE_FLUSH_TEST_MODE=1`との対設定を必須化し、片方だけの設定・不正値(非数値/負値/桁溢れ)は起動時exit 2で拒否する構造にした——production運用では`TEST_MODE`を立てぬ以上、この環境変数単体でage偽装は構造的に不能になった(§6参照)。残る面: `TEST_MODE=1`**かつ**当該env var名の**両方**を本番実行時に意図的に対設定すれば依然偽装可能——誤操作(片方だけの設定)は確実に拒否されるが、**意図的な対設定までは機械的に阻めない事を§8で実測確認済(★未閉鎖・残欄として明記★)**。ゼロにはなっていない。

## §6 補修三令⒜⒝⒞（fake clock契約違反是正・commit `c2bcf1d`）

本部長殿22:10:17判定「env varでage<300へ偽装可能ならば契約違反」を受けての是正。令④により「300」は
本部長殿指定の閾値である旨、原文(msg_20260806_221926_c656c7f8)を実行の刻に確認した(下記§6コード引用参照)。

**⒜ TEST_MODE gating**（`scripts/pending_notice_flush.sh` L50-77）: `PENDING_NOTICE_FLUSH_NOW_EPOCH`が
設定されているのに`PENDING_NOTICE_FLUSH_TEST_MODE=1`が同時設定されていなければ、起動直後に`exit 2`で
拒否しFATAL文言をstderrへ出す。値そのものも`^[0-9]+$`(非数値・負値を拒否)と`253402300799`(9999年UTC相当)
上限の二重検証を行い、いずれの違反もexit 2で拒否する。「令の側を固定300以上とする」ではなく「startup で
下限を拒否せよ」側で実装した(本部長殿の二択のうち後者を選択・理由=閾値そのものを固定するより、age判定の
入力(now_epoch)を production では実clock強制にする方が、cap/interval設定の柔軟性を将来も保った上で
偽装経路を塞げるため)。

**⒝ invalid/unset/negative/overflowのRED→GREEN追加**（`tests/pending_notice_flush_sandbox_test.sh` §6-§10）:

```
=== §6 ★契約RED gate★: NOW_EPOCH設定・TEST_MODE非設定 → exit 2 で拒否(spoofing不能化の核心) ===
ok: §6: TEST_MODE無しでNOW_EPOCH設定 → exit code=2
ok: §6: stderrにFATAL明記
ok: §6: 拒否時はdispatch 0(何も送信されぬ・偽装は起き得ぬ)

=== §7 invalid: NOW_EPOCH非数値(TEST_MODE=1) → exit 2 ===
ok: §7: NOW_EPOCH非数値 → exit code=2
ok: §7: stderrにFATAL明記

=== §8 negative: NOW_EPOCH負値(TEST_MODE=1) → exit 2 ===
ok: §8: NOW_EPOCH負値 → exit code=2(正規表現^[0-9]+$が'-'を拒否)

=== §9 overflow: NOW_EPOCH桁溢れ(TEST_MODE=1) → exit 2 ===
ok: §9: NOW_EPOCH桁溢れ(9999年超・253402300799超) → exit code=2

=== §10 sanity: TEST_MODE=1のみ(NOW_EPOCH未設定) → 正常動作(実clockを使うのみ・拒否されぬ事) ===
ok: §10: TEST_MODE=1のみ(NOW_EPOCH未設定)は拒否されず exit 0

=== 判定 ===
snapshot: target(実装あり) — §2以降がRED gate契約に照らしGREENである事を確認する断面
=== ALL PASS ===
```

§1〜§10全節、target断面で実行しALL PASS(exit 0)を確認済み(2026-08-06T23:26:26+09:00測)。

**⒞ 旧base mv RED — 復元SHA + porcelain clean証拠化**:

```
$ git status --porcelain            # ①mv前: クリーン
(出力なし)
$ sha256sum scripts/pending_notice_flush.sh   # ②mv前SHA
e34dcf9837adb053b7191d3a164c9d474985570acb651b0a95f757b4a935684b  scripts/pending_notice_flush.sh
[2026-08-06T23:26:53+09:00]

$ mv scripts/pending_notice_flush.sh /tmp/_lanea_moved_away.sh
$ ls scripts/pending_notice_flush.sh
ls: cannot access 'scripts/pending_notice_flush.sh': No such file or directory   # ③不在を確認

$ bash tests/pending_notice_flush_sandbox_test.sh ; echo $?
（§1〜§4はskip・§2の契約RED本体が正しくFAILを返す）
=== 判定 ===
snapshot: 旧base(実装なし) — 契約「flush entry一回→exactly1dispatch」を充足する手段が
存在しない事自体をFAILとして記録する断面(★期待通りの結果★)
=== FAIL(s) present ===
1                                    # ④exit code=1・期待通りのRED

$ mv /tmp/_lanea_moved_away.sh scripts/pending_notice_flush.sh
$ sha256sum scripts/pending_notice_flush.sh   # ⑤復元後SHA
e34dcf9837adb053b7191d3a164c9d474985570acb651b0a95f757b4a935684b  scripts/pending_notice_flush.sh
[2026-08-06T23:27:05+09:00]
                                     # ⑥②と⑤のSHA完全一致=復元確認
$ git status --porcelain            # ⑦復元後: クリーン(mv/RED実験がworking treeに痕跡を残していない)
(出力なし)

$ bash tests/pending_notice_flush_sandbox_test.sh | tail -3   # ⑧sanity: target断面が再びGREENである事
ok: §10: TEST_MODE=1のみ(NOW_EPOCH未設定)は拒否されず exit 0
=== 判定 ===
=== ALL PASS ===
```

①②⑤⑦は本便のため実際に打ち直したコマンド・出力の逐語(要約せず)。③mv直後の不在確認・④旧base側の
exit code・⑥SHA一致・⑧復元後の再GREEN、悉く現物で確認済み(commit `c2bcf1d`断面に対して実施)。

## §7 残欄㈠ — 真並行2本競合の実測（軍師second指名・commit `3c28377`）

下命: karo-second msg_20260806_233724_731b0ad1 (23:37:24)。「競合し得る」を論ずるのではなく
「現に競合させよ」との指名。RED＝旧断面で二重flush/二重dispatchが現に起きる／GREEN＝exactly1・dup0。

**旧断面の扱い方（誤読防止のため明記）**: `scripts/pending_notice_flush.sh`は初回commit(`4ff4d91`)
からlockingを常に備えており、「lockが無かった過去のバージョン」は実在しない。本残欄専用に、実物
scriptを機械変換(awk・`_release_lock()`の閉じ括弧直後にno-op override 2行を挿入し、
`flush_content="$(cat "$buffer")"`直後にrace window明示化のsleep 1行を挿入・計+3行)した
「no-lock変異体」を作り、lock機構そのものの因果効果を真並行下で切り分けた。**production script
本体は一切変更していない**（前回補修三令で「新たな攻撃面」を指摘された教訓を踏まえ、本体を触らず
test専用ファイル内で完結させる設計を選んだ）。

barrierは「両プロセスがgo_fileの出現をbusy-wait監視し、go_fileが出現した瞬間に同時解放される」形
（`touch "$go_file"`が唯一の同期点）で、真にOSレベルで並行実行させている(逐次実行のシミュレーション
ではない)。stub_inbox_write.shの追記自体は`flock`で直列化しているが、これは計測用ログの破損防止に
過ぎず被験対象(dispatch回数)には影響しない。

```
$ bash tests/pending_notice_flush_concurrency_race_test.sh
[2026-08-06T23:44:31+09:00]
no-lock変異体 機械生成完了: 元script=169行 → 変異体=172行(+3行=no-op override2行+sleep1行)
ok: 変異体には override/sleep 挿入行が計3行存在

=== ㈠-RED: no-lock変異体を 真並行2本 走らせる (旧断面相当・locking の因果効果を切り分け) ===
ok: ㈠-RED: no-lock変異体は真並行下で二重(以上)dispatchが現に起きる (actual=2 >= 2)

=== ㈠-GREEN: 実物 scripts/pending_notice_flush.sh (commit c2bcf1d・不変) を 真並行2本 走らせる ===
ok: ㈠-GREEN: 実物(lockあり)は真並行下でも exactly 1 dispatch(dup 0)
ok: ㈠-GREEN: flush後 buffer は空(0行・重複残留なし)

=== 判定 ===
=== ALL PASS ===
```

5回連続実行(2026-08-06T23:26台〜23:44台)で悉くこの結果(RED側dispatch=2固定・GREEN側dispatch=1固定)
となり、非決定性(たまたま再現しない回)は観測されなかった。

## §8 残欄㈡ — TEST_MODE=1かつNOW_EPOCHの意図的対設定が本番で立ち得るかの機械実測

下命同上。「立ち得るならば立ち得ると書け（閉じたと書くな）」との明示指示。

**実測（本便のため実際に打ち直した・要約せず逐語）**:

```
$ date -Iseconds
2026-08-06T23:44:48+09:00
$ real_now_epoch=1786027488  forged_now_epoch=1787027487   # 実clockより約999999秒先
$ PENDING_NOTICE_FLUSH_TEST_MODE=1 \
  PENDING_NOTICE_FLUSH_NOW_EPOCH=1787027487 \
  INBOX_WRITE_DISPATCH_NOTICE_DIR=<isolated dir> \
  PENDING_NOTICE_FLUSH_INBOX_WRITE_BIN=<stub> \
      bash scripts/pending_notice_flush.sh
[pending_notice_flush] PERIODIC_FLUSHED: 1 pending unroutable notice(s) sent to 'demo'
[pending_notice_flush] done: buffers_checked=1 flushed=1
rc=0
$ cat dispatch.log
DISPATCHED_WITH_FORGED_CLOCK target=demo
$ date -Iseconds
2026-08-06T23:44:48+09:00
```

buffer中のnoticeは実測直前(`real_now_epoch`)に生成した=実clock基準ではage≒0で本来flush条件
(age>=300)を満たさぬ筈だが、`NOW_EPOCH`を偽装した瞬間に age>300 と誤判定されflushが起きた。
この呼び出し方は`scripts/pending_notice_flush.sh`自身のヘッダーcomment(L27-41)に**公然と明記**
されている手順そのものであり、隠された裏口ではない。**production運用でこの2変数を意図的に対で
設定する事を機械的に阻む仕組みは、現時点で存在しない**（OS/プロセスレベルでの隔離・呼び出し元検証・
CI限定フラグ等、いずれも未実装）。

**★結論——残欄㈡は「閉じた」とは書かぬ★**: ⒜のTEST_MODE gatingは「片方だけの設定・不正値」という
**誤操作**を確実に拒否する(§6で実証済)。しかし「両方を意図的に対で正しく設定する」という**意図的な
偽装**までは防いでいない——これは§【この修正が新たに開ける穴】に元々記載していた残存面と同一であり、
本§8はそれが実在する事を初めて機械的に実測で確認したもの(従来は推測、本便で実証に格上げ)。防ぐには
実行主体の認証・呼び出し元制限・監査ログ等の追加機構が要るが、これは本補修三令の令④「300は本部長殿
指定の閾値」の範囲を超える設計判断であり、当職の権限外(★閉じ得なんだ残欄として明記・上へ仰ぐ★)。

## 己の手で為した事／己で直した誤り

- `_notify_pc_dispatcher_of_unroutable`の`dispatcher`変数が第2引数(target)ではなく`INBOX_WRITE_DISPATCH_NOTICE_TARGET`環境変数由来である事を当初取り違え(buffer file名が期待と異なり試験が失敗)、旧関数のコードを読み直して自ら是正した。
- `grep -c ... || echo 0`が`grep -c`自体0マッチ時にも"0"を出力する事を知らず、フォールバックが二重に"0"を出力する自作バグを踏み、`|| true`形へ訂正した。
- サブプロセス(stub script)への環境変数伝播漏れ(`STUB_LOG`未export)により最初のcap=5陽性対照が偽FAILになった事を、`set -x`でのトレース実行により自ら特定・是正した。
- RED再現の初稿は「旧関数を実際に呼ばず状態を手で作文する」形だったが、これでは同義反復(tautology)に留まり本当の旧実装の欠陥を実証していない事に気付き、`awk`による機械抽出＋実呼出へ書き直した。
- 追令(RED gate仕様)着信に気付くのが遅れ、先の提出(commit 4ff4d91)は本部長殿仕様策定(21:23:26)前の形のまま送っていた——「18h45mの現物」を RED そのものと扱っていた誤りを、追令受領後に自ら是正し§2契約テストを追加(commit e1c9c00)。
- fake clock導入前の初版は「buffer先頭epochを実`date +%s`から400秒差し引いて書き換える」形で age超過を模していたが、これは実clockに部分依存しており本部長殿仕様の「fake clock」要件を字義通り満たしていなかった事に気付き、`PENDING_NOTICE_FLUSH_NOW_EPOCH`による完全決定的な注入方式へ書き直した。
- 【self-disclosure→escalation】§【この修正が新たに開ける穴】で己が自ら記した「fake clock env var名の誤設定で本番age判定を偽装できる」の一文を、当職自身は「文書化すれば足る小さな限界」と判じていたが、本部長殿はこれを**契約違反**と裁定し実コード修正を要すと判じられた。この裁定差自体が学びに御座る——自ら開けた穴の重さは、開けた本人の見立てが軽くとも、格上の判定を仰ぐまでは確定しない。§6のTEST_MODE gatingはこの裁定を受けての是正。

- 【残欄実測の手法設計】残欄㈠につき、当初「production scriptに lock無効化フラグを test-only で追加する」案を検討したが、これは前回契約違反(fake clock env var)と同型の「新たな攻撃面をproduction本体に追加する」誤りを繰り返す事に気付き、test専用ファイル内でのみ完結するno-lock変異体(機械挿入)へ設計を改めた。production script自体は残欄㈠の対応でも一切変更していない。

## 残欄（★閉じ得なんだ物・明記★）

- **残欄㈡は未閉鎖**: TEST_MODE=1とNOW_EPOCHの意図的な対設定は、production運用で機械的に阻む仕組みが現時点で存在しない(§8実測済)。誤操作(片方だけの設定)は⒜で確実に拒否されるが、意図的な偽装までは防いでいない。追加の実行主体認証・呼出元制限等は本補修三令の範囲(令④「300は本部長殿指定の閾値」)を超える設計判断であり、当職の権限外——上へ仰ぐ。
- **並行実行の限界**: §7のGREEN実測は2プロセスに限定(barrier同期の2本)。3本以上の同時競合、あるいは異なるホスト間での競合は未測。

## 禁則遵守声明

既存`_notify_pc_dispatcher_of_unroutable`は不変(追加のみ)・systemd/cron未装着(artifactのみ)・ログは非患者ID+数値のみ・`/tmp/resimg-*`不触・push/deploy/DB操作0・実`queue/`不触(sandbox隔離)・軍師secondへ実装を頼まず(自ら実装)・commit前提のThird-Party Audit Ruleは「未監査」として本便で明記・`git gc`/`prune`/`reflog expire`不実行・`slim_yaml.sh`不実行・merge/rebase/cherry-pick悉く0。以上、悉く遵守。
