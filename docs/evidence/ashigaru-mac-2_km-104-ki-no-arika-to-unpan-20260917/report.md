★門 rc=0 / 母數 33 / 條① 一致 33・相違 0・実体無 0・読めぬ行 0★(控 `_gate/` の★最も新しい `92_gate_*`★・`KM_GATE_MANIFEST_BASE=.`・臺帳=束内相対)

# km-104 ―― 器の在り処と運搬

專任2(ashigaru-mac-2) 第45弾。的 = ★「門と臺帳の器が、版の上に在るか」一件のみ★。
札 = `queue/tasks/ashigaru-mac-2.yaml` task_id=`km-104-ki-no-arika-to-unpan-20260917`(家老mac・L5)。
束の名は裁 ⑷ に従ひ ★席名の全部★(`ashigaru-mac-2_`)で始めた。

## 一 結論(先に書く)

1. ★紙を焼くのに現に名が出る艦隊の器は 14 本。其の内 origin/main に在るのは 6 本、欠は 8 本。★
2. 幹 `68b6e07b` が運ぶのは ★2 本だけ★(`karo_mac_dasumae_gate.sh` / `karo_mac_gate4.sh`)。
   ∴ ★幹が着地しても尚 欠ける器 = 6 本★ ―― 其れが次の小PR の中身である。
3. 其の 6 本は ★二色★である。
   - ★repo の中に在るのに版に無い器 = 1 本 `scripts/checks/karo_mac_manifest_append.py`★。
     ★path を抱へる ref = 0/90。disk の版の blob は object としても存在せぬ(cat-file rc=1)。★
     ＝ ★此の一本は、今 disk にしか無い。disk が失せれば、45 束の臺帳を建てる術が消える。★
   - ★repo の外(`~/bin`)に在る器 = 5 本★(`agent_letter.py` `deferral_gate.py` `fleet_liveness_check.sh`
     `inbox_mark_read.py` `sb`)。★幹に載り様が無い★ ―― PR では治らぬ。置き場の裁が要る。
4. ★「版の上に在る」は「今使つて居る物が版に在る」の意では無い。★
   在る 6 本の内 2 本(`context_usage_warn.sh` `karo_mac_manifest_verify.py`)は ★disk と異版★。
   幹が運ぶ 2 本も ★幹の版 ≠ disk の版★。
5. ★版は走つて居る間に動いた。★origin の `karo-mac/km-gate-kou-otsu-20260917` は前弾(km-101・14:50)の
   `363d5fb0` から ★`68b6e07b`(＝幹)へ進んだ★。之に依り家老の宣「45 枝」は當方の刻では ★46 枝★と出る(下 二)。

## 二 母數 ―― 枝 46 本(家老の 45 との差を先に名指す)

- 「mac 枝」の宣: `refs/heads/{karo-mac,ashigaru-mac-1,ashigaru-mac-2,ashigaru-mac-3}/` 前置。
  `ls-remote` 240 行の内 ★60 本★(karo-mac 42 / a1 7 / a2 5 / a3 6)。相異なる sha = 59
  (同 sha 対 = `e8470d8c` `karo-mac/gate5-20260909` と `karo-mac/gate5-note-20260909`)。
  `tools/karo-mac-gate7-20260908` は席前置で無いゆゑ母數の外。★除いたのであつて、無いのではない。★
- 「不要」の宣: 其の tip が ★他の枝の tip の真の祖先★(＝呑まれて居る)。★同 sha は真の祖先に非ず★。
- 出目: ★不要 14 / 残 46 / 測れぬ 0★(`git cat-file -e` rc=0 が 60/60)。
- ★家老の 45 との差 1 本は `karo-mac/km-gate-kou-otsu-20260917` である。★
  前弾の刻に其の tip は `363d5fb0` で、★46 本の枝に呑まれて居た★(＝不要)。
  今 `68b6e07b`(幹)へ進み、呑む枝が 0 に成つた ∴ 残へ移つた。
  ★之は家老の測りが誤つて居たの意では無い。★測つた刻が違ふ。
- 器: `ki/20_eda45.py` → `raw/20_eda60.tsv`(60 本・呑み判定付) / `raw/20_eda45.txt`(46 本)。

## 三 ㋑ 45(當方は 46)枝の門が要る器 ―― 逐語で拾ふ

### 拾ひの根と字(先に宣する)

- 根: 各枝 X の `git diff --name-only 4be3ee19e1c5...X -- docs/evidence/` の内、
  ★`.py`/`.sh` で終るか path に `/_gate/` か `/ki/` を含む物★ ＝ 其の枝が自ら加へた門控と driver。
  延べ 2639 / 相異 1146 path。origin/main から受け繼いだ物は根の外。★「根の外」は「無い」の意では無い。★
- 字: `scripts/checks/<名>` / `bin/<名>` / `karo_mac_<名>` / `inbox_mark_read.py` `agent_letter.py`
  `deferral_gate.py` / `<名>gate<名>.(sh|py)`。拾つた名は basename へ畳んだ(置き場は㋐で測る)。
- 出目: 相異 67 名 / 延べ 4841。門控/driver が 0 本の枝 = 2(`karo-mac/daiko-teishutsu-20260916`
  `karo-mac/lot48235904-provenance-20260916`)。
- 器: `ki/30_hiroi.py` → `raw/30_hiroi.tsv` / `raw/30_hiroi_eda.tsv`。

### ★數が何を意味せぬか(数の規律3)★

1. ★「名が現れた」は「走つた」では無い。★註にも紙の本文にも器の名は出る。延べ 4841 は呼出回数では★ない★。
2. ★枝数 46 中 44 は「44 枝が其の器を要する」の證では無い。★「44 枝の門控か driver に其の名が在る」だけである。
3. ★0 本の枝 2 本は「門を通して居らぬ」の證では無い。★其の枝が `docs/evidence/` へ driver を
   加へて居らぬ(紙のみ・或は他の path へ置いた)といふ事である。
4. ★67 名は「67 種の器」では無い。★下の判じで 甲14/乙23/丙7/丁23 に割れる。

### 判じ(機械が決める・字面で決めぬ)

- 甲 = 其の名の file が `scripts/checks/` か `/Users/momizimac/bin` に実在する ＝ ★艦隊の器★ → ★14★
- 丙 = 甲に非ず、束の中(`docs/evidence/**` 追跡下)に同名が在る ＝ 束内の私器 → 7
- 乙 = 甲丙に非ず、`command -v` が `/bin` `/usr/bin` `/usr/sbin` `/opt/homebrew/bin` に解ける ＝ 系の器 → 23
- 丁 = 何れにも当たらぬ(切れた名・控の名) → 23
- ★㋐の表に載せるのは甲のみ。乙丙丁は名を `raw/40_bunrui.tsv` に残した。★

## 四 ㋐ 器の母數と、四つの目

母數の宣 = (A) `scripts/checks/` と `/Users/momizimac/bin` 直下の常の file(100 本・22+78)
∪ (B) ㋑の甲(14 本)。表は ★(B) に当たつた 14 本★を載せる(全 100 本は `raw/40_arika.tsv`)。

| 器 | 置き場 | ⑴disk | ⑵origin/main | ⑶local main | ⑷path を抱へる ref(90中) | ⑷同(origin heads 240中) | 枝(46中) |
|---|---|---|---|---|---|---|---|
| karo_mac_dasumae_gate.sh | scripts/checks | 有 | ★無★ | 有 | 61 | 55 | 44 |
| karo_mac_manifest_verify.py | scripts/checks | 有 | 有 | 有 | 65 | 59 | 44 |
| karo_mac_manifest_append.py | scripts/checks | 有 | ★無★ | ★無★ | ★0★ | ★0★ | 43 |
| karo_mac_gate4.sh | scripts/checks | 有 | ★無★ | 有 | 61 | 59 | 42 |
| context_usage_warn.sh | scripts/checks | 有 | 有 | 有 | 67 | 81 | 42 |
| deferral_gate.py | ~/bin | 有 | ★無★ | ★無★ | ★0★ | ★0★ | 13 |
| sb | ~/bin | 有 | ★無★ | ★無★ | ★0★ | ★0★ | 6 |
| inbox_mark_read.py | ~/bin | 有 | ★無★ | ★無★ | ★0★ | ★0★ | 5 |
| karo_mac_gate7.sh | scripts/checks | 有 | 有 | 有 | 65 | 69 | 2 |
| codex_cli_required_persona.sh | scripts/checks | 有 | 有 | 有 | 67 | 81 | 2 |
| agent_letter.py | ~/bin | 有 | ★無★ | ★無★ | ★0★ | ★0★ | 2 |
| dd169_kill_term_guard.sh | scripts/checks | 有 | 有 | 有 | 67 | 81 | 1 |
| fleet_liveness_check.sh | ~/bin | 有 | ★無★ | ★無★ | ★0★ | ★0★ | 1 |
| pretooluse_bash_guard.sh | scripts/checks | 有 | 有 | 有 | 67 | 81 | 1 |

- ref の母數: 手許 ★90★(heads 59 / remotes 7 / tags 23 / stash 1)。★家老の「64」と違ふ。★
  當方は `git for-each-ref` の全出目を採り、内訳を上に書いた。何れが正かは器の宣の違ひであつて、
  ★どちらかが誤つて居るの意では無い★。
- origin heads の母數 = `ls-remote` 240 本。★内 手許に物が在り測れたのは 83 本のみ★。
  残 157 本は ★測れぬ★(object が手許に無い・`fetch` は禁ゆゑ取りに行かぬ)。
  ∴ 表の「240中」欄は ★83 本を歩いた結果★であり、240 本を歩いた結果では★ない★。
- ★`~/bin` は repo の外ゆゑ ⑵⑶⑷ は構造上 悉く 0 である。★
  ★之は「器が無い」の意では無く、「git が知り得ぬ置き場に在る」の意である。★
- 器: `ki/40_arika.py` → `raw/40_arika.tsv` `raw/40_bunrui.tsv` `raw/40_ref_bosuu.txt`。

### ★「在る」と「同じ」は別 ―― 版の突合せ★

disk の内容の blob sha1 を ★自前で算じ★(`hash-object` は object を書き得るゆゑ使はず)、tree の blob と突合せた。

| 器 | disk blob | origin/main | local main | 幹 68b6e07b | ⑷a path ref | ⑷b ★版★ ref | ⑷c object rc |
|---|---|---|---|---|---|---|---|
| codex_cli_required_persona.sh | 1d1db3ffc807 | 同 | 同 | 同 | 67 | 67 | 0 |
| context_usage_warn.sh | 3212039429ae | ★異★ | 異 | 異 | 67 | ★3★ | 0 |
| dd169_kill_term_guard.sh | d0a3219f11a6 | 同 | 同 | 同 | 67 | 67 | 0 |
| karo_mac_dasumae_gate.sh | 054c442eaee3 | 無 | ★異★ | ★異★ | 61 | ★1★ | 0 |
| karo_mac_gate4.sh | da73cfef07e6 | 無 | ★異★ | ★異★ | 61 | ★1★ | 0 |
| karo_mac_gate7.sh | 3ef09fbd6983 | 同 | 同 | 同 | 65 | 65 | 0 |
| karo_mac_manifest_append.py | b56d6576c822 | ★無★ | ★無★ | ★無★ | ★0★ | ★0★ | ★1★ |
| karo_mac_manifest_verify.py | ebfc4c0ecc08 | ★異★ | 異 | 異 | 65 | ★1★ | 0 |
| pretooluse_bash_guard.sh | 8720591d7c09 | 同 | 同 | 同 | 67 | 67 | 0 |

- ★path を抱へる ref が 61〜67 在つても、今 disk で走つて居る版を抱へる ref は 1〜3 本しか無い。★
  `karo_mac_dasumae_gate.sh` / `karo_mac_gate4.sh` / `karo_mac_manifest_verify.py` は ★1/90★。
- 其の 4 本は worktree 未 commit の直し(`git status --porcelain -- scripts/checks/` = 4 行)である。
  ★之は當方が触つたのでは無い★ ―― 共有工作樹に他席の手が在る。當方は ★読取のみ★(下 七)。
- ⑷c は「object が在る」であり ★「ref から辿れる」の意では無い★(dangling・途中の commit・他席の枝が在り得る)。
- 器: `ki/55_dohitsu.py` `ki/56_ban.py` → `raw/55_dohitsu.tsv` `raw/56_ban.tsv`。

### `~/bin` の 5 本 ―― 名でも版でも repo に無い

全 ref・全 path の basename 表(相異 5402)に当たり、同名 path を数へた。

| 器 | disk blob | ⑸同名 path(全 ref) | ⑹object rc |
|---|---|---|---|
| agent_letter.py | c1f86701366b | ★0★ | ★1★ |
| deferral_gate.py | 1df478e2471b | ★0★ | ★1★ |
| fleet_liveness_check.sh | 37c5e804ef41 | ★0★ | 0 |
| inbox_mark_read.py | fdfaae089a02 | ★0★ | ★1★ |
| sb | 3e63aa3af8af | ★0★ | ★1★ |

- ★4 本は版の何處にも無い(同名 path 0・object 無)。★
- `fleet_liveness_check.sh` のみ ⑹=0 ＝ ★同じ中身の blob は object として在る★が、
  ★其の名の path を持つ ref は無い★。＝ 何處かの束に控として入つて居る蓋然が高い。
  ★但し「何處に」は測つて居らぬ。★測るなら全 ref の全 blob と突合せる要が在る。
- 器: `ki/57_hbin.py` → `raw/57_hbin.tsv`。

## 五 ㋒ 幹 68b6e07b が運ぶ器と、引き算

- 幹の素性: `MomiziMac` / `Thu Sep 17 15:25:22 2026 +0900` /
  「docs(evidence): 幹の push 願ひ の紙を ★commit の中へ据ゑる★(裁 seq326145・軍師mac 326139 REVISE)」。
- ★幹は既に origin へ着いて居る★ ―― `refs/heads/karo-mac/km-gate-kou-otsu-20260917`(手許・origin 共)。
  ★但し origin/main には無い。★
- 幹の `scripts/checks/` = ★15 本★ / origin/main = ★13 本★ / 幹のみ = ★2 本★ / main のみ = 0 / 両方 = 13。
  幹のみ: `scripts/checks/karo_mac_dasumae_gate.sh` `scripts/checks/karo_mac_gate4.sh`。

引き算の則(先に宣する): 欠 = ㋐の甲で ⑵origin/main=0 の物。幹が運ぶ = 幹の tree に其の path が在る。
残る欠 = 欠 − 幹が運ぶ。★「幹が運ぶ」は「幹が origin/main に着く」の意では無い。★

| | 本数 | 名 |
|---|---|---|
| ㋑の甲 | 14 | ― |
| 内 origin/main に在る | 6 | codex_cli_required_persona.sh / context_usage_warn.sh / dd169_kill_term_guard.sh / karo_mac_gate7.sh / karo_mac_manifest_verify.py / pretooluse_bash_guard.sh |
| ★欠★ | ★8★ | ― |
| 幹が運ぶ | 2 | karo_mac_dasumae_gate.sh / karo_mac_gate4.sh |
| ★残る欠★ | ★6★ | ★karo_mac_manifest_append.py★ ＋ ~/bin 5本(agent_letter.py / deferral_gate.py / fleet_liveness_check.sh / inbox_mark_read.py / sb) |

- ★∴ 幹が origin/main へ着地しても、臺帳を建てる器 `karo_mac_manifest_append.py` は版に載らぬ。★
- ★幹が運ぶ 2 本も「幹の版 ≠ disk の版」である(上 四)。★
  ∴ 幹の着地は ★「名が版に載る」までを果たし、「今の版が載る」までは果たさぬ★。
- 器: `ki/50_miki.py` → `raw/50_miki.tsv` `raw/50_hikizan.tsv`。

## 六 ㋓ 運ぶ枝の案(★紙に書くのみ・据ゑず★)

★変更統制(委員長許可)ゆゑ、実行は裁の後。當方は一つも据ゑて居らぬ。★

### 案甲 ―― 残る欠の内、repo で治る一本

- ★何の器を★: `scripts/checks/karo_mac_manifest_append.py`(disk blob `b56d6576c822`・object すら無い版)。
- ★何処へ★: 幹 `68b6e07b` を親とする新枝一本 → origin/main への小PR。幹と同じ枝に相乗りさせぬ
  (幹は既に軍師の裁を経て居り、後から中身を足せば其の裁が古びる)。
- ★何故★: 45 束の臺帳は悉く此の一本で建てられて居る(㋑ 43/46 枝で名が出る)。
  版に無い ∴ ★disk が失せれば、過去の紙を建て直す術が消える★。門は幹が運ぶが、臺帳は誰も運ばぬ。
- ★戻し方★: 新枝ゆゑ `main` は不動。取り消しは其の PR を閉ぢるだけ(refs の書換も revert も要らぬ)。
  着地後に戻すなら `git revert <merge sha>` 一手 ―― 追加のみの commit ゆゑ衝突面は
  `scripts/checks/karo_mac_manifest_append.py` 一 file に閉ぢる。

### 案乙 ―― `~/bin` の 5 本(★PR では治らぬ★)

- ★何の器を★: `agent_letter.py` `deferral_gate.py` `fleet_liveness_check.sh` `inbox_mark_read.py` `sb`。
- ★何処へ★: ★當方は置き場を決めぬ。★二つの道が在り、何れも ★変更統制の案件★である。
  道①＝repo の中(例 `scripts/tools/`)へ写しを据ゑ、`~/bin` は其の写しを指す。
  道②＝repo の外に留め、★「席の私器であつて艦隊の器では無い」と正本に明記する★。
- ★何故★: 今は ★どちらでも無い★。紙は此の 5 本に依つて居るのに、正本は其れを器として数へて居らぬ。
  ★曖昧な儘なら、disk が失せた時に「誰の落度か」すら決まらぬ。★
- ★戻し方★: 道①は追加のみゆゑ `git revert`。道②は正本の一行の差し戻し。
  ★何れも「器を動かす」前に「どちらの道か」を裁で決める要が在る。★當方は案のみ出す。

### 案丙 ―― 版の食ひ違ひ(★着地の後に測る事★)

- ★何の器を★: `context_usage_warn.sh` `karo_mac_manifest_verify.py`(origin/main に在るが disk と異版)、
  および幹が運ぶ `karo_mac_dasumae_gate.sh` `karo_mac_gate4.sh`(幹の版 ≠ disk の版)。
- ★何処へ★: 何処へも動かさぬ。★測る段を一つ足すだけ★。
- ★何故★: 幹が着いた時「器は版に載つた」と読むと、★載つたのは名であつて版では無い★ を見落とす。
  4 本とも ★今 disk で走つて居る版を抱へる ref は 1〜3 本★しか無い。
- ★戻し方★: 測るだけゆゑ戻す物が無い。測つて尚 差が残るなら、其の時に別の札とせよ。

## 七 禁の順守

| 禁 | 當方の所業 | 物證 |
|---|---|---|
| 枝を一本も消すな | 消して居らぬ | `for-each-ref \| wc -l` = 90(始 90 / 終 90・下 九) |
| checkout するな | 打つて居らぬ | HEAD は始終 `260f2a06`(他席 專任3 の枝)の儘 |
| refs を書換へるな | 書換へて居らぬ | `ls-remote` は読取・`fetch`/`push` 一度も打たず |
| 器を `scripts/` へ据ゑるな | 据ゑて居らぬ | `git status --porcelain -- scripts/` の 4 行は★當方の前から在る他席の直し★ |
| 読取のみ | 守つた | `hash-object` すら使はず sha1 を自前で算じた(object を書き得るゆゑ) |
| PR を起票するな | 起票して居らぬ | ㋓は★紙の上の案★であり、`gh` を一度も打つて居らぬ |
| 他席の pane を覗くな | 覗いて居らぬ | `tmux capture-pane` 一度も打たず |

## 八 ㋔ 零の四つの札

本紙の零は三つ。同じ路・同じ器で陽性対照を鳴らした(`ki/58_taishou.py` → `raw/58_taishou.txt`)。

| 零 | 值 | 陽性対照 | 対照の出目 | 根と深さ | rc | 刻 |
|---|---|---|---|---|---|---|
| ① append を抱へる ref | ★0★ | 同じ歩きで verify を数へる | ★65★ | repo 全 90 ref・`ls-tree`(path 指定) | 0 | 2026-09-17T15:53:08 |
| ② ~/bin 甲 5本の同名 path | ★0★ | 同じ basename 表で `CLAUDE.md` | ★在り★ | 全 90 ref・`ls-tree -r`(全 path) | 0 | 同上 |
| ③ 其の版の object | ★無(rc=1)★ | 同じ `cat-file -e` で `HEAD:CLAUDE.md` | ★rc=0★ | git object 庫 | 1 | 同上 |

★対照 三つ悉く鳴つた ∴ 零は器の黙りでは無く、實の零である。★

## 九 門控・臺帳・臺帳外

- 臺帳は ★束内相対★(裁 seq322699)。`ki/91_daichou.py` が束へ `cd` してから
  `scripts/checks/karo_mac_manifest_append.py` を呼ぶ。★其の器こそが、本紙の主題である一本である。★
  (＝ ★本紙は、版に無い器で焼かれた紙である。★之を紙の上で宣する事が、此の弾の要點の一つである。)
- 門は `KM_GATE_MANIFEST_BASE=.` 付きで通した。控は `_gate/` の ★最も新しい `92_gate_*`★。
- 臺帳外: `_gate/` 下の門控と `__pycache__`。★門の出目は門の後に生まれる ∴ 臺帳に載り様が無い。★
  `ki/91_daichou.py` は `_gate` と `__pycache__` を歩きから除く。
  ★「除いた」は「歩いて居らぬ」の意であり、「無い」の意では無い。★
- 陽性対照(門其の物): `ki/92b_taishou.py` ―― 臺帳の行を丸ごと file 名として渡し、門が鳴る事を確かめる。
  ★鳴らねば門を信じるな。★
- 一行目の数は ★手で書いて居らぬ★。`ki/93_ume.py` が控の `.rc` と `.out` から拾ひ、
  当たつた行を数へて(1本・頭)から焼く。★当たらぬ置換は黙つて何もせぬ ∴ 数へねば「直つた様に見える」。★
- ★其の器自身が臺帳の母數を +2 する★(`ki/93_ume.py` と `raw/93_ume.txt`)。
  ゆゑに 器→kaki→臺帳→門 を ★二度★ 回した。一度目の門の数(母數 31)は★己を含まぬ古い数★であり、
  紙に焼いたのは二度目以降の ★33★ である。★紙は己を含む臺帳の数を、一度では書けぬ。★

## 十 納め便

- 家老mac へ `report_received` で送る。★300字が條★・`python3` の `len` で測り其の数を此処へ焼く。
- 着手便: 273 字(`raw/95_chakushu.txt`)・`msg_20260917_154455_e1b4ab25`(箱の写しで検めた)。
- 納め便の字数と id は `raw/95_bin.txt` と `_gate/96_todoke_*.txt` に残す。
- ★軍師mac は死箱ゆゑ、監査は家老mac が代送する。★

## 十一 commit せぬ事(前弾の答を承けて)

家老の答 ⑴〜⑷ を承けた。★席は commit せぬ。★refs は家老が plumbing で扱ふ。
束の名は ⑷ に従ひ ★`ashigaru-mac-2_` で始めた★。`.gitignore:7` の裸 `*` は触つて居らぬ。

## 十二 次に何を測れば判ずるか

1. ★`fleet_liveness_check.sh` の blob が何處の ref・何處の path に在るか。★
   (全 ref の全 blob と突合せる要が在る ―― 本弾では測つて居らぬ。)
2. ★origin heads 240 本の内 測れぬ 157 本。★`fetch` が解かれた時に初めて測れる。
   ∴ 表の「240中」は ★83 本を歩いた結果★である事を、読む者に必ず添へよ。
3. ★門を枝の上で走らせた時 rc=0 か。★`checkout` 禁ゆゑ本弾でも測れて居らぬ(前弾 km-101 と同じ)。
4. ★`~/bin` の 5 本を、正本は器として数へて居るか。★数へて居らぬなら、案乙の道②が先に要る。
