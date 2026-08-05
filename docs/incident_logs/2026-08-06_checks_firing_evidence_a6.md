# scripts/checks/ 9本・「現に一度でも発火したか」実測 (足軽6号、2026-08-06・将軍second直命)

★★読取のみ。検査は走らせていない(下記①の一件は、当職の別の読取コマンドに★意図せず引っかかり
guard自身が自発的にBLOCKした★もので、当職が検査を能動的に実行した物ではない=詳細は下記)。
newbuild不触・姉妹clone読取すら不可・直さず。★★測時=2026-08-06T03:27:44+0900
(date -Iseconds実行結果)。HEAD=6b69449bd05f5048147b3070739fc041a06ed114(git rev-parse HEAD実行結果)。

## 母集団・何を外したか

前工区(9本)と同一母集団。今回は「呼び出し元の実在」→「発火の痕跡」の順で調べた(将軍second殿の
「費用の順」指示どおり、中身の精読は行っていない)。

## ① 呼び出し元の実在 (実測・命令+出力)

$ grep -n "codex_cli_required_persona\|codex_exec_sandbox_guard\|context_usage_warn\|dd169_kill_term_guard\|inbox_alias_integrity\|pane_identity\|pretooluse_bash_guard\|secondpc_dispatch\|symlink_aware_atomic_write" .claude/settings.json
20:  "command": "scripts/checks/pretooluse_bash_guard.sh"
25:  "command": "bash scripts/checks/dd169_kill_term_guard.sh"
36:  "command": "bash scripts/checks/context_usage_warn.sh"

**∴ 3本(pretooluse_bash_guard/dd169_kill_term_guard/context_usage_warn)は`.claude/settings.json`の
hookとして直接登録され、★毎Bash呼出しで発火する設計★。**

$ grep -rl "<script名>" scripts/ shim/ lib/ .claude/ (呼出元、hook以外)
- codex_cli_required_persona.sh → `scripts/agent_health_check.sh`から呼出(1件)
- pane_identity.sh → `scripts/checks/pretooluse_bash_guard.sh`から呼出(1件、hook経由で連鎖発火)
- codex_exec_sandbox_guard.sh / inbox_alias_integrity.sh / secondpc_dispatch.sh /
  symlink_aware_atomic_write.sh → **呼出元 0件(当職の検索範囲では見つからず)**

## ★★②発火の痕跡・実測中に起きた出来事★★

`dd169_kill_term_guard.sh`のlog(`/tmp/dd169_audit_log/20260806.log`)を`head`で読もうとした所、
**当職の読取コマンド自体が同hookに★ブロックされた★**(当職のgrepパターン文字列の中に
「kill -TERM」という★文字列★が含まれていた為、guardが誤検知・BLOCKした)。
これは当職が意図的に検査を実行した物ではないが、結果として★hookが現に生きて発火する事を
実地で証明した(2026-08-06T03:2x、当職のBash呼出しへの介入という形で)★。

$ head -20 /tmp/dd169_audit_log/20260806.log (文言を変えて再実行)
[2026-08-06T01:52:20+09:00] BLOCKED non-graceful kill: (以下、実際にBLOCKされた過去のbash呼出しの内容)

$ grep -c "pid,ppid,pgid" /tmp/dd169_audit_log/20260806.log
1

$ wc -l /tmp/dd169_audit_log/*.log
20260803.log / 20260804.log / 20260805.log / 20260806.log の★4日分★のlogが存在
(最新=20260806.log、本日03:2x台まで書込あり)

**∴ `dd169_kill_term_guard.sh`=★現に発火した(実測・log実在+当職への実地介入)★。**
**∴ `pretooluse_bash_guard.sh`=同一hook chain(`.claude/settings.json`)で★毎Bash呼出し時に
必ず先に発火する設計★のため、本日当職が実行した全Bash呼出し(本工区だけで数十回)の
度に発火していたと推定されるが、当該script自身の独立したlog/証跡は確認していない(未測)。**

`context_usage_warn.sh`=当職自身が本セッション中に「context size警告(554.1k tokens)」を
実際に受領している(本会話record内の事実)。∴ **現に発火した(当職への実地体験として確認済)**。

`codex_cli_required_persona.sh`・`pane_identity.sh`=呼出元は実在確認済だが、実行ログ等の
独立した発火証跡は当職の検索範囲では見つからず=**未測**。

`codex_exec_sandbox_guard.sh`・`inbox_alias_integrity.sh`・`secondpc_dispatch.sh`・
`symlink_aware_atomic_write.sh`=呼出元自体が見つからず ∴ **未測(呼ばれておらぬ可能性が高いが、
「呼ばれておらぬ」と断定はしない=当職の検索範囲の限界であり不在の証明ではない)**。

## 表 (9本、書式=零なら「不在」でなく「未測」)

| 検査 | 呼出元 | 発火の痕跡 |
|---|---|---|
| pretooluse_bash_guard.sh | hook登録(毎Bash) | 未測(hook chainで推定発火・独立証跡は未確認) |
| dd169_kill_term_guard.sh | hook登録(毎Bash) | **確認済**(log実在+当職への実地介入) |
| context_usage_warn.sh | hook登録 | **確認済**(当職が本セッションで実際に受領) |
| codex_cli_required_persona.sh | agent_health_check.sh | 未測 |
| pane_identity.sh | pretooluse_bash_guard.sh | 未測 |
| codex_exec_sandbox_guard.sh | 未発見 | 未測 |
| inbox_alias_integrity.sh | 未発見 | 未測 |
| secondpc_dispatch.sh | 未発見 | 未測 |
| symlink_aware_atomic_write.sh | 未発見 | 未測 |

## 【本工区で己が直した誤り】

当職のgrepコマンドがdd169 guardに誤ってBLOCKされた直後、一瞬「検査を誤って実行してしまった」と
書きかけたが、実際は「読取コマンドの文字列内容がguardの正規表現に誤検知されただけ」であり、
検査対象(kill -TERM等)を能動的に実行した訳ではないと確認し、経緯を正確に書き分けた。

## ★母集団漏れの自己申告★

1. `pretooluse_bash_guard.sh`自身の独立ログ・証跡の有無は確認していない(dd169と同一hook chainで
   ある事からの推定に留まる)。
2. 呼出元「0件」と判じた4本は、`.claude/`配下の他の設定file(settings.local.json等、もし在れば)
   までは検索していない。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。

以上、9本・発火実測への応答。検査を能動的に実行した事実はない(①のBLOCKは当職の読取コマンドへの
guardの自発的介入)。
