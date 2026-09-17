# 第53弾 ★一本の歩き根で 22口 を数へ直し、6/7/8 を名指す★

席= ashigaru-mac-3(足軽mac3号・專任3) ／ 枝= ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917
task_id= km-53-hitotsu-no-aruki-ne-de-file-suu-wo-soroe-20260917 ／ 下知= 2026-09-17T09:55:00(karo-mac)
紙を組んだ刻= 2026-09-17T10:57:03+0900

## 〇 答(先に一行で)

★6/7/8 は三席の誤りではない。三つの別の母數である。★
加へて本走で ★口 22 其の物も刻の函数であつた★ ―― 同じ條・同じ根で、disk は 10:24 に 23口、10:28 に 22口 と出た(下 二節)。

| 何の定義で | 口 | file | 出所 |
|---|---|---|---|
| 甲 disk(★歩いた其の刻の disk★) / 單位 occ ∧ 既定≥1 ∧ 註 nuku | 22 | 6 | nama/30_kazu_disk.txt(刻 2026-09-17T10:28:20+0900) |
| 乙 凍結点 6ba8fcb(本走の頭で固めた版) / 單位 occ ∧ 既定≥1 ∧ 註 nuku | 22 | 7 | nama/31_kazu_kotei.txt(刻 2026-09-17T10:28:21+0900) |
| 丙 6dbe09e(當席・專任1 が指した版) / 單位 occ ∧ 既定≥1 ∧ 註 nuku | 23 | 7 | nama/32_kazu_6dbe09e.txt(刻 2026-09-17T10:28:22+0900) |
| 丁 6dbe09e ★當席の枡★ / 單位 ★line★ ∧ 既定≥1 ∧ 註 ★komu★ | 22 | 8 | nama/33_kazu_touseki.txt(刻 2026-09-17T10:28:22+0900) |

∴ ★「誰が正しい」ではない。★ 定義丁(專任1 km-77 逐語 = 出現單位・既定≥1・註行除く)で立つのは ★disk 22口/6file★ と ★凍結点 22口/7file★ であり、當席の ★22口/8file★ は ★行單位 ∧ 既定≥1 ∧ 註行込★ の枡で立つ。三つ悉く「其の定義では正しい」。

## 一 ㋐ 一本の歩き根 ―― 根・深さ・除外(宣)・rc・刻

器 = `ki/30_kazu.py`(argv で 源・根・單位・既定閾・註 を受く ―― 枡を argv で動かせる形)。

```
根(歩き根 一本) = scripts .claude   ★三席の食ひ違ひは此処から出る故、一本に固めた★
深さ           = 全深(git 追跡の全 path・上限無し)
頂(根の基点)   = /Users/momizimac/multi-agent-shogun   ★cwd に依らず repo 頂へ固定する(疵①・下 五節)★
除外(宣) ①git 非追跡(.claude/worktrees/ 配下の別 checkout・*.bak 控 等)は根に入らぬ
         ②非UTF-8 は「讀めぬ」として別行に数へる(黙つて落とさぬ)
         ③本器は docs/evidence/ に在り根の外ゆゑ己を数へぬ(★宣して除く★)
```

| 枡 | 刻 | 歩いた/讀めぬ | rc | 條(全)の口 | 丁閾 |
|---|---|---|---|---|---|
| 甲 | 2026-09-17T10:28:20+0900 | 82 / 0 | rev-parse --show-toplevel:0 ls-files:0 | 88 | ★[丁閾] 口= 22  file= 6★ |
| 乙 | 2026-09-17T10:28:21+0900 | 82 / 0 | rev-parse --show-toplevel:0 ls-tree:0 | 79 | ★[丁閾] 口= 22  file= 7★ |
| 丙 | 2026-09-17T10:28:22+0900 | 82 / 0 | rev-parse --show-toplevel:0 ls-tree:0 | 84 | ★[丁閾] 口= 23  file= 7★ |
| 丁 | 2026-09-17T10:28:22+0900 | 82 / 0 | rev-parse --show-toplevel:0 ls-tree:0 | 84 | ★[丁閾] 口= 22  file= 8★ |

★歩いた file は四枡悉く 82・讀めぬ 0・rc 悉く 0★ ―― 母數の器は同じ物である。

### 甲 disk(★歩いた其の刻の disk★) ―― 單位 occ ∧ 既定≥1 ∧ 註 nuku

刻 2026-09-17T10:28:20+0900 ／ ★[丁閾] 口= 22  file= 6★

| file | 口數 | 名:-既定@行 |
|---|---|---|
| `scripts/checks/karo_mac_dasumae_gate.sh` | 2 | DASUMAE_MAX_BYTES:-10485760@20 DASUMAE_READ_TIMEOUT:-10@86 |
| `scripts/inbox_watcher.sh` | 12 | NUDGE_COOLDOWN_SEC:-60@228 NUDGE_COOLDOWN_SEC_CODEX:-300@230 ASW_PHASE:-2@246 ASW_NO_IDLE_FULL_READ:-1@250 NUDGE_COOLDOWN_SEC:-60@329 NUDGE_COOLDOWN_SEC_CODEX:-300@331 NUDGE_COOLDOWN_SEC_CLAUDE:-60@335 ASW_NO_IDLE_FULL_READ:-1@504 APPROVAL_ALERT_COOLDOWN:-300@933 MAX_TYPING_SKIP:-5@1101 INOTIFY_TIMEOUT:-30@1569 ASW_PROCESS_TIMEOUT:-1@1633 |
| `scripts/lib/detect_stale.sh` | 1 | DETECT_STALE_STALE_SEC:-120@33 |
| `scripts/pane_enter_watcher_supervisor.sh` | 4 | STALE_SEC:-300@50 POLL_SEC:-10@50 STALE_SEC:-300@52 POLL_SEC:-10@52 |
| `scripts/stop_hook_inbox.sh` | 2 | STOP_HOOK_STDIN_TIMEOUT:-10@64 MASS_UNREAD_THRESHOLD:-5@197 |
| `scripts/watchdogs/enter_restart_commander_watchdog.sh` | 1 | ER_THRESHOLD_MIN:-2@35 |

### 乙 凍結点 6ba8fcb(本走の頭で固めた版) ―― 單位 occ ∧ 既定≥1 ∧ 註 nuku

刻 2026-09-17T10:28:21+0900 ／ ★[丁閾] 口= 22  file= 7★

| file | 口數 | 名:-既定@行 |
|---|---|---|
| `scripts/checks/karo_mac_dasumae_gate.sh` | 2 | DASUMAE_MAX_BYTES:-10485760@20 DASUMAE_READ_TIMEOUT:-10@75 |
| `scripts/inbox_watcher.sh` | 12 | NUDGE_COOLDOWN_SEC:-60@185 NUDGE_COOLDOWN_SEC_CODEX:-300@187 ASW_PHASE:-2@203 ASW_NO_IDLE_FULL_READ:-1@207 ASW_PROCESS_TIMEOUT:-1@212 NUDGE_COOLDOWN_SEC:-60@283 NUDGE_COOLDOWN_SEC_CODEX:-300@285 NUDGE_COOLDOWN_SEC_CLAUDE:-60@289 ASW_NO_IDLE_FULL_READ:-1@458 MAX_TYPING_SKIP:-5@1024 INOTIFY_TIMEOUT:-30@1476 ASW_PROCESS_TIMEOUT:-1@1540 |
| `scripts/lib/detect_stale.sh` | 1 | DETECT_STALE_STALE_SEC:-120@33 |
| `scripts/pane_enter_watcher_supervisor.sh` | 4 | STALE_SEC:-300@50 POLL_SEC:-10@50 STALE_SEC:-300@52 POLL_SEC:-10@52 |
| `scripts/redundancy/shogun_report_watcher.sh` | 1 | SHOGUN_REPORT_WATCHER_COOLDOWN:-60@29 |
| `scripts/stop_hook_inbox.sh` | 1 | MASS_UNREAD_THRESHOLD:-5@146 |
| `scripts/watchdogs/enter_restart_commander_watchdog.sh` | 1 | ER_THRESHOLD_MIN:-2@35 |

### 丙 6dbe09e(當席・專任1 が指した版) ―― 單位 occ ∧ 既定≥1 ∧ 註 nuku

刻 2026-09-17T10:28:22+0900 ／ ★[丁閾] 口= 23  file= 7★

| file | 口數 | 名:-既定@行 |
|---|---|---|
| `scripts/checks/karo_mac_dasumae_gate.sh` | 2 | DASUMAE_MAX_BYTES:-10485760@20 DASUMAE_READ_TIMEOUT:-10@75 |
| `scripts/inbox_watcher.sh` | 13 | NUDGE_COOLDOWN_SEC:-60@197 NUDGE_COOLDOWN_SEC_CODEX:-300@199 ASW_PHASE:-2@215 ASW_NO_IDLE_FULL_READ:-1@219 ASW_PROCESS_TIMEOUT:-1@224 NUDGE_COOLDOWN_SEC:-60@295 NUDGE_COOLDOWN_SEC_CODEX:-300@297 NUDGE_COOLDOWN_SEC_CLAUDE:-60@301 ASW_NO_IDLE_FULL_READ:-1@470 APPROVAL_ALERT_COOLDOWN:-300@899 MAX_TYPING_SKIP:-5@1067 INOTIFY_TIMEOUT:-30@1535 ASW_PROCESS_TIMEOUT:-1@1599 |
| `scripts/lib/detect_stale.sh` | 1 | DETECT_STALE_STALE_SEC:-120@33 |
| `scripts/pane_enter_watcher_supervisor.sh` | 4 | STALE_SEC:-300@50 POLL_SEC:-10@50 STALE_SEC:-300@52 POLL_SEC:-10@52 |
| `scripts/redundancy/shogun_report_watcher.sh` | 1 | SHOGUN_REPORT_WATCHER_COOLDOWN:-60@29 |
| `scripts/stop_hook_inbox.sh` | 1 | MASS_UNREAD_THRESHOLD:-5@146 |
| `scripts/watchdogs/enter_restart_commander_watchdog.sh` | 1 | ER_THRESHOLD_MIN:-2@35 |

### 丁 6dbe09e ★當席の枡★ ―― 單位 ★line★ ∧ 既定≥1 ∧ 註 ★komu★

刻 2026-09-17T10:28:22+0900 ／ ★[丁閾] 口= 22  file= 8★

| file | 口數 | 名:-既定@行 |
|---|---|---|
| `scripts/checks/karo_mac_dasumae_gate.sh` | 2 | DASUMAE_MAX_BYTES:-10485760@20 DASUMAE_READ_TIMEOUT:-10@75 |
| `scripts/checks/karo_mac_gate4.sh` | 1 | VAR:-50@71 |
| `scripts/inbox_watcher.sh` | 13 | NUDGE_COOLDOWN_SEC:-60@197 NUDGE_COOLDOWN_SEC_CODEX:-300@199 ASW_PHASE:-2@215 ASW_NO_IDLE_FULL_READ:-1@219 ASW_PROCESS_TIMEOUT:-1@224 NUDGE_COOLDOWN_SEC:-60@295 NUDGE_COOLDOWN_SEC_CODEX:-300@297 NUDGE_COOLDOWN_SEC_CLAUDE:-60@301 ASW_NO_IDLE_FULL_READ:-1@470 APPROVAL_ALERT_COOLDOWN:-300@899 MAX_TYPING_SKIP:-5@1067 INOTIFY_TIMEOUT:-30@1535 ASW_PROCESS_TIMEOUT:-1@1599 |
| `scripts/lib/detect_stale.sh` | 1 | DETECT_STALE_STALE_SEC:-120@33 |
| `scripts/pane_enter_watcher_supervisor.sh` | 2 | STALE_SEC:-300@50 STALE_SEC:-300@52 |
| `scripts/redundancy/shogun_report_watcher.sh` | 1 | SHOGUN_REPORT_WATCHER_COOLDOWN:-60@29 |
| `scripts/stop_hook_inbox.sh` | 1 | MASS_UNREAD_THRESHOLD:-5@146 |
| `scripts/watchdogs/enter_restart_commander_watchdog.sh` | 1 | ER_THRESHOLD_MIN:-2@35 |

## 二 ㋑ 6/7/8 の差を一本ずつ名指す

器 = `ki/32_sa.py`(二つの枡を argv で受け、file 差と口 差を名で出す)。

### 差① 6 ⇔ 7 ―― ★凍結点⇔disk★(判定ではない)

落ちた(disk に無く凍結点に在る)file は ★一本★ ――

```
scripts/redundancy/shogun_report_watcher.sh	口 1	SHOGUN_REPORT_WATCHER_COOLDOWN:-60
```

`scripts/redundancy/shogun_report_watcher.sh` は凍結点 6ba8fcb で `SHOGUN_REPORT_WATCHER_COOLDOWN:-60`@29 を一口持つ。disk では此の生形が無い (e768e71 09:12:47「閾を★比較器そのもので★検め…」で甲乙の番人へ書き替はつた)。
∴ ★之は数へ方の差に非ず、版の差である。★ 同じ條で歩いても、凍結点を見る席は 7、disk を見る席は 6 と出る。

同じ對に在る他の増減(file は動かさぬ) ――

```
scripts/inbox_watcher.sh	左 13 ⇔ 右 12	左のみ名[APPROVAL_ALERT_COOLDOWN:-300] 右のみ名[]
scripts/stop_hook_inbox.sh	左 2 ⇔ 右 1	左のみ名[STOP_HOOK_STDIN_TIMEOUT:-10] 右のみ名[]
file: 左 6 ― 左のみ 0 + 右のみ 1 = 右 7
口  : 左 23 ― 左のみ 0 + 右のみ 1 + 共通の増減 -2 = 22 (右の實測 22 ―― 一致=真)
```

★此の對の刻は 10:24:18 であり、左(disk)は 23口 と出て居る。★ 上の内訳表(10:28:20)の disk は 22口 である ―― 差は下 「差④」。

### 差② 7 ⇔ 8 ―― ★閾らしき名の判定★(逐語)

入つた(當席の枡にのみ在る)file は ★一本★ = `scripts/checks/karo_mac_gate4.sh`。其の口の逐語 ――

```
入つた file : scripts/checks/karo_mac_gate4.sh	口 1	VAR:-50
scripts/checks/karo_mac_gate4.sh:71  VAR:-50   ★註行★
  員外の理由(定義丁の枡) : VAR:-50@71(註行)
```

判定は一点のみである ―― 名 `VAR` は `^[A-Z][A-Z0-9_]*$` を満たし、既定 50 は ≥1 を満たす。∴ ★之を落とすのは「註行か否か」の一條だけ★ である。註行を込める枡では此の file が立ち、file は 7 → 8 に成る。

### 差③ 口 23 ⇔ 22 ―― ★單位(出現 ⇔ 行)★

```
scripts/pane_enter_watcher_supervisor.sh	左 4 ⇔ 右 2	左のみ名[POLL_SEC:-10] 右のみ名[]
file: 左 7 ― 左のみ 0 + 右のみ 1 = 右 8
口  : 左 23 ― 左のみ 0 + 右のみ 1 + 共通の増減 -2 = 22 (右の實測 22 ―― 一致=真)
```

`scripts/pane_enter_watcher_supervisor.sh` は 50 行と 52 行に `STALE_SEC:-300` と `POLL_SEC:-10` を ★一行に二口★ 持つ。出現單位なら 4、行單位なら 2 ―― ∴ 23 − 2 + 1(差②) = ★22★、7 + 1 = ★8★。

### 掃き ―― 22口8file が立つ枡は 112 の内 幾つか

器 = `ki/33_sou.py`。源 14 × 單位 2 × 既定閾 2 × 註 2 = ★112 枡★ を悉く歩いた(刻 2026-09-17T10:25:20+0900・rc 悉く 0)。★口= 22 ∧ file= 8★ が立つ枡 ――

```
6dbe09e	line	1	komu	口= 22	file= 8	rc= 0
638807f	line	1	komu	口= 22	file= 8	rc= 0
```

★112 枡の内 2 枡★ のみ ―― 何れも ★行單位 ∧ 既定≥1 ∧ 註行込★ である。∴ 當席の 8 は「或る一つの枡で確かに立つ數」であり、其の枡の名は上の四欄で書ける。

### 差④ ★disk は我が走の中で動いた★(本弾で新たに出た根)

器 = `ki/34_ugoki.py`。同じ根・同じ條で、disk と凍結点の口を名で並べた(刻 2026-09-17T10:28:57+0900) ――

```
★動いた名★ APPROVAL_ALERT_COOLDOWN:-300 : disk 1 ⇔ 6ba8fcb2402c0487ccfe4b60d910050807ac5007 0 (+1)
★動いた名★ ASW_PROCESS_TIMEOUT:-1 : disk 1 ⇔ 6ba8fcb2402c0487ccfe4b60d910050807ac5007 2 (-1)
★動いた名★ STOP_HOOK_STDIN_TIMEOUT:-10 : disk 1 ⇔ 6ba8fcb2402c0487ccfe4b60d910050807ac5007 0 (+1)
★動いた名★ SHOGUN_REPORT_WATCHER_COOLDOWN:-60 : disk 0 ⇔ 6ba8fcb2402c0487ccfe4b60d910050807ac5007 1 (-1)
```

`ASW_PROCESS_TIMEOUT:-1` が disk で 1・凍結点で 2 である ―― `scripts/inbox_watcher.sh` の生形一つが `fix_flag` 呼びへ書き替はつた。其の file の mtime は ★10:25:19★ = ★本走の最中★ である。
∴ 實測 : disk は 10:24:18 に 23口、10:25:20 以後は 22口。
★∴ 三席が「disk」を別々の分で測れば、條が一字も違はずとも數は合はぬ。★ 母數を述べる時は ★源(disk か版か)と刻★ を必ず添へねばならぬ。

## 三 ㋒ 弾⑴の陰陽対照(据ゑず・束の中・寫しで測る)

器 = `ki/40_inyou.py`(argv `--mato <對象> --atai <値> --dest <寫し>`)／兄弟口 = `ki/41_inyou_kyoudai.py`。★hook 本体は一字も触れて居らぬ★(對象は讀むのみ・判定は束の中の寫しで行ふ)。

### 札の「:70」は今 何處に在るか ―― 版を先に名指す

| 版 | sha16 | bytes / 行 | 判定行(字面・-F) | 旧形glob の行 | 陽性対照 |
|---|---|---|---|---|---|
| km-81_before控(札が :70 と指す版) | 42c83a9ab41c0166 | 14418 / 268 | 70 | 54,185,190 | 13口 |
| disk現物(★未commit★) | f1b49820e234a1ee | 16434 / 288 | 53,90 | 52,205,210 | 15口 |
| 凍結点 6ba8fcb | 0fb2e72891d65297 | 10865 / 221 | ★零(rc=1)★ | ★零(rc=1)★ | 9口 |

★列の単位★ bytes = `wc -c < <file>` / 行 = `grep -c ''` / 判定行・旧形glob = `grep -n ★-F★` の行番(註行を含む) / 陽性対照 = 同じ器で `stop_hook` を数へた口。

scripts/stop_hook_inbox.sh | 69 +++++++++++++++++++++++++++++++++++++++++++++-
1 file changed, 68 insertions(+), 1 deletion(-)
∴ ★弾⑴の直し(判定行 新形)は disk に在るのみで、臺帳(commit 6ba8fcb)には未だ入つて居らぬ。★
∴ ★札が指す :70 は disk の行番に非ず ―― disk では 90 行、km-81_before控で 70 行である。★

∴ ★札の `:70` は disk には無い。★ 之を「無い」で済ませば陰陽が建たぬ故、★旧形は km-81 の `_before` 控を對象に取り、新形は disk を對象に取つた★ ―― 二形を並べる。
判定行は ★字面で探し、註行と `if…then` で絞つた★(行番号を決め打ちせぬ・疵②)。

### 四枡(陽性 = 20桁の十進 / 陰性 = 正しい十進)

| 枡 | 對象 | 入れた値 | bash -n | 閾比較の素 rc | 出目 |
|---|---|---|---|---|---|
| 旧形・陽 | km-81 _before(判定行 70) | `99999999999999999999` | 0 | 2 | ★時限切れを見ぬ(else へ落ちた ―― 危険側)★ |
| 旧形・陰 | km-81 _before(判定行 70) | `10` | 0 | 0 | ★時限切れを見る(then へ入つた)★ |
| 新形・陽 | disk 現物(判定行 90) | `99999999999999999999` | 0 | 0 | ★時限切れを見る(then へ入つた)★ |
| 新形・陰 | disk 現物(判定行 90) | `10` | 0 | 0 | ★時限切れを見る(then へ入つた)★ |

★陽性(旧形)の意味★ ―― 20桁の十進は `case … *[!0-9]*` の glob を ★通る★(悉く数字ゆゑ)。通つた値は `[ x -ge y ]` で 2^63 を超え、比較器が ★rc=2★(真でも偽でもない)を返す。`if` も `elif` も起たず、制御は ★黙つて else へ落ちる★ ―― ∴ ★時限切れを見ぬ(危険側へ倒れる)★。`2>/dev/null` は stderr を隠すが rc は隠さぬ。

比較器自身の言(旧形・陽性の枡の stderr 逐語) ―― ★之が rc=2 の正体である★

```
line 18: [: 99999999999999999999: integer expression expected
```

### ★兄弟口★ ―― 直しは 一 file 二口の内 ★一口★ のみに当たつて居る

同じ `scripts/stop_hook_inbox.sh` の disk 現物に、旧形の glob が ★もう一口★ 残つて居る。
★「護り無し」ではない ―― 旧形の glob で護られて居る。破れるのは其の形である。★

```
58:num_same_op() { [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }
65:if ! num_same_op "$STOP_HOOK_STDIN_TIMEOUT"; then
90:    if [ "$__read_rc" -gt 128 ] || [ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]; then

204:case "$MASS_UNREAD_THRESHOLD" in
205:    ''|*[!0-9]*)
206:        echo "[stop_hook] ★MASS_UNREAD_THRESHOLD が數でない(「${MASS_UNREAD_THRESHOLD}」) — 既定 5 へ倒す(fail-closed)★" >&2
207:        MASS_UNREAD_THRESHOLD=5 ;;
208:esac
209:case "${UNREAD_COUNT:-0}" in
210:    ''|*[!0-9]*)
211:        echo "[stop_hook] ★UNREAD_COUNT が數でない(「${UNREAD_COUNT:-}」) — 0 へ倒す(fail-closed)★" >&2
212:        UNREAD_COUNT=0 ;;
213:esac
214:if [ "${UNREAD_COUNT:-0}" -gt "$MASS_UNREAD_THRESHOLD" ]; then
215:    FLAG="${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}"
216:    touch "$FLAG"
217:    echo "[stop_hook] $AGENT_ID has ${UNREAD_COUNT} unread (> ${MASS_UNREAD_THRESHOLD}) — refusing to block (loop防止). bulk ack 推奨。" >&2
218:    exit 0
```

甲は `num_same_op`(=`[ x -ge 0 ]` の rc を見る)で閾を検め、20桁なら既定 10 へ倒す。乙は `case` の glob `*[!0-9]*` で検める ―― ★20桁の十進は悉く數字ゆゑ glob に当たらず、既定へ倒れぬ儘 `-gt` へ渡る★。∴ rc=2 ⇒ `else` ⇒ `:218 exit 0`(loop 防止)を ★見ぬ★。

★最も重いのは、當席が其の理を同じ file の註に既に書いて居る事である。★

```
52:# ★甲(裁 seq322952)★ 閾は ★後で比べる時と同じ演算子★ で検めよ ―― 旧形の glob `*[!0-9]*` は
53:#   20桁の十進を「數」として通すが、下の `[ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]` は
54:#   2^63 超で rc=2 を返し ★黙つて else(時限切れを見ぬ側)へ落つる★。
55:#   加へて `read -t <20桁>` は bash に ★拒まれ(invalid timeout specification)★ ―― 實測(當席 2026-09-17):
56:#   rc=1・★讀めた字数 0★ ∴ hook 入力 JSON を ★丸ごと落として先へ進む★。而して上の rc=2 ゆゑ ★其の事を報せぬ★。
```

- 甲 num_same_op を通す閾= 1 口
- 乙 旧形 glob case を通す閾= 2 口(註行を除く)
- ∴ ★同じ file・同じ危險の二口に、★別々の護り★が当たつて居る。★

∴ ★直しは「當たつた口」で閉ぢ、「同じ理が当たる隣の口」で閉ぢて居らぬ。★ memory「Added forms do not remove the consumer’s assumption」の同型 ―― 理を書く事は、其の理を全ての口へ及ばせる事ではない。

```
# 對象= scripts/stop_hook_inbox.sh / sha16= f1b49820e234a1ee / 行= 288 / 閾名= MASS_UNREAD_THRESHOLD / 左項= UNREAD_COUNT
# 番人域(逐語)= 197〜213 行(17 行) / 判定行= 214 行
#   214 行: 註行=偽 / if…then=真 / 採=★之★ : if [ "${UNREAD_COUNT:-0}" -gt "$MASS_UNREAD_THRESHOLD" ]; then
# 判定行(逐語): if [ "${UNREAD_COUNT:-0}" -gt "$MASS_UNREAD_THRESHOLD" ]; then
```

| 枡 | 閾名 | 左項 | 入れた値 | 閾比較の素 rc | 出目 |
|---|---|---|---|---|---|
| 兄弟・陽 | MASS_UNREAD_THRESHOLD | UNREAD_COUNT | MASS_UNREAD_THRESHOLD=[99999999999999999999] UNREAD_COUNT=[7] | 2 | ★閾を越えたと見ぬ(else へ落ちた)★ |
| 兄弟・陰 | MASS_UNREAD_THRESHOLD | UNREAD_COUNT | MASS_UNREAD_THRESHOLD=[5] UNREAD_COUNT=[7] | 0 | ★閾を越えたと見る(then へ入つた)★ |

★之が本節の最重である。★ 弾⑴の直しは 64/65/90 行(新形)に当たつたが、★同じ file の 197〜214 行は旧形の儘★ である。rc=2 で else へ落ちる先は `:218 exit 0` の手前 ―― ∴ ★大量未讀の時に走を止める護りが、閾に 20桁を入れられると効かぬ。★
(本紙は直しを ★提さぬ★。scripts/ は讀むのみ・變更は委員長の許可を要る故、事實のみ記す。)

### 再測の形(當席が当てた後に同じ器で引ける)

```sh
cd /Users/momizimac/multi-agent-shogun
B=docs/evidence/km-53-hitotsu-no-aruki-ne-de-file-suu-wo-soroe-20260917
# 陽性(どの版でも・argv で對象を取る)
/usr/bin/python3 -B "$B/ki/40_inyou.py" --mato <對象sh> --atai 99999999999999999999 \
    --keika 99 --dest "$B/utsushi/<名>.sh"
# 陰性
/usr/bin/python3 -B "$B/ki/40_inyou.py" --mato <對象sh> --atai 10 --keika 99 \
    --dest "$B/utsushi/<名>.sh"
# 兄弟口(閾名・左項も argv)
/usr/bin/python3 -B "$B/ki/41_inyou_kyoudai.py" --mato <對象sh> \
    --na MASS_UNREAD_THRESHOLD --sahen UNREAD_COUNT --sahenatai 7 \
    --atai 99999999999999999999 --dest "$B/utsushi/<名>.sh"
```

## 四 ㋓ `scripts/karo_overload_monitor.sh` ―― ★別行として立てる★

器 = `ki/50_bangai.py`(argv で對象を取り、二條を別々に当てる)。

```
# sha256/16= 3196a91236e9b8ef / bytes= 20862 / 行= 523
[甲] 條(全)の口= 0 / 其の内 條(閾)を満たす口= 0
  ★甲の口が一つも無い ―― 此の file は定義丁の母數に ★一行も★ 入らぬ(閾を直に代入して居る故)★
```

### 之が内訳表に ★一行も★ 出ぬ理由(字面で名指す)

定義丁の條(全) = `\$\{[A-Za-z_][A-Za-z0-9_]*:-[0-9]+\}` ―― ★`:-`(展開時のみ既定)を要る★。
本 file は閾を ★`:=`(展開時に代入)★ で宣して居る ――

```
: "${KARO_UNREAD_THRESHOLD:=10}"        # 71 行
: "${KARO_LATENCY_THRESHOLD_SEC:=300}"  # 72 行
: "${DISPATCH_LATENCY_THRESHOLD_SEC:=300}" # 73 行
: "${PARALLEL_CMD_NEW_THRESHOLD:=5}"    # 74 行
: "${UNSTARTED_SUBPHASE_THRESHOLD:=3}"  # 75 行
: "${COOLDOWN_SEC:=300}"                # 78 行
: "${ALERT_CAP_PER_HOUR:=5}"            # 79 行
```

∴ ★甲=0 は「閾が無い」の意ではない。「條の字面に当たらぬ」の意である。★ 裁の三口(⑴⑵⑶)にも定義丁の母數にも入らぬ ―― 故に落ちる。★7本の閾は悉く env から上書き可であり、之は定義丁が数へる `:-` と危さに於て同格である。★

### 乙(素の比較 ∧ 同行に `2>/dev/null`)―― 地と項を分けて数へる

```
  180	左=$ts -ge 右=$cutoff	if [ "$ts" -ge "$cutoff" ] 2>/dev/null; then
  438	左=$m1 -ge 右=$KARO_UNREAD_THRESHOLD	[ "$m1" -ge "$KARO_UNREAD_THRESHOLD" ] 2>/dev/null && hits_csv="${hits_csv:+$hits_csv,}M1"
  439	左=$m2 -ge 右=$KARO_LATENCY_THRESHOLD_SEC	[ "$m2" -ge "$KARO_LATENCY_THRESHOLD_SEC" ] 2>/dev/null && hits_csv="${hits_csv:+$hits_csv,}M2"
  440	左=$m3 -ge 右=$DISPATCH_LATENCY_THRESHOLD_SEC	[ "$m3" -ge "$DISPATCH_LATENCY_THRESHOLD_SEC" ] 2>/dev/null && hits_csv="${hits_csv:+$hits_csv,}M3"
  441	左=$m4 -ge 右=$PARALLEL_CMD_NEW_THRESHOLD	[ "$m4" -ge "$PARALLEL_CMD_NEW_THRESHOLD" ] 2>/dev/null && hits_csv="${hits_csv:+$hits_csv,}M4"
  442	左=$m5 -ge 右=$UNSTARTED_SUBPHASE_THRESHOLD	[ "$m5" -ge "$UNSTARTED_SUBPHASE_THRESHOLD" ] 2>/dev/null && hits_csv="${hits_csv:+$hits_csv,}M5"
  452	左=$ts -ge 右=$cutoff_1h	if [ "$ts" -ge "$cutoff_1h" ] 2>/dev/null; then
  472	左=$since_last -lt 右=$COOLDOWN_SEC	if [ "$since_last" -lt "$COOLDOWN_SEC" ] 2>/dev/null; then
  481	左=$CURRENT_ALERT_COUNT_1H -ge 右=$ALERT_CAP_PER_HOUR	if [ "$CURRENT_ALERT_COUNT_1H" -ge "$ALERT_CAP_PER_HOUR" ] 2>/dev/null; then
```

★第52弾の「12/12 悉く素」は ★項★ の數である。★ 本器は同じ file を ★地(行)= 9★ と出した ―― 之は矛盾ではなく單位の差である。項で数へ直し、各項の ★生れ(値が何處から来るか)★ を對象の中で實測した ――

```
[乙・項] 項の數= 18 (地 9 × 左右2) ―― ★「12」は此の單位の數である★
  180	左 $ts	外から入る=★真★	生れ= 状態/一覧を辿る(for)@178,450
  180	右 $cutoff	外から入る=偽	生れ= 算($((…)))@174
  438	左 $m1	外から入る=★真★	生れ= env既定(:=・展開時に代入)@424 / 他器の出目(read で受く)@423 / 直書き@331,375 / 引數で受く(local N="$k")@331,375
  438	右 $KARO_UNREAD_THRESHOLD	外から入る=★真★	生れ= env既定(:=・展開時に代入)@71
  439	左 $m2	外から入る=★真★	生れ= 他器の出目(read で受く)@423 / 直書き@332,376 / 引數で受く(local N="$k")@332,376
  439	右 $KARO_LATENCY_THRESHOLD_SEC	外から入る=★真★	生れ= env既定(:=・展開時に代入)@72
  440	左 $m3	外から入る=★真★	生れ= 他器の出目(read で受く)@423 / 直書き@333,377 / 引數で受く(local N="$k")@333,377
  440	右 $DISPATCH_LATENCY_THRESHOLD_SEC	外から入る=★真★	生れ= env既定(:=・展開時に代入)@73
  441	左 $m4	外から入る=★真★	生れ= 他器の出目(read で受く)@423 / 直書き@334,378 / 引數で受く(local N="$k")@334,378
  441	右 $PARALLEL_CMD_NEW_THRESHOLD	外から入る=★真★	生れ= env既定(:=・展開時に代入)@74
  442	左 $m5	外から入る=★真★	生れ= env既定(:=・展開時に代入)@427 / 外器の出目($(…))@426 / 直書き@335,379 / 引數で受く(local N="$k")@335,379
  442	右 $UNSTARTED_SUBPHASE_THRESHOLD	外から入る=★真★	生れ= env既定(:=・展開時に代入)@75
  452	左 $ts	外から入る=★真★	生れ= 状態/一覧を辿る(for)@178,450
  452	右 $cutoff_1h	外から入る=偽	生れ= 算($((…)))@445
  472	左 $since_last	外から入る=偽	生れ= 算($((…)))@471
  472	右 $COOLDOWN_SEC	外から入る=★真★	生れ= env既定(:=・展開時に代入)@78
  481	左 $CURRENT_ALERT_COUNT_1H	外から入る=偽	生れ= 算($((…)))@453 / 直書き@446,521
  481	右 $ALERT_CAP_PER_HOUR	外から入る=★真★	生れ= env既定(:=・展開時に代入)@79
[乙・項] ★外から値が入り得る項= 14 / 18★
[乙・項] ★外から値が入り得る項= 0 / 0★
```

| 單位 | 數 | 何を数へたか |
|---|---|---|
| 甲(定義丁 條(全)) | ★0★ | `${N:-既定}` の口 ―― 本 file は `:=` 故 当たらぬ |
| 乙・地(行) | ★9★ | 素の比較 ∧ 同行に `2>/dev/null` が在る行 |
| 乙・項 | ★18★ | 其の 9 行の左右 |
| 乙・項の内 外から値が入り得る物 | ★14★ | env 既定 7 + 他器の出目 5 + 状態 file を辿る `ts` 2 |
| 第52弾の數 | ★12★ | 名附の閾 7 + 左項 m1〜m5 の 5 |

★12 と 14 の差は `ts`(180 行・452 行)★ である ―― `for ts in $STATE_ALERT_HISTORY`(450 行)で ★状態 file の値★ を辿る故、之も外から入る。∴ 第52弾の 12 は ★過少★ であり、其の向きは危い側ではなく安全側の誤りである。

★rc=2 が此処で起きると何が起きるか★ ―― 438〜442 行は `[ … ] 2>/dev/null && hits_csv=…` の形である。rc=2 なら `&&` の右が起きぬ ―― ∴ ★過負荷を検めても `hits_csv` に積まれず、警めが鳴らぬ。★ 472/481 行が倒れれば cooldown と 1h 上限の護りが外れる。

## 五 ★疵★ ―― 己の器が刷つた偽の出目 三件(悉く直して再測した)

### 疵① 歩き根が cwd 相対で、★黙つて零★ を返した

`git ls-files -- scripts .claude` の path 指定は ★cwd 相対★ である。束の中(docs/evidence/…)から呼んだ最初の走は一つも当たらず、★rc=0 の儘 口 0 / file 0★ を刷つた ―― 「測れぬ」ではなく「零」に見えた。
直し = ⑴`git rev-parse --show-toplevel` で頭を引き chdir し、頂を冠に書く ⑵歩いた file が 0 なら `sys.exit(3)` で倒す。陽性対照 = `--ne "nai_ne_desu"` で rc=3 と「測れぬ」が出る事を確かめた。

### 疵② ★註行★ を判定行の座に置き、syntax error の儘 出目を刷つた

寫しを組む器が `-ge "$STOP_HOOK_STDIN_TIMEOUT"` の字面だけで判定行を探し、★其の比較を説明して居る註行★ を先に拾つた。結果、寫しは `if` の座に `#` の行を置き ―― `line 35: syntax error near unexpected token else` を出しながら ★[out] ★時限切れを見る★★ を刷つた。★rc=2 で倒れた寫しの出目であり、偽である。★
直し = ⑴判定行の條を三つにする(字面を含む ∧ 註行に非ず ∧ `if`/`elif` で起き `; then` で閉づ)⑵候補を悉く旗附きで刷る ⑶`bash -n` を通し rc≠0 なら判定を刷らず倒す ⑷走つた後 rc≠0 なら「上の出目を用ゐるな」と書く。六枡を再測し `bash -n rc= 0`。

### 疵③ 先読みの括りを誤り、生れの札を一つ落とした

項の生れを分ける器で `\$\(?!\(` と書いた ―― 之は「`$` + 任意の `(` + 字面 `!`」であり先読みに成つて居らぬ。∴ `m5=$(count_unstarted_subphases)` の「外器の出目」札が落ちた。(判定 14/18 は此の疵に依らず立つて居た ―― 落ちたのは札のみ。)直した上で刷り直した。加へて ★`str.replace` の當たり數を assert で検める★ 事を再び踏んだ ――一度目の直しは assert が 0 を出して止まり、★止まつた事に気付かず次の命が走つた★。

### 疵④ `grep` の條の中の `$` を ★行末の錨★ と解され、★三版悉く「無し」★ と出た

版を測る器で `grep -n -- '-ge "$STOP_HOOK_STDIN_TIMEOUT"'` と書いた ―― 此の shell の `grep` は ★ugrep 7.8.4★ であり、條の中の `$` は行末の錨と解される。∴ 字面に成らず ★rc=0・0行★ で返り、「其の版には無い」と讀める形の零が出た。`-F` を付けて當たつた。直し = ⑴`-F` を必ず付ける ⑵零へ ★同じ器・同じ path の陽性対照★ を添へる(本紙の版の表は `stop_hook` の口を併記して居る ―― 故に 6ba8fcb の零は「讀めぬ」ではなく「無い」と言へる)。

### 疵⑤ `$(cat f)` が ★末尾改行を落とし★、sha16 と bytes が現物と合はなんだ

胴を `$(…)` で受けて測つた故、disk の bytes が 16434 ではなく 16433、sha16 が `f1b49820e234a1ee` ではなく `7b3430dd5a6f8d91` と出た。★命の代入は末尾改行を剥ぐ★。版の同一性は ★file を直に器へ食はせて★ 測る。(前弾の記録 `f1b49820e234a1ee` と食ひ違つた事で気付いた ―― ★己の前の數と合はぬ時、先に疑ふべきは器である。★)

### 疵⑥ 生の三本が ★`>` で直に取られ 0byte の儘★ 束に残つて居た

`nama/20_kotei.err` / `nama/bin/b0_okuri.err` / `nama/bin/b0_okuri.out` の三本は 器の出目を `>` で直に受けた故、★整へ器(`ki/10_kaki.py`)を通らず 0byte で残つた★。0byte は出す前 門 の條④が鳴る形であり、且つ 裁 seq310228⑶ に依れば ★空の結果は 0byte の file ではなく「空であつた」と述べる一行である★。∴ 臺帳を建てる前に三本を空流れとして kaki へ通し、一行の宣へ改めた。★「空であつた」事は消して居らぬ ―― 0byte から一行へ、述べ方を改めたのみである。★

## 六.五 門 v7 の七欄に応へる ―― 提出前の二問

★問一 何を走らせたか★ ―― `ki/` の十二器を悉く此の走で走らせ、出目を `nama/` に置いた。數表は `ki/60_kami.py` が `nama/` から ★切り嵌め★ で取る ―― ★轉記(手で打ち写す事)は一切して居らぬ★。∴ 紙の數と生の數は同じ字である(食ひ違へば生が勝つ)。

★問二 何を走らせて居らぬか★ ―― ⑴`scripts/` への變更は一指も加へて居らぬ(讀取のみ)。⑵hook 本体は走らせて居らぬ ―― 陰陽は `utsushi/` の寫し六本で測つた。⑶押し(push)は為して居らぬ。

★欄4 轉記★ = 無し(器が切り嵌める)。★欄5 勝ち筋★ = ★食ひ違ふ時は現物(生の出目)が勝つ★ ―― 紙の文は器の出目に従属する。原票が勝つ。

### 門の所見 ―― `karo_mac_gate7.sh` は ★呼ばれぬ門★ である

本走で三門を通した際、`scripts/checks/karo_mac_gate7.sh` は ★出目零・rc=0★ で返つた。「通」と讀みかけたが、器の素を数へた ――

```
行= 21 / 定義 `gate7(){` = 1 口 / ★呼出(行頭または ; の後の裸の gate7) = 0 口(rc=1)★
陽性対照(同じ器 grep -c -F): 字面 `gate7` = 2 口 ∴ ★file は讀めて居る。呼出が無いのである。★
```

∴ 此の file は ★門ではなく器の函★ であり、`source` して `gate7 <紙>` と呼ばねば一路も塞がぬ。★script として走らせれば、必ず rc=0・出目零 ―― 即ち「悉く通」と見える fail-open である。★memory「呼ばれぬ門は一路も塞がぬ」の再現。

正しく `source` して本紙へ当てた出目は 便 に併記する(紙は己の出目を先に書けぬ ―― 書けば其の一行が次の測りを変へる)。

## 六 此の數が ★意味せぬ★ 事

- ★「22口」は「閾が 22 本」ではない。★ 定義丁の條に字面で当たる口の數である。`:=` で宣された閾(㋓ の 7 本)は入らぬ。
- ★「6file」は「危い file が 6 本」ではない。★ 條に当たる口を一つ以上持つ file の數である。
- ★「甲=0」は「fail-open が無い」ではない。★ 同じ file に乙が 9 地 18 項 在る。
- ★本紙の數は悉く「源と刻」に縛られる。★ disk は本走の中で動いた(差④)。源・刻を落とした母數は、条件が同じでも合はぬ。
- 本紙は臺帳(`_manifest.txt`)の總數を述べぬ ―― 紙は己を含む臺帳の數を書けぬ故。
