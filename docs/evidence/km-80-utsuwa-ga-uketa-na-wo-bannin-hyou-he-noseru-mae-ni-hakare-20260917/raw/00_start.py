# -*- coding: utf-8 -*-
"""00 起(第76弾 km-80)―― 刻・枝・HEAD・的(scripts/inbox_watcher.sh)の HEAD と disk の差を先に取る。読取のみ(km-77 の写し・的を一本に絞る)。"""
import os, sys, time, hashlib, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; T = 'scripts/inbox_watcher.sh'
def git(*a): p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=M); return p.stdout.strip(), p.returncode
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); head, _ = git('rev-parse', 'HEAD'); br, _ = git('branch', '--show-current')
diff, rc = git('diff', '--name-only', 'HEAD', '--', T); st = os.stat(M + '/' + T); dsha = hashlib.sha256(open(M + '/' + T, 'rb').read()).hexdigest()
hsha, _ = git('rev-parse', 'HEAD:' + T); hsize, _ = git('cat-file', '-s', 'HEAD:' + T)
out = [f'# 00 起 / 刻 {koku} / 枝 {br} / HEAD {head[:12]} / 的= {T} 一本(裁 324588 1弾=1file)']
out.append(f'disk: inode {st.st_ino} / bytes {st.st_size} / mtime {time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime))} / sha256 {dsha[:16]}')
out.append(f'HEAD: blob {hsha[:12]} / bytes {hsize} / git diff --name-only HEAD -- {T} (rc {rc}) = {len(diff.splitlines())} 本 → ' + ('★disk は HEAD と違ふ(未 commit の差あり)★' if diff else '差 0'))
out.append('生器へ 0 字(scripts/ ~/bin/ は讀むのみ)/ 稼働中 watcher 不觸(裁 323062⑷)/ 毒は束内の写し器へ当てる。')
K.kaku(D + '/raw/00_start.txt', '\n'.join(out)); print('\n'.join(out))
