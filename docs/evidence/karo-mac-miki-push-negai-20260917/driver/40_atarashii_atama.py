#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""裁 seq326145 ―― ★紙を commit の中へ入れた後の頭★で secret 0 を固定検証する。
使ひ方:
    40_atarashii_atama.py <頭の ref か sha>   ―― 其の頭で測る(軍師mac の再現用)
    40_atarashii_atama.py --mae               ―― ★据ゑる前★= 幹363d5fb0 の足す行 ∪ 束の全byte
何を測るか(母數を二つに割る):
    乙 = origin/main...<頭> で ★足した行だけ★(PR の可否を決めるのは此方のみ)
    束 = 此の束の file の全byte(据ゑれば悉く「足す行」に成る故)
零の四札: ⑴陽性対照 ⑵根と深さ ⑶rc ⑷刻 を悉く刷る。値は一字も刷らぬ(伏字のみ)。
"""
import hashlib, os, re, subprocess, sys, time

MAIN = 'origin/main'
PAT = [
    ('sk_ant',   rb'sk-ant-[A-Za-z0-9_\-]{20,}'),
    ('jwt',      rb'eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}'),
    ('gh_pat',   rb'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}'),
    ('aws_akid', rb'AKIA[0-9A-Z]{16}'),
    ('slack',    rb'xox[baprs]-[A-Za-z0-9-]{10,}'),
    ('pem',      rb'[-]{5}BEGIN [A-Z ]*PRIVATE KEY[-]{5}'),
    ('ssh_priv', rb'[-]{5}BEGIN OPENSSH PRIVATE KEY[-]{5}'),
    ('kv_assign', rb'(?i)(service_role_key|api_key|apikey|secret|password|passwd|token)'
                  rb'\s*[=:]\s*["\']?[A-Za-z0-9_\-/+=]{20,}'),
]
RE = [(t, re.compile(p)) for t, p in PAT]
STRICT = {t for t, _ in PAT if t != 'kv_assign'}


def atari(buf, moto):
    """buf を測り、当りを (札, 出所, 伏字) で返す。★値は返さぬ★"""
    out = []
    for t, r in RE:
        for m in r.finditer(buf):
            out.append((t, moto, '<伏:%d字>' % len(m.group(0))))
    return out


def sh(*a):
    p = subprocess.run(list(a), capture_output=True)
    return p.returncode, p.stdout


def kaki(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(l.replace('\r', '').rstrip() for l in lines) + '\n')


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    mode = sys.argv[1]
    root = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                          capture_output=True, text=True).stdout.strip()
    束 = os.path.join(root, 'docs/evidence/karo-mac-miki-push-negai-20260917')
    L = []
    L.append('刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    L.append('根 = ' + root)
    L.append('走らせ方 = ' + mode)

    # ⑴陽性対照 ―― 測る路に乗せる(検出子が生きて居る事を先に示す)
    ctrl = b'x\nAKIA' + b'A' * 16 + b'\napi_key = "' + b'Z' * 32 + b'"\n'
    c = atari(ctrl, '対照')
    L.append('★陽性対照★ = %d件 鳴(期待2)  札=%s' % (len(c), ','.join(t for t, _, _ in c)))

    head = '363d5fb060845171338c067ef42bfcbef8ad9188' if mode == '--mae' else mode
    rc, sha = sh('git', 'rev-parse', '--verify', head + '^{commit}')
    if rc:
        L.append('★頭が引けぬ★ rc=%d' % rc)
        kaki(os.path.join(束, 'raw/40_atama.txt'), L)
        return 3
    head = sha.decode().strip()
    L.append('頭 = ' + head)
    L.append('基 = %s (%s)' % (subprocess.run(['git', 'rev-parse', MAIN],
             capture_output=True, text=True).stdout.strip(), MAIN))

    # 乙 ―― ★足した行だけ★
    rc, d = sh('git', 'diff', '-U0', MAIN + '...' + head)
    add = [l for l in d.split(b'\n') if l[:1] == b'+' and l[:3] != b'+++']
    rc2, nm = sh('git', 'diff', '--name-only', '-z', MAIN + '...' + head)
    files = [x for x in nm.split(b'\0') if x]
    otsu = []
    for i, l in enumerate(add):
        otsu += atari(l[1:], '乙:足した行 %d' % (i + 1))
    L.append('乙 母數 = 足した行 %d / 触れた file %d  (diff rc=%d / name-only rc=%d)'
             % (len(add), len(files), rc, rc2))
    L.append('★乙 当り = %d件★' % len(otsu))
    for t, m, f in otsu:
        L.append('   %s %s %s' % (t, m, f))

    # 束 ―― 据ゑれば悉く足す行に成る故、全byte を測る
    hon, yome, tsuka = 0, 0, 0
    taba = []
    for dp, dn, fn in os.walk(束):
        dn[:] = [d for d in dn if d != '__pycache__']
        for n in sorted(fn):
            p = os.path.join(dp, n)
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            hon += 1
            try:
                b = open(p, 'rb').read()
            except OSError:
                yome += 1
                continue
            tsuka += 1
            taba += atari(b, '束:' + os.path.relpath(p, 束))
    L.append('束 母數 = 本 %d / 読めぬ %d / 測つた %d' % (hon, yome, tsuka))
    L.append('★束 当り = %d件★' % len(taba))
    for t, m, f in taba:
        L.append('   %s %s %s' % (t, m, f))

    kei = otsu + taba
    gen = [x for x in kei if x[0] in STRICT]
    L.append('')
    L.append('★合 = %d件 (内 厳密形 %d件 / 緩形 %d件)★'
             % (len(kei), len(gen), len(kei) - len(gen)))
    L.append('註: 陽性対照は母數の外(検出子の生死を示す為だけに測る路へ乗せた)。')
    L.append('註: ★此の紙自身(raw/40_atama.txt)・MANIFEST.txt・門の控は本走の後に生れる★')
    L.append('    ∴ 束の母數の外に残る。其れは据ゑた後の頭を引数に渡して再走すれば悉く入る。')
    kaki(os.path.join(束, 'raw/40_atama.txt'), L)
    for l in L:
        print(l)
    return 0 if not kei else 1


sys.exit(main())
