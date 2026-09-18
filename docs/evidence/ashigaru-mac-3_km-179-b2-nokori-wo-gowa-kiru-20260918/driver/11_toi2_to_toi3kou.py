# -*- coding: utf-8 -*-
"""★問ひ② 1:1 の維持 / 問ひ③-甲 構造の到達 ―― 閾は型の源から引く(己で作らぬ)★"""
import io, os, re, json, subprocess, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
K = importlib.import_module("00_kaki")

ROOT="/Users/momizimac/multi-agent-shogun"
B=os.path.join(ROOT,"docs/evidence/ashigaru-mac-3_km-179-b2-nokori-wo-gowa-kiru-20260918")
RAW=os.path.join(B,"raw")
FE="/Users/momizimac/DentalBI/frontend"
SE=os.path.join(FE,"src/features/child-passport/story-engine")
EPD=os.environ.get("KM179_EPD") or os.path.join(SE,"episodes")
SFX=os.environ.get("KM179_RAWSFX","")
NO_UE=os.environ.get("KM179_NO_UE")=="1"   # 上の器(vitest)を撃たぬ走り
KAI=os.path.join(FE,"src/features/teriha-passport/story/parentExplanations.S3S4.ts")

WA=(os.environ["KM179_WA"].split(",") if os.environ.get("KM179_WA")
    else ["S3-EP2","S3-EP12","S4-EP1","S4-EP2","S4-EP3"])
print("標的 ―― EPD=%s / 話=%s / 出目の尾=%r" % (EPD, WA, SFX))

# ── 閾は ★型の源★ から引く ──────────────────────────────
T=io.open(os.path.join(SE,"types.ts"),encoding="utf-8").read()
m=re.search(r"export const MAX_CHOICE_LABEL_CHARS = (\d+)", T); assert m, "★閾 label が引けぬ★"
LABEL_MAX=int(m.group(1))
m=re.search(r"export const CHOICE_OPTION_COUNT = (\d+)", T); assert m, "★閾 択数 が引けぬ★"
TAKU=int(m.group(1))
print("型の源より ―― MAX_CHOICE_LABEL_CHARS=%d / CHOICE_OPTION_COUNT=%d" % (LABEL_MAX,TAKU))

# ── 解説の鍵(★出所を一つに★) ───────────────────────────
KAI_HON=io.open(KAI,encoding="utf-8").read()
KAGI=re.findall(r"^  '([^']+)': explanation\(", KAI_HON, re.M)
print("解説の鍵 = %d 個(出所 %s)" % (len(KAGI), os.path.relpath(KAI,FE)))

# ── 母數 = 現物の話 悉く(重なりは全體で見ねば測れぬ) ───────
ARUITA=sorted([f[:-5] for f in os.listdir(EPD) if f.endswith(".json")])
# ★宣して除く ―― 「除いた」は「歩いて居らぬ」ではない ∴ 両方の数を刷る★
NOZOKU=["TEMPLATE"]   # 雛形(id=S0-EP1)。話ではない。既存 test『TEMPLATE.json は そのままで valid』が守る物
ZEN=[w for w in ARUITA if w not in NOZOKU]
print("歩いた json = %d 本 ／ ★除いた(宣)= %s★ ／ 母數(現物の話)= %d 話" % (len(ARUITA), NOZOKU, len(ZEN)))
print("  ★除いた理由★: TEMPLATE.json の id は S0-EP1 で、解説の鍵 15 個に S0-EP1 は無い")
print("  ∴ 之を話に数へると ★未解決 1 件★ が立つが、其れは雛形であつて話の疵ではない")
ref_zen={}
for w in ZEN:
    d=json.load(io.open(os.path.join(EPD,w+".json"),encoding="utf-8"))
    ref_zen[w]=d["episode"].get("parent_explanation_ref")
kasanari={}
for w,r in ref_zen.items(): kasanari.setdefault(r,[]).append(w)

# ── 問ひ② ──────────────────────────────────────────────
t2=[["話","ref","⑴自話と等しいか","⑵解説の鍵に在るか","⑶他話と重ならぬか","判"]]
tsu2=0
for w in WA:
    r=ref_zen[w]
    a = (r==w)
    b = (r in KAGI)
    c = (len(kasanari.get(r,[]))==1)
    han = "通" if (a and b and c) else "否"
    if han=="通": tsu2+=1
    t2.append([w,str(r),"○" if a else "×","○" if b else "×",
               "○" if c else "×(%s)"%kasanari.get(r),han])
K.kaku_tsv(os.path.join(RAW,"20_toi2_1to1%s.tsv"%SFX),t2)
print("問ひ② ―― 通 %d / 五話" % tsu2)

# ── 問ひ③-甲 ────────────────────────────────────────────
t3=[["話","場の数","場 id の冠","場 id の重複","effects[].at 範外","choices 有る行","択数が%dでない"%TAKU,
     "label が%d字超"%LABEL_MAX,"最後の場の最後の行","判"]]
tsu3=0
meisai=[["話","何","詳"]]
for w in WA:
    d=json.load(io.open(os.path.join(EPD,w+".json"),encoding="utf-8"))
    epid=d["episode"]["id"]; sc=d["scenes"]
    kanmuri=[s["id"] for s in sc if not s["id"].startswith(epid+"-")]
    mita=set(); juu=[]
    for s in sc:
        if s["id"] in mita: juu.append(s["id"])
        mita.add(s["id"])
    hangai=[]; ch=0; takuchigai=[]; nagai=[]
    for i,s in enumerate(sc):
        n=len(s.get("lines",[]))
        for j,e in enumerate(s.get("effects",[])):
            at=e.get("at")
            if not isinstance(at,int) or at<0 or at>=n:
                hangai.append("場%d effects[%d] at=%r (lines %d)"%(i,j,at,n))
        for j,l in enumerate(s.get("lines",[])):
            if "choices" in l:
                ch+=1
                cs=l["choices"]
                if not isinstance(cs,list) or len(cs)!=TAKU:
                    takuchigai.append("場%d lines[%d] 択 %s"%(i,j,len(cs) if isinstance(cs,list) else type(cs).__name__))
                else:
                    for o in cs:
                        lb=o.get("label","")
                        if len(lb)>LABEL_MAX: nagai.append("場%d lines[%d] label %d字"%(i,j,len(lb)))
    saigo = bool(sc) and bool(sc[-1].get("lines"))
    ok = (not kanmuri) and (not juu) and (not hangai) and (not takuchigai) and (not nagai) and saigo
    if ok: tsu3+=1
    t3.append([w,str(len(sc)),
               "○" if not kanmuri else "×%s"%kanmuri,
               "○" if not juu else "×%s"%juu,
               "0" if not hangai else str(len(hangai)),
               str(ch),
               "0" if not takuchigai else str(len(takuchigai)),
               "0" if not nagai else str(len(nagai)),
               "○(%d 行)"%len(sc[-1]["lines"]) if saigo else "×",
               "通" if ok else "否"])
    for na,v in (("at 範外",hangai),("択数違",takuchigai),("label 超",nagai),("冠違",kanmuri),("id 重複",juu)):
        for x in v: meisai.append([w,na,x])
K.kaku_tsv(os.path.join(RAW,"21_toi3kou_kouzou%s.tsv"%SFX),t3)
K.kaku_tsv(os.path.join(RAW,"22_toi3kou_meisai%s.tsv"%SFX),meisai if len(meisai)>1 else [["話","何","詳"],["―","―","★赤 0 件(母數 5 話・全ての場・全ての行・全ての効果を歩いた)★"]])
print("問ひ③-甲 ―― 通 %d / 五話 ／ 明細の赤 %d 件" % (tsu3,len(meisai)-1))

# ── 上の器(製品樹の test) ―― ② の裏を取る ────────────────
if NO_UE:
    rc=-1; de=""                                  # ★-1 は「撃つて居らぬ」★
else:
    p=subprocess.run(["npx","vitest","run","src/features/child-passport/story-engine/episodes/__tests__/episodes.test.tsx"],
                     cwd=FE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    rc=p.returncode                               # ★管を通さぬ★
    de=p.stdout.decode("utf-8","replace")
K.kaku(os.path.join(RAW,"23_ue_no_ki_vitest%s.txt"%SFX), "rc=%d\n--- out+err ---\n%s"%(rc,de.rstrip("\n")))
m=re.search(r"Tests\s+(\d+) passed", de); tou=m.group(1) if m else "★引けぬ★"
sk=re.search(r"(\d+) skipped", de)
print("上の器(vitest) ―― rc=%d / 通 %s 本 / skip %s" % (rc, tou, sk.group(1) if sk else "0"))
K.kaku_tsv(os.path.join(RAW,"24_ue_no_ki_matome%s.tsv"%SFX),
           [["器","cwd","rc","通つた本数","skip","言"],
            ["npx vitest run …/episodes/__tests__/episodes.test.tsx",FE,str(rc),tou,
             sk.group(1) if sk else "0","★0 本で緑は緑に非ず ∴ 本数を書く★"]])
