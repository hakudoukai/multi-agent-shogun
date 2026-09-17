#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""幹 363d5fb06084 の ★secret 0★ を検算する(読取のみ)。裁 seq326093 ①。
母數は★二つ★:
  甲 = 幹の tree に在る file 悉く(PR が世に出す物の全体)
  乙 = origin/main...幹 の patch の ★足した行★のみ(PR が足す物)
★零には四つの札★: ⑴陽性対照 ⑵根と深さ ⑶rc ⑷刻。値は一字も刷らぬ(masked)。
"""
import re, subprocess, sys, os, datetime

MIKI = '363d5fb06084'
MAIN = '4be3ee19e1c5'
ROOT = subprocess.run(['git','rev-parse','--show-toplevel'],capture_output=True,text=True).stdout.strip()

# 名(鍵の名)と 値(鍵の形) を分けて持つ。名だけなら宣言・値が付けば漏れ。
PAT = [
 ('sk_ant',      re.compile(rb'sk-ant-[A-Za-z0-9_\-]{20,}')),
 ('jwt',         re.compile(rb'eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}')),
 ('gh_pat',      re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}')),
 ('aws_akid',    re.compile(rb'AKIA[0-9A-Z]{16}')),
 ('slack',       re.compile(rb'xox[baprs]-[A-Za-z0-9-]{10,}')),
 ('pem',         re.compile(rb'[-]{5}BEGIN [A-Z ]*PRIVATE KEY[-]{5}')),
 ('ssh_priv',    re.compile(rb'[-]{5}BEGIN OPENSSH PRIVATE KEY[-]{5}')),
 ('kv_assign',   re.compile(rb'(?i)(service_role_key|api_key|apikey|secret|password|passwd|token)\s*[=:]\s*["\']?[A-Za-z0-9_\-/+=]{20,}')),
]

def scan(name, data):
    """(札名, 行, 伏せた抜粋) の列を返す。★値は刷らぬ★。"""
    out = []
    for i, line in enumerate(data.split(b'\n'), 1):
        if len(line) > 4000:            # 長行は二次曲線を避け、頭尾のみ見る
            line = line[:2000] + line[-2000:]
        for tag, rx in PAT:
            m = rx.search(line)
            if m:
                out.append((tag, name, i, '<伏:%d字>' % len(m.group(0))))
    return out

def g(*a):
    p = subprocess.run(['git'] + list(a), capture_output=True)
    return p.returncode, p.stdout

def kaki(path, lines):
    body = '\n'.join(l.replace('\r','').rstrip() for l in lines)
    open(path, 'w', encoding='utf-8').write(body + '\n')

def main():
    koku = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    rep = ['刻=%s' % koku, '根=%s' % ROOT, '幹=%s  基=%s' % (MIKI, MAIN), '']

    # ⑴陽性対照 ―― 検出子が★実際に鳴る★事を、同じ路で示す
    ctrl = b'x\nAKIA' + b'A'*16 + b'\napi_key = "' + b'Z'*32 + b'"\n'
    ch = scan('<陽性対照>', ctrl)
    rep.append('⑴陽性対照 = %d 件 (%s) %s' % (len(ch), '・'.join(sorted({c[0] for c in ch})),
                                              '★鳴つた★' if len(ch) >= 2 else '★鳴らぬ=検出子が死んで居る★'))
    if len(ch) < 2:
        rep.append('★止★ 陰性対照(0件)を名乗る資格が無い')
        kaki(os.path.join(os.path.dirname(__file__), '..', 'raw', '10_secret.txt'), rep)
        return 3

    # ⑵根と深さ ―― 甲: 幹の tree 全 file
    rc1, ls = g('ls-tree','-r','-z','--name-only',MIKI)
    names = [n for n in ls.decode('utf-8','surrogateescape').split('\0') if n]
    rep.append('⑵-甲 幹 tree の file = %d 本 (ls-tree rc=%d)' % (len(names), rc1))
    hits_a, yomenu, hijou = [], 0, 0
    for n in names:
        rc, blob = g('cat-file','-p','%s:%s' % (MIKI, n))
        if rc != 0:
            yomenu += 1; continue
        if b'\0' in blob[:8000]:
            hijou += 1; continue          # 2進 file は行で測れぬ ―― 数へて宣する
        hits_a += scan(n, blob)
    rep.append('     読めぬ %d 本 / 2進 %d 本 / 測つた %d 本' % (yomenu, hijou, len(names)-yomenu-hijou))

    # ⑵-乙: origin/main...幹 の ★足した行★のみ
    rc2, pat = g('diff','--unified=0','%s...%s' % (MAIN, MIKI))
    added = b'\n'.join(l[1:] for l in pat.split(b'\n') if l.startswith(b'+') and not l.startswith(b'+++'))
    rc3, fl = g('diff','--name-only','%s...%s' % (MAIN, MIKI))
    nfile = len([x for x in fl.decode('utf-8','surrogateescape').split('\n') if x])
    rep.append('⑵-乙 patch 足した行 = %d 行 / 触れた file = %d 本 (diff rc=%d/%d)' % (len(added.split(b'\n')), nfile, rc2, rc3))
    hits_b = scan('<patch:足した行>', added)

    rep.append('')
    rep.append('⑶rc = ls-tree %d / diff %d %d / cat-file 落ち %d' % (rc1, rc2, rc3, yomenu))
    rep.append('★甲(tree 全体) の当り = %d 件★' % len(hits_a))
    rep.append('★乙(足した行)   の当り = %d 件★' % len(hits_b))
    for tag, nm, ln, msk in hits_a + hits_b:
        rep.append('   %s  %s:%d  %s' % (tag, nm, ln, msk))
    rep.append('')
    rep.append('⑷刻 = %s ―― 此の数は★此の刻の 363d5fb06084 の中身★の函数である' % koku)
    rep.append('★數が意味せぬ事★: 之は「secret が repo の歴史に無い」の証に非ず。')
    rep.append('  測つたのは幹の tree(甲)と幹が足した行(乙)のみ。origin/main に既に在る物は母數の外。')
    kaki(os.path.join(ROOT, 'docs/evidence/karo-mac-miki-push-negai-20260917/raw/10_secret.txt'), rep)
    print('\n'.join(rep))
    return 0 if not (hits_a or hits_b) else 1

sys.exit(main())
