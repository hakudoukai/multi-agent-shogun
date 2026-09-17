#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 42_hatan2.py ―― 第52弾 ㋑ の破れ器(第二走)。
# ★40_hatan.py の疵I★ guard の写しを `num_same_op` から切つた故、其の手前に在る ★`_th_say` を落とした★。
#   ∴ 鳴の欄が悉く `_th_say: command not found` と成り、★『鳴つた』を測つて居らず『壊れた』を測つて居た★。
#   直し = 切り口を `_th_say(){` へ上げる(凍結点 context_usage_warn.sh L32〜L75)。
# ★40_hatan.py の疵J★ 「閾が非数か」を Python の str.isdigit で判じた故、`' 120'`(先頭空白)を
#   ★非数と誤判★ した。test(1) は先頭空白を受ける ―― 判ずるのは ★bash 自身★ でなければならぬ。
#   直し = 出た閾を `[ "$v" -ge 0 ] 2>/dev/null` に掛け、rc<=1 なら数と看做す。
# (原記)40_hatan.py ―― 第52弾 ㋑ の破れ器。★当てずに数へるな★ に従ひ、
#   数へた箇所の ★一つ残らず★ に「fail-open に成る入力」を ★實際に当てて★ rc を記録する。
#
# ★何を当てるか(六形)★
#   ①未設定  ②空文字 ''  ③空白のみ ' '  ④全角数字 '１２０'  ⑤2^63超 '99999999999999999999'
#   ⑥先頭空白 ' 120'
#   ―― 何れも env から入る。⑤は test(1) の整数解釈を越え、★rc=2★ を返す(0でも1でもない)。
#
# ★何を測るか(二面)★
#   甲 ★素の比較★: 其の箇所の比較式を逐語で取り、閾の側へ毒を入れて bash で走らせ rc を録る。
#      rc=2 ⇒ if も elif も偽 ⇒ ★else へ黙つて落ちる(= fail-open)★。
#   乙 ★guard 通過後★: 凍結点の fix_threshold を束内へ写し、同じ毒を通して
#      ⑴閾が何に成つたか ⑵鳴つたか黙つたか を録る。
#
# ★之が測らぬ物★ 本番 script は一行も走らせて居らぬ(讀取のみ・作法⑴)。
#   比較式のみを取り出して別 shell で走らせた ―― ∴「其の行が実際に踏まれる頻度」は測つて居らぬ。
import sys, io, os, re, json, subprocess

ROOT   = '/Users/momizimac/multi-agent-shogun'
FREEZE = '6dbe09e6'
BASH   = '/bin/bash'
DOKU = [(u'未設定',       None),
        (u'空文字',       u''),
        (u'空白のみ',     u' '),
        (u'全角数字',     u'１２０'),
        (u'2^63超',       u'99999999999999999999'),
        (u'先頭空白',     u' 120')]
RE_CMP = re.compile(r'(\S+)[ \t]+(-(?:eq|ne|lt|le|gt|ge))[ \t]+(\S+)')

def blob(path):
    o = subprocess.run(['git','show','%s:%s'%(FREEZE,path)], cwd=ROOT, capture_output=True)
    return o.stdout.decode('utf-8','replace') if o.returncode==0 else None

def run(script, env):
    e = dict(os.environ); e.update({k:v for k,v in env.items() if v is not None})
    for k,v in env.items():
        if v is None: e.pop(k, None)
    p = subprocess.run([BASH,'-c',script], capture_output=True, env=e)
    return p.returncode, p.stdout.decode('utf-8','replace'), p.stderr.decode('utf-8','replace')

# ─── 甲 素の比較 ───
def sona(expr_line, name):
    """比較式を逐語で取り、閾側へ毒を当てる。他項は中立 0。"""
    m = RE_CMP.search(expr_line)
    if not m: return None
    a, op, b = m.group(1), m.group(2), m.group(3)
    def names(t): return set(re.findall(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)', t))
    side = 'b' if name in names(b) else ('a' if name in names(a) else None)
    if side is None: return None
    other = a if side=='b' else b
    onames = names(other)
    pre = '; '.join('%s=0'%n for n in onames if n != name)
    out = []
    for lab, val in DOKU:
        setup = ('unset %s'%name) if val is None else ('%s=%s'%(name, shq(val)))
        sc = 'set +u; %s; %s; export %s; [ %s %s %s ]; echo rc=$?' % (
              pre if pre else ':', setup, name, a, op, b)
        rc, so, se = run(sc, {})
        out.append({'doku':lab,'rc':int(so.strip().split('=')[-1]) if 'rc=' in so else -1})
    return {'expr':'%s %s %s'%(a,op,b),'side':side,'probes':out}

def shq(s):
    return "'" + s.replace("'", "'\\''") + "'"

# ─── 乙 guard 通過後 ───
GUARD_SRC = None
def guard_src():
    global GUARD_SRC
    if GUARD_SRC: return GUARD_SRC
    t = blob('scripts/checks/context_usage_warn.sh').split('\n')
    lo = next(i for i,l in enumerate(t) if l.startswith('_th_say'))
    hi = next(i for i,l in enumerate(t) if l.startswith('fix_threshold ')) # 最初の呼の手前まで
    GUARD_SRC = '\n'.join(t[lo:hi])
    io.open('ki/41_guard_utsushi.sh','w',encoding='utf-8').write(
        u'# 41_guard_utsushi.sh ―― 凍結点 %s:scripts/checks/context_usage_warn.sh L%d-%d の ★逐語の写し★。\n'
        u'# ★生器へは一字も書いて居らぬ。束内の写しである(作法⑴)。★\n%s\n' % (FREEZE, lo+1, hi, GUARD_SRC))
    return GUARD_SRC

def is_num(v):
    """★判ずるのは bash 自身★ ―― test(1) が整数の項として受けるか否か。"""
    rc, so, se = run('[ "$V" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; echo rc=$?', {'V': v})
    return so.strip().endswith('rc=0')

def otsu(name, default):
    g = guard_src(); out = []
    for lab, val in DOKU:
        setup = ('unset %s'%name) if val is None else ('%s=%s'%(name, shq(val)))
        sc = ('set +u\n%s\n%s\nexport %s\nfix_threshold %s %s __OUT\n'
              'echo "VALUE=$__OUT"\n') % (g, setup, name, name, default)
        rc, so, se = run(sc, {})
        v = ''
        for l in so.split('\n'):
            if l.startswith('VALUE='): v = l[6:]
        out.append({'doku':lab,'value':v,'natta':1 if se.strip() else 0,'koe':se.strip()[:90]})
    return out

kess = json.load(io.open('nama/32_kessai3.json',encoding='utf-8'))
bos  = json.load(io.open('nama/23_bosuu4.raw',encoding='utf-8'))
texts = {}
def lineof(path, n):
    if path not in texts: texts[path] = (blob(path) or '').split('\n')
    L = texts[path]
    return L[n-1] if 0 < n <= len(L) else ''

print(u'★第52弾 ㋑ ―― fail-open に成る入力を、★實際に当てた★ 記録★')
print(u'凍結点=%s ／ 器=ki/42_hatan2.py ／ guard の写し=ki/41_guard_utsushi.sh' % FREEZE)
print(u'毒の六形: ' + u' / '.join(l for l,_ in DOKU))
print(u'')

# 甲 = guard 側 22 本
print(u'━━ 甲 ★guard(fix_threshold)を通る 22 本★ ―― 毒を guard へ通した結果 ━━')
kou_bad = 0
for r in kess['freeze']:
    o = otsu(r['name'], r['def'])
    bad = [p for p in o if not is_num(p['value'])]
    tag = u'★閾が非数の儘 残る毒= %s★' % u'・'.join(p['doku'] for p in bad) if bad else u'★毒六形 悉く 数へ倒れた(fail-closed)★'
    if bad: kou_bad += 1
    print(u'  %s:%d %s' % (r['file'], r['decl'], r['name']))
    for p in o:
        print(u'     毒=%-10s → 閾=%-22s 鳴=%d %s' % (p['doku'], repr(p['value']), p['natta'], p['koe'][:60]))
    print(u'     ⇒ %s' % tag)

# 乙 = 素で比べる側
print(u'')
print(u'━━ 乙 ★素で比べる箇所★ ―― 毒を比較器へ直に当てた結果(rc=2 が fail-open) ━━')
guarded = set((r['file'], r['name']) for r in kess['freeze'])
otsu_rows = [r for r in bos['rows'] if (r['file'], r['env']) not in guarded and r['cmp_lines']]
n2 = 0
for r in sorted(otsu_rows, key=lambda x:(x['file'],x['env'])):
    ln = r['cmp_lines'][0]
    s = sona(lineof(r['file'], ln), r['env'])
    if not s: continue
    n2 += 1
    rcs = u' '.join(u'%s:rc%d' % (p['doku'], p['rc']) for p in s['probes'])
    fo = [p['doku'] for p in s['probes'] if p['rc'] == 2]
    print(u'  %s:%d %-30s 式=[ %s ]' % (r['file'], ln, r['env'], s['expr']))
    print(u'     %s   ⇒ ★fail-open(rc=2)に成る毒= %s★' % (rcs, u'・'.join(fo) if fo else u'無し'))
print(u'')
print(u'━━ 結 ━━')
print(u'  甲 guard 22本 ―― 毒六形を悉く当てた。★閾が非数の儘 残つた本数= %d★' % kou_bad)
print(u'  乙 素の箇所 ―― 式を取れた %d 本に毒六形を当てた(取れなんだ物は式が比較器の形でない)。' % n2)
sys.stderr.write(u'★破れ器 了 甲=%d 乙=%d★\n' % (len(kess['freeze']), n2))
