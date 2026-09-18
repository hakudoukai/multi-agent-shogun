# -*- coding: utf-8 -*-
"""★新基底は一本では走らぬ ―― 兄弟器を伴はねば濡れ衣を着る★
driver/70 の第一走で判つた事: origin/main の門は L154 で `$(dirname "$0")/karo_mac_fukashiji.py` を呼ぶ。
束へ門一本だけ置いて走らせると兄弟器が隣に居らず、★條②④が「測れぬ」で rc=1★ ―― 之は門の疵ではなく ★當席の据ゑ方の疵★。
∴ origin/main から ★兄弟器ごと★ 束内 _fx/shin_kitei/ へ引き、同じ住処から走らせ直す。
併せて ★共用樹 disk には karo_mac_fukashiji.py が無い★(HEAD にも無い)事を数で残す ―― main の門は此の樹では其の儘走らぬ。
四札: 刻=冠 / 根=cwd / rc=returncode(★管を通さず★) / 陽性対照=閾1(両基底)+兄弟器を除いた走り。"""
import os
import sys
import shutil
import hashlib
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); hz = import_module("05_hashiraseru")
kaku, kaku_tsv, mieru = kaki_m.kaku, kaki_m.kaku_tsv, hz.mieru

REF = "origin/main"
KYUU = "scripts/checks/karo_mac_dasumae_gate.sh"
SUMIKA = os.path.join(BUNDLE, "_fx", "shin_kitei")
if os.path.isdir(SUMIKA):
    shutil.rmtree(SUMIKA)
os.makedirs(SUMIKA)

def g(args):
    p = subprocess.run(["git"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout, p.stderr.decode("utf-8", "replace").strip(), p.returncode

def sha(b):
    return hashlib.sha256(b).hexdigest()

# ―― main の checks を一覧し、門が名指す兄弟器を引く ――
names, _e, rc_ls = g(["ls-tree", "--name-only", REF, "scripts/checks/"])
main_files = [n for n in names.decode().split("\n") if n.strip()]
gate_src = open(os.path.join(BUNDLE, "base_gate.sh"), encoding="utf-8").read()
kyoudai = sorted({n.split("/")[-1] for n in main_files
                  if n.split("/")[-1] in gate_src and n.split("/")[-1].endswith((".py", ".sh"))})

hikae = []
for nm in kyoudai:
    body, e, rc = g(["show", "%s:scripts/checks/%s" % (REF, nm)])
    assert rc == 0 and body, "兄弟器が引けぬ: %s rc=%d %s" % (nm, rc, e)
    with open(os.path.join(SUMIKA, nm), "wb") as fh:
        fh.write(body)
    ondisk = os.path.join("scripts/checks", nm)
    d_exists = os.path.exists(ondisk)
    _h, _e2, rc_head = g(["rev-parse", "HEAD:scripts/checks/%s" % nm])
    hikae.append([nm, len(body), sha(body)[:16],
                  ("在り" if d_exists else "★共用樹 disk に無し★"),
                  ("在り" if rc_head == 0 else "★HEAD に無し★"),
                  ("門が名指す" if nm in gate_src else "-")])
kaku_tsv(os.path.join(BUNDLE, "raw", "75_kyoudai_ki.tsv"), hikae,
         header=["兄弟器(main より)", "byte", "sha256(頭16)", "共用樹 disk", "本枝 HEAD", "門との関はり"])

FX = os.path.join(BUNDLE, "_fx", "kiyoi.txt")
T = os.path.getsize(FX)
SHIN = os.path.join(SUMIKA, "karo_mac_dasumae_gate.sh")

def hashiru(gate, val, tmo=120):
    e = dict(os.environ)
    if val is None:
        e.pop("DASUMAE_MAX_BYTES", None)
    else:
        e["DASUMAE_MAX_BYTES"] = val
    p = subprocess.run(["bash", gate, "--", FX], env=e,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=tmo)
    err = p.stderr.decode("utf-8", "replace")
    lines = [l for l in err.split("\n") if l.strip()]
    return {"rc": p.returncode, "err": err,
            "shikii": " / ".join(l for l in lines if "閾 DASUMAE_MAX_BYTES" in l) or "-",
            "jou5": " / ".join(l for l in lines if "條⑤" in l) or "-",
            "jou24": " / ".join(l for l in lines if "條②" in l or "條④" in l) or "-",
            "ketsu": " / ".join(l for l in lines if "出す前 門" in l) or "-"}

KEI = [
    ("正 数(既定と同じ)", "10485760"),
    ("正 数(小・★陽性対照★)", "1"),
    ("形0 未設定", None),
    ("形1 非数", "abc"),
    ("形2 空文字", ""),
    ("形3 空白のみ(半角)", "   "),
    ("形3' 空白のみ(全角U+3000)", "　"),
    ("形4 2^63-1(比較器の上限内)", "9223372036854775807"),
    ("形4' 2^63(比較器が倒れる)", "9223372036854775808"),
    ("形4'' 2^64以上", "99999999999999999999"),
    ("参考 010(八進に非ず十進)", "010"),
]

def nazeka(r):
    """rc を條へ割る ―― ★rc だけでは何が鳴つたか言へぬ★(第40弾の法)。"""
    if r["rc"] == 2:
        return "閾が使へぬ(fix_threshold が止めた)"
    if r["rc"] == 0:
        return "鳴らず"
    if "測れぬ" in r["jou24"]:
        return "★條②④ 測れぬ(兄弟器の不在等)★"
    if "條⑤" in r["jou5"] and ("以上" in r["jou5"] or "超" in r["jou5"]):
        return "條⑤ 寸法"
    return "其の他(逐語を見よ)"

rows, kawatta, fudou = [], 0, 0
chiku = []
for na, val in KEI:
    k = hashiru(KYUU, val)
    s = hashiru(SHIN, val)
    han = "★変つた★" if k["rc"] != s["rc"] else "不動"
    kawatta += 1 if k["rc"] != s["rc"] else 0
    fudou += 0 if k["rc"] != s["rc"] else 1
    rows.append([na, mieru(val), k["rc"], nazeka(k), s["rc"], nazeka(s), han,
                 (s["shikii"] if s["shikii"] != "-" else s["jou5"])[:70]])
    chiku.append("### %s  与へた値=%s\n[旧基底 stderr 逐語]\n%s\nrc: %d\n[新基底(兄弟器同居) stderr 逐語]\n%s\nrc: %d"
                 % (na, mieru(val), k["err"].rstrip("\n") or "(空)", k["rc"],
                    s["err"].rstrip("\n") or "(空)", s["rc"]))
kaku_tsv(os.path.join(BUNDLE, "raw", "76_futatsu_no_kitei_naoshi.tsv"), rows,
         header=["形", "与へた値", "旧基底 rc", "旧は何が鳴つたか", "新基底 rc", "新は何が鳴つたか", "判",
                 "新基底が刷る行(70字で截つ)"])

# ―― 境目三点(新は兄弟器同居) ――
saka = []
for na, shikii in [("和=閾-1", T + 1), ("和=閾", T), ("和=閾+1", T - 1)]:
    k = hashiru(KYUU, str(shikii))
    s = hashiru(SHIN, str(shikii))
    kg = "以上" if "以上" in k["jou5"] else ("超" if "超" in k["jou5"] else ("未満" if "未満" in k["jou5"] else "-"))
    sg = "以上" if "以上" in s["jou5"] else ("超" if "超" in s["jou5"] else ("未満" if "未満" in s["jou5"] else "-"))
    saka.append([na, T, shikii, ("和>閾" if T > shikii else ("和=閾" if T == shikii else "和<閾")),
                 kg, k["rc"], sg, s["rc"],
                 ("★旧=語がずれ / 新=合ふ★" if (T == shikii and kg == "超" and sg == "以上") else "語と實は合ふ")])
kaku_tsv(os.path.join(BUNDLE, "raw", "77_sakaime_naoshi.tsv"), saka,
         header=["点", "byte和", "閾", "實の関係", "旧が刷る語", "旧 rc", "新が刷る語", "新 rc", "名と實"])

# ―― ★陽性対照★ 兄弟器を隣から退けたら新基底は「測れぬ」で落ちる(driver/70 第一走の再現) ――
NOKETA = os.path.join(BUNDLE, "_fx", "shin_kitei_kyoudai_nashi")
if os.path.isdir(NOKETA):
    shutil.rmtree(NOKETA)
os.makedirs(NOKETA)
shutil.copyfile(SHIN, os.path.join(NOKETA, "karo_mac_dasumae_gate.sh"))
n = hashiru(os.path.join(NOKETA, "karo_mac_dasumae_gate.sh"), "10485760")
y = hashiru(SHIN, "10485760")
kaku_tsv(os.path.join(BUNDLE, "raw", "78_kyoudai_no_umu.tsv"),
         [["兄弟器 同居(正)", y["rc"], nazeka(y), y["jou24"][:60]],
          ["★兄弟器 無し(陽性対照)★", n["rc"], nazeka(n), n["jou24"][:60]]],
         header=["据ゑ方", "rc", "何が鳴つたか", "條②④の行(60字で截つ)"])

kaku(os.path.join(BUNDLE, "raw", "80_naoshi_sengen.txt"),
     "as-of %s(UTC)\n根=%s\n"
     "旧基底=%s sha256 %s(★未commit の三つ目の版・触れず読むのみ★)\n"
     "新基底=_fx/shin_kitei/karo_mac_dasumae_gate.sh sha256 %s(%s より)\n"
     "兄弟器=%s(門が名指す物のみ引いた ―― 引いた数 %d)\n"
     "byte和 T=%d / 形 %d / 境目 %d 点\n"
     "rc の動き(形): 変つた %d / 不動 %d(合 %d = 母數)\n"
     "★driver/70 の第一走は新基底を門一本で走らせた ―― 兄弟器が隣に居らず條②④が『測れぬ』で rc=1 と成つた。\n"
     "  之は門の疵に非ず ★當席の据ゑ方の疵★ である。raw/70・71 は其の儘残し(捨てず)、本器 raw/76・77 が正しい対照である。★\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT,
        KYUU, sha(open(KYUU, "rb").read()), sha(open(SHIN, "rb").read()), REF,
        ",".join(kyoudai), len(kyoudai), T, len(KEI), len(saka), kawatta, fudou, kawatta + fudou))
kaku(os.path.join(BUNDLE, "raw", "81_naoshi_chikugo.txt"),
     "as-of %s(UTC)\n根=%s\n\n%s" % (
         datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT,
         "\n\n".join(chiku)))
print("兄弟器=%s / 形=%d 変つた=%d 不動=%d" % (",".join(kyoudai), len(KEI), kawatta, fudou))
