# 閾の番人 横展開 ―― 甲/乙 を共有器四本へ当てる(裁 seq323062⑷)

- 発=総監督(seq323062)「20箇所6fileは共有器=repo source が正。貴席が枝で甲乙を当てよ(重い順 inbox_watcher→watchdog→health→warn)・各1形負テスト・稼働中watcherは触らず次respawnで反映・4PC配布は監督lot」
- 前弾=`docs/evidence/km-gate4-kou-otsu-20260917/`(門 gate4 に同じ甲乙を当てた紙・commit a6587c02)
- 枝=`karo-mac/km-shikii-yokotenkai-20260917`

## 一 ―― 何を直したか

| | 甲 | 乙 |
|---|---|---|
|條|閾は★比較に使ふのと同じ演算子★で検めよ|未設定/空文字/空白のみ を分け、既定へ倒す時は刷れ|
|旧|`is_num` = case の字面判定|`X="${ENV:-既定}"` = 未設定も空文字も黙つて既定|
|新|`num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }`|`env_state` が四状態を名指し、`fix_threshold` が一本の道で定める|

`is_num` は `99999999999999999999` を「數」と呼ぶ。然し後段の `[ x -ge 閾 ]` は其の値で
★rc=2★ に倒れ、`if` も `elif` も偽＝★黙つて既定の枝へ落ちる★。之が fail-open の実体である。

## 二 ―― 前後の sha(實測)

|器|前 sha16|後 sha16|前行|後行|`bash -n`|閾|
|---|---|---|---|---|---|---|
|`scripts/inbox_watcher.sh`|`e64662a6323c1086`|`6f6954b455cecf4e`|1627|1654|rc=0|10|
|`scripts/watchdogs/enter_restart_common_watchdog.sh`|`136f41957e4746d4`|`31956e6427ade32f`|390|417|rc=0|3|
|`scripts/agent_health_check.sh`|`bf2ec4b3336e9e7c`|`e5bd6ab3e28f1f9c`|450|476|rc=0|3|
|`scripts/checks/context_usage_warn.sh`|`6d1bc7b008b64d71`|`be4b1b210f815f0d`|60|88|rc=0|2|

★上表の「後 sha16」は ★作業樹★ の値である。commit した blob は inbox_watcher と warn で之と異なる ――
他席の未commit を載せなかつた故(`raw/08_commit_plan.txt` に commit 版の blob と sha16・行数・bash -n rc を悉く載せた)。
commit 版: inbox_watcher=`5ff53f30cd274956`(1607行) / watchdog=`31956e6427ade32f`(417行・作業樹と同一) /
health=`e5bd6ab3e28f1f9c`(476行・作業樹と同一) / warn=`82e15f7f6e77eccd`(88行)。

計 ★18箇所/4file★。残る2箇所は `scripts/redundancy/shogun_report_watcher.sh`(1) と
`~/bin/fleet_liveness_check.sh`(1)。後者は★repo 外★ゆゑ裁⑷の「共有器=repo source」の外に置き、
前者は本弾の負テストの★舊器の逐語出所★として未patch の儘残した(下記 四)。∴ 20 = 18 + 1(未着手) + 1(repo外)。

## 三 ―― 負テスト(`raw/05_negative_matrix.txt` ―― 四器 × 六形 × 二器 = 48走)

|形|舊器 鳴|舊器の値|新器 鳴|新器の値|判|
|---|---|---|---|---|---|
|甲 20桁 `99999999999999999999`|**0**|**20桁の儘**|1|既定|★fail-open を四器悉くで再現し、四器悉くで塞いだ★|
|乙 空文字 `""`|**0**|既定|1|既定|倒れる先は同じ。★黙るか言ふか★が差|
|乙 空白のみ `"   "`|1|既定|1|既定|差無し(is_num も空白は非數と見る)|
|乙 未設定|0|既定|0|既定|★乙′(下記)により新器も黙る★|
|陽性 `7`|0|7|0|7|正しい閾は素通り＝閾の意味は不変|
|陽性 `-5`|1|既定|1|既定|差無し|

### 段の鎖への波及(`raw/06_consequence_watcher.txt`)

齢0秒の席に対し `[ 0 -lt 99999999999999999999 ]` は ★rc=2★(實測)。∴ `if` も `elif` も偽 →
★Phase3 の枝★へ落ちる。陽性対照: 齢300秒→Phase3(正)・齢180秒→Phase2(正)・新器(閾120/240)で齢0秒→黙(正)。
★何が飛ぶかは版で違ふ★ ―― HEAD 版の Phase3 は `/clear`、当作業樹は未commit の seq232016 手当で
Escape+nudge。軽いが、齢0秒で段を上げ timer を潰す事自体が疵である。

## 四 ―― 己の疵と、断つた事

1. **舊器を打ち直さなかつた**。負テストの `is_num` は `scripts/redundancy/shogun_report_watcher.sh` L31
   (器 sha16 `8746f02c321d96f6`)から `sed -n 31p` で抜いた逐語である。前弾で
   ★旧器を名指す時は「どの旧器か」を sha で定めよ★ を犯した故。
2. **★乙′ ―― 高頻度器では「未設定」を黙る★(家老mac の申告・裁を請ふ)**。
   乙の字面は「既定へ倒す時は必ず刷る」。然し本四器は起動毎/prompt 毎に走る。
   `context_usage_warn.sh` は UserPromptSubmit hook ゆゑ、一便毎に全席の stderr へ
   「未設定＝既定」を 2 行刷る事になる＝★氾濫★(watcher の旧註も同旨を警めて居た)。
   ∴ ★異常の三形(空文字・空白のみ・比較器で扱へぬ)は必ず鳴らし、設計上の常態である「未設定」は黙り、
   代りに本紙と器の註へ明記する★ 形を採つた。門(gate4=低頻度器)では四形悉く刷る儘である。
   ★此の一点は裁の字面からの逸脱ゆゑ、委員長の裁を請ふ。★
3. **負値も倒す**。`num_same_op` は `-5` を「比較器で扱へる」と見る(rc=1)。然し本18閾は悉く
   秒/分/回数/byte ＝非負ゆゑ `[ "$v" -ge 0 ]` を併せた。之は「不正なら倒す」(裁322952)の内と見る。
4. **稼働中の watcher は触つて居らぬ**。`ps` 実測=3本(a1/a2/a3・稼働6日9時間)。器の file を
   書き換へても走る process は★旧 inode★を読む ∴ 反映は次 respawn。本弾で respawn は為さぬ(watcher の
   起こし直しは Mac事業部長の職・seq299502/299680)。
5. **他席の未commit を commit に載せぬ**。本四器の作業樹には★己の帯以外★の未commit の手当が3本在る
   (watcher: 承認 dialog 検知・mac 席名・Phase3 の /clear 停止 / warn: BSD `stat -f` 退避)。
   之は當席の物に非ず ∴ ★己の hunk だけを一時 index に載せて commit した★(`raw/08_commit_plan.txt`)。
   作業樹は其の儘＝他席の手当は未commit の儘残る。

## 五 ―― 戻し方

```
git checkout <此の commit>^ -- scripts/inbox_watcher.sh scripts/watchdogs/enter_restart_common_watchdog.sh \
  scripts/agent_health_check.sh scripts/checks/context_usage_warn.sh
```
(★但し作業樹には他席の未commit が乗つて居る ∴ 戻す前に `git diff` を見よ★)

## 六 ―― 紙の一覧(raw/)

|紙|中身|
|---|---|
|`00_sha_before.txt`|手入前の四器 sha16 と行数|
|`01_is_num_residue.txt`|`is_num` の残は註1行のみ(実行の出現=0)|
|`02_sha_after.txt`|手入後 sha16(註の修正前の値)|
|`03_old_instrument_identified.txt`|index/HEAD と手入前が★一致せぬ★事の實測|
|`04_diff_hunks.txt`|hunk 見出し ―― 己の帯と他席の帯の切り分け|
|`05_negative_matrix.txt`|負テスト 48走の本体|
|`06_consequence_watcher.txt`|段の鎖への波及と rc の實測|
|`07_phase3_today.txt`|今日の Phase3 が実際に何を為すか|
|`08_commit_plan.txt`|一時 index で己の hunk だけを載せた記録|
