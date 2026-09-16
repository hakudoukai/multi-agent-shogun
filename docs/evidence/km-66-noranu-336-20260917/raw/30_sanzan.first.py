# -*- coding: utf-8 -*-
r"""三山の器 30(第66弾)―― 載らぬ file を 00_start の則(甲1→甲2→甲3→甲4→乙1→丙1→乙2→丙2→乙3→乙4・丙0)の順で ★最初に当たつた山★ へ入れる。読取のみ。
母數・載らぬの定義は前弾 26 と同一(21_jou1_besho.py を讀み込み・40 本の臺帳は 21 の tsv)。歩き根は絶対 path(main 樹 queue/reports)。
出目: 30_sanzan.txt(要約)/ 30_sanzan.tsv(一本ごと: 臺帳 相對path bytes mtime 山 細目 理由)/ 30_sanzan_per_ledger.tsv(臺帳ごとの山の本数)。
使ひ方: 30_sanzan.py            … 40 本(母數 = 前弾 21 の tsv)
        30_sanzan.py --one <ev_root> <臺帳> <紙 or -> <出目の頭>   … 一つの根へ同じ則を掛ける(㋔ 己の束へ門の後に掛ける・出目は根の外)
甲4 の実装: 宣の行 = 臺帳の非項行(# 行と sha256 を含まぬ行)+ 紙(.md)の全行。行に 員外|ingai|門の後|載せぬ|門控 の何れかが在り、★同じ行★に file の相對 path が逐語で在るか、file の親 dir の相對 path + '/' が逐語で在る時。
丙2 は「同秒」を本形とし、「同分」へ締めた数も併記する(㋒ 丙が零なら則が緩い)。2MB 超の file は開かぬ(sha を出せぬ → 丙0)。"""
import os, sys, re, stat, time, hashlib, importlib.util, collections
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; os.chdir(M)
R65 = M + '/queue/reports/ashigaru-mac-1_km-65-daichou-ga-aru-to-daichou-ga-kiku-wa-betsu-besshono-40-hon-ni-jou1-wo-kakero-20260917_evidence/raw'
sp = importlib.util.spec_from_file_location('j21', R65 + '/21_jou1_besho.py'); J = importlib.util.module_from_spec(sp); sp.loader.exec_module(J)
sp2 = importlib.util.spec_from_file_location('ap', M + '/scripts/checks/karo_mac_manifest_append.py'); AP = importlib.util.module_from_spec(sp2); sp2.loader.exec_module(AP)
D = M + '/queue/reports'; t0 = time.strftime('%Y-%m-%dT%H:%M:%S%z'); MAXB = 2000000
KW = re.compile(r'員外|ingai|門の後|載せぬ|門控'); HEXRX = re.compile(r'[0-9a-fA-F]{64}')
ORDER = ['甲1 門の出目', '甲2 臺帳の器の出目', '甲3 __pycache__', '甲4 宣で員外', '乙1 届かぬ(同sha項あり)', '丙1 同名別sha', '乙2 名が器を破る', '丙2 同秒(門の前後 決められぬ)', '乙3 門の後に生れた', '乙4 器へ渡さなかつた', '丙0 測れぬ']
def yama(k): return k[0]
def sha_of(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
def ledger_parse(man, bs):
    """項(path, sha)と非項行を返す。26 と同じく FORMS で讀む。"""
    items = []; nonitem = []; covered = set()
    for ln in open(man, 'rb').read().decode('utf-8', 'replace').split('\n'):
        s = ln.rstrip('\r').strip()
        if not s: continue
        m = None
        if not s.startswith('#'):
            for nm, rx in J.FORMS:
                m = rx.match(s)
                if m: break
        if not m: nonitem.append(s); continue
        p = m.group('p').strip().strip('"\''); want = m.group('s').lower(); items.append((p, want))
        cands = [p] if p.startswith('/') else [os.path.normpath(os.path.join(b_, p)) for b_ in bs]
        for full in cands:
            try: st = os.lstat(full)
            except OSError: continue
            if stat.S_ISREG(st.st_mode) and st.st_size <= MAXB and sha_of(full) == want: covered.add(os.path.realpath(full)); break
    return items, nonitem, covered
def classify(ev, man, paper, gran='s'):
    """一つの根 ev(配下を歩く)・臺帳 man・紙 paper へ則を掛ける。返り = 一本ごとの (rel, size, mtime, 山細目, 理由) の列 + 母數の数。"""
    bs = J.bases_for(man, paper) if paper and paper != '-' else [os.path.abspath(os.path.dirname(man)) + os.sep, os.path.abspath(ev) + os.sep]
    items, nonitem, covered = ledger_parse(man, bs)
    shas = {s for _, s in items}; bases = {os.path.basename(p) for p, _ in items}
    decl = list(nonitem) + ([l.rstrip('\n') for l in open(paper, encoding='utf-8', errors='replace')] if paper and paper != '-' and os.path.isfile(paper) else [])
    decl = [l for l in decl if KW.search(l)]
    try: lm = os.lstat(man).st_mtime
    except OSError: lm = None
    files = []; nonreg = 0
    for d, ds, fs in os.walk(ev):
        for f in fs:
            q = os.path.join(d, f); st = os.lstat(q)
            if not stat.S_ISREG(st.st_mode): nonreg += 1; continue
            if os.path.realpath(q) == os.path.realpath(man): continue
            files.append((q, st))
    rows = []
    for q, st in files:
        rp = os.path.realpath(q); rel = os.path.relpath(q, ev); base = os.path.basename(q)
        if rp in covered: rows.append((rel, st.st_size, int(st.st_mtime), '載る', '')); continue
        k = None; why = ''
        if re.search(r'(^|/)mon/', rel) or re.search(r'gate|gatelog|_mon\d', base) or re.match(r'mon\d*[_.].*\.(out|err|rc)$', base): k = ORDER[0]
        elif re.search(r'manifest|daichou', base, re.I): k = ORDER[1]
        elif '/__pycache__/' in '/' + rel: k = ORDER[2]
        else:
            parents = []; pp = os.path.dirname(rel)
            while pp: parents.append(pp + '/'); pp = os.path.dirname(pp)
            hit = [l for l in decl if rel in l or any(par in l for par in parents)]
            if hit: k = ORDER[3]; why = hit[0][:120]
        if k is None:
            if lm is None or st.st_size > MAXB: k = ORDER[10]; why = '臺帳 mtime 無' if lm is None else f'{st.st_size}B > 2MB 開かぬ'
            else:
                try: s_ = sha_of(q)
                except OSError as e: k = ORDER[10]; why = f'開けぬ {e.__class__.__name__}'; s_ = None
                if s_ is not None:
                    if s_ in shas: k = ORDER[4]; why = '臺帳の項 ' + [p for p, s in items if s == s_][0][:80]
                    elif base in bases: k = ORDER[5]; why = '臺帳の項 ' + [p for p, s in items if os.path.basename(p) == base][0][:60] + ' sha ' + [s for p, s in items if os.path.basename(p) == base][0][:12] + '≠実 ' + s_[:12]
                    elif any(c in rel for c in '"\'\n\r'): k = ORDER[6]; why = 'append.py togame=' + str(AP.togame(rel))[:60]
                    else:
                        fm = int(st.st_mtime); lmi = int(lm)
                        same = (fm == lmi) if gran == 's' else (fm // 60 == lmi // 60)
                        if same: k = ORDER[7]; why = f'file {time.strftime("%H:%M:%S", time.localtime(fm))} 臺帳 {time.strftime("%H:%M:%S", time.localtime(lmi))}'
                        elif fm > lmi: k = ORDER[8]; why = f'file {time.strftime("%m-%d %H:%M:%S", time.localtime(fm))} > 臺帳 {time.strftime("%m-%d %H:%M:%S", time.localtime(lmi))} (+{fm - lmi}s)'
                        else: k = ORDER[9]; why = f'file {time.strftime("%m-%d %H:%M:%S", time.localtime(fm))} < 臺帳 {time.strftime("%m-%d %H:%M:%S", time.localtime(lmi))} 名清く sha 無'
        rows.append((rel, st.st_size, int(st.st_mtime), k, why))
    return rows, len(items), nonreg, lm
def summarize(allrows):
    cnt = collections.Counter(); byt = collections.Counter(); rep = collections.defaultdict(list)
    for led, rel, sz, mt, k, why in allrows:
        if k == '載る': continue
        cnt[k] += 1; byt[k] += sz
        if len(rep[k]) < 3: rep[k].append(f'{led}:{rel}')
    return cnt, byt, rep
if len(sys.argv) >= 2 and sys.argv[1] == '--one':
    ev, man, paper, outp = sys.argv[2:6]
    rows, ni, nonreg, lm = classify(ev, man, paper)
    allrows = [('己', *r) for r in rows]; cnt, byt, rep = summarize(allrows); nor = [r for r in rows if r[3] != '載る']
    out = [f'# 己の束へ同じ則(30・--one)/ 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 根 {ev} / 臺帳 {man}(項 {ni}・mtime {time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(lm)) if lm else "無"})/ 配下 通常 file {len(rows)}(非通常 {nonreg})/ 載る {len(rows) - len(nor)} / ★載らぬ {len(nor)}★']
    for k in ORDER: out.append(f'  {k}: {cnt[k]} 本 / {byt[k]} B / 代表 {" ; ".join(rep[k]) if rep[k] else "-"}')
    out.append(f'  甲計 {sum(cnt[k] for k in ORDER if k[0] == "甲")} / 乙計 {sum(cnt[k] for k in ORDER if k[0] == "乙")} / 丙計 {sum(cnt[k] for k in ORDER if k[0] == "丙")} / 総和 {sum(cnt.values())} = 載らぬ {len(nor)} 差 {sum(cnt.values()) - len(nor)}')
    out.append('## 一本ごと(相對path bytes mtime 山 理由):')
    for rel, sz, mt, k, why in sorted(nor): out.append(f'  {rel}\t{sz}\t{time.strftime("%H:%M:%S", time.localtime(mt))}\t{k}\t{why}')
    K.kaku(outp, '\n'.join(out)); print('\n'.join(out)); sys.exit(0)
tsv = [l.rstrip('\n').split('\t') for l in open(R65 + '/21_jou1_besho.tsv', encoding='utf-8')][1:]
allrows = []; per = []; tot_f = tot_n = 0; ap_birth = os.stat(M + '/scripts/checks/karo_mac_manifest_append.py').st_birthtime; led_after_ap = 0
for gran in ('s', 'm'):
    allrows = []; per = []; tot_f = tot_n = 0; nonreg_t = 0
    for r in tsv:
        paper = os.path.join(D, r[0]); man = os.path.join(D, r[1]); ev = os.path.join(D, os.path.basename(paper)[:-3] + '_evidence')
        if not os.path.isdir(ev): per.append((r[0][:44], 0, 0, collections.Counter())); continue
        rows, ni, nonreg, lm = classify(ev, man, paper, gran); nonreg_t += nonreg
        if gran == 's' and lm and lm > ap_birth: led_after_ap += 1
        nor = [x for x in rows if x[3] != '載る']; tot_f += len(rows); tot_n += len(nor)
        c = collections.Counter(x[3] for x in nor); per.append((r[0][:44], len(rows), len(nor), c))
        allrows += [(r[0][:44], *x) for x in rows]
    cnt, byt, rep = summarize(allrows)
    if gran == 's':
        out = [f'# 三山 30 / 刻 {t0} / 母數 = 前弾 21 の臺帳 {len(tsv)} 本 / 歩き根 {D}(絶対)/ 配下 = <紙>_evidence(os.walk・lstat・S_ISREG・臺帳自身を除く・非通常 {nonreg_t} 本除く)/ 則 = 00_start(順序が則の一部・最初に当たつた山)',
               f'## 配下の通常 file 計 {tot_f} / ★載らぬ {tot_n}★(前弾 02:11:54 は 1532 / 336 → {"動かぬ" if tot_n == 336 and tot_f == 1532 else "★動いた★ 差 file " + str(tot_f - 1532) + " / 載らぬ " + str(tot_n - 336)})',
               f'## ★追記器 karo_mac_manifest_append.py の生 {time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ap_birth))}(birthtime)より後の mtime を持つ臺帳 = {led_after_ap}/{len(tsv)} ∴ 「追記器が拒んだ(rc=3)」の実測は {led_after_ap} 本の臺帳でしか起こり得ぬ ―― 乙2 は「器なら拒む名(rc=3 相当・togame)」である★',
               '## 山ごと(本数 / byte 和 / 代表 3):']
        for k in ORDER: out.append(f'  {k}: {cnt[k]} 本 / {byt[k]} B / 代表 {" ; ".join(rep[k]) if rep[k] else "-"}')
        kou = sum(cnt[k] for k in ORDER if k[0] == '甲'); otsu = sum(cnt[k] for k in ORDER if k[0] == '乙'); hei = sum(cnt[k] for k in ORDER if k[0] == '丙')
        out.append(f'  ★甲(載せぬのが正) {kou} 本 {sum(byt[k] for k in ORDER if k[0] == "甲")} B / 乙(疵) {otsu} 本 {sum(byt[k] for k in ORDER if k[0] == "乙")} B / 丙(決められぬ) {hei} 本 {sum(byt[k] for k in ORDER if k[0] == "丙")} B / 総和 {kou + otsu + hei} = 載らぬ {tot_n} 差 {kou + otsu + hei - tot_n}★')
        out.append('## 臺帳ごと(紙 配下 載らぬ 甲 乙 丙 細目):')
        for nm, nf, nn, c in per:
            if nn: out.append(f'  {nm}\t{nf}\t{nn}\t{sum(v for k, v in c.items() if k[0] == "甲")}\t{sum(v for k, v in c.items() if k[0] == "乙")}\t{sum(v for k, v in c.items() if k[0] == "丙")}\t' + ' '.join(f'{k[:2]}={v}' for k, v in sorted(c.items())))
        K.kaku_tsv(E + '/30_sanzan.tsv', [(led, rel, sz, time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(mt)), k, why) for led, rel, sz, mt, k, why in allrows if k != '載る'], header=['臺帳(紙)', '相對path', 'bytes', 'mtime', '山', '理由'])
        K.kaku_tsv(E + '/30_sanzan_per_ledger.tsv', [(nm, nf, nn, ' '.join(f'{k}={v}' for k, v in sorted(c.items()))) for nm, nf, nn, c in per], header=['紙', '配下file', '載らぬ', '山'])
        cnt_s = cnt
    else:
        out.append(f'## ★㋒ 丙2 を「同秒」から「同分」へ締めた時★: 丙2 {cnt_s[ORDER[7]]} → {cnt[ORDER[7]]} 本 / 乙3 {cnt_s[ORDER[8]]} → {cnt[ORDER[8]]} / 乙4 {cnt_s[ORDER[9]]} → {cnt[ORDER[9]]} / 丙計 {sum(cnt_s[k] for k in ORDER if k[0] == "丙")} → {sum(cnt[k] for k in ORDER if k[0] == "丙")}')
K.kaku(E + '/30_sanzan.txt', '\n'.join(out)); print('\n'.join(out))
