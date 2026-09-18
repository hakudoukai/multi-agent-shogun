# -*- coding: utf-8 -*-
"""★上の器(validateEpisode)を五話と対照甲へ当てる ―― 宣が甲に要求した rc≠0 を満たす為★

條: ⑴呼び出し器は本束(driver/13_ue_no_mon.ts)・製品樹は ★読み取りのみ★
    ⑵rc は ★管を通さぬ★ ⑶陽性(崩して居らぬ五話)と陰性(崩した写し)を ★同じ路★ で撃つ
    ⑷鳴らねば「鳴らず ―― 器を疑へ」と書く
"""
import io, os, subprocess, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
K = importlib.import_module("00_kaki")
ROOT="/Users/momizimac/multi-agent-shogun"
B=os.path.join(ROOT,"docs/evidence/ashigaru-mac-3_km-179-b2-nokori-wo-gowa-kiru-20260918")
RAW=os.path.join(B,"raw"); B2=os.path.join(B,"_b2"); DRV=os.path.join(B,"driver")
FE="/Users/momizimac/DentalBI/frontend"
EPD=os.path.join(FE,"src/features/child-passport/story-engine/episodes")
HASHIRI=os.environ.get("KM179_HASHIRI","h1")
WA=["S3-EP2","S3-EP12","S4-EP1","S4-EP2","S4-EP3"]
RUNNER=os.path.join(DRV,"13_ue_no_mon.ts")

def utsu(p):
    q=subprocess.run(["node","--import",os.path.join(DRV,"13_kaiketsushi_touroku.mjs"),RUNNER,p],
                     cwd=FE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return q.returncode, q.stdout.decode("utf-8","replace")   # ★管を通さぬ★

t=[["撃つた物","path","bytes","sha256","rc","valid","errors","逐語(初の三)"]]
warui=[]
# ── 陽性 ―― 崩して居らぬ五話 ────────────────────────────
for w in WA:
    p=os.path.join(EPD,w+".json"); nama=io.open(p,"rb").read()
    rc,de=utsu(p)
    ii=[x.strip() for x in de.split("\n") if x.startswith("  ・")][:3]
    t.append(["陽性 %s"%w,os.path.relpath(p,FE),str(len(nama)),hashlib.sha256(nama).hexdigest(),
              str(rc),"true" if rc==0 else "false",
              de.split("errors=")[1].split("\n")[0] if "errors=" in de else "★引けぬ★",
              " / ".join(ii) if ii else "KARA"])
    if rc!=0: warui.append("陽性 %s が rc=%d(崩して居らぬのに赤)"%(w,rc))
# ── 陰性 ―― 対照甲の崩した写し ──────────────────────────
kou=os.path.join(B2,"taishou_%s_kou"%HASHIRI,"S3-EP2.json")
assert os.path.exists(kou), "★対照甲の写しが無い ―― driver/12 を先に走らせよ★"
nama=io.open(kou,"rb").read()
rc,de=utsu(kou)
ii=[x.strip() for x in de.split("\n") if x.startswith("  ・")][:3]
t.append(["★陰性 対照甲(未知 key)★",os.path.relpath(kou,B),str(len(nama)),hashlib.sha256(nama).hexdigest(),
          str(rc),"true" if rc==0 else "false",
          de.split("errors=")[1].split("\n")[0] if "errors=" in de else "★引けぬ★",
          " / ".join(ii) if ii else "KARA"])
nari = (rc!=0) and ("未知の key" in de)
if not nari: warui.append("★対照甲が上の器で鳴らず(rc=%d) ―― 器を疑へ★"%rc)
K.kaku(os.path.join(RAW,"35_ue_no_mon_kou_%s.txt"%HASHIRI),
       "★上の器 validateEpisode を対照甲へ当てた★\npath= %s\nrc=%d\n--- out+err ---\n%s"
       % (os.path.relpath(kou,B), rc, de.rstrip("\n")))
K.kaku_tsv(os.path.join(RAW,"36_ue_no_mon_matome_%s.tsv"%HASHIRI), t)
for r in t[1:]: print("%s ―― rc=%s / errors=%s" % (r[0],r[4],r[6]))
print("★対照甲 上の器で %s★" % ("鳴つた(rc≠0 かつ『未知の key』を名指した)" if nari else "鳴らず ―― 器を疑へ"))
if warui:
    print("★不審 = %s★" % warui); sys.exit(4)
print("★陽性 5 悉く緑・陰性 1 赤 ∴ 上の器は測つて居る★")
