# -*- coding: utf-8 -*-
"""㋒ rc が管を渡る箇所を數へる 33(第68弾)―― 母數 = km-67 と km-68 の束の ★全 通常 file★(拡張子を問はぬ・非通常は除き數へる)。
検出子(讀手が判ぜられる様に刷る):
  甲 python: 同じ文(括弧が閉ぢるまで ≤8 行)に shell=True と、文字列の中の | が在る / os.system( / os.popen( / subprocess.getoutput( / getstatusoutput(
  乙 shell 文(拡張子を問はず・.sh も .txt/.md に写された命令行も): `| <cmd>` の在る行の ★同じ行か次の行★ に $? が在る(pipe の後の rc を讀む形)
  丙 .sh の file 単位: `set -o pipefail` が無い(pipe の rc が隠れる器)―― 之は行でなく file の札
★陽性対照★ = raw/fixture/33_positive.sh(乙)と raw/fixture/33_positive.py(甲)を己で書き ★同じ歩きに乗せ★ 鳴る事を示す。陰性対照 = raw/fixture/33_negative.sh(pipefail 有・$? は pipe の無い行)。
★己★ = 此の器自身(検出子の文字列を含む)は path 一致で「己」札を付けて別に數へる(字面で除かぬ)。
直す = km-68 の器に当たれば直す。km-67 は錠の下・讀むのみ(直さぬ本数と理由を書く)。出目 raw/33_rc_pipe.txt + .tsv。"""
import os, sys, re, stat, time
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
W = '/Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1'; ROOTS = [W + '/docs/evidence/km-67-mon-no-ato-20260917', os.path.dirname(E)]
SELF = os.path.realpath(__file__); FX = E + '/fixture'; os.makedirs(FX, exist_ok=True)
# ★陽性対照・陰性対照を己で書く(同じ歩きに乗せる)★
K.kaku(FX + '/33_positive.sh', '#!/bin/bash\n# 33 の陽性対照(乙)―― pipe の後の $? を讀む形。此の file は鳴らねばならぬ。\nls /nonexistent | head -1\nrc=$?\necho "rc=$rc"\n')
K.kaku(FX + '/33_positive.py', '# 33 の陽性対照(甲)―― shell=True の cmd に | が在る形。此の file は鳴らねばならぬ。\nimport subprocess\np = subprocess.run("false | true", shell=True)\nprint(p.returncode)\n')
K.kaku(FX + '/33_negative.sh', '#!/bin/bash\n# 33 の陰性対照 ―― pipefail 有・$? は pipe の無い行。此の file は鳴つてはならぬ。\nset -o pipefail\nout=$(ls /nonexistent)\nrc=$?\necho "$out" | head -1\n')
def moji_gyou(text):
    """python の source で ★文字列/註の中★ に在る行番号の集合(tokenize)。当たりが其処に在れば「文」であつて「実行」ではない。tokenize できねば空(=全て実行と看做す・保守側)。"""
    import tokenize, io as _io
    got = set()
    try:
        for tok in tokenize.generate_tokens(_io.StringIO(text).readline):
            if tok.type in (tokenize.STRING, tokenize.COMMENT) or tokenize.tok_name.get(tok.type, '').startswith('FSTRING'):  # ★三走目★ 3.12+ の f-string は STRING でなく FSTRING_* に割れる(二走目は 70_paper.py:102 の f-string を「実行」と誤札)
                for ln in range(tok.start[0], tok.end[0] + 1): got.add(ln)
    except Exception: return set()
    return got
KOU_ONE = re.compile(r'os\.system\(|os\.popen\(|subprocess\.getoutput\(|subprocess\.getstatusoutput\(')
OTSU = re.compile(r'\|\s*(head|tail|grep|wc|sort|cut|sed|awk|tee|cat|less|uniq|xargs|tr)\b')
hits = []; nfiles = 0; nonreg = 0; sh_files = []
for root in ROOTS:
    for d, ds, fs in os.walk(root):
        for f in sorted(fs):
            p = os.path.join(d, f); st = os.lstat(p)
            if not stat.S_ISREG(st.st_mode): nonreg += 1; continue
            nfiles += 1; rel = os.path.relpath(p, W); own = os.path.realpath(p) == SELF
            try: t = open(p, 'rb').read().decode('utf-8', 'replace')
            except Exception as e: hits.append(('讀めぬ', rel, 0, str(e), own, '-')); continue
            L = t.split('\n'); MOJI = moji_gyou(t) if f.endswith('.py') else None  # .py 以外(.md .txt .tsv .sh)は実行されぬ紙か shell ―― .sh のみ実行
            if f.endswith('.sh'):
                sh_files.append((rel, 'set -o pipefail' in t, own))
            if f.endswith('.py'):
                i = 0
                while i < len(L):
                    if 'subprocess' in L[i] or 'shell' in L[i] or 'Popen' in L[i] or 'run(' in L[i]:
                        bun = L[i]; j = i
                        while bun.count('(') > bun.count(')') and j + 1 < len(L) and j - i < 8: j += 1; bun += ' ' + L[j].strip()
                        if re.search(r'shell\s*=\s*True', bun) and re.search(r'["\'][^"\']*\|[^"\']*["\']', bun): hits.append(('甲 shell=True+|', rel, i + 1, bun.strip()[:160], own, '文' if (i + 1) in MOJI else '実行'))
                        i = j + 1; continue
                    i += 1
                for k, l in enumerate(L, 1):
                    if KOU_ONE.search(l): hits.append(('甲 system/popen/getoutput', rel, k, l.strip()[:160], own, '文' if k in MOJI else '実行'))
            for k, l in enumerate(L):
                if OTSU.search(l) and ('$?' in l or (k + 1 < len(L) and '$?' in L[k + 1])):
                    hits.append(('乙 pipe→$?', rel, k + 1, (l.strip() + (' ⏎ ' + L[k + 1].strip() if '$?' not in l and k + 1 < len(L) else ''))[:160], own, ('文' if (MOJI is not None and (k + 1) in MOJI) else ('実行' if f.endswith(('.py', '.sh')) else '文(紙)'))))
OWN_STEM = os.path.basename(SELF).rsplit('.', 1)[0] + '.'  # ★三走目★ 己の産物(33_rc_pipe.*.txt/.tsv/.stdout …)は己の一走目の当たりを逐語で含む ―― 母數に入れれば走る度に膨れる(二走目 24 本の因)。名の頭(己の stem)で札を付け、字面では除かぬ。
san = [h for h in hits if (not h[4]) and os.path.basename(h[1]).startswith(OWN_STEM)]
hits_hon = [h for h in hits if not ((not h[4]) and os.path.basename(h[1]).startswith(OWN_STEM))]
ji = [h for h in hits_hon if h[4]]; ta = [h for h in hits_hon if not h[4]]
fx = [h for h in ta if '/fixture/33_' in h[1]]; hon = [h for h in ta if '/fixture/33_' not in h[1]]
pos_sh = any(h[1].endswith('33_positive.sh') and h[0].startswith('乙') for h in fx); pos_py = any(h[1].endswith('33_positive.py') and h[0].startswith('甲') for h in fx); neg = any(h[1].endswith('33_negative.sh') for h in fx)
k67 = [h for h in hon if 'km-67' in h[1]]; k68 = [h for h in hon if 'km-68' in h[1]]
K.kaku_tsv(E + '/33_rc_pipe.tsv', [(h[0], h[1], h[2], h[3], '己' if h[4] else ('己の産物' if os.path.basename(h[1]).startswith(OWN_STEM) else ('対照' if '/fixture/33_' in h[1] else '本')), h[5]) for h in hits], ('検出子', 'path', '行', '逐語', '札', '文/実行'))
jikkou = [h for h in hon if h[5] == '実行']; bun = [h for h in hon if h[5] != '実行']
out = [f'# 33 ㋒ rc が管を渡る箇所 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 歩き根 2(km-67・km-68)/ 母數 通常 file {nfiles}(非通常 {nonreg})/ 検出子 甲(python)乙(pipe→$?)丙(.sh の pipefail 無)',
       f'## 陽性対照: 33_positive.sh(乙) {"鳴つた" if pos_sh else "★黙つた=器ではない★"} / 33_positive.py(甲) {"鳴つた" if pos_py else "★黙つた=器ではない★"} / 陰性対照 33_negative.sh {"★鳴つた=騒音★" if neg else "黙つた"}',
       f'## 当たり(対照と己と己の産物を除く) {len(hon)} 箇所 = km-67 {len(k67)} / km-68 {len(k68)} ‖ 己(33 自身・字面で除かず path で札) {len(ji)} ‖ 己の産物(33_rc_pipe.* ―― 一走目・二走目の出目が己の当たりを逐語で含む) {len(san)} ‖ 対照 {len(fx)} ‖ 和 {len(hon) + len(ji) + len(san) + len(fx)} = 全当たり {len(hits)}']
for h in hon: out.append(f'  [{h[5]}] {h[0]} {h[1]}:{h[2]}  {h[3]}')
out.append(f'## 当たりの内 ★実行★(rc が実際に管を渡る) {len(jikkou)} / 文(紙・則・註・文字列の中で管を語る) {len(bun)} ―― 文は「rc が管を渡る箇所」ではない。字面で除かず、tokenize の STRING/COMMENT と file の種で割つた(二走目で足した札・一走目 .first は札無し)')
out.append(f'## 丙 .sh の file 単位(pipefail 無 = pipe の rc が隠れる器): 母數 {len(sh_files)}')
for rel, pf, own in sh_files: out.append(f'  {"pipefail 有" if pf else "★pipefail 無★"} {rel}' + (' (対照)' if '/fixture/33_' in rel else ''))
out.append(f'## 直した本数 = km-68 の ★実行★ の当たり {sum(1 for h in k68 if h[5] == "実行")} 本 / 直さぬ = km-68 の文 {sum(1 for h in k68 if h[5] != "実行")} 本(則の記述・測る前に書いた文ゆゑ触らぬ)+ km-67 の {len(k67)} 本(錠の下・凍つた束・讀むのみ)')
out.append('## ★此の器が数へぬ物★: 對話(shell の入力)で打つた `cmd | head; echo $?` は束に写らぬ限り母數に無い ―― 第67弾 §7-3 の疵は其の形であつた(束の器には無く、席の手に在つた)。∴ 本弾の 0 は「束の器に無い」であつて「席の手に無い」ではない。')
out.append(f'# 結 33: 対照 {"3/3 期待通り" if pos_sh and pos_py and not neg else "★期待と違ふ★"} / 本の当たり {len(hon)} = 実行 {len(jikkou)} + 文 {len(bun)}')
K.kaku(E + '/33_rc_pipe.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if (pos_sh and pos_py and not neg) else 1)
