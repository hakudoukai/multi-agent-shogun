# -*- coding: utf-8 -*-
"""usage: 40_hashiru.py <bundle> ―― 写し三本 × 基点十一形 × 臺帳二形 を回す。
★生器は一度も呼ばぬ★(呼ぶのは utsushi/ の写しのみ)。
欄: 器 / 形札 / 形名 / 臺帳 / rc / 條①の札 / stderr 行数 / 偽行の混入
"""
import sys, os, subprocess, hashlib, base64, json
bundle = os.path.abspath(sys.argv[1])
root = os.getcwd()
UT = os.path.join(bundle, 'utsushi')
FX = os.path.join(bundle, 'raw', 'fx')
os.makedirs(FX, exist_ok=True)

# ―― fixture: 清い紙 2 枚(末尾空白無・CR無・EOF改行丁度1)――
paths = []
for i in (1, 2):
    p = os.path.join(FX, 'kami%d.txt' % i)
    open(p, 'w', encoding='utf-8').write('第53弾 fixture %d\n' % i)
    paths.append(p)

def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()

# 臺帳 二形
man_taba = os.path.join(FX, 'manifest_taba.txt')   # 束内相対(fx/ からの相対)
man_kyu  = os.path.join(FX, 'manifest_kyu.txt')    # 舊形(repo 根相対)
with open(man_taba,'w',encoding='utf-8') as f:
    f.write('# 本形: path=<p> sha256=<64> ―― 基点は ★fx/ からの相対★\n')
    for p in paths: f.write('path=%s sha256=%s\n' % (os.path.basename(p), sha(p)))
with open(man_kyu,'w',encoding='utf-8') as f:
    f.write('# 本形: path=<p> sha256=<64> ―― 基点は ★repo 根からの相対(舊形)★\n')
    for p in paths: f.write('path=%s sha256=%s\n' % (os.path.relpath(p, root), sha(p)))

FORGE = '條① 台帳とdiskの差 = 一致(manifest_verify.py rc=0)'
KATACHI = [
    ('01','未設定',            None),
    ('02','空文字',            ''),
    ('03','空白のみ(ASCII)',   '   '),
    ('04','点(cwd 相対の明示)', '.'),
    ('05','絶対(束の fx)',      FX),
    ('06','絶対(repo 根)',      root),
    ('07','★零倒★ 0',          '0'),
    ('08','★極倒★ 2^63 超',    '99999999999999999999'),
    ('09','★八進★ 010',        '010'),
    ('10','★行注入★ 改行+偽行', FX + '\n' + FORGE),
    ('11','全角空白のみ',       '　'),
]
MANS = [('taba','束内相対',man_taba), ('kyu','舊形(repo根)',man_kyu)]
GATES = ['gate_base.sh','gate_an_i.sh','gate_an_ro.sh']

rows = []
logdir = os.path.join(bundle,'raw','40_logs'); os.makedirs(logdir, exist_ok=True)
for g in GATES:
    for mk, mlabel, man in MANS:
        for tag, kname, val in KATACHI:
            env = dict(os.environ)
            env.pop('KM_GATE_MANIFEST_BASE', None)
            if val is not None:
                env['KM_GATE_MANIFEST_BASE'] = val
            r = subprocess.run(['bash', os.path.join(UT,g), man] + paths,
                               capture_output=True, env=env, cwd=root)
            err = r.stderr.decode('utf-8','replace')
            out = r.stdout.decode('utf-8','replace')
            fn = '%s_%s_%s.err' % (g.replace('.sh',''), mk, tag)
            open(os.path.join(logdir,fn),'w',encoding='utf-8').write(err)
            jou1 = [l for l in err.split('\n') if l.startswith('條①') or '條①' in l]
            fuda = ' / '.join(x.strip()[:58] for x in jou1) or '(條①の札 無し)'
            # 偽行: 「真に器が刷つた一致行」と「注入された行」を分ける
            forged = sum(1 for l in err.split('\n') if l.strip() == FORGE)
            rows.append(dict(ki=g, man=mk, manlabel=mlabel, tag=tag, kata=kname,
                             rc=r.returncode, fuda=fuda, errlines=len(err.split('\n')),
                             forged=forged, stdout_len=len(out)))

tsv = os.path.join(bundle,'raw','40_hashiru.tsv')
with open(tsv,'w',encoding='utf-8') as f:
    f.write('#colspec\t器\t臺帳\t形札\t形名\trc\t偽行\tstderr行\tstdout字\t條①の札\n')
    for r in rows:
        f.write('%s\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%s\n' % (r['ki'],r['man'],r['tag'],r['kata'],
                r['rc'],r['forged'],r['errlines'],r['stdout_len'],r['fuda']))
print('走 %d 件 → %s' % (len(rows), os.path.relpath(tsv, root)))
json.dump(rows, open(os.path.join(bundle,'raw','40_hashiru.json'),'w'), ensure_ascii=False, indent=1)
