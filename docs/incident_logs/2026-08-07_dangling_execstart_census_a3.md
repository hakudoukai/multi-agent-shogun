# 当repo内 unit/timer/service 定義 — ExecStart 悉皆実在census (足軽3号)

owner: ashigaru3 / report_to: karo-second
task key: `current_order_10_20260807_001200_DANGLING_EXECSTART_CENSUS` (mode=read-only)
測時: 2026-08-07T00:12〜00:22 JST（器=`find`/`/usr/bin/grep -r`/`sha256sum`/`stat`/`git`/`ls`・date -Iseconds実値）
主repo HEAD: `5da21919d74b780df14683d276a81faa6305e476`（branch `feat/dd169-d006-conditional-exception`、2026-08-06T23:52:33+09:00 commit）
主repo path: `/home/hakudokai/projects/multi-agent-shogun`（★本 census が「主repo」と呼ぶ対象＝当 checkout★）

★実行内容＝読取のみ（`find`/`grep -r`/`sha256sum`/`stat`/`ls`/`git log`,`git show`,`git branch`,`git remote -v`,`git rev-parse`/`crontab -l`）。
systemctl enable/start/link/daemon-reload・commit・push・merge・実 send・機構への再試行 ＝ 悉く 0（実行せず）★

## 母集団宣言（★除外を書かぬ★・使ったcommandそのまま）

```
find . -type f -name "*.service"
find . -type f -name "*.timer"
/usr/bin/grep -rl "ExecStart=" .
/usr/bin/grep -rl "crontab" .
/usr/bin/grep -rl "systemctl enable\|systemctl link\|systemctl daemon-reload" .
/usr/bin/grep -rnE '^\s*[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+\s+[0-9*/,-]+\s+\S+' .
/usr/bin/grep -rl "^\[Unit\]" .
```

`find` は `.git`/`.venv`/`node_modules` 等を除外せず全数探索（`--exclude` 未使用）。`/usr/bin/grep -r`（`git grep` に非ず）を用いた理由＝
`git grep` は `.gitignore` 対象を無警告 skip する既知欠陥（本隊 memory `grep-git-grep-silently-skip-gitignored`）を避ける為。

## ㈠ 当repo内の unit/timer/service 定義・全数（8 file・唯一の population）

| # | file | 種別 |
|---|---|---|
| 1 | `scripts/watchdogs/enter_restart_shogun_main.service` | service |
| 2 | `scripts/watchdogs/enter_restart_shogun_second.service` | service |
| 3 | `scripts/watchdogs/enter_restart_shogun_third.service` | service |
| 4 | `scripts/watchdogs/enter_restart_commander.service` | service |
| 5 | `scripts/watchdogs/enter_restart_shogun_main.timer` | timer |
| 6 | `scripts/watchdogs/enter_restart_shogun_second.timer` | timer |
| 7 | `scripts/watchdogs/enter_restart_shogun_third.timer` | timer |
| 8 | `scripts/watchdogs/enter_restart_commander.timer` | timer |

`*.timer` 4件はいずれも `Unit=<対応する.service>` を参照するのみ（自身に `ExecStart` を持たぬ・独自 path なし）。
実行対象path検査は4件の `.service` の `ExecStart=` 行に限られる（`ExecStartPre=/bin/mkdir` は `/bin/mkdir` という標準binaryであり主repo/newbuild いずれにも属さぬ実在確認対象外 — 触れぬ）。

### cron相当＝当repo内に定義 0件（判定＝実測・以上）

`crontab -l` を当PCで実行 → `no crontab for hakudokai`（★実測・空★）。
`crontab` の語を含む file 群（`scripts/lib/ignored_active_predicate.sh`／`scripts/fukuincho_detect_stale_cli.sh`／`shim/hakudokai/hakudokai_heartbeat_archive.py`／`hakudokai_dashboard_sync.py`／`hakudokai_heartbeat_check.py`／各 incident_logs／各 queue report）を全件開いて中身を確認した結果、
いずれも①`crontab -l` を**読取る**検出述語（定義に非ず）、②`/path/to/...` 等の**プレースホルダー**を用いた設置**例**のdocstring/comment、のいずれかであり、
**実際に登録された cron エントリの定義は当repo内に0件**（母集団＝上記 grep 結果 15 file・全件を目視で分類・以上）。
5フィールド cron 構文の直接埋込み検索でも一致は `shim/hakudokai/*.py` の3例のコメント（同上・プレースホルダー）と `.venv` 内 chardet の無関係バイト列のみ。

`^\[Unit\]` 検索でも上記4 `.service` + `docs/runbooks/enter_restart_shogun_reference.md`（skeleton 掲載doc・定義に非ず）のみヒット。他に埋込み定義0件。

★他PCで稼働中の live unit（`shogun-self-check.service`／`shogun_auto_claim.service`／`senmu-desktop-*`／`honbucho-*`／`dentalbi-*`／`secondpc-alive-monitor*`／`auto-git-sync.*`）は
当PCの `~/.config/systemd/user/` には実在するが、当repo内に対応する `.service`/`.timer` ファイルも埋込み定義も**一件も無い**（各 unit 名で grep→0件・以上）。
∴ これらは本census の母集団（＝当repo内定義）に**含まれぬ**（射程外・当repoに定義が無い物は「実在確認」の対象になり得ぬ）。

## ㈡＋㈢ ExecStart 実行対象path — 主repo 実在確認（4件・全件実測）

| # | file (ExecStart) | 記載path（`%h`展開後・`%h`=`/home/hakudokai`） | 主repoに実在するか | 実在するならどこか |
|---|---|---|---|---|
| 1 | `enter_restart_shogun_main.service` | `/home/hakudokai/projects/multi-agent-shogun-newbuild/scripts/watchdogs/enter_restart_shogun_main_watchdog.sh` | ★否★（主repo内に此のpathは無い・当repoの構造は `.../multi-agent-shogun/scripts/watchdogs/...` であり `-newbuild` disk上に実在（822 byte定義のExecStart文字列と完全一致）。**別repository**（`git remote -v`＝`origin git@github.com:hakudoukai/multi-agent-shogun-newbuild.git`）。★主repoの他branchではない★（`git branch -a`／`git ls-tree -r HEAD` で "newbuild" 文字列 0件・主repoのどのbranchにもこの絶対pathは存在せぬ）。 |
| 2 | `enter_restart_shogun_second.service` | `/home/hakudokai/projects/multi-agent-shogun-newbuild/scripts/watchdogs/enter_restart_shogun_second_watchdog.sh` | ★否★（同上） | 同上（別repository `multi-agent-shogun-newbuild`、branch=main）。★かつ現に live★＝`~/.config/systemd/user/enter_restart_shogun_second.service` は該当pathへの **symlink実体**（本census で実測・足軽6号 a6 の先行census 2026-08-06T02:55 とも一致）。 |
| 3 | `enter_restart_shogun_third.service` | `/home/hakudokai/scripts/enter_restart_shogun_third_watchdog.sh` | ★否★（`~/scripts/` 直下に此の名のfile無し・実測=`ls ~/scripts/` で2件のみ存在=`codex_state_healthcheck.sh`／`shogun_auto_claim_rest.sh`、該当file含まず） | **見付からず**（`$HOME` 配下 maxdepth 6 の全域探索でも同名fileは `.../multi-agent-shogun/scripts/watchdogs/...`・`.../projects/multi-agent-shogun/scripts/watchdogs/...`（＝主repo自身）の2箇所のみ・いずれも記載pathと構造が異なる＝`watchdogs/`副階層が記載pathに欠落）。third_pcでの実在は★未確認★（SSH禁・当census境界外）。 |
| 4 | `enter_restart_commander.service` | `/home/hakudokai/scripts/enter_restart_commander_watchdog.sh` | ★否★（同上・`~/scripts/`直下に無し） | 同上（見付からず・主repo自身の `scripts/watchdogs/enter_restart_commander_watchdog.sh` は構造が異なり不一致）。third_pcでの実在は★未確認★。 |

### 設計意図の補足（★裁定に非ず・commit historyの実測のみ★）

`git show 86e5fc5` を実測（read-only）した所、#1/#2 の `-newbuild` path は事故ではなく **副院長令 baabd1ca【固め手順】②「enter_restart 4ユニット配備（両PC newbuild配下）順守」に基づく意図的記載**（commit message原文に明記）。
一方 `docs/runbooks/enter_restart_shogun_reference.md` §4.1 が掲げる skeleton の `ExecStart` は `%h/scripts/enter_restart_shogun_<pc>_watchdog.sh`（flat配置・手動copy配備手順§2.2前提）であり、#3/#4 はこの skeleton 記法と一致する一方、#1/#2 は同じ skeleton から外れた別方式（newbuild配下で直接実行）を採る。
★2種の記法が同一репоの4 unit間に混在している事実のみを記す。優劣・正誤の裁定は当職の権限外ゆえ行わぬ★。

## ㈣ 結論（述語）

**dangling ExecStart（主repo基準）＝ 非0（4/4）。**

主repo内に定義された `.service` 4件全てについて、`ExecStart=` が指す絶対pathは主repo checkout内のいかなる場所にも一致しない：
- 2件（main/second）＝ 副院長令に基づき意図的に**別repository**（`multi-agent-shogun-newbuild`）を指す設計。当該pathは**そちらには実在**（内容実測済）。
- 2件（third/commander）＝ 記載pathは `$HOME` 配下のどこにも実在確認できず（当PC上）。third_pc上の実在は未確認（境界外）。

★上記「非0」は「主repo内に定義された.serviceのExecStartが主repo自身の中では完結しない」という事実命題であり、
「稼働に支障がある」という運用判断とは別軸（#2 second.service は現に別repo経由で live 稼働中）。両者を混同せぬよう分けて記した。★

## 監査体制・提出

三者監査は暫定二者制（軍師second + Gemini。Codex leg停止中・SAFETY裁定 seq132707）。本票を軍師second へ提出。
発注三行を付す＝①同意を探すな・潰しに掛かれ ②己の手で為した事（試したcommand／当たったfile／立てた反例）を書け ③被監査者の語を引いて「成立」と書くな。

## 【本工区で己が直した誤り】

初動では `.service`/`.timer` の grep一致（`ExecStart=`）だけで母集団を確定させかけたが、
`docs/runbooks/enter_restart_shogun_reference.md` の skeleton 記述と commit history (`86e5fc5`) を実測せずに
「4件とも同型の誤り」と一括りに書きかけた。実測の結果、main/second と third/commander は**別の記法・別の設計意図**（意図的別repo参照 vs 手動配備手前提の記法）であると判明し、報告を分けて書き直した。

## 判じ得ぬ点（推して埋めず・以上）

1. third_pc上で `~/scripts/enter_restart_shogun_third_watchdog.sh` および `~/scripts/enter_restart_commander_watchdog.sh` が実在するか＝★未確認★（当census境界＝SSH禁・third_pcは環境部長殿専権）。
2. 当repoに定義の無い他 live unit（`shogun_auto_claim.service` 等）が別途どこかに source管理されているか＝★未確認★（母集団を当repo内に限定した為・射程外と判じたが射程の当否は上位の裁定事項）。

## 禁の遵守確認

実 send=0／systemctl enable・start・daemon-reload=0／commit=0／push=0／merge=0／機構が拒みし物への再試行=0（本工区中、機構からの拒否は発生せず）。
worktree／lane に一字も触れず（当census は主repo checkout上のread-onlyのみ）。
