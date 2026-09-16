# -*- coding: utf-8 -*-
"""㋐ 第67弾 ㋓ の引き直し 21(第68弾)―― 讀手 verify.py を ★版刻器 20 の Han.module() を通してのみ★ 走らせ、settrace の行番号を ★走らせた其の bytes★ の行本文へ引き当てる。
的 = 第67弾の mini 臺帳 26 本(km-67 raw/otsu1/lines/・錠の下・讀むのみ)。第67弾の otsu1_genbutsu.tsv(讀むのみ)の A/B/C 落ちる行と一本づつ突き合はせ、139/133/152→158 が同じ数で出るかを數へる。
出目 = raw/21_otsu1.txt + raw/21_otsu1.tsv。讀むのみ(他席・前弾の束へ 0 byte)。"""
import os, sys, re, io, time, contextlib, collections, hashlib
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K; import importlib.util as _iu
_sp = _iu.spec_from_file_location('hanban', E + '/20_hanban.py'); H = _iu.module_from_spec(_sp); _sp.loader.exec_module(H)  # 数字始まりの名は import 文で読めぬ故
M = '/Users/momizimac/multi-agent-shogun'; R = M + '/queue/reports'; VP = M + '/scripts/checks/karo_mac_manifest_verify.py'
W = M + '/.claude/worktrees/karo-mac-a1'; B67 = W + '/docs/evidence/km-67-mon-no-ato-20260917'; LINES = B67 + '/raw/otsu1/lines'; TSV67 = B67 + '/raw/otsu1_genbutsu.tsv'
TERM = {133: 'continue', 139: 'unreadable += 1', 152: 'miss += 1', 158: 'ok += 1', 160: 'ng += 1'}
# ★走らせる直前に版を刻む★ ―― 此の Han の bytes だけが走り、行本文も此の bytes から引く
han, fuda = H.sono_mae_ni(VP, sorted(TERM), against=W + '/scripts/checks/karo_mac_manifest_verify.py')
V = han.module('kv')
# ★行番号 → 本文 の引き当てを走らせる bytes で検める★(讀んだ版が違へば此処で落ちる)
kizu_line = [(n, han.line(n).strip()) for n in TERM if TERM[n] not in han.line(n)]
rows67 = [l.rstrip('\n').split('\t') for l in open(TSV67, encoding='utf-8')][1:]; assert len(rows67) == 26, len(rows67)
def run_reader(mini, bases):
    hits = []
    def tr(frame, ev, arg):
        if frame.f_code.co_filename == han.path:
            if ev == 'line': hits.append(frame.f_lineno)
            return tr
        return None
    buf = io.StringIO(); cwd = os.getcwd(); os.chdir(M)
    try:
        sys.settrace(tr)
        with contextlib.redirect_stdout(buf): rc = V.main([VP, mini] + bases)
    finally: sys.settrace(None); os.chdir(cwd)
    term = [h for h in hits if h in TERM]; s = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', buf.getvalue())
    return (term[-1] if term else 0), rc, (f'{s.group(1)}/{s.group(2)}/{s.group(3)}/{s.group(4)}' if s else '?'), (int(s.group(5)) if s else -1), len(hits)
out_rows = []; hdr = ('山', '臺帳(紙)', '臺帳の行', 'mini', '實體', '67:A', '68:A', '同A', '67:B', '68:B', '同B', '67:C', '68:C', '同C', '68 出目A', '68 出目B', '68 母數A', '68 本文(落ちる行・走らせた bytes)')
for r in rows67:
    yama, paper, n, rel = r[0], r[1], int(r[2]), r[4]; stem = paper[:-3]; ev = f'{R}/{stem}_evidence'
    short = re.sub(r'^ashigaru-mac-\d_|^karo_mac_|_2026\d+$', '', stem); mini = f'{LINES}/{short}_L{n:02d}.txt'; assert os.path.isfile(mini), mini
    sub = rel.split('/')[0] if '/' in rel and rel.split('/')[0] in ('raw', 'kizai') else ''
    A = run_reader(mini, ['']); Bb = run_reader(mini, [ev + '/']); C = run_reader(mini, [f'{ev}/{sub}/']) if sub else ('=B', Bb[1], Bb[2], Bb[3], 0)
    a67, b67, c67 = r[9], r[11], r[13]
    out_rows.append((yama, paper, n, os.path.basename(mini), rel, a67, A[0], a67 == str(A[0]), b67, Bb[0], b67 == str(Bb[0]), c67, C[0], c67 == str(C[0]), A[2], Bb[2], A[3], han.line(A[0]).strip() if isinstance(A[0], int) and A[0] else '-'))
K.kaku_tsv(E + '/21_otsu1.tsv', out_rows, hdr)
cA68 = collections.Counter((r[0], r[6]) for r in out_rows); cA67 = collections.Counter((r[0], r[5]) for r in out_rows); cB68 = collections.Counter((r[0], r[9]) for r in out_rows); cB67 = collections.Counter((r[0], r[8]) for r in out_rows)
same = sum(1 for r in out_rows if r[7] and r[10] and r[13]); diff = [r for r in out_rows if not (r[7] and r[10] and r[13])]
def cnt(c): return ' / '.join(f'{k[0]}→{k[1]}: {v} 本' for k, v in sorted(c.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))))
out = [f'# 21 ㋐ 第67弾 ㋓ の引き直し(版刻器 20 越し) / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 的 mini 臺帳 {len(out_rows)} 本(km-67 raw/otsu1/lines/・讀むのみ)/ 第67弾の tsv {os.path.relpath(TSV67, W)}(讀むのみ)'] + fuda
out += [f'## 行番号→本文 の検め(走らせた bytes で): {"悉く合ふ" if not kizu_line else "★合はぬ " + str(kizu_line) + "★"} ―― ' + ' / '.join(f'L{n}={TERM[n]!r}' for n in sorted(TERM)),
        f'## 落ちる行の本数 A 基点 ""(cwd main 樹): 第67弾 {cnt(cA67)} ‖ 本弾(20 越し) {cnt(cA68)}',
        f'## 落ちる行の本数 B 基点 <紙>_evidence/: 第67弾 {cnt(cB67)} ‖ 本弾(20 越し) {cnt(cB68)}',
        f'## 一本づつ A/B/C 悉く同じ {same} / 違ふ {len(diff)} / 母數 {len(out_rows)}']
for r in diff: out.append(f'  ★違ふ★ {r[0]} {r[1]} L{r[2]} 67:{r[5]}/{r[8]}/{r[11]} 68:{r[6]}/{r[9]}/{r[12]}')
n = lambda k, v: sum(1 for r in out_rows if r[0] == k and r[6] == v)
out.append(f'## 結: 乙1 139 = {n("乙1", 139)} / 乙1 133 = {n("乙1", 133)} / 乙5 152(A) = {n("乙5", 152)} / 乙5 158(B) = {sum(1 for r in out_rows if r[0] == "乙5" and r[9] == 158)} ―― 第67弾は 19/4/3/3。{"★同じ数で出た★" if (n("乙1", 139), n("乙1", 133), n("乙5", 152), sum(1 for r in out_rows if r[0] == "乙5" and r[9] == 158)) == (19, 4, 3, 3) else "★違ふ数が出た★"}。同じ数が出た事も「器を通して初めて言へる」―― 第67弾の二走目は行番号を手(cat -n)で置き、本弾は走らせた bytes から引いた(版札の封が其れを縛る)。')
K.kaku(E + '/21_otsu1.txt', '\n'.join(out)); print('\n'.join(out))
sys.exit(0 if not diff and not kizu_line else 1)
