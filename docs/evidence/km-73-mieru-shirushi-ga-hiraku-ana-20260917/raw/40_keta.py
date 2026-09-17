# -*- coding: utf-8 -*-
"""㋓ 多byte印は桁を壊すか 40 ―― 乙/甲/現行 の札(watcher・陽性形と長い形)に cut -c / cut -b / printf %-Ns・%.Ns / ${v:0:N} / awk length / wc -m / wc -c を
C と UTF-8 の二 locale で当て、出目の UTF-8 正否・LF の数・長さを刷る。N は ␊ の byte 位置の ★中★ に置く(第72弾 cut -c1-40 と同族か)。"""
import os, sys, subprocess, time
D = sys.argv[1]; E = D + '/raw'; sys.path.insert(0, E); import kaki as K, dai73 as T
loc = subprocess.run(['locale', '-a'], capture_output=True, text=True).stdout.split(); U8 = next((l for l in ('en_US.UTF-8', 'ja_JP.UTF-8', 'C.UTF-8') if l in loc), None)
FORMS = [('陽性 1\\n偽札', '1\n' + T.FAKE), ('長 x×60+\\n+y', 'x' * 60 + '\n' + 'y'), ('三印 1\\n\\r\\t2', '1\n\r\t2')]
rows = []; out = [f'# 40 桁 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / UTF-8 locale = {U8} / C locale']
def fuda(an, v):
    p = T.dai_path(E + '/dai', 'watcher', an); rc, so, se = T.hashi(p, v); return se.rstrip(b'\n')
for an in ('現行', '甲', '乙'):
    for nm, v in FORMS:
        f = fuda(an, v); pos = f.find('␊'.encode()) if an == '乙' else f.find(b'\xb6') if an == '甲' else f.find(b'\n')
        N = pos + 2 if pos >= 0 else 40  # ␊ の 3byte の ★二つ目★ で切る(甲は 1byte 故 印の直後・現行は改行の直後)
        for lc in ('C', U8):
            if lc is None: continue
            env = {'LC_ALL': lc}
            ops = [('cut -c1-%d' % N, ['cut', '-c1-%d' % N]), ('cut -b1-%d' % N, ['cut', '-b1-%d' % N]), ('cut -c1-40', ['cut', '-c1-40']), ('awk length', ['awk', '{print length($0)}']), ('wc -m', ['wc', '-m']), ('wc -c', ['wc', '-c']), ('wc -l', ['wc', '-l'])]
            for on, argv in ops:
                r = subprocess.run(argv, input=f, capture_output=True, env=env); o = r.stdout
                rows.append((an, nm, lc, on, N, T.u8(o), o.count(b'\n'), len(o), T.esc(o)[:100]))
            for on, cmd in [('bash printf %%-%ds|' % (N + 20), 'printf "%%-%ds|" "$V"' % (N + 20)), ('bash printf %%.%ds' % N, 'printf "%%.%ds" "$V"' % N), ('bash ${V:0:%d}' % N, 'printf "%%s" "${V:0:%d}"' % N), ('bash ${#V}', 'printf "%s" "${#V}"')]:
                r = subprocess.run(['/bin/bash', '-c', cmd], capture_output=True, env={'LC_ALL': lc, 'V': f.decode('utf-8', 'surrogateescape')} if T.u8(f) == '正' else {'LC_ALL': lc}, input=None)
                o = r.stdout; rows.append((an, nm, lc, on, N, T.u8(o) if T.u8(f) == '正' else '(札が UTF-8 不正ゆゑ env に載せず)', o.count(b'\n'), len(o), T.esc(o)[:100]))
K.kaku_tsv(E + '/40_keta.tsv', rows, ['案', '形', 'locale', '器', 'N', '出目のUTF-8', '出目のLF数', '出目bytes', '出目(esc・100字迄)'])
bad = [r for r in rows if r[0] == '乙' and r[5].startswith('不正')]; addlf = [r for r in rows if r[0] == '乙' and r[3].startswith('cut') and r[6] > 0]
out.append(f'★乙の札を byte で切る器が UTF-8 不正を産んだ走 = {len(bad)}/{sum(1 for r in rows if r[0]=="乙")}: ' + ' / '.join(f'{r[2]} {r[3]}({r[1]})→{r[5]}' for r in bad))
out.append(f'★乙の札に cut が LF を足した走 = {len(addlf)}: ' + ' / '.join(f'{r[2]} {r[3]}({r[1]}) LF {r[6]}' for r in addlf))
lens = [r for r in rows if r[0] == '乙' and r[1].startswith('陽性') and r[3] in ('awk length', 'wc -m', 'wc -c', 'bash ${#V}')]
out.append('★同じ乙の札の「長さ」が器で違ふ★: ' + ' / '.join(f'{r[2]} {r[3]}={r[8].strip()}' for r in lens))
out.append('読み: 第72弾 3-1(cut -c1-40 が LF を足す)と同族か否かは 70 が此の表から断ずる。')
K.kaku(E + '/40_keta.txt', '\n'.join(out)); print('\n'.join(out))
