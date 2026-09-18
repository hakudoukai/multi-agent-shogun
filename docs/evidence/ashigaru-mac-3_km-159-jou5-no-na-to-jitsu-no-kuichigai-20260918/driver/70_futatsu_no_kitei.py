# -*- coding: utf-8 -*-
"""★二つの基底を並べて測る★ ―― km-159 ㋐㋑ の出目は『旧基底(共用樹 disk)』に対する物であつた。
新基底(origin/main 04672e15…)で同じ十一形・境目三点を走らせ、★何が今も立ち、何が既に閉ぢたか★ を分ける。
器は ★argv から基底を取る★(焼き込まぬ) ―― 既定は 旧=共用樹 disk / 新=束内 base_gate.sh。
路に依る差を排す為、旧基底の ★写し★ を束へ置いて同じ場所から走らせる対照も取る。
四札: 刻=冠 / 根=cwd / rc=subprocess の returncode(★管を通さず★) / 陽性対照=閾1 の走り(各基底とも)。"""
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

KYUU = sys.argv[1] if len(sys.argv) > 1 else "scripts/checks/karo_mac_dasumae_gate.sh"
SHIN = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BUNDLE, "base_gate.sh")
UTSUSHI = os.path.join(BUNDLE, "_fx", "kyuu_kitei_no_utsushi.sh")   # 旧基底の写し(路の対照)
shutil.copyfile(KYUU, UTSUSHI)

FX = os.path.join(BUNDLE, "_fx", "kiyoi.txt")
with open(FX, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("清き紙 ―― 條②③④を満たす(末尾空白0・CR0・EOF改行丁度1)。\n")
T = os.path.getsize(FX)


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
    return {
        "rc": p.returncode,
        "shikii": " / ".join(l for l in lines if "閾 DASUMAE_MAX_BYTES" in l) or "-",
        "jou5": " / ".join(l for l in lines if "條⑤" in l) or "-",
        "ketsu": " / ".join(l for l in lines if "出す前 門" in l) or "-",
        "err": err,
        "out": p.stdout.decode("utf-8", "replace"),
    }


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

rows, chiku, kawatta, fudou = [], [], 0, 0
for na, val in KEI:
    k = hashiru(KYUU, val)
    s = hashiru(SHIN, val)
    han = "★変つた★" if k["rc"] != s["rc"] else "不動"
    if k["rc"] != s["rc"]:
        kawatta += 1
    else:
        fudou += 1
    rows.append([na, mieru(val), k["rc"], ("鳴つた" if k["rc"] else "鳴らず"),
                 s["rc"], ("鳴つた" if s["rc"] else "鳴らず"), han,
                 (k["shikii"] if k["shikii"] != "-" else k["jou5"])[:58],
                 (s["shikii"] if s["shikii"] != "-" else s["jou5"])[:58]])
    chiku.append("### %s  与へた値=%s\n[旧基底 stderr 逐語]\n%s\nrc: %d\n[新基底 stderr 逐語]\n%s\nrc: %d"
                 % (na, mieru(val), k["err"].rstrip("\n") or "(空)", k["rc"],
                    s["err"].rstrip("\n") or "(空)", s["rc"]))

kaku_tsv(os.path.join(BUNDLE, "raw", "70_futatsu_no_kitei.tsv"), rows,
         header=["形", "与へた値", "旧基底 rc", "旧基底 門は", "新基底 rc", "新基底 門は", "判",
                 "旧基底が刷る行(58字で截つ)", "新基底が刷る行(58字で截つ)"])

# ―― ㋑ 境目の三点を二基底で ――
saka = []
for na, shikii in [("和=閾-1", T + 1), ("和=閾", T), ("和=閾+1", T - 1)]:
    k = hashiru(KYUU, str(shikii))
    s = hashiru(SHIN, str(shikii))
    kg = "超" if "超" in k["jou5"] and "超」に非ず" not in k["jou5"] else ("以上" if "以上" in k["jou5"] else ("未満" if "未満" in k["jou5"] else "-"))
    sg = "以上" if "以上" in s["jou5"] else ("超" if "超" in s["jou5"] else ("未満" if "未満" in s["jou5"] else "-"))
    saka.append([na, T, shikii, ("和>閾" if T > shikii else ("和=閾" if T == shikii else "和<閾")),
                 kg, k["rc"], sg, s["rc"],
                 ("★旧は語がずれ・新は合ふ★" if (T == shikii and kg == "超" and sg == "以上")
                  else ("語と實は合ふ" if kg in ("未満", sg) or sg == kg else "-"))])
kaku_tsv(os.path.join(BUNDLE, "raw", "71_sakaime_futatsu.tsv"), saka,
         header=["点", "byte和", "閾", "實の関係", "旧が刷る語", "旧 rc", "新が刷る語", "新 rc", "名と實"])

# ―― 路の対照(同じ旧基底を束から走らせても出目が動かぬ事) ――
tai = []
for na, val in [("形1 非数", "abc"), ("正 数(小)", "1")]:
    a = hashiru(KYUU, val)
    b = hashiru(UTSUSHI, val)
    tai.append([na, mieru(val), a["rc"], b["rc"], ("同じ" if (a["rc"], a["jou5"]) == (b["rc"], b["jou5"]) else "★異なる★"),
                "出目は門を置いた路に依らぬ" if (a["rc"], a["jou5"]) == (b["rc"], b["jou5"]) else "★路に依る★"])
kaku_tsv(os.path.join(BUNDLE, "raw", "72_michi_no_taishou.tsv"), tai,
         header=["形", "与へた値", "在処のまま rc", "束の写し rc", "判", "意"])

sh = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
kaku(os.path.join(BUNDLE, "raw", "73_futatsu_sengen.txt"),
     "as-of %s(UTC)\n根=%s\n"
     "旧基底=%s sha256 %s\n新基底=%s sha256 %s\n"
     "byte和 T=%d(_fx/kiyoi.txt 一本のみ ―― 和の母數は argv の file だけ)\n"
     "母數=形 %d / 境目 %d 点 / 路の対照 %d 形\n"
     "rc の動き: 変つた %d / 不動 %d(合 %d ―― 足して母數に成る)\n"
     "陽性対照=「正 数(小)」の走り ―― 両基底とも閾1 で條⑤が現に鳴る事を先に見せた\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT,
        KYUU, sh(KYUU), os.path.relpath(SHIN, ROOT), sh(SHIN), T,
        len(KEI), len(saka), len(tai), kawatta, fudou, kawatta + fudou))
kaku(os.path.join(BUNDLE, "raw", "74_futatsu_chikugo.txt"),
     "as-of %s(UTC)\n根=%s\n\n%s" % (
         datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT,
         "\n\n".join(chiku)))
print("形=%d 変つた=%d 不動=%d / 境目=%d / 路の対照=%d" % (len(KEI), kawatta, fudou, len(saka), len(tai)))
