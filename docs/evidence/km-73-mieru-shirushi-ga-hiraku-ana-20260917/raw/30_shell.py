# -*- coding: utf-8 -*-
"""㋒ 器が bash か否か 30 ―― 四器の shebang・${v//pat/rep} と $'\\n' の既存使用数・呼び手(誰が何で起動するか)・
乙の台を bash3.2 / sh(=bash posix) / dash / zsh / env bash で実走・生器四本を各 shell の -n(構文のみ・起動せず)に掛ける。"""
import os, sys, re, subprocess, time, glob
D = sys.argv[1]; E = D + '/raw'; sys.path.insert(0, E); import kaki as K, dai73 as T
M = T.M; out = [f'# 30 器が bash か / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}']
SH = [('/bin/bash', '/bin/bash'), ('/bin/sh', '/bin/sh'), ('/bin/dash', '/bin/dash'), ('/bin/zsh', '/bin/zsh'), ('env bash', subprocess.run(['/usr/bin/env', 'bash', '-c', 'command -v bash'], capture_output=True, text=True).stdout.strip())]
ver = {n: subprocess.run([p, '-c', 'echo "${BASH_VERSION:-${ZSH_VERSION:-(版の変数無し=dash か)}}"'], capture_output=True, text=True).stdout.strip() for n, p in SH}
out.append('shell の版: ' + ' / '.join(f'{n}({p}) {ver[n]}' for n, p in SH) + f' / /var/select/sh → {os.readlink("/var/select/sh") if os.path.islink("/var/select/sh") else "-"}')
out.append('## ⑴ shebang と bash 固有の語の既存使用数(生器・讀むのみ)')
rows = []
for key, rel in T.TGT:
    s = open(M + '/' + rel, encoding='utf-8').read(); first = s.split('\n')[0]
    rows.append((rel, first, len(re.findall(r'\$\{[A-Za-z_][A-Za-z0-9_]*//', s)), len(re.findall(r"\$'", s)), len(re.findall(r'\[\[', s)), len(re.findall(r'\blocal\b', s)), len(re.findall(r'declare -A', s)), len(re.findall(r'\$\{[A-Za-z_][A-Za-z0-9_]*:[0-9]', s))))
K.kaku_tsv(E + '/30_shebang.tsv', rows, ['生器', 'shebang', '${v//', "$'", '[[', 'local', 'declare -A', '${v:N'])
out += ['  ' + '\t'.join(str(x) for x in r) for r in rows]
out.append('## ⑵ 呼び手(scripts/ .claude/ config/ ~/Library/LaunchAgents の grep・讀むのみ)―― shebang を跨いで sh で起動する呼び手が在るか')
names = [os.path.basename(rel) for _, rel in T.TGT]; hits = []
for root in (M + '/scripts', M + '/.claude', M + '/config', os.path.expanduser('~/Library/LaunchAgents')):
    for dp, ds, fs in os.walk(root):
        for f in fs:
            q = os.path.join(dp, f)
            try: t = open(q, encoding='utf-8', errors='replace').read()
            except Exception: continue
            for ln, l in enumerate(t.split('\n'), 1):
                for n in names:
                    if n in l and not l.lstrip().startswith('#'):
                        how = 'sh ' if re.search(r'(^|[\s/"])sh\s+\S*' + re.escape(n), l) else ('bash ' if re.search(r'bash\s+\S*' + re.escape(n), l) else ('直 exec' if re.search(r'(^|[\s"=])\S*' + re.escape(n) + r'\b', l) else '言及'))
                        hits.append((os.path.relpath(q, M) if q.startswith(M) else q, ln, n, how, l.strip()[:110]))
K.kaku_tsv(E + '/30_yobite.tsv', hits, ['file', '行', '器', '起動の形', '逐語(110字迄)'])
kind = {}
for h in hits: kind[(h[2], h[3])] = kind.get((h[2], h[3]), 0) + 1
out.append(f'  呼び手の行 {len(hits)} 本: ' + ' / '.join(f'{k[0]}←{k[1]}:{v}' for k, v in sorted(kind.items())) + ' ―― ★「sh <器>」の形 = ' + str(sum(v for k, v in kind.items() if k[1] == 'sh ')) + ' 本★')
out.append('## ⑶ 乙の台(watcher)を五つの shell で実走(値 = 1\\n偽札)―― ${v//$\'\\n\'/␊} が其の shell に在るか')
rows = []
for key, rel in T.TGT:
    for an in ('現行', '乙'):
        p = T.dai_path(E + '/dai', key, an)
        for n, sh in SH:
            rc, so, se = T.hashi(p, '1\n' + T.FAKE, shell=sh); y = T.yomite(se); t = se.decode('utf-8', 'surrogateescape')
            rows.append((rel, an, n, rc, y['LF'], '有' if '␊' in t else '無', '有' if "$'" in t or '\\n' in t else '無', T.out_of(so), T.esc(se)[:140]))
K.kaku_tsv(E + '/30_shell.tsv', rows, ['生器', '案', 'shell', 'rc', 'LF行', '␊が札に', "$'\\n'の字面が札に", 'OUT', 'stderr(esc)'])
for r in rows:
    if r[1] == '乙': out.append('  ' + '\t'.join(str(x) for x in r[:8]))
out.append('## ⑷ 小さな検め: 各 shell で v=$\'a\\nb\'; printf %s "${v//$\'\\n\'/␊}"')
for n, sh in SH:
    r = subprocess.run([sh, '-c', "v=$'a\\nb'; printf '%s' \"${v//$'\\n'/␊}\""], capture_output=True); out.append(f'  {n}: rc {r.returncode} stdout {T.esc(r.stdout)!r} stderr {T.esc(r.stderr)[:80]!r}')
out.append('## ⑸ 生器四本を各 shell の -n(構文のみ・起動せず)に掛ける ―― sh で走らせ得る器か')
rows = []
for key, rel in T.TGT:
    for n, sh in SH:
        r = subprocess.run([sh, '-n', M + '/' + rel], capture_output=True); rows.append((rel, n, r.returncode, T.esc(r.stderr)[:120]))
K.kaku_tsv(E + '/30_syntax.tsv', rows, ['生器', 'shell', '-n rc', 'stderr(esc)'])
out += ['  ' + '\t'.join(str(x) for x in r) for r in rows]
K.kaku(E + '/30_shell.txt', '\n'.join(out)); print('\n'.join(out))
