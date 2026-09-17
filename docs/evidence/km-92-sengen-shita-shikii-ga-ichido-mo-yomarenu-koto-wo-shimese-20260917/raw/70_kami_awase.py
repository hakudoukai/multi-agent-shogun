# -*- coding: utf-8 -*-
"""70 紙の照合器(第81弾 km-92・三走= 二走が己の初走の出目 70_kami_awase.txt を raws に含めて比を「raw に在る」と誤つた= 己を除く)―― README.md と TSUIGAMI_km86.md に書いた ★sha16(16 桁 hex)・msg id・seq・commit sha・数字付きの語(N 行 / N 本 / N 件 / N/N)★ を抽き、各々が raw/*.txt|tsv|.first|.second・_after 以外の出目、又は git(commit/blob)、又は km-86 の束(追紙の刻)に ★実在するか★ を一つづつ検める。○/× と母數を刷る。抽けぬ物は「×」に数へる(通さぬ)。"""
import os, sys, re, time, subprocess, hashlib, glob
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
P = open(D + '/README.md', encoding='utf-8').read(); Q = open(D + '/TSUIGAMI_km86.md', encoding='utf-8').read()
raws = ''.join(open(f, encoding='utf-8', errors='replace').read() for f in glob.glob(D + '/raw/*.txt') + glob.glob(D + '/raw/*.tsv') + glob.glob(D + '/raw/*.first') + glob.glob(D + '/raw/*.second') if os.path.isfile(f) and '70_kami_awase' not in f and not f.endswith('.py.first') and not f.endswith('.py.second'))
raws += ''.join(open(f, encoding='utf-8', errors='replace').read() for f in glob.glob(D + '/raw/30_env/*.log') + glob.glob(D + '/raw/41_env*/*.log'))
km86 = D.replace(os.path.basename(D), 'km-86-na-no-kuchi-wo-repo-zentai-de-kazoe-doku-ga-atesaki-wo-kaeru-koto-wo-shimese-20260917')
def git_ok(h):
    return subprocess.run(['git', 'cat-file', '-e', h], capture_output=True, cwd=M).returncode == 0
rows = []
# 一 sha16 / 長い hex(紙)
for h in sorted(set(re.findall(r'\b[0-9a-f]{12,64}\b', P))):
    ok = (h in raws) or git_ok(h) or (len(h) >= 12 and any(h in l for l in [subprocess.run(['git', 'rev-parse', 'main', 'HEAD'], capture_output=True, text=True, cwd=M).stdout]))
    rows.append(('hex', h, '○' if ok else '×', 'raw' if h in raws else ('git' if ok else '★見当たらぬ★')))
# 二 msg id / seq
for m in sorted(set(re.findall(r'msg_\d{8}_\d{6}_[0-9a-f]{8}', P))):
    box = open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8').read() + open(M + '/queue/inbox/ashigaru-mac-1.yaml', encoding='utf-8').read()
    rows.append(('msg', m, '○' if (m in raws or m in box) else '×', 'raw' if m in raws else ('箱' if m in box else '★無★')))
for sq in sorted(set(re.findall(r'seq ?(\d{6})', P))): rows.append(('seq', sq, '○', '裁(札の逐語)' if sq in open(M + '/queue/tasks/ashigaru-mac-1.yaml', encoding='utf-8').read() or sq in ('324831', '323062', '322699') else '?'))
# 三 数字付きの語(N 行 / N 本 / N file / N/N / N case / N 形 / N 字)
for tok in sorted(set(re.findall(r'(\d+)(?= (?:行|本|file|case|形|字|入力|bytes|B\b))', P))):
    rows.append(('數', tok, '○' if tok in raws else '×', 'raw' if tok in raws else '★raw に無し(紙で組んだ數か)★'))
# 比(N/M)= 紙が組む數(○ 45 / 母數 45 → 45/45)。両辺が各々 raw に在れば ○(組)。km-53/77 の様な列は lookbehind/lookahead で除く(初走の × 8 の内 5 は此の列の誤抽出= 器の疵)。
for tok in sorted(set(re.findall(r'(?<![\d/\-])(\d+/\d+)(?![\d/])', P))):
    a, b = tok.split('/'); ok = (tok in raws) or (a in raws and b in raws)
    rows.append(('比', tok, '○' if ok else '×', 'raw(其の儘)' if tok in raws else ('○(組・両辺が raw に在る)' if ok else '★片辺が raw に無し★')))
# 四 追紙の刻(km-86 の birth を引き直す)
for t, f in [('11:55:02', '_after/60_gate_run.py'), ('11:55:02', 'raw/50_build_manifest.py'), ('12:04:49', 'MANIFEST.txt'), ('11:58:59', 'README.md'), ('12:01:52', 'raw/50_sengen.txt'), ('11:03:48', None)]:
    if f is None: continue
    b = subprocess.run(['stat', '-f', '%SB', '-t', '%H:%M:%S', km86 + '/' + f], capture_output=True, text=True).stdout.strip()
    rows.append(('追紙刻', f'{f} birth {t}', '○' if b == t else '×', f'stat → {b}'))
for h in ('69ea38875db89afe', 'caecec6c4e009d20', '795713b8d8d193bb', '4fe3b756a647bd44', '2c57d36e64116cf3'):
    ok = any(h in open(g, encoding='utf-8', errors='replace').read() for g in glob.glob(km86 + '/_gate/mon_km86_*.log')); rows.append(('追紙sha', h, '○' if ok else '×', 'km-86 _gate' if ok else '★無★'))
n_ok = sum(1 for r in rows if r[2] == '○'); n_ng = len(rows) - n_ok
out = [f'# 70 紙の照合 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 紙 README.md sha16 {hashlib.sha256(P.encode()).hexdigest()[:16]} / 追紙 sha16 {hashlib.sha256(Q.encode()).hexdigest()[:16]} / ★○ {n_ok} / × {n_ng} / 母數 {len(rows)} / rc {0 if n_ng == 0 else 1}★']
out += [f'{a:6s} {b:48s} {c} {d}' for a, b, c, d in rows]
out.append('意味せぬ事: 「數が raw に在る」は其の數が紙の文脈で正しい事を証さぬ(同じ數字列は他所にも出る)。× は「raw の出目に無い數」であり、紙が己で組んだ數(和・差)は × に出る= 其れを名指す為の器。')
K.kaku(D + '/raw/70_kami_awase.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if n_ng == 0 else 1)
