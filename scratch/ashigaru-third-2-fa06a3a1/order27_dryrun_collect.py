
import subprocess, sys, time, json, re
ROOT='/mnt/c/DentalBI'
SCRIPT=ROOT+'/scripts/sync_source_cache.py'
t0=time.time()
p=subprocess.Popen([sys.executable, SCRIPT, '--dry-run'], cwd=ROOT,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
MARK=b"INSERT INTO source_code_cache (file_path, content, line_count, file_size, commit_hash, updated_at)\n"
total=0; nmark=0; carry=b''; head=b''; paths=[]; stmt_bytes=[]; cur=0
VAL=re.compile(rb"^VALUES \('([^']*)'", re.M)
while True:
    chunk=p.stdout.read(1<<20)
    if not chunk: break
    total+=len(chunk)
    if len(head)<4096: head+=chunk[:4096-len(head)]
    buf=carry+chunk
    # count statement marks
    c=buf.count(MARK)
    if c:
        nmark+=c
        for m in VAL.finditer(buf):
            paths.append(m.group(1).decode('utf-8','replace'))
    carry=buf[-len(MARK)-4096:] if len(buf)>len(MARK)+4096 else buf
    # avoid double counting: drop counted portion
    if c:
        carry=buf[buf.rfind(MARK)+len(MARK):][-4096:]
err=p.stderr.read().decode('utf-8','replace')
rc=p.wait()
el=time.time()-t0
out={'stdout_bytes':total,'insert_marks':nmark,'paths_seen':len(paths),'paths_head':paths[:3],
     'stderr':err,'returncode':rc,'elapsed_sec':round(el,1)}
json.dump(out, open('/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/order27_dryrun_agg.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
open('/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/order27_dryrun_head.txt','wb').write(head[:400])
print('done', out['stdout_bytes'], out['insert_marks'], out['elapsed_sec'], rc)
