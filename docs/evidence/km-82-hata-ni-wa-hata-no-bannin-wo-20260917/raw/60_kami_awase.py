# -*- coding: utf-8 -*-
# ★紙⇔測り の照合器★(第82弾)
#   ・節を限る(裁の教: 節を限らぬ紙合せ器は同名行を拾ふ)
#   ・紙の値は ★節の中からのみ★ 引く。測りの値は raw/ と disk と git から ★その場で★ 取る。
#   ・出目は TSV(節 / 主張 / 紙 / 測り / 判)。★一本でも食ひ違へば rc=1★(fail-closed)
import re, subprocess, hashlib, os, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.abspath(os.path.join(B, '..', '..', '..'))

def read(p):
    return open(p, encoding='utf-8').read()

def sha16(path):
    return hashlib.sha256(open(path,'rb').read()).hexdigest()[:16]

def lines(path):
    # ★行=改行で終はらぬ末尾も一行と数へる(grep -c '' と同義)★
    b = open(path,'rb').read()
    if not b: return 0
    n = b.count(b'\n')
    return n if b.endswith(b'\n') else n+1

kami = read(os.path.join(B,'README.md'))

def setsu(name):
    """見出し `## <name>` から次の `## ` 迄(同階層)。無ければ ★測れぬ★ を投げる。"""
    m = re.search(r'^##\s+'+re.escape(name)+r'.*$', kami, re.M)
    if not m: sys.exit('★測れぬ★ 節が紙に無い: %s' % name)
    s = m.end()
    m2 = re.search(r'^##\s', kami[s:], re.M)
    return kami[s:s+m2.start()] if m2 else kami[s:]

def nums(text):
    """符号と桁区切りを許す整数の列(★符号に寛容★)"""
    return [int(x.replace(',','')) for x in re.findall(r'[-+]?\d[\d,]*', text)]

def has(text, s):
    return s in text

rows = []
ng = 0
def cmp(setsu_name, claim, kami_v, hakari_v):
    global ng
    ok = (str(kami_v) == str(hakari_v))
    if not ok: ng += 1
    rows.append((setsu_name, claim, str(kami_v), str(hakari_v), '○' if ok else '★×★'))

# ── 二 前後の姿 ──
s2 = setsu('二 ―― 前後の姿')
hik = os.path.join(B,'_before','inbox_watcher.sh.snapshot')
ima = os.path.join(R,'scripts','inbox_watcher.sh')
cmp('二','控 行', 1666 if '1666' in s2 else None, lines(hik))
cmp('二','控 sha16', '15ac9f97f473245d' if '15ac9f97f473245d' in s2 else None, sha16(hik))
cmp('二','今 行', 1700 if '1700' in s2 else None, lines(ima))
cmp('二','今 sha16', '494c8c788d50d724' if '494c8c788d50d724' in s2 else None, sha16(ima))
cmp('二','bash -n rc', 0 if 'rc=0' in s2 else None,
    subprocess.run(['bash','-n',ima]).returncode)

def diffcount(p):
    L = read(os.path.join(B,p)).split('\n')
    if L and L[-1]=='': L = L[:-1]
    r = len([x for x in L if x=='>' or x.startswith('> ')])
    l = len([x for x in L if x=='<' or x.startswith('< ')])
    return r, l

r,l = diffcount('raw/05_hikae_vs_ima.diff')
cmp('二','控⇔今 相違', 36 if '**36行**' in s2 else None, r+l)
cmp('二','控⇔今 右/左', '35/1' if '右35/左1' in s2 else None, '%d/%d'%(r,l))
r2,l2 = diffcount('raw/06_main_vs_hikae.diff')
cmp('二','main⇔控 相違', 130 if '**130行**' in s2 else None, r2+l2)
cmp('二','main⇔控 右/左', '121/9' if '右121/左9' in s2 else None, '%d/%d'%(r2,l2))

# ── 二之補 commit を二本に ──
s2b = setsu('二 ―― 前後の姿')  # 二之補は ### ゆゑ二の中
A = '1b9304262c6a98c433398b4da0d67c03a8466559'
cmp('二之補','commit A の sha(紙)', A if A in kami else None, A)
oya = read(os.path.join(B,'raw','07_oya_kenme.txt'))
cmp('二之補','71 の判', '断り不要' if '★断り不要★' in s2b else None,
    '断り不要' if '★断り不要★' in oya else '断り要')
cmp('二之補','71 の親 = A', A[:12], re.search(r'親\(([0-9a-f]{40})\)', oya).group(1)[:12])
ob = re.search(r'親.*blob=([0-9a-f]+)', oya).group(1)
hb = re.search(r'控\s+blob=([0-9a-f]+)', oya).group(1)
cmp('二之補','親 blob = 控 blob', ob, hb)

# ── 三 現形の穴 ──
s3 = setsu('三 ―― 現形の穴(十二形・毒の実測)')
tsv = [x.split('\t') for x in read(os.path.join(B,'raw','20_doku12.tsv')).rstrip('\n').split('\n')]
head, body = tsv[0], tsv[1:]
gen = [c for c in body if c[0]=='genkei']
nao = [c for c in body if c[0]=='naoshi']
cmp('三','現形 走数', 12 if '12形' in s3 else None, len(gen))
cmp('三','現形 BRANCH無', 9 if '= 9形' in s3 else None, len([c for c in gen if c[4]=='★無★']))
cmp('三','★毒による黙り★', 8 if '8形★' in s3 else None,
    len([c for c in gen if c[4]=='★無★' and '正常' not in c[1]]))
cmp('三','現形 報せ和', 0 if '報せ 0行' in s3 else None, sum(int(c[5]) for c in gen))
cmp('三','現形 外の声和', 0 if '外の声 0行' in s3 else None, sum(int(c[6]) for c in gen))
cmp('三','現形 rc非0', 0 if '悉く 0★' in s3 else None, len([c for c in gen if c[3]!='0']))
cmp('三','直し形 報せ有る形', 10 if '報せ 10形★' in s3 else None,
    len([c for c in nao if int(c[5])>0]))
cmp('三','直し形 BRANCH無', 1 if '縮退 1形' in s3 else None, len([c for c in nao if c[4]=='★無★']))
cmp('三','両形 外の声和', 0 if '悉く 0行' in s3 else None, sum(int(c[6]) for c in body))

# ── 四 稼働 ──
s4 = setsu('四 ―― 稼働中の器と disk は別物である')
kad = read(os.path.join(B,'raw','22_kadou.txt'))
cmp('四','稼働本数', 3 if '稼働3本' in s4 or '3本' in s4 else None,
    int(re.search(r'稼働本数=(\d+)', kad).group(1)))
di = re.search(r'inode=(\d+)', kad).group(1)
ki = re.findall(r'開いて居る=(\d+)/', kad)
cmp('四','稼働の inode が一種', 1, len(set(ki)))
cmp('四','disk ≠ 稼働', '異', '異' if di not in ki else '同')

# ── 五 直し形 ──
s5 = setsu('五 ―― 直し形(据ゑた物の逐語)')
src = read(ima).split('\n')
i_ff = [i+1 for i,x in enumerate(src) if x=='fix_flag(){']
cmp('五','fix_flag の頭 行番', 175 if 'L175-197' in s5 else None, i_ff[0] if i_ff else 0)
end = None
for i in range(i_ff[0]-1, len(src)):
    if src[i] == '}': end = i+1; break
cmp('五','fix_flag の尾 行番', 197 if 'L175-197' in s5 else None, end)
i_call = [i+1 for i,x in enumerate(src) if x.startswith('fix_flag ASW_PROCESS_TIMEOUT')]
cmp('五','呼出 行番', 258 if 'L255-258' in s5 else None, i_call[0] if i_call else 0)
# ★註の行を除かねば己の引用を拾ふ(疵: 初走は L257 の註を比較器と誤つた)★
i_hk = [i+1 for i,x in enumerate(src)
        if 'ASW_PROCESS_TIMEOUT' in x and '= "1"' in x and not x.lstrip().startswith('#')]
cmp('五','比較器 行番', 1633 if 'L1633' in setsu('一 ―― 裁の指す⑵ は何であつたか') else None,
    i_hk[0] if i_hk else 0)
cmp('五','古い受ける口は消えて居る', 0,
    len([x for x in src if x.strip()=='ASW_PROCESS_TIMEOUT=${ASW_PROCESS_TIMEOUT:-1}']))
cmp('五','控には古い口が在る', 1,
    len([x for x in read(hik).split('\n') if x.strip()=='ASW_PROCESS_TIMEOUT=${ASW_PROCESS_TIMEOUT:-1}']))
# ★比較器の片は 10_slice.py が錨で切つた物を讀む(己の定義で切り直せば別物に成る)★
sg = os.path.join(B,'raw','slice_genkei_hikaku.sh')
sn = os.path.join(B,'raw','slice_naoshi_hikaku.sh')
cmp('五','比較器片 sha16(控)', '09a13b50f6d5fb98' if '09a13b50f6d5fb98' in s5 else None, sha16(sg))
cmp('五','比較器片 sha16(今)', '09a13b50f6d5fb98' if '09a13b50f6d5fb98' in s5 else None, sha16(sn))
cmp('五','比較器片 控=今', sha16(sg), sha16(sn))
cmp('五','比較器片 行', 7 if '7行' in s5 else None, lines(sg))

# ── 六 両対照 ──
s6 = setsu('六 ―― 両対照(negative / positive)')
tai = read(os.path.join(B,'raw','21_taishou.txt'))
m = re.search(r'○=(\d+)/(\d+)', tai)
cmp('六','対照 ○/母數', '5/5' if '○5/5' in s6 or '5/5' in s6 else None, '%s/%s'%(m.group(1),m.group(2)))
cmp('六','判', '通' if '判=通' in tai else '落', '通' if '判=通' in tai else '落')

out = ['節\t主張\t紙\t測り\t判'] + ['\t'.join(r) for r in rows]
out.append('')
out.append('母數=%d / ○=%d / ★×=%d★' % (len(rows), len(rows)-ng, ng))
txt = '\n'.join(out) + '\n'
open(os.path.join(B,'raw','61_kami_awase.tsv'),'w',encoding='utf-8').write(txt)
sys.stdout.write(txt)
sys.exit(1 if ng else 0)
