# -*- coding: utf-8 -*-
"""㋑ 終端(人の目)の讀手 25 ―― 乙の札を ★tmux の私設 socket(-L km73・誰の pane でもない・send-keys は使はぬ)★ に cat させ、capture-pane(讀むのみ)で「画面の行数」を数へる。
pyte は無い(ModuleNotFoundError)ゆゑ tmux の端末機構を讀手とする。陽性対照 = 現行 + \\n(2 行の筈)・陰性 = abc(1 行の筈)。
★疵(初走 .first)★: new-session に -s を付けず session 名が「0」に成り、capture-pane -t km73:0 が的を外して 0 行 ―― 陽性対照が 0 で鳴つた故に判つた(陽性対照無くば「乙は画面でも一行」と書いて居た)。札は束外 ~/km73-utsushi-20260917/ へ置く。"""
import os, sys, time, subprocess, shutil
D = sys.argv[1]; E = D + '/raw'; sys.path.insert(0, E); import kaki as K, dai73 as T
S = os.path.expanduser('~/km73-utsushi-20260917'); os.makedirs(S, exist_ok=True); TM = shutil.which('tmux'); L = 'km73'
NAMED = [('LF \\n', '\n'), ('CR \\r', '\r'), ('TAB \\t', '\t'), ('VT \\v', '\x0b'), ('FF \\f', '\x0c'), ('BS \\b', '\x08'), ('ESC', '\x1b'), ('ESC[2K', '\x1b[2K'), ('U+2028 LS', ' '), ('U+2029 PS', ' '), ('U+0085 NEL', '\x85'), ('U+00A0 NBSP', '\xa0'), ('U+3000 全角空白', '　')]
rows = []; out = [f'# 25 終端の讀手 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / tmux {TM} / socket -L {L}(私設・他の誰の pane でもない・send-keys 0)']
def screen(fuda, tag):
    fp = os.path.join(S, 'fuda_%s.bin' % tag); open(fp, 'wb').write(fuda)
    subprocess.run([TM, '-L', L, 'kill-server'], capture_output=True)
    r = subprocess.run([TM, '-L', L, 'new-session', '-d', '-s', L, '-x', '240', '-y', '15', "cat '%s'; sleep 20" % fp], capture_output=True, text=True)
    time.sleep(0.4); c = subprocess.run([TM, '-L', L, 'capture-pane', '-p', '-t', L + ':0'], capture_output=True)
    subprocess.run([TM, '-L', L, 'kill-server'], capture_output=True)
    lines = [l for l in c.stdout.decode('utf-8', 'replace').split('\n') if l.strip()]; return len(lines), T.esc(c.stdout)[:150].replace('\n', '⏎')
i = 0
for an, nm, ch in [('現行', '陽性対照 LF \\n', '\n'), ('乙', '陰性対照 abc', None)] + [('乙', nm, ch) for nm, ch in NAMED]:
    p = T.dai_path(E + '/dai', 'watcher', an); v = 'abc' if ch is None else '1' + ch + T.FAKE; i += 1
    rc, so, se = T.hashi(p, v); n, scr = screen(se, '%02d' % i); rows.append((an, nm, T.yomite(se)['LF'], n, scr))
K.kaku_tsv(E + '/25_terminal.tsv', rows, ['案', '形', 'LF讀手の行', '★画面の行(tmux capture-pane・非空)★', '画面(esc・150字迄)'])
pos = rows[0][3]; neg = rows[1][3]; two = [r for r in rows[2:] if r[3] >= 2]
out.append(f'陽性対照(現行+\\n)画面 {pos} 行 / 陰性対照(abc)画面 {neg} 行 / 乙で画面が ≥2 行に成つた形 {len(two)}/{len(rows)-2}: ' + ' / '.join(f'{r[1]}={r[3]}' for r in two))
out.append('読み: 画面の行は「LF 讀手」とも「py.splitlines」とも別の數 ―― 人の目には VT/FF が改行に見える端末が多い(tmux の機構で測つた・他の端末では測つて居らぬ)。')
K.kaku(E + '/25_terminal.txt', '\n'.join(out)); print('\n'.join(out)); print('\n'.join('\t'.join(str(x) for x in r[:4]) for r in rows))
