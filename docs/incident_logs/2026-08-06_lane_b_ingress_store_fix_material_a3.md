# Lane B — 入口・器を直すべきか否かの材料（足軽3号）

- 下命: 家老second msg_20260806_215058_9d846fd4（21:50:58）
- 測時（本票起筆）= 2026-08-06T21:55:44+09:00（`date -Iseconds` 実行結果）
- 器＝`/usr/bin/grep -rn`／`Read` tool（`scripts/diagnose.sh` 実読）／`ls -la`／`crontab -l`／`systemctl --user list-timers --all`／`findmnt`／`df -T`／`stat`
- 範囲＝`scripts/diagnose.sh` 全文（実読）、`docs/runbooks/*.md` front matter 全8件、`docs/error-design-medical.md`、`docs/runbooks/err-ekarte-001.md`、`~/.openclaw/`、`/tmp/`、systemd --user timer 一覧、crontab
- 禁の順守＝`night_mode` flag／`disable_night_mode` flag／`/tmp/morning_digest.json` のいずれも作成せず（`touch`/`mkdir`/書込コマンド0件）。`scripts/diagnose.sh`・`scripts/morning_digest_send.sh` のいずれも実行せず（呼出0件）。`_dead_letter_second.yaml` 不触。`/tmp/resimg-*` 不触。読取のみ。

## ⒜ 入口（`~/.openclaw/night_mode`）＝誰が立てる筈であったか

**己の手で `scripts/diagnose.sh` を実読**（L1-170、L12-17・L118-155 を含む）。

- `NIGHT_MODE_FLAG="$HOME/.openclaw/night_mode"`（L15）。`check_night_mode()`（L118-155）は**この file の存在有無を読むだけ**（L120 `if [[ ! -f "$NIGHT_MODE_FLAG" ]]; then return 0`）。
- 実測＝`/usr/bin/grep -rn "night_mode" . --include=*.sh --include=*.py --include=*.md --include=*.yaml --include=*.yml` を己の手で実行。ヒットは `scripts/diagnose.sh` 自身の read 箇所（L15,120-122,262,265）と `docs/incident_logs/*` の既存所見・`queue/reports/*` の監査票のみ——**この flag を作成/削除する code は repo 内に0件**。
- 一方、`docs/runbooks/err-ekarte-001.md:53-59`「夜間モード（理事長殿の睡眠保護）」節を己の手で実読。設計としては「22:00-7:00 (JST) は**自動的に** night mode」「理事長フラグ `~/.openclaw/disable_night_mode` で無効化可」と記す——**時刻で自動 ON・明示 OFF flag** という設計。
- ∴ **doc の設計どおりなら「誰かが立てる」のではなく「時刻判定 code が自動で立てる（または動的に判定する）」筈であった**。しかし実装（`diagnose.sh`）にその時刻判定 code は無い（`date`/時刻比較を用いた night_mode 関連分岐は L1-170 中に0件、`/usr/bin/grep -n "22:00\|07:00\|hour" scripts/diagnose.sh` 実行=ヒット0件）。
- ∴ 結論＝**「誰が立てる筈であったか」の答えは doc 上は「時刻判定 code（未実装）」であり、人間（理事長殿含む）が手動で `touch` する運用は、repo内のどの runbook・手順書にも記載を見つけられず**（`/usr/bin/grep -rn "touch.*night_mode\|理事長.*night_mode手動" docs/ instructions/ CLAUDE.md` 実行=ヒット0件）。
- 実測（測時同時点）＝`ls -la ~/.openclaw/night_mode ~/.openclaw/disable_night_mode` → 両方とも `No such file or directory`（現に未設定）。

## ⒝ 器（`/tmp/morning_digest.json`）＝誰が書く筈であったか・`/tmp`ゆえ再起動で消えるか

**書く筈であった主体**: `check_night_mode()`（`scripts/diagnose.sh` L130-150）自身。`night_mode` flag が在り、かつ `night_policy != immediate` の時、`mkdir -p` の後 Python で JSON 配列へ追記する。★別の書き手は repo 内に存在しない★（`/usr/bin/grep -rn "MORNING_DIGEST\|morning_digest.json" --include=*.sh --include=*.py .` 実行、ヒットは `scripts/diagnose.sh`（書込）と 本件で足軽3号が新設した `scripts/morning_digest_send.sh`（読取専用・既に4061f26+本コミットで存在）のみ）。∴ **器は入口と同一関数に同居しており、入口さえ生きれば器は自動的に機能する**（別途「誰かが器を書く」運用は不要）。

**`/tmp`ゆえ再起動で消えるか——己の手で実測**:

```
findmnt /tmp            → 出力無し（独立マウントではない）
df -T /tmp               → /dev/sdd  ext4  1055762868K  6% used  マウント先 /
stat /tmp                → Birth: 2026-04-28 15:12:14  Modify: 2026-08-06 21:54:29
find /tmp -maxdepth 1 -type f -mtime +1 | head -5 → /tmp/frp.sh 等、複数日〜数ヶ月前の file が現存
```

∴ **当PC（WSL2/Ubuntu 無印）の `/tmp` は tmpfs ではなく、root と同じ ext4 パーティション上の通常ディレクトリ**。`Birth: 2026-04-28` は約3ヶ月半前——その間に少なくとも複数回の WSL/プロセス再起動があった蓋然性が高いにもかかわらず `/tmp` 配下の古い file が現存。`systemctl --user list-timers --all`／`/etc/tmpfiles.d`／`/usr/lib/tmpfiles.d/*.conf` を確認したが `/tmp` を定期的に空にする timer は当PC（`--user`スコープ）に見当たらず（`/usr/lib/tmpfiles.d/` はシステム標準の物のみで `tmp.conf` 系の存在有無・発火実績までは本票では未測——★systemd-tmpfiles のシステムスコープ設定は `--user` 権限では読取・検証しきれず未測★）。

★∴ **「`/tmp` ゆえ再起動で消える」という当初令の前提は、当PCの実測からは支持されない（少なくとも過去3ヶ月半、消えていない）**★。ただし「実際にWSLを完全再起動（`wsl --shutdown`）した際に消えるか」は破壊的操作となるため本票では**未測**（禁＝script/破壊操作を試すな、の範囲内で測れる限界）。

## ⒞「出口だけ直った今」何が起き得るか

現況（本票測時点で再確認）＝`~/.openclaw/night_mode` 不在・`/tmp/morning_digest.json` 不在・`crontab -l`=`no crontab for hakudokai`・`diagnose.sh`/`morning_digest_send.sh` を呼ぶ timer/cron は `systemctl --user list-timers --all`（実測7件）中に0件。

㈠ **何も起きぬ（入口が死んでおるゆえ）＝★現況はこれ★**。`night_mode` flag が無いので `check_night_mode()` は L120 で即 `return 0`——器（`/tmp/morning_digest.json`）は一度も書かれず、新設した reader/sender（`scripts/morning_digest_send.sh`）を仮に手動実行しても「digest file 不在→0 send」（本コミットの T-002 相当）で終わる。

㈡ **入口が生きれば動く（部分的に真だが要注意）**。仮に `~/.openclaw/night_mode` を人が touch すれば、`check_night_mode()` が発火し器へ蓄積が始まる。★然れど reader/sender（出口）自体を7:30に走らせる timer/cron は本工区の境㈠により未装着（installer は `--apply` を明示 REFUSE する作り）★——∴ 器に溜まっても、**誰かが `morning_digest_send.sh` を手動で叩かない限り、7:30に自動送信はされない**。「入口が生きれば動く」は「器への蓄積」に限っては真だが、「7:30の自動送信」まで含めると**別の未装着ピース（出口の起動trigger）が要る**——これは境㈠により当職の権外（本工区が意図的に据え置いた部分）。

㈢ **入口が生きてもなお動かぬ（器の所為）＝当職の実測では支持されない**。器（`/tmp/morning_digest.json`書込）は入口と同一関数内にあり、入口さえ発火すれば器も同時に機能する（⒝参照）。器固有の障害（権限・path不在等）は `mkdir -p "$(dirname "$MORNING_DIGEST")"` があるため見当たらず。∴ ㈢に該当する既知の障害は**現時点で0件（判じ難きは無し）**——ただし「/tmp の永続性」自体が当初想定と異なる（⒝）ため、器の**内容が「意図通りの永続性」を持つかは別問題**（消えないことが判明した一方、それは「揮発を避けたい」という当初令の意図とは別の理由による偶然の永続——設計として保証された永続性ではない）。

## ⒟ 直すなら誰の権か

- **入口の是正**（自動時刻判定 code の新設 or 手動運用手順の制定）＝**我らの権内に非ず**。doc（`err-ekarte-001.md`）と code（`diagnose.sh`）のどちらを正とするかは設計判断であり、令に無い（本工区は「材料」のみ・「裁定は為すな」と明記）。
- **器の是正**（`/tmp`から永続pathへの移設）＝実測上は「今のところ消えていない」ため緊急性は低いが、設計として永続性を保証したいなら code 変更が要る——これも **我らの権内に非ず**（既存 `diagnose.sh` は本工区の境「既存通知経路はbyte不変」の対象）。
- **出口の起動trigger（7:30 timer/cron 装着）**＝本工区の境㈠で明示的に据え置かれた部分。装着には systemd/cron への実装置が要り、**運用への実影響を伴う変更ゆえ上位の裁定要**（家老second/将軍second経由）。

∴ 三点とも**当職の権内では直せず、上位裁定が要る**。材料の要旨＝「入口は doc/code の設計不一致（人間手動 touch の手順書は0件）」「器は入口と同一機構ゆえ入口が直れば自動的に動くが、/tmp永続性は当初令の前提と異なり実測では消えていない（設計保証ではなく偶然）」「出口の自動起動は境㈠によりそもそも本工区の対象外」。

## ⒠ 己の手で為した事（証跡コマンド）

```
Read scripts/diagnose.sh (offset=1, limit=170)                                  # 全体構造・L12-17/118-155 実読
/usr/bin/grep -rn "night_mode" --include=*.sh --include=*.py --include=*.md .   # 入口を書くcode=0件を自分で確認
/usr/bin/grep -rn "morning_digest.json|MORNING_DIGEST" --include=*.sh --include=*.py --include=*.md .
/usr/bin/grep -n -B2 -A15 "夜間モード|night.mode|night_mode" docs/error-design-medical.md
sed -n '45,65p' docs/runbooks/err-ekarte-001.md                                 # 夜間モード節 実読
/usr/bin/grep -rn "disable_night_mode|touch.*night_mode|理事長.*flag|夜間モード" docs/ CLAUDE.md instructions/
findmnt /tmp ; df -T /tmp ; stat /tmp ; find /tmp -maxdepth 1 -type f -mtime +1  # /tmp揮発性の自前実測
systemctl --user list-timers --all ; crontab -l                                 # 起動trigger不在の自前確認
ls -la ~/.openclaw/ ~/.openclaw/night_mode ~/.openclaw/disable_night_mode /tmp/morning_digest.json  # 現況再確認
```

以上（読めぬfileは無かった・flag/器を作成せず・script を実行せず・CLAUDE.md/canon 未改変・`/tmp/resimg-*` 未改変）。

## 発注三行（軍師second 提出時 必須）

1. 同意を探すな・潰しに掛かれ。
2. 返信に己の手で為した事（試した command／当たった file／立てた反例）を書け。
3. 被監査者（当職）の語を引いて「成立」と書くな——引くなら己が引き直したと明記せよ。

report_to: karo-second
