# `_dead_letter_second.yaml` 書込経路 runtime process census（足軽6号）

下命=家老second msg_20260806_223746_5f94d3b9（current_order_6_20260806_2240_RUNTIME_WRITER_INDEX、2026-08-06T22:37:46）。
棲み分け＝足軽4号がstatic側（code上のwriter/reader）、当職はruntime側（現に生きておるprocess）。読取専用。

禁＝process止めるな・killするな・restartするな（読取のみ）／原本`_dead_letter_second.yaml`は読まず（grep/wc/cat不使用、size含め本票では一切触れていない、ls/statも未使用＝不要と判じ触れず）／`hakudokai-dev`へ一字も書かず・cdもせず／codeを書き換えず・新規scriptを作らず。

測時=2026-08-06T22:43:17+09:00。git rev-parse HEAD=552fa64526aaffad4f4d0c350e8fbc232608f782。hostname=USER-O6AK917NTU（SecondPC）。

## ⒞ 索いた範囲（母集団）を先に書く

```
$ /usr/bin/grep -rl "_dead_letter_second" scripts/ shim/ （.bak/__pycache__/.pyc除く）
→ shim/hakudokai/hakudokai_secondpc_receiver_poll.py の1件のみ
$ /usr/bin/grep -rliE "dead.?letter" scripts/ shim/ （広域、"_second"接尾辞に限らぬ）
→ 8件（内訳は下記「除外」節）
```
範囲＝`scripts/**`・`shim/**`全体（`.bak*`／`__pycache__`／`.pyc`は対象外、コード実体ではないため）。
当PC（SecondPC、USER-O6AK917NTU）上で`ps`により観測可能なprocessのみを母集団とする。
★MainPC・third PC上に同名処理を行うprocessが在るか否かは、当職からは確認不能＝判らぬまま記す（第四値）★。

## ⒜ `_dead_letter_second.yaml`（正確に該当file）へ書き得るcode経路＝1件

`shim/hakudokai/hakudokai_secondpc_receiver_poll.py` の `append_dead_letter()` 関数（232-254行実測）が
`queue/inbox/_dead_letter_second.yaml` へ★追記書込み（`path.write_text`）★する唯一のcode経路。
未ルーティング(unresolved target)のmessageを受けた時に発火。

### 除外した候補（"dead_letter"広域一致だが対象外と判じた根拠、隠さず記す）

| file | 実態 | 対象外の根拠 |
|---|---|---|
| `scripts/lib/inbox_path.sh` | `queue/dead_letter/${agent}/` （別path、"_second"接尾辞なし） | 別のdead-letter機構（agent別dir） |
| `scripts/diagnose.sh` | `/tmp/dead_letter_errors.json` | 別path・別形式（tmp上のjson） |
| `scripts/inbox_write.sh` | `queue/dead_letter/_unroutable/` | 別path（`_dead_letter_second.yaml`ではない） |
| `scripts/archive/message_delivery_v2_full_20260508/dead_letter.sh` | `queue/dead_letter/<agent>/<msg_id>.yaml` | ★`scripts/archive/`配下＝廃止済実装（旧v2、稼働対象外と判じた。本票では実行有無を`ps`で別途確認、下記参照）★ |
| `scripts/archive/message_delivery_v2_full_20260508/watcher.sh` | 上記dead_letter.shを`source` | 同上、archive配下 |
| `shim/hakudokai/hakudokai_secondpc_watcher_poll.py` | Supabase `pc_handshake`行を`acknowledged_by=dead_letter`でPATCH（DB側、file書込みではない） | ★対象file(`_dead_letter_second.yaml`)を一切参照せず（50-90行実読で確認、該当文字列0件）★ |
| `shim/hakudokai/hakudokai_fukuincho_reverse_poll.py` | 同上（Supabase PATCH、file書込みなし） | 同上 |
| `shim/hakudokai/hakudokai_fukuincho_poll.py` | 同上（Supabase PATCH、file書込みなし） | 同上 |

∴ ★`_dead_letter_second.yaml`という★正確なfile★へ書き得るcode経路は、母集団8件中★1件のみ★（`hakudokai_secondpc_receiver_poll.py`）。

## runtime process の列挙（数えるな・列挙せよ、の条を順守）

`hakudokai_secondpc_receiver_poll.py`は単発poll（1回実行して終了、`sys.exit`で終わる設計、末尾実読で確認）ゆえ、
★之を反復実行する親wrapper★＝`shim/hakudokai/hakudokai_secondpc_receiver.sh`（`while true; do ...; python3 hakudokai_secondpc_receiver_poll.py ...; done`構造、全文実読で確認）が
★実質的な「書き得る経路を持つ生きたprocess」★である。

```
$ ps -eo pid,ppid,pgid,sid,lstart,etime,tty,cmd | /usr/bin/grep -iE "receiver|secondpc"
    PID    PPID CMD
    401     275 doppler ... hakudokai_secondpc_watcher.sh --interval 5    ★別経路(watcher.sh)、下記②で対象外と確認★
    527     401 bash ... hakudokai_secondpc_watcher.sh --interval 5       同上（子process）
 478747     275 doppler ... hakudokai_secondpc_receiver.sh --interval 5  ★対象①★
 478764  478747 bash ... hakudokai_secondpc_receiver.sh --interval 5     ★対象①の子process★
```

★列挙結果＝2件（1 pair）★＝
1. PID 478747（`doppler run ...`、親process、PPID=275=`systemd --user`）
2. PID 478764（PPID=478747、`bash .../hakudokai_secondpc_receiver.sh --interval 5`、★実質の書込主体★）

★同一pane内二重の有無★＝`tmux list-panes -a`実測（全11pane列挙）の結果、いずれのpane_pidも478747/478764と一致せず
（`multiagent-second:0.0`〜`0.8`のpane_pidは209561〜567564の範囲、`hermes-*`/`shogun-second`も別pid）。
∴ ★之はtmux paneに属さず、systemd userサービスとして独立起動しておる★（下記参照）。同一pane内での二重watcher問題は★該当なし★（そもそもpane非属）。
`ps`全体を再走査した結果、上記2件以外に`receiver`/`secondpc`を含むprocessは★0件★（`hakudokai_secondpc_watcher.sh`系2件を除く）。

### 除外した`hakudokai_secondpc_watcher.sh`（PID 401/527）の扱い

```
$ /usr/bin/grep -nE "dead_letter|receiver_poll|_dead_letter_second" shim/hakudokai/hakudokai_secondpc_watcher.sh
→ 0件ヒット
```
`watcher.sh`はoutbound方向（`dentalbi-secondpc-watcher.service`のDescription="SecondPC outbound watcher"、実測）であり、
`_dead_letter_second.yaml`への書込経路を一切持たない（code実読で確認）。★対象外・稼働はしているが本題の母集団には含めず★。

### `scripts/archive/message_delivery_v2_full_20260508/`配下（旧v2実装）のprocess有無

```
$ ps -eo cmd | /usr/bin/grep -i "message_delivery_v2"
→ 0件（該当process無し）
```
稼働中process★0件★。code上はdead_letter経路を持つが、archive配下＝旧v2実装であり現に走っていないため、本票の「現に生きておる」母集団からは除外（存在した事実のみ記録）。

## ⒜ 起動時刻／pane／親子関係

| PID | 役割 | PPID | pane | 起動時刻(ps lstart) | 備考 |
|---|---|---|---|---|---|
| 478747 | doppler wrapper(親) | 275(`systemd --user`) | ★非該当（tmux pane外）★ | Mon Aug 3 18:56:28 2026 | 下記「食い違い」参照 |
| 478764 | bash本体（実質書込主体） | 478747 | 同上 | Mon Aug 3 18:56:29 2026 | 親の1秒後にfork、自然な親子関係 |

★食い違い、事実として記す（判定はせぬ）★＝
`systemctl --user show dentalbi-secondpc-receiver.service --property=ActiveEnterTimestamp,ExecMainStartTimestamp,NRestarts`実測＝
`ActiveEnterTimestamp=Mon 2026-08-03 17:27:20 JST` / `ExecMainStartTimestamp=同時刻` / `NRestarts=0`。
∴ ★systemd側は「17:27:20から一度も再起動せず継続稼働」と申告するが、`ps`が読む実プロセスの起動時刻(`/proc`由来)は18:56:28＝★1時間29分8秒の差★★。
`NRestarts=0`ゆえsystemdの管理上は同一instanceのはずだが、カーネルの申告する起動時刻とは食い違う。
★原因は当職には判定不能（doppler wrapperの内部exec挙動等が想像されるが確証無し、憶測は記さぬ）★——★之は判らぬまま記す（第四値）★。
両者いずれの数値も実測のまま両方記載する（どちらか一方を「正」と決めていない）。

## ⒝ 再起動時の挙動

```
$ systemctl --user cat dentalbi-secondpc-receiver.service
[Service]
Type=simple
Restart=on-failure
RestartSec=5
...
[Install]
WantedBy=default.target

$ systemctl --user is-enabled dentalbi-secondpc-receiver.service
enabled
```

★supervisor＝systemd（user session）★。`enabled`ゆえ★次回のuser-session起動（再起動/再ログイン）時に自動起動★。
`Restart=on-failure`ゆえ★process異常終了時は5秒後(RestartSec=5)に自動再起動★。
cron登録＝★0★（`crontab -l`は前工区で実測済＝no crontab、本票では再測せず前実測を援用する旨明記）。
手動起動のみに依存する部分＝★無し★（systemd管理下のみ）。

## ⒟ 判らぬまま残す事

- systemd側とkernel側の起動時刻食い違い（89分8秒）の原因＝判らぬ。
- MainPC/third PC上に同種processが存在するか＝判らぬ（当職の観測範囲は当PCのみ）。
- `dentalbi-secondpc-receiver.service`という名称の由来（"DentalBI"というproduct名がなぜこの多agent系mailboxの一部を担っておるか）＝本票の範囲外につき追及せず、事実（Description欄の文言）のみ転記。

## 己の手で為した事

- `/usr/bin/grep -rl "_dead_letter_second" scripts/ shim/` で正確file一致の候補を索索（1件）
- `/usr/bin/grep -rliE "dead.?letter" scripts/ shim/` で広域候補を索索（8件、bak/pycache除く）、各fileを個別に`grep -niE`で中身確認し対象外理由を記録
- `shim/hakudokai/hakudokai_secondpc_receiver_poll.py`の`append_dead_letter()`関数（232-254行）を実読、書込先pathを確認
- `shim/hakudokai/hakudokai_secondpc_receiver_poll.py`末尾を`tail`で実読、単発poll設計（sys.exitで終了）を確認
- `shim/hakudokai/hakudokai_secondpc_receiver.sh`全文を`cat`で実読、`while true`反復loop構造とpython3呼出しを確認
- `shim/hakudokai/hakudokai_secondpc_watcher_poll.py`・`hakudokai_fukuincho_reverse_poll.py`・`hakudokai_fukuincho_poll.py`の`dead_letter_message()`相当部を実読、Supabase PATCH（file書込みでない）である事を確認
- `shim/hakudokai/hakudokai_secondpc_watcher.sh`を`grep`し、dead_letter関連文字列0件を確認
- `ps -eo pid,ppid,pgid,sid,lstart,etime,tty,cmd`を実行、`receiver|secondpc`で絞り込み全件列挙（pgrep -fc等の水増しされ得る計数手法は使用せず）
- `ps -eo cmd | grep message_delivery_v2`で旧v2 archive実装の稼働有無を確認（0件）
- `tmux list-panes -a -F ...`で全11 paneのpane_pidを列挙し、478747/478764/401/527のいずれとも一致しない事を確認（pane非属の裏付け）
- `ps -p 275 -o pid,ppid,cmd`でPPID=275が`systemd --user`である事を確認
- `systemctl --user status 478747`・`systemctl --user status 401`で両doppler processの所属serviceを特定（各々`dentalbi-secondpc-receiver.service`・`dentalbi-secondpc-watcher.service`）
- `systemctl --user cat dentalbi-secondpc-receiver.service`で`Restart=on-failure`・`RestartSec=5`・`WantedBy=default.target`を実測
- `systemctl --user is-enabled dentalbi-secondpc-receiver.service`で`enabled`を確認
- `systemctl --user show dentalbi-secondpc-receiver.service --property=ActiveEnterTimestamp,ExecMainStartTimestamp,ExecMainPID,NRestarts`で正確な起動時刻・再起動回数を実測、`ps lstart`との食い違いを発見・そのまま記録
- process停止・kill・restartは一切行っていない（読取のみ）。`_dead_letter_second.yaml`本体には一度も触れていない（grep/wc/cat/ls/stat悉く不使用）。`hakudokai-dev`へは触れておらず、cdもしていない（本票の作業は全て`multi-agent-shogun`リポジトリ内および`ps`/`systemctl`/`tmux`のprocess観測のみ）

## 数の扱い

測時=2026-08-06T22:43:17+09:00／器=`ps`+`systemctl --user`+`grep`+`tmux list-panes`／範囲=当PC(SecondPC)上で観測可能な全process＋`scripts/`・`shim/`全code。
`_dead_letter_second.yaml`へ書き得るcode経路＝1件。之を反復実行するprocess（親子pair）＝★1組・2 PID★（478747＋478764）。同一pane内二重＝0件（pane非属ゆえ該当構造なし）。稼働中の別経路（archive配下v2実装）＝0件。
以上（読めぬfileは無かった。`_dead_letter_second.yaml`本体は範囲外につき対象外）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。
