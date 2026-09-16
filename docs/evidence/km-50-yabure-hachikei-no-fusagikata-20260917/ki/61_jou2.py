#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 61_jou2.py ―― ★出す前門 條②(末尾空白)の落ちを「言ひ訳」でなく「測り」にする。★
#   門は 10 本を名指して落ちた。之を「書式の都合」と ★書いて済ませぬ★。
#   ⑴ an/*.diff 7本 ―― 末尾空白を削つた写しが ★当たるか・戻るか★ を 60 と同じ機構で測る。
#      削つても当たるなら「書式の都合」は偽であり、當席が削るべきである。
#   ⑵ .nama/hyou51_…㋐12_kegare.*.txt 3本 ―― 其の末尾空白が
#      ★汚れ fixture 自身の内容★ に由来する事を、fixture と突き合せて示す。
#      由来するなら、削る事は ★陽性対照の實体を消す★ 事に等しい。
#   生器へは一字も書かぬ(作法⑴)。当てる先は束外の写し。
import hashlib, io, os, shutil, subprocess, sys, tempfile

SEI = {'gate4': '../../../scripts/checks/karo_mac_gate4.sh',
       'dasumae': '../../../scripts/checks/karo_mac_dasumae_gate.sh'}
DIFF = ['kou_gate4', 'kou_dasumae', 'otsu_dasumae', 'hei_gate4',
        'hei_dasumae', 'gou_gate4', 'gou_dasumae']
HYOU = ['.nama/hyou51_gate4_GATE4_MAX_FILE_MB_㋐12_kegare.gou.txt',
        '.nama/hyou51_gate4_GATE4_MAX_FILE_MB_㋐12_kegare.sei.txt',
        '.nama/hyou51_gate4_GATE4_MAX_FILE_MB_㋐12_kegare.tan.txt']
KEGARE = os.path.expanduser('~/.km50_kari_ki/02_kegare.txt')


def sha16(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]


def ate(d, diff, gyaku):
    cmd = ['git', 'apply', '--unsafe-paths', '--directory', '.', '-p1']
    if gyaku:
        cmd.append('-R')
    p = subprocess.run(cmd + [os.path.abspath(diff)], cwd=d, capture_output=True)
    return p.returncode, (p.stdout + p.stderr).decode('utf-8', 'replace').strip()


def kezuru(src, dst):
    u"""條② に従ふ ―― 各行の末尾空白を削る。削つた行数を返す。"""
    t = io.open(src, encoding='utf-8').read()
    ls = t.split(u'\n')
    n = sum(1 for l in ls if l != l.rstrip())
    io.open(dst, 'w', encoding='utf-8').write(u'\n'.join(l.rstrip() for l in ls))
    return n


def main():
    w = sys.stdout.write
    warui = 0
    w(u'★① an/*.diff ―― 末尾空白を削つたら 当たるか・戻るか★\n')
    w(u'\t'.join([u'案', u'門', u'削つた行', u'生 当て rc', u'生 戻り',
                  u'削 当て rc', u'削 戻り', u'★條②に従へるか★']) + u'\n')
    for na in DIFF:
        an, mon = na.split('_', 1)
        diff = 'an/%s.diff' % na
        d = tempfile.mkdtemp(prefix='km50_jou2_')
        try:
            kezu = os.path.join(d, 'kezutta.diff')
            n = kezuru(diff, kezu)
            res = []
            for which in (diff, kezu):
                e = tempfile.mkdtemp(prefix='km50_jou2w_')
                try:
                    dst = os.path.join(e, os.path.basename(SEI[mon]))
                    shutil.copy2(SEI[mon], dst)
                    s0 = sha16(dst)
                    r1, _ = ate(e, which, False)
                    s1 = sha16(dst)
                    r2, _ = ate(e, which, True)
                    s2 = sha16(dst)
                    res.append((r1, u'○' if (s1 != s0 and s2 == s0 and r2 == 0)
                                else u'★×★'))
                finally:
                    shutil.rmtree(e, ignore_errors=True)
            (r_sei, m_sei), (r_kez, m_kez) = res
            ok = (r_kez == 0 and m_kez == u'○')
            if n == 0:
                # ★「削る行が零」と「削れば通る」を一つに数へるな★
                hantei = u'★既に條②を満たす(末尾空白 0 行)★'
            elif ok:
                warui += 1
                hantei = u'★従へる ―― 當席が削るべきである★'
            else:
                hantei = u'★従へぬ ―― 削ると当たらぬ(rc=%d)★' % r_kez
            w(u'\t'.join([an, mon, str(n), str(r_sei), m_sei,
                          str(r_kez), m_kez, hantei]) + u'\n')
        finally:
            shutil.rmtree(d, ignore_errors=True)

    w(u'\n★② 門票3本の末尾空白の ★出所★ ―― 汚れ fixture と突き合せる★\n')
    if not os.path.isfile(KEGARE):
        w(u'★測れぬ ―― 汚れ fixture %s が無い★\n' % KEGARE)
        warui += 1
    else:
        moto = io.open(KEGARE, encoding='utf-8').read().split(u'\n')[0]
        w(u'汚れ fixture 第一行 逐語 = %r (末尾空白=%s)\n'
          % (moto, u'有' if moto != moto.rstrip() else u'無'))
        w(u'\t'.join([u'門票', u'疵の行', u'逐語', u'fixture 由来か']) + u'\n')
        for h in HYOU:
            if not os.path.isfile(h):
                w(u'%s\t★実体無★\n' % h); warui += 1; continue
            hit = 0
            for i, l in enumerate(io.open(h, encoding='utf-8').read().split(u'\n'), 1):
                if l != l.rstrip():
                    hit += 1
                    yurai = (moto in l)
                    if not yurai:
                        warui += 1
                    w(u'\t'.join([os.path.basename(h), str(i), repr(l),
                                  u'★由来する★' if yurai
                                  else u'★由来せぬ ―― 當席の疵★']) + u'\n')
            if hit == 0:
                w(u'%s\t―\t―\t★末尾空白が無い★\n' % os.path.basename(h))
    w(u'\n當席が削るべき件 = %d 件%s\n'
      % (warui, u'' if warui else u'(★空である旨の一行★)'))
    return 1 if warui else 0


if __name__ == '__main__':
    sys.exit(main())
