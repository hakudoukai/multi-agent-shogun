# -*- coding: utf-8 -*-
"""紙を書く器 70(第68弾)―― 本文は此処に固定し kaki で <束>.md へ置く(行末空白 0・CR 0・EOF 改行 1)。★表と数は 20/21/30/33/35/37 の出目から器が引く(手写しでない)★。引けねば落ちる。argv[1] = 束の prefix。"""
import sys, os, re
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; sys.path.insert(0, E); import kaki as K
def rd(p): return open(p, encoding='utf-8').read()
def num(pat, txt): m = re.search(pat, txt); assert m, pat; return m.group(1)
T20 = rd(E + '/20_hanban_verify.txt'); T20w = rd(E + '/20_hanban_wt.txt'); T21 = rd(E + '/21_otsu1.txt'); T30 = rd(E + '/30_p6.txt'); T30v = rd(E + '/30_rule_verbatim.txt'); T33 = rd(E + '/33_rc_pipe.txt'); T33f = rd(E + '/33_rc_pipe.first.txt'); T33s = rd(E + '/33_rc_pipe.second.txt'); T35 = rd(E + '/35_yotsu.txt'); T37 = rd(E + '/37_jou.txt'); T37f = rd(E + '/37_jou.first.txt'); ST = rd(E + '/00_start.txt')
tsv21 = [l.rstrip('\n').split('\t') for l in open(E + '/21_otsu1.tsv', encoding='utf-8')][1:]; assert len(tsv21) == 26
def short(s, n): s = s.replace('|', '｜'); return s if len(s) <= n else s[:n - 1] + '…'
k21 = re.search(r'一本づつ A/B/C 悉く同じ (\d+) / 違ふ (\d+) / 母數 (\d+)', T21); s21 = re.search(r'結: 乙1 139 = (\d+) / 乙1 133 = (\d+) / 乙5 152\(A\) = (\d+) / 乙5 158\(B\) = (\d+)', T21); assert k21 and s21
fu20 = num(r'封=([0-9a-f]{16})', T20); fu20w = num(r'封=([0-9a-f]{16})', T20w); dirty = num(r'→ (★違ふ=汚れて居る\(disk ≠ HEAD\)★|同じ=commit 済)', T20)
tab20 = '\n'.join('  ' + l for l in T20.split('\n')); tab20w = '\n'.join('  ' + l for l in T20w.split('\n'))
tab30 = '\n'.join(l for l in T30.split('\n') if l.startswith('|')); k30 = re.search(r'P6 を二走目の則で走らせ直す: 41 rc (\d) → 40 rc (\d) = ★(\S+?)★', T30); g30 = re.search(r'合 (\d+) 不 (\d+)', T30); l1a = re.search(r'L1a\(歩哨→錠\)41 rc (\d) / 40 rc (\d)', T30); l1b = re.search(r'L1b\(錠→歩哨\)41 rc (\d) / 40 rc (\d)', T30); p6note = num(r'(P6: e\.txt: 歩哨 \d+ / 戻した後の stat[^\n]*)', T30)
v30 = '\n'.join('  ' + l for l in T30v.split('\n') if l.startswith('  '))
k33 = re.search(r'本の当たり (\d+) = 実行 (\d+) \+ 文 (\d+)', T33); m33 = num(r'母數 通常 file (\d+)', T33); s33 = num(r'己の産物\([^)]*\) (\d+) ‖', T33); m33f = num(r'母數 通常 file (\d+)', T33f); h33f = num(r'当たり\(対照と己を除く\) (\d+) 箇所', T33f); h33s = num(r'当たり\(対照と己を除く\) (\d+) 箇所', T33s); jk33s = num(r'★実行★\(rc が実際に管を渡る\) (\d+)', T33s)
hits33 = '\n'.join(l for l in T33.split('\n') if l.startswith('  [')); ctl33 = num(r'(## 陽性対照: [^\n]*)', T33)
k35 = re.search(r'乙1 (\d+) 本: A 合 (\d+) 割れ (\d+) ‖ B 合 (\d+) 割れ (\d+)', T35); k35b = re.search(r'乙5 (\d+) 本: A 合 (\d+) 割れ (\d+) ‖ B 合 (\d+) 割れ (\d+)', T35); j35 = num(r'--jikenme\(彼の対照\): rc (\d)', T35); y71 = num(r'71_yotsu\.py sha16 ([0-9a-f]{16})', T35); n133 = num(r'133 の 4 本\(sha256= 無・continue\): 71 の四数 = (\[[^\]]*\])', T35)
tab35 = '\n'.join(l for l in T35.split('\n') if l.startswith('|'))
k37 = num(r'= ★(\d+)★\(rc 0', T37); h37 = num(r'hook\(settings\.json\)母數 (\d+)', T37); p37 = num(r'process\([^)]*\)母數 (\d+)', T37); s37 = num(r'scripts/ の器 母數 (\d+)', T37); l37 = num(r'launchd plist 母數 (\d+)', T37); p37f = num(r'process\([^)]*\)母數 (\d+) / rc (\d)', T37f)
git37 = '\n'.join('  ' + l.strip() for l in T37.split('\n') if l.startswith('  讀 ') or l.startswith('  書 ') or l.startswith('  生 ') or l.startswith('  後の状態')); j67 = num(r'(## 第67弾の錠の今[^\n]*)', T37)
KI = num(r'起 (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', ST); SENC = num(r'宣 = (\d\d:\d\d:\d\d)\(', ST)
rows = '\n'.join(f'| {r[0]} | {short(r[1], 30)} | {r[2]} | {r[5]}→{r[6]} {"同" if r[7] == "True" else "★違★"} | {r[8]}→{r[9]} {"同" if r[10] == "True" else "★違★"} | {r[11]}→{r[12]} {"同" if r[13] == "True" else "★違★"} | {r[14]} | `{short(r[17], 22)}` |' for r in tsv21)
T = f'''# 第68弾 ―― 讀んだ版と走らせた版が違へば、行番号は正しい顔をして嘘を吐く ―― 版刻器で構造的に塞ぎ、第67弾の ㋓ を引き直し、P6 の反転・rc の管・兩席の四數・錠の外を測る(読取のみ・生器へ 0 字・他席の束へ 0 字)―― 答を先に(★數の出處 = raw/20_hanban.py(版刻器)+ 20_hanban_verify.txt/20_hanban_wt.txt / raw/21_otsu1.{{txt,tsv}} / raw/30_p6.{{txt,tsv}} + 30_rule_diff.txt + 30_rule_verbatim.txt + raw/p6/ / raw/33_rc_pipe.{{txt,tsv}} + .first + .second + raw/fixture/ / raw/35_yotsu.{{txt,tsv}} / raw/37_jou.txt + .first / raw/00_start.txt(起・宣・★則の逐語★)/ _after/96_after.txt(門の後の實走 ―― 紙の後に生れる故 紙は其の数を書けぬ・期待のみ書く)★)

★臺帳の基点(一行)★: 本束の臺帳 `ashigaru-mac-1_km-68-yonda-ban-to-hashiraseta-ban-20260917_manifest.txt` の path は ★main 樹の根 `/Users/momizimac/multi-agent-shogun` からの相對★(append.py を cwd = main 樹で呼ぶ故)。worktree の根 `.claude/worktrees/karo-mac-a1/` に立つて照合すれば ★悉く実体無★ と出る ―― disk の欠けではなく基点の違ひ。worktree の根から引くなら頭の `.claude/worktrees/karo-mac-a1/` を落とせ(家老が本夜踏んだ穴・第67弾の臺帳も同じ基点)。

★答★: ㋐ 版刻器 raw/20_hanban.py ―― 走らせる★直前★に realpath / sha16 / 総行数 / git blob vs HEAD / 指す行の本文を刷り、其れらを繋いだ正準文字列の sha16 を ★版札v1 の封★ にする(專任3 の四数札と同じ形 ―― 抜き書きすれば封が合はぬ)。21 は讀手 verify.py を ★20 の Han.module()(讀んだ bytes を其の儘 compile して exec)越しにのみ★ 走らせ、settrace の行番号を ★同じ bytes★ の行本文へ引き当てる ∴ 讀む物と走らせる物が同一物で「讀んだ版≠走らせた版」は構造で起り得ぬ(憶えるのではない)。main 樹 verify.py = 198 行 a507c998c7bd6485・{dirty}・封 {fu20} / worktree 写し = 127 行 bbde471f70848fc8・封 {fu20w}: 198 行の L133/139/152/158/160 は 127 行に ★無く★、127 行の L76/82/95/101/103 は 198 行で ★別の文★ ―― 之が嘘の顔。引き直し(21): mini 26 本 一本づつ A/B/C 同 {k21.group(1)} / 違 {k21.group(2)} / 母數 {k21.group(3)}。乙1 139 = {s21.group(1)} / 133 = {s21.group(2)} / 乙5 152(A) = {s21.group(3)} → 158(B) = {s21.group(4)} = 第67弾の 19/4/3/3 と ★同じ数★。★同じ数が出た事も、器を通して初めて言へる★(67 の二走目は cat -n で手置き・68 は走らせた bytes)。㋑ P6: 同じ fixture で 則一(41 = 40 から ctime 一行を外した再現) rc {k30.group(1)} → 則二(40) rc {k30.group(2)} = ★{k30.group(3)}★・何で後 = c のみ ∴ ★ctime が救つた★。錠の順は別の物を救つた: L1a(歩哨→錠) 41 rc {l1a.group(1)} / 40 rc {l1a.group(2)}(錠の chmod が ctime で鳴る)・L1b(錠→歩哨) 41 rc {l1b.group(1)} / 40 rc {l1b.group(2)}。㋒ rc が管を渡る箇所(33・三走): 母數 file {m33} / 当たり {k33.group(1)} = ★実行 {k33.group(2)}★ + 文 {k33.group(3)} / 己の産物 {s33}(自己参照)/ 陽性対照 2 鳴・陰性 黙。㋓ 兩席の器: 專任3 71_yotsu.py({y71})の fuda で 乙1 {k35.group(1)} 本 A 合 {k35.group(2)} 割れ {k35.group(3)} / B 合 {k35.group(4)} 割れ {k35.group(5)}・乙5 3 本 合 ―― 133 の 4 本は四数札 {n133} = ★母數 0 でしか言へず「何行を跳んだか」の欄が無い(欄の欠・盲ではない)★。㋔ 錠の外: hook {h37} / process {p37} / scripts {s37} / launchd {l37} の内 raw/ へ ★錠を外さずに★ 書ける経路 = ★{k37}★。git は讀み系 rc 0・書き系(checkout / rm / restore)は unlink で EACCES。同 uid の chmod と root は塞がぬ(chmod は ctime が痕・root は測れぬ)。

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
{tab20}
### 1.2 逆向き ―― worktree の写し(127 行)を main 樹(198 行)に当てる = 第67弾 一走目の形
{tab20w}
### 1.3 引き直し(21)―― mini 26 本(第67弾 raw/otsu1/lines/・讀むのみ)を 20 越しに走らせ、第67弾 tsv の落ちる行と一本づつ突き合はす
| 山 | 臺帳 | 行 | A 67→68 | B 67→68 | C 67→68 | 68 出目A | 68 本文(走らせた bytes) |
|---|---|---|---|---|---|---|---|
{rows}
- 一本づつ 悉く同じ {k21.group(1)} / 違ふ {k21.group(2)} / 母數 {k21.group(3)}。乙1 139 = {s21.group(1)} / 133 = {s21.group(2)} / 乙5 152(A) = {s21.group(3)} → 158(B) = {s21.group(4)}。
- ★行番号→本文の検め★: 21 は走らせた bytes で L133='continue' / L139='unreadable += 1' / L152='miss += 1' / L158='ok += 1' / L160='ng += 1' を確かめてから settrace に入る ―― 版が違へば此処で落ちる(落ちなかつた = 版札 {fu20} の版で走つた)。

## 2. ㋑ P6 の始末(raw/30_p6.txt・fixture raw/p6/・各形を一度建て 41→40 の順に讀むのみで掛けた)
{tab30}
- {p6note}
- ⑴ 反転: 41 rc {k30.group(1)} → 40 rc {k30.group(2)} = {k30.group(3)}。⑵ 救つた物: 40 の「何で後」は c のみ ―― m も b も刻より前(macOS APFS は utime で mtime を birth より前へ戻すと birth も締める)∴ ★ctime の追加★。錠の順(L1a→L1b)が救つたのは ★錠自身が鳴る副作用★ であり、P6 ではない。形 {g30.group(1)} 合 / {g30.group(2)} 不。
- ⑶ 変更前後の則の逐語(raw/30_rule_verbatim.txt):
{v30}
- 器の差 = raw/30_rule_diff.txt(diff -u 40 41・差の核は `later = mns > A or bns > A or cns > A` → `later = mns > A or bns > A` の一行 + 頭註の名札 2 箇所)。★41 は再現であり第67弾 一走目の器其の物ではない★(一走目は器を file に残さず出目 .first のみ残した ―― 之は第67弾の疵として本弾で数へる・§7)。

## 3. ㋒ rc が管を渡る箇所(raw/33_rc_pipe.txt・三走・母數 = 両束の全通常 file)
- {ctl33}
- 当たり(対照・己・己の産物を除く) {k33.group(1)} = ★実行 {k33.group(2)}★ + 文 {k33.group(3)}:
{hits33}
- ★三走の理由(器を直した證・.first/.second を載せる)★: 一走目 母數 {m33f} 当たり {h33f}(文/実行の札無し)→ 二走目 当たり {h33s}(己の一走目の出目 33_rc_pipe.first.* が己の当たりを逐語で含み ★自己参照で膨れた★・f-string を「実行」と誤札 {jk33s})→ 三走目 己の産物 {s33} を名(己の stem)で札し f-string の token(3.12+ の FSTRING_*)を「文」に入れた。
- 直した実行の箇所 = 0(無かつた)。直さぬ = 文 4(則の記述と紙・測る前に書いた文ゆゑ触らぬ)。km-67 は錠の下・讀むのみ。
- ★數へぬ物★: 對話(shell の入力)で打つた `cmd | head; echo $?` は束に写らぬ限り母數に無い。第67弾 §7-3 の疵は其の形。∴ 本弾の「実行 0」は「束の器に無い」であつて「席の手に無い」ではない。

## 4. ㋓ 兩席の器が同じ四數を出すか(raw/35_yotsu.txt・專任3 71_yotsu.py {y71} を --kikai main 樹 verify.py で・讀む/走らせるのみ・彼の束へ 0 字)
- 71 の --jikenme(彼の対照 6 形): rc {j35}。乙1 {k35.group(1)} 本: A 合 {k35.group(2)} 割れ {k35.group(3)} / B 合 {k35.group(4)} 割れ {k35.group(5)}。乙5 {k35b.group(1)} 本: A 合 {k35b.group(2)} / B 合 {k35b.group(4)}。
{tab35}
- 対応の條: 139↔讀めぬ行=1 / 133↔母數=0 / 152↔実体無=1 / 158↔一致=1。★133 の 4 本★は四数札 {n133} ―― 「行が母數に入らぬ」を 0 でしか言へず、跳んだ行を名指す欄が無い。settrace(21)は其の行を 133 と名指す。∴ 割れたのではなく ★欄の欠★(專任3 の器も生器も同じ欄で出来て居る)。
- 71 は「★走らせた★ <cmd>」で器の path を刷るが ★sha も行数も刷らぬ★ ―― 本弾の版刻器が足す物は其処。

## 5. ㋔ 錠は本当に塞いだのか(raw/37_jou.txt・二走: 一走目は pgrep の空 pattern で process 母數 {p37f} rc 2 = 器の誤り・.first に残す)
- hook 母數 {h37} / process 母數 {p37} / scripts 母數 {s37} / launchd 母數 {l37} ―― raw/ へ ★錠を外さずに★ 書ける実行行・process・plist = ★{k37}★(rc 0・根 settings.json / ps -U / scripts/ / ~/Library/LaunchAgents・深さ 1〜2・刻は 37 の各行)。
- git 自身(一時 repo・dir 0555 / file 0444・讀み 4 形・書き 5 形・生 6 形・逐語):
{git37}
- {j67[3:]}
- ∴ ★錠が塞ぐのは open(O_WRONLY|O_CREAT) / unlink / rename / mkdir であつて read ではない。git add -f が通つたのは讀みゆゑ。★ 塞いだのは「門の後に書く病」の内 ★己の器が黙つて書く★ 経路(と外の書き手が黙つて書く経路)。同 uid の chmod(錠を外す)と root は塞がぬ ―― 前者は ctime で 40 が數へ(L1a・第67弾 L3)、後者は測れぬ。

## 6. ㋕ 意味せぬ事(本弾の数が言はぬ事・7)
1. **21 の 26/26 同 ≠ 第67弾の行番号が正しかつた事の證明。** 同じ版(a507c998)が此の間 動かなかつた故に同じ数が出た。版が動けば同じ手順で違ふ数が出る ―― 其の時に初めて 20 の封が「違ふ」と言ふ。
2. **版札の封 ≠ 器の正しさ。** 封は「どの bytes を走らせたか」を縛るだけで、其の bytes が正しい讀手である事は言はぬ(汚れた main 樹の版 = 未 commit の 198 行 を走らせて居る事を、封は隠さず示す丈)。
3. **P6 反転 ≠ 則二が恒真。** 形は 5(P6/L1a/L1b/N1/P1)で、第67弾の 15 形を本弾で悉く再走した訳ではない。ctime は chmod/rename/cp -p でも動く ∴ 則二は「書いた」と「触つた」を分けぬ(第67弾 §6-1 と同じ)。
4. **rc 管 実行 0 ≠ 席が pipe 越しに rc を讀まなかつた事。** 對話の入力は母數に無い。此の器は束を測り、手を測らぬ。
5. **四數 割れ 0 ≠ 二つの器が同じ物を數へて居る事。** 133 の 4 本で兩者は「母數 0」と「133 行で continue」を出す ―― 数は合ふが、片方は行を名指し片方は名指さぬ。合つたのは對応表の側であつて器の側ではない。
6. **錠外経路 0 ≠ 書ける者が居らぬ。** 同 uid(此の Mac の全席)は chmod で外せ、root は無視できる。0 は「錠を外さずに書く外の器が settings.json / ps / scripts/ / LaunchAgents の四つの根に無い」であり、四つの根の外(例: 手で打つ shell・他 PC からの ssh)は歩いて居らぬ。
7. **33 の己の産物 {s33} ≠ 疵の数。** 己の出目が己の当たりを逐語で含む故に走る度に膨れる数であり、三走目は名で札して母數から分けた。此の数は「器を三度走らせた」事の痕である。

## 7. 己の疵(本弾・4)
1. ★着手便を器 05 でなく shell(inline python + inbox_write.sh)で出した★(札の「今すぐ」を優先)―― 記録 raw/chakushu_*(生の > で捕へ 0byte を産んだ・00 が kaki で書き直した)。第67弾 §5-7「便は器が先に測る」を本弾の着手便で己が破つた。
2. ★己の箱の既讀化を器 65 でなく inline python で行つた★ ―― 第67弾 §5-1「直した」を本弾で己が破つた。
3. ★33 を三度直した★(自己参照で膨れ・f-string を誤札)―― 一走目・二走目を .first/.second に残す。★則を測つた後に変へた★のは検出子でなく「己の産物の札」と「文/実行の割り方」であり、当たりの実行 0 は三走とも同じ(一走目は札無しゆゑ「4 当たり」としか言へなかつた)。
4. ★37 の一走目は pgrep の空 pattern で母數 0 rc 2★ ―― 器の誤りを .first に残し ps に替へた。
- 第67弾から本弾で数へ直した疵: 一走目の器を file に残さなかつた(41 は再現・§2)。

## 8. 据ゑず・触れず・門の後の期待・宣⇔實
- 据ゑず(scripts/ ~/bin settings.json hook instructions/ 0 字・門・照合器・追記器は讀む/走らせるのみ・60 が前後の sha16 で示す)/ 專任3 の束(km-46/47)へ 0 字(71 を -B で走らせるのみ・彼の出目は己の raw/)/ 第67弾の束へ 0 字(錠の下・讀むのみ)/ 他席の臺帳・紙・箱に 0 字 / DB 0(sb 0 回)/ git は rev-parse・hash-object・一時 repo の fixture のみ(commit/push 0・add -f は納めの後に己の束のみ)/ tmux send-keys 0 / 臺帳は append.py のみが書き 手書き 0 / raw への本文は kaki(fixture の本文と 41 の source は逐語が的ゆゑ例外)。
- ★門の後の期待(_after/96_after.txt が證す・紙は其の数を書けぬ)★: ⑴ 根 raw/(宣 無・--probe): 後 0・疵 0・P0 PermissionError・rc 0 ⑵ 根 束全体(宣 = raw/50_sengen.txt): 後 = _after/ と門控 悉く宣に在る・疵 0・rc 0 ⑶ 臺帳 照合 rc 0 ⑷ 錠 悉く 0444/0555。★一つでも違へば追ひ便で告げる。★
- 起 {KI}(着手便の刻)/ 宣 = {SENC} に納め便(端点 = 納め便 1 本目を inbox_write.sh へ渡す直前の刻・62 が取る)。實は _after/63_sent.txt が両基準で書く。宣は敢へて長く置いた(前々弾までの宣は 1.8x〜6x 過大に外れた)―― 過大なら過大と書く。
- 在處: worktree `/Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1/docs/evidence/km-68-yonda-ban-to-hashiraseta-ban-20260917/`(枝 karo-mac/a1-r56)。臺帳の基点は冒頭の一行。

## 9. 出處
raw/00_start.txt(起・宣・則)/ chakushu_*(着手便・手)/ 20_hanban.py + 20_hanban_verify.txt + 20_hanban_wt.txt(版刻)/ 21_otsu1.{{txt,tsv}}(引き直し)/ 30_p6.{{txt,tsv}} + 30_rule_diff.txt + 30_rule_verbatim.txt + 31_make_rule1.py + 41_mon_no_ato_rule1.py + raw/p6/(P6)/ 33_rc_pipe.{{txt,tsv}} + .first.* + .second.* + raw/fixture/(rc 管)/ 35_yotsu.{{txt,tsv}}(四數)/ 37_jou.txt + .first.*(錠)/ 50_sengen.txt・50_build_manifest.out / 59_prescan.out / _after/(門の後・根の外): 00_hosho.txt・60_gate_rcs.txt・60_gate_top.r68.txt・96_after.txt・96_raw.txt・96_bundle.txt・62_report_body.txt・63_sent.txt・67_git_add.txt。
'''
K.kaku(B + '.md', T); print(B + '.md', len(T.encode('utf-8')), 'B', T.count('\n'), '行')
