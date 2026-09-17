# -*- coding: utf-8 -*-
"""50 ★三つの札★(㋑) ―― 生器の口 81 に一枚づつ貼る
札① fail-open する(何が抜けるかを一行で) / 札② 比較器に入らぬゆゑ疵でない / 札③ ★測れぬ★(理由)
★由来★ の欄を併せ立てる ―― 「外から与へ得るか」で ★誰が困るか★ が変る:
  外来 = 生器の何処かで export される / 生器の何処にも代入が無く env のみが源
  内生 = 同じ file 内で `NAME=$(...)`(命令の出目) 又は 字面から代入される
  ★内生でも改行入りは届く★(命令の出目が複数行に成る場合) ―― 空白のみは届き難い
    (実測: `[ " 12" -gt 0 ]` は rc=0 ゆゑ wc -l の前置空白は倒さぬ)。
★測れぬ★ は「下流の消費者を当席の器が見付けられぬ」ではなく、
  ★見付けた上で當席の手では走らせられぬ★ 場合に限る(理由を必ず書く)。"""
import os, re, sys, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
R = '/Users/momizimac/multi-agent-shogun/'
live = [l.split('\t') for l in open(D+'/raw/11_live.tsv',encoding='utf-8').read().splitlines()[1:]]
kaw = collections.defaultdict(set)
for c in [l.split('\t') for l in open(D+'/raw/20_kawashimo.tsv',encoding='utf-8').read().splitlines()[1:]]:
    kaw[(c[0], c[1])].add(c[4])
k41 = {}
for c in [l.split('\t') for l in open(D+'/raw/41_kuchi.tsv',encoding='utf-8').read().splitlines()[1:]]:
    k41[(c[0], c[1])] = [c[9+i] for i in range(8)]
FN = ['1未設定','2空文字','3空白のみ','4二十桁','5正常値7','6負数','7改行入り','8既存␊']
srcs = {}
for f in sorted({c[0] for c in live}):
    try: srcs[f] = open(R+f, encoding='utf-8', errors='replace').read()
    except Exception: srcs[f] = ''
alltext = '\n'.join(srcs.values())
# 丙 の三口 ―― 下流が shell の外に在る口(別に測つた)
HEI = {'STALE_SEC':'python', 'POLL_SEC':'python', 'ER_THRESHOLD_MIN':'fixth', 'DETECT_STALE_STALE_SEC':'dead'}
# ★輪の形の番人★(初走の見落し) ―― inbox_watcher.sh:173-178 は
#   `for _t in NAME:既定 …; do fix_threshold "$_n" "$_d" "$_n"; done` で十名を一度に守る。
#   點呼器は `fix_threshold NAME` を ★口の行で★ 探したゆゑ之を数へず、三口へ ①を誤り貼つた。
#   52 で写しを走らせ、十名 × 八形 悉く倒れぬ事(番人を通つた後 rc=2 が 0 組)を実測した。
import re as _re
_wa = _re.search(r'for _t in (.+?); do', open(D+'/utsushi/bannin_loop_verbatim.txt',
                 encoding='utf-8').read(), _re.S)
WA = {t.split(':')[0] for t in _wa.group(1).replace('\\\n', ' ').split()}
WAF = 'scripts/inbox_watcher.sh'
rows = []
for f, ln, name, dflt, ban, gen in live:
    kinds = kaw.get((f, name), set())
    body = srcs.get(f, '')
    exported = re.search(r'\bexport\s+(?:[A-Za-z_]\w*=\S*\s+)*' + re.escape(name) + r'\b', alltext) is not None
    # ★口の行そのものを「内生の代入」に数へるな★(初走の疵):
    #   `NAME="${NAME:-5}"` は ★口★ であつて内生ではない。右辺に己の名が出る代入は口の一種ゆゑ除く。
    cmd_l, lit_l = [], []
    for i, bl in enumerate(body.splitlines(), 1):
        m = re.match(r'\s*(?:local\s+|export\s+)?' + re.escape(name) + r'=(.*)$', bl)
        if not m or str(i) == ln: continue
        rhs = m.group(1)
        if re.search(r'\$\{?' + re.escape(name) + r'\b', rhs): continue   # 己の名を含む右辺=口
        # ★番人の倒し先を「内生」と数へるな★(二走目の疵):
        #   `case … *[!0-9]*) NAME=10 ;;` の 10 は ★既定へ倒す手★ であつて値の源ではない。
        #   右辺が既定と同じ字面なら口の一部と見る ―― 外から与へ得る事は変らぬ。
        rhs_c = re.sub(r'\s*;;\s*$', '', rhs)          # case の終り `;;` を落す
        rhs_c = re.sub(r'\s+#.*$', '', rhs_c).strip().strip('"\'')
        if rhs_c == dflt: continue
        (cmd_l if rhs.lstrip().startswith('$(') else lit_l).append(i)
    gen_ = ('内生(命令の出目)' if cmd_l else ('内生(字面)' if lit_l else
            ('外来(export有)' if exported else '外来(env のみ)')))
    res = k41.get((f, name))
    hei = HEI.get(name)
    if f == WAF and name in WA:
        fuda, riyu = '②疵でない', '同 file 173-178 の★輪の形の番人★(fix_threshold)が守る ―― 52 で写しを八形走らせ倒れ 0 組'
    elif hei == 'dead':
        fuda, riyu = '③測れぬ', '生器全体で参照が此の一行のみ ―― 代入され二度と讀まれぬ★死口★。比較器が無いゆゑ8形に意味が無い'
    elif hei == 'python':
        fuda, riyu = '②疵でない', '下流は python の int() ―― ValueError で起動時に落ち、監督が5秒で建て直す★fail-closed・声在り★'
    elif hei == 'fixth':
        fuda, riyu = '②疵でない', '呼ばれる側 enter_restart_common_watchdog.sh:120 の fix_threshold が★file を跨いで★守る'
    elif res:
        bad = [FN[i] for i in range(8) if res[i] == '2']
        fuda, riyu = '①fail-open', '/'.join(bad)
    elif kinds and kinds <= {'他食','字比'}:
        fuda, riyu = '②疵でない', '川下は ' + '・'.join(sorted(kinds)) + ' のみ ―― 数の比較器に入らぬゆゑ rc=2 に成り得ぬ'
    elif not kinds:
        fuda, riyu = '③測れぬ', '当席の川下器が同 file 内に消費者を当てられなんだ(名の再代入・間接展開の疑ひ)'
    else:
        fuda, riyu = '③測れぬ', '川下は ' + '・'.join(sorted(kinds)) + ' ―― 比較器の逐語を切り出せなんだ'
    rows.append([f, ln, name, dflt, ban, gen_, fuda, riyu])
rows.sort(key=lambda r: (r[6], r[0], int(r[1])))
K.kaku_tsv(D+'/raw/50_fuda.tsv', rows,
           header=['file','line','name','default','bannin','由来','札','理由/何が抜けるか'])
c = collections.Counter(r[6] for r in rows); g = collections.Counter(r[5] for r in rows)
gf = collections.Counter(r[5] for r in rows if r[6] == '①fail-open')
sm = ['# 50 三つの札 / 生器の口 母數= %d 口 / %d file' % (len(rows), len({r[0] for r in rows}))]
sm.append('# ★札は排他★(一口一枚)。合計が母數に一致する事を以て検算とする:')
for k in sorted(c): sm.append('    %-12s %2d 口' % (k, c[k]))
sm.append('    ' + '-'*24)
sm.append('    %-12s %2d 口  (母數 %d と %s)' % ('合計', sum(c.values()), len(rows),
          '一致' if sum(c.values()) == len(rows) else '★不一致★'))
sm.append('')
uniq = len({(r[0], r[2]) for r in rows if r[6] == '①fail-open'})
sm.append('★①の %d 口は ★名の重複★ を含む ―― 相異なる (file,name) は %d 組。' % (c['①fail-open'], uniq))
sm.append('  41 は (file,name) 毎に一度走らせたゆゑ、同名が別行に立つ口へ同じ札が及ぶ。')
sm.append('  ∴ ★「口 %d」と「走らせた組 %d」は別の數である。★' % (c['①fail-open'], uniq))
sm.append('')
sm.append('# 由来(母數 %d の内訳):' % len(rows))
for k in sorted(g): sm.append('    %-16s %2d 口   (内 ①fail-open= %d)' % (k, g[k], gf.get(k, 0)))
sm.append('')
sm.append('★①fail-open の %d 口は悉く 3空白のみ/4二十桁/7改行入り/8既存␊ の四形で倒れ、' % c['①fail-open'])
sm.append('  1未設定/2空文字/5正常値/6負数 では倒れぬ ―― ★`:-` が未設定と空を既定へ倒すゆゑ★。')
sm.append('  ∴ ★「番人が無い」口でも、未設定と空だけは既に守られて居る。★')
K.kaku(D+'/raw/50_fuda_summary.txt', '\n'.join(sm))
print('\n'.join(sm))
