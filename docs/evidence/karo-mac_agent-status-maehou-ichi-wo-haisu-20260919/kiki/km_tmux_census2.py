# -*- coding: utf-8 -*-
# 第二の歩行器: ★走る器★のみを母數とし、tmux の的を
#   甲 -t 直の裸名  乙 的を組む代入行(裸 session 名)  丙 pane_id  丁 =完全一致
# へ分ける。変数へ落ちる物は「代入の源」を見て判ずる。
import os, sys, re, io, stat
SKIPDIR = {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache",
           "worktrees", "backups", "test-results", "evidence"}
EXT = ('.sh', '.py', '.bats', '.zsh', '.bash')
# 既知の session 名(裸で書かれると前方一致の的に成る)
SESS = r'(?:multiagent|shogun-main|shogun-second|shogun-third|shogun|hermes-[A-Za-z0-9_-]+|multiagent-mac|gunshi)'
RE_BARE_T   = re.compile(r'-t[= ]+(["\']?)(' + SESS + r')(?![A-Za-z0-9_-])')
RE_ASSIGN   = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(["\']?)(' + SESS + r')(?![A-Za-z0-9_-])([^\s"\']*)')
RE_PANEID_T = re.compile(r'-t[= ]+(["\']?)%')
RE_EQ_T     = re.compile(r'-t[= ]+(["\']?)=')

roots = sys.argv[1:]
n_file=n_ki=n_read=0; rc=0
bare=[]; asg=[]; pid=[]; eqm=[]
skipped_ext=0
for root in roots:
    if not os.path.exists(root):
        print("★根が無い★ %s"%root); rc=1; continue
    if os.path.isfile(root):
        cand=[root]
    else:
        cand=[]
        for dp,dns,fns in os.walk(root):
            dns[:]=[d for d in dns if d not in SKIPDIR]
            for fn in fns: cand.append(os.path.join(dp,fn))
    for p in cand:
        if os.path.islink(p) or not os.path.isfile(p): continue
        n_file+=1
        try: st=os.stat(p)
        except OSError: rc=1; continue
        is_exec = bool(st.st_mode & stat.S_IXUSR)
        if not (p.endswith(EXT) or is_exec):
            skipped_ext+=1; continue
        if '.bak' in p or p.endswith('~'): skipped_ext+=1; continue
        n_ki+=1
        try: b=io.open(p,'rb').read()
        except OSError: rc=1; continue
        if b'\0' in b: continue
        s=b.decode('utf-8','replace'); n_read+=1
        for i,ln in enumerate(s.split('\n'),1):
            t=ln.strip()
            if t.startswith('#') or t.startswith('//'): continue
            if 'tmux' in ln:
                for m in RE_BARE_T.finditer(ln): bare.append((p,i,m.group(2),t[:170]))
                if RE_PANEID_T.search(ln): pid.append((p,i,t[:120]))
                if RE_EQ_T.search(ln):     eqm.append((p,i,t[:120]))
            for m in RE_ASSIGN.finditer(ln):
                val=m.group(3)+m.group(4)
                if ':' in val or val in ('multiagent','shogun','multiagent-mac'):
                    asg.append((p,i,m.group(1),val,t[:170]))
print("=== 母數(★走る器★) ===")
print("根        = %s"%" ".join(roots))
print("rc(歩行)  = %d"%rc)
print("全file    = %d / 器(実行bit or 拡張子, .bak除) = %d / 読めた = %d / 器でない=%d"%(n_file,n_ki,n_read,skipped_ext))
def dump(title, rows, fmt):
    print(); print("=== %s : %d件 / %d本 ==="%(title,len(rows),len(set(r[0] for r in rows))))
    for r in rows: print(fmt%r)
dump("甲 ★-t に裸の session 名★(前方一致で当たる)", bare, "  %s:%d  的=%s\n      | %s")
dump("乙 ★的を組む代入に裸の session 名★(-t は変数ゆゑ甲に出ぬ)", asg, "  %s:%d  %s=%s\n      | %s")
print(); print("=== 丙 -t %%N (pane_id) : %d件 / %d本 ==="%(len(pid),len(set(r[0] for r in pid))))
for r in pid: print("  %s:%d | %s"%r)
print(); print("=== 丁 -t =名 (完全一致) : %d件 / %d本 ==="%(len(eqm),len(set(r[0] for r in eqm))))
for r in eqm: print("  %s:%d | %s"%r)
