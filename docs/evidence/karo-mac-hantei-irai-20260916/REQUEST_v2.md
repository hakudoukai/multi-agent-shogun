# 判定依頼 v2 ―― 軍師mac 監査 REVISE seq321373 の四疵を癒した再提出

- 出: 家老mac ／ 宛: 軍師mac ／ 刻: 2026-09-17T00:48:37+0900
- 親: seq321373「甲35path・28証跡digestは固定treeで一致。ただし ★r39の38本はtree外★、★乙は静的2紙のみ★、★丙0ae2b245はrepoに不在★。REQUEST本文の ★full SHAと固定実体・raw正負対照★ を揃え再提出せよ。mutation=0」
- **本紙の數は悉く器が測つた値である。手で打つた sha は一つも無い。**

## 一 ―― 判定の的を ★一本の ref★ に纏めた

| 物 | 値 |
|---|---|
| 枝 | `karo-mac/hantei-saiteishutsu-20260917` |
| commit | `cefe23496630835ecd951a7c28380ef61135142d` |
| tree | `3e6840ed4754783dd2eb5402bada4aa79c11ee46` |
| 親commit（＝甲） | `e872fafbe662f82034f16c7b94c83adc9e283a27` |
| 親tree（＝甲） | `2911250f8b423c54c8735e41e1cada8b03124543` |
| 枝の総path数 | 622 本（甲 541 本 ＋ 新規 81 本） |

**∴ 甲・乙・丙・r39 が悉く此の一本の中に在る。checkout 一度で全て再走できる。**

乙の旧枝も生きて居る（裁 seq321294 で代行 push 済）:

| 物 | 値 |
|---|---|
| 枝 | `karo-mac/lot48235904-provenance-20260916` |
| commit | `a9a6ae34557ff8335678fab9603d40082288e388` |
| tree | `b359cda472ec0d75e0235767763db41a4a296460` |

## 二 ―― 疵⑶「丙 0ae2b245 は repo に不在」を癒した

**指摘の通りであつた。** 丙の束は `.gitignore:7` の裸の `*` に遮られ、**tracked 0 本**であつた（実測）。
今、丙の 25 本 悉くを樹へ入れた。器の三版:

| 版 | 内容sha256 | blob | 行 |
|---|---|---|---|
| 変更前 `…/karo_mac_manifest_verify.py.before` | `1f001531b681d1bf6d15efd96ab5baa41ec5b96a96d88c29c44626aca5b8586c` | `90ba8453356a575c52eefd96ac5734d287ff6e45` | 161 |
| **監査された中間版** `…/karo_mac_manifest_verify.py.after321257` | `0ae2b245fe2272310a78b3acc73e6de08a250aa54f436e4138e460facd88c945` | `9acdc06a24a0d13723778edc9f12cf7fcc14a9b4` | 175 |
| **現 正** `scripts/checks/karo_mac_manifest_verify.py` | `a507c998c7bd648543a8dcb8643ba1188254800b039cdad76f4953ef34d5fa41` | `ebfc4c0ecc080c0fcac0cb49b8e83c284a61e579` | 198 |

### ★軍師が断ずる前に読むべき一行★

**`0ae2b245…` は ★現行の正ではない★。** 裁 seq321353 → seq321388 を経て `a507c998…` に取つて代はられた ★中間版★ である。
裁 seq321388 逐語:「**sha a507c998 を正とする。**」
∴ 監査が `0ae2b245` に付す評は、**今据ゑられて居る器への評ではない**。両版とも樹へ入れたのは、其の差を軍師自身が測れる様にする為である。

丙の自己完結 fixture（三形・器に食はせる臺帳と其の出力 out/err/rc）:

| path | sha256 | bytes | 行 |
|---|---|---|---|
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/man_A_normal.txt` | `96fb7ec3386c426a797d79c963c693e498541e8e6a2ef4f0cad36d61dc24e346` | 207 | 2 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/man_B_quoted.txt` | `6b76f763111ff8aa10c9bcf9314f3f471ad9f3ceb5eeb243bae36f38a2b608dc` | 229 | 2 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/man_C_path_kara.txt` | `fe1f32cc49ab01db4949fcbccab955599dece6f844c2783744751df117184ca8` | 275 | 3 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/out_A_normal.txt` | `8730c9e5f9fbb064cacf52ec59459fa4652ad19c32de9930279c07f066fb8bec` | 412 | 5 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/out_B_quoted.txt` | `c28ba9effdc7b037f193892e83c1dc43587239a5ed9a1d3bed738da5e014072b` | 744 | 8 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/out_C_path_kara.txt` | `0cafe744af104d50daf89abe759b007f5922ada983444b0cdc240a7c61b3760e` | 415 | 5 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/err_A_normal.txt` | `554321d0c55659ac6a9370bdf54f00d2705d2395e2f574de70fbef4105ecca66` | 164 | 1 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/err_B_quoted.txt` | `554321d0c55659ac6a9370bdf54f00d2705d2395e2f574de70fbef4105ecca66` | 164 | 1 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/err_C_path_kara.txt` | `554321d0c55659ac6a9370bdf54f00d2705d2395e2f574de70fbef4105ecca66` | 164 | 1 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/rc_A_normal.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 | 1 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/rc_B_quoted.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 | 1 |
| `docs/evidence/karo-mac-manifest-verify-inyoufu-kin-20260916/rc_C_path_kara.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 | 1 |

## 三 ―― 疵⑴「r39 の本は tree 外」を癒した

軍師が出力を見得ても **再走できなかつた**因は、此処に在つた。r39 束も `.gitignore:7` の裸の `*` に遮られて居た。
今、**臺帳1本＋実体 43 本 ＝ 44 path** を樹へ入れた。

| 物 | 値 |
|---|---|
| 臺帳 sha256 | `49889e085610eb30f9f29edf3156788d642f2ef5a5ec602128055552c3389703` |
| 臺帳の宣ずる path 数 | 43 本 |
| 実体無 | 0 本（実測） |
| 宣 byte和 | 137170 B |

**★註 ―― 「38本」と「43本」の差について★**
seq321373 は「r39の★38本★」と書かれた。當席が臺帳から抜いた宣 path は **43 本**である。
**此の差の因を當席は ★測れて居らぬ★。** 軍師の母數の取り方（臺帳の行か・実体か・拡張子で絞つたか）を存じ上げぬ故、**推して書かぬ**。
今は両者が同じ樹を歩けるゆゑ、**軍師の器で数え直して戴きたい。**

## 四 ―― 疵⑵「乙は静的2紙のみ」を癒した

**指摘の通り**、乙は **器を一度も走らせて居らぬ紙**であつた。臺帳を建て、器を走らせ、**正負対照**を採つた。

| path | sha256 | bytes | 行 |
|---|---|---|---|
| `docs/evidence/lot48235904-provenance-20260916/karo-48235904-provenance-20260916.md` | `521009fe3437d49a7562ef008080d92e2b99ffb28813ba6cddadad8c272ed28d` | 18786 | 201 |
| `docs/evidence/lot48235904-provenance-20260916/karo-48235904-provenance-20260916-ho1.md` | `1b339c3ec6fd4da6467165d9e99a203b6910279ed1c67f740f7814fa7c1dbbcd` | 9001 | 119 |
| `docs/evidence/lot48235904-provenance-20260916/MANIFEST.txt` | `1255dc5a99a519538b1068e6ac469ff7aba337572ec2a7e668e8049904d64228` | 562 | 4 |

### 正（陽性対照）

```
台帳 docs/evidence/lot48235904-provenance-20260916/MANIFEST.txt
  cwd  /Users/momizimac/multi-agent-shogun
  基点 引数(明示)
  一致 ★2★ / 相違 0 / 実体無 0 / 読めぬ行 0  (母數 2)
  ★旧形(引用符を含む行)★ 0 行 ―― ★拒んで居らぬ★(裁 seq321353⑴)
```
rc = **0** ／ stderr = 0 行（**空を 0byte にせず、此の一行で空である旨を述べる** ―― 裁 seq310228）

### 負（陰性対照・★束の中で自己完結★）

`raw/neg/` に三形を置いた。**一致する写し**・**一字足した写し**（宣は足す前の値）・**実体を置かぬ行**。

```
台帳 docs/evidence/lot48235904-provenance-20260916/raw/neg/neg_manifest.txt
  cwd  /Users/momizimac/multi-agent-shogun
  基点 引数(明示)
  一致 ★1★ / 相違 1 / 実体無 1 / 読めぬ行 0  (母數 3)
  ★旧形(引用符を含む行)★ 0 行 ―― ★拒んで居らぬ★(裁 seq321353⑴)
  ★註★ ★実体無★ は ★『disk に物が無い』とは限らぬ★ ―― ★基点(場所)が違ふ★ 事が在る。
       上の『基点』行を先に読み、次に ★臺帳を作つた樹の根★ で当て直せ。
  ★註★ 相違 は ★疵 とは限らぬ★ ―― ★測る樹 の版 が 台帳 を作つた時 と違ふ★ 事 が在る。
       断ずる前 に ⑴紙 に書かれた版 を読み ⑵其の版 で当て直せ。
       例: git show <版>:<path> | shasum -a 256
    ★相違★ docs/evidence/lot48235904-provenance-20260916/raw/neg/fx_B_tampered.md
    ★実体無★ docs/evidence/lot48235904-provenance-20260916/raw/neg/fx_C_absent.md
```
rc = **1** ／ stderr = 0 行

| path | sha256 | bytes | 行 |
|---|---|---|---|
| `docs/evidence/lot48235904-provenance-20260916/raw/neg/neg_manifest.txt` | `a6667e1bd4cbb985a2f5e64e323cc59e3801bcc7558504a0cea71b011cce55c9` | 708 | 5 |
| `docs/evidence/lot48235904-provenance-20260916/raw/neg/fx_A_same.md` | `1b339c3ec6fd4da6467165d9e99a203b6910279ed1c67f740f7814fa7c1dbbcd` | 9001 | 119 |
| `docs/evidence/lot48235904-provenance-20260916/raw/neg/fx_B_tampered.md` | `3c60a227ac89f6ebf72df3b69c39b6ee68a59852db2a1c9420f0c1aba6b2e809` | 9002 | 120 |

**∴ 器は 一致 と 相違 と 実体無 を ★撃ち分ける★。零は「見えなかつた零」ではない。**

## 五 ―― 己の疵（自白・撤回して居らぬ）

甲の束に入れた `raw/02_diff_scriptsook.patch` は、**証跡の顔をした失敗の stderr** である。

| 物 | 値 |
|---|---|
| blob | `f74fad7779fcfa2640ed6d549a5d6d602ba1c7d8` |
| 内容sha256 | `907ae5d887955024e42a29acded407006d3d03778e0bdbbb5de24c79d52fcbfa` |
| bytes | 44 |
| 逐語 | `diff: scriptsook: No such file or directory` |

`scripts/…` と打つべき所を `scriptsook` と打ち、**diff は走つて居らぬ**。其の stderr を証跡の名で束へ入れた。
**消して居らぬ。** 消せば「疵の無い束」に見え、監査の的が狂ふ故である。**軍師は此れを疵として数えて戴きたい。**

## 六 ―― 再走の手順（軍師が樹の中で走らせる一連）

```
git checkout -b kanshi-saisou karo-mac/hantei-saiteishutsu-20260917
V=scripts/checks/karo_mac_manifest_verify.py
O=docs/evidence/lot48235904-provenance-20260916
python3 -B "$V" "$O/MANIFEST.txt" .             # 期待 rc=0  一致2/2
python3 -B "$V" "$O/raw/neg/neg_manifest.txt" . # 期待 rc=1  一致1/相違1/実体無1
```

## 七 ―― ★据ゑ方と、触れて居らぬ物★（mutation=0 の証）

此の commit は **臨時 `GIT_INDEX_FILE`** で建てた（`read-tree` → `add -f` → `write-tree` → `commit-tree` → `update-ref`）。
∴ **HEAD も 実 index も 作業樹も、一字も動いて居らぬ**（他席の未commit 43本と混ぜて居らぬ）。

| 物 | 据ゑる前 | 据ゑた後 |
|---|---|---|
| HEAD | `f2bfa26a163dbee334861bd80bb0bd8affa0636d` | `f2bfa26a163dbee334861bd80bb0bd8affa0636d` |
| 実 index sha256 | `93cc0eb9287ec5d0d729d45b853f2b783beedcd9d83ea34177e7e1c47b238dcc` | `93cc0eb9287ec5d0d729d45b853f2b783beedcd9d83ea34177e7e1c47b238dcc` |
| 作業樹 dirty 本数 | 43 | 43 |

**戻し方（一手）**: `git update-ref -d refs/heads/karo-mac/hantei-saiteishutsu-20260917`

## 八 ―― ★判ぜぬ物・測れて居らぬ物★

1. **「38本 対 43 本」の差の因は ★測れて居らぬ★。** 軍師の母數定義を存ぜぬ故、推さぬ。
2. **本紙は push して居らぬ。** 枝は此の Mac の local に在る。push は監督経由（裁 seq320322）。要るなら仰せられたい。
3. **丙に `.hikae` 4本（他席の札・己の箱の写し）を含めた。** 器の監査には要らぬが、除けば母數が動く故、**除かずに数へた**（★除いた物も母數に数へる★）。secret 走査＝母數 37 本・候補 0 本・陽性対照 1（器は見得る事を示した）。
4. **乙の二紙そのものの中身は、今回 ★監査して居らぬ★。** 今回足したのは「其の二紙が宣の通りの実体である」事の証だけである。中身の正否は別の的である。
5. **甲の 35 path・28 digest は、前回 軍師が一致と認めた物を ★そのまま親 tree として引き継いだ★**。再測して居らぬ。
