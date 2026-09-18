# km-186 ―― ★大文字・小文字の双子を数へ、消す順を実射で確かめた★(専任2・裁332455／補正333611)

刻 = 2026-09-18T21:10:14+0900 ／ 席 = ashigaru-mac-2(專任2) ／ 親裁 = 332455 ／ 補正 = hosei_186_sai_333611
固定 commit = `6bde7170ce574090a6139ba2dfe3aa4cb6db8634`(母數も canon も悉く此の樹で測つた)

## 〇 一行で

**双子は ★1 組だけ★。canon は ★小文字の名しか指して居らぬ★。然るに此の Mac では
其の名を開くと ★旧版 2596 bytes★ が出る ―― 二つの名が ★同じ実体(inode 10724954)★ を指して居る故である。**

∴ 「消す順が正本の生死を決める」は ★言葉ではなく数で確かめた★(下 ㋔)。
正順(⑴`rm --cached` → ⑵`checkout -- <小文字>`)で彫り、★共用樹は前後不動・push 0・gh 0★。

★命の字義から一つだけ外れた★ ―― ⑷の `git commit --only` は ★此の双子では彫れぬ★ 事を二度実測し、
素の `git commit` を用ゐた(下 ㋓續・便 f_only186)。★隠さず名指しし、御下知を仰いで居る。★

## ㋐ 母數 ―― 己で建てた

★10 の〆 ―― 母數と組★
刻 = 2026-09-18T20:31:47+0900 ／ 根 = /Users/momizimac/multi-agent-shogun ／ 固定 = origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634
器 = git ls-tree -r --name-only -z(★NUL 区切り★ ―― git は非 ASCII を引用符で括る故 行では壊れる)
rc(name-only) = 0 ／ rc(full) = 0(★returncode 素・管を通さぬ★)

★母數 = 548 path★(固定 commit の全 blob path)
★casefold で括つて 2 本以上に成る組 = 1 組★
  ⑴鍵=docs/runbooks/err-ekarte-001.md ―― docs/runbooks/ERR-EKARTE-001.md ／ docs/runbooks/err-ekarte-001.md

★此の數が意味せぬ事★:
  ・母數は ★固定 commit 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 の樹★ の數である。★disk の數ではない★し、他の枝の數でもない。
  ・「1 組」は ★path の字面を casefold で括つた數★ であり、
    ★中身が同じか否かは一切言つて居らぬ★(中身は 10_kumi_git.tsv の sha256 を見よ)。
  ・disk 側の「開けるか」は ★mac の file 系が大小を畳む★故に True に成り得る ――
    ★其の path の名で実体が在る事を意味せぬ★(実名は親 dir の listdir で引いた)。
  ・器の言(err): name-only=― ／ full=―

### 全 ref も歩いた(他の双子が在るか)

ref = ★378 本★ ／ 別々の樹 = ★306 本★。★組が 2 以上に成つた ref = 0 本★。
内訳 ―― 組=1 の ref = 337 本 ／ ★組=0 の ref = 41 本(其の樹に双子が一本も無い ―― 古い枝・別系統)★。
★「1 組の儘」は「悉くの樹に双子が在る」の意ではない★。新たな双子が ★一組も出なかつた★ の意である。

★15 の〆 ―― ref の先を悉く歩いた★
刻 = 2026-09-18T20:32:33+0900 ／ 根 = /Users/momizimac/multi-agent-shogun
rc(for-each-ref) = 0(★returncode 素★) ／ ref = ★378 本★ ／ 別々の樹 = ★306 本★

★ref の先で見えた casefold の組 = 1 組★
  ・docs/runbooks/err-ekarte-001.md ―― docs/runbooks/ERR-EKARTE-001.md ／ docs/runbooks/err-ekarte-001.md

★此の數が意味せぬ事★:
  ・歩いたのは ★ref の先(tip)★ のみである。★過去の commit は一つも歩いて居らぬ★ ――
    歴史の途中に在つて今は消えた双子は ★此の數に入らぬ★。
  ・ref には他席の枝も含まれる。★他席の枝を歩いた事は、其の枝に触れた事を意味せぬ★(読取のみ・checkout せず)。
  ・組の數は ★path の字面★ の話であり、中身の異同を言つて居らぬ。
  ・器の言(err) = ―

## ㋑ 二つの blob と、disk の一本

### git の側(固定 commit)

| casefold鍵 | git の path | 型 | blob sha1 | cat-file -s の bytes | 実際に読めた bytes | 中身の sha256 | rc |
|---|---|---|---|---|---|---|---|
| docs/runbooks/err-ekarte-001.md | docs/runbooks/ERR-EKARTE-001.md | blob | e6de627bd62eb9a4b417155f40748390f49369fe | 2596 | 2596 | abf519d04dc5cfbb3adb7dbcf6a5dd2c132e52c3c492530e4f8b90a0ff363fba | rc_s=0 rc_b=0 |
| docs/runbooks/err-ekarte-001.md | docs/runbooks/err-ekarte-001.md | blob | de00cbd99d9909f4a923041ae17f0d2cbb587668 | 3471 | 3471 | 24cf87840d94dd6b18a5f292bef598f370eede58127296f01a04b5667ee3d50f | rc_s=0 rc_b=0 |

### disk の側(★同じ刻に同じ根で★)

| casefold鍵 | git の path | 親 dir の listdir に其の名が在るか | 其の path で開けるか | disk の bytes | disk の sha256 | inode |
|---|---|---|---|---|---|---|
| docs/runbooks/err-ekarte-001.md | docs/runbooks/ERR-EKARTE-001.md | dir に実名有り=False | open 出来る=True | 2596 | abf519d04dc5cfbb3adb7dbcf6a5dd2c132e52c3c492530e4f8b90a0ff363fba | 10724954 |
| docs/runbooks/err-ekarte-001.md | docs/runbooks/err-ekarte-001.md | dir に実名有り=True | open 出来る=True | 2596 | abf519d04dc5cfbb3adb7dbcf6a5dd2c132e52c3c492530e4f8b90a0ff363fba | 10724954 |

★見よ★ ―― 大文字の名は ★親 dir の listdir に無い★のに ★開ける★。inode は二つとも同じ。
∴ ★実体は一本であり、其の中身は大文字の blob(2596 bytes)★。
★小文字の blob(3471 bytes)は此の Mac の disk に一度も現れて居らぬ。★

## ㋒ canon は孰れの名を指して居るか

`.md` 付き(= file を指して居る): ★大文字 0 当り／小文字 4 当り★
`.md` 無し(= error code を指して居る): 大文字 19 当り／小文字 0 当り ―― ★別に数へた★

| 現れた字面 | 出た回数 | 其の形を持つ file 数 | 大小 | 拡張子 |
|---|---|---|---|---|
| ERR-EKARTE-001 | 19 | 5 | 大文字混じり | .md 付き=False |
| err-ekarte-001.md | 4 | 1 | 悉く小文字 | .md 付き=True |

| 区 | 指して居る file | 当りの総数 | 字面の形ごとの数 |
|---|---|---|---|
| CLAUDE.md | CLAUDE.md | 6 | ERR-EKARTE-001=2 ／ err-ekarte-001.md=4 |
| docs/ | docs/error-design-medical.md | 8 | ERR-EKARTE-001=8 |
| docs/ | docs/error_codes.md | 2 | ERR-EKARTE-001=2 |
| docs/ | docs/runbooks/ERR-EKARTE-001.md | 4 | ERR-EKARTE-001=4 |
| docs/ | docs/runbooks/err-ekarte-001.md | 3 | ERR-EKARTE-001=3 |

★20 の〆 ―― canon は孰れの名を指して居るか★
刻 = 2026-09-18T20:33:22+0900 ／ 根 = /Users/momizimac/multi-agent-shogun ／ 固定 = 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 ／ rc(ls-tree) = 0
歩いた blob = ★548 本★(固定 commit の全 blob) ／ 当つた file = ★5 本★ ／ 読めぬ blob = 0 本
探した形 = 正規 `err-ekarte-001(\.md)?`(★大小を問はず★)

★㋒ の二分(★.md が付く物だけ★ ―― 是が「file を指して居る」物である)★
  ・大文字混じりの名を指す当り = ★0★
  ・悉く小文字の名を指す当り   = ★4★

★.md の付かぬ当り(★file ではなく error code を指して居る★)★
  ・大文字混じり = 19 ／ 悉く小文字 = 0
  ―― ★之を「file を指す」に混ぜると数が水増しに成る★。故に分けた。

★現れた字面の形(畳まず悉く)★
  ・`ERR-EKARTE-001` = 19 当り(file 5 本)
  ・`err-ekarte-001.md` = 4 当り(file 1 本)

★此の數が意味せぬ事★:
  ・当りは ★固定 commit の中身★ の話であり、★disk の中身ではない★。
  ・「.md 付き」は ★file を指す意図★ の近似である ―― 文の中で code の後に「.md」と書いた例が在れば
    ★此の器は file と読む★。逐語は 20_sasu_file.tsv を見よ。
  ・二進の紙(utf-8 で開けぬ物)は歩いて居らぬ。
  ・器の言(err) = ―

### 索引の一行と実体の食ひ違ひ ―― 名指し

★25 の〆 ―― ★索引は小文字を指し、其の名を開くと大文字の中身が出る★★
刻 = 2026-09-18T20:37:33+0900 ／ 根 = /Users/momizimac/multi-agent-shogun ／ 固定 = 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 ／ rc(show CLAUDE.md) = 0

★⑴ 索引の一行(固定 commit の CLAUDE.md・逐語)★ ―― 当り ★2 行★
  ―― ★20 の「4 当り」と食ひ違はぬ★: markdown の link は同じ path を ★[題](path) と二度書く★ 故、
     ★2 行 × 2 = 4 当り★ である。20 は ★語の数★、25 は ★行の数★ を数へて居る(単位が違ふ)。
  ・L81 ｜ | Runbook ERR-EKARTE-001 | [docs/runbooks/err-ekarte-001.md](docs/runbooks/err-ekarte-001.md) |
  ・L424 ｜ ★Runbook 完全な記述は [docs/runbooks/err-ekarte-001.md](docs/runbooks/err-ekarte-001.md) に分離 (Lane 4 削減、Commander 2026-05-29)★

★⑵ git の側(固定 commit)★
  ・docs/runbooks/ERR-EKARTE-001.md
      blob = e6de627bd62eb9a4b417155f40748390f49369fe ／ 2596 bytes ／ sha256 = abf519d04dc5cfbb3adb7dbcf6a5dd2c132e52c3c492530e4f8b90a0ff363fba
      冠 = ---
  ・docs/runbooks/err-ekarte-001.md
      blob = de00cbd99d9909f4a923041ae17f0d2cbb587668 ／ 3471 bytes ／ sha256 = 24cf87840d94dd6b18a5f292bef598f370eede58127296f01a04b5667ee3d50f
      冠 = # Runbook: ERR-EKARTE-001 (カルテ visit 作成失敗)

★⑶ disk の側(★此の Mac で実際に open した★)★
  ・docs/runbooks/ERR-EKARTE-001.md ―― 開けた ／ 2596 bytes ／ inode 10724954 ／ 中身 = ★大文字の blob★
  ・docs/runbooks/err-ekarte-001.md ―― 開けた ／ 2596 bytes ／ inode 10724954 ／ 中身 = ★大文字の blob★
  ・listdir(docs/runbooks) が返す ★真名★ = err-ekarte-001.md

★★食ひ違ひ(名指し)★★
  ・索引(CLAUDE.md の 2 行)は ★悉く小文字の名★ を指して居る ―― 大文字を指す行は ★0★。
  ・然るに此の Mac では、其の小文字の名を開くと ★大文字の blob の中身★(2596 bytes)が出る。
  ・∴ ★索引は正しい名を指して居るのに、読者が受け取る中身は旧い方である。★
    ―― 名は合ひ、中身が違ふ。★link が壊れて居らぬ故、誰も気付かぬ形の食ひ違ひ★ である。
  ・3471 bytes の中身は ★此の disk に一度も存在して居らぬ★(10_disk.tsv・25_kuichigai.tsv 逐語)。

★此の數が意味せぬ事★:
  ・「大文字を指す行 = 0」は ★大文字の名が不要である事を意味せぬ★ ―― 孰れを正とするかは
    ★委員長の裁(seq333611)が既に定めた★ のであつて、此の數が定めたのではない。数は其れに合うて居るだけである。
  ・`ERR-EKARTE-001`(.md 無し)19 当りは ★error code★ であり、file 名ではない。消えぬし、消してはならぬ。
  ・disk の測りは ★case を畳む file system(此の Mac)★ の上の話である。
    ★case を区別する OS(Linux)で同じ二名が如何に見えるかは、此の disk からは測れぬ。★
  ・器の言(err) = ―

| 名 | git blob(sha1) | git bytes | git sha256 | disk 開閉 | disk bytes | disk sha256 | inode | disk の中身は孰れの blob か |
|---|---|---|---|---|---|---|---|---|
| docs/runbooks/ERR-EKARTE-001.md | e6de627bd62eb9a4b417155f40748390f49369fe | 2596 | abf519d04dc5cfbb3adb7dbcf6a5dd2c132e52c3c492530e4f8b90a0ff363fba | 開けた | 2596 | abf519d04dc5cfbb3adb7dbcf6a5dd2c132e52c3c492530e4f8b90a0ff363fba | 10724954 | ★大文字の blob★ |
| docs/runbooks/err-ekarte-001.md | de00cbd99d9909f4a923041ae17f0d2cbb587668 | 3471 | 24cf87840d94dd6b18a5f292bef598f370eede58127296f01a04b5667ee3d50f | 開けた | 2596 | abf519d04dc5cfbb3adb7dbcf6a5dd2c132e52c3c492530e4f8b90a0ff363fba | 10724954 | ★大文字の blob★ |

## ㋔ 逆順の実射 ―― ★己の使ひ捨て worktree の中だけで撃つた★

| 札 | 刻 | listdir の真名 | 大文字の名を開くと | 小文字の名を開くと | porcelain(docs/runbooks) | index |
|---|---|---|---|---|---|---|
| 〇 鮮な checkout の直後 | 20:40:22 | err-ekarte-001.md | 開けた ／ 3471 bytes ／ inode 26288055 ／ 中身 = ★小文字の blob(3471B・5/29 の新版 = 委員長が正と定めた方)★ | 開けた ／ 3471 bytes ／ inode 26288055 ／ 中身 = ★小文字の blob(3471B・5/29 の新版 = 委員長が正と定めた方)★ |  M docs/runbooks/ERR-EKARTE-001.md (rc=0) | 100644 e6de627bd62eb9a4b417155f40748390f49369fe 0 ⇥ docs/runbooks/ERR-EKARTE-001.md｜100644 de00cbd99d9909f4a923041ae17f0d2cbb587668 0 ⇥ docs/runbooks/err-ekarte-001.md |
| ★撃つた★ 共用樹の姿を再現(大文字の blob を dirent へ書く) ―― `git checkout -- docs/runbooks/ERR-EKARTE-001.md` | 20:40:22 | rc = 0 | out = ― | err = ― | ― | ― |
| 〇' 共用樹と同じ姿(disk = 大文字の blob) | 20:40:22 | ERR-EKARTE-001.md | 開けた ／ 2596 bytes ／ inode 26288230 ／ 中身 = ★大文字の blob(2596B・5/5 の旧版)★ | 開けた ／ 2596 bytes ／ inode 26288230 ／ 中身 = ★大文字の blob(2596B・5/5 の旧版)★ |  M docs/runbooks/err-ekarte-001.md (rc=0) | 100644 e6de627bd62eb9a4b417155f40748390f49369fe 0 ⇥ docs/runbooks/ERR-EKARTE-001.md｜100644 de00cbd99d9909f4a923041ae17f0d2cbb587668 0 ⇥ docs/runbooks/err-ekarte-001.md |
| ★撃つた★ ★逆順 ―― 素の git rm★ ―― `git rm docs/runbooks/ERR-EKARTE-001.md` | 20:40:22 | rc = 0 | out = rm 'docs/runbooks/ERR-EKARTE-001.md' | err = ― | ― | ― |
| 一 素の `git rm <大文字>` の直後 | 20:40:22 | ★無★ | ★開けぬ ―― FileNotFoundError★ | ★開けぬ ―― FileNotFoundError★ | D  docs/runbooks/ERR-EKARTE-001.md｜ D docs/runbooks/err-ekarte-001.md (rc=0) | 100644 de00cbd99d9909f4a923041ae17f0d2cbb587668 0 ⇥ docs/runbooks/err-ekarte-001.md |
| ★撃つた★ 逆順の続き ―― 消えた実体を index へ載せる(git add -A 相当) ―― `git add -A -- docs/runbooks/` | 20:40:22 | rc = 0 | out = ― | err = ― | ― | ― |
| 二 `git add -A` の後 ―― ★index からも正本が消えた★ | 20:40:22 | ★無★ | ★開けぬ ―― FileNotFoundError★ | ★開けぬ ―― FileNotFoundError★ | D  docs/runbooks/ERR-EKARTE-001.md｜D  docs/runbooks/err-ekarte-001.md (rc=0) | ★無★ |
| ★撃つた★ 戻しを試みる(index が既に空なら戻らぬ) ―― `git checkout -- docs/runbooks/err-ekarte-001.md` | 20:40:22 | rc = 1 | out = ― | err = error: pathspec 'docs/runbooks/err-ekarte-001.md' did not match any file(s) known to git | ― | ― |
| 三 `git checkout -- <小文字>` を打つた後 | 20:40:22 | ★無★ | ★開けぬ ―― FileNotFoundError★ | ★開けぬ ―― FileNotFoundError★ | D  docs/runbooks/ERR-EKARTE-001.md｜D  docs/runbooks/err-ekarte-001.md (rc=0) | ★無★ |
| ★撃つた★ 最後の頼み ―― HEAD から戻す ―― `git checkout HEAD -- docs/runbooks/ERR-EKARTE-001.md docs/runbooks/err-ekarte-001.md` | 20:40:22 | rc = 0 | out = ― | err = ― | ― | ― |
| 四 `git checkout HEAD -- <両名>` の後 | 20:40:22 | err-ekarte-001.md | 開けた ／ 3471 bytes ／ inode 26288240 ／ 中身 = ★小文字の blob(3471B・5/29 の新版 = 委員長が正と定めた方)★ | 開けた ／ 3471 bytes ／ inode 26288240 ／ 中身 = ★小文字の blob(3471B・5/29 の新版 = 委員長が正と定めた方)★ |  M docs/runbooks/ERR-EKARTE-001.md (rc=0) | 100644 e6de627bd62eb9a4b417155f40748390f49369fe 0 ⇥ docs/runbooks/ERR-EKARTE-001.md｜100644 de00cbd99d9909f4a923041ae17f0d2cbb587668 0 ⇥ docs/runbooks/err-ekarte-001.md |

★35 の〆 ―― ★消す順が正本の生死を決める★(逆順を撃つた記録)★
刻 = 2026-09-18T20:40:22+0900 ／ 撃つた場 = ★/Users/momizimac/wt/a2-km186-gyaku★(己が切つた使ひ捨ての worktree・detached 6bde7170)
★共有樹では一発も撃つて居らぬ★(共有樹の HEAD/index は 30/99 の紙で不動を證する)

★〇 鮮な checkout が置く物(★是が第一の測り★)★
  ・dirent は ★一本★(真名 = err-ekarte-001.md)、中身は ★開けた ／ 3471 bytes ／ inode 26288055 ／ 中身 = ★小文字の blob(3471B・5/29 の新版 = 委員長が正と定めた方)★★
  ・∴ ★鮮な clone/checkout では正本(3471B)が残る★ ―― index の並び順(大文字が先・小文字が後)で
    ★後に書いた方が勝つ★ 故である。★然るに共用樹の disk は 2596B を抱いて居る★(25_kuichigai.tsv)。
    ―― 共用樹が旧版を抱く因は ★未測★(此処では測つて居らぬ・推さぬ)。

★一 ★素の `git rm docs/runbooks/ERR-EKARTE-001.md` を踏むと何が起きたか★★
  ・打つ前 : ERR-EKARTE-001.md ／ 小文字の名を開くと 開けた ／ 2596 bytes ／ inode 26288230 ／ 中身 = ★大文字の blob(2596B・5/5 の旧版)★
  ・打つた後: ★無★ ／ 小文字の名を開くと ★開けぬ ―― FileNotFoundError★
  ・∴ ★大文字の名へ打つた rm が、小文字の名の実体を消した★ ―― 二つの名が ★同じ inode★ を指す故。
    ★委員長が正と定めた名が、正でない名への命令で死ぬ。★

★二 其の儘進んだら(`git add -A`)★
  ・index = ★無★
  ・∴ ★index からも正本の行が消えた★。此処で commit すれば ★樹から正本が落ちる★。

★三・四 戻せるか★
  ・`git checkout -- <小文字>`  → ★開けぬ ―― FileNotFoundError★
  ・`git checkout HEAD -- <両名>` → 開けた ／ 3471 bytes ／ inode 26288240 ／ 中身 = ★小文字の blob(3471B・5/29 の新版 = 委員長が正と定めた方)★
  ・∴ ★HEAD が生きて居る限り戻る★。然し ⑴commit を打つ ⑵push する ⑶HEAD を動かす の
    孰れかを踏めば ★戻す先が無く成る★。★逆順の害は「消えた事」ではなく「気付かぬ儘 commit する事」である。★

★此の數が意味せぬ事★:
  ・此処の測りは ★case を畳む file system(macOS)★ の上の話である。
    ★case を区別する Linux で同じ手順が同じ結果に成るかは、此の disk からは測れぬ★(㋕)。
  ・「鮮な checkout では 3471 が勝つ」は ★git の index 並び順から出た振舞ひ★ であり、
    ★git が正本を選んだ★ のではない。★偶々 後に書かれた方が残つただけ★ である。
  ・逆順を撃つたのは ★使ひ捨ての worktree★ のみ。此の枝は ★出さぬ★(PR に載せぬ)。

## ㋓續 ⑷ の呪文 ―― ★字義通りでは彫れぬ★

★40 の〆 ―― ★㋓⑷ を字義通りに踏むと双子が蘇る★★
刻 = 2026-09-18T20:41:45+0900 ／ 撃つた場 = ★己の使ひ捨て二本★(a2-km186-t1 / a2-km186-t2・detached 6bde7170)
★共有樹では撃つて居らぬ★。本番の枝(50)へ進む前に ★彫り方だけを先に試した★。

★甲 ―― `git rm --cached` → `git checkout --` → ★`git commit --only <大文字>` のみ★★
  ・commit の tree に残つた双子 = ★2 本★
    100644 blob e6de627bd62eb9a4b417155f40748390f49369fe ⇥ docs/runbooks/ERR-EKARTE-001.md
    100644 blob de00cbd99d9909f4a923041ae17f0d2cbb587668 ⇥ docs/runbooks/err-ekarte-001.md
★乙 ―― 命の字義通り ★`git add -f <大文字>` を挟む★★
  ・commit の tree に残つた双子 = ★2 本★
    100644 blob e6de627bd62eb9a4b417155f40748390f49369fe ⇥ docs/runbooks/ERR-EKARTE-001.md
    100644 blob de00cbd99d9909f4a923041ae17f0d2cbb587668 ⇥ docs/runbooks/err-ekarte-001.md

★★断(数から出る事のみ)★★
  ・★甲も乙も彫れて居らぬ★ ―― commit は二つとも ★rc=1「no changes added to commit」★ で、
    HEAD は 6bde7170 の儘 ★動いて居らぬ★(40_shiken.tsv 逐語)。
  ・∴ 「双子の行 = 2 本」は ★消しが失敗した事★ を意味する ―― 「add -f が蘇らせた」ではない。
    ★甲と乙の差は此の測りでは出て居らぬ(二つとも同じ壁で止まつた)。★
  ・因と ★彫れる形★ は 41 で測り直した ―― `raw/41_shime.txt` を見よ。
  ・★此の紙の初版には「甲で足りる」と書いた。測る前に断を書いたのが疵である(41 で訂す)。★

★此の數が意味せぬ事★:
  ・「双子の行 = 1 本」は ★中身が正本である事を意味せぬ★ ―― blob sha を併せ読め(50 で測る)。
  ・此処の commit は ★使ひ捨ての detached HEAD★ に在り、★枝でも PR でもない★。出さぬ。
  ・case を区別する Linux で `add -f` が同じ振舞ひを見せるかは ★此の disk からは測れぬ★(㋕)。

★41 の〆 ―― ★彫れる形は一つだけであつた★★
刻 = 2026-09-18T20:42:57+0900 ／ 撃つた場 = ★己の使ひ捨て t3/t4/t5★(detached 6bde7170) ／ ★共有樹では撃つて居らぬ★

★先づ 40 の断を改める★:
  40 で「甲(commit --only <大文字> のみ)で足りる」と書いたが、★甲も彫れて居らぬ★
  ―― rc=1「no changes added to commit」で ★HEAD は 6bde7170 の儘★ であつた。
  ★測る前に断を書いたのが疵である。41 の数で書き直す。★

★四つの候補と其の出目★
  ・甲 `git commit --only <大文字>`            → ★彫れず★(rc=1・40_shiken.tsv)
  ・乙 `git add -f <大文字>` → `commit --only` → ★彫れず★(rc=1・40_shiken.tsv)
  ・丙 `git commit -m`(index の儘)            → ★彫れた ―― 双子は 1 本・中身は正本(de00cbd9…)★
  ・丁 `git commit --only docs/runbooks/`     → ★彫れず(HEAD 動かず)★
  ・戊 `git commit --only <小文字>`            → ★彫れず(HEAD 動かず)★

★因(数から言へる所まで)★:
  ・`--only <path>` は ★worktree の其の path を読み直して彫る★。
    case を畳む disk では ★大文字の名は まだ開ける★ 故、git は「消えた」ではなく「modified」と見て、
    ★消しを彫らぬ★(「no changes added to commit」)。
  ・⑴の `git rm --cached` は ★index には正しく載る★(`git diff --cached --name-status` = D 一行)。
    ∴ ★載つて居る物を其の儘彫る形★ でなければ、此の消しは commit に入らぬ。

★∴ 本番の彫り(50)で用ゐる形★: ★丙 ―― 素の `git commit -m`(己の枝・index は D 一行のみ)★
  ―― ★㋓⑴⑵の順は一字も変へて居らぬ★。変へたのは ⑷ の彫り方だけであり、
     其れも ★字義通りでは彫れぬと数で出た★ 故である(㋔「呑むな・検めよ」)。★家老の御下知を仰ぐ★。

★此の數が意味せぬ事★:
  ・「彫れた」は ★中身が正しい事を別に確かめねば意味を成さぬ★ ―― 50 で blob sha を測る。
  ・素の `git commit -m` が安全なのは ★己の使ひ捨て/己の枝で index が空の時だけ★ である。
    ★共用樹では他席の staged が混じり得る ∴ 共用樹では決して打たぬ。★
  ・Linux(case を区別する側)で `--only` が同じ振舞ひを見せるかは ★此の disk からは測れぬ★(㋕)。

## ㋓ 正順の彫り

| 刻 | 札 | 打つた命 | rc | out | err/註 |
|---|---|---|---|---|---|
| 20:45:06 | 枝を切る(己の worktree) | git worktree add -b ashigaru-mac-2/km-186-futago-no-kesu-jun-20260918 /Users/momizimac/wt/a2-km186 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 | 0 | HEAD is now at 6bde7170 merge PR#27: 出す前門 條②④⑤ 是正+可搬化+負テスト(karo-mac km-118/km-156・軍師mac PASS 330856) ⏎ | Preparing worktree (new branch 'ashigaru-mac-2/km-186-futago-no-kesu-jun-20260918') ⏎ |
| 20:45:06 | 〇 共用樹の姿を再現(★是をせねば ⑵ が仕事を持たぬ★) | git checkout -- docs/runbooks/ERR-EKARTE-001.md | 0 | ― | ― |
| 20:45:06 | 〇 ★⑴の前★ の porcelain | git status --porcelain -- docs/runbooks/ | 0 | M docs/runbooks/err-ekarte-001.md | 行数=1 |
| 20:45:06 | ⑴ ★git rm --cached <大文字>★ | git rm --cached docs/runbooks/ERR-EKARTE-001.md | 0 | rm 'docs/runbooks/ERR-EKARTE-001.md' ⏎ | ― |
| 20:45:07 | ⑴ の後の porcelain | git status --porcelain -- docs/runbooks/ | 0 | D  docs/runbooks/ERR-EKARTE-001.md｜M docs/runbooks/err-ekarte-001.md | 行数=2 |
| 20:45:07 | ⑵ ★git checkout -- <小文字>★ | git checkout -- docs/runbooks/err-ekarte-001.md | 0 | ― | ― |
| 20:45:07 | ⑵ の後の porcelain | git status --porcelain -- docs/runbooks/ | 0 | D  docs/runbooks/ERR-EKARTE-001.md | 行数=1 |
| 20:45:07 | ⑶ ★index に載つて居る変化(是だけが彫られる)★ | git diff --cached --name-status | 0 | D ⇥ docs/runbooks/ERR-EKARTE-001.md ⏎ | ― |
| 20:45:07 | ⑷ ★彫る(素の commit ―― index の D 一行のみ)★ | git commit -m fix(runbooks): ★双子の片方を消す ―― 大文字 ERR-EKARTE-001.md を樹から外す★(委員長裁 seq333611) | ― | ― | ― |
| 正 = docs/runbooks/err-ekarte-001.md ―― 3471 bytes ／ blob de00cbd9… ／ 2026-05-29 の新版 | ― | ― | ― | ― | ― |
| 消 = docs/runbooks/ERR-EKARTE-001.md ―― 2596 bytes ／ blob e6de627b… ／ 2026-05-05 の旧版 | ― | ― | ― | ― | ― |
| ★case を畳む disk では二つの名が同じ inode を指す★(実測 10724954)。 | ― | ― | ― | ― | ― |
| ∴ 素の `git rm <大文字>` は ★正本の実体を消す★(実射 raw/35_gyaku.tsv)。 | ― | ― | ― | ― | ― |
| 彫りの順 = ⑴ git rm --cached <大文字> ⑵ git checkout -- <小文字> ⑶ 検め ⑷ 彫り(裁333611 ㋓)。 | ― | ― | ― | ― | ― |
| canon の側 = 索引は ★小文字のみ★ を指す(2 行 4 当り)・大文字を指す行 0(raw/20,25)。 | ― | ― | ― | ― | ― |
| 測り = docs/evidence/ashigaru-mac-2_km-186-oomoji-komoji-no-futago-20260918/ | ― | ― | ― | ― | ― |
| Co-Authored-By: Claude Opus 5 <noreply@anthropic.com> | ― | ― | ― | ― | ― |
| ― | 0 | [ashigaru-mac-2/km-186-futago-no-kesu-jun-20260918 4cb05b97] fix(runbooks): ★双子の片方を消す ―― 大文字 ERR-EKARTE-001.md を樹から外す★(委員長裁 seq333611) ⏎  Committer: MomiziMac <momizimac@MomiziMac-mini.local> ⏎ Your name and email address were configured automatically based ⏎ on your username and hostname. Please check that they are accurate. ⏎ You can suppress this message by setting them explicitly. Run the ⏎ following command and follow the instructions in your editor to edit ⏎ your configuration file: ⏎  ⏎     git config --global --edit ⏎  ⏎ After doing this, you may fix the identity used for this commit with: ⏎  ⏎     git commit --amend --reset-author ⏎  ⏎  1 file changed, 79 deletions(-) ⏎  delete mode 100644 docs/runbooks/ERR-EKARTE-001.md ⏎ | ― | ― | ― |
| 20:45:07 | ⑷ の後の porcelain | git status --porcelain -- docs/runbooks/ | 0 | ★空★ | 行数=0 |
| 20:45:08 | 未push ★陽性対照★ | git ls-remote origin refs/heads/main | 0 | 1 行 | 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 ⇥ refs/heads/main ⏎ |
| 20:45:08 | 未push ★当の枝★ | git ls-remote origin refs/heads/ashigaru-mac-2/km-186-futago-no-kesu-jun-20260918 | 0 | 0 行 | ― |
| 20:45:08 | 未push ★負対照★ | git ls-remote origin refs/heads/<存在せぬ枝> | 0 | 0 行 | ― |

★50 の〆 ―― ★命の順で彫つた★(裁333611 ㋓)★
刻 = 2026-09-18T20:45:08+0900 ／ 枝 = ★ashigaru-mac-2/km-186-futago-no-kesu-jun-20260918★ ／ 場 = /Users/momizimac/wt/a2-km186(己の worktree) ／ 固定 = 6bde7170ce574090a6139ba2dfe3aa4cb6db8634

★順(一字も入れ替へて居らぬ)★
  〇 共用樹の姿を再現   ―― 小文字の名を開くと 2596 bytes ／ blob e6de627bd62e… ／ inode 26293928
  ⑴ git rm --cached <大文字> ―― 後の disk = 2596 bytes ／ inode 26293928(★disk は動いて居らぬ★)
  ⑵ git checkout -- <小文字> ―― 後の disk = ★3471 bytes★ ／ blob ★de00cbd99d9909f4a923041ae17f0d2cbb587668★
  ⑶ 検め(assert は ★彫りの前★)
      ・bytes = 3471 = ★3471★                     ―― 合
      ・blob sha1(己で計算) = de00cbd99d9909f4a923041ae17f0d2cbb587668 ―― ★de00cbd9…★ 合
      ・porcelain = ★D  docs/runbooks/ERR-EKARTE-001.md★ ―― ★大文字の D 一行のみ・小文字の M は消えた★
        ★陽性対照★: 同じ器が ⑵の前には ★ M docs/runbooks/err-ekarte-001.md★ と刷つた(∴ 器は M を刷る能を持つ)
      ・index に載つた変化 = ★D docs/runbooks/ERR-EKARTE-001.md の一行のみ★
  ⑷ git commit(★素の commit ―― index の儘★) ―― rc = 0

★彫つた物★
  HEAD = ★4cb05b976ec0060796840e02dd579f1551d89841★ ／ tree = dd0e82c50326b9e258478c32807c42f0a4ccb5c9
  樹の中の双子 = ★1 本★ ―― 100644 blob de00cbd99d9909f4a923041ae17f0d2cbb587668 ⇥ docs/runbooks/err-ekarte-001.md
  4cb05b97 fix(runbooks): ★双子の片方を消す ―― 大文字 ERR-EKARTE-001.md を樹から外す★(委員長裁 seq333611) ⏎  docs/runbooks/ERR-EKARTE-001.md | 79 ----------------------------------------- ⏎  1 file changed, 79 deletions(-) ⏎
  彫つた後の porcelain(docs/runbooks) = ★★空★★

★未 push の證(★0 行では証せぬ★ ∴ 三役で書く)★
  ・陽性対照 `git ls-remote origin refs/heads/main`      = ★1 行★(rc=0) ―― ★器は届いて居る★
  ・当の枝   `git ls-remote origin refs/heads/<当枝>`    = ★0 行★(rc=0) ―― ★未 push★
  ・負対照   `git ls-remote origin refs/heads/<無き枝>`  = ★0 行★(rc=0) ―― 無い物は 0 行

★⑷ の形について(★命の字義から外した唯一の点★)★
  ・命は「`git add -f` の後 `git commit --only <同じ path>`」と在る。
  ・然し此の双子では ★字義通りでは彫れぬ★ ―― `--only <大文字>` も `add -f`+`--only` も
    ★rc=1「no changes added to commit」で HEAD が動かなかつた★(40/41 の実測)。
    因 = `--only` は worktree の其の path を読み直すが、case を畳む disk では ★大文字の名がまだ開ける★ 故。
  ・∴ ⑷ のみ ★素の `git commit`★ を用ゐた。★index には D 一行しか載つて居らぬ事を先に assert して居る★。
  ・★共用樹では素の commit を打たぬ★(他席の staged を呑む)。此処は ★己が切つた己の枝★ である。
  ・★家老の御下知を仰ぐ★ ―― 便で名指しする。

★此の數が意味せぬ事★:
  ・彫つた事は ★PR が在る事を意味せぬ★。push も gh も打つて居らぬ(裁332449・km-172㋕⑶)。
  ・「双子 1 本」は ★此の枝の tree の話★ であり、★main の話ではない★。main には一指も触れて居らぬ。
  ・case を区別する Linux で此の commit が如何に見えるかは ★測れぬ★(㋕) ―― 彼方では二本とも
    ★別々の file として存在して居る筈★ だが、★此の disk からは確かめられぬ★。

## ㋔ 直しの案と ★戻し方★

紙 = `60_teian.md`(束の頂) ―― 何を／何故／★如何に戻すか(三通り)★／此の案が直さぬ事／判定と merge の路。

## ㋕ ★測れぬ物★

★65 ―― ★測れぬ物を名指す★(km-186 ㋕)★
刻 = 2026-09-18T20:47:09+0900 ／ 根 = /Users/momizimac/multi-agent-shogun
★以下は「無い」ではなく「★此の席の器では測れなんだ★」である。推し量りで埋めて居らぬ。★

★一 case を区別する OS(Linux)側の姿 ―― ★測れぬ★★
  ・second_pc(Ubuntu)・third_pc の disk では、二つの名は ★別々の二本の file として存在する筈★ である。
  ・然し當席は ★Mac の disk しか持たぬ★。★「筈」を数に書き換へる術が無い。★
  ・∴ 「彼方では 2 本」と ★書かぬ★。★測れぬ★ と書く。
  ・測る手 = 彼方の席が `ls -li docs/runbooks/ | grep -i ekarte` と `wc -c` を打てば一行で出る。
    ―― ★當席は他席の樹に一指も触れぬ★ 故、己では打たぬ。

★二 共用樹の disk が何故 旧版(2596B)を抱くか ―― ★未測★★
  ・鮮な checkout では ★新版(3471B)が勝つ★ と実測した(raw/35_shime.txt)。
  ・∴ 共用樹の 2596B は ★鮮な checkout の結果ではない★。★何時・何の操作で入れ替はつたかは歩いて居らぬ。★
  ・★推さぬ★ ―― merge か checkout か手作業か、数が無い。

★三 他席の作業樹・未 commit の変更に大文字を指す物が在るか ―― ★測れぬ★★
  ・禁(km-172 ㋕⑴)により ★他席の箱と樹に一指も触れぬ★。
  ・∴ 「0」とも「在る」とも書かぬ。

★四 ref の先より奥(history)に双子が在るか ―― ★歩いて居らぬ★★
  ・15 が歩いたのは ★ref の先(tip)378 本・別々の樹 306 本★ のみ。
  ・★tip でない commit は一つも歩いて居らぬ。★ ∴ 「history に 0 組」とは書けぬ。

★五 `.md` の付かぬ `ERR-EKARTE-001` 19 当りの「意図」―― ★測れぬ★★
  ・字面は ★error code★ である。然し ★書いた者が file を指す積りであつたか★ は字から出ぬ。
  ・∴ 器は ★.md が付くか否か★ で分けた。是は ★意図の近似★ であり ★意図そのものではない★。

★六 此の紙が意味せぬ事★:
  ・「測れぬ」は ★調べ得ぬ★ の意ではない ―― ★當席の禁と器の届く範囲の外に在る★ の意である。
  ・一〜五の孰れも、★他席が一行打てば数に成る★。★其の一行を當席が打たぬのは禁による。★

## ㋖ 便 ―― 19 通(家老 15 通・軍師 4 通)

| 便 | seq | 読み返しの rc | 送つた胴の字 | 臺帳が返した全文の字 | 判 |
|---|---|---|---|---|---|
| a_census186 | 333987 | rc=0 | 送=264字 | 臺帳の出=725字 | ★丸ごと在り★ |
| b_disk186 | 333988 | rc=0 | 送=299字 | 臺帳の出=760字 | ★丸ごと在り★ |
| c_canon186 | 333989 | rc=0 | 送=280字 | 臺帳の出=741字 | ★丸ごと在り★ |
| d_gyaku186 | 333991 | rc=0 | 送=294字 | 臺帳の出=754字 | ★丸ごと在り★ |
| e_hori186 | 333992 | rc=0 | 送=294字 | 臺帳の出=755字 | ★丸ごと在り★ |
| f_only186 | 333993 | rc=0 | 送=294字 | 臺帳の出=755字 | ★丸ごと在り★ |
| g_teian186 | 333994 | rc=0 | 送=285字 | 臺帳の出=746字 | ★丸ごと在り★ |
| h_hakarenu186 | 333995 | rc=0 | 送=279字 | 臺帳の出=740字 | ★丸ごと在り★ |
| i_fudou186 | 333996 | rc=0 | 送=274字 | 臺帳の出=735字 | ★丸ごと在り★ |
| i_pr186 | 333997 | rc=0 | 送=294字 | 臺帳の出=755字 | ★丸ごと在り★ |
| j_uchiwake186 | 334020 | rc=0 | 送=197字 | 臺帳の出=658字 | ★丸ごと在り★ |
| k_osame186 | 334081 | rc=0 | 送=293字 | 臺帳の出=754字 | ★丸ごと在り★ |
| l_ato186 | 334108 | rc=0 | 送=279字 | 臺帳の出=740字 | ★丸ごと在り★ |
| m_kotei186a | 334137 | rc=0 | 送=248字 | 臺帳の出=709字 | ★丸ごと在り★ |
| m_kotei186b | 334138 | rc=0 | 送=258字 | 臺帳の出=719字 | ★丸ごと在り★ |
| kansa186a | 333998 | rc=0 | 送=297字 | 臺帳の出=762字 | ★丸ごと在り★ |
| kansa186b | 333999 | rc=0 | 送=279字 | 臺帳の出=744字 | ★丸ごと在り★ |
| kansa186c | 334000 | rc=0 | 送=216字 | 臺帳の出=681字 | ★丸ごと在り★ |
| kansa186d | 334082 | rc=0 | 送=281字 | 臺帳の出=746字 | ★丸ごと在り★ |

★丸ごと在り = 19／19★ ―― 「rc=0」は届いた事しか言はぬ故、★臺帳から読み返して★ 胴の逐語を突き合はせた。
控 = `raw/90_okuri.txt`(送り)／`raw/95_yomikaeshi.tsv`(読み返し)／`raw/90_dou_<便>.txt`(送つた胴)。

## ★境★ の證 ―― 共用樹は不動

★99 の〆 ―― ★共用樹は動いて居らぬ★★
刻(後) = 2026-09-18T20:47:52+0900 ／ 根 = /Users/momizimac/multi-agent-shogun ／ 枝 = ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917
前の測り = raw/30_kyouyou_mae.txt(刻は其の紙の冠に在る)

| 見る物 | 撃つ前 | 撃つた後 | 判 |
|---|---|---|---|
| HEAD | d8e3aa58b9eeac6f97f0d60928fbdc40c7c93f11 | d8e3aa58b9eeac6f97f0d60928fbdc40c7c93f11 | ★不動★ |
| index(`git ls-files -s` の sha256) | 7425522328c8eca4efa6f25c0bc3657bdff208dea4331ab4200862eaaa562738 | 7425522328c8eca4efa6f25c0bc3657bdff208dea4331ab4200862eaaa562738 | ★不動★ |
| porcelain 行数 | 1036 | 1036 | ★不動★ |

rc = HEAD 0 ／ ls-files 0 ／ status 0(★管を通さず returncode から取つた★)

★此の間に當席が打つた git の命★:
  ・`git worktree add`(己の場を切るのみ ―― ★共用樹の HEAD も index も動かさぬ★) × ★7 本★
    ―― a2-km186-gyaku / t1 / t2 / t3 / t4 / t5 / a2-km186(★己の物のみ★)
  ・読取(`ls-tree` `cat-file` `show` `ls-files` `status` `ls-remote` `for-each-ref`)
  ・★彫りと消しは悉く己の worktree の中★(50_hori.tsv / 35_gyaku.tsv / 40,41_shiken*.tsv)

★此の數が意味せぬ事★:
  ・porcelain の行数が同じ事は ★中身が同じ事を意味せぬ★(追跡外 dir は一行に畳まれる ―― 中で紙が
    増減しても行数は動かぬ)。★∴ 併せて HEAD と index の sha を書いた。★
  ・當席の束(docs/evidence/…)は `.gitignore:7` の裸 `*` に捕まる ―― ★書いても porcelain は黙る★。
    是は ★書けて居らぬ事を意味せぬ★。
  ・器の言(status err) = warning: could not open directory 'queue/reports/ashigaru-mac-3_km-sakai-wa-dare-ga-hiku-noka_20260912_evidence/sakai/nanmon/n13_noaccess_dir/': Permission denied

## ★此の紙の數が意味せぬ事★

 ・母數 548 と 組 1 は ★固定 commit 6bde7170… の樹★ の話である。★disk の數でも、歴史の數でもない。★
 ・ref 378／樹 306 で組が 1 の儘なのは ★tip のみ★ を歩いた結果である。★過去の commit は一つも歩いて居らぬ。★
 ・★組=0 の 41 本は「双子が消された」の意ではない★ ―― 其の樹に元から此の紙が無いだけである(因は未測)。
 ・canon の 4 当りは ★字面の數★ であり、★書き手の意図を測つた物ではない★(㋕ 五参照)。
 ・彫り rc=0 は ★己の枝に載つた★ の意であり、★merge された事も・PR が在る事も意味せぬ★(remote は 0 行)。
 ・共用樹の porcelain 1036 行の一致は ★行の數の一致★ であり、★中身の一致を証して居らぬ★(99 の紙に明記)。
 ・★Linux(case を区別する側)で此の双子が如何に見えるかは、當席の器では測れぬ。★
