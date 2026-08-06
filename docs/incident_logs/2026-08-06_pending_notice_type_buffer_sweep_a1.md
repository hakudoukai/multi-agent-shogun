# 「詰まった報せ」全数調査 — pending-notice型 buffer 機構の scripts/** 横断索き（足軽1号）

- 下命: karo-second msg_20260806_205742_fbc3a45d (2026-08-06T20:57:42)
- 前工区: docs/incident_logs/2026-08-06_gunshi_second_clear_defect_currency_check_a1.md（third_pc.yaml 518h 停まりの現況、commit `17a7c26` にて PASS 収載済）
- 端緒: `_pending_notice` の flush は次の同種事象が来ねば出さぬ（独立 timer 無し・a5 実測）。
- 測時=2026-08-06T21:01:09+09:00（`date -Iseconds` 実行結果）／器=`ls -la`/`cat`/`stat`/`/usr/bin/grep -rln`/`systemctl --user list-timers --all`/`crontab -l`／範囲=`queue/dead_letter/_pending_notice/` 全file + `scripts/` 配下全 `.sh`/`.py`（`.bak`/`__pycache__` は除外・理由=旧版残骸・実行対象外ゆえ）。
- git rev-parse HEAD = `17a7c26ecef363cfb866773187dc73e8bcb280bc`

**禁の順守**＝flush を起こしていない（`_notify_pc_dispatcher_of_unroutable` を呼ぶ script は一切実行せず）・script は一切実行せず読むのみ・`queue/inbox/_dead_letter_second.yaml` は不触（grep/wc/cat 含め一度も参照せず）。

## ⒜ `queue/dead_letter/_pending_notice/` の全file

```
$ ls -la queue/dead_letter/_pending_notice/
shogun-second.log       (324 bytes, mtime 2026-08-06 02:02:41)
shogun-second.log.lock  (0 bytes,   mtime 2026-08-06 02:02:41)
```

全filesystem entry数=**2**。

`.lock` を「詰まった報せ」の数に入れるか＝**入れない**。理由＝サイズ0byte・作成時刻から一度も書き換わっていない（Modify=Change=Birth 全て同時刻）＝`_acquire_lock2`/`_release_lock2` が使う flock 用の mutex 実体であり、通知本文を一切保持しない。従って「詰まった報せ」＝**1件**（`shogun-second.log` 内の1行）。

`shogun-second.log` 中身（cat 実行結果、全1行）:
```
1785949361 2026-08-06T02:02:41 FROM不明の便を墓場へ落とした / .../unroutable_20260806_020241_2f3af34c.yaml (target==... reason=unroutable_target_and_unresolvable_from)
```

現況＝滞留 **18時間58分28秒**（entry epoch 1785949361 [2026-08-06T02:02:41] → 測時 21:01:09、`datetime` 差分実測）。宛先ファイル名は `shogun-second.log` のみ＝**問い「今詰まっておる報せは将軍second宛の一件だけか」の答＝はい、現存する pending-notice buffer file は shogun-second 宛の1本のみ（他の宛先file無し、`ls` で実測）**。

## ⒝ 同種buffer機構の scripts/** 横断索き

検索= `/usr/bin/grep -rln` で以下語彙を横断: `pending`/`buffer`/`flush`/`should_flush`/`CAP:-`/`INTERVAL_SECONDS`/`_acquire_lock2`/`束ね`/`溜め`/`溜まった`/`貯めて`/`bundle`/`coalesce`/`digest`/`batch.*interval`/`accumulat`。`.bak`・`__pycache__` は除外。

**同型ヒット＝1件、`scripts/diagnose.sh` の夜間モード morning_digest 繰延**:

- 該当関数 `check_night_mode()`（L118-155）。`NIGHT_MODE_FLAG=~/.openclaw/night_mode` が存在し、runbook の `night_policy != immediate` の時、`/tmp/morning_digest.json` へ JSON配列で追記（1エラー1entry）。
- `docs/runbooks/err-ekarte-001.md` L57 記載の設計意図＝「ERROR/WARN は morning_digest として翌朝7:30にまとめて通知」。
- **実測＝`/tmp/morning_digest.json` を読み取る/送信する処理は `scripts/` 配下に0件**（`/usr/bin/grep -rln "morning_digest"` 実行結果、ヒットは `scripts/diagnose.sh` 自身のみ＝書き込み箇所のみ）。
- **7:30 flush を担う cron/systemd timer も0件**（`crontab -l`＝"no crontab for hakudokai"、`systemctl --user list-timers --all` 実測7件中 diagnose/digest 関連0件＝`enter_restart_shogun_second`/`shogun_auto_claim`/`auto-git-sync`/`secondpc-alive-monitor-v0.2`/`shogun-self-check`/`codex-healthcheck`/`launchpadlib-cache-clean` のみ）。
- 現況＝`/tmp/morning_digest.json` 自体が**現存しない**（`night_mode` flag も現存しない）＝本機構は**現在は実データを溜めていない（潜在的欠陥・目下は未発火）**。`_pending_notice/shogun-second.log`（現に19h弱・実entry在り）とは状態が異なる点を区別して記す。

**同型に見えたが除外した候補**（理由付き）:

| 候補 | 除外理由 |
|---|---|
| `scripts/diagnose.sh` の `add_dead_letter()`（`/tmp/dead_letter_errors.json`） | 追記のみ・cap/interval判定が無い（無条件append）。設計文書上も「後で自動送信する」意図の記載を見つけられず＝pending-notice（後で送る前提の一時buffer）ではなく永続監査ログの性格に近いと判じた。読者も0件だが、性格が違うため同型扱いは避けた。 |
| `scripts/karo_second_reception_check.sh`（SKIP/未読 閾値判定） | 状態を蓄積するbuffer fileを持たない。実行の都度その場でSKIP件数と未読件数を`agent_status.sh`等から動的取得し閾値判定するだけの単発診断ツール（永続化なし＝flush概念自体が無い）。 |
| `scripts/fukuincho_report_poke_bundle.py`（bundle構造） | 「bundle」はcorrelation_id単位で即時同期実行（報告INSERT→即poke）。蓄積して後続事象を待つ設計ではない（1件即処理、次事象待ちのbuffer file無し）。 |
| `backend/etl/quartetto_pdf_watcher.py` の pending-queue（`queue/reports/ashigaru4_...`記載） | 別repo（`/mnt/c/Projects/hakudokai-dev`）＝下命範囲「scripts/**」（本repo）の外。参考までに読んだが、flush契機も「次の同種事象」でなく「watcher起動時」＋`max_retry`上限付きで構造が異なる（除外理由は範囲外である事を主とする）。 |

## ⒞ 見付けた各々の引き金・止まれば何が起きるか

1. **`queue/dead_letter/_pending_notice/shogun-second.log`**（`_notify_pc_dispatcher_of_unroutable`、`scripts/inbox_write.sh` L385-446）
   - 引き金＝**次に同関数が呼ばれた時**（＝次にFROM不明/unroutable宛の便が dead-letter へ落ちた時）に限り、その時点で `count>=5行` または `age>=300秒` を満たせば flush。独立timer/cronは実測0件（前票a5実測を本票でも再確認、対象は同一箇所ゆえ再測はしていない）。
   - 止まれば＝次の同種事象が来るまで**無期限に**buffer内に滞留（現に18h58m滞留中）。

2. **`/tmp/morning_digest.json`**（`scripts/diagnose.sh` `check_night_mode()`）
   - 引き金＝**入り口（accumulate）のみ実装**＝夜間モード中の非CRITICALエラー発生時にappendされる。**出口（flush）のコードが repo 内に存在しない**＝「次の同種事象」にすら依存できない、_pending_notice より一段深刻な形（次善のトリガーすら無い）。
   - 止まれば＝ドキュメント記載の「翌朝7:30通知」が**恒久的に発生しない**（コードが無いため）。現在は night_mode flag・digest file とも不在ゆえ実害は目下ゼロだが、night_mode運用を実際に有効化した場合に初めて顕在化する潜在的欠陥。

## ⒟ 「無い」判定の対象

`scripts/` 配下で `_pending_notice` と同型（accumulate→条件付flush、次事象または独立timer依存）の buffer file が上記2件**以外に無いか**を、⒝記載の語彙横断 grep で索いた。3件目以降＝**0件**（索いた語彙・除外理由は⒝表に記載の通り）。

## ⒠ 己の手で為した事

```
ls -la queue/dead_letter/_pending_notice/
cat queue/dead_letter/_pending_notice/shogun-second.log
stat queue/dead_letter/_pending_notice/shogun-second.log queue/dead_letter/_pending_notice/shogun-second.log.lock
date -Iseconds ; git rev-parse HEAD
/usr/bin/grep -rln "pending" scripts/
/usr/bin/grep -n "notify_pc_dispatcher_of_unroutable|_pending_notice|flush|BUFFER|buffer_count" scripts/inbox_write.sh
sed -n '380,450p' scripts/inbox_write.sh   # _notify_pc_dispatcher_of_unroutable 全文精読
/usr/bin/grep -rln "should_flush|_flush|flush_content" scripts/*.sh scripts/lib/*.sh
/usr/bin/grep -rln "count.*-ge|CAP:-|INTERVAL_SECONDS|_acquire_lock2|buffer" scripts/*.sh scripts/lib/*.sh scripts/*.py
sed -n '1,40p' scripts/karo_second_reception_check.sh   # 除外判断のため精読
/usr/bin/grep -rlnE "coalesce|digest|batch.*(interval|cap)|accumulat" scripts/ --include=*.sh --include=*.py
sed -n '1,30p;100,190p' scripts/diagnose.sh   # check_night_mode/add_dead_letter 全文精読
/usr/bin/grep -n "MORNING_DIGEST|morning_digest|night_mode|NIGHT_MODE" scripts/diagnose.sh
/usr/bin/grep -rln "morning_digest" . --include=*.sh --include=*.py --include=*.md
ls -la /tmp/morning_digest.json /tmp/dead_letter_errors.json ~/.openclaw/night_mode ~/.openclaw/disable_diagnose   # 全て不在確認
crontab -l
systemctl --user list-timers --all
/usr/bin/grep -rln "diagnose.sh" . --include=*.sh --include=*.py --include=*.md   # 呼出元0件（doc参照のみ）確認
/usr/bin/grep -n -B3 -A10 "morning_digest|7:30|night_mode" docs/error-design-medical.md
head -40 queue/reports/ashigaru4_planA_step4_stage2_pending_queue_impl_20260707.md   # 別repo・範囲外である事の確認のため
```

以上（読めぬfileは無かった・scriptは一度も実行していない・flushは起こしていない）。

## 監査体制

暫定二者制（軍師second + Gemini）。Codex leg停止中（2026-07-21事案）。「二者PASS」を「三者PASS」と書かない。
