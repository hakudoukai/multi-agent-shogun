# -*- coding: utf-8 -*-
"""讀手の則(第79弾 km-86・10 と 20 が共に使ふ= 二重実装せぬ)―― 或る env 名 N(python は別名も)を参照する ★註でない行★ を、下流で何に成るかで分ける。
害の類(㋑): ⑴ tmux の target(-t の右・send-keys/capture-pane/display-message 等) ⑵ session 名(has-session/new-session/kill-session/attach/-s の右・名に SESSION) ⑶ path/dir(test -f/-d…・cat/ls/mkdir/…・"$N/"・リダイレクト・python open/Path/os.path) ⑷ topic/宛先 role(inbox_write.sh の第一引数・--to・queue/inbox/$N・target_agent/topic/pc_handshake) ⑸ 比較(= == != の左右・case・=~・python ==/in)。
數の讀手(閾の証)= -eq -ne -gt -ge -lt -le・(( ))・$(( ))・python int()/数との比較。讀まぬ参照= 伝(echo/log/printf/export/子器へ env 渡し)・口(受ける口)・他。"""
import re
def _ref(N): return r'\$\{?' + re.escape(N) + r'(?![A-Za-z0-9_])'
def strip_comment_sh(l):  # ★二走: 単引用符の中は展開されぬゆゑ落とす(bash -c '…' の内側は例外・疵に書く)
    return '' if l.lstrip().startswith('#') else re.sub(r"'[^']*'", "''", re.sub(r'\s#.*$', '', l))
def strip_comment_py(l):  # ★二走: 文字列 literal の中の名は参照でない(f-string の {…} を含む物だけ残す)
    if l.lstrip().startswith('#'): return ''
    s = l.split('#', 1)[0]
    return re.sub(r'"(?:\\.|[^"\\{])*"|\'(?:\\.|[^\'\\{])*\'', '""', s)
CMDS_PATH = r'(cat|head|tail|ls|mkdir|touch|rm|cp|mv|source|cd|find|stat|wc|chmod|chown|ln|tee|readlink|realpath|dirname|basename|du|flock|diff|cmp|tar|zip|unzip|file|less|more|install|rsync|scp|shasum|sha256sum|md5|jq|yq|sqlite3|git -C|inotifywait|fswatch)'  # ★三走: python3/bash/sh/nohup/exec/sed/awk/grep/sort/cut は path とは限らぬ(引数が文でも当たる)ゆゑ外す
def classes_sh(N, l):
    s = strip_comment_sh(l); R = _ref(N); c = set()
    if not re.search(R, s): return c, s
    seg = s
    # ⑴⑵ tmux
    for m in re.finditer(r'\btmux\b[^|;&]*', s):
        t = m.group(0)
        if not re.search(R, t): continue
        if not (re.search(r'\s-[ts]\s+"?' + R, t) or re.search(r'\s-[ts]\s+"?\$\{?[A-Za-z_][A-Za-z0-9_]*\}?"?[:.]', t) and re.search(R, t)): continue  # ★二走: -t/-s の右に名が無ければ文(prose)と見て数へぬ
        if re.search(r'\b(has-session|new-session|kill-session|attach(-session)?|switch-client|rename-session)\b', t) or re.search(r'-s\s+"?' + R, t) or 'SESSION' in N: c.add('⑵')
        else: c.add('⑴')
    # ⑷ 宛先/topic
    if re.search(r'inbox_write\.sh"?\s+"?' + R, s) or re.search(r'--to[= ]"?' + R, s) or re.search(r'queue/inbox/"?' + R, s) or re.search(r'(target_agent|topic|pc_handshake|agent_letter|sb write|receiver|recipient|to_pc)[^|;&]*' + R, s) or re.search(r'(inbox_write\.sh|send_inbox|inbox_write)\s+"?\$\{?\w+\}?"?\s+[^|;&]*' + R + r'[^|;&]*\s+\S+\s+"?' + R, s): c.add('⑷')
    # ⑶ path/dir/file
    envpass = re.sub(r'\b[A-Za-z_][A-Za-z0-9_]*="?\$\{?' + re.escape(N) + r'\}?"?', 'ENVPASS', s)  # ★三走: `env X="$N" cmd` / `X="$N"` の形は伝(子器へ渡す)であつて path でない
    if (re.search(r'\[\[?\s+(!\s+)?-[fdersxwLhpcbSgkuOGN]\s+"?' + R, s) or re.search(r'(^|[\s;|&(])' + CMDS_PATH + r'\s[^|;&]*' + R, envpass) or re.search(r'"' + R + r'\}?/', s) or re.search(R + r'\}?"?/', s) or re.search(r'[^$]/' + R, s) or re.search(r'[<>]{1,2}\s*"?' + R, s) or re.search(r'--?(file|dir|path|log|out|output|config|cfg|manifest|root|base)[= ]"?' + R, s) or re.search(r'\$\(<\s*"?' + R, s) or re.search(r'\bcd\s+"?' + R, s)): c.add('⑶')
    # ⑸ 比較(字面)
    intest = re.search(r'(^|[\s;(&|!])(\[\[?|test)\s', s) is not None  # ★三走: 比較は test の中か case のみ(代入 X="$N" を比較と誤つた)
    if (intest and (re.search(r'\[\[?\s[^\]]*"?' + R + r'\}?"?\s*(==|!=|=|=~)\s', s) or re.search(r'(==|!=|=|=~)\s*"?' + R + r'\}?"?\s*(\]|\)|&&|\|\||;|$)', s))) or re.search(r'\bcase\s+"?' + R, s): c.add('⑸')
    # 數
    if re.search(r'"?' + R + r'\}?"?\s*-(eq|ne|gt|ge|lt|le)\s', s) or re.search(r'-(eq|ne|gt|ge|lt|le)\s+"?' + R, s) or re.search(r'\(\([^)]*' + R + r'[^)]*\)\)', s) or re.search(r'\$\(\([^)]*' + R, s) or re.search(r'\b(sleep|timeout|head -n|tail -n|seq|expr)\s+"?' + R, s) or re.search(r'\[\[?\s[^\]]*"?' + R + r'\}?"?\s*[<>]\s', s): c.add('數')
    if not c:
        if re.search(r'^\s*' + re.escape(N) + r'="?\$\{' + re.escape(N) + r'[^}]*\}"?\s*$', s) or re.search(r'^\s*(export\s+)?' + re.escape(N) + r'="?\$\{' + re.escape(N), s) or re.search(r'^\s*fix_(flag|threshold)\s+' + re.escape(N), s) or re.search(r'^\s*:\s+"?\$\{' + re.escape(N), s): c.add('口')
        elif re.search(r'^\s*(export|local|readonly|declare)\s', s) or re.search(r'\b(echo|printf|log|say|log_struct|_th_say|_log|logger|log_info|log_warn|log_error|warn|die|info|debug)\b', s) or re.search(r'^\s*[A-Za-z_][A-Za-z0-9_]*=', s) or re.search(r'\b(env|export)\b[^|;&]*' + re.escape(N) + r'=', s): c.add('伝')
        else: c.add('他')
    return c, s
def classes_py(N, alias, l):
    s = strip_comment_py(l); c = set(); names = [N] + sorted(alias)
    A = r'(?<![A-Za-z0-9_.])(' + '|'.join(re.escape(n) for n in names) + r')(?![A-Za-z0-9_])'
    if not re.search(A, s): return c, s
    if re.search(r'\btmux\b', s) and re.search(r'-[ts]\b', s) and re.search(A, s): c.add('⑵' if 'SESSION' in N else '⑴')
    if re.search(r'(target_agent|topic|to_pc|receiver|recipient|inbox_write|--to)', s): c.add('⑷')
    if re.search(r'\b(open|Path|os\.path\.\w+|os\.(listdir|makedirs|remove|rename|stat|chdir|walk|access)|shutil\.\w+|glob\.glob)\(\s*[^)]*' + A, s) or re.search(A + r'\s*/\s*', s) or re.search(r'/\s*' + A, s) or re.search(r'\{' + A + r'\}[^"\']*/', s) or re.search(r'/[^"\']*\{' + A + r'\}', s) or re.search(r'\.joinpath\(', s) and re.search(A, s): c.add('⑶')
    if re.search(r'(==|!=)\s*' + A, s) or re.search(A + r'\s*(==|!=)', s) or re.search(A + r'\s+(not\s+)?in\s', s) or re.search(r'\bin\s+' + A, s) or re.search(r'\.startswith\(|\.endswith\(', s) and re.search(A, s): c.add('⑸')
    if re.search(r'\b(int|float)\(\s*' + A, s) or re.search(A + r'\s*(<|>|<=|>=)\s*\d', s) or re.search(r'\d\s*(<|>|<=|>=)\s*' + A, s) or re.search(r'\bsleep\(\s*' + A, s) or re.search(r'timeout\s*=\s*' + A, s): c.add('數')
    if not c:
        if re.search(r'os\.(environ|getenv)', s): c.add('口')
        elif re.search(r'\b(logger\.\w+|print|log|logging\.\w+)\(', s) or re.search(r'^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*' + A + r'\s*$', s): c.add('伝')
        else: c.add('他')
    return c, s
