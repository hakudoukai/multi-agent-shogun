# -*- coding: utf-8 -*-
"""問一の後半 32(第56弾)。30(HH:MM:SS)と 31(日付込み・秒 / ns の二定義)と 第55弾 97(其の刻の實測)を ★同じ根★で並べ、集合で差を出す。argv = <30 の .txt> <31 の .txt> <第55弾 97 の .txt>。讀むのみ。"""
import re, sys
def rd(p, rx):
    t = open(p, encoding='utf-8').read(); return t, {m.group(1): int(m.group(2)) for m in re.finditer(rx, t, re.M)}
t30, a30 = rd(sys.argv[1], r'^  後 (\S+) (\d+)B '); t31, a31 = rd(sys.argv[2], r'^  後 (\S+) (\d+)B '); t97, a97 = rd(sys.argv[3], r'^  後 (\S+) (\d+)B ')
ns = re.search(r'ns > 秒\.000 で比べると\(第55弾 97 の定義\): (\d+) 本 / byte 和 (\d+) ―― 差 = 門控と同じ秒に生れた (\d+) 本 / (\d+) B: \[(.*?)\]', t31)
same = [x.strip("' ") for x in ns.group(5).split(',')] if ns else []
fake = sorted(set(a30) - set(a31)); both = sorted(set(a30) & set(a31)); only31 = sorted(set(a31) - set(a30))
born_after_97 = sorted((set(a31) | set(same)) - set(a97)); gone_since_97 = sorted(set(a97) - (set(a31) | set(same)))
S = lambda d, ks: sum(d[k] for k in ks)
print(f'# 32 並べ(同じ根 = 第55弾 _evidence・同じ門控の刻 2026-09-16T17:21:25)')
print('器\t定義\t後 本\tbyte 和\t刻')
print(f'30_kusari(第55弾の器の写し)\tHH:MM:SS の文字列 > 17:21:25\t{len(a30)}\t{S(a30, a30)}\t{re.search(r"刻 (\S+)", t30).group(1)}')
print(f'31 秒\tYYYY-MM-DDTHH:MM:SS > 門控(秒)\t{len(a31)}\t{S(a31, a31)}\t{re.search(r"刻 (\S+)", t31).group(1)}')
print(f'31 ns\tst_mtime_ns > 門控.000(97 と同じ)\t{ns.group(1)}\t{ns.group(2)}\t同上')
print(f'97(第55弾・其の刻)\tst_mtime > 門控.000\t{len(a97)}\t{S(a97, a97)}\t{re.search(r"刻 (\S+)", t97).group(1)}')
print(f'## 30 − 31秒 = 偽の「後」(日付落ち・09-13 の器) {len(fake)} 本 / {S(a30, fake)} B ⇔ 97 が刷つた「偽つた物 32 本 / 62791 B」と {"一致" if len(fake) == 32 and S(a30, fake) == 62791 else "★不一致★"}')
print(f'## 30 ∩ 31秒 = {len(both)} 本 / {S(a31, both)} B ; 31秒 − 30 = {len(only31)} 本(0 でなければ 30 が見落とす形が在る)')
print(f'## 31ns − 97 = 97 の後に生れた {len(born_after_97)} 本 / {sum(a31.get(k, 0) for k in born_after_97)} B: {born_after_97}')
print(f'## 97 − 31ns = 97 が見て今は無い {len(gone_since_97)} 本: {gone_since_97 or "(空 ―― 消えた物は無い)"}')
print(f'## ∴ 30 の 55 = 偽 {len(fake)} + 真(秒) {len(both)} ; 31ns {ns.group(1)} = 真(秒) {len(a31)} + 門控と同じ秒 {ns.group(3)}(= 門自身 8) ; 97 の 22 + 後に生れた {len(born_after_97)} = {len(a97) + len(born_after_97)} ⇔ 31ns {ns.group(1)} → {"閉ぢる" if len(a97) + len(born_after_97) - len(gone_since_97) == int(ns.group(1)) else "★閉ぢぬ★"}')
