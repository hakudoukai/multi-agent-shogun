#!/usr/bin/env python3
# 乙′ の測り ―― 生器四本から「閾の番人」の塊を★其の場で抜き★、三形(A 毎回/B 黙る/C 一度)で鳴りを数へる。
# 生器は読取のみ。走らせるのは抜いた塊のみ(daemon 本体は起動せぬ)。
import re,subprocess,sys,os,tempfile
FILES=[("watcher","scripts/inbox_watcher.sh"),
       ("watchdog","scripts/watchdogs/enter_restart_common_watchdog.sh"),
       ("health","scripts/agent_health_check.sh"),
       ("warn","scripts/checks/context_usage_warn.sh")]
def block(src):
    L=src.splitlines(True)
    s=next(i for i,l in enumerate(L) if l.startswith("_th_say("))
    fi=next(i for i,l in enumerate(L) if l.startswith("fix_threshold("))
    e=next(i for i in range(fi,len(L)) if L[i].rstrip("\n")=="}")
    return "".join(L[s:e+1]), s+1, e+1
def thresholds(src):
    out=[]
    for m in re.finditer(r'^\s*fix_threshold ([A-Z_][A-Z0-9_]*) (\S+) ([A-Z_][A-Z0-9_]*)',src,re.M):
        out.append((m.group(1),m.group(2)))
    for m in re.finditer(r'^\s*for _t in (.+?); do',src,re.M|re.S):
        for tok in re.findall(r'([A-Z_][A-Z0-9_]*):(\d+)',m.group(1)): out.append(tok)
    return out
def run(blk,ths,form,case_var=None,case_val=None):
    # form A=毎回(番人を外す) B=黙る(旧 ab2a1f1) C=一度(裁323687⑵)
    b=blk
    if form=="A":
        b=b.replace('if [ "${_th_unset_told:-0}" -eq 0 ]; then','if [ 1 -eq 1 ]; then')
    if form=="B":
        b=re.sub(r'    unset\)\n(?:.*\n)*?      eval "\$_ft_o=\\\$_ft_d"; return 0 ;;\n',
                 '    unset) eval "$_ft_o=\\$_ft_d"; return 0 ;;\n', b, count=1)
    body=['log(){ printf "%s\\n" "$*" >&2; }', b]
    for n,d in ths:
        body.append('unset %s'%n)
    if case_var is not None:
        body.append('%s=%s; export %s'%(case_var,case_val,case_var))
    for n,d in ths:
        body.append('fix_threshold %s %s OUT_%s'%(n,d,n))
        body.append('printf "RESULT %s=[%%s]\\n" "$OUT_%s"'%(n,n))
    with tempfile.NamedTemporaryFile('w',suffix='.sh',delete=False,encoding='utf-8') as fh:
        fh.write("\n".join(body)+"\n"); p=fh.name
    r=subprocess.run(["/bin/bash",p],capture_output=True,text=True)
    os.unlink(p)
    nari=[l for l in r.stderr.splitlines() if "閾" in l]
    res=dict(re.findall(r'RESULT ([A-Z_][A-Z0-9_]*)=\[(.*)\]',r.stdout))
    return nari,res,r.returncode
print("★乙′ 三形の鳴り ―― 生器四本・閾は實際の呼び出しから取つた★")
for tag,f in FILES:
    src=open(f,encoding='utf-8').read()
    blk,l0,l1=block(src); ths=thresholds(src)
    print("\n== %s : %s L%d-%d 閾=%d本 (%s) =="%(tag,f,l0,l1,len(ths),",".join(n for n,_ in ths)))
    for form,name in (("A","形A 裁322952の字義=毎回刷る"),("B","形B ab2a1f1=未設定は黙る"),("C","形C 裁323687⑵=一度だけ")):
        nari,res,rc=run(blk,ths,form)
        print("  %-28s 未設定悉く → 鳴=%d rc=%d"%(name,len(nari),rc))
        if form=="C" and nari: print("      逐語: %s"%nari[0])
    v0=ths[0][0]
    for cv,label in (("''","負 乙空文字"),("'   '","負 乙空白のみ"),("99999999999999999999","負 甲20桁"),("7","陽性 正しい値")):
        nari,res,rc=run(blk,ths,"C",v0,cv)
        print("  形C %-14s %s=%s → 鳴=%d RESULT %s=[%s]"%(label,v0,cv,len(nari),v0,res.get(v0)))
