# Lane A: _pending_notice 定期flush 入口 実装 (足軽5号)

## 下命

karo-second msg_20260806_212616_312e26af (2026-08-06T21:26:16)。当職が同日21:07票
(`docs/incident_logs/2026-08-06_26834_count_to_events_material_a5.md` 内「reactive-flush-stalls-in-quiet-periods」節)
で己の手で測った欠陥——`_notify_pc_dispatcher_of_unroutable()` (`scripts/inbox_write.sh`) の
cap=5/age=300s 束ね判定は「関数が呼ばれた時」にしか評価されず、独立timer/cron が無いため
事象が疎らな時期は buffer が無期限に stall し得る（実測18時間45分・将軍second宛notice単独滞留）
——への実装GO。本部長殿令21:19:27／Commander裁定`seq152276`＋将軍second追加四つを転記した下命。

## 回収材料

- **owner**: 足軽5号
- **branch**: `feat/pending-notice-periodic-flush`
- **base**: `4061f26128a3c824061f941b746c1bfdff2b76fd`
- **worktree**: `/tmp/hakudokai-worktrees/pending-notice-periodic-flush`（clean隔離・`git worktree add`・`/tmp`配下）
- **commit**: `4ff4d913302ff8aaca6584b36b1cde769fd188dd`（local commit のみ・push/deploy/DB操作 悉く0）
- **RED実走**: 下記§1参照（旧実装を機械抽出し実際に呼んで再現・全4assertion PASS＝旧実装の欠陥そのものを実証）
- **GREEN実走**: 下記§2参照（新entry script実走・全6assertion PASS）
- **artifact path＋SHA256**:

| path | 行数 | sha256 |
|---|---|---|
| `scripts/pending_notice_flush.sh` | 125 | `d6566fbe1687bb9e2553ea4afa9ca8e3f4b2864e68717129376a36bf8f4858c6` |
| `tests/pending_notice_flush_sandbox_test.sh` | 183 | `f045aede0d5dae1b7a8dc31e9eea9e7e26d045410e0dd2745279e281fbe5dc14` |
| `scripts/pending_notice_flush_artifacts/README.md` | — | `eb712351d64f4bc616857b5702017ccd6be0bfbdebeb96646c043b93f522b073` |
| `scripts/pending_notice_flush_artifacts/pending-notice-flush.service` | — | `a151eb5b5deb93220b117751ceb13bf50f5f9cda80c291078ffc8f074953a391` |
| `scripts/pending_notice_flush_artifacts/pending-notice-flush.timer` | — | `8f7b3f183d7873c9412d85156077a4c0620b0fa184b6aaf526288a1b2be626d0` |
| `scripts/pending_notice_flush_artifacts/crontab.example` | — | `6959a92bcf2737f184445c94d549984c64368071490e0a820efc2e2836f76c49` |

測時=2026-08-06T21:46:30+09:00。本 doc 自体は主リポジトリ(`feat/dd169-d006-conditional-exception`)へ保全、実コードは上記隔離branchに存在（両者混同せぬ事）。

## 実装内容

- `_notify_pc_dispatcher_of_unroutable()` (scripts/inbox_write.sh) は **一切書き換えていない**（追加のみ）。
- 新規 `scripts/pending_notice_flush.sh`: 既存と同一の buffer file規約(`<dispatcher>.log`)・同一lock規約(`${buffer}.lock`/`${lockfile}.d`)・同一cap/interval既定(5件/300s、同一env変数名で上書き可)を再利用し、`queue/dead_letter/_pending_notice/*.log` を**次事象非依存**に走査してflush判定する入口。flush送信は `inbox_write.sh` を既存の`_write_message`呼出と同一argv形(TARGET/CONTENT/TYPE/FROM一致・expires/supersedes空)で呼ぶため、通知経路が生む便のバイトは既存の反応的経路と実質同一（本文header行にのみ「定期flush・次事象非依存」の由を追記——読む側の解析形は壊さぬ設計）。
- idempotent: buffer clear は lock保持中に行い、送信はlock解放後(buffer既に空)に行う。再実行・空dir実行いずれも二重送信0（§2下部の idempotent確認1/2で実証）。
- ㈠ systemd/cron へは装着せず。`scripts/pending_notice_flush_artifacts/` に unit file (`*.service`/`*.timer`) と cron例を **参考artifactとしてのみ** 配置（README.mdに未装着を明記）。GREENの立て方は entry script を試験が直に呼ぶ形（時計に頼らない）。
- ㈡ ログ出力は dispatcher名(非患者の安定ID)・件数・interval/cap数値・rcコードのみ。患者本文・実path・token・鍵は一切出力していない。
- ㈢ worktreeに CLAUDE.md 8行差分は現れず（`git diff 4061f26 -- CLAUDE.md` 差分0で確認済・正常）。
- ㈣ `/tmp/resimg-*` (hakudokai-devのlane) は不触（探索・確認のみ、書込0）。

## §1 RED実走（旧実装を機械抽出して実際に呼び、欠陥そのものを再現）

`_notify_pc_dispatcher_of_unroutable()` を自筆写しでなく `awk`で自己位置決め抽出（2026-08-05 a2先例と同一手法）し、依存先(`_acquire_lock2`/`_release_lock2`/`_write_message`)を最小stub化した上で実際に呼び出した。

1. 旧関数を単発事象で1回呼ぶ→buffer 1行(cap/interval未到達で当然未flush、これ自体はバグでない)。
2. 続いてbuffer先頭epochを400秒前(interval300s超過)へ書き換え、時間経過を模す。★旧関数を再度呼ばない★(=次の同種事象が一切起きないシナリオ)。
3. **age条件は満たしているにも関わらず、buffer は1行のまま**——旧実装には時間経過のみで再評価する経路が存在せぬ事を実測で示した。これが実測18h45mの欠陥そのもの。

## §2 GREEN実走＋idempotent＋陽陰性対照（全15assertion PASS、実行ログ全文）

```
=== RED: 旧実装(反応的flushのみ)は次事象が来ねば独立に評価されぬ事を示す ===
ok: RED-a: 旧関数を1回(単発事象)呼んだ直後は1行(cap/interval未到達で当然未flush)
ok: RED-a: 単発事象では _write_message は呼ばれぬ(正常な挙動・これ自体はバグでない)
ok: RED-b: 時間経過(age超過)でも次事象が無ければ旧実装は再評価せず buffer は減らぬ(実測18h45mの欠陥そのもの)
ok: RED-b: 旧実装の _write_message 呼出は依然0のまま(時間経過だけでは何も起きぬ)

=== GREEN: 新規 entry script (次事象非依存) を直に呼ぶと flush される ===
ok: GREEN: 定期flush後 buffer は空(0行)
ok: GREEN: stub(=inbox_write.sh 相当)が1回だけ呼ばれた
ok: 送信先が buffer名(=dispatcher)と一致
ok: type=unroutable_notice_bundle 一致(既存経路と同一type)
ok: from=inbox_write 一致(既存経路と同一from)
ok: 本文に既存の便本文(束ね対象の生ログ由来)が含まれる

=== idempotent 確認1: 直後の再実行は二重送信を起こさぬ(buffer空) ===
ok: idempotent: 再実行後も stub 呼出は依然1回のまま(二重送信=0)

=== idempotent 確認2: 空 buffer dir(何も無い状態)での実行は安全に no-op ===
ok: idempotent: 空dir実行の exit code=0
ok: idempotent: 空dir実行後も stub 呼出は増えぬ(依然1回)

=== 陽性対照: cap=5到達での定期flush(次事象非依存でも件数条件は機能する事) ===
ok: cap=5到達で1回flush(束ねてtarget=cap_targetへ1通)

=== 陰性対照: cap/interval いずれも未到達なら flush しない ===
ok: cap未到達(2<5)・interval未到達(新しい epoch)なら flush 0回
ok: 陰性対照: buffer は2行のまま残る(未flushで正)

=== ALL PASS ===
```

実 `queue/dead_letter/`・実 `queue/inbox/*.yaml` は本試験中 一切不触（`mktemp -d`隔離sandbox＋`inbox_write.sh`をstub化）。bats は使わず plain bash のみで完結（2026-08-05 a2先例踏襲）。3回連続実行で再現性確認済み(rc=0固定)。

## 【この修正が新たに開ける穴】

- 本 script 自体をsystemd/cronへ実際に装着していない現時点では、**この定期flushは誰かが手動で呼ばぬ限り作動しない**——設計上の欠陥は塞いだが、運用上の欠陥（誰も呼ばねば同じ穴が開いたまま）はまだ塞がっていない。装着判断は理事長殿の専権であり、当職の権限外。
- 新script と旧反応的経路は同一lockを取るため相互排他は効くが、**両者が同一buffer上で極めて近接したタイミングで動いた場合の挙動（片方がlockを取っている間もう片方は最大5秒待ってから諦める）は sandbox 上の逐次実行でしか確認していない**——真の並行実行(同時プロセス2本)での競合は本試験の範囲外(未測)。
- flush送信を`inbox_write.sh`のCLI経由(argv)で行うため、**cross-PC bridge の事前チェックを新たに経由する**(旧反応的経路は`_write_message`を直接呼びcross-PC bridgeをスキップしていた)。dispatcher(shogun-second)がローカル宛の場合は実質無害と判断したが、**pc_mapping設定次第で挙動が変わる可能性は実測していない**(未測、限界として明記)。

## 己の手で為した事／己で直した誤り

- `_notify_pc_dispatcher_of_unroutable`の`dispatcher`変数が第2引数(target)ではなく`INBOX_WRITE_DISPATCH_NOTICE_TARGET`環境変数由来である事を当初取り違え(buffer file名が期待と異なり試験が失敗)、旧関数のコードを読み直して自ら是正した。
- `grep -c ... || echo 0`が`grep -c`自体0マッチ時にも"0"を出力する事を知らず、フォールバックが二重に"0"を出力する自作バグを踏み、`|| true`形へ訂正した。
- サブプロセス(stub script)への環境変数伝播漏れ(`STUB_LOG`未export)により最初のcap=5陽性対照が偽FAILになった事を、`set -x`でのトレース実行により自ら特定・是正した。
- RED再現の初稿は「旧関数を実際に呼ばず状態を手で作文する」形だったが、これでは同義反復(tautology)に留まり本当の旧実装の欠陥を実証していない事に気付き、`awk`による機械抽出＋実呼出へ書き直した。

## 禁則遵守声明

既存`_notify_pc_dispatcher_of_unroutable`は不変(追加のみ)・systemd/cron未装着(artifactのみ)・ログは非患者ID+数値のみ・`/tmp/resimg-*`不触・push/deploy/DB操作0・実`queue/`不触(sandbox隔離)・軍師secondへ実装を頼まず(自ら実装)・commit前提のThird-Party Audit Ruleは「未監査」として本便で明記。以上、悉く遵守。
