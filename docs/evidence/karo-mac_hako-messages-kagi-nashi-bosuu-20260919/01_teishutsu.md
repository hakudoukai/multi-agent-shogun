# 判定提出の束 ―― 裁337507⑵ 箱の同型（messages 鍵無）を母數行へ常設

親裁の逐語（seq337507⑵）:
> **⑵箱の同型=潜在ゆゑ触れぬが正。但し母數行へ messages鍵無=N を常設し顕在化を見える形に。**

∴ 本弾は **表の顔を一切変へず**（触れぬ）、**母數行へ `★messages鍵無=N★(内 空帳=M)` を常設**（0 でも刷る）した物である。

---

## ■① 対象 tuple（一組のみ）

```
ref名   = refs/heads/karo-mac/km-agent-status-hako-kagi-nashi-bosuu-20260919
commit  = ★下記の検算コマンドで出せ★（紙は己を含む tuple の 40桁を書けぬ）
tree    = ★同★
```

★紙が己の 40桁を書けぬ理由★: 本紙は commit する tuple の中に入る ∴ 紙に 40桁を焼くと
自己参照で確定せぬ。**40桁は便（pc_handshake）に書き、紙には検算コマンドを置く。**

```bash
cd /Users/momizimac/multi-agent-shogun
git rev-parse refs/heads/karo-mac/km-agent-status-hako-kagi-nashi-bosuu-20260919          # = commit 40桁
git rev-parse refs/heads/karo-mac/km-agent-status-hako-kagi-nashi-bosuu-20260919^{tree}   # = tree 40桁
git rev-list --count refs/heads/karo-mac/km-agent-status-hako-kagi-nashi-bosuu-20260919 ^2ae4484504b1a8f81e9743b65e0cf5681ff836f2   # = 1（本弾1個のみ）
```

★ref が「先端」であることの検算★ = 上の `git rev-parse <ref>` が便に記した commit と一致する
（祖先を出して居らぬ）。**この tuple は提出後 不動。**

### ★逸脱の申告 ―― 親を origin/main に取らず 前弾に取つた★

```
親 = 2ae4484504b1a8f81e9743b65e0cf5681ff836f2
     （裁337507⑶疵① ―― usage/rc 分けの弾。委員長 seq338134 で押し完了・実視済）
```

**「1弾1枝＝origin/main から切る」への逸脱である。**
援用: **裁338111②「★逸脱認可★ 親=前弾 可（blob 一致で差分1弾）」**。
本弾の触る本体は `scripts/agent_status.sh` 一本であり、前弾が同じ file を彫つてゐる ∴
origin/main から切ると前弾の 15 行を呑み、差分が 2 弾分に成る。前弾を親に取れば差分は本弾のみ。

★実測（差分は 1 弾分）★:
```
git diff --numstat 2ae4484504b1a8f81e9743b65e0cf5681ff836f2 -- scripts/agent_status.sh
→ 42      15      scripts/agent_status.sh
```

---

## ■② 成果物（artifact）

### 本体（彫つた物・1 本）

| repo-relative path | sha256(64桁) | bytes | lines(grep -c '') |
|---|---|---|---|
| `scripts/agent_status.sh` | `82bf3043565060d4b49685dfe45c3a84cc55f95374ff429d22015aaf79f9e1bd` | 29205 | 586 |

前版（親 `2ae44845…` の物）= `8552c2c967088c35c889ce4d1574e3ab30c3014e6d7c9df481afc323c30f77fb` / 26917 byte / 559 行。
`bash -n scripts/agent_status.sh` rc=0（実走）。据ゑた箇所 **13**（附一に逐一）。

### 束（器 4 本・fixture 10 本・raw 9 本 ＋ 本紙 ＝ 24 本）

| repo-relative path | sha256(64桁) | bytes | lines |
|---|---|---|---|
| `docs/evidence/karo-mac_hako-messages-kagi-nashi-bosuu-20260919/kiki/km_hako_ryoutaishou.sh` | `a0d7be3f734b2cd81d40b8321af850079a233dd28e06519ab2af8361d21b1a4d` | 3825 | 80 |
| `…/kiki/km_patch_hako.py` | `1b7c9ce0c07948ba159ceaddb361c9ce55809ca43ebb3eea0a4ef042309838d5` | 6906 | 150 |
| `…/kiki/km_hako_hantei.sh` | `e59e3d34ea48c728f62330297b8d77a67c7aa345e4bf6f3f1be188c0f7ff5c86` | 2303 | 46 |
| `…/kiki/km_genbutsu_hako_kagi.py` | `4badbf513ca7c4fd36d0ad583331ab1c43513fbccc6d420012897752f9bf2e11` | 2073 | 42 |
| `…/fixtures/hideyoshi.yaml` | `e5eddef1cf8386e42b863e516fd75683870243642d6c88963b80994b860653bb` | 143 | 7 |
| `…/fixtures/ashigaru1.yaml` | `ab1a54afd56934aa64cbaf657fc3cabaf89559dd0761113f748f1e24de42b24a` | 13 | 1 |
| `…/fixtures/ashigaru2.yaml` | `90e5e6292b2a93a135e3dd5088888e0c92b62cd8c09c432f1ab829115e28189c` | 57 | 2 |
| `…/fixtures/ashigaru3.yaml` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 | 0 |
| `…/fixtures/ieyasu.yaml` | `7aa19bb3e7511b5339a2cadaf945cfcc1f46877eaaa176f547412cf9f15a2668` | 49 | 2 |
| `…/fixtures/takenaka.yaml` | `3b5be00209fc00f2821e0b2f68fd02f8e147a105769a72d317b233995575a681` | 72 | 4 |
| `…/fixtures/maeda.yaml` | `f1ef1fad69280b228394a99c86b62096e2bef5b54039263a149d2ec5532b2f2c` | 62 | 3 |
| `…/fixtures/ashigaru5.yaml` | `0ee1757dc68d133fceab8d6a2376529a9f8c1f021cee2d0f51ce8c19114b65fb` | 104 | 5 |
| `…/fixtures/ashigaru6.yaml` | `fcb86d2a4154083dcdb7fed00027b2dd451008eb39b8ac37b8a577efb98db0bc` | 68 | 3 |
| `…/fixtures/ashigaru7.yaml` | `3da8ea2cc73b3f647e99bb9d5719a74a7c947d7b2a20b06281a8c97a3b5506de` | 84 | 3 |
| `…/raw/40_fixtures.txt` | `4031d5f38b4a407a9c1cf510b00db31a8a9ab1b91928b4daf90eeca837686880` | 1795 | 18 |
| `…/raw/50_before.txt` | `1f83b78d47de36d47d04b1b0af820c2eae07e93941d95f7dc49d324eddfbb664` | 3172 | 54 |
| `…/raw/60_after.txt` | `1a85bd865850161524fd10dee0546838bd3945397e8e48bb1ba809cdab17ce41` | 3357 | 53 |
| `…/raw/61_after_kagi_ari_only.txt` | `e2ccf4822cbcd2f533a82df95739fe09489b2f7434d882d5f74f9a69d8e0111a` | 2091 | 39 |
| `…/raw/62_hyou_byte_totsugou.txt` | `f1a71242e26145fe19d4e809ce43b0e59ef5f51a928b95fca41b3e416e530a96` | 1885 | 31 |
| `…/raw/63_genbutsu.txt` | `e41afc6433c00fe4cd0282430818f1a6b6b5eb19fa2e6f370e8ad492fdca19c6` | 1865 | 26 |
| `…/raw/64_hantei.txt` | `b461375aa7a4f6c1783c1cf3a566b8f58bba748ee424e3826daf3227ea5f83d7` | 2485 | 58 |
| `…/raw/65_genbutsu_hako_kagi.txt` | `0a16f1e3703a01bc022d8a77bdf8345c05c6537496c9a4d1933e754b9cd19078` | 2280 | 33 |
| `…/raw/66_saisei.txt` | `2ef5f3f3a7d1188681467a64cc7e9f0f275425e1eace4b2bb34b8382bbbca4eb` | 4823 | 86 |

★席-local path は一つも用ゐて居らぬ★（悉く repo-relative）。
但し **raw の本文中には砂場の絶対 path（`/var/folders/...`）が刷られてゐる** ―― 之は
「何処で走らせたか」の申告であつて成果物の所在ではない。

★㋚ 第十一の形＝「箱が無い」（`ashigaru8`）は fixture を置かぬことで作る★ ∴ file は 10 本で母數は 11。

---

## ■③ 実走の raw（①と同一 tuple の disk 状態）

| 何を測つた走か | raw path | rc |
|---|---|---|
| fixture の byte/sha256/意味・母數 11=10+1 の宣 | `…/raw/40_fixtures.txt` | 0 |
| **前版**（親 `2ae44845…` の `scripts/agent_status.sh`）を砂場で走らせた | `…/raw/50_before.txt` | 0 |
| **後版**（本弾）を同じ砂場・同じ fixture で走らせた | `…/raw/60_after.txt` | 0 |
| **鍵在のみ 4 席**に絞つて後版を走らせた（0 でも刷る證） | `…/raw/61_after_kagi_ari_only.txt` | 0 |
| 前後の **表（stdout）の byte 突合** | `…/raw/62_hyou_byte_totsugou.txt` | 0 |
| **生きた樹**で読取のみ走らせた | `…/raw/63_genbutsu.txt` | 0 |
| 判定器で期する表と突合 | `…/raw/64_hantei.txt` | 0 / 0 / **1** |
| **生きた箱 19 本**の鍵の census（読取のみ） | `…/raw/65_genbutsu_hako_kagi.txt` | 0 |
| **tuple から復元して再走・再判定**（⑥ 再正） | `…/raw/66_saisei.txt` | 0 / 0 |

各 raw の sha256 は ② の表に在る。cwd と argv は **raw の冠に逐語で刷つてゐる**（下は代表 4 本）。

```
# 50/60（両対照の器）
cwd  = /Users/momizimac/multi-agent-shogun
argv = bash docs/evidence/karo-mac_hako-messages-kagi-nashi-bosuu-20260919/kiki/km_hako_ryoutaishou.sh <前版sha|後版>
       （器の中で mktemp -d した砂場へ lib/ config/ scripts/*.sh scripts/checks を写し、
         .venv は ln -s で★読取 symlink★、fixtures を queue/inbox/ へ置き、
         cd $SAND && bash scripts/km_hako_target.sh を走らせる）

# 61（鍵在のみ）
argv = KM_HAKO_ONLY="hideyoshi ashigaru1 ashigaru5 ashigaru6" bash …/kiki/km_hako_ryoutaishou.sh 後版

# 63（生きた樹・読取のみ）
cwd  = /Users/momizimac/multi-agent-shogun
argv = bash scripts/agent_status.sh

# 65（生きた箱の census・読取のみ）
argv = .venv/bin/python3 -B …/kiki/km_genbutsu_hako_kagi.py queue/inbox
```

★rc は pipe に通さず其の場で読んだ★（`raw/64` の冠に明記。`… | tail` の rc を読む疵を本段で一度踏み、直した）。

---

## ■④ 依存の境界

```
lockfile = requirements.txt  sha256=46ab49a3e33f78c3f3313886a94834884a636df9589516bba066ae6122c46844  (13 byte)
外部 node_modules 参照        = ★無し★（本弾は bash + python3 のみ・node を一切用ゐぬ）
外部 symlink 参照             = ★無し★（repo の外を指す symlink は張つて居らぬ）
```

★★申告（symlink を一つ張つてゐる）★★:
両対照の器は砂場（`mktemp -d`）の中に **`ln -s <repo>/.venv <砂場>/.venv`** を張る。
之は **repo 内の `.venv` を指す読取 symlink** であり、**repo の外を指さぬ**。
理由: `scripts/agent_status.sh` は `PYTHON="${SCRIPT_DIR}/.venv/bin/python3"` を見る ∴
砂場に `.venv` が無いと **`PYTHON_AVAILABLE=false` へ黙つて倒れ、箱を一本も読まぬのに rc=0** に成る
（★己の疵★・附二⑴）。`cp -P .venv/bin/python3` では `sys.prefix` が砂場を指し yaml が落ちる ∴ symlink が正。

---

## ■⑤ 件数

```
正 = 15/15（前版・判定器 rc=0）   ★器自身の陰性対照★＝鍵無欄が無い・no-key 0 本を期して当たる
正 = 17/17（後版・判定器 rc=0）
```

★意味負★（★恒真でないことの證★）= **3/10**
箱を置いた 10 席の内、旗が立つのは **3 本のみ**である。

| 立つ（鍵無＝3） | 立たぬ（鍵在で真に未読 0 ＝3） |
|---|---|
| ㋒ `ashigaru2` 57B ―― `messages` 鍵の無い dict | ㋑ `ashigaru1` 13B ―― `messages: []`（空 list） |
| ㋓ `ashigaru3` 0B ―― 空帳（`None` ∴ 鍵も無い）→ `e` | ㋗ `ashigaru5` 104B ―― 全既読 |
| ㋙ `ashigaru7` 84B ―― 偽鍵 `message`（単数） | ㋘ `ashigaru6` 68B ―― 項が写像に非ず |

残り 4 本（㋐未読2／㋔頂が list／㋕壊れ yaml／㋖messages が dict）は
**前から在る「数に非ざる顔」（`!`/`S`/`E`/`X`）** へ落ちる ∴ 鍵無の旗は立たぬ。
**∴ 旗は恒真でなく、「鍵が無い」形のみを拾ふ。**

```
陽性対照 = 鍵無 3 形（㋒ dict／㋓ 空帳／㋙ 偽鍵）を置いた走で ★messages鍵無=3★(内 空帳=1) と立つ（raw/60）
陰性対照 = 鍵在のみ 4 席に絞つた走で ★messages鍵無=0★(内 空帳=0) と ★0 でも刷る★（raw/61）
           ＋ 前版の走では ★欄自体が存在せぬ★（raw/50）= 器が本当に新設欄を測つてゐる證
```

### ★裁の「触れぬが正」を満たした證（表は byte 同一）★

```
前版の表(stdout) sha256 = 8d4c1a9325537587dbb3cda36104445eb8e2c51fafbd92a8ac646fd87f276647  1137 byte  15 行
後版の表(stdout) sha256 = 8d4c1a9325537587dbb3cda36104445eb8e2c51fafbd92a8ac646fd87f276647  1137 byte  15 行
diff -u 前 後 = 空（rc=0）
stderr のみ増えた: 842 byte / 5 行 → 1508 byte / 9 行
```
∴ **表の顔は 1 byte も動いて居らぬ。増えたのは母數行と註（＝stderr）のみ。**

---

## ■⑥ 復元

```
復元後の sha256 = ① の tuple から取り出して測る（下記コマンドの出目が ② と一致する）
```

```bash
R=refs/heads/karo-mac/km-agent-status-hako-kagi-nashi-bosuu-20260919
SPEC="${R}:scripts/agent_status.sh"; git show "$SPEC" | shasum -a 256
#  → 82bf3043565060d4b49685dfe45c3a84cc55f95374ff429d22015aaf79f9e1bd
for f in kiki/km_hako_ryoutaishou.sh kiki/km_patch_hako.py kiki/km_hako_hantei.sh \
         kiki/km_genbutsu_hako_kagi.py 01_teishutsu.md; do
  SPEC="${R}:docs/evidence/karo-mac_hako-messages-kagi-nashi-bosuu-20260919/$f"
  printf '%s ' "$f"; git show "$SPEC" | shasum -a 256
done
```
★`SPEC` を別変数に取る理由★: zsh では `git show "$REF:path"` が `:s` 修飾と読まれ
`(eval): bad substitution` ＋空 sha を吐く（己が踏んだ罠）。

```
clean 確認 = ★未測（理由）★
```
**理由**: 当樹は **共用樹**（他席が同時に働いてゐる）であり、かつ `.gitignore:7` が
**裸の `*`（allowlist 方式）** である ∴ `git status --porcelain -uall` は
**「追跡外が悉く畳まれて 0 行」** に成り得る ―― **0 行が clean の證に成らぬ（偽の通）**。
加へて他席の未commit が同じ出目に混じる ∴ **本席の弾の clean を此の器では測れぬ**。

★代替（blob = disk を実測した）★:
```bash
git cat-file -p "${R}:scripts/agent_status.sh" | shasum -a 256   # = 82bf3043…（上と一致）
shasum -a 256 scripts/agent_status.sh                            # = 82bf3043…（disk）
```
∴ **「tuple の中身 = disk の中身」を sha256 で突き合はせた**。之が clean の代替である
（裁338134 丁「⑥clean 未測＋blob=disk 代替で可」を援用）。

```
再正 = ★17/17（実測・rc=0）★  raw = `…/raw/66_saisei.txt`
```
★実際に tuple から復元して再走した★:
```
復元した版 sha256 = 82bf3043565060d4b49685dfe45c3a84cc55f95374ff429d22015aaf79f9e1bd（② と一致）
復元版の表(stdout) sha256 = 8d4c1a9325537587dbb3cda36104445eb8e2c51fafbd92a8ac646fd87f276647 / 1137 byte（⑤ と一致）
判定 = 正 17/17 否 0 ／ 走 rc=0 ／ 判定 rc=0（★悉く pipe に通さず其の場で読んだ★）
```
★入力の版だけは /tmp へ置いた（`/tmp/km_saisei_body.sh`）★ ―― 之は走の入力であつて證の紙ではない。
證は束内の `raw/66_saisei.txt` である（「證の紙を /tmp に置くな」を破つて居らぬ）。

---

## ■⑦ 法令根拠

★該当せず★（算定・記載要件に触れぬ・器の観測欄の追加のみ）。

---

## 附一 ―― 据ゑた 13 箇所（`scripts/agent_status.sh`）

1. 度數宣言へ `N_BOX_NOKEY=0` を追加（註＝裁337507⑵ の逐語）
2. 度數宣言へ `N_BOX_KARA=0` を追加（註＝「0 でも刷る」）
3. `get_unread_count` 器無の道 → `echo "P -"`
4. 同 帳無の道 → `echo "- -"`
5. 同 python 内 読めぬ → `print('! -')`
6. 同 空 → `print('E -')`
7. 同 `S`（頂が dict でない）→ `print('S -')`
8. **★新分岐★** `if 'messages' not in data:` → stderr へ
   `no-key %s: messages 鍵が無い ―― 顔は 0 だが「未読が無い」ではない` ＋ `print('0 n')`
9. `data is None`（空帳）→ stderr へ `…空帳ゆゑ messages 鍵も無い…` ＋ `print('0 e')`
10. `msgs = data.get('messages', [])` → **`msgs = data['messages']`**（同型化の源を絶つ）
11. 数へた道 → `print('%d k' % …)` / `print('S k')`、落ちた道 → `|| echo "X -"`
12. 呼び手を二欄受けへ: `box_out=$(get_unread_count "$agent")` →
    `read -r unread box_flag <<< "$box_out"` → `unread="${unread:--}"; box_flag="${box_flag:--}"`
    （欄が落ちたら **「判ぜず」へ倒す**・黙つて 0 にせぬ）＋
    `case "$box_flag" in n) N_BOX_NOKEY=$((N_BOX_NOKEY+1));; e) N_BOX_NOKEY=$((N_BOX_NOKEY+1)); N_BOX_KARA=$((N_BOX_KARA+1));; esac`
13. 結語へ `／ 箱: 数に非ざる顔=%d ★messages鍵無=%d★(内 空帳=%d) ／` ＋ 新 註一行

★表に刷るのは `$unread` のみ★ ―― `$box_flag` は母數行と註にしか出さぬ（∴ 表が byte 同一に成る）。
★空帳は鍵無の内数★ ―― `e` は NOKEY と KARA の両方を上げる（空帳は「鍵も無い」ゆゑ）。
★註は「黙らぬ」の和には入れぬ★ ―― 既在の数の規律を壊さぬため別行に出す。

## 附二 ―― 己の疵 三件（自ら申す）

⑴ **砂場に `.venv` を張らず、器が箱を一本も読まぬのに rc=0 で通つた走を、一度 正として扱つた。**
   初回走は「器無=11／箱: 数に非ざる顔=11」＝**測れて居らぬ**。`raw/50_before.txt` の冠に
   **「初回走は無効」と自ら宣して**載せ、`ln -s` へ改めて再走した。
   ★教訓★: `PYTHON_AVAILABLE=false` は **黙つて rc=0** に倒れる ∴ 砂場の器は
   「python が生きてゐるか」を陽性対照で先に確かめねばならぬ。

⑵ **多 file の突合で、`grep -h '★母數★' 50 60 61` の出力順が argv 順でなかつた。**
   shell の `grep` は **ugrep** であり、並べた file の出る順は argv 順とは限らぬ（61→50→60 の順に出た）。
   一瞬「file が入れ替はつた」と読んだが、**file ごとに `sed -n` / `grep -m1` で個別に読み直し**、
   三本悉く正しいことを実視した。★多 file の突合は file ごとに個別に読め。★

⑶ **rc を pipe に通した。** `bash 判定器 … | tail -12; echo "rc=$?"` は tail の rc である
   （己の既在の条を踏んだ）。出を file へ取り `RC_Z=$?` を其の場で読み直し、
   `raw/64_hantei.txt` に **「★rc は pipe に通さず其の場で読んだ★」** と冠した。

## 附三 ―― ★本弾が「今 起きてゐる害」を直した物ではない旨★

**生きた箱 19 本を読取のみで歩いた（raw/65）**:
```
母數 = 19 本 ／ 鍵在(k)=19 ★鍵無=0★(内 空帳=0) 形違=0 parse不能=0
```
∴ **現に鍵無の箱は一本も無い。本弾は「今は起きて居らぬが起き得る潜在」を顕在化する物である**
 ―― 之は親裁の「⑵箱の同型=**潜在ゆゑ触れぬが正**」と合致する。

**生きた樹での走（raw/63）は rc=0・鍵無=0 であつたが、之を「疵が無い證」と読むな。**
`scripts/agent_status.sh` が歩く席は
`SECTION18_MAINPC_PANE_ORDER`（6 名: hideyoshi ashigaru1 ashigaru2 ashigaru3 ieyasu takenaka）＋
`SECTION18_SECONDPC_AGENTS`（5 名: maeda ashigaru5 ashigaru6 ashigaru7 ashigaru8）＝ **11 席**であり、
**Mac の席名は入つて居らぬ** ∴ 生きた樹では **11 席の箱が悉く不在（帳無=11）** である。
**∴ 生きた樹の「鍵無=0」は「箱が無いゆゑの 0」であつて、疵の不在の證ではない。**
（鍵無が立つか否かを実測した路は砂場の両対照＝raw/50・60・61 のみである。）
