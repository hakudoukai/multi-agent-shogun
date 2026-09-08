
import subprocess, sys, time, json
ROOT='/mnt/c/DentalBI'
D='/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/'
scope=set(json.load(open(D+'order27_scope.json',encoding='utf-8'))['files'])
SEP=b"\n\nINSERT INTO source_code_cache (file_path, content, line_count, file_size, commit_hash, updated_at)\nVALUES ('"
t0=time.time()
p=subprocess.Popen([sys.executable, ROOT+'/scripts/sync_source_cache.py', '--dry-run'], cwd=ROOT,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
total=0; carry=b''; paths=[]
while True:
    chunk=p.stdout.read(1<<22)
    if not chunk: break
    total+=len(chunk)
    buf=carry+chunk
    parts=buf.split(SEP)
    for seg in parts[1:]:
        q=seg.find(b"'")
        paths.append(seg[:q].decode('utf-8','replace') if q>=0 and q<400 else '(截れ)')
    carry=parts[-1][-len(SEP)-500:]
err=p.stderr.read().decode('utf-8','replace'); rc=p.wait(); el=time.time()-t0
mono=[]; prev=''
for x in paths:
    if x in scope and x>prev: mono.append(x); prev=x
oos=[x for x in paths if x not in scope]
out={'stdout_bytes':total,'sep_matches':len(paths),'in_scope_monotonic':len(mono),
     'out_of_scope':len(oos),'out_of_scope_head':[x.split('/')[0]+'/…' for x in oos[:5]],
     'stderr':err,'rc':rc,'elapsed_sec':round(el,1),'last_path_dir':mono[-1].split('/')[0]+'/…' if mono else None}
json.dump(out, open(D+'order27_dryrun_agg2.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('done', out['sep_matches'], out['in_scope_monotonic'], out['elapsed_sec'])
