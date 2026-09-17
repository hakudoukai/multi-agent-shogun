# -*- coding: utf-8 -*-
"""35 ㋕ 直し形は紙にのみ(第79弾 km-86)―― 案五つ(A 空を拒む / B 正規化+根の内 / C 字類の禁 / D 存在・往復の確認 / E 許容集合)の
「塞ぐ毒 / 塞がぬ毒 / 偽陽性の見積」を ★repo の今の既定と讀手から数へる★(据ゑぬ・提案のみ)。
偽陽性の見積= 其の案を今の口に当てた時、★今 repo が宣として持つ既定★ が拒まれる口の數(既定が拒まれる= 案が正当な値を拒む証)。
問「名は許容集合でしか守れぬのか」= B/C/D は許容集合(名の列挙)でなく、各々 ≥1 の毒を塞ぐ ⇒ 反例。表 10 毒 × 5 案。"""
import os, sys, re, time, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
na = [l.split('\t') for l in open(D + '/raw/10_na.tsv', encoding='utf-8').read().split('\n')[1:] if l]
r20 = [l.split('\t') for l in open(D + '/raw/20_shimo.tsv', encoding='utf-8').read().split('\n')[1:] if l]
rx = [l.split('\t') for l in open(D + '/raw/20_cross.tsv', encoding='utf-8').read().split('\n')[1:] if l]
POIS = ['空文字', '空白のみ', '全角空白', ';入り', '$(…)入り', '改行入り', '..入り', '絶対path', '在らぬ名', '256字超']
def strip_q(s): s = s.strip(); return s[1:-1] if len(s) >= 2 and s[0] == s[-1] and s[0] in '\'"' else s
defaults = [(r[0], r[2], strip_q(r[5]) if r[5] != '(空)' else '', r[3], r[4], r[7]) for r in na]
empty = [d for d in defaults if d[2] in ('', '(無)', '(必須)')]
# 案A 空を拒む(`${X:-d}`→`${X:?}` / 空なら止まる): 偽陽性= 既定が空の口の内、同 file が -z/-n で空を扱ふ(空= 未設定の意で正当)物
SRC = {}
def src(f):
    if f not in SRC: SRC[f] = open(M + '/' + f, encoding='utf-8', errors='replace').read().split('\n')
    return SRC[f]
a_fp = [d for d in empty if any(re.search(r'-[nz]\s+"?\$\{?' + re.escape(d[1]) + r'(?![A-Za-z0-9_])', l) for l in src(d[0]) if not l.lstrip().startswith('#'))]
# 案B 正規化(realpath)+根の内(repo 根 or $HOME の下): 偽陽性= 既定が path で repo 根の外を指す物
OUT = ('/tmp', '/var', '/usr', '/opt', '/etc', '/private', '/dev', '/Applications', '/System', '/Library')
paths = [d for d in defaults if d[5] == '既定が path']
b_fp = [d for d in paths if d[2].startswith(OUT) or d[2].startswith('~') or d[2].startswith('$HOME') or d[2].startswith('${HOME')]
b_home = [d for d in paths if d[2].startswith('~') or d[2].startswith('$HOME') or d[2].startswith('${HOME')]
# 案C 字類の禁(空白のみ・全角空白・制御/改行・; ・$( ・256 超・先頭 -): 偽陽性= 今の既定が其の字を含む物
BAD = re.compile(r'[\x00-\x1f;　]|\$\(|^\s*$|^-')
c_fp = [d for d in defaults if d[2] not in ('(無)', '(必須)') and (BAD.search(d[2]) or len(d[2]) > 255) and d[2] != '']
c_sp = [d for d in defaults if ' ' in d[2] and d[2] not in ('(無)', '(必須)')]
# 案D 存在・往復の確認(tmux display-message -t X が通る / [ -e ] / 往復で同じ名): 偽陽性= 0(動的)。今の repo での慣行= ⑴ の讀手の前 8 行に has-session/display-message の検めが在る行
h1 = [r for r in r20 if r[3] == '⑴'] + [(r[2], r[3], r[1], r[4], r[5], r[6]) for r in rx if r[4] == '⑴']
d_prac = 0
for r in h1:
    f, ln = r[0], int(r[1]); L = src(f)
    if any(re.search(r'tmux\s+(has-session|display-message|list-panes)', L[k]) for k in range(max(0, ln - 9), ln - 1)): d_prac += 1
# 案E 許容集合(roster): ⑷= queue/inbox/<名>.yaml の存在 / ⑴⑵= queue/pane_registry.yaml に名が在る
roster = {p[:-5] for p in os.listdir(M + '/queue/inbox') if p.endswith('.yaml')}
h4 = [r for r in r20 if r[3] == '⑷']
reg = M + '/queue/pane_registry.yaml'; regtxt = open(reg, encoding='utf-8').read() if os.path.exists(reg) else ''
e4 = []   # ⑷ の口の既定(役職名)が roster に在るか
for d in defaults:
    if d[5].startswith('既定が語') and re.fullmatch(r'[a-z][a-z0-9-]*', d[2]):
        if any(r[0] == d[0] and r[2] == d[1] and r[3] == '⑷' for r in r20): e4.append((d, d[2] in roster))
e4_out = [x for x in e4 if not x[1]]
e1 = [(d, (d[2] in regtxt)) for d in defaults if re.fullmatch(r'[A-Za-z0-9_-]+:[A-Za-z0-9_.]+', d[2])]
e1_out = [x for x in e1 if not x[1]]
# 直に inbox_write.sh を呼ぶ行の第一引数(字面)が roster に在るか(根A)
rootA = [l for l in open(D + '/raw/00_rootA.txt', encoding='utf-8').read().split('\n') if l]
lit = collections.Counter(); lit_out = collections.Counter()
for f in rootA:
    for l in src(f):
        if l.lstrip().startswith('#'): continue
        m = re.search(r'(?:^|[\s;(])(?:bash\s+|sh\s+|\./|\$[A-Za-z_{][^\s]*/|/)\S*inbox_write\.sh"?\s+([a-z][a-z0-9-]*)\s', l)   # ★二走: 呼出の形(bash …/inbox_write.sh <役職>)のみ・文の中の語(not/shell/path…)を除く
        if m: lit[m.group(1)] += 1; lit_out[m.group(1)] += (m.group(1) not in roster)
# 甲/乙: `${X-D}`→`${X:-D}` は空文字のみ塞ぐ(根A に乙 0 ゆゑ当てる口 0)
table = {
 'A 空を拒む(:? / 空なら止まる)':        {'空文字': '塞ぐ', '空白のみ': '塞がぬ(非空)', '全角空白': '塞がぬ', ';入り': '塞がぬ', '$(…)入り': '塞がぬ', '改行入り': '塞がぬ', '..入り': '塞がぬ', '絶対path': '塞がぬ', '在らぬ名': '塞がぬ', '256字超': '塞がぬ'},
 'B 正規化+根の内(realpath ⊂ 根)':      {'空文字': '塞ぐ(根=空→根そのもの≠内)', '空白のみ': '塞ぐ(在らぬ)', '全角空白': '塞ぐ(在らぬ)', ';入り': '塞ぐ(在らぬ)', '$(…)入り': '塞ぐ(在らぬ)', '改行入り': '塞ぐ(在らぬ)', '..入り': '塞ぐ', '絶対path': '塞ぐ', '在らぬ名': '塞ぐ(在らぬ)', '256字超': '塞ぐ(在らぬ)'},
 'C 字類の禁(空白/制御/;/$(/256/先頭-)': {'空文字': '塞ぐ', '空白のみ': '塞ぐ', '全角空白': '塞ぐ', ';入り': '塞ぐ', '$(…)入り': '塞ぐ', '改行入り': '塞ぐ', '..入り': '★塞がぬ★', '絶対path': '★塞がぬ★', '在らぬ名': '★塞がぬ★', '256字超': '塞ぐ'},
 'D 存在・往復の確認(has-session/-e/往復)': {'空文字': '塞ぐ(往復で別名)', '空白のみ': '塞ぐ', '全角空白': '塞ぐ', ';入り': '塞ぐ', '$(…)入り': '塞ぐ', '改行入り': '塞ぐ', '..入り': '塞ぐ(在らねば)/★塞がぬ(在れば)★', '絶対path': '同左', '在らぬ名': '塞ぐ', '256字超': '塞ぐ'},
 'E 許容集合(roster/registry)':          {p: '塞ぐ' for p in POIS},
}
out = [f'# 35 ㋕ 直し形(紙にのみ・据ゑず) / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 名の口 {len(na)} / 既定空 {len(empty)} / 既定が path {len(paths)}',
       '## 案 × 毒(塞ぐ/塞がぬ)'] + [f'  {k}\t' + '\t'.join(f'{p}={v[p]}' for p in POIS) for k, v in table.items()]
out += ['## 偽陽性の見積(今 repo の既定・讀手を其の案に当てた數= 正当な値が拒まれる證)',
        f'  A 空を拒む: 既定が空の名の口 {len(empty)} の内、同 file が -z/-n で「空= 未設定」と扱ふ口 ★{len(a_fp)}★(之は空が正当ゆゑ A は偽陽性)。残り {len(empty) - len(a_fp)} は空が下流へ行く(⑶ なら根へ・30 の 124 走)。例: ' + ' / '.join(f'{d[0].split("/")[-1]}:{d[1]}' for d in a_fp[:8]),
        f'  B 正規化+根の内: 既定が path の口 {len(paths)} の内、repo 根の外(/tmp /var /usr /opt /etc /private・$HOME・~)を宣で指す口 ★{len(b_fp)}★(内 $HOME/~ {len(b_home)})= 根を repo に限れば之が偽陽性 → 根は「repo ∪ $HOME ∪ /tmp」の集合で宣する要。例: ' + ' / '.join(f'{d[0].split("/")[-1]}:{d[1]}={d[2][:30]}' for d in b_fp[:8]),
        f'  C 字類の禁: 今の既定に禁の字(制御/改行/;/$(/全角空白/256 超/先頭 -)を含む口 ★{len(c_fp)}★(0 なら偽陽性 0)/ 空白を含む既定 {len(c_sp)}(空白を禁に入れれば偽陽性)。例: ' + (' / '.join(f'{d[0].split("/")[-1]}:{d[1]}={d[2][:30]!r}' for d in (c_fp or c_sp)[:6]) or '0'),
        f'  D 存在・往復: 偽陽性 0(動的・名を列挙せぬ)。★塞がぬ形= 在る別の pane/file への誤配★(往復も通る)。今の慣行: ⑴ の讀手 {len(h1)} 行の内、前 8 行に has-session/display-message/list-panes の検めが在る ★{d_prac}★ 行(enter_restart_common_watchdog.sh L180 の形)。',
        f'  E 許容集合: ⑷ の口の既定(役職名)を queue/inbox/<名>.yaml の roster({len(roster)} 箱)に当てると 在らぬ ★{len(e4_out)}/{len(e4)}★(之は「既定が死箱を指す」= 偽陽性でなく★宣の腐り★・inbox_write.sh の IW_DEAD の柵が之を止める): ' + (' / '.join(f'{d[0].split("/")[-1]}:{d[1]}={d[2]}' for d, ok in e4_out[:10]) or '0'),
        f'    ⑴⑵ の既定(pane target 形 `s:w.p`)を queue/pane_registry.yaml({"在" if regtxt else "無"})に当てると 在らぬ ★{len(e1_out)}/{len(e1)}★: ' + (' / '.join(f'{d[0].split("/")[-1]}:{d[1]}={d[2]}' for d, ok in e1_out[:10]) or '0'),
        f'    inbox_write.sh を直に呼ぶ行の第一引数(字面・根A)= {sum(lit.values())} 行 / 異なり {len(lit)}: ' + ' / '.join(f'{k}×{v}' + ('(★箱無し★)' if lit_out[k] else '') for k, v in lit.most_common()),
        '## 問「名は許容集合でしか守れぬのか」の答(反例)',
        '  反例 B= 正規化+根の内: 名を列挙せず「根の下に在るか」で 10 毒中 10 を塞ぐ(path の類のみ・tmux/topic には効かぬ)。',
        '  反例 C= 字類の禁: 名を列挙せず 10 毒中 7 を塞ぐ(.. / 絶対 / 在らぬ名 は字類で見分けられぬ= ★字類の番人の限界★)。',
        '  反例 D= 存在・往復: 名を列挙せず 10 毒中 9〜10 を塞ぐ(在る別名への誤配のみ塞がぬ)。',
        '  ∴ 許容集合(E)は「在る別名への誤配」を塞ぐ唯一の形だが、偽陽性= 宣の腐り(既定が roster に無い)が今 ★' + str(len(e4_out)) + '★ 口在り、E を据ゑれば之が鳴る(鳴るのが正)。',
        '  乙→甲(`${X-D}`→`${X:-D}`)は空文字のみ塞ぐ。根A に乙は 0 ゆゑ当てる口 0(python get の 96 口は乙と同じ振舞ひ・空文字を素通し)。',
        '## 案の順(見立て・据ゑるは家老の裁の後): 口の直後に C(字類)→ 類別に B(path)/D(tmux・箱)→ E は roster の在る ⑷ のみ。A は -z/-n で空を扱ふ口 ' + str(len(a_fp)) + ' を除いて当てる。']
K.kaku(D + '/raw/35_naoshi.txt', '\n'.join(out)); print('\n'.join(out))
