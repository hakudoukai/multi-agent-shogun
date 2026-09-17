# -*- coding: utf-8 -*-
"""門を最後に走らせる器 60(第76弾 km-80・km-77 の写し・_after= 臺帳の後の器・員外)―― ① 錠(raw/ 0444・dir 0555)→ ② 歩哨 → ③ selftest → ④ 本走 main(MANIFEST.txt+員内・KM_GATE_MANIFEST_BASE=.・cwd 束の根)/nobase(基点無し・落ちて正)→ ⑤ 門控= _gate/mon_km80_<刻>.log(★走ごとに一意★・員外)。rc は subprocess の returncode(pipe 無し)。"""
import os, sys, subprocess, hashlib, time, stat, re
assert sys.flags.dont_write_bytecode, '-B で走らせよ'
D = sys.argv[1]; RN = '76'; RAW = D + '/raw'; AFT = D + '/_after'; MAN = D + '/MANIFEST.txt'; M = '/Users/momizimac/multi-agent-shogun'; GATE = M + '/scripts/checks/karo_mac_dasumae_gate.sh'
sys.path.insert(0, RAW); import kaki as K
STAMP = time.strftime('%Y%m%dT%H%M%S'); LOG = D + f'/_gate/mon_km80_{STAMP}.log'; assert not os.path.exists(LOG)
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]; GSHA = sha16(open(GATE, 'rb').read()); os.makedirs(AFT, exist_ok=True)
items = [re.search(r'^path=(\S+) ', l).group(1) for l in open(MAN, encoding='utf-8') if l.startswith('path=')]
out = [f'# 第{RN}弾 門控(員外・名= mon_km80_{STAMP}) / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {GSHA} / 照合器 sha16 {sha16(open(M + "/scripts/checks/karo_mac_manifest_verify.py", "rb").read())} / 臺帳 sha16 {sha16(open(MAN, "rb").read())} / 紙 sha16 {sha16(open(D + "/README.md", "rb").read())} / 臺帳の項 {len(items)} / 基点 {D}(束内相対・KM_GATE_MANIFEST_BASE=.)']
assert not [f for d, ds, fs in os.walk(RAW) for f in fs if '__pycache__' in d]
nf = nd = 0
for d, ds, fs in os.walk(RAW, topdown=False):
    for f in fs:
        q = os.path.join(d, f)
        if stat.S_ISREG(os.lstat(q).st_mode): os.chmod(q, 0o444); nf += 1
    os.chmod(d, 0o555); nd += 1
out.append(f'① 錠 {time.strftime("%H:%M:%S")} / raw/ 通常 file {nf} → 0444 / dir {nd} → 0555')
K.kaku(AFT + '/00_hosho.txt', f'歩哨 ―― 門の直前の一行 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 第{RN}弾'); out.append('② 歩哨 _after/00_hosho.txt')
def run(name, argv, env):
    p = subprocess.run(argv, capture_output=True, cwd=D, env=env); K.kaku(AFT + f'/60_gate_{name}.err', p.stderr.decode('utf-8', 'replace')); K.kaku(AFT + f'/60_gate_{name}.out', p.stdout.decode('utf-8', 'replace')); K.kaku(AFT + f'/60_gate_{name}.rc', str(p.returncode))
    e = p.stderr.decode('utf-8', 'replace'); ket = [x for x in e.split('\n') if x.startswith('★') and ('門' in x or '自己検め' in x)]
    return p.returncode, ket, e
env = dict(os.environ); env['KM_GATE_MANIFEST_BASE'] = '.'
rc, ket, e = run('selftest', ['bash', GATE, '--selftest'], env); out.append(f'③ selftest | 渡した 0 | rc {rc} | 結語 {ket}')
rc1, ket1, e1 = run('main', ['bash', GATE, MAN] + [os.path.join(D, i) for i in items], env); out.append(f'④ main | 渡した {len(items)} | rc {rc1} | 結語 {ket1}')
env2 = dict(os.environ); env2.pop('KM_GATE_MANIFEST_BASE', None)
rc2, ket2, e2 = run('nobase', ['bash', GATE, MAN] + [os.path.join(D, i) for i in items], env2); out.append(f'④′ nobase(基点無し・落ちて正) | 渡した {len(items)} | rc {rc2} | 結語 {ket2}')
K.kaku(AFT + '/60_gate_rcs.txt', f'③ selftest | rc {rc}\n④ main | 渡した {len(items)} | rc {rc1}\n④′ nobase | rc {rc2}\n門控 {os.path.relpath(LOG, D)}')
out.append('## 走り main(stderr 逐語)'); out += ['  ' + x for x in e1.split('\n') if x.strip()]
out.append('## 走り nobase(stderr 逐語・基点無し)'); out += ['  ' + x for x in e2.split('\n') if x.strip()]
out.append('## 此の門が意味せぬ事: rc0 は形(空白/CR/EOF/寸法/臺帳との一致)のみ。門は箱・logs・scripts の中身を讀まぬ。門控と _after は員外(臺帳の後)。')
K.kaku(LOG, '\n'.join(out)); print('\n'.join(out)[:2600])
