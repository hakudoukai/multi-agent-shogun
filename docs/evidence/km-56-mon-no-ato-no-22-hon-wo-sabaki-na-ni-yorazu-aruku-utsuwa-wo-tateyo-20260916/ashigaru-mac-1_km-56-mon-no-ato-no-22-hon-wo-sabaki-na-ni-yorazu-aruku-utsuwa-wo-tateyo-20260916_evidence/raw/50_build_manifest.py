# -*- coding: utf-8 -*-
"""臺帳を組む器(第56弾・第55弾 raw/50 を写して ★門の後の出目を根の外 <束>_after/ へ移した★ ―― 根(_evidence)に門の後に生れる物は 門自身の産物(59_/60_/61_)のみ・99/62/63/96/64/63b は根の外の名で宣す)。弾番と門控の名は束の名から導く。
歩き根 = <束>_evidence / file の定義 = lstat 通常 file(symlink・dir は ㊃・母數の外)/ 目盛 = sha256・bytes(讀んだ byte 数)・lines(b'\\n' の数 ―― ★宣言であつて照合値ではない・§2⑷㋓★)。
員外(理由付): ㊀ 名に改行 / ㊂ 凍結後に生れる物(59_/60_/61_/62_/63_/99_ ―― 名を先に宣す)/ ㊄ 初回の出目(.first)/ ㊅ 己の産物(50_build_manifest.out・名で宣す)/ ㊆ .part / ㊇ 證の fixture(raw/fx/ ―― ㊂ 境の一本 = 空白のみの行(空白/tab/U+3000/NBSP/ZWSP・改行の無い末尾)を byte 其の儘で書いた臺帳 fixture・條②を鳴らす物を含む・門に掛けぬ・直さぬ・名と sha を註に宣す)。
器は悉く臺帳に載る(kaki/20/21/30_fx_driver/30_fx_letter/32/40/50/59/60/99)。紙 1 枚(本紙)。"""
import os, sys, re, hashlib, datetime, subprocess
SELF_PRODUCTS = ('50_build_manifest.out', '50_build_manifest.stdout', '50_build_manifest.err', '50_build_manifest.rc')   # ★二度目: 10_run が 50 の後に書く三本も己の産物(一走目の物が二走目の歩きに入り 條① が鳴つた = 疵 8)★
RN = None
POST_DECLARED_T = ['raw/50_build_manifest.out', 'raw/50_build_manifest.stdout', 'raw/50_build_manifest.err', 'raw/50_build_manifest.rc', 'raw/59_prescan.out', 'raw/59_prescan.rc', 'raw/59_prescan.stdout', 'raw/59_prescan.err', 'raw/59_gate_pre.err', 'raw/59_gate_pre.out', 'raw/59_gate_pre.rc',
                 'raw/60_gate_selftest.err', 'raw/60_gate_selftest.out', 'raw/60_gate_selftest.rc', 'raw/60_gate_main.err', 'raw/60_gate_main.out', 'raw/60_gate_main.rc',
                 'raw/60_gate_all.err', 'raw/60_gate_all.out', 'raw/60_gate_all.rc', 'raw/60_gate_rcs.txt', 'raw/61_gate_argv_main.txt', 'raw/61_gate_argv_all.txt', 'raw/60_gate_top.r{RN}.txt', '(根の外) <束>_gate.txt',
                 '(根の外・門の後の出目は悉く此処) <束>_after/10_run.py', '<束>_after/kaki.py', '<束>_after/60_gate_run.stdout', '<束>_after/60_gate_run.err', '<束>_after/60_gate_run.rc', '<束>_after/99_after_gate.txt', '<束>_after/99_after_gate.stdout', '<束>_after/99_after_gate.err', '<束>_after/99_after_gate.rc', '<束>_after/62_report_body.txt', '<束>_after/63_sent.txt', '<束>_after/62_letters.stdout', '<束>_after/62_letters.err', '<束>_after/62_letters.rc', '<束>_after/96_after_send.txt', '<束>_after/96_after_send.stdout', '<束>_after/96_after_send.err', '<束>_after/96_after_send.rc', '<束>_after/63b_sent.txt', '<束>_after/64_letter7.stdout', '<束>_after/64_letter7.err', '<束>_after/64_letter7.rc']
def selection(root):
    keep=[]; ex_nl=[]; ex_post=[]; ex_first=[]; ex_self=[]; ex_part=[]; nonreg=[]; ex_copy=[]
    for d, ds, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            if not os.path.isfile(p) or os.path.islink(p): nonreg.append(p); continue
            base = os.path.basename(p)
            if base.endswith('.part'): ex_part.append(p); continue
            if base in SELF_PRODUCTS: ex_self.append(p); continue
            if '\n' in p or '\r' in p: ex_nl.append(p); continue
            if os.path.basename(d) == 'fx' or (os.sep + 'fx' + os.sep) in p: ex_copy.append(p); continue   # ㊇ 證の fixture(byte 其の儘・門に掛けぬ・直さぬ)―― 第43弾: fx/ochi/(他席の臺帳の写し + 空白のみの行 1 本)も含む
            if '.first' in base: ex_first.append(p); continue   # ★第54弾: .first を .py より先に見る(落ちた走りの 05_chakushu.first.py / .first2.py も ㊄ へ・第53弾は .py が先で .first.py が項に載る形であつた)★
            if base.endswith('.py'): keep.append(p); continue
            if any(base.startswith(k) for k in ('59_', '60_', '61_')): ex_post.append(p); continue   # ★第56弾: 根に門の後に生れるのは門自身(59_/60_/61_)のみ ―― 62/63/96/99/64/63b は根の外 _after/ へ★
            keep.append(p)
    return sorted(keep), sorted(ex_nl), sorted(ex_post), sorted(nonreg), sorted(ex_first), sorted(ex_self), sorted(ex_part), sorted(ex_copy)
def entry(p):
    b = open(p, 'rb').read(); return f'path={p} sha256={hashlib.sha256(b).hexdigest()} bytes={len(b)} lines={b.count(b"\n")}', len(b)
def write_atomic(path, text):
    tmp = path + '.part'
    with open(tmp, 'w', encoding='utf-8') as f: f.write(text); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
if __name__ == '__main__':
    B = sys.argv[1]; RN = re.search(r'_km-(\d+)-', B).group(1); POST_DECLARED = [p.replace('{RN}', RN) for p in POST_DECLARED_T]; ROOT = B + '_evidence'; PAPER = B + '.md'; MAN = B + '_manifest.txt'
    now = datetime.datetime.now().astimezone().isoformat(timespec='seconds'); head = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    keep, ex_nl, ex_post, nonreg, ex_first, ex_self, ex_part, ex_copy = selection(ROOT)
    assert os.path.isfile(PAPER)
    lines = [f'# 臺帳 ―― {os.path.basename(B)}(第{RN}弾)/ 刻 {now} / cwd {os.getcwd()} / HEAD {head}',
             "# 形 = path=<p> sha256=<64> bytes=<n> lines=<n>(家老の錨器の B 素形 四欄・照合器 paths_of の②形)。歩き根 = <束>_evidence / file の定義 = lstat 通常 file(symlink・dir は ㊃ ―― 母數の外)/ 目盛 = sha256・bytes(讀んだ byte 数)・lines(b'\\n' の数 ―― ★宣言であつて照合値ではない(第39弾 §2⑵: 三器とも lines= を讀まぬ)★)",
             f'# 員外(理由付)= ㊀ 名に改行 {len(ex_nl)} / ㊂ 凍結後に生れる物(★59_/60_/61_ = 門自身のみ★・此の刻 {len(ex_post)} 本)/ ㊃ 通常 file でない物 {len(nonreg)} / ㊄ 初回の出目(.first){len(ex_first)} / ㊅ 己の産物 = 臺帳を建てる器の出目 ★path={ROOT}/raw/50_build_manifest.out★(自己参照ゆゑ sha を焼かぬ・此の刻の本数 {len(ex_self)})/ ㊆ .part {len(ex_part)} / ㊇ 證の fixture raw/fx/(本弾は作らぬ・{len(ex_copy)} 本) / 臺帳自身・門控',
             '# 器は悉く臺帳に載る(kaki/10〔駆動器〕/05/20/30〔第55弾の写し・byte 同一〕/31/32/70/80/81/50/59/60/62/64 ―― 臺帳より先に書いた)。python は悉く -B。出目は 10_run.py が subprocess で受け kaki で書く。00_start は kaki で書いた。kaki.py・10/30/59/60 は第55弾と byte 同一(器を変へず)。落ちた走り = 05 の二走(.first 324 字 / .first2 310 字 = 字数を書く前に測れ、を二度踏んだ)・70 の三走(.first = zsh が $SH を一語で渡した)・80 の一走(.first = file を根に取れず)・31/30 の一走(.first = 31 が秒のみで比べ門自身を隠した ∴ ns 併記へ)→ ㊄。sb read 0 呼・sb write 0 回。★門の後の歩きは 31_kusari_dated.py(日付込み・出力 dir を argv で取る)を 99_after_gate / 96_after_send の名で ★根の外 <束>_after/ へ★ 出す。門控の名は毎回別 ―― 本弾は r' + RN + '(<束>_gate.txt 一行目 + raw/60_gate_top.r' + RN + '.txt)。★',
             '# 案は文のみ・据ゑず(scripts/ 0 字・.gitignore 0 字・~/bin 0 字・.git/index は前後同一・70_sha_walk.py は束の中に建てた = 据ゑず)。DB へ POST/PATCH/DELETE 0(sb write 0 回・sb read 0 呼)。添状は _report.yaml の名では出さぬ ―― <束>_after/62_report_body.txt(本文)+ <束>_after/63_sent.txt(rc と id の列)+ <束>_after/63b_sent.txt(便 7 = 96 の出目を運ぶ追ひ便)が添状(★名を此処に宣す・根の外★)。★門の後に根(_evidence)へ書く物は門自身の産物のみ・他は根の外 _after/(本弾の問一の答を手で示す)。★',
             '# ★門の後に生れる物(名を先に宣す・員外・此の臺帳の凍結後に生れる)★: ' + ' / '.join(POST_DECLARED),
             '#   此の欄に無い名が門の後に生れたら、其れは宣に無い産物である(_after/96_after_send.txt が 99 との差を出す・根の中は 31 の「後」が出す)。']
    tot = 0; n = 0
    e, sz = entry(PAPER); lines.append(e); tot += sz; n += 1
    for p in keep: e, sz = entry(p); lines.append(e); tot += sz; n += 1
    for tag, grp in (('㊀ 名に改行(員外・⏎ で示す)', ex_nl), ('㊂ 凍結前に在る予告の出目(員外)', ex_post), ('㊄ 初回の出目(員外・器を直す前)', ex_first), ('㊆ .part(員外)', ex_part), ('㊇ 證の fixture raw/fx/(員外・byte 其の儘・門に掛けぬ)', ex_copy)):
        lines.append(f'# {tag}:')
        for p in grp: e, sz = entry(p); lines.append('#   ' + e.replace('\n', '⏎'))
    lines.append('# ㊃ 通常 file でない物(員外・lstat のみ):')
    for p in nonreg: lines.append(f'#   {os.path.relpath(p, ROOT)} ' + (f'symlink→{os.readlink(p)!r} lstat={os.lstat(p).st_size}' if os.path.islink(p) else 'dir'))
    lines.append('# ㊅ 己の産物(母數の外・★sha/bytes を焼かぬ★・★名で宣す★): path=' + ROOT + '/raw/50_build_manifest.out')
    lines.append(f'# 宣(註・家老の DECL に合ふ形): 本数 {n} / byte和 {tot}')
    lines.append(f'# 項 {n}(紙 1 + 證 {n-1})/ byte和 {tot} / 員外 = ㊀{len(ex_nl)} + ㊂{len(ex_post)}(此の刻)+ ㊃{len(nonreg)} + ㊄{len(ex_first)} + ㊅{len(ex_self)}(母數の外)+ ㊆{len(ex_part)} + ㊇{len(ex_copy)}')
    write_atomic(MAN, '\n'.join(lines) + '\n')
    rep = [f'臺帳 {MAN} / 項 {n} / byte和 {tot} / 員外 ㊀{len(ex_nl)} ㊂{len(ex_post)} ㊃{len(nonreg)} ㊄{len(ex_first)} ㊅{len(ex_self)} ㊆{len(ex_part)} ㊇{len(ex_copy)} / 刻 {now}']
    for tag, grp in (('㊀', ex_nl), ('㊂', ex_post), ('㊃', nonreg), ('㊄', ex_first), ('㊅', ex_self), ('㊆', ex_part), ('㊇', ex_copy)):
        for p in grp: rep.append(f'  員外{tag} {os.path.relpath(p, ROOT)!r}')
    write_atomic(ROOT + '/raw/50_build_manifest.out', '\n'.join(rep) + '\n'); print('\n'.join(rep))
