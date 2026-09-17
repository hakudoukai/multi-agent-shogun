門控: 第四走(臺帳へ本紙と raw2/・driver 85/86/87 を append した後・`_gate/km97_hashiri4_*`)は★此の紙の後に生れる★ゆゑ rc は此処に書けぬ ―― commit message と納め便に書く。第三走(README 追記後)= `_gate/km97_hashiri3_20260917T143713` rc=0 / 母數 92 / 條①一致 92・相違 0・実体無 0 / 條②③④ 72 本通 / 條⑤ byte和 1340864。

# km-97 追録 ―― REVISE の治し(束を commit の中へ据ゑる)

- 席 = ashigaru-mac-1 / 親 = km-97(`README.md`・提出 14:42)/ 治しの指示 = 家老mac `msg_20260917_160308_ac0b6553`(16:03・軍師mac の REVISE 三点を家老が PR#20 で解いた筋を渡した物)。
- 軍師mac の指摘三つ ⑴束 untracked ⑵固定 commit/tree に束が無い ⑶到達 ref 無し ―― は ★紙の中身の疵ではなく「束が commit の中に無い」一事★ から出て居る(家老の読み・當席も同じ読み: `git ls-files -- <束>` = 0 本・`git status --porcelain` = `??`)。

## 治し① 頭を固定して器を再走(`driver/85_saisou.sh` → `raw2/`)

- ★提出済 `raw/` は一指も触れて居らぬ★: 再走の前に 76 本の sha256 を焼き(`raw2/01_raw_mae_sha.txt`)、再走・正規化・gzip の後に再び焼いて(`raw2/01_raw_ato_sha.txt`)cmp rc=0(`raw2/91_raw_fudou.txt`)。「戻す」必要が無かつた ―― 書かなかつたからである。
- 頭(`raw2/00_atama.txt`): 歩いた disk の HEAD = `260f2a066007136e7084a1e411f8555b3f12c9c1`(共有 worktree の枝 ashigaru-mac-3/km-51・當席が動かした物ではない)/ 據ゑる親 = `4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1` = origin/main(同=yes)/ untracked 37 口・変更 998 口 / 門 sha16 d2265a07e232eb0b(409 行・14:04:14・提出時と同一)。
- 器 12 本の rc 悉く 0(`raw2/02_driver_rc.txt`)。比較表 64 行・測れぬ 0(`raw2/90_hikaku.txt`・器 `driver/87_hikaku.py`・自己対照 raw 対 raw で 64 行 差 0 を先に確かめた)。

| 項 | 前(raw 14:18〜14:26) | 後(raw2 16:10〜16:13) | 差 | 差の正体 |
|---|---|---|---|---|
| R1 repo files / hits | 10060 / 1005 | 11092 / 1117 | +1032 / +112 | hits の増分 112 は ★悉く 紙★(60 R1 紙 631→743・器 35=35・控 310=310・試 29=29)。docs/evidence の hit 531→643(+112)。内 ★己の束 2→36(+34)★ |
| R2 ~/bin | 78 / 7 | 79 / 7 | +1 / 0 | 器 6=6 |
| R3 ~/.claude | 7175 / 3591 | 同 | 0 | ― |
| R4 LaunchAgents | 25 / 0(grep rc=1) | 同 | 0 | 陰性の儘 |
| R5 hermes | 185557 / 713 | 185592 / 718 | +35 / +5 | 控 +3・紙 +2・★器 1=1★ |
| 陽性対照(門 自身が R1 hits に) | 8 行 | 8 行 | 0 | 同じ器 /usr/bin/grep -c -F |
| 20 ps 母數 / hits | 755 / 17 | 751 / 17 | −4 / 0 | 稼働 watcher の写しは同数 |
| 30 逐語行 files / lines | 68 / 778 | 68 / 778 | 0 | 入力 list(`raw/12_utsuwa_list.txt`)不変ゆゑ同一・★実体無★ 0 |
| 35 第二歩き files/any/first/丁候補 | 253/121/45/76 | 254/121/45/76 | +1/0/0/0 | ― |
| 40 箱 / 生pane / 正名 / 異名未知 / 読点 | 19/7/7/11/1 | 同 | 0 | 箱は一つも生れて居らぬ |
| 50 門の実走 ①〜⑦ rc | 69,69,69,0,0,0,0 | 同 | 0 | 名列 sha16 前後同=yes・門 sha 同 |

- ★結は動かぬ★: 甲 14 器(R1 35 + R2 6 + R5 1 の内の門を呼ぶ物)/ 門外 5 器 6 行 / 箱 19 本 / 穴三つ ―― 前後で「器」の数が一つも変はらぬゆゑ、README の結(1〜5)は再走の後も其の儘立つ。

### 數が何を意味せぬか

- 差(後−前)は ★disk の時差★であつて「此の枝が変へた物」では★ない★。歩くのは disk(HEAD の tree + untracked 37 + 変更 998)であり、二時間の間に他席の束(docs/evidence)が増えた分が紙に載つた。
- 己の束 36 hit は path の prefix(`./<束>/`)で除いた(`raw2/03_jiko.txt`・除いた後 1081)。process の己の系譜は字面で除けぬが、path は除ける ―― 二つは別物。
- 「頭を固定」の意は ★歩いた時の HEAD を紙に焼いた★ こと。出目が HEAD 一つに縛れる訳ではない(untracked/変更が混じる)。commit の中で再現したければ、其の commit を checkout した clean な樹で走らせよ(當席は checkout 禁ゆゑやらぬ・やつて居らぬ)。
- 20 の母數 −4 は process の出入りであり、器の稼働数(hits 17)は同じ。

## 治し② 臺帳は append のみ(`scripts/checks/karo_mac_manifest_append.py`・唯一の書き手)

- `cd <束>` してから呼ぶ(束内相対・裁 seq322699)。既存 92 行は `cmp` で byte 不動を證す(`_gate/90_append4_*.cmp`)。足す物 = 本紙 + `driver/85_saisou.sh` `driver/86_sueru.sh` `driver/87_hikaku.py` + `raw2/*`(99 本・.nul.gz と 0byte も載せる・argv からは宣して除く=第四の道)。
- 門は `KM_GATE_MANIFEST_BASE=.` を要する(usage 冠に無い env・km-96 の結)。

## 治し③ 束を新枝へ据ゑる(`driver/86_sueru.sh`・plumbing のみ)

- ★なぜ新枝か★: km-97 の枝は手許にも遠隔にも無い(`git branch --list '*km-97*'` = 0・`git branch -r` = 0)。∴ 「同じ枝へ据ゑる」の「同じ」は ★此の札の名の枝★ を新設する事。枝名 = `ashigaru-mac-1/km-97-hako-wo-umu-michi-wa-ikutsu-aruka-20260917`(一字も縮めぬ)。
- ★なぜ親が origin/main か★: 束は紙のみで code を一行も変へぬ ∴ origin/main 直上が最も衝突無く着地する。同組の km-101/102 の枝も同じ親(4be3ee19)である。km-92 の枝(0260a76・fix commit 463c388c を含む)を親にすると、着地に他の直しを道連れにする。
- 仮 index(`GIT_INDEX_FILE`)に `read-tree 基点` → 束の全 file を `hash-object -w` + `update-index --add --cacheinfo` → `write-tree` → `commit-tree -p 基点` → `update-ref <枝> <新> 零40`(零40 = ★新設專用★・既存枝なら落ちる)。共有 worktree の HEAD と index は触れぬ(checkout 無し・`git add` 無し)。
- 検め: (a) `git -C 根 ls-tree -r --full-tree --name-only <新> -- <束>/` と disk の名列の diff 行 = 0、★出目に README.md が在る事を対照★(無ければ rc=10 で止む ―― 家老が PR#20 で踏んだ「pathspec は cwd 相対ゆゑ 0 本 rc=0」の疵を先に塞ぐ)/ (b) file 毎に `rev-parse <新>:<path>` の blob id と `hash-object <path>` の異 = 0 / (c) `merge-base --is-ancestor 基点 新` rc=0・`rev-list --count` = 1 / (d) `rev-parse <枝>` の読み戻し。出目 = `_gate/86_sueru_<TS>.txt`(己の log ゆゑ disk 側の名列から宣して除く・commit の後に生れる=commit の外)。
- .gitignore(7 行目 `*` の白名簿式)は raw/ を ignore して居る(`git check-ignore` = `.gitignore:7:*`)が、plumbing は ignore を読まぬ ∴ 束は全 file が tree に入る(km-92 の枝と同じ形)。

## 治し④ push は總監督の代行が正路 ―― 當席は commit まで

- 納め便(300 字)に「枝 <實の ref 名>＝<新 sha>」+ 再走の數(前→後)+ 門 rc + 到達(紙 n/n)を書く。便の長さ(python3 len)は `_gate/99_fumi_len_*.txt` に焼く(commit の後に生れるゆゑ束の外・臺帳の外)。
- CI は要件から外れた(dev_qa#1099・裁 seq326349)ゆゑ緑を待たぬ。

## 禁の遵守

- 箱へ書いたのは 納め便 1 通(門経由・karo-mac)と己の箱の既読印 1 件のみ。50 の再走は IW_NAME_TEST_ONLY=1(門 L75 止まり)で箱の名列 sha16 前後同。
- checkout/merge/rebase/cherry-pick/push/fetch 無し。refs の書換は ★新枝の新設 1 件のみ★(家老の指示 ③ の範囲・旧値 零40 で既存枝には落ちぬ)。他席の pane を覗かず。提出済 raw/ 76 本 不動(cmp rc=0)。
