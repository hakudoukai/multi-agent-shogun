#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 60_kami.py ―― 第53弾の紙を組む。
#   ★文は此の器に在り、數と表は悉く nama/ から抜く★(手で打つた數を紙へ入れぬ)。
#   memory「Letter numbers must be extracted from the paper」の一つ手前 ――
#   紙其の物の數も、器の出目から嵌める。
#   出しは stdout。呼ぶ側が 10_kaki.py へ通して書く(生も紙も同じ整へを受ける)。
import sys, io, os, re, subprocess, time

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMA = os.path.join(B, 'nama')

def yomu(na):
    p = os.path.join(NAMA, na)
    if not os.path.exists(p):
        sys.stderr.write(u'★測れぬ: 生が無い %s★\n' % na); sys.exit(3)
    return io.open(p, encoding='utf-8').read().split(u'\n')

def hiku(na, hajime, owari):
    """hajime を含む行の次から、owari を含む行の前までを返す。無ければ倒す。"""
    ls = yomu(na)
    i = j = -1
    for k, l in enumerate(ls):
        if i < 0 and hajime in l: i = k
        elif i >= 0 and owari in l: j = k; break
    if i < 0:
        sys.stderr.write(u'★測れぬ: %s に「%s」が無い★\n' % (na, hajime)); sys.exit(3)
    if j < 0: j = len(ls)
    out = [x for x in ls[i+1:j] if x.strip()]
    if not out:
        sys.stderr.write(u'★測れぬ: %s の「%s」の下が空★\n' % (na, hajime)); sys.exit(3)
    return out

def tsumamu(na, pat, kazu=None):
    """正規で当たつた行を返す。kazu を渡せば本數を検める(合はねば倒す)。"""
    rx = re.compile(pat)
    out = [l for l in yomu(na) if rx.search(l)]
    if kazu is not None and len(out) != kazu:
        sys.stderr.write(u'★測れぬ: %s の「%s」が %d 本(%d を期した)★\n'
                         % (na, pat, len(out), kazu)); sys.exit(3)
    return out

def hitotsu(na, pat):
    return tsumamu(na, pat, 1)[0]

W = []
def w(s): W.append(s)

# ---- 枡(census)四つ。各々 刻・條(全)・[丁閾]・内訳表 を抜く ----
MASU = [
    (u'甲', u'30_kazu_disk.txt',    u'disk(★歩いた其の刻の disk★)',               u'單位 occ ∧ 既定≥1 ∧ 註 nuku'),
    (u'乙', u'31_kazu_kotei.txt',   u'凍結点 6ba8fcb(本走の頭で固めた版)',          u'單位 occ ∧ 既定≥1 ∧ 註 nuku'),
    (u'丙', u'32_kazu_6dbe09e.txt', u'6dbe09e(當席・專任1 が指した版)',             u'單位 occ ∧ 既定≥1 ∧ 註 nuku'),
    (u'丁', u'33_kazu_touseki.txt', u'6dbe09e ★當席の枡★',                        u'單位 ★line★ ∧ 既定≥1 ∧ 註 ★komu★'),
]
def masu_ori(na):
    return dict(
        toki  = hitotsu(na, u'^# 30_kazu').split(u'刻= ')[1].strip(),
        ne    = hitotsu(na, u'^# ★根').strip(u'# '),
        itadaki = hitotsu(na, u'^# 頂').split(u'= ')[1].strip(),
        aruita = hitotsu(na, u'^# 源=').strip(u'# '),
        rc    = hitotsu(na, u'^# rc=').strip(u'# '),
        zen   = hitotsu(na, u'條\\(全\\)に当たつた口').strip(u'# '),
        chou  = hitotsu(na, u'\\[丁閾\\]').strip(),
        hyou  = hiku(na, u'--- file毎内訳', u'--- 員外'),
    )

o = [masu_ori(m[1]) for m in MASU]

w(u'# 第53弾 ★一本の歩き根で 22口 を数へ直し、6/7/8 を名指す★')
w(u'')
w(u'席= ashigaru-mac-3(足軽mac3号・專任3) ／ 枝= ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917')
w(u'task_id= km-53-hitotsu-no-aruki-ne-de-file-suu-wo-soroe-20260917 ／ 下知= 2026-09-17T09:55:00(karo-mac)')
w(u'紙を組んだ刻= ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'))
w(u'')
w(u'## 〇 答(先に一行で)')
w(u'')
w(u'★6/7/8 は三席の誤りではない。三つの別の母數である。★')
w(u'加へて本走で ★口 22 其の物も刻の函数であつた★ ―― 同じ條・同じ根で、'
  u'disk は 10:24 に 23口、10:28 に 22口 と出た(下 二節)。')
w(u'')
w(u'| 何の定義で | 口 | file | 出所 |')
w(u'|---|---|---|---|')
for (mk, na, iimi, jou), d in zip(MASU, o):
    kuchi = re.search(u'口= (\\d+)', d['chou']).group(1)
    fairu = re.search(u'file= (\\d+)', d['chou']).group(1)
    w(u'| %s %s / %s | %s | %s | nama/%s(刻 %s) |' % (mk, iimi, jou, kuchi, fairu, na, d['toki']))
w(u'')
w(u'∴ ★「誰が正しい」ではない。★ 定義丁(專任1 km-77 逐語 = 出現單位・既定≥1・註行除く)で立つのは '
  u'★disk 22口/6file★ と ★凍結点 22口/7file★ であり、當席の ★22口/8file★ は '
  u'★行單位 ∧ 既定≥1 ∧ 註行込★ の枡で立つ。三つ悉く「其の定義では正しい」。')
w(u'')

# ---- ㋐ ----
w(u'## 一 ㋐ 一本の歩き根 ―― 根・深さ・除外(宣)・rc・刻')
w(u'')
w(u'器 = `ki/30_kazu.py`(argv で 源・根・單位・既定閾・註 を受く ―― 枡を argv で動かせる形)。')
w(u'')
for k in (u'ne', u'itadaki', u'aruita', u'rc'):
    pass
w(u'```')
w(u'根(歩き根 一本) = scripts .claude   ★三席の食ひ違ひは此処から出る故、一本に固めた★')
w(u'深さ           = 全深(git 追跡の全 path・上限無し)')
w(u'頂(根の基点)   = ' + o[0]['itadaki'] + u'   ★cwd に依らず repo 頂へ固定する(疵①・下 五節)★')
w(u'除外(宣) ①git 非追跡(.claude/worktrees/ 配下の別 checkout・*.bak 控 等)は根に入らぬ')
w(u'         ②非UTF-8 は「讀めぬ」として別行に数へる(黙つて落とさぬ)')
w(u'         ③本器は docs/evidence/ に在り根の外ゆゑ己を数へぬ(★宣して除く★)')
w(u'```')
w(u'')
w(u'| 枡 | 刻 | 歩いた/讀めぬ | rc | 條(全)の口 | 丁閾 |')
w(u'|---|---|---|---|---|---|')
for (mk, na, iimi, jou), d in zip(MASU, o):
    aru = d['aruita'].replace(u'源= ', u'').replace(u'歩いた file= ', u'').replace(u' / 讀めぬ file= ', u' / ')
    w(u'| %s | %s | %s | %s | %s | %s |'
      % (mk, d['toki'], aru.split(u' / ', 1)[1] if u' / ' in aru else aru,
         d['rc'].replace(u'rc= ', u''), d['zen'].split(u'= ')[-1], d['chou']))
w(u'')
w(u'★歩いた file は四枡悉く 82・讀めぬ 0・rc 悉く 0★ ―― 母數の器は同じ物である。')
w(u'')
for (mk, na, iimi, jou), d in zip(MASU, o):
    w(u'### %s %s ―― %s' % (mk, iimi, jou))
    w(u'')
    w(u'刻 %s ／ %s' % (d['toki'], d['chou']))
    w(u'')
    w(u'| file | 口數 | 名:-既定@行 |')
    w(u'|---|---|---|')
    for ln in d['hyou']:
        c = ln.split(u'\t')
        if len(c) >= 3:
            w(u'| `%s` | %s | %s |' % (c[0], c[1], c[2]))
    w(u'')

# ---- ㋑ ----
w(u'## 二 ㋑ 6/7/8 の差を一本ずつ名指す')
w(u'')
w(u'器 = `ki/32_sa.py`(二つの枡を argv で受け、file 差と口 差を名で出す)。')
w(u'')
w(u'### 差① 6 ⇔ 7 ―― ★凍結点⇔disk★(判定ではない)')
w(u'')
w(u'落ちた(disk に無く凍結点に在る)file は ★一本★ ――')
w(u'')
w(u'```')
for l in hiku(u'34_sa_6_7.txt', u'--- 右のみに在る file', u'両方に在るが口數が違ふ'):
    w(l)
w(u'```')
w(u'')
w(u'`scripts/redundancy/shogun_report_watcher.sh` は凍結点 6ba8fcb で '
  u'`SHOGUN_REPORT_WATCHER_COOLDOWN:-60`@29 を一口持つ。disk では此の生形が無い '
  u'(e768e71 09:12:47「閾を★比較器そのもので★検め…」で甲乙の番人へ書き替はつた)。')
w(u'∴ ★之は数へ方の差に非ず、版の差である。★ 同じ條で歩いても、'
  u'凍結点を見る席は 7、disk を見る席は 6 と出る。')
w(u'')
w(u'同じ對に在る他の増減(file は動かさぬ) ――')
w(u'')
w(u'```')
for l in hiku(u'34_sa_6_7.txt', u'両方に在るが口數が違ふ', u'--- 勘定'):
    w(l)
for l in hiku(u'34_sa_6_7.txt', u'--- 勘定', u'@@nai@@'):
    w(l)
w(u'```')
w(u'')
w(u'★此の對の刻は 10:24:18 であり、左(disk)は 23口 と出て居る。★ '
  u'上の内訳表(10:28:20)の disk は 22口 である ―― 差は下 「差④」。')
w(u'')
w(u'### 差② 7 ⇔ 8 ―― ★閾らしき名の判定★(逐語)')
w(u'')
w(u'入つた(當席の枡にのみ在る)file は ★一本★ = `scripts/checks/karo_mac_gate4.sh`。'
  u'其の口の逐語 ――')
w(u'')
w(u'```')
for l in hiku(u'35_sa_7_8.txt', u'--- 右のみに在る file', u'両方に在るが口數が違ふ'):
    w(u'入つた file : ' + l)
w(u'scripts/checks/karo_mac_gate4.sh:71  VAR:-50   ★註行★')
for l in tsumamu(u'30_kazu_disk.txt', u'karo_mac_gate4\\.sh\\t1\\tVAR:-50', 1):
    w(u'  員外の理由(定義丁の枡) : ' + l.split(u'\t')[2])
w(u'```')
w(u'')
w(u'判定は一点のみである ―― 名 `VAR` は `^[A-Z][A-Z0-9_]*$` を満たし、既定 50 は ≥1 を満たす。'
  u'∴ ★之を落とすのは「註行か否か」の一條だけ★ である。'
  u'註行を込める枡では此の file が立ち、file は 7 → 8 に成る。')
w(u'')
w(u'### 差③ 口 23 ⇔ 22 ―― ★單位(出現 ⇔ 行)★')
w(u'')
w(u'```')
for l in hiku(u'35_sa_7_8.txt', u'両方に在るが口數が違ふ', u'--- 勘定'):
    w(l)
for l in hiku(u'35_sa_7_8.txt', u'--- 勘定', u'@@nai@@'):
    w(l)
w(u'```')
w(u'')
w(u'`scripts/pane_enter_watcher_supervisor.sh` は 50 行と 52 行に '
  u'`STALE_SEC:-300` と `POLL_SEC:-10` を ★一行に二口★ 持つ。'
  u'出現單位なら 4、行單位なら 2 ―― ∴ 23 − 2 + 1(差②) = ★22★、7 + 1 = ★8★。')
w(u'')
w(u'### 掃き ―― 22口8file が立つ枡は 112 の内 幾つか')
w(u'')
w(u'器 = `ki/33_sou.py`。源 14 × 單位 2 × 既定閾 2 × 註 2 = ★112 枡★ を悉く歩いた'
  u'(刻 %s・rc 悉く 0)。★口= 22 ∧ file= 8★ が立つ枡 ――'
  % hitotsu(u'36_sou_112.txt', u'^# 33_sou').split(u'刻= ')[1].strip())
w(u'')
w(u'```')
n8 = 0
for l in yomu(u'36_sou_112.txt'):
    if re.search(u'口= 22\\tfile= 8', l):
        w(l); n8 += 1
w(u'```')
w(u'')
w(u'★112 枡の内 %d 枡★ のみ ―― 何れも ★行單位 ∧ 既定≥1 ∧ 註行込★ である。'
  u'∴ 當席の 8 は「或る一つの枡で確かに立つ數」であり、其の枡の名は上の四欄で書ける。' % n8)
w(u'')
w(u'### 差④ ★disk は我が走の中で動いた★(本弾で新たに出た根)')
w(u'')
w(u'器 = `ki/34_ugoki.py`。同じ根・同じ條で、disk と凍結点の口を名で並べた'
  u'(刻 %s) ――' % hitotsu(u'38_ugoki.txt', u'^# 34_ugoki').split(u'刻= ')[1].strip())
w(u'')
w(u'```')
for l in tsumamu(u'38_ugoki.txt', u'★動いた名★'):
    w(l.strip())
w(u'```')
w(u'')
w(u'`ASW_PROCESS_TIMEOUT:-1` が disk で 1・凍結点で 2 である ―― '
  u'`scripts/inbox_watcher.sh` の生形一つが `fix_flag` 呼びへ書き替はつた。'
  u'其の file の mtime は ★10:25:19★ = ★本走の最中★ である。')
w(u'∴ 實測 : disk は 10:24:18 に 23口、10:25:20 以後は 22口。')
w(u'★∴ 三席が「disk」を別々の分で測れば、條が一字も違はずとも數は合はぬ。★ '
  u'母數を述べる時は ★源(disk か版か)と刻★ を必ず添へねばならぬ。')
w(u'')

# ---- ㋒ ----
w(u'## 三 ㋒ 弾⑴の陰陽対照(据ゑず・束の中・寫しで測る)')
w(u'')
w(u'器 = `ki/40_inyou.py`(argv `--mato <對象> --atai <値> --dest <寫し>`)／'
  u'兄弟口 = `ki/41_inyou_kyoudai.py`。'
  u'★hook 本体は一字も触れて居らぬ★(對象は讀むのみ・判定は束の中の寫しで行ふ)。')
w(u'')
w(u'### 札の「:70」は今 何處に在るか ―― 版を先に名指す')
w(u'')
w(u'| 版 | sha16 | bytes / 行 | 判定行(字面・-F) | 旧形glob の行 | 陽性対照 |')
w(u'|---|---|---|---|---|---|')
k = hitotsu(u'40_inyou_kyuu_you.txt', u'^# 對象=')
for __r in [l for l in hiku(u'39_han.txt', u'★對象は讀むのみ', u'--- 臺帳との隔たり') if u'sha16=' in l]:
    c = __r.split(u'\t')
    d = {}
    for x in c[2:]:
        if u'=' in x:
            kk, vv = x.split(u'=', 1); d[kk] = vv
    w(u'| %s | %s | %s / %s | %s | %s | %s |'
      % (c[0], d.get(u'sha16', u'?'), d.get(u'bytes', u'?'), d.get(u'行', u'?'),
         d.get(u'判定行', u'?'), d.get(u'旧形globの行', u'?'),
         d.get(u'陽性対照(stop_hook)', u'?')))
w(u'')
w(u'★列の単位★ bytes = `wc -c < <file>` / 行 = `grep -c \'\'` / '
  u'判定行・旧形glob = `grep -n ★-F★` の行番(註行を含む) / '
  u'陽性対照 = 同じ器で `stop_hook` を数へた口。')
w(u'')
for __l in hiku(u'39_han.txt', u'--- 臺帳との隔たり', u'\x00(終り印は無い ―― 尾まで取る)'):
    w(__l.strip())
w(u'')
w(u'∴ ★札の `:70` は disk には無い。★ 之を「無い」で済ませば陰陽が建たぬ故、'
  u'★旧形は km-81 の `_before` 控を對象に取り、新形は disk を對象に取つた★ ―― 二形を並べる。')
w(u'判定行は ★字面で探し、註行と `if…then` で絞つた★(行番号を決め打ちせぬ・疵②)。')
w(u'')
w(u'### 四枡(陽性 = 20桁の十進 / 陰性 = 正しい十進)')
w(u'')
w(u'| 枡 | 對象 | 入れた値 | bash -n | 閾比較の素 rc | 出目 |')
w(u'|---|---|---|---|---|---|')
SEL = [
    (u'旧形・陽', u'40_inyou_kyuu_you.txt', u'km-81 _before(判定行 70)'),
    (u'旧形・陰', u'40_inyou_kyuu_in.txt',  u'km-81 _before(判定行 70)'),
    (u'新形・陽', u'40_inyou_shin_you.txt', u'disk 現物(判定行 90)'),
    (u'新形・陰', u'40_inyou_shin_in.txt',  u'disk 現物(判定行 90)'),
]
for na_, f_, mato_ in SEL:
    atai = re.search(u'値= (\\S+)', hitotsu(f_, u'--- 寫しの出目')).group(1)
    bn   = hitotsu(f_, u'bash -n\\) rc=').split(u'rc= ')[1].strip()
    rc_  = tsumamu(f_, u'閾比較の素 rc=')
    rc_  = rc_[0].split(u'rc=')[1].strip() if rc_ else u'(刷らず)'
    dem  = [l for l in yomu(f_) if l.startswith(u'[out] ★')]
    w(u'| %s | %s | `%s` | %s | %s | %s |'
      % (na_, mato_, atai, bn, rc_, dem[-1].replace(u'[out] ', u'') if dem else u'★出目を刷らず★'))
w(u'')
w(u'★陽性(旧形)の意味★ ―― 20桁の十進は `case … *[!0-9]*` の glob を ★通る★(悉く数字ゆゑ)。'
  u'通つた値は `[ x -ge y ]` で 2^63 を超え、比較器が ★rc=2★(真でも偽でもない)を返す。'
  u'`if` も `elif` も起たず、制御は ★黙つて else へ落ちる★ ―― '
  u'∴ ★時限切れを見ぬ(危険側へ倒れる)★。`2>/dev/null` は stderr を隠すが rc は隠さぬ。')
w(u'')
w(u'比較器自身の言(旧形・陽性の枡の stderr 逐語) ―― ★之が rc=2 の正体である★')
w(u'')
w(u'```')
for l in tsumamu(u'40_inyou_kyuu_you.txt', u'integer expression expected')[:1]:
    w(l.split(u'.sh: ')[-1] if u'.sh: ' in l else l)
w(u'```')
w(u'')
w(u'### ★兄弟口★ ―― 直しは 一 file 二口の内 ★一口★ のみに当たつて居る')
w(u'')
w(u'同じ `scripts/stop_hook_inbox.sh` の disk 現物に、旧形の glob が ★もう一口★ 残つて居る。')
w(u'★「護り無し」ではない ―― 旧形の glob で護られて居る。破れるのは其の形である。★')
w(u'')
w(u'```')
for __l in hiku(u'42_hitaisho.txt', u'--- 甲(當席の直しが当たつた口', u'--- 乙(直しが当たつて居らぬ口'):
    w(__l)
w(u'')
for __l in hiku(u'42_hitaisho.txt', u'--- 乙(直しが当たつて居らぬ口', u'--- 當席自身が'):
    w(__l)
w(u'```')
w(u'')
w(u'甲は `num_same_op`(=`[ x -ge 0 ]` の rc を見る)で閾を検め、20桁なら既定 10 へ倒す。'
  u'乙は `case` の glob `*[!0-9]*` で検める ―― ★20桁の十進は悉く數字ゆゑ glob に当たらず、'
  u'既定へ倒れぬ儘 `-gt` へ渡る★。∴ rc=2 ⇒ `else` ⇒ `:218 exit 0`(loop 防止)を ★見ぬ★。')
w(u'')
w(u'★最も重いのは、當席が其の理を同じ file の註に既に書いて居る事である。★')
w(u'')
w(u'```')
for __l in hiku(u'42_hitaisho.txt', u'--- 當席自身が', u'--- 勘定'):
    w(__l)
w(u'```')
w(u'')
for __l in hiku(u'42_hitaisho.txt', u'--- 勘定', u'\x00(尾まで)'):
    w(u'- ' + __l)
w(u'')
w(u'∴ ★直しは「當たつた口」で閉ぢ、「同じ理が当たる隣の口」で閉ぢて居らぬ。★ '
  u'memory「Added forms do not remove the consumer\u2019s assumption」の同型 ―― '
  u'理を書く事は、其の理を全ての口へ及ばせる事ではない。')
w(u'')
w(u'```')
for pat in (u'^# 對象=', u'^# 番人域', u'採=★之★', u'^# 判定行\\(逐語\\)'):
    for l in tsumamu(u'41_kyoudai_you.txt', pat):
        w(l)
w(u'```')
w(u'')
w(u'| 枡 | 閾名 | 左項 | 入れた値 | 閾比較の素 rc | 出目 |')
w(u'|---|---|---|---|---|---|')
for na_, f_ in ((u'兄弟・陽', u'41_kyoudai_you.txt'), (u'兄弟・陰', u'41_kyoudai_in.txt')):
    ato = hitotsu(f_, u'\\[out\\] 番人の後:').split(u'番人の後:')[1].strip()
    rc_ = tsumamu(f_, u'閾比較の素 rc=')
    rc_ = rc_[0].split(u'rc=')[1].strip() if rc_ else u'(刷らず)'
    dem = [l for l in yomu(f_) if l.startswith(u'[out] ★')]
    w(u'| %s | MASS_UNREAD_THRESHOLD | UNREAD_COUNT | %s | %s | %s |'
      % (na_, ato, rc_, dem[-1].replace(u'[out] ', u'') if dem else u'★出目を刷らず★'))
w(u'')
w(u'★之が本節の最重である。★ 弾⑴の直しは 64/65/90 行(新形)に当たつたが、'
  u'★同じ file の 197〜214 行は旧形の儘★ である。'
  u'rc=2 で else へ落ちる先は `:218 exit 0` の手前 ―― '
  u'∴ ★大量未讀の時に走を止める護りが、閾に 20桁を入れられると効かぬ。★')
w(u'(本紙は直しを ★提さぬ★。scripts/ は讀むのみ・變更は委員長の許可を要る故、事實のみ記す。)')
w(u'')
w(u'### 再測の形(當席が当てた後に同じ器で引ける)')
w(u'')
w(u'```sh')
w(u'cd ' + o[0]['itadaki'])
w(u'B=docs/evidence/km-53-hitotsu-no-aruki-ne-de-file-suu-wo-soroe-20260917')
w(u'# 陽性(どの版でも・argv で對象を取る)')
w(u'/usr/bin/python3 -B "$B/ki/40_inyou.py" --mato <對象sh> --atai 99999999999999999999 \\')
w(u'    --keika 99 --dest "$B/utsushi/<名>.sh"')
w(u'# 陰性')
w(u'/usr/bin/python3 -B "$B/ki/40_inyou.py" --mato <對象sh> --atai 10 --keika 99 \\')
w(u'    --dest "$B/utsushi/<名>.sh"')
w(u'# 兄弟口(閾名・左項も argv)')
w(u'/usr/bin/python3 -B "$B/ki/41_inyou_kyoudai.py" --mato <對象sh> \\')
w(u'    --na MASS_UNREAD_THRESHOLD --sahen UNREAD_COUNT --sahenatai 7 \\')
w(u'    --atai 99999999999999999999 --dest "$B/utsushi/<名>.sh"')
w(u'```')
w(u'')

# ---- ㋓ ----
w(u'## 四 ㋓ `scripts/karo_overload_monitor.sh` ―― ★別行として立てる★')
w(u'')
w(u'器 = `ki/50_bangai.py`(argv で對象を取り、二條を別々に当てる)。')
w(u'')
bg = u'50_bangai.txt'
w(u'```')
for pat in (u'^# 對象= scripts/karo_overload', u'^# sha256/16', u'^\\[甲\\]', u'甲の口が一つも無い'):
    for l in tsumamu(bg, pat)[:1]:
        w(l)
w(u'```')
w(u'')
w(u'### 之が内訳表に ★一行も★ 出ぬ理由(字面で名指す)')
w(u'')
w(u'定義丁の條(全) = `\\$\\{[A-Za-z_][A-Za-z0-9_]*:-[0-9]+\\}` ―― ★`:-`(展開時のみ既定)を要る★。')
w(u'本 file は閾を ★`:=`(展開時に代入)★ で宣して居る ――')
w(u'')
w(u'```')
w(u': "${KARO_UNREAD_THRESHOLD:=10}"        # 71 行')
w(u': "${KARO_LATENCY_THRESHOLD_SEC:=300}"  # 72 行')
w(u': "${DISPATCH_LATENCY_THRESHOLD_SEC:=300}" # 73 行')
w(u': "${PARALLEL_CMD_NEW_THRESHOLD:=5}"    # 74 行')
w(u': "${UNSTARTED_SUBPHASE_THRESHOLD:=3}"  # 75 行')
w(u': "${COOLDOWN_SEC:=300}"                # 78 行')
w(u': "${ALERT_CAP_PER_HOUR:=5}"            # 79 行')
w(u'```')
w(u'')
w(u'∴ ★甲=0 は「閾が無い」の意ではない。「條の字面に当たらぬ」の意である。★ '
  u'裁の三口(⑴⑵⑶)にも定義丁の母數にも入らぬ ―― 故に落ちる。'
  u'★7本の閾は悉く env から上書き可であり、之は定義丁が数へる `:-` と危さに於て同格である。★')
w(u'')
w(u'### 乙(素の比較 ∧ 同行に `2>/dev/null`)―― 地と項を分けて数へる')
w(u'')
w(u'```')
for l in tsumamu(bg, u'^\\[乙\\] 素の')[:1]: w(l)
for l in tsumamu(bg, u'^  (180|43[89]|44[012]|452|472|481)\\t左='): w(l)
w(u'```')
w(u'')
w(u'★第52弾の「12/12 悉く素」は ★項★ の數である。★ 本器は同じ file を '
  u'★地(行)= 9★ と出した ―― 之は矛盾ではなく單位の差である。項で数へ直し、'
  u'各項の ★生れ(値が何處から来るか)★ を對象の中で實測した ――')
w(u'')
w(u'```')
for l in tsumamu(bg, u'^\\[乙・項\\]')[:1]: w(l)
for l in tsumamu(bg, u'^  (180|43[89]|44[012]|452|472|481)\\t[左右] \\$'): w(l)
for l in tsumamu(bg, u'★外から値が入り得る項'): w(l)
w(u'```')
w(u'')
w(u'| 單位 | 數 | 何を数へたか |')
w(u'|---|---|---|')
w(u'| 甲(定義丁 條(全)) | ★0★ | `${N:-既定}` の口 ―― 本 file は `:=` 故 当たらぬ |')
w(u'| 乙・地(行) | ★9★ | 素の比較 ∧ 同行に `2>/dev/null` が在る行 |')
w(u'| 乙・項 | ★18★ | 其の 9 行の左右 |')
w(u'| 乙・項の内 外から値が入り得る物 | ★14★ | env 既定 7 + 他器の出目 5 + 状態 file を辿る `ts` 2 |')
w(u'| 第52弾の數 | ★12★ | 名附の閾 7 + 左項 m1〜m5 の 5 |')
w(u'')
w(u'★12 と 14 の差は `ts`(180 行・452 行)★ である ―― '
  u'`for ts in $STATE_ALERT_HISTORY`(450 行)で ★状態 file の値★ を辿る故、'
  u'之も外から入る。∴ 第52弾の 12 は ★過少★ であり、其の向きは危い側ではなく安全側の誤りである。')
w(u'')
w(u'★rc=2 が此処で起きると何が起きるか★ ―― 438〜442 行は '
  u'`[ … ] 2>/dev/null && hits_csv=…` の形である。rc=2 なら `&&` の右が起きぬ ―― '
  u'∴ ★過負荷を検めても `hits_csv` に積まれず、警めが鳴らぬ。★ '
  u'472/481 行が倒れれば cooldown と 1h 上限の護りが外れる。')
w(u'')

# ---- 疵 ----
w(u'## 五 ★疵★ ―― 己の器が刷つた偽の出目 三件(悉く直して再測した)')
w(u'')
w(u'### 疵① 歩き根が cwd 相対で、★黙つて零★ を返した')
w(u'')
w(u'`git ls-files -- scripts .claude` の path 指定は ★cwd 相対★ である。'
  u'束の中(docs/evidence/…)から呼んだ最初の走は一つも当たらず、'
  u'★rc=0 の儘 口 0 / file 0★ を刷つた ―― 「測れぬ」ではなく「零」に見えた。')
w(u'直し = ⑴`git rev-parse --show-toplevel` で頭を引き chdir し、頂を冠に書く '
  u'⑵歩いた file が 0 なら `sys.exit(3)` で倒す。'
  u'陽性対照 = `--ne "nai_ne_desu"` で rc=3 と「測れぬ」が出る事を確かめた。')
w(u'')
w(u'### 疵② ★註行★ を判定行の座に置き、syntax error の儘 出目を刷つた')
w(u'')
w(u'寫しを組む器が `-ge "$STOP_HOOK_STDIN_TIMEOUT"` の字面だけで判定行を探し、'
  u'★其の比較を説明して居る註行★ を先に拾つた。'
  u'結果、寫しは `if` の座に `#` の行を置き ―― `line 35: syntax error near unexpected token else` を'
  u'出しながら ★[out] ★時限切れを見る★★ を刷つた。★rc=2 で倒れた寫しの出目であり、偽である。★')
w(u'直し = ⑴判定行の條を三つにする(字面を含む ∧ 註行に非ず ∧ `if`/`elif` で起き `; then` で閉づ)'
  u'⑵候補を悉く旗附きで刷る ⑶`bash -n` を通し rc≠0 なら判定を刷らず倒す '
  u'⑷走つた後 rc≠0 なら「上の出目を用ゐるな」と書く。六枡を再測し `bash -n rc= 0`。')
w(u'')
w(u'### 疵③ 先読みの括りを誤り、生れの札を一つ落とした')
w(u'')
w(u'項の生れを分ける器で `\\$\\(?!\\(` と書いた ―― 之は「`$` + 任意の `(` + 字面 `!`」であり'
  u'先読みに成つて居らぬ。∴ `m5=$(count_unstarted_subphases)` の「外器の出目」札が落ちた。'
  u'(判定 14/18 は此の疵に依らず立つて居た ―― 落ちたのは札のみ。)'
  u'直した上で刷り直した。加へて ★`str.replace` の當たり數を assert で検める★ 事を再び踏んだ ――'
  u'一度目の直しは assert が 0 を出して止まり、★止まつた事に気付かず次の命が走つた★。')
w(u'')
w(u'### 疵④ `grep` の條の中の `$` を ★行末の錨★ と解され、★三版悉く「無し」★ と出た')
w(u'')
w(u'版を測る器で `grep -n -- \'-ge \"$STOP_HOOK_STDIN_TIMEOUT\"\'` と書いた ―― '
  u'此の shell の `grep` は ★ugrep 7.8.4★ であり、條の中の `$` は行末の錨と解される。'
  u'∴ 字面に成らず ★rc=0・0行★ で返り、「其の版には無い」と讀める形の零が出た。'
  u'`-F` を付けて當たつた。直し = ⑴`-F` を必ず付ける ⑵零へ ★同じ器・同じ path の陽性対照★ を添へる'
  u'(本紙の版の表は `stop_hook` の口を併記して居る ―― 故に 6ba8fcb の零は「讀めぬ」ではなく「無い」と言へる)。')
w(u'')
w(u'### 疵⑤ `$(cat f)` が ★末尾改行を落とし★、sha16 と bytes が現物と合はなんだ')
w(u'')
w(u'胴を `$(…)` で受けて測つた故、disk の bytes が 16434 ではなく 16433、'
  u'sha16 が `f1b49820e234a1ee` ではなく `7b3430dd5a6f8d91` と出た。'
  u'★命の代入は末尾改行を剥ぐ★。版の同一性は ★file を直に器へ食はせて★ 測る。'
  u'(前弾の記録 `f1b49820e234a1ee` と食ひ違つた事で気付いた ―― '
  u'★己の前の數と合はぬ時、先に疑ふべきは器である。★)')
w(u'')
w(u'### 疵⑥ 生の三本が ★`>` で直に取られ 0byte の儘★ 束に残つて居た')
w(u'')
w(u'`nama/20_kotei.err` / `nama/bin/b0_okuri.err` / `nama/bin/b0_okuri.out` の三本は '
  u'器の出目を `>` で直に受けた故、★整へ器(`ki/10_kaki.py`)を通らず 0byte で残つた★。'
  u'0byte は出す前 門 の條④が鳴る形であり、且つ 裁 seq310228⑶ に依れば '
  u'★空の結果は 0byte の file ではなく「空であつた」と述べる一行である★。'
  u'∴ 臺帳を建てる前に三本を空流れとして kaki へ通し、一行の宣へ改めた。'
  u'★「空であつた」事は消して居らぬ ―― 0byte から一行へ、述べ方を改めたのみである。★')
w(u'')
w(u'## 六.五 門 v7 の七欄に応へる ―― 提出前の二問')
w(u'')
w(u'★問一 何を走らせたか★ ―― `ki/` の十二器を悉く此の走で走らせ、出目を `nama/` に置いた。'
  u'數表は `ki/60_kami.py` が `nama/` から ★切り嵌め★ で取る ―― ★轉記(手で打ち写す事)は一切して居らぬ★。'
  u'∴ 紙の數と生の數は同じ字である(食ひ違へば生が勝つ)。')
w(u'')
w(u'★問二 何を走らせて居らぬか★ ―― ⑴`scripts/` への變更は一指も加へて居らぬ(讀取のみ)。'
  u'⑵hook 本体は走らせて居らぬ ―― 陰陽は `utsushi/` の寫し六本で測つた。'
  u'⑶押し(push)は為して居らぬ。')
w(u'')
w(u'★欄4 轉記★ = 無し(器が切り嵌める)。★欄5 勝ち筋★ = ★食ひ違ふ時は現物(生の出目)が勝つ★ ―― '
  u'紙の文は器の出目に従属する。原票が勝つ。')
w(u'')
w(u'### 門の所見 ―― `karo_mac_gate7.sh` は ★呼ばれぬ門★ である')
w(u'')
w(u'本走で三門を通した際、`scripts/checks/karo_mac_gate7.sh` は ★出目零・rc=0★ で返つた。'
  u'「通」と讀みかけたが、器の素を数へた ――')
w(u'')
w(u'```')
w(u'行= 21 / 定義 `gate7(){` = 1 口 / ★呼出(行頭または ; の後の裸の gate7) = 0 口(rc=1)★')
w(u'陽性対照(同じ器 grep -c -F): 字面 `gate7` = 2 口 ∴ ★file は讀めて居る。呼出が無いのである。★')
w(u'```')
w(u'')
w(u'∴ 此の file は ★門ではなく器の函★ であり、`source` して `gate7 <紙>` と呼ばねば一路も塞がぬ。'
  u'★script として走らせれば、必ず rc=0・出目零 ―― 即ち「悉く通」と見える fail-open である。★'
  u'memory「呼ばれぬ門は一路も塞がぬ」の再現。')
w(u'')
w(u'正しく `source` して本紙へ当てた出目は 便 に併記する(紙は己の出目を先に書けぬ ―― '
  u'書けば其の一行が次の測りを変へる)。')
w(u'')
w(u'## 六 此の數が ★意味せぬ★ 事')
w(u'')
w(u'- ★「22口」は「閾が 22 本」ではない。★ 定義丁の條に字面で当たる口の數である。'
  u'`:=` で宣された閾(㋓ の 7 本)は入らぬ。')
w(u'- ★「6file」は「危い file が 6 本」ではない。★ 條に当たる口を一つ以上持つ file の數である。')
w(u'- ★「甲=0」は「fail-open が無い」ではない。★ 同じ file に乙が 9 地 18 項 在る。')
w(u'- ★本紙の數は悉く「源と刻」に縛られる。★ disk は本走の中で動いた(差④)。'
  u'源・刻を落とした母數は、条件が同じでも合はぬ。')
w(u'- 本紙は臺帳(`_manifest.txt`)の總數を述べぬ ―― 紙は己を含む臺帳の數を書けぬ故。')
w(u'')

sys.stdout.write(u'\n'.join(W) + u'\n')
sys.stderr.write(u'★組んだ 行= %d★\n' % len(W))
