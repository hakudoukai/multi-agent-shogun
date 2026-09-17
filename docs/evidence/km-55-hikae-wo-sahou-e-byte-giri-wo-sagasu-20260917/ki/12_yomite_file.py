# -*- coding: utf-8 -*-
"""★讀手の file 單位 上限★(第55弾 ㋑ 補)

11_yomite.tsv は ★同じ行★ の byte 切りしか数へぬ。然し讀手は
  scripts/agent_health_check.sh 2> /tmp/x   …(行A)
  cut -b1-40 /tmp/x                         …(行B)
の形で ★別行★ で切り得る。∴ 本器は ★file 全体★ を歩き、上限を出す。
母數 = 11_yomite.tsv が挙げた「四本の名を呼ぶ行」を持つ file の集合。
出目が 0 なら ―― ★其の file の何処にも byte 切りが無い★ ゆゑ、別行の形も在り得ぬ。
使ひ方: python3 12_yomite_file.py <11_yomite.tsv> <出力tsv>
"""
import sys, os, re, importlib.util

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('bg', os.path.join(here, '10_byte_giri.py'))
# 10_byte_giri.py は末尾で sys.exit する ∴ import せず、正規表現のみ逐語で写す(同一である事を下で検む)
DIALECTS = [
    ('cut_b',   re.compile(r'\bcut\b[^|;&\n]*?(?:-b(?=[0-9 ])|--bytes)')),
    ('cut_c',   re.compile(r'\bcut\b[^|;&\n]*?(?:-c(?=[0-9 ])|--characters)')),
    ('bash_sl', re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\s*:\s*[0-9$][^}]*:[^}]*\}')),
    ('pf_prec', re.compile(r'printf\b[^\n]*%[-+ #0]*\.[0-9]+s')),
    ('head_c',  re.compile(r'\bhead\b[^|;&\n]*?(?:-c(?=[0-9 ])|--bytes)')),
    ('dd_bs',   re.compile(r'\bdd\b[^|;&\n]*?\bbs=')),
    ('awk_sub', re.compile(r'\bsubstr\s*\(')),
]
src = open(os.path.join(here, '10_byte_giri.py'), encoding='utf-8').read()
onaji = all(rx.pattern in src for _, rx in DIALECTS)

tsv, out = sys.argv[1], sys.argv[2]
files = []
for ln in open(tsv, encoding='utf-8'):
    if ln.startswith(('#', '母數', '四本', '其の', '\n')):
        continue
    p = ln.split('\t')[0]
    if p and os.path.isfile(p):
        files.append(p)
files = sorted(set(files))

rows, nhit = [], 0
for p in files:
    try:
        ls = open(p, encoding='utf-8', errors='surrogateescape').read().split('\n')
    except Exception as e:
        rows.append((p, '?', '讀めぬ', str(e))); continue
    for i, l in enumerate(ls, 1):
        for nm, rx in DIALECTS:
            m = rx.search(l)
            if m:
                rows.append((p, str(i), nm, l.strip()[:140])); nhit += 1

w = open(out, 'w', encoding='utf-8')
w.write('#colspec\t讀手file\t行\t形\t逐語(140字迄)\n')
w.write('七形の逐語が 10_byte_giri.py と同一か=%s\n' % ('★同一★' if onaji else '★異なる ―― 信ずるな★'))
w.write('母數(四本の名を呼ぶ行を持つ file)=%d\n' % len(files))
w.write('file 全体で当つた byte 切り=%d\n\n' % nhit)
for r in rows:
    w.write('\t'.join(r) + '\n')
w.close()
sys.stderr.write('讀手file=%d 当り=%d 同一=%s\n' % (len(files), nhit, onaji))
