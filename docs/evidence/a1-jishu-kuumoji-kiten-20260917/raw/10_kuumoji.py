# -*- coding: utf-8 -*-
"""10 空文字基点の測り(自主束・km-70 便5「基点の口が空文字の時は未測」の埋め)。
的: 門 L197 `${KM_GATE_MANIFEST_BASE+set}` は空文字でも set を返し、verify.py L97 `argv[2:]` は [''] を真とし base_src=「引数(明示)」を刷る。
   L146 `os.path.join(b, p) if b else p` は b='' で ★cwd 相対★ ―― ∴ 札は「明示」・出目は cwd 次第、が予想。
形: 二器(verify 直 / 門 main=[臺帳, 紙, 臺帳])× 基点四態(unset / 明示=束の根 / 空文字 "" / 空白 " ")× cwd 二所(repo 根 / km-70 束の根)= 16 走。
臺帳は km-70 の凍結済(束内相対・項 139)。★共有器へ 0 byte・km-70 束へ 0 byte(讀むのみ・raw/ は 0555 の儘)★。"""
import os, sys, subprocess, hashlib, re, time
assert sys.flags.dont_write_bytecode, '-B で走らせよ'
B = sys.argv[1]; RAW = B + '/raw'; sys.path.insert(0, RAW); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; GATE = M + '/scripts/checks/karo_mac_dasumae_gate.sh'; VER = M + '/scripts/checks/karo_mac_manifest_verify.py'
KM70 = M + '/docs/evidence/km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917'; MAN = KM70 + '/ashigaru-mac-1_km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917_manifest.txt'; PAPER = KM70 + '/ashigaru-mac-1_km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917.md'
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
def snap(d):
    rows = []
    for r, ds, fs in os.walk(d):
        for f in fs:
            q = os.path.join(r, f)
            if os.path.isfile(q) and not os.path.islink(q): rows.append(os.path.relpath(q, d) + ' ' + hashlib.sha256(open(q, 'rb').read()).hexdigest())
    rows.sort(); return hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16], len(rows)
mae = {'gate': sha16(GATE), 'verify': sha16(VER), 'km70': snap(KM70)}
out = [f'# 10 空文字基点の測り / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 門 sha16 {mae["gate"]} / 照合器 sha16 {mae["verify"]} / 臺帳 {os.path.relpath(MAN, M)} sha16 {sha16(MAN)} / km-70 束の印 {mae["km70"]}',
       '# 基点四態: unset=環境変数を落とす / meiji=束の根(絶対) / kuu=空文字 "" / kuuhaku=空白一つ " " ―― 門は KM_GATE_MANIFEST_BASE で、verify 直は argv[2] で同じ値を渡す(unset は argv[2] 無し)',
       '# 期待(讀んだ逐語から): kuu は札「引数(明示)」の儘 cwd 相対 ∴ cwd=repo根 → 実体無 139 rc1 / cwd=束の根 → 一致 139 rc0。kuuhaku は os.path.join(" ", p)=" /…" ∴ 両 cwd で実体無 139 rc1・札「明示」。unset は既定(repo 根)で実体無 139 rc1。meiji は両 cwd で一致 139 rc0']
tsv = [('器', '基点', 'cwd', 'rc', '母數', '一致', '相違', '実体無', '読めぬ', '基点の札', 'cwd依存', '期待通り')]
BASES = [('unset', None), ('meiji', KM70), ('kuu', ''), ('kuuhaku', ' ')]; CWDS = [('repo', M), ('taba', KM70)]
res = {}
for tool in ('verify', 'gate'):
    for bk, bv in BASES:
        for ck, cv in CWDS:
            key = f'{tool}_{bk}_{ck}'; env = dict(os.environ); env.pop('KM_GATE_MANIFEST_BASE', None)
            if tool == 'verify': argv = ['python3', '-B', VER, MAN] + ([] if bv is None else [bv])
            else:
                argv = ['bash', GATE, MAN, PAPER, MAN]
                if bv is not None: env['KM_GATE_MANIFEST_BASE'] = bv
            p = subprocess.run(argv, capture_output=True, cwd=cv, env=env); so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace')
            K.kaku(f'{RAW}/10_{key}.out', so); K.kaku(f'{RAW}/10_{key}.err', se); K.kaku(f'{RAW}/10_{key}.rc', str(p.returncode)); K.kaku(f'{RAW}/10_{key}.argv', f'# cwd={cv} / KM_GATE_MANIFEST_BASE={"(unset)" if (tool=="gate" and bv is None) else repr(bv) if tool=="gate" else "(argv)"}\n' + '\n'.join(repr(a) for a in argv))
            j = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', so); fuda = re.search(r'基点 (.+)', so); fuda = fuda.group(1).strip()[:30] if fuda else '−'
            g = j.groups() if j else ('−',) * 5; res[key] = (p.returncode, g, fuda)
            tsv.append((tool, bk, ck, p.returncode, g[4], g[0], g[1], g[2], g[3], fuda, '', ''))
# cwd 依存 = 同じ器・同じ基点で cwd を変へたら (rc, 四数) が変はるか
rows = list(tsv[1:]); tsv = [tsv[0]]
for r in rows:
    tool, bk, ck = r[0], r[1], r[2]; a = res[f'{tool}_{bk}_repo']; b = res[f'{tool}_{bk}_taba']; dep = 'cwd依存★' if (a[0], a[1]) != (b[0], b[1]) else '不依存'
    rc, g = res[f'{tool}_{bk}_{ck}'][0], res[f'{tool}_{bk}_{ck}'][1]
    kitai = {'unset': ('1', '0', '139'), 'meiji': ('0', '139', '0'), 'kuu': ('1', '0', '139') if ck == 'repo' else ('0', '139', '0'), 'kuuhaku': ('1', '0', '139')}[bk]
    ok = (str(rc), g[0], g[2]) == kitai; tsv.append(r[:10] + (dep, 'True' if ok else '★外れ★'))
K.kaku_tsv(RAW + '/10_kuumoji.tsv', tsv[1:], header=tsv[0])
out.append('| ' + ' | '.join(tsv[0]) + ' |'); out.append('|' + '---|' * len(tsv[0]))
for r in tsv[1:]: out.append('| ' + ' | '.join(str(x) for x in r) + ' |')
hazure = [r for r in tsv[1:] if r[-1] != 'True']; out.append(f'外れ {len(hazure)} 行 / 母數 {len(tsv)-1} 走')
# 門の札の逐語(kuu の二走)
for ck in ('repo', 'taba'):
    se = open(f'{RAW}/10_gate_kuu_{ck}.err', encoding='utf-8').read(); kt = [l for l in se.split('\n') if l.startswith('條① 基点') or l.startswith('★出す前')]
    out.append(f'門 kuu cwd={ck}: ' + ' / '.join(kt))
ato = {'gate': sha16(GATE), 'verify': sha16(VER), 'km70': snap(KM70)}
out.append(f'禁域と km-70 束 前⇔後: 門 {mae["gate"]}→{ato["gate"]} {"同" if mae["gate"]==ato["gate"] else "★違★"} / 照合器 {mae["verify"]}→{ato["verify"]} {"同" if mae["verify"]==ato["verify"] else "★違★"} / km-70 印 {mae["km70"]}→{ato["km70"]} {"同" if mae["km70"]==ato["km70"] else "★違★"}')
K.kaku(RAW + '/10_kuumoji.txt', '\n'.join(out)); print('\n'.join(out))
sys.exit(0 if not hazure and mae == ato else 1)
