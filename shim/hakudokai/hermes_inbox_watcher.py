#!/usr/bin/env python3
"""Safe Hermes advisor inbox watcher: unread YAML -> exact Hermes pane nudge.
No C-c, restart, clear, escalation, or message-body injection.
"""
import argparse, datetime as dt, fcntl, json, os, pathlib, subprocess, tempfile, time
import yaml
ROOT=pathlib.Path('/home/hakudoukai/multi-agent-shogun');INBOX=ROOT/'queue/inbox/hermes.yaml';LOCK=pathlib.Path(str(INBOX)+'.lock');HEALTH=pathlib.Path.home()/'.local/state/dentalbi/hermes_inbox_watcher_health.json'
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def atomic_health(d):
 HEALTH.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=HEALTH.name+'.',dir=HEALTH.parent,text=True)
 try:
  with os.fdopen(fd,'w') as f:json.dump(d,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
  os.chmod(tmp,0o600);os.replace(tmp,HEALTH)
 finally:
  try:os.unlink(tmp)
  except FileNotFoundError:pass
# 2026-08-09 委員長: ★許可列挙をやめ除外列挙へ反転★。
# 由来: 艦隊の pane_current_command 実測 = doppler 11 / python3 3 / python 1。
#   同じHermes役職でも3つの値を返す(gunshi-third=doppler / 部長3体=python3 / 相談役=python)。
#   ∴ 許可を列挙する限り、新しい起動形が増えるたびに★無言で全断★する(31時間53便の実害)。
# ★守りの門は default-deny が正。配送の門は default-deliver が正★ ――
#   落とすことが害である以上、判別不能なら届ける。除外するのは「TUIが死んで shell に落ちた」状態だけ。
IDLE_SHELLS = ('bash', 'sh', 'zsh', 'fish', 'dash')


def pane():
 out=subprocess.check_output(['tmux','list-panes','-a','-F','#{session_name}:#{window_index}.#{pane_index}|#{pane_id}|#{pane_pid}|#{pane_current_command}|#{pane_dead}|#{@agent_id}'],text=True)
 hits=[x for x in out.splitlines() if x.endswith('|hermes-third')]
 if len(hits)!=1:return None
 a=hits[0].split('|');
 if a[0]!='hermes-sodanyaku:0.0' or a[3] in IDLE_SHELLS or a[4]!='0':return None
 return a[0],a[1],int(a[2])
def unread():
 if not INBOX.exists():return []
 LOCK.touch(exist_ok=True)
 with LOCK.open('r+') as lf:
  fcntl.flock(lf,fcntl.LOCK_SH);d=yaml.safe_load(INBOX.read_text()) or {};return [m for m in d.get('messages',[]) if isinstance(m,dict) and not m.get('read',False)]
def ready(target):
 s=subprocess.check_output(['tmux','capture-pane','-p','-J','-t',target,'-S','-80'],text=True,errors='replace')
 tail='\n'.join(s.splitlines()[-15:])
 if not (any(x in tail for x in ('ready │','─ ready ','─ rea','rea…')) and '❯' in tail and 'Working' not in tail and 'running' not in tail.lower()):return False
 # ★入力欄に未送信の文字が在るなら打たない(委員長 2026-08-10)★
 #   ready だけで打つと前の催促の末尾へ追記され連結する(実測: hermes.yamlinbox14)
 for _ln in reversed(s.splitlines()):
  _st=_ln.strip()
  if _st.startswith(chr(10095)):
   _body=_st[1:].replace(chr(160),"").replace(chr(12288),"").strip()
   if _body=="":return True
   # ★2026-08-14 是正: 残っているのが★自分の nudge★なら掃除して先へ進む★
   #   旧実装は「文字が在る＝打たない」で止まり、★自分が入れた nudge で自分を永久に締め出していた★
   #   （相談役で実測: inbox20 が残り続け、20秒後も同一）。他人の入力・本文は従来どおり触らない。
   if _body.startswith("inbox") and "agent=" in _body and "queue/inbox/" in _body:
    for _k in ("C-u","C-a","C-k"):
     try:subprocess.run(["tmux","send-keys","-t",target,_k],check=False)
     except Exception:pass
     time.sleep(0.15)
    _s2=subprocess.check_output(["tmux","capture-pane","-p","-J","-t",target,"-S","-80"],text=True,errors="replace")
    for _l2 in reversed(_s2.splitlines()):
     _t2=_l2.strip()
     if _t2.startswith(chr(10095)):
      return _t2[1:].replace(chr(160),"").replace(chr(12288),"").strip()==""
    return True
   return False
 return True
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--interval',type=int,default=2);ap.add_argument('--cooldown',type=int,default=1800);ap.add_argument('--once',action='store_true');a=ap.parse_args();last_sig='';last_at=0.0
 while True:
  try:
   p=pane();u=unread();sig=','.join(str(x.get('_handshake_id') or x.get('id')) for x in u)
   sent=False
   if p and u and ready(p[0]) and (sig!=last_sig or time.time()-last_at>=a.cooldown):
    msg=f'inbox{len(u)} agent=hermes file=queue/inbox/hermes.yaml'
    subprocess.run(['tmux','send-keys','-t',p[0],'-l',msg],check=True)
    # Hermes TUI submit contract: Enter x3, then capture. Use C-j only if the exact payload remains.
    for _ in range(3):subprocess.run(['tmux','send-keys','-t',p[0],'Enter'],check=True)
    time.sleep(0.4)
    post=subprocess.check_output(['tmux','capture-pane','-p','-J','-t',p[0],'-S','-30'],text=True,errors='replace')
    if msg in '\n'.join(post.splitlines()[-8:]):
     subprocess.run(['tmux','send-keys','-t',p[0],'C-j'],check=True)
     time.sleep(0.2)
     post=subprocess.check_output(['tmux','capture-pane','-p','-J','-t',p[0],'-S','-30'],text=True,errors='replace')
     if msg in '\n'.join(post.splitlines()[-8:]):
      # ★2026-08-14 理事長ご指摘の是正: ★失敗した時こそ入力欄を掃除する★
      #   旧実装は掃除せずに raise しており、残骸が残る → 次ループで ready() が false →
      #   ★以後 永久に nudge が届かなくなる★（相談役で実際に発生。連絡が取れなくなる）
      for _k in ('C-u','C-a','C-k'):
       try: subprocess.run(['tmux','send-keys','-t',p[0],_k],check=False)
       except Exception: pass
       time.sleep(0.15)
      post2=subprocess.check_output(['tmux','capture-pane','-p','-J','-t',p[0],'-S','-30'],text=True,errors='replace')
      if msg in '\n'.join(post2.splitlines()[-8:]):
       raise RuntimeError('nudge_payload_remained_after_cleanup')
      # 掃除できた → 今回は諦めるが★残骸は残さない★（次のcooldown後に再送される）
    last_sig=sig;last_at=time.time();sent=True
   atomic_health({'status':'running','last_poll_at':now(),'pane':p[0] if p else None,'pane_id':p[1] if p else None,'pane_pid':p[2] if p else None,'unread':len(u),'last_nudge_at':now() if sent else None,'last_signature_count':len(sig.split(',')) if sig else 0})
  except Exception as e:atomic_health({'status':'error','at':now(),'error_type':type(e).__name__})
  if a.once:return
  time.sleep(a.interval)
if __name__=='__main__':main()
