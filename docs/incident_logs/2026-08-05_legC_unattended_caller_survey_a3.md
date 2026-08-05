# leg C 附帯・第三便 — 「見ておらぬ6箇所」は 無人の呼び手か (足軽3号)

- **下命**: karo-second (msg_20260805_113240_f83469b2)。将軍second 殿の戒め=
  「名で推すな (推測から入るな)、実際の launcher を当たれ」。
- **問い**: 先の測定 (survey_a3.md) で **DOES NOT CHECK** と判定した6箇所は、
  各々 ⑴起動の主体 ⑵失敗時に人の目に触れる経路の有無 ⑶無人/有人の判定+根拠、を実測せよ。
- **本書もなお測定のみ**。四巡目契約の執筆は保留のまま (下命どおり)。

---

## 実測手段 (推測を排すため)

- 起動主体: repo 内 grep で launcher script を特定 + (可能な範囲で) 現在稼働中 process を
  `ps -eo pid,ppid,pgid,stat,etime,cmd` で実地確認 (SecondPC 上・当職の視界内)。
- 失敗の着地先: 各 launcher の redirect (`>>`/`&>`/`2>&1`) を実読。
- 「無人/有人」の根拠: **file の名や coment だけで判じず、実際の起動コマンド (`nohup`/`setsid`/`systemd`/hook 登録) を当たった**。

## 実測結果 — 全6箇所

| # | file:line | 起動主体 (実測根拠) | 失敗の着地先 | 無人/有人 判定 |
|---|---|---|---|---|
| 3,4 | `shim/hakudokai/hakudokai_activity_monitor.sh:155,188` | **無人 daemon**。自身の header comment が「デーモン」と自称 (推測ではなく自己申告として採用)。`shim/hakudokai/hakudokai_start_watchers.sh:143` で `nohup bash ... --idle-threshold 300 --interval 30 >> /tmp/... 2>&1 </dev/null &` により起動 (実 grep 確認)。 | `/tmp/hakudokai_activity_monitor.log` (先の追補で恒常読者は未確認と判定済) | **無人 (根拠=nohup起動+header自己申告・推測なし)** |
| 12 | `scripts/stop_hook_inbox.sh:123` | **性質が二重**。hook 本体は `.claude/settings.json` に Stop hook として登録済 (実 grep 確認・`"command": "bash scripts/stop_hook_inbox.sh"`)。★hook 自体は agent の turn 終了ごとに同期実行される★ (=当 turn も含め、現に「人/agentが居る」文脈で走る)。然れど★問題の当該箇所 (line 123) は hook 自身の header comment で「background, non-blocking」と明記★ — hook 本体が同期でも、この一行だけは意図して待ち合わせを外している。 | 無し (background 起動のみ、`&` の先を誰も待たず、結果を見る経路が構造上存在しない) | **この一行に限っては 無人と同等** (親 context は有人でも、当該呼出は誰も待たぬ設計) |
| 14 | `scripts/inbox_watcher.sh` token-warning (~1619-1621) | **無人 daemon (現に稼働中を実地確認)**。`ps -eo pid,ppid,pgid,stat,etime,cmd` で当 SecondPC 上に `ashigaru1〜7`/`karo-second`/`shogun-second`/`gunshi-second`/`honbucho` 分の `inbox_watcher.sh` process を実測 (例: PID 3182121 `inbox_watcher.sh ashigaru3 multiagent-second:0.3 claude`、起動 08:52:01〜)。親 process (`watcher_supervisor.sh` 系の再起動処理と見られる、PID 3181668) の実行内容を読むと `setsid nohup bash "$S" "$A" "$PANE" "$CLI" </dev/null >>"$L" 2>&1 &` (`$L` は `/tmp/watcher-$A.log` 相当) — `setsid` は制御端末からの完全分離であり、`nohup` より強い無人化。 | `/tmp/watcher-<agent>.log` (本会話でも既知: `/tmp/watcher-karo-second.log` 等) — 常時読む者は未確認 (先の追補と同様) | **無人 (根拠=setsid+nohup、稼働中processを実地確認・推測なし)** |
| 16 | `scripts/agent_periodic_push.sh:109` | **無人 (自己文書による — 実 unit file は repo に無く独立検証は未達)**。file 冒頭 comment に
  「systemd user timer で 15分毎実行」と明記 (自己申告)。但し `find . -iname "*.service" -o -iname "*.timer"` では該当 unit file を
  発見できず (repo 外・host 個別設定の可能性)、`systemctl list-units` にも該当なし (当 SecondPC host には無いか、権限外)。
  ∴ ★「systemd timer」は file 自身の記述のみに拠る・当職は実 unit を目視で確認できていない (この限界を隠さず記す)★。 | `/tmp/agent_periodic_push.log` | **無人 (根拠=自己文書+`\|\| true`パターン。実 unit file 未確認という限界つき)** |
| 17 | `scripts/ntfy_listener.sh:171` | **無人 daemon**。`shutsujin_departure.sh:1079` に `nohup bash "$SCRIPT_DIR/scripts/ntfy_listener.sh" &>/dev/null &` を実 grep で確認。 | **無し** — `&>/dev/null` で起動時点から stdout/stderr 双方を完全破棄。★6箇所中★最も重い★ (log file にすら残らぬ)。 | **無人 (根拠=nohup起動を実 grep 確認・推測なし)** |

## 集計・結論

- **6箇所中 5箇所 = 明確に無人 daemon/timer** (nohup または setsid、稼働中processまたは起動script grepで実測確認)。
- **1箇所 (stop_hook_inbox.sh) = 親processは有人 (agentのturn終了ごとに同期実行) だが、
  問題の当該呼出そのものは設計上 誰も待たぬ background 送信** — 純粋な「無人」とは性質が異なるが、
  ★実効的には無人と同じ帰結★ (結果を見る経路が構造上ゼロ)。
- ★∴ 将軍second 殿の懸念「6件悉く無人と見える」は ★推測ではなく実測で概ね裏付けられた★
  (5/6 は明確な無人daemon、残り1/6も実効的に同型)。
- **着地先の重さにも差がある**: `ntfy_listener.sh` は log file すら残らぬ (`&>/dev/null`)。
  他5件は log file には残るが、恒常的な読者は先の追補 (addendum_a3.md) の通り未確認。

## 積み残し (隠さず記す)

- `agent_periodic_push.sh` の systemd unit file 実体は当職未確認 (repo 内不在・当 host `systemctl` 権限/該当なし)。
  MainPC 側に別途 unit が存在する可能性があるが、★当職はそれを見ておらぬ・見たと書かぬ★。
- `hakudokai_activity_monitor.sh`・他 shim watcher 群は header 上 MainPC 対象を明記しており、
  当 SecondPC host では実際に稼働中か (`ps`) は確認していない (grep による起動script実在の確認のみ)。
  ★「起動 script が在る」と「今この瞬間 動いておる」は別物★であり、後者は当 host では未検証。

## 禁則の遵守

測定のみ (discovery、凍結対象外)。影 file 不触・dd189 不触・process 不触・commit 禁・scope 拡大なし。
