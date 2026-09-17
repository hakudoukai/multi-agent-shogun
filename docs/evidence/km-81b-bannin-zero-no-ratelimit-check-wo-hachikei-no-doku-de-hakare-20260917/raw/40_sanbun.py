# -*- coding: utf-8 -*-
"""40 ㋓(第77弾 km-81b)―― 受ける口の名を ★三分類★(閾= 數で比べる右項 / 旗= 二値 0|1・true|false・True|False で比べる or `if $名` で実行 / 状態変数= 其の他・process 内で更新)し、
★排他性★を器が言ふ(各名は丁度一つの類・三つの和= 母數)。母數= 10 の 甲(`${NAME:-}` 5 名)∪ 乙(外から値が入る 46 名)・重なりを刷る。
併せて「受けぬ閾」(literal のみ・母數の外)と「數比較器の左項に立つ名」(毒が届く所)を欄で示す。根拠は逐語の行(10_hikakuki.tsv の行番号)。"""
import os, sys, re, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; T = 'scripts/ratelimit_check.sh'
L = open(M + '/' + T, encoding='utf-8').read().split('\n')
uke = [l.split('\t') for l in open(D + '/raw/10_ukeru.tsv', encoding='utf-8').read().split('\n')[1:] if l.startswith('disk\t')]
kou = sorted({r[3] for r in uke if r[1].startswith('甲')}); otsu = sorted({r[3] for r in uke if r[1].startswith('乙')}); hei = sorted({r[3] for r in uke if r[1].startswith('丙')})
assert otsu == open(D + '/raw/10_otsu_disk.txt', encoding='utf-8').read().split(), '乙の名が 10 の出目と違ふ'
bo = sorted(set(kou) | set(otsu)); kasanari = sorted(set(kou) & set(otsu))
hik = [l.split('\t') for l in open(D + '/raw/10_hikakuki.tsv', encoding='utf-8').read().split('\n')[1:] if l.startswith('disk\t')]
NIC = {'"0"', '"1"', '0', '1', 'true', 'false', '"true"', '"false"', '"True"', '"False"', 'True', 'False'}
def uses(nm):
    """比較器表で此の名が左項/右項/case/exec に立つ行を集める(逐語の根拠)。"""
    pat = re.compile(r'\$\{?' + re.escape(nm) + r'(?![A-Za-z0-9_])')
    return [h for h in hik if pat.search(h[2]) or pat.search(h[4])]
def cls(nm):
    us = uses(nm); num_right = [h for h in us if h[5].startswith('數') and re.search(r'\$\{?' + re.escape(nm) + r'\b', h[4])]
    if num_right: return '閾(數比較器の右項)', us
    flag_uses = [h for h in us if (h[3] in ('==', '!=', '=') and h[4] in NIC) or h[5].startswith('変数を命令')]
    if us and len(flag_uses) == len([h for h in us if not h[5].startswith('単項')]) and flag_uses: return '旗(二値で比べる)', us
    return '状態変数(其の他・process 内で更新)', us
rows = ['名\t定義(甲/乙/甲∩乙)\t類\t數比較器の左項に立つ(毒が届く)\t根拠(比較器表の行番号: 左項 演算子 右項)']; tally = {}; seen = {}
LEFT_NUM = {re.sub(r'^"?\$\{?([A-Za-z_][A-Za-z_0-9]*).*$', r'\1', h[2]) for h in hik if h[5].startswith('數')}
for nm in bo:
    c, us = cls(nm); assert nm not in seen; seen[nm] = c; tally[c] = tally.get(c, 0) + 1
    rows.append(f'{nm}\t' + ('甲∩乙' if nm in kasanari else ('甲' if nm in kou else '乙')) + f'\t{c}\t' + ('★立つ★' if nm in LEFT_NUM else '-') + '\t' + ('; '.join(f'L{h[1]} {h[2]} {h[3]} {h[4]}' for h in us) or '(比較器に立たぬ)'))
derived = sorted(LEFT_NUM - set(bo))
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
out = [f'# 40 ㋓ / 刻 {koku} / 的 {T} / 母數= 甲 {len(kou)} ∪ 乙 {len(otsu)} = {len(bo)} 名(重なり {len(kasanari)}: {" ".join(kasanari)})/ 丙(函数引数・母數の外) {len(hei)} 名']
for c in ('閾(數比較器の右項)', '旗(二値で比べる)', '状態変数(其の他・process 内で更新)'): out.append(f'  {c}: {tally.get(c, 0)} 名' + (' = ' + ' '.join(n for n, k in seen.items() if k == c) if tally.get(c, 0) and tally.get(c, 0) <= 8 else ''))
s = sum(tally.values()); out.append(f'★排他性★: 各名は丁度一つの類(assert)・三類の和 {s} ' + ('= 母數 ' + str(len(bo)) + ' ★一致★' if s == len(bo) else '★≠ 母數 ' + str(len(bo)) + '★'))
lit = [(i + 1, l.strip()) for i, l in enumerate(L) if re.match(r'^(CODEX_CONTEXT_WARN|CODEX_CONTEXT_CRIT|CODEX_LIMIT_HITS_WARN)=\d+$', l.strip())]
lit80 = [(i + 1) for i, l in enumerate(L) if re.search(r' -ge 80 ', l)]
out.append(f'母數の外「受けぬ閾」(literal で定まり `${{NAME:-}}` の口を持たぬ): 名 {len(lit)}(' + ' / '.join(f'L{a} {b}' for a, b in lit) + f') + 裸の 80 ×{len(lit80)}(L{",".join(map(str, lit80))}) ―― ∴ ★閾の類が 0 名なのは「閾が無い」のではなく「閾が口を持たぬ」から★。')
out.append(f'數比較器の左項に立つ名(毒が届く所) {len(LEFT_NUM)}= ' + ' '.join(sorted(LEFT_NUM)) + f' / 内 母數に在る {len(LEFT_NUM & set(bo))}({" ".join(sorted(LEFT_NUM & set(bo)))})・母數の外の派生/内部 {len(derived)}({" ".join(derived)}: fh_int/sd_int は乙 CLAUDE_5H/7D_UTIL の `%.*` 派生・count/#/配列長は内部)')
out.append('分類の則(器が決める): 閾= 數比較器の右項に立つ / 旗= 立つ比較器が悉く二値 literal(0|1・true|false・True|False)との字面比較か `if $名` の実行 / 状態変数= 残り。單項(-n/-z/-f/-x)は類の根拠にせぬ。')
out.append('此の器が意味せぬ事: 「状態変数」は「毒が効かぬ」の意ではない(30 の P1-P5 の左項は悉く状態変数の類)。類は「番人の形」を決める為の分類であり(閾→數の番人・旗→case の番人・状態→出所の番人)、害の有無は 30 で測る。')
K.kaku(D + '/raw/40_sanbun.txt', '\n'.join(out)); K.kaku(D + '/raw/40_sanbun.tsv', '\n'.join(rows)); print('\n'.join(out)); print('\n'.join(rows))
