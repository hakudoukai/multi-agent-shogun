# -*- coding: utf-8 -*-
"""起の器 00(第68弾)―― 起・宣ETA・則を ★測る前に★ 器で書く。刻は date と同じ time.strftime、札と禁域の sha16 は器が今計る。
着手便は札の「今すぐ」に従ひ ★器 05 を建てる前に shell(inline python + inbox_write.sh)で出した★ ―― 其の記録(raw/chakushu_*)は生の > で捕へた故 0byte(chakushu_send.out)が生れた。本器が kaki で書き直す(疵として紙に書く)。"""
import os, sys, time, hashlib, subprocess
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; W = M + '/.claude/worktrees/karo-mac-a1'
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
now = time.strftime('%Y-%m-%dT%H:%M:%S%z'); T = M + '/queue/tasks/ashigaru-mac-1.yaml'; tb = open(T, 'rb').read()
head = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, cwd=W).stdout.strip()
FORBID = ['scripts/checks/karo_mac_dasumae_gate.sh', 'scripts/checks/karo_mac_manifest_verify.py', 'scripts/checks/karo_mac_manifest_append.py', '.gitignore', '.claude/settings.json', 'scripts/inbox_write.sh']
KI = open(E + '/chakushu_send_koku.txt', encoding='utf-8').read().strip()  # 着手便を送つた刻(date・送る前に取つた)
SEN_CLOCK = '06:00:00'
# 生の > で捕へた 0byte を kaki で書き直す(0byte にせぬ・裁 310228)
for nm in ('chakushu_send.out', 'chakushu_send.err'):
    q = E + '/' + nm; b = open(q, 'rb').read()
    K.kaku(q, b.decode('utf-8', 'replace'))
L = [f'起 {KI} (= 着手便を inbox_write.sh へ渡す直前の date の刻・raw/chakushu_send_koku.txt) / 此の file は器 00 が {now} に書いた(自己識別 03:54:30 → 札 → 第67弾の紙・器・專任3 の器 71_yotsu.py を讀む → 骨 03:58 → 00)',
     f'task sha16 {hashlib.sha256(tb).hexdigest()[:16]} (札 queue/tasks/ashigaru-mac-1.yaml・{len(tb)} B・{tb.count(b"\n")} 行 grep -c 相当)/ 家老の宣 e51e8330b9674c33・7443B・66行 / assigned_at 03:52:00',
     f'束の在處 = worktree {W}/docs/evidence/km-68-yonda-ban-to-hashiraseta-ban-20260917(枝 karo-mac/a1-r56・HEAD {head}・第67弾と同じ型・裁 320577/320321)。紙 = ashigaru-mac-1_km-68-yonda-ban-to-hashiraseta-ban-20260917.md / 臺帳 = 同名 _manifest.txt(★karo_mac_manifest_append.py のみで建てる・手書き 0★)/ 門控 = 同名 _gate.txt(員外)/ raw/ = 器と出目 / _after/ = 門の後の出目(根の外)。置くのみ・git add -f のみ・commit/push は家老。',
     '★臺帳の基点(紙に一行で明記せよ・家老が本夜踏んだ穴)★: 臺帳の path は ★main 樹の根 /Users/momizimac/multi-agent-shogun からの相對★(.claude/worktrees/karo-mac-a1/docs/evidence/km-68-…/…)。worktree の根に立つて照合すれば ★悉く実体無★ と出る ―― 其れは disk の欠けではなく基点の違ひ。worktree の根から引くなら頭の .claude/worktrees/karo-mac-a1/ を落とせ。',
     '禁域の前の sha16(main 樹・門は main 樹の器を使ふ): ' + ' / '.join(f'{p} {sha16(M + "/" + p)}' for p in FORBID) + f' ―― 悉く讀む・走らせるのみ。worktree の写し gate.sh {sha16(W + "/" + FORBID[0])} / verify.py {sha16(W + "/" + FORBID[1])}(HEAD の版・127 行)は ★讀んだ版≠走らせた版 の對照★ として讀むのみ・走らせぬ。',
     f'★宣ETA(端点を先に定める)★: 起点 = 着手便の刻 {KI[11:]} / 端点 = 納め便 1 本目を inbox_write.sh へ渡す直前の date の刻(62 が取る)。宣 = {SEN_CLOCK}(着手便に書いた通り・{KI[11:]} → {SEN_CLOCK} = 124.6 分)。家老基準 = 札 assigned_at 03:52:00 〜 札の done_at。織り込み = 器 8 本(20 版刻/21 ㋓引直し/30 P6/33 rc管/35 四數/37 錠/50 臺帳+60 門/70 紙)。前弾 67 は宣 26 で實 23.7(席・器 6 本)= 器 1 本 4 分 → 8 本 32 分 + 專任3 の器を讀む 10 + 對照の形 20 + 紙 20 = 82 分。★宣 124.6 は其の 1.5 倍★ ―― 前々弾までの宣は 1.8x〜6x 過大に外れた(家老 memory)故、本弾は敢へて長く置く。宣は二方向に外れる ―― 過大なら過大と書く。',
     '★則(測る前に書く)★',
     '㋐ 版刻器 20_hanban.py: argv = <走らせる実体の path> [--lines n,n,…] [--against <別の版の path>]。走らせる★直前★に ⑴ realpath ⑵ sha256(先頭16)⑶ 総行数(grep -c 相当)⑷ git hash-object と HEAD の blob が同じか(= commit 済か・汚れて居るか)⑸ 指す行番号の★其の実体の★本文 を刷り、⑴〜⑸ を繋いだ正準文字列の sha16 を ★版札★ として末尾に刷る(專任3 の四数札と同じ形 ―― 抜き書きすれば封が合はぬ)。--against は同じ行番号を別の版に当て、本文が違ふ事を並べて見せる(嘘の顔)。載せ方: 21 は verify.py を ★20 の load() を通してのみ★ import し、settrace の行番号は ★load した其の bytes★ の linecache から引く ―― 讀む bytes と走らせる bytes が同一物になる故「讀んだ版≠走らせた版」は起り得ぬ(憶えるのではなく構造で塞ぐ)。',
     '  21_otsu1_hanban.py: 第67弾の mini 臺帳 26 本(km-67 raw/otsu1/lines/・讀むのみ)を 20 越しに main 樹の verify.py へ食はせ、落ちる行を settrace で採る。第67弾の otsu1_genbutsu.tsv の A/B/C 落ちる行と ★一本づつ★ 突き合はせ、139/133/152→158 の本数が同じ数で出るかを數へる。出ぬなら出ぬと書き、どちらが正で何故かを一行。',
     '㋑ P6 の始末 30_p6.py: 40(則二 = mtime|birth|ctime・第67弾の二走目・逐語の写し 4bc8f1dfafd9ee9a)と 41(則一 = mtime|birth・第67弾の一走目の則を 40 から一行だけ戻した物・31_make_rule1.py が作り diff -u を raw/30_rule_diff.txt に刷る)を ★同じ P6 fixture★ に掛け rc が 0→1 に反転するかを見る。反転せぬなら則の変更は P6 を救つて居らぬ ―― 何が救つたかを名指す。加へて L1(錠→歩哨 / 歩哨→錠 の両順)を則一・則二の四通りで掛け「錠の順を変へた」のが何を救つたかを分ける。逐語の則 = 00_start(km-67)の㋐「ctime は使はぬ」の行 と 40 の docstring「ctime を足し」の行を並べる。',
     '㋒ rc が管を渡る箇所 33_rc_pipe.py: 母數 = km-67 と km-68 の束の ★全 file★(.py .sh .txt .md .tsv …・非通常は除き数へる)。検出子 = ⑴ python: shell=True の cmd 文字列に | / os.system( / os.popen( / subprocess.getoutput / getstatusoutput ⑵ shell 文(.sh と .txt/.md に写された命令行): | の在る行の同行か次行に $? / rc= / returncode。当たつた行を path:行番号+逐語で列挙。★陽性対照★ = raw/fixture/33_positive.sh(⑵の形)と raw/fixture/33_positive.py(⑴の形)を己で書き ★同じ歩きに乗せ★ 鳴る事を示す。直す = 本弾の器に在れば直す(第67弾の束は錠の下・讀むのみ・直さぬ本数と理由を書く)。',
     '㋓ 四數 35_yotsu.py: 專任3 の 71_yotsu.py(main 樹 docs/evidence/km-47-…/ki/・讀む・走らせるのみ・-B・彼の束へ 0 字)の fuda を --kikai main 樹 verify.py で 23 本の mini 臺帳(乙1 19+4)に掛け、四数札v1(母數/一致/相違/実体無/讀めぬ行+封)を採る。基点 A = ""(cwd main 樹)/ B = <紙>_evidence/。己の 21(settrace の落ちる行)と一本づつ突き合はせ、139↔讀めぬ行=1 / 133↔母數=0 / 152↔実体無=1 / 158↔一致=1 の対応で割れる本数を數へる。割れたら「どちらの器が何を数へて居らぬか」を一行。',
     '㋔ 錠 37_jou.py: 束の外の書き手を數へる ―― ⑴ settings.json の hook(母數・各 command が docs/evidence へ書くか)⑵ 稼働中 process(pgrep -U 己・母數・argv に docs/evidence を持つ物)⑶ scripts/ の器(docs/evidence を含む file・其の行が書きか讀みか)⑷ launchd plist(母數・repo を指す物)⑸ git 自身: 一時 repo の fixture で dir 0555/file 0444 の下へ checkout / restore / clean が書けるか(rc と stderr 逐語)⑹ 同 uid の他席: chmod で外せる(L3 の形・ctime で鳴る)⑺ root。各々に rc と根と深さと刻。0 なら 0 と。★錠が塞ぐのは open(O_WRONLY|O_CREAT) と unlink であつて read ではない ―― git add -f が通つたのは讀みゆゑ。★',
     '㋕ 意味せぬ事 ≥ 5(紙 §6)。',
     '作法: 便の器 62 は臺帳より先に書く / 字数の器は鎖の前 / 鎖の守りは尾まで(10_run で一つづつ rc)/ ad-hoc python は -B / raw への本文は悉く kaki / 門控の名 = 60_gate_top.r68 / 門の後に根へ 0 字(錠 + 40 が證す)/ 非通常 file は S_ISREG で除き本数を宣す / rc は pipe に通さぬ / grep -c 零は rc=1 ―― 器の中で python が数へる / 生器(scripts/)へ 0 字 / 專任3 の束へ 0 字 / 第67弾の束へ 0 字(錠の下・讀むのみ)。',
     '★己の疵(起の時点で既に 2)★: ⑴ 着手便を器 05 でなく shell(inline)で出した ―― 記録は raw/chakushu_*(生の > で捕へ 0byte を産んだ・本器が kaki で書き直した)。⑵ 己の箱の既讀化を器 65 でなく inline python で行つた(第67弾 §5-1 で「直した」と書いた事を本弾で己が破つた)。']
K.kaku(E + '/00_start.txt', '\n'.join(L)); print(open(E + '/00_start.txt', encoding='utf-8').read())
