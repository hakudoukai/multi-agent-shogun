# leg C 「無人6箇所」独立再測 (足軽7号、2026-08-05)

家老second殿下命(msg_20260805_124007_b59d1a11、出所=将軍second令msg_20260805_123441_86285f5d、執行=karo-second)への応答。
足軽3号殿の測定(`2026-08-05_legC_unattended_caller_survey_a3.md`、52行/sha256=0a5e233053dec548)を
★独立再測★(足軽1号の17箇所台帳=同一母集団ゆえ彼では独立に成らず・当職が適任と判じられた)。測定のみ、凍結に触れず。

台帳file・a3殿/a1殿成果物・影file・dd189・process、いずれも不触(Read/grep/ps/systemctl/find/gitのみ)。
bats実行なし(止血継続中)。commit・push・stage一切なし。

断面=2026-08-05T12:45:30+0900。base_commit=502cbfe(実測=HEAD一致)。

参照した正本: `docs/incident_logs/2026-08-05_legC_unattended_caller_survey_a3.md`(全52行)/
`docs/incident_logs/2026-08-05_legC_17site_ledger_a1.md`(母集団確認用、冒頭のみ)/
`scripts/agent_periodic_push.sh`/`scripts/inbox_watcher.sh`(L1610-1630)/`scripts/stop_hook_inbox.sh`/
`shim/hakudokai/hakudokai_activity_monitor.sh`/`scripts/ntfy_listener.sh`/`shim/hakudokai/hakudokai_start_watchers.sh`/
`shutsujin_departure.sh`/`scripts/watcher_supervisor.sh`/`scripts/watcher_supervisor_third.sh`/
`.claude/settings.json`/`scripts/agent_health_check.sh`(全文Read)。

---

## 実測結果 — 6件

| # | 対象 | ⒜起動主体(実測) | ⒝失敗の人目経路 | ⒞判定 |
|---|---|---|---|---|
| 1 | `agent_periodic_push.sh` | 自己文書「systemd user timerで15分毎実行」。★実測=`systemctl --user list-units --all`/`list-unit-files`/`list-timers --all`いずれも★該当0件★(陽性対照=同コマンドで`auto-git-sync.timer`等★実7件★を検出=検索機構は健全)。`crontab -l`=無し・`/etc/cron.d`=無し。 | `/tmp/agent_periodic_push.log`★自体が存在せず★(実測=`ls`で確認、`/tmp`は他log群Aug03-05分が現存し消去されていない事を陽性対照で確認済) | **無人(確定)——自己文書の launcher は当hostに実在せず、実行痕跡もゼロ** |
| 2 | `inbox_watcher.sh` L1619-1621(TOKEN-WARN) | `scripts/watcher_supervisor.sh:57`/`watcher_supervisor_third.sh:68`に`setsid nohup bash scripts/inbox_watcher.sh ... >>"$log_file" 2>&1 &`実測(grep直接確認)。現に12process稼働中を`ps -ef`で実測(例:ashigaru7自身のwatcher含む)。 | stderrは`/tmp/watcher-<agent>.log`へ着地(setsid+nohupゆえ制御端末からは完全分離)。恒常的読者を探索=`scripts/agent_health_check.sh`が類似のERR-TOKEN-WARN-001を持つが★別経路(jsonl直読、この logは不読)★と確認。自動読者は発見できず。 | **無人(=着地先はあるが自動読者なし。人が随時手動で見る可能性は判定不能)** |
| 3 | `stop_hook_inbox.sh` L120-125 | `.claude/settings.json`にStop hook登録実測(`"command": "bash scripts/stop_hook_inbox.sh"`)。当該行自体を実読=「Send notification to karo (background, non-blocking)」のコメント直下、`bash ... inbox_write.sh karo ... &`(末尾`&`でbackground・非待機)実測確認。 | 親hookは同期実行(agent turn終了毎)だが、この一行だけは`&`で切り離され、結果を見る経路が構造上ゼロ。 | **この一行に限り無人(親contextは有人だが当該呼出は誰も待たぬ)** |
| 4 | `hakudokai_activity_monitor.sh`(a3殿番号#3,4=同一file内 line155,188の2箇所参照、★別processではない事を確認★) | header自己申告「エージェント稼働監視デーモン」。`hakudokai_start_watchers.sh:143`に`nohup bash ... >> /tmp/hakudokai_activity_monitor.log 2>&1 </dev/null &`実測確認(呼出箇所は1箇所のみ・他に起動元は探索範囲で発見できず)。★ps実測=現在この瞬間 process 0件★(a3殿は「grepによる起動script実在確認のみ・ps未実施」と自ら積み残しにしていた点を当職が補完)。 | `/tmp/hakudokai_activity_monitor.log`★自体が存在せず★(ls実測)。`/tmp/hakudokai_activity_dashboard.json`も同様に不在。 | **無人(確定、かつ★現在非稼働も確定★——script在るは動いておるに非ず、の実例) ★「×2」の意味=同一fileの2行参照であり2process目は発見できず(判定不能)★** |
| 5 | `ntfy_listener.sh` | `shutsujin_departure.sh:1079`に`nohup bash "$SCRIPT_DIR/scripts/ntfy_listener.sh" &>/dev/null &`実測確認(a3殿引用と完全一致)。ps実測=現在0件。 | `&>/dev/null`で起動時点からstdout/stderr双方を完全破棄——★6件中最重(logにすら残らぬ)★。 | **無人(確定)** |

## 3 ⒜⒝⒞ 突合(将軍second令の作法どおり、食い違うたら先に問う)

a3殿の5件全てを実地で追試した結果、**★食い違いは1件も無かった★**——同じ物(同一file・同一行)を・同じ名で・
(a3殿の断面19:xx台と当職の断面12:45で)ほぼ同時に見た。「本日五度とも観測条件差」の型が★六度目には現れず、
むしろ★独立2経路が完全一致した★★という結果になった(a3殿の自己申告した限界=「常時読者未確認」「ps未実施」の
2点を、当職がそれぞれ「読者探索で不発見」「ps実測でゼロ」として埋めた形)。

## 足軽3号殿の積み残し二件

**① agent_periodic_push.shのsystemd unit実体**: 当host(SecondPC)には★確定して存在しない★
(list-units/list-unit-files/list-timers全て0件・陽性対照で検索機構自体は健全と確認済)。
★但しMainPC側の存在有無は当職の権限・接続範囲外ゆえ未確認★(a3殿と同じ限界が残る。見ておらぬ物は見たと書かず)。

**② shim watcher群が当hostで今稼働中か(ps未実施だった点)**: `shim/hakudokai/*.sh`全46件を`ps -ef`で個別実測。
★稼働中★=`hakudokai_secondpc_receiver.sh`/`hakudokai_secondpc_watcher.sh`/`senmu_desktop_route_watcher.sh`(inbound)/
`senmu_desktop_route_watcher.py`(inbound)/同(outbound)×2。★非稼働★=`hakudokai_activity_monitor.sh`(上記)・
`hakudokai_fukuincho_watcher.sh`・`hakudokai_fukuincho_reverse_watcher.sh`・`hakudokai_kuro_desktop_watcher.sh`・
`hakudokai_watchdog.sh`・`hakudokai_reports_sync.sh`・`hakudokai_task_sync.sh`他(一部は一回性setup/departure
scriptゆえ非稼働が正常。watcher/monitor/daemon型に絞れば上記の通り★稼働と非稼働が混在★——「shim watcher群は
悉く不稼働」ではなく「一部は生き・一部は死んでいる」が実態)。

---

## 【本工区で己が直した誤り】

無し(己の測定手順・結論で訂正した箇所は今回は見当たらず)。

## 【この工区と対に成る他工区】

`docs/incident_logs/2026-08-05_legC_unattended_caller_survey_a3.md`(足軽3号、独立再測の対象そのもの)。
副次的に`2026-08-05_legC_17site_ledger_a1.md`(足軽1号、同一母集団ゆえ独立性は無いが17箇所全体像の出所)。
他に直接対をなす工区は当職の探索範囲(下命本文+両ファイル全文)では見つからず、これ以上の有無は判定不能とする。

## 母集団漏れの自己申告

1. MainPC側のsystemd unit/cron/pane稼働状況は当職のアクセス範囲外(SecondPC上のみ実測)。
2. a3殿の17箇所全体のうち、本工区で再測したのは指定6件+積み残し2件のみ——残り11箇所は範囲外。
3. `/tmp/watcher-<agent>.log`の恒常的読者について「自動読者なし」までは確定したが、人が随時手動でtail/catする
   運用習慣の有無までは当職の観測手段では判定不能。

## 監査体制

暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、独立再測、家老second殿の受理判断へ供する。
