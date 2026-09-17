# -*- coding: utf-8 -*-
"""00_heihou.py ―― ★閉包(closure)を、測る前に定義し、追跡で閉ぢる★。

★宣(定義)★ ―― 本弾で「要る器」と呼ぶ物は、次の一文で尽きる:
  「★一つの束の臺帳を建て、出す前門を通し、其の出目を検めるまでに、實際に process として
    起動される器★」。起点は二本のみ ―― 臺帳の唯一の書き手 karo_mac_manifest_append.py と、
    門 karo_mac_dasumae_gate.sh。此の二本から ★呼出の連鎖を辿つて★ 閉ぢる。

★宣の外(測らぬ物)を先に名指す ―― 後から「入れ忘れ」と言はれぬ為★:
  ⑴ 便の器(inbox_write.sh / inbox_mark_read.py / sb *) ―― ★臺帳も門も呼ばぬ★。
  ⑵ 束ごとの私器(_inst/, _saisou/, kaki 等) ―― 束と共に commit される ∴「版に無い」問に掛からぬ。
  ⑶ 番人(hook)類(pretooluse_bash_guard.sh, dd169_kill_term_guard.sh 等) ―― 門の連鎖の外。
     ★但し context_usage_warn.sh は家老が「中身異」と名指した ∴ 丁(宣外だが名指された物)として
       表には載せ、甲乙丙の判じからは外す。★「外した」は「無い」の意に非ず。★
  ⑷ python 標準ライブラリ ―― repo の物に非ず。
  ⑸ /bin/sh, git, grep 等の系の器 ―― repo が運ぶ物に非ず。

★追跡の仕方(機械)★:
  ・shell: `python3 <path>` / `bash <path>` / `sh <path>` / `source <path>` / `. <path>`
    ＋ `$(dirname "$0")/<name>` の形
  ・python: `subprocess` の argv 先頭 / `import` の内 repo 由来
  各当りを ★逐語の行★ ごと録る(数だけでなく「何處の何行が呼んで居るか」を残す)。
  見付けた器は ★同じ規で再び走査★ し、新しい当りが尽きるまで繰り返す(不動点)。

出目: _raw/01_heihou.tsv   閉包の器(一本一行)
      _raw/02_yobidashi.tsv 呼出の辺(呼ぶ側 / 行 / 逐語 / 呼ばれる側)
"""
import os, re, sys

NE = '/Users/momizimac/multi-agent-shogun'
CHK = os.path.join(NE, 'scripts/checks')
KIT = ['scripts/checks/karo_mac_manifest_append.py',
       'scripts/checks/karo_mac_dasumae_gate.sh']     # ★起点は此の二本のみ★

# 宣外(⑴〜⑸)。当りが此に落ちたら辺は録るが、閉包には入れぬ。
SYS = {'python3','python','bash','sh','git','grep','sed','awk','cat','date','shasum',
       'find','sort','uniq','wc','cmp','tee','mkdir','rm','cp','mv','printf','echo'}

def yomu(rel):
    p = os.path.join(NE, rel)
    try:
        return open(p, encoding='utf-8', errors='replace').read()
    except OSError as e:
        return None

# ―― 当りの規(逐語で残す) ――――――――――――――――――――――――
SH = [
    (r'\$\(dirname\s+"?\$0"?\)/([A-Za-z0-9_.\-]+)', 'dirname相対'),
    (r'(?:^|[;&|(]\s*|\s)(?:python3|python|bash|sh)\s+"?([A-Za-z0-9_./\-${}"]*[A-Za-z0-9_.\-]+\.(?:py|sh))"?', '直呼び'),
    (r'(?:^|\s)(?:source|\.)\s+"?([A-Za-z0-9_./\-${}"]*[A-Za-z0-9_.\-]+\.(?:sh|bash))"?', '読込み'),
]
PY = [
    (r'subprocess\.(?:run|Popen|call|check_output)\(\s*\[?\s*[\'"]([^\'"]+)[\'"]', 'subprocess'),
    (r'^\s*(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)', 'import'),
]

def atari(rel, s):
    out = []
    rules = PY if rel.endswith('.py') else SH
    for i, line in enumerate(s.split('\n'), 1):
        if line.lstrip().startswith('#'):
            continue
        for pat, kind in rules:
            for m in re.finditer(pat, line, re.M):
                out.append((i, kind, m.group(1), line.strip()))
    return out

heihou, hen, machi, mita = {}, [], list(KIT), set()
while machi:
    rel = machi.pop(0)
    if rel in mita: continue
    mita.add(rel)
    s = yomu(rel)
    heihou[rel] = ('読めた' if s is not None else '★読めぬ★')
    if s is None: continue
    for ln, kind, tgt, gyo in atari(rel, s):
        base = os.path.basename(tgt)
        # 系の器・標準ライブラリは辺に録るのみ
        if base in SYS or (kind == 'import' and not os.path.exists(os.path.join(CHK, base + '.py'))):
            hen.append((rel, ln, kind, tgt, '―', '宣外(系/標準)', gyo))
            continue
        cand = os.path.join('scripts/checks', base)
        if os.path.exists(os.path.join(NE, cand)):
            hen.append((rel, ln, kind, tgt, cand, '★閉包へ★', gyo))
            if cand not in mita: machi.append(cand)
        else:
            hen.append((rel, ln, kind, tgt, base, '★見当らぬ★', gyo))

B = os.path.join(NE, 'docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917')
with open(os.path.join(B, '_raw/01_heihou.tsv'), 'w', encoding='utf-8') as f:
    f.write('# 閉包 ―― 起点=%s / 不動点まで走査\n' % ' , '.join(KIT))
    f.write('# 刻=%s\n' % __import__('subprocess').run(['date','+%Y-%m-%dT%H:%M:%S'],
            capture_output=True, text=True).stdout.strip())
    f.write('path\tyomi\n')
    for k in sorted(heihou): f.write('%s\t%s\n' % (k, heihou[k]))
with open(os.path.join(B, '_raw/02_yobidashi.tsv'), 'w', encoding='utf-8') as f:
    f.write('yobu\tgyo\tkata\tmojizura\tyobareru\thanji\tgyo_chikugo\n')
    for e in hen: f.write('%s\t%d\t%s\t%s\t%s\t%s\t%s\n' % e)

print('★閉包の定義は上の docstring に在る(測る前に宣つた)★')
print('閉包の器 = ★%d本★' % len(heihou))
for k in sorted(heihou): print('   %s  (%s)' % (k, heihou[k]))
print('呼出の辺 = %d本 / 内 ★閉包へ★=%d / 見当らぬ=%d / 宣外=%d'
      % (len(hen), sum(1 for e in hen if e[5]=='★閉包へ★'),
         sum(1 for e in hen if e[5]=='★見当らぬ★'), sum(1 for e in hen if e[5].startswith('宣外'))))
print('★閉包へ★ の辺(逐語):')
for e in hen:
    if e[5]=='★閉包へ★': print('   %s:%d [%s] %s' % (e[0], e[1], e[2], e[6][:88]))
print('★見当らぬ★ の辺:')
for e in hen:
    if e[5]=='★見当らぬ★': print('   %s:%d [%s] %s → %s' % (e[0], e[1], e[2], e[3], e[4]))
