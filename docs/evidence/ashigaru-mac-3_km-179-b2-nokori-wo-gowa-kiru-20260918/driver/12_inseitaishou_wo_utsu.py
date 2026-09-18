# -*- coding: utf-8 -*-
"""★陰性対照 ―― 故意に崩した一話を通し、式が赤で鳴る事を示す★

條: ⑴製品樹へ一字も書かぬ ―― 崩すのは ★本束の内に取つた写しの樹★ である
    ⑵対照は走る毎に ★別名★(門控の名が衝つと出目が混ざる ∴ 走りの札 HASHIRI を名に焼く)
    ⑶崩した事を ★byte で確かめる★(写しと原が同一なら崩れて居らぬ ∴ 止まる)
    ⑷鳴りの判は「rc」ではなく ★崩した箇所を器が名指したか★ ―― 己の器は数へる器ゆゑ
       (上の器=CLI は rc で判ずる。之は rc≠0 を要求する)
    ⑸鳴らねば ★緑と書かず「鳴らず ―― 器を疑へ」と書く★
    ⑹rc は ★管を通さぬ★
"""
import io, os, re, json, shutil, subprocess, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
K = importlib.import_module("00_kaki")

ROOT="/Users/momizimac/multi-agent-shogun"
B=os.path.join(ROOT,"docs/evidence/ashigaru-mac-3_km-179-b2-nokori-wo-gowa-kiru-20260918")
RAW=os.path.join(B,"raw"); B2=os.path.join(B,"_b2"); DRV=os.path.join(B,"driver")
FE="/Users/momizimac/DentalBI/frontend"
EPD_MOTO=os.path.join(FE,"src/features/child-passport/story-engine/episodes")
WA="S3-EP2"                      # 崩す一話(五話の内の一)
HASHIRI=os.environ.get("KM179_HASHIRI","h1")   # ★走りの札★

def utsushi(na):
    """EPD の写しを本束へ取り、path を返す。★原は一字も触らぬ★"""
    saki=os.path.join(B2,"taishou_%s_%s"%(HASHIRI,na))
    if os.path.isdir(saki): shutil.rmtree(saki)
    os.makedirs(os.path.join(saki,"scripts"))
    for f in sorted(os.listdir(EPD_MOTO)):
        if f.endswith(".json") or f=="validateEpisode.ts":
            shutil.copyfile(os.path.join(EPD_MOTO,f), os.path.join(saki,f))
    for f in sorted(os.listdir(os.path.join(EPD_MOTO,"scripts"))):
        if f.endswith(".md"):
            shutil.copyfile(os.path.join(EPD_MOTO,"scripts",f), os.path.join(saki,"scripts",f))
    return saki

def kowasu_json(saki, te):
    """写しの json を崩す。★原と byte が違ふ事を確かめる★"""
    p=os.path.join(saki,WA+".json")
    mae=io.open(p,"rb").read()
    d=json.loads(mae.decode("utf-8")); te(d)
    ato=json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8")+b"\n"
    io.open(p,"wb").write(ato)
    gen=io.open(os.path.join(EPD_MOTO,WA+".json"),"rb").read()
    assert ato!=gen, "★崩れて居らぬ(写しと原が同一) ―― 止まる★"
    return len(gen), len(ato), hashlib.sha256(gen).hexdigest(), hashlib.sha256(ato).hexdigest()

def hashiru(kiki, kankyou):
    """器を子で撃つ。★rc は管を通さぬ★"""
    kan=dict(os.environ); kan.update(kankyou); kan["PYTHONDONTWRITEBYTECODE"]="1"
    p=subprocess.run([sys.executable,"-B",os.path.join(DRV,kiki)],
                     cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=kan)
    return p.returncode, p.stdout.decode("utf-8","replace")

def yomu(na):
    with io.open(os.path.join(RAW,na),encoding="utf-8") as f:
        return [x.split("\t") for x in f.read().split("\n") if x!=""]

deme=[["対照","崩した所","器","期する鳴り","rc","鳴つたか","器が名指した逐語"]]
shizuka=[]

# ── 対照甲 ―― 未知 key(封の頂 と episode の中) → 問ひ①の(門) ──────────
saki=utsushi("kou")
def te_kou(d):
    d["shiranu_top"]=1                     # 頂の未知 key(TOP_KEYS の外)
    d["episode"]["shiranu_meta"]=1         # meta の未知 key(META_KEYS の外)
b_gen,b_ato,s_gen,s_ato=kowasu_json(saki,te_kou)
SFX="_%s_kou"%HASHIRI
rc,de=hashiru("10_kei_wo_ateru.py",{"KM179_EPD":saki,"KM179_WA":WA,"KM179_NO_CLI":"1","KM179_RAWSFX":SFX})
K.kaku(os.path.join(RAW,"30_taishou_kou%s.txt"%SFX),
       "★対照甲 未知 key★\n崩した写し= %s\n原 %d B sha %s\n写 %d B sha %s\ndriver/10 rc=%d\n--- out+err ---\n%s"
       % (os.path.relpath(saki,B), b_gen,s_gen, b_ato,s_ato, rc, de.rstrip("\n")))
nari="";
for r in yomu("12_toi1_ran%s.tsv"%SFX):
    if r[0]==WA and r[1].startswith("(門)") and r[2]=="欠": nari=r[3]
deme.append(["甲","封の頂に shiranu_top / episode に shiranu_meta","driver/10 問ひ①(門)",
             "(門)の欄が『欠』に成り 未知 key を名指す", str(rc),
             "★鳴つた★" if nari else "★鳴らず ―― 器を疑へ★", nari or "KARA"])
if not nari: shizuka.append("甲")

# ── 対照乙 ―― ref を他話の id へ → 問ひ② ⑴⑶ ──────────────────
saki=utsushi("otsu")
def te_otsu(d): d["episode"]["parent_explanation_ref"]="S3-EP3"
b_gen,b_ato,s_gen,s_ato=kowasu_json(saki,te_otsu)
SFX="_%s_otsu"%HASHIRI
rc,de=hashiru("11_toi2_to_toi3kou.py",{"KM179_EPD":saki,"KM179_WA":WA,"KM179_NO_UE":"1","KM179_RAWSFX":SFX})
K.kaku(os.path.join(RAW,"31_taishou_otsu%s.txt"%SFX),
       "★対照乙 ref を他話へ★\n崩した写し= %s\n原 %d B sha %s\n写 %d B sha %s\ndriver/11 rc=%d\n--- out+err ---\n%s"
       % (os.path.relpath(saki,B), b_gen,s_gen, b_ato,s_ato, rc, de.rstrip("\n")))
nari=""
for r in yomu("20_toi2_1to1_%s_otsu.tsv"%HASHIRI):
    if r[0]==WA and r[-1]=="否": nari="ref=%s ⑴%s ⑶%s 判=%s"%(r[1],r[2],r[4],r[5])
deme.append(["乙","episode.parent_explanation_ref = S3-EP3(他話の id)","driver/11 問ひ②",
             "⑴が× ∵自話と違ふ / ⑶が× ∵S3-EP3 と重なる / 判=否", str(rc),
             "★鳴つた★" if nari else "★鳴らず ―― 器を疑へ★", nari or "KARA"])
if not nari: shizuka.append("乙")

# ── 対照丙 ―― effects[].at を範外へ → 問ひ③-甲 ────────────────
saki=utsushi("hei")
def te_hei(d):
    ba=d["scenes"][0]
    ba.setdefault("effects",[{"type":"enter","at":0,"target":"hana"}])
    ba["effects"][0]["at"]=999
b_gen,b_ato,s_gen,s_ato=kowasu_json(saki,te_hei)
SFX="_%s_hei"%HASHIRI
rc,de=hashiru("11_toi2_to_toi3kou.py",{"KM179_EPD":saki,"KM179_WA":WA,"KM179_NO_UE":"1","KM179_RAWSFX":SFX})
K.kaku(os.path.join(RAW,"32_taishou_hei%s.txt"%SFX),
       "★対照丙 at を範外へ★\n崩した写し= %s\n原 %d B sha %s\n写 %d B sha %s\ndriver/11 rc=%d\n--- out+err ---\n%s"
       % (os.path.relpath(saki,B), b_gen,s_gen, b_ato,s_ato, rc, de.rstrip("\n")))
nari=""
for r in yomu("22_toi3kou_meisai_%s_hei.tsv"%HASHIRI):
    if r[0]==WA and r[1]=="at 範外": nari=r[2]
han=""
for r in yomu("21_toi3kou_kouzou_%s_hei.tsv"%HASHIRI):
    if r[0]==WA: han=r[-1]
deme.append(["丙","scenes[0].effects[0].at = 999","driver/11 問ひ③-甲",
             "at 範外 ≥1 / 明細が場と添字を名指す / 判=否", str(rc),
             "★鳴つた★" if (nari and han=="否") else "★鳴らず ―― 器を疑へ★",
             ("%s ／ 判=%s"%(nari,han)) if nari else "KARA(判=%s)"%han])
if not (nari and han=="否"): shizuka.append("丙")

# ── 対照丁 ―― md を崩して ★上の器(CLI)★ を鳴らす ──────────────
saki=utsushi("tei")
mdp=os.path.join(saki,"scripts",WA+".md")
mae=io.open(mdp,encoding="utf-8").read()
m=re.search(r"^@effect (\w+) at=(\d+)( .*)?$", mae, re.M)
assert m, "★md に @effect の行が無い ―― 崩し方を変へねばならぬ★"
kizu=m.group(0); atarashii=kizu.replace("at=%s"%m.group(2), "at=999", 1)
n=mae.count(kizu); assert n>=1, "★逐語が当たらぬ★"
io.open(mdp,"w",encoding="utf-8").write(mae.replace(kizu,atarashii,1))
gen=io.open(os.path.join(EPD_MOTO,"scripts",WA+".md"),"rb").read()
ato=io.open(mdp,"rb").read(); assert ato!=gen, "★崩れて居らぬ★"
SFX="_%s_tei"%HASHIRI
rc,de=hashiru("10_kei_wo_ateru.py",{"KM179_EPD":saki,"KM179_WA":WA,"KM179_RAWSFX":SFX})
cli=os.path.join(RAW,"11_cli_%s%s.txt"%(WA,SFX))
clihon=io.open(cli,encoding="utf-8").read() if os.path.exists(cli) else "KARA"
m2=re.match(r"rc=(-?\d+)", clihon); clirc=int(m2.group(1)) if m2 else 999
K.kaku(os.path.join(RAW,"33_taishou_tei%s.txt"%SFX),
       "★対照丁 md の @effect at を範外へ(上の器=CLI を撃つ)★\n崩した写し= %s\n"
       "崩した逐語 前= %r\n崩した逐語 後= %r\n原 md %d B / 写 md %d B\n"
       "driver/10 rc=%d ／ ★CLI rc=%d★\n--- driver out+err ---\n%s"
       % (os.path.relpath(saki,B), kizu, atarashii, len(gen), len(ato), rc, clirc, de.rstrip("\n")))
ii=[x for x in clihon.split("\n") if ("at" in x or "effect" in x or "rror" in x or "場" in x)][:3]
deme.append(["丁","scripts/%s.md の %r → at=999"%(WA,kizu),"★上の器★ npm run validate:episode-md",
             "CLI rc≠0(上の器は rc で判ずる)", str(clirc),
             "★鳴つた★" if clirc!=0 else "★鳴らず ―― 器を疑へ★",
             " / ".join(ii) if ii else "KARA"])
if clirc==0: shizuka.append("丁")

K.kaku_tsv(os.path.join(RAW,"39_taishou_matome_%s.tsv"%HASHIRI), deme)
print("★陰性対照 四つ 撃つた(走りの札 %s)★" % HASHIRI)
for r in deme[1:]: print("  %s ―― %s / rc=%s / %s" % (r[0],r[3][:28],r[4],r[5]))
if shizuka:
    print("★黙つた対照 = %s ―― 其の式は測つて居らぬ。緑と書かぬ★" % shizuka); sys.exit(3)
print("★四つ悉く鳴つた ∴ 式は測つて居る★")
