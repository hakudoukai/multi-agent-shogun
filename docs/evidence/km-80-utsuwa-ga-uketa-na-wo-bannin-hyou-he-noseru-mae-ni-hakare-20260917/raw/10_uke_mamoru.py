# -*- coding: utf-8 -*-
"""10 ㋐㋑(第76弾 km-80)―― 表A「受ける口」= ASW_PROCESS_TIMEOUT の語を含む行 悉く(行番号+逐語・分類)/ 表B「守る表」= `for _t in` 〜 `done` を逐語で(名を分解)/ ㋑ 比較器= 其の名が [ ] の中に立つ行の 左項・演算子・右項。disk と HEAD の二列。行番号は ★己の器で引く★(家老札の L224/L1599/L173-175 は照合対象)。陽性対照= ESCALATE_PHASE1(表に在る)・陰性対照= ZZ_KM80_NEG(樹に無い)。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; T = 'scripts/inbox_watcher.sh'; NAME = 'ASW_PROCESS_TIMEOUT'
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=M).stdout.strip()
src = {'disk': open(M + '/' + T, encoding='utf-8').read().split('\n'), 'HEAD': subprocess.run(['git', 'show', head + ':' + T], capture_output=True, text=True, cwd=M).stdout.split('\n')}
def cls(l):
    s = l.strip()
    if s.startswith('#'): return '註'
    if re.match(r'^' + NAME + r'=\$\{' + NAME + r':-', s): return '受(NAME=${NAME:-既定})'
    if re.search(r'\[\s*"?\$\{?' + NAME, l): return '比較器([ ] の中)'
    return '他'
out = [f'# 10 ㋐㋑ / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 的 {T} / HEAD {head[:12]} / 名 {NAME}']
A = ['版\t行\t分類\t逐語']; cmp_rows = ['版\t行\t左項\t演算子\t右項\t演算子の種\t逐語']
for v in ('disk', 'HEAD'):
    ls = [(i + 1, l) for i, l in enumerate(src[v]) if NAME in l]
    out.append(f'表A 受ける口({v}): 語 {NAME} を含む行 {len(ls)} 本')
    for n, l in ls:
        A.append(f'{v}\t{n}\t{cls(l)}\t{l.strip()}')
        for m in re.finditer(r'\[\s*(\S+)\s+(-eq|-ne|-lt|-le|-gt|-ge|=|==|!=)\s+(\S+)\s*\]', l):
            if NAME in m.group(0): cmp_rows.append(f'{v}\t{n}\t{m.group(1)}\t{m.group(2)}\t{m.group(3)}\t' + ('文字列比較(=/==/!=)' if m.group(2) in ('=', '==', '!=') else '數比較(-eq 等・非数で rc2)') + f'\t{l.strip()}')
    # 表B 守る表
    fi = [i for i, l in enumerate(src[v]) if l.startswith('for _t in ')]; assert len(fi) == 1, f'{v}: for _t in の行が {len(fi)} 本'
    j = fi[0]
    while not src[v][j].startswith('done'): j += 1
    blk = src[v][fi[0]:j + 1]; names = re.findall(r'\b([A-Z][A-Z0-9_]*):(\d+)', '\n'.join(blk))
    out.append(f'表B 守る表({v}): L{fi[0]+1}-L{j+1}(逐語 下記)/ 名 {len(names)} 本= ' + ' '.join(n for n, d in names))
    for k, l in enumerate(blk): out.append(f'  {v} L{fi[0]+1+k}: {l}')
    out.append(f'  {v} 判定: {NAME} は守る表に ' + ('★在る★' if NAME in [n for n, d in names] else '★無い★') + f' / 陽性対照 ESCALATE_PHASE1 ' + ('在る' if 'ESCALATE_PHASE1' in [n for n, d in names] else '★無い(器が疑はしい)★') + ' / 陰性対照 ZZ_KM80_NEG ' + ('★在る(器が疑はしい)★' if 'ZZ_KM80_NEG' in [n for n, d in names] else '無い') + f' / 同形で守られぬ隣人 ASW_NO_IDLE_FULL_READ ' + ('在る' if 'ASW_NO_IDLE_FULL_READ' in [n for n, d in names] else '無い(km-77 ㋒B と一致)'))
    # 全 ${NAME:-N} 形の受口で表B に無い名(disk のみ数へる)
    if v == 'disk':
        rec = {}
        for i, l in enumerate(src[v]):
            if l.strip().startswith('#'): continue
            for m in re.finditer(r'^([A-Z][A-Z0-9_]*)=\$\{\1:-([^}]*)\}', l.strip()): rec.setdefault(m.group(1), []).append((i + 1, m.group(2)))
        nb = {k: w for k, w in rec.items() if k not in [n for n, d in names]}
        out.append(f'  disk 補: NAME=${{NAME:-既定}} の受口 {len(rec)} 名の内 守る表に無い名 {len(nb)}= ' + ' '.join(f'{k}(L{",".join(str(a) for a,b in w)}:既定 {w[0][1][:12]})' for k, w in sorted(nb.items())))
out.append(f'零の札: 陽性= 語 {NAME} disk {sum(1 for l in src["disk"] if NAME in l)} 行・HEAD {sum(1 for l in src["HEAD"] if NAME in l)} 行 / 陰性= 語 ZZ_KM80_NEG disk {sum(1 for l in src["disk"] if "ZZ_KM80_NEG" in l)} 行 / 根= 的 file 一本(全行)/ 刻= 頭')
K.kaku(D + '/raw/10_uke_mamoru.txt', '\n'.join(out)); K.kaku(D + '/raw/10_ukeru.tsv', '\n'.join(A)); K.kaku(D + '/raw/10_hikakuki.tsv', '\n'.join(cmp_rows)); print('\n'.join(out)); print('\n'.join(A)); print('\n'.join(cmp_rows))
