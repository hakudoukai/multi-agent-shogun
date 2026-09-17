# -*- coding: utf-8 -*-
"""10 ―― 定義甲(fix_threshold の呼出)・乙(定義を持つ file)・丙(「既定へ倒す/fail-closed」の文言)を ★別々の表★ で数へる。disk と HEAD 6ba8fcb2 を併記。読取のみ。"""
import sys, re
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from gg import gg, fuda, koku, HEAD, is_comment
T = []
# ---- 甲 ----
RE_ANY = r'fix_threshold'; RE_DEF = r'^fix_threshold\(\)\{'
rows_k = []; sum_k = []
for rev in (None, HEAD):
    tag = 'disk' if rev is None else 'HEAD'
    allr, rc, argv = gg(RE_ANY, rev); calls = []; defs = []; cmts = []
    for path, no, text in allr:
        if re.match(RE_DEF, text): defs.append((path, no)); kind = 'def'
        elif is_comment(text): cmts.append((path, no)); kind = 'comment'
        elif re.match(r'^\s*fix_threshold\s+', text):
            a = text.split('#')[0].split()
            if a[1].startswith('"$'): kind = 'call(loop)'; names = '★loop 変数(list は上の for 行)★'
            else: kind = 'call'; names = a[1]
            calls.append((path, no, kind, names)); rows_k.append((tag, path, no, kind, names, text.strip()[:90]))
        else: kind = 'other'; rows_k.append((tag, path, no, kind, '-', text.strip()[:90]))
    # loop の list(inbox_watcher: for _t in NAME:既定 …)
    # ★.first の疵★: git grep の ERE に \s は無く(macOS regcomp)、for の續き行 2 本を落として loop list が 3 に縮んだ。→ file 本文を讀んで `for _t in` から `; do` までを取る。
    import subprocess
    src = open('/Users/momizimac/multi-agent-shogun/scripts/inbox_watcher.sh', encoding='utf-8').read() if rev is None else subprocess.run(['git', 'show', f'{rev}:scripts/inbox_watcher.sh'], capture_output=True, cwd='/Users/momizimac/multi-agent-shogun').stdout.decode('utf-8', 'replace')
    m = re.search(r'^for _t in (.*?); do$', src, re.S | re.M); assert m, 'for _t in が無い'
    loopn = sorted(set(w.split(':')[0] for w in m.group(1).replace('\\\n', ' ').split() if ':' in w))
    files = sorted(set(p for p, *_ in calls))
    sum_k.append(f'[{tag}] git grep rc {rc} / 総 {len(allr)} 行 = 定義 {len(defs)} + 呼出行 {len(calls)}(内 loop 行 {sum(1 for c in calls if c[2]=="call(loop)")}) + 註 {len(cmts)} + 他 {len(allr)-len(defs)-len(calls)-len(cmts)} / 呼出行の file {len(files)} / ★守る名= 明示 {sum(1 for c in calls if c[2]=="call")} + loop list {len(loopn)} = {sum(1 for c in calls if c[2]=="call") + len(loopn)}★ / loop list= {" ".join(loopn)}')
    sum_k.append(f'  器の逐語: {argv}')
K.kaku_tsv(D + '/raw/10_kou.tsv', rows_k, ['rev', 'path', 'line', 'kind', 'name', 'text'])
K.kaku(D + '/raw/10_kou.txt', f'# 10 定義甲 fix_threshold の呼出 / 刻 {koku()} / 根= scripts .claude(git 追跡 file 全深・archive/ 含む) / 條= 行頭空白+fix_threshold+空白 を呼出・^fix_threshold(){{ を定義・# 起しを註\n' + '\n'.join(sum_k) + '\n零の札:\n' + '\n'.join(fuda(RE_ANY)))
# ---- 乙 ----
rows_o = []; sum_o = []
for rev in (None, HEAD):
    tag = 'disk' if rev is None else 'HEAD'; r, rc, argv = gg(RE_DEF, rev)
    for path, no, text in r: rows_o.append((tag, path, no))
    sum_o.append(f'[{tag}] rc {rc} / 定義を持つ file ★{len(set(p for p,_,_ in r))}★(行 {len(r)}) / 逐語: {argv}')
K.kaku_tsv(D + '/raw/20_otsu.tsv', rows_o, ['rev', 'path', 'line'])
K.kaku(D + '/raw/20_otsu.txt', f'# 20 定義乙 fix_threshold() の定義を持つ file / 刻 {koku()} / 根= 同上 / 條= ^fix_threshold(){{\n' + '\n'.join(sum_o) + '\n零の札:\n' + '\n'.join(fuda(RE_DEF)))
# ---- 丙 ----
RE_H = r'既定[^ 	]{0,8}へ倒す|fail-closed'
rows_h = []; sum_h = []
for rev in (None, HEAD):
    tag = 'disk' if rev is None else 'HEAD'; r, rc, argv = gg(RE_H, rev); per = {}
    for path, no, text in r:
        kind = '註' if is_comment(text) else ('文字列(_th_say/say/echo)' if re.search(r'_th_say|\bsay\b|echo|printf|log\(|log ', text) else '他')
        per.setdefault(path, [0, 0, 0]); per[path][0] += 1; per[path][1 if kind == '註' else 2] += 1
        rows_h.append((tag, path, no, kind, text.strip()[:100]))
    sum_h.append(f'[{tag}] rc {rc} / 行 {len(r)} / ★file {len(per)}★ / archive/ 除く file {len([p for p in per if "/archive/" not in p])} / 逐語: {argv}')
    for p, (n, c, s) in sorted(per.items()): sum_h.append(f'    {p} 行 {n}(註 {c}・文字列/他 {s})')
K.kaku_tsv(D + '/raw/30_hei.tsv', rows_h, ['rev', 'path', 'line', 'kind', 'text'])
K.kaku(D + '/raw/30_hei.txt', f'# 30 定義丙 「既定へ倒す」/「fail-closed」の文言 / 刻 {koku()} / 根= 同上 / 條= ERE 「既定[^ \\t]{{0,8}}へ倒す|fail-closed」(1 行 1 ―― 一行に二度出ても 1)\n' + '\n'.join(sum_h) + '\n零の札:\n' + '\n'.join(fuda(RE_H)))
for f in ('10_kou', '20_otsu', '30_hei'): print(open(D + f'/raw/{f}.txt', encoding='utf-8').read())
