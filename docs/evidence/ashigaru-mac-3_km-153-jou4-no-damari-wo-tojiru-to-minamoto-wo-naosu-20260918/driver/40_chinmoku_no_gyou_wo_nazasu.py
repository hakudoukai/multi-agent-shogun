# -*- coding: utf-8 -*-
"""★器の何行目が條④を黙らせて居るかを逐語で名指す★(家老令 km-153 ㋐ 前段)
行番は ★焼き込まず★ 逐語の錨で引く(錨が 1 件でなければ何も書かず落ちる = fail-closed)。
四札: 刻=冠 / 根=cwd と二基底の sha256 / rc=本器の returncode / 対照=新基底(閉ぢて居る側)を並べて示す。
此の數が意味せぬ事: 行を名指した事は ★門を直した事ではない★(門は変更統制 ∴ 據ゑず材のみ)。"""
import os
import sys
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

KYUU = os.path.join(BUNDLE, "_fx", "base_kyuu_disk.sh")
SHIN = os.path.join(BUNDLE, "_fx", "base_shin_origin_main.sh")

def yomu(p):
    b = open(p, "rb").read()
    return b, hashlib.sha256(b).hexdigest(), b.decode("utf-8").split("\n")

KB, KSHA, KL = yomu(KYUU)
SB, SSHA, SL = yomu(SHIN)

def hiku(lines, anchor, na):
    """逐語の錨から行番を引く。★1 件でなければ書かずに落ちる★"""
    hit = [i + 1 for i, l in enumerate(lines) if anchor in l]
    if len(hit) != 1:
        raise SystemExit("錨『%s』(%s)が %d 件 ―― 行番を焼き込まず錨を直せ" % (anchor, na, len(hit)))
    return hit[0]

# ―― 旧基底(共用樹 disk・此の席が現に走らせて居る版) ――
KOU = [
    ('elif [ "$sz" -ge 2 ]; then', "外枠 ―― 寸法 2 byte 以上の時だけ末尾二字を見に行く(此処は疵ではない)"),
    ('last2=$(tail -c2 "$f"', "末尾 ★二字だけ★ を 16 進で取る ―― 「末尾の行」ではなく「末尾の 2 byte」を見て居る"),
    ('elif [ "$last2" = "0a0a" ]; then', "★之が黙らせて居る一行★ ―― 末尾二字が丁度 0a0a の時だけ鳴る"),
    ('say "★EOF改行が複数(末尾に空行) ―― ${f}★"', "鳴りの口 ―― 上の一行に届かねば此処へ来られぬ"),
]
# ―― 新基底(origin/main・裁 seq330497 で閉ぢた側) ――
SHN = [
    ("舊 條④ は末尾二字の", "上流が自ら疵を逐語で記した註"),
    ('fks=$(python3 -B "$(dirname "$0")/karo_mac_fukashiji.py"', "兄弟器へ委ね codepoint の類で判ずる(★此の器は disk に無い★)"),
    ('case "$fk4" in', "★閉ぢた一行★ ―― byte 比べを捨て、札 0/1/2/3 で分ける"),
    ("條④ ―― 札 0=良 / 1=EOF改行無 / 2=末尾行が不可視のみ", "札の定義 ―― 空行も不可視字一字の行も同じ札 2 に入る"),
]

rows = []
for anchor, yaku in KOU:
    n = hiku(KL, anchor, "旧")
    rows.append(["旧(共用樹 disk・321行)", n, KL[n - 1].strip(), yaku])
for anchor, yaku in SHN:
    n = hiku(SL, anchor, "新")
    rows.append(["新(origin/main・339行)", n, SL[n - 1].strip(), yaku])
kaku_tsv(os.path.join(BUNDLE, "raw", "40_chinmoku_no_gyou.tsv"), rows,
         header=["基底", "行番", "逐語(前後の空白のみ落とす)", "役"])

# ―― 末尾二字を實測し、なぜ其の一行で黙るかを數で示す ――
FX = os.path.join(BUNDLE, "raw", "fx")
me = []
for na in sorted(os.listdir(FX)):
    p = os.path.join(FX, na)
    if not os.path.isfile(p):
        continue
    b = open(p, "rb").read()
    last2 = b[-2:].hex() if len(b) >= 2 else "(寸法<2)"
    saigo = b.split(b"\n")[-2] if b.endswith(b"\n") and b.count(b"\n") >= 1 else b""
    sg = saigo.decode("utf-8", "replace")
    # ★照合の判は三つに分ける ―― 「合はぬ」の中に『黙るのが正しい紙』と『黙つては成らぬ紙』が混じる★
    if len(b) < 2:
        han = "掛らぬ(寸法<2 ∴ 0byte の口で鳴る)"
    elif last2 == "0a0a":
        han = "合ふ ∴ 鳴る(空行の一形のみ)"
    elif sg.strip() == "" or sg.strip("\u3000\u00a0\u2003\ufeff\t\r ") == "":
        han = "★合はぬが末尾行は空/不可視のみ ∴ 黙つては成らぬ ―― 之が黙り★"
    else:
        han = "合はぬ(末尾行に可視字 ∴ 黙るのが正)"
    me.append([na, len(b), last2, han, repr(sg)])
kaku_tsv(os.path.join(BUNDLE, "raw", "41_matsubi_nibyte.tsv"), me,
         header=["札(fixture)", "byte", "末尾2byte(16進)", '旧 167行 `= "0a0a"` との照合', "末尾行(python repr)"])

kaku(os.path.join(BUNDLE, "raw", "42_nazashi_dan.txt"),
     "as-of %s(UTC)\n根=%s\n旧基底 %s sha256 %s\n新基底 %s sha256 %s\n\n"
     "【名指し ―― 條④を黙らせて居る行】\n"
     "★旧基底 %d 行目★ 逐語: %s\n"
     "  之は「末尾の ★2 byte★ が丁度 `0a0a` か」しか問はぬ。∴ 末尾行が空でも byte 形が違へば此の口へ入れぬ。\n"
     "  實測(raw/41): CRLF 空行 = `0d0a` / U+3000 一字の行 = `800a` / 素の空行 = `0a0a`。\n"
     "  ∴ 三つの内 ★一つ(素の空行)だけ★ が鳴り、他二つは黙る。之が當席が km-150 で見た黙りの正体である。\n"
     "  黙りを作つて居るのは %d 行目の `last2=$(tail -c2 ...)`(行ではなく byte を見る取り方)と\n"
     "  %d 行目の一致比べの二行であり、%d 行目の鳴り口には ★届いて居らぬだけ★ である(鳴り口に疵は無い)。\n\n"
     "【新基底 ―― 上流が既に閉ぢて居る】\n"
     "★新基底 %d 行目★ 逐語: %s\n"
     "  byte 比べを捨て、兄弟器 karo_mac_fukashiji.py の札(0=良/1=EOF改行無/2=末尾行が不可視のみ/3=0byte)で分ける。\n"
     "  ∴ 空行・CRLF 空行・不可視字一字の行が ★同じ札 2★ に入り、三つとも鳴る(raw/30 實測: fx05 fx06 fx07 が新基底で悉く rc=1)。\n\n"
     "【之が意味せぬ事】\n"
     "・上流が閉ぢた事は ★此の席の門が直つた事ではない★ ―― 走つて居るのは旧基底(disk・未commit)である。\n"
     "・行を名指した事は門を直した事ではない。門は変更統制 ∴ 當席は據ゑず ★材(當て紙)のみ★ を出す。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT,
        os.path.relpath(KYUU, ROOT), KSHA, os.path.relpath(SHIN, ROOT), SSHA,
        rows[2][1], rows[2][2], rows[1][1], rows[2][1], rows[3][1],
        rows[6][1], rows[6][2]))
print("名指し完了 ―― 旧 %d行目 `%s`" % (rows[2][1], rows[2][2]))
print("            新 %d行目 `%s`" % (rows[6][1], rows[6][2]))
