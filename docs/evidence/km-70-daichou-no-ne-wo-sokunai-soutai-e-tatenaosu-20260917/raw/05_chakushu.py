# -*- coding: utf-8 -*-
"""着手便の器 05(第70弾・第69弾の 05 を写して RN/宣/胴を改めた)。argv: <宛先> [--dry] [--swap] [--tag X]。
門 G1〜G7(宛先の形と名簿 / self-send / 死箱 / 胴が役職名の形 / 40..300 字 / work_started= 宣ETA= 端点 / 先送り語)を ★胴と封筒の中身★ に掛け、一つでも鳴れば送らぬ。
--dry = 門を通しても送らず封筒のみ(陰性対照)/ --swap = 宛先と胴を入れ替へて門へ(陽性対照・家老の空便の形)。送つた後は箱から逐語で讀み返す(第八の番人)。"""
import os, sys, re, time, glob, subprocess, hashlib
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; DEAD = {'gunshi-mac'}; RN = '70'
KM = 'km-70-daichou-no-ne-wo-sokunai-soutai-e-tatenaosu-20260917'
args = sys.argv[1:]; DRY = '--dry' in args; SWAP = '--swap' in args; TAG = None
pos = [a for a in args if not a.startswith('--')]
if '--tag' in args: TAG = args[args.index('--tag') + 1]; pos = [a for a in pos if a != TAG]
to = pos[0] if pos else ''
KI_N = 10; MIN_PER = 2.78; BAI = 1.5; SEN_MIN = round(KI_N * MIN_PER * BAI)  # 2.78 = (67: 3.95 + 68: 2.39 + 69: 2.01) / 3 分/器(席基準・紙と便を含む)
now_s = time.strftime('%Y-%m-%dT%H:%M:%S'); eta = time.strftime('%H:%M', time.localtime(time.time() + SEN_MIN * 60))
body = (f'★着手★ 第{RN}弾 km-70 臺帳を束内相対へ work_started={now_s[:16]} 宣ETA={eta}'
        f'(端点=納め便1本目の inbox_write 直前の date 刻・起点=本便・宣={KI_N}器×{MIN_PER}分/器×{BAI}={SEN_MIN}分)。'
        'km-47/50 の臺帳を cd 束+append.py で建て直し新束へ。對照㋐明示基点→一致N/実体無0 ㋑既定→実体無N/rc1 ㋒出鱈目→rc1 を verify+門で。'
        f'在處=main樹 docs/evidence/{KM}/')  # ★一走目(.first)366 字・二走目(.second)330 字・三走目(.third)312 字で己の G5 が鳴つた ―― 着手便は一通の條ゆゑ削つた
ROSTER = sorted(os.path.basename(p)[:-5] for p in glob.glob(M + '/queue/inbox/*.yaml') if not os.path.basename(p).startswith('_'))
def guard(to, body):
    naru = []
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{1,31}', to or ''): naru.append(f'G1 宛先の形が不正: {to[:40]!r}')
    elif to not in ROSTER: naru.append(f'G1 宛先が局所箱の名簿に無い: {to!r}')
    if to == ME: naru.append('G2 self-send')
    if to in DEAD: naru.append(f'G3 死箱: {to}')
    if body in ROSTER or re.fullmatch(r'[a-z0-9_-]+', body or ''): naru.append(f'G4 ★胴が役職名の形★ {body[:40]!r} = 宛先と胴が入れ替つた疑ひ(家老の空便四通の形)')
    if not (40 <= len(body) <= 300): naru.append(f'G5 字数 {len(body)} が 40..300 の外')
    for k in ('work_started=', '宣ETA=', '端点'):
        if k not in body: naru.append(f'G6 胴に {k} が無い')
    dg = os.path.expanduser('~/bin/deferral_gate.py')
    if os.path.isfile(dg):
        p = subprocess.run(['python3', '-B', dg], input=body.encode('utf-8'), capture_output=True)
        if p.returncode == 10: naru.append('G7 先送り語: ' + p.stdout.decode('utf-8', 'replace').strip()[:120])
    else: naru.append('G7 ★測れぬ★ deferral_gate.py が無い')
    return naru
g_to, g_body = (body, to) if SWAP else (to, body)
naru = guard(g_to, g_body)
out = [f'# 05 着手便の器(第{RN}弾)/ 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 札 {TAG or "本走"} / dry={DRY} swap={SWAP} / 宛先(門へ) {g_to[:40]!r} / 胴(門へ) 字数 {len(g_body)} 頭 {g_body[:40]!r}',
       f'名簿(queue/inbox/*.yaml・_ で始まる物を除く) {len(ROSTER)} 本: {" ".join(ROSTER)}', f'門 {"★鳴 " + str(len(naru)) + "★" if naru else "通(0 鳴)"}'] + ['  ' + n for n in naru]
if naru or DRY:
    out.append('★送らぬ★' + ('(門が鳴つた)' if naru else '(--dry・封筒のみ)')); out.append(f'封筒: bash scripts/inbox_write.sh {g_to!r} <胴 {len(g_body)} 字> report {ME}'); out.append('胴: ' + g_body)
    K.kaku(E + f'/05_chakushu.dry.{TAG or "x"}.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(1 if naru else 0)
koku = time.strftime('%Y-%m-%dT%H:%M:%S'); K.kaku(E + '/05_chakushu_koku.txt', koku)
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', g_to, g_body, 'report', ME], capture_output=True, cwd=M)
so = p.stdout.decode('utf-8', 'replace'); se = p.stderr.decode('utf-8', 'replace')
import yaml
ms = (yaml.safe_load(open(M + f'/queue/inbox/{g_to}.yaml', encoding='utf-8')) or {}).get('messages') or []
hit = [m for m in ms if m.get('from') == ME and str(m.get('content', '')).rstrip('\n') == g_body]
out += [f'送つた刻(直前・date と同じ) {koku} / inbox_write rc={p.returncode} / stdout {so.strip()[:160]!r} / stderr {se.strip()[:200]!r}', f'字数 {len(g_body)} / 胴 sha16 {hashlib.sha256(g_body.encode()).hexdigest()[:16]}',
        f'第八の番人(箱 queue/inbox/{g_to}.yaml・from={ME}・content 逐語一致): {len(hit)} 本 {[m["id"] for m in hit]} / 箱の字数 {[len(str(m.get("content", "")).rstrip(chr(10))) for m in hit]}', '胴: ' + g_body]
K.kaku(E + '/05_chakushu.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 3)
