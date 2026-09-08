import subprocess, sys, time, json, hashlib
from pathlib import Path
W='/home/hakudoukai/a2/wt-order28-sync-rewrite'
D='/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/'
SEP=b"\n\nINSERT INTO source_code_cache (file_path, content, line_count, file_size, commit_hash, updated_at)\nVALUES ('"

def run(script_path, label):
    t0=time.time()
    p=subprocess.Popen([sys.executable, script_path, '--dry-run'], cwd=W,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    total=0; carry=b''; n=0; h=hashlib.sha256()
    while True:
        chunk=p.stdout.read(1<<22)
        if not chunk: break
        total+=len(chunk); h.update(chunk)
        buf=carry+chunk
        parts=buf.split(SEP)
        n+=len(parts)-1
        carry=parts[-1][-len(SEP)-8:]
    err=p.stderr.read().decode('utf-8','replace'); rc=p.wait()
    return {'label':label,'stdout_bytes':total,'sha256':h.hexdigest(),
            'sep_matches':n,'statements':(n+1 if total else 0),'stderr':err.strip().splitlines(),
            'rc':rc,'elapsed_sec':round(time.time()-t0,1)}

old=Path(W+'/scripts/_order28_old_sync_source_cache.py')  # repo_root=樹 に解決させる為 樹内に置く (追跡外・後で除く)
old.write_bytes(subprocess.run(['git','show','HEAD:scripts/sync_source_cache.py'],cwd=W,
                               capture_output=True).stdout)
try:
    res=[run(str(old),'旧 (HEAD:scripts/sync_source_cache.py)'),
         run(W+'/scripts/sync_source_cache.py','新 (a2-fa06a3a1-sync-rewrite)')]
finally:
    old.unlink(missing_ok=True)
out={'runs':res,
     'same_statements':res[0]['statements']==res[1]['statements'],
     'same_stdout_sha':res[0]['sha256']==res[1]['sha256']}
json.dump(out, open(D+'order28_dryrun_compare.json','w',encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('done', res[0]['statements'], res[1]['statements'], out['same_stdout_sha'])
