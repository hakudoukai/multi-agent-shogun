# -*- coding: utf-8 -*-
"""建て直しの器 20(第70弾)―― km-47・km-50 の臺帳を ★束内相対★ で建て直す(裁 322699)。
既成の臺帳(讀むのみ)の行を verify.py の paths_of で讀み → 頭 docs/evidence/<束>/ を落とす → ★cd <束の根>★ で append.py を呼び raw/saiken/<束>_manifest.txt へ建てる。
検め: 頭違ひ 0 / 束に無い名 0 / 新旧 (相対名, sha256) 対の一致 / 括つた行 / 員外 / 封。既成束・生器へ 0 字。"""
import os, sys, subprocess, hashlib, stat, time, re
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; AP = M + '/scripts/checks/karo_mac_manifest_append.py'
sys.path.insert(0, M + '/scripts/checks'); import karo_mac_manifest_verify as V
SAI = E + '/saiken'; os.makedirs(SAI, exist_ok=True)
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]
KISEI = ['km-47-yotsu-no-kazu-20260917', 'km-50-kara-wa-todokazu-20260917']
out = [f'# 20 建て直し / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / append.py sha16 {sha16(open(AP, "rb").read())} / verify.py(paths_of を借りる・讀むのみ) sha16 {sha16(open(V.__file__, "rb").read())}']
tsv = [('束', '相対名', '旧 sha256', '新 sha256', '対一致', '括つた')]
allok = True
for km in KISEI:
    BD = M + '/docs/evidence/' + km; pre = 'docs/evidence/' + km + '/'
    olds = [f for f in os.listdir(BD) if f.endswith('_manifest.txt')]; assert len(olds) == 1, olds
    OLD = BD + '/' + olds[0]; ob = open(OLD, 'rb').read()
    rows = []; atama_chigai = []; yomenu = 0
    for raw in ob.decode('utf-8').split('\n'):
        s = raw.strip()
        if not s or s.startswith('#'): continue
        m = V.SHA.search(s)
        if not m: yomenu += 1; continue
        c = V.paths_of(s)
        if not c: yomenu += 1; continue
        p = c[0]
        if not p.startswith(pre): atama_chigai.append(p); continue
        rows.append((p[len(pre):], m.group(1)))
    nai = [r for r, _ in rows if not os.path.isfile(os.path.join(BD, r))]
    NEW = SAI + '/' + km + '_manifest.txt'
    if os.path.exists(NEW): os.replace(NEW, NEW + '.prev')  # 二度目の走なら前の物を残す
    rels = [r for r, _ in rows]
    p = subprocess.run(['python3', '-B', AP, NEW] + rels, capture_output=True, cwd=BD)
    K.kaku(E + f'/20_append_{km[:5]}.stdout', p.stdout.decode('utf-8', 'replace')); K.kaku(E + f'/20_append_{km[:5]}.err', p.stderr.decode('utf-8', 'replace')); K.kaku(E + f'/20_append_{km[:5]}.rc', str(p.returncode))
    nb = open(NEW, 'rb').read() if os.path.isfile(NEW) else b''
    new = {}; kukuri = 0; nkou = 0
    for raw in nb.decode('utf-8').split('\n'):
        s = raw.strip()
        if not s or s.startswith('#'): continue
        m = V.SHA.search(s); c = V.paths_of(s)
        if not m or not c: continue
        nkou += 1; new[c[0]] = m.group(1)
        if s.startswith('path="'): kukuri += 1
    icchi = sum(1 for r, h in rows if new.get(r) == h); soui = sum(1 for r, h in rows if r in new and new[r] != h)
    kyuu_nomi = [r for r, _ in rows if r not in new]; shin_nomi = [r for r in new if r not in dict(rows)]
    for r, h in rows: tsv.append((km[:5], r, h[:16], new.get(r, '-')[:16], new.get(r) == h, r in new and any(l.startswith('path="' + r) for l in nb.decode('utf-8').split('\n'))))
    disk = []; hi = 0
    for d, ds, fs in os.walk(BD):
        for f in fs:
            q = os.path.join(d, f)
            if not stat.S_ISREG(os.lstat(q).st_mode): hi += 1; continue
            disk.append(os.path.relpath(q, BD))
    ingai = sorted(set(disk) - set(rels))
    ok = (not atama_chigai) and (not nai) and p.returncode == 0 and icchi == len(rows) == nkou and not kyuu_nomi and not shin_nomi
    allok = allok and ok
    out += [f'## {km}', f'既成の臺帳 {olds[0]} sha16 {sha16(ob)} bytes {len(ob)} 行 {ob.count(b"\n")} / 項(sha256= 有・path 讀めた) {len(rows)} / 讀めぬ {yomenu} / ★頭が {pre} でない行 {len(atama_chigai)}★ {atama_chigai[:3]} / ★束に無い名 {len(nai)}★ {nai[:3]}',
            f'append.py(cwd = {BD}) rc {p.returncode} / stdout 頭 {p.stdout.decode("utf-8", "replace").strip()[:110]!r}',
            f'新臺帳 raw/saiken/{km}_manifest.txt ★封 sha256 {hashlib.sha256(nb).hexdigest()}★ sha16 {sha16(nb)} bytes {len(nb)} 行 {nb.count(b"\n")} / 項 {nkou} / 括つた(空白名) {kukuri} / 一行目 {nb.decode("utf-8").split(chr(10))[2][:70]!r}',
            f'新旧の対: 母數(旧の項) {len(rows)} / 対一致(同じ相対名・同じ sha256) {icchi} / 相違 {soui} / 旧のみ {len(kyuu_nomi)} {kyuu_nomi[:3]} / 新のみ {len(shin_nomi)} {shin_nomi[:3]}',
            f'員外(束の disk に在つて臺帳に無い通常 file) {len(ingai)} 本 / disk 通常 file {len(disk)} / 非通常 {hi}: ' + ' '.join(ingai),
            f'判 {"★建て直せた★" if ok else "★建て直せて居らぬ★"}']
K.kaku(E + '/20_tatenaoshi.txt', '\n'.join(out)); K.kaku_tsv(E + '/20_tatenaoshi.tsv', tsv[1:], tsv[0]); print('\n'.join(out)); sys.exit(0 if allok else 1)
