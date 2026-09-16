# -*- coding: utf-8 -*-
"""㋑⑶ 則一の器を作る 31(第68弾)―― 40_mon_no_ato.py(第67弾 二走目・則二 = mtime|birth|ctime・逐語の写し)から ★一行だけ★ ctime を外して 41_mon_no_ato_rule1.py(則一 = mtime|birth・第67弾 一走目の則)を作る。
第67弾は一走目の器を file として残さず(.first は出目のみ)、則の変更は 40 の docstring と 00_start の則行に逐語で在る ∴ 則一は「40 から其の一行を戻した物」として再現し、diff -u を raw/30_rule_diff.txt に、逐語の則の並びを raw/30_rule_verbatim.txt に刷る。
再現である事を隠さぬ ―― 一走目の器其の物ではない。"""
import os, sys, subprocess, hashlib, time
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
W = '/Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1'; ST67 = W + '/docs/evidence/km-67-mon-no-ato-20260917/raw/00_start.txt'
src = open(E + '/40_mon_no_ato.py', encoding='utf-8').read()
OLD = 'later = mns > A or bns > A or cns > A'; NEW = 'later = mns > A or bns > A'
assert src.count(OLD) == 1, src.count(OLD)
HOLD = "out = [f'# 40 捕へ器(二走目・mtime|birth|ctime) / {name}"; HNEW = "out = [f'# 41 捕へ器(則一の再現・mtime|birth・ctime 無) / {name}"
assert src.count(HOLD) == 1
dst = src.replace(OLD, NEW, 1).replace(HOLD, HNEW, 1)
dst = dst.replace('"""捕へ器 40(第67弾・㋐)', '"""捕へ器 41 = ★則一の再現★(第68弾 ㋑・40 から `or cns > A` を一つ外した物・31_make_rule1.py が作る)―― 元: 捕へ器 40(第67弾・㋐)', 1)
with open(E + '/41_mon_no_ato_rule1.py', 'w', encoding='utf-8', newline='\n') as fh: fh.write(dst)
p = subprocess.run(['diff', '-u', E + '/40_mon_no_ato.py', E + '/41_mon_no_ato_rule1.py'], capture_output=True, text=True)
K.kaku(E + '/30_rule_diff.txt', f'# diff -u 40(則二) 41(則一の再現) / rc {p.returncode}(1 = 差が在る・期待)/ 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}\n' + p.stdout)
st = open(ST67, encoding='utf-8').read().split('\n'); mae = [l for l in st if 'ctime は使はぬ' in l]; ato = [l for l in src.split('\n') if '則を一つ変へた' in l]
K.kaku(E + '/30_rule_verbatim.txt', '\n'.join([f'# ㋑⑶ 変更前後の則を逐語で並べる / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}',
    '## 前(則一)= 第67弾 raw/00_start.txt の則行(測る前に書いた・逐語):'] + ['  ' + l for l in mae] +
    ['## 後(則二)= 第67弾 raw/40_mon_no_ato.py の docstring(測つた後に変へた・逐語):'] + ['  ' + l for l in ato] +
    ['## 器の差 = raw/30_rule_diff.txt(diff -u)/ 差の核 = `' + OLD + '` → `' + NEW + '`(一行)+ 頭註の名札 2 箇所',
     f'## 40 sha16 {hashlib.sha256(src.encode()).hexdigest()[:16]} / 41 sha16 {hashlib.sha256(dst.encode()).hexdigest()[:16]}']))
print(open(E + '/30_rule_diff.txt', encoding='utf-8').read()); print(open(E + '/30_rule_verbatim.txt', encoding='utf-8').read())
sys.exit(0 if p.returncode == 1 and len(mae) == 1 and len(ato) == 1 else 1)
