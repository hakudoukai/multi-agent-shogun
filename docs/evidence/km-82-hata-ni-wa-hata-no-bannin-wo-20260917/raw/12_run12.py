# -*- coding: utf-8 -*-
# 十二形の毒を 両器形(現形/直し形)へ当てる ―― 写し器=/bin/bash。★稼働中の器は触らぬ★。
# 欄を分ける: ★器の報せ行(^[watcher])★ と ★外の声行(bash 自身の悲鳴)★ は別物である。
import subprocess, os, sys, re
SH = '/bin/bash'
FORMS = [
    ('①未設定',        None),
    ('②空文字',        ''),
    ('③空白半',        ' '),
    ('④空白全',        '　'),
    ('⑤非数',          'abc'),
    ('⑥20桁',          '9' * 20),
    ('⑦域外2',         '2'),
    ('⑧域外01',        '01'),
    ('⑨域外+1',        '+1'),
    ('⑩先頭改行',      '\n1'),
    ('⑪正常1(宣)',     '1'),
    ('⑫正常0(宣)',     '0'),
]
def harness(form):
    g = lambda n: open('raw/slice_%s_%s.sh' % (form, n), encoding='utf-8').read()
    return ('#!/bin/bash\n' + g('bannin') + '\n' + g('uke')
            + '\nprocess_unread(){ printf \'BRANCH=%s\\n\' "$1"; }\nrc=2\n'
            + g('hikaku')
            + '\nprintf \'FINAL=[%s]\\n\' "${ASW_PROCESS_TIMEOUT-★未設定★}"\n')
def vis(v):
    if v is None: return '(未設定)'
    if v == '': return '(空文字)'
    return v.replace('\n', '␊').replace('\r', '␍').replace('\t', '␉').replace('　', '␠全')
rows = []
for form in ('genkei', 'naoshi'):
    src = harness(form)
    open('raw/13_harness_%s.sh' % form, 'w', encoding='utf-8').write(src)
    for name, val in FORMS:
        env = dict(os.environ)
        env.pop('ASW_PROCESS_TIMEOUT', None)
        if val is not None:
            env['ASW_PROCESS_TIMEOUT'] = val
        p = subprocess.run([SH, 'raw/13_harness_%s.sh' % form], capture_output=True, text=True, env=env)
        out, err = p.stdout, p.stderr
        shirase = [l for l in err.splitlines() if l.startswith('[watcher]')]
        hoka    = [l for l in err.splitlines() if l and not l.startswith('[watcher]')]
        br = [l.split('=', 1)[1] for l in out.splitlines() if l.startswith('BRANCH=')]
        fin = [l.split('=', 1)[1] for l in out.splitlines() if l.startswith('FINAL=')]
        rows.append((form, name, vis(val), p.returncode,
                     (br[0] if br else '★無★'), len(shirase), len(hoka),
                     (fin[0] if fin else '★無★'),
                     (shirase[0][:60] if shirase else '')))
hdr = ['器形', '形', '値(可視印)', 'rc', 'BRANCH', '器の報せ行', '外の声行', 'FINAL', '報せの頭60字']
w = open('raw/20_doku12.tsv', 'w', encoding='utf-8')
w.write('\t'.join(hdr) + '\n')
for r in rows:
    w.write('\t'.join(str(x) for x in r) + '\n')
w.close()
print('\t'.join(hdr))
for r in rows:
    print('\t'.join(str(x) for x in r))
# 要約 ―― ★沈黙の縮退★ の数を両形で数へる
def cnt(form, pred): return sum(1 for r in rows if r[0] == form and pred(r))
sil = lambda r: r[4] == '★無★' and r[5] == 0            # 枝を踏まず・報せ0 = 黙つて縮退
print('\n★要約★')
for form in ('genkei', 'naoshi'):
    print('%s: 母數12 / 黙つて縮退=%d / 報せ有=%d / 外の声有=%d / rc非0=%d'
          % (form, cnt(form, sil), cnt(form, lambda r: r[5] > 0),
             cnt(form, lambda r: r[6] > 0), cnt(form, lambda r: r[3] != 0)))
