# -*- coding: utf-8 -*-
"""己の器 33(第66弾・㋔)―― ①己の束(km-64/65・sibling _manifest 形)は 40 本の外か(21 の tsv に在るか)②其の配下の通常 file 本数(= 母數から「別所」の定義で外れて居る己の本数・己が除いたのではなく定義が外した ―― 本数を書く)③本弾の束(worktree docs/evidence/km-66…)の今の本数(門の前の刻)。門の後の己の三山は 30 --one が _after/ へ出す。読取のみ。"""
import os, sys, stat, time
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; D = M + '/queue/reports'; B66 = os.path.dirname(E)
R65 = D + '/ashigaru-mac-1_km-65-daichou-ga-aru-to-daichou-ga-kiku-wa-betsu-besshono-40-hon-ni-jou1-wo-kakero-20260917_evidence/raw'
tsv = [l.rstrip('\n').split('\t') for l in open(R65 + '/21_jou1_besho.tsv', encoding='utf-8')][1:]; in40 = {r[0] for r in tsv}
def walk(root):
    n = b = nr = 0
    for d, ds, fs in os.walk(root):
        for f in fs:
            st = os.lstat(os.path.join(d, f))
            if stat.S_ISREG(st.st_mode): n += 1; b += st.st_size
            else: nr += 1
    return n, b, nr
out = [f'# 己 33 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 40 本(21 の tsv)に己の紙が在るか・己の束の本数']
mine = sorted(e.name for e in os.scandir(D) if e.name.startswith('ashigaru-mac-1_km-6') and e.name.endswith('_evidence') and e.is_dir(follow_symlinks=False))
tot = 0
for ev in mine:
    paper = ev[:-9] + '.md'; n, b, nr = walk(os.path.join(D, ev)); tot += n
    out.append(f'  {ev[:60]}… : 紙が 40 本に在る = {paper in in40} / 配下 通常 file {n} 本 {b} B(非通常 {nr})/ 兄弟 _manifest.txt {"在る" if os.path.isfile(os.path.join(D, ev[:-9] + "_manifest.txt")) else "無い"}(sibling 形 = 別所でない ∴ 定義が外す)')
a1_in40 = sorted(x for x in in40 if x.startswith('ashigaru-mac-1_'))
out.append(f'  ★40 本の内 己(ashigaru-mac-1_)の紙 = {len(a1_in40)} 本(B12_*/B2_*/B3_*/J*/KM_*/km-0fc…/km-29c… = 舊い弾の別所形)―― 己の km-6x 束は {len(mine)} 本とも 40 の外・配下計 {tot} 本は母數 1532 に入つて居らぬ(除いたのは己でなく「別所」の定義)★')
n, b, nr = walk(B66); out.append(f'  本弾の束 {B66} : 今(門の前)の通常 file {n} 本 {b} B(非通常 {nr})―― 門の後の三山は _after/33_onore_after.txt(30 --one)')
K.kaku(E + '/33_onore.txt', '\n'.join(out)); print('\n'.join(out))
