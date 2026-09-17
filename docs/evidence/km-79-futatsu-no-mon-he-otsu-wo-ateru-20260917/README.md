# km-79 ―― 二つの門へ ★乙(行注入の封じ)★ を当てた

- 家老mac(係長格・Mac レーン)／2026-09-17／裁 **seq324481**「★次の『二つの門へ乙』は自枝で進めよ★」
- 上流の裁: **seq323980⑵**(行注入の印=乙 ␊ を採る・印が既在なら拒否=fail-closed)／**seq322952**(甲=同じ演算子で先に検め、乙=未設定/空/空白を分けて刷る)
- 臺帳の基点 = **束内相対**(裁 seq322699)。臺帳は束の中へ降りて建てた。

## 一、箇所 ―― 何處に穴が在つたか

| 器 | 現形 sha256(16) | 行 | 直し形 sha256(16) | 行 | 疵の在處(現形) |
|---|---|---:|---|---:|---|
| `scripts/checks/karo_mac_dasumae_gate.sh` | `e11f0d0142549086` | 310 | `2b8449bccd608a1a` | 321 | L58-59(判定の道へ生値)・L39(註が偽) |
| `scripts/checks/karo_mac_gate4.sh` | `95b027ea5e4f0fc5` | 122 | `59cf051d3595fd97` | 133 | L91-92(同)・L72(同) |

両器とも **甲(`num_same_op`)は既に在つた**。欠けて居たのは **乙の後半=行注入の封じ** である。
∴ 「閾 20箇所 6file を 1/1 で閉ぢた」と當席が報じた時、**閉ぢて居たのは甲であつて乙ではない**。

### 一之補 ―― 本 commit が運ぶ物は「乙」だけではない(★遮断の乙=未commit★)

`git show main:…` と控を並べると:

- `karo_mac_dasumae_gate.sh`: main ⇔ 控 = **差 0 行**(甲/乙前半は既に main に在る)。
- `karo_mac_gate4.sh`: main ⇔ 控 = **差 36 行** ―― main は未だ `MAXF="${GATE4_MAX_FILE_MB:-50}"; MAXT=…` の一行形で、
  **甲(`num_same_op`)と乙前半(`env_state`/`fix_threshold`)は worktree にのみ在つて commit されて居らなんだ**(當席の前弾の仕事)。

∴ 本 commit の `gate4` の差は **47行増/4行減** となり、**其の内 36 行は前弾の取り残し**、
11 行が本弾の乙(行注入の封じ)＋註の直しである。**「据ゑた」と「commit した」は別事であつた**と明記する。

## 二、現形(逐語・控 `_before/*.snapshot` より)

```bash
50:  local name="$1" dflt="$2" out="$3" st raw          # ← vp が無い
58:  if num_same_op "$raw"; then eval "$out=\$raw"; return 0; fi
59:  say "★閾 ${name} が比較器で扱へぬ(「${raw}」) ―― 既定 ${dflt} へ倒す(fail-closed)★"
39:#   註: 「空白のみ」は ASCII の空白類のみを見る(全角空白は value 側へ落ち、比較器が拒む)。
```

L59 は **env 由来の生値を己の判定の道(stderr)へ流す**。値が改行を含めば
**己の報せに見える偽の行が一本立つ**。`say(){ printf '%s\n' "$*" >&2; }`(甲 L22／乙 L17)。

## 三、直し形(逐語・両器で ★本体 逐語一致=差0行★ `raw/52_niki_doukei.txt`)

```bash
  if num_same_op "$raw"; then eval "$out=\$raw"; return 0; fi
  case "$raw" in
    *␊*|*␍*|*␉*) say "★閾 ${name} が可視印(␊␍␉)を既に含む ―― 値を刷らず既定 ${dflt} へ倒す(fail-closed・裁 seq323980⑵)★"; eval "$out=\$dflt"; return 0 ;;
  esac
  vp="${raw//$'\n'/␊}"; vp="${vp//$'\r'/␍}"; vp="${vp//$'\t'/␉}"
  say "★閾 ${name} を比較器が扱へぬ(「${vp}」) ―― 既定 ${dflt} へ倒す(fail-closed)★"
  eval "$out=\$dflt"
```

形は **兄弟器 `scripts/redundancy/shogun_report_watcher.sh` L63-69 から引いた**(印も同じ ␊␍␉)。
`local` へ `vp` を足した(甲 L52／乙 L85)。`bash -n` 両器 rc=0。

## 四、負テスト形 ―― 8形 × 2器(台は ★機械で切り出した★)

台 = `raw/10_slice.py` が `num_same_op(){` の行から **最初の `fix_threshold <NAME>` 呼出の直前** までを切る。
∴ **呼出行は台に乗らぬ**=他器の閾名が紛れ込まぬ。走らせ手 = `raw/12_run8.sh`(閾名 `KM79_PROBE`・既定 50)。

| 形 | 値 | 現形 rc/出値/報せ行/偽行 | 直し形 rc/出値/報せ行/偽行 |
|---|---|---|---|
| ①未設定 | (unset) | 0 / 50 / 1 / 0 | 0 / 50 / 1 / 0 |
| ②空文字 | `""` | 0 / 50 / 1 / 0 | 0 / 50 / 1 / 0 |
| ③空白のみ | `"   "` | 0 / 50 / 1 / 0 | 0 / 50 / 1 / 0 |
| ④全角空白 | `"　"` | 0 / 50 / 1 / 0 | 0 / 50 / 1 / 0 |
| ⑤正の數 | `77` | 0 / **77** / 0 / 0 | 0 / **77** / 0 / 0 |
| ⑥20桁(2^63超) | `999…9` | 0 / 50 / 1 / 0 | 0 / 50 / 1 / 0 |
| ⑦改行注入 | `50␊★閾 KM79_INJECTED…★` | 0 / 50 / **2** / **1** | 0 / 50 / **1** / **0** |
| ⑧印を既に含む | `5␊0` | 0 / 50 / 1 / 0(**値を刷る**) | 0 / 50 / 1 / 0(**刷らず倒す**) |

**締め** ―― 現形: 偽行 **1形/8形**(⑦)・⑧は印の曖昧を放置。直し形: 偽行 **0形/8形**・⑧は刷らずに倒す。
rc は **16/16 悉く 0**(形が変つても器は死なぬ)。両器の出目は **byte 一致**(`cmp` 通・`raw/52_niki_doukei.txt`)。

## 五、實器を通した ―― 直しが門の判定を動かして居らぬ事

| 走 | 現形控 | 直し形 |
|---|---|---|
| 甲 `--selftest` | ― | rc=**0** |
| 甲 素(紙1本) | rc=**0** | rc=**0** |
| 乙 素(紙1本) | rc=**1** | rc=**1** |
| 甲 閾へ改行注入 → **行頭に立つた注入** | **1本** | **0本** |
| 乙 閾へ改行注入 → **行頭に立つた注入** | **1本** | **0本** |
| stderr 総行(注入走) | 甲7 / 乙9 | 甲6 / 乙8 |

**乙の rc=1 は本直しの産物ではない**。因は 條①(遠に枝 `origin/ashigaru-mac-3/km-51-…` が無い)と staged=0 であり、
**現形控も同じ引数で rc=1** である(`raw/51_zengo_narabe.txt`)。

## 六、當席の疵 二つ ―― 己の檢出子が己を騙した

1. **「偽行=『★閾』で起らぬ行」と数へた** ⇒ 注入語を「★閾…」に擬した故 **偽行=0 と出た**(最初の走)。
   ∴ 偽行は **字面でなく期待行数の差**(倒す形=1行・通る形=0行)で数へ直した。
2. **「注入語が在るか」で測つた** ⇒ 語は値の一部ゆゑ **直し形でも一行の中に現れ 1 と出る**。
   ∴ 測るべきは **語が行頭に立つたか**(`grep -c '^★閾 KM79_INJECTED'`)。之で 1 → **0** が見えた。

## 七、器の註が偽であつた ―― 併せて直した

現形 L39(甲)／L72(乙) は「全角空白は value 側へ落ち、比較器が拒む」と書いて在つた。**偽である。**
實測: `printf '　' | tr -d '[:space:]'` → **空**(BSD tr は U+3000 を空白と讀む) ∴ ④は **blank 側**へ落ちる。
出目も「空白のみ」と刷る(`raw/20_genkei_matrix_dasumae.txt` の④)。∴ 註を實測の文言へ改めた。**數は変らぬが、讀む者を誤らせる。**

## 八、併せて上げる ―― 「1/1 閉」は ★裁の定義の下でのみ★ 真である

當席が 09:26 に測り直した(定義丁 = `${NAME:-N}` の閾名):

- **22口 / 8file**。番人(`fix_threshold`)無き file = `scripts/pane_enter_watcher_supervisor.sh`(STALE_SEC:-300・POLL_SEC:-10)／
  `scripts/stop_hook_inbox.sh`(STOP_HOOK_STDIN_TIMEOUT:-10)／`scripts/lib/detect_stale.sh`(DETECT_STALE_STALE_SEC:-120)／
  `scripts/watchdogs/enter_restart_commander_watchdog.sh`(ER_THRESHOLD_MIN:-2)。
- **閉ぢた file の中にも守られぬ名が在る** ―― `scripts/inbox_watcher.sh` の `ASW_PROCESS_TIMEOUT`(L224/L1599 で受けるが L173-175 の番人表に無い)。
- 但し **「番人無し」は「穴が開く」ではない**。比較器に入る口のみ fail-open に成り得る:
  `scripts/stop_hook_inbox.sh:70` の `[ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]` は **成る**(20桁 ⇒ rc=2 ⇒ 時限切れを見ぬ)／
  `inbox_watcher.sh:1599` は **字面比較**ゆゑ疵ではない／残る四口は **測れて居らぬ**(專任2 第56弾 km-78 に負テストを命じた)。

∴ **「閾 20箇所 6file 1/1 閉」は 裁の母數の定義(甲=呼出行)の下でのみ真**であり、
定義丁の下では **22口/8file・番人無し4file・未守1口・到達可能な fail-open 1口**が残る。之を當席の疵として上げる。

註: `raw/50_jikki_toshi.txt` は乙の出す ★空行★ を捕つた故、行末に前置の空白が一行残つた。
門の條②に触れる故 **末尾空白を落した(1行)**。落したのは行末の空白のみで、行数(27)も出目も変へて居らぬ。

## 九、門を当てる道で踏んだ疵 二つ(己の手の記録)

1. **★zsh は裸の `$var` を語分割せぬ★**(既知の法を再び踏んだ)。`F="a b c"; gate MANIFEST.txt $F` は
   **一引数**として渡り、門は「★file が無い★」+「條⑤ 測れぬ(default-deny)」で rc=1 に倒れた。
   ∴ 配列 `F=(…)` を作り `"${F[@]}"` で 18 本を渡した。**門の落ちは束の疵ではなく渡し方の疵であつた。**
2. **控の門は `_before/` から走らせられぬ**。門は照合器 `karo_mac_manifest_verify.py` を
   **己の在處(SCRIPT_DIR)の隣**に探す故、控を `_before/` へ置いて走らせると
   `can't open file '…/_before/karo_mac_manifest_verify.py'` で 條① が落ちる。
   ∴ 「現形控の門と直し形の門の出目が逐語一致」とは **言へぬ**(比べる土台が無い)。
   現形/直し形の比べは **§五の實器通し**(同じ引数・同じ rc)で示した。

## 十、紙の中身(束の構成)

- `README.md`(本紙) ／ `MANIFEST.txt`(束内相対・4欄 lines= 有) ／ `_gate/`(門の控)
- `_before/karo_mac_dasumae_gate.sh.snapshot`(310行) `_before/karo_mac_gate4.sh.snapshot`(122行)
- `raw/00_sha_genkei.txt`(2) `raw/10_slice.py`(20) `raw/11_genkei_dai_dasumae_gate.sh`(47) `raw/11_genkei_dai_gate4.sh`(34)
  `raw/12_run8.sh`(27) `raw/20_genkei_matrix_dasumae.txt`(16) `raw/21_genkei_matrix_gate4.txt`(16) `raw/25_sha_naoshikei.txt`(2)
  `raw/30_naoshikei_dai_dasumae_gate.sh`(58) `raw/30_naoshikei_dai_gate4.sh`(45)
  `raw/40_naoshikei_matrix_dasumae.txt`(15) `raw/41_naoshikei_matrix_gate4.txt`(15)
  `raw/50_jikki_toshi.txt`(27) `raw/51_zengo_narabe.txt`(7) `raw/52_niki_doukei.txt`(7)

**可逆**: 両器の `fix_threshold` から `case "$raw" in *␊*…esac` と `vp=` の二節を除き `${vp}`→`${raw}` へ戻せば現形。
控は `_before/` に在る。**當席は本件で他席の器へ一字も書いて居らぬ**(触れたのは自席の門二本のみ・裁 seq320321⑴「門とhookは自席の器」)。
