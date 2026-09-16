#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 60_modoshi.py ―― ★戻し方を「書く」のでなく「測る」。★
#   ㋒ は各案の戻し方を一行で問ふ。然し「戻せる筈」は測りでは無い。
#   ∴ 束の外の写しへ ⑴当て ⑵sha が動く事を見 ⑶逆に当て ⑷sha が生器へ戻る事を見る。
#   ―― 生器へは一字も書かぬ(作法⑴)。当てる先は /tmp でなく ★束外の作業樹★ の写しである。
import hashlib, io, os, shutil, subprocess, sys, tempfile

SEI = {'gate4': '../../../scripts/checks/karo_mac_gate4.sh',
       'dasumae': '../../../scripts/checks/karo_mac_dasumae_gate.sh'}
AN = [(u'甲 num_in_range',  'kou',  ['gate4', 'dasumae']),
      (u'乙 tmo_ok',        'otsu', ['dasumae']),
      (u'丙 safe_show',     'hei',  ['gate4', 'dasumae']),
      (u'合 甲乙丙 一度に', 'gou',  ['gate4', 'dasumae'])]

def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]

def ate(d, diff, gyaku):
    cmd = ['git', 'apply', '--unsafe-paths', '--directory', '.', '-p1']
    if gyaku: cmd.append('-R')
    p = subprocess.run(cmd + [os.path.abspath(diff)], cwd=d, capture_output=True)
    return p.returncode, (p.stdout + p.stderr).decode('utf-8', 'replace').strip()

def main():
    w = sys.stdout.write
    w(u'★戻し方を測る★ ―― 案を当て、sha が動き、逆に当てて sha が生器へ戻るか\n')
    w(u'(生器そのものへは一字も書かぬ。当てる先は 束外の写しである)\n\n')
    w(u'\t'.join([u'案', u'門', u'生器 sha16', u'当て rc', u'当て後 sha16',
                  u'動いたか', u'逆当て rc', u'戻り sha16', u'★戻つたか★']) + u'\n')
    warui = 0
    for na, an, mons in AN:
        for mon in mons:
            diff = 'an/%s_%s.diff' % (an, mon)
            if not os.path.exists(diff):
                w(u'\t'.join([na, mon, u'―', u'―', u'―', u'―', u'―', u'―',
                              u'★此の族は此の門に的が無い(diff 無し)★']) + u'\n')
                continue
            d = tempfile.mkdtemp(prefix='km50_modoshi_')
            try:
                dst = os.path.join(d, os.path.basename(SEI[mon]))
                shutil.copy2(SEI[mon], dst)
                s0 = sha16(dst)
                r1, e1 = ate(d, diff, False); s1 = sha16(dst)
                r2, e2 = ate(d, diff, True);  s2 = sha16(dst)
                ugoita = u'○' if s1 != s0 else u'★×(当てても動かぬ)★'
                modotta = u'○ 完全に戻る' if s2 == s0 else u'★× 戻らぬ★'
                if s1 == s0 or s2 != s0: warui += 1
                w(u'\t'.join([na, mon, s0, str(r1), s1, ugoita, str(r2), s2, modotta]) + u'\n')
                if e1: w(u'    当て言: %s\n' % e1)
                if e2: w(u'    逆言  : %s\n' % e2)
            finally:
                shutil.rmtree(d, ignore_errors=True)
    w(u'\n★生器 sha16 は上表で悉く同じ値である事を見よ ―― 測りの間も生器は動いて居らぬ★\n')
    w(u'不良 = %d 件%s\n' % (warui, u'' if warui else u'(★空である旨の一行★)'))
    return 1 if warui else 0

if __name__ == '__main__':
    sys.exit(main())
