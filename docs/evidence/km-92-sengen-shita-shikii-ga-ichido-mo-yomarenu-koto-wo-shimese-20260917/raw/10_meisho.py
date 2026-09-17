# -*- coding: utf-8 -*-
"""10 名の口(第81弾 km-92 ㋐)―― `DETECT_STALE_STALE_SEC` が真に一度も讀まれぬかを ★二器・二根★ で数へる。零には四つの札(陽性対照・根と深さ・rc・刻)。
器A= python os.walk(根= repo 根・深さ無制限・除外を宣す・file の中身を bytes で regex)。器B= `git grep -n -I -e <名>`(追跡 file 全て・docs/evidence/ を含む・rc を刷る)。
第三の根= ~/bin(lib を source し得る器の置き場)。加へて file の中の「口(代入)」と「讀手(展開 $X / ${X)」を分けて数へる(宣が 1 でも讀手が 0 なら死んで居る)。
陽性対照= DETECT_STALE_LOG(同 file の隣の宣・讀手が在る筈)/ 陰性対照= ZZ_KM92_NEG(在らぬ名)。己の束は path で除く(器が己を数へる疵の予防)。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; HB = os.path.expanduser('~/bin')
NAMES = ['DETECT_STALE_STALE_SEC', 'DETECT_STALE_LOG', 'ZZ_KM92_NEG', 'STALE_THRESHOLD_SEC']
EXCL_DIR = {'.git', 'queue', 'node_modules', '.venv', '__pycache__', 'backups', '.claude/worktrees'}
OWN = os.path.relpath(D, M)
def walk(root, excl_rel):
    n = 0; nb = 0; hits = {k: [] for k in NAMES}; skipped = 0
    for d, ds, fs in os.walk(root):
        rel = os.path.relpath(d, root)
        ds[:] = sorted(x for x in ds if x not in EXCL_DIR and os.path.normpath(os.path.join(rel, x)) not in excl_rel and os.path.normpath(os.path.join(rel, x)) not in EXCL_DIR)
        for f in fs:
            q = os.path.join(d, f)
            try:
                st = os.lstat(q)
                import stat as S_
                if not S_.S_ISREG(st.st_mode): skipped += 1; continue
                b = open(q, 'rb').read()
            except OSError: skipped += 1; continue
            n += 1; nb += len(b)
            for k in NAMES:
                for i, ln in enumerate(b.split(b'\n'), 1):
                    if k.encode() in ln: hits[k].append((os.path.relpath(q, root), i, ln.decode('utf-8', 'replace').strip()[:160]))
    return n, nb, hits, skipped
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
out = [f'# 10 名の口 ㋐ / 刻 {koku} / 名(逐語・部分一致 bytes) {NAMES} / 己の束 {OWN}(除く)']
# 器A 根1= repo 根(docs/evidence/ を除く) ／ 根1′= docs/evidence/ のみ(先例の束の写し・己の束除く)
n1, b1, h1, s1 = walk(M, {'docs/evidence'} | set(EXCL_DIR))
out.append(f'★器A 根1= {M} / 深さ無制限 / 除外(宣)= {sorted(EXCL_DIR)} + docs/evidence/ / 歩いた通常 file {n1} 本 {b1} bytes / 非通常・讀めぬ {s1} / rc 0(例外なし)★')
for k in NAMES: out.append(f'  {k}: {len(h1[k])} 行' + (''.join(f'\n    {p}:{i}: {t}' for p, i, t in h1[k][:12]) if h1[k] else ' ← ★零★'))
ev = M + '/docs/evidence'; n2, b2, h2, s2 = walk(ev, {OWN.split('/', 2)[2]})
out.append(f'器A 根1′= {ev} / 深さ無制限 / 己の束 {OWN.split("/")[-1]} を除く / 歩いた通常 file {n2} 本 {b2} bytes / 非通常 {s2}')
for k in NAMES: out.append(f'  {k}: {len(h2[k])} 行(束別: ' + ', '.join(f'{x} {c}' for x, c in sorted(__import__("collections").Counter(p.split("/")[0] for p, _, _ in h2[k]).items())) + ')' + (''.join(f'\n    {p}:{i}: {t}' for p, i, t in h2[k][:6]) if h2[k] else ''))
n3, b3, h3, s3 = walk(HB, set())
out.append(f'器A 根3= {HB} / 深さ無制限 / 歩いた通常 file {n3} 本 {b3} bytes / 非通常 {s3}')
for k in NAMES: out.append(f'  {k}: {len(h3[k])} 行' + (''.join(f'\n    {p}:{i}: {t}' for p, i, t in h3[k][:6]) if h3[k] else ''))
# 器B git grep(追跡 file 全て・docs/evidence 含む)
for k in NAMES:
    p = subprocess.run(['git', 'grep', '-n', '-I', '-e', k, '--', '.'], capture_output=True, text=True, cwd=M)
    lines = [x for x in p.stdout.split('\n') if x]; own = [x for x in lines if x.startswith(OWN)]; ev_ = [x for x in lines if x.startswith('docs/evidence/') and not x.startswith(OWN)]; rest = [x for x in lines if not x.startswith('docs/evidence/')]
    out.append(f'★器B `git grep -n -I -e {k} -- .`(追跡 file・repo 根)= rc {p.returncode} / {len(lines)} 行= docs/evidence/ 外 {len(rest)} + 先例の束 {len(ev_)} + 己の束 {len(own)}(未追跡ゆゑ 0 が正)★' + ''.join(f'\n    {x[:170]}' for x in rest[:12]))
# 口と讀手を分ける(器A 根1 の出目・DETECT_STALE_STALE_SEC と陽性対照)
for k in ('DETECT_STALE_STALE_SEC', 'DETECT_STALE_LOG'):
    kuchi = [(p, i, t) for p, i, t in h1[k] if re.match(r'^\s*(export\s+)?' + k + r'=', t)]
    yomite = [(p, i, t) for p, i, t in h1[k] if re.search(r'\$\{?' + k + r'\b', re.sub(r'^\s*(export\s+)?' + k + r'="?\$\{' + k + r':-[^}]*\}"?', '', t))]
    out.append(f'★{k}: 口(代入 `{k}=`) {len(kuchi)} 行 / 讀手(展開 `${k}` `${{{k}` ・己の宣の RHS `${{{k}:-…}}` は除く) {len(yomite)} 行★' + ''.join(f'\n    讀手 {p}:{i}: {t}' for p, i, t in yomite[:8]))
out.append('意味せぬ事: 器A は部分一致(語境界無し)ゆゑ多めに出る側(零なら真に零)。queue/ は 13GB ゆゑ器A で除く(追跡分は器B が歩く)。crontab/launchd/環境の export は歩いて居らぬ(次の行で crontab -l のみ刷る)。')
p = subprocess.run('crontab -l 2>&1', shell=True, capture_output=True, text=True); out.append(f'crontab -l rc {p.returncode}: ' + (p.stdout + p.stderr).strip().replace('\n', ' ␊ ')[:300])
p = subprocess.run('env | grep -c DETECT_STALE; env | grep DETECT_STALE', shell=True, capture_output=True, text=True); out.append('此の席の env に DETECT_STALE*: ' + (p.stdout.strip().replace('\n', ' ␊ ') or '0'))
K.kaku(D + '/raw/10_meisho.txt', '\n'.join(out)); print('\n'.join(out))
