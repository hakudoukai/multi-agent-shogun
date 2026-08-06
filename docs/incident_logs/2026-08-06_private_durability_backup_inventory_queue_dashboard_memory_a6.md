# queue/**・dashboard.md・memory/** の私有耐久（backup）棚卸し（足軽6号）

下命=家老second msg_20260806_211658_d09ddb49（2026-08-06T21:16:58、本部長殿裁定21:15:50を承けた工区）。読取のみ・材料提出のみ（裁定は為さぬ）。
禁＝backupを走らせるな・復旧を試すな・`queue/`へ書くな・`.gitignore`に触れるな／`queue/inbox/_dead_letter_second.yaml`は読まず（`grep`/`wc`/`cat`不使用、本票では触れていない）／lane不触（freeze継続）。

測時=2026-08-06T21:22:11+09:00（本票の最終再測）。git rev-parse HEAD=5eaf396a7ced0a6c3619c4c0252722ad3310f7ee。

## ①の前提（訂正の受領）

本部長殿裁定＝git外は欠陥に非ず（`.gitignore`はwhitelist方式・既定全除外・OSS公開対象のみ許可という設計）。
問うべきは「gitに在るか」ではなく「消えたら戻せるか」。以下、この問いのみを扱う。

## ⒜ 索いた先と実測（振舞いで探索、関数名でなく実行内容を確認）

### systemd timer/service（`systemctl --user list-timers --all` + `systemctl list-timers --all`、読取のみ）

```
$ systemctl --user list-timers --all 実測=7件
auto-git-sync.timer / enter_restart_shogun_second.timer / shogun_auto_claim.timer /
secondpc-alive-monitor-v0.2.timer / shogun-self-check.timer / codex-healthcheck.timer /
launchpadlib-cache-clean.timer
$ systemctl list-timers --all（system側） 実測=12件、悉くOS標準(apt/logrotate/man-db等)ゆえ本題と無関係
```

`ExecStart`を全timer分実測し中身を確認：
- `auto-git-sync.service`→`auto_git_sync.sh`は`REPO_ROOT="$HOME/projects/multi-agent-shogun-newbuild"`（★本repo`multi-agent-shogun`ではなく別repo★）を対象とし、かつ`git fetch`+`--ff-only pull`のみ（★commit/push無し=F007遵守、backupに非ず★）。本repoのqueue/dashboard.md/memoryには一切触れない。
- 他4件（enter_restart/shogun_auto_claim/secondpc-alive-monitor/shogun-self-check/codex-healthcheck）は`ExecStart`実読の結果、悉く運用監視・自動claim・DB整合修復であり、backup/複製の類ではない。

### `crontab -l`
```
no crontab for hakudokai
```
0件。

### `scripts/**`・`shim/**`（`rsync|tar -c|cp -a |backup`の振舞い検索→ヒットfile個別に中身確認）

- `scripts/bulk_ack.sh`＝★queue/inbox/{agent}.yaml を書き換える直前に `cp "$INBOX" "${INBOX}.bak.$(date...)_bulkack"` するコードが在る★（79-90行実測）。
  ただし★実際に発火した形跡=0件★（下記「実物の有無」参照）。かつ発火しても複製先は★同一ディレクトリ（queue/inbox/）★＝ディレクトリ/ディスク単位の喪失には無力。
- `scripts/ntfy_listener.sh`＝backupコード在るが対象は`NTFY_INBOX_PATH`環境変数が指す★別のqueue★（ntfy通知用、queue/inbox配下ではない、90-107行実測で確認）。本題対象外。
- `scripts/setup_shogun_standard.sh`＝コメント中の"backup"はcodex state DB（別題材）を指す。本題対象外。
- `scripts/visual_smoke.sh`＝rsyncはスクリーンショット出力の集約用、queue/dashboard/memoryとは無関係。
- `shim/**`＝上記振舞い検索で0件ヒット。
- `shim/hakudokai/hakudokai_dashboard_sync.py`（別経路で発見、380行実読）＝★Supabase DBから最新statusを取得して`~/.openclaw/dashboard.md`（★本repoの`dashboard.md`とは別path★、デフォルト値実測）を★新規生成★する仕掛け。本repoのdashboard.mdの複製・退避ではない（向きが逆＝DB→file生成であり、file→他所への退避ではない）。

### `~/.claude/**`
```
$ /usr/bin/grep -rlE "backup|rsync|tar -c" ~/.claude/ 実測
`~/.claude/file-history/**` が多数ヒット（各fileにつき@v1〜vN形式の版が存在）
```
Claude Codeが自身のEdit toolでの編集ごとに版を残す組込機構。ただし★これはClaude Code経由の編集にのみ発火する副次的な物★であり、queue/dashboard.md/memoryを目的として作られた専用backup機構ではない。script/他processによる書換（本system全体の主たる書換経路）はこの版管理の対象外。

### git履歴・`.gitignore`
```
$ git log --oneline -- dashboard.md（全履歴）→ 2026-01-29の"chore: untrack runtime files"2件(72f627a・11173bd、同時刻06:29:36)で追跡除外。それ以前(2026-01-25発足〜01-29)は追跡されていた。
$ git check-ignore -v dashboard.md → .gitignore:7の`*`(既定全除外)にヒット、除外中
$ git check-ignore -v memory/MEMORY.md → 同上、除外中
$ /usr/bin/grep -n "^!.*queue|^!.*memory" .gitignore → !memory/・!memory/MEMORY.md.sample・!queue/・!queue/pane_registry.yaml
```
★queue/配下で唯一 `queue/pane_registry.yaml` のみ継続追跡中（gitが現在も耐久を提供）★。
memory/配下は`MEMORY.md.sample`（雛形・空の見本）のみ追跡、実物の`memory/MEMORY.md`は非追跡。
dashboard.md・queue/*.yaml(pane_registry.yaml以外)・memory/MEMORY.mdは★2026-01-29以降、git上の断面が更新されず凍結（=それ以降の変更は一切gitに残らない、6か月超前の断面のみ）★。

### `docs/**`（`backup|復旧手順|recovery|preserved|保全`等で検索）

- `docs/shogun-only-freeze-recovery.md`＝信長paneのプロセス/tmuxフリーズからの復旧手順書であり、★データ喪失時の復元手順ではない★（対象が別、除外）。
- `docs/incident_logs/2026-08-05_frozen_copies_ledger_karo_second.md`（家老second作、55行実読）＝★本題に直結する先行知見★。委員長殿の3要件「①失われない②他者が到達できる③同一性が示せる(sha)」を提示し、家老second/将軍secondの`/tmp`scratchpad上の写し（対象=個別script、queue/dashboard/memoryではない）は要件②(session UUID固有pathゆえ他sessionから到達不能・再起動でも失われ得る)を満たさず「一時退避であって保全ではない」と結論。加えて第四要件「④物が失われても復元し得る形が別に在るか」を提起し、「file単体を救えずとも記述(docs)から復元し得れば意味は救われる」との整理を残す。
- `docs/incident_logs/2026-08-06_role_canon_gitignored_preserved_copy_instructions_a1.md`（足軽1号作）＝★instructions/配下6件のみ★、2026-08-06T07:12〜07:44の★一回限り★の全文複写をgit管理下(docs/incident_logs/)へ保全した記録（HEAD=d76b025時点の断面）。人が書いたcanon（不変）ゆえ全文複写が妥当と判断された経緯。
- `docs/incident_logs/2026-08-06_role_canon_gitignored_preserved_copy_dashboard_a1.md`（同・訂正版）＝★dashboard.mdは明示的に全文複写★せず★、path・行数・sha256・HEAD等の「git外である事実」のみ保全する方針に07:14:44訂正された記録。理由＝dashboard.mdは家老・軍師が絶えず書き換える状態表（生き物）ゆえ、全文複写を残すと「保全写しの札を付けた古い状態表」が後の読者を誤読させる（幽霊正本化）危険がある、との明示判断。
- `memory/**`を対象とした同種の保全写しdocは★検索0件★（instructions/・dashboard.mdの姉妹文書に相当する物がmemoryには存在しない）。
- `queue/**`全般を対象とした専用backup/耐久runbookも★検索0件★。

## ⒝ 実物の有無・世代・最終実行刻

**scripts/bulk_ack.shの`.bak.*_bulkack`パターン＝実物0件**（`ls queue/inbox/*.bak.*_bulkack`→"No such file or directory"、コードは在るが一度も発火した痕跡が無い）。

**queue/inbox/配下の既存`.bak.*`file＝6件実測**（悉く一過性・手動/個別script起因、体系的backupに非ず、悉く同一ディレクトリ内＝ディレクトリ喪失に無力）：
```
karo.yaml.bak.20260508_213900              size=41415B  mtime=2026-05-08 21:42
ashigaru8.yaml.bak.20260505_170320         size=134684B mtime=2026-05-05 17:03
ashigaru2.yaml.bak.1777865461(epoch)       size=150429B mtime=2026-05-04 12:31（epoch復号=2026-05-04T12:31:01+09、一致）
ashigaru4.yaml.bak.20260804_135931_a4manual        size=111307B mtime=2026-08-04 13:59
ashigaru4.yaml.bak.20260804_140623_a4manual_flock  size=114863B mtime=2026-08-04 14:06
ashigaru2.yaml.bak.20260507_misroute       size=142162B mtime=2026-05-07 17:31
```

**git（queue/pane_registry.yamlのみ）＝継続追跡中、最終commitは通常のgitログで随時遡及可能（本票では個別コミット追跡は範囲外・存在のみ確認）。**
**git（dashboard.md・他queue/*.yaml・memory/MEMORY.md）＝2026-01-29T06:29:36+0900の2 commit（72f627a・11173bd）を最後に凍結、以降6か月超の変更は反映されず。**

**instructions/6件の一回限り全文保全＝HEAD=d76b025時点（2026-08-06T07:19:27+09時点測定）の1世代のみ。queue/dashboard/memoryはこの型の保全対象に★入っていない★。**

## ⒞ 無い、と書く（索いて確認した根拠）

★queue/**・dashboard.md・memory/** を対象とした、体系的（定期実行・専用設計）な私有backup／複製先／耐久機構は、上記の索索範囲内では見つからなかった★。

見つかった物は悉く以下のいずれかに該当し、「体系的backup」の要件を満たさない：
1. 別repo・別対象を扱う仕組み（auto-git-sync＝別repo、DB→dashboard生成＝向きが逆）
2. コードは存在するが未発火（bulk_ack.shの`.bak.*_bulkack`＝0件）
3. 発火はしたが一過性・手動・同一ディレクトリ内（既存`.bak.*`6件）
4. Claude Code編集時の副次的版管理（対象範囲が編集経路に限定、queue/dashboard/memory専用ではない）
5. 明示的に「複写しない」と決定済（dashboard.md、2026-08-06 07:14訂正）
6. 対象がqueue/dashboard/memoryではなく別カテゴリ（instructions/6件の一回限り保全）
7. git自体は`queue/pane_registry.yaml`のみ継続、他は2026-01-29断面で凍結

## ⒟ runbook（復旧手順書）の有無

`docs/**`を索いた結果、★queue/**・dashboard.md・memory/** の「喪失後にどう復元するか」を扱った文書として作られた物は0件★。
`docs/shogun-only-freeze-recovery.md`はプロセス/pane復旧であり対象が異なる（除外）。
`docs/incident_logs/2026-08-05_frozen_copies_ledger_karo_second.md`は★手順書ではなく知見（3要件+第四要件の整理）★であり、之に従って何かを実際に試した形跡（実行ログ・commit等）は本票の索索範囲内では見当たらなかった。
∴ runbookそのものが存在せず、従って「試された形跡」も論じる前提を欠く。

## ⒠ 己の手で為した事

- `systemctl --user list-timers --all` / `systemctl list-timers --all` を実行、全19 timerを実測・列挙
- 該当7 user timerの`systemctl --user cat <unit>`で`ExecStart`/`Description`を全件実読
- `crontab -l` を実行（0件）
- `/usr/bin/grep -rlE "rsync|tar -c|tar czf|tar cvf|cp -a |cp -r.*archive|backup" scripts/ shim/` で振舞い候補を抽出、ヒット4件+0件を個別に`sed -n`で中身確認
- `shim/hakudokai/hakudokai_dashboard_sync.py`（380行）を全読し、出力先pathとデータの向き（DB→file生成）を確認
- `~/.claude/`配下を`grep -rlE`で走査、`file-history/**`の存在と性質（Edit tool副次物）を確認
- `git log --all -- dashboard.md/memory//queue/**` で追跡履歴の有無・untrack commit（72f627a・11173bd）の日時を`git show -s`で実測
- `git check-ignore -v dashboard.md` `git check-ignore -v memory/MEMORY.md` で現在の除外状態を実測
- `/usr/bin/grep -nE "^!.*(queue|dashboard|memory)"` .gitignore で whitelist entry を実測
- `df -h .` でrepoの設置filesystemを確認（`/dev/sdd`直下・`/mnt/c`ではない＝Windows側自動同期の根拠は見当たらず）
- `docs/**`を`backup|復旧手順|recovery|disaster|preserved|保全`等の複数語で`grep -rliE`し、ヒットfileを個別に開いて対象を確認（`shogun-only-freeze-recovery.md`・`frozen_copies_ledger_karo_second.md`・`role_canon_gitignored_preserved_copy_{instructions,dashboard}_a1.md`の4件を実読）
- 既存`queue/inbox/*.bak.*`6件を`stat -c`で実測（size/mtime）、epoch形式1件をPython `datetime.fromtimestamp`で復号し他の実測値と照合
- `scripts/bulk_ack.sh`の`.bak.*_bulkack`パターンが実際に現存するか`ls`で確認（0件）
- backupは一切走らせず、復旧は一切試みず、`queue/`への書込・`.gitignore`への変更は一切行っていない
- `queue/inbox/_dead_letter_second.yaml`には一切触れていない（本題対象外、grep/wc/cat不使用）

## 数の扱い

令に個数の明示は無し（「棚卸しせよ」）。
測時=2026-08-06T21:22:11+09:00／器=上記各コマンド（`systemctl`/`crontab`/`grep`/`git`/`stat`/`ls`）／範囲=上記⒜列挙の全探索対象。
以上（読めぬfileは無かった。`_dead_letter_second.yaml`は範囲外につき対象外）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。

## 裁定は為さず、材料のみ

本票は「backupが在るか」の実測材料に留める。「これで足りるか」「増やすべきか」の裁定は当職の権外。
