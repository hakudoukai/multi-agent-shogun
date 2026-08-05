#!/usr/bin/env python3
"""Role-specific pc_handshake watcher pair for an exact desktop Codex bridge.

Inbound: durable DB row -> atomic role job -> existing audited Windows actuator.
Outbound: role-origin DB row -> local durable receipt ledger (DB row is upstream transport).
No database ACK is written here; visible proof remains the completion gate.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,subprocess,time,urllib.parse,urllib.request,uuid

ROLE='senmu_codex_second'
THREAD_ID='019e1447-487e-7143-b7f0-095e7c6ba57f'
EXPECTED_TITLE='sha256:f012411f8fe7771469117bc8446f054ba62170ebd7c71af767a7f8f5973abea4'
EXPECTED_TITLE_SHA256='f012411f8fe7771469117bc8446f054ba62170ebd7c71af767a7f8f5973abea4'
EXPECTED_PLACEHOLDER_SHA256='562e03a4230482dcb807ab98b686ac0804c4f3af2aad32b7fd76c082089dcce7'
ROOT=pathlib.Path('/mnt/c/DentalBI/codex_comm/desktop-role-bridge/senmu_codex_second')
STATE_ROOT=pathlib.Path.home()/'.cache'/'dentalbi_senmu_desktop_route'
TRIGGER=ROOT/'bin'/'trigger_senmu_role_bridge.ps1'
POWERSHELL=pathlib.Path('/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe')
MAX_ATTEMPTS=3
MIN_SEQ=int(os.environ.get('SENMU_DESKTOP_MIN_SEQ','137986'))

def now_iso(): return time.strftime('%Y-%m-%dT%H:%M:%S%z')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def atomic_json(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp')
 tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,path)
def load(path):
 try:return json.loads(path.read_text(encoding='utf-8'))
 except:return {}
def fetch(params):
 url=os.environ.get('SUPABASE_URL','').rstrip('/');key=os.environ.get('SUPABASE_SERVICE_ROLE_KEY','')
 if not url or not key:raise RuntimeError('supabase_env_missing')
 req=urllib.request.Request(url+'/rest/v1/pc_handshake?'+urllib.parse.urlencode(params,safe='(),.*'))
 req.add_header('Authorization','Bearer '+key);req.add_header('apikey',key);req.add_header('Accept','application/json')
 with urllib.request.urlopen(req,timeout=15) as r:data=json.load(r)
 return data if isinstance(data,list) else []
def rules():
 names=('AGENTS.md','senmu-role-AGENTS.md','delivery-protocol.md','visual-first-verification.md');out=[]
 for n in names:
  p=ROOT/'canon'/n
  if not p.exists():raise RuntimeError('required_rule_missing:'+n)
  out.append({'name':n,'sha256':sha(p),'target':str(p).replace('/mnt/c/','C:/').replace('/','\\')})
 return out
def win(path):
 s=str(path)
 if s.startswith('/mnt/c/'):return 'C:\\'+s[len('/mnt/c/'):].replace('/','\\')
 return s
def eligible(row):
 if not row.get('id'):return False
 if row.get('message_type')=='ack':return False
 t=str(row.get('topic') or '')
 return not (t.startswith('[ACK') or ('enter_restart' in t and row.get('message_type')=='status_update'))
def notice(row):
 topic=' '.join(str(row.get('topic') or '').split())[:180]
 return f"pc_handshake新着\nseq={row.get('seq')}\nfrom={row.get('from_pc')}\ntopic={topic}\n本文・証拠はSupabase pc_handshakeの当該seqをSELECTして確認。受領だけでなく処理結果をparented reply。"
def trigger(row,state):
 mid=str(row['id']);seq=int(row['seq']);payload=notice(row)
 inbox=ROOT/'inbox';outbox=ROOT/'outbox';inbox.mkdir(parents=True,exist_ok=True);outbox.mkdir(parents=True,exist_ok=True)
 payload_path=inbox/f'{seq}--pc-handshake.notice';payload_path.write_text(payload,encoding='utf-8')
 nonce=hashlib.sha256(f'{mid}:{sha(payload_path)}:{time.time_ns()}'.encode()).hexdigest()
 status_path=outbox/f'{mid}.{nonce}.actuator.json'
 job={'allow_live':True,'attempt_nonce':nonce,'dry_run':False,'expected_title':EXPECTED_TITLE,'expected_title_sha256':EXPECTED_TITLE_SHA256,'expected_placeholder_sha256':EXPECTED_PLACEHOLDER_SHA256,'job_id':f'pc-handshake-seq{seq}','parent_message_id':mid,'payload_file':win(payload_path),'payload_sha256':sha(payload_path),'required_rules':rules(),'role':ROLE,'status_file':win(status_path),'thread_id':THREAD_ID,'timeout_seconds':20}
 atomic_json(ROOT/'current-job.json',job)
 completed=subprocess.run([str(POWERSHELL),'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',win(TRIGGER)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=False,timeout=55)
 result=load(status_path)
 return {'rc':completed.returncode,'result':result,'status_file':str(status_path),'payload_sha256':sha(payload_path),'job_id':job['job_id']}
def inbound_once(state):
 rows=fetch({'select':'id,seq,message_type,from_pc,to_pc,topic,priority,created_at','to_pc':f'eq.{ROLE}','acknowledged_at':'is.null','seq':f'gt.{MIN_SEQ}','order':'seq.asc','limit':'25'})
 handled=state.setdefault('rows',{})
 for row in rows:
  if not eligible(row):continue
  rid=str(row['id']);saved=handled.get(rid,{})
  if saved.get('status') in ('pending_visual','processed_by_role','delivery_unknown_no_retry','retry_exhausted','terminal_isolated'):continue
  if saved.get('status')=='queued_unrung' and time.time()<float(saved.get('next_retry_epoch',0)):continue
  attempts=int(saved.get('attempts',0))
  if attempts>=MAX_ATTEMPTS:continue
  result=trigger(row,state);attempts+=1;act=result.get('result') or {};ast=str(act.get('status') or '')
  if ast in ('fired','submitted','success','desktop_inserted'):status='pending_visual'
  elif ast in ('skipped_busy','skipped_user_draft','skipped_modal','blocked_task_title','blocked_window_identity','blocked_composer_count'):
   status='terminal_isolated' if attempts>=MAX_ATTEMPTS else 'queued_unrung'
  elif ast in ('delivery_unverified','paste_or_enter_failed'):status='delivery_unknown_no_retry'
  elif attempts>=MAX_ATTEMPTS:status='retry_exhausted'
  else:status='pending_delivery'
  record={'seq':row.get('seq'),'status':status,'attempts':attempts,'last_result':result,'updated_at':now_iso(),'database_ack_written':False}
  hold_fields={}
  if status in ('queued_unrung','terminal_isolated'):
   hold_fields={'preflight_blocks':int(saved.get('preflight_blocks',0))+1,'box_held':True,'return_to_sender_required':True,'return_reason':ast,'return_event_key':f'{rid}:attempt:{attempts}'}
   record.update(hold_fields)
   if status=='queued_unrung':record['next_retry_epoch']=time.time()+30
   else:record['terminal_reason']='attempt_limit_reached';hold_fields['terminal_reason']='attempt_limit_reached'
  handled[rid]=record
  # hold_fields (box_held/return_to_sender_required/return_reason/return_event_key/preflight_blocks/
  # terminal_reason) had zero readers anywhere in-repo (write-only since introduction) even though this
  # process's stdout is the file's documented completion gate ("visible proof remains the completion
  # gate") -- they were written to local state only, never to that gate. Folding them into the printed
  # line is the minimal fix that stays inside this file's own no-DB-ACK design; it does not perform an
  # actual cross-PC return-to-sender (that needs a new authorized send path -- open item, see
  # docs/incident_logs/2026-08-06_senmu_watcher_type4_return_to_sender_a2.md).
  log_line={'mode':'inbound','role':ROLE,'seq':row.get('seq'),'status':status,'actuator_status':ast,'database_ack_written':False}
  log_line.update(hold_fields)
  print(json.dumps(log_line,ensure_ascii=False),flush=True)
  break
def outbound_once(state):
 floor=int(state.get('outbound_floor',MIN_SEQ));rows=fetch({'select':'id,seq,message_type,from_pc,to_pc,topic,parent_message_id,created_at','from_pc':f'eq.{ROLE}','seq':f'gt.{floor}','order':'seq.asc','limit':'50'})
 receipts=state.setdefault('outbound_receipts',{})
 for row in rows:
  rid=str(row.get('id') or '')
  if not rid:continue
  receipts[rid]={'seq':row.get('seq'),'to_pc':row.get('to_pc'),'parent_message_id':row.get('parent_message_id'),'observed_at':now_iso()}
  floor=max(floor,int(row.get('seq') or 0))
  print(json.dumps({'mode':'outbound','role':ROLE,'seq':row.get('seq'),'to_pc':row.get('to_pc'),'status':'observed_upstream'},ensure_ascii=False),flush=True)
 state['outbound_floor']=floor

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('inbound','outbound'),required=True);ap.add_argument('--interval',type=int,default=5);ap.add_argument('--once',action='store_true');a=ap.parse_args()
 STATE_ROOT.mkdir(parents=True,exist_ok=True);path=STATE_ROOT/(a.mode+'.json');state=load(path);state.setdefault('role',ROLE);state.setdefault('completion_gate','visual_only_then_database')
 while True:
  try:
   (inbound_once if a.mode=='inbound' else outbound_once)(state);state['last_poll_status']='ok';state.pop('last_error',None)
  except Exception as e:
   state['last_poll_status']='error';state['last_error']=f'{type(e).__name__}:{str(e)[:240]}';print(json.dumps({'mode':a.mode,'role':ROLE,'status':'error','error':state['last_error']},ensure_ascii=False),flush=True)
  state['last_poll_at']=now_iso();atomic_json(path,state)
  if a.once:return 0
  time.sleep(max(5,a.interval))
if __name__=='__main__':raise SystemExit(main())
