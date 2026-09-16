# -*- coding: utf-8 -*-
"""30 順序(第72弾 ㋑)―― 甲・乙・丙 の dasumae diff を patch で ★順に重ねる★(3! = 6 順)。建つた物を 合(gou)の写しと比べ、合が「三案を順に当てた物」と同じか、手で織つた別物かを数へる。gate4 は 甲・丙 の 2 順。rej は消さず数へる。"""
import os, sys, subprocess, hashlib, itertools, shutil, time
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K; KI = RAW + '/ki'; AN = KI + '/an'; J = RAW + '/junjo'; os.makedirs(J, exist_ok=True)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
out = [f'# 30 順序 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}']
def stack(f, names):
    d = J + '/' + '_'.join(n.split('_')[0] for n in names) + '_' + f.split('_')[2].split('.')[0]; os.makedirs(d, exist_ok=True); shutil.copyfile(f'{KI}/nama/{f}', f'{d}/{f}'); log = []
    for n in names:
        p = subprocess.run(['patch', '-p1', '-N', '-d', d, '-i', f'{AN}/{n}.diff'], capture_output=True, text=True); log.append(f'{n.split("_")[0]} rc{p.returncode}[' + ';'.join(l.replace('Hunk #', 'H') for l in p.stdout.splitlines() if 'Hunk' in l or 'FAILED' in l or 'ignored' in l) + ']')
    rej = sorted(x for x in os.listdir(d) if x.endswith('.rej')); return d, ' → '.join(log), rej
for f, fam in (('karo_mac_dasumae_gate.sh', ['kou_dasumae', 'otsu_dasumae', 'hei_dasumae']), ('karo_mac_gate4.sh', ['kou_gate4', 'hei_gate4'])):
    gs = sha16(f'{KI}/gou/{f}'); same = 0; n = 0
    for perm in itertools.permutations(fam):
        d, log, rej = stack(f, list(perm)); s = sha16(f'{d}/{f}'); n += 1; same += (s == gs)
        out.append(f'{f} 順 {"→".join(p.split("_")[0] for p in perm)}: {log} / rej {rej} / 建つた物 sha16 {s} ⇔ 合 {gs} {"★同★" if s == gs else "違"} / bash -n rc {subprocess.run(["bash", "-n", f"{d}/{f}"]).returncode}')
    out.append(f'★{f}: {n} 順の内 合と同じ物が建つたのは {same} 順★')
K.kaku(RAW + '/30_junjo.txt', '\n'.join(out)); print('\n'.join(out))
