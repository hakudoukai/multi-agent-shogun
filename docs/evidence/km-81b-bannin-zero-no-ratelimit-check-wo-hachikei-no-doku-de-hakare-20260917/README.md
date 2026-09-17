# 第77弾 ―― 番人が一本も無い file(scripts/ratelimit_check.sh)へ八形の毒を当てて測れ: 毒は閾へは届かず「數比較器の左項」へ落ち、枠の口では 20 走の内 14 が黙つて OK(⚠️ 無し)を刷る ―― 直し形は紙にのみ書く

- 弾: km-81b(家老便 msg_20260917_102252_53799ee8・札 sha16 2b8df2e59c8d4465 52行)/ 束 docs/evidence/km-81b-bannin-zero-no-ratelimit-check-wo-hachikei-no-doku-de-hakare-20260917 / 書手 ashigaru-mac-1 / 宛 karo-mac(監査 gunshi-mac へ pc_handshake)
- 裁: seq324588(親 324585)の ⑵ inbox_watcher(當席= 家老mac)・⑶ 番人無し 4file(專任2 km-78)と ★重ならぬ一本★ = scripts/ratelimit_check.sh(ccflare の枠を見る器)。1弾=1file・負テスト両対照・repo の器へ 0 字(束の中に建てた)・稼働 process 不觸(裁 323062⑷)・直し形は紙のみ(据ゑず)。
- 刻: 紙を書いた刻 2026-09-17T10:42 / 着手便 msg_20260917_102839_2d4c53b5(10:28:39・宣ETA 30 分・起点= 着手便 timestamp・端点= 納め最終便 timestamp)/ 凍結点 HEAD 6ba8fcb2 / 的= disk = HEAD = main(sha16 7f1e031114966744・22145B・582 行・inode 1238425・`00`)。
- 器: 讀むのみ。scripts/ ~/bin/ lib/ へ 0 字・箱へは家老便 1 通の既讀印と着手便 1 通のみ・process へ信号 0・send-keys 0。的を其の儘一度起こした(`46`・引数無し・tmux へは届く前に止まる)。生は `raw/`(以下 `NN`)。臺帳= MANIFEST.txt・門控= _gate/(員外・名は走ごとに一意)・_after/ は臺帳の後。
- 家老札の數(582 行・fix_threshold 0 本・受口 3・比較器 13)は ★信ぜず己の器で引き直した★(`10`)。582 行・fix_threshold 0 は一致。「受口 3」は甲(`${NAME:-既定}`)で 5 口・「比較器 13」は `[[ "$` の形で 24 行/比較器の個で 66 ―― 札の數の定義が分からぬゆゑ ★己の定義を欄名へ焼いて数へ直した★(㊁㊂)。

## ㊀ 結語を先に

1. ★㋐ 受ける口は二定義で別々に数へた: 甲 `${NAME:-既定}` の字面 5 口(L108・417・492・543・556)/ 乙「外から値が入る変数」58 口 46 名 / 丙 函数内で `$1/$2` を受ける local 2 名(母數の外)。守る表(fix_threshold/env_state/num_same_op/_th_say/`for _t in`)は ★0 行★ ―― 零の四札: 陽性対照= 同じ語を inbox_watcher.sh に当てて 22 行 rc0 / 陰性対照= ZZ_KM81B_NEG 0 行 rc1(両 file)/ 根= 的 file 一本 全 582 行・深さ 0 / 刻 10:34:25(`10`)。★閾 3 名(L40-42)と裸の 80 ×2(L462・470)は literal で定まり `${NAME:-}` の口を持たぬ ∴ 毒は閾へは届かず、★數比較器の左項(外来の値)★ へ落ちる。★
2. ★㋑ 比較器 66 件= 數 17 / 字面 16 / 單項 27 / case 2 / 変数を命令として実行 3 / 正規 1。數 17 は ★悉く `[[ ]]`★(`[ ` は 0 行)。`[[ ]]` の數比較は家老の弾⑴が測つた `[` と ★挙動が違ふ★: 20桁(2^63超)は rc2 に非ず ★黙つて巻く★(P1 では OK・P3 では ⚠️)/ rc2(構文誤り)が出るのは 非ASCII・`?`・`1e3` で、if は偽へ落ち stderr 1 行・process の rc は 0 の儘 / 識別子(abc・None)は変数名と讀まれ ★set -u が「unbound variable」rc1 で鳴つて止める★(`30`)。★
3. ★㋒ 八形(10 値)× 6 口= 60 走: 黙つて通る(枝= 正常・stderr 0)37 / 黙つて別枝 13 / 鳴つて止まる 5 / 刷つて通る 4 / 刷つて別枝 1。★枠の口(P3 5h・P4 7d)20 走の内 14 が黙つて OK(⚠️ 無し)★ ―― 空白・負数・2・01・+1・␊1・空文字は皆「N% used」を刷つて STATUS=OK。両対照は 7 口とも ○(陽性= 正しい別の値で枝が変はる / 陰性= 正常値で黙つて通る・`35`)。∴ ★害の向き= 「枠を見ずに走る」(黙る)が主★。「見えぬ儘止まる」は set -u が鳴らすゆゑ黙らぬ(未設定・None・abc・`--lang` 単独 = rc1・stderr 1 行)。稀に偽の警報(P1 空白/負数/␊1 → CRITICAL・P2 20桁 → WARNING に化物の數)。★
4. ★㋓ 三分類: 母數 48(甲 5 ∪ 乙 46・重なり 3)= 閾 0 + 旗 2(was_zoomed・CLAUDE_EXTRA_ENABLED)+ 状態変数 46 ―― 和 48 = 母數 ★一致★(各名は丁度一つの類・assert・`40`)。閾 0 は「閾が無い」のではなく「閾が口を持たぬ」から(母數の外に literal 3+2)。數比較器の左項 10 の内 母數に在る 3(ctx・CODEX_LIMIT_HITS・CLAUDE_TODAY_TOTAL)・fh_int/sd_int は乙 CLAUDE_5H/7D_UTIL の `%.*` 派生。★
5. ★㋔ 稼働 0(全 process の lsof を名で当てて 0・ps 0・陽性対照= watcher を pid で引き 3 本 inode 20564860)・呼び手 0(scripts/ config/ instructions/ ~/bin/ launchd crontab)・disk inode 1238425 = HEAD = main(22145B)・6 commit 最新 ff30760(05-07)。★此の Mac の bash は /bin/bash 3.2.57 のみ(homebrew bash 無し・`declare -A` rc2)ゆゑ、本走は L30 の source 先 lib/_section18_roles.sh L108 `declare -A` で set -u が「shogun: unbound variable」を刷り rc1 で止まる(`46`)★ → 的の L64 にも比較器(L397〜)にも届かぬ。lib 三本は在る(git 追跡)―― 着手便に書いた「三本無し」は ★己の path 誤り★(㊇疵⑥)。★

## ㊁ ㋐ 受ける口と守る表(`10` / 10_ukeru.tsv・10_uke.txt・10_otsu_disk.txt)

### 表A 甲 `${NAME:-既定}` の字面(disk・HEAD 逐語同一・5 口)

| 行 | 名 | 出所の種 | 逐語 |
|---|---|---|---|
| 108 | 2 | 位置引数(函数の第2引数・既定 -80) | `local start="${2:--80}"` |
| 417 | CODEX_LIMIT_HITS | 内部状態(既定 0・L414 の grep -c 由来) | `CODEX_LIMIT_HITS="${CODEX_LIMIT_HITS:-0}"` |
| 492 | CLAUDE_DATA_DATE | 内部状態(既定 $TODAY) | `if [[ "${CLAUDE_DATA_DATE:-$TODAY}" != "$TODAY" ]]; then` |
| 543 | codex_model | 内部状態(既定 gpt-5.3-codex) | `printf "  Quota (%s)\n" "${codex_model:-gpt-5.3-codex}"` |
| 556 | CODEX_MODEL_LABEL | 内部状態(既定 Model) | `printf "  %s:\n" "${CODEX_MODEL_LABEL:-Model}"` |

★甲の 5 口は悉く「既定を持つ内部変数」であり、環境変数から閾や旗を受ける口は ★一つも無い★(inbox_watcher.sh の `ASW_PROCESS_TIMEOUT=${ASW_PROCESS_TIMEOUT:-1}` の形は 0 行)。

### 表B 乙「外から値が入る変数」(disk・HEAD 同一・58 口 46 名・全行は 10_ukeru.tsv)

出所の種= env `$HOME`(L35・36・190)/ argv(L18 `--lang $2`)/ 命令置換 `$( )`(tmux・curl/python・grep・date・cd…・53 口)/ read(L299・process substitution)。丙= 函数内で `$1/$2` を受ける local(pane L107・130 / start L108)は「内部から渡る」ゆゑ乙に数へぬ。

### 守る表 ―― 零の四札

| 札 | 値 |
|---|---|
| 的(disk) 語 `fix_threshold\|env_state\|num_same_op\|_th_say\|^for _t in ` | ★0 行・rc 1★(grep -c は 0 の時 rc1 = 器が「無い」と言ふ) |
| 的(HEAD) 同語(python re) | 0 行 |
| ★陽性対照★ scripts/inbox_watcher.sh(disk)同語 | 22 行・rc 0 → 器は同じ語で鳴る |
| ★陰性対照★ ZZ_KM81B_NEG | 的 0 行 rc1 / inbox_watcher.sh 0 行 rc1 |
| 根と深さ | 的 file 一本・全 582 行・再帰無し(深さ 0) |
| 刻 | 2026-09-17T10:34:25+0900 |

### 受けぬ閾(母數の外)

| 行 | 逐語 | `${NAME:-}` の口 |
|---|---|---|
| 40 | `CODEX_CONTEXT_WARN=20` | 無 |
| 41 | `CODEX_CONTEXT_CRIT=10` | 無 |
| 42 | `CODEX_LIMIT_HITS_WARN=3` | 無 |
| 462 / 470 | `if [[ "$fh_int" -ge 80 ]]` / `if [[ "$sd_int" -ge 80 ]]` | 裸の literal |

∴ 此の器で「番人が無い」の意味は inbox_watcher.sh と ★形が違ふ★: 彼処は「環境から受けた閾/旗に番人が無い」、此処は「閾は固定で、★比較器の左項へ流れ込む外来の値★(tmux の出力・API の JSON・log の grep -c)に番人が無い」。

## ㊂ ㋑ 比較器の種(`10` / 10_hikakuki.tsv・disk 66 件・HEAD 同一)

| 種 | 件 | 左項の内訳 |
|---|---|---|
| 數(`[[ ]]` 内・算術評価) | 17 | 内部 9(`$#` L16・配列長 ×7・`$count` L536)/ ★外来 8★(ctx ×4 L397・400・528・530 / CODEX_LIMIT_HITS L422 / fh_int L462 / sd_int L470 / CLAUDE_TODAY_TOTAL L490) |
| 字面(==/!=) | 16 | 二値の旗 3(was_zoomed `!= "1"` ×2・CLAUDE_EXTRA_ENABLED `== "True"`)/ 番人 3(ctx `!= "?"` ×2・CLAUDE_5H_UTIL `!= "?"`)/ 其の他 10 |
| 單項(-n/-z/-f/-x) | 27 | 空/存在の番人 |
| case | 2 | L17 `case "$1"`(argv)・L99 `case "${AGENT_CLI[$agent]}"` |
| 変数を命令として実行 | 3 | L122・149 `if $restore_zoom`・L344 `if ! $_rl_quota_done`(内部の true/false) |
| 正規 =~ | 1 | L420 `[[ "$CODEX_LIMIT_HITS" =~ ^[0-9]+$ ]]`(★上限無し★ → 20桁が通る) |

★`[[ ]]` の數比較器の性(`30` で實測・bash 3.2.57)★:
- 20桁 `99999999999999999999`: rc2 は出ず ★黙つて巻く★ ―― `[[ … -lt 10 ]]` 偽・`-ge 80` 真。家老の弾⑴(`[` は rc2 → else へ fail-open)とは ★別の形★。
- 非ASCII(全角空白)・`?`・`1e3`: `syntax error: invalid arithmetic operator` / `operand expected` / `value too great for base` を stderr へ 1 行刷り ★rc2 → if 偽★。set -e は if の条件では止めぬ ∴ process は続き rc 0。
- 識別子(abc・None): 変数名と讀まれ、★set -u が「unbound variable」で rc1★ ―― 鳴つて止まる(`[` なら「integer expression expected」rc2 で黙つて偽)。
- 空文字・空白(半角)・先頭改行: 算術で 0 / 1 と讀まれ ★黙つて數に化ける★(P1 空白 → 0 < 10 → CRITICAL)。

## ㊃ ㋒ 八形の毒を實際に当てた(`30` / 30_doku.tsv 100 走・`35` 集計)

写し器: 的から錨(行の字面・一致 1 本を assert)で区画を逐語で切り出し、頭に L8 `set -euo pipefail` と閾 L40-42 を置く。値は env で渡す(bash は env を其の名の変数として受ける・未設定= env に無し)。/bin/bash 3.2.57・env LANG=C.UTF-8。

| 口 | 区画 | 出所 | 八形 10 | 黙つて通る(毒が見えぬ) | 刷つて通る | 黙つて別枝 | 刷つて別枝 | 鳴つて止まる | 陽性 | 陰性 |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 ctx | L339+L396-406 | tmux capture の grep | 10 | 2(空文字→`?`は宣どおり・20桁) | 1(全角・stderr 2) | ★6★(空白・負数・2・01・+1・␊1 → 偽 CRITICAL) | 0 | 1(未設定 set -u) | ○ | ○ |
| P2 CODEX_LIMIT_HITS | L417-427 | log の grep -c | 10 | 9(L419-420 の番人が 0 へ倒す・刷らず) | 0 | ★1★(20桁 → WARNING「limit_hits=9999…/h」) | 0 | 0 | ○ | ○ |
| P3 CLAUDE_5H_UTIL | L458-475 | OAuth API(python が刷る) | 10 | ★7★(空文字は番人で段ごと消え・空白/負数/2/01/+1/␊1 は「N% used」を刷り OK) | 1(全角) | 1(20桁 → 偽 ⚠️) | 0 | 1(未設定) | ○ | ○ |
| P4 CLAUDE_7D_UTIL | L468-475(★`?` の番人無し★) | 同上 | 10 | ★7★ | 1(全角) | 1(20桁) | 0 | 1(未設定) | ○ | ○ |
| P5 CLAUDE_TODAY_TOTAL | L490-501 | python sum | 10 | 3 | 1(全角) | 4(2・01・+1・␊1 → Tokens 段を刷る) | 1(20桁 → printf が 9223372036854775807 に飽和・warning 1 行) | 1(未設定) | ○ | ○ |
| P6 LANG_MODE | L435-439(字面) | argv | 10 | 9(域外は悉く ja へ) | 0 | 0 | 0 | 1(未設定) | ○ | ○ |
| P7 argv --lang | L13-25(case) | argv | (外・8 走) | ― | ― | 4(空文字・空白・xx・␊en を其の儘受ける) | ― | 2(`--lang` 単独= set -u rc1 / `--bogus`= rc1 だが「Unknown option」は ★stdout★・stderr 0) | ○ | ○ |

補(八形の外・python が現に刷り得る値・`30`): `None`(JSON null)→ P3/P4 とも set -u で rc1 鳴つて止まる / `?`(鍵無しの既定 L217-222)→ P3 は L458 の番人で Quota 段ごと消えて OK(黙る)・P4 は番人無しゆゑ「?% used」を刷り stderr 1 行・OK / `1e3` → stderr 1 行・OK / `101` → ⚠️(數としては正)。LC_ALL=C でも P2 の全角は 0 へ(tr の locale 差は此処では出ぬ)。

★害の向き(家老が「貴席が測つて決めよ」と委ねた分)★: 枠の口(P3+P4)20 走の内 ★14 が黙つて OK★・2 が偽 ⚠️・2 が刷つて OK・2 が鳴つて止まる(`35`)。∴ ★主= 「枠を見ずに走る」(讀めぬ枠が OK の顔をする・黙る)★。副= 「鳴つて止まる」(set -u・None/未設定 ― 黙らぬゆゑ「見えぬ儘」ではない)。稀= 偽の警報(P1 6 形・P2/P3/P4 の 20桁)。★「讀めぬ枠は OK ではない」が此の器に無い一文である。★

## ㊄ ㋓ 三分類と排他性(`40` / 40_sanbun.tsv)

| 類 | 則(器が決める) | 名 |
|---|---|---|
| 閾(數で比べる) | 數比較器の右項に立つ | ★0★(閾は literal ゆゑ母數の外: L40-42 + 80×2) |
| 旗(0\|1・二値) | 立つ比較器が悉く二値 literal との字面比較か `if $名` | 2= was_zoomed(`!= "1"`)・CLAUDE_EXTRA_ENABLED(`== "True"`) |
| 状態変数(process 内で更新) | 残り | 46 |

★排他性★: 母數 48(甲 5 ∪ 乙 46・重なり 3= CLAUDE_DATA_DATE・CODEX_LIMIT_HITS・CODEX_MODEL_LABEL)・各名は丁度一つの類(assert)・三類の和 48 = 母數 ★一致★。丙 2 名(pane・start)は母數の外と宣した。單項(-n/-z/-f/-x)は類の根拠にせぬ。「状態変数」は「毒が効かぬ」の意ではない ―― 30 の P1-P5 の左項は悉く状態変数の類であり、類は番人の形(閾→數の番人・旗→case・状態→出所の番人)を決める為の物。

## ㊅ ㋔ 稼働・inode・呼び手・此の PC で走るか(`45`・`46`・`00`・読取のみ・信号 0)

| 問 | 測り |
|---|---|
| 的を開く process | lsof を path で 0 行 rc1 / ★全 process の lsof -n を名で当てて 0 行 rc0★(14943 行・己の系譜を pid の鎖で除く)/ ps 0 |
| 陽性対照(同じ器) | inbox_watcher.sh を ★pid で★ 引き 3 本(9826/9838/9859・fd 255r・inode 20564860・74274B)―― path で引くと 0(稼働は置換前の inode を開く・㊇疵③) |
| disk ⇔ git | inode 1238425 / 22145B / mtime 07-11 20:05 / sha16 7f1e0311 = HEAD blob 239d5316 = main(git diff 0)/ 6 commit・最新 ff30760(2026-05-07) |
| 呼び手 | scripts/ config/ instructions/ ~/bin/ に 0 行(.bak と的自身を除く)/ launchd plist 0 / crontab 0(rc1) |
| source 三本(L28-30) | SCRIPT_DIR= `scripts/..` = ★repo 根★ → lib/agent_status.sh・lib/cli_adapter.sh・lib/_section18_roles.sh ★在★(git 追跡・check-ignore rc1) |
| 此の PC の bash | `command -v bash` = /bin/bash 3.2.57 のみ(/opt/homebrew/bin/bash・/usr/local/bin/bash 無)・`declare -A` rc2 |
| 本走(`46`・引数無し) | ★rc 1・stderr 1 行「lib/_section18_roles.sh: line 108: shogun: unbound variable」★ ―― L108 `declare -A SECTION18_ROLE_ALIASES=( [shogun]=… )` を bash 3.2 が算術の添字と讀み set -u に触れた。陽性対照 `--help`= rc0・Usage 1 行(L19-22 は source より前) |

∴ ★此の Mac では的は L30 の source の中(lib L108)で ★鳴つて★ 止まり、L64 `declare -A` にも比較器にも届かぬ。「稼働に無い」は推定でなく構造(bash 3.2)である。★ 的が走る筈の Linux(bash 5.x)での挙動と、lib 三本が其処に在るかは ★測れぬ★(SSH は本弾の外)。lsof 0 は「今」の一瞬(one-shot CLI)。

## ㊆ 直し形 ―― 紙にのみ書く(★据ゑて居らぬ★・repo へ 0 字・据ゑるは當席の役)

閾に口が無いゆゑ fix_threshold(閾の番人)を当てる所が無い。要るのは ★左項(外来の値)の番人★ を比較器の直前に置く事 ―― 「讀めぬ値は OK ではない」を刷つて UNKNOWN へ倒す(fail-closed)。

```bash
# ⑴ 枠の口(P3/P4・L458-475 の前)―― 百分率の番人: 0..100 の十進のみ通す。空/符号/空白/改行/文字/4桁以上は名指して刷り UNKNOWN へ
_pct_ok(){ case "${2%.*}" in ''|*[!0-9]*|????*) printf '★枠 %s を比較器が扱へぬ(「%s」) ―― STATUS=UNKNOWN(枠が讀めぬ)★\n' "$1" "${2//$'\n'/␊}" >&2; return 1;; esac; [ "${2%.*}" -le 100 ]; }
if _pct_ok CLAUDE_5H_UTIL "$CLAUDE_5H_UTIL"; then fh_int=${CLAUDE_5H_UTIL%.*}; … 現 L461-467 …; else CLAUDE_STATUS="UNKNOWN(5h 枠が讀めぬ)"; fi
if _pct_ok CLAUDE_7D_UTIL "$CLAUDE_7D_UTIL"; then sd_int=${CLAUDE_7D_UTIL%.*}; … 現 L469-475 …; else CLAUDE_STATUS="UNKNOWN(7d 枠が讀めぬ)"; fi
# ⑵ ctx(P1・L339 の次)―― 3 桁以下の十進のみ。外は `?`(宣どおりの「不明」の枝)へ、刷つて倒す
case "$ctx" in ''|*[!0-9]*|????*) printf '★ctx を比較器が扱へぬ(「%s」) ―― ? へ倒す★\n' "${ctx//$'\n'/␊}" >&2; ctx="?";; esac
# ⑶ CODEX_LIMIT_HITS(P2・L420)―― 上限を焼く(20桁を通さぬ)
[[ "$CODEX_LIMIT_HITS" =~ ^[0-9]{1,18}$ ]] || { printf '★limit_hits を比較器が扱へぬ(「%s」) ―― 0 へ倒す★\n' "$CODEX_LIMIT_HITS" >&2; CODEX_LIMIT_HITS=0; }
# ⑷ CLAUDE_TODAY_TOTAL(P5・L490 の前)―― 同形(printf %'d の飽和を封じる)
[[ "$CLAUDE_TODAY_TOTAL" =~ ^[0-9]{1,18}$ ]] || { printf '★tokens を比較器が扱へぬ(「%s」) ―― 0 へ倒す★\n' "$CLAUDE_TODAY_TOTAL" >&2; CLAUDE_TODAY_TOTAL=0; }
# ⑸ argv(P7・L18・L23)―― 域を焼き、誤りは stderr へ
--lang) case "${2-}" in en|ja) LANG_MODE="$2" ;; *) echo "Unknown lang: ${2-<none>}" >&2; exit 1 ;; esac; shift 2 ;;
*) echo "Unknown option: $1" >&2; exit 1 ;;
# ⑹ 頭(L8 の次)―― 此の器は連想配列を使ふ ∴ bash 4 未満を名指して止める(今は lib L108 で set -u が代弁して居る)
[ "${BASH_VERSINFO[0]}" -ge 4 ] || { echo "★bash >= 4 が要る(此処は ${BASH_VERSION})★" >&2; exit 1; }
```

- ⑴ が本弾の的(ccflare の枠)を閉ぢる。八形 10 値の内 2・01 は正しい百分率ゆゑ通り(陰性)、残り 8 と補(None・?・1e3・abc・101)は ★刷つて UNKNOWN★ へ(陽性)。20桁は `????*` が受ける。
- ⑵⑶⑷ は同形の番人(出所= tmux/grep/python の外来値)。⑸ は字面の域。⑹ は此の Mac で「lib の中で set -u が鳴る」を「己が名指して鳴る」へ。
- ★負テスト両対照(据ゑる時)★: 陽性= 本束の `30_P3.sh`/`30_P4.sh` の頭に ⑴ を挟み、八形の 8 形+補 5 形で「stderr 1 行 ∧ STATUS=UNKNOWN」を見る / 陰性= 10.0・85.5・2・01 で stderr 0 行・枝は今と同じ。`30_doku.py` の KUCHI に ⑴ 入りの script を足せば其の儘負テストに成る(束の中で当てた・repo へは書いて居らぬ)。
- 据ゑるのは裁の後・當席の役。Linux(bash 5)での `[[ ]]` 算術の差は据ゑる前に其処で測るべし(本弾は 3.2 のみ)。

## ㊇ 此の紙が意味せぬ事・疵

- 意味せぬ: Linux(bash 5.x)での挙動(写し器は 3.2 のみ)/ lib 三本が他 PC に在るか / 稼働 0 は今の一瞬 / 門の rc0 は形のみ / 「黙つて通る」は害の有無を言はぬ(口ごとに ㊃ で讀んだ)/ 三分類の則は己が決めた則であり裁の則ではない。
- ★疵①(`10` 初走)★: 陽性対照の數を結語に「4 行」と ★手で書いた★(器は 22 行)。「紙の數は器で抽く」を己が破つた。f-string へ直し `.first` に残す。
- 疵②(`10` 初走): 乙に `$((count + 1))` の `$((` と函数内の `$1/$2`(pane・start)が混入し 62 口 49 名と出た → `$(` の直後の `(` を除き函数内引数を丙へ分けて 58 口 46 名。`.first`。
- 疵③(`45` 初走): 陽性対照を lsof の path で引き ★0 行で倒れた★ ―― 稼働 watcher は置換前の inode を開くゆゑ今の path を開く者は無い。pid で引き直して 3 本。的も全 process の lsof を名で当てる形へ。`.first`。
- 疵④(`30` 初走): 尾の printf 行を `%` 書式で組み `%s` と衝突して一行も出ず(TypeError)。`{VAR}` の replace へ。`.py.first`。
- 疵⑤(`30` 二走): stderr 欄が束の長い path に食はれ本文が見えなんだ → path を raw/ に縮めて三走。rc・行数・枝の三欄は diff で ★同一★ を検めた。`.tsv.first`・`.txt.first`。
- ★疵⑥(`00`・`45`・着手便)★: L28-30 の source 先を `scripts/lib/` と誤読した(L10 SCRIPT_DIR は `scripts/..` = repo 根)→ 着手便 msg_20260917_102839_2d4c53b5 に「三本が disk に無し ∴ L28 で止まる」と ★誤りを送つた★。00 `.first`・45 `.first`/`.second`。納め便で訂正する。
- 疵⑦(`46` 初走・二走): 初走は測る前に讀み(「L28 で file 無し」)を書いた。二走は讀みを loop の最後の走(--help)から取り「止まらなんだ」と書いた(loop 外の index は n−1)。三走で本走の結果を名指して導く。`.first`・`.second`。
- 疵⑧(`45` 初走): 結語に「稼働 0・呼び手 0」を手で書いた → f-string へ(二走で直した)。
- 宣⇔實: 納め便(`_after/62`)に書く(紙は門で凍る)。
