# 判定提出 ―― 裁337507⑶疵① 「`--type` 値無しの `$2` unbound」を usage で閉ぢ rc を分く

提出席: 家老mac（%68）／宛: 委員長（判定席）
雛形: JUDGE-SUBMISSION-BUNDLE-TEMPLATE v1.1（①〜⑦・欄はこれで全部）
親裁: seq337507 ⑶疵① ―― 逐語:
> 「⑶疵①`--type`値無しの`$2` unbound=別弾で直せ。usageで閉ぢ rc を分けよ(使ひ方の誤=1/器の死=2)。」

---

## ■① 対象 tuple（一組のみ）

```
ref名   = refs/heads/karo-mac/km-agent-status-kizu1-usage-rc-wakatsu-20260919
commit  = ★此の紙は己を含む tuple の 40桁を書けぬ★（紙が tree に入る故・自己参照）
tree    = ★同じ理由で書けぬ★
```

**∴ 40桁は ★便（pc_handshake）に書く★。判定席は下の検算で紙と tuple を結べる:**

```bash
cd /Users/momizimac/multi-agent-shogun
git rev-parse refs/heads/karo-mac/km-agent-status-kizu1-usage-rc-wakatsu-20260919
git rev-parse refs/heads/karo-mac/km-agent-status-kizu1-usage-rc-wakatsu-20260919^{tree}
# ★ref が「先端」であることの検算★ = 上の一つ目が便の commit40桁と一致（祖先を出して居らぬ）
git cat-file -p refs/heads/karo-mac/km-agent-status-kizu1-usage-rc-wakatsu-20260919 | sed -n '1,4p'
```

### ★逸脱の宣 ―― 親は origin/main でなく「前弾」である★

```
親 (-p) = cef84a32caa6a52e7e0b8597befb47f39406b3ca   ← 前弾（疵②・origin へ押し済）
origin/main = 6bde7170ce574090a6139ba2dfe3aa4cb6db8634
```

**「1弾1枝＝origin/main から切れ」（裁334442）からの逸脱であり、★認可を得て居る★。**
裁338111② 逐語:
> 「②★逸脱認可★親=前弾776ce71f 可（blob一致で差分1弾＝判定者の読む量が半分・可逆）。」

**本弾も同形である（前弾の blob と disk の前版が byte 一致 ∴ 差分は本弾一発分のみ）。実測:**

| 親に何を取るか | 本体 `scripts/agent_status.sh` の差分 |
|---|---|
| **`cef84a32`（本弾の親・逸脱）** | **112 挿入 / 20 削除 ＝ ★本弾一発分★** |
| `6bde7170`（origin/main） | 333 挿入 / 53 削除 ＝ 三弾分が混ざる |

検算:
```bash
git diff --numstat cef84a32caa6a52e7e0b8597befb47f39406b3ca -- scripts/agent_status.sh
git diff --numstat 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 -- scripts/agent_status.sh
git show cef84a32caa6a52e7e0b8597befb47f39406b3ca:scripts/agent_status.sh | shasum -a 256
#   → 55c9acd9a9f1215625d4e47afad03aed562fdeceed89b79ed415612500514e31（＝本弾の前版）
```

---

## ■② 成果物（artifact）

**本体（一本）**

| repo-relative path | sha256 | bytes | 行(grep -c '') |
|---|---|---|---|
| `scripts/agent_status.sh` | `8552c2c967088c35c889ce4d1574e3ab30c3014e6d7c9df481afc323c30f77fb` | 26917 | 559 |

前版（＝`cef84a32` の blob と一致）: `55c9acd9a9f1215625d4e47afad03aed562fdeceed89b79ed415612500514e31` / 21898 byte / 467 行
`bash -n scripts/agent_status.sh` → rc=0

**束（`docs/evidence/karo-mac_agent-status-kizu1-usage-rc-wakatsu-20260919/`・全 12 file）**

| path（束内相対） | sha256 | bytes | 行 |
|---|---|---|---|
| `kiki/km_patch_kizu1.py` | `e901d5f4b90b31106f1332dc418b858d0a482f6c6f1645cd772749e2a870a7b6` | 10778 | 210 |
| `kiki/km_ryoutaishou_kizu1.sh` | `25cda17b0fed88be845e8a7f03ad3f65ddadb69587dbcb78732186079886619e` | 4499 | 89 |
| `kiki/km_seiro_totsugou.sh` | `41a440fccb7d7027090995f65e6699dbc0c3b75f49d52df0486fafec6b8ca4ae` | 1481 | 31 |
| `raw/49_before_mukou.txt` ★無効★ | `fe0ce16c96822dbdb9c9cf2e4c05da73d5f98e770c640e09db62665cb1c50c8f` | 4450 | 128 |
| `raw/50_before.txt` | `b29d8edbfea93981d0d670701691b5f324ddf566b3773ecd0d02bce5c6b31230` | 4649 | 137 |
| `raw/51_tmux_fuzai_project.txt` | `39ae7651e22a78655917a6ae867cc9110dd8d043b80a4f2a053127e897205f66` | 2547 | 29 |
| `raw/60_after.txt` | `31dd4b0e13549962233be4fa434132fa7217ab1211df4700f28f22916166c1d5` | 5106 | 146 |
| `raw/61_tmux_fuzai_go.txt` | `0a616187684dcf1b67aa2deb240cbd2a357dcf49d1cc74a85237ad8195dd8ef3` | 933 | 15 |
| `raw/62_seiro_totsugou_mukou.txt` ★無効★ | `a7b3d7a31dec86625b72fb3e6c0a3824d5400a1b352135e28916490cc8b07ea9` | 3041 | 55 |
| `raw/63_seiro_byte_totsugou.txt` | `ff8222fc4fc1412f3f278af81c09ddf674a29923dd7d3d32ade71b9a40704115` | 1788 | 28 |
| `raw/64_nokoru_ana.txt` | `30428aac06f8ef00adff35ee623d12d95b902cc075f77721fd5bfcf1292ea346` | 1520 | 28 |
| `01_teishutsu.md`（此の紙） | ★己の sha256 は書けぬ（自己参照）★ | ― | ― |

此の紙の數は判定席が測れる:
```bash
cd docs/evidence/karo-mac_agent-status-kizu1-usage-rc-wakatsu-20260919
shasum -a 256 01_teishutsu.md; wc -c < 01_teishutsu.md; grep -c '' 01_teishutsu.md
```
席-local path は一つも欄に書いて居らぬ（控 `/tmp/agent_status.sh.bak-…-kizu1` は**戻し用の控であつて證の紙でない**・束に入れて居らぬ）。

---

## ■③ 実走の raw（①と同一 tuple・同一器）

**器**: `kiki/km_ryoutaishou_kizu1.sh`（18 路 ㋐〜㋠を一本で撃つ）
 cwd = `/Users/momizimac/multi-agent-shogun`
 前版の起し方 = `git show cef84a32…:scripts/agent_status.sh > scripts/.km_kizu1_zenban.sh`（★`SCRIPT_DIR=$(dirname)/..` ゆゑ scripts/ の下に置かねば根が狂ふ★）→ 測了後に削除

| # | argv（実際に打つた行） | rc | raw path | sha256 |
|---|---|---|---|---|
| 1 | `bash docs/evidence/…/kiki/km_ryoutaishou_kizu1.sh scripts/.km_kizu1_zenban.sh` | 127 | `raw/49_before_mukou.txt` | `fe0ce16c…`（上表） |
| 2 | 同上（器を `BASH_BIN="${BASH:-/bin/bash}"` へ直した後） | 0 | `raw/50_before.txt` | `b29d8edb…` |
| 3 | `bash docs/evidence/…/kiki/km_ryoutaishou_kizu1.sh scripts/agent_status.sh` | 0 | `raw/60_after.txt` | `31dd4b0e…` |
| 4 | `PATH=<tmux のみ抜いた shim dir> bash scripts/agent_status.sh --type project`（他） | 2 | `raw/61_tmux_fuzai_go.txt` | `0a616187…` |
| 5 | 前版を tmux 不在で走らせた生（project 路） | 0 | `raw/51_tmux_fuzai_project.txt` | `39ae7651…` |
| 6 | 突合を Bash tool の中へ直に書いた物 | ― | `raw/62_seiro_totsugou_mukou.txt` ★無効★ | `a7b3d7a3…` |
| 7 | `bash docs/evidence/…/kiki/km_seiro_totsugou.sh` | 0 | `raw/63_seiro_byte_totsugou.txt` | `ff8222fc…` |
| 8 | 閉ぢて居らぬ穴の実測 | 0 | `raw/64_nokoru_ana.txt` | `30428aac…` |

★無効を宣した生 二本★（冠に因を逐語で書いた・**消して居らぬ**）:
- `raw/49_before_mukou.txt` ―― 己の疵。末の ㋟ で PATH を空 dir に据ゑた儘 `bash` を**PATH 越しに**呼び rc=127「bash: command not found」＝**的でなく測り器自身が死んだ**。一走の生を割つて使はぬ故 全体を無効とした。
- `raw/62_seiro_totsugou_mukou.txt` ―― 己の疵（**二度目の再踏**）。突合を Bash tool の中へ直に書いた ―― **当機の Bash tool は zsh** ゆゑ `$a` が語分割されず一語に成り、両版とも「未知の旗」を刷つた。bash の file（`kiki/km_seiro_totsugou.sh`・位置引数）で測り直した。

---

## ■④ 依存の境界（repository-local）

```
lockfile = requirements.txt / sha256 = 46ab49a3e33f78c3f3313886a94834884a636df9589516bba066ae6122c46844 / 13 byte
外部 node_modules 参照 = ★無し★
外部 symlink 参照      = ★無し★
```
本体・束の器は **bash（`/bin/bash` 3.2）と python3（標準 lib のみ）** で走る。外から持つて来た物は無い。
検算:
```bash
shasum -a 256 requirements.txt
find docs/evidence/karo-mac_agent-status-kizu1-usage-rc-wakatsu-20260919 -type l | grep -c '' # → 0
grep -rn 'node_modules' docs/evidence/karo-mac_agent-status-kizu1-usage-rc-wakatsu-20260919 | grep -c '' # → 0
```

---

## ■⑤ 件数

### 正 = ★18/18★（期した出目が悉く出た）

| 出目 | 路 | 本数 |
|---|---|---|
| **使ひ方の誤 rc=1** | ㋓㋔㋕㋖㋗㋘㋙（新設の門 7）＋㋜㋝㋞（疵②由来の既設 3） | 10 |
| **器の死 rc=2** | ㋟（tmux 不在×standalone）＋㋠×2（tmux のみ抜いた shim PATH・二路） | 3 |
| **正 rc=0** | ㋐㋑㋒㋚㋛ | 5 |

### ★意味負★ = ★10/18★（＝門が実際に働いた證・恒真でない）

前後で**出目または出が変はつた**件を数へた（`raw/50_before.txt` ⇔ `raw/60_after.txt`）:

| 路 | 前 → 後 | 何が変はつたか |
|---|---|---|
| ㋖ `--type` 値無し | **rc=0 → 1** | ★親裁の疵①其のもの★。前は `$2` unbound で bash が死ぬ／黙つて通る形 |
| ㋗ `--lang` 値無し | **rc=0 → 1** | 同じ形 |
| ㋘ `--panes` 値無し | **rc=0 → 1** | 同じ形 |
| ㋟ tmux 不在×standalone | **rc=1 → 2** | ★偽の因★（使ひ方の誤に見えた）→ 器の死 |
| ㋠-1 shim PATH×project | **rc=1 → 2** | 同 |
| ㋠-2 shim PATH×standalone | **rc=0 → 2** | ★前は tmux 無しで rc=0 を返して居た★ |
| ㋓㋔㋕㋙ | rc=1 の儘 | **bash の内部診断 → usage 文へ／stdout → stderr へ**（因が読める形に成つた） |

**∴ 8 路は前後で不変（恒真の路）・10 路が動いた。**

### 退行無し ―― 正路 5/5 が ★byte 一致★

`raw/63_seiro_byte_totsugou.txt`: ㋐㋑㋒㋚㋛ の出を前後版で sha256 突合 → **5/5 一致**（不一致なら diff を刷る器）。

### 陽性対照 / 陰性対照

```
陽性対照 = ㋛ 「--type standalone（正しい値）」 → rc=0・表が出る
           ＝★門が正しい入力を撥ねて居らぬ★ことの證（門を足して全部 1 に成つたのではない）
陰性対照 = ㋜ 「--type nonsense（未知の値）」  → rc=1
           ＝疵②で既に据ゑた撥ね。本弾の新門を通らずに 1 へ落ちる（新門が既設を壊して居らぬ）
```

---

## ■⑥ 復元

```
復元後の sha256 = 8552c2c967088c35c889ce4d1574e3ab30c3014e6d7c9df481afc323c30f77fb
              （＝②の本体と同一。tuple から取り出して測れる）
再正 = 18/18（同じ器で撃てば同じ出目）
clean 確認 = ★未測（理由）★ ← 下記
```

復元の検算（判定席が自席で撃てる形）:
```bash
git show <便の commit40桁>:scripts/agent_status.sh | shasum -a 256
#   → 8552c2c967088c35c889ce4d1574e3ab30c3014e6d7c9df481afc323c30f77fb
```

### ★未測の理由 ―― `git status --porcelain -uall` が空に成らぬ（構造上）★

```
HEAD = a02391d8deca9b176644ea0a1f188a91dd09e38c
枝   = ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917  ← ★專任3 の枝★
```
⑴ **当 worktree は共用である**（HEAD は專任3 の枝に在り、家老が動かしてはならぬ）∴ 本弾の tuple は
 **plumbing（`GIT_INDEX_FILE` 別・`read-tree`/`hash-object`/`update-index`/`write-tree`/`commit-tree`/`update-ref`）で作り、
 共用の HEAD・index は前後で不変を検めた**（index sha256 = `5f070053c5213936fd4bd78ce5421259e795b0d9deb6c4a44d237d1a35ff99ae`）。
⑵ `.gitignore:7` が**裸の `*`**（allowlist 式）ゆゑ `-uall` は追跡外を一行も刷らぬ ―― **空に見えても證に成らぬ**。
∴ **「clean＝空」は本 worktree では★構造上満たせぬ★**。代へて ⑴ tuple の blob と disk の sha256 一致 ⑵ 差分 112/20 が本弾一発分 の二つを出した。

---

## ■⑦ 法令根拠

**該当せず**（算定・記載要件に触れぬ・器の出目の規律のみ）。

---

# 附一 ―― 据ゑた中身（7 箇所）

```
readonly KM_RC_OK=0      # 正
readonly KM_RC_USAGE=1   # ★使ひ方の誤★ ―― 呼び手が直せる
readonly KM_RC_KIKI=2    # ★器の死★     ―― 呼び手では直せぬ
```

| # | 何處 | 何を |
|---|---|---|
| ⑴ | `# ─── Parse args ───` の前 | 出目の規律の註＋三つの `readonly`＋`km_usage()`（fd 引数・`{ … } >&"$fd"`・"Exit codes:" 三行）＋`km_need_value()` |
| ⑵ | case の四腕 | 各旗で `km_need_value --X "$#" "${2-}" \|\| exit "$KM_RC_USAGE"` を**`$2` を触る前に**打つ。`--help\|-h` は `km_usage 1; exit "$KM_RC_OK"`（使ひ方を**求めた**のは誤でない ∴ 0・stdout）。`*` は `echo "Error: 未知の旗: $1" >&2; km_usage 2; exit "$KM_RC_USAGE"` |
| ⑶ | `source` の前 | ★器の死の門 二つ★ ―― `command -v tmux` 不在 → rc=2／共用 lib が `-r` でない → rc=2 |
| ⑷⑸⑹ | 疵②の三つの `exit 1` | `exit "$KM_RC_USAGE"   # ★使ひ方の誤★`（値は旧と同じ 1・**振舞は変へぬ**） |
| ⑺ | L196 の註 | 実装に追随（「tmux 無き所で走るのが並」を削り、「不在は入口で rc=2・此の `\|\| echo 0` が覆ふのは pane-base-index 未設定のみ」へ） |

`km_need_value` の三つの撥ね: ⒜ `argc -lt 2`（値が無い） ⒝ `-z "$nxt"`（値が空） ⒞ `--*`（値が旗に見える）。
**`$#` と `${2-}` で判ずる ―― `$2` を直に触れば `set -u` で shell が死に、usage を出す機を失ふ。**

# 附二 ―― ★己の疵 四件★（先に申す）

1. **`raw/49`**: PATH を空にした儘 `bash` を PATH 越しに呼び rc=127。器が死んだ生を「的の生」と呼びかけた。→ 無効を宣し `BASH_BIN="${BASH:-/bin/bash}"` へ直した（4 箇所・assert 付き）。
2. **㋟ の交絡**: PATH を空にすると `dirname` も消え `SCRIPT_DIR` が `//` に成る ∴ **「tmux 不在」を測れて居らぬ**。→ ㋠（`mktemp -d` に tmux 以外 23 本を symlink した shim PATH）を足した。**之が決め手と成り、前版の「tmux 不在×standalone=rc=0」を掴んだ**。
3. **`raw/51` の見出しで ★偽の通★ と書いたのは言ひ過ぎ**。刷つた表の中身は正直であつた（Pane=不在・Status=`---`・母數行が「解けた=0／寫像不能(session無)=6」を宣す）。**疵は中身でなく rc=0 である**。→ 生の冠を自訂の逐語で書き直した。
4. **`raw/62` の zsh 語分割（★二度目の再踏★）**: 突合を Bash tool の中へ直に書いた。→ 無効を宣し bash の file で測り直した。

# 附三 ―― ★本弾で閉ぢて居らぬ穴★（`raw/64_nokoru_ana.txt`・別弾候補）

| 穴 | 実測 | 何故本弾で閉ぢぬか |
|---|---|---|
| `--lang zz` | rc=0（未知の言語を黙つて受ける） | 親裁は**値の有無**を命じた。値の**中身**の検めは別の的 |
| `--panes 0,abc` | rc=0（悪い語を黙つて捨てる） | 同上 |
| `--panes abc` | rc=1 だが因は「該当無」 | **出目は正しいが因が違ふ**（使ひ方の誤として刷るべき） |
| `--lang ja --lang en` | 後の旗が勝つ（宣して居らぬ） | 振舞を変へると既存の呼び手に当たる ∴ 先に宣を書く弾が要る |

**∴ 本弾は「値の有無」と「器の死」の二つを閉ぢた。上の四つは★未着手であると明記して出す★。**

# 附四 ―― 触つて居らぬ物

- **`lib/agent_status.sh` は★触つて居らぬ★**。`agent_is_busy_check()` の `return 2` は**死んで居る**（`display-message` が不在でも rc=0 で現用 pane へ黙つて倒れる故）→ ★偽の待機中★。**稼働中の watcher が source する**ゆゑ本弾では触らず、消費者側 7 本を fail-closed にする別弾として出す。
- 他席の living tree・共用 worktree の HEAD/index には触れて居らぬ（⑥に検算を置いた）。
