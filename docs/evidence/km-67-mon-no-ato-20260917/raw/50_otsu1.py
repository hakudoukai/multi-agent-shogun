# -*- coding: utf-8 -*-
"""㋓ 乙1 23 + 乙5 3 の現物 50_otsu1(第67弾)―― 66 の 30_sanzan.tsv から乙1/乙5 の 26 行を引き(手写しでない)、各々の實體の sha256 を計り、臺帳の ★生の行(bytes)★ を sha で引き当て、一行づつ mini 臺帳(raw/otsu1/lines/)へ逐語で写し、★main 樹の讀手 karo_mac_manifest_verify.py の main() を sys.settrace で走らせ★ verify.py の何行で落ちるかを實走で採る(133 sha無→continue / 139 読めぬ行 / 152 実体無 / 158 一致 / 160 相違 ―― main 樹の版の行)。
基点 三形: A = 門が渡す形 [""](cwd = main 樹)/ B = <紙>_evidence/ / C = <紙>_evidence/<sub>/(raw・kizai)。直すのではない ―― 何處で落ち、何を渡せば届くかを測る。乙5 の 3 行は生バイトを 16 進で。出目 = raw/otsu1_genbutsu.tsv(專任3 へ渡す一枚)+ raw/50_otsu1.txt(臺帳ごとの全件走り・門と同じ基点)。讀むのみ(他席の臺帳・紙へ 0 byte)。"""
import os, sys, re, io, hashlib, time, contextlib, importlib.util
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; R = M + '/queue/reports'; VP = M + '/scripts/checks/karo_mac_manifest_verify.py'
W = M + '/.claude/worktrees/karo-mac-a1'; T66 = W + '/docs/evidence/km-66-noranu-336-20260917/raw/30_sanzan.tsv'
spec = importlib.util.spec_from_file_location('kv', VP); V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
VSHA = hashlib.sha256(open(VP, 'rb').read()).hexdigest()[:16]
rows66 = [l.rstrip('\n').split('\t') for l in open(T66, encoding='utf-8')][1:]
tgt = [r for r in rows66 if r[4].startswith('乙1') or r[4].startswith('乙5')]
assert len(tgt) == 26, len(tgt)
LINES = E + '/otsu1/lines'; os.makedirs(LINES, exist_ok=True)
TERM = {133: '133 sha256= 無→continue(★数へられぬ・母數にも入らぬ★)', 139: '139 読めぬ行(path 候補 0 = "/" を含む語が無い)', 152: '152 実体無(候補は在るが基点で届かぬ)', 158: '158 一致', 160: '160 相違'}
# ★二走目★: 行番号は ★main 樹の讀手(a507c998c7bd6485・198 行)★ の物。一走目は worktree HEAD の写し(bbde471f70848fc8・127 行)を cat -n で讀んで 76/82/95/101/103 と置き、走らせた器は main 樹の物ゆゑ 0/82 と喰ひ違つた(.first に残す)。★讀んだ版と走らせた版が別であつた ―― 器が暴いた。★
def run_reader(mini, bases):
    hits = []
    def tr(frame, ev, arg):
        if frame.f_code.co_filename == VP:
            if ev == 'line': hits.append(frame.f_lineno)
            return tr
        return None
    buf = io.StringIO(); cwd = os.getcwd(); os.chdir(M)
    try:
        sys.settrace(tr)
        with contextlib.redirect_stdout(buf): rc = V.main([VP, mini] + bases)
    finally: sys.settrace(None); os.chdir(cwd)
    term = [h for h in hits if h in TERM]; s = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)', buf.getvalue())
    return (term[-1] if term else 0), rc, (f'{s.group(1)}/{s.group(2)}/{s.group(3)}/{s.group(4)}' if s else '?'), len(hits)
out_rows = []; hdr = ('山', '臺帳(紙)', '臺帳の行', '生の行(逐語・tab は \\t)', '實體(_evidence からの相對)', 'bytes', '實 sha16', '行の sha = 實 sha', '讀手 paths_of の候補', '落ちる行[A 基点 ""]', '一致/相違/実体無/読めぬ[A]', '落ちる行[B 基点 _evidence/]', '出目[B]', '落ちる行[C 基点 _evidence/<sub>/]', '出目[C]', '生バイト 16 進(乙5 のみ)')
per_ledger = {}
for r in tgt:
    paper, rel, sz, mt, yama = r[0], r[1], int(r[2]), r[3], r[4][:2]
    stem = paper[:-3]; ev = f'{R}/{stem}_evidence'; man = ev + '/manifest.txt'; f = f'{ev}/{rel}'
    fb = open(f, 'rb').read(); sha = hashlib.sha256(fb).hexdigest(); assert len(fb) == sz, (f, len(fb), sz)
    mb = open(man, 'rb').read(); lines = mb.split(b'\n'); idx = [i for i, l in enumerate(lines) if sha.encode() in l.lower()]
    assert len(idx) == 1, (man, sha, idx); n = idx[0]; raw = lines[n]
    short = re.sub(r'^ashigaru-mac-\d_|^karo_mac_|_2026\d+$', '', stem); mini = f'{LINES}/{short}_L{n + 1:02d}.txt'
    with open(mini, 'wb') as fh: fh.write(raw + b'\n')
    line_s = raw.decode('utf-8', 'replace'); cands = V.paths_of(line_s.strip()); m = V.SHA.search(line_s); same_sha = (m.group(1) == sha) if m else False
    sub = rel.split('/')[0] if '/' in rel and rel.split('/')[0] in ('raw', 'kizai') else ''
    A = run_reader(mini, ['']); Bb = run_reader(mini, [ev + '/']); C = run_reader(mini, [f'{ev}/{sub}/']) if sub else ('=B', Bb[1], Bb[2], 0)
    tail = ('末尾空白' if re.search(rb'[ \t]$', raw) else '') + ('CR' if b'\r' in raw else '')
    out_rows.append((yama, paper, n + 1, line_s.replace('\t', '\\t') + (f' ★{tail}★' if tail else ''), rel, sz, sha[:16], same_sha, ' | '.join(cands) if cands else '(無)', A[0], A[2], Bb[0], Bb[2], C[0], C[2], raw.hex() if yama == '乙5' else '-'))
    per_ledger.setdefault(stem, (man, ev));
K.kaku_tsv(E + '/otsu1_genbutsu.tsv', out_rows, hdr)
import collections; cA = collections.Counter((r[0], r[9]) for r in out_rows); cB = collections.Counter((r[0], r[11]) for r in out_rows); cC = collections.Counter((r[0], r[13]) for r in out_rows)
out = [f'# 50 ㋓ 乙1/乙5 の現物 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 讀手 = main 樹 karo_mac_manifest_verify.py sha16 {VSHA}(讀む・走らせるのみ)/ 的 26 本(66 30_sanzan.tsv から: 乙1 {sum(1 for r in out_rows if r[0] == "乙1")} / 乙5 {sum(1 for r in out_rows if r[0] == "乙5")})/ mini 臺帳 {len(out_rows)} 本 raw/otsu1/lines/ / 一枚 = raw/otsu1_genbutsu.tsv({len(out_rows)} 行 + 頭)',
       '## 落ちる行(實走・settrace・verify.py の行番号)―― 山 × 基点', '   A 基点 ""(門が渡す形・cwd main 樹): ' + ' / '.join(f'{k[0]} → {TERM.get(k[1], k[1])}: {v} 本' for k, v in sorted(cA.items())),
       '   B 基点 <紙>_evidence/: ' + ' / '.join(f'{k[0]} → {TERM.get(k[1], k[1])}: {v} 本' for k, v in sorted(cB.items())),
       '   C 基点 <紙>_evidence/<sub>/(raw・kizai・無ければ =B): ' + ' / '.join(f'{k[0]} → {TERM.get(k[1], str(k[1]))}: {v} 本' for k, v in sorted(cC.items(), key=lambda kv: (kv[0][0], str(kv[0][1])))),
       '## 臺帳ごとの全件走り(門と同じ基点 "" と B・C)']
for stem, (man, ev) in per_ledger.items():
    sub = next((r[4].split('/')[0] for r in out_rows if r[1][:-3] == stem and '/' in r[4] and r[4].split('/')[0] in ('raw', 'kizai')), '')
    a = run_reader(man, ['']); b = run_reader(man, [ev + '/']); c = run_reader(man, [f'{ev}/{sub}/']) if sub else ('=B', b[1], b[2], 0)
    nl = sum(1 for l in open(man, 'rb').read().split(b'\n') if l.strip() and not l.startswith(b'#')); nsha = sum(1 for l in open(man, encoding='utf-8', errors='replace') if V.SHA.search(l))
    out.append(f'   {stem}_evidence/manifest.txt: 実体行 {nl} / sha256= を含む行 {nsha} / A rc {a[1]} {a[2]} / B rc {b[1]} {b[2]} / C({sub or "=B"}) rc {c[1]} {c[2]}')
out.append('## 生バイト 16 進(乙5・3 行・臺帳の行そのまま・改行は含まぬ)')
for r in out_rows:
    if r[0] == '乙5': out.append(f'   {r[1]} L{r[2]} {len(bytes.fromhex(r[15]))} B: {r[15]}')
K.kaku(E + '/50_otsu1.txt', '\n'.join(out)); print('\n'.join(out)); print('--- tsv 頭 3 行'); print(open(E + '/otsu1_genbutsu.tsv', encoding='utf-8').read()[:1500])
