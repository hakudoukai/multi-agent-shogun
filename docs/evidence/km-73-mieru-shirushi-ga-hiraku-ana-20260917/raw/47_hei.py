# -*- coding: utf-8 -*-
"""㋕ 丙(當席の案)を紙の為に測る 47 ―― 丙1 printf %q / 丙2 base64 / 丙3 数のみ / 丙4 刷らぬ を、20 の十三形 + 陰性二形で watcher/ctxwarn に当て、
讀手四つの行数・UTF-8・可逆(%q は eval・base64 は decode で戻すか)・札の長さ(bytes/字)・dash での可否・偽陽性(清い値が変るか)を刷る。"""
import sys, time, subprocess, base64, re
D = sys.argv[1]; E = D + '/raw'; sys.path.insert(0, E); import kaki as K, dai73 as T
sys.path.insert(0, E); from importlib import import_module
NAMED = import_module('20_seigyo').NAMED if False else [('LF \\n', '\n'), ('CR \\r', '\r'), ('TAB \\t', '\t'), ('VT \\v', '\x0b'), ('FF \\f', '\x0c'), ('BS \\b', '\x08'), ('ESC', '\x1b'), ('U+2028 LS', '\u2028'), ('U+2029 PS', '\u2029'), ('U+0085 NEL', '\x85'), ('U+00A0 NBSP', '\xa0'), ('U+3000 全角空白', '\u3000'), ('陰性 abc', None), ('陰性 全角０', None), ('元から␊ 1␊2', None)]
rows = []; out = [f'# 47 丙を測る / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}']
def val(nm, ch):
    if nm == '陰性 abc': return 'abc'
    if nm == '陰性 全角０': return '０'
    if nm == '元から␊ 1␊2': return '1␊2'
    return '1' + ch + T.FAKE
def kagyaku(an, se, v):
    m = re.search(r'「(.*)」', se.decode('utf-8', 'surrogateescape'), re.S)
    if not m: return '札に値無し'
    x = m.group(1)
    if an == '丙1 %q':
        r = subprocess.run(['/bin/bash', '-c', 'eval "r=$1"; printf "%s" "$r"', '_', x], capture_output=True, env={'LC_ALL': 'C'}); return '戻る' if r.stdout == v.encode('utf-8') else f'戻らぬ({T.esc(r.stdout)[:30]})'
    if an == '丙2 base64':
        try: return '戻る' if base64.b64decode(x[4:]) == v.encode('utf-8') else '戻らぬ'
        except Exception as e: return f'戻らぬ({e})'
    return '不可逆(設計)'
for key in ('watcher', 'ctxwarn'):
    for an in T.HEI:
        p = T.dai_path(E + '/dai', key, an)
        for nm, ch in NAMED:
            v = val(nm, ch); rc, so, se = T.hashi(p, v); y = T.yomite(se); t = se.decode('utf-8', 'surrogateescape'); m = re.search(r'「(.*)」', t, re.S); f = m.group(1) if m else ''
            rd = subprocess.run(['/bin/dash', p], capture_output=True, env={'LC_ALL': 'C', 'KM73_TH': v}) if '\x00' not in v else None
            rows.append((dict(T.TGT)[key], an, nm, y['LF'], y['py.splitlines'], y['wc-l'], y['awk-NR'], T.u8(se), kagyaku(an, se, v), len(f.encode('utf-8', 'surrogateescape')), len(f), '変らず' if (nm.startswith('陰性') and f == v) else ('★変る★' if nm.startswith('陰性') else '-'), f'dash rc {rd.returncode} 行 {T.yomite(rd.stderr)["LF"]} {T.esc(rd.stderr)[:60]}' if rd else '-', T.out_of(so), T.esc(f)[:80]))
K.kaku_tsv(E + '/47_hei.tsv', rows, ['生器', '案', '形', 'LF', 'py.splitlines', 'wc-l', 'awk-NR', 'UTF-8', '可逆', '札の値 bytes', '札の値 字', '陰性が変るか', 'dash', 'OUT', '札の値(esc)'])
for an in T.HEI:
    rs = [r for r in rows if r[1] == an]; out.append(f'{an}: 走 {len(rs)} / いづれかの讀手で ≥2 行 {sum(1 for r in rs if max(r[3:7]) >= 2)} / UTF-8 不正 {sum(1 for r in rs if r[7] != "正")} / 可逆「戻る」{sum(1 for r in rs if r[8] == "戻る")} / 陰性が変る {sum(1 for r in rs if r[11] == "★変る★")} / dash で rc≠0 {sum(1 for r in rs if "dash rc 0" not in r[12])} / OUT 99 以外 {sum(1 for r in rs if r[13] != "99")}')
K.kaku(E + '/47_hei.txt', '\n'.join(out)); print('\n'.join(out))
