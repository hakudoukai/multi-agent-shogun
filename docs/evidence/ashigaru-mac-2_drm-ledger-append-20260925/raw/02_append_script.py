# -*- coding: utf-8 -*-
import json, hashlib, subprocess, sys, os
LED='/Users/momizimac/akahon-r8/.evidence-370771/remaining24-image-handoff.json'
WT='/Users/momizimac/wt/a2-akahon-rem24'
C1='2e9fdd25c1cbe358533a74b8c181302b7d89f69d'; B1='docs/evidence/ashigaru-mac-2_akahon-r8-rem24-20260925'
C2='19030846e9759d12dece62631b0f0aceee1220e6'; B2='docs/evidence/ashigaru-mac-2_akahon-r8-rereading3-20260925'
EXP='99e0c1963215361631be980ac7fe6d4b52dd96194d6ad54052067d3b37300a95'
KEY='mac2_visual_reading'
raw=open(LED,'rb').read()
if hashlib.sha256(raw).hexdigest()!=EXP: sys.exit('input sha mismatch')
d=json.loads(raw)
def dump(o): return (json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()
for ea in (False,True):
  for tail in ('','\n'):
    if (json.dumps(d,ensure_ascii=ea,indent=2)+tail).encode()==raw: print('roundtrip ensure_ascii=%s tail=%r'%(ea,tail)); FMT=(ea,tail)
if 'FMT' not in dir(): sys.exit('roundtrip failed: format unknown')
def show(c,p): return subprocess.run(['git','-C',WT,'show','%s:%s'%(c,p)],capture_output=True,check=True).stdout
readme2=show(C2,B2+'/README.md').decode()
for r in d:
  if KEY in r: sys.exit('already has key: page %s'%r['page'])
  pg='%s/pages/p%04d.md'%(B1,r['page']); b=show(C1,pg)
  e={'reader':'ashigaru-mac-2 (Claude Code, PNG 目視)','source_commit':C1,'source_path':pg,
     'source_sha256':hashlib.sha256(b).hexdigest(),'image_sha256_checked':r['image_sha256'],
     'reading_md':b.decode(),'note':'候補(AI/OCR)は不変・採否は Dr-M。visual_decision は未裁定の儘。'}
  if r['page'] in (440,450,493):
    e['rereading']={'commit':C2,'readme':B2+'/README.md',
      'readme_sha256':'1859d821f6acd26b4d24ccc993c33df3f84991fce72341fe981b149d1c5e67b3',
      'result':'歯式の横線 26箇所を再読・初読との差0・初読の「確信を持てぬ」三件を確定(詳細は readme)'}
  r[KEY]=e
out=(json.dumps(d,ensure_ascii=FMT[0],indent=2)+FMT[1]).encode()
if '--write' in sys.argv:
  tmp=LED+'.a2tmp'; open(tmp,'wb').write(out); os.replace(tmp,LED)
print('rows',len(d),'out_sha',hashlib.sha256(out).hexdigest(),'bytes',len(out),'lines',out.count(b'\n'))
