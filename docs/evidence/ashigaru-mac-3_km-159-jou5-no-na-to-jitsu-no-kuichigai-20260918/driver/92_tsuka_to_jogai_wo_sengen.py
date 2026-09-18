# -*- coding: utf-8 -*-
"""臺帳に載せる物と ★除く物★ を先に宣し、除く物が汚れて居るか否かを ★測つて★ から除く。
★「除いた」は「歩いて居らぬ」ではない★ ―― 束の全 file を歩き、載せる/除くの内訳と理由を表にする。
四札: 刻=冠 / 根=束(bundle 相対) / rc=returncode(管を通さず) / 陽性対照=_fx の汚し紙(門が鳴る筈)。"""
import os
import sys
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(BUNDLE)                       # ★根は束★(臺帳は束内相対・裁 seq322699)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv
GATE = os.path.join(ROOT, "scripts", "checks", "karo_mac_dasumae_gate.sh")

NOSERU = ("00_shodan.md", "driver", "raw", "_letters")
NOZOKU = {
    "_fx": "型紙(fixture) ―― ★故意に汚した紙・他席の門の写し★を含む。載せれば條②③④が鳴るのが正",
    "_gate": "門自身の出目 ―― ★臺帳が己を照らす★形に成る(裁 seq310228⑴ 自己言及の禁)",
    "base_gate.sh": "origin/main の門の ★byte 忠実の抜き取り★ ―― 當席が書いた紙に非ず(直せぬ)",
    "MANIFEST.txt": "臺帳其の物 ―― 己を己で照らせぬ",
}

def arukine(top):
    if os.path.isfile(top):
        yield top
        return
    for d, dirs, fs in os.walk(top):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for f in sorted(fs):
            p = os.path.relpath(os.path.join(d, f), ".")
            if os.path.isfile(p) and not os.path.islink(p):
                yield p

zen = []
for e in sorted(os.listdir(".")):
    zen.extend(sorted(arukine(e)))
zen = sorted(set(zen))

rows = []
noseru_ls = []
for p in zen:
    atama = p.split(os.sep)[0]
    if atama in NOZOKU:
        rows.append([p, os.path.getsize(p), "★除く★", NOZOKU[atama]])
    elif atama in NOSERU:
        rows.append([p, os.path.getsize(p), "載す", "-"])
        noseru_ls.append(p)
    else:
        rows.append([p, os.path.getsize(p), "★未分類(宣の漏れ)★", "★此の行が在れば宣が足らぬ★"])
kaku_tsv(os.path.join("raw", "92_bundle_no_uchiwake.tsv"), rows,
         header=["path(束内相対)", "bytes", "臺帳に", "除く理由"])
kaku(os.path.join("raw", "93_noseru_ichiran.txt"), "\n".join(noseru_ls) + "\n")

# ―― 除く物が現に汚れて居るか(測つてから除く) ――
shirabe = []
for p, riyuu in [("base_gate.sh", "origin/main の門"),
                 ("_fx/kiyoi.txt", "清い型紙(★陰性対照★)"),
                 ("_fx/shin_kitei/karo_mac_dasumae_gate.sh", "新基底の写し"),
                 ("_fx/kyuu_kitei_no_utsushi.sh", "旧基底の写し")]:
    if not os.path.exists(p):
        shirabe.append([p, riyuu, "-", "★束に無し★", "-"])
        continue
    q = subprocess.run(["bash", GATE, "--", p], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    err = q.stderr.decode("utf-8", "replace")
    natta = " / ".join(l.strip() for l in err.split("\n") if l.strip().startswith("★條"))
    shirabe.append([p, riyuu, q.returncode,
                    ("鳴らず(清い)" if q.returncode == 0 else "★鳴つた★"), (natta or "-")[:110]])
kaku_tsv(os.path.join("raw", "94_nozoku_mono_no_joudaku.tsv"), shirabe,
         header=["除く path", "何か", "門の rc", "判", "鳴つた條(110字で截つ)"])

kaku(os.path.join("raw", "95_daichou_no_sengen.txt"),
     "as-of %s(UTC)\n根=%s(★束内相対★ ―― 臺帳の根は束であり repo ではない・裁 seq322699)\n"
     "★束の全 file を歩いた★: %d 本(symlink と __pycache__ は歩かず)\n"
     "  内 臺帳に載す = %d 本(00_shodan.md / driver / raw / _letters)\n"
     "  内 ★除く★   = %d 本 ―― 除く群と理由は raw/92 に一本づつ書いた\n"
     "★『除いた』は『歩いて居らぬ』ではない★ ―― 除いた物も歩き、寸法を数へ、門に掛けて汚濁を測つた(raw/94)。\n"
     "此の數が意味せぬ事: ⑴除いた物が『清い』とは言つて居らぬ(_fx は故意に汚して在る)。\n"
     "  ⑵臺帳の %d 本が束の総てではない。⑶_gate は本器の後に出来る ∴ 此の歩きには未だ無い物が在る。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), os.getcwd(),
        len(zen), len(noseru_ls), len(zen) - len(noseru_ls), len(noseru_ls)))
# ―― ★二度目の歩き★ ―― 一度目の後に ★己が書いた紙★ が増える。差を隠さず数へる。
ato = []
for e in sorted(os.listdir(".")):
    ato.extend(sorted(arukine(e)))
ato = sorted(set(ato))
fueta = [x for x in ato if x not in set(zen)]
kaku_tsv(os.path.join("raw", "97_futatabi_aruku.tsv"),
         [[x, os.path.getsize(x), "★本器が書いた紙★"] for x in fueta] or [["(増えず)", 0, "-"]],
         header=["一度目の後に増えた path", "bytes", "何か"])
kaku(os.path.join("raw", "98_aruki_no_sa.txt"),
     "as-of %s(UTC)\n根=%s\n"
     "一度目の歩き=%d 本 / 二度目の歩き=%d 本 / 差=%d 本\n"
     "%s"
     "∴ raw/92 の内訳表は ★一度目の刻の束★ であり、臺帳はもう一つ後の刻に積む。\n"
     "  二つの數が違ふのは誤りではなく、★刻が違ふ★ からである(刻を書かねば此の差は嘘に成る)。\n"
     "此の數が意味せぬ事: ⑴二度目の %d 本が最終形ではない(_gate は臺帳の後に出来る)。\n"
     "  ⑵差 %d 本が『載せぬ』の意ではない ―― 臺帳は二度目より後に積む ∴ 悉く載る。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        os.getcwd(), len(zen), len(ato), len(fueta),
        ("★差は悉く『本器が書いた紙』である★ ―― 器は己の産物を数へられぬ。\n"
         if fueta else
         "★差 0 は『器が紙を書かぬ』の意ではない★ ―― 前の走りが既に同じ紙を置いた後ゆゑ増えぬ。\n"
         "  本器は毎走 raw/92・93・94・95・97・98 を置く ∴ 初走でのみ其の分だけ増える。\n"),
        len(ato), len(fueta)))

print("全 %d / 載す %d / 除く %d / 未分類 %d" %
      (len(zen), len(noseru_ls), len(zen) - len(noseru_ls),
       sum(1 for r in rows if "未分類" in r[2])))
print("二度目の歩き %d(増 %d ―― 己の産物)" % (len(ato), len(fueta)))
