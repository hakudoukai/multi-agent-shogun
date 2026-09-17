門控: 出す前の門 第四走(器を -z へ直した後・_gate/km100_h4_20260917T154008) rc=0 / 母數 192 / 條① 一致 192・相違 0・実体無 0 / 條②③④ 53 本 通(宣して除いた 139 = 写し 5・他器出力 72・git 名一覧 54・0byte 8 ―― _gate/96_nozoita_uchiwake_h4.txt) / 條⑤ byte和 177128 ‖ gate7(胴=一行目を除く・_gate/gate7_body_h4_*) rc=0 痕跡無(甲=0 ゆゑ課さず)/甲=0 乙=3 丙=27 數主張=0(欄3 課さず)/★欄4 無★/★欄5 無★/欄6 通(20) ‖ 第五走(README を臺帳に足した後・_gate/km100_h5_*)は此の行の後に生れる。第一〜三走(splitlines 版・h1 rc=0 母數 193 / h2 疵 / h3 rc=0 母數 196)は _gate/km100_h[123]_* に控

# km-100 ―― 枝 45 本の着地仕分け(ashigaru 系 18 本の組) ―― 消さず・触らず・測る

- 席 = ashigaru-mac-1(足軽mac1号) / bloom L5 / task_id = `km-100-eda-yonjuugo-no-chakuchi-shiwake-ashigaru-gun-20260917`
- 着 2026-09-17T14:51:16+0900(tmux 自己識別直後の date) / 器着手 `raw/00_chaku_toki.txt` 一行目 / 着手便 `msg_20260917_145021_3147200c`(宣ETA 無し ―― 着手便に ETA を書かなんだ。實は着〜納め便 約 60 分)
- 親裁 = 委員長裁 seq325884(親 325872)「枝削除は不可逆＝理事長専管ゆゑ★消さない★。残 45 本を着地/捨てへ仕分けよ」。札 = `raw/01_fuda_utsushi.yaml`。
- 的 = 一事のみ ―― ★割当 18 本(ashigaru-mac-1/2/3 の枝)を「着地させる(PR)／捨てる(理事長裁待ち)／測れぬ」へ仕分ける★。枝は一本も触れて居らぬ(後述「禁の順守」)。
- 60 本の tip 一覧は家老mac 臺帳の写し `raw/02_karo_60tips_utsushi.tsv`(原本 `docs/evidence/karo-mac-eda-fuyou-20260917/MANIFEST.txt` sha256 頭 `17d7dbf7` ―― `raw/04_karo_daichou_sha.txt` で一致を確かめた)。

## 結(先に述べる)

1. ★仕分け = 甲(着地候補) 18 / 乙(捨て候補) 0 / 丙(測れぬ) 0★(`an/95_shiwake.tsv`・器 `driver/70_shiwake.py` rc=0)。拠り所 R0〜R4 は下「㋓」に先に宣した。乙が 0 なのは「R1(他 tip の祖先)に当たる枝が 18 本中 0」「R2(全 file が他 tip に同一 blob)に当たる枝が 0」を器で測つた結果であり、判断で零にしたのではない。
2. ★18 本は悉く「一本の幹の葉」である★。幹 = 家老mac が「不要 15」と名指した karo-mac 枝の列(`skills-tools-20260908b`†→`gate4`†→`gate5`†→`manifest-verify`†→`km-dead-inbox-gate`†→`a3-r39-fix`†→`km-50-47`†→`km-gate-kou-otsu`†→`km-gate4-kou-otsu`†→`km-shikii-yokotenkai`†)。各葉は其の幹の三駅(`km-gate-kou-otsu`/`km-gate4-kou-otsu`/`km-shikii-yokotenkai`)の何れかから ★独自 commit 1〜2 個★ を生やす(`raw/52_kusari.tsv`)。
3. ★⑴ と ⑵ は別物★: ⑴(対 origin/main 3-dot)= 465〜1101 file、⑵(自前 = 最寄り祖先 tip との差)= 1〜637 file。⑴の大半は幹の分であり、★枝が変へた file 数ではない★(数の規律3・下「數が何を意味せぬか」)。
4. ★origin/main は 18 tip の何れの祖先でもない★(18/18 `merge-base --is-ancestor` rc=1)。分岐点は悉く `6e9d4060`(=`skills-tools-20260908b`・main に入つた唯一の mac 枝)で、main は其処から 21 commit / 14 file 進んで居る(`raw/86_main_gawa_files.txt`)。
5. ㋕ ★割当 18 本の中に「tip が他 tip の祖先」の対は 0★(60×59=3540 回の `is-ancestor` の内、割当同士は 0 対・`raw/50_warimochi_nai_anc.tsv`)。∴ 群内に鎖は無く、★末端だけ着地させれば足りる、は成り立たぬ ―― 18 本各々(又は一本に束ねた枝)を着地させねば内容は main に届かぬ★。逆に幹(不要 15)は ★どの葉の PR にも自動で乗る★ ゆゑ、幹自身の PR は要らぬ。
6. ㋔ ★PR 衝突: 対 origin/main は 18/18 衝突 0★(`git merge-tree --write-tree` rc=0・`raw/89_merge_tree.tsv`)。陽性対照 = 同じ器を残 45 本の総当たり 990 対へ当てて ★61 対が鳴つた★(`raw/90_merge_tree_taishou.tsv`・器は鳴る)。鳴つた相手は `karo-mac/hantei-saiteishutsu-20260917` が 18/18(file=`scripts/checks/karo_mac_dasumae_gate.sh`)、`km-79` 15、`km-82` 6 ―― ★他席 lot の karo 枝が先に着地すると、当群の PR は rebase を要する★。群内(18 本同士)は own file 交差 0 対・merge-tree 衝突 0 対。
7. ㋔ ★tip の束そのものへ門を当てた★(`git archive` で repo 外 scratch へ展開・`raw/75_tip_mon.tsv`): 條①(臺帳と disk)一致 18/19 dir(a2 `km-53` のみ相違 1 = `_gate/92_gate.err`)、臺帳は 19/19 束内相対、出す前の門 通 11 / 落 8。落ちた 8 は悉く 條②④(末尾空白・EOF・0byte)で、其の file は `.rej`/`.nama/`/`hako/`/`fixture` 等 ★門を破る為の汚れ(fixture)★ に見える(`raw/78_ochita_shubetsu.tsv`)。∴ 受入条件は「fixture と宣して argv から除く(第四の道)」で足りる見込み ―― ただし ★見込みであり、宣の有無は各束の紙を読んで判ずる事(当席は読んで居らぬ)★。
8. ★器(docs/evidence 外)を含む枝 = 2 本★: `ashigaru-mac-1/km-92`(`scripts/lib/detect_stale.sh` +63/−6)と `ashigaru-mac-3/km-91`(`scripts/stop_hook_inbox.sh` +79/−1・`raw/85_kiki_diffstat.txt`)。km-91 の tip は ★器のみで紙を持たぬ★ ―― 紙は `karo-mac/km-91-a3-20260917`(ce97a6d・他席 lot)に在る。両枝は ★軍師mac(死箱ゆゑ家老mac 代送)の器監査★ を受入条件に加へよ。
9. 手許の枝 head と origin tip の差: `ashigaru-mac-3/km-51` のみ手許が +1(`260f2a0` km-99)。測つたのは札の sha(origin tip `0039e13`)である(`raw/92_local_vs_origin.tsv`)。

## ㋐ 母數 = 18(割当を逐語で列べ・full sha・`git cat-file -e <sha>^{commit}` の rc)

| # | 枝 | sha40 | cat-file rc |
|---|---|---|---|
| 1 | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` | `12d304e55ebd587441fdac2d24d33c76710eb4fc` | 0 |
| 2 | `ashigaru-mac-1/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917` | `ac551f027c60f3e1d5a0ce115c400d086b9ec8bf` | 0 |
| 3 | `ashigaru-mac-1/km-71-kuumoji-wa-atai-toshite-furumau-20260917` | `622ce44744b7961552fd672c0f47f38b2049b286` | 0 |
| 4 | `ashigaru-mac-1/km-71b-fusagikata-ni-an-20260917` | `b1ba78d2b876976a9ff2376a3c757009358b766a` | 0 |
| 5 | `ashigaru-mac-1/km-72-tasekki-no-fusagikata-wo-kami-de-yabure-20260917` | `49e36d1e2dc36b8efa7030374a59c820aa6183ab` | 0 |
| 6 | `ashigaru-mac-1/km-86-na-no-kuchi-wo-repo-zentai-de-kazoe-doku-ga-atesaki-wo-kaeru-koto-wo-shimese-20260917` | `a5d2cadde8873d9537351378a0c4049ba3e5acfb` | 0 |
| 7 | `ashigaru-mac-1/km-92-sengen-shita-shikii-ga-ichido-mo-yomarenu-koto-wo-shimese-20260917` | `0260a76a600836efe950efa58965134928b71e88` | 0 |
| 8 | `ashigaru-mac-2/km-51-usage-wo-yomazu-ni-yonda-20260917` | `87d1a6177c2e40c3676f599d3132a00395e41a42` | 0 |
| 9 | `ashigaru-mac-2/km-52-shikii-no-bannin-wo-yoko-kara-yabure-20260917` | `a4cafdfd384dc0c704c58ff3b286e8f0a4b3c34f` | 0 |
| 10 | `ashigaru-mac-2/km-53-tasekki-no-fusagikata-wo-kami-de-yabure-20260917` | `454e4fb22179c8000b0a7f42bbe88f8cc2d9cb11` | 0 |
| 11 | `ashigaru-mac-2/km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917` | `05b29300ca8754e6c30a2e40e021297408277b51` | 0 |
| 12 | `ashigaru-mac-2/km-87-tatoeba-ochite-mo-toosu-kuchi-20260917` | `56c8b43caaea96a8937e4be50db6fff7e5d23552` | 0 |
| 13 | `ashigaru-mac-3/km-48-nise-no-tsuuka-20260917` | `12ac572845e777ba8c07d200afdb3e07229cb4d0` | 0 |
| 14 | `ashigaru-mac-3/km-49-shikii-no-bannin-wo-yaburi-ni-yuke-20260917` | `87762b41b9b58a03d7438bef9dfd0f67b5c6e64b` | 0 |
| 15 | `ashigaru-mac-3/km-50-yabure-hachikei-no-fusagikata-20260917` | `a9bb89a47849c7d6716eafe49f28dad5ed9ccc0c` | 0 |
| 16 | `ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917` | `0039e1321654e52c15c3bec4998b96282b05667f` | 0 |
| 17 | `ashigaru-mac-3/km-85-onore-no-bannin-no-ana-wo-hachihon-de-hakare-20260917` | `c2f6dd9bd96f81ffce002783b67605c6199394fb` | 0 |
| 18 | `ashigaru-mac-3/km-91-bannin-no-hikaku-ki-ga-fu-wo-toosu-ana-wo-hakare-20260917` | `eb6cf51de16fd06b76eaf1cf36c47d535e2d5373` | 0 |

rc=0 が 18/18(`raw/10_a_tenmoto.tsv`)。割当 18 本は 60 本一覧に逐語で在る(無い物 0・`raw/90_log.txt`)。

## ㋑㋒㋓㋔ 一本づつ(`an/96_shiwake_hyou.md` を其の儘写す・数は `an/95_shiwake.tsv` が原)

| # | 枝 | sha12 | ⑴3dot | ⑵own | B_min(†不要15) | own c | 領域 | 甲乙丙 | 則 | 條①/門(tip束) | merge-tree 対main | 受入条件 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917` | `12d304e55ebd` | 597 | 118 | `km-gate4-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/0(通) | rc=0 | 條①一致 / 門通 / 対main衝突0 / 群内交差0 |
| 2 | `ashigaru-mac-1/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917` | `ac551f027c60` | 676 | 197 | `km-gate4-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/0(通) | rc=0 | 條①一致 / 門通 / 対main衝突0 / 群内交差0 |
| 3 | `ashigaru-mac-1/km-71-kuumoji-wa-atai-toshite-furumau-20260917` | `622ce44744b7` | 611 | 132 | `km-gate4-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/0(通) | rc=0 | 條①一致 / 門通 / 対main衝突0 / 群内交差0 |
| 4 | `ashigaru-mac-1/km-71b-fusagikata-ni-an-20260917` | `b1ba78d2b876` | 564 | 85 | `km-gate4-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/0(通) | rc=0 | 條①一致 / 門通 / 対main衝突0 / 群内交差0 |
| 5 | `ashigaru-mac-1/km-72-tasekki-no-fusagikata-wo-kami-de-yabure-20260917` | `49e36d1e2dc3` | 680 | 187 | `km-shikii-yokotenkai-20260917`† | 1 | docs | **甲** | R4 | 0/1(落) | rc=0 | 條①一致 / ★門落(fixture の汚れなら宣して argv から除く=第四の道)★ / 対main衝突0 / 群内交差0 |
| 6 | `ashigaru-mac-1/km-86-na-no-kuchi-wo-repo-zentai-de-kazoe-doku-ga-atesaki-wo-kaeru-koto-wo-shimese-20260917` | `a5d2cadde887` | 1102 | 637 | `km-gate-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/0(通) | rc=0 | 條①一致 / 門通 / 対main衝突0 / 群内交差0 |
| 7 | `ashigaru-mac-1/km-92-sengen-shita-shikii-ga-ichido-mo-yomarenu-koto-wo-shimese-20260917` | `0260a76a6008` | 734 | 269 | `km-gate-kou-otsu-20260917`† | 2 | docs,scripts ★scripts/lib/detect_stale.sh★ | **甲** | R4 | 0/0(通) | rc=0 | 條①一致 / 門通 / 対main衝突0 / 群内交差0 / ★器差分の監査(scripts/lib/detect_stale.sh)★ |
| 8 | `ashigaru-mac-2/km-51-usage-wo-yomazu-ni-yonda-20260917` | `87d1a6177c2e` | 659 | 180 | `km-gate4-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/1(落) | rc=0 | 條①一致 / ★門落(fixture の汚れなら宣して argv から除く=第四の道)★ / 対main衝突0 / 群内交差0 |
| 9 | `ashigaru-mac-2/km-52-shikii-no-bannin-wo-yoko-kara-yabure-20260917` | `a4cafdfd384d` | 566 | 87 | `km-gate4-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/1(落) | rc=0 | 條①一致 / ★門落(fixture の汚れなら宣して argv から除く=第四の道)★ / 対main衝突0 / 群内交差0 |
| 10 | `ashigaru-mac-2/km-53-tasekki-no-fusagikata-wo-kami-de-yabure-20260917` | `454e4fb22179` | 648 | 155 | `km-shikii-yokotenkai-20260917`† | 1 | docs | **甲** | R4 | 1/1(落) | rc=0 | ★條① 相違を先に解け★ / ★門落(fixture の汚れなら宣して argv から除く=第四の道)★ / 対main衝突0 / 群内交差0 |
| 11 | `ashigaru-mac-2/km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917` | `05b29300ca87` | 525 | 32 | `km-shikii-yokotenkai-20260917`† | 1 | docs | **甲** | R4 | 0/0(通) | rc=0 | 條①一致 / 門通 / 対main衝突0 / 群内交差0 |
| 12 | `ashigaru-mac-2/km-87-tatoeba-ochite-mo-toosu-kuchi-20260917` | `56c8b43caaea` | 656 | 191 | `km-gate-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/1(落) | rc=0 | 條①一致 / ★門落(fixture の汚れなら宣して argv から除く=第四の道)★ / 対main衝突0 / 群内交差0 |
| 13 | `ashigaru-mac-3/km-48-nise-no-tsuuka-20260917` | `12ac572845e7` | 531 | 52 | `km-gate4-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/0(通) | rc=0 | 條①一致 / 門通 / 対main衝突0 / 群内交差0 |
| 14 | `ashigaru-mac-3/km-49-shikii-no-bannin-wo-yaburi-ni-yuke-20260917` | `87762b41b9b5` | 521 | 42 | `km-gate4-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/1(落) | rc=0 | 條①一致 / ★門落(fixture の汚れなら宣して argv から除く=第四の道)★ / 対main衝突0 / 群内交差0 |
| 15 | `ashigaru-mac-3/km-50-yabure-hachikei-no-fusagikata-20260917` | `a9bb89a47849` | 670 | 191 | `km-gate4-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/1(落) | rc=0 | 條①一致 / ★門落(fixture の汚れなら宣して argv から除く=第四の道)★ / 対main衝突0 / 群内交差0 |
| 16 | `ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917` | `0039e1321654` | 648 | 155 | `km-shikii-yokotenkai-20260917`† | 2 | docs | **甲** | R4 | 0,0/1,0(落,通) | rc=0 | 條①一致 / ★門落(fixture の汚れなら宣して argv から除く=第四の道)★ / 対main衝突0 / 群内交差0 |
| 17 | `ashigaru-mac-3/km-85-onore-no-bannin-no-ana-wo-hachihon-de-hakare-20260917` | `c2f6dd9bd96f` | 504 | 39 | `km-gate-kou-otsu-20260917`† | 1 | docs | **甲** | R4 | 0/0(通) | rc=0 | 條①一致 / 門通 / 対main衝突0 / 群内交差0 |
| 18 | `ashigaru-mac-3/km-91-bannin-no-hikaku-ki-ga-fu-wo-toosu-ana-wo-hakare-20260917` | `eb6cf51de16f` | 466 | 1 | `km-gate-kou-otsu-20260917`† | 1 | scripts ★scripts/stop_hook_inbox.sh★ | **甲** | R4 | 束無/束無(-) | rc=0 | ★tip に紙(evidence 束)が無い=器のみ・紙の所在を示せ★ / 対main衝突0 / 群内交差0 / ★器差分の監査(scripts/stop_hook_inbox.sh)★ |

### ㋓ 拠り所(先に宣した順・最初に当たる則で決まる・`driver/70_shiwake.py` 冒頭と同文)

| 則 | 条件 | 判 | 当たつた枝 |
|---|---|---|---|
| R0 | ㋐ rc≠0(物が無い) | 丙 | 0 |
| R1 | tip が 60 の他 tip の真の祖先(`raw/51_warimochi_ga_sosen_ka.tsv`) | 乙 | 0 |
| R2 | own diff の全 file が他 tip に同一 blob で在る(`raw/80_naiyou_kasanari.tsv` Y_full_n>0) | 乙 | 0 |
| R3 | 祖先 tip 無し・⑵ 測れぬ | 丙 | 0 |
| R4 | 其れ以外(独自 commit を持ち他枝に無い) | 甲 | 18 |

- 「紙のみか／器を含むか」は ★甲乙を分けぬ★(紙も main に届いて初めて残る)。器を含む 2 本は受入条件に「器監査」を足すのみ。
- R2 の部分重なり: `ashigaru-mac-3/km-51` の own 155 file の内 43 file は `karo-mac/km-53-hitotsu-no-aruki-ne-de-file-suu-wo-soroe-20260917` と同一 blob(其の枝の `km-53-hitotsu…` dir の写し)。同一 blob ゆゑ何れが先に着地しても衝突せぬ(merge-tree でも 0)。

### ㋔ 受入条件(甲 18 本に共通)

1. 條① 一致(tip 束で `karo_mac_manifest_verify.py <臺帳> .` rc=0)―― 17 本は既に 0。a2 `km-53` は `_gate/92_gate.err` の相違を解く(臺帳を作つた後に其の file が書き換はつた形・`raw/75_logs/*km-53-tasekki*.jou1.out`)。
2. 出す前の門 rc=0 ―― 落ちる 8 本は落ち file が fixture なら ★紙で宣して argv から除く(第四の道)★。宣が無ければ紙に足す(fixture の汚れを剥がすのは ★的を壊す★ ゆゑ不可)。
3. 対 origin/main で `merge-tree` 衝突 0 ―― 18/18 満たす(★ただし他席 lot の `hantei-saiteishutsu`/`km-79`/`km-82`/`km-81` が先に main に入れば再測が要る★)。
4. 群内 file 交差 0 ―― 満たす(own diff 同士の交差 0 対・`raw/60_shoutotsu_own_pairs.tsv`)。
5. 器を含む 2 本(km-92 / a3 km-91)は器差分の監査印。km-91 は紙(`karo-mac/km-91-a3`)と ★同じ PR 又は連続 PR★ で出す(器だけ main に入ると紙の無い変更になる)。
6. ★着地順★: 最初に通る一本が幹 17〜18 commit(不要 15 の内容)を運ぶ。以後の 17 本は own 1〜2 commit の差だけになる。順は問はぬ(群内交差 0)が、★一本目は幹の器差分(`.gitignore`/`karo_mac_manifest_verify.py`/`inbox_watcher.sh`・`raw/88_kousa_blob_rekishi.txt`)を含む★ ゆゑ其の PR の監査が最も重い。

## ㋕ 重なり・鎖

- 割当 18 本の中で tip が他 tip の祖先に成る対 = ★0★(`raw/50_warimochi_nai_anc.tsv`・器 `driver/10_hakari.py`・呼出 3540 回の内 rc=0 は 509 対、其の全てが「幹→葉」か「幹→幹」)。
- 割当 18 本の内、60 本の他 tip の祖先に成つて居る枝 = 0(`raw/51_warimochi_ga_sosen_ka.tsv`)。∴ 家老mac の「不要 15」と当群は交はらぬ。
- 鎖(`raw/52_kusari.tsv`): 三駅 ―― `km-gate4-kou-otsu`† 駅 = 9 本(a1-jishu/km-70/71/71b, a2 km-51/52, a3 km-48/49/50)／`km-gate-kou-otsu`† 駅 = 5 本(km-86/92, a2 km-87, a3 km-85/91)／`km-shikii-yokotenkai`† 駅 = 4 本(km-72, a2 km-53/53b, a3 km-51)。
- ★末端のみ着地で足りるか★ = 否。群内に鎖が無い(全て葉)ゆゑ、各葉の own commit は其の葉を着地させねば main に届かぬ。幹は最初の葉に乗る。

## 數が何を意味せぬか(数の規律3)

- ⑴ 3-dot(465〜1101)は「枝が変へた file 数」では ★ない★。分岐点 `6e9d4060` から tip までの差 = 幹(不要 15 の内容・約 450〜470 file)+ own。main が幹を取り込めば ⑴ は own に縮む。
- ⑴ 2-dot(`d1_2dot_files`)は 3-dot より 10〜11 大きい ―― main 側が分岐後に変へた 14 file の内、枝側と重ならぬ分。「main が何 file 遅れて居るか」は ⑴ 3-dot であり 2-dot ではない。
- ⑵ own(1〜637)は「最寄りの祖先 tip との差」であり、祖先 tip は悉く不要 15 の karo 枝。own が大きい枝(km-86 637)は束が大きいだけで、器の変更量ではない(器 file は km-92/km-91 の各 1 のみ)。
- 「衝突 0」は ★origin/main `4be3ee19` の今★ に対する値。main が動けば変はる。
- 門「落 8」は束の疵の数ではない ―― 落ち行の file 名から fixture と見えるが、★各束の紙を読んで宣の有無を確かめて居らぬ★。
- 「甲 18」は「PR を出せ」の意ではない ―― 起票は監督 lot・判定は軍師mac(裁 325884)。当紙は測りである。

## 測り方(逐語・追試できる形・悉く読取)

```
git cat-file -e <sha>^{commit}                              # ㋐ 18/18 rc=0
git merge-base --is-ancestor <B> <X>                        # 60×59=3540 回 → rc=0 509 対(同 sha の対は真の祖先に数へぬ)
git rev-list --count <B>..<X>                               # 最小の B を B_min とする(同点 0)
git diff --name-only -z 4be3ee19e1c5...<X> | tr -cd '\0' | wc -c   # ⑴  (★-z=NUL 区切り★・名に U+2028/TAB/" を持つ fixture 3 本を割らず一本づつ数へる)
git diff --name-only <B_min>..<X>  | wc -l                  # ⑵
git rev-list --count 4be3ee19e1c5..<X>                      # ㋒ commit 数 17〜20
git ls-tree -r <Y> -- <own files>                           # R2 同一 blob の検め(18×59)
git merge-tree --write-tree --name-only 4be3ee19e1c5 <X>    # ㋔ 衝突(rc=0 無/1 有)・object のみ書き refs/工作樹/index 不触
git archive <X> -- docs/evidence/<dir> | tar -x -C <scratch>  # tip 束の展開(checkout せず)
python3 -B scripts/checks/karo_mac_manifest_verify.py <臺帳> .   ;  KM_GATE_MANIFEST_BASE=. bash scripts/checks/karo_mac_dasumae_gate.sh <臺帳> $(臺帳の path)
```

- 器: `driver/10_hakari.py`(㋐㋑㋒㋕・rc=0)/`20_ukeire.py`/`30_naiyou_kasanari.py`/`40_kusari.py`/`50_tip_mon.sh`/`60_merge_tree.sh`/`65_merge_tree_taishou.sh`/`70_shiwake.py`(悉く rc=0・`raw/*_run.rc`)。
- 第一走の疵: `git` が非ASCII path を引用符で括り `"docs` が領域に混じつた → `-c core.quotePath=false` を足して走り直し(第一走は `_gate/hashiri1_quotepath/` に退けた)。
- ★第二走の疵(家老mac 檢分 `msg_20260917_153703_5f9074b5` が器の中に見た)★: `10_hakari.py` が git の名一覧を Python の `str.splitlines()` で割つて居た。`splitlines()` は `\n` だけでなく ★U+2028(LINE SEPARATOR)等も行末と見做す★ ゆゑ、fixture `docs/evidence/km-46-yomite-no-kizu-20260917/fixture/kata/A06/a<U+2028>b.txt` が「…/a」と「b.txt」の二本に化け、⑴ 3-dot と 2-dot の ★36 欄が悉く丁度 1 多かつた★(旧 597 → 新 596 等)。家老mac の實測(`--name-only -z`)と同じ形へ直した ―― 全 git 名一覧を `-z`(NUL 区切り)で受け `split('\0')`、控の再読は `split('\n')`。own(⑵)18/18・甲乙丙 18/0/0・㋕・衝突は ★不動★(`raw/40_hakari.tsv` 新旧比較: 変はつた欄 70 = d1_3dot 18 + d1_2dot 18 + areas_d1 18 + 空欄の有無 16)。第二走の出目は `_gate/hashiri2_splitlines/` に退けた。65 の第一走は bash 3.2 に `mapfile` が無く配列が空 → 空 sha で git が rc=1 を返し「990 対鳴つた」と ★偽の陽性★ が出た(`_gate/90_merge_tree_taishou_hashiri1_mapfile_nashi.tsv`)。read ループへ直し、空 sha と rc≥2 で止まる守りを足して 61/990 を得た。
- scratch = `/Users/momizimac/km100_tips_extract_20260917/`(repo 外・`git archive` の写し・sha から再生可能・`raw/74_scratch_basho.txt`)。

## 禁の順守

- 枝を消して居らぬ・checkout/merge/rebase/cherry-pick/push/fetch/refs 書換 = 0 回。HEAD は着時と同じ `260f2a0`(`ashigaru-mac-3/km-51…` の枝・当席の物ではない)。
- `merge-tree --write-tree` は object(dangling tree)を書くが refs/index/工作樹は触らぬ ―― 読取の枠内と判じた。異論あらば `git gc` で消える物ゆゑ可逆。
- ★当束は commit して居らぬ★ ―― HEAD が他席(a3)の枝で、commit すれば ★測つた ref(0039e13 の枝)を動かす★(禁「refs 書換」)。km-97 束も未 commit(`??`)の前例に倣ふ。commit の要否は家老mac の裁。
- 他席の pane は覗いて居らぬ。origin へは一度も当たつて居らぬ(60 本一覧は家老mac の臺帳の写し)。

## 納め便

- 宛 = karo-mac(軍師mac は死箱ゆゑ家老mac が監査代送)。胴 = `an/98_osame_bin.txt`・初便 295 字(`msg_20260917_151109_ffcaf7c9`・第一稿 406/第二稿 308 は條超)。直し便(親 `msg_20260917_153703_5f9074b5`)= 296 字(python3 len・條 300・`an/99_osame_len.txt`・第一稿 307 は條超)。
