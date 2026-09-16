# -*- coding: utf-8 -*-
"""對照の器 30(第70弾)―― 建て直した臺帳(raw/saiken/*)に三本の對照を ★verify.py 直★ と ★門(KM_GATE_MANIFEST_BASE)★ の双方で掛ける。cwd = main 樹。
㋐ 明示基点 = 束の根 → 期待 一致 N / 実体無 0 / rc 0  ㋑ 基点を渡さず(環境変数 unset・既定 = repo 根)→ 期待 実体無 N / rc 1  ㋒ 出鱈目 /detarame/naki/ne → 期待 実体無 N / rc 1
参考 ㋓ verify 基点 ""(cwd 相対)を cwd = 束の根で → 一致 N(cwd に依る故 使はぬ)。門は min(臺帳を file としても渡す・條②〜⑤を清い一本に)と all(臺帳の項 悉く)の二走 ―― rc は條で割る。"""
import os, sys, subprocess, re, time, hashlib
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; VP = M + '/scripts/checks/karo_mac_manifest_verify.py'; GATE = M + '/scripts/checks/karo_mac_dasumae_gate.sh'
sys.path.insert(0, M + '/scripts/checks'); import karo_mac_manifest_verify as V
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]
KISEI = ['km-47-yotsu-no-kazu-20260917', 'km-50-kara-wa-todokazu-20260917']; DETA = '/detarame/naki/ne'
out = [f'# 30 對照 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / verify.py sha16 {sha16(open(VP, "rb").read())} / 門 sha16 {sha16(open(GATE, "rb").read())} / cwd {M}(門・verify とも)']
tsv = [('束', '對照', '器', '渡した', 'rc', '母數', '一致', '相違', '実体無', '讀めぬ', '旧形', '基点の文言', '期待通り')]
def save(tag, p):
    K.kaku(f'{E}/30_{tag}.out', p.stdout.decode('utf-8', 'replace')); K.kaku(f'{E}/30_{tag}.err', p.stderr.decode('utf-8', 'replace')); K.kaku(f'{E}/30_{tag}.rc', str(p.returncode))
def yon(so):
    j = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', so); k = re.search(r'基点 ([^\n]*)', so); q = re.search(r'★旧形\(引用符を含む行\)★ (\d+) 行', so)
    return (j.group(5), j.group(1), j.group(2), j.group(3), j.group(4)) if j else ('?',) * 5, (k.group(1).strip()[:60] if k else '?'), (q.group(1) if q else '?')
allok = True
for km in KISEI:
    BD = M + '/docs/evidence/' + km; MAN = E + '/saiken/' + km + '_manifest.txt'; k5 = km[:5]
    rows = []
    for raw in open(MAN, encoding='utf-8'):
        s = raw.strip()
        if s and not s.startswith('#') and V.SHA.search(s): rows.append(V.paths_of(s)[0])
    N = len(rows); out.append(f'## {km} / 臺帳 raw/saiken/{km}_manifest.txt 項 {N} / 束の根 {BD}')
    for lab, argv, cwd, kitai in (('㋐明示基点=束の根', [MAN, BD], M, ('0', N, 0)), ('㋑基点無し(既定=repo根)', [MAN], M, ('1', 0, N)), ('㋒出鱈目', [MAN, DETA], M, ('1', 0, N)), ('㋓参考 基点""・cwd=束の根', [MAN, ''], BD, ('0', N, 0))):
        p = subprocess.run(['python3', '-B', VP] + argv, capture_output=True, cwd=cwd); save(f'{k5}_{lab[0]}_verify', p); so = p.stdout.decode('utf-8', 'replace')
        (bo, ic, so_, mi, yo), kt, ky = yon(so); ok = (str(p.returncode) == kitai[0] and ic == str(kitai[1]) and mi == str(kitai[2]) and bo == str(N))
        allok = allok and (ok or lab.startswith('㋓')); tsv.append((k5, lab, 'verify', ' '.join(a.replace(M + '/', '') or '""' for a in argv[1:]) or '(無)', p.returncode, bo, ic, so_, mi, yo, ky, kt, ok))
        out.append(f'{lab} verify 直(cwd {"束の根" if cwd == BD else "main 樹"}): rc {p.returncode} / 母數 {bo} 一致 {ic} 相違 {so_} 実体無 {mi} 讀めぬ {yo} 旧形 {ky} / 基点 {kt} / 期待(rc {kitai[0]}・一致 {kitai[1]}・実体無 {kitai[2]}) {"通" if ok else "★外れ★"}')
    for lab, envv, kitai in (('㋐明示基点=束の根', BD, '0'), ('㋑基点無し(unset・既定=repo根)', None, '1'), ('㋒出鱈目', DETA, '1')):
        env = dict(os.environ); env.pop('KM_GATE_MANIFEST_BASE', None)
        if envv is not None: env['KM_GATE_MANIFEST_BASE'] = envv
        for fl, files in (('min', [MAN]), ('all', [os.path.join(BD, r) for r in rows])):
            p = subprocess.run(['bash', GATE, MAN] + files, capture_output=True, cwd=M, env=env); save(f'{k5}_{lab[0]}_gate_{fl}', p)
            so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace'); (bo, ic, so_, mi, yo), kt, ky = yon(so)
            j1 = [l for l in se.split('\n') if l.startswith('條① 基点') or l.startswith('★條①') or l.startswith('條① 台帳')]; j234 = [l for l in se.split('\n') if re.match(r'★?條[②③④]', l)]; j5 = [l for l in se.split('\n') if '條⑤' in l]; ketsu = [l for l in se.split('\n') if l.startswith('★出す前')]
            j1_ochi = any(l.startswith('★條①') for l in j1); j234_ochi = sum(1 for l in j234 if l.startswith('★')); j5_ochi = any(l.startswith('★條⑤') for l in j5)
            ok = (str(p.returncode) == kitai) if fl == 'min' else ((not j1_ochi) if kitai == '0' else j1_ochi)
            allok = allok and ok; tsv.append((k5, lab, f'門 {fl}', len(files), p.returncode, bo, ic, so_, mi, yo, ky, kt, ok))
            out.append(f'{lab} 門 {fl}(渡した {len(files)}): rc {p.returncode} / 條① {"★落★" if j1_ochi else "通"}[{bo}/{ic}/{so_}/{mi}/{yo}] 基点の文言 {[l for l in j1 if "基点" in l][0][:48] if any("基点" in l for l in j1) else "?"} / 條②③④ 鳴 {j234_ochi} / 條⑤ {"★超★" if j5_ochi else (re.search(r"byte和 (\d+)", se).group(1) if re.search(r"byte和 (\d+)", se) else "?")} / 結語 {ketsu[0] if ketsu else "?"} / 期待(rc {kitai}{"・條①で判ず" if fl == "all" else ""}) {"通" if ok else "★外れ★"}')
            for l in j234[:4]:
                if l.startswith('★'): out.append('    ' + l.replace(BD + '/', '')[:140])
out.append('## 結: ' + ('★三本とも期待通り ―― 明示基点で 一致 N / 実体無 0 / rc 0、既定基点と出鱈目で 実体無 N / rc 1。建て直せて居る。★' if allok else '★期待と外れた對照が在る ―― 上の ★外れ★ を讀め★'))
K.kaku(E + '/30_taishou.txt', '\n'.join(out)); K.kaku_tsv(E + '/30_taishou.tsv', tsv[1:], tsv[0]); print('\n'.join(out)); sys.exit(0 if allok else 1)
