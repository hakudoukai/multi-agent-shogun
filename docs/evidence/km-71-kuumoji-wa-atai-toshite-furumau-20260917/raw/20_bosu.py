# -*- coding: utf-8 -*-
"""20 母數の檢出子(第71弾 ㋐㋒㋓)―― 己の束の .py を AST で歩き、★長さ0の文字列が判定に効き得る箇所★を形で数へる。
形: A 包含 in(Compare In/NotIn・右が str 定数)/ B 等価(Compare Eq/NotEq・何れかが '' 定数)/ C 既定落ち or(BoolOp Or・末尾が定数)/
    D 真偽(If/While/IfExp/内包 の test が裸の Name/Subscript/Attribute/Call か其の not)/ E 三項の既定(IfExp の orelse が定数)/ F startswith|endswith('')。
歩き根 = km-70 束・自主束・km-71 束(己)。深さ = 無限(os.walk)。規約 = S_ISREG かつ .py。非通常・非 .py は別に数へる。fixture/ は同じ路で歩き ★現物と分けて★数へる(陽性 pos.py / 陰性 neg.py)。
己(20_bosu.py)は歩かれるが「自身」として別に札する(字面でなく path の一致)。零には四つの札(陽性対照・根と深さ・rc・刻)。"""
import os, sys, ast, stat, time, hashlib, collections
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; SELF = os.path.abspath(__file__)
ROOTS = [M + '/docs/evidence/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917', M + '/docs/evidence/a1-jishu-kuumoji-kiten-20260917', D]
def is_const_str(n): return isinstance(n, ast.Constant) and isinstance(n.value, str)
def is_empty(n): return isinstance(n, ast.Constant) and n.value == ''
def bare(n): return isinstance(n, (ast.Name, ast.Subscript, ast.Attribute, ast.Call))
def sites(tree, src):
    out = []
    def seg(n): return (ast.get_source_segment(src, n) or '').replace('\n', ' ')[:70]
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare):
            for op, comp in zip(n.ops, n.comparators):
                if isinstance(op, (ast.In, ast.NotIn)) and is_const_str(comp): out.append(('A', n.lineno, seg(n), 'high' if isinstance(n.left, ast.Subscript) and isinstance(n.left.slice, ast.Slice) else 'low'))
                if isinstance(op, (ast.Eq, ast.NotEq)) and (is_empty(comp) or is_empty(n.left)): out.append(('B', n.lineno, seg(n), 'low'))
        elif isinstance(n, ast.BoolOp) and isinstance(n.op, ast.Or) and isinstance(n.values[-1], ast.Constant) and any(bare(v) for v in n.values[:-1]): out.append(('C', n.lineno, seg(n), 'low'))
        elif isinstance(n, (ast.If, ast.While, ast.IfExp)):
            t = n.test; tt = t.operand if isinstance(t, ast.UnaryOp) and isinstance(t.op, ast.Not) else t
            if bare(tt): out.append(('D', n.lineno, seg(t), 'low'))
            if isinstance(n, ast.IfExp) and isinstance(n.orelse, ast.Constant): out.append(('E', n.lineno, seg(n), 'low'))
        elif isinstance(n, ast.comprehension):
            for t in n.ifs:
                tt = t.operand if isinstance(t, ast.UnaryOp) and isinstance(t.op, ast.Not) else t
                if bare(tt): out.append(('D', t.lineno, seg(t), 'low'))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ('startswith', 'endswith') and n.args and is_empty(n.args[0]): out.append(('F', n.lineno, seg(n), 'high'))
    return out
rows = [('束', 'file', '種', '行', '形', '危', '逐語')]; per_file = []; hi_non = collections.Counter(); nonpy = collections.Counter(); N = collections.Counter(); Mcnt = collections.Counter(); byform = collections.Counter(); fx = collections.Counter(); parse_fail = []
for root in ROOTS:
    tab = os.path.basename(root)
    for r, ds, fs in os.walk(root):
        ds[:] = [x for x in ds if x != '__pycache__']
        for f in sorted(fs):
            q = os.path.join(r, f); rel = os.path.relpath(q, root)
            if not stat.S_ISREG(os.lstat(q).st_mode): hi_non[tab] += 1; continue
            if not f.endswith('.py'): nonpy[tab] += 1; continue
            kind = 'fixture' if '/fixture/' in q else ('自身' if os.path.abspath(q) == SELF else '現物'); N[(tab, kind)] += 1
            try: src = open(q, encoding='utf-8').read(); tree = ast.parse(src)
            except Exception as e: parse_fail.append((tab, rel, str(e)[:60])); continue
            ss = sites(tree, src); per_file.append((tab, kind, rel, len(ss)))
            for form, ln, s, risk in ss:
                rows.append((tab, rel, kind, ln, form, risk, s))
                if kind == 'fixture': fx[(f, form)] += 1
                else: Mcnt[(tab, kind)] += 1; byform[(kind, form)] += 1
K.kaku_tsv(RAW + '/20_bosu.tsv', rows[1:], header=rows[0])
n_gen = sum(v for (t, k), v in N.items() if k == '現物'); n_self = sum(v for (t, k), v in N.items() if k == '自身'); n_fx = sum(v for (t, k), v in N.items() if k == 'fixture')
m_gen = sum(v for (t, k), v in Mcnt.items() if k == '現物'); m_self = sum(v for (t, k), v in Mcnt.items() if k == '自身')
FORMS = 'ABCDEF'; pos_hit = {f: fx[('pos.py', f)] for f in FORMS}; neg_hit = {f: fx[('neg.py', f)] for f in FORMS}
pos_ok = all(pos_hit[f] >= 1 for f in FORMS); neg_ok = all(neg_hit[f] == 0 for f in FORMS)
out = [f'# 20 母數 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 檢出子 sha16 {hashlib.sha256(open(SELF, "rb").read()).hexdigest()[:16]} / python {sys.version.split()[0]}',
       '## 数へ方: 歩き根 = ' + ' / '.join(os.path.relpath(r, M) for r in ROOTS) + ' / 深さ 無限(os.walk・__pycache__ は降りぬ)/ 規約 = S_ISREG かつ名が .py で終はる / 非通常(symlink 等)と非 .py は別に数へ母數に入れぬ / fixture/ 配下は同じ路で歩き現物と分ける / 己(20_bosu.py)は path 一致で「自身」と札し現物から外す',
       f'## ★N(器・現物)= {n_gen} 本★(自身 {n_self} 本・fixture {n_fx} 本は別) / 非通常 {sum(hi_non.values())} / 非 .py {sum(nonpy.values())} / parse 失敗 {len(parse_fail)} {parse_fail}',
       f'## ★M(長さ0の文字列が判定に効き得る箇所・現物)= {m_gen} 箇所★(自身 {m_self} 箇所は別)',
       '## 束別 N / M(現物): ' + ' / '.join(f'{t} N {N[(t, "現物")]} M {Mcnt[(t, "現物")]}' for t in [os.path.basename(r) for r in ROOTS]),
       '## 形別 M(現物): ' + ' / '.join(f'{f} {byform[("現物", f)]}' for f in FORMS) + f' / 内 危=high(形A の左が slice・形F) {sum(1 for r in rows[1:] if r[2] == "現物" and r[5] == "high")}',
       '## 形の名: A 包含 in(右が str 定数)/ B 等価 ==,!= と \'\' / C 既定落ち x or 定数 / D 真偽 if x, if not x(裸)/ E 三項 … if m else 定数 / F startswith|endswith(\'\')',
       f'## ★陽性対照 fixture/pos.py★ 形別 拾つた数 {pos_hit} → {"★悉く拾つた★" if pos_ok else "★拾へぬ形あり★"} / ★陰性対照 fixture/neg.py★ 形別 {neg_hit} → {"★一つも拾はず★" if neg_ok else "★誤つて拾つた★"}',
       f'## 零の札: 陽性対照 {"通" if pos_ok else "落"} / 根と深さ 上記 / rc {0 if (pos_ok and neg_ok) else 1} / 刻 上記',
       '## file 別(束 / 種 / file / 箇所):'] + [f'  {t} / {k} / {rel} / {c}' for t, k, rel, c in per_file]
K.kaku(RAW + '/20_bosu.txt', '\n'.join(out)); print('\n'.join(out[:10])); print('... file 別', len(per_file), '行 / tsv', len(rows) - 1, '行')
sys.exit(0 if (pos_ok and neg_ok) else 1)
