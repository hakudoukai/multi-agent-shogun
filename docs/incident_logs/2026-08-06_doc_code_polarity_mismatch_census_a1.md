# 『極性の食い違い』全数調査 — flag/option/env の doc-vs-code 横断（足軽1号）

- 下命: karo-second msg_20260806_212036_7113955c（2026-08-06T21:20:36）
- 前工区: docs/incident_logs/2026-08-06_night_mode_morning_digest_trigger_a1.md（`night_mode` 名称・極性不一致を単発発見、PASS収載済）— 本票は⒡「一般化せよ」への回答
- 測時=2026-08-06T21:24:26+09:00（`date -Iseconds`）／器=`/usr/bin/grep -rohE`（実装側 flag basename 抽出）＋`/usr/bin/grep -rln`（doc側 突合。★`git grep` は使っていない＝gitignore を無言で飛ばす懸念を避けるため★）／範囲=実装側`scripts/**`+`shim/**`、文書側`docs/**`+`CLAUDE.md`+`instructions/**`
- git rev-parse HEAD = `4061f26128a3c824061f941b746c1bfdff2b76fd`（前票測時 `70caeee` から進んでいる＝他agentの並行commitを実行の刻に確認、本票は本HEADを正とする）

**禁の順守**＝読取のみ・flagは一度も立てていない・scriptは一度も実行していない。

## 母集団宣言

実装側: `/usr/bin/grep -rohE '\.openclaw/[A-Za-z0-9_]+' scripts/ shim/` で抽出した `.openclaw/*` flag basename、重複排除後 **30件**。これに加えて、CLAUDE.md が名指しで claim する非ファイル型 env/regex を2件（`CONTEXT_WARN_BYTES`/`CONTEXT_DANGER_BYTES` の組、DD-169 `dd169_kill_term_guard.sh` の regex claim）と、runbook front-matter `auto_fix` フィールドの1系統を追加でスポットチェック（計 33 件相当を実測）。

★除外した2件★＝`.openclaw/dashboard`・`.openclaw/role` — 抽出はされたが、中身が enable/disable の**極性を持たない**成果物（dashboard.md 出力先パス／role.json 識別情報ファイル）ゆえ「食い違い」を論じる対象外と判じた（理由付き除外）。

## ⒜⒝ 食い違いの一覧（doc と code で名 or 極性が食い違う物・向き付き）

30件中、docs/**+CLAUDE.md+instructions/** に**意味のある説明**（自票の自己言及のみでなく、第三者文書として当該flagの挙動を記述した箇所）が見つかったのは **5件**。うち **2件が食い違い**：

| # | flag（code側実名） | doc側の記述 | 食い違いの型 | どちらを読むと何を誤るか |
|---|---|---|---|---|
| 1 | `~/.openclaw/night_mode`（`scripts/diagnose.sh:15,118-122`・存在チェックのみ＝opt-in、立てるcodeは0件） | `docs/runbooks/err-ekarte-001.md:53-59`「夜間モード」節＝22:00-7:00自動発動・`~/.openclaw/disable_night_mode`で無効化（opt-out） | **名称★と★極性 両方不一致**（`night_mode` vs `disable_night_mode`／opt-in vs opt-out） | doc**のみ**読む者＝「今夜も自動で morning_digest に繰延されている」と誤信（実際は入口自体が無く常時無効）。code**のみ**読む者＝「手動で flag を立てれば有効化できる」と誤信（時刻連動の仕組みは repo 内どこにも実装されず、doc が描く「自動発動」機能そのものが存在しない）。（前票にて確定済・再掲） |
| 2 | `~/.openclaw/disable_inbox_watcher_<agent>`（`scripts/watcher_supervisor.sh:43`／`watcher_supervisor_third.sh:54`／`scripts/inbox_watcher.sh:1601`＝3箇所で統一） | `docs/tier1_redundancy_layer_for_two_pc_integrity_design_2026-05-08.md:111`「watcher zombie│process kill (= `disable_watcher_<agent>` flag 配置) → watchdog が再 spawn」 | **名称不一致**（`disable_watcher_<agent>` vs 実名 `disable_inbox_watcher_<agent>`＝`inbox_` の有無）＋**因果の向きが逆**（doc＝flag配置→respawnする、code実測＝flag存在時は`start_watcher_if_missing()`が`return 0`で★respawnしない★=真逆） | doc**のみ**読む者＝「zombie化したwatcherは、flagを置けば killされ、その後 watchdog が自動で綺麗な物に respawn してくれる」と誤信。code**のみ**読む者（doc記載の`disable_watcher_<agent>`という名を頼りに探す場合）＝そのものずばりの名の flag が存在しない事に気づけず探索が空振りする。★根本＝doc が指す `system_integrity_recover.sh` 自体が repo 内に実在しない★（`find . -iname "system_integrity_recover*"` 実測0件）＝設計提案が実装されずに放置され、実際に稼働している類似機構（`watcher_supervisor.sh`系）と名も挙動も揺れたまま併存している。 |

## ⒞ 既定値の食い違い

上記 #1 (`night_mode`) が既定値の食い違いも兼ねる＝doc の設計＝「22:00-7:00 は★既定で有効★（明示 disable flag が無い限り自動発動）」、code の実装＝「★既定で無効★（明示 night_mode flag を立てない限り何も起きない）」——opt-in/opt-out の逆転はそのまま既定値の逆転でもある。これ以外に「既定 有効／既定 無効」を明示的に主張する記述を `既定|デフォルト|default` 語彙で `instructions/common/*.md`・`docs/error-design-medical.md`・`docs/01-architecture/watcher-design.md`・`CLAUDE.md` に索いたが **0件**（該当語彙自体が見当たらず＝主張が無いので比較しようが無い、の意）。

## 一致（食い違い無し）と判じた3件＋スポットチェック3件（過大に言わぬ為の対照）

| flag / env | doc | code | 判定 |
|---|---|---|---|
| `disable_pane_identity_hook` | `docs/proposals/pane_identity_pretool_hook_proposal.md:53,91,97`＝「検出時は即exit0でスキップ」 | `scripts/checks/pane_identity.sh:32,47`＝同一名・同一極性（presence→即exit0） | 一致 |
| `global_disable` | 複数doc（`docs/01-architecture/watcher-design.md`他）＝「presence→全機能停止」 | `watcher_supervisor.sh`等 複数箇所で presence→全停止、統一実装 | 一致（全 doc hit は精読せず代表数件のみ抽出確認＝母集団漏れ自己申告） |
| `registry_updating` | `docs/cmd_phase2_watchdog_registry_draft.md:32,83-86`＝「presence→restart抑制」 | `shim/hakudokai/hakudokai_watchdog.sh:337-340`＝presence→前回値保持・restart しない | 一致 |
| `CONTEXT_WARN_BYTES`/`CONTEXT_DANGER_BYTES` | `CLAUDE.md:162-165`＝閾値1.6MB/2.0MB・env上書き可 | `scripts/checks/context_usage_warn.sh:27-28`＝`${CONTEXT_WARN_BYTES:-1600000}`/`${CONTEXT_DANGER_BYTES:-2000000}` | 完全一致 |
| DD-169 kill-TERM regex | `CLAUDE.md`「D006 conditional exception」＝`^kill -TERM [0-9]+$` | `scripts/checks/dd169_kill_term_guard.sh:69`＝`^kill[[:space:]]+-TERM[[:space:]]+[0-9]+$` | 実質一致（空白許容の書き方の差のみ・極性/名称の食い違いに非ず） |
| `auto_fix`（runbook front matter） | `docs/error-design-medical.md:199`「自動修復試行（限定的）」＝グローバル既定の主張なし、runbook毎に個別値 | `scripts/diagnose.sh:299`＝`if [[ "$auto_fix" == "true" ]]` で runbook毎の値をそのまま使用 | 一致（doc がグローバル既定を主張していないので比較対象自体が無い＝矛盾しようがない） |

## 未言及22件＋2件除外（0件の内訳・推して埋めず）

`disable_auto_continue_`/`disable_cross_pc_bridge`/`disable_diagnose`/`disable_fukuincho_check`/`disable_fukuincho_reverse_watcher`/`disable_fukuincho_watcher`/`disable_health_check`/`disable_honda_meta_audit`/`disable_inbox_watcher_`（前置詞のみ）/`disable_karo_overload_monitor`/`disable_kuro_desktop_watcher`/`disable_persona_check`/`disable_secondpc_receiver`/`disable_secondpc_watcher`/`disable_supervisor_secondpc`/`disable_supervisor_v2`/`disable_task_heartbeat`/`disable_token_check`/`disable_watchdog`/`disable_watcher_supervisor`/`disable_watcher_supervisor_third`/`notified_`（22件）＝`docs/**`+`CLAUDE.md`+`instructions/**` に**意味のある説明が0件**（`/usr/bin/grep -rln`実測、ヒット0）。★これは「食い違い」ではない★——doc側に主張自体が存在しないゆえ、比較対象を欠き「食い違い」の定義（doc と code の両方が存在してこそ争える）に該当しない。裁定はしていない（直すな、との令通り）。

`dashboard`・`role`（2件）＝上記「母集団宣言」の通り、極性を持たぬ成果物ゆえ対象外。

## ⒟ 0件の書き方（本票内で0件と書いた項目の索き方）

- 「既定値の食い違い」の追加事例＝`既定|デフォルト|default` 語彙横断で0件（範囲＝上記4 file）。
- 「未言及22件」の doc 説明＝flag basename の完全一致文字列で `docs/**`+`CLAUDE.md`+`instructions/**` 横断、ヒット0（誤検出防止のため部分一致でなく basename そのものを検索語に使用）。

## ⒠ 己の手で為した事／直すな・指せ

```
date -Iseconds ; git rev-parse HEAD
/usr/bin/grep -rohE '\.openclaw/[A-Za-z0-9_]+' scripts/ shim/ | sort -u   # 実装側30件抽出
for f in <30件>; do /usr/bin/grep -rln -- "$(basename $f)" docs/ CLAUDE.md instructions/; done   # doc突合
sed -n '25,55p' scripts/checks/pane_identity.sh ; grep -n disable_pane_identity_hook docs/proposals/pane_identity_pretool_hook_proposal.md
grep -n -B15 "disable_watcher_" docs/tier1_redundancy_layer_for_two_pc_integrity_design_2026-05-08.md
find . -iname "system_integrity_recover*" ; find . -iname "integrity_check.sh"   # 未実装確認
grep -n "disable_watcher\|disable_inbox_watcher" scripts/watcher_supervisor.sh scripts/watcher_supervisor_third.sh scripts/inbox_watcher.sh
grep -n -B3 -A3 registry_updating docs/cmd_phase2_watchdog_registry_draft.md docs/cmd_phase3_shutsujin_dynamic_pane_draft.md docs/incident_logs/2026-05-08_pane_mapping_drift.md
grep -n -B2 -A5 REGISTRY_UPDATING shim/hakudokai/hakudokai_watchdog.sh
grep -n "CONTEXT_WARN_BYTES\|CONTEXT_DANGER_BYTES\|1.6MB\|2.0MB" CLAUDE.md ; cat scripts/checks/context_usage_warn.sh
grep -n "kill -TERM\|regex" scripts/checks/dd169_kill_term_guard.sh
grep -n auto_fix docs/runbooks/*.md ; grep -n -B2 -A2 auto_fix docs/error-design-medical.md ; sed -n '258,300p' scripts/diagnose.sh
grep -n "既定で有効\|デフォルトで有効\|default.*enabled\|既定で無効\|デフォルトで無効\|default.*disabled" instructions/common/*.md docs/error-design-medical.md docs/01-architecture/watcher-design.md CLAUDE.md
```

以上（読めぬfileは無かった・flagは一度も立てていない・scriptは一度も実行していない）。**直すな、との令ゆえ是正は一切していない**（#1・#2 いずれも指摘のみ）。

## 監査体制

暫定二者制（軍師second + Gemini）。Codex leg停止中（2026-07-21事案）。「二者PASS」を「三者PASS」と書かない。
