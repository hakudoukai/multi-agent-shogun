# km-195 ―― `sh -n` と `bash -n` は別の器 ―― shebang を見ずに文法を検める器の census(紙のみ・直さぬ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `tsugi_no_tama_195_20260918T2105`(task_id km-195・家老mac 発・家老自身の疵を種・板は起票後に家老が焼く)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T21:06:19+0900 / 着手便 21:05(宣ETA 21:40)/ 測り 21:02〜21:05
- 枝 = `ashigaru-mac-1/km-195-kanmuri-wo-yomanu-shirabe-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km195)。押さず。束名は家老の指定。
- 出所 = 家老が `#!/bin/bash` の器に `sh -n` を当て `done < <(…)` で「syntax error」を得、健全な file を疵と読んだ。`bash -n` は rc 0。

## ㋐ 結語

1. ★macOS の `sh` の実体(㋒・raw/20・実測)★: `/bin/sh` は `GNU bash 3.2.57` で `shopt -o posix` = ★on★(POSIX 模式の bash 3.2・/bin/bash とは別 binary だが同じ版)。`<( )`(process substitution)は POSIX 模式で無効ゆゑ `sh -n` は撥ねる(種 `while read -r l; do :; done < <(echo a)`: bash -n rc 0 / ★sh -n rc 2★ / zsh -n rc 0)。
2. ★實射(㋑・raw/30・31)★: 己の樹(origin/main)の冠 `#!/bin/bash`|`#!/usr/bin/env bash` の .sh = ★109 本★(全 .sh 110 の内)。三様 -n の四分: 甲(三様 rc0)★97★ / ★乙(bash 0・sh 非0 = 本件の形)11★ / 丙(bash 非0 = 真の疵)★0★ / 丁(bash 0・sh 0・zsh 非0)1。乙 11 本の sh の叫びは ★11/11 が `unexpected token \`<'`(process substitution)★。陽性対照 = 乙の一本の写しに `if [` を足す → 三様とも非0(bash 2・sh 2・zsh 1・元は不変 sha 0db0857e…)。陰性対照 = 同じ file 二度 = 同値(bash 0・sh 2・zsh 0)。
3. ★census(㋐・raw/10)★: 文法を検める器の呼出の字面 = 74 行 / 31 file(己の樹 73・~/bin 1)。内 ★註・指示行 36★(`# shellcheck disable=`/`source=` と註 = 呼出でない・別勘定)。呼出 38 = 甲(冠を読む)2 / 乙(器を固定)30 / 丙(可変)0 / 測れぬ(二形 A≠B)6 → ★和 74 = 母數(排他)★。★code の呼出は 2 本のみ★: shim/hakudokai/hakudokai_audit_scheduler.sh L48 `bash -n "$f"`(乙・冠を見ず bash 固定)・scripts/agent_health_check.sh L388 `python3 -m py_compile`(乙・py 固定)。CI .github/workflows/test.yml L173/181 の shellcheck 8 行は字面は乙だが ★shellcheck 自身が冠を読む★(㋓ 實測: 同じ中身で冠を `#!/bin/sh` に替へると SC3001「process substitution is undefined in sh」が 2 件立つ)= 甲の器。紙 19 行(CONTRIBUTING/SECURITY/docs)は例文。
4. 「冠を読んで居る」の判は器で二形(㋓): A = 同じ行に shebang/#!/head -1 の読み・B = 前後 5 行に在る。A≠B 6 を「測れぬ」で別に数へた。
5. 案は ㋔(据ゑず)。

## ㋑ census の作り方(raw/01・10・12)

- 器 = raw/01_walk_syntax_checkers.py(己・python os.walk・歩き根は argv・読むのみ)。根 = /Users/momizimac/wt/a1-km195(origin/main の樹)・/Users/momizimac/bin。除外 .git/node_modules/.venv/__pycache__/queue・bak 名。走査 = sh/bash/bats・py・yaml・md/txt/json。深さ 10。rc 0。刻 21:03。
- 網 = `(bash|sh|zsh|dash|ksh) -n` / `shellcheck` / `py_compile` / `compileall`。註行と `# shellcheck disable=|source=|shell=` の指示行は「註」に分ける(初版は之を呼出と数へ 乙 56 と出た=疵・round1 の控を残す)。
- 判: 甲 = A も B も shebang 読みの字面(shebang|#!|head -1|sed -n 1p|interpreter|冠)/ 乙 = 何れも無し / 丙 = 器名が `$SHELL`/`$SH`/argv 等で可変 / 測れぬ = A≠B。
- 陽性対照(raw/12): 己の種 5 形(`bash -n`・`sh -n`・冠を head -1 で読んで分ける・`"$SHELL" -n`・py_compile)= 甲 1(冠を読む行)が甲、他は乙/測れぬに分かれた。
- 排他: 甲+乙+丙+測れぬ+註 = 母數(74)。

| kind | 行 | file | 甲 | 乙 | 丙 | 測れぬ | 註 |
|---|---|---|---|---|---|---|---|
| sh/bats | 41 | 20 | 1(己の種) | 2(hakudokai_audit_scheduler L48・agent_health_check L388) | 0 | 3 | 35 |
| py | 6 | 3 | 0 | 3(docstring の文言) | 0 | 2 | 1 |
| yaml(CI) | 8 | 1 | 0 | 8(test.yml の shellcheck) | 0 | 0 | 0 |
| 紙 | 19 | 7 | 1 | 17 | 0 | 1 | 0 |
| ~/bin | 1 | 1 | 0 | 0 | 0 | 0 | 1(idle_backlog_wake.sh の source= 指示) |

★家老の器(~/bin/karo_mac_*)に文法検めの呼出は 0★(零の札: 根 ~/bin・深さ 1・rc 0・陽性対照 = 己の種)。家老の `sh -n` は手で打たれた命令 = 網の外(手打ちの履歴は歩かず)。

## ㋒ 三様 -n の實射(raw/30・31)

| 分 | 本数 | 名 |
|---|---|---|
| 甲(三様 rc0) | 97 | ― |
| ★乙(bash 0・sh 非0)★ | ★11★ | queue/reports/karo-main/20260917_safe_nudge_doppler_bats_shim.sh・scripts/agent_health_check.sh・scripts/agent_status.sh・scripts/checks/codex_cli_required_persona.sh・★scripts/checks/karo_mac_gate4.sh★・scripts/checks/symlink_aware_atomic_write.sh・scripts/inbox_watcher.sh(zsh も 1)・scripts/ntfy.sh・scripts/ntfy_listener.sh(zsh も 1)・scripts/ratelimit_check.sh・scripts/redundancy/shogun_report_watcher.sh |
| 丙(bash 非0 = 真の疵) | 0 | ― |
| 丁(bash 0・sh 0・zsh 非0) | 1 | tests/e2e/mock_behaviors/common.sh(zsh: parse error near `200` = `200>` の fd 記法・zsh の方言差) |

- 乙 11 本の叫びは悉く `<(`(process substitution・raw/30_sanyou.tsv)。∴ ★`sh -n` は健全な bash の器 11 本を疵と呼ぶ★。bash -n は 109/109 で rc 0(丙 0)。
- 陽性対照・陰性対照は ㋐2 の通り(raw/31)。

## ㋓ 判定を器で決めた事・shellcheck の冠読み

- 二形 A/B の食ひ違ひ = 6(悉く B のみ = 近くの行に冠の読みが在るが同じ行には無い)。
- shellcheck(0.10.0)は ★冠から shell を選ぶ★(同じ中身で冠 bash → 警告 0・冠 sh → SC3001 ×2)。∴ CI の shellcheck 呼出は「器を固定して呼ぶ」字面だが、器自身が冠を読むゆゑ本件の形(sh で bash を検める)には落ちぬ。

## ㋔ 案(★紙のみ・据ゑぬ・委員長の許可の後★)

- 文法を検める時は ★冠から器を引く★: `case "$(head -1 "$f")" in *bash*) bash -n "$f";; *zsh*) zsh -n "$f";; *) sh -n "$f";; esac`。冠の無い file は「測れぬ」で止める(sh に落とさぬ)。
- 手で検める時も同じ: `sh -n` は POSIX 模式の bash 3.2 であり bash の器には合はぬ ―― `bash -n` か `shellcheck`(冠を読む)を使ふ。
- hakudokai_audit_scheduler.sh L48 の `bash -n` 固定は、対象が bash の器に限られる限り害無し(冠を読む形にするなら一行)。

## ㋕ 測れぬ物・意味せぬ事

- 手で打たれた命令(家老の `sh -n`)は歩いて居らぬ。
- 他 PC(Linux)の `sh` は dash であり、撥ねる形が macOS と同じかは測れぬ(dash も `<(` を持たぬ筈だが叫びの字面は別)。
- 丁 1 本(zsh 非0)は zsh の方言差であり file の疵ではない(bash で走る器)。
- 「甲 97」は -n(文法)のみ。走らせて居らぬ。

## ㋖ 疵

⑴ census 初版が `# shellcheck disable=` の指示行を呼出と数へ 乙 56 と出た(round1 控・直して再走)⑵ process substitution の種の初版が `while` 無しで bash でも落ちた(round1 控・作り直し)⑶ 着手便は km-194 の納めの後に出した(順)。

## 宣⇔實

宣ETA 21:40。實 = 納め便の刻(紙の外・21:1x 見込み)。
