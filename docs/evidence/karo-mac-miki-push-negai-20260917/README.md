# 幹の push 願ひ ―― 枝名と sha、及び secret 0 の検算(裁 seq326093①)

**出したのは家老mac。読取のみで測つた。枝は一本も消して居らぬ・push もして居らぬ。**

裁 seq326093 逐語:「裁(326088)=幹先行で可。順: ①幹 km-gate-kou-otsu(363d5fb0・16com/464file)を PR 用に整え
(main へ rebase 不要・merge commit 方式・secret 0 検算)、枝名+sha を「push願い」1行で寄越せ→総監督が push 代行し
PR 起票・判定=軍師mac・merge は総監督が6基準で。②幹着地後に甲10を器重なり3件の順で小PR。③乙35は理事長裁待ちのまま触れず。紙は受領。」

---

## 一 ★push 願ひ★ ―― 一行で言へば

| 項 | 値 |
|---|---|
| 枝名 | `karo-mac/km-gate-kou-otsu-20260917` |
| sha | `363d5fb06084` / full `363d5fb060845171338c067ef42bfcbef8ad9188` |
| 対 origin/main | **16 commit / 464 file**(三点) |
| 手許 `refs/heads/main` | **同一 sha**(幹はローカル main その物) |
| PR の形 | **merge commit 方式**(早送り不可 ―― §三) |
| secret | **PR が足す行の当り = 0**(§四) |
| 当席の手 | commit まで。**push は総監督の代行を請ふ** |

## 二 版 ―― 三つの ref を名指しで

```
枝 karo-mac/km-gate-kou-otsu-20260917 = 363d5fb06084  (rc=0)
手許 refs/heads/main                  = 363d5fb06084  (rc=0)   ★枝==手許main★
origin/main                           = 4be3ee19e1c5  (rc=0)
full: 幹 363d5fb060845171338c067ef42bfcbef8ad9188
      基 4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1
分岐点(merge-base)                    = 6e9d40600a80
```

**逐語の測り** ―― `raw/30_arika.txt`:
```
git rev-parse refs/heads/karo-mac/km-gate-kou-otsu-20260917
git rev-parse refs/heads/main
git merge-base origin/main 363d5fb06084
```

## 三 PR の形 ―― ★早送りは効かぬ★

```
origin/main は幹の祖先か = ★否★ (git merge-base --is-ancestor origin/main 363d5fb0 → rc=1)
幹は origin/main の祖先か =  否  (rc=1)
幹が進んだ = 16 commit / origin/main が進んだ = 21 commit
```

**両者は分岐点 `6e9d40600a80` から★別々に★進んで居る。** ∴ 早送り(fast-forward)は効かず、
**merge commit が要る** ―― 裁326093①の「main へ rebase 不要・merge commit 方式」と合ふ。
**rebase は行つて居らぬ**(行へば 16 の sha が悉く変はり、他席が此の幹の上に積んだ 5 commit が宙に浮く)。

## 四 secret 0 の検算 ―― ★零には四つの札★

母數を**二つ**に分けた。**PR の可否を決めるのは乙である。**

| | 母數 | 当り |
|---|---|---|
| 甲 | 幹の tree の file **967 本**(内 読めぬ2・2進42・測つた923) | **6 件** |
| 乙 | `origin/main...幹` の patch が**足した行 15144 行**(触れた file 464 本) | **★0 件★** |

**⑴陽性対照** = 同じ検出子・同じ路へ贋の鍵二本を流し、**2 件鳴つた**(`aws_akid`・`kv_assign`)。
∴ 「0 件」は検出子が死んで居る故の 0 ではない。
**⑵根と深さ** = 根 `/Users/momizimac/multi-agent-shogun`、深さ = 幹の tree 全体(甲)と三点 patch の足した行(乙)。
**⑶rc** = ls-tree 0 / diff 0・0 / cat-file 落ち 2(2進・読めぬ分は数へて宣した)。
**⑷刻** = 2026-09-17T15:08:10+09:00。

### 甲の 6 件 ―― ★PR が足す物ではない★

| file | 幹が触れたか | blob 幹==origin/main |
|---|---|---|
| `SECURITY.md` | **否** | **★同★** |
| `tests/test_karo_second_send_iincho.bats` (4行) | **否** | **★同★** |
| `tests/unit/test_ntfy_auth.bats` | **否** | **★同★** |

**三本とも幹が触れて居らず、blob は origin/main と一字も違はぬ。**
∴ 当り 6 件は**既に origin/main に在る物**であり、本 PR が世に出す物ではない。

**値の素性**(値は一字も刷らぬ):

```
厳密形(sk-ant / jwt / gh_pat / aws_akid / slack / pem)の当り = ★0 件★
緩形  (鍵名 = 20字以上の字)             の当り = 6 件
```

6 件は悉く緩形のみ。**英大文字が 0 桁**であり、base64 の鍵や JWT の形を成さぬ。
∴ 「鍵の名を書いた行」であつて「鍵の形をした値」ではない。

## 五 ★數が何を意味せぬか★

1. **「464 file」は PR が世に出す file の総数ではない。** 幹の tree は 967 本。464 は「幹が基から変へた数」。
2. **「16 commit」は片側の数である。** 対称差は 37(基の側が 21)。**16 と 37 を混ぜるな。**
3. **464 は★三点(`...`)★で測つた。** 二点(`..`)なら **475** と出る ―― 分岐後に origin/main が動いた分を混ぜる故。
   裁326093①の「464file」と合ふのは三点の側である。
4. **secret 0 は「repo の歴史に secret が無い」の証ではない。** 測つたのは幹の tree と幹が足した行のみ。
5. **甲の 6 件を「贋」と断じて居らぬ。** 示したのは⑴幹が足して居らぬ事と⑵既知の鍵の形に当たらぬ事の二つのみ。
   **基 origin/main に既に在る物の是非は別件**として、本 PR とは切り離して上申する(§六-4)。

## 六 家老の申し條

1. **push は請ふのみ。** 押し並べて push は総監督の代行が正路ゆゑ、当席は commit までで止め、枝名と sha を告げる。
2. **rebase せず・squash せず。** 幹の 16 sha は他席が上に積んで居る(HEAD=`260f2a066007` は幹の 5 commit 先)。
   書き換へれば其の 5 本が宙に浮く。**merge commit 方式が正しい。**
3. **判定は軍師mac**(裁326093)。当席は判定せぬ。
4. **別件の上申**: `SECURITY.md:47` / `tests/unit/test_ntfy_auth.bats:50` 他 6 行は**既に origin/main に在る**。
   厳密形には当たらぬが、**「鍵名 = 長い字」の形で公に在る**事は事実である。本 PR の可否とは切り離し、
   **理事長専管(鍵・token)の筋**として別に裁を仰ぐ。当席は触れて居らぬ。
5. **幹が入つた後**: 甲10 を器の重なり 3 件の順で小 PR へ(裁326093②)。乙35 は理事長裁待ちのまま触れぬ(同③)。

## 七 ★裁 seq326145 への応へ★ ―― 紙を commit の中へ据ゑた

軍師mac 326139 の指摘は正しい。**紙が commit の外(untracked)に在れば、secret 0 は固定検証できぬ。**
以下、据ゑるに当つて起きた事を悉く書く。

### 七-1 何故 commit の外に在つたか ―― ★裸の `*` 一字★

| file | 遮断の則 |
|---|---|
| `README.md` | `.gitignore:18:!README.md` ―― **解かれて居る** |
| 残り 8 本(driver/・raw/・MANIFEST・門の控) | `.gitignore:7:*` ―― **遮断** |

`.gitignore` は 7 行目が裸の `*` の allowlist 形である。∴ **`git add <束>` では 9 本中 8 本が黙つて落ちる**。
落ちた事は rc にも出ぬ。ゆゑに plumbing(`hash-object -w` → `update-index --add`)で据ゑた。
遮断を書き換へては居らぬ(`.gitignore` 不触)。幹は既に `docs/evidence/` を **407 本**載せて居り、据ゑる事自体は先例に沿ふ。

### 七-2 ★器が己を撃つた★ ―― 厳密形 4 件

据ゑる前に束の全 byte を測つた所、**厳密形 4 件が鳴つた**。出所は悉く**検出子自身の字面**である:

- `driver/10_secret_kenzan.py` に `pem` / `ssh_priv` 2 件
- `driver/40_atarashii_atama.py` に同 2 件

PEM の冠は正規表現の中に**そのまま書けば本物の冠**であり、器が検体に成る。
治し = `-----` を **`[-]{5}`** と書く。正規表現としては寸分同じ物を指し、字面には検体が残らぬ。
同値は検で示した(`[-]{5}BEGIN OPENSSH PRIVATE KEY[-]{5}` が指す本物の冠 等 4 本の検体で旧新の当りが一致)。
**紙も同じ疵を踏み得る** ―― 此の節も一度は冠を字面で書いて鳴つた。紙の中でも冠は `[-]{5}` で書く。
`__pycache__` は旧字面を抱いて居た故、束から除いた(据ゑて居らぬ)。

> **∴ 此の疵は「secret が在つた」のではない。「secret を探す器が、己を数へて居た」のである。**
> 治した後の器で測り直した數は、刻を除き**前走と一字も違はぬ**(甲 6 / 乙 0 / 464 / 16 / 37 / 475 / 967)。

### 七-3 PR head ref の固定 と ★紙は己の sha を書けぬ★

- **此の紙が測つた頭** = `363d5fb060845171338c067ef42bfcbef8ad9188`(= 据ゑる commit の**親**)
- **此の紙を載せた commit の sha は、此の紙には書けぬ。** 書けば書いた事で sha が変はる。
  ∴ 新 sha は **push 願ひの便(pc_handshake)に書く**。

### 七-4 据ゑれば母數が変はる ―― 束の全 byte も測つた

据ゑれば束の file は悉く「PR が足す行」に成る。∴ 乙の母數は束の分だけ増える。両方測つた:

| 母數 | 中身 | 当り |
|---|---|---|
| 乙(足した行) | 15144 行 / 触れた file 464 本 | **0 件** |
| 束(全 byte) | 11 本 / 読めぬ 0 / 測つた 11 | **0 件** |
| ⑴陽性対照 | 測る路に乗せた合成 2 件 | **2 件 鳴**(検出子は生きて居る) |

器 = `driver/40_atarashii_atama.py`(rc=0)、控 = `raw/40_atama.txt`。

### 七-5 ★本走の後に生れる物 = 残余★(軍師mac への一行)

`MANIFEST.txt` ・門の控 ・`raw/40_atama.txt` 自身は**本走の後に生れる**。
∴ 上表の束 11 本には入らぬ。**此の残余は、据ゑた後の頭を引数に渡して再走すれば悉く母數に入る**:

```
python3 -B docs/evidence/karo-mac-miki-push-negai-20260917/driver/40_atarashii_atama.py <新sha>
```

器は頭を `argv` から取る(焼き込んで居らぬ)。rc=0 が 0 件、rc=1 が当り有り、rc=2 が使ひ方の誤り。

### 七-6 共有の器に触れて居らぬ証

当席の worktree は**他席と共有**であり、HEAD は `ashigaru-mac-3/km-51-…`(幹の 5 commit 先)、
共有 index には他席の **959 本**が staged で載つて居る。
∴ `git add` / `git commit` は使はず、**`GIT_INDEX_FILE` で別の index を建てて**据ゑた。
共有 index の 959 本は**一本も動いて居らぬ**(据ゑる前後で計測)。`refs/heads/main` も `363d5fb0` に据ゑ置き、
**進めたのは PR 枝 `karo-mac/km-gate-kou-otsu-20260917` 一本のみ**である。

### 七-7 前便との差 ―― ★超えられた數★

前便 seq326120 で告げた `README.md sha=d58ffa6e…` ・ `MANIFEST sha=045f0142…` ・門の控 `…T151122.log` は、
**本 REVISE で超えられた**(節七を継ぎ、器 2 本を治し、器 1 本と控 1 本を足した故)。
新しい値は本束の `MANIFEST.txt` と新しい門の控に在る。**古い sha で照合するな。**
