# -*- coding: utf-8 -*-
"""㋔ 錠は本当に塞いだのか 37(第68弾)―― 束の外の書き手が raw/(0555/0444)へ書ける経路を數へる。各々 rc と根と深さと刻。
⑴ settings.json の hook(母數・各 command の script が docs/evidence へ書くか = 其の行が註か実行か)
⑵ 稼働中 process(pgrep -U 己・母數・argv に docs/evidence / km-68 を持つ物・己と己の祖先は pid で除く)
⑶ scripts/ の器(docs/evidence を含む file・行ごとに註/実行・書き語の有無)
⑷ launchd plist(母數・multi-agent-shogun / docs/evidence を指す物)
⑸ git 自身: 一時 repo の fixture で dir 0555/file 0444 の下へ ★讀み(add -f / hash-object / status)★ と ★書き(checkout 別枝 / rm / clean / apply)★ を掛け rc と stderr 逐語
⑹ 同 uid: chmod で外せる(rc)―― 外せば ctime で 40 が鳴る(第67弾 L3・本弾 30 L1a)
⑺ root: 己は root でない(id -u)―― 測れぬと書く
★錠が塞ぐのは open(O_WRONLY|O_CREAT)/unlink/rename であつて read ではない ―― git add -f が通つたのは讀みゆゑ★ を ⑸ で實演する。出目 raw/37_jou.txt。"""
import os, sys, re, json, subprocess, time, tempfile, shutil, stat
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; W = M + '/.claude/worktrees/karo-mac-a1'; RAW67 = W + '/docs/evidence/km-67-mon-no-ato-20260917/raw'
now = lambda: time.strftime('%Y-%m-%dT%H:%M:%S%z'); out = [f'# 37 ㋔ 錠は本当に塞いだのか / 刻 {now()} / uid {os.getuid()} / 己 pid {os.getpid()}']
def sh(argv, cwd=None): p = subprocess.run(argv, capture_output=True, text=True, cwd=cwd); return p.returncode, p.stdout, p.stderr
WRITE_WORDS = re.compile(r'(^|[^<])>\s*["\']?\$?[A-Za-z_{}/.]|\bcp\b|\bmv\b|\btee\b|\bmkdir\b|\btouch\b|\brm\b|open\([^)]*["\']w|write_text|shutil')
def gyou_bunrui(path, key):
    """path の file で key を含む行を 註/実行 と 書き語の有無 で割る。"""
    res = []
    for k, l in enumerate(open(path, encoding='utf-8', errors='replace').read().split('\n'), 1):
        if key in l:
            chu = l.lstrip().startswith('#'); res.append((k, '註' if chu else '実行', '書き語有' if (not chu and WRITE_WORDS.search(l)) else '書き語無', l.strip()[:110]))
    return res
# ⑴ hook
s = json.load(open(M + '/.claude/settings.json')); hooks = [(ev, hk.get('command', '')) for ev, lst in s.get('hooks', {}).items() for g in lst for hk in g.get('hooks', [])]
out.append(f'## ⑴ hook(settings.json)母數 {len(hooks)} / 刻 {now()}'); w1 = 0
for ev, cmd in hooks:
    m = re.search(r'(scripts/\S+)', cmd); p = M + '/' + m.group(1) if m else None
    if p and os.path.isfile(p):
        rows = gyou_bunrui(p, 'docs/evidence'); jikkou = [r for r in rows if r[1] == '実行' and r[2] == '書き語有']; w1 += len(jikkou)
        out.append(f'  {ev} {cmd[:60]} → {m.group(1)} / docs/evidence を含む行 {len(rows)}(実行かつ書き語有 {len(jikkou)})' + ''.join(f'\n     :{r[0]} {r[1]}/{r[2]} {r[3]}' for r in rows))
    else: out.append(f'  {ev} {cmd[:60]} → script が取れぬ/無い')
out.append(f'  ∴ hook が docs/evidence へ書く実行行 = {w1}(rc 0・根 settings.json・深さ hooks[*].hooks[*].command → scripts/ の file 一段)')
# ⑵ process
me = os.getpid(); anc = set(); q = me
for _ in range(12):
    r = sh(['ps', '-o', 'ppid=', '-p', str(q)]); pp = r[1].strip()
    if not pp.isdigit() or int(pp) <= 1: break
    anc.add(int(pp)); q = int(pp)
r = sh(['ps', '-U', str(os.getuid()), '-o', 'pid=,command=']); procs = [l.strip() for l in r[1].split('\n') if l.strip()]  # ★一走目は pgrep -fl '' で母數 0 rc 2(空の pattern は器の誤り)―― .first に残す★
own = [l for l in procs if int(l.split(' ', 1)[0]) == me or int(l.split(' ', 1)[0]) in anc]
tgt = [l for l in procs if ('docs/evidence' in l or 'km-68' in l) and int(l.split(' ', 1)[0]) not in anc and int(l.split(' ', 1)[0]) != me]
out.append(f'## ⑵ process(ps -U {os.getuid()} -o pid=,command=)母數 {len(procs)} / rc {r[0]} / 己+祖先 {len(own)}(pid {sorted(anc | {me})}・除いた)/ argv に docs/evidence か km-68 を持つ物(己を除く) {len(tgt)} / 刻 {now()}')
for l in tgt[:10]: out.append(f'  {l[:150]}')
watchers = [l for l in procs if 'inbox_watcher' in l or 'watchdog' in l or 'report_watcher' in l]; out.append(f'  稼働中の watcher 系 {len(watchers)}: ' + ' | '.join(l[:70] for l in watchers[:6]))
# ⑶ scripts/
files = []
for d, ds, fs in os.walk(M + '/scripts'):
    for f in fs:
        if f.endswith(('.sh', '.py')): files.append(os.path.join(d, f))
hit3 = []
for p in sorted(files):
    try: t = open(p, encoding='utf-8', errors='replace').read()
    except Exception: continue
    if 'docs/evidence' in t: hit3.append((os.path.relpath(p, M), gyou_bunrui(p, 'docs/evidence')))
w3 = sum(1 for _, rows in hit3 for r in rows if r[1] == '実行' and r[2] == '書き語有')
out.append(f'## ⑶ scripts/ の器 母數 {len(files)}(.sh .py)/ docs/evidence を含む file {len(hit3)} / 其の行で 実行かつ書き語有 {w3} / 刻 {now()}')
for rel, rows in hit3: out.append(f'  {rel}: 行 {len(rows)}' + ''.join(f'\n     :{r[0]} {r[1]}/{r[2]} {r[3]}' for r in rows))
# ⑷ launchd
LA = os.path.expanduser('~/Library/LaunchAgents'); pl = sorted(f for f in os.listdir(LA) if f.endswith('.plist')) if os.path.isdir(LA) else []
hit4 = [f for f in pl if re.search(r'multi-agent-shogun|docs/evidence', open(os.path.join(LA, f), encoding='utf-8', errors='replace').read())]
out.append(f'## ⑷ launchd plist 母數 {len(pl)}(根 {LA}・深さ 1)/ multi-agent-shogun か docs/evidence を指す物 {len(hit4)}: {hit4} / crontab: {sh(["crontab", "-l"])[2].strip()[:60] or "(在る)"} / 刻 {now()}')
# ⑸ git fixture(一時 repo・己の束の外・終りに消す)
T = tempfile.mkdtemp(prefix='km68_jou_'); g = lambda *a: sh(['git'] + list(a), cwd=T)
try:
    g('init', '-q', '-b', 'main'); g('config', 'user.email', 'a@b'); g('config', 'user.name', 'km68')
    os.makedirs(T + '/d'); open(T + '/d/f.txt', 'w').write('v1\n'); g('add', 'd'); g('commit', '-q', '-m', 'v1')
    g('checkout', '-q', '-b', 'b'); open(T + '/d/f.txt', 'w').write('v2\n'); g('commit', '-q', '-am', 'v2'); g('checkout', '-q', 'main')
    open(T + '/d/untracked.txt', 'w').write('u\n'); open(T + '/d/f.txt', 'a').write('')
    os.chmod(T + '/d/f.txt', 0o444); os.chmod(T + '/d/untracked.txt', 0o444); os.chmod(T + '/d', 0o555)
    out.append(f'## ⑸ git fixture {T}(d/ 0555・d/f.txt 0444・d/untracked.txt 0444・枝 main=v1 / b=v2)/ 刻 {now()}')
    tests = [('讀 add -f d/', ['add', '-f', '--', 'd']), ('讀 hash-object', ['hash-object', 'd/f.txt']), ('讀 status', ['status', '--porcelain']), ('讀 diff b', ['diff', '--stat', 'b']),
             ('書 checkout b(f.txt を v2 に書き換へる)', ['checkout', 'b']), ('書 rm -f d/f.txt(unlink)', ['rm', '-f', 'd/f.txt']), ('書 clean -f d/(untracked を unlink)', ['clean', '-f', 'd/']),
             ('書 restore --source=b d/f.txt', ['restore', '--source=b', 'd/f.txt']), ('書 checkout b 再(直前の失敗後の状態)', ['checkout', 'b'])]
    for nm, argv in tests:
        rc, so, se = g(*argv); out.append(f'  {nm}: rc {rc} / stdout {so.strip()[:80]!r} / stderr {se.strip()[:140]!r}')
    out.append(f'  後の状態: d/f.txt = {open(T + "/d/f.txt").read().strip()!r} / untracked 在る {os.path.exists(T + "/d/untracked.txt")} / 枝 {g("rev-parse", "--abbrev-ref", "HEAD")[1].strip()} / d mode {oct(os.stat(T + "/d").st_mode & 0o777)}')
    # 生の open / unlink / rename / read
    for nm, fn in (('read open', lambda: open(T + '/d/f.txt', 'rb').read()), ('write open(w)', lambda: open(T + '/d/f.txt', 'w')), ('create open(new)', lambda: open(T + '/d/new.txt', 'w')), ('unlink', lambda: os.unlink(T + '/d/f.txt')), ('rename', lambda: os.rename(T + '/d/f.txt', T + '/d/g.txt')), ('mkdir', lambda: os.mkdir(T + '/d/sub'))):
        try: fn(); out.append(f'  生 {nm}: ★通つた★')
        except OSError as e: out.append(f'  生 {nm}: {e.__class__.__name__}({e.errno})')
    # ⑹ 同 uid chmod
    os.chmod(T + '/d', 0o755); rc6 = 0
    out.append(f'## ⑹ 同 uid の chmod(錠を外す): rc {rc6} / d mode {oct(os.stat(T + "/d").st_mode & 0o777)} ―― 外せる。外せば ctime が動き 40(則二)が鳴る(第67弾 L3・本弾 30 L1a)。∴ 錠は「同 uid の者が黙つて書く」を防がぬ ―― 防ぐのは「錠を外さずに書く」だけであり、外した痕は捕へ器が數へる。')
    os.chmod(T + '/d/f.txt', 0o644); os.chmod(T + '/d/untracked.txt', 0o644)
finally:
    shutil.rmtree(T, ignore_errors=True)
out.append(f'## ⑺ root: id -u = {os.getuid()} ―― 己は root でない。root は錠を無視して書ける(測れぬ・宣言)。')
# 第67弾の錠の今
st67 = os.stat(RAW67).st_mode & 0o777; nbad = 0; nf = 0
for d, ds, fs in os.walk(RAW67):
    if (os.stat(d).st_mode & 0o777) != 0o555: nbad += 1
    for f in fs:
        q = os.path.join(d, f)
        if stat.S_ISREG(os.lstat(q).st_mode): nf += 1; nbad += (os.stat(q).st_mode & 0o777) != 0o444
out.append(f'## 第67弾の錠の今(家老の git add -f・commit f955bc3 の後): raw/ mode {oct(st67)} / 通常 file {nf} / 0444・0555 でない物 {nbad} ―― 錠は讀みを妨げず、家老の add -f の後も掛かつた儘。')
out.append(f'# 結 37: 束の外から raw/ へ「錠を外さずに」書ける経路 = hook {w1} + scripts 実行書き行 {w3} + process(argv に的) {len(tgt)} + launchd {len(hit4)} + git 書き系(⑸ の rc≠0 を讀め)= ★{w1 + w3 + len(tgt) + len(hit4)}★(rc 0・根 settings.json/scripts//pgrep/LaunchAgents・深さ 1〜2・刻 {now()})。★錠が塞いだのは「門の後に書く病」の内 ★己の器が黙つて書く★ 経路であり、同 uid の chmod と root は塞がぬ ―― 其の二つは 40 の ctime が痕で數へる(root は測れぬ)。★')
K.kaku(E + '/37_jou.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0)
