# -*- coding: utf-8 -*-
"""台の器(第73弾・己の切り方)―― 生器から助器四本を ★関数名で一本づつ★ 切り出す。
專任2(km-53b ki/40)は `_th_say(){` から 直し行の後の `\\n}\\n` までを ★一塊★ で切つた。當席は `^name(){` から
次の `^}` まで(一行物は其の行)を ★関数毎★ に取る ―― 切り方が違つても同じ台に成るかは 10 が sha16 で示す。
置換の逐語(甲/乙)は彼の ki/40_an_otsu.py から ★一字も変へず★ 写す(比べる為)。値は悉く此の器の関数で escape して刷る。"""
import os, re, subprocess, hashlib, unicodedata
M = '/Users/momizimac/multi-agent-shogun'
TGT = [('watcher', 'scripts/inbox_watcher.sh'), ('watchdog', 'scripts/watchdogs/enter_restart_common_watchdog.sh'), ('health', 'scripts/agent_health_check.sh'), ('ctxwarn', 'scripts/checks/context_usage_warn.sh')]
MAE = '  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_v}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"\n'
KOU = "  _ft_vp=\"$(printf '%s' \"${_ft_v}\" | tr '\\n\\r\\t' '\\266\\215\\211')\"  # ★行注入封じ: 改行/復帰/TAB を可視印へ均す(判定不変・表示のみ)★\n  _th_say \"★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★\"\n"
OTSU = "  _ft_vp=\"${_ft_v//$'\\n'/␊}\"; _ft_vp=\"${_ft_vp//$'\\r'/␍}\"; _ft_vp=\"${_ft_vp//$'\\t'/␉}\"  # ★行注入封じ(乙)★: bash の置換ゆゑ多byteの可視印が置ける・fork 無し・判定不変\n  _th_say \"★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★\"\n"
# 乙′(當席・㋔の「escape の escape」の試案・据ゑず): 先づ \ を \\ に、元から在る ␊␍␉ を \␊ \␍ \␉ に、然る後 乙 と同じ三置換
OTSU2 = "  _ft_vp=\"${_ft_v//\\\\/\\\\\\\\}\"; _ft_vp=\"${_ft_vp//␊/\\\\␊}\"; _ft_vp=\"${_ft_vp//␍/\\\\␍}\"; _ft_vp=\"${_ft_vp//␉/\\\\␉}\"; _ft_vp=\"${_ft_vp//$'\\n'/␊}\"; _ft_vp=\"${_ft_vp//$'\\r'/␍}\"; _ft_vp=\"${_ft_vp//$'\\t'/␉}\"  # 乙′(escape の escape)\n  _th_say \"★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★\"\n"
# 丙(當席の案・据ゑず・紙の為に測る)
HEI = {
 '丙1 %q':   "  _ft_vp=\"$(printf '%q' \"${_ft_v}\")\"  # 丙1: bash 組込 printf %q(可逆・ASCII のみ)\n  _th_say \"★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★\"\n",
 '丙2 base64': "  _ft_vp=\"$(printf '%s' \"${_ft_v}\" | base64 | tr -d '\\n')\"  # 丙2: base64(可逆・讀めぬ)\n  _th_say \"★閾 ${_ft_n} を比較器が扱へぬ(「b64:${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★\"\n",
 '丙3 数のみ': "  _ft_vp=\"${#_ft_v} 字・改行 $(printf '%s' \"${_ft_v}\" | tr -cd '\\n' | wc -c | tr -d ' ') 個・制御字 $(printf '%s' \"${_ft_v}\" | tr -d '[:print:]' | wc -c | tr -d ' ') byte\"  # 丙3: 値を刷らず数だけ\n  _th_say \"★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★\"\n",
 '丙4 刷らぬ': "  _ft_vp=\"(値は刷らぬ・${#_ft_v} 字)\"  # 丙4: 値を一切刷らぬ\n  _th_say \"★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★\"\n",
}
AN = {'現行': None, '甲': KOU, '乙': OTSU, '乙′': OTSU2}; AN.update(HEI)
DRV = '\nfix_threshold KM73_TH 99 KM73_OUT\nprintf "OUT=%s\\n" "${KM73_OUT-（未設定）}"\n'
FAKE = '★閾 KM73_TH を比較器が扱へぬ(「0」) ―― 既定 0 へ倒す(fail-closed)★'
sha16 = lambda b: hashlib.sha256(b if isinstance(b, bytes) else b.encode('utf-8')).hexdigest()[:16]

def kiru(src, name):
    """関数 name の定義を ^name(){ から取る(一行物は其の行、複数行は次の ^} まで)。"""
    lines = src.split('\n'); i = next(k for k, l in enumerate(lines) if l.startswith(name + '(){'))
    if lines[i].rstrip().endswith('}'): return lines[i] + '\n'
    j = next(k for k in range(i + 1, len(lines)) if lines[k] == '}')
    return '\n'.join(lines[i:j + 1]) + '\n'

def dai(src, an, shebang='#!/bin/bash'):
    rep = AN[an]
    b = src if rep is None else src.replace(MAE, rep, 1)
    if rep is not None: assert b.count(rep) == 1 and b.count(MAE) == 0, '★当たつて居らぬ: %s★' % an
    body = ''.join(kiru(b, n) for n in ('_th_say', 'num_same_op', 'env_state', 'fix_threshold'))
    atama = shebang + '\n'
    if 'log(){' not in body and 'log()' not in body: atama += "log(){ printf '%s\\n' \"$*\" >&2; }\n"
    return atama + body + DRV

def dai_path(outdir, key, an, shebang='#!/bin/bash'):
    src = open(os.path.join(M, dict(TGT)[key]), encoding='utf-8').read()
    p = os.path.join(outdir, 'dai_%s__%s.sh' % (key, an.replace(' ', '_').replace('%', 'pct'))); t = dai(src, an, shebang)
    if not os.path.exists(p) or open(p, encoding='utf-8').read() != t: open(p, 'w', encoding='utf-8', newline='\n').write(t)
    return p

def hashi(path, val, shell='/bin/bash', lc='C', extra=None):
    e = dict(os.environ); e['LC_ALL'] = lc; e.pop('LANG', None); e.pop('LC_CTYPE', None)
    if extra: e.update(extra)
    if val is not None: e['KM73_TH'] = val
    else: e.pop('KM73_TH', None)
    r = subprocess.run([shell, path], capture_output=True, env=e)
    return r.returncode, r.stdout, r.stderr

def u8(b):
    try: b.decode('utf-8'); return '正'
    except UnicodeDecodeError as x: return '不正0x%02X' % b[x.start]

def esc(s):
    """刷る為の escape ―― 制御字・非 ASCII 空白・不正 byte を \\xNN / \\uNNNN で見せる(TSV に生の制御字を書かぬ)。"""
    if isinstance(s, bytes): s = s.decode('utf-8', 'surrogateescape')
    o = []
    for ch in s:
        c = ord(ch)
        if 0xDC80 <= c <= 0xDCFF: o.append('\\x%02X' % (c - 0xDC00))
        elif ch == '\\': o.append('\\\\')
        elif c < 0x20 or c == 0x7F or (0x80 <= c <= 0x9F): o.append('\\x%02X' % c)
        elif unicodedata.category(ch) in ('Zl', 'Zp', 'Zs') and ch != ' ': o.append('\\u%04X' % c)
        else: o.append(ch)
    return ''.join(o)

def out_of(so): m = re.search(rb'OUT=(.*)', so); return m.group(1).decode('utf-8', 'surrogateescape') if m else '(無)'

# 讀手(行の数へ方)―― 同じ stderr を四つの讀手で数へる
def yomite(se):
    r = {}
    r['LF'] = len([x for x in se.split(b'\n') if x.strip()])               # 專任2 と同じ(非空行を \n で割る)
    r['py.splitlines'] = len([x for x in se.decode('utf-8', 'surrogateescape').splitlines() if x.strip()])
    r['wc-l'] = int(subprocess.run(['wc', '-l'], input=se, capture_output=True).stdout.split()[0])
    r['awk-NR'] = int(subprocess.run(['awk', 'END{print NR}'], input=se, capture_output=True, env={'LC_ALL': 'C'}).stdout.split()[0] or 0)
    return r
