# km-185 ―― ★五束を己の樹へ固定した★(専任2・裁332455／333060③／329271)

刻 = 2026-09-19T00:09:32+0900 ／ 席 = ashigaru-mac-2(専任2) ／ 親裁 = 332455・333060③・329271

## 〇 一行で

**追跡外であつた五束 314 本の紙に、己の樹で固定 commit を与へた。**
共用樹の HEAD・index・porcelain は ★前後で不動★。push は打たず、main には触れて居らぬ。

★當席が「commit を打てぬ」と断じた三因の内、二つは己の樹を切る事で消えた★ ――
⑴禁④(共用樹の HEAD・index) は ★己の樹なら動かぬ★ ⑵枝が他席の物 → ★己の枝を切つた★。
⑶`.gitignore:7` の裸の `*` は ★`git add -f` で名指せば越えられた★。
∴ ★解禁の令は要らなんだ。當席の断は誤りであつた。★

## ㋐ 三枝 ―― 悉く origin/main の固定 sha から切つた

切り元 = `6bde7170ce574090a6139ba2dfe3aa4cb6db8634`(裁333060③ 1弾1枝)

| ki | eda | oya_sha | kotei_sha | tree | file_hon | zougen | rc_add | rc_commit |
|---|---|---|---|---|---|---|---|---|
| a2-km171 | ashigaru-mac-2/km-171-uke-ire-no-jimen-20260918 | 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 | 4b21e86be32feedbbff1e23c65372a03a74efb10 | efe032725674b5d9a5e42186c5eca66b43ad77da | 191 | 191 files changed, 4412 insertions(+) | 0 | 0 |
| a2-km172 | ashigaru-mac-2/km-172-hako-no-utsushi-fail-open-20260918 | 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 | b6ff8a80dd91ba98197ed62d0661695de1bbb002 | c4459cfc27ce2f0c111bb167835942bfe3018792 | 71 | 71 files changed, 6497 insertions(+) | 0 | 0 |
| a2-km174 | ashigaru-mac-2/km-174-otona-ban-yoyaku-iriguchi-20260918 | 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 | 729f2cd7c458ff82637388c605936e8824812abd | 27b22f6265c5a84e667b695bae87f450b10a94e4 | 52 | 52 files changed, 1769 insertions(+) | 0 | 0 |

★固定 commit と tree の 40桁は上表の逐語★。彫りは `git add -f <path>` の後 `git commit --only <同じ path>`。
`reset` は打たず・`push` せず・`main` に触れず・`gh` を叩いて居らぬ(裁332449)。

## ㋑ 紙の數 ―― 家老の數と己の數

家老の宣: 59／71／61／71／52(計314)。★當席が己で歩き直した數も同じである(計314)。★
∴ ★差の一本も無い ―― 消して揃へた物は無い。★

| taba | kami_zen | pycache | kami_jo_pycache | byte_wa |
|---|---|---|---|---|
| docs/evidence/ashigaru-mac-2_km-171-ukeire-to-genbutsu-no-sa-wo-hakaru-403-ka-404-ka-20260918 | 59 | 0 | 59 | 137228 |
| docs/evidence/ashigaru-mac-2_km-171-uke-ire-no-jimen-wo-404-he-20260918 | 71 | 1 | 70 | 120595 |
| docs/evidence/ashigaru-mac-2_km-171-toi-heno-kotae-20260918 | 61 | 0 | 61 | 78361 |
| docs/evidence/ashigaru-mac-2_km-172-hako-no-utsushi-de-fail-open-wo-jissho-suru-20260918 | 71 | 0 | 71 | 448640 |
| docs/evidence/ashigaru-mac-2_km-174-otona-ban-yoyaku-iriguchi-ichi-oufuku-20260918 | 52 | 0 | 52 | 127478 |

★pycache の一本★: `…uke-ire-no-jimen-wo-404-he…` 束に `driver/__pycache__` が一本在る。
臺帳は之を除く方言(50 の歩きが `__pycache__` を落とす)ゆゑ ★臺帳 31 行 対 disk 71 本★ と成る。
★消さなかつた譯★ = ㋓「元の束は一指も触れるな」。★其の儘 commit に入れた(彫つた 71 本の内の一本)。★

## ㋒ 写しの證 ―― 母數と一致数を両方書く

```
★写しの〆★ 刻 = 2026-09-18T19:57:37+0900
★母數(控の行) = 314★
  ⑴宛に實體が在る  = 314 / 314
  ⑵bytes が等しい  = 314 / 314
  ⑶sha256 が等しい = 314 / 314
  ★悪い行 = 0 本★(raw/20_warui.tsv 逐語)
写し先: ashigaru-mac-2_km-171-toi-→~/wt/a2-km171 / ashigaru-mac-2_km-171-uke-→~/wt/a2-km171 / ashigaru-mac-2_km-171-ukei→~/wt/a2-km171 / ashigaru-mac-2_km-172-hako→~/wt/a2-km172 / ashigaru-mac-2_km-174-oton→~/wt/a2-km174
★此の數が意味せぬ事★: 一致 314/314 は ★写しが正しい★ の意のみ。
  ・★commit された事を意味せぬ★(30 の仕事・docs/evidence は .gitignore:7 の裸の `*` に落ちる故 add -f を要する)。
  ・★元の束が不動である事を意味せぬ★(之は 25 が共用樹の porcelain と控で別に測る)。
```

★三つを別々に数へた譯★: 一つに畳むと「宛に實體が無い」が「sha が違ふ」に紛れる。

## ㋓ 元の束と共用樹の不動

```
★共用樹と元束の不動 ―― 控=mae★ 刻 = 2026-09-18T20:11:26+0900
[元の束]
  母數(控の紙) = 314 ／ ★増えた = 0 ／ 消えた = 0 ／ 中身が動いた = 0★
  (束ごとの内訳 = raw/25_taba_mae.tsv 逐語)
[共用樹 /Users/momizimac/multi-agent-shogun]
  HEAD(40桁) = d8e3aa58b9eeac6f97f0d60928fbdc40c7c93f11  (rc=0)
  index = git ls-files -s の sha256 = 7425522328c8eca4efa6f25c0bc3657bdff208dea4331ab4200862eaaa562738  (rc=0・2789行)
  porcelain = ★1036 行★(rc=0・★stdout のみ★ ―― stderr の warning は数へて居らぬ)
    stderr(逐語) = warning: could not open directory 'queue/reports/ashigaru-mac-3_km-sakai-wa-dare-ga-hiku-noka_20260912_evidence/sakai/nanmon/n13_noaccess_dir/': Permission denied
  docs/runbooks の porcelain (rc=0) =
     M docs/runbooks/err-ekarte-001.md
★此の數が意味せぬ事★:
  ・増えた/消えた/動いた が悉く 0 は ★元の束を當席が触れて居らぬ★ の意。
    ★他席が触れて居らぬ事は之では言へぬ★(當席は他席の手を測れぬ)。
  ・porcelain の行数が前後で同じでも ★中身が同じとは限らぬ★ ∴ docs/runbooks の逐語を併せ採つた。
```

―― 彫つた後(控=ato)――

```
★共用樹と元束の不動 ―― 控=ato★ 刻 = 2026-09-18T20:15:02+0900
[元の束]
  母數(控の紙) = 314 ／ ★増えた = 0 ／ 消えた = 0 ／ 中身が動いた = 0★
  (束ごとの内訳 = raw/25_taba_ato.tsv 逐語)
[共用樹 /Users/momizimac/multi-agent-shogun]
  HEAD(40桁) = d8e3aa58b9eeac6f97f0d60928fbdc40c7c93f11  (rc=0)
  index = git ls-files -s の sha256 = 7425522328c8eca4efa6f25c0bc3657bdff208dea4331ab4200862eaaa562738  (rc=0・2789行)
  porcelain = ★1036 行★(rc=0・★stdout のみ★ ―― stderr の warning は数へて居らぬ)
    stderr(逐語) = warning: could not open directory 'queue/reports/ashigaru-mac-3_km-sakai-wa-dare-ga-hiku-noka_20260912_evidence/sakai/nanmon/n13_noaccess_dir/': Permission denied
  docs/runbooks の porcelain (rc=0) =
     M docs/runbooks/err-ekarte-001.md
★此の數が意味せぬ事★:
  ・増えた/消えた/動いた が悉く 0 は ★元の束を當席が触れて居らぬ★ の意。
    ★他席が触れて居らぬ事は之では言へぬ★(當席は他席の手を測れぬ)。
  ・porcelain の行数が前後で同じでも ★中身が同じとは限らぬ★ ∴ docs/runbooks の逐語を併せ採つた。
```

## ㋔㋕ 門 ―― 各束 二度・cwd=束・`KM_GATE_MANIFEST_BASE=.`

| soku | ki | kai | rc | watashita_path | byte_wa | narishi_jou |
|---|---|---|---|---|---|---|
| k171a | a2-km171 | ichi | 0 | 32 | 108094 | ― |
| k171a | a2-km171 | ni | 0 | 32 | 108094 | ― |
| k171b | a2-km171 | ichi | 1 | 31 | 68572 | ★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★ |
| k171b | a2-km171 | ni | 1 | 31 | 68572 | ★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★ |
| k171c | a2-km171 | ichi | 1 | 37 | 54028 | ★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★ |
| k171c | a2-km171 | ni | 1 | 37 | 54028 | ★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★ |
| k172 | a2-km172 | ichi | 1 | 36 | 420766 | ★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★ |
| k172 | a2-km172 | ni | 1 | 36 | 420766 | ★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★ |
| k174 | a2-km174 | ichi | 1 | 21 | 104232 | ★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★ |
| k174 | a2-km174 | ni | 1 | 21 | 104232 | ★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★ |

★二度の byte和★:

| soku | ichi_byte_wa | ni_byte_wa | onaji_ka |
|---|---|---|---|
| k171a | 108094 | 108094 | 同 |
| k171b | 68572 | 68572 | 同 |
| k171c | 54028 | 54028 | 同 |
| k172 | 420766 | 420766 | 同 |
| k174 | 104232 | 104232 | 同 |

### ★門が四束で rc=1 に成つた ―― 之は疵であり、隠さぬ★

落ちたのは ★悉く條①(臺帳と disk の差)★ である。條②③④⑤ は五束とも通つて居る。
鳴つた札は七本、逐語は下表:

| soku | rel_path | sen_bytes | disk_bytes | sen_sha16 | disk_sha16 | kata |
|---|---|---|---|---|---|---|
| k171b | raw/90_okuri.txt | 109 | 1089 | 2bcfe79b261e5610 | 55c0b3dd5836bcfa | bytes も sha も動いた |
| k171c | driver/60_daichougai.py | 6585 | 6869 | af48d70a8646219e | c2afb1eb40cba683 | bytes も sha も動いた |
| k171c | raw/90_okuri.txt | 1081 | 1631 | e415e1fc13cfaaa9 | ecb2059529723767 | bytes も sha も動いた |
| k171c | raw/95_yomikaeshi.tsv | 762 | 152 | d6661cd1571c7476 | 2e936e7e5144101f | bytes も sha も動いた |
| k172 | driver/60_daichougai.py | 4168 | 6398 | deffb30942719d8c | 093c2d7fab8d4fab | bytes も sha も動いた |
| k172 | raw/90_okuri.txt | 109 | 1418 | aeaf27f2bed45ddb | ac54663fa96151f0 | bytes も sha も動いた |
| k174 | driver/60_daichougai.py | 4199 | 4168 | 2fd6bccdbd721528 | deffb30942719d8c | bytes も sha も動いた |

★因★: 臺帳は ★建てた刻の disk★ を凍らせる。然るに其の後に
⑴`raw/90_okuri.txt` は便を出す度に追記され ⑵`raw/95_yomikaeshi.tsv` は読み返しで書かれ
⑶`driver/60_daichougai.py` は當席が己の疵を直して書き換へた(km-171-toi 束の oi4 便で申した通り)。
∴ ★臺帳を建てた後に動いた札である。★ 紙は己より後に生まれる物を書けぬ。

★直さなかつた譯★: 直すには臺帳を建て直す事に成り、之は ㋓「元の束は一指も触れるな」と
`evidence_bundle: 既に在る五束を其の儘固定する・新しい紙は作らず` に反する。
∴ ★食ひ違ひごと固定した。★ 固定した今、★誰でも同じ rc=1 を再現できる★(以前は disk が動く故 再現すら出来なんだ)。

★此の rc=1 が意味せぬ事★:
 ・★束の中身が誤りである事を意味せぬ★ ―― 條①は「臺帳の宣と今の disk の差」であり、中身の正否ではない。
 ・★彫りが失敗した事を意味せぬ★ ―― `git commit --only` の rc は五束とも 0、彫つた紙は disk と一本ずれず一致する(下表)。

## ㋕続 三つの數は同じ物ではない

| soku | daichou_gyou | hotta_kami | disk_kami | pycache | daichougai | daichou_ari_disk_nashi | soui | rc_lstree |
|---|---|---|---|---|---|---|---|---|
| k171a | 32 | 59 | 59 | 0 | 27 | 0 | 0 | 0 |
| k171b | 31 | 71 | 71 | 1 | 40 | 0 | 1 | 0 |
| k171c | 37 | 61 | 61 | 0 | 24 | 0 | 3 | 0 |
| k172 | 36 | 71 | 71 | 0 | 35 | 0 | 2 | 0 |
| k174 | 21 | 52 | 52 | 0 | 31 | 0 | 1 | 0 |

★臺帳の行 < 彫つた紙★ に成る理由は四つ ―― ⑴臺帳は己(`manifest.txt`)を含めぬ
⑵`mon_*`(門控)を除く ⑶`__pycache__` を除く ⑷臺帳を建てた後に生まれた紙は載らぬ。
彫りは disk を其の儘持つ故、★臺帳外も悉く commit に入る★。
`彫つた紙 == disk の紙` は五束とも成立(器が assert して居る)。

## ㋖ 未 push の證 ―― ★0 行では立たぬ★

各枝の `origin/main..<固定 sha>` の commit 数と、★陽性対照★ `git ls-remote origin refs/heads/main` の
行数を並べて `raw/30_shime.txt` に採つた。★遠方が引ける事を先に示さねば、0 は器の沈黙と區別が付かぬ。★

同じ器・同じ遠方で ★三役★ を当てた(`raw/32_mipush.tsv`):

| yaku | ref | rc | gyou | chikugo |
|---|---|---|---|---|
| 陽性対照 | refs/heads/main | 0 | 1 | 6bde7170ce574090a6139ba2dfe3aa4cb6db8634\trefs/heads/main |
| 己の枝 | refs/heads/ashigaru-mac-2/km-171-uke-ire-no-jimen-20260918 | 0 | 0 | ― |
| 己の枝 | refs/heads/ashigaru-mac-2/km-172-hako-no-utsushi-fail-open-20260918 | 0 | 0 | ― |
| 己の枝 | refs/heads/ashigaru-mac-2/km-174-otona-ban-yoyaku-iriguchi-20260918 | 0 | 0 | ― |
| 負の対照 | refs/heads/ashigaru-mac-2/kore-wa-arienu-eda-20260918 | 0 | 0 | ― |

```
★未 push の證★ 刻 = 2026-09-18T20:16:49+0900
器 = git -C ~/wt/a2-km171 ls-remote origin <ref>(同じ器・同じ遠方で三役を当てた)
  ⑴陽性対照 refs/heads/main      = ★1 行★ ―― 器は生きて居り、遠方は引ける
  ⑵己の三枝                      = ★悉く 0 行★ ―― 遠方に無い(= push して居らぬ)
  ⑶負の対照 在り得ぬ枝名          = ★0 行★ ―― 器は「無い物」に 0 を返すと確かめた
★此の三つを並べねば 0 は證に成らぬ★(0 対 0 は器の沈黙と區別が付かぬ)。
★此の數が意味せぬ事★: ★今 遠方に無い★ の意であり、★誰かが後で push せぬ事を意味せぬ★。
逐語 = raw/32_mipush.tsv
```

## ★測れぬ物★

 ・★他席が元の束に触れて居らぬ事★ は當席には測れぬ。上の「不動」は ★當席が触れて居らぬ★ の意である。
 ・★此の三枝が後で push されぬ事★ は測れぬ。測つたのは「★今★ 遠方に無い」までである。
 ・★門の rc=1 が委員長・軍師の目に何と映るか★ は當席の断ずる所ではない ―― 事実のみ置く。

## 帳と板

己の帳(`queue/tasks/ashigaru-mac-2.yaml`)の ★己の鍵だけ★ を改めた(㋗)。
★書込の前に parse を当て★、bak を取り、鍵の数と順と既存欄の逐語一致を assert した(裁333131②)。
★板は書かぬ ―― 板は家老の手である。★

## 十二 便(㋘) ―― ★送つた物と、送つた後に讀み返した物★

★便の臺(raw/90_okuri.txt)★
```
eta185	karo-mac	parent_seq=332455	字=253	rc=0	★karo-mac へ送出した★ seq=333613（parent_seq=332455）
eta186	karo-mac	parent_seq=332455	字=296	rc=0	★karo-mac へ送出した★ seq=333614（parent_seq=332455）
a1	karo-mac	parent_seq=332455	字=250	rc=0	★karo-mac へ送出した★ seq=333779（parent_seq=332455）
b_a2-km171	karo-mac	parent_seq=332455	字=292	rc=0	★karo-mac へ送出した★ seq=333781（parent_seq=332455）
b_a2-km172	karo-mac	parent_seq=332455	字=299	rc=0	★karo-mac へ送出した★ seq=333782（parent_seq=332455）
b_a2-km174	karo-mac	parent_seq=332455	字=299	rc=0	★karo-mac へ送出した★ seq=333783（parent_seq=332455）
c_kami	karo-mac	parent_seq=332455	字=207	rc=0	★karo-mac へ送出した★ seq=333787（parent_seq=332455）
d_utsushi	karo-mac	parent_seq=332455	字=229	rc=0	★karo-mac へ送出した★ seq=333788（parent_seq=332455）
e_fudou	karo-mac	parent_seq=332455	字=257	rc=0	★karo-mac へ送出した★ seq=333790（parent_seq=332455）
f_mon1	karo-mac	parent_seq=332455	字=211	rc=0	★karo-mac へ送出した★ seq=333791（parent_seq=332455）
g_mon2	karo-mac	parent_seq=332455	字=176	rc=0	★karo-mac へ送出した★ seq=333792（parent_seq=332455）
g_mon2b	karo-mac	parent_seq=332455	字=206	rc=0	★karo-mac へ送出した★ seq=333793（parent_seq=332455）
h_mon3	karo-mac	parent_seq=332455	字=184	rc=0	★karo-mac へ送出した★ seq=333794（parent_seq=332455）
i_taba	karo-mac	parent_seq=332455	字=197	rc=0	★karo-mac へ送出した★ seq=333795（parent_seq=332455）
kansa1	gunshi-mac	parent_seq=332455	字=256	rc=0	★gunshi-mac へ送出した★ seq=333797（parent_seq=332455）
kansa2	gunshi-mac	parent_seq=332455	字=217	rc=0	★gunshi-mac へ送出した★ seq=333798（parent_seq=332455）
kansa2b	gunshi-mac	parent_seq=332455	字=189	rc=0	★gunshi-mac へ送出した★ seq=333799（parent_seq=332455）
kansa3	gunshi-mac	parent_seq=332455	字=208	rc=0	★gunshi-mac へ送出した★ seq=333800（parent_seq=332455）
j_chou	karo-mac	parent_seq=332455	字=260	rc=0	★karo-mac へ送出した★ seq=333802（parent_seq=332455）
j_chou2	karo-mac	parent_seq=332455	字=240	rc=0	★karo-mac へ送出した★ seq=333803（parent_seq=332455）
eta186b	karo-mac	parent_seq=332455	字=247	rc=0	★karo-mac へ送出した★ seq=333804（parent_seq=332455）
q_pr	karo-mac	parent_seq=332455	字=189	rc=0	★karo-mac へ送出した★ seq=333805（parent_seq=332455）
n_kotei185_171	karo-mac	parent_seq=333944	字=280	rc=0	★karo-mac へ送出した★ seq=334868（parent_seq=333944）
n_kotei185_172	karo-mac	parent_seq=333944	字=277	rc=0	★karo-mac へ送出した★ seq=334869（parent_seq=333944）
n_kotei185_174	karo-mac	parent_seq=333944	字=281	rc=0	★karo-mac へ送出した★ seq=334870（parent_seq=333944）
o_mipush185	karo-mac	parent_seq=333944	字=235	rc=0	★karo-mac へ送出した★ seq=334871（parent_seq=333944）
p_yoncha185	karo-mac	parent_seq=333944	字=220	rc=0	★karo-mac へ送出した★ seq=334872（parent_seq=333944）
```

★第八の守り ―― 臺帳から讀み返した出目(raw/95_yomikaeshi.tsv)★
| 便 | seq | 読み返しの rc | 送つた胴の字 | 臺帳が返した全文の字 | 判 |
|---|---|---|---|---|---|
| eta185 | 333613 | rc=0 | 送=253字 | 臺帳の出=714字 | ★丸ごと在り★ |
| eta186 | 333614 | rc=0 | 送=296字 | 臺帳の出=757字 | ★丸ごと在り★ |
| a1 | 333779 | rc=0 | 送=250字 | 臺帳の出=711字 | ★丸ごと在り★ |
| b_a2-km171 | 333781 | rc=0 | 送=292字 | 臺帳の出=753字 | ★丸ごと在り★ |
| b_a2-km172 | 333782 | rc=0 | 送=299字 | 臺帳の出=760字 | ★丸ごと在り★ |
| b_a2-km174 | 333783 | rc=0 | 送=299字 | 臺帳の出=760字 | ★丸ごと在り★ |
| c_kami | 333787 | rc=0 | 送=207字 | 臺帳の出=668字 | ★丸ごと在り★ |
| d_utsushi | 333788 | rc=0 | 送=229字 | 臺帳の出=690字 | ★丸ごと在り★ |
| e_fudou | 333790 | rc=0 | 送=257字 | 臺帳の出=718字 | ★丸ごと在り★ |
| f_mon1 | 333791 | rc=0 | 送=211字 | 臺帳の出=672字 | ★丸ごと在り★ |
| g_mon2 | 333792 | rc=0 | 送=176字 | 臺帳の出=637字 | ★丸ごと在り★ |
| g_mon2b | 333793 | rc=0 | 送=206字 | 臺帳の出=667字 | ★丸ごと在り★ |
| h_mon3 | 333794 | rc=0 | 送=184字 | 臺帳の出=645字 | ★丸ごと在り★ |
| i_taba | 333795 | rc=0 | 送=197字 | 臺帳の出=658字 | ★丸ごと在り★ |
| kansa1 | 333797 | rc=0 | 送=256字 | 臺帳の出=721字 | ★丸ごと在り★ |
| kansa2 | 333798 | rc=0 | 送=217字 | 臺帳の出=682字 | ★丸ごと在り★ |
| kansa2b | 333799 | rc=0 | 送=189字 | 臺帳の出=654字 | ★丸ごと在り★ |
| kansa3 | 333800 | rc=0 | 送=208字 | 臺帳の出=673字 | ★丸ごと在り★ |
| j_chou | 333802 | rc=0 | 送=260字 | 臺帳の出=721字 | ★丸ごと在り★ |
| j_chou2 | 333803 | rc=0 | 送=240字 | 臺帳の出=701字 | ★丸ごと在り★ |
| eta186b | 333804 | rc=0 | 送=247字 | 臺帳の出=708字 | ★丸ごと在り★ |
| q_pr | 333805 | rc=0 | 送=189字 | 臺帳の出=650字 | ★丸ごと在り★ |
| n_kotei185_171 | 334868 | rc=0 | 送=280字 | 臺帳の出=741字 | ★丸ごと在り★ |
| n_kotei185_172 | 334869 | rc=0 | 送=277字 | 臺帳の出=736字 | ★丸ごと在り★ |
| n_kotei185_174 | 334870 | rc=0 | 送=281字 | 臺帳の出=741字 | ★丸ごと在り★ |
| o_mipush185 | 334871 | rc=0 | 送=235字 | 臺帳の出=696字 | ★丸ごと在り★ |
| p_yoncha185 | 334872 | rc=0 | 送=220字 | 臺帳の出=680字 | ★丸ごと在り★ |

★此の表が意味せぬ事★:
  ・rc=0 は ★届いた★ の意であつて ★讀まれた★ の意ではない。
  ・「丸ごと在り」は 送つた胴が臺帳の全文に ★含まれて居る★ の意である ――
    臺帳は頭書きを添へる故、完全一致では測れぬ(字数を併せ書いたのは其の為)。
  ・本表は ★此の紙を書いた刻まで★ の便である。★之より後に出す便は此の表に載らぬ。★
