# -*- coding: utf-8 -*-
"""起の器 00(第70弾)―― 起・宣ETA・則・禁域と既成束の印を ★測る前に★ 器で書く。起は raw/05_chakushu_koku.txt(器 05 が取つた)から引く。"""
import os, sys, time, hashlib, subprocess, stat
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; KM = 'km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917'
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
now = time.strftime('%Y-%m-%dT%H:%M:%S%z')
head = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, cwd=M).stdout.strip()
br = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True, cwd=M).stdout.strip()
FORBID = ['scripts/checks/karo_mac_dasumae_gate.sh', 'scripts/checks/karo_mac_manifest_verify.py', 'scripts/checks/karo_mac_manifest_append.py', '.gitignore', '.claude/settings.json', 'scripts/inbox_write.sh']
KISEI = ['docs/evidence/km-47-yotsu-no-kazu-20260917', 'docs/evidence/km-50-kara-wa-todokazu-20260917']
def taba_in(d):
    """既成束の印 = 通常 file の (相対名, sha256) を名で並べた和の sha16 と本数・非通常の本数。"""
    rows = []; hi = 0
    for r, ds, fs in os.walk(M + '/' + d):
        for f in fs:
            q = os.path.join(r, f)
            if not stat.S_ISREG(os.lstat(q).st_mode): hi += 1; continue
            rows.append(os.path.relpath(q, M + '/' + d) + ' ' + hashlib.sha256(open(q, 'rb').read()).hexdigest())
    rows.sort(); return hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16], len(rows), hi
KI = open(E + '/05_chakushu_koku.txt', encoding='utf-8').read().strip()
SEN_MIN = 42; KI_N = 10
L = [f'起 {KI} (= 着手便を inbox_write.sh へ渡す直前の date の刻・raw/05_chakushu_koku.txt・★器 05 が取つた★) / 此の file は器 00 が {now} に書いた(/clear 復帰 → 自己識別 05:30 → 箱 msg_20260917_052946_7760b288(家老の第70弾発注・★唯一の命★・札 queue/tasks/ashigaru-mac-1.yaml は km-69 done の儘で km-70 の札は無い)→ append.py / verify.py / 門 の usage と本文・km-47/km-50 の臺帳・第69弾の器(05/00/10/62/60/67/98)を讀む → 05 を建て(一〜三走目 366/330/312 字で己の G5 が鳴つた・.first/.second/.third)→ {KI[11:]} に着手便 → 00)',
     f'命の出處 = 箱 queue/inbox/ashigaru-mac-1.yaml の msg_20260917_052946_7760b288(from karo-mac・type task_assigned・05:29:46)。裁 322699(臺帳の根は束内相対)+ 322949(門に基点の口・commit 363d5fb・KM_GATE_MANIFEST_BASE)。',
     f'束の在處 = ★main 樹★ {M}/docs/evidence/{KM}(枝 {br}・HEAD {head})。第69弾は worktree karo-mac-a1 に置いたが、本弾は main 樹に置く ―― 理由: ⑴建て直す km-47/km-50 の束は main 樹にのみ在る(worktree の枝 a1-r56 tip 86ae873 には無い)⑵基点の口を持つ門(363d5fb)も main 樹の枝にのみ在る。紙 = ashigaru-mac-1_{KM}.md / 臺帳 = 同名 _manifest.txt(append.py のみ・手書き 0)/ 門控 = 同名 _gate.txt(員外)/ raw/ = 器と出目 / raw/saiken/ = 建て直した km-47・km-50 の臺帳 / _after/ = 門の後の出目。置くのみ・git add -f のみ・commit/push は家老。',
     f'★臺帳の基点(一行)★: 本束の臺帳 ashigaru-mac-1_{KM}_manifest.txt の path は ★束の根 {M}/docs/evidence/{KM}/ からの相對(束内相対・裁 322699)★ ―― append.py を cwd = 束の根で呼ぶ故。照合は KM_GATE_MANIFEST_BASE=<束の根> を門に渡すか、verify.py の第二引数に束の根を渡せ。既定基点(repo 根)で当てれば ★悉く実体無★ と出る ―― disk の欠けではなく基点の違ひ(之が本弾の對照㋑其の物)。raw/saiken/ の二本(km-47・km-50)も同じく ★各々の束の根からの相對★。',
     '禁域の前の sha16(main 樹): ' + ' / '.join(f'{p} {sha16(M + "/" + p)}' for p in FORBID),
     '★既成束の印(前・一字も書かぬ事を 96 が後で同じ器で検める)★: ' + ' / '.join(f'{d.split("/")[-1][:5]} 印 {taba_in(d)[0]} file {taba_in(d)[1]} 非通常 {taba_in(d)[2]}' for d in KISEI),
     f'★宣ETA(端点を先に定める)★: 起点 = 着手便の刻 {KI[11:]} / 端点 = 納め便 1 本目を inbox_write.sh へ渡す直前の date の刻(62 が取る)。宣 = 起 + {SEN_MIN} 分 = 06:17:25(着手便には 06:17 と書いた)。家老基準 = 発注便の刻 05:29:46 〜 納め便の端点(札が無い故 assigned_at の代りに発注便の刻を使ふ)。★建て方★: 器 {KI_N} 本(00/05/20/30/50/59/60/62/70/67)× 2.78 分/器 × 1.5 = {KI_N * 2.78 * 1.5:.1f} → {SEN_MIN} 分。2.78 = 第67弾 3.95・第68弾 2.39・第69弾 2.01(席基準 實 ÷ 器)の平均。第69弾は 3.2 で建てて +27.9 分の過大 ―― 平均を三弾へ延ばした(數を一つ更新した・「気を付ける」ではない)。宣は二方向に外れる ―― 過大なら過大と書く。',
     '★則(測る前に書く)★',
     '㋐ 建て直し 20_tatenaoshi.py: km-47・km-50 の既成の臺帳(各束の *_manifest.txt・讀むのみ)の行を verify.py の paths_of(讀み手と同じ器)で讀み、path の頭 docs/evidence/<束>/ を落として束内相対の名に直し、★cd <束の根>★ で karo_mac_manifest_append.py を呼んで raw/saiken/<束>_manifest.txt に建てる(新しい臺帳・既成の臺帳へ 0 字)。母數 = 既成の臺帳の項。検め: ⑴頭が束の名でない行 = 0 ⑵束に無い名 = 0 ⑶新旧の (相対名, sha256) 対が悉く一致 ⑷括つた行の数(空白名・km-47 の fixture 1 本を期待)⑸員外(束に在つて臺帳に無い file)の名と数 ⑹封 = 新臺帳の sha256・bytes・行。',
     '㋑ 對照 30_taishou.py(各束 × 三本・verify.py 直と門の双方・cwd = main 樹): ㋐ 明示基点 = 束の根(verify 第二引数 / 門 KM_GATE_MANIFEST_BASE=束の根)→ 期待 一致 N / 実体無 0 / rc 0 ㋑ 基点を渡さず(既定 = repo 根・環境変数を ★unset★)→ 期待 ★実体無 N / rc 1★(出なければ建て直せて居らぬ)㋒ 出鱈目な基点 /detarame/naki/ne → 期待 実体無 N / rc 1。参考 ㋓ 基点 ""(cwd 相対)を cwd = 束の根で → 一致 N(第69弾 98 の再現・cwd に依る故 使はぬ)。門は「min」(臺帳を file としても渡す・條②〜⑤を清い一本に掛けて條①を孤立させる)と「all」(臺帳の項 悉く)の二走 ―― rc は條で割つて書く(條②〜④が既成束の file で鳴つても條①の出目と混ぜぬ)。四数(母數・一致・相違・実体無)・讀めぬ行・旧形・基点の文言・rc を悉く紙へ。',
     '㋒ 己の臺帳 50: cd 束の根 → append.py(束内相対)。門 60 は KM_GATE_MANIFEST_BASE=束の根 で main/all の二走 + 基点無しの一走(★落ちる事を見せる★・門控には三走とも写す)。',
     '作法: 便の器 62 は臺帳より先に書く / 字数は鎖の前 / 鎖は一つづつ rc / ad-hoc python は -B / raw への本文は悉く kaki / 門控の名 = 60_gate_top.r70 / 生器(scripts/ ~/bin)へ 0 字 / 既成束(km-47・km-50・km-69)へ 0 字(讀むのみ・印で證す)/ 倒れた走は .first に残す / 空は「空である旨の一行」/ rc は pipe に通さぬ。',
     '★己の疵(起の時点で既に)★: ⑴ 束の骨組み(mkdir・kaki/10_run の cp)と .first の cp を手で打つた。⑵ 05 の胴を三度削つた(削るより割れの條に反する ―― 着手便は一通の條を優先した)。⑶ 既讀化は ~/bin/inbox_mark_read.py(器)で行つた(第69弾の疵⑴を塞いだ)。']
K.kaku(E + '/00_start.txt', '\n'.join(L)); print(open(E + '/00_start.txt', encoding='utf-8').read()[:1200])
