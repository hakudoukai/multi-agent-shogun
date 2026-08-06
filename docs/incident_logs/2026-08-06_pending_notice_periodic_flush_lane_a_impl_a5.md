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

## 回収材料

- **owner**: 足軽5号
- **branch**: `feat/pending-notice-periodic-flush`
- **base**: `4061f26128a3c824061f941b746c1bfdff2b76fd`
- **worktree**: `/tmp/hakudokai-worktrees/pending-notice-periodic-flush`（clean隔離・`git worktree add`・`/tmp`配下）
- **commit**: `e1c9c00`（`4ff4d91`の直後子・local commitのみ・push/deploy/DB操作 悉く0）。`4ff4d91`=最初の実装、`e1c9c00`=RED gate仕様反映の追加commit。
- **RED gate実走（契約本体）**: 下記§2参照（fake clock+isolated store・old-base自己判定・全11assertion PASS。entry script不在(旧base相当)を`mv`で模した際は正しくFAIL(exit1)になる事も確認済み）
- **構造的裏付け（RED seed）**: 下記§1参照（旧実装を機械抽出し実際に呼んで再現）
- **artifact path＋SHA256**（`e1c9c00`断面）:

| path | 行数 | sha256 |
|---|---|---|
| `scripts/pending_notice_flush.sh` | 129 | `c74e2e03eab6a5f809b38e502359b1083ce9c5e281b701810eb6342029727ab5` |
| `tests/pending_notice_flush_sandbox_test.sh` | 233 | `f4d6fe5b203097449ebae3924fa3e4bc5515bc08ce4259b0a2bdc58392f01900` |
| `scripts/pending_notice_flush_artifacts/README.md` | — | `eb712351d64f4bc616857b5702017ccd6be0bfbdebeb96646c043b93f522b073` |
| `scripts/pending_notice_flush_artifacts/pending-notice-flush.service` | — | `a151eb5b5deb93220b117751ceb13bf50f5f9cda80c291078ffc8f074953a391` |
| `scripts/pending_notice_flush_artifacts/pending-notice-flush.timer` | — | `8f7b3f183d7873c9412d85156077a4c0620b0fa184b6aaf526288a1b2be626d0` |
| `scripts/pending_notice_flush_artifacts/crontab.example` | — | `6959a92bcf2737f184445c94d549984c64368071490e0a820efc2e2836f76c49` |

測時=2026-08-06T21:57:47+09:00。本 doc 自体は主リポジトリ(`feat/dd169-d006-conditional-exception`)へ保全、実コードは上記隔離branchに存在（両者混同せぬ事）。

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
- fake clock(`PENDING_NOTICE_FLUSH_NOW_EPOCH`)は本番実行時は未設定(=実clock使用)ゆえ本番挙動には影響せぬ設計だが、**この環境変数名を知る者が本番実行時に誤って設定すれば意図的にage判定を偽装できる**——新たな(小さな)攻撃面。値は非機密の整数epochのみで患者リスクは無いと判断したが、この面自体は旧実装には存在しなかった新規の追加。

## 己の手で為した事／己で直した誤り

- `_notify_pc_dispatcher_of_unroutable`の`dispatcher`変数が第2引数(target)ではなく`INBOX_WRITE_DISPATCH_NOTICE_TARGET`環境変数由来である事を当初取り違え(buffer file名が期待と異なり試験が失敗)、旧関数のコードを読み直して自ら是正した。
- `grep -c ... || echo 0`が`grep -c`自体0マッチ時にも"0"を出力する事を知らず、フォールバックが二重に"0"を出力する自作バグを踏み、`|| true`形へ訂正した。
- サブプロセス(stub script)への環境変数伝播漏れ(`STUB_LOG`未export)により最初のcap=5陽性対照が偽FAILになった事を、`set -x`でのトレース実行により自ら特定・是正した。
- RED再現の初稿は「旧関数を実際に呼ばず状態を手で作文する」形だったが、これでは同義反復(tautology)に留まり本当の旧実装の欠陥を実証していない事に気付き、`awk`による機械抽出＋実呼出へ書き直した。
- 追令(RED gate仕様)着信に気付くのが遅れ、先の提出(commit 4ff4d91)は本部長殿仕様策定(21:23:26)前の形のまま送っていた——「18h45mの現物」を RED そのものと扱っていた誤りを、追令受領後に自ら是正し§2契約テストを追加(commit e1c9c00)。
- fake clock導入前の初版は「buffer先頭epochを実`date +%s`から400秒差し引いて書き換える」形で age超過を模していたが、これは実clockに部分依存しており本部長殿仕様の「fake clock」要件を字義通り満たしていなかった事に気付き、`PENDING_NOTICE_FLUSH_NOW_EPOCH`による完全決定的な注入方式へ書き直した。

## 禁則遵守声明

既存`_notify_pc_dispatcher_of_unroutable`は不変(追加のみ)・systemd/cron未装着(artifactのみ)・ログは非患者ID+数値のみ・`/tmp/resimg-*`不触・push/deploy/DB操作0・実`queue/`不触(sandbox隔離)・軍師secondへ実装を頼まず(自ら実装)・commit前提のThird-Party Audit Ruleは「未監査」として本便で明記。以上、悉く遵守。
