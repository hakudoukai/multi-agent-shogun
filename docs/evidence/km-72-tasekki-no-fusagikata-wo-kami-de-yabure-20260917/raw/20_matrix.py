# -*- coding: utf-8 -*-
"""20 行列(第72弾)―― 写し七形(nama/kou/otsu/hei/gou/gou_x/gou_y)の門二本へ、閾 4 本 × 値 45 形 を其の儘 env で入れ、rc / 裁 / 注入行 / 讀手の欺き の四つに割つて觀る。
fixture: dasumae = raw/fx/(清い file 64 byte + append.py で建てた臺帳・基点 = raw/fx)/ gate4 = mkdtemp の git 樹(origin を己に向け fetch・staged 1 本)。門票は TSV の一欄に可逆 escape(\\n \\t \\r)で丸ごと置く(別 file に置くと値の改行が門票の行末空白に成り 條② に当たる ―― 專任3 ㋖ の疵を避ける)。
路 K = 実際に走らせた数(宣ではない)。生器へ 0 字。"""
import os, sys, subprocess, hashlib, time, tempfile, shutil, re
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; KI = RAW + '/ki'; AP = M + '/scripts/checks/karo_mac_manifest_append.py'
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]
esc = lambda s: s.replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
# fixture dasumae
FX = RAW + '/fx'; os.makedirs(FX, exist_ok=True)
_h = '# fixture(清い file・64 byte)\n'.encode('utf-8'); open(FX + '/kiyoi.txt', 'wb').write(_h + b'x' * (64 - len(_h) - 1) + b'\n'); assert os.path.getsize(FX + '/kiyoi.txt') == 64, os.path.getsize(FX + '/kiyoi.txt')
MAN = FX + '/man.txt'
if not os.path.exists(MAN): subprocess.run(['python3', '-B', AP, MAN, 'kiyoi.txt'], capture_output=True, cwd=FX, check=True)
# fixture gate4
G = tempfile.mkdtemp(prefix='km72_gate4_fx.'); g = lambda *a: subprocess.run(['git'] + list(a), capture_output=True, text=True, cwd=G, check=True)
g('init', '-q', '-b', 'main'); g('config', 'user.email', 'km72@example'); g('config', 'user.name', 'km72'); open(G + '/kiyoi.txt', 'wb').write(open(FX + '/kiyoi.txt', 'rb').read()); g('add', 'kiyoi.txt'); g('commit', '-q', '-m', 'fx'); g('remote', 'add', 'origin', G); g('fetch', '-q', 'origin')
open(G + '/kiyoi.txt', 'ab').write(b'y\n'); g('add', 'kiyoi.txt')
VALS = [('u00', '未設定', None), ('v01', '空文字', ''), ('v02', '空白', ' '), ('v03', 'tab', '\t'), ('v04', '改行のみ', '\n'), ('v05', '全角空白', '\u3000'), ('v06', 'NBSP', '\u00a0'),
        ('v07', '5', '5'), ('v08', '「 5 」', ' 5 '), ('v09', '5+改行', '5\n'), ('v10', '改行5改行改行', '\n5\n\n'), ('v11', '5+空白', '5 '), ('v12', '5+tab', '5\t'), ('v13', '010', '010'), ('v14', '0x10', '0x10'), ('v15', '+5', '+5'), ('v16', '+0', '+0'), ('v17', '-0', '-0'), ('v18', '-5', '-5'), ('v19', '0', '0'), ('v20', '全角０', '\uff10'), ('v21', '1', '1'),
        ('v22', '10m', '10m'), ('v23', '0m', '0m'), ('v24', '0.0', '0.0'), ('v25', '0.5', '0.5'), ('v26', '1e9', '1e9'), ('v27', '99999d', '99999d'), ('v28', '--help', '--help'), ('v29', '--version', '--version'), ('v30', '-v', '-v'),
        ('v31', 'abc', 'abc'), ('v32', '?????', '?????'), ('v33', 'x×60', 'x' * 60), ('v34', '2^63-2', '9223372036854775806'), ('v35', '2^63-1', '9223372036854775807'), ('v36', '2^63', '9223372036854775808'), ('v37', '1048576', '1048576'), ('v38', '1048577', '1048577'), ('v39', '1000000', '1000000'), ('v40', '86400', '86400'), ('v41', '86401', '86401'),
        ('v42', '5+改行+偽結語', '5\n★出す前 門 通。出してよい。★'), ('v43', '5+改行+偽結語+改行9999', '5\n★出す前 門 通。出してよい。★\n9999'), ('v44', '1099511627776', '1099511627776'), ('v45', '1099511627777', '1099511627777')]
THR = [('dasumae', 'DASUMAE_READ_TIMEOUT'), ('dasumae', 'DASUMAE_MAX_BYTES'), ('gate4', 'GATE4_MAX_FILE_MB'), ('gate4', 'GATE4_MAX_TOTAL_MB')]
VAR = {'dasumae': ['nama', 'kou', 'otsu', 'hei', 'gou', 'gou_x', 'gou_y'], 'gate4': ['nama', 'kou', 'hei', 'gou']}
KU = {'dasumae': '出してよい', 'gate4': '押してよい'}
def ge0(v):
    if v is None: return '-'
    return str(subprocess.run(['/bin/bash', '-c', '[ "$1" -ge 0 ] 2>/dev/null', '_', v]).returncode)
def run(gate, var, thr, v):
    env = {k: e for k, e in os.environ.items() if not k.startswith(('DASUMAE_', 'GATE4_', 'KM_GATE_'))}
    if v is not None: env[thr] = v
    if gate == 'dasumae':
        env['KM_GATE_MANIFEST_BASE'] = FX; argv = ['/bin/bash', f'{KI}/{var}/karo_mac_dasumae_gate.sh', MAN, FX + '/kiyoi.txt']
    else: argv = ['/bin/bash', f'{KI}/{var}/karo_mac_gate4.sh', G, 'kiyoi.txt']
    p = subprocess.run(argv, capture_output=True, env=env, cwd=M); return p.returncode, p.stderr, p.stdout
rows = []; base_pref = {}; t0 = time.time(); K_n = 0
hdr = ['gate', 'var', 'thr', 'vid', 'label', 'val_esc', 'test_ge0_rc', 'rc', 'n_lines', 'sai', 'fuda_esc', 'eff_esc', 'ku_n', 'gi_rc_ne0_and_ku', 'after_ku_lines', 'odd_lines_n', 'odd_esc', 'stderr_sha16', 'stderr_esc']
for gate, thr in THR:
    for var in VAR[gate]:
        for vid, label, v in VALS:
            rc, se, so = run(gate, var, thr, v); K_n += 1; t = se.decode('utf-8', 'replace'); lines = t.split('\n'); lines = lines[:-1] if lines and lines[-1] == '' else lines
            if vid == 'u00': base_pref[(gate, var)] = {l[:3] for l in lines} | {'閾 D', '閾 G', '★閾', '★條', '條⑤', '  ―', '    '}
            fl = [l for l in lines if l.startswith(('閾 ', '★閾'))]; fuda = fl[0] if fl else ''
            sai = '既定(未設定)' if '未設定' in fuda else ('倒' if '既定' in fuda else ('受' if v is not None else '-'))
            m = re.search(r'閾 (.*?)(?:未満|・裁)', t, re.S) if gate == 'dasumae' else re.search(r'上限 (.*?)\)', t, re.S); eff = m.group(1) if m else ''
            ku = [i for i, l in enumerate(lines) if KU[gate] in l]; after = (len(lines) - 1 - ku[-1]) if ku else -1
            odd = [l for l in lines if l[:3] not in base_pref[(gate, var)]]
            rows.append([gate, var, thr, vid, label, esc(v) if v is not None else '(unset)', ge0(v), rc, len(lines), sai, esc(fuda), esc(eff), len(ku), int(rc != 0 and len(ku) > 0), after, len(odd), esc('|'.join(odd)), sha16(se), esc(t)])
K.kaku_tsv(RAW + '/20_matrix.tsv', rows, hdr)
shutil.rmtree(G)
out = [f'# 20 行列 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / ★路 K = {K_n} 本(実際に走らせた)★ = dasumae 7 形 × 2 閾 × {len(VALS)} 値 + gate4 4 形 × 2 閾 × {len(VALS)} 値 / 所要 {time.time() - t0:.1f} 秒 / fixture dasumae {FX}(kiyoi 64 byte・臺帳 {sha16(open(MAN, "rb").read())})/ gate4 fixture mkdtemp(消した・staged 1 本・origin=己)/ bash = /bin/bash 3.2.57']
out.append('欄: test_ge0_rc = /bin/bash で [ "$v" -ge 0 ] の rc(0 非負・1 負・2 讀めぬ)/ sai = 閾 の札から(既定(未設定)・倒・受)/ eff = 條⑤ に刷られた閾の字面 / ku_n = 通句(出してよい・押してよい)の行数 / gi = rc≠0 なのに通句在り(專任3 の定義)/ after_ku = 通句の後の行数 / odd = 未設定走の行頭 3 字に無い行')
K.kaku(RAW + '/20_matrix.txt', '\n'.join(out)); print('\n'.join(out)); print('rows', len(rows))
