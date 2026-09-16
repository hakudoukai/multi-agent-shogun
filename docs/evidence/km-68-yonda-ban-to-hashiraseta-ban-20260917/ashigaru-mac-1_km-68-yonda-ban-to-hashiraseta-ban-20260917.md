# 第68弾 ―― 讀んだ版と走らせた版が違へば、行番号は正しい顔をして嘘を吐く ―― 版刻器で構造的に塞ぎ、第67弾の ㋓ を引き直し、P6 の反転・rc の管・兩席の四數・錠の外を測る(読取のみ・生器へ 0 字・他席の束へ 0 字)―― 答を先に(★數の出處 = raw/20_hanban.py(版刻器)+ 20_hanban_verify.txt/20_hanban_wt.txt / raw/21_otsu1.{txt,tsv} / raw/30_p6.{txt,tsv} + 30_rule_diff.txt + 30_rule_verbatim.txt + raw/p6/ / raw/33_rc_pipe.{txt,tsv} + .first + .second + raw/fixture/ / raw/35_yotsu.{txt,tsv} / raw/37_jou.txt + .first / raw/00_start.txt(起・宣・★則の逐語★)/ _after/96_after.txt(門の後の實走 ―― 紙の後に生れる故 紙は其の数を書けぬ・期待のみ書く)★)

★臺帳の基点(一行)★: 本束の臺帳 `ashigaru-mac-1_km-68-yonda-ban-to-hashiraseta-ban-20260917_manifest.txt` の path は ★main 樹の根 `/Users/momizimac/multi-agent-shogun` からの相對★(append.py を cwd = main 樹で呼ぶ故)。worktree の根 `.claude/worktrees/karo-mac-a1/` に立つて照合すれば ★悉く実体無★ と出る ―― disk の欠けではなく基点の違ひ。worktree の根から引くなら頭の `.claude/worktrees/karo-mac-a1/` を落とせ(家老が本夜踏んだ穴・第67弾の臺帳も同じ基点)。

★答★: ㋐ 版刻器 raw/20_hanban.py ―― 走らせる★直前★に realpath / sha16 / 総行数 / git blob vs HEAD / 指す行の本文を刷り、其れらを繋いだ正準文字列の sha16 を ★版札v1 の封★ にする(專任3 の四数札と同じ形 ―― 抜き書きすれば封が合はぬ)。21 は讀手 verify.py を ★20 の Han.module()(讀んだ bytes を其の儘 compile して exec)越しにのみ★ 走らせ、settrace の行番号を ★同じ bytes★ の行本文へ引き当てる ∴ 讀む物と走らせる物が同一物で「讀んだ版≠走らせた版」は構造で起り得ぬ(憶えるのではない)。main 樹 verify.py = 198 行 a507c998c7bd6485・★違ふ=汚れて居る(disk ≠ HEAD)★・封 3bbd1e2233956044 / worktree 写し = 127 行 bbde471f70848fc8・封 c329345698fec007: 198 行の L133/139/152/158/160 は 127 行に ★無く★、127 行の L76/82/95/101/103 は 198 行で ★別の文★ ―― 之が嘘の顔。引き直し(21): mini 26 本 一本づつ A/B/C 同 26 / 違 0 / 母數 26。乙1 139 = 19 / 133 = 4 / 乙5 152(A) = 3 → 158(B) = 3 = 第67弾の 19/4/3/3 と ★同じ数★。★同じ数が出た事も、器を通して初めて言へる★(67 の二走目は cat -n で手置き・68 は走らせた bytes)。㋑ P6: 同じ fixture で 則一(41 = 40 から ctime 一行を外した再現) rc 0 → 則二(40) rc 1 = ★反転★・何で後 = c のみ ∴ ★ctime が救つた★。錠の順は別の物を救つた: L1a(歩哨→錠) 41 rc 0 / 40 rc 1(錠の chmod が ctime で鳴る)・L1b(錠→歩哨) 41 rc 0 / 40 rc 0。㋒ rc が管を渡る箇所(33・三走): 母數 file 316 / 当たり 4 = ★実行 0★ + 文 4 / 己の産物 153(自己参照)/ 陽性対照 2 鳴・陰性 黙。㋓ 兩席の器: 專任3 71_yotsu.py(6e5f66b63404bae1)の fuda で 乙1 23 本 A 合 23 割れ 0 / B 合 23 割れ 0・乙5 3 本 合 ―― 133 の 4 本は四数札 ['0/0/0/0/0'] = ★母數 0 でしか言へず「何行を跳んだか」の欄が無い(欄の欠・盲ではない)★。㋔ 錠の外: hook 6 / process 447 / scripts 80 / launchd 16 の内 raw/ へ ★錠を外さずに★ 書ける経路 = ★0★。git は讀み系 rc 0・書き系(checkout / rm / restore)は unlink で EACCES。同 uid の chmod と root は塞がぬ(chmod は ctime が痕・root は測れぬ)。

## 0. 断(先に)
1. **★行番号は版に属する。版を刻まぬ行番号は数ではない。★** 20 は sha16・総行数・blob・本文を一つの封に縛る。封の違ふ二つの版(a507c998 / bbde471f)に同じ行番号を当てれば、本文は「無い」か「別の文」になる(§1 の二表)。
2. **★讀んだ版≠走らせた版 を「出来なく」したのは順序ではなく同一性である。★** 21 は path を二度讀まぬ ―― 一度讀んだ bytes を compile し、同じ bytes を行に割る。器が別の版を讀む余地が無い。
3. **★第67弾の 19/4/3/3 は本弾でも 19/4/3/3。★** 然し此の「同じ」は本弾で初めて器が言へた ―― 第67弾は手で置いた行番号が偶々合つて居た(main 樹の版が此の 4 時間で変つて居らぬ故)。版が動けば同じ手順が違ふ数を出す。
4. **★P6 を救つたのは ctime であつて錠の順ではない。★** 41(則一) 黙 → 40(則二) 鳴 の反転を同じ fixture で見た。錠の順の変更は「ctime を足した事で錠自身が鳴る」副作用を消す為の物で、P6 とは別の物を救つた(L1a/L1b)。
5. **★rc が管を渡る「実行」の箇所は両束の器に 0。★** 当たり 4 は悉く「文」(紙・則・f-string の中で管を語る行)。第67弾 §7-3 の疵は束の器に無く席の手(對話の入力)に在つた ―― 此の器は其れを數へぬ(§3)。
6. **★兩席の器は同じ現物で割れなかつた。★** 26/26 で settrace の落ちる行と四数札が対応する。割れる余地が在るとすれば 133(sha256= 無)―― 四数札は母數 0 でしか言へず、跳んだ行を名指す欄が無い。
7. **★錠が塞いだのは「錠を外さずに書く」だけ。★** 外の書き手(hook/process/scripts/launchd)に raw/ へ書く実行行は 0。同 uid の chmod と root は塞がぬ ―― chmod は ctime で 40 が數へ、root は測れぬ。
8. **★己の疵は起の時点で 2、終りで 4。★**(§7)

## 1. ㋐ 版刻器 20 と引き直し 21
### 1.1 版刻(走らせる直前に刷る・逐語)―― main 樹の讀手を worktree の写しに当てる
  ★版刻(走らせる直前)★ realpath /Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_manifest_verify.py
    sha16 a507c998c7bd6485 / 総行数 198 / mtime 2026-09-17T00:01:41 / git blob ebfc4c0ecc080c0f vs HEAD b19ec9ea259653d9 → ★違ふ=汚れて居る(disk ≠ HEAD)★ 枝 main 根 /Users/momizimac/multi-agent-shogun
    L133:             continue
    L139:             unreadable += 1
    L152:             miss += 1
    L158:             ok += 1
    L160:             ng += 1
  版札v1 sha16=a507c998c7bd6485 lines=198 blob=ebfc4c0ecc080c0f head=b19ec9ea259653d9 行=133,139,152,158,160 封=3bbd1e2233956044
  --against(別の版) /Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1/scripts/checks/karo_mac_manifest_verify.py sha16 bbde471f70848fc8 / 総行数 127 / 同じ=commit 済 枝 karo-mac/a1-r56 根 /Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1
    L133: ★違ふ★ | 別の版: ★133 行目は無い(総行数 127)★
    L139: ★違ふ★ | 別の版: ★139 行目は無い(総行数 127)★
    L152: ★違ふ★ | 別の版: ★152 行目は無い(総行数 127)★
    L158: ★違ふ★ | 別の版: ★158 行目は無い(総行数 127)★
    L160: ★違ふ★ | 別の版: ★160 行目は無い(総行数 127)★

### 1.2 逆向き ―― worktree の写し(127 行)を main 樹(198 行)に当てる = 第67弾 一走目の形
  ★版刻(走らせる直前)★ realpath /Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1/scripts/checks/karo_mac_manifest_verify.py
    sha16 bbde471f70848fc8 / 総行数 127 / mtime 2026-09-16T21:34:43 / git blob b19ec9ea259653d9 vs HEAD b19ec9ea259653d9 → 同じ=commit 済 枝 karo-mac/a1-r56 根 /Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1
    L76:             continue
    L82:             unreadable += 1
    L95:             miss += 1
    L101:             ok += 1
    L103:             ng += 1
  版札v1 sha16=bbde471f70848fc8 lines=127 blob=b19ec9ea259653d9 head=b19ec9ea259653d9 行=76,82,95,101,103 封=c329345698fec007
  --against(別の版) /Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_manifest_verify.py sha16 a507c998c7bd6485 / 総行数 198 / ★違ふ=汚れて居る(disk ≠ HEAD)★ 枝 main 根 /Users/momizimac/multi-agent-shogun
    L76: ★違ふ★ | 別の版:         if tok.startswith("sha256=") or tok.startswith("bytes=") or tok.startswith("lines="):
    L82: ★違ふ★ | 別の版:     return out
    L95: ★違ふ★ | 別の版:     #   引数で基点を渡した時は其れを尊ぶ(従来通り・明示は cwd 相対で宜しい)。
    L101: ★違ふ★ | 別の版:         _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    L103: ★違ふ★ | 別の版:                  os.path.join(_root, "queue", "reports") + os.sep,

### 1.3 引き直し(21)―― mini 26 本(第67弾 raw/otsu1/lines/・讀むのみ)を 20 越しに走らせ、第67弾 tsv の落ちる行と一本づつ突き合はす
| 山 | 臺帳 | 行 | A 67→68 | B 67→68 | C 67→68 | 68 出目A | 68 本文(走らせた bytes) |
|---|---|---|---|---|---|---|---|
| 乙5 | ashigaru-mac-2_B0_axis2_20260… | 24 | 152→152 同 | 158→158 同 | =B→=B 同 | 0/0/1/0 | `miss += 1` |
| 乙5 | ashigaru-mac-2_B0_axis2_20260… | 16 | 152→152 同 | 158→158 同 | =B→=B 同 | 0/0/1/0 | `miss += 1` |
| 乙5 | ashigaru-mac-2_B0_axis2_20260… | 20 | 152→152 同 | 158→158 同 | =B→=B 同 | 0/0/1/0 | `miss += 1` |
| 乙1 | ashigaru-mac-2_B2_30_20260907… | 12 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_30_20260907… | 4 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_30_20260907… | 5 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_30_20260907… | 3 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_30_20260907… | 7 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_30_20260907… | 11 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_30_20260907… | 8 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_30_20260907… | 9 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_30_20260907… | 6 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_30_20260907… | 10 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_31_20260907… | 7 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_31_20260907… | 8 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_31_20260907… | 11 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_31_20260907… | 4 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_31_20260907… | 3 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_31_20260907… | 6 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_31_20260907… | 9 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_31_20260907… | 5 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | ashigaru-mac-2_B2_31_20260907… | 10 | 139→139 同 | 139→139 同 | 139→139 同 | 0/0/0/1 | `unreadable += 1` |
| 乙1 | karo_mac_B0_10_kizai_hozen_20… | 1 | 133→133 同 | 133→133 同 | 133→133 同 | 0/0/0/0 | `continue` |
| 乙1 | karo_mac_B0_10_kizai_hozen_20… | 3 | 133→133 同 | 133→133 同 | 133→133 同 | 0/0/0/0 | `continue` |
| 乙1 | karo_mac_B0_10_kizai_hozen_20… | 5 | 133→133 同 | 133→133 同 | 133→133 同 | 0/0/0/0 | `continue` |
| 乙1 | karo_mac_B0_10_kizai_hozen_20… | 4 | 133→133 同 | 133→133 同 | 133→133 同 | 0/0/0/0 | `continue` |
- 一本づつ 悉く同じ 26 / 違ふ 0 / 母數 26。乙1 139 = 19 / 133 = 4 / 乙5 152(A) = 3 → 158(B) = 3。
- ★行番号→本文の検め★: 21 は走らせた bytes で L133='continue' / L139='unreadable += 1' / L152='miss += 1' / L158='ok += 1' / L160='ng += 1' を確かめてから settrace に入る ―― 版が違へば此処で落ちる(落ちなかつた = 版札 3bbd1e2233956044 の版で走つた)。

## 2. ㋑ P6 の始末(raw/30_p6.txt・fixture raw/p6/・各形を一度建て 41→40 の順に讀むのみで掛けた)
| id | 形 | 真の期待 | 41 期待 | 41 rc | 41 疵 | 41 何で後 | 40 期待 | 40 rc | 40 疵 | 40 何で後 | 41→40 | 判 | 母數 |
| P6 | utime で mtime を前へ戻した新 file(birth が後) | 1 | 0 | 0 | 0 | - | 1 | 1 | 1 | c | 反転 | 合 | 2 |
| L1a | 歩哨→錠(一走目の順) | 0 | 0 | 0 | 0 | - | 1 | 1 | 1 | c | 反転 | 合 | 1 |
| L1b | 錠→歩哨(二走目の順) | 0 | 0 | 0 | 0 | - | 0 | 0 | 0 | - | 同じ | 合 | 1 |
| N1 | 悉く前 | 0 | 0 | 0 | 0 | - | 0 | 0 | 0 | - | 同じ | 合 | 2 |
| P1 | 新 file を後に | 1 | 1 | 1 | 1 | mbc | 1 | 1 | 1 | mbc | 同じ | 合 | 2 |
- P6: e.txt: 歩哨 1789585577343441825 / 戻した後の stat(mtime birth ctime)= 1789585576.343441825 1789585576.343441825 1789585577.343529199 ―― birth が mtime へ締められて居るか(macOS APFS)
- ⑴ 反転: 41 rc 0 → 40 rc 1 = 反転。⑵ 救つた物: 40 の「何で後」は c のみ ―― m も b も刻より前(macOS APFS は utime で mtime を birth より前へ戻すと birth も締める)∴ ★ctime の追加★。錠の順(L1a→L1b)が救つたのは ★錠自身が鳴る副作用★ であり、P6 ではない。形 5 合 / 0 不。
- ⑶ 変更前後の則の逐語(raw/30_rule_verbatim.txt):
      後 = file の mtime_ns > 刻 ★又は★ birth(生れた刻・stat -f %FB)> 刻。同 = mtime_ns == 刻(決められぬ・数へる)。前 = 何れも < 刻。ctime は使はぬ(chmod/rename/cp -p が動かし、中身の書込みと区別できぬ)。歩く = os.walk・lstat・S_ISREG のみ(非通常は数へて宣す)。母數 0 なら rc 2(★歩いて居らぬ = 通でも鳴でもない★)。後 ∧ 宣に無い ≥ 1 なら rc 1(鳴)。後 ∧ 宣に在る のみなら rc 0。宣 = fnmatch(brace {a,b} は展開)。
    ★則を一つ変へた(一走目の後・42 P6 が黙つた故)★: 一走目は ctime を使はなかつた(chmod/rename が動かす故)。然し macOS は utime で mtime を birth より前へ戻すと birth も其処へ締める ∴ 前へ戻された新 file は mtime/birth では見えず、ctime(utime も今へ動かす)でしか見えぬ。∴ ctime を足し、錠(chmod)は歩哨の ★前★ に掛ける順へ変へた(錠が後なら錠自身が鳴る = L1 一走目の形)。一走目の出目は *.first.* に残す。
- 器の差 = raw/30_rule_diff.txt(diff -u 40 41・差の核は `later = mns > A or bns > A or cns > A` → `later = mns > A or bns > A` の一行 + 頭註の名札 2 箇所)。★41 は再現であり第67弾 一走目の器其の物ではない★(一走目は器を file に残さず出目 .first のみ残した ―― 之は第67弾の疵として本弾で数へる・§7)。

## 3. ㋒ rc が管を渡る箇所(raw/33_rc_pipe.txt・三走・母數 = 両束の全通常 file)
- ## 陽性対照: 33_positive.sh(乙) 鳴つた / 33_positive.py(甲) 鳴つた / 陰性対照 33_negative.sh 黙つた
- 当たり(対照・己・己の産物を除く) 4 = ★実行 0★ + 文 4:
  [文(紙)] 乙 pipe→$? docs/evidence/km-67-mon-no-ato-20260917/ashigaru-mac-1_km-67-mon-no-ato-20260917.md:143  3. 45 の rc を `| head` の後の `$?` で讀んだ(pipe 越し)―― 45_km66.rc(10_run 直採)が正。
  [文] 乙 pipe→$? docs/evidence/km-67-mon-no-ato-20260917/raw/70_paper.py:102  3. 45 の rc を `| head` の後の `$?` で讀んだ(pipe 越し)―― 45_km66.rc(10_run 直採)が正。
  [文] 甲 shell=True+| docs/evidence/km-68-yonda-ban-to-hashiraseta-ban-20260917/raw/00_start.py:27  '㋒ rc が管を渡る箇所 33_rc_pipe.py: 母數 = km-67 と km-68 の束の ★全 file★(.py .sh .txt .md .tsv …・非通常は除き数へる)。検出子 = ⑴ python: shell=True の cmd 文字列に | / os.system( / os.popen(
  [文] 甲 system/popen/getoutput docs/evidence/km-68-yonda-ban-to-hashiraseta-ban-20260917/raw/00_start.py:27  '㋒ rc が管を渡る箇所 33_rc_pipe.py: 母數 = km-67 と km-68 の束の ★全 file★(.py .sh .txt .md .tsv …・非通常は除き数へる)。検出子 = ⑴ python: shell=True の cmd 文字列に | / os.system( / os.popen(
- ★三走の理由(器を直した證・.first/.second を載せる)★: 一走目 母數 279 当たり 4(文/実行の札無し)→ 二走目 当たり 26(己の一走目の出目 33_rc_pipe.first.* が己の当たりを逐語で含み ★自己参照で膨れた★・f-string を「実行」と誤札 1)→ 三走目 己の産物 153 を名(己の stem)で札し f-string の token(3.12+ の FSTRING_*)を「文」に入れた。
- 直した実行の箇所 = 0(無かつた)。直さぬ = 文 4(則の記述と紙・測る前に書いた文ゆゑ触らぬ)。km-67 は錠の下・讀むのみ。
- ★數へぬ物★: 對話(shell の入力)で打つた `cmd | head; echo $?` は束に写らぬ限り母數に無い。第67弾 §7-3 の疵は其の形。∴ 本弾の「実行 0」は「束の器に無い」であつて「席の手に無い」ではない。

## 4. ㋓ 兩席の器が同じ四數を出すか(raw/35_yotsu.txt・專任3 71_yotsu.py 6e5f66b63404bae1 を --kikai main 樹 verify.py で・讀む/走らせるのみ・彼の束へ 0 字)
- 71 の --jikenme(彼の対照 6 形): rc 0。乙1 23 本: A 合 23 割れ 0 / B 合 23 割れ 0。乙5 3 本: A 合 3 / B 合 3。
| 山 | mini | 21 落ちる行 A | 71 rc A | 71 四数 A(母/一/相/実/讀) | 封 A | 合否 A | 21 落ちる行 B | 71 rc B | 71 四数 B | 封 B | 合否 B |
| 乙5 | B0_axis2_L24.txt | 152 | 1 | 1/0/0/1/0 | 6984c1053f180bfc | 合(実体無=1) | 158 | 0 | 1/1/0/0/0 | 6dbc44f8cb471f0b | 合(一致=1) |
| 乙5 | B0_axis2_L16.txt | 152 | 1 | 1/0/0/1/0 | 6984c1053f180bfc | 合(実体無=1) | 158 | 0 | 1/1/0/0/0 | 6dbc44f8cb471f0b | 合(一致=1) |
| 乙5 | B0_axis2_L20.txt | 152 | 1 | 1/0/0/1/0 | 6984c1053f180bfc | 合(実体無=1) | 158 | 0 | 1/1/0/0/0 | 6dbc44f8cb471f0b | 合(一致=1) |
| 乙1 | B2_30_L12.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_30_L04.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_30_L05.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_30_L03.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_30_L07.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_30_L11.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_30_L08.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_30_L09.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_30_L06.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_30_L10.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_31_L07.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_31_L08.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_31_L11.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_31_L04.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_31_L03.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_31_L06.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_31_L09.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_31_L05.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B2_31_L10.txt | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) | 139 | 1 | 1/0/0/0/1 | 3aa25d46ae16a6f1 | 合(讀めぬ行=1) |
| 乙1 | B0_10_kizai_hozen_L01.txt | 133 | 1 | 0/0/0/0/0 | 7815d4a7ef831f40 | 合(母數=0) | 133 | 1 | 0/0/0/0/0 | 7815d4a7ef831f40 | 合(母數=0) |
| 乙1 | B0_10_kizai_hozen_L03.txt | 133 | 1 | 0/0/0/0/0 | 7815d4a7ef831f40 | 合(母數=0) | 133 | 1 | 0/0/0/0/0 | 7815d4a7ef831f40 | 合(母數=0) |
| 乙1 | B0_10_kizai_hozen_L05.txt | 133 | 1 | 0/0/0/0/0 | 7815d4a7ef831f40 | 合(母數=0) | 133 | 1 | 0/0/0/0/0 | 7815d4a7ef831f40 | 合(母數=0) |
| 乙1 | B0_10_kizai_hozen_L04.txt | 133 | 1 | 0/0/0/0/0 | 7815d4a7ef831f40 | 合(母數=0) | 133 | 1 | 0/0/0/0/0 | 7815d4a7ef831f40 | 合(母數=0) |
- 対応の條: 139↔讀めぬ行=1 / 133↔母數=0 / 152↔実体無=1 / 158↔一致=1。★133 の 4 本★は四数札 ['0/0/0/0/0'] ―― 「行が母數に入らぬ」を 0 でしか言へず、跳んだ行を名指す欄が無い。settrace(21)は其の行を 133 と名指す。∴ 割れたのではなく ★欄の欠★(專任3 の器も生器も同じ欄で出来て居る)。
- 71 は「★走らせた★ <cmd>」で器の path を刷るが ★sha も行数も刷らぬ★ ―― 本弾の版刻器が足す物は其処。

## 5. ㋔ 錠は本当に塞いだのか(raw/37_jou.txt・二走: 一走目は pgrep の空 pattern で process 母數 0 rc 2 = 器の誤り・.first に残す)
- hook 母數 6 / process 母數 447 / scripts 母數 80 / launchd 母數 16 ―― raw/ へ ★錠を外さずに★ 書ける実行行・process・plist = ★0★(rc 0・根 settings.json / ps -U / scripts/ / ~/Library/LaunchAgents・深さ 1〜2・刻は 37 の各行)。
- git 自身(一時 repo・dir 0555 / file 0444・讀み 4 形・書き 5 形・生 6 形・逐語):
  讀 add -f d/: rc 0 / stdout '' / stderr ''
  讀 hash-object: rc 0 / stdout '626799f0f85326a8c1fc522db584e86cdfccd51f' / stderr ''
  讀 status: rc 0 / stdout 'A  d/untracked.txt' / stderr ''
  讀 diff b: rc 0 / stdout 'd/f.txt         | 2 +-\n d/untracked.txt | 1 +\n 2 files changed, 2 insertions(+),' / stderr ''
  書 checkout b(f.txt を v2 に書き換へる): rc 0 / stdout 'M\td/f.txt\nA\td/untracked.txt' / stderr "error: unable to unlink old 'd/f.txt': Permission denied\nSwitched to branch 'b'"
  書 rm -f d/f.txt(unlink): rc 128 / stdout "rm 'd/f.txt'" / stderr "fatal: git rm: 'd/f.txt': Permission denied"
  書 clean -f d/(untracked を unlink): rc 0 / stdout '' / stderr ''
  書 restore --source=b d/f.txt: rc 255 / stdout '' / stderr "error: unable to unlink old 'd/f.txt': Permission denied"
  書 checkout b 再(直前の失敗後の状態): rc 0 / stdout 'M\td/f.txt\nA\td/untracked.txt' / stderr "Already on 'b'"
  後の状態: d/f.txt = 'v1' / untracked 在る True / 枝 b / d mode 0o555
  生 read open: ★通つた★
  生 write open(w): PermissionError(13)
  生 create open(new): PermissionError(13)
  生 unlink: PermissionError(13)
  生 rename: PermissionError(13)
  生 mkdir: PermissionError(13)
- 第67弾の錠の今(家老の git add -f・commit f955bc3 の後): raw/ mode 0o555 / 通常 file 165 / 0444・0555 でない物 0 ―― 錠は讀みを妨げず、家老の add -f の後も掛かつた儘。
- ∴ ★錠が塞ぐのは open(O_WRONLY|O_CREAT) / unlink / rename / mkdir であつて read ではない。git add -f が通つたのは讀みゆゑ。★ 塞いだのは「門の後に書く病」の内 ★己の器が黙つて書く★ 経路(と外の書き手が黙つて書く経路)。同 uid の chmod(錠を外す)と root は塞がぬ ―― 前者は ctime で 40 が數へ(L1a・第67弾 L3)、後者は測れぬ。

## 6. ㋕ 意味せぬ事(本弾の数が言はぬ事・7)
1. **21 の 26/26 同 ≠ 第67弾の行番号が正しかつた事の證明。** 同じ版(a507c998)が此の間 動かなかつた故に同じ数が出た。版が動けば同じ手順で違ふ数が出る ―― 其の時に初めて 20 の封が「違ふ」と言ふ。
2. **版札の封 ≠ 器の正しさ。** 封は「どの bytes を走らせたか」を縛るだけで、其の bytes が正しい讀手である事は言はぬ(汚れた main 樹の版 = 未 commit の 198 行 を走らせて居る事を、封は隠さず示す丈)。
3. **P6 反転 ≠ 則二が恒真。** 形は 5(P6/L1a/L1b/N1/P1)で、第67弾の 15 形を本弾で悉く再走した訳ではない。ctime は chmod/rename/cp -p でも動く ∴ 則二は「書いた」と「触つた」を分けぬ(第67弾 §6-1 と同じ)。
4. **rc 管 実行 0 ≠ 席が pipe 越しに rc を讀まなかつた事。** 對話の入力は母數に無い。此の器は束を測り、手を測らぬ。
5. **四數 割れ 0 ≠ 二つの器が同じ物を數へて居る事。** 133 の 4 本で兩者は「母數 0」と「133 行で continue」を出す ―― 数は合ふが、片方は行を名指し片方は名指さぬ。合つたのは對応表の側であつて器の側ではない。
6. **錠外経路 0 ≠ 書ける者が居らぬ。** 同 uid(此の Mac の全席)は chmod で外せ、root は無視できる。0 は「錠を外さずに書く外の器が settings.json / ps / scripts/ / LaunchAgents の四つの根に無い」であり、四つの根の外(例: 手で打つ shell・他 PC からの ssh)は歩いて居らぬ。
7. **33 の己の産物 153 ≠ 疵の数。** 己の出目が己の当たりを逐語で含む故に走る度に膨れる数であり、三走目は名で札して母數から分けた。此の数は「器を三度走らせた」事の痕である。

## 7. 己の疵(本弾・4)
1. ★着手便を器 05 でなく shell(inline python + inbox_write.sh)で出した★(札の「今すぐ」を優先)―― 記録 raw/chakushu_*(生の > で捕へ 0byte を産んだ・00 が kaki で書き直した)。第67弾 §5-7「便は器が先に測る」を本弾の着手便で己が破つた。
2. ★己の箱の既讀化を器 65 でなく inline python で行つた★ ―― 第67弾 §5-1「直した」を本弾で己が破つた。
3. ★33 を三度直した★(自己参照で膨れ・f-string を誤札)―― 一走目・二走目を .first/.second に残す。★則を測つた後に変へた★のは検出子でなく「己の産物の札」と「文/実行の割り方」であり、当たりの実行 0 は三走とも同じ(一走目は札無しゆゑ「4 当たり」としか言へなかつた)。
4. ★37 の一走目は pgrep の空 pattern で母數 0 rc 2★ ―― 器の誤りを .first に残し ps に替へた。
- 第67弾から本弾で数へ直した疵: 一走目の器を file に残さなかつた(41 は再現・§2)。

## 8. 据ゑず・触れず・門の後の期待・宣⇔實
- 据ゑず(scripts/ ~/bin settings.json hook instructions/ 0 字・門・照合器・追記器は讀む/走らせるのみ・60 が前後の sha16 で示す)/ 專任3 の束(km-46/47)へ 0 字(71 を -B で走らせるのみ・彼の出目は己の raw/)/ 第67弾の束へ 0 字(錠の下・讀むのみ)/ 他席の臺帳・紙・箱に 0 字 / DB 0(sb 0 回)/ git は rev-parse・hash-object・一時 repo の fixture のみ(commit/push 0・add -f は納めの後に己の束のみ)/ tmux send-keys 0 / 臺帳は append.py のみが書き 手書き 0 / raw への本文は kaki(fixture の本文と 41 の source は逐語が的ゆゑ例外)。
- ★門の後の期待(_after/96_after.txt が證す・紙は其の数を書けぬ)★: ⑴ 根 raw/(宣 無・--probe): 後 0・疵 0・P0 PermissionError・rc 0 ⑵ 根 束全体(宣 = raw/50_sengen.txt): 後 = _after/ と門控 悉く宣に在る・疵 0・rc 0 ⑶ 臺帳 照合 rc 0 ⑷ 錠 悉く 0444/0555。★一つでも違へば追ひ便で告げる。★
- 起 2026-09-17T03:55:25(着手便の刻)/ 宣 = 06:00:00 に納め便(端点 = 納め便 1 本目を inbox_write.sh へ渡す直前の刻・62 が取る)。實は _after/63_sent.txt が両基準で書く。宣は敢へて長く置いた(前々弾までの宣は 1.8x〜6x 過大に外れた)―― 過大なら過大と書く。
- 在處: worktree `/Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1/docs/evidence/km-68-yonda-ban-to-hashiraseta-ban-20260917/`(枝 karo-mac/a1-r56)。臺帳の基点は冒頭の一行。

## 9. 出處
raw/00_start.txt(起・宣・則)/ chakushu_*(着手便・手)/ 20_hanban.py + 20_hanban_verify.txt + 20_hanban_wt.txt(版刻)/ 21_otsu1.{txt,tsv}(引き直し)/ 30_p6.{txt,tsv} + 30_rule_diff.txt + 30_rule_verbatim.txt + 31_make_rule1.py + 41_mon_no_ato_rule1.py + raw/p6/(P6)/ 33_rc_pipe.{txt,tsv} + .first.* + .second.* + raw/fixture/(rc 管)/ 35_yotsu.{txt,tsv}(四數)/ 37_jou.txt + .first.*(錠)/ 50_sengen.txt・50_build_manifest.out / 59_prescan.out / _after/(門の後・根の外): 00_hosho.txt・60_gate_rcs.txt・60_gate_top.r68.txt・96_after.txt・96_raw.txt・96_bundle.txt・62_report_body.txt・63_sent.txt・67_git_add.txt。
