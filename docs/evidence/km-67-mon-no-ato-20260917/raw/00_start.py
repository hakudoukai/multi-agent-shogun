# -*- coding: utf-8 -*-
"""起の器 00(第67弾)―― 起・宣ETA・則を ★測る前に★ 器で書く(前弾は手で書き疵とした・§8-4)。刻は date と同じ time.strftime、札と禁域の sha16 は器が今計る。"""
import os, sys, time, hashlib, subprocess
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; W = M + '/.claude/worktrees/karo-mac-a1'
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
now = time.strftime('%Y-%m-%dT%H:%M:%S%z'); T = M + '/queue/tasks/ashigaru-mac-1.yaml'; tb = open(T, 'rb').read()
head = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, cwd=W).stdout.strip()
FORBID = ['scripts/checks/karo_mac_dasumae_gate.sh', 'scripts/checks/karo_mac_manifest_verify.py', 'scripts/checks/karo_mac_manifest_append.py', '.gitignore', '.claude/settings.json']
ETA = 26
sen = time.strftime('%H:%M:%S', time.localtime(time.mktime(time.strptime(now[:19], '%Y-%m-%dT%H:%M:%S')) + ETA * 60))
L = [f'起 {now} (date ―― 家老の /clear 03:0x → 自己識別 03:09:24(date・tmux @agent_id=ashigaru-mac-1)→ 札 → 前弾 km-66 の紙・器・臺帳 4 本の現物を讀む(03:10〜03:13)→ 束の骨を建て 03:13:02 → 此の file は器 00 が書いた)',
     f'task sha16 {hashlib.sha256(tb).hexdigest()[:16]} (札 queue/tasks/ashigaru-mac-1.yaml・{len(tb)} B・{tb.count(b"\n")} 行 grep -c 相当)/ 家老の宣 e638748eb93c5f8a・5415B・52行',
     f'束の在處 = worktree {W}/docs/evidence/km-67-mon-no-ato-20260917(枝 karo-mac/a1-r56・HEAD {head}・第66弾と同じ型・裁 320577/320321)。紙 = ashigaru-mac-1_km-67-mon-no-ato-20260917.md / 臺帳 = 同名 _manifest.txt(★karo_mac_manifest_append.py のみで建てる・手書き 0★)/ 門控 = 同名 _gate.txt(員外)/ raw/ = 器と出目 / _after/ = 門の後の出目(根の外)。置くのみ・git add -f のみ・commit/push は家老。',
     '禁域の前の sha16(main 樹・門は main 樹の器を使ふ・第66弾と同じ): ' + ' / '.join(f'{p} {sha16(M + "/" + p)}' for p in FORBID) + f' ―― 悉く讀む・走らせるのみ(worktree の写し gate.sh {sha16(W + "/" + FORBID[0])} / verify.py {sha16(W + "/" + FORBID[1])} は HEAD の版で main 樹と違ふ・使はぬ)。',
     f'★宣ETA(端点を先に定める)★: 席基準 = 此の 起 {now[:19]} 〜 門控の刻(60_gate_top.r67 の 刻)/ 家老基準 = 札 assigned_at 03:06:00 〜 札の done_at。宣 = 起 + {ETA} 分 = {sen} に門。織り込み = 器 6 本(40 捕へ器/42 對照/45 第66弾へ/50 乙1現物/50 臺帳+60 門+錠/70 紙)。前弾 66 は宣 28 で實 14.7(席)= 器 4 本 → 14.7 × 6/4 ≈ 22 + 對照の形 9 で +4 = 26。宣は二方向に外れる ―― 過小なら過小と書く。',
     '★則(測る前に書く)★',
     '㋐ 捕へ器 40_mon_no_ato.py: argv = <歩き根> <歩哨file> <宣file or -> <出力dir> <名>。刻 = ★歩哨 file の st_mtime_ns(ns)★。歩哨 = 60 が門を呼ぶ直前に raw/60_hosho.txt として書く一行。★何故 歩哨か(門控でなく)★: 門控は門の最後の産物ゆゑ、門自身の産物(60_gate_*.err 等)は門控より前になり「後」の集合が門の産物を隠す。歩哨を門の前に置けば門の産物は悉く「後」に入り、其れが宣に在るかで分かれる ∴ 疵 = 後 ∧ 宣に無い、が過不足なく出る。stat -f %Fm と os.stat().st_mtime_ns は同じ kernel の値(器が歩哨で両方を印字し一致を示す)ゆゑ python の ns を採る。',
     '  後 = file の mtime_ns > 刻 ★又は★ birth(生れた刻・stat -f %FB)> 刻。同 = mtime_ns == 刻(決められぬ・数へる)。前 = 何れも < 刻。ctime は使はぬ(chmod/rename/cp -p が動かし、中身の書込みと区別できぬ)。歩く = os.walk・lstat・S_ISREG のみ(非通常は数へて宣す)。母數 0 なら rc 2(★歩いて居らぬ = 通でも鳴でもない★)。後 ∧ 宣に無い ≥ 1 なら rc 1(鳴)。後 ∧ 宣に在る のみなら rc 0。宣 = fnmatch(brace {a,b} は展開)。',
     '  ★錠(出来なくする)★: 60 は門控を書いた直後に raw/ と其の配下の通常 file を a-w にする(chmod 0o555 / 0o444)。錠の後に根へ書けば EACCES で落ちる ―― 之が「出来なく」の一層目。40 は錠の後に走り、根へ 1 byte 書けるかを試み PermissionError を記録する(P0)。二層目 = 40 の ns 比較(錠を外した者・錠の前の隙を捕へる)。',
     '㋑ 第66弾へ: 根 = km-66/raw、歩哨は無い故 刻 = 門控 _gate.txt の mtime_ns(代用・理由を書く)。宣 = km-66 raw/50_sengen.txt の ㊂ 行。あの 1 本 2 B(60_gate_run.rc)が 後 に入るか、宣に在るか。加へて根 = km-66 束全体(_after/ 込み)でも走らせる。',
     '㋒ 對照(器 42 が建て・悉く 40 を subprocess で通す・手前で折り返さぬ・母數を印字し 0 なら偽の通過として落とす): 陽性 P1 新file / P2 既存へ追記 / P3 touch(中身同・mtime のみ後)/ P4 ★同秒の後 ns★(66 の穴)/ P5 新dir+file / P6 utime で mtime を歩哨の前へ戻した新file(birth が後)/ P7 宣に在る名と無い名が共に後(無い名で鳴る)。陰性 N1 悉く前 / N2 ★同秒の前 ns★ / N3 宣に在る名だけが後 / N4 深い dir・0byte file・悉く前。Z1 空の根 → rc 2。期待: 陽性 7 とも rc 1・陰性 4 とも rc 0・Z1 rc 2。陰性が一形でも鳴れば騒音と書く。',
     '㋓ 乙1 23 + 乙5 3 の現物(器 50_otsu1.py): 臺帳の生の行(bytes)を一行づつ mini 臺帳へ写し(raw/otsu1/lines/)、main 樹の讀手 karo_mac_manifest_verify.py の main() を sys.settrace で走らせ、verify.py の行番号の列を採り、落ちる行(76 sha無→continue / 82 読めぬ行 / 95 実体無 / 103 相違 / 101 一致)を實走で示す。基点は門が渡す形 [""](cwd = main 樹)を第一とし、届く基点(<_evidence>/raw/ 等)も併せて測る(直すのではない・測る)。乙5 の 3 行は生バイトを 16 進で。出目 = raw/otsu1_genbutsu.tsv(專任3 へ渡す一枚)。',
     '㋔ 66 §8 の疵 7 の内: 直す = 1(既讀化を器 65 で)・4(00_start を器で)・7(便を先に器で測る)。直さぬ = 2/3/5/6(本弾の的でない・理由は紙)。',
     '作法: 便の器(05/62)は臺帳より先に書く / 字数の器は鎖の前 / 鎖の守りは尾まで(10_run で一つづつ rc)/ ad-hoc python は -B / raw への本文は悉く kaki(mini 臺帳の生 bytes のみ例外 = 逐語が的)/ 門控の名 = 60_gate_top.r67 / 門の後に根へ 0 字(錠 + 40 が證す)/ 非通常 file は S_ISREG で除き本数を宣す / rc は pipe に通さぬ / grep -c 零は rc=1 ―― 器の中で python が数へる / 生器(scripts/)へ 0 字。']
K.kaku(E + '/00_start.txt', '\n'.join(L)); print(open(E + '/00_start.txt', encoding='utf-8').read())
