# -*- coding: utf-8 -*-
"""50 ―― ㋒ の為の ★寫し器★ を作る。生器へは ★一字も★ 書かぬ。
作り方: 生器の行域を ★逐語★ で切り出し、前後に「冠」と「附録(駆動部)」を付ける。
    冠と附録は ★印で括る★ ゆゑ、後から寫し部だけを抜いて生器の切片と sha16 で突き合はせられる。
出目: utsushi/*.sh と nama/50_utsushi.tsv(寫しの證)。"""
import os, sys, hashlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kaki as K
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
BUNDLE = os.path.abspath(os.path.join(HERE, ".."))
UTS = os.path.join(BUNDLE, "utsushi")

HAJIME = u"# ===== 寫し ここから(生器 逐語・一字も違へず) ====="
OWARI  = u"# ===== 寫し ここまで ====="

def sha16b(b):
    return hashlib.sha256(b).hexdigest()[:16]

def sha16f(p):
    with open(p, "rb") as fh:
        return sha16b(fh.read())

def slice_lines(rel, spans):
    """spans = [(a,b), …] 1 起点・両端含む。逐語で継ぐ。"""
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read().split("\n")
    out = []
    for a, b in spans:
        out.extend(src[a - 1:b])
    return u"\n".join(out)

# ―― 寫し器の献立 ――
#   name, 生器, shell宣, 前置(逐語で要る helper の行域), 番人の行域, 閾名, 既定, 受け皿, 下流(行域), 附録
KONDATE = [
    dict(name="kou_health", kata=u"甲", rel="scripts/agent_health_check.sh",
         opt="set -uo pipefail", spans=[(85, 129)], hensuu="HEALTH_CHECK_COOLDOWN_SEC",
         kitei="300", uke="ALERT_COOLDOWN_SEC", karyuu=[(144, 146)], karyuu_gyo=u"144-146",
         pre=[u"__k(){ elapsed=0"], post=[u"  return 0", u"}", u"__k; __krc=$?"],
         eda=u'[ "${__krc}" = 1 ] && __kbranch="TAKEN(冷却中=報せを抑へる)" || __kbranch="NOTTAKEN(報せを出す)"',
         imi=u"elapsed(=0秒) を閾と比べ、冷却中なら報せを抑へる"),
    dict(name="otsu_gate4", kata=u"乙", rel="scripts/checks/karo_mac_gate4.sh",
         opt="set -u", spans=[(17, 17), (63, 107)], hensuu="GATE4_MAX_FILE_MB",
         kitei="50", uke="MAXF", karyuu=[(115, 115)], karyuu_gyo=u"115",
         pre=[u"big=0; mb=1; f=__nise_no_file__"], post=[],
         eda=u'[ "$big" = 1 ] && __kbranch="TAKEN(條⑤鳴る)" || __kbranch="NOTTAKEN(條⑤黙る)"',
         imi=u"1MB の file を閾(MB)と比べ、條⑤ を鳴らすか決める"),
    dict(name="otsu_dasumae", kata=u"乙", rel="scripts/checks/karo_mac_dasumae_gate.sh",
         opt="set -u", spans=[(22, 22), (36, 72), (92, 92)], hensuu="DASUMAE_MAX_BYTES",
         kitei="10485760", uke="MAXB", karyuu=[(254, 259)], karyuu_gyo=u"254-259",
         pre=[u"total=6; fail=0"], post=[],
         eda=u'[ "$fail" = 1 ] && __kbranch="TAKEN(條⑤鳴る)" || __kbranch="NOTTAKEN(條⑤黙る)"',
         imi=u"byte和 6 を閾(byte)と比べ、條⑤ を鳴らすか決める"),
    dict(name="otsu_hook", kata=u"乙", rel="scripts/stop_hook_inbox.sh",
         opt="set -euo pipefail", spans=[(52, 93)], hensuu="STOP_HOOK_STDIN_TIMEOUT",
         kitei="10", uke="STOP_HOOK_STDIN_TIMEOUT", karyuu=None, karyuu_gyo=u"78・90(寫しの内)",
         pre=[], post=[],
         eda=u'__kbranch="讀めた字数=${#INPUT}"',
         imi=u"read -r -d \'\' -t <閾> で stdin を待ち、経過秒を閾と比べる"),
]

os.makedirs(UTS, exist_ok=True)
t0 = time.time(); kiz = time.strftime("%Y-%m-%dT%H:%M:%S%z")
rows = []
for k in KONDATE:
    rel, name = k["rel"], k["name"]
    utsu = slice_lines(rel, k["spans"])
    L = []
    L.append(u"#!/bin/bash")
    L.append(u"# ★寫し器★ %s(型=%s) ―― 生器 %s の逐語切片。★生器へは一字も書いて居らぬ★" % (name, k["kata"], rel))
    L.append(u"#   生器 sha16=%s / 切り出した行域=%s / 作つた刻=%s"
             % (sha16f(os.path.join(ROOT, rel)), " ".join("%d-%d" % s for s in k["spans"]), kiz))
    L.append(u"#   生器と同じ shell 宣: %s" % k["opt"])
    L.append(k["opt"])
    L.append(HAJIME)
    L.append(utsu)
    L.append(OWARI)
    L.append(u"# ===== 附録(當席が書いた駆動部・寫しに非ず) =====")
    L.append(u'__uke="${%s-《受け皿が立たず》}"' % k["uke"])
    L.append(u"__kbranch=UNRUN")
    if k["karyuu"] is not None:
        L.append(u"# ↓ 下流 逐語(%s:%s) ―― %s ／ 前後の括りは當席の物、中は一字も違へず"
                 % (rel, k["karyuu_gyo"], k["imi"]))
        L.extend(k["pre"])
        L.append(u"# --- 下流 寫し ここから ---")
        L.append(slice_lines(rel, k["karyuu"]))
        L.append(u"# --- 下流 寫し ここまで ---")
        L.extend(k["post"])
    else:
        L.append(u"# 下流は寫しの内(%s:%s) ―― %s" % (rel, k["karyuu_gyo"], k["imi"]))
    L.append(k["eda"])
    L.append(u'__k3="${__read_rc-\u2015}"   # read の rc(在る器のみ)')
    L.append(u'printf "RESULT\\t%s\\t%s\\t%s\\n" "$__uke" "$__kbranch" "$__k3"')
    txt = u"\n".join(x for x in L if x != u"")
    p = os.path.join(UTS, name + ".sh")
    K.kaku(p, txt)
    os.chmod(p, 0o755)
    # 寫しの證 ―― 書いた file から寫し部だけを抜き直し、生器の切片と突き合はせる
    back = open(p, encoding="utf-8").read().split("\n")
    i, j = back.index(HAJIME), back.index(OWARI)
    nuki = u"\n".join(back[i + 1:j])
    rows.append([name, k["kata"], rel, " ".join("%d-%d" % s for s in k["spans"]),
                 sha16b(utsu.encode("utf-8")), sha16b(nuki.encode("utf-8")),
                 u"○同一" if nuki == utsu else u"×相違", os.path.getsize(p)])

K.kaku_tsv(os.path.join(BUNDLE, "nama", "50_utsushi.tsv"), rows,
           ["#寫し器", "型", "生器", "切り出した行域", "生器切片 sha16", "寫し部 sha16", "突合", "寫し器 byte"])
ng = [r for r in rows if r[6] != u"○同一"]
sys.stderr.write("50 done n=%d 相違=%d 経過=%.2fs\n" % (len(rows), len(ng), time.time() - t0))
sys.exit(5 if ng else 0)
