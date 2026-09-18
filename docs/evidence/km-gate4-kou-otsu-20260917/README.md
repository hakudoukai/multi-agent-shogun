# 門(gate4)へ ★甲・乙★ を当てる ―― 裁 seq322952 の横展開 第一手

- 日付: 2026-09-17
- 席: 家老mac
- 器: `scripts/checks/karo_mac_gate4.sh`
- 親: 委員長裁 **seq322952**(甲=同じ演算子で閾を先に検めよ／乙=未設定・空文字・空白のみを分け、既定へ倒す時は必ず刷れ)
- 先例: `docs/evidence/km-gate-kou-otsu-kiten-20260917/`(出す前門・同日)。本件は其処の 横展開1行「次弾で gate4 から当てる」の履行。

## 一 前後の sha

| | sha256(頭16) | 行 |
|---|---|---:|
| commit 済の版(HEAD 0db0857e…) | `0db0857e32d95b3d` | 88 |
| ★編集の直前★(未commitの is_num 4行 入り) | `9a58a8b993511c9a` | 92 |
| 編集の後 | `95b027ea5e4f0fc5` | 122 |

`bash -n` rc=0。`is_num` は註の中に3度残るのみで、★走る行は0★(`grep -n is_num | grep -vc ':#'` = 0)。

**註 ―― 編集前の版は commit されて居なかつた**。`is_num` の番人4行(專任3 第40弾の産)が未commitの儘置かれて居た故、
本編集は「HEAD からの1段」ではなく「未commitの版からの1段」である。其の4行の差は `raw/08_prior_uncommitted_diff.txt`。
失はれた直前版は、今の file から塊を旧5行へ戻して建て直し、sha 一致で同一を証した(`raw/09_reconstruct.txt`)。

## 二 何を足したか(三つ・悉く可逆)

1. **甲** `num_same_op()` ―― `[ "$v" -ge 0 ]` を空打ちし rc<=1 の時のみ「使へる閾」とする。
   `is_num`(case glob)は `99999999999999999999` を「數」と讀むが、後段の `[ -ge ]` は **rc=2 で倒れ else へ落ちて通す**。
   二つの器が別の答を出し、★食ひ違ひが門を開けて居た★。∴ `is_num` は捨てた。
2. **乙** `env_state()` ―― 未設定 / 空文字 / 空白のみ / 値 を分けて名指す。
   旧形 `${VAR:-50}` は **未設定と空文字を一つに混ぜ、黙つて既定へ倒して居た**(倒れた事が紙に残らぬ＝no-silent-failure の破り)。
   註: 「空白のみ」は ASCII の空白類のみ。全角空白は value 側へ落ち、比較器が拒む。
3. **一本の道** `fix_threshold <変数名> <既定> <受け皿>` ―― 閾を定める路を一つにし、**既定へ倒す時は必ず刷る**。
   呼出は2箇所: `GATE4_MAX_FILE_MB`(既定50) / `GATE4_MAX_TOTAL_MB`(既定100)。

## 三 負テスト ―― 生 `big.bin` = 54525952 byte = 52 MB / 既定 MAXF=50 ∴ ★鳴るのが正★

`raw/02_matrix_three_tools.txt`(三器を同じ生へ通した)。條① は試樹に遠枝が無く常に落ちる故、**條⑤の行で判じた**(rc を條で割る)。

| 閾 | HEAD(番人無し) | 直前(is_num 有) | ★新器★ |
|---|---|---|---|
| `99999999999999999999` | ★通(偽の合格)★ | ★通(偽の合格)★ ← 甲の実害 | **鳴る**＋「比較器で扱へぬ…既定50へ倒す」 |
| 空文字 `""` | 鳴る(但し★黙つて★倒れた) | 鳴る(★黙つて★) | **鳴る**＋「空文字…倒す」 |
| 空白のみ `" "` | ★通(偽の合格)★ | 鳴る＋「數でない」 | **鳴る**＋「空白のみ…倒す」 |
| 未設定 | 鳴る(★黙つて★) | 鳴る(★黙つて★) | **鳴る**＋「未設定…既定を用ゐる」 |

陽性対照(`raw/06_kou_pos.txt`) ―― ★正しい閾は今も効く★:
`MAXF=60` → 52<60 ゆゑ鳴らず「條⑤ 寸法 = 単 file 上限 60 MB 以下」／`MAXF=1` → 鳴る／`GATE4_MAX_TOTAL_MB=10` → 総和でも鳴る。

実樹での一走(`raw/07_live_run.txt`): 閾2本とも「未設定 ―― 既定を用ゐる」と刷り、staged 0 file を捕へて rc=1(★之を『通』と読むな★の條が効いた)。

**己の疵**: `raw/02_kou_neg.txt` は最初の走りで、**HEAD 版だけを「旧器」と呼んで居た**。直前版(is_num 有)と取り違へた儘では
「甲＝is_num と比較器の食ひ違ひ」を証せぬ。∴ 建て直して三器で測り直した。紙は両方残す。

## 四 横展開 ―― ★数へ直した(前便 seq322982 の「7箇所4file」は過少である)★

`grep -rn 'is_num "' scripts/ ~/bin` で数へ直した。**env 由来の閾を is_num だけで検める箇所 = 20 / 6 file**。

| file | 箇所 | 席の物か | 実害の見立 |
|---|---:|---|---|
| `scripts/inbox_watcher.sh` L132-134 | **10**(一つの輪で10の閾) | ★他席・共有★ | 閾が 2^63 以上なら段の判定が総崩れ(註に「else=Phase3 へ落ちる」と自ら書いて在る) |
| `scripts/agent_health_check.sh` | 3 | 共有 | 警めの欠落 |
| `scripts/watchdogs/enter_restart_common_watchdog.sh` | 3 | 共有 | 再起動の閾が効かぬ |
| `scripts/checks/context_usage_warn.sh` | 2 | 共有(hook) | `exit 0` 強制ゆゑ★番人が黙るに留まる★ |
| `scripts/redundancy/shogun_report_watcher.sh` | 1 | 共有 | 冷却の閾 |
| `~/bin/fleet_liveness_check.sh` | 1 | repo外 | 幅の閾 |

**当てられるのは此処まで** ―― 上の6本は悉く★自席の器ではない★(裁320322 が許すのは家老mac の門と hook)。
∴ 変更統制に従ひ、**当職は手を入れず、裁を請ふ**。重い順は inbox_watcher(10) → watchdog(3) → health_check(3)。

なほ `karo_mac_dasumae_gate.sh` に残る `is_num` 4箇所は★閾ではない★(測つた寸法 `sz`・`ws_n` 等の検め)。
其処は既に「測れぬは通さぬ(default-deny)」ゆゑ甲の穴に当らぬ。★同じ語で違ふ物を数へるな★。

## 五 戻し方(一手)

```
git checkout HEAD~1 -- scripts/checks/karo_mac_gate4.sh
```
(之で「未commitの is_num 版」ではなく HEAD 版へ戻る。is_num 4行を含む直前版へ戻したい時は `raw/08_prior_uncommitted_diff.txt` を当てよ)
