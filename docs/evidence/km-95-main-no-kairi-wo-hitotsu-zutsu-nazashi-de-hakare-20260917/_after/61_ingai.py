# -*- coding: utf-8 -*-
"""61 員外を己で数へる(第82弾 km-95・員外・臺帳の後)―― 束を disk で歩き(通常 file・symlink・FIFO を分けて数へ)、臺帳の path 集合と突き合はせ、載らぬ file を ★名指し★ で列べる。己の出目 _after/61_ingai.txt は歩く前には無く書いた後に在る ∴ 自産として +1 を宣す。刻を焼く(員外は門の後も増える)。"""
import os, sys, stat, time, re, hashlib
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
man = {re.search(r'^path=(\S+) ', l).group(1) for l in open(D + '/MANIFEST.txt', encoding='utf-8') if l.startswith('path=')}
reg = []; other = []
for d, ds, fs in os.walk(D):
    ds[:] = sorted(ds)
    for f in sorted(fs):
        q = os.path.join(d, f); rel = os.path.relpath(q, D); st = os.lstat(q)
        (reg if stat.S_ISREG(st.st_mode) else other).append(rel)
ingai = sorted(set(reg) - man); nai = sorted(man - set(reg))
out = [f'# 61 員外 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 歩き根= 束の根 / 深さ 無制限 / 通常 file {len(reg)} / 非通常 {len(other)} {other} / 臺帳の項 {len(man)} / 臺帳に在り disk に無い {len(nai)} {nai}']
out.append(f'員外(臺帳に載らぬ通常 file)= ★{len(ingai)}★ 本 + 自産 1(此の 61_ingai.txt・歩いた時には無い)= 書いた後の disk では {len(ingai) + 1}')
grp = {}
for p in ingai: grp.setdefault(p.split('/')[0] if '/' in p else '(根)', []).append(p)
for k, v in grp.items(): out.append(f'  {k}: {len(v)} 本'); out += [f'    {p}' for p in v]
out.append('★疵 8(紙の後・紙は臺帳で固定ゆゑ此処に)★: raw/__pycache__/(kaki.cpython-314.pyc)が門の直前に在つた ―― 紙を書いた ad-hoc python(heredoc)を -B 無しで走らせ kaki を import した故。己の産物ゆゑ rm -r で除いた(臺帳には載つて居らず・門 60 の assert が止めた)。')
out.append('意味せぬ事: 員外は「載せ忘れ」ではなく宣した類(臺帳・門控・50 の出目・_after)。数は此の刻の物で、62/64 が書く便の出目で更に増える(其の分は名指せぬ ―― 書く前ゆゑ)。予告: _after/62_letters.txt・62_dry.txt(鳴れば)・64_audit.txt・64_dry.txt(鳴れば)・64_readback_<seq>.txt。')
K.kaku(D + '/_after/61_ingai.txt', '\n'.join(out)); print('\n'.join(out))
