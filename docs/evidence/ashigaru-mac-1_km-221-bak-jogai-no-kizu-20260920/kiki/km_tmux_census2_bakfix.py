# -*- coding: utf-8 -*-
# km-221: 旧器(km_tmux_census2.py sha256=956c4669...)の .bak 除外を三形へ拡げた新器。
# 旧器の本体(甲/乙/丙/丁 census 部)は不変・変更点=行38の除外条件のみ+bak三形の計測を追加。
import os, sys, re, io, stat
SKIPDIR = {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache",
           "worktrees", "backups", "test-results", "evidence"}
EXT = ('.sh', '.py', '.bats', '.zsh', '.bash')
SESS = r'(?:multiagent|shogun-main|shogun-second|shogun-third|shogun|hermes-[A-Za-z0-9_-]+|multiagent-mac|gunshi)'
RE_BARE_T   = re.compile(r'-t[= ]+(["\']?)(' + SESS + r')(?![A-Za-z0-9_-])')
RE_ASSIGN   = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(["\']?)(' + SESS + r')(?![A-Za-z0-9_-])([^\s"\']*)')
RE_PANEID_T = re.compile(r'-t[= ]+(["\']?)%')
RE_EQ_T     = re.compile(r'-t[= ]+(["\']?)=')

FORM1 = '.bak'
FORM2 = '.bak-'
FORM3 = '-bak-'

roots = sys.argv[1:]
n_file=n_ki=n_read=0; rc=0
bare=[]; asg=[]; pid=[]; eqm=[]
skipped_ext=0
cand_all=[]
form1_hits=[]; form2_hits=[]; form3_hits=[]
newly_excluded=[]  # 旧filterでは残つたが新filterで落ちた file
git_control_seen=False
git_control_target = None
neg_control_seen=False
neg_control_target = None
for ridx, root in enumerate(roots):
    if not os.path.exists(root):
        print("★根が無い★ %s"%root); rc=1; continue
    if os.path.isfile(root):
        cand=[root]
    else:
        cand=[]
        for dp,dns,fns in os.walk(root):
            dns[:]=[d for d in dns if d not in SKIPDIR]
            for fn in fns: cand.append(os.path.join(dp,fn))
    cand_all.extend(cand)
    for p in cand:
        if os.path.islink(p) or not os.path.isfile(p): continue
        n_file+=1
        try: st=os.stat(p)
        except OSError: rc=1; continue
        is_exec = bool(st.st_mode & stat.S_IXUSR)
        if not (p.endswith(EXT) or is_exec):
            skipped_ext+=1; continue
        hit1 = FORM1 in p
        hit2 = FORM2 in p
        hit3 = FORM3 in p
        if hit1: form1_hits.append(p)
        if hit2: form2_hits.append(p)
        if hit3: form3_hits.append(p)
        if hit1 or hit2 or hit3 or p.endswith('~'):
            skipped_ext+=1
            if not hit1:
                newly_excluded.append((p, hit1, hit2, hit3))
            continue
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

print("=== 母數(★走る器★・新器=三形bak除外) ===")
print("根        = %s"%" ".join(roots))
print("rc(歩行)  = %d"%rc)
print("全file    = %d / 器(実行bit or 拡張子, bak三形除) = %d / 読めた = %d / 器でない=%d"%(n_file,n_ki,n_read,skipped_ext))

def dump(title, rows, fmt):
    print(); print("=== %s : %d件 / %d本 ==="%(title,len(rows),len(set(r[0] for r in rows))))
    for r in rows: print(fmt%r)
dump("甲 ★-t に裸の session 名★(前方一致で当たる)", bare, "  %s:%d  的=%s\n      | %s")
dump("乙 ★的を組む代入に裸の session 名★(-t は変数ゆゑ甲に出ぬ)", asg, "  %s:%d  %s=%s\n      | %s")
print(); print("=== 丙 -t %%N (pane_id) : %d件 / %d本 ==="%(len(pid),len(set(r[0] for r in pid))))
for r in pid: print("  %s:%d | %s"%r)
print(); print("=== 丁 -t =名 (完全一致) : %d件 / %d本 ==="%(len(eqm),len(set(r[0] for r in eqm))))
for r in eqm: print("  %s:%d | %s"%r)

print()
print("=== bak除外三形(排他性の實測) ===")
s1=set(form1_hits); s2=set(form2_hits); s3=set(form3_hits)
uni = s1|s2|s3
print("form1(literal '.bak')  hit件数=%d 実本数=%d"%(len(form1_hits), len(s1)))
print("form2(literal '.bak-') hit件数=%d 実本数=%d"%(len(form2_hits), len(s2)))
print("form3(literal '-bak-') hit件数=%d 実本数=%d"%(len(form3_hits), len(s3)))
print("和集合(いずれか1つ以上を含む) 実本数=%d"%len(uni))
ov12=s1&s2; ov13=s1&s3; ov23=s2&s3; ov123=s1&s2&s3
print("排他性: form1∩form2=%d本 / form1∩form3=%d本 / form2∩form3=%d本 / 三形全交差=%d本"%(len(ov12),len(ov13),len(ov23),len(ov123)))
if ov12 or ov13 or ov23:
    print("  ∴ 排他でない(重なりあり)。重なる本の逐語:")
    for p in sorted(ov12|ov13|ov23):
        print("    %s  form1=%s form2=%s form3=%s"%(p, p in s1, p in s2, p in s3))
else:
    print("  ∴ 三形は互いに排他(重なり無し)")

print()
print("=== 旧器母数に入り新器で抜けた file(名指し・hit件数) : %d本 ==="%len(newly_excluded))
for p,h1,h2,h3 in newly_excluded:
    print("  %s  form1=%s form2=%s form3=%s"%(p,h1,h2,h3))

print()
print("=== .git 配下 歩行対照(SKIPDIRに'.git'在り) ===")
git_targets = [t for t in cand_all if t.replace(os.sep,'/').find('/.git/')>=0 or t.replace(os.sep,'/').startswith('.git/')]
print("cand_all中 '.git/' を含む path の本数 = %d"%len(git_targets))
CTRL_POS_SUFFIX = ".git/logs/refs/heads/ashigaru-mac-1/km-181-mitsu-no-naoshi-kagyaku-bak-futekisuto-20260918"
CTRL_NEG_SUFFIX = "CLAUDE.md"
pos_hit = any(c.replace(os.sep,'/').endswith(CTRL_POS_SUFFIX) for c in cand_all)
neg_hit = any(c.replace(os.sep,'/').endswith(CTRL_NEG_SUFFIX) for c in cand_all)
print("陽性対照 %s が cand_all(全歩行file)に在るか = %s"%(CTRL_POS_SUFFIX, pos_hit))
print("陰性対照 %s が cand_all(全歩行file)に在るか = %s"%(CTRL_NEG_SUFFIX, neg_hit))
print("cand_all 総数 = %d"%len(cand_all))
