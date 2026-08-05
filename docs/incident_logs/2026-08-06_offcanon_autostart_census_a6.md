# 正本の外を指す自動起動・悉皆列挙 (足軽6号、2026-08-06・家老second下命)

★★読取のみ(systemctl list-unit-files/show/cat・crontab -l・grep実施のみ)。systemctlの
enable/disable/start/stop/mask・symlink張替・unit編集・checkout操作は一切行っていない。★★
測時=2026-08-06T02:55:07+0900(date -Iseconds実行結果)。HEAD=46939a4b93c1ce12c02f243180c4cce48d7bae2c
(git rev-parse HEAD実行結果)。

## 母集団 (実測・命令+出力)

$ systemctl --user list-unit-files --type=service --type=timer --no-pager | wc -l
44 (OS標準・デスクトップ環境の物を含む全数)

このうち本プロジェクト関連と判じたカスタムunit=19種(service 13 + timer 6、対応関係あり)を対象とした。
OS標準(dbus/gpg-agent/dconf/at-spi/wslg-session/snapd/systemd-*/ssh-agent/keyboxd/dirmngr/
pk-debconf-helper/launchpadlib-cache-clean/session-migration)は対象外(明記)。

$ crontab -l
no crontab for hakudokai

$ grep -n "multi-agent-shogun" ~/.bashrc ~/.profile ~/.bash_profile
(該当なし・0件)

**∴ cron・shell rc経由の自動起動=0件(測って0件)。**

## ⒜⒝⒞⒟⒠ 表 (systemd unit 19種、実測)

| unit | 状態 | ExecStart等の指す先 | 正本か別木か | unit file自体がsymlinkか |
|---|---|---|---|---|
| auto-git-sync.service/.timer | enabled | `.../multi-agent-shogun-★newbuild★/scripts/auto_git_sync.sh` | ★別木★ | 否(実file) |
| better-ccflare.service | disabled | `~/.local/bin/better-ccflare` | 対象外(repo外の独立tool) | 否 |
| codex-healthcheck.service/.timer | enabled | `~/scripts/codex_state_healthcheck.sh` | 対象外(別tree・repo無関係) | 否 |
| dentalbi-provider-status-first.service | enabled | `~/.local/bin/provider_status_first.py` | 対象外 | 否 |
| dentalbi-secondpc-receiver.service | enabled | `.../multi-agent-shogun/shim/.../hakudokai_secondpc_receiver.sh` | 正本 | 否 |
| dentalbi-secondpc-watcher.service | enabled | `.../multi-agent-shogun/shim/.../hakudokai_secondpc_watcher.sh` | 正本 | 否 |
| **enter_restart_shogun_second.service/.timer** | **linked+enabled** | `.../multi-agent-shogun-★newbuild★/scripts/watchdogs/enter_restart_shogun_second_watchdog.sh` | **★別木★** | **★是・symlink実体★** |
| honbucho-downlink-watcher.service | enabled | `~/hermes-departments/honbucho/bin/...` | 対象外(hermes別系統) | 否 |
| honbucho-local-inbox-watcher.service | enabled | `.../multi-agent-shogun/scripts/inbox_watcher.sh honbucho ...` | 正本 | 否 |
| openclaw-gateway.service | enabled | `/usr/lib/node_modules/openclaw/...` | 対象外 | 否 |
| secondpc-alive-monitor-v0.2.service/.timer | static/enabled | `.../multi-agent-shogun/scripts/alive_to_productive_monitor_v0_2_once.sh` | 正本 | 否 |
| senmu-desktop-inbound-watcher.service | enabled | `.../multi-agent-shogun/shim/.../senmu_desktop_route_watcher.sh` | 正本 | 否 |
| senmu-desktop-outbound-watcher.service | enabled | 同上(outbound) | 正本 | 否 |
| shogun-self-check.service/.timer | enabled | `.../multi-agent-shogun/scripts/shogun_self_check.sh` | 正本 | 否 |
| shogun-tunnel.service | enabled | `~/bin/shogun-tunnel.sh` | 対象外 | 否 |
| **shogun_auto_claim.service/.timer** | enabled | ExecStart=`~/scripts/shogun_auto_claim_rest.sh`(第三の木)・**WorkingDirectory=`.../multi-agent-shogun-★newbuild★`** | **★別木(WorkingDirectoryのみ)★** | 否 |
| shogun_dispatcher.service | enabled | `~/shogun_dispatcher/shogun_dispatcher.py`(第三の木、repoとも newbuildとも別) | 対象外(独立tree) | 否 |
| shogun_watchdog.service | disabled | `.../multi-agent-shogun/shim/.../hakudokai_watchdog.sh` | 正本(但しdisabled=不稼働) | 否 |

## ⒠ 別木を指す3件の差分実測 (sha256+行数差)

$ sha256sum scripts/watchdogs/enter_restart_shogun_second.service /home/hakudokai/.config/systemd/user/enter_restart_shogun_second.service
be63a5631072764f4d3152c0abde5271f01d2376d61a28339bde15a90dea89d7  (両方・完全一致)

**∴ symlink先(newbuild)のunit file内容は、現時点で正本の同名fileと★sha完全一致★(中身は同一・
場所のみ別木)。**

$ sha256sum scripts/watchdogs/enter_restart_shogun_second_watchdog.sh /home/hakudokai/projects/multi-agent-shogun-newbuild/scripts/watchdogs/enter_restart_shogun_second_watchdog.sh
7a6650aa...(正本) / 93c65924...(newbuild) ——★不一致★
$ diff scripts/watchdogs/enter_restart_shogun_second_watchdog.sh /home/hakudokai/projects/multi-agent-shogun-newbuild/scripts/watchdogs/enter_restart_shogun_second_watchdog.sh
31a32
> export ER_HEARTBEAT_MODE="${ER_HEARTBEAT_MODE:-events_only}"

**∴ 差=1行追加のみ(環境変数の既定値設定)。正本は2026-07-20付・newbuildは2026-07-15付
(★下命が戒めた「旧いcheckoutが旧い版とは限らぬ」の実例=日付は正本の方が新しいが、
実際に走っておるのはnewbuild側の版★)。**

$ find . -iname "auto_git_sync.sh"
(該当なし・正本には★この名のfileが一度も存在しない★)

**∴ auto-git-sync.service/.timerが指す`scripts/auto_git_sync.sh`は、正本repoには
★存在した事がない(比較対象そのものが無い)★——「旧版」ではなく「正本側に相当物なし」の型。**

## 【本工区で己が直した誤り】

初稿で対象unitを「enter_restart_shogun_second関連の1組のみ」と決め打ちしかけたが、下命が
「全件」を求めている事を思い出し、全19種を実測し直した所★auto-git-sync.service/.timer
(既知例とは別のnewbuild依存)と shogun_auto_claim.service(WorkingDirectoryのみnewbuild)の
2件を追加発見★した。将軍second殿の実測(2件のみ確認)も母集団を測っていなかった、との
下命本文の指摘が、当職自身の初稿にも同じ形で現れかけた。

## ★母集団漏れの自己申告★

1. OS標準unit(dbus等)は「本プロジェクト関連ではない」と当職が判じて対象外としたが、
   この判断基準自体を第三者が検めていない。
2. `shogun_dispatcher.service`(`~/shogun_dispatcher/`)・`codex-healthcheck.service`
   (`~/scripts/`)等の「第三の木」(正本でもnewbuildでもない独立tree)は、本下命の主題
   (正本 vs newbuild)の対象外と判じたが、これらも広義には「正本の外」であり、下命の
   文言次第では母集団に含めるべきだったかもしれない。
3. `honbucho-downlink-watcher.service`(hermes-departments系)も同様の理由で対象外とした。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。

以上、正本の外を指す自動起動・悉皆列挙への応答。systemctl操作・symlink・unit編集・checkout操作
いずれも一切行っていない。
