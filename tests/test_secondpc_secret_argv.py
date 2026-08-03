#!/usr/bin/env python3
from pathlib import Path
import tempfile,subprocess,os,time,json,hashlib,shutil,sys,re
HERE=Path(__file__).resolve().parent
BASE=HERE if (HERE/'hakudokai_secondpc_watcher.sh').exists() else HERE.parent/'shim/hakudokai'
MOCK='mock_key_secondpc_argv_20260721'
MARKERS=[MOCK,'Authorization: Bearer','apikey:']
def scan(proc,samples=200,delay=.01):
 hits=set();n=0
 for _ in range(samples):
  n+=1
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:c=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='ignore')
   except:continue
   if any(x in c for x in MARKERS):hits.add((p.name,hashlib.sha256(c.encode()).hexdigest()))
  if proc.poll() is not None and _>100:break
  time.sleep(delay)
 return hits,n
with tempfile.TemporaryDirectory(prefix='secondpc_argv_test_') as td:
 t=Path(td);repo=t/'repo';d=repo/'shim/hakudokai';(d/'lib').mkdir(parents=True);b=t/'bin';b.mkdir();state=t/'state';state.mkdir();home=t/'home';(home/'.openclaw').mkdir(parents=True)
 for n in ['hakudokai_secondpc_watcher.sh','hakudokai_secondpc_watcher_poll.py','hakudokai_secondpc_receiver_poll.py']:shutil.copy2(BASE/n,d/n)
 helper=BASE/'sb_auth.sh' if (BASE/'sb_auth.sh').exists() else BASE/'lib/sb_auth.sh'
 shutil.copy2(helper,d/'lib/sb_auth.sh')
 calls=t/'calls.jsonl'
 fakecurl=b/'curl';fakecurl.write_text(r'''#!/usr/bin/env python3
import sys,os,json,time,stat
args=sys.argv[1:];cfg=None;out=None
for i,a in enumerate(args):
 if a=='--config' and i+1<len(args):cfg=args[i+1]
 if a=='-o' and i+1<len(args):out=args[i+1]
rec={'tool':'curl','argv_markers':sum(('mock_key_secondpc_argv_20260721' in a or 'Authorization: Bearer' in a or 'apikey:' in a) for a in args),'mode':oct(stat.S_IMODE(os.stat(cfg).st_mode)) if cfg else None,'config_headers':None}
if cfg:
 s=open(cfg).read();rec['config_headers']=int('Authorization: Bearer' in s)+int('apikey:' in s)
with open(os.environ['CALLS'],'a') as f:f.write(json.dumps(rec)+'\n')
time.sleep(.5)
if out:json.dump([{'id':'11111111-2222-4333-8444-555555555555','from_pc':'second_pc','to_pc':'main_pc','topic':'mock','content':'mock','priority':'high','message_type':'answer','created_at':'2026-07-21T00:00:00Z'}],open(out,'w'))
''');fakecurl.chmod(0o755)
 fakepy=b/'python3';fakepy.write_text(r'''#!/usr/bin/env bash
if [[ "${1:-}" == *secondpc_watcher_poll.py ]]; then
 markers=0
 for a in "$@"; do
  case "$a" in *mock_key_secondpc_argv_20260721*|*"Authorization: Bearer"*|*"apikey:"*) markers=$((markers+1));; esac
 done
 printf '{"tool":"python_child","argv_markers":%d,"argc":%d}\n' "$markers" "$(( $# - 1 ))" >>"${CALLS:?}"
 /bin/sleep .5
 exit 0
else
 exec /usr/bin/python3 "$@"
fi
''');fakepy.chmod(0o755)
 env={**os.environ,'PATH':str(b)+os.pathsep+os.environ['PATH'],'HOME':str(home),'SUPABASE_URL':'https://mock.invalid','SUPABASE_SERVICE_ROLE_KEY':MOCK,'CALLS':str(calls),'SECONDPC_WATCHER_PROCESSED_FILE':str(state/'processed'),'SECONDPC_WATCHER_RESPONSE_TMP':str(state/'response.json'),'SECONDPC_WATCHER_HEALTH_FILE':str(state/'health.json'),'SECONDPC_WATCHER_RETRY_TRACKER_FILE':str(state/'retry.json')};(state/'processed').write_text('')
 # RED detector capability with mock-only vulnerable argv shape.
 red=subprocess.Popen([str(fakecurl),'-H',f'Authorization: Bearer {MOCK}','-H',f'apikey: {MOCK}'],env=env);rh,_=scan(red,120,.005);red.wait()
 if not rh:raise SystemExit('RED detector missed vulnerable mock argv')
 # Require the deliberate RED process to disappear before GREEN accounting.
 for _ in range(50):
  stale=False
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:c=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='ignore')
   except:continue
   if any(x in c for x in MARKERS):stale=True;break
  if not stale:break
  time.sleep(.02)
 if stale:raise SystemExit('RED probe did not quiesce before GREEN')
 calls.write_text('')
 green=subprocess.Popen(['bash',str(d/'hakudokai_secondpc_watcher.sh'),'--once'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);gh,samples=scan(green,220,.01);o,e=green.communicate(timeout=10)
 if green.returncode!=0:raise SystemExit(f'watcher rc={green.returncode} stderr={e}')
 recs=[json.loads(x) for x in calls.read_text().splitlines() if x.strip()]
 if gh or len(recs)!=2 or any(r['argv_markers'] for r in recs):raise SystemExit(f'GREEN argv failure hits={gh} recs={recs} watcher_stderr={e}')
 cr=[r for r in recs if r['tool']=='curl'][0];pr=[r for r in recs if r['tool']=='python_child'][0]
 if cr['mode']!='0o600' or cr['config_headers']!=2 or pr['argc']!=4:raise SystemExit(f'GREEN contract failure {recs}')
 # Real pollers accept four positionals + env and reject missing env; no argv fallback.
 empty=state/'empty.json';empty.write_text('[]');processed=state/'poll_processed';processed.write_text('')
 for poll in [d/'hakudokai_secondpc_watcher_poll.py',d/'hakudokai_secondpc_receiver_poll.py']:
  ok=subprocess.run(['/usr/bin/python3',str(poll),str(empty),str(processed),str(repo),'https://mock.invalid/rest/v1'],env=env,capture_output=True,text=True)
  if ok.returncode!=0:raise SystemExit(f'poll env run failed {poll.name}')
  badenv=dict(env);badenv.pop('SUPABASE_SERVICE_ROLE_KEY',None)
  bad=subprocess.run(['/usr/bin/python3',str(poll),str(empty),str(processed),str(repo),'https://mock.invalid/rest/v1'],env=badenv,capture_output=True,text=True)
  if bad.returncode==0:raise SystemExit(f'poll missing-env fail-closed absent {poll.name}')
 residue=[]
 for p in Path('/tmp').glob('sb_auth.*'):
  try:
   if MOCK in p.read_text(errors='ignore'):residue.append(str(p))
  except:pass
 if residue:raise SystemExit(f'residue {residue}')
 print(json.dumps({'RED_mock_hit_fingerprints':len(rh),'GREEN_samples':samples,'GREEN_interval_ms':10,'GREEN_exact_or_header_hits':0,'curl_config_mode':'0600','curl_config_headers':2,'python_child_argc_without_secret':4,'poller_env_only_pass':2,'poller_missing_env_fail_closed':2,'temp_residue':0},sort_keys=True))
