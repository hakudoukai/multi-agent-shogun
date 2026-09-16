# -*- coding: utf-8 -*-
"""臺帳の駆動器 50(第68弾・66 の形)―― ★臺帳へ行を書くのは karo_mac_manifest_append.py のみ(手書き 0)★。⑴ 選 = <束>/raw の lstat 通常 file 悉く(員外 = 己の産物 4 本・名に改行・非通常)⑵ 員外と門の後に生れる名の宣を raw/50_sengen.txt へ(項として載る)⑶ append.py に [紙] + 選 を絶対 path で渡す(cwd = main 樹の根 → 項の path は main 樹の根からの相對)。rc=3 なら本数と名を .out へ。
本弾(第68弾): 第67弾の形を其の儘。對照 fixture(raw/p6/・raw/fixture/)と .first(33/37 の一走目)も ★載せる★(器を直した證)。★臺帳の基点 = main 樹の根(append.py の cwd)―― 紙に一行で明記する(家老が本夜踏んだ穴)★。"""
import os, sys, subprocess, time, hashlib
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; AP = M + '/scripts/checks/karo_mac_manifest_append.py'
SELF = ('50_build_manifest.out', '50_build_manifest.stdout', '50_build_manifest.err', '50_build_manifest.rc')
POST = ['_after/(根の外・門の後の出目は悉く此処): 00_hosho.txt 60_gate_selftest.{out,err,rc} 60_gate_main.{out,err,rc} 60_gate_all.{out,err,rc} 60_gate_rcs.txt 60_gate_top.r68.txt 61_gate_argv_main.txt 61_gate_argv_all.txt 60_gate_run.{stdout,err,rc} 96_after.{txt,stdout,err,rc} 96_raw.txt 96_bundle.txt 62_report_body.txt 63_sent.txt 62_letters.{stdout,err,rc} 67_git_add.txt 10_run.py kaki.py', '<束>_gate.txt(門控・根の外)']
def selection(root):
    keep = []; ex_nl = []; ex_self = []; nonreg = []
    for d, ds, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            if os.path.islink(p) or not os.path.isfile(p): nonreg.append(p); continue
            if '\n' in p or '\r' in p: ex_nl.append(p); continue
            if f in SELF: ex_self.append(p); continue
            keep.append(p)
    return sorted(keep), sorted(ex_nl), sorted(ex_self), sorted(nonreg)
if __name__ == '__main__':
    B = sys.argv[1]; D = os.path.dirname(B); ROOT = D + '/raw'; PAPER = B + '.md'; MAN = B + '_manifest.txt'; now = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    assert os.path.isfile(PAPER), PAPER; assert not os.path.exists(MAN), '臺帳が既に在る(凍結は一度)'
    sen = [f'# 宣 50(第68弾)/ 刻 {now} / 臺帳 = {os.path.basename(MAN)} は karo_mac_manifest_append.py({hashlib.sha256(open(AP, "rb").read()).hexdigest()[:16]})のみが書く・此の宣は項として載る', '# 歩き根 = <束>/raw(lstat 通常 file 悉く)+ 紙 1 / 項の path = main 樹の根からの相對(.claude/worktrees/karo-mac-a1/docs/evidence/km-68-yonda-ban-to-hashiraseta-ban-20260917/…)―― worktree の根から引くなら頭の .claude/worktrees/karo-mac-a1/ を落とす',
           '# 員外 ㊅ 己の産物(名で宣す・sha を焼かぬ): ' + ' '.join('raw/' + s for s in SELF), '# 員外 ㊂ 門の後に生れる物(名を先に宣す): ' + ' / '.join(POST), '# 錠: 60 は門の前に <束>/raw と配下を 0555/0444 にする ―― 門の後に其処へ書ける者は無い(書けば EACCES・40 --probe が證す)', '# 員外 ㊀ 名に改行: (50 が数へる) / ㊃ 通常 file でない物: (50 が数へる)', '# .first(33/37 の一走目の出目)は ★載せる★ ―― 器を直した證 / ★基点★: 此の臺帳の path は main 樹の根 /Users/momizimac/multi-agent-shogun からの相對 ―― worktree の根に立てば悉く実体無と出る(disk の欠けではない)']
    K.kaku(ROOT + '/50_sengen.txt', '\n'.join(sen))
    keep, ex_nl, ex_self, nonreg = selection(ROOT)
    p = subprocess.run(['python3', '-B', AP, MAN, PAPER] + keep, capture_output=True, text=True, cwd=M)
    rep = [f'50 / 刻 {now} / append.py rc={p.returncode} / 渡した {1 + len(keep)}(紙 1 + 證 {len(keep)})/ 員外 ㊀{len(ex_nl)} ㊅{len(ex_self)} ㊃{len(nonreg)}', '--- append.py stdout', p.stdout.rstrip('\n'), '--- append.py stderr', p.stderr.rstrip('\n')]
    if p.returncode == 3: rep.append('★拒まれた(rc=3)―― 一行も書かれて居らぬ・拒まれた名は上の stderr に逐語★')
    for tag, grp in (('㊀', ex_nl), ('㊅', ex_self), ('㊃', nonreg)):
        for q in grp: rep.append(f'  員外{tag} {os.path.relpath(q, ROOT)!r}')
    if os.path.isfile(MAN): mb = open(MAN, 'rb').read(); rep.append(f'臺帳 {MAN} / bytes {len(mb)} / 行 {mb.count(b"\n")} / path= 行 {sum(1 for l in mb.split(b"\n") if l.startswith(b"path="))} / sha16 {hashlib.sha256(mb).hexdigest()[:16]}')
    K.kaku(ROOT + '/50_build_manifest.out', '\n'.join(rep)); print('\n'.join(rep)); sys.exit(p.returncode)
