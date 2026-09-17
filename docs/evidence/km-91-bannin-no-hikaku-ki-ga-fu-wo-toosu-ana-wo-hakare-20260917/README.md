# km-91 ―― ★番人の比較器が負を通す穴を測れ★ ／ 專任3(ashigaru-mac-3) 第56弾

- 札: `queue/tasks/ashigaru-mac-3.yaml` sha16=`9c0abe25a2a57cb9` 49行 4090B（家老mac の宣と★一致★）
- 的: `scripts/stop_hook_inbox.sh` 一本のみ（sha16=`f1b49820e234a1ee` 288行 16434B・git HEAD=`0039e132`）
- 裁: seq324588 順⑴「到達可能な fail-open（最重）」
- 殻: `/bin/bash` 3.2.57(1) arm64-apple-darwin25。★此の機に bash 5 は無い★（`command -v bash`=/bin/bash、`/opt/homebrew/bin/bash`・`/usr/local/bin/bash` 共に不在）→ 生器 L87-88 の註と一致。
- 刻: 2026-09-17 12:52〜13:1x JST
- 據ゑ先: 枝 `ashigaru-mac-3/km-91-bannin-no-hikaku-ki-ga-fu-wo-toosu-ana-wo-hakare-20260917`
  ／ commit ★`eb6cf51de16fd06b76eaf1cf36c47d535e2d5373`★（親=`main` 363d5fb・★push はせぬ★）

---

## 〇 一言

★比較器は「負が通る」だけではなかった。★`0` も通り、`0` の方が質が悪い★ ―― 負は
`invalid timeout specification` を stderr に一行吐くが、`0` は ★一行も吐かずに★ stdin を丸ごと捨てる。★
治（`num_in_range`）で 3 札の穴が悉く塞がり、陰性 8 札は一つも壊れなかった。
併せて ★治が塞がぬ残穴が一つ★ 在る（下 §5）――「時限が實際に切れた時」は治前も治後も番人が死ぬ。
之は比較器の疵ではなく `read -t` の設計の疵ゆゑ、本弾では★直さず・報せるに留めた★。

---

## 一 比較器の逐語と行番 ―― ★己で引いた★（受入⑴）

裁は「`:70`」と行番で指すが、★其の版は既に動いて居る★。當席が引いた現物:

```
58:num_same_op() { [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }
65:if ! num_same_op "$STOP_HOOK_STDIN_TIMEOUT"; then
```

裁の指す **L70 の現物**は `        *)`（`cat -v -e` で `        *)$`）＝ `case` の既定枝に過ぎぬ。
∴ ★行番で追ふな・逐語で引け★。家老mac の宣「行番で追ふな（裁の :70 は版が動いた）」と★一致★。

**家老mac 12:44 の實測との突合**（陰性/陽性/境 の出目）:

| 値 | 家老の宣 | 當席の實測 | 一致 |
|---|---|---|---|
| 10 | 通 | 通 | ✓ |
| 0 | 通 | 通 | ✓ |
| -5 | ★通★ | ★通★ | ✓ |
| abc | 止 | 止 | ✓ |
| 空 | 止 | 止 | ✓ |
| 99999999999999999999 | 止 | 止 | ✓ |
| 010 | 通 | 通 | ✓ |

★違ふ点は一つも無かつた。★ 逐語器＝`_after/03_comparator_probe.sh` ／ 出目＝`_after/03_comparator_probe.txt`。

**何故通るか**: `[ "$v" -ge 0 ]` は 真=rc0／偽=rc1／扱へぬ=rc2 を返す。
`[ $? -le 1 ]` は rc0 と rc1 を★共に通す★ ―― 即ち此の比較器は
「**値が 0 以上か**」ではなく「**`-ge` が扱へる値か**」しか問うて居らぬ。負は「扱へる」ゆゑ通る。

---

## 一.5 ★的の版は main に無い ―― 裁の指す穴は「git を main で讀む者には見えぬ」★

據ゑる前に測つた（`_after/31_target_version_in_git.txt`）。

| 版 | blob |
|---|---|
| `main` (363d5fb) | `229c0557…` ―― 該当箇所は今も逐語 `INPUT=$(cat)`（221行・10865B） |
| `HEAD` (0039e13) | `229c0557…`（main と同じ） |
| ★worktree（當席が測つた現物）★ | `8bcea329…`（288行・16434B） |

80 本の ref を悉く歩いた結果、worktree と同じ blob を持つ ref は ★一本★ ――
`refs/heads/karo-mac/km-81-hook-no-jigen-wo-onaji-enzanshi-de-kenme-20260917`。

∴ 穴在る版は **家老mac の自枝に commit 済・main へは未合流・共有 worktree には展開済**。
hook が實際に走らせるのは worktree の file ゆゑ ★穴は現に到達可能★（裁の「到達可能」と合ふ）。
**が、`main` だけを讀む者には一行も見えぬ。**

> ★當席の訂★: 最初に刷つた文は「何れの ref にも無い」と書いて居た。★偽である。★
> 歩く器を走らせる前に断じた。上の 80 本の歩きが出た後に書き直した（`_after/31` に訂の跡ごと残す）。

**據ゑ方への含意**: 親を `main` に取ると、commit の差分に家老mac の km-81 分（68行）が土臺として
含まれ、★當席の手が何處かが読み取れぬ★。札は `-p main` と指して居る故 ★從つた★ 上で、
commit 文に「當席の手は 38 行のみ（`_after/21_fix_diff.txt`）」と明記した。§四 に代案を併記する。

---

## 二 通つた後に何が起きたか（受入⑵⑶） ―― ★「通/止」で終らせぬ★

`_after/11_harness.sh` で ★写し★（生器 L1-93 逐語 ＋ 番人の口 L117-121 逐語 ＋ 計測印）を叩いた。
写しの L1-93 が生器と一字も違はぬ事は `_after/10_utsushi_diff_L1_93.txt`（0 行＝差無し）が証す。
stdin は ★真な hook JSON `{"stop_hook_active": true, ...}` 75字★ ―― 讀めれば番人は効き、讀めねば死ぬ。

| 札 | 時限(前) | rc | 讀めた字数 | 経過秒 | stop_hook_active | 番人 | stderr |
|---|---|---|---|---|---|---|---|
| 陰性 10 | 10 | 1 | 75 | 0 | True | 効く | （空） |
| 陰性 0 | 0 | 1 | **0** | 0 | False | ★効かぬ★ | `★stdin 時限切れ(0秒経過・rc=1) — 讀めた 0 字で続行★` |
| 陰性 既定(未設定) | 10 | 1 | 75 | 0 | True | 効く | （空） |
| 陽性 -5 | -5 | 1 | **0** | 0 | False | ★効かぬ★ | `read: -5: invalid timeout specification` ＋ `★stdin 時限切れ(-5秒経過・rc=1)★` |
| 陽性 -1 | -1 | 1 | **0** | 0 | False | ★効かぬ★ | 同上（-1） |
| 境 空文字 | 10 | 1 | 75 | 0 | True | 効く | `★空文字 — 既定 10 へ倒す★` |
| 境 空白のみ | 10 | 1 | 75 | 0 | True | 効く | `★比較器が扱へぬ(「 」)★` |
| 境 非数 abc | 10 | 1 | 75 | 0 | True | 効く | `★比較器が扱へぬ(「abc」)★` |
| 境 010 | 010 | 1 | 75 | 0 | True | 効く | （空） |
| 境 2^63超(20桁) | 10 | 1 | 75 | 0 | True | 効く | `★比較器が扱へぬ(「999…」)★` |
| 境 可視印␊既在 | 10 | 1 | 75 | 0 | True | 効く | `★可視印(␊␍␉)を既に含む★` |

（rc は全札 0、hook 自身の壁時計は全札 0.05〜0.07s。生の出目＝`_after/11_controls_before.txt`）

### ⑴ ★「負が通ると何が消えるか」を實測で示した★（受入⑶）

`-5` → `read -t -5` が `invalid timeout specification` で撥ね ★即 rc=1・讀めた字数 0★（待たぬ）
→ `INPUT=""` → L120 の `json.load` が倒れ `|| echo "False"` へ落ちる
→ `STOP_HOOK_ACTIVE=False` → L121 の `[ "$STOP_HOOK_ACTIVE" = "True" ]` が★永久に偽★
→ **「既に Stop hook から続いて居るなら今回は止まらせる」無限ループ防ぎが消える。**

★家老mac の見立ては正しかつた。★ 見立てのままに置かず、番人の口まで写しに継いで `bannin=★効かぬ★` を刷らせた。

### ⑵ ★家老の見立てより一つ多い ―― `0` も同じ穴（札の分類と違ふ）★

札は `0` を **陰性（守る筈）** に列べて居る。だが實測では `0` も番人を殺す。★札の分類と違ふ★ゆゑ明記する。

`read -t 0` は「今すぐ讀める物が在るか」を問ふだけで ★一字も讀まぬ★。
競合（data が未着）ではない事を `_after/12_read_t_probe.txt` の★regular file 供給★で証した ――
file なら data は必ず在るのに、それでも `讀めた字数=0`。遅れて来る供給（slowpipe）でも 0。

**しかも `0` は負より質が悪い**: 負は `invalid timeout specification` を stderr へ一行吐くが、
`0` は ★裸の read でも stderr が空★（`_after/12`）。hook 側の
`★stdin 時限切れ(0秒経過・rc=1)★` だけが出るが、之は★嘘★である
――「時限が切れた」のではなく「時限が 0 ゆゑ初めから讀まなかつた」。

### ⑶ ★斷じ得ぬ事／生器の註が偽である事★

- 生器 L56 は「而して上の rc=2 ゆゑ ★其の事を報せぬ★」と書くが、之は **20桁（rc=2）の話**。
  負・`0` の路では `★stdin 時限切れ★` が★一行出る★。∴「完全に黙る」は★偽★ ――
  黙るのではなく ★偽の理由を告げる★。番人が消えた事は孰れにせよ★一言も報せぬ★。
- 生器 L46 の「★時限切れでも bash は讀めた分を変数へ入れる★(man bash: saves any partial input)」は
  ★此の機の bash 3.2 では偽★（§5 で實測）。
- `010` が通るのは★疵に非ず★ ―― `[` も `read -t` も 010 を十進 10 と解し、讀めた字数 75。害は測れなかつた。

---

## 三 治（受入⑷） ―― 案と、★其れを選んだ根拠★

```bash
num_in_range() { [ "${1:-}" -ge 1 ] 2>/dev/null && [ "${1:-}" -le 86400 ] 2>/dev/null; }
```

**根拠**:

1. **問ひを変へた。** 舊は「`-ge` が扱へるか」（rc≦1）。新は「★下流の二口が共に食へる範囲か★」。
   下流の口は二つ ―― `read -t "$V"`（1 以上の整数のみ受ける）と
   `[ "$__stdin_el" -ge "$V" ]`（2^63 超で rc=2 を返し★黙つて else へ落つる★）。
   両方が食へる値だけを通せば、どちらの口でも黙つて倒れぬ。
2. **甲（裁 seq322952）＝★同じ演算子で検む★を守つた。** 下流と同じ `-ge` を使ふ。
   `-le` も同族ゆゑ、非数・2^63超は第一の `[` が rc=2 を返し `&&` が短絡して★止★。
   別種の器（`case` の glob や `expr`）を持ち込まぬ ―― 舊形 glob `*[!0-9]*` が 20桁を通した轍を踏まぬ。
3. **`[ $? -le 1 ]` を捨てた。** 之こそが rc=1（＝0 と負）を通して居た当の一句。
   `-ge 1` に閾を畳み込めば、真偽と範囲が★一つの演算子で★決まる。
4. **上限 86400（1日）の根拠。** `read -t` の實受容上限は此の bash 3.2 で ★4294967295（2^32-1）★
   ―― 4294967296 で `invalid timeout specification`（實測 `_after/13_upper_bound.txt`）。
   だが之は★版に依る★数ゆゑ其の儘は書かぬ。hook の既定は 10 秒であり、
   運用上 1 日を超える stdin 待ちは有り得ぬ。∴ ★版依存の崖より遙か手前★ で切る。
   之で `9223372036854775807`（`-ge 1` は通すが `read -t` は撥ねる帯）も塞がる。
5. **診断の文言も直した。** `比較器が扱へぬ` → `1〜86400 の整数に非ず`。
   新器では `-5`・`0` は「扱へぬ」のではなく「範囲外」ゆゑ、舊文言は★嘘に成る★。
   乙（裁 seq323980⑵）の可視印分岐は★一字も触れず温存★。

**当て方**: `_after/20_apply_fix.py` ―― ★行番で追はず逐語で探し、置換数が 1 で無ければ `exit 3`★
（無一致の `replace` は黙つて素通りし「直つた様に見える」ゆゑ）。
併せて舊名 `num_same_op` が★註以外に★一行も残らぬ事を検め、残れば `exit 4`。
出目＝`_after/20_apply_fix.out`（置換数 1×3・残り 0）。差分＝`_after/21_fix_diff.txt`（38行）。
`/bin/bash -n` rc=0。

### 治後 ―― ★同じ harness・同じ stdin・同じ 11 札★

| 札 | 時限(後) | 讀めた字数 | 番人 |
|---|---|---|---|
| 陰性 10 / 既定 / 010 | 10 / 10 / 010 | 75 | 効く（stderr 空） |
| **陰性 0** | **10** | **75** | **効く** ← 塞がつた |
| **陽性 -5 / -1** | **10** | **75** | **効く** ← 塞がつた |
| 境 空文字/空白/abc/20桁/可視印 | 10 | 75 | 効く |

- ★治前に番人が死んで居た札 = 3（0・-5・-1）／治後に死んで居る札 = 0★
- ★陰性の壊れ = 0（全 11 札で 75 字讀めた）★
- 生の出目＝`_after/23_controls_after.txt` ／ 一覧＝`_after/30_ryoutaisho_table.txt`

### 治が★余分に★塞いだ帯（裁も家老も名指して居らぬ）

`4294967296`（2^32）: 治前 `bannin=★効かぬ★` → 治後 `bannin=効く`。
`[ -ge 0 ]` は rc=0 で通すが `read -t` が撥ねる帯 ―― ★同じ穴の、名の無い上半分★。
（`86400`・`86401`・`4294967295` は治前後とも `効く`＝差無し。`_after/24_timeout_still_fires.txt`）

### 治が時限を殺して居らぬ事（陽性対照）

口を閉ぢぬ供給（FIFO・3秒居座る）に `timeout=1` を宛て、★hook 自身の壁時計★ を測つた:
治前 **1.09s** ／ 治後 **1.08s**。両者とも `★stdin 時限切れ(1秒経過)★` を吐く。
∴ 治は時限を no-op にして居らぬ。

> ★當席の器の疵（隠さず記す）★
> ⑴ 初版は `{ printf; sleep 30; } | hook` の形で ★pipeline 全体★ の寿命（30.04s）を測つて居た。
>   hook 自身は 1 秒で戻つて居た（`##KM91 elapsed=1` が其の証）。∴ FIFO で供給元と切り離した。
> ⑵ 裸 read の probe が `set -u` 下で `I` 未初期化 → `I: unbound variable` で死んだ。`I=""` を置いた。
> ⑶ 第二版は後片付けに強制終了の器を使ひ ★DD-169 guard に止められた★（★正しく止めた★）。
>   供給元が自ら退く形（`sleep 3`）に改め、其の器を一切使はぬ。
> ★三度とも、直す前の出目を消して居らぬ。★

---

## 四 据ゑ方（受入⑸） ―― 生器は一字も触れて居らぬ

- ★生の `scripts/stop_hook_inbox.sh` は読取のみ。★ 測りは悉く写し（`_after/10_utsushi.sh`・`_after/22_utsushi_fixed.sh`）。
- 治は ★温 recipe（`GIT_INDEX_FILE` を別に立て、`read-tree`→`update-index`→`write-tree`→`commit-tree`）★
  で自枝 `refs/heads/ashigaru-mac-3/km-91-...` へ据ゑた。worktree の生 file は書き換へて居らぬ。
- 據ゑた結果（`_after/40_commit_and_porcelain.txt`・器＝`_after/40_commit.sh`）:

| 項 | 値 |
|---|---|
| 枝 | `refs/heads/ashigaru-mac-3/km-91-bannin-no-hikaku-ki-ga-fu-wo-toosu-ana-wo-hakare-20260917` |
| commit | `eb6cf51de16fd06b76eaf1cf36c47d535e2d5373` |
| 親 | `363d5fb060845171338c067ef42bfcbef8ad9188`（＝`main`・札の指図通り） |
| tree | `737405059969773179e273d1b67b301106eb9b32` |
| 触る file | ★1 本のみ★ `scripts/stop_hook_inbox.sh`（★的以外 0 本★） |
| 據ゑた blob の sha256 | `9dd41120d80cc5cc` ＝ 写し `_after/20_fixed_full.sh` と★一致★ |
| porcelain 前 → 後 | **1017 → 1017（差 0）** |
| porcelain の★中身★の差 | **0 行**（本数だけでなく `diff` で逐語照合した） |
| worktree の生 file | blob `8bcea329…`・sha256 `f1b49820…` ―― ★測る前と同一★ |

> ★數が何を意味せぬか★（数の規律3）: porcelain が動かぬのは
> 「當席が何も書かなかつた」意ではない。束は `.gitignore`（`!README.md` の allowlist 形）に依り
> ★ディレクトリ 1 行 `?? docs/evidence/km-91-…/` に畳まれて居る★ ゆゑ、
> 束の中に何本足しても本数は動かぬ。**worktree を触つて居らぬ證は porcelain ではなく、
> 上の「生 file の blob と sha256 が測る前と同一」の行である。**
> `git status --porcelain` の stderr 1 行（`queue/reports/…/n13_noaccess_dir/: Permission denied`）は
> 前後とも同じで、★本数には入れて居らぬ★。

- ★push はせぬ。★ 枝名と commit sha を納め便に告げ、家老mac 経由で代行を請ふ。
- ★家老mac への伺ひ★: 親を `main` でなく `karo-mac/km-81-hook-no-jigen-wo-onaji-enzanshi-de-kenme-20260917`
  に取れば、差分は ★當席の 38 行だけ★ に成る（今は 106 行で、内 68 行は家老の km-81 分）。
  一手で替はる ―― `git commit-tree 7374050… -p karo-mac/km-81-… -F <同じ文>` → `git update-ref <同じ枝> <新sha>`。
  ★札が main と指して居る故、當席は勝手に替へぬ。★
- `.claude/settings.json` は★触れて居らぬ★（家老が 12:46 に別件で据ゑた ―― 重ねぬ）。
- 走る watcher・他席の pane・他人の箱は★触れて居らぬ★。

---

## 五 ★治が塞がぬ残穴（一つ）★ ―― 報せるに留め、直して居らぬ

**時限が實際に切れた時、番人は治前も治後も死ぬ。**

生器 L46 は斯う書く ―― 「★時限切れでも bash は讀めた分を変数へ入れる★(man bash: saves any partial input)」。
★此の機の bash 3.2 では偽である。★ 實測（`_after/25_partial_input_claim.txt`）:

| 形 | 出目 |
|---|---|
| 口を閉ぢぬ供給・`read -d "" -t 1` | rc=1 **len=0** |
| 口を閉ぢぬ供給・`read -t 1`（改行区切） | rc=1 **len=0** |
| ★陽性対照★ 口が閉ぢる（EOF）・`read -d "" -t 1` | rc=1 **len=26** |

陽性対照が 26 字讀めて居る ∴ ★器が壊れて居るのではない★。
此の機の `man bash` に `partial input` の語は★無い★（其の文言は bash 4.x 以降の man）。

**含意**: 時限は「永久に塞がる」を「★番人を黙つて失ふ★」に替へただけ、とも読める。
`read -t 1` が切れた瞬間 `INPUT=""` → `stop_hook_active` は常に False。

**何故本弾で直さぬか**: 之を直すには `read` の形そのもの（`-d ''` を捨てる／`-N` で刻む／
時限切れを検知したら `exit 0` で fail-closed にする 等）を変へる要が在り、
★hook の停止判断の意味が変はる★。札は「一本の file の比較器の fail-open」を的に指して居り、
之は★別の裁を要する設計変更★と見る。∴ ★測つて報せ、直さぬ★。
（實運用では Claude Code が JSON 送出後に stdin を閉ぢる故 EOF が来て時限を踏まぬ ――
 が、★踏まぬ事を當席は實運用で測つて居らぬ★ ∴ ★斷じ得ぬ★と書く。）

---

## 六 受入との突合

| # | 受入条件 | 充足 | 証 |
|---|---|---|---|
| ⑴ | 比較器の逐語と行番を己で引いた／家老と違へば違ふと書く | ✓ | `_after/01`（L58・L65）／突合表＝★7 札全一致★ |
| ⑵ | 陰性3・陽性2・境6 を悉く走らせ rc/stderr行/字数/経過秒 を表で | ✓ | §二 の表・`_after/11_controls_before.txt` |
| ⑶ | 「負が通ると何が消えるか」を實測で | ✓ | `bannin=★効かぬ★` を写しに刷らせた・§二⑴ |
| ⑷ | 治を写しへ当て 陽性が止まり陰性が通る | ✓ | 穴 3→0・陰性の壊れ 0・§三 |
| ⑸ | 自枝 commit（親=main）・束外0・porcelain 不動 | ✓ | `_after/40_commit_and_porcelain.txt`（commit=`eb6cf51d`・的以外 0 本・1017→1017・中身差 0 行）・§四 |
| ⑹ | 門 rc=0・臺帳の食ひ違ひ0・欠0 | ✓ | `_gate/`・`_post/10_rcs.txt`・納め便 |

**境は札が 6 種を挙げる（空文字・空白のみ・非数 abc・010・2^63超・可視印␊既在）** ―― 悉く走らせた。
加へて當席の判断で **上の境 4 種（86400・86401・4294967295・4294967296）** を足した（`_after/24`）。

---

## 七 束の中身

| path | 何 |
|---|---|
| `README.md` | 此の紙 |
| `MANIFEST.txt` | 臺帳（4欄 `path= sha256= bytes= lines=`・根は★束内相対★） |
| `_after/01_target_freeze.txt` | 的・札の固定、比較器の逐語と行番、裁の `:70` の現物 |
| `_after/02_shell_env.txt` | 走らせた殻（bash 3.2.57 一択である事） |
| `_after/03_comparator_probe.sh` / `.txt` | 比較器 単体 ―― 内側 `[ -ge 0 ]` の rc と出目 |
| `_after/10_utsushi.sh` | ★治前★ の写し（生器 L1-93 逐語＋番人＋計測印） |
| `_after/10_utsushi_diff_L1_93.txt` | 写しの L1-93 が生器と差無し（0 行） |
| `_after/11_harness.sh` / `11_controls_before.txt` | 11 札 両対照 harness と治前の出目 |
| `_after/12_read_t_probe.sh` / `.txt` | `read -t` 単体（pipe/file/slowpipe の三供給） |
| `_after/13_upper_bound.txt` | 上の境 ―― `[ -ge ]` と `read -t` の受容上限の食ひ違ひ |
| `_after/20_apply_fix.py` / `20_apply_fix.out` | 治を当てる器（逐語探索・置換数 assert） |
| `_after/20_fixed_full.sh` | 治した全文（299行）＝自枝へ据ゑた中身 |
| `_after/21_fix_diff.txt` | 生器との差分（38行） |
| `_after/22_utsushi_fixed.sh` | ★治後★ の写し（截り方は 10 と同一） |
| `_after/23_controls_after.txt` | 同じ 11 札の治後の出目 |
| `_after/24_timeout_still_fires.sh` / `.txt` | 時限が生きて居る事＋上の境の両器比較 |
| `_after/25_partial_input_claim.sh` / `.txt` | 生器 L46 の主張の検め（★偽★） |
| `_after/30_ryoutaisho_table.txt` | 両対照 一覧（機械が組んだ表） |
| `_after/31_target_version_in_git.txt` | 的の版が git の何處に在るか（80 ref の歩き・當席の訂込み） |
| `_after/40_commit.sh` / `40_commit_and_porcelain.txt` / `40_commit.err` | 温 recipe の器と出目・porcelain 前後照合 |
| `_post/` | 臺帳組み・門・porcelain 不動・納め便 |
| `_gate/` | 門控 |
