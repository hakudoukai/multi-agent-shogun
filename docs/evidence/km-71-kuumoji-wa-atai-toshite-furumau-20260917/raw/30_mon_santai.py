# -*- coding: utf-8 -*-
"""30 門の基点 三態(第71弾 ㋑・据ゑず・讀取のみ)―― KM_GATE_MANIFEST_BASE を unset / 空文字 "" / "." の三態に分け、四臺帳(km-47・km-50 = 舊形 repo根相対 / km-70・自主束 = 束内相対)× cwd 二所(repo 根・其の束の根)= 24 走で 條① の通/落を実測。
門の argv = [臺帳, 臺帳](min 形・條②〜⑤を臺帳一本に掛け條①を孤立)。通/落は 條① で判ず(門の rc は條②〜⑤も混ざる故 別に記す)。共有器へ 0 byte・四束へ 0 byte(讀むのみ)。"""
import os, sys, subprocess, hashlib, re, time
assert sys.flags.dont_write_bytecode, '-B で走らせよ'
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; GATE = M + '/scripts/checks/karo_mac_dasumae_gate.sh'; VER = M + '/scripts/checks/karo_mac_manifest_verify.py'
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
MANS = [('km-47', '舊形(repo根相対)', 'docs/evidence/km-47-yotsu-no-kazu-20260917', 'ashigaru-mac-3_km-47-yotsu-no-kazu-20260917_manifest.txt'),
        ('km-50', '舊形(repo根相対)', 'docs/evidence/km-50-kara-wa-todokazu-20260917', 'km-50-kara-wa-todokazu-20260917_manifest.txt'),
        ('km-70', '束内相対', 'docs/evidence/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917', 'ashigaru-mac-1_km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917_manifest.txt'),
        ('a1-jishu', '束内相対', 'docs/evidence/a1-jishu-kuumoji-kiten-20260917', 'ashigaru-mac-1_a1-jishu-kuumoji-kiten-20260917_manifest.txt')]
STATES = [('unset', None), ('kuu', ''), ('dot', '.')]
def snap(d):
    rows = []
    for r, ds, fs in os.walk(d):
        for f in fs:
            q = os.path.join(r, f)
            if os.path.isfile(q) and not os.path.islink(q): rows.append(os.path.relpath(q, d) + ' ' + hashlib.sha256(open(q, 'rb').read()).hexdigest())
    rows.sort(); return hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16] + f'({len(rows)})'
mae = {k: snap(M + '/' + d) for k, _, d, _ in MANS}; g0, v0 = sha16(GATE), sha16(VER)
hdr = ('臺帳', '形', '基点', 'cwd', '門rc', '條①', '母數', '一致', '相違', '実体無', '読めぬ', '基点の札')
rows = []; tally = {}
for k, kind, d, mf in MANS:
    MAN = M + '/' + d + '/' + mf
    for sk, sv in STATES:
        for ck, cv in (('repo', M), ('taba', M + '/' + d)):
            env = dict(os.environ); env.pop('KM_GATE_MANIFEST_BASE', None)
            if sv is not None: env['KM_GATE_MANIFEST_BASE'] = sv
            p = subprocess.run(['bash', GATE, MAN, MAN], capture_output=True, cwd=cv, env=env); so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace'); key = f'{k}_{sk}_{ck}'
            K.kaku(f'{RAW}/30_{key}.out', so); K.kaku(f'{RAW}/30_{key}.err', se); K.kaku(f'{RAW}/30_{key}.rc', str(p.returncode))
            j = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', so); gq = j.groups() if j else ('−',) * 5
            j1 = '通' if '條① 台帳とdiskの差 = 一致' in se else ('落' if '條① 台帳とdiskの差が落ちた' in se else '−'); fuda = re.search(r'條① 基点=(.{0,26})', se); fuda = fuda.group(1) if fuda else '−'
            rows.append((k, kind, sk, ck, p.returncode, j1, gq[4], gq[0], gq[1], gq[2], gq[3], fuda)); tally.setdefault(sk, {}).setdefault(j1, 0); tally[sk][j1] += 1
K.kaku_tsv(RAW + '/30_mon_santai.tsv', rows, header=hdr)
out = [f'# 30 門の基点 三態 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {g0} / 照合器 sha16 {v0} / 走 {len(rows)} = 臺帳 4 × 態 3 × cwd 2 / argv=[臺帳, 臺帳]',
       '# 態: unset=環境変数を落とす / kuu=空文字 "" / dot="."(cwd 相対を字で明示)。cwd: repo=repo 根 / taba=其の臺帳の束の根',
       '| ' + ' | '.join(hdr) + ' |', '|' + '---|' * len(hdr)] + ['| ' + ' | '.join(str(x) for x in r) + ' |' for r in rows]
out.append('## ★條① 通/落 の数(態別・24 走中 各 8)★: ' + ' / '.join(f'{sk}: 通 {tally.get(sk, {}).get("通", 0)} 落 {tally.get(sk, {}).get("落", 0)} 不明 {tally.get(sk, {}).get("−", 0)}' for sk, _ in STATES))
for sk, _ in STATES:
    for kind in ('舊形(repo根相対)', '束内相対'):
        for ck in ('repo', 'taba'):
            sub = [r for r in rows if r[2] == sk and r[1] == kind and r[3] == ck]; out.append(f'  {sk} × {kind} × cwd={ck}: 通 {sum(1 for r in sub if r[5] == "通")} / 落 {sum(1 for r in sub if r[5] == "落")} (母數 {len(sub)})')
dep = [(k, sk) for k, _, _, _ in MANS for sk, _ in STATES if [r for r in rows if r[0] == k and r[2] == sk and r[3] == 'repo'][0][5] != [r for r in rows if r[0] == k and r[2] == sk and r[3] == 'taba'][0][5]]
out.append(f'## cwd で條①が反転した (臺帳, 態) = {len(dep)} 組 {dep} ―― unset は 0 組が期待(cwd に依らぬ既定)')
ato = {k: snap(M + '/' + d) for k, _, d, _ in MANS}; out.append(f'## 禁域と四束 前⇔後: 門 {g0}→{sha16(GATE)} / 照合器 {v0}→{sha16(VER)} / 束の印 ' + ' / '.join(f'{k} {mae[k]}→{ato[k]} {"同" if mae[k] == ato[k] else "★違★"}' for k in mae) + f' / 共有器 {"同" if (g0, v0) == (sha16(GATE), sha16(VER)) else "★違★"}')
K.kaku(RAW + '/30_mon_santai.txt', '\n'.join(out)); print('\n'.join(out[:2] + out[4 + len(rows):]))
sys.exit(0 if mae == ato and (g0, v0) == (sha16(GATE), sha16(VER)) else 1)
