# -*- coding: utf-8 -*-
"""臺帳の駆動器 50(第66弾)―― ★臺帳へ行を書くのは karo_mac_manifest_append.py のみ(手書き 0・此の器は行を一つも書かぬ)★。此の器は ⑴ 選(root=<束>/raw の lstat 通常 file・員外を除く)を決め ⑵ 員外の宣と門の後に生れる名の宣を raw/50_sengen.txt へ書き(臺帳には註を書けぬ故・宣は項として載る)⑶ append.py に [紙] + 選 を絶対 path で渡す(cwd = main 樹の根 → 項の path は main 樹の根からの相對 = .claude/worktrees/karo-mac-a1/docs/evidence/…)。rc=3(禁に触れた)なら本数と名を 50_build_manifest.out に書く(拒まれた事自体が測定)。
員外: ㊀ 名に改行 / ㊅ 己の産物 raw/50_build_manifest.{out,stdout,err,rc} / ㊂ 門の後に生れる物 raw/60_* raw/61_*(門自身)・<束>_gate.txt・_after/ 悉く(根の外)/ ㊃ 通常 file でない物。.first(一走目の出目)は ★載せる★(器を直した證)。"""
import os, sys, subprocess, time, hashlib
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; AP = M + '/scripts/checks/karo_mac_manifest_append.py'
SELF = ('50_build_manifest.out', '50_build_manifest.stdout', '50_build_manifest.err', '50_build_manifest.rc')
POST = ['raw/60_gate_selftest.{out,err,rc}', 'raw/60_gate_main.{out,err,rc}', 'raw/60_gate_all.{out,err,rc}', 'raw/60_gate_rcs.txt', 'raw/60_gate_top.r66.txt', 'raw/61_gate_argv_main.txt', 'raw/61_gate_argv_all.txt', 'raw/60_gate_run.{stdout,err,rc}(10_run が 60 の後に書く)', '<束>_gate.txt(門控・根の外)',
        '_after/(根の外・門の後の出目は悉く此処): 10_run.py kaki.py 99_after_gate.{txt,stdout,err,rc} 62_report_body.txt 63_sent.txt 62_letters.{stdout,err,rc} 33_onore_after.{txt,stdout,err,rc} 96_after_send.{txt,stdout,err,rc} 63b_sent.txt 64_letter6.{stdout,err,rc} 67_git_add.{txt,stdout,err,rc}']
def selection(root):
    keep = []; ex_nl = []; ex_self = []; ex_post = []; nonreg = []
    for d, ds, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            if os.path.islink(p) or not os.path.isfile(p): nonreg.append(p); continue
            if '\n' in p or '\r' in p: ex_nl.append(p); continue
            if f in SELF: ex_self.append(p); continue
            if f.endswith('.py'): keep.append(p); continue   # ★器は悉く載せる(60_gate_run.py も)―― 前置 59 の一走で 60_gate_run.py が ㊂ に落ちた疵を直した★
            if f.startswith(('60_', '61_')): ex_post.append(p); continue
            keep.append(p)
    return sorted(keep), sorted(ex_nl), sorted(ex_self), sorted(ex_post), sorted(nonreg)
if __name__ == '__main__':
    B = sys.argv[1]; D = os.path.dirname(B); ROOT = D + '/raw'; PAPER = B + '.md'; MAN = B + '_manifest.txt'; now = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    assert os.path.isfile(PAPER), PAPER; assert not os.path.exists(MAN), '臺帳が既に在る(凍結は一度)'
    sen = [f'# 宣 50(第66弾)/ 刻 {now} / 臺帳 = {os.path.basename(MAN)} は karo_mac_manifest_append.py({hashlib.sha256(open(AP, "rb").read()).hexdigest()[:16]})のみが書く・此の宣は項として載る', '# 歩き根 = <束>/raw(lstat 通常 file)+ 紙 1 / 項の path = main 樹の根からの相對(.claude/worktrees/karo-mac-a1/docs/evidence/km-66-noranu-336-20260917/…)―― worktree の根から引くなら頭の .claude/worktrees/karo-mac-a1/ を落とす(照合器の既定基点は器の在處から導いた main 樹の根)',
           '# 員外 ㊅ 己の産物(名で宣す・sha を焼かぬ): ' + ' '.join('raw/' + s for s in SELF), '# 員外 ㊂ 門の後に生れる物(名を先に宣す): ' + ' / '.join(POST), '# 員外 ㊀ 名に改行: (50 が数へる) / ㊃ 通常 file でない物: (50 が数へる)', '# .first(30_sanzan.first.* 7 本 = 2MB 閾を持つた一走目の出目)は ★載せる★ ―― 器を直した證']
    K.kaku(ROOT + '/50_sengen.txt', '\n'.join(sen))
    keep, ex_nl, ex_self, ex_post, nonreg = selection(ROOT)
    p = subprocess.run(['python3', '-B', AP, MAN, PAPER] + keep, capture_output=True, text=True, cwd=M)
    rep = [f'50 / 刻 {now} / append.py rc={p.returncode} / 渡した {1 + len(keep)}(紙 1 + 證 {len(keep)})/ 員外 ㊀{len(ex_nl)} ㊅{len(ex_self)} ㊂{len(ex_post)}(此の刻)㊃{len(nonreg)}', '--- append.py stdout', p.stdout.rstrip('\n'), '--- append.py stderr', p.stderr.rstrip('\n')]
    if p.returncode == 3: rep.append(f'★拒まれた(rc=3)―― 一行も書かれて居らぬ・拒まれた名は上の stderr に逐語★')
    for tag, grp in (('㊀', ex_nl), ('㊅', ex_self), ('㊂', ex_post), ('㊃', nonreg)):
        for q in grp: rep.append(f'  員外{tag} {os.path.relpath(q, ROOT)!r}')
    if os.path.isfile(MAN): mb = open(MAN, 'rb').read(); rep.append(f'臺帳 {MAN} / bytes {len(mb)} / 行 {mb.count(b"\n")} / path= 行 {sum(1 for l in mb.split(b"\n") if l.startswith(b"path="))} / sha16 {hashlib.sha256(mb).hexdigest()[:16]}')
    K.kaku(ROOT + '/50_build_manifest.out', '\n'.join(rep)); print('\n'.join(rep)); sys.exit(p.returncode)
