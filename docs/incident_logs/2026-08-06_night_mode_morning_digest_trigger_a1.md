# `night_mode` が立つ条件と溜まる物 — morning_digest 機構の深掘り（足軽1号）

- 下命: karo-second msg_20260806_211107_cb10d27f（2026-08-06T21:11:07）
- 前工区: docs/incident_logs/2026-08-06_pending_notice_type_buffer_sweep_a1.md（`_pending_notice`=引き金は在るが来ぬ、`morning_digest`=引き金そのものが無い、と分けて PASS 収載済・commit `70caeee`）
- 測時=2026-08-06T21:16:09+09:00（`date -Iseconds` 実行結果）／器=`Read`/`/usr/bin/grep -rn`/`ls -la`/`systemctl --user list-timers --all`/`crontab -l`／範囲=`scripts/diagnose.sh` 全文（373行）＋`docs/runbooks/*.md`＋`docs/error-design-medical.md`＋`instructions/*.md`＋`scripts/**` 横断（append-mode / read-modify-write JSON 蓄積パターン語彙）
- git rev-parse HEAD = `70caeee9242ecc0bc38960423055ed4de1beff4f`

**禁の順守**＝`night_mode` flag を一度も立てていない（`touch`/`mkdir` 等の書込コマンドは一度も実行せず）・script は一度も実行していない（`bash scripts/diagnose.sh` 呼出0件）・読むのみ。

## ⒜ `night_mode` flag を誰が・何処で・如何なる条件で立てるか

`scripts/diagnose.sh:15` — `NIGHT_MODE_FLAG="$HOME/.openclaw/night_mode"`。`check_night_mode()`（L118-155）はこの file の**存在有無を読むだけ**（L120 `if [[ ! -f "$NIGHT_MODE_FLAG" ]]; then return 0`）。

**実測＝この flag を作成/削除する code は repo 内に0件**（`/usr/bin/grep -rn "night_mode" . --include=*.sh --include=*.py --include=*.md --include=*.yaml --include=*.yml` を実行、ヒット全件を目視確認——`diagnose.sh` 自身の read 箇所と、前票・本票の incident_log 記述のみ）。`touch`/`mkdir`/`open(...,'w')` 等で `~/.openclaw/night_mode` を書く箇所は見つからず。cron（`crontab -l` = "no crontab for hakudokai"）・systemd timer（`systemctl --user list-timers --all` 実測7件、内訳=`auto-git-sync`/`enter_restart_shogun_second`/`shogun_auto_claim`/`secondpc-alive-monitor-v0.2`/`shogun-self-check`/`codex-healthcheck`/`launchpadlib-cache-clean`——night_mode/22時/朝7時に関わる物は0件）にも該当無し。

一方、`docs/runbooks/err-ekarte-001.md:53-59`「夜間モード（理事長殿の睡眠保護）」節は**設計として**「22:00-7:00 (JST) は自動的に night mode」「理事長フラグ `~/.openclaw/disable_night_mode` で無効化可」と記す——これは**時刻で自動 ON・明示 OFF flag** という设計。だが実装（`diagnose.sh`）は逆で、**明示 ON flag（`night_mode`)・時刻判定コード無し**——flag 名・極性ともに doc と code が一致しない（doc=`disable_night_mode` を探す opt-out 型、code=`night_mode` の有無を見る opt-in 型）。★これは所見の記述に留め、裁定はしていない★。

結論＝「立つ条件」は**存在しない**（★何処にも★ 立てる code が無い＝人間が手動で `touch ~/.openclaw/night_mode` する以外に立ちようが無い、その手動操作も repo 内の手順書・runbook いずれにも記載を見つけられず）。`ls -la ~/.openclaw/night_mode ~/.openclaw/disable_night_mode` 実測＝両方とも `No such file or directory`（測時時点で未設定）。

## ⒝ 立った時に morning_digest に何がどれだけ溜まるか

**見積り不可（出来ぬ、と正直に書く）**。理由＝

1. `check_night_mode()` は `run_diagnosis()`（L222）内、`diagnose.sh` が **エラーコード引数付きで呼ばれた回数だけ** 実行される。
2. `/usr/bin/grep -rn "diagnose\.sh" . --include=*.sh --include=*.py` を実行した結果、**`scripts/diagnose.sh` 自身以外に呼出元は repo 内に0件**（`docs/error-design-medical.md`/`docs/runbooks/err-ekarte-001.md` に「信長（将軍）が nudge 受信時に手動判断で実行する」という設計記述はあるが、これは AI agent の判断による手動実行であり、shell/python からの自動呼出しではない）。
3. ∴ 溜まる件数は「night_mode 中に non-immediate ERR-*/WARN が何回発生し、その都度 shogun が `diagnose.sh <ERR-CODE>` を手動実行するか」という**運用頻度**に懸かっており、静的読解からは値を導けぬ。
4. 参考=runbook 側の `night_mode:` 前置詞（front matter）実測：`ERR-INFRA-001`=`immediate`、`ERR-WATCHER-001`=`immediate`（この2つは night_mode 中でも即時扱い＝溜まらぬ）。残り6件（`ERR-SUPABASE-001`/`ERR-AUTH-001`/`ERR-PDF-001`/`ERR-BILLING-001`/`ERR-EKARTE-001`/`ERR-CARTE-001`）は `defer` または `defer_unless_critical`＝night_mode 中は原則 morning_digest 行き（`docs/runbooks/*.md` front matter 全8件を実読、`night_mode:` 行を突合）。

現況＝`night_mode` flag も `/tmp/morning_digest.json` も測時点で不在ゆえ、実データの蓄積量は**現在ゼロ**（前票と同じ状態・変化なし）。

## ⒞『溜まった物を読む者』は在るか

**実測＝在らず**。`/usr/bin/grep -rn "morning_digest" . --include=*.sh --include=*.py` の全ヒットは `scripts/diagnose.sh` 内の書込箇所（L12定義・L130-150 append処理・L275 dry-run文言）のみ——読取（`open(...).read`/`cat`/`json.load` して中身を消費する箇所）は0件。

∴ **『書いて誰も読まぬ』三例目**——前々票の `_pending_notice`（引き金は在るが来ぬ・実害在り）、前票の `morning_digest`（引き金の出口が無い・潜在）に続き、本票で**入口すら手動 flag 依存で常時死んでいる**ことまで確認できた（three-tier: ①実害在り→②潜在→③入口も封鎖）。

## ⒟ 同型をもう一つ（関数名でなく振舞いで、`scripts/**`）

検索方針＝read-modify-write の JSON/YAML 配列蓄積パターン（`.append(` を含む file）を `scripts/**` 横断で洗い、既知の除外候補（`karo_second_reception_check.sh` は状態非永続、`fukuincho_report_poke_bundle.py` は即時処理、前票既報の`add_dead_letter()`は性格が異なり除外済）を除いて精読。

**同型ヒット＝`scripts/ntfy_listener.sh` の `append_ntfy_inbox()`（L48-130）＋`shutsujin_departure.sh` の archival step（L1014-1070）の組**：

- `append_ntfy_inbox()` は ntfy から受信した message を `queue/ntfy_inbox.yaml` の `inbox:` 配列へ `status: "pending"` で無条件追記（read-modify-write、flock/mkdir lock 付き、L112-116）。
- `shutsujin_departure.sh:1015-1070`「STEP 6.7.5」は起動時に一度だけ、`status == 'processed'` かつ `timestamp` が7日超の entry を `queue/ntfy_inbox_archive.yaml` へ退避する——**だが `status` を `'processed'` へ遷移させる code が repo 内（archive 配下の廃止済 `dedup.sh` を除く）に0件**（`/usr/bin/grep -rn "'processed'\|\"processed\"" --include=*.sh --include=*.py .` 実行結果、非archive/非docs/非queueヒットは `shutsujin_departure.sh:1040`（読む側の条件式）のみ、書く側は0件）。
- ∴ `queue/ntfy_inbox.yaml` の entry は `status: "pending"` のまま**永久に**溜まり続け、退避条件（`status=='processed'`）が構造上満たされ得ぬ——「引き金の出口が無い」morning_digest と同型（accumulate はあるが consume/flush へ渡す遷移条件が誰にも実装されていない）。
- 現況＝`queue/ntfy_inbox.yaml` は測時点で**現存しない**（`ls -la` 実測 `No such file or directory`）＝ntfy_listener.sh 自体が起動していない（`pgrep -af ntfy_listener` 実測ヒット0件、本コマンド実行時の bash wrapper 自身の誤マッチを除く）ため、これも実害ゼロの潜在欠陥（morning_digest と同じ「目下は未発火」状態）。

## ⒠ 己の手で為した事

```
date -Iseconds ; git rev-parse HEAD
sed -n '1,373p' scripts/diagnose.sh   # 全文精読（既読部分含め再確認）
/usr/bin/grep -rn "night_mode" . --include=*.sh --include=*.py --include=*.md --include=*.yaml --include=*.yml
ls -la ~/.openclaw/ ; ls -la ~/.openclaw/night_mode ~/.openclaw/disable_night_mode
crontab -l
systemctl --user list-timers --all
find / -maxdepth 6 -iname "*openclaw*" 2>/dev/null   # night_mode/disable_night_mode 系ファイル無しを再確認
sed -n '40,64p' docs/runbooks/err-ekarte-001.md   # 夜間モード節精読
/usr/bin/grep -n "night_mode:" docs/runbooks/ERR-*.md   # 全8 runbook front matter 突合
/usr/bin/grep -rn "diagnose\.sh" . --include=*.sh --include=*.py   # 呼出元0件確認
/usr/bin/grep -rn "morning_digest" . --include=*.sh --include=*.py
/usr/bin/grep -rln "\.append(" scripts/*.sh scripts/**/*.sh scripts/**/*.py
sed -n '1,130p' scripts/ntfy_listener.sh   # append_ntfy_inbox 全文精読
/usr/bin/grep -n "ntfy_inbox" shutsujin_departure.sh
sed -n '1010,1080p' shutsujin_departure.sh   # STEP 6.7.5 archival step 全文精読
/usr/bin/grep -rn "'processed'\|\"processed\"" --include=*.sh --include=*.py .
ls -la queue/ntfy_inbox.yaml queue/ntfy_inbox_archive.yaml
pgrep -af ntfy_listener
ls -la /tmp/morning_digest.json
```

以上（読めぬfileは無かった・`night_mode` flag は一度も立てていない・script は一度も実行していない・flush は起こしていない）。

## 監査体制

暫定二者制（軍師second + Gemini）。Codex leg停止中（2026-07-21事案）。「二者PASS」を「三者PASS」と書かない。
