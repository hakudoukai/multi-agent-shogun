# -*- coding: utf-8 -*-
"""衝突印走査 ―― 引数の根を歩き(regular file のみ)、行頭の <<<<<<< / ======= / >>>>>>> を数へる。
出目: 四つの札(根・深さ・rc・刻)+ 三印の行数 + 「印が順に揃つた file」の数。"""
import os, sys, stat, time, re
root = sys.argv[1]
exclude_dirs = {'.git'}
files=0; maxdepth=0; n_lt=0; n_eq=0; n_gt=0; ordered=[]; lt_files=[]; eq_files=[]; gt_files=[]
skipped_nonreg=0
for dp, dns, fns in os.walk(root):
    dns[:] = [d for d in dns if d not in exclude_dirs]
    depth = dp[len(root):].count(os.sep)
    for fn in fns:
        p=os.path.join(dp,fn)
        st=os.lstat(p)
        if not stat.S_ISREG(st.st_mode):
            skipped_nonreg+=1; continue
        files+=1; maxdepth=max(maxdepth, depth+1)
        with open(p,'rb') as f: data=f.read()
        rel=os.path.relpath(p,root)
        lt=[i for i,l in enumerate(data.split(b'\n')) if l.startswith(b'<<<<<<< ')]
        eq=[i for i,l in enumerate(data.split(b'\n')) if l.rstrip(b'\r')==b'=======']
        gt=[i for i,l in enumerate(data.split(b'\n')) if l.startswith(b'>>>>>>> ')]
        n_lt+=len(lt); n_eq+=len(eq); n_gt+=len(gt)
        if lt: lt_files.append((rel,len(lt)))
        if eq: eq_files.append((rel,len(eq)))
        if gt: gt_files.append((rel,len(gt)))
        # 順に揃つた印(<<<<<<< → ======= → >>>>>>>)
        for a in lt:
            e=[i for i in eq if i>a]; g=[i for i in gt if e and i>e[0]]
            if e and g: ordered.append((rel,a+1)); break
print("root=%s"%root)
print("files_walked=%d maxdepth=%d skipped_nonregular=%d"%(files,maxdepth,skipped_nonreg))
print("lines_lt(行頭'<<<<<<< ')=%d  files=%d"%(n_lt,len(lt_files)))
print("lines_eq(行全体'=======')=%d  files=%d"%(n_eq,len(eq_files)))
print("lines_gt(行頭'>>>>>>> ')=%d  files=%d"%(n_gt,len(gt_files)))
print("files_with_ordered_triplet=%d"%len(ordered))
for r,n in lt_files: print("  lt %s x%d"%(r,n))
for r,n in gt_files: print("  gt %s x%d"%(r,n))
for r,n in eq_files[:40]: print("  eq %s x%d"%(r,n))
if len(eq_files)>40: print("  eq ... (%d more)"%(len(eq_files)-40))
for r,l in ordered: print("  ORDERED %s L%d"%(r,l))
print("koku=%s"%time.strftime('%Y-%m-%dT%H:%M:%S%z'))
sys.exit(1 if ordered else 0)
