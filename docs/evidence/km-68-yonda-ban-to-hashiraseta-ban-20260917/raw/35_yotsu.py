# -*- coding: utf-8 -*-
"""㋓ 兩席の器が同じ四數を出すか 35(第68弾)―― 專任3 の 71_yotsu.py(main 樹 docs/evidence/km-47-yotsu-no-kazu-20260917/ki/・讀む・走らせるのみ・-B・彼の束へ 0 字)の fuda を、
--kikai main 樹 verify.py で 第67弾の mini 臺帳 26 本(乙1 19+4 = 23 が的・乙5 3 は併せて)に掛け、四数札v1(母數/一致/相違/実体無/讀めぬ行+封)を採る。基点 A = ""(cwd main 樹)/ B = <紙>_evidence/。
己の 21(settrace の落ちる行)と一本づつ突き合はせる ―― 対応: 139↔讀めぬ行=1 / 133↔母數=0 / 152↔実体無=1 / 158↔一致=1 / 160↔相違=1。割れたら「どちらの器が何を数へて居らぬか」を一行。
加へて 71 の --jikenme(彼の陽性/負対照)を走らせ rc を採る。出目 raw/35_yotsu.txt + .tsv。"""
import os, sys, re, subprocess, time, hashlib
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; R = M + '/queue/reports'; VP = M + '/scripts/checks/karo_mac_manifest_verify.py'; Y71 = M + '/docs/evidence/km-47-yotsu-no-kazu-20260917/ki/71_yotsu.py'
W = M + '/.claude/worktrees/karo-mac-a1'; B67 = W + '/docs/evidence/km-67-mon-no-ato-20260917'; LINES = B67 + '/raw/otsu1/lines'
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
rows21 = [l.rstrip('\n').split('\t') for l in open(E + '/21_otsu1.tsv', encoding='utf-8')][1:]; assert len(rows21) == 26
FUDA = re.compile(r'四数札v1 母數=(\d+) 一致=(\d+) 相違=(\d+) 実体無=(\d+) 讀めぬ行=(\d+) 和検=(\S+) 封=([0-9a-f]{16})')
def fuda(mini, base):
    p = subprocess.run(['python3', '-B', Y71, 'fuda', '--kikai', VP, mini, base], capture_output=True, text=True, cwd=M)
    m = FUDA.search(p.stdout); ran = re.search(r'★走らせた★ (.*)', p.stdout)
    return p.returncode, (tuple(int(x) for x in m.groups()[:5]) if m else None), (m.group(7) if m else '-'), (ran.group(1) if ran else '-'), p.stdout, p.stderr
MAP = {139: ('讀めぬ行', 4), 133: ('母數', 0), 152: ('実体無', 3), 158: ('一致', 1), 160: ('相違', 2)}
def awase(term, q):
    """settrace の落ちる行 term と 四数 q=(母數,一致,相違,実体無,讀めぬ行) の対応。"""
    if q is None: return '★71 が四数を出さぬ★'
    if term == 133: return '合(母數=0)' if q[0] == 0 else f'★割れ★ 母數={q[0]}'
    if term in MAP:
        nm, i = MAP[term]; return f'合({nm}=1)' if (q[i] == 1 and q[0] == 1) else f'★割れ★ {nm}={q[i]} 母數={q[0]}'
    return f'★21 の落ちる行が {term}★'
out_rows = []; hdr = ('山', 'mini', '21 落ちる行 A', '71 rc A', '71 四数 A(母/一/相/実/讀)', '封 A', '合否 A', '21 落ちる行 B', '71 rc B', '71 四数 B', '封 B', '合否 B')
ran_paths = set(); errs = []
for r in rows21:
    yama, paper, mini = r[0], r[1], LINES + '/' + r[3]; stem = paper[:-3]; ev = f'{R}/{stem}_evidence/'
    tA, tB = int(r[6]), int(r[9])
    a = fuda(mini, ''); b = fuda(mini, ev); ran_paths.add(a[3].split(' ')[2] if a[3] != '-' else '-')
    if a[5].strip(): errs.append(f'{r[3]} A stderr: {a[5].strip()[:120]}')
    out_rows.append((yama, r[3], tA, a[0], '/'.join(map(str, a[1])) if a[1] else '-', a[2], awase(tA, a[1]), tB, b[0], '/'.join(map(str, b[1])) if b[1] else '-', b[2], awase(tB, b[1])))
K.kaku_tsv(E + '/35_yotsu.tsv', out_rows, hdr)
jk = subprocess.run(['python3', '-B', Y71, '--jikenme'], capture_output=True, text=True, cwd=M); jkl = [l for l in jk.stdout.split('\n') if l.startswith('★自検め★')]
otsu1 = [r for r in out_rows if r[0] == '乙1']; otsu5 = [r for r in out_rows if r[0] == '乙5']
wa = lambda rows, i: sum(1 for r in rows if r[i].startswith('合')); ware = lambda rows, i: [r for r in rows if not r[i].startswith('合')]
out = [f'# 35 ㋓ 兩席の器が同じ四數を出すか / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 專任3 の器 {os.path.relpath(Y71, M)} sha16 {sha16(Y71)}(讀む・走らせるのみ・-B)/ --kikai {os.path.relpath(VP, M)} sha16 {sha16(VP)} / 的 乙1 {len(otsu1)} 本 + 乙5 {len(otsu5)} 本 / 71 が走らせた器の path(出目の「★走らせた★」行から) {sorted(ran_paths)}',
       f'## 71 の --jikenme(彼の対照): rc {jk.returncode} / {jkl}',
       f'## 乙1 {len(otsu1)} 本: A 合 {wa(otsu1, 6)} 割れ {len(ware(otsu1, 6))} ‖ B 合 {wa(otsu1, 11)} 割れ {len(ware(otsu1, 11))}',
       f'## 乙5 {len(otsu5)} 本: A 合 {wa(otsu5, 6)} 割れ {len(ware(otsu5, 6))} ‖ B 合 {wa(otsu5, 11)} 割れ {len(ware(otsu5, 11))}',
       '| ' + ' | '.join(hdr) + ' |'] + ['| ' + ' | '.join(str(x) for x in r) + ' |' for r in out_rows]
n133 = [r for r in otsu1 if r[2] == 133]
out.append(f'## 133 の 4 本(sha256= 無・continue): 71 の四数 = {sorted(set(r[4] for r in n133))} / 71 rc = {sorted(set(r[3] for r in n133))} ―― 四数札は「行が母數に入らぬ」を ★母數=0★ でしか言へず、★何行が讀まれもせず跳ばれたか★ は數へぬ。settrace(21)は其の行を 133 と名指す。∴ 此処で割れるなら「71 が数へて居らぬ」のではなく ★四数の器は 133 を數へる欄を持たぬ★ ―― 器の盲ではなく欄の欠(專任3 の器も生器も同じ)。')
out.append(f'## 讀手の版: 71 は「★走らせた★ <cmd>」で path を刷るが ★sha も行数も刷らぬ★ ―― 本弾の版刻器 20 が足す物は其処(21 の版札 参照)。')
out += errs[:5]
allok = not ware(out_rows, 6) and not ware(out_rows, 11)
out.append(f'# 結 35: {"★兩席の器は同じ現物で割れなかつた(26/26 対応が合ふ)★" if allok else "★割れた ―― 上の ★割れ★ の行を讀め★"} / 71 --jikenme rc {jk.returncode}')
K.kaku(E + '/35_yotsu.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if allok and jk.returncode == 0 else 1)
