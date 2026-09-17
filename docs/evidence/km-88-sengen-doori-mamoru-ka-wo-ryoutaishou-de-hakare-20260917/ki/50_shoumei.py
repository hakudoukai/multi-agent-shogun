# -*- coding: utf-8 -*-
"""紙(README.md)に書いた数を ★紙を書いた後で★ 器に問ひ直す(裁: 紙の命令は逐語で走らせよ)。
落ちた検めは ★落ちた儘★ 刷る ―― 直して黙るのが一番の疵ゆゑ。"""
import os, subprocess, hashlib, datetime
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = [l.rstrip('\n').split('\t') for l in open('raw/20_taishou.tsv', encoding='utf-8')]
H, rows = R[0], R[1:]
D = dict(((r[0], r[1]), r) for r in rows)
FORMS = sorted(set(r[1] for r in rows))
out=[]; W=out.append
ok=ng=0
def chk(name, got, want):
    global ok, ng
    g = (got == want)
    ok += g; ng += (not g)
    W('  [%s] %-56s 得=%s  期=%s' % ('合' if g else '★違★', name, got, want))

W('# 50_shoumei ―― 紙の数を器に問ひ直す(刻 %s)' % datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
W('')
W('== 紙の主張 ⇔ 筵の実 ==')
chk('走の総数(4版×14形)', len(rows), 56)
chk('rc は 56走 悉く -9', sorted(set(r[3] for r in rows)), ['-9'])
chk('stdout は 56走 悉く 0 byte', sorted(set(r[4] for r in rows)), ['0'])
proc = lambda v,f: int(D[(v,f)][7]) > 0
chk('陽性 shin f04_zero は処理せぬ', proc('shin','f04_zero'), False)
chk('陰性 shin f05_one は処理する', proc('shin','f05_one'), True)
chk('shin は f04 以外 13形 悉く処理する',
    sorted(f for f in FORMS if f!='f04_zero' and not proc('shin',f)), [])
chk('index の14形は kyuu と出目一致',
    [f for f in FORMS if proc('index',f)!=proc('kyuu',f)], [])
chk('hashiru_kouho の14形は kyuu と出目一致',
    [f for f in FORMS if proc('hashiru_kouho',f)!=proc('kyuu',f)], [])
chk('変つた組合せ = 10口',
    len([f for f in FORMS if proc('kyuu',f)!=proc('shin',f)]), 10)
chk('変らぬ組合せ = 4口',
    sorted(f for f in FORMS if proc('kyuu',f)==proc('shin',f)),
    ['f01_unset','f02_empty','f04_zero','f05_one'])
chk('stderr 行が二版で同じ形 = 0(14形 悉く動いた)',
    [f for f in FORMS if D[('kyuu',f)][5]==D[('shin',f)][5]], [])
chk('零の升 = 34口', len([r for r in rows if r[7]=='0']), 34)
chk('shin f04_zero の trace 総行', D[('shin','f04_zero')][6], '769')
chk('fix_flag を呼ぶ版は shin のみ',
    sorted(set(r[0] for r in rows if r[10]!='0')), ['shin'])

W('')
W('== 紙の逐語引用 ⇔ ki/shin.sh の実(行番も己で引き直す) ==')
S = open('ki/shin.sh', encoding='utf-8').read().split(chr(10))
def line(n): return S[n-1]
chk('L251 逐語', line(251), '# Optional safety toggles:')
chk('L252 逐語', line(252), '# - ASW_DISABLE_ESCALATION=1: disable phase2/phase3 escalation actions')
chk('L253 逐語(宣)', line(253),
    '# - ASW_PROCESS_TIMEOUT=0: do not process unread on timeout ticks (event-only)')
chk('L258 逐語(直し)', line(258), 'fix_flag ASW_PROCESS_TIMEOUT 1 ASW_PROCESS_TIMEOUT')
chk('L1633 逐語(比較器)', line(1633),
    '        if [ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; then')
chk('ASW_PROCESS_TIMEOUT の宣は L253 の一行のみ',
    [i+1 for i,l in enumerate(S) if l.startswith('# - ASW_PROCESS_TIMEOUT')], [253])
chk('ESCALATE 閾の行(L204)に PHASE1:120/PHASE2:240/COOLDOWN:300',
    all(x in line(204) for x in ('ESCALATE_PHASE1:120','ESCALATE_PHASE2:240','ESCALATE_COOLDOWN:300')),
    True)

W('')
W('== 走る器 ⇔ disk ⇔ .bak(㋔) ==')
def st(p):
    s = os.stat(p); return s.st_ino, s.st_size
gi, gb = st('/Users/momizimac/multi-agent-shogun/scripts/inbox_watcher.sh')
chk('生器 ino', gi, 22062559)
chk('生器 bytes', gb, 83319)
chk('走る器の ino(21:11 実測) ≠ 生器の ino', 20564860 != gi, True)
bak = ['/Users/momizimac/multi-agent-shogun/scripts/' + x
       for x in sorted(os.listdir('/Users/momizimac/multi-agent-shogun/scripts'))
       if x.startswith('inbox_watcher.sh.bak')]
W('  .bak 候補 = %d 本' % len(bak))
for b in bak:
    i, n = st(b)
    W('    %-58s ino=%-10d bytes=%d' % (os.path.basename(b), i, n))
chk('走る器の ino は .bak の何れとも合はぬ(∴同定は推)',
    20564860 in [st(b)[0] for b in bak], False)
# ★疵9★ 初版は「.bak は悉く 74274 B」と括つた ―― 実は 4本中 3本。控=raw/50_shoumei.txt.first
chk('74274 B の .bak = 3 本', sorted(st(b)[1] for b in bak), [74274, 74274, 74274, 76554])
_h = [(os.path.basename(b), hashlib.sha256(open(b,'rb').read()).hexdigest()[:16])
      for b in bak if st(b)[1] == 74274]
chk('其の 3 本は byte 同一(sha16 一種)', sorted(set(x[1] for x in _h)), ['09b661fe8ec2839b'])
chk('束の hashiru_kouho.sh は其の sha と合ふ',
    hashlib.sha256(open('ki/hashiru_kouho.sh','rb').read()).hexdigest()[:16], '09b661fe8ec2839b')

# 走る器は今も生きて居るか(止めて居らぬ事の證)
p = subprocess.run(['/bin/ps','-o','pid=,lstart=,command=','-p','9859'],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
W('')
W('== scope_out⑴ ―― 走る watcher を止めて居らぬ事(ps rc=%d) ==' % p.returncode)
W('  ' + (p.stdout.decode('utf-8','replace').strip() or '★得られず★'))

# 生器へ一字も書いて居らぬ事(scope_out⑵)
g = subprocess.run(['/usr/bin/git','-C','/Users/momizimac/multi-agent-shogun',
                    'diff','--stat','HEAD','--','scripts/'],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
W('')
W('== scope_out⑵ ―― scripts/ の HEAD 差(git rc=%d) ==' % g.returncode)
for l in g.stdout.decode('utf-8','replace').rstrip().split(chr(10)):
    W('  ' + l)
W('  ※ 上の差は ★本弾の前から在つた家老の直し★。mtime=2026-09-17T10:25:19 は下命(12:03)より前。')
W('     本席は 12:11 以降 scripts/ へ一字も書いて居らぬ。')

W('')
W('== 結 ==')
W('  合=%d / ★違★=%d' % (ok, ng))
open('raw/50_shoumei.txt','w',encoding='utf-8').write(chr(10).join(out)+chr(10))
print(chr(10).join(out))
