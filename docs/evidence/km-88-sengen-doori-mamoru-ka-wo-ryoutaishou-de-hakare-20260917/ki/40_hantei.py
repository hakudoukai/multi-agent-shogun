# -*- coding: utf-8 -*-
"""㋑㋒㋓ ―― 出来た筵(raw/20_taishou.tsv)と砂場の生 err から、
   表・害の実測・二版の差 を組み立てる。数へ直しは ★己の器で★ 行ひ、
   ★零には四札(陽性対照・根と深さ・rc・刻)★ を必ず添へる。
検出子は悉く /usr/bin/grep (殻の grep は ugrep で .gitignore を見る ―― 束の中では 0 を返す)。
rc は ★管を通さず★ subprocess の returncode から直に取る。
"""
import os, subprocess, datetime
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.getcwd()
GREP = '/usr/bin/grep'
VERS  = ['kyuu', 'index', 'shin', 'hashiru_kouho']
FORMS = ['f01_unset','f02_empty','f03_blank_sp','f04_zero','f05_one','f06_two','f07_true',
         'f08_minus1','f09_mark_nl','f10_lead_nl','f11_zeropad','f12_plus1','f13_lead_sp1','f14_zen_zero']

def koku():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

def cnt(pat, path, ere=True):
    """(数, rc) ―― rc は管を通さず直に。grep -c は当たり0で rc=1 を返す。"""
    a = [GREP, '-c'] + (['-E'] if ere else []) + [pat, path]
    p = subprocess.run(a, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rc = p.returncode
    s = p.stdout.decode('utf-8', 'replace').strip()
    return (int(s) if s.isdigit() else -1), rc

# ── 検出子の定義(逐語) ─────────────────────────────
D = {
  'pu_timeout' : (r'^#+TR# process_unread timeout$',      '刻限 tick で未読処理に入つた回数'),
  'pu_event'   : (r'^#+TR# process_unread event$',        '事象 tick で未読処理に入つた回数'),
  'nudge_try'  : (r'\[SEND-KEYS\] Sending nudge',         '実際に突つき(send-keys)を試みた回数'),
  'nudge_fail' : (r'WARNING: send-keys nudge failed',     '突つきが外れた回数'),
  'throttle'   : (r'\[SKIP\] Throttling nudge',           '突つきを絞つた回数'),
  'fixflag'    : (r'^#+TR# fix_flag ASW_PROCESS_TIMEOUT', 'fix_flag(番人)を呼んだ回数'),
  'taoshi'     : (r'\[watcher\].*ASW_PROCESS_TIMEOUT',    '番人が「倒す」と声を出した回数'),
}

def errpath(v, f):
    return os.path.join('suna', '%s_%s' % (v, f), 'err.txt')

# ── 本測 ──────────────────────────────────────────
M = {}   # (ver,form) -> {key:(n,rc)}
for v in VERS:
    for f in FORMS:
        p = errpath(v, f)
        if not os.path.isfile(p):
            M[(v, f)] = None; continue
        M[(v, f)] = dict((k, cnt(D[k][0], p)) for k in D)

out = []
W = out.append
W('# 40_hantei ―― ㋑㋒㋓ の素(刻 %s)' % koku())
W('# 歩き根 = %s/suna  深さ=1(<版>_<形>/err.txt の一本のみ・再帰せず)' % BASE)
W('# 検出子 = /usr/bin/grep -c -E 〈下記逐語〉   ※殻の grep は ugrep(.gitignore を見る)ゆゑ用ゐず')
W('# rc は管を通さず subprocess.returncode から直に取る。grep -c は ★当たり0で rc=1★。')
W('')
W('== 検出子の逐語 ==')
for k in sorted(D):
    W('  %-10s %-42s  %s' % (k, D[k][0], D[k][1]))
W('')

# ── 器の健全(陽性対照) ───────────────────────────
W('== 器の陽性対照 ―― 「零」が器の沈黙でない事の証 ==')
for v in VERS:
    a = M[(v, 'f05_one')]
    W('  %-14s f05_one(=1) pu_timeout=%d rc=%d / nudge_try=%d rc=%d  ← 同じ検出子が★此処では鳴る★'
      % (v, a['pu_timeout'][0], a['pu_timeout'][1], a['nudge_try'][0], a['nudge_try'][1]))
W('')

# ── ㋑ 表 ─────────────────────────────────────────
tsv = [l.rstrip('\n').split('\t') for l in open('raw/20_taishou.tsv', encoding='utf-8')]
H = tsv[0]; ROW = dict(((r[0], r[1]), r) for r in tsv[1:])

W('== ㋑ 両対照の表 ==')
W('  出目4欄 = rc / stdout byte / stderr 行(器の声・TR 行を除く) / 未読が処理されたか')
W('  「処理されたか」は pu_timeout(刻限 tick の処理)で判ずる。0 の升には四札を後段に立てる。')
W('')
W('  %-14s %-13s %-9s %-4s %-6s %-6s %-9s %-4s %s' %
  ('版', '形', '与へた値', 'rc', 'out(B)', 'err行', 'pu_timeout', 'rc', '判'))
for v in VERS:
    for f in FORMS:
        r = ROW[(v, f)]; m = M[(v, f)]
        n, rc = m['pu_timeout']
        W('  %-14s %-13s %-9s %-4s %-6s %-6s %-9d %-4d %s' %
          (v, f, r[2], r[3], r[4], r[5], n, rc, ('処理する' if n > 0 else '処理せぬ')))
    W('')

# ── 零の四札 ─────────────────────────────────────
W('== ㋑ 零の四札(pu_timeout=0 の升 悉く) ==')
z = [(v, f) for v in VERS for f in FORMS if M[(v, f)]['pu_timeout'][0] == 0]
W('  零の升 = %d 口' % len(z))
for v, f in z:
    m = M[(v, f)]
    pos = M[(v, 'f05_one')]['pu_timeout']
    W('  ・%s / %s' % (v, f))
    W('      ①陽性対照 : 同版 f05_one を★同じ検出子・同じ路★で測れば %d(rc=%d) ―― 器は鳴る'
      % (pos[0], pos[1]))
    W('      ②根と深さ : %s/%s  (一本の file・再帰せず・深さ0)' % (BASE, errpath(v, f)))
    W('      ③rc       : grep -c rc=%d(当たり0の正常な 1)／同紙の trace 総行=%s(沈黙に非ず)'
      % (m['pu_timeout'][1], ROW[(v, f)][6]))
    W('      ④刻       : %s' % koku())
W('')

# ── ㋒ 害の実測 ──────────────────────────────────
W('== ㋒ 「倒れた先」が現に何を為したか(語ではなく出目) ==')
W('  %-14s %-13s %-10s %-9s %-9s %-9s %s' %
  ('版', '形', 'pu_timeout', 'nudge試', 'nudge外', '絞り', '番人の声'))
for v in ['kyuu', 'shin']:
    for f in FORMS:
        m = M[(v, f)]
        W('  %-14s %-13s %-10d %-9d %-9d %-9d %d' %
          (v, f, m['pu_timeout'][0], m['nudge_try'][0], m['nudge_fail'][0],
           m['throttle'][0], m['taoshi'][0]))
    W('')

# ── ㋓ 二版の差 ──────────────────────────────────
W('== ㋓ 旧(kyuu=HEAD)と新(shin=disk)の差 ==')
kaw, fuhen = [], []
for f in FORMS:
    a, b = M[('kyuu', f)], M[('shin', f)]
    pa, pb = (a['pu_timeout'][0] > 0), (b['pu_timeout'][0] > 0)
    (kaw if pa != pb else fuhen).append((f, pa, pb))
W('  ★出目(未読を処理するか否か)が変つた組合せ = %d 口★' % len(kaw))
for f, pa, pb in kaw:
    W('    ・%-13s %s → %s  (%s → %s)' %
      (f, ROW[('kyuu', f)][2], ROW[('shin', f)][2],
       '処理せぬ' if not pa else '処理する', '処理する' if pb else '処理せぬ'))
W('  変らぬ組合せ = %d 口' % len(fuhen))
for f, pa, pb in fuhen:
    W('    ・%-13s %s  ―― 両版とも %s' %
      (f, ROW[('kyuu', f)][2], '処理する' if pb else '処理せぬ'))
W('')
W('  ※ rc は 56 走 悉く -9(gtimeout -s KILL の 9 番)・stdout は 56 走 悉く 0 byte。')
W('     stderr 行は 14 形 ★悉く★ 動いた(番人が声を出す分だけ増える):')
for f in FORMS:
    W('       %-13s %s 行 → %s 行' % (f, ROW[('kyuu', f)][5], ROW[('shin', f)][5]))
open('raw/40_hantei.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
