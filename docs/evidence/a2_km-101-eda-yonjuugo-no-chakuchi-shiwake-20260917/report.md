★門 rc=0 / 母數 36 / 條① 一致 36・相違 0・実体無 0・読めぬ行 0★(控 `_gate/` の★最も新しい `92_gate_*`★・`KM_GATE_MANIFEST_BASE=.`・臺帳=束内相対)

# 第44弾 「枝45本の着地仕分け ―― karo-mac 前半13本」 ―― ★甲13 / 乙0 / 丙0★

★臺帳の基点★: 本束の `_manifest.txt` の `path=` は ★本束の根(docs/evidence/a2_km-101-eda-yonjuugo-no-chakuchi-shiwake-20260917/)からの相対★ である(新法・總監督裁 seq322699)。

- 席: ashigaru-mac-2(專任2) / 札: `queue/tasks/ashigaru-mac-2.yaml`(写し=`raw/00_fuda.yaml`)
- 受: `msg_20260917_145021_c8814e56`(家老mac 14:50:21)
- 親裁: 委員長裁 seq325884(親 325872) ―― ★枝は一本も消さぬ★(不可逆削除は理事長専管)
- 測つた刻: 2026-09-17 14:53〜15:0x(JST) / 基点 main = `4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1`
- ★禁の順守★: checkout / merge / rebase / cherry-pick / push / fetch / refs 書換 ―― ★一度も打つて居らぬ★。
  用ひた git は `cat-file -e` `rev-parse` `diff` `rev-list` `merge-base --is-ancestor` `show` `ls-tree` `for-each-ref` `ls-remote` のみ(悉く読取)。
  `ls-remote` は ★ref を一本も書かぬ★ ―― 打つ前 `for-each-ref | wc -l`=88、打つた後も ★88★(本紙 七節)。

## 一、結論 ―― ★13本悉く「着地させる(甲)」。而して単独では出せぬ★

| 出目 | 数 | 中身 |
|---|---|---|
| ★甲(着地させる=PR)★ | ★13★ | 悉く鎖の末端。呑む tip 0 本。自前 11〜633 file を持つ |
| 乙(捨てる=裁を待つ) | ★0★ | ⑵=0 の枝も、他 tip に呑まれた枝も一本も無かつた |
| 丙(測れぬ) | ★0★ | 13本とも `cat-file -e` rc=0、祖先 tip も 5〜14 本在り ⑵ が測れた |

★而して「甲＝今すぐ PR を起こせる」では無い。★13本とも ★基準枝が割当の外に在る★ ゆゑ、
★先に基準枝が着かねば、PR は自前 11〜633 file ではなく ★484〜637 file★ を担いで出る事に成る(四節)。

## 二、㋐ 母數 ―― ★13/13 手許に物在り★

`ki/10_bosuu.py` → `raw/10_bosuu_warimochi.tsv` / `raw/10_bosuu_mac60.tsv` / `raw/10_bosuu_koku.txt`。
割当は ★札の `eda_warimochi` から機械で読んだ★(手で打ち直して居らぬ・40桁hex と2語を assert)。

- 割当 = ★13 本★、`git cat-file -e <sha>^{commit}` ★rc=0 が 13/13★(欠 0)。
- origin の mac 枝 = ★60 本★(`raw/00_lsremote.txt` が生の写し)、★相異なる sha は 59★
  ―― 同 sha の対 = `karo-mac/gate5-20260909` / `karo-mac/gate5-note-20260909`(`e8470d8c4536…`)。
- 60 本とも手許に物在り(rc=0)。∴ 60 本総当りの祖先判定を ★取りこぼし無く★ 出来た。
- ★親の申し立てを己の器で検め直した★(`ki/15_torikomi.py`): main に取り込まれて居る mac 枝 = ★1 本★
  (`karo-mac/skills-tools-20260908b`)。「1/60」は ★受け売りでなく実測で一致★。

## 三、㋑ 二つの差分 ―― ★⑴は自前の 4.3 倍。混ぜれば其れ自体が疵★

`ki/20_sashi.py` → `raw/20_sashi.tsv`(生の数) / `raw/20_sosen.tsv`(祖先 tip の全列挙)。

| 枝(karo-mac/ を略す) | ⑴対main | ⑵自前 | ⑵の基準枝B | B迄 | commit | 領域⑵ |
|---|---|---|---|---|---|---|
| a1-r56 | 635 | ★633★ | manifest-verify-20260909 | 7 | 11 | docs,scripts |
| daiko-teishutsu-20260916 | 5 | ★3★ | manifest-verify-20260909 | 3 | 7 | docs,scripts |
| hantei-saiteishutsu-20260917 | 121 | ★84★ | gate-hook-fix-20260916 | 2 | 9 | docs,queue,scripts |
| km-52-shikii-no-bosuu-wo-kakutei-seyo | 526 | ★62★ | km-gate-kou-otsu-20260917 | 1 | 17 | docs |
| km-53-hitotsu-no-aruki-ne-de-file-suu-wo-soroe | 510 | ★46★ | km-gate-kou-otsu-20260917 | 1 | 17 | docs |
| km-54-naoshi-wo-sue-kadobikae-wo-ingai-e | 519 | ★55★ | km-gate-kou-otsu-20260917 | 1 | 17 | docs |
| km-55-hikae-wo-sahou-e-byte-giri-wo-sagasu | 562 | ★98★ | km-gate-kou-otsu-20260917 | 1 | 17 | docs |
| km-73-mieru-shirushi-ga-hiraku-ana | 637 | ★173★ | km-gate-kou-otsu-20260917 | 1 | 17 | docs |
| km-74-shirushi-no-kawashimo-wo-hakare | 505 | ★41★ | km-gate-kou-otsu-20260917 | 1 | 17 | docs |
| km-76-repogai-no-ichikasho-wo-nushi-he-watasu | 552 | ★11★ | km-75-shikii-no-nokori-hitotsu-wo-tojiru | 1 | 22 | docs |
| km-77-shikii-no-bosuu-wo-yotsu-no-teigi-de-kakutei | 522 | ★58★ | km-gate-kou-otsu-20260917 | 1 | 17 | docs |
| km-78-bannin-naki-kuchi-ga-honto-ni-hiraku-ka | 612 | ★148★ | km-gate-kou-otsu-20260917 | 1 | 17 | docs |
| km-79-futatsu-no-mon-he-otsu-wo-ateru | 484 | ★22★ | km-gate-kou-otsu-20260917 | 1 | 17 | docs,scripts |
| ★総和★ | ★6190★ | ★1434★ | ―― | ―― | ―― | ―― |

### ★數が何を意味せぬか(数の規律3)★

1. ★⑴は「此の枝が変へた file 数」では無い。★ `merge-base(main,X)..X` ゆゑ、
   ★祖先枝から受け継いだ分を悉く含む★ ―― ★main が此の枝から何 file 遅れて居るか★の数である。
   実際、13本の ⑴ の総和 6190 に対し自前 ⑵ の総和は 1434 ―― ★4.3 倍が「他人の仕事」である★。
2. ★⑵は「此の枝の値打ち」では無い。★ ★直近の祖先 tip から見た差★に過ぎず、其の祖先が着地せねば意味を成さぬ。
3. ★commit 数は file 数と揃はぬ。★ km-52〜km-79 は commit 17 本でも自前 file は 22〜173 と散る。
4. ★⑴ の内訳は追加が殆どである(`raw/40_status.tsv`)★ ―― 改変(M)は 1〜7 file、削除(D)・改名(R)は ★13本とも 0★。
5. ★同点の断り★: `rev-list --count B..X` が最小の B は ★13本とも 1 本きり(同点 0)★ ゆゑ、
   「辞書順で選んだ」が効いた枝は ★一本も無い★(恣意の入る余地が無かつた)。
6. ★名の断り★: file 数は `-z`(NUL 区切り)で数へた。素の行数とも突き合はせ、★13本とも一致★
   (改行を含む名は無かつた ―― 之は「無い事を測つた」のであつて「見なかつた」のではない)。

## 四、㋒㋓ 仕分け ―― ★拠り所を先に宣し、其の儘機械で当てた★

拠り所(`ki/40_shiwake.py` の冒頭に逐語で据ゑ、其の文字列の儘 if で当てて居る):

```
丙(測れぬ) = ①手許に物が無い(cat-file rc≠0) または ②祖先 tip 0 本で ⑵ が測れぬ。
乙(捨てる=PR を起こさず理事長裁を待つ) = ①⑵=0 file(自前の中身が無い) または
                                         ②tip が他の mac tip の真の祖先(他枝が悉く含む)。
甲(着地させる=PR) = 丙でも乙でも無い物。
★乙は「消す」に非ず★ ―― 裁 325884 により不可逆削除は理事長専管。乙 = ★PR を起こさず裁を待つ★。
```

出目 = ★甲13 / 乙0 / 丙0★(`raw/40_shiwake.tsv` に一行づつ理由付き)。
乙が 0 に成つたのは ★13本が悉く鎖の末端だつたから★ である(六節) ―― 既に名指された「不要15本」が
先に除かれて居た結果であり、★此の13本を選んだ側が正しく選んで居た★事の裏書きでもある。

### ★丙が 0 でも「測れぬ」が無かつた訳では無い★

㋔の内 ★「門 rc=0 か」は此の席では真には測れぬ★(五節末)。丙の欄に上げなかつたのは、
丙が ★枝の仕分け★の出目であり、受入条件の測り残しは別欄だからである ―― 混ぜて 0 と書けば偽りに成る。

## 五、㋔ 受入条件 ―― ★甲13本に共通の三つ + 各個★

`ki/50_ukeire.py` → `raw/50_ukeire.tsv` / `raw/50_daichou_gyou.tsv`(`git show` の読取のみ・checkout せず)。

### 共通(13本とも満たさねば通せぬ)

- ★受① 基準枝が先に着く事★ ―― 13本とも基準枝Bが ★割当13本の外★ に在る(`raw/60_jun.tsv`)。
  B=`km-gate-kou-otsu-20260917` に ★9 本★、`manifest-verify-20260909` に 2 本、
  `gate-hook-fix-20260916` に 1 本、`km-75-…-tojiru` に 1 本が乗る。
  ★B が着けば PR は 11〜633 file。着かねば 484〜637 file を担ぐ。★
- ★受② main 側との重なりを手で解く事★(`raw/46_main_gawa.tsv`)。
  13本は ★merge-base が悉く同一★(`6e9d40600a801aa713ac238e2e62bbae06c9e683`)。
  main は其処から ★14 file★ 動いて居り、各枝との交はりは ★2〜3 file★、
  内 ★blob が異なる(手で解く要り)のは 1〜2 file★ ―― 実体は `.gitignore` と
  `scripts/checks/karo_mac_manifest_verify.py`、km-76 のみ `scripts/inbox_watcher.sh` を加へる。
  ★之は小さい。13本の着地を阻む壁では無い。★
- ★受③ 臺帳が束内相対である事★ ―― 自前差分に臺帳を含む枝は ★7 本★、
  内 ★束内相対 6 本★(km-52 / km-53 / km-54 / km-55 / km-76 / km-79)、
  ★旧形(docs/ 起し) 1 本 = `hantei-saiteishutsu-20260917`★(★之のみ直しが要る★)。
  残 ★6 本★ は臺帳を ★一本も commit して居らぬ★ ―― 疵では無く、`.gitignore` 7 行目の allowlist(`*`)が
  `_manifest.txt` を弾いて居る為である(`git check-ignore -v` で実測)。∴ ★「臺帳が無い」ではなく「追跡外」★。

### 各個(`raw/50_ukeire.tsv` の生の数)

| 枝(略) | 自前file | 臺帳 | 束内相対 | 旧形 | 門控.rc | rc=0 | rc≠0 | 対照らしき紙 |
|---|---|---|---|---|---|---|---|---|
| a1-r56 | 633 | 0 | 0 | 0 | 102 | 88 | ★14★ | 85 |
| daiko-teishutsu | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hantei-saiteishutsu | 84 | 1 | 0 | ★1★ | 2 | 1 | ★1★ | 0 |
| km-52 | 62 | 1 | 1 | 0 | 1 | 1 | 0 | 0 |
| km-53 | 46 | 1 | 1 | 0 | 1 | 1 | 0 | 0 |
| km-54 | 55 | 1 | 1 | 0 | 2 | 2 | 0 | 0 |
| km-55 | 98 | 1 | 1 | 0 | 17 | 1 | ★16★ | 0 |
| km-73 | 173 | 0 | 0 | 0 | 19 | 12 | ★7★ | 9 |
| km-74 | 41 | 0 | 0 | 0 | 4 | 3 | ★1★ | 3 |
| km-76 | 11 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| km-77 | 58 | 0 | 0 | 0 | 5 | 3 | ★2★ | 3 |
| km-78 | 148 | 0 | 0 | 0 | 9 | 7 | ★2★ | 0 |
| km-79 | 22 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |

### ★rc≠0 の控を「落ちた」と読むな ―― 此の器では分けられぬ★

rc≠0 の控は計 43 本在るが、★其の多くは意図した陽性対照(鳴らねば器でない)の控である★。
本器は ★rc の数を読むだけ★ で、陽性対照か本番の落ちかを ★分けられぬ★。
∴ ★「門 rc=0 か」は此の席では未測である★ ―― checkout 無しに其の枝の上で門を走らせる術が無い。
判ずるには ★其の枝を出す席が己の束で門を通し直す★ か、監督 lot が work tree を別に立てる要り。
★之を「PASS」と書けば偽りに成るゆゑ、未測と書く。★

## 六、㋕ 重なり ―― ★鎖は 0 本。13本は互ひに独立★

`ki/30_kasanari.py` → `raw/30_uchi_pairs.tsv` / `raw/30_soto_nomikomi.tsv` / `raw/30_kusari.txt`。
★真の祖先★の定義: `merge-base --is-ancestor A B` rc=0 ★かつ sha(A)≠sha(B)★
(is-ancestor は A=B でも rc=0 ゆゑ、此の但書を落とせば全枝が己の祖先に成る)。

- 割当13本の内、tip が他の tip の祖先に成つて居る対 = ★0 対★。
- 60本まで広げても、割当13本を ★呑む tip は一本も無い★(13本とも 0 本)。
- ∴ ★鎖は一本も描けぬ。「末端のみ着地させれば足りるか」の問は、13本とも己が末端ゆゑ★
  ★「13本悉く要る」が答である。★一本でも落とせば其の自前 11〜633 file は何処にも残らぬ。

### 衝突 ―― ★78 対中、真の衝突は 0★

`ki/45_shoutotsu_blob.py` → `raw/45_shoutotsu_shin.tsv`。
素朴に「同じ file を改変した対」を数へると ★78/78 対★ が当たる(`raw/40_shoutotsu_M.tsv`)。
★而して其の儘では衝突の数では無い。★ 同じ path でも ★blob が同一★ なら共通祖先から受け継いだ儘で、
併せても衝突せぬ。blob で検め直すと ―― ★blob が相異なる対 = 0★。
実際 13本の `.gitignore` の blob は ★悉く `3f066ffda9f41ed9139e61a37278d05fb1ba6c9e`★ の一つきり。
∴ ★13本は互ひに衝突せぬ。順序さへ決まれば並べて着地させられる。★

## 七、禁の順守を物で示す

- `for-each-ref | wc -l` = ★88★(`ls-remote` の前) → ★88★(後)。★ref を一本も書いて居らぬ。★
- 枝は ★一本も消して居らぬ★(削除の口を打つて居らぬ)。work tree も触れて居らぬ
  ―― 差分は悉く ref 同士(`A...B` / `A..B`)で取り、`git show` で blob を読んだだけである。
- PR は ★一件も起票して居らぬ★(起票は監督 lot・判定は軍師mac)。他席の pane も覗いて居らぬ。

## 九、門控・臺帳・臺帳外(何を数へ、何を数へて居らぬか)

- 門 = `scripts/checks/karo_mac_dasumae_gate.sh`、`KM_GATE_MANIFEST_BASE=.`(★束内相対の臺帳ゆゑ、
  之を渡さねば條①は既定基点=repo 根で照合し、36 本悉く「実体無」で落ちる★)。
- 本番控 = `_gate/` の ★最も新しい `92_gate_*.{out,err,rc}`★ ―― ★rc=0★。
  ★控の名を刻で固定せぬ★ ―― 紙を書き足せば紙の sha が変り臺帳と控を建て直す要りが生じ、
  刻を焼けば其の一行が必ず古びる(★己を含む臺帳の數を紙は書けぬ★)。
  ∴ 名では無く ★規則★ で指す。数(rc=0 / 母數 36 / 條① 一致 36)は建て直しても動かぬ。
  條① 一致 36 / 相違 0 / 実体無 0 / 読めぬ行 0(母數 36)・旧形(引用符を含む行) 0。
  條②③④ = 全 36 本通。條⑤ の byte和 は控に在り(閾 10485760 未満)。
  ★rc は pipe を通さず subprocess の returncode を直に書いた★(pipe 越しの `$?` は門の rc では無い)。
- ★陽性対照★ `_gate/92b_taishou_20260917T150832.*` ―― ★rc=1・條⑤「測れぬ」32 本鳴★。
  器(`ki/92b_taishou.py`)が ★態と★ 臺帳の行を丸ごと file 名として渡した物である。
  ∴ 本番の rc=0 は ★「鳴らぬ器で測つた 0」では無い★。
- ★己の疵を隠さぬ★: 最初の門(15:07:08)は ★己の器の疵で落ちた★ ―― 臺帳の四欄行を `ln[5:]` で切り、
  `raw/…tsv sha256=… bytes=… lines=…` を file 名として渡して居た。
  ★其の控は、臺帳を建てる前に己が消した★ ゆゑ物として残つて居らぬ。
  代りに ★同じ疵を器で再現した物★ が上の陽性対照である ―― ★復元では無く再現であると宣する。★
- ★臺帳外★(臺帳に載せて居らぬ物)= `_manifest.txt` 自身 と `_gate/` 配下の悉く。
  ★数を焼かぬ★ ―― 門を走らせる度に三本(out/err/rc)増えるゆゑ、焼いた数は必ず古びる。
  何が在るかは控の名(器名+刻)で辿れる: `92_gate_*`(本番)・`92b_taishou_*`(陽性対照)・
  `96_todoke_*`(納め便の届け控)。
  門控は ★臺帳を建てた後★ に生まれる物ゆゑ、臺帳に入れれば己を照合する輪に成り條①が必ず崩れる。
  `ki/91_daichou.py` は `_gate` と `__pycache__` を歩かぬ(逐語で器に書いた)。
  ★「除いた」は「歩いて居らぬ」の意であり、「無い」の意では無い。★
- 器は悉く `python3 -B` で走らせた(`__pycache__` を束に残さぬ為)。

## 十、納め便(家老mac 宛)

- 宛 = ★家老mac★。★軍師mac は死箱★(`inbox_write` が rc=68 で撥ねる)ゆゑ、監査は家老mac が代送する。
- 器 = `ki/95_bin.py`、胴 = `raw/95_bin.txt`(★送る物と同一の bytes★)。
- ★字数 = 265 字★(條 300)。★python3 の `len`(符号点)で測つた★ ――
  macOS の `awk length()` は byte を返すゆゑ用ゐて居らぬ(★字と byte は別の數である★)。
- 送つた後に ★箱の尾を読み返して★ 着いた事を検める(★送つた ≠ 届いた★)。
  届け控は臺帳を建てた後に生まれる物ゆゑ ★臺帳外★ に置き、其の旨を此処に宣する。


## 十一、★本束を commit して居らぬ ―― 其の理由を宣する★

- 今この工作樹が立つて居る枝は ★`ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917`★
  ―― ★他席(專任3)の枝★である(`git rev-parse --abbrev-ref HEAD` で読んだ)。
- 札の `kin` は ★「checkout / … / refs 書換 悉く禁 ―― 読取のみ」★ と据ゑて居る。
  commit は ★HEAD の ref を書く★ ゆゑ此の禁に当たり、且つ ★他席の枝を汚す★。
  枝を分けるには checkout が要り、其れも禁である。
- 加へて、本束は ★`.gitignore` 7 行目の allowlist(`*`)★ に当たり ★悉く追跡外★ である
  (`git check-ignore -v … report.md` → `.gitignore:7:*`)。
  載せるには `-f` か `.gitignore` の書換が要り、後者は ★変更統制(委員長許可)★ の案件である。
- ∴ ★本束は disk に在り、門を通つた状態で置く。★ commit は ★監督 lot / 家老mac の指図を待つ。★
  ★「commit して居らぬ」は「紙が無い」の意では無い。★ 束の在處 =
  `docs/evidence/a2_km-101-eda-yonjuugo-no-chakuchi-shiwake-20260917/`。


## 八、次に何を測れば判ずるか(丙は 0 でも残る問)

1. ★門 rc=0 の実測★ ―― 監督 lot が別 work tree を立て、各枝の束で `karo_mac_dasumae_gate.sh` を
   `KM_GATE_MANIFEST_BASE` 付きで走らせる。★此の席では checkout 禁ゆゑ打てぬ。★
2. ★基準枝4本(km-gate-kou-otsu / manifest-verify-20260909 / gate-hook-fix-20260916 / km-75)の仕分け★
   ―― 割当の外ゆゑ本席は触れぬ。★之が着かねば13本とも 500 file の PR に成る。★
3. `hantei-saiteishutsu-20260917` の旧形臺帳 1 本 ―― 束内相対へ直すのは ★其の枝の主★の仕事。
