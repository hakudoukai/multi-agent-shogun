# leg C 附帯 — inbox_write.sh 呼び手17箇所 台帳 (足軽1号)

- **下命**: karo-second (msg_20260805_115735_5068d515)。leg C を閉じる条件(a)。
  出所=委員長殿既裁可の範囲内・将軍second 令 msg_20260805_115301_3680148b・執行=karo-second。
- **典拠 (足軽3号 実測)**: `docs/incident_logs/2026-08-05_legC_exitcode_caller_survey_a3.md`(122行)、
  `_addendum_a3.md`(89行)、`_unattended_caller_survey_a3.md`(53行)。
  ★下命により写さず、本書の数字・行番号・判定は当職が独立に (`/usr/bin/grep -r`・`sed -n`・`ps -eo`) 引き直した★。
  典拠と食い違えば §6 に食い違いとして記す。

---

## 0. この帳は何を以て閉じるか (冒頭必須・行き先の無い帳は書いた時点で墓場)

- **閉じる条件**: 本帳が (1) 17件全件を判定込みで列挙し、(2) DOES NOT CHECK 6件を実名で明示し、
  (3) 残る11件の内訳も併記し (分母を隠さず)、(4) 各件に無人/有人を独立実測で付し、
  (5) karo-second の受理を得た時点で、★台帳化そのもの★ は閉じる。
- **閉じないもの (別工区として明記して残す・(c)の必須条件ではない、karo-second 裁定 msg_20260805_115134_1b5d5f8d)**:
  - 17箇所の是正 (握り潰しを CHECKS へ変える実装作業) — 未着手・別工区。
  - 母集団B (`instructions/generated/*.md` 16本) の扱い — ★既に別途裁定済★:
    委員長殿裁定 (足軽3号 msg_20260805_115028_0e886499 経由) により「No state checking…」の逐語は
    ★生成残骸と確定★。足軽3号が16本へ廃止マーカー prepend 実施中 (本書執筆時点で当職は完了未確認・§5 参照)。
  - 条件(b)「閉じ得ぬ物は閉じ得ぬと明記して残せ」(人手 dispatch 層) の担当者 — ★当職の視界では不明★。
    karo-second 自身か、別途配下へ下命されるかは、本書の情報だけでは判定不能 (§5 に自己申告)。
- **明日この帳が使われなんだ時、どこを見ればそれが判るか**: 本帳が指す17 file:line のいずれかが
  改修されても本帳が追随更新されなければ、本帳の判定列と実コードが乖離する。★次回検知法★=
  `/usr/bin/grep -rn "inbox_write\.sh" --include="*.sh" --include="*.py" scripts/ shim/` を再実行し
  行数・箇所数が17と一致するかを見よ (§1 の抽出コマンド)。不一致なら本帳は陳腐化している。

## 1. 母集団の定義・断面凍結 (先に宣言)

- **抽出コマンド (当職が独立実行、典拠と同一手段で再現)**:
  `/usr/bin/grep -rn "inbox_write\.sh" --include="*.sh" --include="*.py" scripts/ shim/`
  (`scripts/archive/`・`.bak*`・test file・散文言及(comment/docstring/Usage文)を除外)
- **断面凍結時刻**: 2026-08-05T12:01:48+0900 (`date` 実測)。
- **母集団A (production code call site) = 17件** (足軽3号の数と一致 — 独立再現で確認)。
- **母集団B (agent 手順書) = 16 file** — 本帳の対象外 (§0 の通り既に別途処理中)。
- **除外**: `tests/*.bats`・`tests/*.py` の inbox_write.sh 呼出 (振る舞い検証であり本番呼び手ではない)、
  `docs/`・`queue/reports/*.md` の散文言及、変数代入のみで実呼出ではない行 (例:
  `scripts/karo_overload_monitor.sh:63` の `INBOX_WRITE_CMD` 定義行自体は数えず、実呼出行のみ数えた)。

## 2. 判定基準 (典拠と同一定義を継承・当職が変更せず引用)

| 区分 | 定義 |
|---|---|
| **CHECKS** | exit code / returncode を明示分岐し、失敗時に何らかの handling を行う。 |
| **CHECKS-STRUCTURAL-ONLY** | `set -euo pipefail` 下で失敗すれば script 全体が死ぬが、専用の log/報告は無い。 |
| **ALT-CHANNEL** | exit code 自体は見ていないが、別経路で成否を独立確認し、かつその旨を自ら明記。 |
| **DOES NOT CHECK** | `\|\| true`・background(`&`)・`2>/dev/null` 単体等で失敗を明示的に握り潰す。 |

## 3. 全17件 台帳 (独立実測。file:line / 判定 / 無人・有人 / 根拠)

| # | file:line | 判定 | 無人/有人 (根拠) |
|---|---|---|---|
| 1 | `shim/hakudokai/hakudokai_secondpc_watcher_poll.py:282` | CHECKS | 有人扱い保留 (§5)。`subprocess.run(check=True)` + `except CalledProcessError` を当職が実読確認。稼働中か (`ps`) は当PCでは未検証。 |
| 2 | `shim/hakudokai/hakudokai_fukuincho_reverse_poll.py:151` | CHECKS | 同上パターンを実読確認。 |
| 3 | `shim/hakudokai/hakudokai_activity_monitor.sh:155` | **DOES NOT CHECK** | **無人**。`hakudokai_start_watchers.sh:143` に `nohup bash ... hakudokai_activity_monitor.sh ... >> /tmp/hakudokai_activity_monitor.log 2>&1 </dev/null &` を当職が実 grep 確認 (nohup+background)。当PCで `ps` 実測=非稼働 (MainPC対象と見られ、当SecondPCでは起動 script の実在確認のみ・稼働中確認は未達)。 |
| 4 | `hakudokai_activity_monitor.sh:188` | **DOES NOT CHECK** | 同上 (同一起動経路)。 |
| 5 | `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:352` | CHECKS | `result.returncode == 0` 分岐をコード実読で確認。稼働主体は未検証。 |
| 6 | `shim/hakudokai/hakudokai_fukuincho_poll.py:125` | CHECKS | `check=True` パターンを実読確認。 |
| 7 | `hakudokai_fukuincho_poll.py:136` | CHECKS | 同上。 |
| 8 | `scripts/agent_health_check.sh:159` | CHECKS | `\|\| echo ... >> LOG` を実読確認 (159行、当職の `sed`/`grep` で特定)。★常時読む者は未確認 (§4)★。 |
| 9 | `scripts/redundancy/shogun_report_watcher.sh` `notify_shogun()` (233-238行) | CHECKS | 当職が `sed -n '225,245p'` で実読: `if [ -x "$INBOX_WRITE" ]; ... \|\| echo WARN >&2` の分岐を確認。stderr の着地先 (launcher) は未特定。 |
| 10 | `scripts/karo_overload_monitor.sh` (350,358行) | CHECKS | 当職が `sed -n '340,362p'` で実読: `if bash "$INBOX_WRITE_CMD" ...; then ok=1; else log_json ERROR ...; fi` の明示分岐を2箇所 (takenaka宛/shogun宛) 確認。 |
| 11 | `scripts/fukuincho_report_poke_bundle.py` (378-410行、INSERT wrapper) | CHECKS | 当職が `sed -n '375,412p'` で実読: `ReportInsertResult(rc=proc.returncode, ...)` を返す構造体設計を確認 (呼び手が `.rc` を実際に検めるかは未確認・§5)。 |
| 12 | `scripts/stop_hook_inbox.sh:123` | **DOES NOT CHECK** | **実効的に無人**。`.claude/settings.json:8` の Stop hook 登録を実 grep 確認、hook 本体は同期実行だが当該呼出は `&` background で待ち合わせ無し。★当職自身、本 turn 実行中に `ps` で `stop_hook_inbox.sh` の稼働 (PID 739555/739556) を直接目撃★ — 親 context 有人・当該一行のみ無人相当、という典拠の判定を実地で裏付けた。 |
| 13 | `scripts/inbox_watcher.sh` `return_message_to_sender()` (594行) | ALT-CHANNEL | 当職が `sed -n '576,608p'` で実読: 送り主 inbox を re-read し着地確認、未確認時 `"may have failed silently"` を自ら stderr 明記。コード冒頭コメントに B-4 Return-Path 準拠の限界 (人間到達までは保証せぬ) が明記されているのも確認。 |
| 14 | `scripts/inbox_watcher.sh` token-warning (呼出開始1619行・`\|\| true` は1621行) | **DOES NOT CHECK** | **無人 (現に稼働中を実地確認)**。当職が `ps -eo pid,ppid,stat,etime,cmd` で当SecondPC上に `inbox_watcher.sh` process 多数 (例: PID 1990805 karo-second 15:19:47〜起動) を実測。起動元は `scripts/watcher_supervisor.sh:57` `nohup bash scripts/inbox_watcher.sh ... &` および third系 `watcher_supervisor_third.sh:68` `setsid nohup bash scripts/inbox_watcher.sh ... &` を実 grep 確認。★行番号の食い違い注記★: 典拠 addendum は「呼出=1619・`\|\| true`=1621、委員長殿指摘の"L1620"とは数え方の相違」と記す。当職の `sed -n '1615,1622p'` 実読でも同じく1619/1621を確認 — 典拠と一致。 |
| 15 | `scripts/shogun_self_check.sh:31` | CHECKS-STRUCTURAL-ONLY | 当職が `sed -n '1,10p;25,35p'` で実読: file 冒頭 `set -euo pipefail` (3行目) を確認、31行目の呼出に専用 log/報告は無し。systemd timer 登録 (`shogun-self-check.timer`) が `~/.config/systemd/user/` に実在するのを当職が独立に確認 (§5・典拠にはこの確証は無い、当職の追加所見)。 |
| 16 | `scripts/agent_periodic_push.sh:109` | **DOES NOT CHECK** | **無人 (自己文書のみ・実 unit file 未確認は典拠と同じ限界)**。`\|\| true` を実読確認。当職が `~/.config/systemd/user/*.timer` を実 ls したが `agent_periodic_push` 相当の timer は不在 (`auto-git-sync` / `codex-healthcheck` / `enter_restart_shogun_second` / `secondpc-alive-monitor-v0.2` / `shogun-self-check` / `shogun_auto_claim` の6件のみ確認、periodic_push 無し)。★file 自身の「systemd timer」自称は当PCでは裏取れず★ — 典拠の限界表明と一致。 |
| 17 | `scripts/ntfy_listener.sh:171` | **DOES NOT CHECK** | **無人**。`shutsujin_departure.sh:1079` に `nohup bash "$SCRIPT_DIR/scripts/ntfy_listener.sh" &>/dev/null &` を当職が実 grep 確認 (stdout/stderr 双方破棄、log file にすら残らぬ)。当PCで `ps` 実測=非稼働。 |

## 4. (a) DOES NOT CHECK 6件 — 実名列挙 (下命必達①)

1. `shim/hakudokai/hakudokai_activity_monitor.sh:155`
2. `shim/hakudokai/hakudokai_activity_monitor.sh:188`
3. `scripts/stop_hook_inbox.sh:123`
4. `scripts/inbox_watcher.sh` token-warning便 (呼出1619行・`|| true`は1621行)
5. `scripts/agent_periodic_push.sh:109`
6. `scripts/ntfy_listener.sh:171`

**無人/有人集計 (独立実測)**: 6件中5件=明確に無人 (nohup/setsid起動を実grep確認、うち14番は現に稼働中processを実測)。
残1件 (`stop_hook_inbox.sh:123`) は親 context こそ有人 (Stop hookは当turnも同期実行され、当職自身が実行中processを目撃) だが、
当該一行は待ち合わせ無しのbackground送信であり実効的に無人と同型。★これは典拠の判定 (5明確無人+1実効無人) と当職の独立実測が一致した★。

## 5. (b) 残る11件 — 内訳 (下命必達②・分母を隠さぬ)

- **CHECKS = 9件**: #1, #2, #5, #6, #7, #8, #9, #10, #11
- **CHECKS-STRUCTURAL-ONLY = 1件**: #15 (`shogun_self_check.sh:31`)
- **ALT-CHANNEL = 1件**: #13 (`inbox_watcher.sh` `return_message_to_sender`)
- 合計 9+1+1 = 11件、DOES NOT CHECK 6件と合わせて **17件** (§1の母集団と一致)。

**★但し「CHECKS=良好」と読むな★**: 典拠addendumが既に指摘の通り、CHECKSは「分岐している」だけであり
「その先を誰かが実際に受け取っているか」は別問題。#13以外の10件 (CHECKS 9 + STRUCTURAL 1) は、
失敗情報の終着点 (log file) への★恒常的な読者の実在が当職の独立検証でも未確認★ (§6 陽性対照参照)。

## 6. 陽性対照 (0件と書く前に検出器が生きている事を示す・下命の作法通り)

★「恒常的な読者0件」と書く前に、当職の検出法 (grep で運用doc内の log path 言及を探す) が
★実在する読者を正しく検出できる事★ を先に示す:

- **陽性対照成功例**: `docs/restart-and-mcp.md` (トラブル対応手順書) には `/tmp/vite-dev-server.log`・
  `/tmp/fastapi-server.log` への言及が実在し (136,140,386,390行等・当職 grep 実測)、「サーバが落ちたらこのlogを見よ」という
  ★運用文脈での読者存在の記述★ を検出できた。★∴ 当職の検出法は機能している★。
- **同一検出法を6件のlog pathへ適用**: `/tmp/hakudokai_activity_monitor.log`・`/tmp/watcher-*.log`・
  `/tmp/agent_periodic_push.log` を `docs/` `instructions/` `CLAUDE.md` 全域で grep したところ、
  ★ヒットは `docs/incident_logs/2026-08-05_legC_*` (=本測定シリーズ自身) のみ★ — 陽性対照 (`restart-and-mcp.md`) の
  ような★運用手順書からの参照は0件★。
- **★この0件の性質を正直に記す★**: これは「読者が存在しないと確定した」のではなく、「当職の grep 到達範囲
  (`docs/` `instructions/` `CLAUDE.md`) 内には運用文脈での参照が見当たらぬ」に留まる。人間オペレータが
  手動で `tail -f /tmp/....log` を叩く可能性は、この grep では原理的に検出できぬ (docに書かれずとも行われ得る)。
  ★∴ 判定不能の余地を残したまま「未確認」と書く。「存在しない」とは書かぬ★。

## 7. 【本工区で己が直した誤り】(必須欄・「無し」可・空欄不可)

**無し。** 典拠3書 (survey_a3 / addendum_a3 / unattended_caller_survey_a3) の17件・行番号・判定・
無人有人分類を当職が独立に (`grep`/`sed -n`/`ps`) 再実測したが、典拠との★不一致は検出されなかった★。
唯一の軽微な追加所見は #15 (`shogun_self_check.sh`) の systemd timer 実在を当職が新規に確認した点
(典拠には無い追加証跡であり、「誤りの訂正」ではなく「補強」)。
★この「0件」自体にも§6と同型の限界がある★= 当職の再測手段 (grep/sed/ps) が典拠の手段とほぼ同型であるため、
典拠側の手段固有の見落とし (もしあれば) は当職の再測でも同様に見落とされ得る。独立とは言え方法論は近い。

## 8. 【この工区と対に成る他工区】(必須欄)

- **足軽2号 leg B 実装** (`tests/test_shadow_mailbox_failclosed.bats`・msg_20260805_115134_1b5d5f8d でカラーグリーン11/11確定済) —
  本帳が扱う母集団Aの「失敗を握り潰す呼び手」は、leg Bのfail-closed設計が守ろうとする「配送経路」そのものの上流に位置する。
  本帳はleg Bを直接補強しないが、同じ配送の脆さを別角度 (呼び手側) から記録している。
- **足軽3号 手順書16本 廃止マーカー prepend** (msg_20260805_115028_0e886499、実施中・当職未確認) —
  本帳の母集団A (production code) に対して、母集団B (agent手順書) 側の「No state checking」逐語の扱いを閉じる対工区。
  両者合わせて「呼び手はexit codeを見ておるか」の全体像 (母集団A+B) が揃う。
- **条件(b)「閉じ得ぬ物は閉じ得ぬと明記して残せ」(人手dispatch層)** — ★担当・所在ともに当職の視界では不明★。
  karo-second裁定 (msg_20260805_115134_1b5d5f8d) に条件として明記されているが、誰が実施するかの下命を当職は受領していない。
  §0 に自己申告済。

## 9. 積み残し・母集団漏れの自己申告

- #9 (`shogun_report_watcher.sh`) の起動 launcher (systemd/tmux/nohup) は典拠同様、当職も未特定のまま (時間の都合)。
- #11 (`fukuincho_report_poke_bundle.py` wrapper) の実際の呼び手が `.rc` を検めるかは、呼び手コード側を
  当職は未調査 (典拠addendumの積み残しをそのまま継承、着手できず)。
- #1,2,5,6,7 (shim watcher poll 系) の★現在稼働中か★は当SecondPC上の `ps` では非該当 (MainPC対象の可能性) —
  「起動script が在る」と「今動いておる」は別物であり、当職は後者を当PCでは確認していない。
- 母集団定義そのもの (production code のみ・test/docs除外) の妥当性は当職の裁定範囲外 — 典拠の定義を継承したのみ。

## 10. 二者制の併記 (下命必達)

★本帳の監査は 二者制 (軍師second + Gemini)。Codex leg は7/21事案により停止中、監査モデルgpt-5.4暫定★。
「三者PASS」と書いてはならぬ (委員長殿裁定を継承)。本帳は提出前・両者未実施。

## 11. 禁則の遵守

測定・台帳化のみ (discovery、凍結対象外)。影 file 不触・dd189 不触・process 不触・commit/push/stage 禁・
scope 拡大なし・Dレーン (削除・DB・本番) 不触。17箇所の是正 (実装) は本工区の範囲外 (§0 の通り)。
