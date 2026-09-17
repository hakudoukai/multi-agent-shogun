# -*- coding: utf-8 -*-
"""45 ㋔ 稼働中 watcher の inode ⇔ repo の版(第76弾 km-80)―― ps で inbox_watcher.sh の process を引き(己の系譜を除く・除いた残りも刷る)、lsof で fd 255 の inode/寸法を取り、disk と HEAD 系譜の blob 寸法に突き合はせる。読取のみ・process へ信号 0。"""
import os, sys, re, time, subprocess, hashlib
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; T = 'scripts/inbox_watcher.sh'
def sh(*a, **k): p = subprocess.run(list(a), capture_output=True, text=True, cwd=M, **k); return p.stdout, p.returncode
ps, rc = sh('ps', '-axo', 'pid=,ppid=,lstart=,command=')
me = os.getpid(); rows = [l for l in ps.split('\n') if 'inbox_watcher.sh' in l]
hit = [l for l in rows if re.search(r'^\s*\d+\s+\d+\s+.{24}\s+bash scripts/inbox_watcher\.sh ', l)]; rest = [l for l in rows if l not in hit]
out = [f'# 45 ㋔ / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / ps rc {rc} / 語 inbox_watcher.sh を含む行 {len(rows)} = 條(bash scripts/inbox_watcher.sh 起し) {len(hit)} + 残り {len(rest)}(己の系譜等・逐語下記)']
for l in rest: out.append('  残り: ' + l.strip()[:160])
tbl = ['pid\tppid\tlstart\tfd\tinode\tbytes\tpath\tpane']
for l in hit:
    m = re.match(r'^\s*(\d+)\s+(\d+)\s+(.{24})\s+(.*)$', l); pid, ppid, ls, cmd = m.groups()
    lo, lrc = sh('lsof', '-p', pid); fl = [x for x in lo.split('\n') if x.endswith(T) or ('/' + T) in x]
    for x in fl:
        c = x.split(); tbl.append(f'{pid}\t{ppid}\t{ls.strip()}\t{c[3]}\t{c[7]}\t{c[6]}\t{c[8]}\t{cmd.split()[2] if len(cmd.split())>2 else "?"}')
    if not fl: tbl.append(f'{pid}\t{ppid}\t{ls.strip()}\t?\t?\t?\t(lsof に {T} 無し rc {lrc})\t?')
st = os.stat(M + '/' + T); dsha = hashlib.sha256(open(M + '/' + T, 'rb').read()).hexdigest()[:16]
out.append(f'disk: inode {st.st_ino} / bytes {st.st_size} / mtime {time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime))} / sha16 {dsha}')
log, _ = sh('git', 'log', '--format=%h %ci', '--', T); blobs = []
for l in log.split('\n'):
    if not l.strip(): continue
    h, ci = l.split(' ', 1); sz, r = sh('git', 'cat-file', '-s', h + ':' + T); blobs.append((h, ci.strip(), sz.strip(), r))
out.append('HEAD 系譜(git log -- 的)の blob 寸法(git cat-file -s <h>:<path>・python 経由= zsh の :s 修飾を踏まぬ):')
for h, ci, sz, r in blobs[:8]: out.append(f'  {h} {ci} bytes {sz} rc {r}')
run_sizes = sorted({r.split('\t')[5] for r in tbl[1:]}); run_inodes = sorted({r.split('\t')[4] for r in tbl[1:]})
match = [(h, ci) for h, ci, sz, r in blobs if sz in run_sizes]
out.append(f'稼働 inode {run_inodes} / 稼働 bytes {run_sizes} ⇔ disk inode {st.st_ino} bytes {st.st_size} → ' + ('★同じ inode★' if str(st.st_ino) in run_inodes else '★別 inode(稼働は置換前の版・repo 版は次 respawn まで効かぬ)★'))
out.append(f'稼働 bytes と一致する HEAD 系譜 blob= {len(match)} 本 {match}(寸法一致は版の同定の必要條件であつて十分條件ではない ―― 稼働 inode の中身は他 process の fd ゆゑ讀めず sha は取れぬ)')
out.append('此の器が意味せぬ事: 稼働 process の版の逐語は取れぬ(寸法と起動刻のみ)。process へは信号 0・kill 0 も打たぬ。')
K.kaku(D + '/raw/45_inode.txt', '\n'.join(out)); K.kaku(D + '/raw/45_inode.tsv', '\n'.join(tbl)); print('\n'.join(out)); print('\n'.join(tbl))
