# -*- coding: utf-8 -*-
"""★一話目の形を五話へ当てる ―― 形は sha 担保で紙から抜き、手で写さぬ★

條: ⑴源の紙の sha が合はねば ★止まる★(fail-closed) ⑵18 行を器で抜き、数が 18 でなければ止まる
    ⑶鍵の許容集合は ★型の源★ から引く(己で作らぬ) ⑷空の定義を宣する ―― 0 と False は ★空でない★
    ⑸製品樹へ一字も書かぬ(写しは本束へ) ⑹rc は ★管を通さぬ★
"""
import io, os, re, json, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
K = importlib.import_module("00_kaki")

ROOT="/Users/momizimac/multi-agent-shogun"
B=os.path.join(ROOT,"docs/evidence/ashigaru-mac-3_km-179-b2-nokori-wo-gowa-kiru-20260918")
RAW=os.path.join(B,"raw"); B2=os.path.join(B,"_b2")
FE="/Users/momizimac/DentalBI/frontend"
EPD=os.environ.get("KM179_EPD") or os.path.join(FE,"src/features/child-passport/story-engine/episodes")
SFX=os.environ.get("KM179_RAWSFX","")      # ★走り毎に出目の名を別にする★
NO_CLI=os.environ.get("KM179_NO_CLI")=="1" # 対照は己の器のみ撃つ事が在る

# ── 一 源の紙を sha で担保して 18 行を抜く ───────────────────────────
KAMI=os.path.join(ROOT,"docs/evidence/ashigaru-mac-3_km-175-b1-b3-hantei-teishutsu-to-b2-1wa-20260918/_b2/00_ukeire_kei_ichiwa.md")
SHA_MACHI="55900890f5964004b9632625d5e5f848cece4a163a29ee36b602e279ee5df213"
import hashlib
nama=io.open(KAMI,"rb").read()
sha=hashlib.sha256(nama).hexdigest()
print("源の紙 %s" % KAMI)
print("  sha256 待=%s" % SHA_MACHI)
print("  sha256 實=%s" % sha)
assert sha==SHA_MACHI, "★源の紙が動いて居る ―― 止まる(形を当てられぬ)★"
print("  ★一致 ∴ 形は此の紙の物である★")

hon=nama.decode("utf-8")
# 18 行の表 = 「| 項目 | 型 | 定義の在処」の見出しを持つ表の、見出しと罫を除いた行
gyou=hon.split("\n")
atama=None
for i,x in enumerate(gyou):
    if x.startswith("| 項目 | 型 | 定義の在処"):
        atama=i; break
assert atama is not None, "★表の頭が見つからぬ★"
hyou=[]
for x in gyou[atama+2:]:
    if not x.startswith("|"): break
    ran=[c.strip() for c in x.strip().strip("|").split("|")]
    assert len(ran)==4, "★欄が 4 でない: %r★" % x
    hyou.append(ran)
print("抜いた行 = %d 行" % len(hyou))
assert len(hyou)==18, "★18 行でない(%d) ―― 形が動いた★" % len(hyou)
K.kaku_tsv(os.path.join(RAW,"10_kei_18gyou%s.tsv"%SFX),
           [["項目","型","定義の在処","條"]]+hyou)

# ── 二 鍵の許容集合を型の源から引く ─────────────────────────────
VE=io.open(os.path.join(EPD,"validateEpisode.ts"),encoding="utf-8").read()
m=re.search(r"const META_STRING_KEYS = \[(.*?)\] as const", VE, re.S)
assert m, "★META_STRING_KEYS が引けぬ★"
META_STR=re.findall(r"'([^']+)'", m.group(1))
m2=re.search(r"const TOP_KEYS = \[(.*?)\] as const", VE)
assert m2, "★TOP_KEYS が引けぬ★"
TOP=re.findall(r"'([^']+)'", m2.group(1))
m3=re.search(r"const EPISODE_ID_RE = /(.*?)/", VE)
assert m3, "★EPISODE_ID_RE が引けぬ★"
IDRE=re.compile(m3.group(1))
META=META_STR+["visit"]
print("型の源より ―― TOP_KEYS=%s / META_KEYS=%d 個 / EPISODE_ID_RE=%s" % (TOP,len(META),m3.group(1)))

# ── 三 空の定義(宣する) ────────────────────────────────────────
def kara(v):
    """★空 = None / '' / [] / {} ―― 0 と False は 空でない★"""
    if v is None: return True
    if isinstance(v,(str,list,dict,tuple)) and len(v)==0: return True
    return False

WA=(os.environ["KM179_WA"].split(",") if os.environ.get("KM179_WA")
    else ["S3-EP2","S3-EP12","S4-EP1","S4-EP2","S4-EP3"])
print("標的 ―― EPD=%s / 話=%s / 出目の尾=%r" % (EPD, WA, SFX))

def mitsu(d, komoku):
    """18 行の項目名を受け、(出目, 言) を返す。出目= 埋 / 欠 / 空 / 測れぬ"""
    ep=d.get("episode"); sc=d.get("scenes")
    if komoku.startswith("episode.") and komoku!="episode.id":
        k=komoku.split(".",1)[1]
        if not isinstance(ep,dict) or k not in ep: return ("欠","episode に鍵 %s が無い"%k)
        return ("空" if kara(ep[k]) else "埋", repr(ep[k])[:40])
    if komoku=="episode.id":
        if not isinstance(ep,dict) or "id" not in ep: return ("欠","鍵無し")
        v=ep["id"]
        if kara(v): return ("空","")
        return ("埋" if IDRE.match(v) else "欠","%s (ID_RE %s)"%(v,"合"if IDRE.match(v) else "★不合★"))
    if komoku=="scenes[]":
        if not isinstance(sc,list): return ("欠","scenes が list でない")
        return ("空" if len(sc)==0 else "埋","場 %d"%len(sc))
    if komoku.startswith("scene."):
        michi=komoku[len("scene."):]
        kaku=0; kake=[]
        for i,s in enumerate(sc or []):
            if michi=="background":
                if "background" not in s: kake.append("場%d 鍵無"%i)
                elif kara(s["background"]): kake.append("場%d 空"%i)
                else: kaku+=1
            else:
                oya,ha=michi.split("[].")
                ko=s.get(oya)
                if not isinstance(ko,list): kake.append("場%d %s が list でない"%(i,oya)); continue
                for j,e in enumerate(ko):
                    if ha not in e: kake.append("場%d %s[%d] 鍵 %s 無"%(i,oya,j,ha))
                    elif kara(e[ha]): kake.append("場%d %s[%d] %s 空"%(i,oya,j,ha))
                    else: kaku+=1
        if kake: return ("欠","埋 %d / 欠 %d ―― 初= %s"%(kaku,len(kake),kake[0]))
        return ("埋","%d 箇所 悉く埋"%kaku)
    if komoku.startswith("(門)"):
        warui=[k for k in d.keys() if k not in TOP]
        warui+= ["episode.%s"%k for k in (ep or {}).keys() if k not in META]
        return ("埋","未知 key 0") if not warui else ("欠","未知 key %s"%warui)
    return ("測れぬ","項目名を解せぬ: %s"%komoku)

# ── 四 五話へ当てる ───────────────────────────────────────────
deme=[["話","項目","出目","言"]]
matome=[["話","md bytes","md sha256","json bytes","json sha256","18項目 埋","欠","空","CLI rc","CLI 出目 字"]]
for w in WA:
    md_moto=os.path.join(EPD,"scripts",w+".md")
    js=os.path.join(EPD,w+".json")
    md_utsushi=os.path.join(B2,w+SFX+".md")   # ★走り毎に別名 ―― 対照が本走の写しを上書きせぬ★
    if os.path.exists(md_moto):
        shutil.copyfile(md_moto, md_utsushi)      # ★製品樹へは書かぬ・本束へ写す★
    mdb=io.open(md_moto,"rb").read(); jsb=io.open(js,"rb").read()
    d=json.loads(jsb.decode("utf-8"))
    kazu={"埋":0,"欠":0,"空":0,"測れぬ":0}
    for ran in hyou:
        st,koto=mitsu(d, ran[0])
        kazu[st]=kazu.get(st,0)+1
        deme.append([w,ran[0],st,koto])
    if NO_CLI:
        rc=-1; de=""                               # ★-1 は「撃つて居らぬ」 ―― 緑でも赤でもない★
    else:
        p=subprocess.run(["npm","run","--silent","validate:episode-md","--",md_utsushi],
                         cwd=FE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc=p.returncode                            # ★管を通さぬ★
        de=p.stdout.decode("utf-8","replace")
        K.kaku(os.path.join(RAW,"11_cli_%s%s.txt"%(w,SFX)), "rc=%d\n--- out+err ---\n%s"%(rc,de.rstrip("\n")))
    matome.append([w,str(len(mdb)),hashlib.sha256(mdb).hexdigest(),str(len(jsb)),hashlib.sha256(jsb).hexdigest(),
                   str(kazu["埋"]),str(kazu["欠"]),str(kazu["空"]),str(rc),str(len(de))])
    print("%s ―― 埋 %d / 欠 %d / 空 %d / CLI rc=%d" % (w,kazu["埋"],kazu["欠"],kazu["空"],rc))

K.kaku_tsv(os.path.join(RAW,"12_toi1_ran%s.tsv"%SFX), deme)
K.kaku_tsv(os.path.join(RAW,"13_toi1_matome%s.tsv"%SFX), matome)
print("★問ひ① 置いた ―― raw/12_toi1_ran.tsv(%d 行) / raw/13_toi1_matome.tsv★" % (len(deme)-1))
